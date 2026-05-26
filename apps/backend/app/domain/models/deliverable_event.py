"""DeliverableEvent model definition.

Audit trail for deliverable workflow state transitions.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.deliverable import Deliverable
    from app.domain.models.user import User


class DeliverableEvent(Base):
    """An event recording a state transition in a deliverable's workflow.

    Attributes:
        id: Unique identifier (UUID).
        deliverable_id: Reference to the deliverable.
        from_status: The state before the transition.
        to_status: The state after the transition.
        user_id: The user who performed the transition.
        comment: Optional justification or feedback.
        created_at: When the event occurred.
    """

    __tablename__ = "deliverable_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    deliverable_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deliverables.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[str | None] = mapped_column(String(30))
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    comment: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    # ── Relations ──────────────────────────────────────────────────
    deliverable: Mapped[Deliverable] = relationship(back_populates="events")
