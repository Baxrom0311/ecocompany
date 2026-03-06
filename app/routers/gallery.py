"""
ECO COMPANY — Public Gallery Router
Album + Items (public)
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.gallery import GalleryAlbum, GalleryItem
from app.schemas.gallery import GalleryAlbumResponse, GalleryAlbumListResponse

router = APIRouter()


@router.get("/albums")
async def get_albums(
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Aktiv albumlar ro'yxati (items siz)"""
    query = db.query(GalleryAlbum).filter(GalleryAlbum.is_active == True)

    if category:
        query = query.filter(GalleryAlbum.category == category)

    albums = query.order_by(GalleryAlbum.order_index.asc()).all()

    # Items count qo'shish
    result = []
    for album in albums:
        data = GalleryAlbumListResponse.model_validate(album)
        data.items_count = len(album.items)
        result.append(data)

    return {"success": True, "data": result}


@router.get("/albums/{album_id}")
async def get_album(album_id: UUID, db: Session = Depends(get_db)):
    """Bitta album (barcha items bilan)"""
    album = (
        db.query(GalleryAlbum)
        .filter(GalleryAlbum.id == album_id, GalleryAlbum.is_active == True)
        .first()
    )
    if not album:
        raise HTTPException(status_code=404, detail="Album topilmadi")

    return {
        "success": True,
        "data": GalleryAlbumResponse.model_validate(album),
    }
