import io
import base64
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from PIL import Image

from app.workers.tasks import scan_url_task, scan_text_task, scan_image_task, scan_qr_task


def _valid_png_b64() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), color=0).save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _mock_scan(input_type: str = "url"):
    s = MagicMock()
    s.id = uuid4()
    s.input_type = input_type
    s.risk_level = "low"
    s.confidence_score = 0.5
    s.explanation = "Test explanation"
    s.findings = []
    s.created_at = MagicMock()
    return s


_URL_STATE = {
    "features": None,
    "risk_score": 10,
    "risk_level": "low",
    "confidence": 0.6,
    "findings": [],
    "explanation": "Domain looks safe.",
}

_TEXT_STATE = {
    "rag_context": [],
    "se_signals": [],
    "se_score": 0,
    "se_confidence": 0.5,
    "risk_score": 20,
    "risk_level": "low",
    "confidence": 0.7,
    "findings": [],
    "explanation": "No scam signals detected.",
}

_IMAGE_STATE = {
    "extracted_text": "",
    "rag_context": [],
    "se_signals": [],
    "se_score": 0,
    "risk_score": 30,
    "risk_level": "medium",
    "confidence": 0.8,
    "findings": [],
    "explanation": "Suspicious screenshot.",
}

_QR_STATE = {
    "decoded_content": "https://example.com",
    "content_type": "url",
    "risk_score": 5,
    "risk_level": "low",
    "confidence": 0.9,
    "findings": [],
    "explanation": "QR links to a known domain.",
}


def test_scan_url_task_returns_scan_id():
    mock_scan = _mock_scan("url")
    with (
        patch("app.agents.url_agent.url_graph.ainvoke", AsyncMock(return_value=_URL_STATE)),
        patch("app.db.repositories.scan_repo.scan_repo.create", AsyncMock(return_value=mock_scan)),
        patch("app.db.repositories.scan_repo.scan_repo.add_finding", AsyncMock(return_value=MagicMock())),
        patch("app.db.session.async_session_factory") as mock_factory,
    ):
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = mock_session

        result = scan_url_task("https://example.com")

    assert result["risk_level"] == "low"
    assert "scan_id" in result


def test_scan_text_task_returns_scan_id():
    mock_scan = _mock_scan("text")
    with (
        patch("app.agents.text_agent.text_graph.ainvoke", AsyncMock(return_value=_TEXT_STATE)),
        patch("app.services.rag_service.rag_service.retrieve", AsyncMock(return_value=[])),
        patch("app.db.repositories.scan_repo.scan_repo.create", AsyncMock(return_value=mock_scan)),
        patch("app.db.repositories.scan_repo.scan_repo.add_finding", AsyncMock(return_value=MagicMock())),
        patch("app.db.session.async_session_factory") as mock_factory,
    ):
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = mock_session

        result = scan_text_task("A recruiter asked me to pay 500 for onboarding.")

    assert result["risk_level"] == "low"
    assert "scan_id" in result


def test_scan_image_task_returns_scan_id():
    mock_scan = _mock_scan("image")
    with (
        patch("app.agents.image_agent.image_graph.ainvoke", AsyncMock(return_value=_IMAGE_STATE)),
        patch("app.services.rag_service.rag_service.retrieve", AsyncMock(return_value=[])),
        patch("app.db.repositories.scan_repo.scan_repo.create", AsyncMock(return_value=mock_scan)),
        patch("app.db.repositories.scan_repo.scan_repo.add_finding", AsyncMock(return_value=MagicMock())),
        patch("app.db.session.async_session_factory") as mock_factory,
    ):
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = mock_session

        result = scan_image_task(_valid_png_b64())

    assert result["risk_level"] == "medium"
    assert "scan_id" in result


def test_scan_qr_task_returns_scan_id():
    mock_scan = _mock_scan("qr")
    with (
        patch("app.agents.qr_agent.qr_graph.ainvoke", AsyncMock(return_value=_QR_STATE)),
        patch("app.db.repositories.scan_repo.scan_repo.create", AsyncMock(return_value=mock_scan)),
        patch("app.db.repositories.scan_repo.scan_repo.add_finding", AsyncMock(return_value=MagicMock())),
        patch("app.db.session.async_session_factory") as mock_factory,
    ):
        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_factory.return_value = mock_session

        result = scan_qr_task(_valid_png_b64())

    assert result["risk_level"] == "low"
    assert "scan_id" in result


def test_scan_url_task_propagates_exception_after_max_retries():
    with (
        patch("app.agents.url_agent.url_graph.ainvoke", AsyncMock(side_effect=RuntimeError("LLM down"))),
        patch.object(scan_url_task, "retry", side_effect=RuntimeError("max retries exceeded")),
    ):
        with pytest.raises(RuntimeError, match="max retries exceeded"):
            scan_url_task.apply(args=["https://evil.com"]).get()
