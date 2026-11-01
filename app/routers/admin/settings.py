"""
ECO COMPANY — Admin Settings
"""
from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.setting import SiteSetting
from app.schemas.setting import SettingBulkUpdate, SettingResponse, SettingUpdate
from app.dependencies.auth import get_current_user, get_super_admin
from app.models.user import User
from app.utils.site_settings import (
    is_env_managed_setting,
    is_non_public_setting,
)

router = APIRouter()


@router.get("")
async def list_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Barcha sozlamalar (admin)"""
    query = db.query(SiteSetting)
    if current_user.role != "super_admin":
        query = query.filter(SiteSetting.is_public == True)

    settings = []
    for setting in query.all():
        if is_env_managed_setting(setting.key):
            continue
        if current_user.role != "super_admin" and is_non_public_setting(setting.key):
            continue
        settings.append(SettingResponse.model_validate(setting))

    return {"success": True, "data": settings}


@router.put("/bulk")
async def bulk_update_settings(
    items: Annotated[list[SettingBulkUpdate], Body(max_length=100)],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """Ko'p sozlamani bir vaqtda saqlash (faqat super_admin)"""
    blocked_keys = sorted(
        {
            item.key
            for item in items
            if is_env_managed_setting(item.key)
        }
    )
    if blocked_keys:
        raise HTTPException(
            status_code=400,
            detail=(
                "Quyidagi sozlamalar `.env` orqali boshqariladi va bu yerda "
                f"saqlanmaydi: {', '.join(blocked_keys)}"
            ),
        )

    updated = 0
    for item in items:
        key = item.key
        value = item.value

        is_public = not is_non_public_setting(key)
        setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if setting:
            setting.value = value
            setting.is_public = is_public
        else:
            db.add(SiteSetting(key=key, value=value, is_public=is_public))
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
    if is_env_managed_setting(key):
        raise HTTPException(
            status_code=400,
            detail=f"`{key}` `.env` orqali boshqariladi va bu endpoint bilan o'zgarmaydi",
        )

    is_public = not is_non_public_setting(key)
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not setting:
        # Yangi yaratish
        setting = SiteSetting(key=key, value=data.value, is_public=is_public)
        db.add(setting)
    else:
        setting.value = data.value
        setting.is_public = is_public

    db.commit()
    db.refresh(setting)
    return {"success": True, "data": SettingResponse.model_validate(setting)}
