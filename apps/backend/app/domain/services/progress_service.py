"""Domain service for progress logging.

Handles creation and retrieval of task progress log entries,
which feed into the EVM computation pipeline.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List, Optional

import structlog

from app.core.exceptions import NotFoundError
from app.domain.models.progress_log import ProgressLog
from app.domain.repositories.interfaces import IProgressLogRepository, ITaskRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


from sqlalchemy.ext.asyncio import AsyncSession

class ProgressService:
    """Service for managing task progress logs."""

    def __init__(
        self,
        progress_repo: IProgressLogRepository | AsyncSession,
        task_repo: ITaskRepository | None = None,
    ) -> None:
        """Initialize with progress and task repositories.

        Args:
            progress_repo: IProgressLogRepository or AsyncSession.
            task_repo: ITaskRepository or None.
        """
        if isinstance(progress_repo, AsyncSession):
            db = progress_repo
            from app.infrastructure.repositories.sqlalchemy_repos import (
                SQLAlchemyProgressLogRepository,
                SQLAlchemyTaskRepository,
            )
            self.progress_repo = SQLAlchemyProgressLogRepository(db)
            self.task_repo = SQLAlchemyTaskRepository(db)
        else:
            self.progress_repo = progress_repo
            self.task_repo = task_repo  # type: ignore

    async def log_progress(
        self,
        task_id: uuid.UUID,
        log_date: date,
        physical_percent: float,
        actual_hours: float = 0.0,
        actual_cost_dh: float = 0.0,
        logged_by: Optional[uuid.UUID] = None,
        notes: Optional[str] = None,
    ) -> ProgressLog:
        """Record a progress entry for a task.

        Args:
            task_id: UUID of the task.
            log_date: Date of the progress report.
            physical_percent: Physical completion percentage (0-100).
            actual_hours: Hours worked.
            actual_cost_dh: Actual cost in currency.
            logged_by: UUID of the user logging progress.
            notes: Optional notes.

        Returns:
            ProgressLog: The persisted log entry.

        Raises:
            NotFoundError: If the task does not exist.
        """
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError("Task", str(task_id))

        entry = ProgressLog(
            task_id=task_id,
            log_date=log_date,
            physical_percent=physical_percent,
            actual_hours=actual_hours,
            actual_cost_dh=actual_cost_dh,
            logged_by=logged_by,
            notes=notes,
        )
        await self.progress_repo.add(entry)

        # Update task's physical percent to latest
        task.progress_percent = physical_percent
        await self.task_repo.add(task)

        await self.progress_repo.commit()
        await self.progress_repo.refresh(entry)
        logger.info(
            "progress_logged",
            task_id=str(task_id),
            percent=physical_percent,
            date=str(log_date),
        )
        return entry

    async def get_task_progress_history(
        self, task_id: uuid.UUID
    ) -> List[ProgressLog]:
        """Retrieve full progress history for a task, newest first.

        Args:
            task_id: UUID of the task.

        Returns:
            List of ProgressLog entries ordered by date descending.
        """
        logs = await self.progress_repo.get_task_logs(task_id)
        # Sort desc by date
        return sorted(logs, key=lambda x: x.log_date, reverse=True)

    async def get_latest_progress(
        self, task_id: uuid.UUID
    ) -> Optional[ProgressLog]:
        """Retrieve the most recent progress entry for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            Latest ProgressLog or None if no logs exist.
        """
        logs = await self.progress_repo.get_task_logs(task_id)
        if not logs:
            return None
        return max(logs, key=lambda x: x.log_date)
