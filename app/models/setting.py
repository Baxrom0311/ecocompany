"""
ECO COMPANY — Site Settings Model
Sayt sozlamalari (key-value)
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime
from datetime import datetime, timezone
from app.database import Base
from app.models.base import UUIDMixin


class SiteSetting(Base, UUIDMixin):
    __tablename__ = "site_settings"

    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    type = Column(String(50), default="text", nullable=False)  # text|image|json|boolean
    label = Column(String(255), nullable=True)                  # UI da ko'rsatish uchun
    is_public = Column(Boolean, default=True, nullable=False)   # False = faqat super_admin
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
