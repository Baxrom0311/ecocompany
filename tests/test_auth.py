"""
Test Auth — login, me, logout, change-password, edge cases
"""
import uuid


class TestLogin:
    def test_login_success(self, client, admin_user):
        resp = client.post("/api/v1/auth/login", json={
            "email": "admin@test.com", "password": "Admin123!",
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "admin@test.com"
        assert data["user"]["role"] == "super_admin"

    def test_login_wrong_password(self, client, admin_user):
        resp = client.post("/api/v1/auth/login", json={
            "email": "admin@test.com", "password": "wrong",
        })
        assert resp.status_code == 401

    def test_login_nonexistent_user(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "nobody@test.com", "password": "Test123!",
        })
        assert resp.status_code == 401

    def test_login_empty_email(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "", "password": "Test123!",
        })
        assert resp.status_code == 422

    def test_login_invalid_email_format(self, client):
        resp = client.post("/api/v1/auth/login", json={
            "email": "not-an-email", "password": "Test123!",
        })
        assert resp.status_code == 422

    def test_login_missing_password(self, client):
        resp = client.post("/api/v1/auth/login", json={"email": "admin@test.com"})
        assert resp.status_code == 422

    def test_login_empty_body(self, client):
        resp = client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422


class TestMe:
    def test_me_authenticated(self, client, admin_headers):
        resp = client.get("/api/v1/auth/me", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["email"] == "admin@test.com"
        assert data["name"] == "Test Admin"
        assert "password" not in data  # parol qaytmasligi kerak

    def test_me_unauthenticated(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)

    def test_me_invalid_token(self, client):
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"})
        assert resp.status_code in (401, 403)

    def test_me_expired_token(self, client):
        # Expired format token
        resp = client.get("/api/v1/auth/me", headers={"Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0ZXN0IiwiZXhwIjoxfQ.invalid"})
        assert resp.status_code in (401, 403)

    def test_me_nonexistent_user_token(self, client):
        from app.services.auth_service import create_access_token
        token = create_access_token({"sub": str(uuid.uuid4())})
        resp = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code in (401, 404)


class TestLogout:
    def test_logout(self, client, admin_headers):
        resp = client.post("/api/v1/auth/logout", headers=admin_headers)
        assert resp.status_code == 200

    def test_logout_unauthenticated(self, client):
        resp = client.post("/api/v1/auth/logout")
        assert resp.status_code in (401, 403)


class TestChangePassword:
    def test_change_password_success(self, client, admin_headers):
        resp = client.post("/api/v1/auth/change-password", headers=admin_headers, json={
            "current_password": "Admin123!",
            "new_password": "NewPass123!",
        })
        assert resp.status_code == 200

    def test_change_password_wrong_old(self, client, admin_headers):
        resp = client.post("/api/v1/auth/change-password", headers=admin_headers, json={
            "current_password": "WrongOld1!",
            "new_password": "NewPass123!",
        })
        assert resp.status_code in (400, 401)

    def test_change_password_weak_new(self, client, admin_headers):
        resp = client.post("/api/v1/auth/change-password", headers=admin_headers, json={
            "current_password": "Admin123!",
            "new_password": "short",
        })
        assert resp.status_code == 422

    def test_change_password_unauthenticated(self, client):
        resp = client.post("/api/v1/auth/change-password", json={
            "current_password": "Admin123!",
            "new_password": "NewPass123!",
        })
        assert resp.status_code in (401, 403)


class TestHealthCheck:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["status"] == "ok"
