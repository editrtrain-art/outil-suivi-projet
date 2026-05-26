"""Integration tests for NEXUS V3 API endpoints.

Verifies the full request–response cycle through the ASGI transport,
ensuring routers, dependencies, and service logic integrate correctly.

Uses an in-memory SQLite backend for isolation (no external Postgres needed).
"""

from __future__ import annotations

import os
import uuid
from typing import Any, AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

# ── Environment setup (before app import) ─────────────────────────────────────

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "development"
os.environ["CLERK_SECRET_KEY"] = ""
os.environ["CLERK_JWKS_URL"] = ""

from app.core.database import engine  # noqa: E402
from app.domain.models import Base  # noqa: E402
from app.main import app  # noqa: E402


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
async def _setup_database() -> AsyncGenerator[None, None]:
    """Create all tables before each test, drop them after.

    Yields:
        None: Control returns to the test body.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an httpx AsyncClient wired to the ASGI app.

    Yields:
        AsyncClient: Test client for making requests against the app.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


def _mock_headers(role: str = "pm") -> dict[str, str]:
    """Return Authorization headers with a mock development token.

    Returns:
        Dict with Bearer mock token header.
    """
    return {"Authorization": f"Bearer mock_{role}_testuser_test@nexus.local"}


# ── Health Endpoints ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    """GET /health should return 200 with version info."""
    response = await client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "version" in body


@pytest.mark.asyncio
async def test_ready_endpoint(client: AsyncClient) -> None:
    """GET /ready should return 200."""
    response = await client.get("/ready")
    assert response.status_code == 200


# ── Authentication ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_unauthenticated_request_is_rejected(client: AsyncClient) -> None:
    """Endpoints requiring auth should return 403 without a Bearer token."""
    response = await client.get("/api/v1/workspaces/")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_authenticated_request_succeeds(client: AsyncClient) -> None:
    """Authenticated requests to workspace list should return 200."""
    response = await client.get("/api/v1/workspaces/", headers=_mock_headers())
    assert response.status_code == 200
    assert isinstance(response.json(), list)


# ── Workspace CRUD ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_list_workspace(client: AsyncClient) -> None:
    """POST then GET workspaces should return the created workspace."""
    headers = _mock_headers()

    # Create
    create_resp = await client.post(
        "/api/v1/workspaces/",
        json={"name": "Test Workspace", "slug": "test-ws"},
        headers=headers,
    )
    assert create_resp.status_code == 201
    ws = create_resp.json()
    assert ws["name"] == "Test Workspace"
    assert ws["slug"] == "test-ws"
    workspace_id = ws["id"]

    # List
    list_resp = await client.get("/api/v1/workspaces/", headers=headers)
    assert list_resp.status_code == 200
    workspaces = list_resp.json()
    assert any(w["id"] == workspace_id for w in workspaces)


# ── Project CRUD ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_get_project(client: AsyncClient) -> None:
    """POST a project under a workspace, then GET it by ID."""
    headers = _mock_headers()

    # Create workspace first
    ws_resp = await client.post(
        "/api/v1/workspaces/",
        json={"name": "Project WS", "slug": "proj-ws"},
        headers=headers,
    )
    workspace_id = ws_resp.json()["id"]

    # Create project
    project_resp = await client.post(
        "/api/v1/projects/",
        json={
            "workspace_id": workspace_id,
            "name": "Test Project",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "budget_total": 50000.0,
        },
        headers=headers,
    )
    assert project_resp.status_code == 201
    project = project_resp.json()
    project_id = project["id"]
    assert project["name"] == "Test Project"

    # Get by ID
    get_resp = await client.get(
        f"/api/v1/projects/{project_id}",
        headers=headers,
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Test Project"


# ── Phase + Task CRUD ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_phase_and_task(client: AsyncClient) -> None:
    """POST a phase and task under a project, verify WBS auto-generation."""
    headers = _mock_headers()

    # Setup: workspace + project
    ws = (await client.post(
        "/api/v1/workspaces/",
        json={"name": "Phase WS", "slug": "phase-ws"},
        headers=headers,
    )).json()

    proj = (await client.post(
        "/api/v1/projects/",
        json={
            "workspace_id": ws["id"],
            "name": "Phase Project",
            "start_date": "2026-01-01",
            "end_date": "2026-12-31",
        },
        headers=headers,
    )).json()

    # Create phase
    phase_resp = await client.post(
        "/api/v1/phases/",
        json={
            "project_id": proj["id"],
            "name": "Phase Alpha",
            "weight_percent": 50.0,
        },
        headers=headers,
    )
    assert phase_resp.status_code == 201
    phase = phase_resp.json()
    phase_id = phase["id"]

    # Create task
    task_resp = await client.post(
        "/api/v1/tasks/",
        json={
            "phase_id": phase_id,
            "name": "Task Alpha-1",
            "duration_days": 10,
        },
        headers=headers,
    )
    assert task_resp.status_code == 201
    task = task_resp.json()
    assert task["name"] == "Task Alpha-1"
    assert task["duration_days"] == 10
    # WBS code should be auto-generated
    assert task["wbs_code"] is not None


# ── EVM Endpoints ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_evm_indicators_endpoint(client: AsyncClient) -> None:
    """GET EVM indicators for a project should return a valid response."""
    headers = _mock_headers()

    # Setup: workspace + project
    ws = (await client.post(
        "/api/v1/workspaces/",
        json={"name": "EVM WS", "slug": "evm-ws"},
        headers=headers,
    )).json()

    proj = (await client.post(
        "/api/v1/projects/",
        json={
            "workspace_id": ws["id"],
            "name": "EVM Project",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "budget_total": 100000.0,
        },
        headers=headers,
    )).json()

    # GET EVM indicators
    evm_resp = await client.get(
        f"/api/v1/evm/project/{proj['id']}/indicators",
        headers=headers,
    )
    assert evm_resp.status_code == 200
    evm = evm_resp.json()
    assert "spi" in evm
    assert "cpi" in evm


# ── Export Endpoints ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pdf_export_endpoint(client: AsyncClient) -> None:
    """GET PDF export for a project should return 200 with PDF content type."""
    headers = _mock_headers()

    # Setup
    ws = (await client.post(
        "/api/v1/workspaces/",
        json={"name": "Export WS", "slug": "export-ws"},
        headers=headers,
    )).json()

    proj = (await client.post(
        "/api/v1/projects/",
        json={
            "workspace_id": ws["id"],
            "name": "Export Project",
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
        },
        headers=headers,
    )).json()

    # GET PDF export
    pdf_resp = await client.get(
        f"/api/v1/exports/project/{proj['id']}/pdf",
        headers=headers,
    )
    assert pdf_resp.status_code == 200
    assert "pdf" in pdf_resp.headers.get("content-type", "").lower()
