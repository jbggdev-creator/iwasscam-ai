"""Tests for the LangGraph text analysis workflow."""
import pytest

from app.agents.social_engineering_agent import detect_social_engineering
from app.agents.text_agent import (
    TextAnalysisState,
    _rule_based_explanation,
    _score_risk_node,
    build_text_graph,
)


def _base_state(**overrides) -> TextAnalysisState:
    base: TextAnalysisState = {
        "scenario": "test scenario",
        "rag_context": [],
        "se_signals": [],
        "se_score": 0,
        "se_confidence": 0.5,
        "risk_score": 0,
        "risk_level": "low",
        "confidence": 0.5,
        "findings": [],
        "explanation": "",
    }
    return {**base, **overrides}  # type: ignore[misc]


def _state_with_se(scenario: str, **overrides) -> TextAnalysisState:
    """Build state where SE detection has already run (simulates post-detect_se_node)."""
    se = detect_social_engineering(scenario)
    return _base_state(
        scenario=scenario,
        se_signals=se.signals,
        se_score=se.total_score,
        se_confidence=se.confidence,
        **overrides,
    )


@pytest.mark.asyncio
async def test_score_risk_no_signals_stays_low():
    state = _state_with_se("I want to buy a phone from a trusted friend.")
    result = await _score_risk_node(state)
    assert result["risk_level"] == "low"
    assert result["risk_score"] < 30


@pytest.mark.asyncio
async def test_score_risk_upfront_payment_raises_score():
    state = _state_with_se("A recruiter asked me to pay a registration fee before starting.")
    result = await _score_risk_node(state)
    assert result["risk_score"] >= 40
    assert result["risk_level"] in ("medium", "high", "critical")


@pytest.mark.asyncio
async def test_rag_context_adds_known_scam_finding():
    state = _state_with_se(
        "A recruiter asked me to pay a registration fee before starting.",
        rag_context=[
            {"source": "DICT Alert — Fake Job Recruitment Scam", "content": "...", "metadata": {}}
        ],
    )
    result = await _score_risk_node(state)
    finding_types = {f["finding_type"] for f in result["findings"]}
    assert "known_scam_pattern" in finding_types


@pytest.mark.asyncio
async def test_rag_context_boosts_confidence():
    scenario = "Work from home easy money no experience needed."
    no_rag = await _score_risk_node(_state_with_se(scenario))
    with_rag = await _score_risk_node(
        _state_with_se(
            scenario,
            rag_context=[{"source": "DICT Alert", "content": "...", "metadata": {}}],
        )
    )
    assert with_rag["confidence"] >= no_rag["confidence"]


def test_rule_based_explanation_critical():
    findings = [
        {"finding_type": "prize_lottery_claim", "description": "Prize claim detected.", "severity": "critical"},
        {"finding_type": "upfront_payment_demand", "description": "Payment demand.", "severity": "critical"},
    ]
    explanation = _rule_based_explanation("critical", findings, [])
    assert "2 serious" in explanation
    assert "do not" in explanation.lower()


def test_rule_based_explanation_low_risk():
    explanation = _rule_based_explanation("low", [], [])
    assert "low-risk" in explanation


def test_rule_based_explanation_includes_rag_note():
    rag_context = [{"source": "BSP Advisory", "content": "...", "metadata": {}}]
    explanation = _rule_based_explanation("high", [], rag_context)
    assert "known Philippine scam" in explanation


@pytest.mark.asyncio
async def test_full_graph_returns_complete_state():
    graph = build_text_graph()
    initial: TextAnalysisState = {
        "scenario": "They said I won a prize but need to pay a fee first via gcash.",
        "rag_context": [],
        "se_signals": [],
        "se_score": 0,
        "se_confidence": 0.5,
        "risk_score": 0,
        "risk_level": "low",
        "confidence": 0.5,
        "findings": [],
        "explanation": "",
    }
    result = await graph.ainvoke(initial)
    assert result["explanation"] != ""
    assert result["risk_level"] in ("low", "medium", "high", "critical")
    assert 0.0 <= result["confidence"] <= 1.0
    assert isinstance(result["findings"], list)


@pytest.mark.asyncio
async def test_full_graph_clean_scenario():
    graph = build_text_graph()
    initial: TextAnalysisState = {
        "scenario": "My friend wants to sell me a laptop. He's asking for the market price.",
        "rag_context": [],
        "se_signals": [],
        "se_score": 0,
        "se_confidence": 0.5,
        "risk_score": 0,
        "risk_level": "low",
        "confidence": 0.5,
        "findings": [],
        "explanation": "",
    }
    result = await graph.ainvoke(initial)
    assert result["risk_level"] == "low"
    assert result["explanation"] != ""
