"""API Router for Deliverables.

Endpoints for CRUD operations on project deliverables and workflow transitions.
"""

from __future__ import annotations

import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_contributor, require_pm, require_viewer
from app.domain.services.deliverable_service import DeliverableService

router = APIRouter(prefix="/deliverables", tags=["deliverables"])


class DeliverableCreate(BaseModel):
    """Schema for creating a deliverable."""

    task_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: str | None = None
    due_date: str | None = None


class DeliverableResponse(BaseModel):
    """Schema for returning a deliverable."""

    id: uuid.UUID
    task_id: uuid.UUID
    name: str
    description: str | None = None
    status: str
    due_date: str | None = None

    model_config = ConfigDict(from_attributes=True)


class TransitionRequest(BaseModel):
    """Schema for requesting a deliverable workflow transition."""

    action: str = Field(..., description="submit | review | approve | reject")
    comment: str | None = None


@router.post("/", response_model=DeliverableResponse, status_code=status.HTTP_201_CREATED)
async def create_deliverable(
    data: DeliverableCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_pm),
) -> DeliverableResponse:
    """Create a new deliverable linked to a task."""
    service = DeliverableService(db)
    return await service.create_deliverable(
        task_id=data.task_id,
        name=data.name,
        description=data.description,
    )


@router.get("/task/{task_id}", response_model=List[DeliverableResponse])
async def list_task_deliverables(
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict[str, Any] = Depends(require_viewer),
) -> List[DeliverableResponse]:
    """List all deliverables for a given task."""
    service = DeliverableService(db)
    return await service.get_task_deliverables(task_id)


@router.post("/{deliverable_id}/transition", response_model=DeliverableResponse)
async def transition_deliverable(
    deliverable_id: uuid.UUID,
    data: TransitionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_contributor),
) -> DeliverableResponse:
    """Apply a workflow transition to a deliverable.

    Actions: submit (contributor), review (pm), approve (pm), reject (pm).
    """
    service = DeliverableService(db)
    user_id = uuid.UUID(current_user["sub"])
    return await service.transition_deliverable(
        deliverable_id=deliverable_id,
        action=data.action,
        user_id=user_id,
        comment=data.comment,
    )
