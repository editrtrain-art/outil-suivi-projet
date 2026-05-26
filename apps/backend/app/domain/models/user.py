"""User model definition.

Users are synchronized from Clerk and can belong to multiple workspaces.
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.domain.models.workspace_member import WorkspaceMember


class User(Base, TimestampMixin):
    """A user of the NEXUS platform.

    Attributes:
        id: Unique identifier (mapped from Clerk user_id).
        email: Primary email address.
        first_name: Given name.
        last_name: Family name.
        avatar_url: Link to the user's profile picture.
        role_global: Global system role (user, admin).
    """

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    first_name: Mapped[str | None] = mapped_column(String(100))
    last_name: Mapped[str | None] = mapped_column(String(100))
    avatar_url: Mapped[str | None] = mapped_column(Text)
    role_global: Mapped[str] = mapped_column(String(20), server_default="user")

    # ── Relations ──────────────────────────────────────────────────
    workspace_memberships: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
