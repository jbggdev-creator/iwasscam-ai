import json
import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.prompts import TEXT_ANALYSIS_SYSTEM_PROMPT
from app.agents.social_engineering_agent import detect_social_engineering

logger = logging.getLogger(__name__)

_SCORE_CAP = 100
_RAG_HIT_SCORE_BONUS = 10


class TextAnalysisState(TypedDict):
    scenario: str
    rag_context: list[dict]   # pre-fetched before graph invocation
    se_signals: list[dict]
    se_score: int
    se_confidence: float
    risk_score: int
    risk_level: str
    confidence: float
    findings: list[dict]
    explanation: str


# ── Nodes ─────────────────────────────────────────────────────────────────────

async def _detect_se_node(state: TextAnalysisState) -> TextAnalysisState:
    result = detect_social_engineering(state["scenario"])
    return {
        **state,
        "se_signals": result.signals,
        "se_score": result.total_score,
        "se_confidence": result.confidence,
    }


async def _score_risk_node(state: TextAnalysisState) -> TextAnalysisState:
    score = state["se_score"]
    findings: list[dict] = list(state["se_signals"])

    rag_hit_count = len(state["rag_context"])
    if rag_hit_count > 0:
        rag_bonus = min(_RAG_HIT_SCORE_BONUS * rag_hit_count, 20)
        score = min(score + rag_bonus, _SCORE_CAP)
        findings.append(
            {
                "finding_type": "known_scam_pattern",
                "description": (
                    f"This scenario matches {rag_hit_count} known scam pattern(s) "
                    "from our Philippine fraud intelligence database."
                ),
                "severity": "high",
            }
        )

    if score >= 80:
        risk_level = "critical"
    elif score >= 60:
        risk_level = "high"
    elif score >= 30:
        risk_level = "medium"
    else:
        risk_level = "low"

    rag_confidence_boost = min(rag_hit_count * 0.07, 0.2)
    confidence = round(
        min(0.95, state["se_confidence"] + rag_confidence_boost), 2
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
        "critical": f"This scenario has {count} serious warning sign(s) and is very likely a scam.",
        "high": f"This scenario shows {count} suspicious indicator(s) and should be treated with extreme caution.",
        "medium": f"This scenario has {count} potential red flag(s). Proceed carefully.",
        "low": "This scenario appears relatively low-risk based on the signals we checked.",
    }
    intro = intros.get(risk_level, intros["medium"])
    top = " ".join(f["description"] for f in findings[:2])
    advice = (
        " Do NOT make any payments or share personal information until you have independently verified the other party."
        if risk_level in ("high", "critical")
        else " Always verify the identity of anyone requesting money or personal details."
    )
    source_note = (
        " This matches known Philippine scam patterns documented in fraud advisories."
        if rag_context
        else ""
    )
    return f"{intro} {top}{advice}{source_note}".strip()


async def _generate_explanation_node(state: TextAnalysisState) -> TextAnalysisState:
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
                    "scenario": state["scenario"][:500],
                    "signals": [f["finding_type"] for f in state["se_signals"]],
                    "rag_matches": [r["source"] for r in state["rag_context"]],
                    "risk_level": state["risk_level"],
                },
                ensure_ascii=False,
            )
            response = await llm.ainvoke(
                [
                    SystemMessage(content=TEXT_ANALYSIS_SYSTEM_PROMPT),
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

def build_text_graph():
    graph: StateGraph = StateGraph(TextAnalysisState)
    graph.add_node("detect_se", _detect_se_node)
    graph.add_node("score_risk", _score_risk_node)
    graph.add_node("generate_explanation", _generate_explanation_node)
    graph.set_entry_point("detect_se")
    graph.add_edge("detect_se", "score_risk")
    graph.add_edge("score_risk", "generate_explanation")
    graph.add_edge("generate_explanation", END)
    return graph.compile()


text_graph = build_text_graph()
