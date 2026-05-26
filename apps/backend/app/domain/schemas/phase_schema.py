from __future__ import annotations

import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class PhaseCreate(BaseModel):
    """Schema for creating a new project phase."""

    project_id: uuid.UUID = Field(..., description="Reference to the owning project")
    name: str = Field(..., max_length=200, description="Phase name")
    weight_percent: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0,
        description="Weight of this phase as a percentage of the project",
    )


class PhaseUpdate(BaseModel):
    """Schema for partially updating an existing phase."""

    name: str | None = Field(None, max_length=200, description="Updated phase name")
    weight_percent: float | None = Field(
        None,
        ge=0.0,
        le=100.0,
        description="Updated weight percentage",
    )
    order_index: int | None = Field(None, description="Updated display order")


class PhaseResponse(BaseModel):
    """Schema returned when reading a phase."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the phase")
    project_id: uuid.UUID = Field(..., description="Reference to the owning project")
    name: str = Field(..., max_length=200, description="Phase name")
    wbs_code: str = Field(..., description="Work Breakdown Structure code")
    order_index: int = Field(..., description="Display order within the project")
    weight_percent: float = Field(..., description="Weight percentage of the project")
    planned_start: date | None = Field(None, description="Planned start date")
    planned_finish: date | None = Field(None, description="Planned finish date")
