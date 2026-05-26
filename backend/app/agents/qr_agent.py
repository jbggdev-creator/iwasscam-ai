import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.prompts import QR_ANALYSIS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_SCORE_CAP = 100


class QRAnalysisState(TypedDict):
    image_bytes: bytes
    decoded_content: str
    content_type: str   # "url", "text", "unreadable"
    risk_score: int
    risk_level: str
    confidence: float
    findings: list[dict]
    explanation: str


# ── Nodes ─────────────────────────────────────────────────────────────────────

async def _decode_qr_node(state: QRAnalysisState) -> QRAnalysisState:
    from app.services.qr_service import decode_qr_from_image

    decoded = decode_qr_from_image(state["image_bytes"])
    if decoded is None:
        return {
            **state,
            "decoded_content": "",
            "content_type": "unreadable",
            "findings": [
                *state["findings"],
                {
                    "finding_type": "qr_unreadable",
                    "description": "Could not decode the QR code. Ensure the image is clear and well-lit.",
                    "severity": "low",
                },
            ],
        }

    if decoded.startswith("http://") or decoded.startswith("https://"):
        content_type = "url"
    else:
        content_type = "text"

    return {**state, "decoded_content": decoded, "content_type": content_type}


async def _analyze_content_node(state: QRAnalysisState) -> QRAnalysisState:
    content_type = state["content_type"]
    findings: list[dict] = list(state["findings"])

    if content_type == "url":
        from app.agents.url_agent import _score_features
        from app.services.url_intelligence import UrlIntelligenceService

        service = UrlIntelligenceService()
        features = await service.analyze(state["decoded_content"])
        score, risk_level, confidence, url_findings = _score_features(features)

        decoded = state["decoded_content"]
        if len(decoded) > 80:
            url_preview = f"{decoded[:80]}..."
        else:
            url_preview = decoded

        findings.extend(url_findings)
        findings.append(
            {
                "finding_type": "qr_encoded_url",
                "description": f"QR code contains URL: {url_preview}",
                "severity": "medium",
            }
        )

        return {
            **state,
            "risk_score": score,
            "risk_level": risk_level,
            "confidence": confidence,
            "findings": findings,
        }

    if content_type == "text":
        from app.agents.social_engineering_agent import detect_social_engineering

        result = detect_social_engineering(state["decoded_content"])
        findings.extend(result.signals)
        return {
            **state,
            "risk_score": result.total_score,
            "risk_level": result.risk_level,
            "confidence": result.confidence,
            "findings": findings,
        }

    # content_type == "unreadable" — keep defaults
    return {**state, "findings": findings}


async def _generate_explanation_node(state: QRAnalysisState) -> QRAnalysisState:
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
                    "decoded_content": state["decoded_content"][:500],
                    "content_type": state["content_type"],
                    "risk_level": state["risk_level"],
                    "findings": [f["finding_type"] for f in state["findings"]],
                },
                ensure_ascii=False,
            )
            response = await llm.ainvoke(
                [
                    SystemMessage(content=QR_ANALYSIS_SYSTEM_PROMPT),
                    HumanMessage(content=payload),
                ]
            )
            explanation = str(response.content).strip()
        except Exception as exc:
            logger.warning("LLM explanation failed, falling back to rule-based: %s", exc)

    if not explanation:
        explanation = _rule_based_explanation(state)

    return {**state, "explanation": explanation}


def _rule_based_explanation(state: QRAnalysisState) -> str:
    content_type = state["content_type"]
    risk_level = state["risk_level"]
    findings = state["findings"]
    count = len(findings)

    if content_type == "unreadable":
        return (
            "The QR code could not be decoded from the provided image. "
            "Ensure the image is clear, well-lit, and the QR code is fully visible before scanning."
        )

    intros = {
        "critical": f"This QR code has {count} serious warning sign(s) and is very likely a scam.",
        "high": f"This QR code shows {count} suspicious indicator(s) and should be treated with extreme caution.",
        "medium": f"This QR code has {count} potential red flag(s). Proceed carefully.",
        "low": "This QR code appears relatively low-risk based on the signals we checked.",
    }
    intro = intros.get(risk_level, intros["medium"])
    top = " ".join(f["description"] for f in findings[:2])

    if content_type == "url":
        advice = (
            " Do NOT visit this URL or enter any personal information."
            if risk_level in ("high", "critical")
            else " Verify this URL is from a trusted source before proceeding."
        )
        return f"{intro} {top}{advice}".strip()

    # content_type == "text"
    advice = (
        " Do NOT respond to or act on this message without independently verifying the source."
        if risk_level in ("high", "critical")
        else " Always verify the identity of anyone sending QR codes requesting action or payment."
    )
    return f"{intro} {top}{advice}".strip()


# ── Graph assembly ─────────────────────────────────────────────────────────────

def build_qr_graph():
    graph: StateGraph = StateGraph(QRAnalysisState)
    graph.add_node("decode_qr", _decode_qr_node)
    graph.add_node("analyze_content", _analyze_content_node)
    graph.add_node("generate_explanation", _generate_explanation_node)
    graph.set_entry_point("decode_qr")
    graph.add_edge("decode_qr", "analyze_content")
    graph.add_edge("analyze_content", "generate_explanation")
    graph.add_edge("generate_explanation", END)
    return graph.compile()


qr_graph = build_qr_graph()
