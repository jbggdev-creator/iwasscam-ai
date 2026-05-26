import io

import pytest
from PIL import Image

from app.services.image_sanitizer import ImageSanitizationError, sanitize_image


def _make_png(width: int = 10, height: int = 10, mode: str = "RGB") -> bytes:
    buf = io.BytesIO()
    Image.new(mode, (width, height), color=0).save(buf, format="PNG")
    return buf.getvalue()


def _make_jpeg(width: int = 10, height: int = 10) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=0).save(buf, format="JPEG")
    return buf.getvalue()


def test_returns_bytes_for_valid_rgb_image():
    result = sanitize_image(_make_png())
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_output_is_valid_png():
    result = sanitize_image(_make_png())
    img = Image.open(io.BytesIO(result))
    assert img.format == "PNG"


def test_jpeg_input_converted_to_png():
    result = sanitize_image(_make_jpeg())
    img = Image.open(io.BytesIO(result))
    assert img.format == "PNG"


def test_rgba_image_preserves_alpha_channel():
    result = sanitize_image(_make_png(mode="RGBA"))
    img = Image.open(io.BytesIO(result))
    assert img.mode == "RGBA"


def test_rgb_image_output_mode_is_rgb():
    result = sanitize_image(_make_png(mode="RGB"))
    img = Image.open(io.BytesIO(result))
    assert img.mode == "RGB"


def test_raises_for_invalid_bytes():
    with pytest.raises(ImageSanitizationError, match="not a valid image"):
        sanitize_image(b"this is not an image")


def test_raises_for_oversized_width():
    with pytest.raises(ImageSanitizationError, match="exceed the maximum"):
        sanitize_image(_make_png(width=9000, height=100))


def test_raises_for_oversized_height():
    with pytest.raises(ImageSanitizationError, match="exceed the maximum"):
        sanitize_image(_make_png(width=100, height=9000))


def test_raises_on_decompression_bomb(monkeypatch):
    def _boom(*_a, **_kw):
        raise Image.DecompressionBombError("bomb")

    monkeypatch.setattr(Image, "open", _boom)
    with pytest.raises(ImageSanitizationError, match="decompression bomb"):
        sanitize_image(_make_png())


def test_wraps_unexpected_exception(monkeypatch):
    def _crash(*_a, **_kw):
        raise RuntimeError("unexpected")

    monkeypatch.setattr(Image, "open", _crash)
    with pytest.raises(ImageSanitizationError, match="Image processing failed"):
        sanitize_image(_make_png())
