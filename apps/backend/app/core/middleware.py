"""ASGI middleware for structured request logging.

Logs every HTTP request with method, path, status code, and
duration in milliseconds via structlog.
"""

from __future__ import annotations

import time
from typing import Any

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs every request/response cycle.

    Captures HTTP method, path, response status code, and elapsed
    time in milliseconds.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """Process a request and log its completion.

        Args:
            request: The incoming HTTP request.
            call_next: Callable that forwards the request to the next
                middleware or route handler.

        Returns:
            Response: The HTTP response returned by the application.
        """
        start_time: float = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms: float = round((time.perf_counter() - start_time) * 1000, 2)

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response
