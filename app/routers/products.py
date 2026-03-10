"""
ECO COMPANY — Public Products Router
Mahsulotlar (public, faqat aktiv)
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.models.category import Category
from app.schemas.product import ProductResponse
from app.utils.pagination import paginate

router = APIRouter()


@router.get("")
async def get_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(12, ge=1, le=100),
    category_id: UUID | None = None,
    is_on_sale: bool | None = None,
    search: str | None = None,
    db: Session = Depends(get_db),
):
    """Barcha aktiv mahsulotlar (pagination bilan)"""
    query = db.query(Product).filter(Product.is_active == True)

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if is_on_sale:
        query = query.filter(Product.is_on_sale == True)
    if search:
        safe_search = search.replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{safe_search}%"
        query = query.filter(
            or_(
                Product.name_uz.ilike(pattern),
                Product.name_ru.ilike(pattern),
                Product.name_en.ilike(pattern),
                Product.desc_uz.ilike(pattern),
                Product.desc_ru.ilike(pattern),
                Product.desc_en.ilike(pattern),
            )
        )

    query = query.order_by(Product.order_index.asc())
    result = paginate(query, page, per_page)

    return {
        "success": True,
        "data": {
            "items": [ProductResponse.model_validate(p) for p in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "pages": result["pages"],
        },
    }


@router.get("/featured")
async def get_featured_products(db: Session = Depends(get_db)):
    """Featured mahsulotlar (max 6)"""
    products = (
        db.query(Product)
        .filter(Product.is_active == True, Product.is_featured == True)
        .order_by(Product.order_index.asc())
        .limit(6)
        .all()
    )
    return {
        "success": True,
        "data": [ProductResponse.model_validate(p) for p in products],
    }


@router.get("/{product_id}")
async def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Bitta mahsulot (ID bo'yicha)"""
    product = (
        db.query(Product)
        .filter(Product.id == product_id, Product.is_active == True)
        .first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    return {
        "success": True,
        "data": ProductResponse.model_validate(product),
    }
