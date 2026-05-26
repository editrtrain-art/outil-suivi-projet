from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import AsyncGenerator, List
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.domain.models.base import Base
from app.domain.models.workspace import Workspace
from app.domain.models.user import User
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.task_assignment import TaskAssignment
from app.domain.models.resource import Resource
from app.domain.models.risk import Risk
from app.domain.services.baseline_service import BaselineService
from app.domain.services.resource_leveler import ResourceLevelerService
from app.domain.services.export_service import ExportService
from app.domain.services.llm_service import LLMService


@pytest_asyncio.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an in-memory SQLite database session for unit testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session

    await engine.dispose()


async def seed_data(session: AsyncSession) -> tuple[Workspace, User, Project, Phase, list[Task], Resource]:
    """Seed a basic workspace, PM user, project, phase, resource, and tasks."""
    user = User(
        id=uuid.uuid4(),
        email="pm@test.com",
        first_name="Project",
        last_name="Manager",
    )
    workspace = Workspace(
        id=uuid.uuid4(),
        name="Test Workspace",
        slug="test-workspace",
        created_by=user.id,
    )
    session.add_all([user, workspace])
    await session.flush()

    project = Project(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Build Platform",
        start_date=date.today(),
        end_date=date.today() + timedelta(days=20),
        budget_total=100000.0,
        status="active",
        pm_user_id=user.id,
    )
    session.add(project)
    await session.flush()

    phase = Phase(
        id=uuid.uuid4(),
        project_id=project.id,
        name="Phase 1",
        wbs_code="1.0",
        order_index=1,
    )
    session.add(phase)
    await session.flush()

    # Create 2 parallel tasks
    task1 = Task(
        id=uuid.uuid4(),
        phase_id=phase.id,
        wbs_code="1.1",
        name="Task A",
        duration_days=5,
        start_date_scheduled=date.today(),
        end_date_scheduled=date.today() + timedelta(days=5),
        early_start=date.today(),
        early_finish=date.today() + timedelta(days=5),
        late_start=date.today(),
        late_finish=date.today() + timedelta(days=5),
        total_float=0,
        free_float=0,
        is_critical=True,
        weight_percent=50.0,
        priority=1,
    )
    task2 = Task(
        id=uuid.uuid4(),
        phase_id=phase.id,
        wbs_code="1.2",
        name="Task B",
        duration_days=5,
        start_date_scheduled=date.today(),
        end_date_scheduled=date.today() + timedelta(days=5),
        early_start=date.today(),
        early_finish=date.today() + timedelta(days=5),
        late_start=date.today() + timedelta(days=2),
        late_finish=date.today() + timedelta(days=7),
        total_float=2,
        free_float=2,
        is_critical=False,
        weight_percent=50.0,
        priority=2,
    )
    session.add_all([task1, task2])
    await session.flush()

    resource = Resource(
        id=uuid.uuid4(),
        workspace_id=workspace.id,
        name="Engineer 1",
        role="Developer",
        monthly_capacity_hours=168.0,  # 100% capacity
    )
    session.add(resource)
    await session.flush()

    await session.commit()
    return workspace, user, project, phase, [task1, task2], resource


@pytest.mark.asyncio
async def test_baseline_creation_and_comparison(async_session: AsyncSession) -> None:
    """Test creating a snapshot and performing variance comparison on tasks."""
    _, pm_user, project, _, tasks, _ = await seed_data(async_session)
    task1, task2 = tasks

    baseline_service = BaselineService(async_session)
    
    # 1. Create baseline snapshot B0
    baseline = await baseline_service.create_baseline(
        project_id=project.id,
        version_code="B0",
        description="Initial approved plan",
        is_active=True,
        creator_id=pm_user.id,
    )

    assert baseline.version_code == "B0"
    assert baseline.is_active is True
    assert len(baseline.snapshot["tasks"]) == 2

    # 2. Modify task schedule (introduce 3 days delay)
    task1.end_date_scheduled = task1.end_date_scheduled + timedelta(days=3)
    async_session.add(task1)
    await async_session.commit()

    # 3. Compare current planning state with B0
    comparison = await baseline_service.compare_baseline(baseline.id)
    
    assert comparison["baseline_id"] == str(baseline.id)
    assert comparison["version_code"] == "B0"
    
    variances = {v["task_id"]: v for v in comparison["variances"]}
    
    # Task 1 has 3 days delay
    assert variances[str(task1.id)]["finish_variance_days"] == 3
    assert variances[str(task1.id)]["slip_status"] == "delayed"

    # Task 2 has no modifications
    assert variances[str(task2.id)]["finish_variance_days"] == 0
    assert variances[str(task2.id)]["slip_status"] == "on_track"


