"""Validate untrusted uploads and discard image metadata before storing."""
from io import BytesIO
from pathlib import Path
import warnings

from PIL import Image, UnidentifiedImageError
from fastapi import HTTPException, UploadFile

MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_VIDEO_SIZE = 100 * 1024 * 1024
IMAGE_FORMATS = {
    "image/jpeg": ("JPEG", {".jpg", ".jpeg"}),
    "image/png": ("PNG", {".png"}),
    "image/webp": ("WEBP", {".webp"}),
    "image/gif": ("GIF", {".gif"}),
    "image/bmp": ("BMP", {".bmp"}),
    "image/tiff": ("TIFF", {".tif", ".tiff"}),
}
OTHER_TYPES = {"application/pdf": ".pdf", "video/mp4": ".mp4", "video/webm": ".webm"}


async def read_upload(file: UploadFile) -> bytes:
    if file.content_type not in IMAGE_FORMATS and file.content_type not in OTHER_TYPES:
        raise HTTPException(400, "Fayl turi qo'llab-quvvatlanmaydi")
    limit = MAX_VIDEO_SIZE if file.content_type.startswith("video/") else MAX_IMAGE_SIZE
    data = bytearray()
    while chunk := await file.read(min(1024 * 1024, limit + 1 - len(data))):
        data.extend(chunk)
        if len(data) > limit:
            raise HTTPException(400, f"Fayl juda katta. Max: {limit // 1024 // 1024} MB")
    return bytes(data)


def validate_upload(data: bytes, filename: str, content_type: str) -> bytes:
    suffix = Path(filename).suffix.lower()
    try:
        if content_type in IMAGE_FORMATS:
            expected, extensions = IMAGE_FORMATS[content_type]
            if suffix not in extensions:
                raise ValueError("Extension does not match image type")
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(BytesIO(data)) as image:
                    if image.format != expected:
                        raise ValueError("Image format does not match MIME type")
                    image.verify()
                with Image.open(BytesIO(data)) as image:
                    frames = getattr(image, "n_frames", 1)
                    if image.width * image.height * frames > 40_000_000:
                        raise ValueError("Image pixel limit exceeded")
                    output = BytesIO()
                    options = {"save_all": True} if expected in {"GIF", "WEBP", "TIFF"} and frames > 1 else {}
                    image.save(output, format=expected, **options)
                    if output.tell() > MAX_IMAGE_SIZE:
                        raise ValueError("Decoded image is too large")
                    return output.getvalue()
        if suffix != OTHER_TYPES.get(content_type):
            raise ValueError("Extension does not match media type")
        valid = (
            content_type == "application/pdf" and data.startswith(b"%PDF-") and b"%%EOF" in data[-1024:]
            or content_type == "video/mp4" and len(data) >= 12 and data[4:8] == b"ftyp"
            or content_type == "video/webm" and data.startswith(b"\x1a\x45\xdf\xa3") and b"webm" in data[:4096]
        )
        if not valid:
            raise ValueError("Invalid media signature")
        return data
    except (ValueError, OSError, SyntaxError, UnidentifiedImageError, Image.DecompressionBombWarning, Image.DecompressionBombError) as exc:
        raise HTTPException(400, "Fayl mazmuni yoki kengaytmasi yaroqsiz") from exc
