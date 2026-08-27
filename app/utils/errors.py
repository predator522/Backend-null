"""
Centralized FastAPI Error Handlers.
Guarantees consistent JSON error payload without stack trace leakage.
"""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.exceptions import NullSecException
from app.utils.logging import logger


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers to FastAPI application."""

    @app.exception_handler(NullSecException)
    async def nullsec_exception_handler(
        request: Request, exc: NullSecException
    ) -> JSONResponse:
        logger.warning(
            "Domain exception raised: %s (%s)",
            exc.code,
            exc.message,
            extra={"endpoint": request.url.path},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                },
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Extract first human-friendly validation error message
        errors = exc.errors()
        first_error = errors[0] if errors else {}
        message = first_error.get("msg", "Request validation failed.")
        loc = first_error.get("loc", ())
        field_name = str(loc[-1]) if loc else "input"

        return JSONResponse(
            status_code=422,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_TARGET",
                    "message": f"Validation error on '{field_name}': {message}",
                },
            },
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        code_map = {
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            429: "RATE_LIMIT_EXCEEDED",
        }
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": {
                    "code": code_map.get(exc.status_code, f"HTTP_{exc.status_code}"),
                    "message": str(exc.detail),
                },
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error(
            "Unhandled internal exception on %s: %s",
            request.url.path,
            type(exc).__name__,
            exc_info=True,
        )
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected defensive toolkit error occurred.",
                },
            },
        )
