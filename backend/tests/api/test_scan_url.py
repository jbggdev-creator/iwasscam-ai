import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone


_AGENT_STATE = {
    "url": "https://evil.tk/phish",
    "features": {},
    "risk_score": 75,
    "risk_level": "high",
    "confidence": 0.82,
    "findings": [
        {
            "finding_type": "suspicious_tld",
            "description": "Domain uses a high-risk TLD (.tk).",
            "severity": "high",
        }
    ],
    "explanation": "This URL shows multiple red flags.",
}

_SCAN_ID = uuid4()
_FINDING_ID = uuid4()
_NOW = datetime.now(timezone.utc)


def _mock_scan():
    scan = MagicMock()
    scan.id = _SCAN_ID
    scan.created_at = _NOW
    return scan


def _mock_finding():
    finding = MagicMock()
    finding.id = _FINDING_ID
    finding.finding_type = "suspicious_tld"
    finding.description = "Domain uses a high-risk TLD (.tk)."
    finding.severity = "high"
    return finding


class TestScanUrlEndpoint:
    async def test_returns_200_with_scan_result(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding()

        with patch("app.api.v1.scan.url_graph.ainvoke", AsyncMock(return_value=_AGENT_STATE)):
            with patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)):
                with patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)):
                    with patch("app.api.v1.scan.get_db"):
                        response = await client.post(
                            "/api/v1/scan/url",
                            json={"url": "https://evil.tk/phish"},
                        )

        assert response.status_code == 200
        body = response.json()
        assert body["risk_level"] == "high"
        assert body["confidence_score"] == pytest.approx(0.82)
        assert len(body["findings"]) == 1
        assert body["findings"][0]["finding_type"] == "suspicious_tld"

    async def test_rejects_private_ip_url(self, client):
        response = await client.post(
            "/api/v1/scan/url",
            json={"url": "http://192.168.1.1/admin"},
        )
        assert response.status_code == 422

    async def test_rejects_localhost_url(self, client):
        response = await client.post(
            "/api/v1/scan/url",
            json={"url": "http://localhost:8080/secret"},
        )
        assert response.status_code == 422

    async def test_rejects_empty_url(self, client):
        response = await client.post("/api/v1/scan/url", json={"url": ""})
        assert response.status_code == 422

    async def test_rejects_non_url_string(self, client):
        response = await client.post("/api/v1/scan/url", json={"url": "not-a-url"})
        assert response.status_code == 422

    async def test_agent_failure_returns_500(self, client):
        with patch("app.api.v1.scan.url_graph.ainvoke", AsyncMock(side_effect=RuntimeError("agent crash"))):
            with patch("app.api.v1.scan.get_db"):
                response = await client.post(
                    "/api/v1/scan/url",
                    json={"url": "https://example.com/"},
                )
        assert response.status_code == 500

    async def test_get_scan_not_found(self, client):
        with patch("app.api.v1.scan.scan_repo.get_by_id", AsyncMock(return_value=None)):
            with patch("app.api.v1.scan.get_db"):
                response = await client.get(f"/api/v1/scan/{uuid4()}")
        assert response.status_code == 404
