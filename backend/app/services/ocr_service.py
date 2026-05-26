import logging

logger = logging.getLogger(__name__)


def extract_text_from_image(image_bytes: bytes) -> str | None:
    """Extract text from image bytes using pytesseract.

    Returns stripped text, or None if unavailable (library missing, blank result).
    Converts image to RGB before OCR to handle RGBA/P modes gracefully.
    """
    try:
        import pytesseract
        from PIL import Image
        import io
    except ImportError:
        logger.warning("pytesseract or Pillow not installed — OCR unavailable")
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        text: str = pytesseract.image_to_string(image)
        stripped = text.strip()
        return stripped if stripped else None
    except Exception as exc:
        logger.warning("OCR extraction failed: %s", exc)
        return None
