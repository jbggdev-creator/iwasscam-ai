import pytest
from unittest.mock import patch, AsyncMock

from app.services.url_intelligence import UrlFeatures
from app.agents.url_agent import build_url_graph


def _make_features(**overrides) -> UrlFeatures:
    base = dict(
        url="https://example.com/",
        domain="example",
        tld="com",
        subdomain="",
        scheme="https",
        domain_age_days=365,
        ssl_valid=True,
        redirect_count=0,
        final_url="https://example.com/",
        url_entropy=3.2,
        is_suspicious_tld=False,
        whois_error=False,
    )
    base.update(overrides)
    return UrlFeatures(**base)


_INITIAL_STATE = {
    "url": "https://example.com/",
    "features": None,
    "risk_score": 0,
    "risk_level": "low",
    "confidence": 0.5,
    "findings": [],
    "explanation": "",
}


@pytest.fixture
def graph():
    return build_url_graph()


class TestRiskScoring:
    async def test_clean_url_scores_low(self, graph):
        features = _make_features()
        with patch("app.agents.url_agent.UrlIntelligenceService.analyze", AsyncMock(return_value=features)):
            with patch("app.agents.url_agent._llm_explanation", AsyncMock(return_value="Safe URL.")):
                state = await graph.ainvoke({**_INITIAL_STATE})
        assert state["risk_level"] == "low"
        assert state["risk_score"] < 30

    async def test_very_new_domain_scores_high(self, graph):
        features = _make_features(domain_age_days=2, ssl_valid=False, is_suspicious_tld=True)
        with patch("app.agents.url_agent.UrlIntelligenceService.analyze", AsyncMock(return_value=features)):
            with patch("app.agents.url_agent._llm_explanation", AsyncMock(return_value="Suspicious.")):
                state = await graph.ainvoke({**_INITIAL_STATE, "url": "https://evil.tk/"})
        assert state["risk_level"] in ("high", "critical")
        assert state["risk_score"] >= 60

    async def test_suspicious_tld_adds_finding(self, graph):
        features = _make_features(is_suspicious_tld=True, tld="tk")
        with patch("app.agents.url_agent.UrlIntelligenceService.analyze", AsyncMock(return_value=features)):
            with patch("app.agents.url_agent._llm_explanation", AsyncMock(return_value="Suspicious TLD.")):
                state = await graph.ainvoke({**_INITIAL_STATE, "url": "https://example.tk/"})
        finding_types = [f["finding_type"] for f in state["findings"]]
        assert "suspicious_tld" in finding_types

    async def test_no_ssl_adds_finding(self, graph):
        features = _make_features(ssl_valid=False)
        with patch("app.agents.url_agent.UrlIntelligenceService.analyze", AsyncMock(return_value=features)):
            with patch("app.agents.url_agent._llm_explanation", AsyncMock(return_value="No SSL.")):
                state = await graph.ainvoke({**_INITIAL_STATE, "url": "http://example.com/"})
        finding_types = [f["finding_type"] for f in state["findings"]]
        assert "invalid_ssl" in finding_types

    async def test_explanation_populated(self, graph):
        features = _make_features()
        with patch("app.agents.url_agent.UrlIntelligenceService.analyze", AsyncMock(return_value=features)):
            with patch("app.agents.url_agent._llm_explanation", AsyncMock(return_value="This URL looks safe.")):
                state = await graph.ainvoke({**_INITIAL_STATE})
        assert len(state["explanation"]) > 0

    async def test_score_capped_at_100(self, graph):
        features = _make_features(
            domain_age_days=1,
            ssl_valid=False,
            is_suspicious_tld=True,
            url_entropy=5.5,
            redirect_count=10,
        )
        with patch("app.agents.url_agent.UrlIntelligenceService.analyze", AsyncMock(return_value=features)):
            with patch("app.agents.url_agent._llm_explanation", AsyncMock(return_value="Very suspicious.")):
                state = await graph.ainvoke({**_INITIAL_STATE, "url": "https://evil.tk/abc123"})
        assert state["risk_score"] <= 100
