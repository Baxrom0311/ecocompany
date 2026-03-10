"""
ECO COMPANY — Gallery Models
Albums + Items tuzilmasi (rasm va video)
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class GalleryAlbum(Base, UUIDMixin, TimestampMixin):
    """Galereya albomi — topic/kategoriya"""
    __tablename__ = "gallery_albums"

    # ── Sarlavhalar (ko'p til) ──
    title_uz = Column(String(500), nullable=False)
    title_ru = Column(String(500), nullable=True)
    title_en = Column(String(500), nullable=True)

    # ── Tavsif ──
    description_uz = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)
    description_en = Column(Text, nullable=True)

    # ── Kategoriya va holat ──
    category = Column(String(50), nullable=True)          # "production"|"office"|"team"|"event"
    cover_item_id = Column(UUID(as_uuid=True), nullable=True)  # Muqova rasm/video ID
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # ── Relationships ──
    items = relationship(
        "GalleryItem",
        back_populates="album",
        cascade="all, delete-orphan",   # Album o'chirilsa items ham
        order_by="GalleryItem.order_index",
        lazy="select",
    )


class GalleryItem(Base, UUIDMixin, TimestampMixin):
    """Albom ichidagi media element (rasm yoki video)"""
    __tablename__ = "gallery_items"

    # ── Album bog'lanish ──
    album_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gallery_albums.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Media ──
    file_url = Column(String(1000), nullable=False)       # Media URL
    file_type = Column(String(20), default="image")       # "image" | "video"
    thumbnail_url = Column(String(1000), nullable=True)   # Video uchun preview rasm
    duration_sec = Column(Integer, nullable=True)          # Video uzunligi (sekund)

    # ── Holat ──
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # ── Relationships ──
    album = relationship("GalleryAlbum", back_populates="items")
