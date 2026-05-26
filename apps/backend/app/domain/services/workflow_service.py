"""Domain service for deliverable workflow management.

Implements the state machine for deliverable lifecycle:
draft → submitted → in_review → approved/rejected.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.models.deliverable import Deliverable
from app.domain.models.deliverable_event import DeliverableEvent

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)

# ── Workflow state machine ────────────────────────────────────────────────────

_TRANSITIONS: dict[str, dict[str, str]] = {
    "draft": {"submit": "submitted"},
    "submitted": {"review": "in_review", "reject": "rejected"},
    "in_review": {"approve": "approved", "reject": "rejected"},
    "rejected": {"submit": "submitted"},
}


class WorkflowService:
    """Service managing deliverable lifecycle transitions."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize with an async database session.

        Args:
            db: AsyncSession for database operations.
        """
        self.db = db

    async def transition(
        self,
        deliverable_id: uuid.UUID,
        action: str,
        user_id: uuid.UUID,
        comment: Optional[str] = None,
    ) -> Deliverable:
        """Apply a workflow transition to a deliverable.

        Args:
            deliverable_id: UUID of the deliverable.
            action: Transition action (submit, review, approve, reject).
            user_id: UUID of the user performing the action.
            comment: Optional comment for the audit trail.

        Returns:
            Deliverable: The updated deliverable.

        Raises:
            NotFoundError: If deliverable does not exist.
            ValidationError: If the transition is invalid.
        """
        deliverable = await self.db.get(Deliverable, deliverable_id)
        if not deliverable:
            raise NotFoundError("Deliverable", str(deliverable_id))

        current_status = deliverable.status
        allowed = _TRANSITIONS.get(current_status, {})
        new_status = allowed.get(action)

        if new_status is None:
            raise ValidationError(
                f"Cannot '{action}' deliverable in status '{current_status}'. "
                f"Allowed actions: {list(allowed.keys())}"
            )

        # Apply transition
        deliverable.status = new_status
        self.db.add(deliverable)

        # Record audit event
        event = DeliverableEvent(
            deliverable_id=deliverable_id,
            action=action,
            from_status=current_status,
            to_status=new_status,
            performed_by=user_id,
            comment=comment,
        )
        self.db.add(event)

        await self.db.commit()
        await self.db.refresh(deliverable)

        logger.info(
            "deliverable_transition",
            deliverable_id=str(deliverable_id),
            action=action,
            from_status=current_status,
            to_status=new_status,
        )
        return deliverable

    async def get_history(
        self, deliverable_id: uuid.UUID
    ) -> List[DeliverableEvent]:
        """Retrieve the full transition history for a deliverable.

        Args:
            deliverable_id: UUID of the deliverable.

        Returns:
            List of DeliverableEvent records ordered chronologically.
        """
        result = await self.db.execute(
            select(DeliverableEvent)
            .where(DeliverableEvent.deliverable_id == deliverable_id)
            .order_by(DeliverableEvent.created_at.asc())
        )
        return list(result.scalars().all())
