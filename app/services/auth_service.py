"""
ECO COMPANY — Auth Service
JWT token yaratish va tekshirish
"""
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.config import settings


def create_access_token(data: dict) -> str:
    """
    JWT token yaratish.
    data = {"sub": str(user.id)} formatida bo'lishi kerak.
    """
    to_encode = data.copy()
    to_encode.setdefault("token_version", 0)
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict | None:
    """
    JWT tokenni tekshirish va decode qilish.
    Muvaffaqiyatli bo'lsa payload qaytaradi, aks holda None.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None
