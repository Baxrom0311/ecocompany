"""
ECO COMPANY — Certificate Model
Sertifikatlar (rasm + PDF qo'llab-quvvatlash)
"""
from sqlalchemy import Column, String, Boolean, Integer, Date
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Certificate(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "certificates"

    # ── Sarlavhalar (ko'p til) ──
    title_uz = Column(String(500), nullable=False)
    title_ru = Column(String(500), nullable=True)
    title_en = Column(String(500), nullable=True)

    # ── Fayl ──
    file_url = Column(String(1000), nullable=False)       # Cloudinary URL (rasm YOKI PDF)
    file_type = Column(String(20), default="image")       # "image" | "pdf"
    preview_url = Column(String(1000), nullable=True)     # PDF uchun JPG preview

    # ── Ma'lumot ──
    issued_by = Column(String(255), nullable=True)        # "ISO 9001", "O'z DSt"
    issue_date = Column(Date, nullable=True)
    expiry_date = Column(Date, nullable=True)             # Amal qilish muddati

    # ── Holat ──
    is_active = Column(Boolean, default=True, nullable=False)
    is_downloadable = Column(Boolean, default=False, nullable=False)
    order_index = Column(Integer, default=0, nullable=False)
