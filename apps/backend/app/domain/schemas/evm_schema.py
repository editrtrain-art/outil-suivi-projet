from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class EVMIndicators(BaseModel):
    """Earned Value Management computed indicators for a project."""

    pv: float = Field(..., description="Planned Value")
    ev: float = Field(..., description="Earned Value")
    ac: float = Field(..., description="Actual Cost")
    bac: float = Field(..., description="Budget At Completion")
    sv: float = Field(..., description="Schedule Variance (EV - PV)")
    cv: float = Field(..., description="Cost Variance (EV - AC)")
    spi: float = Field(..., description="Schedule Performance Index (EV / PV)")
    cpi: float | None = Field(None, description="Cost Performance Index (EV / AC)")
    eac: float = Field(..., description="Estimate At Completion")
    vac: float = Field(..., description="Variance At Completion (BAC - EAC)")
    tcpi: float | None = Field(
        None, description="To-Complete Performance Index"
    )
    status: str = Field(
        ..., description="Overall EVM health status, e.g. 'on_track', 'at_risk'"
    )


class SCurveDataPoint(BaseModel):
    """A single data point on the S-curve timeline."""

    date: str = Field(..., description="Date label for the data point")
    pv_cumulative: float = Field(..., description="Cumulative Planned Value")
    ev_cumulative: float = Field(..., description="Cumulative Earned Value")
    ac_cumulative: float = Field(..., description="Cumulative Actual Cost")


class SCurveResponse(BaseModel):
    """S-curve response containing all data points for a project."""

    project_id: uuid.UUID = Field(..., description="Reference to the project")
    data_points: list[SCurveDataPoint] = Field(
        ..., description="Ordered list of S-curve data points"
    )
