import logging

logger = logging.getLogger(__name__)


def decode_qr_from_image(image_bytes: bytes) -> str | None:
    """Decode a QR code from image bytes using pyzbar.

    Returns the decoded UTF-8 string, or None if unavailable (library missing,
    no QR detected, or decode error).
    """
    try:
        from pyzbar.pyzbar import decode
        from PIL import Image
        import io
    except ImportError:
        logger.warning("pyzbar or Pillow not installed — QR decoding unavailable")
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
        decoded_objects = decode(image)
        if not decoded_objects:
            return None
        return decoded_objects[0].data.decode("utf-8")
    except Exception as exc:
        logger.warning("QR decoding failed: %s", exc)
        return None
