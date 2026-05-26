"""Deliverable service implementation.

Handles deliverable lifecycle and workflow transitions.
"""

from __future__ import annotations

import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.deliverable import Deliverable
from app.domain.models.deliverable_event import DeliverableEvent
from app.core.exceptions import NotFoundError, ForbiddenError


class DeliverableService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_deliverable(self, task_id: uuid.UUID, name: str, due_date: Optional[date] = None) -> Deliverable:
        deliverable = Deliverable(
            task_id=task_id,
            name=name,
            due_date=due_date,
            status="draft"
        )
        self.db.add(deliverable)
        await self.db.commit()
        await self.db.refresh(deliverable)
        return deliverable

    async def get_project_deliverables(self, project_id: uuid.UUID) -> List[Deliverable]:
        # Implementation depends on joining Task and Phase to get to Project
        # Simplified for now
        return []

    async def transition_status(self, deliverable_id: uuid.UUID, new_status: str, user_id: uuid.UUID, comment: str = "") -> Deliverable:
        deliverable = await self.db.get(Deliverable, deliverable_id)
        if not deliverable:
            raise NotFoundError("Deliverable", deliverable_id)
        
        old_status = deliverable.status
        # TODO: Implement state machine validation logic
        
        deliverable.status = new_status
        
        # Log event
        event = DeliverableEvent(
            deliverable_id=deliverable_id,
            from_status=old_status,
            to_status=new_status,
            user_id=user_id,
            comment=comment
        )
        self.db.add(event)
        
        await self.db.commit()
        await self.db.refresh(deliverable)
        return deliverable
