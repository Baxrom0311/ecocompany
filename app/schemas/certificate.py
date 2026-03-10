"""
ECO COMPANY — Certificate Schemas
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, field_validator


class CertificateBase(BaseModel):
    title_uz: str
    title_ru: str | None = None
    title_en: str | None = None
    file_url: str
    file_type: str = "image"
    preview_url: str | None = None
    issued_by: str | None = None
    is_active: bool = True
    is_downloadable: bool = True
    order_index: int = 0

    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, value: str) -> str:
        if value != "image":
            raise ValueError("Faqat rasm sertifikatlar qo'llab-quvvatlanadi")
        return value


class CertificateCreate(CertificateBase):
    pass


class CertificateUpdate(BaseModel):
    title_uz: str | None = None
    title_ru: str | None = None
    title_en: str | None = None
    file_url: str | None = None
    file_type: str | None = None
    preview_url: str | None = None
    issued_by: str | None = None
    is_active: bool | None = None
    is_downloadable: bool | None = None
    order_index: int | None = None

    @field_validator("file_type")
    @classmethod
    def validate_file_type(cls, value: str | None) -> str | None:
        if value is not None and value != "image":
            raise ValueError("Faqat rasm sertifikatlar qo'llab-quvvatlanadi")
        return value


class CertificateResponse(CertificateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
