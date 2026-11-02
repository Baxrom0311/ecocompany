"""
ECO COMPANY — Public site rebuild trigger
Mahsulot/kategoriya/sozlama o'zgarganda Vercel deploy hook orqali saytni qayta build qiladi,
shunda sitemap va oldindan tayyorlangan sahifalar yangilanadi.
"""
import asyncio
import logging

import httpx

from app.config import settings

logger = logging.getLogger("ecocompany")

REBUILD_DELAY_SECONDS = 60
REBUILD_PATH_PREFIXES = (
    "/api/v1/admin/products",
    "/api/v1/admin/categories",
    "/api/v1/admin/settings",
)

_pending: asyncio.Task | None = None


def should_rebuild(method: str, path: str, status_code: int) -> bool:
    return (
        bool(settings.SITE_REBUILD_HOOK_URL)
        and method in {"POST", "PUT", "PATCH", "DELETE"}
        and status_code < 400
        and path.startswith(REBUILD_PATH_PREFIXES)
    )


async def _trigger_after_delay() -> None:
    await asyncio.sleep(REBUILD_DELAY_SECONDS)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(settings.SITE_REBUILD_HOOK_URL)
            response.raise_for_status()
        logger.info("🔄 Sayt qayta build qilinmoqda (deploy hook)")
    except Exception as exc:
        logger.warning("Sayt deploy hook xatosi: %s", exc)


def schedule_site_rebuild() -> None:
    """Ketma-ket o'zgarishlarni bitta build'ga birlashtiradi (debounce)."""
    global _pending
    if _pending and not _pending.done():
        _pending.cancel()
    _pending = asyncio.get_running_loop().create_task(_trigger_after_delay())
