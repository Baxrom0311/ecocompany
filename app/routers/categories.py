"""
ECO COMPANY — Public Categories Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryResponse

router = APIRouter()


@router.get("")
async def get_categories(db: Session = Depends(get_db)):
    """Barcha aktiv kategoriyalar"""
    categories = (
        db.query(Category)
        .filter(Category.is_active == True)
        .order_by(Category.order_index.asc())
        .all()
    )
    return {
        "success": True,
        "data": [CategoryResponse.model_validate(c) for c in categories],
    }
