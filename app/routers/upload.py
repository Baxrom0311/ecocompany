"""
ECO COMPANY — Upload Router (Admin)
Media fayllarni server papkasiga yuklash
"""
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Request
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import storage_service

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

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder: str = Query("ecocompany"),
    current_user: User = Depends(get_current_user),
):
    """Fayl yuklash (rasm/video/PDF → local media storage)"""
    logger.info(f"Upload: filename={file.filename}, content_type={file.content_type}, folder={folder}")

    # Content type tekshirish
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Fayl turi qo'llab-quvvatlanmaydi. "
                f"Faqat rasm (JPEG/PNG/WEBP/SVG/GIF), PDF yoki MP4 yuklash mumkin "
                f"(keldi: {file.content_type})"
            ),
        )

    # Fayl hajmini tekshirish
    contents = await file.read() # Read contents once
    is_video = file.content_type and file.content_type.startswith("video/")
    max_size = MAX_VIDEO_SIZE if is_video else MAX_IMAGE_SIZE # Keep original size logic for now

    if len(contents) > max_size: # Use original max_size logic
        size_mb = max_size // (1024 * 1024)
        raise HTTPException(status_code=400, detail=f"Fayl juda katta. Max: {size_mb} MB")

    # Local storage ga yuklash
    try:
        result = await storage_service.upload_bytes(
            data=contents,
            folder=folder,
            filename=file.filename or "",
            base_url=str(request.base_url),
        )
    except Exception as e:
        logger.error(f"Local storage upload xatosi: {e}")
        raise HTTPException(status_code=500, detail=f"Faylni saqlash xatosi: {str(e)}")

    return {"success": True, "data": result}


@router.delete("/upload/{public_id:path}")
async def delete_uploaded(
    public_id: str,
    current_user: User = Depends(get_current_user),
):
    """Serverdagi media faylni o'chirish"""
    deleted = await storage_service.delete_file(public_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fayl topilmadi yoki allaqachon o'chirilgan")
    return {"success": True, "message": "Fayl o'chirildi"}
