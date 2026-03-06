"""
ECO COMPANY — Auth Router
Login, me, logout endpointlari
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserLogin, UserResponse, TokenResponse, ChangePassword,
)
from app.services.auth_service import create_access_token
from app.utils.hashing import verify_password, hash_password
from app.dependencies.auth import get_current_user

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: Session = Depends(get_db)):
    """Admin login — email + password → JWT token"""

    # 1. Email bo'yicha user topish
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri",
        )

    # 2. Parol tekshirish
    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email yoki parol noto'g'ri",
        )

    # 3. Active tekshirish
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi bloklangan",
        )

    # 4. Token yaratish
    access_token = create_access_token({"sub": str(user.id)})

    return TokenResponse(
        access_token=access_token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Joriy foydalanuvchi ma'lumotlarini olish"""
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout — stateless JWT.
    Frontend token o'zi o'chiradi, backend tarafda hech narsa qilish kerak emas.
    """
    return {"success": True, "message": "Muvaffaqiyatli chiqildi"}


@router.post("/change-password")
async def change_password(
    data: ChangePassword,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Parolni almashtiresh"""

    # Joriy parolni tekshirish
    if not verify_password(data.current_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Joriy parol noto'g'ri",
        )

    # Yangi parolni saqlash
    current_user.password = hash_password(data.new_password)
    db.commit()

    return {"success": True, "message": "Parol muvaffaqiyatli o'zgartirildi"}
