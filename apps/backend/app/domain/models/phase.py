"""Phase model definition.

Phases represent high-level stages of a project (WBS Level 1).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Date, Numeric, Integer, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.project import Project
    from app.domain.models.task import Task


class Phase(Base):
    """A high-level stage or phase of a project.

    Attributes:
        id: Unique identifier (UUID).
        project_id: Reference to the parent project.
        name: Name of the phase.
        wbs_code: Hierarchical code (e.g., '1.0', '2.0').
        order_index: Sorting order within the project.
        weight_percent: Relative importance for EVM aggregation.
        planned_start: Aggregated or planned start date for the phase.
        planned_finish: Aggregated or planned finish date for the phase.
    """

    __tablename__ = "phases"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    wbs_code: Mapped[str] = mapped_column(String(50), nullable=False)
    order_index: Mapped[int] = mapped_column(Integer, server_default="0")
    weight_percent: Mapped[float] = mapped_column(
        Numeric(5, 2),
        server_default="0.0",
    )
    planned_start: Mapped[date | None] = mapped_column(Date)
    planned_finish: Mapped[date | None] = mapped_column(Date)

    # ── Relations ──────────────────────────────────────────────────
    project: Mapped[Project] = relationship(back_populates="phases")
    tasks: Mapped[list[Task]] = relationship(
        back_populates="phase",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("project_id", "wbs_code", name="uq_phase_project_wbs"),
        CheckConstraint("weight_percent BETWEEN 0 AND 100", name="chk_phase_weight"),
    )
