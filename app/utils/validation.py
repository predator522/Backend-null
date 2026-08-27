"""
Defensive Security Input & Target Validation Utilities.
Protects against SSRF, internal host enumeration, and malformed inputs.
"""

import ipaddress
import re
from typing import Set
from urllib.parse import urlparse

from app.core.exceptions import InvalidTargetException, SSRFBlockedException

# Regex pattern for RFC 1035 valid FQDN / domain name
DOMAIN_REGEX = re.compile(
    r"^(?:[a-zA-Z0-9]"
    r"(?:[a-zA-Z0-9-_]{0,61}[a-zA-Z0-9])?\.)+"
    r"[a-zA-Z]{2,63}$"
)

# CVE ID format (e.g., CVE-2024-12345)
CVE_REGEX = re.compile(r"^CVE-\d{4}-\d{4,7}$", re.IGNORECASE)

# Forbidden internal/private TLDs and hostnames
FORBIDDEN_DOMAINS: Set[str] = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",
    "instance-data",
}

FORBIDDEN_TLDS: Set[str] = {
    ".local",
    ".internal",
    ".lan",
    ".home",
    ".corp",
    ".intranet",
    ".test",
    ".localhost",
}

CLOUD_METADATA_IPS: Set[str] = {
    "169.254.169.254",
    "fd00:ec2::254",
}


def is_private_or_loopback_ip(ip_str: str) -> bool:
    """
    Check if a string is an IP address that falls into private, loopback,
    link-local, multicast, or unspecified ranges.
    """
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_unspecified
            or ip_str in CLOUD_METADATA_IPS
        )
    except ValueError:
        return False


def validate_domain(domain: str) -> str:
    """
    Validate and sanitize a domain name target.
    Rejects:
    - IP addresses (direct IPv4/IPv6 private or public literals)
    - Localhost or internal TLDs (.local, .internal, .lan)
    - Cloud metadata hostnames
    - Malformed domain strings with injection characters
    Returns lowercase normalized domain without trailing period.
    """
    if not domain or not isinstance(domain, str):
        raise InvalidTargetException("Domain must be a non-empty string.")

    cleaned = domain.strip().lower().rstrip(".")

    if len(cleaned) > 253:
        raise InvalidTargetException("Domain exceeds maximum length of 253 characters.")

    # Reject cloud metadata or explicit forbidden hosts
    if cleaned in FORBIDDEN_DOMAINS or cleaned in CLOUD_METADATA_IPS:
        raise SSRFBlockedException("Target domain is a restricted internal or metadata host.")

    # Check forbidden suffixes (.local, .internal, etc.)
    for tld in FORBIDDEN_TLDS:
        if cleaned.endswith(tld):
            raise SSRFBlockedException(
                f"Target domain TLD '{tld}' is restricted to internal networks."
            )

    # Check if the user passed an IP literal (IPv4 or IPv6)
    try:
        ip_obj = ipaddress.ip_address(cleaned)
        if is_private_or_loopback_ip(cleaned):
            raise SSRFBlockedException(
                f"IP address '{cleaned}' is private/loopback and blocked by SSRF policy."
            )
        raise InvalidTargetException(
            "Expected a domain name (FQDN), received an IP address literal."
        )
    except ValueError:
        pass  # Not an IP literal, proceed to domain regex

    if not DOMAIN_REGEX.match(cleaned):
        raise InvalidTargetException(
            f"The supplied target '{domain}' is not a valid domain name."
        )

    return cleaned


def validate_ip_public(ip_str: str) -> str:
    """
    Validate an IPv4 or IPv6 string and ensure it is not private/loopback/metadata.
    """
    if not ip_str or not isinstance(ip_str, str):
        raise InvalidTargetException("IP address must be a non-empty string.")

    cleaned = ip_str.strip()
    try:
        ip_obj = ipaddress.ip_address(cleaned)
    except ValueError as exc:
        raise InvalidTargetException(
            f"'{ip_str}' is not a valid IPv4 or IPv6 address."
        ) from exc

    if is_private_or_loopback_ip(cleaned):
        raise SSRFBlockedException(
            f"IP address '{cleaned}' is internal/private and prohibited."
        )

    return str(ip_obj)


def validate_url_target(url_str: str) -> str:
    """
    Validate a URL target for HTTP analysis, ensuring SSRF safety on the hostname.
    """
    if not url_str or not isinstance(url_str, str):
        raise InvalidTargetException("URL must be a non-empty string.")

    cleaned = url_str.strip()
    parsed = urlparse(cleaned)

    if parsed.scheme not in ("http", "https"):
        raise InvalidTargetException(
            "Only HTTP and HTTPS URL schemes are permitted."
        )

    hostname = parsed.hostname
    if not hostname:
        raise InvalidTargetException("URL must contain a valid hostname.")

    # Check if hostname is an IP address
    try:
        ipaddress.ip_address(hostname)
        validate_ip_public(hostname)
    except ValueError:
        # Hostname is a domain name
        validate_domain(hostname)

    return cleaned


def validate_cve_id(cve_id: str) -> str:
    """Validate CVE identifier syntax (e.g. CVE-2024-12345)."""
    if not cve_id or not CVE_REGEX.match(cve_id.strip()):
        raise InvalidTargetException(
            f"'{cve_id}' is not a valid CVE identifier (expected CVE-YYYY-NNNNN)."
        )
    return cve_id.strip().upper()
