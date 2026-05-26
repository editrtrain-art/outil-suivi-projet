"""NEXUS API — FastAPI application entry point.

Creates and configures the FastAPI application with CORS, logging,
health endpoints, and the v1 API router.
"""

from __future__ import annotations

from typing import Any

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationError
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.routers.api_v1 import router as api_v1_router

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

API_VERSION = "3.0.0"


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application.

    Returns:
        FastAPI: The fully configured application instance.
    """
    settings = get_settings()

    configure_logging(
        environment=settings.ENVIRONMENT,
        log_level=settings.LOG_LEVEL,
    )

    app = FastAPI(
        title="NEXUS API",
        version=API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # ── CORS ────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Request logging ─────────────────────────────────────────────
    app.add_middleware(RequestLoggingMiddleware)

    # ── Routers ─────────────────────────────────────────────────────
    app.include_router(api_v1_router)

    # ── Health / readiness ──────────────────────────────────────────
    @app.get("/health", tags=["infra"])
    async def health() -> dict[str, str]:
        """Return a simple health-check payload.

        Returns:
            dict[str, str]: Status and API version.
        """
        return {"status": "healthy", "version": API_VERSION}

    @app.get("/ready", tags=["infra"])
    async def readiness() -> dict[str, str]:
        """Check whether the service is ready to accept traffic.

        Will eventually verify database connectivity.

        Returns:
            dict[str, str]: Readiness status.
        """
        # TODO: add DB ping once database layer is wired
        return {"status": "ready"}

    # ── Exception handlers ──────────────────────────────────────────
    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(ForbiddenError)
    async def forbidden_exception_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
        return JSONResponse(status_code=403, content={"detail": exc.message})

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(request: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(status_code=409, content={"detail": exc.message})

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.message, "errors": exc.errors})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        """Catch-all handler that logs unhandled exceptions.

        Args:
            request: The incoming request.
            exc: The unhandled exception.

        Returns:
            JSONResponse: A generic 500 response.
        """
        logger.exception(
            "unhandled_exception",
            method=request.method,
            path=str(request.url),
            error=str(exc),
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )

    logger.info(
        "app_created",
        environment=settings.ENVIRONMENT,
        version=API_VERSION,
    )

    return app


app: FastAPI = create_app()
