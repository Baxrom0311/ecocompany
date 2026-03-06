"""
ECO COMPANY — Admin Instagram Management
Token status, manual refresh, cache refresh
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import instagram_service

router = APIRouter()


@router.post("/refresh")
async def refresh_instagram_cache(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Instagram postlarni qo'lda yangilash"""
    count = await instagram_service.fetch_and_cache_posts(db)
    return {"success": True, "message": f"{count} ta post yangilandi"}


@router.get("/token-status")
async def get_token_status(
    current_user: User = Depends(get_current_user),
):
    """Instagram token holati"""
    status = await instagram_service.get_token_status()
    return {"success": True, "data": status}


@router.post("/refresh-token")
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """Instagram tokenni qo'lda yangilash"""
    result = await instagram_service.refresh_long_lived_token()
    if result:
        return {"success": True, "data": result}
    return {"success": False, "message": "Token yangilanmadi"}
