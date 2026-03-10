"""
ECO COMPANY — Public Instagram Router
Qo'lda kiritilgan Instagram video linklari.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import instagram_service

router = APIRouter()


@router.get("/posts")
async def get_instagram_posts(db: Session = Depends(get_db)):
    """Qo'lda kiritilgan Instagram reel/post linklari"""
    return {
        "success": True,
        "data": instagram_service.get_manual_links(db),
    }
