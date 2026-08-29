"""Core domain exceptions and primitives."""
from app.core.exceptions import (
    NullSecException,
    InvalidTargetException,
    SSRFBlockedException,
    RateLimitExceededException,
    DNSLookupException,
)

__all__ = [
    "NullSecException",
    "InvalidTargetException",
    "SSRFBlockedException",
    "RateLimitExceededException",
    "DNSLookupException",
]
