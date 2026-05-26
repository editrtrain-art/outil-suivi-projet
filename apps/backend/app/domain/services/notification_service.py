"""Domain service for notification management.

Handles creation, retrieval, and status updates for user notifications.
"""

from __future__ import annotations

import uuid
from typing import List, Optional

import structlog

from app.domain.models.audit_log import Notification
from app.domain.repositories.interfaces import INotificationRepository

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


from sqlalchemy.ext.asyncio import AsyncSession

class NotificationService:
    """Service for managing user notifications."""

    def __init__(self, notification_repo: INotificationRepository | AsyncSession) -> None:
        """Initialize with a notification repository or a database session.

        Args:
            notification_repo: INotificationRepository or AsyncSession for database operations.
        """
        if isinstance(notification_repo, AsyncSession):
            from app.infrastructure.repositories.sqlalchemy_repos import SQLAlchemyNotificationRepository
            self.notification_repo = SQLAlchemyNotificationRepository(notification_repo)
        else:
            self.notification_repo = notification_repo

    async def create_notification(
        self,
        user_id: uuid.UUID,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[uuid.UUID] = None,
    ) -> Notification:
        """Create a notification for a user.

        Args:
            user_id: UUID of the target user.
            notification_type: Type category (e.g., 'risk_alert', 'task_update').
            title: Short notification title.
            message: Optional detailed message body.
            entity_type: Optional entity type for deep linking.
            entity_id: Optional entity UUID for deep linking.

        Returns:
            Notification: The persisted notification.
        """
        notification = Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        await self.notification_repo.add(notification)
        await self.notification_repo.commit()
        await self.notification_repo.refresh(notification)
        logger.info(
            "notification_created",
            user_id=str(user_id),
            type=notification_type,
        )
        return notification

    async def get_user_notifications(
        self,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> List[Notification]:
        """List notifications for a user, newest first.

        Args:
            user_id: UUID of the user.
            limit: Maximum number of notifications to return.

        Returns:
            List of Notification records.
        """
        notifications = await self.notification_repo.get_user_notifications(user_id)
        return notifications[:limit]

    async def mark_read(
        self,
        notification_ids: List[uuid.UUID],
        user_id: uuid.UUID,
    ) -> int:
        """Mark notifications as read for a user.

        Args:
            notification_ids: List of notification UUIDs to mark.
            user_id: UUID of the owning user (security guard).

        Returns:
            int: Number of notifications updated.
        """
        count = await self.notification_repo.mark_notifications_read(notification_ids, user_id)
        await self.notification_repo.commit()
        logger.info(
            "notifications_marked_read",
            user_id=str(user_id),
            count=count,
        )
        return count
