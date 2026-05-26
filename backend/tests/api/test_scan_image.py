import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from uuid import uuid4
from datetime import datetime, timezone

_AGENT_STATE = {
    "image_bytes": b"",
    "extracted_text": "GCash receipt ₱500 reference no 123",
    "rag_context": [],
    "se_signals": [],
    "se_score": 25,
    "risk_score": 25,
    "risk_level": "medium",
    "confidence": 0.65,
    "findings": [
        {
            "finding_type": "fake_receipt_pattern",
            "description": "Image contains GCash receipt-like content.",
            "severity": "high",
        }
    ],
    "explanation": "This image shows a suspicious GCash receipt pattern.",
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


def _mock_finding():
    finding = MagicMock()
    finding.id = _FINDING_ID
    finding.finding_type = "fake_receipt_pattern"
    finding.description = "Image contains GCash receipt-like content."
    finding.severity = "high"
    return finding


def _mock_image_graph(state=_AGENT_STATE):
    return MagicMock(ainvoke=AsyncMock(return_value=state))


class TestScanImageEndpoint:
    async def test_returns_200_with_scan_result(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding()

        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch("app.services.image_sanitizer.sanitize_image", return_value=_FAKE_PNG),
            patch("app.agents.image_agent.image_graph", _mock_image_graph()),
            patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)),
            patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)),
            patch("app.api.v1.scan.rag_service.retrieve", AsyncMock(return_value=[])),
        ):
            response = await client.post(
                "/api/v1/scan/image",
                files={"file": ("receipt.png", _FAKE_PNG, "image/png")},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["risk_level"] == "medium"
        assert body["confidence_score"] == 0.65
        assert len(body["findings"]) == 1
        assert body["findings"][0]["finding_type"] == "fake_receipt_pattern"

    async def test_rejects_unsupported_mime_type(self, client):
        response = await client.post(
            "/api/v1/scan/image",
            files={"file": ("doc.pdf", b"%PDF-fake", "application/pdf")},
        )
        assert response.status_code == 415

    async def test_rejects_oversized_file(self, client):
        big_bytes = b"X" * (11 * 1024 * 1024)
        response = await client.post(
            "/api/v1/scan/image",
            files={"file": ("big.png", big_bytes, "image/png")},
        )
        assert response.status_code == 413

    async def test_returns_422_on_malware_detected(self, client):
        from fastapi import HTTPException, status as http_status

        with patch(
            "app.services.clamav_service.scan_bytes",
            AsyncMock(
                side_effect=HTTPException(
                    status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Malware detected in uploaded file",
                )
            ),
        ):
            response = await client.post(
                "/api/v1/scan/image",
                files={"file": ("evil.png", _FAKE_PNG, "image/png")},
            )
        assert response.status_code == 422

    async def test_returns_422_on_sanitization_failure(self, client):
        from app.services.image_sanitizer import ImageSanitizationError

        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch(
                "app.services.image_sanitizer.sanitize_image",
                side_effect=ImageSanitizationError("Decompression bomb"),
            ),
        ):
            response = await client.post(
                "/api/v1/scan/image",
                files={"file": ("bomb.png", _FAKE_PNG, "image/png")},
            )
        assert response.status_code == 422

    async def test_returns_500_on_agent_failure(self, client):
        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch("app.services.image_sanitizer.sanitize_image", return_value=_FAKE_PNG),
            patch("app.api.v1.scan.rag_service.retrieve", AsyncMock(return_value=[])),
            patch(
                "app.agents.image_agent.image_graph",
                MagicMock(ainvoke=AsyncMock(side_effect=RuntimeError("model unavailable"))),
            ),
        ):
            response = await client.post(
                "/api/v1/scan/image",
                files={"file": ("receipt.png", _FAKE_PNG, "image/png")},
            )
        assert response.status_code == 500

    async def test_proceeds_when_rag_retrieval_fails(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding()

        with (
            patch("app.services.clamav_service.scan_bytes", AsyncMock()),
            patch("app.services.image_sanitizer.sanitize_image", return_value=_FAKE_PNG),
            patch(
                "app.api.v1.scan.rag_service.retrieve",
                AsyncMock(side_effect=Exception("pgvector down")),
            ),
            patch("app.agents.image_agent.image_graph", _mock_image_graph()),
            patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)),
            patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)),
        ):
            response = await client.post(
                "/api/v1/scan/image",
                files={"file": ("receipt.png", _FAKE_PNG, "image/png")},
            )

        assert response.status_code == 200
