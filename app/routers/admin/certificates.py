"""
ECO COMPANY — Admin Certificates CRUD
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateCreate, CertificateUpdate, CertificateResponse
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.audit_service import log_action
from app.services import storage_service

router = APIRouter()


@router.get("")
async def list_certificates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    certs = db.query(Certificate).order_by(Certificate.order_index.asc()).all()
    return {"success": True, "data": [CertificateResponse.model_validate(c) for c in certs]}


@router.post("", status_code=201)
async def create_certificate(
    request: Request,
    data: CertificateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = data.model_dump()
    payload["is_active"] = True
    payload["is_downloadable"] = True
    cert = Certificate(**payload)
    db.add(cert)
    db.flush()
    log_action(db, current_user.id, "create", "certificate", cert.id, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(cert)
    return {"success": True, "data": CertificateResponse.model_validate(cert)}


@router.put("/{cert_id}")
async def update_certificate(
    request: Request,
    cert_id: UUID,
    data: CertificateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")

    previous_urls = [cert.file_url, cert.preview_url]
    update_data = data.model_dump(exclude_unset=True)
    update_data["is_active"] = True
    update_data["is_downloadable"] = True
    for key, value in update_data.items():
        setattr(cert, key, value)

    changes_json = data.model_dump(exclude_unset=True, mode='json')
    log_action(db, current_user.id, "update", "certificate", cert.id, changes=changes_json, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(cert)
    await storage_service.delete_files_by_urls(
        [url for url in previous_urls if url and url not in {cert.file_url, cert.preview_url}], db=db
    )
    return {"success": True, "data": CertificateResponse.model_validate(cert)}


@router.delete("/{cert_id}")
async def delete_certificate(
    request: Request,
    cert_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cert = db.query(Certificate).filter(Certificate.id == cert_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Sertifikat topilmadi")

    previous_urls = [cert.file_url, cert.preview_url]
    log_action(db, current_user.id, "delete", "certificate", cert.id, ip_address=request.client.host if request.client else None)
    db.delete(cert)
    db.commit()
    await storage_service.delete_files_by_urls(previous_urls, db=db)
    return {"success": True, "message": "Sertifikat o'chirildi"}
