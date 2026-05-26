"""API Router for Resources.

Endpoints for managing workspace resources.
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_resource_service
from app.core.permissions import require_pm, require_viewer
from app.domain.services.resource_service import ResourceService

router = APIRouter(prefix="/resources", tags=["resources"])

class ResourceCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str
    role: str
    hourly_rate_dh: float

class ResourceResponse(BaseModel):
    id: uuid.UUID
    name: str
    role: str
    hourly_rate_dh: float

    model_config = ConfigDict(from_attributes=True)

@router.post("", response_model=ResourceResponse, status_code=status.HTTP_201_CREATED)
async def create_resource(
    data: ResourceCreate,
    service: ResourceService = Depends(get_resource_service),
    current_user: dict = Depends(require_pm)
):
    return await service.create_resource(
        workspace_id=data.workspace_id,
        name=data.name,
        role=data.role,
        hourly_rate=data.hourly_rate_dh
    )

@router.get("/workspace/{workspace_id}", response_model=List[ResourceResponse])
async def list_resources(
    workspace_id: uuid.UUID,
    service: ResourceService = Depends(get_resource_service),
    current_user: dict = Depends(require_viewer)
):
    return await service.get_workspace_resources(workspace_id)
