"""
Test Gallery — albums, items, certificates, instagram, settings
"""
import uuid
from app.models.certificate import Certificate
from app.models.gallery import GalleryAlbum, GalleryItem
from app.models.setting import SiteSetting


class TestPublicCertificates:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/certificates")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_list_all(self, client, db):
        db.add(Certificate(title_uz="ISO 9001", file_url="https://x.com/cert.jpg", is_active=True))
        db.add(Certificate(title_uz="Noaktiv", file_url="https://x.com/n.jpg", is_active=False))
        db.commit()
        resp = client.get("/api/v1/certificates")
        assert len(resp.json()["data"]) == 2

    def test_list_ordered(self, client, db):
        db.add(Certificate(title_uz="B", file_url="https://x.com/b.jpg", order_index=1, is_active=True))
        db.add(Certificate(title_uz="A", file_url="https://x.com/a.jpg", order_index=0, is_active=True))
        db.commit()
        resp = client.get("/api/v1/certificates")
        titles = [c["title_uz"] for c in resp.json()["data"]]
        assert titles == ["A", "B"]


class TestAdminCertificates:
    def test_create(self, client, admin_headers):
        resp = client.post("/api/v1/admin/certificates", headers=admin_headers, json={
            "title_uz": "GOST 2024",
            "file_url": "https://example.com/gost.jpg",
            "file_type": "image",
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["title_uz"] == "GOST 2024"
        assert resp.json()["data"]["is_active"] is True
        assert resp.json()["data"]["is_downloadable"] is True

    def test_reject_pdf(self, client, admin_headers):
        resp = client.post("/api/v1/admin/certificates", headers=admin_headers, json={
            "title_uz": "PDF cert",
            "file_url": "https://example.com/gost.pdf",
            "file_type": "pdf",
        })
        assert resp.status_code == 422

    def test_update(self, client, admin_headers, db):
        cert = Certificate(title_uz="Eski", file_url="https://x.com/c.jpg")
        db.add(cert)
        db.commit()
        db.refresh(cert)

        resp = client.put(f"/api/v1/admin/certificates/{cert.id}", headers=admin_headers, json={
            "title_uz": "Yangilangan",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["title_uz"] == "Yangilangan"

    def test_delete(self, client, admin_headers, db):
        cert = Certificate(title_uz="Del", file_url="https://x.com/d.jpg")
        db.add(cert)
        db.commit()
        db.refresh(cert)

        resp = client.delete(f"/api/v1/admin/certificates/{cert.id}", headers=admin_headers)
        assert resp.status_code == 200

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete(f"/api/v1/admin/certificates/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404


class TestPublicGallery:
    def test_albums_empty(self, client):
        resp = client.get("/api/v1/gallery/albums")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_albums_active_only(self, client, db):
        db.add(GalleryAlbum(title_uz="Aktiv", is_active=True))
        db.add(GalleryAlbum(title_uz="Noaktiv", is_active=False))
        db.commit()
        resp = client.get("/api/v1/gallery/albums")
        assert len(resp.json()["data"]) == 1

    def test_album_detail(self, client, db):
        album = GalleryAlbum(title_uz="Fabrika", is_active=True)
        db.add(album)
        db.commit()
        db.refresh(album)

        db.add(GalleryItem(album_id=album.id, file_url="https://x.com/1.jpg"))
        db.add(GalleryItem(album_id=album.id, file_url="https://x.com/2.jpg"))
        db.commit()

        resp = client.get(f"/api/v1/gallery/albums/{album.id}")
        assert resp.status_code == 200

    def test_album_not_found(self, client):
        resp = client.get(f"/api/v1/gallery/albums/{uuid.uuid4()}")
        assert resp.status_code == 404

    def test_albums_filter_category(self, client, db):
        db.add(GalleryAlbum(title_uz="Ishlab chiqarish", category="production", is_active=True))
        db.add(GalleryAlbum(title_uz="Ofis", category="office", is_active=True))
        db.commit()

        resp = client.get("/api/v1/gallery/albums?category=production")
        assert len(resp.json()["data"]) == 1

    def test_albums_include_cover_metadata(self, client, db):
        album = GalleryAlbum(title_uz="Fabrika", is_active=True)
        db.add(album)
        db.commit()
        db.refresh(album)

        db.add(GalleryItem(
            album_id=album.id,
            file_url="https://x.com/video.mp4",
            thumbnail_url="https://x.com/video-thumb.jpg",
            file_type="video",
            is_active=True,
        ))
        db.add(GalleryItem(
            album_id=album.id,
            file_url="https://x.com/hidden.jpg",
            file_type="image",
            is_active=False,
        ))
        db.commit()

        resp = client.get("/api/v1/gallery/albums")
        assert resp.status_code == 200
        data = resp.json()["data"][0]
        assert data["items_count"] == 1
        assert data["cover_url"] == "https://x.com/video.mp4"
        assert data["cover_thumbnail_url"] == "https://x.com/video-thumb.jpg"
        assert data["cover_file_type"] == "video"
        assert len(data["preview_items"]) == 1
        assert data["preview_items"][0]["file_url"] == "https://x.com/video.mp4"


class TestAdminGallery:
    def test_create_album(self, client, admin_headers):
        resp = client.post("/api/v1/admin/gallery/albums", headers=admin_headers, json={
            "title_uz": "Yangi album",
            "category": "team",
        })
        assert resp.status_code == 201

    def test_update_album(self, client, admin_headers, db):
        album = GalleryAlbum(title_uz="Eski")
        db.add(album)
        db.commit()
        db.refresh(album)

        resp = client.put(f"/api/v1/admin/gallery/albums/{album.id}", headers=admin_headers, json={
            "title_uz": "Yangi nom",
        })
        assert resp.status_code == 200

    def test_delete_album_cascade(self, client, admin_headers, db):
        album = GalleryAlbum(title_uz="Del album")
        db.add(album)
        db.commit()
        db.refresh(album)

        db.add(GalleryItem(album_id=album.id, file_url="https://x.com/item.jpg"))
        db.commit()

        resp = client.delete(f"/api/v1/admin/gallery/albums/{album.id}", headers=admin_headers)
        assert resp.status_code == 200
        # Items ham o'chirilgan bo'lishi kerak
        assert db.query(GalleryItem).filter(GalleryItem.album_id == album.id).count() == 0

    def test_add_item(self, client, admin_headers, db):
        album = GalleryAlbum(title_uz="Test")
        db.add(album)
        db.commit()
        db.refresh(album)

        resp = client.post(f"/api/v1/admin/gallery/albums/{album.id}/items", headers=admin_headers, json={
            "file_url": "https://x.com/new.jpg",
            "file_type": "image",
        })
        assert resp.status_code == 201

    def test_delete_item(self, client, admin_headers, db):
        album = GalleryAlbum(title_uz="A")
        db.add(album)
        db.commit()
        db.refresh(album)

        item = GalleryItem(album_id=album.id, file_url="https://x.com/d.jpg")
        db.add(item)
        db.commit()
        db.refresh(item)

        resp = client.delete(
            f"/api/v1/admin/gallery/albums/{album.id}/items/{item.id}",
            headers=admin_headers,
        )
        assert resp.status_code == 200


class TestPublicSettings:
    def test_public_settings(self, client, db):
        db.add(SiteSetting(key="phone_1", value="+998901234567", is_public=True))
        db.add(SiteSetting(key="secret_key", value="secret", is_public=False))
        db.commit()

        resp = client.get("/api/v1/settings/public")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert "phone_1" in data
        assert "secret_key" not in data

    def test_public_settings_excludes_env_managed_keys(self, client, db):
        db.add(SiteSetting(key="smtp_password", value="secret", is_public=True))
        db.add(SiteSetting(key="telegram_bot_token", value="token", is_public=True))
        db.commit()

        resp = client.get("/api/v1/settings/public")
        assert resp.status_code == 200
        assert resp.json()["data"] == {}

    def test_public_settings_empty(self, client):
        resp = client.get("/api/v1/settings/public")
        assert resp.status_code == 200
        assert resp.json()["data"] == {}


class TestAdminSettings:
    def test_list(self, client, admin_headers, db):
        db.add(SiteSetting(key="email", value="info@eco.uz"))
        db.commit()
        resp = client.get("/api/v1/admin/settings", headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_editor_list_hides_non_public_and_env_managed(self, client, editor_headers, db):
        db.add(SiteSetting(key="email", value="info@eco.uz", is_public=True))
        db.add(SiteSetting(key="ai_system_prompt", value="secret prompt", is_public=False))
        db.add(SiteSetting(key="smtp_password", value="super-secret", is_public=True))
        db.commit()

        resp = client.get("/api/v1/admin/settings", headers=editor_headers)
        assert resp.status_code == 200
        keys = {item["key"] for item in resp.json()["data"]}
        assert "email" in keys
        assert "ai_system_prompt" not in keys
        assert "smtp_password" not in keys

    def test_upsert_existing(self, client, admin_headers, db):
        db.add(SiteSetting(key="phone_1", value="old"))
        db.commit()
        resp = client.put("/api/v1/admin/settings/phone_1", headers=admin_headers, json={
            "value": "+998901234567",
        })
        assert resp.status_code == 200

    def test_upsert_new(self, client, admin_headers):
        resp = client.put("/api/v1/admin/settings/new_key", headers=admin_headers, json={
            "value": "new_value",
        })
        assert resp.status_code == 200

    def test_upsert_env_managed_key_rejected(self, client, admin_headers):
        resp = client.put("/api/v1/admin/settings/smtp_password", headers=admin_headers, json={
            "value": "secret",
        })
        assert resp.status_code == 400

    def test_bulk_update(self, client, admin_headers, db):
        db.add(SiteSetting(key="k1", value="v1"))
        db.commit()

        resp = client.put("/api/v1/admin/settings/bulk", headers=admin_headers, json=[
            {"key": "k1", "value": "updated"},
            {"key": "k2", "value": "new"},
        ])
        assert resp.status_code == 200
        assert "2" in resp.json()["message"]

    def test_bulk_update_rejects_env_managed_keys(self, client, admin_headers):
        resp = client.put("/api/v1/admin/settings/bulk", headers=admin_headers, json=[
            {"key": "smtp_password", "value": "secret"},
        ])
        assert resp.status_code == 400

    def test_bulk_update_marks_prompt_non_public(self, client, admin_headers, db):
        resp = client.put("/api/v1/admin/settings/bulk", headers=admin_headers, json=[
            {"key": "ai_system_prompt", "value": "Updated system prompt for admins"},
        ])
        assert resp.status_code == 200

        prompt = db.query(SiteSetting).filter(SiteSetting.key == "ai_system_prompt").first()
        assert prompt is not None
        assert prompt.is_public is False


class TestInstagramPosts:
    def test_public_posts_empty(self, client):
        resp = client.get("/api/v1/instagram/posts")
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_admin_token_status(self, client, admin_headers):
        resp = client.get("/api/v1/admin/instagram/token-status", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["mode"] == "manual"
        assert "link_count" in data

    def test_save_instagram_links(self, client, admin_headers):
        resp = client.put("/api/v1/admin/instagram/links", headers=admin_headers, json={
            "items": [
                {"url": "https://www.instagram.com/reel/C7M1abcd123/"},
            ]
        })
        assert resp.status_code == 200
        assert resp.json()["data"][0]["embed_url"].endswith("/embed")

        public_resp = client.get("/api/v1/instagram/posts")
        assert public_resp.status_code == 200
        assert len(public_resp.json()["data"]) == 1
