"""
ECO COMPANY — Auth Dependencies
JWT tokendan foydalanuvchini aniqlash
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.services.auth_service import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    JWT tokendan joriy foydalanuvchini aniqlash.
    Har bir himoyalangan endpointda ishlatiladi.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token yaroqsiz yoki muddati tugagan",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Token decode
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    import uuid
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception

    try:
        user_uuid = uuid.UUID(user_id_str)
    except (ValueError, TypeError, AttributeError):
        raise credentials_exception

    # DB dan user olish
    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_exception

    if payload.get("token_version") != user.token_version:
        raise credentials_exception

    # Active tekshirish
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Foydalanuvchi bloklangan",
        )

    return user


async def get_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Faqat super_admin ga ruxsat.
    Super admin CRUD operatsiyalari uchun.
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amalni faqat super admin bajara oladi",
        )
    return current_user
