"""
ECO COMPANY — Admin Categories CRUD
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.category import Category
from app.models.product import Product
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.audit_service import log_action
from app.services import storage_service

router = APIRouter()


@router.get("")
async def list_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Barcha kategoriyalar (admin)"""
    categories = db.query(Category).order_by(Category.order_index.asc()).all()
    return {
        "success": True,
        "data": [CategoryResponse.model_validate(c) for c in categories],
    }


@router.post("", status_code=201)
async def create_category(
    request: Request,
    data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Yangi kategoriya"""
    # Slug unique tekshirish
    existing = db.query(Category).filter(Category.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=409, detail="Bu slug allaqachon mavjud")

    category = Category(**data.model_dump())
    db.add(category)
    db.flush()
    log_action(db, current_user.id, "create", "category", category.id, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(category)
    return {"success": True, "data": CategoryResponse.model_validate(category)}


@router.put("/{category_id}")
async def update_category(
    request: Request,
    category_id: UUID,
    data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kategoriyani yangilash"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")

    # Slug unique tekshirish
    previous_icon = category.icon
    update_data = data.model_dump(exclude_unset=True)
    if "slug" in update_data:
        existing = (
            db.query(Category)
            .filter(Category.slug == update_data["slug"], Category.id != category_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=409, detail="Bu slug allaqachon mavjud")

    for key, value in update_data.items():
        setattr(category, key, value)

    changes_json = data.model_dump(exclude_unset=True, mode='json')
    log_action(db, current_user.id, "update", "category", category.id, changes=changes_json, ip_address=request.client.host if request.client else None)
    db.commit()
    db.refresh(category)
    if previous_icon and previous_icon != category.icon:
        await storage_service.delete_file_by_url(previous_icon)
    return {"success": True, "data": CategoryResponse.model_validate(category)}


@router.delete("/{category_id}")
async def delete_category(
    request: Request,
    category_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Kategoriyani o'chirish (mahsuloti bo'lsa taqiqlash)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")

    # Mahsulot tekshirish
    product_count = db.query(Product).filter(Product.category_id == category_id).count()
    if product_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Bu kategoriyada {product_count} ta mahsulot bor. Avval ularni o'chiring.",
        )

    previous_icon = category.icon
    log_action(db, current_user.id, "delete", "category", category.id, ip_address=request.client.host if request.client else None)
    db.delete(category)
    db.commit()
    if previous_icon:
        await storage_service.delete_file_by_url(previous_icon)
    return {"success": True, "message": "Kategoriya o'chirildi"}
