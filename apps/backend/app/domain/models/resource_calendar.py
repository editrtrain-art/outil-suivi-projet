"""ResourceCalendar model definition.

Tracks unavailability events (holidays, leave) for resources.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Date, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import Base

if TYPE_CHECKING:
    from app.domain.models.resource import Resource


class ResourceCalendar(Base):
    """A calendar event for a resource (holiday, leave, overtime).

    Attributes:
        id: Unique identifier (UUID).
        resource_id: Reference to the resource.
        date: The date of the event.
        event_type: Type of event (holiday, leave, overtime).
        description: Optional notes.
    """

    __tablename__ = "resource_calendars"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    resource_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255))

    # ── Relations ──────────────────────────────────────────────────
    resource: Mapped[Resource] = relationship(back_populates="calendars")

    __table_args__ = (
        UniqueConstraint("resource_id", "date", name="uq_resource_calendar_date"),
        CheckConstraint(
            "event_type IN ('holiday', 'leave', 'overtime')",
            name="chk_calendar_event_type",
        ),
    )
