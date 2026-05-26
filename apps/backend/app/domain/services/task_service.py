"""Task service implementation.

Handles task lifecycle, WBS hierarchy, and CPM triggers.
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta
from typing import List, Optional

from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.services.cpm_engine import CPMEngine, TaskNode, DependencyLink, DependencyType
from app.core.exceptions import NotFoundError, ValidationError
from app.domain.repositories.interfaces import ITaskRepository, IPhaseRepository, IProjectRepository


from sqlalchemy.ext.asyncio import AsyncSession

class TaskService:
    """Service layer for task management, WBS codes, and CPM integration."""

    def __init__(
        self,
        task_repo: ITaskRepository | AsyncSession,
        phase_repo: IPhaseRepository | None = None,
        project_repo: IProjectRepository | None = None,
    ) -> None:
        if isinstance(task_repo, AsyncSession):
            db = task_repo
            from app.infrastructure.repositories.sqlalchemy_repos import (
                SQLAlchemyTaskRepository,
                SQLAlchemyPhaseRepository,
                SQLAlchemyProjectRepository,
            )
            self.task_repo = SQLAlchemyTaskRepository(db)
            self.phase_repo = SQLAlchemyPhaseRepository(db)
            self.project_repo = SQLAlchemyProjectRepository(db)
        else:
            self.task_repo = task_repo
            self.phase_repo = phase_repo  # type: ignore
            self.project_repo = project_repo  # type: ignore

    # ── WBS helpers ─────────────────────────────────────────────────────────

    async def _next_wbs_code(
        self,
        phase_id: uuid.UUID,
        parent_task_id: Optional[uuid.UUID] = None,
    ) -> str:
        """Generate the next sequential WBS code for a task.

        Level 2 (no parent): 1.1, 1.2, 1.3 ...
        Level 3+ (with parent): 1.1.1, 1.1.2 ...
        """
        count = await self.task_repo.count_sibling_tasks(phase_id, parent_task_id)

        if parent_task_id is None:
            phase = await self.phase_repo.get_by_id(phase_id)
            if not phase:
                raise NotFoundError("Phase", str(phase_id))
            # phase.wbs_code is like "1.0" — derive prefix from it
            phase_num = phase.wbs_code.split(".")[0]
            return f"{phase_num}.{count + 1}"
        else:
            parent = await self.task_repo.get_by_id(parent_task_id)
            if not parent:
                raise NotFoundError("Task", str(parent_task_id))
            return f"{parent.wbs_code}.{count + 1}"

    # ── CRUD ────────────────────────────────────────────────────────────────

    async def create_task(
        self,
        phase_id: uuid.UUID,
        name: str,
        duration_days: int = 1,
        parent_task_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        weight_percent: float = 0.0,
        priority: int = 3,
        is_milestone: bool = False,
    ) -> Task:
        """Create a task with auto-generated WBS code, then trigger CPM."""
        wbs_code = await self._next_wbs_code(phase_id, parent_task_id)

        task = Task(
            phase_id=phase_id,
            parent_task_id=parent_task_id,
            name=name,
            wbs_code=wbs_code,
            description=description,
            duration_days=duration_days,
            weight_percent=weight_percent,
            priority=priority,
            is_milestone=is_milestone or (duration_days == 0),
            status="not_started",
        )
        await self.task_repo.add(task)
        await self.task_repo.flush()  # get task.id before CPM

        project_id = await self._get_project_id_for_phase(phase_id)
        if project_id:
            await self.run_cpm_for_project(project_id)

        await self.task_repo.commit()
        await self.task_repo.refresh(task)
        return task

    async def get_task_by_id(self, task_id: uuid.UUID) -> Task:
        """Fetch a task by ID."""
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", str(task_id))
        return task

    async def get_phase_tasks(self, phase_id: uuid.UUID) -> List[Task]:
        """Fetch all tasks for a phase, ordered by WBS code."""
        return await self.task_repo.get_phase_tasks(phase_id)

    async def get_project_tasks(self, project_id: uuid.UUID) -> List[Task]:
        """Fetch all tasks for a project, ordered by WBS code."""
        return await self.task_repo.get_project_tasks(project_id)

    async def update_task(self, task_id: uuid.UUID, **kwargs) -> Task:
        """Update a task and trigger CPM recalculation if dates/durations change."""
        task = await self.get_task_by_id(task_id)

        # Track if duration or manual schedules change (requires CPM run)
        cpm_trigger_fields = {"duration_days", "start_date_scheduled", "end_date_scheduled"}
        trigger_cpm = False

        for key, value in kwargs.items():
            if hasattr(task, key):
                if key in cpm_trigger_fields and getattr(task, key) != value:
                    trigger_cpm = True
                setattr(task, key, value)

        # Enforce milestone duration constraint
        if task.is_milestone:
            task.duration_days = 0

        await self.task_repo.flush()

        if trigger_cpm:
            project_id = await self._get_project_id_for_phase(task.phase_id)
            if project_id:
                await self.run_cpm_for_project(project_id)

        await self.task_repo.commit()
        await self.task_repo.refresh(task)
        return task

    async def delete_task(self, task_id: uuid.UUID) -> None:
        """Delete a task (cascades to sub-tasks and dependencies)."""
        task = await self.get_task_by_id(task_id)
        await self.task_repo.delete(task)
        await self.task_repo.commit()

    # ── Dependencies ────────────────────────────────────────────────────────

    async def add_dependency(
        self,
        task_id: uuid.UUID,
        predecessor_id: uuid.UUID,
        dep_type: str = "FS",
        lag_days: int = 0,
    ) -> TaskDependency:
        """Add a dependency and trigger CPM recalculation."""
        if task_id == predecessor_id:
            raise ValidationError(message="A task cannot depend on itself")

        dependency = TaskDependency(
            task_id=task_id,
            predecessor_task_id=predecessor_id,
            dependency_type=dep_type,
            lag_days=lag_days,
        )
        await self.task_repo.add_dependency(dependency)
        await self.task_repo.flush()

        # Get the phase from the task, then the project
        task = await self.get_task_by_id(task_id)
        project_id = await self._get_project_id_for_phase(task.phase_id)
        if project_id:
            await self.run_cpm_for_project(project_id)

        await self.task_repo.commit()
        return dependency

    # ── CPM Engine integration ───────────────────────────────────────────────

    async def _get_project_id_for_phase(self, phase_id: uuid.UUID) -> Optional[uuid.UUID]:
        """Resolve phase_id -> project_id."""
        phase = await self.phase_repo.get_by_id(phase_id)
        return phase.project_id if phase else None

    async def run_cpm_for_project(self, project_id: uuid.UUID) -> None:
        """Run CPM for all tasks in a project and persist results with real dates.

        Steps:
        1. Load all tasks with their dependencies.
        2. Build CPMEngine TaskNodes.
        3. Run forward/backward pass.
        4. Map integer day-offsets back to calendar dates using the project start_date.
        5. Persist ES, EF, LS, LF, TF, FF, is_critical on each task.
        """
        # Load project for start_date reference
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        project_start: date = project.start_date

        # Load all tasks with dependencies and linked risks (join through phases)
        tasks = await self.task_repo.get_project_tasks_with_relations(project_id)

        if not tasks:
            return

        # Build CPM nodes
        import math
        nodes: List[TaskNode] = []
        for t in tasks:
            # Calculate contingency days based on active, threshold-breaching risks
            contingency_days = 0
            for r in t.linked_risks:
                if r.status == "active" and r.risk_score >= r.contingency_threshold:
                    contingency_days += int(math.ceil(t.duration_days * float(r.contingency_factor)))
            
            t.contingency_days = contingency_days
            effective_duration = t.duration_days + contingency_days

            deps = [
                DependencyLink(
                    predecessor_id=d.predecessor_task_id,
                    dep_type=DependencyType(d.dependency_type),
                    lag_days=d.lag_days,
                )
                for d in t.dependencies
                if d.predecessor_task_id in {task.id for task in tasks}
            ]
            nodes.append(TaskNode(id=t.id, duration_days=effective_duration, dependencies=deps))

        # Run CPM engine
        engine = CPMEngine(nodes)
        computed = engine.compute()

        # Map results back to real dates and persist
        for t in tasks:
            node = computed.get(t.id)
            if node is None:
                continue
            t.early_start = project_start + timedelta(days=node.early_start)
            t.early_finish = project_start + timedelta(days=node.early_finish)
            t.late_start = project_start + timedelta(days=node.late_start)
            t.late_finish = project_start + timedelta(days=node.late_finish)
            t.total_float = node.total_float
            t.free_float = node.free_float
            t.is_critical = node.is_critical
            # Update scheduled dates if not manually overridden
            if not t.start_date_scheduled:
                t.start_date_scheduled = t.early_start
            if not t.end_date_scheduled:
                t.end_date_scheduled = t.early_finish
