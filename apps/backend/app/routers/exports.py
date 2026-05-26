"""API Router for Document Exports.

Provides PDF status reports and Excel task schedule downloads.
"""

from __future__ import annotations

import uuid
from datetime import date
from typing import Dict, Any

from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_viewer
from app.core.exceptions import NotFoundError
from app.domain.models.project import Project
from app.domain.models.phase import Phase
from app.domain.models.task import Task
from app.domain.models.progress_log import ProgressLog
from app.domain.services.export_service import ExportService

router = APIRouter(prefix="/exports", tags=["exports"])


async def _get_project_evm_data(project_id: uuid.UUID, db: AsyncSession) -> Dict[str, Any]:
    """Helper to compute EVM metrics for PDF generation."""
    project = await db.get(Project, project_id)
    if not project:
        raise NotFoundError("Project", str(project_id))

    bac = float(project.budget_total or 0.0)

    # Load all tasks
    phases_result = await db.execute(
        select(Phase).where(Phase.project_id == project_id)
    )
    phases = phases_result.scalars().all()
    phase_ids = [p.id for p in phases]

    if not phase_ids:
        return {"pv": 0.0, "ev": 0.0, "ac": 0.0, "spi": 1.0, "cpi": 1.0, "eac": bac, "cv": 0.0, "sv": 0.0}

    tasks_result = await db.execute(
        select(Task).where(Task.phase_id.in_(phase_ids))
    )
    tasks = tasks_result.scalars().all()

    status_date = date.today()
    pv = 0.0
    ev = 0.0
    ac = 0.0

    for task in tasks:
        task_budget = (float(task.weight_percent or 0.0) / 100.0) * bac

        # Planned Value
        if task.end_date_scheduled and task.end_date_scheduled <= status_date:
            pv += task_budget

        # Latest progress log
        log_result = await db.execute(
            select(ProgressLog)
            .where(ProgressLog.task_id == task.id)
            .where(ProgressLog.log_date <= status_date)
            .order_by(ProgressLog.log_date.desc())
            .limit(1)
        )
        log = log_result.scalar_one_or_none()
        if log:
            ev += (float(log.physical_percent or 0.0) / 100.0) * task_budget
            ac += float(log.actual_cost_dh or 0.0)

    # Compute indexes
    spi = ev / pv if pv > 0.0 else 1.0
    cpi = ev / ac if ac > 0.0 else 1.0
    eac = bac / cpi if cpi > 0.0 else bac
    cv = ev - ac
    sv = ev - pv

    return {
        "pv": pv,
        "ev": ev,
        "ac": ac,
        "spi": spi,
        "cpi": cpi,
        "eac": eac,
        "cv": cv,
        "sv": sv,
    }


@router.get("/project/{project_id}/pdf")
async def export_project_pdf(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_viewer),
) -> Response:
    """Download a compiled PDF project status summary report."""
    evm_data = await _get_project_evm_data(project_id, db)
    service = ExportService(db)
    pdf_bytes = await service.generate_project_pdf(project_id, evm_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=project_{project_id}_status.pdf"
        },
    )


@router.get("/project/{project_id}/excel")
async def export_project_excel(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(require_viewer),
) -> Response:
    """Download a compiled Excel WBS scheduling worksheet."""
    service = ExportService(db)
    excel_bytes = await service.generate_project_excel(project_id)

    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename=project_{project_id}_planning.xlsx"
        },
    )
