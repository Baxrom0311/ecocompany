"""
ECO COMPANY — Public Settings Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.setting import SiteSetting
from app.utils.site_settings import is_excluded_from_public

router = APIRouter()


@router.get("/public")
async def get_public_settings(db: Session = Depends(get_db)):
    """
    Public sozlamalar — dict formatda.
    Response: {"phone_1": "+998...", "logo_url": "https://...", ...}
    """
    settings = db.query(SiteSetting).filter(SiteSetting.is_public == True).all()

    return {
        "success": True,
        "data": {
            s.key: s.value
            for s in settings
            if not is_excluded_from_public(s.key)
        },
    }
