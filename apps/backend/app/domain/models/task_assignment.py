"""TaskAssignment model definition.

Association between Tasks and Resources with allocation percentage.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.task import Task
    from app.domain.models.resource import Resource


class TaskAssignment(Base):
    """Assignment of a resource to a specific task.

    Attributes:
        id: Unique identifier (UUID).
        task_id: Reference to the task.
        resource_id: Reference to the resource.
        allocation_percent: Percentage of resource time dedicated to this task.
        planned_hours: Total hours allocated (computed from duration * allocation).
    """

    __tablename__ = "task_assignments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
    )
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
    )
    allocation_percent: Mapped[float] = mapped_column(
        Numeric(5, 2),
        server_default="100.0",
    )
    planned_hours: Mapped[float | None] = mapped_column(Numeric(10, 2))

    # ── Relations ──────────────────────────────────────────────────
    task: Mapped[Task] = relationship(back_populates="assignments")
    resource: Mapped[Resource] = relationship(back_populates="assignments")

    __table_args__ = (
        UniqueConstraint("task_id", "resource_id", name="uq_task_assignment"),
        CheckConstraint("allocation_percent BETWEEN 0 AND 100", name="chk_assignment_allocation"),
    )
