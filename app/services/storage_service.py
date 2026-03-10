"""
ECO COMPANY — Local Storage Service
Media fayllarni serverdagi papkaga saqlash/o'chirish
"""
import asyncio
import re
import uuid
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from collections.abc import Iterable

from fastapi import UploadFile

from app.config import settings

_SAFE_PART_RE = re.compile(r"[^a-zA-Z0-9_-]+")
_SAFE_EXT_RE = re.compile(r"[^a-zA-Z0-9.]")


def _media_root() -> Path:
    root = settings.media_root_path
    root.mkdir(parents=True, exist_ok=True)
    return root


def _sanitize_folder(folder: str | None) -> Path:
    raw_folder = (folder or "ecocompany").strip().replace("\\", "/")
    parts = []
    for part in raw_folder.split("/"):
        part = part.strip()
        if not part or part in {".", ".."}:
            continue
        safe = _SAFE_PART_RE.sub("-", part).strip("-")
        if safe:
            parts.append(safe.lower())
    return Path(*parts) if parts else Path("ecocompany")


def _unique_filename(filename: str | None) -> str:
    original_name = Path(filename or "file").name
    suffix = _SAFE_EXT_RE.sub("", Path(original_name).suffix.lower())[:10]
    stem = _SAFE_PART_RE.sub("-", Path(original_name).stem).strip("-").lower() or "file"
    return f"{stem}-{uuid.uuid4().hex[:12]}{suffix}"


def _resolve_relative_path(public_id: str) -> Path | None:
    relative = Path(public_id.strip().lstrip("/"))
    if relative.is_absolute() or ".." in relative.parts:
        return None

    resolved = (_media_root() / relative).resolve()
    try:
        resolved.relative_to(_media_root().resolve())
    except ValueError:
        return None
    return resolved


def build_file_url(public_id: str, base_url: str | None = None) -> str:
    media_path = f"{settings.media_url_path.rstrip('/')}/{public_id.lstrip('/')}"
    public_base = (settings.PUBLIC_BASE_URL or "").strip()
    if public_base:
        return urljoin(f"{public_base.rstrip('/')}/", media_path.lstrip("/"))
    if base_url:
        return urljoin(f"{base_url.rstrip('/')}/", media_path.lstrip("/"))
    return media_path


def extract_public_id(file_url: str | None) -> str | None:
    """Local media URL dan storage public_id ni ajratib olish."""
    if not file_url:
        return None

    raw_url = file_url.strip()
    if not raw_url:
        return None

    try:
        parsed = urlparse(raw_url)
        path = parsed.path or raw_url
    except ValueError:
        path = raw_url

    media_prefix = f"{settings.media_url_path.rstrip('/')}/"
    if not path.startswith(media_prefix):
        return None

    public_id = unquote(path[len(media_prefix):].lstrip("/"))
    return public_id or None


async def upload_file(file: UploadFile, folder: str = "ecocompany", base_url: str | None = None) -> dict:
    """UploadFile obyektini local media papkaga saqlash."""
    contents = await file.read()
    return await upload_bytes(
        data=contents,
        folder=folder,
        filename=file.filename or "",
        base_url=base_url,
    )


async def upload_bytes(
    data: bytes,
    folder: str = "ecocompany",
    filename: str = "",
    base_url: str | None = None,
) -> dict:
    """Bytes ko'rinishidagi faylni local media papkaga saqlash."""
    target_dir = _media_root() / _sanitize_folder(folder)
    target_dir.mkdir(parents=True, exist_ok=True)

    stored_name = _unique_filename(filename)
    destination = target_dir / stored_name
    await asyncio.to_thread(destination.write_bytes, data)

    public_id = destination.relative_to(_media_root()).as_posix()
    return {
        "url": build_file_url(public_id, base_url=base_url),
        "public_id": public_id,
        "bytes": len(data),
        "filename": stored_name,
    }


async def delete_file(public_id: str) -> bool:
    """Local media papkadagi faylni o'chirish."""
    target = _resolve_relative_path(public_id)
    if target is None or not target.exists() or not target.is_file():
        return False

    await asyncio.to_thread(target.unlink)

    media_root = _media_root().resolve()
    current = target.parent
    while current != media_root:
        try:
            current.rmdir()
        except OSError:
            break
        current = current.parent

    return True


async def delete_file_by_url(file_url: str | None) -> bool:
    """Local media URL bo'yicha faylni o'chirish."""
    public_id = extract_public_id(file_url)
    if not public_id:
        return False
    return await delete_file(public_id)


async def delete_files_by_urls(urls: Iterable[str | None]) -> None:
    """Bir nechta local media URL larni xavfsiz o'chirish."""
    seen: set[str] = set()
    for url in urls:
        public_id = extract_public_id(url)
        if not public_id or public_id in seen:
            continue
        seen.add(public_id)
        await delete_file(public_id)
