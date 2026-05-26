"""API Router for Project Baselines.

Endpoints for managing project schedule snapshots and comparing variances.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional, Any, Dict

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_pm, require_viewer
from app.domain.services.baseline_service import BaselineService

router = APIRouter(prefix="/baselines", tags=["baselines"])


class BaselineCreate(BaseModel):
    project_id: uuid.UUID
    version_code: str
    description: Optional[str] = None
    is_active: bool = False


class BaselineResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    version_code: str
    description: Optional[str] = None
    snapshot: Dict[str, Any]
    locked_by: Optional[uuid.UUID] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VarianceItem(BaseModel):
    task_id: str
    wbs_code: str
    name: str
    is_new: bool
    start_variance_days: int
    finish_variance_days: int
    duration_variance_days: int
    slip_status: str


class BaselineCompareResponse(BaseModel):
    baseline_id: str
    version_code: str
    created_at: str
    variances: List[VarianceItem]


@router.post("", response_model=BaselineResponse, status_code=status.HTTP_201_CREATED)
async def create_baseline(
    data: BaselineCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_pm),
) -> BaselineResponse:
    """Create a new project baseline snapshot."""
    service = BaselineService(db)
    user_id = uuid.UUID(current_user["sub"])
    baseline = await service.create_baseline(
        project_id=data.project_id,
        version_code=data.version_code,
        description=data.description,
        is_active=data.is_active,
        creator_id=user_id,
    )
    return BaselineResponse.model_validate(baseline)


@router.get("/project/{project_id}", response_model=List[BaselineResponse])
async def list_project_baselines(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_viewer),
) -> List[BaselineResponse]:
    """List all baselines for a given project."""
    service = BaselineService(db)
    baselines = await service.get_project_baselines(project_id)
    return [BaselineResponse.model_validate(b) for b in baselines]


@router.get("/{baseline_id}/compare", response_model=BaselineCompareResponse)
async def compare_baseline(
    baseline_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_viewer),
) -> BaselineCompareResponse:
    """Compare a baseline snapshot with the current active project schedule."""
    service = BaselineService(db)
    comparison = await service.compare_baseline(baseline_id)
    return BaselineCompareResponse.model_validate(comparison)
