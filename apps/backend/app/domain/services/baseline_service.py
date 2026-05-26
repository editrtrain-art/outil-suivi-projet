from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, List, Any, Optional
import structlog
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.baseline import ProjectBaseline
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.core.exceptions import NotFoundError

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class BaselineService:
    """Service handling project snapshot creation, activation, and variance calculations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_baseline(
        self,
        project_id: uuid.UUID,
        version_code: str,
        description: Optional[str] = None,
        is_active: bool = False,
        creator_id: Optional[uuid.UUID] = None,
    ) -> ProjectBaseline:
        """Create a frozen planning snapshot (baseline) of a project.

        Args:
            project_id: UUID of the project to snapshot.
            version_code: Version tag (e.g., 'B0', 'B1').
            description: Optional comments.
            is_active: If True, set this baseline as the active reference.
            creator_id: Optional UUID of the PM creator.

        Returns:
            ProjectBaseline: Persisted baseline snapshot model.
        """
        # Load project
        project = await self.db.get(Project, project_id)
        if not project:
            raise NotFoundError("Project", str(project_id))

        # Load all tasks with their schedules
        result = await self.db.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
        )
        tasks = result.scalars().all()

        # Build serialized snapshot state
        task_snapshots = []
        for t in tasks:
            task_snapshots.append({
                "id": str(t.id),
                "wbs_code": t.wbs_code,
                "name": t.name,
                "duration_days": t.duration_days,
                "start_date_scheduled": str(t.start_date_scheduled) if t.start_date_scheduled else None,
                "end_date_scheduled": str(t.end_date_scheduled) if t.end_date_scheduled else None,
                "early_start": str(t.early_start) if t.early_start else None,
                "early_finish": str(t.early_finish) if t.early_finish else None,
                "late_start": str(t.late_start) if t.late_start else None,
                "late_finish": str(t.late_finish) if t.late_finish else None,
                "total_float": t.total_float,
                "is_critical": t.is_critical,
                "is_milestone": t.is_milestone,
                "weight_percent": float(t.weight_percent or 0),
            })

        snapshot = {
            "project_name": project.name,
            "start_date": str(project.start_date),
            "end_date": str(project.end_date),
            "budget_total": float(project.budget_total or 0),
            "tasks": task_snapshots,
        }

        # Create baseline object
        baseline = ProjectBaseline(
            project_id=project_id,
            version_code=version_code,
            description=description,
            snapshot=snapshot,
            locked_by=creator_id,
            is_active=is_active,
        )
        self.db.add(baseline)
        await self.db.flush()

        if is_active:
            # Set all other project baselines to inactive
            await self.db.execute(
                update(ProjectBaseline)
                .where(ProjectBaseline.project_id == project_id)
                .where(ProjectBaseline.id != baseline.id)
                .values(is_active=False)
            )
            # Link project reference
            project.active_baseline_id = baseline.id
            self.db.add(project)

        await self.db.commit()
        await self.db.refresh(baseline)
        logger.info("project_baseline_created", project_id=str(project_id), version=version_code, is_active=is_active)
        return baseline

    async def get_project_baselines(self, project_id: uuid.UUID) -> List[ProjectBaseline]:
        """Fetch all baselines created for a project.

        Args:
            project_id: UUID of the project.

        Returns:
            List[ProjectBaseline]: List of baselines.
        """
        result = await self.db.execute(
            select(ProjectBaseline)
            .where(ProjectBaseline.project_id == project_id)
            .order_by(ProjectBaseline.created_at.desc())
        )
        return list(result.scalars().all())

    async def compare_baseline(self, baseline_id: uuid.UUID) -> Dict[str, Any]:
        """Compute scheduling variance (slippage) between a baseline snapshot and current task dates.

        Args:
            baseline_id: UUID of the baseline snapshot.

        Returns:
            Dict[str, Any]: Comparison variances listing start, finish, and duration drift.
        """
        baseline = await self.db.get(ProjectBaseline, baseline_id)
        if not baseline:
            raise NotFoundError("ProjectBaseline", str(baseline_id))

        # Fetch current project tasks
        result = await self.db.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == baseline.project_id)
        )
        current_tasks = result.scalars().all()

        # Construct lookup map of snapshot tasks by ID
        snap_tasks = {t["id"]: t for t in baseline.snapshot.get("tasks", [])}
        variances = []

        for curr in current_tasks:
            curr_id_str = str(curr.id)
            snap = snap_tasks.get(curr_id_str)

            if not snap:
                # Task created after baseline snapshot
                variances.append({
                    "task_id": curr_id_str,
                    "wbs_code": curr.wbs_code,
                    "name": curr.name,
                    "is_new": True,
                    "start_variance_days": 0,
                    "finish_variance_days": 0,
                    "duration_variance_days": 0,
                    "slip_status": "new",
                })
                continue

            # Parse baseline snapshot dates
            snap_start = snap.get("start_date_scheduled")
            snap_finish = snap.get("end_date_scheduled")
            snap_duration = snap.get("duration_days") or 1

            start_var = 0
            finish_var = 0
            duration_var = (curr.duration_days or 1) - snap_duration

            if snap_start and curr.start_date_scheduled:
                start_var = (curr.start_date_scheduled - date.fromisoformat(snap_start)).days

            if snap_finish and curr.end_date_scheduled:
                finish_var = (curr.end_date_scheduled - date.fromisoformat(snap_finish)).days

            slip_status = "on_track"
            if finish_var > 0:
                slip_status = "delayed"
            elif finish_var < 0:
                slip_status = "ahead"

            variances.append({
                "task_id": curr_id_str,
                "wbs_code": curr.wbs_code,
                "name": curr.name,
                "is_new": False,
                "start_variance_days": start_var,
                "finish_variance_days": finish_var,
                "duration_variance_days": duration_var,
                "slip_status": slip_status,
            })

        return {
            "baseline_id": str(baseline_id),
            "version_code": baseline.version_code,
            "created_at": str(baseline.created_at),
            "variances": variances,
        }
