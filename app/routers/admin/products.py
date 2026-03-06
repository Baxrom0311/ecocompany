"""
ECO COMPANY — Admin Products CRUD
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.utils.pagination import paginate
from app.services.audit_service import log_action

router = APIRouter()


@router.get("")
async def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = None,
    category_id: UUID | None = None,
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Barcha mahsulotlar (admin, filtr bilan)"""
    query = db.query(Product)

    if search:
        safe_search = search.replace("%", "\\%").replace("_", "\\_")
        query = query.filter(Product.name_uz.ilike(f"%{safe_search}%"))
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)

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


@router.post("", status_code=201)
async def create_product(
    request: Request,
    data: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Yangi mahsulot yaratish"""
    product = Product(**data.model_dump())
    db.add(product)
    db.flush()
    log_action(db, current_user.id, "create", "product", product.id, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(product)
    return {"success": True, "data": ProductResponse.model_validate(product)}


@router.put("/{product_id}")
async def update_product(
    request: Request,
    product_id: UUID,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mahsulotni yangilash"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value)

    changes_json = data.model_dump(exclude_unset=True, mode='json')
    log_action(db, current_user.id, "update", "product", product.id, changes=changes_json, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(product)
    return {"success": True, "data": ProductResponse.model_validate(product)}


@router.delete("/{product_id}")
async def delete_product(
    request: Request,
    product_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mahsulotni o'chirish"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")

    log_action(db, current_user.id, "delete", "product", product.id, ip_address=request.client.host if request.client else None)
    db.delete(product)
    db.commit()
    return {"success": True, "message": "Mahsulot o'chirildi"}


@router.post("/reorder")
async def reorder_products(
    items: list[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mahsulotlar tartibini o'zgartirish"""
    for item in items:
        db.query(Product).filter(Product.id == UUID(item["id"])).update(
            {"order_index": item["order_index"]}
        )
    db.commit()
    return {"success": True, "message": "Tartib yangilandi"}
