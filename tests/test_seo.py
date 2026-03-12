from app.config import settings
from app.models.certificate import Certificate
from app.models.gallery import GalleryAlbum, GalleryItem
from app.models.product import Product
from app.models.setting import SiteSetting


class TestSEORoutes:
    def test_robots_txt_exposes_root_sitemap(self, client, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "")
        response = client.get("/robots.txt")

        assert response.status_code == 200
        assert "User-agent: *" in response.text
        assert "Sitemap: http://testserver/sitemap.xml" in response.text

    def test_sitemap_index_lists_sub_sitemaps(self, client, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "")
        response = client.get("/sitemap.xml")

        assert response.status_code == 200
        assert "/sitemaps/pages.xml" in response.text
        assert "/sitemaps/products.xml" in response.text
        assert "/sitemaps/media.xml" in response.text

    def test_pages_sitemap_uses_dynamic_images_and_lastmod(self, client, db, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "")
        db.add(SiteSetting(key="hero_image_url", value="http://testserver/media/settings/hero.jpg", is_public=True))
        db.add(SiteSetting(key="logo_url", value="http://testserver/media/settings/logo.png", is_public=True))
        db.add(Product(name_uz="Premium suv", images=["http://testserver/media/products/suv-1.jpg"], is_active=True))
        db.commit()

        response = client.get("/sitemaps/pages.xml")

        assert response.status_code == 200
        assert "/products" in response.text
        assert "http://testserver/media/settings/hero.jpg" in response.text
        assert "http://testserver/media/settings/logo.png" in response.text
        assert "<image:image>" in response.text

    def test_products_sitemap_contains_product_urls_and_images(self, client, db, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "")
        product = Product(
            name_uz="Premium suv",
            desc_uz="Toza ichimlik suvi",
            images=[
                "http://testserver/media/products/suv-1.jpg",
                "http://testserver/media/products/suv-2.jpg",
            ],
            is_active=True,
        )
        db.add(product)
        db.commit()
        db.refresh(product)

        response = client.get("/sitemaps/products.xml")

        assert response.status_code == 200
        assert f"/products/{product.id}" in response.text
        assert "<image:image>" in response.text
        assert "http://testserver/media/products/suv-1.jpg" in response.text
        assert "Premium suv" in response.text

    def test_media_sitemap_contains_certificate_and_gallery_images(self, client, db, monkeypatch):
        monkeypatch.setattr(settings, "PUBLIC_BASE_URL", "")
        certificate = Certificate(
            title_uz="ISO sertifikat",
            file_url="http://testserver/media/certificates/cert.jpg",
            preview_url="http://testserver/media/certificates/cert-preview.jpg",
            file_type="image",
            is_active=True,
        )
        album = GalleryAlbum(
            title_uz="Ish jarayoni",
            description_uz="O'rnatish rasmlari",
            is_active=True,
        )
        db.add_all([certificate, album])
        db.commit()
        db.refresh(album)

        item = GalleryItem(
            album_id=album.id,
            file_url="http://testserver/media/gallery/album-1.jpg",
            file_type="image",
            is_active=True,
        )
        db.add(item)
        db.commit()

        response = client.get("/sitemaps/media.xml")

        assert response.status_code == 200
        assert "/certificates" in response.text
        assert "/gallery" in response.text
        assert "http://testserver/media/certificates/cert-preview.jpg" in response.text
        assert "http://testserver/media/gallery/album-1.jpg" in response.text
