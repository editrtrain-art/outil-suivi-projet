"""API Router for LLM AI Insights.

Endpoints for automated project risk audits and scheduling analysis.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.permissions import require_pm
from app.domain.models.audit_log import AIInsight
from app.domain.services.llm_service import LLMService

router = APIRouter(prefix="/llm", tags=["llm"])


class ProjectAuditResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    insight_text: str
    generated_at: datetime
    triggered_by: Optional[uuid.UUID] = None

    model_config = ConfigDict(from_attributes=True)


@router.get("/project/{project_id}/audit", response_model=ProjectAuditResponse)
async def get_project_audit(
    project_id: uuid.UUID,
    force_refresh: bool = Query(default=False, description="Force a new LLM generation"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_pm),
) -> ProjectAuditResponse:
    """Fetch the latest AI risk audit report or generate a new one.

    If force_refresh is True or no prior audit report exists, triggers a new API
    request to the configured LLM engine and persists the result.
    """
    user_id = uuid.UUID(current_user["sub"])
    service = LLMService(db)

    if not force_refresh:
        # Check if an audit was already generated
        result = await db.execute(
            select(AIInsight)
            .where(AIInsight.project_id == project_id)
            .order_by(AIInsight.generated_at.desc())
            .limit(1)
        )
        existing = result.scalar_one_or_none()
        if existing:
            return ProjectAuditResponse.model_validate(existing)

    # Generate a new audit
    insight_text = await service.generate_project_audit(project_id, triggered_by=user_id)

    # Fetch the newly saved record
    result = await db.execute(
        select(AIInsight)
        .where(AIInsight.project_id == project_id)
        .order_by(AIInsight.generated_at.desc())
        .limit(1)
    )
    new_insight = result.scalar_one()
    return ProjectAuditResponse.model_validate(new_insight)
