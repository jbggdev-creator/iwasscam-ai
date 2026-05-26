import io
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

_TEXT_AGENT_STATE = {
    "scenario": "They asked me to pay a registration fee before the job interview.",
    "rag_context": [],
    "se_signals": [
        {
            "finding_type": "upfront_payment_demand",
            "description": "Requests payment before delivering goods or services.",
            "severity": "critical",
        }
    ],
    "se_score": 40,
    "se_confidence": 0.55,
    "risk_score": 40,
    "risk_level": "medium",
    "confidence": 0.65,
    "findings": [
        {
            "finding_type": "upfront_payment_demand",
            "description": "Requests payment before delivering goods or services.",
            "severity": "critical",
        }
    ],
    "explanation": "This looks like a job scam.",
}

_SCAN_ID = uuid4()
_FINDING_ID = uuid4()
_NOW = datetime.now(timezone.utc)


def _mock_scan():
    scan = MagicMock()
    scan.id = _SCAN_ID
    scan.input_type = "text"
    scan.risk_level = "medium"
    scan.confidence_score = 0.65
    scan.explanation = "This looks like a job scam."
    scan.created_at = _NOW
    return scan


def _mock_finding():
    f = MagicMock()
    f.id = _FINDING_ID
    f.finding_type = "upfront_payment_demand"
    f.description = "Requests payment before delivering goods or services."
    f.severity = "critical"
    return f


class TestScanTextEndpoint:
    async def test_returns_200_with_scan_result(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding()

        with patch("app.api.v1.scan.rag_service.retrieve", AsyncMock(return_value=[])):
            with patch("app.api.v1.scan.text_graph.ainvoke", AsyncMock(return_value=_TEXT_AGENT_STATE)):
                with patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)):
                    with patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)):
                        with patch("app.api.v1.scan.get_db"):
                            response = await client.post(
                                "/api/v1/scan/text",
                                json={"scenario": "They asked me to pay a registration fee before the job interview."},
                            )

        assert response.status_code == 200
        body = response.json()
        assert body["risk_level"] == "medium"
        assert body["confidence_score"] == pytest.approx(0.65)
        assert len(body["findings"]) == 1
        assert body["findings"][0]["finding_type"] == "upfront_payment_demand"

    async def test_rag_failure_continues_without_context(self, client):
        mock_scan = _mock_scan()
        mock_finding = _mock_finding()

        with patch("app.api.v1.scan.rag_service.retrieve", AsyncMock(side_effect=RuntimeError("db down"))):
            with patch("app.api.v1.scan.text_graph.ainvoke", AsyncMock(return_value=_TEXT_AGENT_STATE)):
                with patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)):
                    with patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=mock_finding)):
                        with patch("app.api.v1.scan.get_db"):
                            response = await client.post(
                                "/api/v1/scan/text",
                                json={"scenario": "They asked me to pay a registration fee before the job."},
                            )

        assert response.status_code == 200

    async def test_agent_failure_returns_500(self, client):
        with patch("app.api.v1.scan.rag_service.retrieve", AsyncMock(return_value=[])):
            with patch("app.api.v1.scan.text_graph.ainvoke", AsyncMock(side_effect=RuntimeError("agent crash"))):
                with patch("app.api.v1.scan.get_db"):
                    response = await client.post(
                        "/api/v1/scan/text",
                        json={"scenario": "Someone asked me to pay a fee before starting."},
                    )

        assert response.status_code == 500

    async def test_rejects_scenario_too_short(self, client):
        response = await client.post("/api/v1/scan/text", json={"scenario": "hi"})
        assert response.status_code == 422

    async def test_rejects_empty_scenario(self, client):
        response = await client.post("/api/v1/scan/text", json={"scenario": ""})
        assert response.status_code == 422


class TestGetScanEndpoint:
    async def test_returns_existing_scan(self, client):
        mock_scan = _mock_scan()
        mock_scan.findings = [_mock_finding()]

        with patch("app.api.v1.scan.scan_repo.get_by_id", AsyncMock(return_value=mock_scan)):
            with patch("app.api.v1.scan.get_db"):
                response = await client.get(f"/api/v1/scan/{_SCAN_ID}")

        assert response.status_code == 200
        body = response.json()
        assert body["risk_level"] == "medium"
        assert len(body["findings"]) == 1


class TestImageEndpoint:
    async def test_image_rejects_invalid_mime(self, client):
        response = await client.post(
            "/api/v1/scan/image",
            files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")},
        )
        assert response.status_code == 415

    async def test_image_accepts_valid_png_and_returns_scan(self, client):
        import base64
        png_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYGAAAAAEAAH2FzhVAAAAAElFTkSuQmCC"
        )
        response = await client.post(
            "/api/v1/scan/image",
            files={"file": ("test.png", io.BytesIO(png_bytes), "image/png")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["input_type"] == "image"
        assert body["risk_level"] in ("low", "medium", "high", "critical")
        assert "explanation" in body

    async def test_image_rejects_oversized_file(self, client):
        big = io.BytesIO(b"X" * (11 * 1024 * 1024))
        response = await client.post(
            "/api/v1/scan/image",
            files={"file": ("big.png", big, "image/png")},
        )
        assert response.status_code == 413


class TestQrEndpoint:
    async def test_qr_rejects_invalid_mime(self, client):
        response = await client.post(
            "/api/v1/scan/qr",
            files={"file": ("test.txt", io.BytesIO(b"data"), "text/plain")},
        )
        assert response.status_code == 415

    async def test_qr_accepts_valid_png_and_returns_scan(self, client):
        import base64
        png_bytes = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNgYGAAAAAEAAH2FzhVAAAAAElFTkSuQmCC"
        )
        _qr_state = {
            "decoded_content": "https://example.com",
            "content_type": "url",
            "risk_score": 20,
            "risk_level": "low",
            "confidence": 0.7,
            "findings": [],
            "explanation": "QR code links to a known safe domain.",
        }
        mock_scan = _mock_scan()
        mock_scan.input_type = "qr"
        with patch("app.agents.qr_agent.qr_graph.ainvoke", AsyncMock(return_value=_qr_state)):
            with patch("app.api.v1.scan.scan_repo.create", AsyncMock(return_value=mock_scan)):
                with patch("app.api.v1.scan.scan_repo.add_finding", AsyncMock(return_value=MagicMock())):
                    with patch("app.api.v1.scan.get_db"):
                        response = await client.post(
                            "/api/v1/scan/qr",
                            files={"file": ("qr.png", io.BytesIO(png_bytes), "image/png")},
                        )
        assert response.status_code == 200
        body = response.json()
        assert body["input_type"] == "qr"
        assert body["risk_level"] in ("low", "medium", "high", "critical")

    async def test_qr_rejects_oversized_file(self, client):
        big = io.BytesIO(b"X" * (11 * 1024 * 1024))
        response = await client.post(
            "/api/v1/scan/qr",
            files={"file": ("big.png", big, "image/png")},
        )
        assert response.status_code == 413
