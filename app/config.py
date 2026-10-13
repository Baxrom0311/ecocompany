"""
ECO COMPANY — Application Configuration
Pydantic Settings orqali .env fayldan sozlamalarni o'qish
"""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Barcha loyiha sozlamalari"""

    # ── Database ──
    DATABASE_URL: str

    # ── JWT ──
    JWT_SECRET: str
    JWT_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # ── Email (SMTP) ──
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = False
    SMTP_START_TLS: bool = True
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    ADMIN_EMAIL: str = ""

    # ── Telegram ──
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_IDS: str = ""  # "id1,id2,id3"

    # ── AI (DeepSeek) ──
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    # ── Media Storage ──
    MEDIA_ROOT: str = "media"
    MEDIA_URL_PATH: str = "/media"
    PUBLIC_BASE_URL: str = ""
    SITE_URL: str = ""

    # ── Instagram ──
    INSTAGRAM_ACCESS_TOKEN: str = ""
    INSTAGRAM_USER_ID: str = ""
    INSTAGRAM_CACHE_HOURS: int = 6

    # ── CORS ──
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8080,http://localhost:8081"

    # ── Environment ──
    ENVIRONMENT: str = "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins(self) -> list[str]:
        """ALLOWED_ORIGINS ni list ga aylantirish"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def telegram_chat_list(self) -> list[str]:
        """TELEGRAM_CHAT_IDS ni list ga aylantirish"""
        if not self.TELEGRAM_CHAT_IDS:
            return []
        return [cid.strip() for cid in self.TELEGRAM_CHAT_IDS.split(",")]

    @property
    def media_root_path(self) -> Path:
        """Media fayllar saqlanadigan absolut papka."""
        media_root = Path(self.MEDIA_ROOT)
        if media_root.is_absolute():
            return media_root
        return Path(__file__).resolve().parents[1] / media_root

    @property
    def media_url_path(self) -> str:
        """Media URL prefixi doim slash bilan boshlansin."""
        path = self.MEDIA_URL_PATH.strip() or "/media"
        return path if path.startswith("/") else f"/{path}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
