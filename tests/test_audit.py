"""
Test Admin Audit Logs — list, filter, pagination, access control
"""
import uuid
from app.models.audit_log import AuditLog
from app.models.user import User
from app.utils.hashing import hash_password


class TestAdminAuditLogs:
    def _seed_logs(self, db, admin_user, count=5):
        for i in range(count):
            db.add(AuditLog(
                user_id=admin_user.id,
                action="create" if i % 2 == 0 else "delete",
                entity_type="product" if i < 3 else "category",
                entity_id=uuid.uuid4(),
                changes={"field": {"old": "a", "new": "b"}} if i % 2 == 0 else None,
            ))
        db.commit()

    def test_list(self, client, admin_headers, admin_user, db):
        self._seed_logs(db, admin_user, 3)
        resp = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 3

    def test_list_pagination(self, client, admin_headers, admin_user, db):
        self._seed_logs(db, admin_user, 25)
        resp = client.get("/api/v1/admin/audit-logs?page=1&per_page=10", headers=admin_headers)
        data = resp.json()["data"]
        assert len(data["items"]) == 10
        assert data["total"] == 25
        assert data["pages"] == 3

    def test_filter_by_entity_type(self, client, admin_headers, admin_user, db):
        self._seed_logs(db, admin_user, 5)
        resp = client.get("/api/v1/admin/audit-logs?entity_type=product", headers=admin_headers)
        for item in resp.json()["data"]["items"]:
            assert item["entity_type"] == "product"

    def test_log_structure(self, client, admin_headers, admin_user, db):
        self._seed_logs(db, admin_user, 1)
        resp = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        item = resp.json()["data"]["items"][0]
        assert "id" in item
        assert "user_name" in item
        assert "action" in item
        assert "entity_type" in item
        assert "entity_id" in item
        assert "created_at" in item

    def test_unauthenticated(self, client):
        resp = client.get("/api/v1/admin/audit-logs")
        assert resp.status_code in (401, 403)

    def test_editor_forbidden(self, client, db):
        """Editor audit-logs ga kira olmaydi"""
        from app.services.auth_service import create_access_token
        editor = User(email="ed@test.com", password=hash_password("Test123!"), name="Ed", role="editor")
        db.add(editor)
        db.commit()
        db.refresh(editor)

        token = create_access_token({"sub": str(editor.id)})
        resp = client.get("/api/v1/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403

    def test_empty_logs(self, client, admin_headers):
        resp = client.get("/api/v1/admin/audit-logs", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["total"] == 0
        assert resp.json()["data"]["items"] == []
