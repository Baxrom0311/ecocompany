"""
ECO COMPANY — Cloudinary Service
Rasm va fayl yuklash/o'chirish
"""
import uuid
import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from app.config import settings

# Cloudinary konfiguratsiya
if settings.CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
    )


def _unique_public_id(filename: str = "") -> str:
    """
    Har bir yuklash uchun unikal public_id yaratish.
    Masalan: 'logo.png' → 'logo_a1b2c3d4'
    Bu bir xil nomdagi fayllar ustiga yozilishini to'xtatadi.
    """
    short_uuid = uuid.uuid4().hex[:8]
    if filename:
        name = filename.rsplit(".", 1)[0]  # kengaytmani olib tashlash
        return f"{name}_{short_uuid}"
    return short_uuid


async def upload_file(file: UploadFile, folder: str = "ecocompany") -> dict:
    """
    Faylni Cloudinary ga yuklash.
    Returns: {url, public_id, width, height, format, resource_type}
    """
    contents = await file.read()

    result = cloudinary.uploader.upload(
        contents,
        folder=folder,
        resource_type="auto",
        access_mode="public",
        public_id=_unique_public_id(file.filename or ""),
        quality="auto:good",
        fetch_format="auto",
    )

    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "width": result.get("width"),
        "height": result.get("height"),
        "format": result.get("format"),
        "resource_type": result.get("resource_type"),
        "bytes": result.get("bytes"),
    }


async def upload_bytes(data: bytes, folder: str = "ecocompany", filename: str = "") -> dict:
    """Bytes dan yuklash"""
    result = cloudinary.uploader.upload(
        data,
        folder=folder,
        resource_type="auto",
        access_mode="public",
        public_id=_unique_public_id(filename),
    )
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
    }


async def delete_file(public_id: str) -> bool:
    """Cloudinary dan faylni o'chirish"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get("result") == "ok"
    except Exception:
        return False
