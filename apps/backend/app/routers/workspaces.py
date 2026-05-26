"""API Router for Workspaces.

Endpoints for workspace management and membership.
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel, ConfigDict
from app.core.dependencies import get_current_user, get_workspace_service
from app.core.permissions import require_admin, require_pm

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

class WorkspaceCreate(BaseModel):
    name: str
    slug: str

class WorkspaceResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    plan_type: str

    model_config = ConfigDict(from_attributes=True)

@router.post("", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    data: WorkspaceCreate,
    service: WorkspaceService = Depends(get_workspace_service),
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user["sub"])
    return await service.create_workspace(name=data.name, slug=data.slug, creator_id=user_id)

@router.get("", response_model=List[WorkspaceResponse])
async def list_user_workspaces(
    service: WorkspaceService = Depends(get_workspace_service),
    current_user: dict = Depends(get_current_user)
):
    user_id = uuid.UUID(current_user["sub"])
    return await service.get_user_workspaces(user_id=user_id)

@router.get("/{workspace_id}", response_model=WorkspaceResponse)
async def get_workspace(
    workspace_id: uuid.UUID,
    service: WorkspaceService = Depends(get_workspace_service),
    current_user: dict = Depends(get_current_user)
):
    return await service.get_workspace_by_id(workspace_id)
