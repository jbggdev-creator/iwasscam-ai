import pytest
from unittest.mock import patch, MagicMock

from app.agents.image_agent import (
    _extract_content_node,
    _detect_signals_node,
    _score_risk_node,
    _generate_explanation_node,
    _rule_based_explanation,
)


def _base_state(**overrides):
    state = {
        "image_bytes": b"fake-image",
        "extracted_text": "",
        "rag_context": [],
        "se_signals": [],
        "se_score": 0,
        "risk_score": 0,
        "risk_level": "low",
        "confidence": 0.5,
        "findings": [],
        "explanation": "",
    }
    state.update(overrides)
    return state


class TestExtractContentNode:
    async def test_stores_extracted_text(self):
        with patch(
            "app.services.ocr_service.extract_text_from_image",
            return_value="GCash receipt ₱500",
        ):
            result = await _extract_content_node(_base_state())
        assert result["extracted_text"] == "GCash receipt ₱500"

    async def test_adds_ocr_failed_finding_when_ocr_returns_none(self):
        with patch("app.services.ocr_service.extract_text_from_image", return_value=None):
            result = await _extract_content_node(_base_state())
        assert result["extracted_text"] == ""
        assert any(f["finding_type"] == "ocr_failed" for f in result["findings"])


class TestDetectSignalsNode:
    async def test_adds_fake_receipt_finding_for_gcash_with_amount_and_ref(self):
        text = "GCash ₱500 reference no 12345"
        mock_se = MagicMock()
        mock_se.signals = []
        mock_se.total_score = 0
        with patch("app.agents.image_agent.detect_social_engineering", return_value=mock_se):
            result = await _detect_signals_node(_base_state(extracted_text=text))
        assert any(f["finding_type"] == "fake_receipt_pattern" for f in result["findings"])

    async def test_adds_credential_phishing_finding_for_login_text(self):
        text = "Enter your password to verify account"
        mock_se = MagicMock()
        mock_se.signals = []
        mock_se.total_score = 0
        with patch("app.agents.image_agent.detect_social_engineering", return_value=mock_se):
            result = await _detect_signals_node(_base_state(extracted_text=text))
        assert any(f["finding_type"] == "credential_phishing" for f in result["findings"])

    async def test_no_findings_for_clean_text(self):
        text = "Hello, this is a normal message."
        mock_se = MagicMock()
        mock_se.signals = []
        mock_se.total_score = 0
        with patch("app.agents.image_agent.detect_social_engineering", return_value=mock_se):
            result = await _detect_signals_node(_base_state(extracted_text=text))
        assert result["findings"] == []

    async def test_skips_se_detection_when_no_text(self):
        result = await _detect_signals_node(_base_state(extracted_text=""))
        assert result["se_signals"] == []
        assert result["se_score"] == 0


class TestScoreRiskNode:
    async def test_critical_risk_at_high_score(self):
        result = await _score_risk_node(_base_state(se_score=85))
        assert result["risk_level"] == "critical"

    async def test_high_risk_at_medium_high_score(self):
        result = await _score_risk_node(_base_state(se_score=65))
        assert result["risk_level"] == "high"

    async def test_medium_risk(self):
        result = await _score_risk_node(_base_state(se_score=40))
        assert result["risk_level"] == "medium"

    async def test_low_risk_at_low_score(self):
        result = await _score_risk_node(_base_state(se_score=10))
        assert result["risk_level"] == "low"

    async def test_rag_context_boosts_score_and_adds_finding(self):
        rag = [{"content": "scam doc 1"}, {"content": "scam doc 2"}]
        result = await _score_risk_node(_base_state(se_score=50, rag_context=rag))
        assert any(f["finding_type"] == "known_scam_pattern" for f in result["findings"])
        assert result["risk_score"] > 50

    async def test_score_capped_at_100(self):
        result = await _score_risk_node(_base_state(se_score=99, rag_context=[{}] * 10))
        assert result["risk_score"] <= 100


class TestGenerateExplanationNode:
    async def test_falls_back_to_rule_based_when_llm_disabled(self):
        mock_settings = MagicMock()
        mock_settings.use_llm = False
        with patch("app.core.config.get_settings", return_value=mock_settings):
            result = await _generate_explanation_node(
                _base_state(
                    risk_level="high",
                    findings=[
                        {
                            "finding_type": "fake_receipt_pattern",
                            "description": "Suspicious receipt.",
                            "severity": "high",
                        }
                    ],
                )
            )
        assert len(result["explanation"]) > 0

    async def test_falls_back_to_rule_based_on_llm_error(self):
        mock_settings = MagicMock()
        mock_settings.use_llm = True
        with (
            patch("app.core.config.get_settings", return_value=mock_settings),
            patch(
                "langchain_ollama.ChatOllama",
                side_effect=ImportError("no ollama"),
            ),
        ):
            result = await _generate_explanation_node(_base_state(risk_level="medium"))
        assert len(result["explanation"]) > 0


class TestRuleBasedExplanation:
    def test_critical_explanation_mentions_warning_signs(self):
        findings = [
            {"description": "Fake receipt detected.", "finding_type": "x", "severity": "critical"}
        ]
        text = _rule_based_explanation("critical", findings, [])
        assert "critical" in text.lower() or "serious" in text.lower()

    def test_low_risk_explanation_is_reassuring(self):
        text = _rule_based_explanation("low", [], [])
        assert "low-risk" in text.lower()

    def test_rag_context_adds_source_note(self):
        text = _rule_based_explanation("high", [], [{"content": "doc"}])
        assert "Philippine" in text or "fraud" in text.lower()
