"""API Router for EVM (Earned Value Management).

Exposes EVM metrics computation for a project based on its
budget, planned progress, and actual costs.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_viewer
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.progress_log import ProgressLog
from app.domain.services.evm_calculator import EVMCalculator, EVMMetrics
from app.core.exceptions import NotFoundError

router = APIRouter(prefix="/evm", tags=["evm"])


class EVMResponse(BaseModel):
    project_id: uuid.UUID
    as_of_date: date
    pv: float = Field(description="Planned Value (BCWS)")
    ev: float = Field(description="Earned Value (BCWP)")
    ac: float = Field(description="Actual Cost (ACWP)")
    bac: float = Field(description="Budget at Completion")
    spi: float | None = Field(default=None, description="Schedule Performance Index")
    cpi: float | None = Field(default=None, description="Cost Performance Index")
    eac: float = Field(description="Estimate at Completion")
    vac: float = Field(description="Variance at Completion")
    status: str


@router.get("/project/{project_id}", response_model=EVMResponse)
@router.get("/project/{project_id}/indicators", response_model=EVMResponse)
async def get_project_evm(
    project_id: uuid.UUID,
    as_of_date: date = Query(default=None, description="Status date (defaults to today)"),
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_viewer),
) -> EVMResponse:
    """Compute EVM indicators for a project as of a given date.

    The calculation:
    - PV = sum of (task.weight_percent / 100 * project.budget_total) for tasks
           whose scheduled end is on or before as_of_date
    - EV = sum of (latest progress_log.physical_percent / 100 * task weight * budget)
    - AC = sum of actual_cost from progress_logs
    """
    from datetime import date as date_type
    status_date = as_of_date or date_type.today()

    # Load project
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project", str(project_id))

    bac = float(project.budget_total or 0)

    # Load all tasks for the project via phases
    phases_result = await db.execute(
        select(Phase).where(Phase.project_id == project_id)
    )
    phases = phases_result.scalars().all()
    phase_ids = [p.id for p in phases]

    if not phase_ids:
        metrics = EVMCalculator.calculate(0, 0, 0, bac)
        return EVMResponse(
            project_id=project_id,
            as_of_date=status_date,
            pv=0, ev=0, ac=0, bac=bac,
            spi=metrics.spi, cpi=metrics.cpi,
            eac=metrics.eac, vac=metrics.vac,
            status=metrics.status,
        )

    tasks_result = await db.execute(
        select(Task).where(Task.phase_id.in_(phase_ids))
    )
    tasks = tasks_result.scalars().all()

    pv = 0.0
    ev = 0.0
    ac = 0.0

    for task in tasks:
        task_budget = (float(task.weight_percent) / 100.0) * bac

        # Planned Value: tasks scheduled to finish on or before status_date
        if task.end_date_scheduled and task.end_date_scheduled <= status_date:
            pv += task_budget

        # Load latest progress log for EV and AC
        log_result = await db.execute(
            select(ProgressLog)
            .where(ProgressLog.task_id == task.id)
            .where(ProgressLog.log_date <= status_date)
            .order_by(ProgressLog.log_date.desc())
            .limit(1)
        )
        log = log_result.scalar_one_or_none()
        if log:
            ev += (float(log.physical_percent) / 100.0) * task_budget
            ac += float(log.actual_cost_dh or 0)

    metrics = EVMCalculator.calculate(pv=pv, ev=ev, ac=ac, bac=bac)

    return EVMResponse(
        project_id=project_id,
        as_of_date=status_date,
        pv=round(pv, 2),
        ev=round(ev, 2),
        ac=round(ac, 2),
        bac=round(bac, 2),
        spi=metrics.spi,
        cpi=metrics.cpi,
        eac=metrics.eac,
        vac=metrics.vac,
        status=metrics.status,
    )
