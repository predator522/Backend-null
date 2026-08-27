"""
Common API Response Schemas for NULLSEC KIT.
Guarantees consistent JSON output structure across all defensive tools.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Healthcheck endpoint status schema."""

    status: str = Field(default="ok", description="Service health state")
    service: str = Field(default="NULLSEC KIT", description="Toolkit identifier")
    version: str = Field(default="1.0.0", description="API version")
    environment: str = Field(default="development", description="Runtime environment")
    timestamp_utc: str = Field(description="ISO 8601 UTC timestamp")


class ErrorDetail(BaseModel):
    """Standardized error code and message object."""

    code: str = Field(description="Machine-readable error identifier")
    message: str = Field(description="Safe human-readable error summary")


class ErrorResponse(BaseModel):
    """Top-level error response envelope returned by global exception handlers."""

    success: bool = Field(default=False)
    error: ErrorDetail
