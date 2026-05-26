from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.services import clamav_service


@pytest.fixture()
def enabled_settings():
    s = MagicMock()
    s.clamav_enabled = True
    s.clamav_socket = "/var/run/clamav/clamd.ctl"
    s.clamav_host = "localhost"
    s.clamav_port = 3310
    return s


@pytest.fixture()
def disabled_settings():
    s = MagicMock()
    s.clamav_enabled = False
    return s


@pytest.mark.asyncio
async def test_skips_scan_when_disabled(disabled_settings):
    with patch("app.core.config.get_settings", return_value=disabled_settings):
        await clamav_service.scan_bytes(b"data")  # must not raise


@pytest.mark.asyncio
async def test_skips_scan_when_clamd_not_installed(enabled_settings):
    with (
        patch("app.core.config.get_settings", return_value=enabled_settings),
        patch.dict("sys.modules", {"clamd": None}),
    ):
        await clamav_service.scan_bytes(b"data")  # must not raise


@pytest.mark.asyncio
async def test_raises_422_when_malware_found(enabled_settings):
    mock_cd = MagicMock()
    mock_cd.instream.return_value = {"stream": ("FOUND", "Eicar-Test-Signature")}

    with (
        patch("app.core.config.get_settings", return_value=enabled_settings),
        patch.dict("sys.modules", {"clamd": MagicMock()}),
        patch("app.services.clamav_service._connect", return_value=mock_cd),
    ):
        with pytest.raises(HTTPException) as exc_info:
            await clamav_service.scan_bytes(b"malware")

    assert exc_info.value.status_code == 422
    assert "Malware" in exc_info.value.detail


@pytest.mark.asyncio
async def test_allows_clean_file(enabled_settings):
    mock_cd = MagicMock()
    mock_cd.instream.return_value = {"stream": ("OK", None)}

    with (
        patch("app.core.config.get_settings", return_value=enabled_settings),
        patch("app.services.clamav_service._connect", return_value=mock_cd),
        patch.dict("sys.modules", {"clamd": MagicMock()}),
    ):
        await clamav_service.scan_bytes(b"clean data")  # must not raise


@pytest.mark.asyncio
async def test_skips_when_daemon_not_reachable(enabled_settings):
    with (
        patch("app.core.config.get_settings", return_value=enabled_settings),
        patch("app.services.clamav_service._connect", return_value=None),
        patch.dict("sys.modules", {"clamd": MagicMock()}),
    ):
        await clamav_service.scan_bytes(b"data")  # must not raise


@pytest.mark.asyncio
async def test_skips_when_instream_raises(enabled_settings):
    mock_cd = MagicMock()
    mock_cd.instream.side_effect = ConnectionError("daemon gone")

    with (
        patch("app.core.config.get_settings", return_value=enabled_settings),
        patch("app.services.clamav_service._connect", return_value=mock_cd),
        patch.dict("sys.modules", {"clamd": MagicMock()}),
    ):
        await clamav_service.scan_bytes(b"data")  # must not raise
