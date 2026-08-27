"""
DNS Lookup Request & Response Pydantic Schemas (Phase 2).
Enforces exact response contract:
{
    "success": true,
    "domain": "example.com",
    "records": {
        "A": [],
        "AAAA": [],
        "MX": [],
        "NS": [],
        "TXT": [],
        "CNAME": [],
        "SOA": []
    }
}
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field, field_validator
from app.utils.validation import validate_domain


class DNSLookupRequest(BaseModel):
    """Payload for POST /api/v1/dns/lookup."""

    domain: str = Field(
        ...,
        json_schema_extra={"example": "example.com"},
        description="Public domain target to inspect (FQDN without trailing period)",
    )

    @field_validator("domain")
    @classmethod
    def sanitize_and_validate_domain(cls, value: str) -> str:
        """Validate FQDN syntax and enforce SSRF protections."""
        return validate_domain(value)


class DNSRecordsMap(BaseModel):
    """Complete map of supported DNS resource record types."""

    A: List[str] = Field(default_factory=list)
    AAAA: List[str] = Field(default_factory=list)
    MX: List[str] = Field(default_factory=list)
    NS: List[str] = Field(default_factory=list)
    TXT: List[str] = Field(default_factory=list)
    CNAME: List[str] = Field(default_factory=list)
    SOA: List[str] = Field(default_factory=list)


class DNSLookupResponse(BaseModel):
    """Structured response returned by POST /api/v1/dns/lookup."""

    success: bool = Field(default=True)
    domain: str = Field(..., json_schema_extra={"example": "example.com"})
    records: DNSRecordsMap
    query_duration_ms: float = Field(
        default=0.0, description="Total resolver elapsed time in milliseconds"
    )
