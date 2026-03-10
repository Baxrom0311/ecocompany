"""
ECO COMPANY — AI Chatbot Service
Claude (Anthropic) AsyncAnthropic + dynamic prompt
"""
import logging
import uuid
from datetime import datetime, timezone
from anthropic import AsyncAnthropic
from sqlalchemy.orm import Session
from app.config import settings
from app.models.chat import ChatSession
from app.models.product import Product
from app.models.setting import SiteSetting

logger = logging.getLogger("ecocompany")

# ── Async Client ──
client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)

# ── Default prompt (DB da bo'lmasa ishlatiladi) ──
DEFAULT_PROMPT = """Siz ECO COMPANY kompaniyasining AI yordamchisisiz.
Kompaniya tozalangan suv va ekologik mahsulotlar ishlab chiqaradi.

QOIDALAR:
1. Faqat kompaniya haqida savollarga javob bering
2. Tilni aniqlab shu tilda javob bering (uz/ru/en)
3. Qisqa va aniq javob bering (max 3-4 gap)
4. Bilmasangiz: "Admin bilan bog'laning"
5. Salomlashishda o'zingizni taqdim eting
6. Xushmuomala va professional bo'ling"""

PROMPT_SETTING_KEY = "ai_system_prompt"


def _get_system_prompt(db: Session) -> str:
    """DB dan dynamic prompt + kompaniya ma'lumotlari"""

    # 1. Prompt — DB dan yoki default
    prompt_setting = db.query(SiteSetting).filter(
        SiteSetting.key == PROMPT_SETTING_KEY
    ).first()
    base_prompt = prompt_setting.value if prompt_setting else DEFAULT_PROMPT

    # 2. Settings dan kompaniya kontekst
    settings_dict = {}
    for s in db.query(SiteSetting).filter(SiteSetting.is_public == True).all():
        settings_dict[s.key] = s.value

    # 3. Aktiv mahsulotlar
    products = db.query(Product).filter(Product.is_active == True).limit(50).all()
    products_text = "\n".join(
        f"- {p.name_uz} ({p.name_ru or ''}): {p.original_price or '—'} so'm"
        for p in products
    ) or "Hozircha mahsulotlar mavjud emas"

    phone = settings_dict.get("phone_1", "")
    email = settings_dict.get("email", "")
    address = (
        settings_dict.get("address_uz")
        or settings_dict.get("address_ru")
        or settings_dict.get("address_en")
        or settings_dict.get("address", "")
    )

    return f"""{base_prompt}

KOMPANIYA MA'LUMOTLARI:
- Telefon: {phone}
- Email: {email}
- Manzil: {address}
- Ish vaqti: {settings_dict.get('working_hours', '')}

MAHSULOTLAR:
{products_text}"""


async def chat(session_id: str | None, message: str, ip_address: str, db: Session) -> dict:
    """
    Chatbot bilan suhbat (async).
    Returns: {"reply": str, "session_id": str}
    """
    # Session topish yoki yaratish
    if session_id:
        session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    else:
        session = None

    if not session:
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            messages=[],
            ip_address=ip_address,
            message_count=0,
        )
        db.add(session)

    # User xabar qo'shish (timestamp bilan)
    now = datetime.now(timezone.utc).isoformat()
    messages = list(session.messages or [])
    messages.append({
        "role": "user",
        "content": message,
        "timestamp": now,
    })

    # Oxirgi 20 ta xabar (context limit)
    recent_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages[-20:]
    ]

    try:
        # Claude API — async
        system_prompt = _get_system_prompt(db)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=system_prompt,
            messages=recent_messages,
        )
        reply = response.content[0].text
    except Exception as e:
        logger.error(f"🤖 AI xato: {e}")
        reply = "Uzr, hozir texnik nosozlik. Iltimos, keyinroq urinib ko'ring yoki bizga qo'ng'iroq qiling."

    # Javobni saqlash (timestamp bilan)
    messages.append({
        "role": "assistant",
        "content": reply,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })

    # Session yangilash
    session.messages = messages
    session.message_count = len(messages)
    session.last_message_at = datetime.now(timezone.utc)
    session.is_active = True
    db.commit()

    return {"reply": reply, "session_id": session.session_id}
