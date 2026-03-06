"""
ECO COMPANY — Audit Log Model
Admin harakatlar jurnali
"""
from sqlalchemy import Column, String, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from app.models.base import UUIDMixin, TimestampMixin


class AuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String(50), nullable=False)          # "create" | "update" | "delete"
    entity_type = Column(String(100), nullable=False)    # "product" | "category" | ...
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    changes = Column(JSON, nullable=True)               # {"field": {"old": x, "new": y}}
    ip_address = Column(String(50), nullable=True)

    # ── Relationships ──
    user = relationship("User", lazy="joined")
