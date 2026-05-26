"""Workspace model definition.

Workspaces provide top-level multi-tenant isolation for projects and resources.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.project import Project
    from app.domain.models.workspace_member import WorkspaceMember
    from app.domain.models.resource import Resource


class Workspace(Base, TimestampMixin):
    """A workspace container for projects and resources.

    Attributes:
        id: Unique identifier (UUID).
        name: Display name of the workspace.
        slug: URL-friendly unique identifier.
        created_by: UUID of the user who created the workspace.
        plan_type: Subscription tier (free, pro, enterprise).
        settings: JSON configuration for workspace-specific rules.
    """

    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    created_by: Mapped[uuid.UUID] = mapped_column(nullable=False)
    plan_type: Mapped[str] = mapped_column(String(20), server_default="free")
    settings: Mapped[dict] = mapped_column(JSON, server_default="{}")

    # ── Relations ──────────────────────────────────────────────────
    members: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    projects: Mapped[list[Project]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    resources: Mapped[list[Resource]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
