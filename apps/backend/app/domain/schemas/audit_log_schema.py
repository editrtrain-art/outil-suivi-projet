from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AuditLogResponse(BaseModel):
    """Schema returned when reading an audit log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(..., description="Unique identifier for the audit entry")
    workspace_id: uuid.UUID = Field(..., description="Workspace scope of the action")
    user_id: uuid.UUID = Field(..., description="ID of the acting user")
    entity_type: str = Field(..., description="Type of entity affected")
    entity_id: uuid.UUID = Field(..., description="ID of the affected entity")
    action: str = Field(..., description="Action performed, e.g. 'create', 'update'")
    old_value: dict[str, Any] | None = Field(
        None, description="Previous state before the action"
    )
    new_value: dict[str, Any] | None = Field(
        None, description="New state after the action"
    )
    ip_address: str | None = Field(None, description="IP address of the requester")
    created_at: datetime = Field(..., description="Timestamp of the action")


class AuditLogFilter(BaseModel):
    """Schema for filtering audit log queries."""

    entity_type: str | None = Field(None, description="Filter by entity type")
    user_id: uuid.UUID | None = Field(None, description="Filter by acting user")
    date_from: datetime | None = Field(None, description="Start of date range filter")
    date_to: datetime | None = Field(None, description="End of date range filter")
