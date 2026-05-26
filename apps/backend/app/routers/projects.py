"""API Router for Projects.

CRUD operations and high-level project management.
"""

from __future__ import annotations

import uuid
from typing import List
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from datetime import date
from app.core.dependencies import get_current_user, get_project_service
from app.core.permissions import require_pm, require_viewer

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    workspace_id: uuid.UUID
    name: str
    description: str | None = None
    start_date: date
    end_date: date
    budget_total: float = 0.0

class ProjectResponse(BaseModel):
    id: uuid.UUID
    name: str
    status: str
    start_date: date
    end_date: date

    model_config = ConfigDict(from_attributes=True)
@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(require_pm)
):
    return await service.create_project(
        workspace_id=data.workspace_id,
        name=data.name,
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        budget_total=data.budget_total
    )

@router.get("/workspace/{workspace_id}", response_model=List[ProjectResponse])
async def list_workspace_projects(
    workspace_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(require_viewer)
):
    return await service.get_workspace_projects(workspace_id)

@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: uuid.UUID,
    service: ProjectService = Depends(get_project_service),
    current_user: dict = Depends(require_viewer)
):
    return await service.get_project_by_id(project_id)
