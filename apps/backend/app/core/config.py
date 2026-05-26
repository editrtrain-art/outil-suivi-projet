"""Application settings loaded from environment variables.

Uses pydantic-settings to parse and validate configuration from a `.env`
file or actual environment variables.  A cached factory function prevents
re-parsing on every access.
"""

from __future__ import annotations

from functools import lru_cache
from typing import ClassVar

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration sourced from environment / .env file.

    Attributes:
        DATABASE_URL: Async PostgreSQL DSN (e.g. ``postgresql+asyncpg://…``).
        DATABASE_POOL_MIN: Minimum connections kept in the pool.
        DATABASE_POOL_MAX: Maximum connections allowed in the pool.
        CORS_ORIGINS: List of allowed CORS origins.
        CLERK_SECRET_KEY: Clerk backend secret key for JWT validation.
        CLERK_PUBLISHABLE_KEY: Clerk publishable key.
        CLERK_JWKS_URL: URL to Clerk's JWKS endpoint for JWT verification.
        LLM_PROVIDER: AI backend to use — ``ollama``, ``openai``, or ``anthropic``.
        LLM_BASE_URL: Base URL of the LLM API.
        LLM_API_KEY: API key for the LLM provider.
        LLM_MODEL: Model identifier passed to the LLM provider.
        ENVIRONMENT: Runtime environment name (``development`` | ``staging`` | ``production``).
        LOG_LEVEL: Python log-level name (``DEBUG``, ``INFO``, …).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    # ── Database ────────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./nexus.db",
        description="Async PostgreSQL DSN, e.g. postgresql+asyncpg://user:pass@host/db",
    )
    DATABASE_POOL_MIN: int = Field(default=2, ge=1)
    DATABASE_POOL_MAX: int = Field(default=10, ge=2)

    # ── CORS ────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    # ── Clerk auth ──────────────────────────────────────────────────
    CLERK_SECRET_KEY: str = Field(default="")
    CLERK_PUBLISHABLE_KEY: str = Field(default="")
    CLERK_JWKS_URL: str = Field(default="")

    # ── LLM / AI engine ────────────────────────────────────────────
    LLM_PROVIDER: str = Field(default="ollama")
    LLM_BASE_URL: str = Field(default="http://localhost:11434/v1")
    LLM_API_KEY: str = Field(default="ollama")
    LLM_MODEL: str = Field(default="llama3:8b")

    # ── General ─────────────────────────────────────────────────────
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance.

    The settings are parsed once from the environment / ``.env`` file
    and reused for the lifetime of the process.

    Returns:
        Settings: Validated application settings.
    """
    return Settings()  # type: ignore[call-arg]
