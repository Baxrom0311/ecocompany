"""
ECO COMPANY — FastMCP tools
Company data va katalogni MCP tool sifatida ochadi.
"""
from decimal import Decimal

from fastmcp import FastMCP
from sqlalchemy import or_

from app.database import SessionLocal
from app.models.category import Category
from app.models.product import Product
from app.models.setting import SiteSetting

mcp = FastMCP("ECO COMPANY MCP")


def _decimal_to_float(value: Decimal | None) -> float | None:
    return float(value) if value is not None else None


def _public_settings_map() -> dict[str, str]:
    with SessionLocal() as db:
        return {
            setting.key: setting.value or ""
            for setting in db.query(SiteSetting).filter(SiteSetting.is_public == True).all()
        }


def _serialize_product(product: Product) -> dict:
    return {
        "id": str(product.id),
        "name_uz": product.name_uz,
        "name_ru": product.name_ru,
        "name_en": product.name_en,
        "desc_uz": product.desc_uz,
        "desc_ru": product.desc_ru,
        "desc_en": product.desc_en,
        "original_price": _decimal_to_float(product.original_price),
        "discount_price": _decimal_to_float(product.discount_price),
        "is_on_sale": product.is_on_sale,
        "is_featured": product.is_featured,
        "is_new": product.is_new,
        "images": product.images or [],
        "category": product.category.name_uz if product.category else None,
    }


@mcp.tool(description="Get ECO COMPANY contact info, address, hours, and social links.")
def get_company_profile() -> dict:
    settings_map = _public_settings_map()
    return {
        "phone_1": settings_map.get("phone_1", ""),
        "phone_2": settings_map.get("phone_2", ""),
        "email": settings_map.get("email", ""),
        "working_hours": settings_map.get("working_hours", ""),
        "address_uz": settings_map.get("address_uz", ""),
        "address_ru": settings_map.get("address_ru", ""),
        "address_en": settings_map.get("address_en", ""),
        "instagram_url": settings_map.get("instagram_url", ""),
        "telegram_url": settings_map.get("telegram_url", ""),
        "whatsapp_url": settings_map.get("whatsapp_url", ""),
        "map_embed": settings_map.get("map_embed", ""),
    }


@mcp.tool(description="List active ECO COMPANY product categories.")
def list_categories() -> list[dict]:
    with SessionLocal() as db:
        categories = (
            db.query(Category)
            .filter(Category.is_active == True)
            .order_by(Category.order_index.asc())
            .all()
        )
        return [
            {
                "id": str(category.id),
                "name_uz": category.name_uz,
                "name_ru": category.name_ru,
                "name_en": category.name_en,
                "slug": category.slug,
            }
            for category in categories
        ]


@mcp.tool(description="List active products with names, categories, prices, and flags.")
def list_active_products(limit: int = 20) -> list[dict]:
    safe_limit = max(1, min(limit, 50))
    with SessionLocal() as db:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .order_by(Product.order_index.asc())
            .limit(safe_limit)
            .all()
        )
        return [_serialize_product(product) for product in products]


@mcp.tool(description="Search active products by name or description. Use for specific product questions.")
def search_products(query: str, limit: int = 10) -> list[dict]:
    safe_query = (query or "").strip()
    if not safe_query:
        return []

    safe_limit = max(1, min(limit, 20))
    pattern = f"%{safe_query.replace('%', '\\%').replace('_', '\\_')}%"

    with SessionLocal() as db:
        products = (
            db.query(Product)
            .filter(Product.is_active == True)
            .filter(
                or_(
                    Product.name_uz.ilike(pattern),
                    Product.name_ru.ilike(pattern),
                    Product.name_en.ilike(pattern),
                    Product.desc_uz.ilike(pattern),
                    Product.desc_ru.ilike(pattern),
                    Product.desc_en.ilike(pattern),
                )
            )
            .order_by(Product.order_index.asc())
            .limit(safe_limit)
            .all()
        )
        return [_serialize_product(product) for product in products]