@pytest.mark.asyncio
async def test_resource_leveler_load_and_leveling(async_session: AsyncSession) -> None:
    """Test resource workload profiling and shunting overload tasks."""
    _, _, project, _, tasks, resource = await seed_data(async_session)
    task1, task2 = tasks

    # Over-allocate resource by assigning to both overlapping parallel tasks
    assignment1 = TaskAssignment(
        id=uuid.uuid4(),
        task_id=task1.id,
        resource_id=resource.id,
        allocation_percent=100.0,
    )
    assignment2 = TaskAssignment(
        id=uuid.uuid4(),
        task_id=task2.id,
        resource_id=resource.id,
        allocation_percent=100.0,
    )
    async_session.add_all([assignment1, assignment2])
    await async_session.commit()

    leveler = ResourceLevelerService(async_session)

    # 1. Check daily load profile (should be 200% allocation on day 1)
    load = await leveler.get_daily_load(project.id)
    assert len(load["timeline"]) > 0
    assert load["resources"][str(resource.id)]["daily_allocations"][0] == 200.0

    # 2. Execute resource leveling
    await leveler.level_resources(project.id)

    # Reload tasks to check dates
    await async_session.refresh(task1)
    await async_session.refresh(task2)

    # Task 2 (lower priority/higher float) should be shunted past Task 1
    # Task 1 starts on day 0, duration 5 -> ends day 5
    # Task 2 should be delayed to start after Task 1
    assert task2.start_date_scheduled > task1.start_date_scheduled


@pytest.mark.asyncio
async def test_document_exporters(async_session: AsyncSession) -> None:
    """Test generating PDF and Excel documents."""
    _, _, project, _, _, _ = await seed_data(async_session)

    exporter = ExportService(async_session)
    evm_mock = {
        "pv": 1000.0,
        "ev": 900.0,
        "ac": 1200.0,
        "spi": 0.9,
        "cpi": 0.75,
        "eac": 1333.3,
    }

    # 1. Test PDF Export
    pdf_bytes = await exporter.generate_project_pdf(project.id, evm_mock)
    assert len(pdf_bytes) > 0
    assert pdf_bytes[:4] == b"%PDF"  # standard PDF header prefix

    # 2. Test Excel Export
    excel_bytes = await exporter.generate_project_excel(project.id)
    assert len(excel_bytes) > 0
    assert excel_bytes[:2] == b"PK"  # standard zip header prefix for xlsx files


@pytest.mark.asyncio
async def test_llm_predictive_audit_fallback(async_session: AsyncSession) -> None:
    """Test LLM report compilation fallback when the LLM server is offline."""
    _, pm_user, project, _, _, _ = await seed_data(async_session)

    # Seed a project risk
    risk = Risk(
        id=uuid.uuid4(),
        project_id=project.id,
        title="Key developer departure",
        category="resources",
        probability=4,
        impact=4,
        risk_score=16,
        status="active",
        mitigation="Cross-train other developers",
    )
    async_session.add(risk)
    await async_session.commit()

    llm_service = LLMService(async_session)
    report = await llm_service.generate_project_audit(project.id, triggered_by=pm_user.id)

    # Audit markdown check
    assert "NEXUS AI Project Performance" in report
    assert "Key developer departure" in report or "Resource Leveling" in report


@pytest.mark.asyncio
async def test_risk_contingency_and_notifications(async_session: AsyncSession) -> None:
    """Test task-risk linking, contingency day calculation, CPM recalculation, and notifications."""
    from app.domain.services.risk_service import RiskService
    from app.domain.services.task_service import TaskService
    from app.domain.models.audit_log import Notification
    from sqlalchemy import select

    _, pm_user, project, _, tasks, _ = await seed_data(async_session)
    task = tasks[0]  # Task A has duration_days=5

    # 1. Create a critical risk (probability=4, impact=4 -> score=16, threshold=15)
    risk_service = RiskService(async_session)
    risk = await risk_service.create_risk(
        project_id=project.id,
        title="Supplier Delays",
        probability=4,
        impact=4,
        category="external",
        owner_id=pm_user.id,
        contingency_threshold=15,
        contingency_factor=0.20,  # 20% increase
    )

    assert risk.risk_score == 16
    assert risk.contingency_threshold == 15

    # Verify notification was created
    result = await async_session.execute(select(Notification).where(Notification.user_id == pm_user.id))
    notifications = result.scalars().all()
    assert len(notifications) > 0
    assert "Supplier Delays" in notifications[0].title

    # 2. Link task to risk
    await risk_service.link_task(risk.id, task.id)

    # Reload task to check contingency days and end dates
    await async_session.refresh(task)
    # 5 days * 0.20 = 1.0 day contingency
    assert task.contingency_days == 1
    # CPM should have recalculated. 5 days base + 1 day contingency = 6 days effective duration.
    # Verify that scheduled finish date has shifted
    assert task.early_finish == task.early_start + timedelta(days=6)

    # 3. Update risk to be mitigated / low score (probability=2, impact=2 -> score=4)
    await risk_service.update_risk(risk.id, probability=2, impact=2)

    # Reload task
    await async_session.refresh(task)
    # Contingency days should drop back to 0 because risk score (4) < threshold (15)
    assert task.contingency_days == 0
    assert task.early_finish == task.early_start + timedelta(days=5)
