from __future__ import annotations

import abc
import uuid
from typing import Generic, List, Optional, TypeVar, Any

T = TypeVar("T")

class IRepository(Generic[T], abc.ABC):
    """Base repository interface."""

    @abc.abstractmethod
    async def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        """Fetch an entity by its UUID."""
        pass

    @abc.abstractmethod
    async def add(self, entity: T) -> T:
        """Add a new entity to the repository context."""
        pass

    @abc.abstractmethod
    async def delete(self, entity: T) -> None:
        """Delete an entity from the repository context."""
        pass

    @abc.abstractmethod
    async def commit(self) -> None:
        """Commit the current transaction context."""
        pass

    @abc.abstractmethod
    async def refresh(self, entity: T) -> None:
        """Refresh the state of the entity from the database."""
        pass

    @abc.abstractmethod
    async def flush(self) -> None:
        """Flush pending changes to the database context."""
        pass


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
from app.domain.models.resource_calendar import ResourceCalendar


class IWorkspaceRepository(IRepository[Workspace], abc.ABC):
    @abc.abstractmethod
    async def get_by_slug(self, slug: str) -> Optional[Workspace]:
        pass

    @abc.abstractmethod
    async def get_user_workspaces(self, user_id: uuid.UUID) -> List[Workspace]:
        pass

    @abc.abstractmethod
    async def add_member(self, member: WorkspaceMember) -> WorkspaceMember:
        pass


class IProjectRepository(IRepository[Project], abc.ABC):
    @abc.abstractmethod
    async def get_workspace_projects(self, workspace_id: uuid.UUID) -> List[Project]:
        pass


class IPhaseRepository(IRepository[Phase], abc.ABC):
    @abc.abstractmethod
    async def get_project_phases(self, project_id: uuid.UUID) -> List[Phase]:
        pass

    @abc.abstractmethod
    async def count_project_phases(self, project_id: uuid.UUID) -> int:
        pass


class ITaskRepository(IRepository[Task], abc.ABC):
    @abc.abstractmethod
    async def count_sibling_tasks(self, phase_id: uuid.UUID, parent_task_id: Optional[uuid.UUID] = None) -> int:
        pass

    @abc.abstractmethod
    async def get_project_tasks_with_relations(self, project_id: uuid.UUID) -> List[Task]:
        pass

    @abc.abstractmethod
    async def get_phase_tasks(self, phase_id: uuid.UUID) -> List[Task]:
        pass

    @abc.abstractmethod
    async def get_project_tasks(self, project_id: uuid.UUID) -> List[Task]:
        pass

    @abc.abstractmethod
    async def add_dependency(self, dependency: TaskDependency) -> TaskDependency:
        pass


class IResourceRepository(IRepository[Resource], abc.ABC):
    @abc.abstractmethod
    async def get_workspace_resources(self, workspace_id: uuid.UUID) -> List[Resource]:
        pass


class ITaskAssignmentRepository(IRepository[TaskAssignment], abc.ABC):
    @abc.abstractmethod
    async def get_task_assignments(self, task_id: uuid.UUID) -> List[TaskAssignment]:
        pass

    @abc.abstractmethod
    async def get_resource_assignments(self, resource_id: uuid.UUID) -> List[TaskAssignment]:
        pass


class IProgressLogRepository(IRepository[ProgressLog], abc.ABC):
    @abc.abstractmethod
    async def get_task_logs(self, task_id: uuid.UUID) -> List[ProgressLog]:
        pass

    @abc.abstractmethod
    async def get_project_logs(self, project_id: uuid.UUID) -> List[ProgressLog]:
        pass


class IDeliverableRepository(IRepository[Deliverable], abc.ABC):
    @abc.abstractmethod
    async def get_task_deliverables(self, task_id: uuid.UUID) -> List[Deliverable]:
        pass

    @abc.abstractmethod
    async def add_event(self, event: DeliverableEvent) -> DeliverableEvent:
        pass


class IRiskRepository(IRepository[Risk], abc.ABC):
    @abc.abstractmethod
    async def get_project_risks(self, project_id: uuid.UUID) -> List[Risk]:
        pass


class IBaselineRepository(IRepository[ProjectBaseline], abc.ABC):
    @abc.abstractmethod
    async def get_project_baselines(self, project_id: uuid.UUID) -> List[ProjectBaseline]:
        pass


class INotificationRepository(IRepository[Notification], abc.ABC):
    @abc.abstractmethod
    async def get_user_notifications(self, user_id: uuid.UUID) -> List[Notification]:
        pass

    @abc.abstractmethod
    async def mark_notifications_read(self, notification_ids: List[uuid.UUID], user_id: uuid.UUID) -> int:
        pass


class IAIInsightRepository(IRepository[AIInsight], abc.ABC):
    @abc.abstractmethod
    async def get_latest_project_insight(self, project_id: uuid.UUID) -> Optional[AIInsight]:
        pass
