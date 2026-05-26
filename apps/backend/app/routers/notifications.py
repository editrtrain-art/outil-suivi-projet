"""API Router for Notifications.

Endpoints for listing, marking read, and managing user notifications.
"""

from __future__ import annotations

import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.domain.models.audit_log import Notification

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    """Schema for returning a notification."""

    id: uuid.UUID
    user_id: uuid.UUID
    type: str
    title: str
    message: str | None = None
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    is_read: bool

    model_config = ConfigDict(from_attributes=True)


class MarkReadRequest(BaseModel):
    """Schema for marking notifications as read."""

    notification_ids: List[uuid.UUID]


@router.get("/", response_model=List[NotificationResponse])
async def list_user_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> List[NotificationResponse]:
    """List all notifications for the current authenticated user."""
    user_id = uuid.UUID(current_user["sub"])
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
        .limit(100)
    )
    return [NotificationResponse.model_validate(n) for n in result.scalars().all()]


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, int]:
    """Get the count of unread notifications for the current user."""
    user_id = uuid.UUID(current_user["sub"])
    from sqlalchemy import func

    result = await db.execute(
        select(func.count(Notification.id))
        .where(Notification.user_id == user_id)
        .where(Notification.is_read == False)  # noqa: E712
    )
    count = result.scalar() or 0
    return {"unread_count": count}


@router.post("/mark-read", status_code=status.HTTP_200_OK)
async def mark_notifications_read(
    data: MarkReadRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict[str, Any] = Depends(get_current_user),
) -> dict[str, str]:
    """Mark specified notifications as read for the current user."""
    user_id = uuid.UUID(current_user["sub"])
    await db.execute(
        update(Notification)
        .where(Notification.id.in_(data.notification_ids))
        .where(Notification.user_id == user_id)
        .values(is_read=True)
    )
    await db.commit()
    return {"status": "ok", "marked_count": str(len(data.notification_ids))}
