"""
ECO COMPANY — Cloudflare R2 Storage Service
S3-compatible boto3 orqali R2 bilan ishlash
"""
import asyncio
import uuid
import re
from pathlib import Path
from urllib.parse import urlparse

from app.config import settings

_SAFE_PART_RE = re.compile(r"[^a-zA-Z0-9_-]+")
_SAFE_EXT_RE = re.compile(r"[^a-zA-Z0-9.]")


def _get_r2_client():
    """Cloudflare R2 boto3 client yaratish (S3-compatible)."""
    try:
        import boto3
        from botocore.config import Config
    except ImportError as e:
        raise RuntimeError("Cloudflare R2 uchun 'boto3' paketi o'rnatilmagan: pip install boto3") from e

    endpoint_url = f"https://{settings.R2_ACCOUNT_ID}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        aws_access_key_id=settings.R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.R2_SECRET_ACCESS_KEY,
        config=Config(
            signature_version="s3v4",
            retries={"max_attempts": 3, "mode": "standard"},
            connect_timeout=5,
            read_timeout=30,
        ),
        region_name="auto",
    )


def _sanitize_folder(folder: str | None) -> str:
    raw_folder = (folder or "ecocompany").strip().replace("\\", "/")
    parts = []
    for part in raw_folder.split("/"):
        part = part.strip()
        if not part or part in {".", ".."}:
            continue
        safe = _SAFE_PART_RE.sub("-", part).strip("-")
        if safe:
            parts.append(safe.lower())
    return "/".join(parts) if parts else "ecocompany"


def _unique_filename(filename: str | None) -> str:
    original_name = Path(filename or "file").name
    suffix = _SAFE_EXT_RE.sub("", Path(original_name).suffix.lower())[:10]
    stem = _SAFE_PART_RE.sub("-", Path(original_name).stem).strip("-").lower() or "file"
    return f"{stem}-{uuid.uuid4().hex[:12]}{suffix}"


def build_r2_url(key: str) -> str:
    """R2 public URL qurilishi."""
    public_url = settings.R2_PUBLIC_URL.rstrip("/")
    if public_url:
        return f"{public_url}/{key.lstrip('/')}"
    raise RuntimeError("R2_PUBLIC_URL sozlanmagan")


import mimetypes
from urllib.parse import urlparse


def extract_r2_key(file_url: str | None) -> str | None:
    """R2 public URL dan object key ni ajratib olish."""
    if not file_url:
        return None

    clean_url = file_url.strip()
    try:
        parsed = urlparse(clean_url)
    except ValueError:
        return None

    public_url = settings.R2_PUBLIC_URL.rstrip("/")
    if public_url:
        try:
            public = urlparse(public_url)
        except ValueError:
            return None
        base_path = public.path.rstrip("/")
        if parsed.scheme == public.scheme and parsed.netloc.lower() == public.netloc.lower():
            if parsed.path.startswith(base_path + "/"):
                key = parsed.path[len(base_path):].lstrip("/")
                return key or None

    # If it's already a relative path / key (e.g. 'ecocompany/image-123.jpg')
    if not parsed.scheme and not clean_url.startswith("/") and "?" not in clean_url and "#" not in clean_url:
        return clean_url

    return None


def _upload_bytes_sync(data: bytes, key: str, content_type: str = "application/octet-stream") -> None:
    """Sync: R2 ga bytes yuklash."""
    client = _get_r2_client()
    client.put_object(
        Bucket=settings.R2_BUCKET_NAME,
        Key=key,
        Body=data,
        ContentType=content_type,
    )


def _delete_object_sync(key: str) -> bool:
    """Sync: R2 dan faylni o'chirish."""
    try:
        client = _get_r2_client()
        client.delete_object(Bucket=settings.R2_BUCKET_NAME, Key=key)
        return True
    except Exception:
        return False


async def upload_bytes(
    data: bytes,
    folder: str = "ecocompany",
    filename: str = "",
    base_url: str | None = None,
) -> dict:
    """Bytes ko'rinishidagi faylni R2 ga yuklash."""
    safe_folder = _sanitize_folder(folder)
    stored_name = _unique_filename(filename)
    key = f"{safe_folder}/{stored_name}"

    content_type, _ = mimetypes.guess_type(stored_name)
    if not content_type:
        content_type = "application/octet-stream"

    await asyncio.to_thread(_upload_bytes_sync, data, key, content_type)

    return {
        "url": build_r2_url(key),
        "public_id": key,
        "bytes": len(data),
        "filename": stored_name,
    }


async def delete_file(key: str) -> bool:
    """R2 dan faylni key bo'yicha o'chirish."""
    if not key:
        return False
    return await asyncio.to_thread(_delete_object_sync, key)
