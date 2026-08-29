"""
Versioned API Router (/api/v1).
Aggregates active Phase 1 & Phase 2 routes and mounts placeholder routes
for future tool implementations.
"""

from fastapi import APIRouter
from app.api.routes import (
    health,
    dns,
    whois,
    ip,
    http_analysis,
    tls,
    headers,
    cors,
    cookies,
    crypto,
    cve,
    reports,
)

api_router = APIRouter(prefix="/api/v1")

# Phase 1 & Phase 2 Complete Routes
api_router.include_router(health.router)
api_router.include_router(dns.router)

# Future Phase Routes Registered Under /api/v1
api_router.include_router(whois.router)
api_router.include_router(ip.router)
api_router.include_router(http_analysis.router)
api_router.include_router(tls.router)
api_router.include_router(headers.router)
api_router.include_router(cors.router)
api_router.include_router(cookies.router)
api_router.include_router(crypto.router)
api_router.include_router(cve.router)
api_router.include_router(reports.router)
