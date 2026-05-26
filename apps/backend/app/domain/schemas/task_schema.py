from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from typing import Literal

class TaskSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=UUID, description="Unique identifier for the task")
    project_id: UUID = Field(..., description="Reference to the associated project")
    name: str = Field(..., max_length=200)
    status: Literal["todo", "in_progress", "done"] = "todo"
    estimated_effort: float = 0.0
    actual_effort: float = 0.0
