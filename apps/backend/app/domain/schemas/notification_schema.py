from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class NotificationResponse(BaseModel):
    """Schema returned when reading a user notification."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the notification")
    user_id: uuid.UUID = Field(..., description="ID of the recipient user")
    type: str = Field(..., description="Notification type, e.g. 'task_assigned'")
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification body message")
    entity_type: str = Field(
        ..., description="Type of entity this notification relates to"
    )
    entity_id: uuid.UUID = Field(
        ..., description="ID of the related entity"
    )
    is_read: bool = Field(..., description="Whether the notification has been read")
    created_at: datetime = Field(..., description="Creation timestamp")


class NotificationMarkRead(BaseModel):
    """Schema for marking a batch of notifications as read."""

    notification_ids: list[uuid.UUID] = Field(
        ..., description="List of notification IDs to mark as read"
    )
