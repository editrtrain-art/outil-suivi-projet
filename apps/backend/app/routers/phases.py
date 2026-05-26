"""API Router for Phases.

Handles creation and listing of project phases (WBS Level 1).
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field, ConfigDict
from app.core.dependencies import get_current_user, get_phase_service
from app.core.permissions import require_pm, require_viewer

router = APIRouter(prefix="/phases", tags=["phases"])


class PhaseCreate(BaseModel):
    project_id: uuid.UUID
    name: str = Field(..., max_length=200)
    weight_percent: float = Field(default=0.0, ge=0, le=100)


class PhaseUpdate(BaseModel):
    name: str | None = Field(None, max_length=200)
    weight_percent: float | None = Field(None, ge=0, le=100)
    planned_start: date | None = None
    planned_finish: date | None = None


class PhaseResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    name: str
    wbs_code: str
    order_index: int
    weight_percent: float
    planned_start: date | None = None
    planned_finish: date | None = None

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=PhaseResponse, status_code=status.HTTP_201_CREATED)
async def create_phase(
    data: PhaseCreate,
    service: PhaseService = Depends(get_phase_service),
    _: dict = Depends(require_pm),
) -> PhaseResponse:
    """Create a new phase under a project (WBS Level 1)."""
    return await service.create_phase(
        project_id=data.project_id,
        name=data.name,
        weight_percent=data.weight_percent,
    )


@router.get("/project/{project_id}", response_model=List[PhaseResponse])
async def list_project_phases(
    project_id: uuid.UUID,
    service: PhaseService = Depends(get_phase_service),
    _: dict = Depends(require_viewer),
) -> List[PhaseResponse]:
    """Retrieve all phases for a given project, ordered by index."""
    return await service.get_project_phases(project_id)


@router.patch("/{phase_id}", response_model=PhaseResponse)
async def update_phase(
    phase_id: uuid.UUID,
    data: PhaseUpdate,
    service: PhaseService = Depends(get_phase_service),
    _: dict = Depends(require_pm),
) -> PhaseResponse:
    """Partially update a phase."""
    updates = data.model_dump(exclude_none=True)
    return await service.update_phase(phase_id, **updates)


@router.delete("/{phase_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_phase(
    phase_id: uuid.UUID,
    service: PhaseService = Depends(get_phase_service),
    _: dict = Depends(require_pm),
) -> Response:
    """Delete a phase and all its tasks (cascading)."""
    await service.delete_phase(phase_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
