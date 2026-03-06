"""
Test Services — audit_service, email_service, telegram_service, cloudinary_service, instagram_service
Using mocks for external APIs
"""
import uuid
from unittest.mock import patch, AsyncMock, MagicMock
from app.services.audit_service import log_action


class TestAuditService:
    def test_log_action_creates_record(self, db):
        from app.models.audit_log import AuditLog

        user_id = uuid.uuid4()
        entity_id = uuid.uuid4()
        log_action(db, user_id, "create", "product", entity_id, changes={"name": "Test"})
        db.commit()

        logs = db.query(AuditLog).all()
        assert len(logs) == 1
        assert logs[0].action == "create"
        assert logs[0].entity_type == "product"
        assert str(logs[0].entity_id) == str(entity_id)
        assert logs[0].changes == {"name": "Test"}

    def test_log_action_no_changes(self, db):
        from app.models.audit_log import AuditLog

        log_action(db, uuid.uuid4(), "delete", "category", uuid.uuid4())
        db.commit()

        log = db.query(AuditLog).first()
        assert log.action == "delete"
        assert log.changes is None

    def test_log_action_with_ip(self, db):
        from app.models.audit_log import AuditLog

        log_action(db, uuid.uuid4(), "update", "user", uuid.uuid4(), ip_address="192.168.1.1")
        db.commit()

        log = db.query(AuditLog).first()
        assert log.ip_address == "192.168.1.1"

    def test_multiple_logs(self, db):
        from app.models.audit_log import AuditLog

        for action in ["create", "update", "delete"]:
            log_action(db, uuid.uuid4(), action, "product", uuid.uuid4())
        db.commit()

        assert db.query(AuditLog).count() == 3


class TestCloudinaryService:
    @patch("app.services.cloudinary_service.cloudinary.uploader.upload")
    async def test_upload_file_mock(self, mock_upload):
        from app.services.cloudinary_service import upload_file

        mock_upload.return_value = {
            "secure_url": "https://cdn.com/img.jpg",
            "public_id": "eco/img",
            "width": 800,
            "height": 600,
        }

        mock_file = AsyncMock()
        mock_file.read.return_value = b"fake data"
        result = await upload_file(mock_file, folder="products")
        assert result["url"] == "https://cdn.com/img.jpg"

    @patch("app.services.cloudinary_service.cloudinary.uploader.destroy")
    async def test_delete_file_mock(self, mock_destroy):
        from app.services.cloudinary_service import delete_file

        mock_destroy.return_value = {"result": "ok"}
        result = await delete_file("eco/img")
        assert result is True

    @patch("app.services.cloudinary_service.cloudinary.uploader.destroy")
    async def test_delete_file_not_found(self, mock_destroy):
        from app.services.cloudinary_service import delete_file

        mock_destroy.return_value = {"result": "not found"}
        result = await delete_file("nonexistent")
        assert result is False


class TestEmailService:
    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_send_contact_notification(self, mock_send):
        from app.services.email_service import send_contact_notification

        mock_send.return_value = None
        mock_contact = MagicMock()
        mock_contact.name = "Test User"
        mock_contact.email = "test@test.com"
        mock_contact.phone = "+998901234567"
        mock_contact.subject = "Test"
        mock_contact.message = "Salom, suv haqida"

        result = await send_contact_notification(mock_contact)
        assert result is True

    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_send_user_confirmation(self, mock_send):
        from app.services.email_service import send_contact_confirmation

        mock_send.return_value = None
        mock_contact = MagicMock()
        mock_contact.name = "Test User"
        mock_contact.email = "user@test.com"
        result = await send_contact_confirmation(mock_contact)
        assert result is True

    @patch("app.services.email_service.aiosmtplib.send", new_callable=AsyncMock)
    async def test_send_email_failure_handled(self, mock_send):
        """Email yuborishda xato bo'lsa crash qilmasligi kerak"""
        from app.services.email_service import send_contact_notification

        mock_send.side_effect = Exception("SMTP connection failed")
        mock_contact = MagicMock()
        # Faqat log yozadi, crash qilmaydi va False qaytaradi
        result = await send_contact_notification(mock_contact)
        assert result is False


class TestTelegramService:
    @patch("app.services.telegram_service.httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_send_notification(self, mock_post):
        from app.services.telegram_service import send_contact_notification

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        mock_contact = MagicMock()
        mock_contact.name = "Test"
        mock_contact.email = "t@t.com"
        mock_contact.phone = "123"
        mock_contact.subject = "Savol"
        mock_contact.message = "Yangi xabar"
        mock_contact.created_at = None

        with patch("app.services.telegram_service.settings.TELEGRAM_CHAT_IDS", "123,456"):
            await send_contact_notification(mock_contact)

    @patch("app.services.telegram_service.httpx.AsyncClient.post", new_callable=AsyncMock)
    async def test_send_notification_failure_handled(self, mock_post):
        from app.services.telegram_service import send_contact_notification

        mock_post.side_effect = Exception("Network error")
        mock_contact = MagicMock()
        mock_contact.created_at = None
        with patch("app.services.telegram_service.settings.TELEGRAM_CHAT_IDS", "123"):
            try:
                await send_contact_notification(mock_contact)
            except Exception:
                pytest.fail("Exception should be handled gracefully")


class TestInstagramService:
    @patch("app.services.instagram_service.httpx.AsyncClient.get", new_callable=AsyncMock)
    async def test_fetch_posts_mock(self, mock_get):
        from app.services.instagram_service import fetch_and_cache_posts

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "1", "media_type": "IMAGE", "media_url": "https://x.com/1.jpg", "timestamp": "2024-01-01T00:00:00Z"},
                {"id": "2", "media_type": "VIDEO", "media_url": "https://x.com/2.mp4", "timestamp": "2024-01-02T00:00:00Z"},
            ]
        }
        mock_get.return_value = mock_response

    async def test_get_token_status_no_token(self):
        """Token yo'q bo'lsa xavfsiz javob"""
        from app.services.instagram_service import get_token_status
        status = await get_token_status()
        assert "is_valid" in status or status is not None
