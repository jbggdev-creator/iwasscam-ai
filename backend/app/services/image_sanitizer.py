import io
import logging

from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

_MAX_DIMENSION = 8000


class ImageSanitizationError(ValueError):
    pass


def sanitize_image(raw: bytes) -> bytes:
    """Re-encode image bytes through Pillow to strip EXIF, metadata, and polyglot payloads.

    Raises ImageSanitizationError if the bytes are not a valid image or exceed
    safe dimension limits (decompression bomb guard).
    """
    try:
        with Image.open(io.BytesIO(raw)) as img:
            width, height = img.size
            if width > _MAX_DIMENSION or height > _MAX_DIMENSION:
                raise ImageSanitizationError(
                    f"Image dimensions {width}x{height} exceed the maximum allowed {_MAX_DIMENSION}px."
                )

            # Convert to RGB or RGBA — new object carries no EXIF or source metadata
            mode = "RGBA" if img.mode in ("RGBA", "LA", "PA") else "RGB"
            clean = img.convert(mode)

    except Image.DecompressionBombError as exc:
        raise ImageSanitizationError("Image rejected: decompression bomb detected.") from exc
    except UnidentifiedImageError as exc:
        raise ImageSanitizationError("Uploaded file is not a valid image.") from exc
    except ImageSanitizationError:
        raise
    except Exception as exc:
        raise ImageSanitizationError(f"Image processing failed: {exc}") from exc

    # Save to a fresh buffer — no info/metadata carried over from the source image
    out = io.BytesIO()
    clean.save(out, format="PNG")
    sanitized = out.getvalue()

    logger.debug(
        "Image sanitized: original=%d bytes → sanitized=%d bytes mode=%s",
        len(raw),
        len(sanitized),
        mode,
    )
    return sanitized
