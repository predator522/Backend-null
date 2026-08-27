"""
Defensive Rate Limiting Middleware.
Protects assessment endpoints from abusive bursts using a sliding window.
"""

import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List, Tuple
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config.settings import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding window in-memory rate limiter per IP address.
    Configurable via RATE_LIMIT_PER_MINUTE environment setting.
    """

    def __init__(self, app: BaseHTTPMiddleware) -> None:
        super().__init__(app)
        self._lock = Lock()
        self._requests: Dict[str, List[float]] = defaultdict(list)

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip rate limit on documentation and CORS preflight
        if request.method == "OPTIONS" or request.url.path in (
            "/docs",
            "/redoc",
            "/openapi.json",
        ):
            return await call_next(request)

        settings = get_settings()
        limit = settings.RATE_LIMIT_PER_MINUTE
        client_ip = (
            request.headers.get("x-forwarded-for", "").split(",")[0].strip()
            or (request.client.host if request.client else "127.0.0.1")
        )
        now = time.time()
        window_start = now - 60.0

        with self._lock:
            # Prune old timestamps
            self._requests[client_ip] = [
                ts for ts in self._requests[client_ip] if ts > window_start
            ]
            current_count = len(self._requests[client_ip])

            if current_count >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "success": False,
                        "error": {
                            "code": "RATE_LIMIT_EXCEEDED",
                            "message": f"Exceeded maximum {limit} requests per minute.",
                        },
                    },
                    headers={
                        "Retry-After": "60",
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            self._requests[client_ip].append(now)
            remaining = max(0, limit - current_count - 1)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
