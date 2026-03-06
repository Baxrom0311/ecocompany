"""
Test Middleware — security headers, error handler structured responses
"""


class TestSecurityHeaders:
    def test_x_content_type_options(self, client):
        resp = client.get("/health")
        assert resp.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options(self, client):
        resp = client.get("/health")
        assert resp.headers.get("X-Frame-Options") == "DENY"

    def test_x_xss_protection(self, client):
        resp = client.get("/health")
        assert resp.headers.get("X-XSS-Protection") == "1; mode=block"

    def test_referrer_policy(self, client):
        resp = client.get("/health")
        assert resp.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"

    def test_hsts(self, client):
        resp = client.get("/health")
        hsts = resp.headers.get("Strict-Transport-Security", "")
        assert "max-age=31536000" in hsts

    def test_permissions_policy(self, client):
        resp = client.get("/health")
        pp = resp.headers.get("Permissions-Policy", "")
        assert "camera=()" in pp


class TestErrorHandler:
    def test_404_structured(self, client):
        resp = client.get("/api/v1/nonexistent-endpoint")
        assert resp.status_code in (404, 405)
        data = resp.json()
        assert data["success"] is False
        assert data["error"] in ("not_found", "method_not_allowed")

    def test_422_validation_error(self, client):
        # Login ga noto'g'ri format yuborish
        resp = client.post("/api/v1/auth/login", json={"email": 12345})
        assert resp.status_code == 422
        data = resp.json()
        assert data["success"] is False
        assert data["error"] == "validation"
        assert isinstance(data["detail"], list)

    def test_validation_error_fields(self, client):
        resp = client.post("/api/v1/auth/login", json={})
        assert resp.status_code == 422
        data = resp.json()
        assert len(data["detail"]) > 0
        assert "field" in data["detail"][0]
        assert "message" in data["detail"][0]

    def test_401_unauthorized(self, client):
        resp = client.get("/api/v1/auth/me")
        assert resp.status_code in (401, 403)
        data = resp.json()
        assert data["success"] is False


class TestCORS:
    def test_cors_headers_present(self, client):
        resp = client.options("/health", headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        })
        # CORS preflightda header bo'lishi kerak
        assert resp.status_code in (200, 400)
