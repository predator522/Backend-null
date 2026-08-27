"""
Test GET /api/v1/health Endpoint & Security Headers (Phase 1).
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_ok(client: AsyncClient) -> None:
    """Verify healthcheck endpoint returns 200 with structured metadata."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "NULLSEC KIT"
    assert data["version"] == "1.0.0"
    assert "timestamp_utc" in data

    # Verify defensive security headers injected by middleware
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert "x-request-id" in response.headers
