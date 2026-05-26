"""Central registry for all domain models.

Imports every model class to ensure SQLAlchemy metadata is fully populated
for Alembic migrations and relationship resolution.
"""

from __future__ import annotations

from app.domain.models.base import Base
from app.domain.models.user import User
from app.domain.models.workspace import Workspace
from app.domain.models.workspace_member import WorkspaceMember
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.task_dependency import TaskDependency
from app.domain.models.resource import Resource
from app.domain.models.task_assignment import TaskAssignment
from app.domain.models.resource_calendar import ResourceCalendar
from app.domain.models.progress_log import ProgressLog
from app.domain.models.deliverable import Deliverable
from app.domain.models.deliverable_event import DeliverableEvent
from app.domain.models.baseline import ProjectBaseline
from app.domain.models.risk import Risk, RiskTaskLink
from app.domain.models.audit_log import AuditLog, Notification, AIInsight

__all__ = [
    "Base",
    "User",
    "Workspace",
    "WorkspaceMember",
    "Project",
    "Phase",
    "Task",
    "TaskDependency",
    "Resource",
    "TaskAssignment",
    "ResourceCalendar",
    "ProgressLog",
    "Deliverable",
    "DeliverableEvent",
    "ProjectBaseline",
    "Risk",
    "RiskTaskLink",
    "AuditLog",
    "Notification",
    "AIInsight",
]
