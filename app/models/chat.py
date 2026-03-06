"""
ECO COMPANY — Chat Session Model
AI chatbot sessiyalari (Chatabase)
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON
from datetime import datetime, timezone
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class ChatSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_sessions"

    session_id = Column(String(255), unique=True, index=True, nullable=False)
    messages = Column(JSON, default=list, nullable=False)  # [{role, content, timestamp}]
    ip_address = Column(String(50), nullable=True)
    message_count = Column(Integer, default=0, nullable=False)
    last_message_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    is_active = Column(Boolean, default=True, nullable=False)
