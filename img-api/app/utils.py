from io import BytesIO

from PIL import Image as PilImage, UnidentifiedImageError

SUPPORTED_FORMATS_MAP = {
    "JPEG": ("image/jpeg", "jpeg"),
    "PNG": ("image/png", "png"),
    "WEBP": ("image/webp", "webp"),
    "GIF": ("image/gif", "gif"),
}


def detect_image_format(data: bytes) -> tuple[str, str, str]:
    """Detect actual image format from bytes via PIL.

    :param data: Raw image bytes.
    :return: Tuple of (pil_format, content_type, extension).
    :raises UnidentifiedImageError: If ``data`` is not a valid image.
    :raises ValueError: If format is not supported.
    """
    with PilImage.open(BytesIO(data)) as img:
        pil_format = img.format
    if pil_format not in SUPPORTED_FORMATS_MAP:
        raise ValueError(f"Unsupported format: {pil_format}")
    content_type, extension = SUPPORTED_FORMATS_MAP[pil_format]
    return pil_format, content_type, extension


def resize_image(
    *, data: bytes, width: int, height: int, img_format: str
) -> tuple[bytes, int, int]:
    """Resize image to fit within (width, height), preserving aspect ratio.

    :param data: Raw image bytes.
    :param width: Maximum output width in pixels.
    :param height: Maximum output height in pixels.
    :param img_format: Pillow format string (e.g. ``JPEG``, ``PNG``).

    :return: Tuple of (resized image bytes, actual width, actual height).
    :raises UnidentifiedImageError: If ``data`` is not a valid image.
    """
    with PilImage.open(BytesIO(data)) as img:
        img.thumbnail((width, height), PilImage.Resampling.LANCZOS)
        act_w, act_h = img.size
        buff = BytesIO()
        img.save(buff, format=img_format)
        return buff.getvalue(), act_w, act_h
