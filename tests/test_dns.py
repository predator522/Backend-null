"""
Integration & Unit Tests for DNS Lookup (Phase 2).
Verifies POST /api/v1/dns/lookup returns exact schema structure and handles errors.
"""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient


class MockRData:
    """Mock dnspython rdata object."""

    def __init__(self, value: str, preference: int = 10) -> None:
        self.value = value
        self.preference = preference
        self.exchange = value
        self.mname = "ns1.example.com."
        self.rname = "hostmaster.example.com."
        self.serial = 2026010101
        self.strings = [b"v=spf1 include:_spf.example.com -all"]

    def __str__(self) -> str:
        return self.value


@pytest.mark.asyncio
async def test_dns_lookup_success_with_mocked_records(client: AsyncClient) -> None:
    """Verify POST /api/v1/dns/lookup returns structured 7-record JSON map."""

    async def mock_resolve(domain: str, rtype: str):
        if rtype == "A":
            return [MockRData("93.184.216.34")]
        if rtype == "AAAA":
            return [MockRData("2606:2800:220:1:248:1893:25c8:1946")]
        if rtype == "MX":
            return [MockRData("mail.example.com")]
        if rtype == "NS":
            return [MockRData("a.iana-servers.net")]
        if rtype == "TXT":
            return [MockRData("v=spf1")]
        if rtype == "SOA":
            return [MockRData("soa")]
        return []

    with patch(
        "dns.asyncresolver.Resolver.resolve",
        new=AsyncMock(side_effect=mock_resolve),
    ):
        response = await client.post(
            "/api/v1/dns/lookup",
            json={"domain": "example.com"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["domain"] == "example.com"
    assert "records" in data
    records = data["records"]
    assert set(records.keys()) == {"A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"}
    assert "93.184.216.34" in records["A"]
    assert len(records["MX"]) == 1
    assert "mail.example.com" in records["MX"][0]


@pytest.mark.asyncio
async def test_dns_lookup_ssrf_protection_blocks_internal_target(
    client: AsyncClient,
) -> None:
    """Verify internal/loopback domain inputs return 403 SSRF blocked error."""
    response = await client.post(
        "/api/v1/dns/lookup",
        json={"domain": "localhost"},
    )
    assert response.status_code == 403
    payload = response.json()
    assert payload["success"] is False
    assert payload["error"]["code"] == "SSRF_BLOCKED"


@pytest.mark.asyncio
async def test_dns_lookup_invalid_domain_returns_controlled_error(
    client: AsyncClient,
) -> None:
    """Verify malformed input returns standardized error JSON."""
    response = await client.post(
        "/api/v1/dns/lookup",
        json={"domain": "invalid domain name!!!"},
    )
    assert response.status_code in (400, 422)
    payload = response.json()
    assert payload["success"] is False
    assert "error" in payload
