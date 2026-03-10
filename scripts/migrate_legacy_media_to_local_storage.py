#!/usr/bin/env python3
"""
ECO COMPANY — Legacy media URL'larni local storage'ga migratsiya qilish
"""
import argparse
import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.category import Category
from app.models.certificate import Certificate
from app.models.gallery import GalleryItem
from app.models.product import Product
from app.models.setting import SiteSetting
from app.services import storage_service

LEGACY_MEDIA_HOST_MARKERS = (
    "res." "clou" "dinary" ".com",
    "clou" "dinary" ".com",
)


def is_legacy_media_url(value: str | None) -> bool:
    return bool(value) and any(marker in value for marker in LEGACY_MEDIA_HOST_MARKERS)


def derive_filename(url: str, fallback: str) -> str:
    parsed = urlparse(url)
    name = Path(parsed.path).name
    return name or fallback


async def download_and_store(
    client: httpx.AsyncClient,
    url: str,
    folder: str,
    fallback_filename: str,
    base_url: str,
    cache: dict[str, str],
) -> str:
    if url in cache:
        return cache[url]

    response = await client.get(url, timeout=60.0)
    response.raise_for_status()
    stored = await storage_service.upload_bytes(
        data=response.content,
        folder=folder,
        filename=derive_filename(url, fallback_filename),
        base_url=base_url,
    )
    cache[url] = stored["url"]
    return stored["url"]


async def migrate(base_url: str, clear_missing: bool = False) -> tuple[int, list[str]]:
    db = SessionLocal()
    cache: dict[str, str] = {}
    updated = 0
    errors: list[str] = []

    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            for product in db.query(Product).all():
                images = list(product.images or [])
                changed = False
                for idx, image_url in enumerate(images):
                    if not is_legacy_media_url(image_url):
                        continue
                    try:
                        images[idx] = await download_and_store(
                            client=client,
                            url=image_url,
                            folder="products",
                            fallback_filename=f"product-{product.id}-{idx}.bin",
                            base_url=base_url,
                            cache=cache,
                        )
                        changed = True
                    except Exception as exc:
                        errors.append(f"Product {product.id} image {idx}: {exc}")
                        if clear_missing:
                            images[idx] = None
                            changed = True
                if changed:
                    product.images = [image for image in images if image]
                    updated += 1

            for certificate in db.query(Certificate).all():
                changed = False
                if is_legacy_media_url(certificate.file_url):
                    try:
                        certificate.file_url = await download_and_store(
                            client=client,
                            url=certificate.file_url,
                            folder="certificates",
                            fallback_filename=f"certificate-{certificate.id}.bin",
                            base_url=base_url,
                            cache=cache,
                        )
                        changed = True
                    except Exception as exc:
                        errors.append(f"Certificate {certificate.id} file_url: {exc}")
                        if clear_missing:
                            certificate.file_url = ""
                            changed = True

                if is_legacy_media_url(certificate.preview_url):
                    try:
                        certificate.preview_url = await download_and_store(
                            client=client,
                            url=certificate.preview_url,
                            folder="certificates",
                            fallback_filename=f"certificate-preview-{certificate.id}.bin",
                            base_url=base_url,
                            cache=cache,
                        )
                        changed = True
                    except Exception as exc:
                        errors.append(f"Certificate {certificate.id} preview_url: {exc}")
                        if clear_missing:
                            certificate.preview_url = None
                            changed = True

                if changed:
                    updated += 1

            for item in db.query(GalleryItem).all():
                changed = False
                if is_legacy_media_url(item.file_url):
                    try:
                        item.file_url = await download_and_store(
                            client=client,
                            url=item.file_url,
                            folder="gallery",
                            fallback_filename=f"gallery-item-{item.id}.bin",
                            base_url=base_url,
                            cache=cache,
                        )
                        changed = True
                    except Exception as exc:
                        errors.append(f"GalleryItem {item.id} file_url: {exc}")
                        if clear_missing:
                            item.file_url = ""
                            changed = True

                if is_legacy_media_url(item.thumbnail_url):
                    try:
                        item.thumbnail_url = await download_and_store(
                            client=client,
                            url=item.thumbnail_url,
                            folder="gallery",
                            fallback_filename=f"gallery-thumb-{item.id}.bin",
                            base_url=base_url,
                            cache=cache,
                        )
                        changed = True
                    except Exception as exc:
                        errors.append(f"GalleryItem {item.id} thumbnail_url: {exc}")
                        if clear_missing:
                            item.thumbnail_url = None
                            changed = True

                if changed:
                    updated += 1

            for category in db.query(Category).all():
                if not is_legacy_media_url(category.icon):
                    continue
                try:
                    category.icon = await download_and_store(
                        client=client,
                        url=category.icon,
                        folder="categories",
                        fallback_filename=f"category-{category.id}.bin",
                        base_url=base_url,
                        cache=cache,
                    )
                    updated += 1
                except Exception as exc:
                    errors.append(f"Category {category.id} icon: {exc}")
                    if clear_missing:
                        category.icon = None
                        updated += 1

            for setting in db.query(SiteSetting).all():
                if not is_legacy_media_url(setting.value):
                    continue
                try:
                    setting.value = await download_and_store(
                        client=client,
                        url=setting.value,
                        folder="settings",
                        fallback_filename=f"setting-{setting.key}.bin",
                        base_url=base_url,
                        cache=cache,
                    )
                    updated += 1
                except Exception as exc:
                    errors.append(f"SiteSetting {setting.key}: {exc}")
                    if clear_missing:
                        setting.value = ""
                        updated += 1

            db.commit()
            return updated, errors
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Legacy media URL'larni local storage'ga ko'chirish")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Local media URL'lari uchun backend public origin. Masalan: https://api.ecocompany.uz",
    )
    parser.add_argument(
        "--clear-missing",
        action="store_true",
        help="Agar eski remote media URL 404 bo'lsa, DB'dan o'chirib tashlaydi",
    )
    args = parser.parse_args()

    updated, errors = asyncio.run(migrate(args.base_url.rstrip("/"), clear_missing=args.clear_missing))
    print(f"Ko'chirilgan yozuvlar: {updated}")
    if errors:
        print("Xatolar:")
        for error in errors:
            print(f"- {error}")


if __name__ == "__main__":
    main()
