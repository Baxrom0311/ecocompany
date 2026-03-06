"""
ECO COMPANY — Product Model
Mahsulotlar (ko'p tilli, chegirmalar bilan)
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, Numeric, Date, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Product(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "products"

    # ── Category ──
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)

    # ── Nomlar (ko'p til) ──
    name_uz = Column(String(500), nullable=False)
    name_ru = Column(String(500), nullable=True)
    name_en = Column(String(500), nullable=True)

    # ── Tavsiflar ──
    desc_uz = Column(Text, nullable=True)
    desc_ru = Column(Text, nullable=True)
    desc_en = Column(Text, nullable=True)

    # ── Narx va Chegirma ──
    original_price = Column(Numeric(10, 2), nullable=True)
    discount_price = Column(Numeric(10, 2), nullable=True)      # NULL = chegirma yo'q
    discount_label = Column(String(100), nullable=True)          # "20% OFF" | "Aksiya"
    discount_until = Column(Date, nullable=True)                 # NULL = muddatsiz
    is_on_sale = Column(Boolean, default=False, nullable=False)  # Tez filtrlash

    # ── Media ──
    images = Column(JSON, default=list, nullable=False)  # Cloudinary URLs ["url1", "url2"]

    # ── Holat ──
    is_featured = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_new = Column(Boolean, default=False, nullable=False)       # "Yangi" badge
    order_index = Column(Integer, default=0, nullable=False)

    # ── Relationships ──
    category = relationship("Category", back_populates="products", lazy="joined")
