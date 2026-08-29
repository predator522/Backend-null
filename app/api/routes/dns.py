"""
DNS Lookup Route (Phase 2).
Exposes POST /api/v1/dns/lookup and delegates to DNSLookupService.
Routes contain zero business logic.
"""

from fastapi import APIRouter
from app.schemas.dns import DNSLookupRequest, DNSLookupResponse
from app.services.dns.service import DNSLookupService

router = APIRouter(prefix="/dns", tags=["DNS Reconnaissance"])


@router.post(
    "/lookup",
    response_model=DNSLookupResponse,
    summary="Query DNS Resource Records",
    description=(
        "Non-blocking passive DNS inspection for public domain targets. "
        "Queries A, AAAA, MX, NS, TXT, CNAME, and SOA resource records."
    ),
)
async def lookup_dns(request: DNSLookupRequest) -> DNSLookupResponse:
    """
    Route request payload directly to DNSLookupService.
    Schema validation runs before service invocation.
    """
    service = DNSLookupService()
    return await service.lookup(request.domain)
