import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.agents.qr_agent import (
    _decode_qr_node,
    _analyze_content_node,
    _generate_explanation_node,
    _rule_based_explanation,
)


def _base_state(**overrides):
    state = {
        "image_bytes": b"fake-qr-image",
        "decoded_content": "",
        "content_type": "unreadable",
        "risk_score": 0,
        "risk_level": "low",
        "confidence": 0.5,
        "findings": [],
        "explanation": "",
    }
    state.update(overrides)
    return state


class TestDecodeQrNode:
    async def test_stores_decoded_url(self):
        with patch(
            "app.services.qr_service.decode_qr_from_image",
            return_value="https://evil.tk/pay",
        ):
            result = await _decode_qr_node(_base_state())
        assert result["decoded_content"] == "https://evil.tk/pay"
        assert result["content_type"] == "url"

    async def test_stores_decoded_text(self):
        with patch(
            "app.services.qr_service.decode_qr_from_image",
            return_value="Call 09171234567 to claim your prize",
        ):
            result = await _decode_qr_node(_base_state())
        assert result["content_type"] == "text"

    async def test_adds_unreadable_finding_when_decode_fails(self):
        with patch("app.services.qr_service.decode_qr_from_image", return_value=None):
            result = await _decode_qr_node(_base_state())
        assert result["decoded_content"] == ""
        assert result["content_type"] == "unreadable"
        assert any(f["finding_type"] == "qr_unreadable" for f in result["findings"])


class TestAnalyzeContentNode:
    async def test_url_content_runs_url_intelligence(self):
        mock_features = MagicMock()

        with (
            patch("app.services.url_intelligence.UrlIntelligenceService") as MockService,
            patch(
                "app.agents.url_agent._score_features",
                return_value=(75, "high", 0.82, []),
            ),
        ):
            instance = MockService.return_value
            instance.analyze = AsyncMock(return_value=mock_features)
            result = await _analyze_content_node(
                _base_state(decoded_content="https://evil.tk/pay", content_type="url")
            )

        assert result["risk_level"] == "high"
        assert result["confidence"] == 0.82
        assert any(f["finding_type"] == "qr_encoded_url" for f in result["findings"])

    async def test_text_content_runs_social_engineering_detection(self):
        mock_se = MagicMock()
        mock_se.signals = [
            {"finding_type": "urgency", "description": "Urgent payment needed.", "severity": "high"}
        ]
        mock_se.total_score = 55
        mock_se.risk_level = "high"
        mock_se.confidence = 0.75

        with patch("app.agents.social_engineering_agent.detect_social_engineering", return_value=mock_se):
            result = await _analyze_content_node(
                _base_state(
                    decoded_content="URGENT: Send ₱1000 now to claim prize",
                    content_type="text",
                )
            )

        assert result["risk_level"] == "high"
        assert len(result["findings"]) > 0

    async def test_unreadable_qr_keeps_defaults(self):
        result = await _analyze_content_node(_base_state(content_type="unreadable"))
        assert result["risk_level"] == "low"
        assert result["risk_score"] == 0


class TestGenerateExplanationNode:
    async def test_falls_back_to_rule_based_when_llm_disabled(self):
        mock_settings = MagicMock()
        mock_settings.use_llm = False
        with patch("app.core.config.get_settings", return_value=mock_settings):
            result = await _generate_explanation_node(
                _base_state(
                    decoded_content="https://evil.tk",
                    content_type="url",
                    risk_level="high",
                    findings=[
                        {
                            "finding_type": "suspicious_tld",
                            "description": "Bad TLD.",
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
            patch("langchain_ollama.ChatOllama", side_effect=ImportError("no ollama")),
        ):
            result = await _generate_explanation_node(
                _base_state(content_type="url", risk_level="medium")
            )
        assert len(result["explanation"]) > 0


class TestRuleBasedExplanation:
    def test_unreadable_returns_decode_guidance(self):
        text = _rule_based_explanation(_base_state(content_type="unreadable"))
        assert "could not be decoded" in text.lower()

    def test_high_risk_url_warns_not_to_visit(self):
        state = _base_state(
            content_type="url",
            risk_level="high",
            findings=[
                {"finding_type": "suspicious_tld", "description": "Bad TLD.", "severity": "high"}
            ],
        )
        text = _rule_based_explanation(state)
        assert "do not" in text.lower() or "don't" in text.lower()

    def test_low_risk_url_gives_verification_advice(self):
        state = _base_state(content_type="url", risk_level="low", findings=[])
        text = _rule_based_explanation(state)
        assert "verify" in text.lower() or "trusted" in text.lower()

    def test_high_risk_text_warns_not_to_respond(self):
        state = _base_state(
            content_type="text",
            risk_level="high",
            findings=[
                {"finding_type": "urgency", "description": "Urgent payment.", "severity": "high"}
            ],
        )
        text = _rule_based_explanation(state)
        assert "do not" in text.lower() or "don't" in text.lower()
