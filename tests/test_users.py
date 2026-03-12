"""
Test Users — admin CRUD (super_admin only)
"""
import uuid
from app.models.user import User
from app.utils.hashing import hash_password


class TestAdminUsers:
    def test_list(self, client, admin_headers, admin_user):
        resp = client.get("/api/v1/admin/users", headers=admin_headers)
        assert resp.status_code == 200
        assert len(resp.json()["data"]) >= 1

    def test_list_unauthenticated(self, client):
        resp = client.get("/api/v1/admin/users")
        assert resp.status_code in (401, 403)

    def test_create(self, client, admin_headers):
        resp = client.post("/api/v1/admin/users", headers=admin_headers, json={
            "email": "editor@test.com",
            "password": "Editor123!",
            "name": "Editor User",
            "role": "editor",
        })
        assert resp.status_code == 201
        data = resp.json()["data"]
        assert data["email"] == "editor@test.com"
        assert data["role"] == "editor"

    def test_create_duplicate_email(self, client, admin_headers, admin_user):
        resp = client.post("/api/v1/admin/users", headers=admin_headers, json={
            "email": "admin@test.com",  # admin_user bilan bir xil
            "password": "Test1234!",
            "name": "Duplicate",
            "role": "editor",
        })
        assert resp.status_code == 409

    def test_update(self, client, admin_headers, db):
        user = User(email="upd@test.com", password=hash_password("Test123!"), name="Old", role="editor")
        db.add(user)
        db.commit()
        db.refresh(user)

        resp = client.put(f"/api/v1/admin/users/{user.id}", headers=admin_headers, json={
            "name": "Updated Name",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["name"] == "Updated Name"

    def test_update_duplicate_email(self, client, admin_headers, db, admin_user):
        user = User(email="other@test.com", password=hash_password("Test123!"), name="Other", role="editor")
        db.add(user)
        db.commit()
        db.refresh(user)

        resp = client.put(f"/api/v1/admin/users/{user.id}", headers=admin_headers, json={
            "email": "admin@test.com",  # admin_user email
        })
        assert resp.status_code == 409

    def test_update_not_found(self, client, admin_headers):
        resp = client.put(f"/api/v1/admin/users/{uuid.uuid4()}", headers=admin_headers, json={
            "name": "X",
        })
        assert resp.status_code == 404

    def test_update_self_role_downgrade_prevented(self, client, admin_headers, admin_user):
        resp = client.put(f"/api/v1/admin/users/{admin_user.id}", headers=admin_headers, json={
            "role": "editor",
        })
        assert resp.status_code == 400

    def test_update_self_deactivate_prevented(self, client, admin_headers, admin_user):
        resp = client.put(f"/api/v1/admin/users/{admin_user.id}", headers=admin_headers, json={
            "is_active": False,
        })
        assert resp.status_code == 400

    def test_delete(self, client, admin_headers, db):
        user = User(email="del@test.com", password=hash_password("Test123!"), name="Del", role="editor")
        db.add(user)
        db.commit()
        db.refresh(user)

        resp = client.delete(f"/api/v1/admin/users/{user.id}", headers=admin_headers)
        assert resp.status_code == 200

    def test_delete_self_prevented(self, client, admin_headers, admin_user):
        resp = client.delete(f"/api/v1/admin/users/{admin_user.id}", headers=admin_headers)
        assert resp.status_code == 400

    def test_delete_not_found(self, client, admin_headers):
        resp = client.delete(f"/api/v1/admin/users/{uuid.uuid4()}", headers=admin_headers)
        assert resp.status_code == 404


class TestEditorAccess:
    def test_editor_cannot_manage_users(self, client, db):
        """Editor users CRUD ga kirishi taqiqlangan"""
        from app.services.auth_service import create_access_token
        editor = User(email="ed@test.com", password=hash_password("Test123!"), name="Ed", role="editor")
        db.add(editor)
        db.commit()
        db.refresh(editor)

        token = create_access_token({"sub": str(editor.id)})
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.get("/api/v1/admin/users", headers=headers)
        assert resp.status_code == 403
