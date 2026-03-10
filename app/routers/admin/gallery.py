"""
ECO COMPANY — Admin Gallery CRUD
Albums + Items boshqarish
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.gallery import GalleryAlbum, GalleryItem
from app.schemas.gallery import (
    GalleryAlbumCreate, GalleryAlbumUpdate, GalleryAlbumResponse,
    GalleryItemCreate, GalleryItemUpdate, GalleryItemResponse,
)
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services import storage_service

router = APIRouter()


# ── ALBUMS ──

@router.get("/albums")
async def list_albums(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    albums = db.query(GalleryAlbum).order_by(GalleryAlbum.order_index.asc()).all()
    return {"success": True, "data": [GalleryAlbumResponse.model_validate(a) for a in albums]}


@router.post("/albums", status_code=201)
async def create_album(
    data: GalleryAlbumCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    payload = data.model_dump()
    payload["category"] = None
    payload["is_active"] = True
    album = GalleryAlbum(**payload)
    db.add(album)
    db.commit()
    db.refresh(album)
    return {"success": True, "data": GalleryAlbumResponse.model_validate(album)}


@router.put("/albums/{album_id}")
async def update_album(
    album_id: UUID,
    data: GalleryAlbumUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(GalleryAlbum).filter(GalleryAlbum.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album topilmadi")

    update_data = data.model_dump(exclude_unset=True)
    update_data["category"] = None
    update_data["is_active"] = True
    for key, value in update_data.items():
        setattr(album, key, value)

    db.commit()
    db.refresh(album)
    return {"success": True, "data": GalleryAlbumResponse.model_validate(album)}


@router.delete("/albums/{album_id}")
async def delete_album(
    album_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(GalleryAlbum).filter(GalleryAlbum.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album topilmadi")

    previous_urls = []
    for item in album.items:
        previous_urls.extend([item.file_url, item.thumbnail_url])
    db.delete(album)  # CASCADE — items ham o'chiriladi
    db.commit()
    await storage_service.delete_files_by_urls(previous_urls)
    return {"success": True, "message": "Album va barcha elementlari o'chirildi"}


# ── ITEMS ──

@router.post("/albums/{album_id}/items", status_code=201)
async def add_item(
    album_id: UUID,
    data: GalleryItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    album = db.query(GalleryAlbum).filter(GalleryAlbum.id == album_id).first()
    if not album:
        raise HTTPException(status_code=404, detail="Album topilmadi")

    item = GalleryItem(album_id=album_id, **data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"success": True, "data": GalleryItemResponse.model_validate(item)}


@router.put("/albums/{album_id}/items/{item_id}")
async def update_item(
    album_id: UUID,
    item_id: UUID,
    data: GalleryItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(GalleryItem).filter(
        GalleryItem.id == item_id, GalleryItem.album_id == album_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Element topilmadi")

    previous_urls = [item.file_url, item.thumbnail_url]
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    await storage_service.delete_files_by_urls(
        [url for url in previous_urls if url and url not in {item.file_url, item.thumbnail_url}]
    )
    return {"success": True, "data": GalleryItemResponse.model_validate(item)}


@router.delete("/albums/{album_id}/items/{item_id}")
async def delete_item(
    album_id: UUID,
    item_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(GalleryItem).filter(
        GalleryItem.id == item_id, GalleryItem.album_id == album_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Element topilmadi")

    previous_urls = [item.file_url, item.thumbnail_url]
    db.delete(item)
    db.commit()
    await storage_service.delete_files_by_urls(previous_urls)
    return {"success": True, "message": "Element o'chirildi"}


@router.post("/albums/{album_id}/items/reorder")
async def reorder_items(
    album_id: UUID,
    items: list[dict],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    for item in items:
        db.query(GalleryItem).filter(
            GalleryItem.id == item["id"], GalleryItem.album_id == album_id
        ).update({"order_index": item["order_index"]})
    db.commit()
    return {"success": True, "message": "Tartib yangilandi"}
