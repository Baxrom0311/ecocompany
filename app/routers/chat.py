"""
ECO COMPANY — Chat Router
AI chatbot (DeepSeek + FastMCP, rate limited)
"""
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.schemas.chat import ChatMessage, ChatResponse
from app.services import ai_service

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("")
@limiter.limit("20/hour")
async def chat(
    request: Request,
    data: ChatMessage,
    db: Session = Depends(get_db),
):
    """AI chatbot bilan suhbat (soatiga max 20 ta)"""
    ip = request.client.host if request.client else None

    try:
        result = await ai_service.chat(
            session_id=data.session_id,
            message=data.message,
            ip_address=ip,
            db=db,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="AI xizmatida xatolik yuz berdi. Iltimos keyinroq qayta urinib ko'ring.")

    return {
        "success": True,
        "data": ChatResponse(
            reply=result["reply"],
            session_id=result["session_id"],
        ),
    }
