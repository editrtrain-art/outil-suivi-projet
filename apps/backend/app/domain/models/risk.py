"""Risk and RiskTaskLink model definitions.

Tracks project risks, their scoring, and linkage to schedule tasks.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, Text, Integer, Numeric, CheckConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.project import Project
    from app.domain.models.user import User
    from app.domain.models.task import Task


class RiskTaskLink(Base):
    """Many-to-Many association between Risks and Tasks."""

    __tablename__ = "risk_task_links"

    risk_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("risks.id", ondelete="CASCADE"),
        primary_key=True,
    )
    task_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Risk(Base, TimestampMixin):
    """A project risk entry.

    Attributes:
        id: Unique identifier (UUID).
        project_id: Reference to the parent project.
        title: Short title of the risk.
        description: Detailed risk event description.
        category: Classification (technical, schedule, budget, etc.).
        probability: Score 1-5.
        impact: Score 1-5.
        risk_score: Computed as probability * impact.
        mitigation: Mitigation plan.
        owner_id: Assigned risk owner.
        status: Current state (active, mitigated, closed).
        contingency_threshold: Score above which contingency is applied.
        contingency_factor: Percentage increase in duration for linked tasks.
    """

    __tablename__ = "risks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    probability: Mapped[int] = mapped_column(Integer, nullable=False)
    impact: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # risk_score is computed in DB or at service layer. 
    # Here we store it for easier indexing.
    risk_score: Mapped[int] = mapped_column(Integer, index=True)
    
    mitigation: Mapped[str | None] = mapped_column(Text)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(
        String(20),
        server_default="active",
        index=True,
    )
    contingency_threshold: Mapped[int] = mapped_column(Integer, server_default="15")
    contingency_factor: Mapped[float] = mapped_column(Numeric(5, 2), server_default="0.15")

    # ── Relations ──────────────────────────────────────────────────
    project: Mapped[Project] = relationship(back_populates="risks")
    linked_tasks: Mapped[list[Task]] = relationship(
        secondary="risk_task_links",
        backref="linked_risks",
    )

    __table_args__ = (
        CheckConstraint("probability BETWEEN 1 AND 5", name="chk_risk_probability"),
        CheckConstraint("impact BETWEEN 1 AND 5", name="chk_risk_impact"),
        CheckConstraint("status IN ('active', 'mitigated', 'closed')", name="chk_risk_status"),
        Index("idx_risks_critical", "risk_score", postgresql_where="status = 'active'"),
    )
