"""Project model definition.

Projects are the primary unit of tracking in NEXUS, belonging to a Workspace.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Date, Numeric, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.workspace import Workspace
    from app.domain.models.user import User
    from app.domain.models.phase import Phase
    from app.domain.models.baseline import ProjectBaseline
    from app.domain.models.risk import Risk


class Project(Base, TimestampMixin):
    """A project within a workspace.

    Attributes:
        id: Unique identifier (UUID).
        workspace_id: Reference to the owning workspace.
        name: Name of the project.
        description: Detailed description.
        start_date: Planned project start date.
        end_date: Planned project end date.
        budget_total: Total authorized budget (BAC).
        status: Current state (draft, active, on_hold, completed, cancelled).
        active_baseline_id: Reference to the currently active baseline.
        pm_user_id: Reference to the assigned Project Manager.
    """

    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    budget_total: Mapped[float] = mapped_column(Numeric(15, 2), server_default="0.0")
    status: Mapped[str] = mapped_column(
        String(30),
        server_default="draft",
        index=True,
    )
    active_baseline_id: Mapped[uuid.UUID | None] = mapped_column(index=True)
    pm_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))

    # ── Relations ──────────────────────────────────────────────────
    workspace: Mapped[Workspace] = relationship(back_populates="projects")
    phases: Mapped[list[Phase]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="Phase.order_index",
    )
    baselines: Mapped[list[ProjectBaseline]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    risks: Mapped[list[Risk]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'active', 'on_hold', 'completed', 'cancelled')",
            name="chk_project_status",
        ),
    )
