from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DeliverableCreate(BaseModel):
    """Schema for creating a new deliverable attached to a task."""

    task_id: uuid.UUID = Field(..., description="ID of the parent task")
    name: str = Field(..., max_length=255, description="Deliverable name")
    description: str | None = Field(None, description="Optional description")
    due_date: date | None = Field(None, description="Expected due date")
    assigned_to: uuid.UUID | None = Field(
        None, description="ID of the user responsible for this deliverable"
    )


class DeliverableUpdate(BaseModel):
    """Schema for partially updating an existing deliverable."""

    name: str | None = Field(None, max_length=255, description="Updated name")
    description: str | None = Field(None, description="Updated description")
    due_date: date | None = Field(None, description="Updated due date")
    status: Literal["draft", "submitted", "in_review", "approved", "rejected"] | None = Field(
        None, description="Updated status"
    )


class DeliverableResponse(BaseModel):
    """Schema returned when reading a deliverable."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the deliverable")
    task_id: uuid.UUID = Field(..., description="ID of the parent task")
    name: str = Field(..., max_length=255, description="Deliverable name")
    description: str | None = Field(None, description="Deliverable description")
    due_date: date | None = Field(None, description="Expected due date")
    status: str = Field(..., description="Current status of the deliverable")
    assigned_to: uuid.UUID | None = Field(
        None, description="ID of the assigned user"
    )
    file_url: str | None = Field(None, description="URL to the attached file")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class DeliverableTransition(BaseModel):
    """Schema for triggering a deliverable state-machine transition."""

    action: Literal["submit", "review", "approve", "reject"] = Field(
        ..., description="Transition action to perform"
    )
    comment: str | None = Field(None, description="Optional comment for the transition")
