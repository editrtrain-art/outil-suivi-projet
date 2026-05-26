"""Risk service implementation.

Handles risk identification, scoring, mitigation tracking, task-risk linking,
contingency application, and notification of critical risks.
"""

from __future__ import annotations

import uuid
from typing import List, Optional, Any

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.domain.models.project import Project
from app.domain.models.risk import Risk, RiskTaskLink

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


class RiskService:
    """Service layer for risk management, contingency factors, and task linking."""

    def __init__(self, db: AsyncSession) -> None:
        """Initialize with database session.

        Args:
            db: Scoped async database session.
        """
        self.db = db

    async def create_risk(
        self,
        project_id: uuid.UUID,
        title: str,
        probability: int,
        impact: int,
        category: str,
        description: Optional[str] = None,
        mitigation: Optional[str] = None,
        owner_id: Optional[uuid.UUID] = None,
        contingency_threshold: int = 15,
        contingency_factor: float = 0.15,
    ) -> Risk:
        """Create a new risk, check criticality, and return the entity.

        Args:
            project_id: Project identifier.
            title: Short risk title.
            probability: Probability rating (1-5).
            impact: Impact rating (1-5).
            category: Classification category.
            description: Optional details.
            mitigation: Optional mitigation plan.
            owner_id: Optional owner user ID.
            contingency_threshold: Risk score above which contingency is applied.
            contingency_factor: Duration modifier percentage for linked tasks.

        Returns:
            Risk: The created risk instance.
        """
        risk_score = probability * impact
        risk = Risk(
            project_id=project_id,
            title=title,
            probability=probability,
            impact=impact,
            risk_score=risk_score,
            category=category,
            description=description,
            mitigation=mitigation,
            owner_id=owner_id,
            contingency_threshold=contingency_threshold,
            contingency_factor=contingency_factor,
            status="active",
        )
        self.db.add(risk)
        await self.db.flush()

        logger.info(
            "risk_created",
            risk_id=str(risk.id),
            project_id=str(project_id),
            score=risk_score,
        )

        # Notify team if risk is critical
        if risk.risk_score >= risk.contingency_threshold:
            await self._notify_critical_risk(risk)

        await self.db.commit()
        await self.db.refresh(risk)
        return risk

    async def get_risk_by_id(self, risk_id: uuid.UUID) -> Risk:
        """Retrieve a single risk or raise NotFoundError.

        Args:
            risk_id: The risk UUID.

        Returns:
            Risk: The found risk instance.

        Raises:
            NotFoundError: If the risk is not found.
        """
        risk = await self.db.get(Risk, risk_id)
        if not risk:
            raise NotFoundError("Risk", str(risk_id))
        return risk

    async def get_project_risks(self, project_id: uuid.UUID) -> List[Risk]:
        """List all risks for a project.

        Args:
            project_id: The project UUID.

        Returns:
            List[Risk]: All risks belonging to the project.
        """
        result = await self.db.execute(
            select(Risk).where(Risk.project_id == project_id)
        )
        return list(result.scalars().all())

    async def update_risk(self, risk_id: uuid.UUID, **kwargs: Any) -> Risk:
        """Partially update a risk, trigger CPM on threshold breach, and notify.

        Args:
            risk_id: The risk UUID.
            **kwargs: Dict of attributes to update.

        Returns:
            Risk: The updated risk instance.
        """
        risk = await self.get_risk_by_id(risk_id)

        old_score = risk.risk_score
        old_status = risk.status

        for key, value in kwargs.items():
            if hasattr(risk, key):
                setattr(risk, key, value)

        # Recalculate score
        risk.risk_score = risk.probability * risk.impact

        await self.db.flush()

        # Check threshold breach changes
        score_breached = risk.risk_score >= risk.contingency_threshold
        old_score_breached = old_score >= risk.contingency_threshold
        status_changed = old_status != risk.status

        # If criticality state changes, we must recalculate CPM schedule
        cpm_trigger = (
            (score_breached != old_score_breached)
            or (status_changed and (score_breached or old_score_breached))
            or (risk.status == "active" and score_breached and "contingency_factor" in kwargs)
        )

        if cpm_trigger:
            logger.info("risk_threshold_recalculation_trigger", risk_id=str(risk_id), project_id=str(risk.project_id))
            from app.domain.services.task_service import TaskService
            task_service = TaskService(self.db)
            await task_service.run_cpm_for_project(risk.project_id)

        # Notify if the risk transitioned to active critical
        if risk.status == "active" and score_breached and not old_score_breached:
            await self._notify_critical_risk(risk)

        await self.db.commit()
        await self.db.refresh(risk)
        return risk

    async def link_task(self, risk_id: uuid.UUID, task_id: uuid.UUID) -> None:
        """Link a task to a risk and run CPM recalculation if risk is active and critical.

        Args:
            risk_id: The risk UUID.
            task_id: The task UUID.

        Raises:
            NotFoundError: If risk or task is missing.
            ValidationError: If entities belong to different projects.
        """
        risk = await self.get_risk_by_id(risk_id)

        from app.domain.models.task import Task
        task = await self.db.get(Task, task_id)
        if not task:
            raise NotFoundError("Task", str(task_id))

        from app.domain.models.phase import Phase
        phase = await self.db.get(Phase, task.phase_id)
        if not phase or phase.project_id != risk.project_id:
            raise ValidationError("Task and Risk must belong to the same project")

        # Check if already linked
        result = await self.db.execute(
            select(RiskTaskLink).where(
                RiskTaskLink.risk_id == risk_id,
                RiskTaskLink.task_id == task_id,
            )
        )
        existing = result.scalar_one_or_none()
        if not existing:
            link = RiskTaskLink(risk_id=risk_id, task_id=task_id)
            self.db.add(link)
            await self.db.flush()

            # Recalculate CPM if this risk is active and critical
            if risk.status == "active" and risk.risk_score >= risk.contingency_threshold:
                logger.info("task_linked_recalculation_trigger", risk_id=str(risk_id), task_id=str(task_id))
                from app.domain.services.task_service import TaskService
                task_service = TaskService(self.db)
                await task_service.run_cpm_for_project(risk.project_id)

            await self.db.commit()

    async def unlink_task(self, risk_id: uuid.UUID, task_id: uuid.UUID) -> None:
        """Unlink a task from a risk and run CPM recalculation if risk was active and critical.

        Args:
            risk_id: The risk UUID.
            task_id: The task UUID.
        """
        risk = await self.get_risk_by_id(risk_id)

        result = await self.db.execute(
            select(RiskTaskLink).where(
                RiskTaskLink.risk_id == risk_id,
                RiskTaskLink.task_id == task_id,
            )
        )
        link = result.scalar_one_or_none()
        if link:
            await self.db.delete(link)
            await self.db.flush()

            # Recalculate CPM if this risk is active and critical
            if risk.status == "active" and risk.risk_score >= risk.contingency_threshold:
                logger.info("task_unlinked_recalculation_trigger", risk_id=str(risk_id), task_id=str(task_id))
                from app.domain.services.task_service import TaskService
                task_service = TaskService(self.db)
                await task_service.run_cpm_for_project(risk.project_id)

            await self.db.commit()

    async def _notify_critical_risk(self, risk: Risk) -> None:
        """Create a notification when a risk score exceeds the contingency threshold.

        Args:
            risk: The critical Risk entity.
        """
        from app.domain.services.notification_service import NotificationService
        notif_service = NotificationService(self.db)

        recipients = set()
        if risk.owner_id:
            recipients.add(risk.owner_id)

        project = await self.db.get(Project, risk.project_id)
        if project and project.pm_user_id:
            recipients.add(project.pm_user_id)

        for user_id in recipients:
            try:
                await notif_service.create_notification(
                    user_id=user_id,
                    notification_type="risk_alert",
                    title=f"Critical Risk: {risk.title}",
                    message=(
                        f"The risk '{risk.title}' has breached its contingency threshold "
                        f"with a score of {risk.risk_score} (Threshold: {risk.contingency_threshold})."
                    ),
                    entity_type="risk",
                    entity_id=risk.id,
                )
            except Exception as e:
                logger.warning("failed_to_send_risk_notification", user_id=str(user_id), error=str(e))
