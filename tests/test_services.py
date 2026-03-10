"""
Test Services — audit_service, email_service, telegram_service, storage_service, instagram_service
Using mocks for external APIs
"""
import pytest
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


class TestStorageService:
    async def test_upload_file_mock(self, tmp_path, monkeypatch):
        from app.services.storage_service import upload_file
        from app.config import settings

        monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))
        mock_file = AsyncMock()
        mock_file.read.return_value = b"fake data"
        mock_file.filename = "photo.jpg"
        result = await upload_file(mock_file, folder="products", base_url="http://testserver")
        assert result["url"].startswith("http://testserver/media/products/")
        assert (tmp_path / result["public_id"]).exists()

    async def test_delete_file_mock(self, tmp_path, monkeypatch):
        from app.services.storage_service import delete_file
        from app.config import settings

        monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))
        target = tmp_path / "products" / "file.jpg"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"test")
        result = await delete_file("products/file.jpg")
        assert result is True
        assert not target.exists()

    async def test_delete_file_not_found(self, tmp_path, monkeypatch):
        from app.services.storage_service import delete_file
        from app.config import settings

        monkeypatch.setattr(settings, "MEDIA_ROOT", str(tmp_path))
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
    def test_save_and_read_manual_links(self, db):
        from app.services.instagram_service import get_manual_links, save_manual_links

        save_manual_links(db, [
            {"url": "https://www.instagram.com/reel/C7M1abcd123/"},
        ])
        links = get_manual_links(db)

        assert len(links) == 1
        assert links[0]["embed_url"].endswith("/embed")

    def test_reject_invalid_instagram_links(self, db):
        from app.services.instagram_service import save_manual_links

        with pytest.raises(ValueError):
            save_manual_links(db, [
                {"url": "https://youtube.com/watch?v=123"},
            ])

    def test_manual_status(self, db):
        from app.services.instagram_service import get_manual_status

        status = get_manual_status(db)
        assert status["mode"] == "manual"
        assert "link_count" in status
