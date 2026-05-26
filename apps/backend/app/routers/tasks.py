"""API Router for Tasks.

Full CRUD for tasks with CPM auto-trigger on create/update,
dependency management, and WBS code auto-generation.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List, Literal

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user, get_task_service
from app.core.permissions import require_pm, require_viewer
from app.domain.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"])


class TaskCreate(BaseModel):
    phase_id: uuid.UUID
    name: str = Field(..., max_length=255)
    description: str | None = Field(None, max_length=1000)
    duration_days: int = Field(default=1, ge=0)
    parent_task_id: uuid.UUID | None = None
    weight_percent: float = Field(default=0.0, ge=0, le=100)
    priority: int = Field(default=3, ge=1, le=5)
    is_milestone: bool = False


class TaskUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    duration_days: int | None = Field(None, ge=0)
    status: Literal["not_started", "in_progress", "completed", "blocked", "cancelled"] | None = None
    weight_percent: float | None = Field(None, ge=0, le=100)
    priority: int | None = Field(None, ge=1, le=5)
    start_date_scheduled: date | None = None
    end_date_scheduled: date | None = None


class DependencyCreate(BaseModel):
    predecessor_id: uuid.UUID
    dep_type: Literal["FS", "SS", "FF", "SF"] = "FS"
    lag_days: int = Field(default=0, ge=0)


class TaskResponse(BaseModel):
    id: uuid.UUID
    phase_id: uuid.UUID
    parent_task_id: uuid.UUID | None = None
    name: str
    wbs_code: str
    description: str | None = None
    duration_days: int
    status: str
    priority: int
    weight_percent: float
    is_milestone: bool
    is_critical: bool
    total_float: int
    free_float: int
    start_date_scheduled: date | None = None
    end_date_scheduled: date | None = None
    early_start: date | None = None
    early_finish: date | None = None
    late_start: date | None = None
    late_finish: date | None = None

    model_config = ConfigDict(from_attributes=True)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_pm),
) -> TaskResponse:
    """Create a task and auto-trigger CPM recalculation for the project."""
    return await service.create_task(
        phase_id=data.phase_id,
        name=data.name,
        duration_days=data.duration_days,
        parent_task_id=data.parent_task_id,
        description=data.description,
        weight_percent=data.weight_percent,
        priority=data.priority,
        is_milestone=data.is_milestone,
    )


@router.get("/phase/{phase_id}", response_model=List[TaskResponse])
async def list_phase_tasks(
    phase_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_viewer),
) -> List[TaskResponse]:
    """List all tasks for a given phase."""
    return await service.get_phase_tasks(phase_id)


@router.get("/project/{project_id}", response_model=List[TaskResponse])
async def list_project_tasks(
    project_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_viewer),
) -> List[TaskResponse]:
    """List all tasks across all phases of a project."""
    return await service.get_project_tasks(project_id)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_viewer),
) -> TaskResponse:
    """Retrieve a single task by ID."""
    return await service.get_task_by_id(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID,
    data: TaskUpdate,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_pm),
) -> TaskResponse:
    """Update task fields and optionally re-trigger CPM."""
    updates = data.model_dump(exclude_none=True)
    return await service.update_task(task_id, **updates)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_pm),
) -> Response:
    """Delete a task and cascade to sub-tasks/dependencies."""
    await service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{task_id}/dependencies", status_code=status.HTTP_201_CREATED)
async def add_dependency(
    task_id: uuid.UUID,
    data: DependencyCreate,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_pm),
) -> dict:
    """Add a dependency link between two tasks and re-run CPM."""
    dep = await service.add_dependency(
        task_id=task_id,
        predecessor_id=data.predecessor_id,
        dep_type=data.dep_type,
        lag_days=data.lag_days,
    )
    return {"task_id": str(dep.task_id), "predecessor_id": str(dep.predecessor_task_id), "dep_type": dep.dependency_type}


@router.post("/project/{project_id}/run-cpm", status_code=status.HTTP_200_OK)
async def trigger_cpm(
    project_id: uuid.UUID,
    service: TaskService = Depends(get_task_service),
    _: dict = Depends(require_pm),
) -> dict:
    """Manually trigger CPM recalculation for all tasks in a project."""
    await service.run_cpm_for_project(project_id)
    return {"status": "CPM recalculation complete", "project_id": str(project_id)}

