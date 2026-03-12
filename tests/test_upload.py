"""
Test Upload Router — file upload validation, auth guard, delete
"""
import io
from unittest.mock import patch, AsyncMock


class TestUpload:
    def test_upload_unauthenticated(self, client):
        resp = client.post("/api/v1/admin/upload", files={
            "file": ("test.jpg", b"fake image data", "image/jpeg"),
        })
        assert resp.status_code in (401, 403)

    def test_upload_image_success_and_delete(self, client, admin_headers):
        # Haqiqiy (lekin juda kichik) PNG byte'lari
        image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8d\xb0\x00\x00\x00\x00IEND\xaeB`\x82'
        
        # 1. YUKLASH (Upload)
        resp = client.post(
            "/api/v1/admin/upload",
            headers=admin_headers,
            files={"file": ("test.png", image_data, "image/png")},
            data={"folder": "test_folder"},
        )
        assert resp.status_code == 200
        resp_data = resp.json()["data"]
        assert "url" in resp_data
        assert "/media/" in resp_data["url"]
        
        public_id = resp_data.get("public_id")
        assert public_id is not None
        
        # 2. O'CHIRISH
        del_resp = client.delete(
            f"/api/v1/admin/upload/{public_id}",
            headers=admin_headers
        )
        assert del_resp.status_code == 200
        assert "o'chirildi" in del_resp.json()["message"].lower()

    def test_upload_invalid_type(self, client, admin_headers):
        resp = client.post(
            "/api/v1/admin/upload",
            headers=admin_headers,
            files={"file": ("hack.exe", b"malware", "application/x-executable")},
        )
        assert resp.status_code == 400
        assert "fayl turi" in resp.json()["message"].lower()

    def test_upload_too_large(self, client, admin_headers):
        # 11 MB — limitdan oshgan (faqat validatsiyani tekshiradi, uploadgacha yetib bormasligi kerak)
        large_file = b"x" * (11 * 1024 * 1024)
        resp = client.post(
            "/api/v1/admin/upload",
            headers=admin_headers,
            files={"file": ("big.jpg", large_file, "image/jpeg")},
        )
        assert resp.status_code == 400
        assert "katta" in resp.json()["message"].lower()

    def test_delete_file_failed(self, client, admin_headers):
        # Mavjud bo'lmagan public_id bilan o'chirishga urinish
        resp = client.delete("/api/v1/admin/upload/ecocompany_test_nonexistent", headers=admin_headers)
        assert resp.status_code == 404

    def test_delete_unauthenticated(self, client):
        resp = client.delete("/api/v1/admin/upload/test123")
        assert resp.status_code in (401, 403)
