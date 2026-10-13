"""
ECO COMPANY — User Schemas
Auth va admin uchun Pydantic sxemalari
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator


def validate_password_length(value: str) -> str:
    if len(value.encode("utf-8")) > 72:
        raise ValueError("Parol UTF-8 formatida 72 baytdan oshmasligi kerak")
    return value


class UserLogin(BaseModel):
    """Login so'rovi"""
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    """Yangi admin yaratish"""
    email: EmailStr
    password: str
    name: str
    role: str = "editor"
    is_active: bool = True

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        validate_password_length(v)
        if len(v) < 8:
            raise ValueError("Parol kamida 8 ta belgi bo'lishi kerak")
        if not any(c.isdigit() for c in v):
            raise ValueError("Parolda kamida 1 ta raqam bo'lishi kerak")
        if not any(c.isalpha() for c in v):
            raise ValueError("Parolda kamida 1 ta harf bo'lishi kerak")
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ("super_admin", "editor"):
            raise ValueError("Role faqat 'super_admin' yoki 'editor' bo'lishi mumkin")
        return v


class UserUpdate(BaseModel):
    """Admin ma'lumotlarini yangilash"""
    email: EmailStr | None = None
    name: str | None = None
    role: str | None = None
    is_active: bool | None = None

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str | None) -> str | None:
        if v is not None and v not in ("super_admin", "editor"):
            raise ValueError("Role faqat 'super_admin' yoki 'editor' bo'lishi mumkin")
        return v


class UserResponse(BaseModel):
    """User javob sxemasi"""
    id: UUID
    email: str
    name: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Login javob — token + user"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ChangePassword(BaseModel):
    """Parol almashtiresh"""
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        validate_password_length(v)
        if len(v) < 8:
            raise ValueError("Yangi parol kamida 8 ta belgi bo'lishi kerak")
        if not any(c.isdigit() for c in v):
            raise ValueError("Parolda kamida 1 ta raqam bo'lishi kerak")
        if not any(c.isalpha() for c in v):
            raise ValueError("Parolda kamida 1 ta harf bo'lishi kerak")
        return v
