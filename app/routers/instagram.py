"""
ECO COMPANY — Public Instagram Router
DB keshdan postlar
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.instagram import InstagramPost

router = APIRouter()


@router.get("/posts")
async def get_instagram_posts(db: Session = Depends(get_db)):
    """So'ngi 12 ta Instagram post (DB keshdan)"""
    posts = (
        db.query(InstagramPost)
        .order_by(InstagramPost.timestamp.desc())
        .limit(12)
        .all()
    )

    return {
        "success": True,
        "data": [
            {
                "id": str(p.id),
                "instagram_id": p.instagram_id,
                "media_type": p.media_type,
                "media_url": p.media_url,
                "thumbnail_url": p.thumbnail_url,
                "permalink": p.permalink,
                "caption": p.caption,
                "timestamp": p.timestamp.isoformat() if p.timestamp else None,
            }
            for p in posts
        ],
    }
