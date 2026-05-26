"""API Router for Risk Register.

Endpoints for CRUD operations on project risks,
risk-task linking, and contingency management.
"""

from __future__ import annotations

import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import require_pm, require_viewer
from app.domain.schemas.risk_schema import RiskCreate, RiskUpdate, RiskResponse
from app.domain.services.risk_service import RiskService

router = APIRouter(prefix="/risks", tags=["risks"])


@router.post("", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    data: RiskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_pm),
) -> Any:
    """Create a new risk entry for a project.

    Args:
        data: Risk details.
        db: Scoped async database session.
        current_user: The authenticated user claims.

    Returns:
        RiskResponse: The created risk representation.
    """
    service = RiskService(db)
    return await service.create_risk(
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        category=data.category,
        probability=data.probability,
        impact=data.impact,
        mitigation=data.mitigation,
        owner_id=data.owner_id,
        contingency_threshold=data.contingency_threshold,
        contingency_factor=data.contingency_factor,
    )


@router.get("/project/{project_id}", response_model=List[RiskResponse])
async def list_project_risks(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict[str, Any] = Depends(require_viewer),
) -> Any:
    """List all risks for a given project.

    Args:
        project_id: The target project identifier.
        db: Scoped async database session.

    Returns:
        List[RiskResponse]: List of project risks.
    """
    service = RiskService(db)
    return await service.get_project_risks(project_id)


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(
    risk_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict[str, Any] = Depends(require_viewer),
) -> Any:
    """Retrieve a single risk by ID.

    Args:
        risk_id: The target risk identifier.
        db: Scoped async database session.

    Returns:
        RiskResponse: The matching risk.
    """
    service = RiskService(db)
    return await service.get_risk_by_id(risk_id)


@router.patch("/{risk_id}", response_model=RiskResponse)
async def update_risk(
    risk_id: uuid.UUID,
    data: RiskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_pm),
) -> Any:
    """Update risk fields.

    Args:
        risk_id: The risk identifier.
        data: Updated fields.
        db: Scoped async database session.
        current_user: The authenticated user claims.

    Returns:
        RiskResponse: The updated risk representation.
    """
    service = RiskService(db)
    updates = data.model_dump(exclude_none=True)
    return await service.update_risk(risk_id, **updates)


@router.post("/{risk_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def link_task(
    risk_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_pm),
) -> dict[str, str]:
    """Link a task to a risk.

    Args:
        risk_id: Risk identifier.
        task_id: Task identifier.
        db: Scoped async database session.
        current_user: The authenticated user claims.

    Returns:
        dict: Success message.
    """
    service = RiskService(db)
    await service.link_task(risk_id, task_id)
    return {"message": "Task linked to risk successfully"}


@router.delete("/{risk_id}/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def unlink_task(
    risk_id: uuid.UUID,
    task_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(require_pm),
) -> dict[str, str]:
    """Unlink a task from a risk.

    Args:
        risk_id: Risk identifier.
        task_id: Task identifier.
        db: Scoped async database session.
        current_user: The authenticated user claims.

    Returns:
        dict: Success message.
    """
    service = RiskService(db)
    await service.unlink_task(risk_id, task_id)
    return {"message": "Task unlinked from risk successfully"}
