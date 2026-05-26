import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

_AGENT_STATE_URL = {
    "image_bytes": b"",
    "decoded_content": "https://evil.tk/pay",
    "content_type": "url",
    "risk_score": 75,
    "risk_level": "high",
    "confidence": 0.82,
    "findings": [
        {
            "finding_type": "suspicious_tld",
            "description": "Domain uses a high-risk TLD (.tk).",
            "severity": "high",
        },
        {
            "finding_type": "qr_encoded_url",
            "description": "QR code contains URL: https://evil.tk/pay",
            "severity": "medium",
        },
    ],
    "explanation": "This QR code encodes a suspicious URL with a high-risk domain.",
}

_AGENT_STATE_UNREADABLE = {
    "image_bytes": b"",
    "decoded_content": "",
    "content_type": "unreadable",
    "risk_score": 0,
    "risk_level": "low",
    "confidence": 0.5,
    "findings": [
        {
            "finding_type": "qr_unreadable",
            "description": "Could not decode the QR code.",
            "severity": "low",
        }
    ],
    "explanation": "The QR code could not be decoded from the provided image.",
}

_SCAN_ID = uuid4()
_FINDING_ID = uuid4()
_NOW = datetime.now(timezone.utc)

_FAKE_PNG = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
    b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
    b"\x00\x0cIDATx\x9cc\xf8\x0f\x00\x00\x01\x01\x00\x05\x18"
    b"\xd8N\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _mock_scan():
    scan = MagicMock()
    scan.id = _SCAN_ID
    scan.created_at = _NOW
    return scan


def _mock_finding(finding_type="suspicious_tld"):
    finding = MagicMock()
    finding.id = _FINDING_ID
    finding.finding_type = finding_type
    finding.description = "Domain uses a high-risk TLD (.tk)."
    finding.severity = "high"
    return finding


def _mock_qr_graph(state):
    return MagicMock(ainvoke=AsyncMock(return_value=state))


class TestScanQrEndpoint:
    async def test_returns_200_for_malicious_url_qr(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding()

        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch("app.services.image_sanitizer.sanitize_image", return_value=_FAKE_PNG),
            patch("app.agents.qr_agent.qr_graph", _mock_qr_graph(_AGENT_STATE_URL)),
            patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)),
            patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)),
        ):
            response = await client.post(
                "/api/v1/scan/qr",
                files={"file": ("qr.png", _FAKE_PNG, "image/png")},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["risk_level"] == "high"
        assert body["confidence_score"] == 0.82
        assert len(body["findings"]) == 2

    async def test_returns_200_for_unreadable_qr(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding("qr_unreadable")

        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch("app.services.image_sanitizer.sanitize_image", return_value=_FAKE_PNG),
            patch("app.agents.qr_agent.qr_graph", _mock_qr_graph(_AGENT_STATE_UNREADABLE)),
            patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)),
            patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)),
        ):
            response = await client.post(
                "/api/v1/scan/qr",
                files={"file": ("blurry.png", _FAKE_PNG, "image/png")},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["risk_level"] == "low"

    async def test_rejects_unsupported_mime_type(self, client):
        response = await client.post(
            "/api/v1/scan/qr",
            files={"file": ("doc.pdf", b"%PDF-fake", "application/pdf")},
        )
        assert response.status_code == 415

    async def test_rejects_oversized_file(self, client):
        big_bytes = b"X" * (11 * 1024 * 1024)
        response = await client.post(
            "/api/v1/scan/qr",
            files={"file": ("big.png", big_bytes, "image/png")},
        )
        assert response.status_code == 413

    async def test_returns_422_on_sanitization_failure(self, client):
        from app.services.image_sanitizer import ImageSanitizationError

        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch(
                "app.services.image_sanitizer.sanitize_image",
                side_effect=ImageSanitizationError("Invalid image"),
            ),
        ):
            response = await client.post(
                "/api/v1/scan/qr",
                files={"file": ("bad.png", _FAKE_PNG, "image/png")},
            )
        assert response.status_code == 422

    async def test_returns_500_on_agent_failure(self, client):
        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch("app.services.image_sanitizer.sanitize_image", return_value=_FAKE_PNG),
            patch(
                "app.agents.qr_agent.qr_graph",
                MagicMock(ainvoke=AsyncMock(side_effect=RuntimeError("graph error"))),
            ),
        ):
            response = await client.post(
                "/api/v1/scan/qr",
                files={"file": ("qr.png", _FAKE_PNG, "image/png")},
            )
        assert response.status_code == 500
