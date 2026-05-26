from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BaselineCreate(BaseModel):
    """Schema for creating a new project baseline snapshot."""

    project_id: uuid.UUID = Field(..., description="Reference to the owning project")
    version_code: str = Field(
        ..., max_length=20, description="Version code, e.g. 'v1.0'"
    )
    description: str | None = Field(None, description="Optional baseline description")
    is_active: bool = Field(
        default=False, description="Whether this baseline is currently active"
    )


class BaselineResponse(BaseModel):
    """Schema returned when reading a baseline."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the baseline")
    project_id: uuid.UUID = Field(..., description="Reference to the owning project")
    version_code: str = Field(..., description="Version code label")
    description: str | None = Field(None, description="Baseline description")
    snapshot: dict[str, Any] = Field(..., description="Frozen project state snapshot")
    locked_by: uuid.UUID | None = Field(
        None, description="ID of the user who locked this baseline"
    )
    is_active: bool = Field(..., description="Whether this baseline is active")
    locked_at: datetime = Field(..., description="Timestamp when the baseline was locked")
