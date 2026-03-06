"""
ECO COMPANY — Chat Schemas
Public + Admin
"""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


# ── Public ──
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


# ── Admin ──
class ChatSessionResponse(BaseModel):
    """Admin — sessiyalar ro'yxati uchun"""
    id: UUID
    session_id: str
    ip_address: str | None = None
    message_count: int
    last_message_at: datetime | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetail(BaseModel):
    """Admin — bitta sessiya to'liq ma'lumot"""
    id: UUID
    session_id: str
    ip_address: str | None = None
    messages: list[dict]  # [{role, content, timestamp}]
    message_count: int
    last_message_at: datetime | None = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class SystemPromptUpdate(BaseModel):
    """AI system prompt yangilash"""
    prompt: str = Field(..., min_length=10, max_length=5000)
