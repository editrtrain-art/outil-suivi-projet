"""WorkspaceMember association model.

Defines the relationship between Users and Workspaces, including roles.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.workspace import Workspace
    from app.domain.models.user import User


class WorkspaceMember(Base):
    """Association between a User and a Workspace with a specific role.

    Attributes:
        workspace_id: ID of the workspace.
        user_id: ID of the user.
        role: Workspace-specific role (admin, pm, contributor, viewer).
        joined_at: When the user joined the workspace.
    """

    __tablename__ = "workspace_members"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ── Relations ──────────────────────────────────────────────────
    workspace: Mapped[Workspace] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="workspace_memberships")
