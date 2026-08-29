"""
Application Configuration & Settings.
Loads environment variables safely without hardcoding secrets.
"""

from functools import lru_cache
from typing import List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Centralized configuration for NULLSEC KIT backend.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "NULLSEC KIT"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = Field(default="development", description="Runtime environment")
    HOST: str = Field(default="0.0.0.0", description="Bind IP address")
    PORT: int = Field(default=8000, description="Bind port")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    # Allowed frontend CORS origins (comma-separated or single URL)
    FRONTEND_URL: str = Field(
        default="http://localhost:3000",
        description="Allowed frontend origin(s) separated by commas",
    )

    # Database configuration
    MONGODB_URI: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    MONGODB_DATABASE: str = Field(
        default="nullsec_kit",
        description="MongoDB database name",
    )
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # Defensive rate limiting
    RATE_LIMIT_PER_MINUTE: int = Field(
        default=30,
        description="Default requests allowed per minute per IP",
    )

    # DNS configuration
    DNS_RESOLVER_TIMEOUT: float = Field(
        default=4.0,
        description="Per-record DNS query timeout in seconds",
    )
    DNS_RESOLVER_LIFETIME: float = Field(
        default=6.0,
        description="Total DNS query lifetime in seconds",
    )

    @property
    def cors_origins(self) -> List[str]:
        """
        Parse comma-separated FRONTEND_URL string into a list of origins.
        Never returns wildcard ['*'] in production.
        """
        origins = [
            origin.strip()
            for origin in self.FRONTEND_URL.split(",")
            if origin.strip()
        ]
        if self.APP_ENV.lower() == "production" and "*" in origins:
            raise ValueError("Wildcard '*' CORS origins are forbidden in production.")
        return origins


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings."""
    return Settings()
