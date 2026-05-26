from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DependencyCreate(BaseModel):
    """Schema for creating a task dependency link."""

    predecessor_task_id: uuid.UUID = Field(
        ..., description="ID of the predecessor task"
    )
    dependency_type: Literal["FS", "SS", "FF", "SF"] = Field(
        default="FS",
        description="Dependency type: Finish-Start, Start-Start, Finish-Finish, Start-Finish",
    )
    lag_days: int = Field(
        default=0, description="Lag in days between the linked tasks"
    )


class DependencyResponse(BaseModel):
    """Schema returned when reading a dependency."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the dependency")
    task_id: uuid.UUID = Field(..., description="ID of the successor task")
    predecessor_task_id: uuid.UUID = Field(
        ..., description="ID of the predecessor task"
    )
    dependency_type: Literal["FS", "SS", "FF", "SF"] = Field(
        ..., description="Type of dependency link"
    )
    lag_days: int = Field(..., description="Lag in days")
    created_at: datetime = Field(..., description="Timestamp when the dependency was created")
