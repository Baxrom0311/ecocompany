"""
ECO COMPANY — Product Schemas
Mahsulot sxemalari (ko'p tilli, chegirmalar)
"""
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, field_validator, computed_field
from typing import Optional


# ── Category (inline) ──
class CategoryInline(BaseModel):
    """Product ichida category ko'rsatish uchun"""
    id: UUID
    name_uz: str
    name_ru: str | None = None
    name_en: str | None = None
    slug: str

    model_config = {"from_attributes": True}


# ── Product ──
class ProductBase(BaseModel):
    name_uz: str
    name_ru: str | None = None
    name_en: str | None = None
    desc_uz: str | None = None
    desc_ru: str | None = None
    desc_en: str | None = None
    original_price: Decimal | None = None
    discount_price: Decimal | None = None
    discount_label: str | None = None
    discount_until: date | None = None
    is_on_sale: bool = False
    images: list[str] = []
    is_featured: bool = False
    is_active: bool = True
    is_new: bool = False
    order_index: int = 0
    category_id: UUID | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    """Barcha maydonlar optional"""
    name_uz: str | None = None
    name_ru: str | None = None
    name_en: str | None = None
    desc_uz: str | None = None
    desc_ru: str | None = None
    desc_en: str | None = None
    original_price: Decimal | None = None
    discount_price: Decimal | None = None
    discount_label: str | None = None
    discount_until: date | None = None
    is_on_sale: bool | None = None
    images: list[str] | None = None
    is_featured: bool | None = None
    is_active: bool | None = None
    is_new: bool | None = None
    order_index: int | None = None
    category_id: UUID | None = None


class ProductResponse(ProductBase):
    id: UUID
    created_at: datetime
    updated_at: datetime | None = None
    category: CategoryInline | None = None

    # Computed fields
    @computed_field
    @property
    def discount_percent(self) -> int | None:
        if self.original_price and self.discount_price and self.original_price > 0:
            return round((1 - float(self.discount_price) / float(self.original_price)) * 100)
        return None

    @computed_field
    @property
    def is_discount_active(self) -> bool:
        if not self.is_on_sale or not self.discount_price:
            return False
        if self.discount_until:
            return date.today() <= self.discount_until
        return True

    model_config = {"from_attributes": True}
