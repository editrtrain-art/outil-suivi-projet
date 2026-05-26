"""Resource model definition.

Resources represent people or roles assigned to tasks within a workspace.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Numeric, Integer, Boolean, JSON, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.workspace import Workspace
    from app.domain.models.user import User
    from app.domain.models.task_assignment import TaskAssignment
    from app.domain.models.resource_calendar import ResourceCalendar


class Resource(Base, TimestampMixin):
    """A human or generic resource within a workspace.

    Attributes:
        id: Unique identifier (UUID).
        workspace_id: Reference to the owning workspace.
        user_id: Optional reference to a system User (Clerk ID).
        name: Resource name or role title.
        role: Professional role (e.g., 'Senior Developer', 'Architect').
        hourly_rate_dh: Unit cost in DH per hour.
        monthly_capacity_hours: Standard available hours per month.
        skills: List of skill tags.
        is_active: Flag for active/archived status.
        entry_date: When the resource started in the workspace.
        exit_date: When the resource left the workspace.
    """

    __tablename__ = "resources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    role: Mapped[str | None] = mapped_column(String(100))
    hourly_rate_dh: Mapped[float] = mapped_column(Numeric(10, 2), server_default="0.0")
    monthly_capacity_hours: Mapped[int] = mapped_column(Integer, server_default="168")
    skills: Mapped[list | None] = mapped_column(JSON, server_default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true")
    entry_date: Mapped[date | None] = mapped_column(Date)
    exit_date: Mapped[date | None] = mapped_column(Date)

    # ── Relations ──────────────────────────────────────────────────
    workspace: Mapped[Workspace] = relationship(back_populates="resources")
    assignments: Mapped[list[TaskAssignment]] = relationship(
        back_populates="resource",
        cascade="all, delete-orphan",
    )
    calendars: Mapped[list[ResourceCalendar]] = relationship(
        back_populates="resource",
        cascade="all, delete-orphan",
    )
