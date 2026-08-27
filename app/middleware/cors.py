"""
CORS Middleware Configuration.
Enforces explicit origins from FRONTEND_URL and forbids wildcard '*' in production.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import Settings


def configure_cors(app: FastAPI, settings: Settings) -> None:
    """Configure CORS for configured frontend origins only."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
        expose_headers=["X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"],
    )
