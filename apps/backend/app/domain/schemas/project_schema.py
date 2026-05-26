from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID
from datetime import date

class ProjectSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=UUID, description="Unique identifier for the project")
    workspace_id: UUID = Field(..., description="Reference to the owning workspace")
    name: str = Field(..., max_length=200)
    description: str | None = Field(None, max_length=1000)
    start_date: date
    end_date: date
    budget_total: float = 0.0
    status: str = "draft"
    active_baseline_id: UUID | None = None
    pm_user_id: UUID | None = None
