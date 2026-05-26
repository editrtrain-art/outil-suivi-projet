from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RiskCreate(BaseModel):
    """Schema for creating a new project risk."""

    project_id: uuid.UUID = Field(..., description="Reference to the owning project")
    title: str = Field(..., max_length=255, description="Short risk title")
    description: str | None = Field(None, description="Detailed risk description")
    category: Literal[
        "technical", "schedule", "budget", "resource", "external", "quality"
    ] = Field(..., description="Risk category")
    probability: int = Field(..., ge=1, le=5, description="Probability rating 1-5")
    impact: int = Field(..., ge=1, le=5, description="Impact rating 1-5")
    mitigation: str | None = Field(None, description="Planned mitigation strategy")
    owner_id: uuid.UUID | None = Field(
        None, description="ID of the risk owner"
    )
    contingency_threshold: int = Field(
        default=15, description="Risk-score threshold that triggers contingency"
    )
    contingency_factor: float = Field(
        default=0.15, description="Contingency budget multiplier"
    )


class RiskUpdate(BaseModel):
    """Schema for partially updating an existing risk."""

    title: str | None = Field(None, max_length=255, description="Updated title")
    description: str | None = Field(None, description="Updated description")
    category: Literal[
        "technical", "schedule", "budget", "resource", "external", "quality"
    ] | None = Field(None, description="Updated category")
    probability: int | None = Field(
        None, ge=1, le=5, description="Updated probability"
    )
    impact: int | None = Field(None, ge=1, le=5, description="Updated impact")
    mitigation: str | None = Field(None, description="Updated mitigation strategy")
    status: Literal["active", "mitigated", "closed"] | None = Field(
        None, description="Updated risk status"
    )


class RiskResponse(BaseModel):
    """Schema returned when reading a risk."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the risk")
    project_id: uuid.UUID = Field(..., description="Reference to the owning project")
    title: str = Field(..., description="Short risk title")
    description: str | None = Field(None, description="Detailed description")
    category: str = Field(..., description="Risk category")
    probability: int = Field(..., description="Probability rating 1-5")
    impact: int = Field(..., description="Impact rating 1-5")
    risk_score: int = Field(..., description="Computed risk score (probability × impact)")
    mitigation: str | None = Field(None, description="Mitigation strategy")
    owner_id: uuid.UUID | None = Field(None, description="ID of the risk owner")
    status: str = Field(..., description="Current risk status")
    contingency_threshold: int = Field(..., description="Score threshold for contingency")
    contingency_factor: float = Field(..., description="Budget contingency multiplier")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class RiskUpdateNote(BaseModel):
    """Schema for adding a note to a risk."""

    note: str = Field(..., description="Risk update note content")
