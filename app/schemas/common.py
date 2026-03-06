"""
ECO COMPANY — Common Schemas
Umumiy response sxemalari (barcha routerlarda ishlatiladi)
"""
from pydantic import BaseModel
from typing import Any, Optional


class SuccessResponse(BaseModel):
    """Muvaffaqiyatli javob"""
    success: bool = True
    data: Any = None
    message: str | None = None


class ErrorResponse(BaseModel):
    """Xato javob"""
    success: bool = False
    error: str
    message: str
    detail: Any = None


class MessageResponse(BaseModel):
    """Oddiy xabar javob"""
    success: bool = True
    message: str


class PaginatedResponse(BaseModel):
    """Pagination bilan javob"""
    items: list[Any]
    total: int
    page: int
    per_page: int
    pages: int
