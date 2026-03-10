"""
ECO COMPANY — Instagram Service
Instagram videolarini qo'lda link orqali boshqarish.
"""
import json
import logging
import re
from sqlalchemy.orm import Session
from app.models.setting import SiteSetting

logger = logging.getLogger("ecocompany")

INSTAGRAM_VIDEO_LINKS_KEY = "instagram_video_links"
INSTAGRAM_LINK_RE = re.compile(
    r"^https?://(?:www\.)?instagram\.com/(?P<kind>reel|p|tv)/(?P<code>[A-Za-z0-9_-]+)/?(?:\?.*)?$",
    re.IGNORECASE,
)


def _normalize_instagram_url(url: str) -> str:
    normalized = (url or "").strip()
    if not normalized:
        raise ValueError("Instagram link bo'sh bo'lmasligi kerak")

    if not normalized.startswith(("http://", "https://")):
        normalized = f"https://{normalized.lstrip('/')}"

    normalized = normalized.rstrip("/")
    match = INSTAGRAM_LINK_RE.match(normalized)
    if not match:
        raise ValueError("Faqat Instagram reel/post linklari qabul qilinadi")

    kind = match.group("kind").lower()
    code = match.group("code")
    return f"https://www.instagram.com/{kind}/{code}/"


def _build_video_payload(url: str) -> dict:
    canonical_url = _normalize_instagram_url(url)
    match = INSTAGRAM_LINK_RE.match(canonical_url.rstrip("/"))
    if not match:
        raise ValueError("Instagram link yaroqsiz")

    kind = match.group("kind").lower()
    code = match.group("code")
    return {
        "id": code,
        "url": canonical_url,
        "permalink": canonical_url,
        "embed_url": f"{canonical_url}embed",
        "media_type": "VIDEO",
        "kind": kind,
    }


def _get_links_setting(db: Session) -> SiteSetting | None:
    return db.query(SiteSetting).filter(SiteSetting.key == INSTAGRAM_VIDEO_LINKS_KEY).first()


def get_manual_links(db: Session) -> list[dict]:
    setting = _get_links_setting(db)
    if not setting or not setting.value:
        return []

    try:
        raw_items = json.loads(setting.value)
    except json.JSONDecodeError:
        logger.warning("Instagram video linklari JSON emas, bo'sh ro'yxat qaytarildi")
        return []

    if not isinstance(raw_items, list):
        return []

    result: list[dict] = []
    seen: set[str] = set()
    for item in raw_items:
        url = item.get("url") if isinstance(item, dict) else str(item)
        try:
            payload = _build_video_payload(url)
        except ValueError:
            logger.warning("Instagram link o'tkazib yuborildi: %s", url)
            continue

        if payload["url"] in seen:
            continue
        seen.add(payload["url"])
        result.append(payload)

    return result


def save_manual_links(db: Session, items: list[dict]) -> list[dict]:
    normalized_links: list[dict] = []
    seen: set[str] = set()

    for item in items:
        url = item.get("url") if isinstance(item, dict) else None
        payload = _build_video_payload(url or "")
        if payload["url"] in seen:
            continue
        seen.add(payload["url"])
        normalized_links.append(payload)

    value = json.dumps(
        [{"url": item["url"]} for item in normalized_links],
        ensure_ascii=False,
    )

    setting = _get_links_setting(db)
    if not setting:
        setting = SiteSetting(
            key=INSTAGRAM_VIDEO_LINKS_KEY,
            value=value,
            type="json",
            label="Instagram video linklari",
            is_public=False,
        )
        db.add(setting)
    else:
        setting.value = value
        setting.type = "json"
        setting.label = "Instagram video linklari"
        setting.is_public = False

    db.commit()
    db.refresh(setting)
    return normalized_links


def get_manual_status(db: Session) -> dict:
    links = get_manual_links(db)
    return {
        "mode": "manual",
        "is_configured": len(links) > 0,
        "link_count": len(links),
        "message": "Instagram videolari API emas, qo'lda kiritilgan linklar orqali ko'rsatiladi.",
    }
