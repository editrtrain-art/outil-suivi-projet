"""Domain service for task-resource assignments.

Handles CRUD operations for task assignments (resource allocations),
including allocation percent and planned hours.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

import structlog

from app.core.exceptions import NotFoundError
from app.domain.models.task_assignment import TaskAssignment
from app.domain.repositories.interfaces import ITaskAssignmentRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


from sqlalchemy.ext.asyncio import AsyncSession

class AssignmentService:
    """Service for managing task-resource assignments."""

    def __init__(self, assignment_repo: ITaskAssignmentRepository | AsyncSession) -> None:
        """Initialize with assignment repository.

        Args:
            assignment_repo: ITaskAssignmentRepository for database operations.
        """
        if isinstance(assignment_repo, AsyncSession):
            from app.infrastructure.repositories.sqlalchemy_repos import SQLAlchemyTaskAssignmentRepository
            self.assignment_repo = SQLAlchemyTaskAssignmentRepository(assignment_repo)
        else:
            self.assignment_repo = assignment_repo

    async def create_assignment(
        self,
        task_id: uuid.UUID,
        resource_id: uuid.UUID,
        allocation_percent: float = 100.0,
        planned_hours: Optional[float] = None,
    ) -> TaskAssignment:
        """Create a task-resource assignment.

        Args:
            task_id: UUID of the task.
            resource_id: UUID of the resource.
            allocation_percent: Percentage of resource capacity (0-100).
            planned_hours: Planned effort hours.

        Returns:
            TaskAssignment: The persisted assignment.
        """
        assignment = TaskAssignment(
            task_id=task_id,
            resource_id=resource_id,
            allocation_percent=allocation_percent,
            planned_hours=planned_hours,
        )
        await self.assignment_repo.add(assignment)
        await self.assignment_repo.commit()
        await self.assignment_repo.refresh(assignment)
        logger.info(
            "assignment_created",
            task_id=str(task_id),
            resource_id=str(resource_id),
        )
        return assignment

    async def get_task_assignments(self, task_id: uuid.UUID) -> List[TaskAssignment]:
        """Retrieve all assignments for a task.

        Args:
            task_id: UUID of the task.

        Returns:
            List of TaskAssignment records.
        """
        return await self.assignment_repo.get_task_assignments(task_id)

    async def delete_assignment(self, assignment_id: uuid.UUID) -> None:
        """Delete a task assignment by ID.

        Args:
            assignment_id: UUID of the assignment to delete.

        Raises:
            NotFoundError: If assignment does not exist.
        """
        assignment = await self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            raise NotFoundError("TaskAssignment", str(assignment_id))
        await self.assignment_repo.delete(assignment)
        await self.assignment_repo.commit()
        logger.info("assignment_deleted", assignment_id=str(assignment_id))
