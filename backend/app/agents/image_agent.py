import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.prompts import IMAGE_ANALYSIS_SYSTEM_PROMPT
from app.agents.social_engineering_agent import detect_social_engineering

logger = logging.getLogger(__name__)

_SCORE_CAP = 100
_RAG_HIT_SCORE_BONUS = 10


class ImageAnalysisState(TypedDict):
    image_bytes: bytes
    extracted_text: str
    rag_context: list[dict]   # pre-fetched before graph invocation
    se_signals: list[dict]
    se_score: int
    risk_score: int
    risk_level: str
    confidence: float
    findings: list[dict]
    explanation: str


# ── Nodes ─────────────────────────────────────────────────────────────────────

async def _extract_content_node(state: ImageAnalysisState) -> ImageAnalysisState:
    from app.services.ocr_service import extract_text_from_image

    text = extract_text_from_image(state["image_bytes"])
    if text is None:
        return {
            **state,
            "extracted_text": "",
            "findings": [
                *state["findings"],
                {
                    "finding_type": "ocr_failed",
                    "description": "Could not extract text from the image. Manual review is recommended.",
                    "severity": "medium",
                },
            ],
        }
    return {**state, "extracted_text": text}


async def _detect_signals_node(state: ImageAnalysisState) -> ImageAnalysisState:
    extracted_text = state["extracted_text"]
    findings: list[dict] = list(state["findings"])
    image_score = 0

    se_signals: list[dict] = []
    se_score = 0

    if extracted_text:
        result = detect_social_engineering(extracted_text)
        se_signals = result.signals
        se_score = result.total_score

        text_lower = extracted_text.lower()

        if any(kw in text_lower for kw in ("gcash", "paymaya", "maya")):
            has_amount = any(marker in extracted_text for marker in ("₱", "PHP"))
            has_ref = any(
                kw in text_lower for kw in ("reference", "ref no", "transaction")
            )
            if has_amount and has_ref:
                findings.append(
                    {
                        "finding_type": "fake_receipt_pattern",
                        "description": (
                            "Image contains GCash/PayMaya receipt-like content. "
                            "Verify this transaction directly in your app."
                        ),
                        "severity": "high",
                    }
                )
                image_score += 25

        if any(
            kw in text_lower
            for kw in ("password", "enter your pin", "verify account", "login")
        ):
            findings.append(
                {
                    "finding_type": "credential_phishing",
                    "description": (
                        "Image appears to show a login or credential entry screen "
                        "— possible phishing page screenshot."
                    ),
                    "severity": "critical",
                }
            )
            image_score += 35

    return {
        **state,
        "se_signals": se_signals,
        "se_score": se_score + image_score,
        "findings": findings,
    }


async def _score_risk_node(state: ImageAnalysisState) -> ImageAnalysisState:
    score = state["se_score"]
    findings: list[dict] = list(state["findings"])
    findings.extend(state["se_signals"])

    rag_hit_count = len(state["rag_context"])
    if rag_hit_count > 0:
        rag_bonus = min(_RAG_HIT_SCORE_BONUS * rag_hit_count, 20)
        score = min(score + rag_bonus, _SCORE_CAP)
        findings.append(
            {
                "finding_type": "known_scam_pattern",
                "description": (
                    f"This image content matches {rag_hit_count} known scam pattern(s) "
                    "from our Philippine fraud intelligence database."
                ),
                "severity": "high",
            }
        )
    else:
        score = min(score, _SCORE_CAP)

    if score >= 80:
        risk_level = "critical"
    elif score >= 60:
        risk_level = "high"
    elif score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"

    rag_confidence_boost = min(rag_hit_count * 0.07, 0.2)
    se_signal_count = len(state["se_signals"])
    confidence = round(
        min(0.95, 0.45 + (se_signal_count * 0.1) + (score / 250) + rag_confidence_boost), 2
    )

    return {
        **state,
        "risk_score": score,
        "risk_level": risk_level,
        "confidence": confidence,
        "findings": findings,
    }


def _rule_based_explanation(
    risk_level: str, findings: list[dict], rag_context: list[dict]
) -> str:
    count = len(findings)
    intros = {
        "critical": f"This image content has {count} serious warning sign(s) and is very likely related to a scam.",
        "high": f"This image content shows {count} suspicious indicator(s) and should be treated with extreme caution.",
        "medium": f"This image content has {count} potential red flag(s). Proceed carefully.",
        "low": "This image content appears relatively low-risk based on the signals we checked.",
    }
    intro = intros.get(risk_level, intros["medium"])
    top = " ".join(f["description"] for f in findings[:2])
    advice = (
        " Do NOT send money or share personal information based on this image without independently verifying the other party."
        if risk_level in ("high", "critical")
        else " Always verify the authenticity of any receipts or messages directly through the official app or website."
    )
    source_note = (
        " This matches known Philippine scam patterns documented in fraud advisories."
        if rag_context
        else ""
    )
    return f"{intro} {top}{advice}{source_note}".strip()


async def _generate_explanation_node(state: ImageAnalysisState) -> ImageAnalysisState:
    from app.core.config import get_settings
    settings = get_settings()
    explanation = ""

    if settings.use_llm:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage
            from langchain_ollama import ChatOllama

            llm = ChatOllama(model=settings.ollama_model, base_url=settings.ollama_base_url)
            payload = json.dumps(
                {
                    "extracted_text": state["extracted_text"][:500],
                    "visual_signals": [f["finding_type"] for f in state["findings"]],
                    "risk_level": state["risk_level"],
                },
                ensure_ascii=False,
            )
            response = await llm.ainvoke(
                [
                    SystemMessage(content=IMAGE_ANALYSIS_SYSTEM_PROMPT),
                    HumanMessage(content=payload),
                ]
            )
            explanation = str(response.content).strip()
        except Exception as exc:
            logger.warning("LLM explanation failed, falling back to rule-based: %s", exc)

    if not explanation:
        explanation = _rule_based_explanation(
            state["risk_level"], state["findings"], state["rag_context"]
        )

    return {**state, "explanation": explanation}


# ── Graph assembly ─────────────────────────────────────────────────────────────

def build_image_graph():
    graph: StateGraph = StateGraph(ImageAnalysisState)
    graph.add_node("extract_content", _extract_content_node)
    graph.add_node("detect_signals", _detect_signals_node)
    graph.add_node("score_risk", _score_risk_node)
    graph.add_node("generate_explanation", _generate_explanation_node)
    graph.set_entry_point("extract_content")
    graph.add_edge("extract_content", "detect_signals")
    graph.add_edge("detect_signals", "score_risk")
    graph.add_edge("score_risk", "generate_explanation")
    graph.add_edge("generate_explanation", END)
    return graph.compile()


image_graph = build_image_graph()
