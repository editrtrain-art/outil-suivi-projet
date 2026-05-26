"""Async SQLAlchemy engine and session management.

Provides a reusable async engine, session factory, and a FastAPI
dependency that yields per-request database sessions.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


def build_engine() -> AsyncEngine:
    """Create the async SQLAlchemy engine from application settings.

    Returns:
        AsyncEngine: Configured async database engine.
    """
    settings = get_settings()
    
    # SQLite-specific handling
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    
    kwargs: dict[str, Any] = {
        "pool_pre_ping": True,
        "echo": settings.ENVIRONMENT == "development",
    }
    
    if not is_sqlite:
        kwargs["pool_size"] = settings.DATABASE_POOL_MIN
        kwargs["max_overflow"] = settings.DATABASE_POOL_MAX - settings.DATABASE_POOL_MIN
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        **kwargs
    )
    
    logger.info(
        "database_engine_created",
        is_sqlite=is_sqlite,
        url=settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
    )
    return engine


engine: AsyncEngine = build_engine()

async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session.

    The session is automatically closed after the request completes,
    regardless of success or failure.

    Yields:
        AsyncSession: A scoped async database session.
    """
    session = async_session_factory()
    try:
        yield session
    finally:
        await session.close()
