from __future__ import annotations

import uuid
from typing import List, Optional, Type, TypeVar

from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.repositories.interfaces import (
    IRepository,
    IWorkspaceRepository,
    IProjectRepository,
    IPhaseRepository,
    ITaskRepository,
    IResourceRepository,
    ITaskAssignmentRepository,
    IProgressLogRepository,
    IDeliverableRepository,
    IRiskRepository,
    IBaselineRepository,
    INotificationRepository,
    IAIInsightRepository,
)
from app.domain.models.workspace import Workspace
from app.domain.models.workspace_member import WorkspaceMember
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.resource import Resource
from app.domain.models.task_assignment import TaskAssignment
from app.domain.models.progress_log import ProgressLog
from app.domain.models.deliverable import Deliverable
from app.domain.models.deliverable_event import DeliverableEvent
from app.domain.models.baseline import ProjectBaseline
from app.domain.models.risk import Risk
from app.domain.models.audit_log import AuditLog, AIInsight, Notification

T = TypeVar("T")

class SQLAlchemyRepository(IRepository[T]):
    """SQLAlchemy implementation of the base repository."""

    def __init__(self, session: AsyncSession, model_cls: Type[T]) -> None:
        self.session = session
        self.model_cls = model_cls

    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        return await self.session.get(self.model_cls, id)

    async def add(self, entity: T) -> T:
        self.session.add(entity)
        return entity

    async def delete(self, entity: T) -> None:
        await self.session.delete(entity)

    async def commit(self) -> None:
        await self.session.commit()

    async def refresh(self, entity: T) -> None:
        await self.session.refresh(entity)

    async def flush(self) -> None:
        await self.session.flush()


class SQLAlchemyWorkspaceRepository(SQLAlchemyRepository[Workspace], IWorkspaceRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Workspace)

    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        result = await self.session.execute(
            select(Workspace).where(Workspace.slug == slug)
        )
        return result.scalar_one_or_none()

    async def get_user_workspaces(self, user_id: uuid.UUID) -> List[Workspace]:
        result = await self.session.execute(
            select(Workspace)
            .join(WorkspaceMember)
            .where(WorkspaceMember.user_id == user_id)
        )
        return list(result.scalars().all())

    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        self.session.add(member)
        return member


class SQLAlchemyProjectRepository(SQLAlchemyRepository[Project], IProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Project)

    async def get_workspace_projects(self, workspace_id: uuid.UUID) -> List[Project]:
        result = await self.session.execute(
            select(Project).where(Project.workspace_id == workspace_id)
        )
        return list(result.scalars().all())


class SQLAlchemyPhaseRepository(SQLAlchemyRepository[Phase], IPhaseRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Phase)

    async def get_project_phases(self, project_id: uuid.UUID) -> List[Phase]:
        result = await self.session.execute(
            select(Phase).where(Phase.project_id == project_id).order_by(Phase.order_index)
        )
        return list(result.scalars().all())

    async def count_project_phases(self, project_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count(Phase.id)).where(Phase.project_id == project_id)
        )
        return result.scalar() or 0


class SQLAlchemyTaskRepository(SQLAlchemyRepository[Task], ITaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)

    async def count_sibling_tasks(self, phase_id: uuid.UUID, parent_task_id: Optional[uuid.UUID] = None) -> int:
        if parent_task_id is None:
            result = await self.session.execute(
                select(func.count(Task.id)).where(
                    Task.phase_id == phase_id,
                    Task.parent_task_id.is_(None),
                )
            )
        else:
            result = await self.session.execute(
                select(func.count(Task.id)).where(
                    Task.parent_task_id == parent_task_id
                )
            )
        return result.scalar() or 0

    async def get_project_tasks_with_relations(self, project_id: uuid.UUID) -> List[Task]:
        result = await self.session.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
            .options(
                selectinload(Task.dependencies),
                selectinload(Task.linked_risks),
                selectinload(Task.assignments).selectinload(TaskAssignment.resource),
            )
        )
        return list(result.scalars().all())

    async def get_phase_tasks(self, phase_id: uuid.UUID) -> List[Task]:
        result = await self.session.execute(
            select(Task)
            .where(Task.phase_id == phase_id)
            .order_by(Task.wbs_code)
        )
        return list(result.scalars().all())

    async def get_project_tasks(self, project_id: uuid.UUID) -> List[Task]:
        result = await self.session.execute(
            select(Task)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
            .order_by(Task.wbs_code)
        )
        return list(result.scalars().all())

    async def add_dependency(self, dependency: TaskDependency) -> TaskDependency:
        self.session.add(dependency)
        return dependency


