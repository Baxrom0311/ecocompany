"""
ECO COMPANY — Upload Router (Admin)
Media fayllarni server papkasiga yuklash
"""
import logging
import asyncio
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.upload_validation import read_upload, validate_upload
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, Request
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import storage_service

logger = logging.getLogger("ecocompany")
router = APIRouter()

@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    folder: str = Query("ecocompany"),
    current_user: User = Depends(get_current_user),
):
    """Fayl yuklash (rasm/video/PDF → local media storage)"""
    logger.info(f"Upload: filename={file.filename}, content_type={file.content_type}, folder={folder}")

    contents = await read_upload(file)
    contents = await asyncio.to_thread(validate_upload, contents, file.filename or "", file.content_type or "")

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
        raise HTTPException(status_code=500, detail="Faylni saqlashda xatolik")

    return {"success": True, "data": result}


@router.delete("/upload/{public_id:path}")
async def delete_uploaded(
    public_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Serverdagi media faylni o'chirish"""
    if storage_service.is_media_referenced(public_id, db):
        raise HTTPException(409, "Fayl hali saytda ishlatilmoqda")
    deleted = await storage_service.delete_file(public_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Fayl topilmadi yoki allaqachon o'chirilgan")
    return {"success": True, "message": "Fayl o'chirildi"}
