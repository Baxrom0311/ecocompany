"""
Test Chat Router — AI chatbot endpoint
"""
from unittest.mock import patch, AsyncMock
from app.models.setting import SiteSetting


class TestChatRouter:
    @patch("app.services.ai_service.chat", new_callable=AsyncMock)
    def test_chat_success(self, mock_chat, client):
        mock_chat.return_value = {
            "reply": "Salom! ECO COMPANY ga xush kelibsiz.",
            "session_id": "test-session-123",
        }
        resp = client.post("/api/v1/chat", json={
            "message": "Salom",
            "session_id": None,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["reply"] == "Salom! ECO COMPANY ga xush kelibsiz."
        assert data["data"]["session_id"] == "test-session-123"

    @patch("app.services.ai_service.chat", new_callable=AsyncMock)
    def test_chat_with_session(self, mock_chat, client):
        mock_chat.return_value = {
            "reply": "Ha, suv filtrlari haqida ma'lumot beraman.",
            "session_id": "existing-session",
        }
        resp = client.post("/api/v1/chat", json={
            "message": "Filtrlar haqida",
            "session_id": "existing-session",
        })
        assert resp.status_code == 200
        assert resp.json()["data"]["session_id"] == "existing-session"

    def test_chat_empty_message(self, client):
        resp = client.post("/api/v1/chat", json={
            "message": "",
        })
        assert resp.status_code == 422

    def test_chat_missing_message(self, client):
        resp = client.post("/api/v1/chat", json={})
        assert resp.status_code == 422

    @patch("app.services.ai_service.chat", new_callable=AsyncMock)
    def test_chat_ai_error_handled(self, mock_chat, client):
        """AI service xato bersa ham server crash qilmasligi"""
        mock_chat.side_effect = Exception("AI API down")
        resp = client.post("/api/v1/chat", json={
            "message": "Test savol",
        })
        # 500 yoki graceful error
        assert resp.status_code in (200, 500)


class TestAdminChatPrompt:
    def test_super_admin_can_read_prompt(self, client, admin_headers, db):
        db.add(SiteSetting(key="ai_system_prompt", value="Secret prompt", is_public=False))
        db.commit()

        resp = client.get("/api/v1/admin/chat/prompt", headers=admin_headers)
        assert resp.status_code == 200
        assert resp.json()["data"]["prompt"] == "Secret prompt"

    def test_editor_cannot_read_prompt(self, client, editor_headers, db):
        db.add(SiteSetting(key="ai_system_prompt", value="Secret prompt", is_public=False))
        db.commit()

        resp = client.get("/api/v1/admin/chat/prompt", headers=editor_headers)
        assert resp.status_code == 403
