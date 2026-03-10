"""
ECO COMPANY — SEO Router
Dynamic robots.txt va sitemap XML fayllari
"""
from datetime import date, datetime
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.certificate import Certificate
from app.models.gallery import GalleryAlbum, GalleryItem
from app.models.product import Product

router = APIRouter(include_in_schema=False)


def _public_site_url(request: Request) -> str:
    if settings.PUBLIC_BASE_URL:
        return settings.PUBLIC_BASE_URL.rstrip("/")
    return str(request.base_url).rstrip("/")


def _xml_response(content: str, media_type: str) -> Response:
    return Response(
        content=content,
        media_type=media_type,
        headers={"Cache-Control": "public, max-age=3600"},
    )


def _format_lastmod(value: datetime | date | None) -> str | None:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return None


def _render_urlset(entries: list[str], *, image_namespace: bool = False) -> str:
    ns = ' xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' if image_namespace else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"{ns}>\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


def _render_url_entry(
    loc: str,
    *,
    lastmod: str | None = None,
    changefreq: str | None = None,
    priority: str | None = None,
    images: list[dict[str, str | None]] | None = None,
) -> str:
    parts = ["  <url>", f"    <loc>{escape(loc)}</loc>"]
    if lastmod:
        parts.append(f"    <lastmod>{escape(lastmod)}</lastmod>")
    if changefreq:
        parts.append(f"    <changefreq>{escape(changefreq)}</changefreq>")
    if priority:
        parts.append(f"    <priority>{escape(priority)}</priority>")
    if images:
        for image in images:
            image_loc = image.get("loc")
            if not image_loc:
                continue
            parts.append("    <image:image>")
            parts.append(f"      <image:loc>{escape(str(image_loc))}</image:loc>")
            if image.get("title"):
                parts.append(f"      <image:title>{escape(str(image['title']))}</image:title>")
            if image.get("caption"):
                parts.append(f"      <image:caption>{escape(str(image['caption']))}</image:caption>")
            parts.append("    </image:image>")
    parts.append("  </url>")
    return "\n".join(parts)


def _sitemap_index(base_url: str) -> str:
    today = date.today().isoformat()
    urls = [
        f"{base_url}/sitemaps/pages.xml",
        f"{base_url}/sitemaps/products.xml",
        f"{base_url}/sitemaps/media.xml",
    ]
    entries = [
        (
            "  <sitemap>\n"
            f"    <loc>{escape(url)}</loc>\n"
            f"    <lastmod>{today}</lastmod>\n"
            "  </sitemap>"
        )
        for url in urls
    ]
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(entries)
        + "\n</sitemapindex>\n"
    )


@router.api_route("/robots.txt", methods=["GET", "HEAD"])
async def robots_txt(request: Request):
    base_url = _public_site_url(request)
    content = "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {base_url}/sitemap.xml",
            "",
        ]
    )
    return _xml_response(content, "text/plain; charset=utf-8")


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"])
async def sitemap_index(request: Request):
    return _xml_response(_sitemap_index(_public_site_url(request)), "application/xml; charset=utf-8")


@router.api_route("/sitemaps/pages.xml", methods=["GET", "HEAD"])
async def pages_sitemap(request: Request):
    base_url = _public_site_url(request)
    entries = [
        _render_url_entry(f"{base_url}/", changefreq="weekly", priority="1.0"),
        _render_url_entry(f"{base_url}/products", changefreq="daily", priority="0.9"),
        _render_url_entry(f"{base_url}/about", changefreq="monthly", priority="0.8"),
        _render_url_entry(f"{base_url}/certificates", changefreq="weekly", priority="0.8"),
        _render_url_entry(f"{base_url}/gallery", changefreq="weekly", priority="0.8"),
        _render_url_entry(f"{base_url}/contact", changefreq="monthly", priority="0.7"),
    ]
    return _xml_response(_render_urlset(entries), "application/xml; charset=utf-8")


@router.api_route("/sitemaps/products.xml", methods=["GET", "HEAD"])
async def products_sitemap(request: Request, db: Session = Depends(get_db)):
    base_url = _public_site_url(request)
    products = (
        db.query(Product)
        .filter(Product.is_active == True)
        .order_by(Product.updated_at.desc().nullslast(), Product.created_at.desc())
        .all()
    )

    entries: list[str] = []
    for product in products:
        name = product.name_uz or product.name_ru or product.name_en or "Product"
        description = product.desc_uz or product.desc_ru or product.desc_en or name
        images = [
            {
                "loc": str(image),
                "title": name,
                "caption": description[:200],
            }
            for image in (product.images or [])
            if image
        ]
        entries.append(
            _render_url_entry(
                f"{base_url}/products/{product.id}",
                lastmod=_format_lastmod(product.updated_at or product.created_at),
                changefreq="weekly",
                priority="0.7",
                images=images,
            )
        )

    return _xml_response(_render_urlset(entries, image_namespace=True), "application/xml; charset=utf-8")


@router.api_route("/sitemaps/media.xml", methods=["GET", "HEAD"])
async def media_sitemap(request: Request, db: Session = Depends(get_db)):
    base_url = _public_site_url(request)
    entries: list[str] = []

    certificates = (
        db.query(Certificate)
        .filter(Certificate.is_active == True)
        .order_by(Certificate.updated_at.desc().nullslast(), Certificate.created_at.desc())
        .all()
    )
    if certificates:
        entries.append(
            _render_url_entry(
                f"{base_url}/certificates",
                lastmod=_format_lastmod(max((c.updated_at or c.created_at) for c in certificates)),
                changefreq="weekly",
                priority="0.6",
                images=[
                    {
                        "loc": c.preview_url or c.file_url,
                        "title": c.title_uz or c.title_ru or c.title_en or "Certificate",
                        "caption": c.title_uz or c.title_ru or c.title_en or "Certificate",
                    }
                    for c in certificates
                    if (c.preview_url or c.file_url)
                ],
            )
        )

    albums = (
        db.query(GalleryAlbum)
        .filter(GalleryAlbum.is_active == True)
        .order_by(GalleryAlbum.updated_at.desc().nullslast(), GalleryAlbum.created_at.desc())
        .all()
    )
    if albums:
        gallery_images = (
            db.query(GalleryItem, GalleryAlbum)
            .join(GalleryAlbum, GalleryItem.album_id == GalleryAlbum.id)
            .filter(GalleryAlbum.is_active == True, GalleryItem.is_active == True, GalleryItem.file_type == "image")
            .order_by(GalleryAlbum.order_index.asc(), GalleryItem.order_index.asc())
            .all()
        )
        entries.append(
            _render_url_entry(
                f"{base_url}/gallery",
                lastmod=_format_lastmod(max((a.updated_at or a.created_at) for a in albums)),
                changefreq="weekly",
                priority="0.6",
                images=[
                    {
                        "loc": item.thumbnail_url or item.file_url,
                        "title": album.title_uz or album.title_ru or album.title_en or "Gallery",
                        "caption": album.description_uz or album.title_uz or "Gallery image",
                    }
                    for item, album in gallery_images
                    if (item.thumbnail_url or item.file_url)
                ],
            )
        )

    return _xml_response(_render_urlset(entries, image_namespace=True), "application/xml; charset=utf-8")
