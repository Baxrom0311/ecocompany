"""
ECO COMPANY — Public Certificates Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.certificate import Certificate
from app.schemas.certificate import CertificateResponse

router = APIRouter()


@router.get("")
async def get_certificates(db: Session = Depends(get_db)):
    """Barcha sertifikatlar"""
    certs = (
        db.query(Certificate)
        .order_by(Certificate.order_index.asc())
        .all()
    )
    return {
        "success": True,
        "data": [CertificateResponse.model_validate(c) for c in certs],
    }
