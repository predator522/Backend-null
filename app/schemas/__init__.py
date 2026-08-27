"""Schemas package for NULLSEC KIT API request and response contracts."""
from app.schemas.common import HealthResponse, ErrorResponse
from app.schemas.dns import DNSLookupRequest, DNSLookupResponse, DNSRecordsMap

__all__ = [
    "HealthResponse",
    "ErrorResponse",
    "DNSLookupRequest",
    "DNSLookupResponse",
    "DNSRecordsMap",
]
