"""
ECO COMPANY — Request/Response Logging Middleware
Har bir so'rov va javobni logga yozish
(Pure ASGI — BaseHTTPMiddleware ishlatilMAYDI, chunki u multipart upload ni buzadi)
"""
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from starlette.types import ASGIApp, Scope, Receive, Send


def setup_logging() -> None:
    """Log fayllar va formatlashni sozlash"""
    if logging.getLogger("ecocompany").handlers:
        return
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # ── App log (umumiy) ──
    app_handler = RotatingFileHandler(
        log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,   # 10 MB
        backupCount=7,               # 7 ta eski fayl
        encoding="utf-8",
    )
    app_handler.setFormatter(formatter)
    app_handler.setLevel(logging.INFO)

    # ── Error log (faqat xatolar) ──
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=7,
        encoding="utf-8",
    )
    error_handler.setFormatter(formatter)
    error_handler.setLevel(logging.ERROR)

    # ── Root logger ──
    root_logger = logging.getLogger("ecocompany")
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)

    # Console da ham ko'rsatish (development uchun)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)


class LoggingMiddleware:
    """
    Har bir request/response ni logga yozish.
    Pure ASGI middleware — BaseHTTPMiddleware o'rniga.
    Bu multipart/form-data (file upload) ni buzmaydi.
    """

    def __init__(self, app: ASGIApp):
        self.app = app
        self.logger = logging.getLogger("ecocompany.request")

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.time()

        # Request ma'lumotlarini olish
        method = scope.get("method", "?")
        path = scope.get("path", "?")
        client = scope.get("client")
        client_host = client[0] if client else "unknown"

        self.logger.info(f"→ {method} {path} | IP: {client_host}")

        # Response status_code ni ushlash uchun
        response_status = None

        async def send_wrapper(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message.get("status", 0)
                # Processing time header qo'shish
                duration_ms = round((time.time() - start_time) * 1000, 1)
                headers = list(message.get("headers", []))
                headers.append(
                    (b"x-process-time", f"{duration_ms}ms".encode())
                )
                message = {**message, "headers": headers}
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.time() - start_time) * 1000, 1)
            log_msg = f"← {method} {path} | {response_status} | {duration_ms}ms"

            if response_status and response_status >= 500:
                self.logger.error(log_msg)
            elif response_status and response_status >= 400:
                self.logger.warning(log_msg)
            else:
                self.logger.info(log_msg)
