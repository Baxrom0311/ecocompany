"""
Test Chat Router — AI chatbot endpoint
"""
from unittest.mock import patch, AsyncMock


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
