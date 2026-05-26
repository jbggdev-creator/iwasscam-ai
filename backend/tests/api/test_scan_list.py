from datetime import datetime, timezone
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest


_SCAN_ID = uuid4()
_FINDING_ID = uuid4()
_NOW = datetime.now(timezone.utc)


def _mock_scan():
    scan = MagicMock()
    scan.id = _SCAN_ID
    scan.input_type = "url"
    scan.risk_level = "high"
    scan.confidence_score = 0.82
    scan.explanation = "This URL shows multiple red flags."
    scan.created_at = _NOW

    finding = MagicMock()
    finding.id = _FINDING_ID
    finding.finding_type = "suspicious_tld"
    finding.description = "Domain uses a high-risk TLD."
    finding.severity = "high"
    scan.findings = [finding]

    return scan


class TestListScansEndpoint:
    async def test_returns_200_with_scan_list(self, client):
        mock_scan = _mock_scan()

        with patch(
            "app.api.v1.scan.scan_repo.list_recent",
            new_callable=AsyncMock,
            return_value=[mock_scan],
        ):
            response = await client.get("/api/v1/scan")

        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 1
        assert body["limit"] == 20
        assert len(body["scans"]) == 1

        scan = body["scans"][0]
        assert scan["id"] == str(_SCAN_ID)
        assert scan["risk_level"] == "high"
        assert scan["input_type"] == "url"
        assert scan["confidence_score"] == pytest.approx(0.82)
        assert len(scan["findings"]) == 1

    async def test_returns_empty_list_when_no_scans(self, client):
        with patch(
            "app.api.v1.scan.scan_repo.list_recent",
            new_callable=AsyncMock,
            return_value=[],
        ):
            response = await client.get("/api/v1/scan")

        assert response.status_code == 200
        body = response.json()
        assert body["scans"] == []
        assert body["page"] == 1

    async def test_respects_page_and_limit_params(self, client):
        with patch(
            "app.api.v1.scan.scan_repo.list_recent",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_list:
            response = await client.get("/api/v1/scan?page=2&limit=5")

        assert response.status_code == 200
        body = response.json()
        assert body["page"] == 2
        assert body["limit"] == 5
        mock_list.assert_awaited_once_with(
            ANY, limit=5, offset=5
        )

    async def test_caps_limit_at_100(self, client):
        with patch(
            "app.api.v1.scan.scan_repo.list_recent",
            new_callable=AsyncMock,
            return_value=[],
        ) as mock_list:
            response = await client.get("/api/v1/scan?limit=999")

        assert response.status_code == 200
        mock_list.assert_awaited_once_with(
            ANY, limit=100, offset=0
        )
