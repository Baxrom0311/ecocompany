"""Public site rebuild trigger."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.config import settings
from app.services import site_rebuild


def test_should_rebuild_only_for_successful_content_writes(monkeypatch):
    monkeypatch.setattr(settings, "SITE_REBUILD_HOOK_URL", "https://hook.example.com")
    assert site_rebuild.should_rebuild("POST", "/api/v1/admin/products", 201)
    assert site_rebuild.should_rebuild("PUT", "/api/v1/admin/settings/bulk", 200)
    assert not site_rebuild.should_rebuild("GET", "/api/v1/admin/products", 200)
    assert not site_rebuild.should_rebuild("POST", "/api/v1/admin/products", 422)
    assert not site_rebuild.should_rebuild("POST", "/api/v1/contacts", 201)


def test_should_rebuild_disabled_without_hook(monkeypatch):
    monkeypatch.setattr(settings, "SITE_REBUILD_HOOK_URL", "")
    assert not site_rebuild.should_rebuild("POST", "/api/v1/admin/products", 201)


def test_rapid_changes_trigger_one_rebuild(monkeypatch):
    monkeypatch.setattr(settings, "SITE_REBUILD_HOOK_URL", "https://hook.example.com")
    monkeypatch.setattr(site_rebuild, "REBUILD_DELAY_SECONDS", 0.05)
    client = MagicMock()
    client.post = AsyncMock(return_value=MagicMock(raise_for_status=MagicMock()))
    client.__aenter__ = AsyncMock(return_value=client)
    client.__aexit__ = AsyncMock(return_value=False)

    async def scenario():
        with patch.object(site_rebuild.httpx, "AsyncClient", return_value=client):
            for _ in range(3):
                site_rebuild.schedule_site_rebuild()
            await asyncio.sleep(0.2)

    asyncio.run(scenario())
    client.post.assert_awaited_once_with("https://hook.example.com")


def test_admin_product_create_schedules_rebuild(client, admin_headers, monkeypatch):
    monkeypatch.setattr(settings, "SITE_REBUILD_HOOK_URL", "https://hook.example.com")
    with patch("app.main.schedule_site_rebuild") as scheduled:
        client.get("/api/v1/admin/products", headers=admin_headers)
        scheduled.assert_not_called()
        client.put("/api/v1/admin/settings/bulk", headers=admin_headers, json=[{"key": "phone_1", "value": "+998"}])
        scheduled.assert_called_once()
