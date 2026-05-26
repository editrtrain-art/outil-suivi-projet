"""EVM (Earned Value Management) Calculator.

Implements the V3 enhanced EVM indicator suite per master-guidelines §6.2.
Computes PV, EV, AC, SPI, CPI, EAC (enhanced), VAC, TCPI, SV, CV.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class EVMMetrics:
    """Complete EVM indicator set per master-guidelines §6.2.

    Attributes:
        pv: Planned Value (BCWS) at reference date.
        ev: Earned Value (BCWP) at reference date.
        ac: Actual Cost (ACWP) at reference date.
        bac: Budget at Completion (total authorized budget).
        sv: Schedule Variance (EV - PV). Negative = behind schedule.
        cv: Cost Variance (EV - AC). Negative = over budget.
        spi: Schedule Performance Index (EV / PV). < 1 = behind.
        cpi: Cost Performance Index (EV / AC). None if AC = 0.
        eac: Estimate at Completion (V3 enhanced formula).
        vac: Variance at Completion (BAC - EAC).
        tcpi: To-Complete Performance Index.
        status: Computed health status string.
    """

    pv: float
    ev: float
    ac: float
    bac: float
    sv: float = 0.0
    cv: float = 0.0
    spi: float = 1.0
    cpi: Optional[float] = None
    eac: float = 0.0
    vac: float = 0.0
    tcpi: Optional[float] = None
    status: str = "on_track"


class EVMCalculator:
    """Core logic for EVM indicator computation.

    Implements the V3 enhanced EAC formula:
    ``EAC = AC + (BAC − EV) / (SPI × CPI)``

    This is more conservative than V2 (``EAC = BAC / CPI``) because
    it accounts for both schedule and cost inefficiency simultaneously.
    """

    @staticmethod
    def calculate(pv: float, ev: float, ac: float, bac: float) -> EVMMetrics:
        """Compute all EVM indicators per master-guidelines §6.2.

        Args:
            pv: Planned Value (interpolated planned progress × budget).
            ev: Earned Value (physical % × budget).
            ac: Actual Cost (sum of actual expenditures to date).
            bac: Budget at Completion (total project budget).

        Returns:
            EVMMetrics: Complete indicator set with division-by-zero guards.
        """
        # Schedule Variance and Cost Variance
        sv = ev - pv
        cv = ev - ac

        # SPI — guard against PV = 0
        spi = ev / pv if pv > 0 else 1.0

        # CPI — per spec, return None if AC = 0 (no cost recorded yet)
        cpi: Optional[float] = None
        if ac > 0:
            cpi = ev / ac

        # EAC — V3 enhanced formula: AC + (BAC − EV) / (SPI × CPI)
        # Fallback to BAC if SPI or CPI would cause division by zero
        if cpi is not None and spi > 0 and cpi > 0:
            eac = ac + (bac - ev) / (spi * cpi)
        elif cpi is not None and cpi > 0:
            # SPI unknown/zero but CPI available — fall back to BAC / CPI
            eac = bac / cpi
        else:
            eac = bac

        # VAC — Variance at Completion
        vac = bac - eac

        # TCPI — To-Complete Performance Index: (BAC − EV) / (BAC − AC)
        tcpi: Optional[float] = None
        denominator = bac - ac
        if denominator > 0:
            tcpi = round((bac - ev) / denominator, 3)

        # Status determination per master-guidelines §6.2 alert thresholds
        status = _determine_status(spi, cpi)

        return EVMMetrics(
            pv=pv,
            ev=ev,
            ac=ac,
            bac=bac,
            sv=round(sv, 2),
            cv=round(cv, 2),
            spi=round(spi, 3),
            cpi=round(cpi, 3) if cpi is not None else None,
            eac=round(eac, 2),
            vac=round(vac, 2),
            tcpi=tcpi,
            status=status,
        )

    @staticmethod
    def interpolate_planned_percent(
        reference_date_offset: int,
        planned_start_offset: int,
        planned_finish_offset: int,
    ) -> float:
        """Compute the planned percent complete at a reference date.

        Uses linear interpolation per master-guidelines §6.2.

        Args:
            reference_date_offset: Days from project start to reference date.
            planned_start_offset: Days from project start to task planned start.
            planned_finish_offset: Days from project start to task planned finish.

        Returns:
            Planned percent complete (0.0 to 100.0).
        """
        if reference_date_offset < planned_start_offset:
            return 0.0
        if reference_date_offset >= planned_finish_offset:
            return 100.0

        duration = planned_finish_offset - planned_start_offset
        if duration <= 0:
            return 100.0

        elapsed = reference_date_offset - planned_start_offset
        return round((elapsed / duration) * 100.0, 2)


def _determine_status(spi: float, cpi: Optional[float]) -> str:
    """Determine project health status from SPI and CPI.

    Args:
        spi: Schedule Performance Index.
        cpi: Cost Performance Index (may be None if AC = 0).

    Returns:
        Status string: "on_track", "at_risk", or "critical".
    """
    effective_cpi = cpi if cpi is not None else 1.0

    if spi < 0.8 or effective_cpi < 0.75:
        return "critical"
    if spi < 0.95 or effective_cpi < 0.90:
        return "at_risk"
    return "on_track"
