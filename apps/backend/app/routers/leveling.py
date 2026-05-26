"""API Router for Resource Leveling and Smoothing.

Endpoints to check resource capacity loads and run heuristics.
"""

from __future__ import annotations

import uuid
from typing import List, Dict

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_pm, require_viewer
from app.domain.services.resource_leveler import ResourceLevelerService

router = APIRouter(prefix="/leveling", tags=["leveling"])


class ResourceLoadDetails(BaseModel):
    name: str
    role: str
    capacity: float
    daily_allocations: List[float]


class DailyLoadResponse(BaseModel):
    timeline: List[str]
    resources: Dict[str, ResourceLoadDetails]


class LevelingActionResponse(BaseModel):
    status: str
    message: str


@router.get("/project/{project_id}/load", response_model=DailyLoadResponse)
async def get_daily_load(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_viewer),
) -> DailyLoadResponse:
    """Get the daily resource allocation profile and timeline bounds for a project."""
    service = ResourceLevelerService(db)
    load = await service.get_daily_load(project_id)
    return DailyLoadResponse.model_validate(load)


@router.post("/project/{project_id}/level", response_model=LevelingActionResponse)
async def run_resource_leveling(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_pm),
) -> LevelingActionResponse:
    """Run the serial-associative resource leveling engine on a project.

    This heuristic shifts task dates past floats when resources are overloaded,
    potentially delaying the project end date. Succeeding dates cascade dynamically.
    """
    service = ResourceLevelerService(db)
    await service.level_resources(project_id)
    return LevelingActionResponse(
        status="success",
        message="Resource leveling executed successfully and project schedule updated.",
    )


@router.post("/project/{project_id}/smooth", response_model=LevelingActionResponse)
async def run_resource_smoothing(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_pm),
) -> LevelingActionResponse:
    """Run the resource smoothing heuristic on a project.

    This shifts tasks strictly within their float windows to minimize resource
    demand fluctuations without extending the project end date.
    """
    service = ResourceLevelerService(db)
    await service.smooth_resources(project_id)
    return LevelingActionResponse(
        status="success",
        message="Resource smoothing executed successfully within float limits.",
    )
