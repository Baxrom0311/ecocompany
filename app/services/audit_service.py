"""
ECO COMPANY — Audit Service
Admin harakatlarni qayd qilish
"""
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog


def log_action(
    db: Session,
    user_id: UUID,
    action: str,
    entity_type: str,
    entity_id: UUID,
    changes: dict | None = None,
    ip_address: str | None = None,
) -> None:
    """Admin harakatini audit log ga yozish"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        changes=changes,
        ip_address=ip_address,
    )
    db.add(log)
    # commit chaqiruvchida qilinadi
