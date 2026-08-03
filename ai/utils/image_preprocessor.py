"""Image preprocessing utilities before sending to vision AI."""
from __future__ import annotations

from io import BytesIO
from PIL import Image


MAX_DIMENSION = 2048
JPEG_QUALITY = 90


def preprocess_sketch(image_bytes: bytes, mime_type: str = "image/jpeg") -> tuple[bytes, str]:
    """
    Resize image to max 2048px on longest side and normalize to JPEG.
    Returns (processed_bytes, mime_type).
    """
    img = Image.open(BytesIO(image_bytes))

    if img.mode in ("RGBA", "P"):
        bg = Image.new("RGB", img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3] if img.mode == "RGBA" else None)
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > MAX_DIMENSION:
        ratio = MAX_DIMENSION / max(w, h)
        img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)

    buf = BytesIO()
    img.save(buf, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buf.getvalue(), "image/jpeg"
