"""Regression coverage for the project review findings."""
import io
import json
import os
import subprocess
import sys
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, patch
import pytest
from PIL import Image
from app.config import settings
from app.models.gallery import GalleryAlbum, GalleryItem
from app.models.product import Product
from app.models.setting import SiteSetting


def test_login_rate_limit(client):
    statuses = [client.post('/api/v1/auth/login', json={'email': 'absent@example.com', 'password': 'wrong'}).status_code for _ in range(6)]
    assert statuses == [401] * 5 + [429]


def test_global_rate_limit(client):
    assert all(client.get('/health').status_code == 200 for _ in range(120))
    assert client.get('/health').status_code == 429


@pytest.mark.parametrize('password', ['x' * 73, 'é' * 37])
def test_long_login_password(client, admin_user, password):
    assert client.post('/api/v1/auth/login', json={'email': admin_user.email, 'password': password}).status_code == 401


def test_long_new_password(client, admin_headers):
    assert client.post('/api/v1/auth/change-password', headers=admin_headers, json={'current_password': 'Admin123!', 'new_password': 'é' * 36 + '1'}).status_code == 422


def test_password_change_revokes_token(client, admin_headers):
    assert client.post('/api/v1/auth/change-password', headers=admin_headers, json={'current_password': 'Admin123!', 'new_password': 'NewPass123!'}).status_code == 200
    assert client.get('/api/v1/auth/me', headers=admin_headers).status_code == 401
    login = client.post('/api/v1/auth/login', json={'email': 'admin@test.com', 'password': 'NewPass123!'})
    assert login.status_code == 200
    assert client.get('/api/v1/auth/me', headers={'Authorization': 'Bearer ' + login.json()['access_token']}).status_code == 200


def test_logout_revokes_token(client, admin_headers):
    assert client.post('/api/v1/auth/logout', headers=admin_headers).status_code == 200
    response = client.get('/api/v1/auth/me', headers=admin_headers)
    assert response.status_code == 401
    assert response.headers['www-authenticate'] == 'Bearer'


@pytest.mark.parametrize('filename, data, mime', [
    ('payload.html', b'<script>alert(1)</script>', 'image/jpeg'),
    ('payload.jpg', b'<script>alert(1)</script>', 'image/jpeg'),
    ('payload.svg', b'<svg onload="alert(1)"/>', 'image/svg+xml'),
    ('payload.mp4', b'<html>not a video</html>', 'video/mp4'),
])
def test_upload_rejects_disguised_content(client, admin_headers, filename, data, mime):
    assert client.post('/api/v1/admin/upload', headers=admin_headers, files={'file': (filename, data, mime)}).status_code == 400


def test_shared_media_survives_deletion(client, admin_headers, db):
    data = io.BytesIO(); Image.new('RGB', (2, 2), 'blue').save(data, format='PNG')
    upload = client.post('/api/v1/admin/upload', headers=admin_headers, files={'file': ('test.png', data.getvalue(), 'image/png')}).json()['data']
    first = Product(name_uz='One', images=[upload['url']]); second = Product(name_uz='Two', images=[upload['url']])
    db.add_all([first, second]); db.commit()
    assert client.delete('/api/v1/admin/upload/' + upload['public_id'], headers=admin_headers).status_code == 409
    assert client.delete(f'/api/v1/admin/products/{first.id}', headers=admin_headers).status_code == 200
    target = settings.media_root_path / upload['public_id']; assert target.exists()
    db.add(SiteSetting(key='partner_logos', value=json.dumps([upload['url']]))); db.commit()
    assert client.delete(f'/api/v1/admin/products/{second.id}', headers=admin_headers).status_code == 200
    assert target.exists()
    db.query(SiteSetting).delete(); db.commit()
    assert client.delete('/api/v1/admin/upload/' + upload['public_id'], headers=admin_headers).status_code == 200
    assert not target.exists()


def test_gallery_detail_filters_and_reorder_validates(client, admin_headers, db):
    album = GalleryAlbum(title_uz='Album'); db.add(album); db.flush()
    item = GalleryItem(album_id=album.id, file_url='/media/yes.png')
    db.add_all([item, GalleryItem(album_id=album.id, file_url='/media/no.png', is_active=False)]); db.commit()
    items = client.get(f'/api/v1/gallery/albums/{album.id}').json()['data']['items']
    assert [entry['file_url'] for entry in items] == ['/media/yes.png']
    url = f'/api/v1/admin/gallery/albums/{album.id}/items/reorder'
    assert client.post(url, headers=admin_headers, json=[{'id': str(item.id), 'order_index': 3}]).status_code == 200
    db.refresh(item); assert item.order_index == 3
    assert client.post(url, headers=admin_headers, json=[{'id': 'invalid', 'order_index': 3}]).status_code == 422


