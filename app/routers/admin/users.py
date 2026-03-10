"""
ECO COMPANY — Admin Users Management
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.dependencies.auth import get_super_admin
from app.utils.hashing import hash_password
from app.services.audit_service import log_action

router = APIRouter()


@router.get("")
async def list_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    users = db.query(User).all()
    return {"success": True, "data": [UserResponse.model_validate(u) for u in users]}


@router.post("", status_code=201)
async def create_user(
    request: Request,
    data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu email allaqachon mavjud")

    user = User(
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        role=data.role,
        is_active=data.is_active,
    )
    db.add(user)
    db.flush()
    log_action(db, current_user.id, "create", "user", user.id, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(user)
    return {"success": True, "data": UserResponse.model_validate(user)}


@router.put("/{user_id}")
async def update_user(
    request: Request,
    user_id: UUID,
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    update_data = data.model_dump(exclude_unset=True)
    if "email" in update_data:
        existing = db.query(User).filter(
            User.email == update_data["email"], User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=409, detail="Bu email allaqachon mavjud")

    for key, value in update_data.items():
        setattr(user, key, value)

    changes_json = data.model_dump(exclude_unset=True, mode='json')
    log_action(db, current_user.id, "update", "user", user.id, changes=changes_json, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(user)
    return {"success": True, "data": UserResponse.model_validate(user)}


@router.delete("/{user_id}")
async def delete_user(
    request: Request,
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    if str(user_id) == str(current_user.id):
        raise HTTPException(status_code=400, detail="O'zingizni o'chira olmaysiz")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Foydalanuvchi topilmadi")

    log_action(db, current_user.id, "delete", "user", user.id, ip_address=request.client.host if request.client else None)
    db.delete(user)
    db.commit()
    return {"success": True, "message": "Foydalanuvchi o'chirildi"}
