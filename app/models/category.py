"""
ECO COMPANY — Category Model
Mahsulot kategoriyalari (ko'p tilli)
"""
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class Category(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "categories"

    name_uz = Column(String(255), nullable=False)
    name_ru = Column(String(255), nullable=True)
    name_en = Column(String(255), nullable=True)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    icon = Column(String(255), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    products = relationship("Product", back_populates="category", lazy="select")
