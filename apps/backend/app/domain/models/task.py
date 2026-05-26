"""Task model definition.

Tasks are the atomic units of work in a project, belonging to a Phase.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Date, Numeric, Integer, Boolean, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.phase import Phase
    from app.domain.models.task_dependency import TaskDependency
    from app.domain.models.task_assignment import TaskAssignment
    from app.domain.models.progress_log import ProgressLog
    from app.domain.models.deliverable import Deliverable
    from app.domain.models.risk import Risk


class Task(Base, TimestampMixin):
    """A task or milestone within a project phase.

    Attributes:
        id: Unique identifier (UUID).
        phase_id: Reference to the parent phase.
        parent_task_id: Reference to a parent task (for sub-tasks WBS).
        name: Name of the task.
        wbs_code: Hierarchical code (e.g., '1.1', '1.1.1').
        description: Detailed task description.
        duration_days: Planned duration in working days.
        start_date_scheduled: Scheduled start date (computed by CPM).
        end_date_scheduled: Scheduled finish date (computed by CPM).
        early_start / early_finish: CPM Forward Pass dates.
        late_start / late_finish: CPM Backward Pass dates.
        total_float: Maximum delay without affecting project end date.
        free_float: Maximum delay without affecting successor start date.
        is_critical: Flagged if the task is on the critical path.
        is_milestone: Flagged if duration is zero.
        weight_percent: Weight for EVM aggregation within the phase.
        contingency_days: Additional days added from linked risks (V3).
        status: Current state (not_started, in_progress, completed, blocked, cancelled).
        priority: Priority level (1-5).
    """

    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    phase_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("phases.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_task_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    wbs_code: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    duration_days: Mapped[int] = mapped_column(Integer, server_default="1")
    
    # ── CPM & Scheduled Dates ──────────────────────────────────────
    start_date_scheduled: Mapped[date | None] = mapped_column(Date)
    end_date_scheduled: Mapped[date | None] = mapped_column(Date)
    early_start: Mapped[date | None] = mapped_column(Date)
    early_finish: Mapped[date | None] = mapped_column(Date)
    late_start: Mapped[date | None] = mapped_column(Date)
    late_finish: Mapped[date | None] = mapped_column(Date)
    total_float: Mapped[int] = mapped_column(Integer, server_default="0")
    free_float: Mapped[int] = mapped_column(Integer, server_default="0")
    is_critical: Mapped[bool] = mapped_column(Boolean, server_default="false")
    is_milestone: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # ── EVM & Progress ─────────────────────────────────────────────
    weight_percent: Mapped[float] = mapped_column(
        Numeric(5, 2),
        server_default="0.0",
    )
    contingency_days: Mapped[int] = mapped_column(Integer, server_default="0")
    status: Mapped[str] = mapped_column(
        String(30),
        server_default="not_started",
        index=True,
    )
    priority: Mapped[int] = mapped_column(Integer, server_default="3")

    # ── Relations ──────────────────────────────────────────────────
    phase: Mapped[Phase] = relationship(back_populates="tasks")
    parent_task: Mapped[Task | None] = relationship(
        "Task",
        remote_side=[id],
        back_populates="sub_tasks",
    )
    sub_tasks: Mapped[list[Task]] = relationship(
        "Task",
        back_populates="parent_task",
        cascade="all, delete-orphan",
    )
    dependencies: Mapped[list[TaskDependency]] = relationship(
        primaryjoin="Task.id == TaskDependency.task_id",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    assignments: Mapped[list[TaskAssignment]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    progress_logs: Mapped[list[ProgressLog]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )
    deliverables: Mapped[list[Deliverable]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("duration_days >= 0", name="chk_task_duration"),
        CheckConstraint("weight_percent BETWEEN 0 AND 100", name="chk_task_weight"),
        CheckConstraint("priority BETWEEN 1 AND 5", name="chk_task_priority"),
        CheckConstraint(
            "status IN ('not_started', 'in_progress', 'completed', 'blocked', 'cancelled')",
            name="chk_task_status",
        ),
        Index("idx_tasks_dates", "start_date_scheduled", "end_date_scheduled"),
        Index("idx_tasks_critical", "is_critical", postgresql_where="is_critical = true"),
    )
