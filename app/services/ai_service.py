"""
ECO COMPANY — AI Chatbot Service
DeepSeek Chat Completions + FastMCP company tools
"""
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastmcp import Client
from openai import AsyncOpenAI
from sqlalchemy.orm import Session

from app.config import settings
from app.models.chat import ChatSession
from app.models.setting import SiteSetting
from app.services.company_mcp import mcp as company_mcp

logger = logging.getLogger("ecocompany")

DEFAULT_PROMPT = """Siz ECO COMPANY kompaniyasining AI yordamchisisiz.
Kompaniya tozalangan suv va ekologik mahsulotlar ishlab chiqaradi.

QOIDALAR:
1. Faqat kompaniya haqida savollarga javob bering
2. Tilni aniqlab shu tilda javob bering (uz/ru/en)
3. Qisqa va aniq javob bering (max 3-4 gap)
4. Bilmasangiz: "Admin bilan bog'laning"
5. Salomlashishda o'zingizni taqdim eting
6. Xushmuomala va professional bo'ling
7. Narx, mahsulot, aloqa yoki manzil bo'yicha fakt kerak bo'lsa tool ishlating
8. Tool natijasida ma'lumot topilmasa, taxmin qilmang"""

PROMPT_SETTING_KEY = "ai_system_prompt"
FALLBACK_REPLY = "Uzr, hozir texnik nosozlik. Iltimos, keyinroq urinib ko'ring yoki bizga qo'ng'iroq qiling."
NOT_CONFIGURED_REPLY = "AI chat hozircha sozlanmagan. Iltimos, admin bilan bog'laning."

_client: AsyncOpenAI | None = None


def _get_llm_client() -> AsyncOpenAI | None:
    global _client
    if not settings.DEEPSEEK_API_KEY:
        return None
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL.rstrip("/"),
        )
    return _client


def _get_system_prompt(db: Session) -> str:
    prompt_setting = db.query(SiteSetting).filter(SiteSetting.key == PROMPT_SETTING_KEY).first()
    base_prompt = prompt_setting.value if prompt_setting else DEFAULT_PROMPT
    return f"""{base_prompt}

TOOL FOYDALANISH:
- get_company_profile: aloqa, manzil, ish vaqti, ijtimoiy linklar
- list_categories: aktiv kategoriyalar
- list_active_products: aktiv mahsulotlar ro'yxati
- search_products: aniq mahsulot yoki kalit so'z bo'yicha qidiruv

Javob berishda faktlarni shu tool natijalariga tayang."""


def _recent_messages(messages: list[dict]) -> list[dict[str, str]]:
    return [
        {"role": message["role"], "content": message["content"]}
        for message in messages[-20:]
        if message.get("role") in {"user", "assistant"} and message.get("content")
    ]


def _tool_payload(tool: Any) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema or {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    }


def _parse_tool_arguments(raw_arguments: str | dict | None) -> dict[str, Any]:
    if isinstance(raw_arguments, dict):
        return raw_arguments
    if not raw_arguments:
        return {}
    try:
        parsed = json.loads(raw_arguments)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        return {}


def _tool_result_content(result: Any) -> str:
    payload = getattr(result, "data", None)
    if payload is not None:
        return json.dumps(payload, ensure_ascii=False)

    content = getattr(result, "content", None) or []
    text_chunks = [getattr(item, "text", "") for item in content if getattr(item, "text", "")]
    if text_chunks:
        return "\n".join(text_chunks)
    return "{}"


async def _generate_reply(db: Session, messages: list[dict[str, str]]) -> str:
    client = _get_llm_client()
    if client is None:
        logger.warning("DeepSeek API key configured emas")
        return NOT_CONFIGURED_REPLY

    system_prompt = _get_system_prompt(db)

    async with Client(company_mcp) as mcp_client:
        tools = [_tool_payload(tool) for tool in await mcp_client.list_tools()]
        conversation: list[dict[str, Any]] = [{"role": "system", "content": system_prompt}, *messages]

        for _ in range(4):
            response = await client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL,
                messages=conversation,
                tools=tools,
                max_tokens=500,
            )

            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls or []
            content = assistant_message.content or ""

            if not tool_calls:
                return content.strip() or FALLBACK_REPLY

            conversation.append(
                {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": [tool_call.model_dump(mode="json") for tool_call in tool_calls],
                }
            )

            for tool_call in tool_calls:
                arguments = _parse_tool_arguments(tool_call.function.arguments)
                tool_result = await mcp_client.call_tool(tool_call.function.name, arguments)
                conversation.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": _tool_result_content(tool_result),
                    }
                )

    return FALLBACK_REPLY


async def chat(session_id: str | None, message: str, ip_address: str, db: Session) -> dict:
    """
    Chatbot bilan suhbat (async).
    Returns: {"reply": str, "session_id": str}
    """
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

    now = datetime.now(timezone.utc).isoformat()
    messages = list(session.messages or [])
    messages.append(
        {
            "role": "user",
            "content": message,
            "timestamp": now,
        }
    )

    try:
        reply = await _generate_reply(db, _recent_messages(messages))
    except Exception as exc:
        logger.error("DeepSeek/FastMCP chat xatosi: %s", exc, exc_info=True)
        reply = FALLBACK_REPLY

    messages.append(
        {
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    )

    session.messages = messages
    session.message_count = len(messages)
    session.last_message_at = datetime.now(timezone.utc)
    session.is_active = True
    db.commit()

    return {"reply": reply, "session_id": session.session_id}