class SQLAlchemyResourceRepository(SQLAlchemyRepository[Resource], IResourceRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Resource)

    async def get_workspace_resources(self, workspace_id: uuid.UUID) -> List[Resource]:
        result = await self.session.execute(
            select(Resource).where(Resource.workspace_id == workspace_id)
        )
        return list(result.scalars().all())


class SQLAlchemyTaskAssignmentRepository(SQLAlchemyRepository[TaskAssignment], ITaskAssignmentRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TaskAssignment)

    async def get_task_assignments(self, task_id: uuid.UUID) -> List[TaskAssignment]:
        result = await self.session.execute(
            select(TaskAssignment)
            .where(TaskAssignment.task_id == task_id)
            .options(selectinload(TaskAssignment.resource))
        )
        return list(result.scalars().all())

    async def get_resource_assignments(self, resource_id: uuid.UUID) -> List[TaskAssignment]:
        result = await self.session.execute(
            select(TaskAssignment).where(TaskAssignment.resource_id == resource_id)
        )
        return list(result.scalars().all())


class SQLAlchemyProgressLogRepository(SQLAlchemyRepository[ProgressLog], IProgressLogRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProgressLog)

    async def get_task_logs(self, task_id: uuid.UUID) -> List[ProgressLog]:
        result = await self.session.execute(
            select(ProgressLog).where(ProgressLog.task_id == task_id).order_by(ProgressLog.log_date)
        )
        return list(result.scalars().all())

    async def get_project_logs(self, project_id: uuid.UUID) -> List[ProgressLog]:
        result = await self.session.execute(
            select(ProgressLog)
            .join(Task, ProgressLog.task_id == Task.id)
            .join(Phase, Task.phase_id == Phase.id)
            .where(Phase.project_id == project_id)
            .order_by(ProgressLog.log_date)
        )
        return list(result.scalars().all())


class SQLAlchemyDeliverableRepository(SQLAlchemyRepository[Deliverable], IDeliverableRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Deliverable)

    async def get_task_deliverables(self, task_id: uuid.UUID) -> List[Deliverable]:
        result = await self.session.execute(
            select(Deliverable).where(Deliverable.task_id == task_id)
        )
        return list(result.scalars().all())

    async def add_event(self, event: DeliverableEvent) -> DeliverableEvent:
        self.session.add(event)
        return event


class SQLAlchemyRiskRepository(SQLAlchemyRepository[Risk], IRiskRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Risk)

    async def get_project_risks(self, project_id: uuid.UUID) -> List[Risk]:
        result = await self.session.execute(
            select(Risk).where(Risk.project_id == project_id)
        )
        return list(result.scalars().all())


class SQLAlchemyBaselineRepository(SQLAlchemyRepository[ProjectBaseline], IBaselineRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ProjectBaseline)

    async def get_project_baselines(self, project_id: uuid.UUID) -> List[ProjectBaseline]:
        result = await self.session.execute(
            select(ProjectBaseline).where(ProjectBaseline.project_id == project_id).order_by(ProjectBaseline.created_at.desc())
        )
        return list(result.scalars().all())


class SQLAlchemyNotificationRepository(SQLAlchemyRepository[Notification], INotificationRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Notification)

    async def get_user_notifications(self, user_id: uuid.UUID) -> List[Notification]:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())

    async def mark_notifications_read(self, notification_ids: List[uuid.UUID], user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            update(Notification)
            .where(Notification.id.in_(notification_ids))
            .where(Notification.user_id == user_id)
            .values(is_read=True)
        )
        return result.rowcount  # type: ignore[union-attr]


class SQLAlchemyAIInsightRepository(SQLAlchemyRepository[AIInsight], IAIInsightRepository):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AIInsight)

    async def get_latest_project_insight(self, project_id: uuid.UUID) -> Optional[AIInsight]:
        result = await self.session.execute(
            select(AIInsight)
            .where(AIInsight.project_id == project_id)
            .order_by(AIInsight.generated_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()
