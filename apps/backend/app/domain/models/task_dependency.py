"""TaskDependency model definition.

Defines the relationships between tasks (FS, SS, FF, SF) and their lag/lead.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.task import Task


class TaskDependency(Base, TimestampMixin):
    """A dependency link between two tasks.

    Attributes:
        id: Unique identifier (UUID).
        task_id: The successor task.
        predecessor_task_id: The predecessor task.
        dependency_type: Link type (FS, SS, FF, SF).
        lag_days: Delay (positive) or lead (negative) in days.
    """

    __tablename__ = "task_dependencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    predecessor_task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    dependency_type: Mapped[str] = mapped_column(
        String(2),
        server_default="FS",
        nullable=False,
    )
    lag_days: Mapped[int] = mapped_column(Integer, server_default="0")

    # ── Relations ──────────────────────────────────────────────────
    task: Mapped[Task] = relationship(
        foreign_keys=[task_id],
        back_populates="dependencies",
    )
    predecessor: Mapped[Task] = relationship(
        foreign_keys=[predecessor_task_id],
    )

    __table_args__ = (
        UniqueConstraint("task_id", "predecessor_task_id", name="uq_task_dependency"),
        CheckConstraint("task_id <> predecessor_task_id", name="chk_no_self_dependency"),
        CheckConstraint(
            "dependency_type IN ('FS', 'SS', 'FF', 'SF')",
            name="chk_dependency_type",
        ),
    )
