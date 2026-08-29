"""
Domain exception hierarchy for NULLSEC KIT.
Prevents leaking stack traces or internal implementation details.
"""

from typing import Any, Dict, Optional


class NullSecException(Exception):
    """
    Base exception class for NULLSEC KIT.
    Maps to standardized error JSON response format:
    {
        "success": false,
        "error": {
            "code": "ERROR_CODE",
            "message": "Human safe description"
        }
    }
    """

    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class InvalidTargetException(NullSecException):
    """Raised when target domain, IP, or URL fails syntax or policy checks."""

    def __init__(self, message: str = "The supplied target is invalid.") -> None:
        super().__init__(
            code="INVALID_TARGET",
            message=message,
            status_code=400,
        )


class SSRFBlockedException(NullSecException):
    """Raised when target resolves to loopback, private, or metadata IPs."""

    def __init__(
        self,
        message: str = "Target blocked: internal or non-public destination not allowed.",
    ) -> None:
        super().__init__(
            code="SSRF_BLOCKED",
            message=message,
            status_code=403,
        )


class RateLimitExceededException(NullSecException):
    """Raised when client exceeds rate limit thresholds."""

    def __init__(
        self,
        message: str = "Rate limit exceeded. Please slow down requests.",
    ) -> None:
        super().__init__(
            code="RATE_LIMIT_EXCEEDED",
            message=message,
            status_code=429,
        )


class DNSLookupException(NullSecException):
    """Raised when a fatal DNS service error occurs."""

    def __init__(
        self,
        message: str = "DNS query failed due to resolver timeout or network error.",
    ) -> None:
        super().__init__(
            code="DNS_LOOKUP_ERROR",
            message=message,
            status_code=502,
        )
