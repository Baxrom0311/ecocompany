"""
ECO COMPANY — Gallery Schemas
Album + Item sxemalari
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


# ── Gallery Item ──
class GalleryItemBase(BaseModel):
    file_url: str
    file_type: str = "image"
    thumbnail_url: str | None = None
    duration_sec: int | None = None
    order_index: int = 0
    is_active: bool = True


class GalleryItemCreate(GalleryItemBase):
    pass


class GalleryItemUpdate(BaseModel):
    file_url: str | None = None
    file_type: str | None = None
    thumbnail_url: str | None = None
    duration_sec: int | None = None
    order_index: int | None = None
    is_active: bool | None = None


class GalleryItemResponse(GalleryItemBase):
    id: UUID
    album_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Gallery Album ──
class GalleryAlbumBase(BaseModel):
    title_uz: str
    title_ru: str | None = None
    title_en: str | None = None
    description_uz: str | None = None
    description_ru: str | None = None
    description_en: str | None = None
    category: str | None = None
    cover_item_id: UUID | None = None
    order_index: int = 0
    is_active: bool = True


class GalleryAlbumCreate(GalleryAlbumBase):
    pass


class GalleryAlbumUpdate(BaseModel):
    title_uz: str | None = None
    title_ru: str | None = None
    title_en: str | None = None
    description_uz: str | None = None
    description_ru: str | None = None
    description_en: str | None = None
    category: str | None = None
    cover_item_id: UUID | None = None
    order_index: int | None = None
    is_active: bool | None = None


class GalleryAlbumResponse(GalleryAlbumBase):
    id: UUID
    created_at: datetime
    items: list[GalleryItemResponse] = []

    model_config = {"from_attributes": True}


class GalleryAlbumListResponse(GalleryAlbumBase):
    """Albumlar ro'yxati (items siz, tezroq)"""
    id: UUID
    created_at: datetime
    items_count: int = 0
    cover_url: str | None = None
    cover_thumbnail_url: str | None = None
    cover_file_type: str | None = None
    preview_items: list[GalleryItemResponse] = []

    model_config = {"from_attributes": True}
