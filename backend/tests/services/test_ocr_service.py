import sys
from unittest.mock import MagicMock, patch

from app.services.ocr_service import extract_text_from_image


class TestExtractTextFromImage:
    def test_returns_none_when_pytesseract_not_installed(self):
        with patch.dict(sys.modules, {"pytesseract": None}):
            result = extract_text_from_image(b"fake-image-bytes")
        assert result is None

    def test_returns_extracted_text_when_available(self):
        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.return_value = "Suspicious invoice\n"
        mock_pil = MagicMock()
        mock_pil.Image.open.return_value.convert.return_value = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "pytesseract": mock_pytesseract,
                "PIL": mock_pil,
                "PIL.Image": mock_pil.Image,
            },
        ):
            result = extract_text_from_image(b"fake-image-bytes")

        assert result == "Suspicious invoice"

    def test_returns_none_when_ocr_result_is_blank(self):
        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.return_value = "   \n"
        mock_pil = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "pytesseract": mock_pytesseract,
                "PIL": mock_pil,
                "PIL.Image": mock_pil.Image,
            },
        ):
            result = extract_text_from_image(b"fake-image-bytes")

        assert result is None

    def test_returns_none_on_exception(self):
        mock_pytesseract = MagicMock()
        mock_pytesseract.image_to_string.side_effect = Exception("OCR failure")
        mock_pil = MagicMock()

        with patch.dict(
            sys.modules,
            {
                "pytesseract": mock_pytesseract,
                "PIL": mock_pil,
                "PIL.Image": mock_pil.Image,
            },
        ):
            result = extract_text_from_image(b"fake-image-bytes")

        assert result is None
