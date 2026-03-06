"""
ECO COMPANY — Certificate Schemas
"""
from datetime import datetime, date
from uuid import UUID
from pydantic import BaseModel


class CertificateBase(BaseModel):
    title_uz: str
    title_ru: str | None = None
    title_en: str | None = None
    file_url: str
    file_type: str = "image"
    preview_url: str | None = None
    issued_by: str | None = None
    issue_date: date | None = None
    expiry_date: date | None = None
    is_active: bool = True
    is_downloadable: bool = False
    order_index: int = 0


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
    issue_date: date | None = None
    expiry_date: date | None = None
    is_active: bool | None = None
    is_downloadable: bool | None = None
    order_index: int | None = None


class CertificateResponse(CertificateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
