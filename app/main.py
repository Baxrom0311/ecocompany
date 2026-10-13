"""
🌿 ECO COMPANY — FastAPI Application
Main entry point — CORS, middleware, routers
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from app.middleware.rate_limit import limiter
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.database import engine, Base
from app.middleware.error_handler import setup_error_handlers
from app.middleware.logging_middleware import LoggingMiddleware, setup_logging
from app.middleware.security import SecurityHeadersMiddleware
from app.services.company_mcp import mcp as company_mcp

# ── Logger ──
logger = logging.getLogger("ecocompany")

# ── MCP HTTP application ──
mcp_app = company_mcp.http_app(path="/", stateless_http=True)


# ── Lifespan (startup/shutdown) ──
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup va shutdown events"""
    # STARTUP
    setup_logging()
    settings.media_root_path.mkdir(parents=True, exist_ok=True)
    logger.info("🌿 ECO COMPANY Backend ishga tushdi")
    logger.info(f"📌 Environment: {settings.ENVIRONMENT}")

    # Import all models so Base.metadata knows about them
    from app.models import user, category, product, certificate  # noqa
    from app.models import gallery, contact, setting, chat  # noqa
    from app.models import instagram, audit_log  # noqa

    # Auto-create tables (development uchun — production da alembic ishlatiladi)
    if not settings.is_production:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tablolar yaratildi (development)")

    try:
        with engine.connect() as conn:
            logger.info("✅ Database ulandi")
    except Exception as e:
        logger.warning(f"⚠️ Database ulanish xatosi: {e}")

    async with mcp_app.lifespan(app):
        yield

    # SHUTDOWN
    logger.info("🛑 ECO COMPANY Backend to'xtadi")
    engine.dispose()


# ── FastAPI App ──
app = FastAPI(
    title="ECO COMPANY API",
    description="🌿 Toza va sifatli suv kompaniyasi API",
    version="3.0.0",
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# ── Rate Limiter ──
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Custom Middleware ──
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(LoggingMiddleware)

# ── Error Handlers ──
setup_error_handlers(app)

# ── Local Media Files ──
settings.media_root_path.mkdir(parents=True, exist_ok=True)
app.mount(
    settings.media_url_path,
    StaticFiles(directory=str(settings.media_root_path)),
    name="media",
)
app.mount(
    "/api/v1/mcp",
    mcp_app,
    name="company-mcp",
)


# ── Health Check ──
@app.get("/health", tags=["Health"])
async def health_check():
    """Server holati tekshirish"""
    return {
        "success": True,
        "data": {
            "status": "ok",
            "version": "3.0.0",
            "environment": settings.ENVIRONMENT,
        },
    }


# ────────────────────────────────────────────────
# Routers
# ────────────────────────────────────────────────

from app.routers import auth, products, categories, certificates
from app.routers import gallery, contacts, settings as settings_router
from app.routers import instagram, upload, chat, seo

# Auth
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# Public API
app.include_router(seo.router)
app.include_router(products.router, prefix="/api/v1/products", tags=["Products"])
app.include_router(categories.router, prefix="/api/v1/categories", tags=["Categories"])
app.include_router(certificates.router, prefix="/api/v1/certificates", tags=["Certificates"])
app.include_router(gallery.router, prefix="/api/v1/gallery", tags=["Gallery"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["Contacts"])
app.include_router(settings_router.router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(instagram.router, prefix="/api/v1/instagram", tags=["Instagram"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])

# Admin
app.include_router(upload.router, prefix="/api/v1/admin", tags=["Upload"])

from app.routers.admin import products as admin_products
from app.routers.admin import categories as admin_categories
from app.routers.admin import certificates as admin_certificates
from app.routers.admin import gallery as admin_gallery
from app.routers.admin import contacts as admin_contacts
from app.routers.admin import settings as admin_settings
from app.routers.admin import users as admin_users
from app.routers.admin import instagram as admin_instagram
from app.routers.admin import audit as admin_audit
from app.routers.admin import chat as admin_chat

app.include_router(admin_products.router, prefix="/api/v1/admin/products", tags=["Admin Products"])
app.include_router(admin_categories.router, prefix="/api/v1/admin/categories", tags=["Admin Categories"])
app.include_router(admin_certificates.router, prefix="/api/v1/admin/certificates", tags=["Admin Certificates"])
app.include_router(admin_gallery.router, prefix="/api/v1/admin/gallery", tags=["Admin Gallery"])
app.include_router(admin_contacts.router, prefix="/api/v1/admin/contacts", tags=["Admin Contacts"])
app.include_router(admin_settings.router, prefix="/api/v1/admin/settings", tags=["Admin Settings"])
app.include_router(admin_users.router, prefix="/api/v1/admin/users", tags=["Admin Users"])
app.include_router(admin_instagram.router, prefix="/api/v1/admin/instagram", tags=["Admin Instagram"])
app.include_router(admin_audit.router, prefix="/api/v1/admin/audit-logs", tags=["Admin Audit"])
app.include_router(admin_chat.router, prefix="/api/v1/admin/chat", tags=["Admin Chat"])
