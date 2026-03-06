"""
ECO COMPANY — Upload Router (Admin)
Cloudinary ga fayl yuklash
"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import cloudinary_service
from app.config import settings

logger = logging.getLogger("ecocompany")
router = APIRouter()

ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/webp", "image/gif",
    "image/svg+xml", "image/bmp", "image/tiff",
    "application/pdf",
    "video/mp4", "video/webm",
}
MAX_IMAGE_SIZE = 10 * 1024 * 1024     # 10 MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024    # 100 MB

@router.get("/upload/debug")
def debug_cloudinary():
    return {
        "cloud_name": settings.CLOUDINARY_CLOUD_NAME,
        "api_key": settings.CLOUDINARY_API_KEY,
        "api_secret": settings.CLOUDINARY_API_SECRET[:5] + "..." if settings.CLOUDINARY_API_SECRET else ""
    }

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    folder: str = Query("ecocompany"),
    current_user: User = Depends(get_current_user),
):
    """Fayl yuklash (rasm/video/PDF → Cloudinary)"""

    print(f"[UPLOAD] filename={file.filename}, content_type={file.content_type}, folder={folder}")
    logger.info(f"Upload: filename={file.filename}, content_type={file.content_type}, folder={folder}")

    # Content type tekshirish
    if file.content_type not in ALLOWED_TYPES:
        print(f"DEBUG: Invalid content type: {file.content_type}")
        raise HTTPException(status_code=400, detail=f"Faqat rasm (JPEG/PNG/WEBP/SVG/GIF), PDF yoki MP4 yuklash mumkin! (Keldi: {file.content_type})")

    # Fayl hajmini tekshirish
    contents = await file.read() # Read contents once
    is_video = file.content_type and file.content_type.startswith("video/")
    max_size = MAX_VIDEO_SIZE if is_video else MAX_IMAGE_SIZE # Keep original size logic for now

    print(f"[UPLOAD] size={len(contents)} bytes")

    if len(contents) > max_size: # Use original max_size logic
        size_mb = max_size // (1024 * 1024)
        raise HTTPException(status_code=400, detail=f"Fayl juda katta. Max: {size_mb} MB")

    # Cloudinary ga yuklash
    try:
        # Re-configure on the fly to be safe
        import cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
        )

        print(f"DEBUG: Calling cloudinary_service.upload_bytes with file: {file.filename}")
        result = await cloudinary_service.upload_bytes(
            data=contents,
            folder=folder,
            filename=file.filename or ""
        )
        print(f"DEBUG: Cloudinary upload result: {result}")
    except Exception as e:
        print(f"[UPLOAD] Cloudinary XATO: {e}")
        logger.error(f"Cloudinary upload xatosi: {e}")
        raise HTTPException(status_code=500, detail=f"Cloudinary yuklash xatosi: {str(e)}")

    print(f"[UPLOAD] SUCCESS: url={result.get('url', 'N/A')}")
    return {"success": True, "data": result}


@router.delete("/upload/{public_id:path}")
async def delete_uploaded(
    public_id: str,
    current_user: User = Depends(get_current_user),
):
    """Cloudinary dan faylni o'chirish"""
    deleted = await cloudinary_service.delete_file(public_id)
    if not deleted:
        raise HTTPException(status_code=400, detail="Fayl o'chirilmadi")
    return {"success": True, "message": "Fayl o'chirildi"}
