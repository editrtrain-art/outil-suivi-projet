"""ProjectBaseline model definition.

Stores planning snapshots for multi-baseline management and comparison.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.project import Project
    from app.domain.models.user import User


class ProjectBaseline(Base, TimestampMixin):
    """A frozen snapshot of a project's planning state.

    Attributes:
        id: Unique identifier (UUID).
        project_id: Reference to the parent project.
        version_code: User-defined version (e.g., 'B0', 'B1').
        description: Optional notes about this baseline.
        snapshot: Full serialized planning state (JSONB).
        locked_by: User ID who created the baseline.
        is_active: Flag for the current reference baseline.
    """

    __tablename__ = "project_baselines"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    version_code: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    snapshot: Mapped[dict] = mapped_column(JSON, nullable=False)
    locked_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="false", index=True)

    # ── Relations ──────────────────────────────────────────────────
    project: Mapped[Project] = relationship(back_populates="baselines")
