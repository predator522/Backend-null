"""
MongoDB Modular Client Manager.
Services decouple data persistence from route logic and gracefully tolerate
unreachable MongoDB nodes in ephemeral lab environments.
"""

from typing import Any, Optional
from app.config.settings import get_settings
from app.utils.logging import logger

_mongo_client: Optional[Any] = None


async def connect_mongodb() -> None:
    """Initialize non-blocking connection to MongoDB if driver is available."""
    global _mongo_client
    settings = get_settings()
    if not settings.MONGODB_URI:
        return
    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        _mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=2000,
        )
        logger.info("MongoDB client pool initialized for %s", settings.MONGODB_DATABASE)
    except ImportError:
        logger.info("Motor async driver not installed; running in memory/stateless mode.")
    except Exception as exc:
        logger.warning("MongoDB connection skipped: %s", exc)


async def close_mongodb() -> None:
    """Close MongoDB connection pool gracefully on shutdown."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None


def get_mongo_db() -> Optional[Any]:
    """Retrieve database handle or None if running stateless."""
    if _mongo_client is None:
        return None
    settings = get_settings()
    return _mongo_client[settings.MONGODB_DATABASE]
