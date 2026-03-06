"""
ECO COMPANY — Admin Contacts
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactResponse, ContactUpdate
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.utils.pagination import paginate

router = APIRouter()


@router.get("")
async def list_contacts(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_read: bool | None = None,
    is_archived: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(ContactMessage)
    if is_read is not None:
        query = query.filter(ContactMessage.is_read == is_read)
    if is_archived is not None:
        query = query.filter(ContactMessage.is_archived == is_archived)

    query = query.order_by(ContactMessage.created_at.desc())
    result = paginate(query, page, per_page)

    return {
        "success": True,
        "data": {
            "items": [ContactResponse.model_validate(c) for c in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "pages": result["pages"],
        },
    }


@router.get("/unread-count")
async def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """O'qilmagan xabarlar soni (admin badge uchun)"""
    count = db.query(ContactMessage).filter(ContactMessage.is_read == False).count()
    return {"success": True, "data": {"count": count}}


@router.get("/{contact_id}")
async def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bitta xabar (avtomatik o'qildi deb belgilanadi)"""
    contact = db.query(ContactMessage).filter(ContactMessage.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")

    if not contact.is_read:
        contact.is_read = True
        db.commit()
        db.refresh(contact)

    return {"success": True, "data": ContactResponse.model_validate(contact)}


@router.patch("/{contact_id}")
async def update_contact(
    contact_id: UUID,
    data: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.query(ContactMessage).filter(ContactMessage.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return {"success": True, "data": ContactResponse.model_validate(contact)}


@router.delete("/{contact_id}")
async def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    contact = db.query(ContactMessage).filter(ContactMessage.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Xabar topilmadi")

    db.delete(contact)
    db.commit()
    return {"success": True, "message": "Xabar o'chirildi"}
