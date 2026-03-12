"""
ECO COMPANY — Public Gallery Router
Album + Items (public)
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload
from app.database import get_db
from app.models.gallery import GalleryAlbum, GalleryItem
from app.schemas.gallery import GalleryAlbumResponse, GalleryAlbumListResponse, GalleryItemResponse

router = APIRouter()


@router.get("/albums")
async def get_albums(
    category: str | None = None,
    db: Session = Depends(get_db),
):
    """Aktiv albumlar ro'yxati (items siz)"""
    query = (
        db.query(GalleryAlbum)
        .options(selectinload(GalleryAlbum.items))
        .filter(GalleryAlbum.is_active == True)
    )

    if category:
        query = query.filter(GalleryAlbum.category == category)

    albums = query.order_by(GalleryAlbum.order_index.asc()).all()

    # Items count qo'shish
    result = []
    for album in albums:
        active_items = [item for item in album.items if item.is_active]
        cover_item = None
        if album.cover_item_id:
            cover_item = next((item for item in active_items if item.id == album.cover_item_id), None)
        if cover_item is None and active_items:
            cover_item = active_items[0]

        data = GalleryAlbumListResponse.model_validate(album)
        data.items_count = len(active_items)
        if cover_item:
            data.cover_url = cover_item.file_url
            data.cover_thumbnail_url = cover_item.thumbnail_url or cover_item.file_url
            data.cover_file_type = cover_item.file_type
        data.preview_items = [GalleryItemResponse.model_validate(item) for item in active_items[:12]]
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
