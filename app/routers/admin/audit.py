"""
ECO COMPANY — Admin Audit Logs
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit_log import AuditLog
from app.dependencies.auth import get_super_admin
from app.models.user import User
from app.utils.pagination import paginate

router = APIRouter()


@router.get("")
async def list_audit_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    entity_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """Admin harakatlar jurnali (faqat super_admin)"""
    query = db.query(AuditLog)

    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    query = query.order_by(AuditLog.created_at.desc())
    result = paginate(query, page, per_page)

    return {
        "success": True,
        "data": {
            "items": [
                {
                    "id": str(log.id),
                    "user_name": log.user.name if log.user else "Unknown",
                    "action": log.action,
                    "entity_type": log.entity_type,
                    "entity_id": str(log.entity_id),
                    "changes": log.changes,
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in result["items"]
            ],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "pages": result["pages"],
        },
    }
