"""
ECO COMPANY — Global Error Handler Middleware
Barcha xatolar bir xil structured formatda qaytadi
"""
import logging
import traceback
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("ecocompany.error")


def setup_error_handlers(app: FastAPI) -> None:
    """Barcha global exception handler larni ro'yxatdan o'tkazish"""

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """HTTP xatolari: 400, 401, 403, 404, 405, 422, 500..."""
        error_map = {
            400: "bad_request",
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            405: "method_not_allowed",
            409: "conflict",
            422: "validation",
            429: "rate_limit",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": error_map.get(exc.status_code, "server_error"),
                "message": str(exc.detail),
                "detail": None,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Pydantic validation xatolari — 422"""
        errors = []
        for error in exc.errors():
            field = " → ".join(str(loc) for loc in error["loc"])
            errors.append({
                "field": field,
                "message": error["msg"],
                "type": error["type"],
            })
        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": "validation",
                "message": "Ma'lumotlar noto'g'ri",
                "detail": errors,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Kutilmagan xatolar — 500"""
        logger.error(
            f"Unhandled error: {exc}\n"
            f"Path: {request.method} {request.url.path}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": "server_error",
                "message": "Ichki server xatosi",
                "detail": None,
            },
        )
