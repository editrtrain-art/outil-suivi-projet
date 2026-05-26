from __future__ import annotations

import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ProgressLogCreate(BaseModel):
    """Schema for creating a progress log entry on a task."""

    task_id: uuid.UUID = Field(..., description="ID of the task being tracked")
    log_date: date = Field(..., description="Date of the progress entry")
    physical_percent: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Physical completion percentage",
    )
    actual_hours: float = Field(
        default=0.0, description="Actual hours spent on this date"
    )
    actual_cost_dh: float = Field(
        default=0.0, description="Actual cost in DH on this date"
    )
    notes: str | None = Field(None, description="Optional notes for the log entry")


class ProgressLogResponse(BaseModel):
    """Schema returned when reading a progress log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the log entry")
    task_id: uuid.UUID = Field(..., description="ID of the tracked task")
    log_date: date = Field(..., description="Date of the progress entry")
    physical_percent: float = Field(..., description="Physical completion percentage")
    actual_hours: float = Field(..., description="Actual hours spent")
    actual_cost_dh: float = Field(..., description="Actual cost in DH")
    logged_by: uuid.UUID | None = Field(
        None, description="ID of the user who logged this entry"
    )
    notes: str | None = Field(None, description="Optional notes")
    created_at: datetime = Field(..., description="Timestamp when the entry was created")
