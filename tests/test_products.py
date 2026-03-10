"""
Test Products — public endpoints, admin CRUD, filters, pagination, computed fields
"""
import uuid
from app.models.product import Product
from app.models.category import Category


class TestPublicProducts:
    def test_list_empty(self, client):
        resp = client.get("/api/v1/products")
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["items"] == []
        assert data["total"] == 0
        assert data["page"] == 1

    def test_list_active_only(self, client, db):
        db.add(Product(name_uz="Aktiv", is_active=True))
        db.add(Product(name_uz="Noaktiv", is_active=False))
        db.commit()
        resp = client.get("/api/v1/products")
        assert resp.json()["data"]["total"] == 1

    def test_list_pagination(self, client, db):
        for i in range(25):
            db.add(Product(name_uz=f"Suv-{i}", is_active=True))
        db.commit()

        resp1 = client.get("/api/v1/products?page=1&per_page=10")
        data1 = resp1.json()["data"]
        assert len(data1["items"]) == 10
        assert data1["total"] == 25
        assert data1["pages"] == 3

        resp3 = client.get("/api/v1/products?page=3&per_page=10")
        assert len(resp3.json()["data"]["items"]) == 5

    def test_filter_by_category(self, client, db):
        cat = Category(name_uz="Suv", slug="suv")
        db.add(cat)
        db.commit()
        db.refresh(cat)

        db.add(Product(name_uz="Suv 1L", category_id=cat.id, is_active=True))
        db.add(Product(name_uz="Filtr", is_active=True))
        db.commit()

        resp = client.get(f"/api/v1/products?category_id={cat.id}")
        assert resp.json()["data"]["total"] == 1
        assert resp.json()["data"]["items"][0]["name_uz"] == "Suv 1L"

    def test_filter_sale(self, client, db):
        db.add(Product(name_uz="Chegirmali", is_active=True, is_on_sale=True, discount_price=5000))
        db.add(Product(name_uz="Oddiy", is_active=True, is_on_sale=False))
        db.commit()

        resp = client.get("/api/v1/products?is_on_sale=true")
        assert resp.json()["data"]["total"] == 1

    def test_search_matches_across_catalog(self, client, db):
        db.add(Product(name_uz="Toza suv 1L", is_active=True))
        db.add(Product(name_uz="Mineral suv", name_ru="Минеральная вода", is_active=True))
        db.add(Product(name_uz="Filtr", is_active=True))
        db.commit()

        resp = client.get("/api/v1/products?search=suv")
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 2

    def test_featured_products(self, client, db):
        db.add(Product(name_uz="Featured 1", is_active=True, is_featured=True))
        db.add(Product(name_uz="Featured 2", is_active=True, is_featured=True))
        db.add(Product(name_uz="Normal", is_active=True, is_featured=False))
        db.commit()

        resp = client.get("/api/v1/products/featured")
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 2

    def test_single_product(self, client, db):
        product = Product(name_uz="Test suv", is_active=True, original_price=10000)
        db.add(product)
        db.commit()
        db.refresh(product)

        resp = client.get(f"/api/v1/products/{product.id}")
        assert resp.status_code == 200
        assert resp.json()["data"]["name_uz"] == "Test suv"

    def test_single_product_not_found(self, client):
        fake_id = uuid.uuid4()
        resp = client.get(f"/api/v1/products/{fake_id}")
        assert resp.status_code == 404

    def test_inactive_product_hidden(self, client, db):
        product = Product(name_uz="Yashirin", is_active=False)
        db.add(product)
        db.commit()
        db.refresh(product)

        resp = client.get(f"/api/v1/products/{product.id}")
        assert resp.status_code == 404


class TestAdminProducts:
    def test_create(self, client, admin_headers):
        resp = client.post("/api/v1/admin/products", headers=admin_headers, json={
            "name_uz": "Yangi suv",
            "name_ru": "Новая вода",
            "original_price": 15000,
            "is_active": True,
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["name_uz"] == "Yangi suv"
        assert data["name_ru"] == "Новая вода"

    def test_create_unauthenticated(self, client):
        resp = client.post("/api/v1/admin/products", json={"name_uz": "Test"})
        assert resp.status_code in (401, 403)

    def test_update(self, client, admin_headers, db):
        product = Product(name_uz="Eski", is_active=True)
        db.add(product)
        db.commit()
        db.refresh(product)

        resp = client.put(f"/api/v1/admin/products/{product.id}", headers=admin_headers, json={
            "name_uz": "Yangilangan",
            "original_price": 20000,
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["name_uz"] == "Yangilangan"

    def test_update_not_found(self, client, admin_headers):
        resp = client.put(f"/api/v1/admin/products/{uuid.uuid4()}", headers=admin_headers, json={
            "name_uz": "Test",
        })
        assert resp.status_code == 404

    def test_delete(self, client, admin_headers, db):
        product = Product(name_uz="O'chiriladigan")
        db.add(product)
        db.commit()
        db.refresh(product)

        resp = client.delete(f"/api/v1/admin/products/{product.id}", headers=admin_headers)
        assert resp.status_code == 200

        # Qayta tekshirish — o'chirilgan bo'lishi kerak
        assert db.query(Product).filter(Product.id == product.id).first() is None

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete(f"/api/v1/admin/products/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404

    def test_admin_list_with_search(self, client, admin_headers, db):
        db.add(Product(name_uz="Toza suv 1L"))
        db.add(Product(name_uz="Mineral suv 5L"))
        db.add(Product(name_uz="Filtr"))
        db.commit()

        resp = client.get("/api/v1/admin/products?search=suv", headers=admin_headers)
        assert resp.json()["data"]["total"] == 2

    def test_admin_list_filter_active(self, client, admin_headers, db):
        db.add(Product(name_uz="Aktiv", is_active=True))
        db.add(Product(name_uz="Noaktiv", is_active=False))
        db.commit()

        resp = client.get("/api/v1/admin/products?is_active=false", headers=admin_headers)
        assert resp.json()["data"]["total"] == 1

    def test_reorder(self, client, admin_headers, db):
        p1 = Product(name_uz="A", order_index=0)
        p2 = Product(name_uz="B", order_index=1)
        db.add_all([p1, p2])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)

        resp = client.post("/api/v1/admin/products/reorder", headers=admin_headers, json=[
            {"id": str(p1.id), "order_index": 1},
            {"id": str(p2.id), "order_index": 0},
        ])
        assert resp.status_code == 200
