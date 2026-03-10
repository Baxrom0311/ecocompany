"""
ECO COMPANY — Admin Instagram Management
Instagram videolarini qo'lda link bilan boshqarish
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import instagram_service
from app.schemas.instagram import InstagramLinksUpdate

router = APIRouter()


@router.get("/token-status")
async def get_token_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Instagram qo'lda boshqarish holati"""
    status = instagram_service.get_manual_status(db)
    return {"success": True, "data": status}


@router.get("/links")
async def get_instagram_links(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Instagram video linklari"""
    return {"success": True, "data": instagram_service.get_manual_links(db)}


@router.put("/links")
async def update_instagram_links(
    data: InstagramLinksUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Instagram video linklarini saqlash"""
    try:
        links = instagram_service.save_manual_links(
            db,
            [item.model_dump() for item in data.items],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {
        "success": True,
        "message": f"{len(links)} ta Instagram video linki saqlandi",
        "data": links,
    }


@router.post("/refresh")
async def refresh_instagram_cache(current_user: User = Depends(get_current_user)):
    """Legacy endpoint — Instagram API ishlatilmaydi"""
    return {
        "success": True,
        "message": "Instagram API integratsiyasi o'chirilgan. Videolar qo'lda link orqali boshqariladi.",
    }


@router.post("/refresh-token")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Legacy endpoint — Instagram token ishlatilmaydi"""
    return {
        "success": True,
        "message": "Instagram token yangilash o'chirilgan. Videolar qo'lda link orqali boshqariladi.",
    }
