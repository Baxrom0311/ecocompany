"""
Test Contacts — public submit, validation, admin list/read/unread/archive/delete
"""
import uuid
from app.models.contact import ContactMessage


class TestPublicContacts:
    def test_create_with_email(self, client):
        resp = client.post("/api/v1/contacts", json={
            "name": "Test User",
            "email": "test@example.com",
            "message": "Salom, suv haqida savol bor",
        })
        assert resp.status_code == 200
        assert resp.json()["success"] is True

    def test_create_with_phone(self, client):
        resp = client.post("/api/v1/contacts", json={
            "name": "Test User",
            "phone": "+998901234567",
            "message": "Narxlar haqida bilmoqchiman",
        })
        assert resp.status_code == 200

    def test_create_with_both(self, client):
        resp = client.post("/api/v1/contacts", json={
            "name": "Test User",
            "email": "t@t.com",
            "phone": "+998901234567",
            "subject": "Narxlar",
            "message": "Salom, narxlar haqida",
        })
        assert resp.status_code == 200

    def test_create_no_email_no_phone(self, client):
        resp = client.post("/api/v1/contacts", json={
            "name": "Test", "message": "Xabar",
        })
        assert resp.status_code == 422

    def test_create_short_name(self, client):
        resp = client.post("/api/v1/contacts", json={
            "name": "A",  # min 2
            "email": "t@t.com",
            "message": "Xabar",
        })
        assert resp.status_code == 422

    def test_create_short_message(self, client):
        resp = client.post("/api/v1/contacts", json={
            "name": "Test",
            "email": "t@t.com",
            "message": "Hi",  # min 10
        })
        assert resp.status_code == 422

    def test_create_empty_body(self, client):
        resp = client.post("/api/v1/contacts", json={})
        assert resp.status_code == 422

    def test_xss_sanitized(self, client, db):
        resp = client.post("/api/v1/contacts", json={
            "name": "<script>alert('xss')</script>Test User",
            "email": "test@example.com",
            "message": "<b>Test</b><script>xss</script> xabar matni",
        })
        assert resp.status_code == 200
        # DB da tekshirish — script tag tozalangan bo'lishi kerak
        contact = db.query(ContactMessage).first()
        assert "<script>" not in contact.name
        assert "<script>" not in contact.message


class TestAdminContacts:
    def _seed(self, db, count=5):
        for i in range(count):
            db.add(ContactMessage(
                name=f"User {i}",
                email=f"user{i}@test.com",
                message=f"Test xabar {i}",
                is_read=(i % 2 == 0),
            ))
        db.commit()

    def test_list(self, client, admin_headers, db):
        self._seed(db, 5)
        resp = client.get("/api/v1/admin/contacts", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 5

    def test_list_pagination(self, client, admin_headers, db):
        self._seed(db, 25)
        resp = client.get("/api/v1/admin/contacts?page=1&per_page=10", headers=admin_headers)
        data = resp.json()["data"]
        assert len(data["items"]) == 10
        assert data["pages"] == 3

    def test_list_filter_unread(self, client, admin_headers, db):
        self._seed(db, 4)
        resp = client.get("/api/v1/admin/contacts?is_read=false", headers=admin_headers)
        assert resp.json()["data"]["total"] == 2

    def test_list_unauthenticated(self, client):
        resp = client.get("/api/v1/admin/contacts")
        assert resp.status_code in (401, 403)

    def test_get_single_auto_read(self, client, admin_headers, db):
        contact = ContactMessage(name="New", email="n@n.com", message="O'qilmagan xabar", is_read=False)
        db.add(contact)
        db.commit()
        db.refresh(contact)

        resp = client.get(f"/api/v1/admin/contacts/{contact.id}", headers=admin_headers)
        assert resp.status_code == 200
        db.refresh(contact)
        assert contact.is_read is True

    def test_get_not_found(self, client, admin_headers):
        resp = client.get(f"/api/v1/admin/contacts/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404

    def test_unread_count(self, client, admin_headers, db):
        db.add(ContactMessage(name="A", email="a@b.com", message="X" * 10, is_read=False))
        db.add(ContactMessage(name="B", email="b@b.com", message="Y" * 10, is_read=False))
        db.add(ContactMessage(name="C", email="c@b.com", message="Z" * 10, is_read=True))
        db.commit()

        resp = client.get("/api/v1/admin/contacts/unread-count", headers=admin_headers)
        assert resp.json()["data"]["count"] == 2

    def test_patch_archive(self, client, admin_headers, db):
        contact = ContactMessage(name="Test", email="t@t.com", message="X" * 10)
        db.add(contact)
        db.commit()
        db.refresh(contact)

        resp = client.patch(f"/api/v1/admin/contacts/{contact.id}", headers=admin_headers, json={
            "is_archived": True,
        })
        assert resp.status_code == 200
        db.refresh(contact)
        assert contact.is_archived is True

    def test_delete(self, client, admin_headers, db):
        contact = ContactMessage(name="Del", email="d@d.com", message="O'chiriladigan")
        db.add(contact)
        db.commit()
        db.refresh(contact)

        resp = client.delete(f"/api/v1/admin/contacts/{contact.id}", headers=admin_headers)
        assert resp.status_code == 200
        assert db.query(ContactMessage).filter(ContactMessage.id == contact.id).first() is None

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete(f"/api/v1/admin/contacts/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404
