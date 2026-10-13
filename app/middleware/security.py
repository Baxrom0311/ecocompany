"""
ECO COMPANY — Security Middleware
XSS himoya, Security Headers
(Pure ASGI — BaseHTTPMiddleware ishlatilMAYDI, chunki u multipart upload ni buzadi)
"""
from starlette.types import ASGIApp, Scope, Receive, Send
from app.config import settings


class SecurityHeadersMiddleware:
    """Xavfsizlik headerlari qo'shish (pure ASGI)"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                # Security Headers
                headers.extend([
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (b"strict-transport-security", b"max-age=31536000; includeSubDomains"),
                    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
                ])
                if scope.get("path", "").startswith(settings.media_url_path.rstrip("/") + "/"):
                    headers.append((b"content-security-policy", b"sandbox; default-src 'none'; img-src 'self' data:; media-src 'self'"))
                    if scope["path"].lower().endswith((".html", ".htm", ".svg", ".pdf")):
                        headers.append((b"content-disposition", b"attachment"))
                message = {**message, "headers": headers}
            await send(message)

        await self.app(scope, receive, send_wrapper)
