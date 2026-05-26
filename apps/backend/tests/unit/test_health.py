"""Unit tests for the /health and /ready endpoints."""

from __future__ import annotations

import os
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

# Ensure a DATABASE_URL is set before the app tries to load settings.
# This fake DSN is never actually connected to during unit tests.
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://test:test@localhost:5432/test_nexus",
)

from app.main import app  # noqa: E402 — must come after env setup


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an httpx AsyncClient wired to the ASGI app.

    Yields:
        AsyncClient: Test client for making requests against the app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_returns_200_with_status(client: AsyncClient) -> None:
    """GET /health should return 200 with status=healthy and correct version."""
    response = await client.get("/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "healthy"
    assert body["version"] == "3.0.0"


@pytest.mark.asyncio
async def test_ready_returns_200(client: AsyncClient) -> None:
    """GET /ready should return 200 with status=ready."""
    response = await client.get("/ready")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"
