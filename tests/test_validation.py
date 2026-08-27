"""
Unit Tests for Defensive Input Validation and SSRF Protections (Phase 1).
"""

import pytest
from app.core.exceptions import InvalidTargetException, SSRFBlockedException
from app.utils.validation import validate_domain, validate_ip_public


def test_validate_domain_valid_fqdn() -> None:
    """Valid public FQDNs should normalize to lowercase without trailing dot."""
    assert validate_domain("example.com") == "example.com"
    assert validate_domain("SUB.EXAMPLE.ORG.") == "sub.example.org"


def test_validate_domain_rejects_localhost_and_internal_tld() -> None:
    """SSRF protection must block localhost and internal TLDs."""
    with pytest.raises(SSRFBlockedException):
        validate_domain("localhost")

    with pytest.raises(SSRFBlockedException):
        validate_domain("router.local")

    with pytest.raises(SSRFBlockedException):
        validate_domain("metadata.google.internal")


def test_validate_domain_rejects_private_ip_literal() -> None:
    """SSRF protection must reject raw loopback or RFC1918 IP addresses."""
    with pytest.raises(SSRFBlockedException):
        validate_domain("127.0.0.1")

    with pytest.raises(SSRFBlockedException):
        validate_domain("10.0.0.5")

    with pytest.raises(SSRFBlockedException):
        validate_domain("169.254.169.254")


def test_validate_domain_rejects_malformed_string() -> None:
    """Malformed domain strings must raise InvalidTargetException."""
    with pytest.raises(InvalidTargetException):
        validate_domain("../etc/passwd")

    with pytest.raises(InvalidTargetException):
        validate_domain("https://example.com")


def test_validate_ip_public() -> None:
    """Verify IP validator allows public IPs and blocks private ranges."""
    assert validate_ip_public("8.8.8.8") == "8.8.8.8"
    with pytest.raises(SSRFBlockedException):
        validate_ip_public("192.168.1.1")
