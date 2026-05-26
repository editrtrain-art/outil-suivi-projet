from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field


class AssignmentCreate(BaseModel):
    """Schema for creating a resource assignment to a task."""

    task_id: uuid.UUID = Field(..., description="ID of the task to assign")
    resource_id: uuid.UUID = Field(..., description="ID of the resource being assigned")
    allocation_percent: float = Field(
        default=100.0,
        ge=0.0,
        le=100.0,
        description="Percentage of the resource allocated to this task",
    )
    planned_hours: float | None = Field(
        None, description="Planned effort in hours for this assignment"
    )


class AssignmentResponse(BaseModel):
    """Schema returned when reading a resource assignment."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the assignment")
    task_id: uuid.UUID = Field(..., description="ID of the assigned task")
    resource_id: uuid.UUID = Field(..., description="ID of the assigned resource")
    allocation_percent: float = Field(
        ..., description="Percentage of resource allocated"
    )
    planned_hours: float | None = Field(
        None, description="Planned effort in hours"
    )
