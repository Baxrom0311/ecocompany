"""
ECO COMPANY — Instagram Service
Token boshqarish va post keshini yangilash
"""
import logging
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from app.config import settings
from app.models.instagram import InstagramPost

logger = logging.getLogger("ecocompany")

GRAPH_API = "https://graph.instagram.com"


async def refresh_long_lived_token() -> dict | None:
    """
    Instagram long-lived tokenni yangilash.
    Har 25 kunda avtomatik (cron) yoki admin panel orqali chaqiriladi.
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{GRAPH_API}/refresh_access_token",
                params={
                    "grant_type": "ig_refresh_token",
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                },
            )
            data = response.json()

            if "access_token" in data:
                logger.info(f"📸 Instagram token yangilandi, expires_in={data.get('expires_in')} sec")
                return {
                    "access_token": data["access_token"],
                    "expires_in": data.get("expires_in", 5184000),
                }
            else:
                logger.error(f"📸 Instagram token xato: {data}")
                return None
    except Exception as e:
        logger.error(f"📸 Instagram token refresh xato: {e}")
        return None


async def get_token_status() -> dict:
    """Token holatini tekshirish"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(
                f"{GRAPH_API}/me",
                params={"access_token": settings.INSTAGRAM_ACCESS_TOKEN},
            )
            if response.status_code == 200:
                return {"is_valid": True, "data": response.json()}
            else:
                return {"is_valid": False, "error": response.json()}
    except Exception as e:
        return {"is_valid": False, "error": str(e)}


async def fetch_and_cache_posts(db: Session, limit: int = 25) -> int:
    """
    Instagram API dan postlarni olish va DB ga keshga saqlash.
    Returns: saqlangan post soni.
    """
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.get(
                f"{GRAPH_API}/me/media",
                params={
                    "fields": "id,media_type,media_url,thumbnail_url,permalink,caption,timestamp",
                    "limit": limit,
                    "access_token": settings.INSTAGRAM_ACCESS_TOKEN,
                },
            )
            data = response.json()

        posts = data.get("data", [])
        if not posts:
            return 0

        # Eski keshni tozalash
        db.query(InstagramPost).delete()

        count = 0
        for post in posts:
            ig_post = InstagramPost(
                instagram_id=post["id"],
                media_type=post.get("media_type", "IMAGE"),
                media_url=post.get("media_url"),
                thumbnail_url=post.get("thumbnail_url"),
                permalink=post.get("permalink"),
                caption=post.get("caption"),
                timestamp=datetime.fromisoformat(post["timestamp"].replace("Z", "+00:00")) if post.get("timestamp") else None,
                cached_at=datetime.now(timezone.utc),
            )
            db.add(ig_post)
            count += 1

        db.commit()
        logger.info(f"📸 Instagram: {count} ta post keshga saqlandi")
        return count
    except Exception as e:
        logger.error(f"📸 Instagram fetch xato: {e}")
        db.rollback()
        return 0
