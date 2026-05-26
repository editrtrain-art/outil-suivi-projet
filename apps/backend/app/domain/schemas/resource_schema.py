from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class ResourceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=UUID, description="Unique identifier for the resource")
    type: str = Field(..., max_length=100, description="Resource type, e.g., 'personnel', 'equipment'")
    capacity: float = Field(..., description="Capacity or amount associated with the resource")
    project_id: UUID | None = Field(None, description="Optional reference to the associated project")
