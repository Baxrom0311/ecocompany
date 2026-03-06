"""
ECO COMPANY — Admin Settings
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.setting import SiteSetting
from app.schemas.setting import SettingResponse, SettingUpdate
from app.dependencies.auth import get_current_user, get_super_admin
from app.models.user import User

router = APIRouter()


@router.get("")
async def list_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Barcha sozlamalar (admin)"""
    settings = db.query(SiteSetting).all()
    return {"success": True, "data": [SettingResponse.model_validate(s) for s in settings]}


@router.put("/bulk")
async def bulk_update_settings(
    items: list[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """Ko'p sozlamani bir vaqtda saqlash (faqat super_admin)"""
    updated = 0
    for item in items:
        key = item.get("key")
        value = item.get("value")
        if not key:
            continue
        setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if setting:
            setting.value = value
        else:
            db.add(SiteSetting(key=key, value=value))
        updated += 1

    db.commit()
    return {"success": True, "message": f"{updated} ta sozlama yangilandi"}


@router.put("/{key}")
async def update_setting(
    key: str,
    data: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """Sozlamani yangilash (faqat super_admin)"""
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not setting:
        # Yangi yaratish
        setting = SiteSetting(key=key, value=data.value)
        db.add(setting)
    else:
        setting.value = data.value

    db.commit()
    db.refresh(setting)
    return {"success": True, "data": SettingResponse.model_validate(setting)}
