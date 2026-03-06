"""
ECO COMPANY — Category Schemas
"""
from uuid import UUID
from pydantic import BaseModel


class CategoryBase(BaseModel):
    name_uz: str
    name_ru: str | None = None
    name_en: str | None = None
    slug: str
    icon: str | None = None
    order_index: int = 0
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name_uz: str | None = None
    name_ru: str | None = None
    name_en: str | None = None
    slug: str | None = None
    icon: str | None = None
    order_index: int | None = None
    is_active: bool | None = None


class CategoryResponse(CategoryBase):
    id: UUID

    model_config = {"from_attributes": True}
