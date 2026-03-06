"""
ECO COMPANY — Admin Chat Router
Chat sessiyalarni boshqarish + system prompt
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.chat import ChatSession
from app.models.setting import SiteSetting
from app.schemas.chat import ChatSessionResponse, ChatSessionDetail, SystemPromptUpdate
from app.dependencies.auth import get_current_user, get_super_admin
from app.models.user import User
from app.utils.pagination import paginate

router = APIRouter()


# ── Default System Prompt ──
DEFAULT_SYSTEM_PROMPT = """Siz ECO COMPANY kompaniyasining AI yordamchisisiz.
Kompaniya tozalangan suv va ekologik mahsulotlar ishlab chiqaradi.

QOIDALAR:
1. Faqat kompaniya haqida savollarga javob bering
2. Tilni aniqlab shu tilda javob bering (uz/ru/en)
3. Qisqa va aniq javob bering (max 3-4 gap)
4. Bilmasangiz: "Admin bilan bog'laning"
5. Salomlashishda o'zingizni taqdim eting
6. Xushmuomala va professional bo'ling"""


@router.get("/sessions")
async def list_chat_sessions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    is_active: bool | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Barcha chat sessiyalar (pagination bilan)"""
    query = db.query(ChatSession)

    if is_active is not None:
        query = query.filter(ChatSession.is_active == is_active)

    query = query.order_by(ChatSession.last_message_at.desc())
    result = paginate(query, page, per_page)

    return {
        "success": True,
        "data": {
            "items": [ChatSessionResponse.model_validate(s) for s in result["items"]],
            "total": result["total"],
            "page": result["page"],
            "per_page": result["per_page"],
            "pages": result["pages"],
        },
    }


@router.get("/sessions/stats")
async def chat_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Chat statistikasi"""
    total = db.query(ChatSession).count()
    active = db.query(ChatSession).filter(ChatSession.is_active == True).count()
    return {
        "success": True,
        "data": {
            "total_sessions": total,
            "active_sessions": active,
        },
    }


@router.get("/sessions/{session_id}")
async def get_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bitta sessiya to'liq xabarlar bilan"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")

    return {
        "success": True,
        "data": ChatSessionDetail.model_validate(session),
    }


@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sessiyani o'chirish"""
    session = db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Sessiya topilmadi")

    db.delete(session)
    db.commit()
    return {"success": True, "message": "Sessiya o'chirildi"}


@router.delete("/sessions")
async def clear_all_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """Barcha sessiyalarni tozalash (faqat super_admin)"""
    count = db.query(ChatSession).delete()
    db.commit()
    return {"success": True, "message": f"{count} ta sessiya o'chirildi"}


# ── System Prompt Management ──
PROMPT_SETTING_KEY = "ai_system_prompt"


@router.get("/prompt")
async def get_system_prompt(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Joriy AI system promptni ko'rish"""
    setting = db.query(SiteSetting).filter(SiteSetting.key == PROMPT_SETTING_KEY).first()
    prompt = setting.value if setting else DEFAULT_SYSTEM_PROMPT

    return {
        "success": True,
        "data": {
            "prompt": prompt,
            "is_default": setting is None,
        },
    }


@router.put("/prompt")
async def update_system_prompt(
    data: SystemPromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """AI system promptni yangilash (faqat super_admin)"""
    setting = db.query(SiteSetting).filter(SiteSetting.key == PROMPT_SETTING_KEY).first()

    if setting:
        setting.value = data.prompt
    else:
        setting = SiteSetting(
            key=PROMPT_SETTING_KEY,
            value=data.prompt,
            type="text",
            label="AI Chatbot System Prompt",
            is_public=False,
        )
        db.add(setting)

    db.commit()
    return {"success": True, "message": "System prompt yangilandi"}


@router.post("/prompt/reset")
async def reset_system_prompt(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_super_admin),
):
    """Promptni default holatga qaytarish"""
    setting = db.query(SiteSetting).filter(SiteSetting.key == PROMPT_SETTING_KEY).first()
    if setting:
        db.delete(setting)
        db.commit()

    return {"success": True, "message": "Prompt default holatga qaytarildi"}
