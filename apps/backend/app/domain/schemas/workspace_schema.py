from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID

class WorkspaceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(default_factory=UUID, description="Unique identifier for the workspace")
    name: str = Field(..., max_length=200)
    owner_id: UUID = Field(..., description="User ID of the workspace owner")
