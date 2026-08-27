"""
Redis Modular Client Manager.
Provides caching and distributed token-bucket rate limiting fallback.
"""

from typing import Any, Optional
from app.config.settings import get_settings
from app.utils.logging import logger

_redis_client: Optional[Any] = None


async def connect_redis() -> None:
    """Initialize asynchronous Redis pool if driver is available."""
    global _redis_client
    settings = get_settings()
    if not settings.REDIS_URL:
        return
    try:
        import redis.asyncio as redis

        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2.0,
        )
        logger.info("Redis client initialized.")
    except ImportError:
        logger.info("redis.asyncio driver not installed; using in-memory token bucket.")
    except Exception as exc:
        logger.warning("Redis connection skipped: %s", exc)


async def close_redis() -> None:
    """Close Redis pool gracefully on shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_redis_client() -> Optional[Any]:
    """Retrieve Redis client handle or None if running in-memory fallback."""
    return _redis_client
