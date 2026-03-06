"""
Test Categories — public list, admin CRUD, slug unique, cascade check
"""
import uuid
from app.models.category import Category
from app.models.product import Product


class TestPublicCategories:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/categories")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    def test_list_active_only(self, client, db):
        db.add(Category(name_uz="Suv", slug="suv", is_active=True))
        db.add(Category(name_uz="Noaktiv", slug="noaktiv", is_active=False))
        db.commit()
        resp = client.get("/api/v1/categories")
        assert len(resp.json()["data"]) == 1
        assert resp.json()["data"][0]["name_uz"] == "Suv"

    def test_list_ordered(self, client, db):
        db.add(Category(name_uz="C", slug="c", order_index=2, is_active=True))
        db.add(Category(name_uz="A", slug="a", order_index=0, is_active=True))
        db.add(Category(name_uz="B", slug="b", order_index=1, is_active=True))
        db.commit()
        resp = client.get("/api/v1/categories")
        names = [c["name_uz"] for c in resp.json()["data"]]
        assert names == ["A", "B", "C"]


class TestAdminCategories:
    def test_create(self, client, admin_headers):
        resp = client.post("/api/v1/admin/categories", headers=admin_headers, json={
            "name_uz": "Ichimlik suvi",
            "slug": "ichimlik-suvi",
        })
        assert resp.status_code == 201
        assert resp.json()["data"]["slug"] == "ichimlik-suvi"

    def test_create_unauthenticated(self, client):
        resp = client.post("/api/v1/admin/categories", json={"name_uz": "X", "slug": "x"})
        assert resp.status_code in (401, 403)

    def test_slug_unique_on_create(self, client, admin_headers, db):
        db.add(Category(name_uz="Suv", slug="suv"))
        db.commit()
        resp = client.post("/api/v1/admin/categories", headers=admin_headers, json={
            "name_uz": "Boshqa", "slug": "suv",
        })
        assert resp.status_code == 409

    def test_slug_unique_on_update(self, client, admin_headers, db):
        cat1 = Category(name_uz="A", slug="a")
        cat2 = Category(name_uz="B", slug="b")
        db.add_all([cat1, cat2])
        db.commit()
        db.refresh(cat2)

        resp = client.put(f"/api/v1/admin/categories/{cat2.id}", headers=admin_headers, json={
            "slug": "a",  # allaqachon mavjud
        })
        assert resp.status_code == 409

    def test_update_own_slug_ok(self, client, admin_headers, db):
        cat = Category(name_uz="Test", slug="test")
        db.add(cat)
        db.commit()
        db.refresh(cat)

        resp = client.put(f"/api/v1/admin/categories/{cat.id}", headers=admin_headers, json={
            "slug": "test",  # o'zi — o'tishi kerak
            "name_uz": "Yangilangan",
        })
        assert resp.status_code == 200

    def test_update_not_found(self, client, admin_headers):
        resp = client.put(f"/api/v1/admin/categories/{uuid.uuid4()}", headers=admin_headers, json={
            "name_uz": "X",
        })
        assert resp.status_code == 404

    def test_delete(self, client, admin_headers, db):
        cat = Category(name_uz="O'chiriladigan", slug="del")
        db.add(cat)
        db.commit()
        db.refresh(cat)

        resp = client.delete(f"/api/v1/admin/categories/{cat.id}", headers=admin_headers)
        assert resp.status_code == 200

    def test_delete_with_products_blocked(self, client, admin_headers, db):
        cat = Category(name_uz="Busy", slug="busy")
        db.add(cat)
        db.commit()
        db.refresh(cat)

        db.add(Product(name_uz="Mahsulot", category_id=cat.id))
        db.commit()

        resp = client.delete(f"/api/v1/admin/categories/{cat.id}", headers=admin_headers)
        assert resp.status_code == 409
        assert "mahsulot" in resp.json()["message"].lower()

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete(f"/api/v1/admin/categories/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404

    def test_admin_list_all(self, client, admin_headers, db):
        db.add(Category(name_uz="Aktiv", slug="aktiv", is_active=True))
        db.add(Category(name_uz="Noaktiv", slug="noaktiv", is_active=False))
        db.commit()

        resp = client.get("/api/v1/admin/categories", headers=admin_headers)
        assert resp.status_code == 200
        # Admin barcha kategoriylarni ko'radi
        assert len(resp.json()["data"]) == 2
