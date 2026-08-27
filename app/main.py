"""
NULLSEC KIT Backend Application Entrypoint (app/main.py).
Responsible exclusively for application bootstrap, middleware setup,
router registration, and graceful database lifecycle hooks.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api.router import api_router
from app.config.settings import get_settings
from app.database.mongodb import connect_mongodb, close_mongodb
from app.database.redis import connect_redis, close_redis
from app.middleware.cors import configure_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security import SecurityHeadersMiddleware
from app.utils.errors import register_exception_handlers
from app.utils.logging import logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup and shutdown lifecycle hooks for NULLSEC KIT backend."""
    logger.info("Bootstrapping NULLSEC KIT defensive security engine...")
    await connect_mongodb()
    await connect_redis()
    yield
    logger.info("Shutting down NULLSEC KIT backend...")
    await close_mongodb()
    await close_redis()


def create_application() -> FastAPI:
    """Create and configure the production FastAPI application instance."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "NULLSEC KIT — Defensive Security Research & Authorized Assessment Toolkit. "
            "Exposes modular passive reconnaissance and security posture inspection APIs."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 1. Global Exception Handlers
    register_exception_handlers(app)

    # 2. Defensive Middleware Stack
    configure_cors(app, settings)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RateLimitMiddleware)

    # 3. Register Versioned API Routes (/api/v1/*)
    app.include_router(api_router)

    # Optional root convenience redirect to /docs
    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_application()
