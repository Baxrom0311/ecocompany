"""
ECO COMPANY — Pagination Utility
API uchun umumiy pagination logikasi
"""
from math import ceil
from sqlalchemy.orm import Query


def paginate(query: Query, page: int = 1, per_page: int = 12) -> dict:
    """
    SQLAlchemy query ni pagination bilan qaytarish.

    Returns:
        {
            "items": [...],
            "total": 100,
            "page": 1,
            "per_page": 12,
            "pages": 9
        }
    """
    # Chegaralash
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # max 100 ta

    # Hisoblash
    total = query.count()
    pages = ceil(total / per_page) if total > 0 else 0
    offset = (page - 1) * per_page

    # Ma'lumotlarni olish
    items = query.offset(offset).limit(per_page).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }
