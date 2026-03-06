"""
ECO COMPANY — Database Configuration
SQLAlchemy engine, session factory, va Base model
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings


# ── Engine ──
# SQLite va PostgreSQL uchun mos sozlamalar
_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=not settings.is_production,
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        echo=not settings.is_production,
    )

# ── Session Factory ──
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ── Base Model ──
Base = declarative_base()


# ── Dependency ──
def get_db():
    """
    FastAPI dependency — har bir request uchun DB session.
    Request tugagach session yopiladi.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
