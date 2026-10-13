"""
ECO COMPANY — Public Contact Router
Aloqa formasi (rate limited + email/telegram)
"""
from fastapi import APIRouter, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from app.middleware.rate_limit import limiter
from app.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactCreate
from app.utils.sanitize import sanitize_html
from app.services import email_service, telegram_service

router = APIRouter()


@router.post("")
@limiter.limit("5/hour")
async def create_contact(
    request: Request,
    data: ContactCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Aloqa xabari yuborish (soatiga max 5 ta)"""

    # XSS sanitize
    contact = ContactMessage(
        name=sanitize_html(data.name),
        email=data.email,
        phone=data.phone,
        subject=sanitize_html(data.subject) if data.subject else None,
        message=sanitize_html(data.message),
    )

    db.add(contact)
    db.commit()
    db.refresh(contact)

    # Background da email + telegram
    background_tasks.add_task(email_service.send_contact_notification, contact)
    background_tasks.add_task(email_service.send_contact_confirmation, contact)
    background_tasks.add_task(telegram_service.send_contact_notification, contact)

    return {
        "success": True,
        "message": "Xabaringiz muvaffaqiyatli yuborildi! Tez orada javob beramiz.",
    }
