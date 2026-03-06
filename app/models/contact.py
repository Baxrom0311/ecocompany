"""
ECO COMPANY — Contact Message Model
Saytdan kelgan xabarlar
"""
from sqlalchemy import Column, String, Text, Boolean
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class ContactMessage(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "contact_messages"

    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    subject = Column(String(500), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    is_archived = Column(Boolean, default=False, nullable=False)
