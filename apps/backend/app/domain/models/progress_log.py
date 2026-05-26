"""ProgressLog model definition.

Records physical progress and actual costs for a task at a specific point in time.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Date, Numeric, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.task import Task
    from app.domain.models.user import User


class ProgressLog(Base, TimestampMixin):
    """A progress entry for a task.

    Attributes:
        id: Unique identifier (UUID).
        task_id: Reference to the task.
        log_date: The date this progress was recorded.
        physical_percent: Physical completion percentage (0-100).
        actual_hours: Hours consumed for this entry.
        actual_cost_dh: Financial cost incurred for this entry.
        logged_by: User ID who recorded the progress.
        notes: Optional comments.
    """

    __tablename__ = "progress_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    log_date: Mapped[date] = mapped_column(Date, nullable=False)
    physical_percent: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)
    actual_hours: Mapped[float] = mapped_column(Numeric(10, 2), server_default="0.0")
    actual_cost_dh: Mapped[float] = mapped_column(Numeric(15, 2), server_default="0.0")
    logged_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[str | None] = mapped_column(Text)

    # ── Relations ──────────────────────────────────────────────────
    task: Mapped[Task] = relationship(back_populates="progress_logs")

    __table_args__ = (
        UniqueConstraint("task_id", "log_date", name="uq_progress_task_date"),
        CheckConstraint("physical_percent BETWEEN 0 AND 100", name="chk_progress_percent"),
        CheckConstraint("actual_hours >= 0", name="chk_progress_hours"),
        CheckConstraint("actual_cost_dh >= 0", name="chk_progress_cost"),
    )
