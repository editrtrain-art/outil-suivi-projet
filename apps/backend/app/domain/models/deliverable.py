"""Deliverable model definition.

Tracks project deliverables, their status, and validation workflow.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Date, Text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.task import Task
    from app.domain.models.user import User
    from app.domain.models.deliverable_event import DeliverableEvent


class Deliverable(Base, TimestampMixin):
    """A project deliverable linked to a task.

    Attributes:
        id: Unique identifier (UUID).
        task_id: Reference to the parent task.
        name: Name of the deliverable.
        description: Detailed description.
        due_date: Targeted delivery date.
        status: Current workflow state (draft, submitted, in_review, approved, rejected).
        assigned_to: User responsible for the deliverable.
        file_url: Link to the uploaded file (Vercel Blob / S3).
    """

    __tablename__ = "deliverables"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    due_date: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(
        String(30),
        server_default="draft",
        index=True,
    )
    assigned_to: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    file_url: Mapped[str | None] = mapped_column(Text)

    # ── Relations ──────────────────────────────────────────────────
    task: Mapped[Task] = relationship(back_populates="deliverables")
    events: Mapped[list[DeliverableEvent]] = relationship(
        back_populates="deliverable",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'submitted', 'in_review', 'approved', 'rejected')",
            name="chk_deliverable_status",
        ),
    )
