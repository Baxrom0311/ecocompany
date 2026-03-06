"""
ECO COMPANY — Telegram Service
Telegramga bildirishnoma yuborish
"""
import logging
import httpx
from app.config import settings

logger = logging.getLogger("ecocompany")

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


async def send_message(chat_id: str, text: str, parse_mode: str = "Markdown") -> bool:
    """Bitta chat ga xabar yuborish"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": parse_mode,
                },
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"🤖 Telegram xato (chat_id={chat_id}): {e}")
        return False


async def send_contact_notification(contact) -> None:
    """Barcha admin chatlarga yangi xabar bildirishmasi"""
    text = (
        f"🌿 *Yangi xabar — ECO COMPANY*\n\n"
        f"👤 *Ism:* {contact.name}\n"
        f"📞 *Tel:* {contact.phone or '—'}\n"
        f"📧 *Email:* {contact.email or '—'}\n"
        f"📝 *Mavzu:* {contact.subject or '—'}\n\n"
        f"💬 *Xabar:*\n{contact.message}\n\n"
        f"🕐 _{contact.created_at.strftime('%Y-%m-%d %H:%M') if contact.created_at else '—'}_"
    )

    chat_ids = settings.telegram_chat_list
    for chat_id in chat_ids:
        await send_message(chat_id.strip(), text)

    logger.info(f"🤖 Telegram: {len(chat_ids)} ta chatga yuborildi")