def test_optional_product_fields_can_be_cleared(client, admin_headers, db):
    product = Product(name_uz='Water', desc_ru='Description', original_price=123); db.add(product); db.commit()
    response = client.put(f'/api/v1/admin/products/{product.id}', headers=admin_headers, json={'desc_ru': None, 'original_price': None})
    assert response.status_code == 200
    assert response.json()['data']['desc_ru'] is None
    assert response.json()['data']['original_price'] is None


def test_chat_reuses_server_session_and_history(client):
    with patch('app.services.ai_service._generate_reply', new_callable=AsyncMock, return_value='Reply') as reply:
        first = client.post('/api/v1/chat', json={'message': 'First', 'session_id': None}).json()['data']
        second = client.post('/api/v1/chat', json={'message': 'Second', 'session_id': first['session_id']}).json()['data']
        assert second['session_id'] == first['session_id']
        assert [message['content'] for message in reply.call_args.args[1]] == ['First', 'Reply', 'Second']


def test_mcp_http_initialize(client):
    response = client.post('/api/v1/mcp/', headers={'Accept': 'application/json, text/event-stream'}, json={
        'jsonrpc': '2.0', 'id': 1, 'method': 'initialize',
        'params': {'protocolVersion': '2025-03-26', 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}},
    })
    assert response.status_code == 200
    assert 'serverInfo' in response.text


def test_sitemap_uses_site_domain(client, db, monkeypatch):
    monkeypatch.setattr(settings, 'PUBLIC_BASE_URL', 'https://api.example.com')
    monkeypatch.setattr(settings, 'SITE_URL', 'https://www.example.com')
    db.add(Product(name_uz='Water')); db.commit()
    response = client.get('/sitemaps/products.xml')
    assert '<loc>https://www.example.com/products/' in response.text
    assert 'https://api.example.com/products/' not in response.text


async def test_smtp_starttls():
    from app.services.email_service import _send_email
    with patch('app.services.email_service.aiosmtplib.send', new_callable=AsyncMock) as send:
        assert await _send_email('test@example.com', 'Test', '<p>Test</p>')
        assert send.call_args.kwargs['use_tls'] is False
        assert send.call_args.kwargs['start_tls'] is True


def test_wsgi_runs_startup_and_mcp():
    code = '''
import httpx
from passenger_wsgi import application
with httpx.Client(transport=httpx.WSGITransport(app=application), base_url="http://testserver") as client:
    assert client.get("/health").status_code == 200
    response = client.post("/api/v1/mcp/", headers={"Accept":"application/json, text/event-stream"}, json={
        "jsonrpc":"2.0", "id":1, "method":"initialize", "params":{
            "protocolVersion":"2025-03-26", "capabilities":{}, "clientInfo":{"name":"test", "version":"1"}}})
    assert response.status_code == 200, response.text
    assert "serverInfo" in response.text
'''
    subprocess.run([sys.executable, '-c', code], check=True, timeout=30, capture_output=True)


def test_migrations_fresh_and_existing_database(tmp_path):
    project = Path(__file__).resolve().parents[1]
    for legacy in (False, True):
        database = tmp_path / f'{legacy}.sqlite'
        env = {**os.environ, 'DATABASE_URL': f'sqlite:///{database}'}
        def alembic(*args):
            subprocess.run([sys.executable, '-m', 'alembic', *args], cwd=project, env=env, check=True, timeout=30, capture_output=True)
        if legacy:
            with sqlite3.connect(database) as connection:
                connection.execute('CREATE TABLE users (id TEXT PRIMARY KEY, email TEXT)')
                connection.execute("INSERT INTO users VALUES ('existing', 'test@example.com')")
            alembic('stamp', '002_add_indexes')
        alembic('upgrade', 'head')
        with sqlite3.connect(database) as connection:
            assert 'token_version' in [row[1] for row in connection.execute('PRAGMA table_info(users)')]
            if legacy: assert connection.execute('SELECT token_version FROM users').fetchone() == (0,)
        alembic('downgrade', '002_add_indexes'); alembic('upgrade', 'head')
