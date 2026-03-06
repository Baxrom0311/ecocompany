"""
ECO COMPANY — Instagram Posts Cache Model
Instagram postlarni keshlab saqlash
"""
from sqlalchemy import Column, String, DateTime
from datetime import datetime, timezone
from app.database import Base
from app.models.base import UUIDMixin


class InstagramPost(Base, UUIDMixin):
    __tablename__ = "instagram_posts"

    instagram_id = Column(String(255), unique=True, index=True, nullable=False)
    media_type = Column(String(50), nullable=False)        # "IMAGE"|"VIDEO"|"CAROUSEL_ALBUM"
    media_url = Column(String(1000), nullable=False)       # To'g'ridan rasm/video URL
    thumbnail_url = Column(String(1000), nullable=True)    # Video uchun cover rasm
    permalink = Column(String(1000), nullable=False)       # Instagram sahifa linki
    caption = Column(String(500), nullable=True)           # Post matni (qisqartirilgan)
    timestamp = Column(DateTime(timezone=True), nullable=False)  # E'lon qilingan vaqt
    cached_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
