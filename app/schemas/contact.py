"""
ECO COMPANY — Contact Schemas
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class ContactCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    subject: str | None = Field(default=None, max_length=500)
    message: str = Field(..., min_length=10, max_length=2000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 2 or len(v) > 100:
            raise ValueError("Ism 2 dan 100 belgigacha bo'lishi kerak")
        return v

    @field_validator("phone", "subject")
    @classmethod
    def trim_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 10 or len(v) > 2000:
            raise ValueError("Xabar 10 dan 2000 belgigacha bo'lishi kerak")
        return v

    @model_validator(mode="after")
    def check_contact_info(self):
        if not self.email and not self.phone:
            raise ValueError("Email yoki telefon raqam kiritilishi shart")
        return self


class ContactResponse(BaseModel):
    id: UUID
    name: str
    email: str | None = None
    phone: str | None = None
    subject: str | None = None
    message: str
    is_read: bool
    is_archived: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ContactUpdate(BaseModel):
    is_read: bool | None = None
    is_archived: bool | None = None
