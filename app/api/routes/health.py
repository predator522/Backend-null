"""
Healthcheck Endpoint Route (Phase 1).
Exposes GET /api/v1/health for container orchestrators and uptime checks.
"""

from datetime import datetime, timezone
from fastapi import APIRouter
from app.config.settings import get_settings
from app.schemas.common import HealthResponse

router = APIRouter(tags=["System Health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service Healthcheck",
    description="Returns defensive security toolkit readiness status and metadata.",
)
async def check_health() -> HealthResponse:
    """Return health status without executing heavy dependencies."""
    settings = get_settings()
    return HealthResponse(
        status="ok",
        service=settings.APP_NAME,
        version=settings.APP_VERSION,
        environment=settings.APP_ENV,
        timestamp_utc=datetime.now(timezone.utc).isoformat(),
    )
