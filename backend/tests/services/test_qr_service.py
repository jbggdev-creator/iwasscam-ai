import sys
from unittest.mock import MagicMock, patch

import pytest

from app.services.qr_service import decode_qr_from_image


class TestDecodeQrFromImage:
    def test_returns_none_when_pyzbar_not_installed(self):
        with patch.dict(sys.modules, {"pyzbar": None, "pyzbar.pyzbar": None}):
            result = decode_qr_from_image(b"fake-image-bytes")
        assert result is None

    def test_returns_decoded_url_when_qr_found(self):
        mock_pyzbar = MagicMock()
        decoded_obj = MagicMock()
        decoded_obj.data = b"https://example.com"
        mock_pyzbar.decode.return_value = [decoded_obj]

        mock_pil = MagicMock()
        mock_pil.Image.open.return_value = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "pyzbar": MagicMock(),
                "pyzbar.pyzbar": mock_pyzbar,
                "PIL": mock_pil,
                "PIL.Image": mock_pil.Image,
            },
        ):
            result = decode_qr_from_image(b"fake-image-bytes")

        assert result == "https://example.com"

    def test_returns_none_when_no_qr_detected(self):
        mock_pyzbar = MagicMock()
        mock_pyzbar.decode.return_value = []
        mock_pil = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "pyzbar": MagicMock(),
                "pyzbar.pyzbar": mock_pyzbar,
                "PIL": mock_pil,
                "PIL.Image": mock_pil.Image,
            },
        ):
            result = decode_qr_from_image(b"fake-image-bytes")

        assert result is None

    def test_returns_none_on_decode_exception(self):
        mock_pyzbar = MagicMock()
        mock_pyzbar.decode.side_effect = Exception("decode error")
        mock_pil = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "pyzbar": MagicMock(),
                "pyzbar.pyzbar": mock_pyzbar,
                "PIL": mock_pil,
                "PIL.Image": mock_pil.Image,
            },
        ):
            result = decode_qr_from_image(b"fake-image-bytes")

        assert result is None
