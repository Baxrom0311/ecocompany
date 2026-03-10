"""
ECO COMPANY — Certificate Model
Sertifikatlar (media fayllar)
"""
from sqlalchemy import Column, String, Boolean, Integer
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Certificate(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "certificates"

    # ── Sarlavhalar (ko'p til) ──
    title_uz = Column(String(500), nullable=False)
    title_ru = Column(String(500), nullable=True)
    title_en = Column(String(500), nullable=True)

    # ── Fayl ──
    file_url = Column(String(1000), nullable=False)       # Media URL
    file_type = Column(String(20), default="image")       # "image" | "pdf"
    preview_url = Column(String(1000), nullable=True)     # PDF uchun JPG preview

    # ── Ma'lumot ──
    issued_by = Column(String(255), nullable=True)        # Qo'shimcha izoh / beruvchi

    # ── Holat ──
    is_active = Column(Boolean, default=True, nullable=False)
    is_downloadable = Column(Boolean, default=True, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
