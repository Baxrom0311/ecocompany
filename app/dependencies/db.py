"""
ECO COMPANY — Database Dependency
FastAPI uchun DB session dependency
"""
from app.database import get_db

# Re-export — routerlarda Depends(get_db) ishlatish uchun
__all__ = ["get_db"]
