import json
import logging
from dataclasses import asdict
from typing import TypedDict

from langgraph.graph import StateGraph, END

from app.agents.prompts import URL_ANALYSIS_SYSTEM_PROMPT
from app.services.url_intelligence import UrlFeatures, UrlIntelligenceService

logger = logging.getLogger(__name__)

_SCORE_CAP = 100


class UrlAnalysisState(TypedDict):
    url: str
    features: dict | None
    risk_score: int
    risk_level: str
    confidence: float
    findings: list[dict]
    explanation: str


# ── Scoring ───────────────────────────────────────────────────────────────────

def _score_features(features: UrlFeatures) -> tuple[int, str, float, list[dict]]:
    score = 0
    findings: list[dict] = []

    def _finding(finding_type: str, description: str, severity: str) -> dict:
        return {"finding_type": finding_type, "description": description, "severity": severity}

    if features.is_brand_impersonation:
        score += 60
        findings.append(_finding(
            "brand_impersonation",
            f"This domain impersonates '{features.impersonated_brand}' using character substitution "
            f"(e.g. '0' instead of 'o', '1' instead of 'l'). This is a textbook phishing technique — do NOT visit this site.",
            "critical",
        ))

    if features.whois_error or features.domain_age_days is None:
        score += 5
        findings.append(_finding(
            "whois_unavailable",
            "Domain registration information is unavailable or private.",
            "low",
        ))
    elif features.domain_age_days < 7:
        score += 40
        findings.append(_finding(
            "very_new_domain",
            f"Domain was registered only {features.domain_age_days} day(s) ago — extremely new domains are a major phishing indicator.",
            "critical",
        ))
    elif features.domain_age_days < 30:
        score += 25
        findings.append(_finding(
            "new_domain",
            f"Domain is only {features.domain_age_days} days old. Newly registered domains are frequently used in scams.",
            "high",
        ))
    elif features.domain_age_days < 90:
        score += 10
        findings.append(_finding(
            "recent_domain",
            f"Domain was registered {features.domain_age_days} days ago, which is relatively recent.",
            "medium",
        ))

    if features.is_suspicious_tld:
        score += 20
        findings.append(_finding(
            "suspicious_tld",
            f"The domain uses a high-risk TLD (.{features.tld}), commonly associated with free hosting and phishing sites.",
            "high",
        ))

    if not features.ssl_valid:
        score += 25
        findings.append(_finding(
            "invalid_ssl",
            "The URL does not use a valid SSL/TLS certificate. Your data would be transmitted insecurely.",
            "high",
        ))

    if features.url_entropy > 4.5:
        score += 15
        findings.append(_finding(
            "high_url_entropy",
            f"The URL contains an unusually random-looking string (entropy: {features.url_entropy:.2f}), a pattern common in auto-generated phishing links.",
            "medium",
        ))

    if features.redirect_count > 3:
        score += 10
        findings.append(_finding(
            "excessive_redirects",
            f"The URL redirects {features.redirect_count} time(s), which can be used to obscure the true destination.",
            "medium",
        ))

    score = min(score, _SCORE_CAP)

    if score >= 80:
        risk_level = "critical"
    elif score >= 60:
        risk_level = "high"
    elif score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"

    signal_count = 4
    if not features.whois_error:
        signal_count += 1
    confidence = round(min(0.95, 0.5 + (signal_count / 10) + (score / 200)), 2)

    return score, risk_level, confidence, findings


# ── LLM explanation ───────────────────────────────────────────────────────────

def _rule_based_explanation(risk_level: str, findings: list[dict]) -> str:
    count = len(findings)
    intros = {
        "critical": f"This URL has {count} serious warning sign(s) and is very likely a scam or phishing attempt.",
        "high": f"This URL shows {count} suspicious indicator(s) and should be treated with extreme caution.",
        "medium": f"This URL has {count} potential red flag(s). Proceed with caution.",
        "low": "This URL appears relatively safe based on the signals we checked.",
    }
    intro = intros.get(risk_level, intros["medium"])
    top_descriptions = " ".join(f["description"] for f in findings[:2])
    advice = (
        " Do NOT enter personal information or make payments on this site."
        if risk_level in ("high", "critical")
        else " Always verify the sender before sharing personal information."
    )
    return f"{intro} {top_descriptions}{advice}".strip()


async def _llm_explanation(features: UrlFeatures, risk_level: str) -> str:
    """Calls Qwen 3 via Ollama. Returns empty string if USE_LLM=false or Ollama is unreachable."""
    from app.core.config import get_settings
    settings = get_settings()

    if not settings.use_llm:
        return ""

    try:
        from langchain_ollama import ChatOllama
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)
        payload = json.dumps({
            "url": features.url,
            "domain_age_days": features.domain_age_days,
            "ssl_valid": features.ssl_valid,
            "is_suspicious_tld": features.is_suspicious_tld,
            "tld": features.tld,
            "redirect_count": features.redirect_count,
            "url_entropy": round(features.url_entropy, 2),
            "is_brand_impersonation": features.is_brand_impersonation,
            "impersonated_brand": features.impersonated_brand,
            "risk_level": risk_level,
        })
        response = await llm.ainvoke([
            SystemMessage(content=URL_ANALYSIS_SYSTEM_PROMPT),
            HumanMessage(content=payload),
        ])
        return str(response.content).strip()
    except Exception as exc:
        logger.warning("LLM explanation failed, using rule-based fallback: %s", exc)
        return ""


# ── LangGraph nodes ───────────────────────────────────────────────────────────

async def _extract_features_node(state: UrlAnalysisState) -> UrlAnalysisState:
    service = UrlIntelligenceService()
    features = await service.analyze(state["url"])
    return {**state, "features": asdict(features)}


async def _score_risk_node(state: UrlAnalysisState) -> UrlAnalysisState:
    features = UrlFeatures(**state["features"])  # type: ignore[arg-type]
    score, risk_level, confidence, findings = _score_features(features)
    return {**state, "risk_score": score, "risk_level": risk_level, "confidence": confidence, "findings": findings}


async def _generate_explanation_node(state: UrlAnalysisState) -> UrlAnalysisState:
    features = UrlFeatures(**state["features"])  # type: ignore[arg-type]
    explanation = await _llm_explanation(features, state["risk_level"])
    if not explanation:
        explanation = _rule_based_explanation(state["risk_level"], state["findings"])
    return {**state, "explanation": explanation}


# ── Graph assembly ────────────────────────────────────────────────────────────

def build_url_graph():
    graph: StateGraph = StateGraph(UrlAnalysisState)
    graph.add_node("extract_features", _extract_features_node)
    graph.add_node("score_risk", _score_risk_node)
    graph.add_node("generate_explanation", _generate_explanation_node)
    graph.set_entry_point("extract_features")
    graph.add_edge("extract_features", "score_risk")
    graph.add_edge("score_risk", "generate_explanation")
    graph.add_edge("generate_explanation", END)
    return graph.compile()


url_graph = build_url_graph()
