"""Unit tests for TaskService WBS code generation logic (pure, no DB).

These tests verify the WBS code generation algorithm in isolation,
plus full V3 EVM calculator compliance per master-guidelines §6.2.
"""

from __future__ import annotations

import pytest


# ── WBS Code logic tests (pure functions) ────────────────────────────────────

def generate_wbs_code(phase_wbs: str, sibling_count: int, parent_wbs: str | None = None) -> str:
    """Pure WBS code generation logic extracted from TaskService."""
    if parent_wbs is None:
        phase_num = phase_wbs.split(".")[0]
        return f"{phase_num}.{sibling_count + 1}"
    return f"{parent_wbs}.{sibling_count + 1}"


class TestWBSCodeGeneration:
    def test_first_task_in_phase(self) -> None:
        """First task in a phase should get code like '1.1'."""
        code = generate_wbs_code(phase_wbs="1.0", sibling_count=0)
        assert code == "1.1"

    def test_second_task_in_phase(self) -> None:
        """Second task in a phase should get code like '1.2'."""
        code = generate_wbs_code(phase_wbs="1.0", sibling_count=1)
        assert code == "1.2"

    def test_task_in_second_phase(self) -> None:
        """First task in second phase should get '2.1'."""
        code = generate_wbs_code(phase_wbs="2.0", sibling_count=0)
        assert code == "2.1"

    def test_sub_task_wbs_code(self) -> None:
        """First sub-task of '1.1' should get '1.1.1'."""
        code = generate_wbs_code(phase_wbs="1.0", sibling_count=0, parent_wbs="1.1")
        assert code == "1.1.1"

    def test_second_sub_task_wbs_code(self) -> None:
        """Second sub-task of '1.2' should get '1.2.2'."""
        code = generate_wbs_code(phase_wbs="1.0", sibling_count=1, parent_wbs="1.2")
        assert code == "1.2.2"

    def test_deep_nested_wbs_code(self) -> None:
        """Deep nested sub-task should generate correct 4-level code."""
        code = generate_wbs_code(phase_wbs="3.0", sibling_count=0, parent_wbs="3.2.1")
        assert code == "3.2.1.1"


# ── EVM V3 Enhanced calculation tests ────────────────────────────────────────

from app.domain.services.evm_calculator import EVMCalculator


class TestEVMCalculator:
    """Tests for the V3 enhanced EVM calculator per master-guidelines §6.2."""

    def test_on_track_project(self) -> None:
        """Perfectly on-track project should have SPI=1.0, CPI=1.0."""
        m = EVMCalculator.calculate(pv=100, ev=100, ac=100, bac=1000)
        assert m.spi == 1.0
        assert m.cpi == 1.0
        assert m.sv == 0.0
        assert m.cv == 0.0
        assert m.status == "on_track"

    def test_behind_schedule(self) -> None:
        """SPI < 0.95 should flag 'at_risk' per V3 thresholds."""
        m = EVMCalculator.calculate(pv=100, ev=85, ac=100, bac=1000)
        assert m.spi < 0.95
        assert m.sv == -15.0  # EV - PV
        assert m.status == "at_risk"

    def test_critical_project(self) -> None:
        """SPI < 0.8 should flag 'critical'."""
        m = EVMCalculator.calculate(pv=100, ev=70, ac=110, bac=1000)
        assert m.spi < 0.8
        assert m.status == "critical"

    def test_zero_pv_guard(self) -> None:
        """Zero PV should not raise; SPI defaults to 1.0."""
        m = EVMCalculator.calculate(pv=0, ev=0, ac=0, bac=500)
        assert m.spi == 1.0
        assert m.cpi is None  # AC = 0 → CPI is None per spec
        assert m.bac == 500

    def test_ac_zero_returns_none_cpi(self) -> None:
        """AC = 0 should return CPI = None (not 1.0) per spec §6.2."""
        m = EVMCalculator.calculate(pv=100, ev=50, ac=0, bac=1000)
        assert m.cpi is None  # Not 1.0 — avoids false reassurance
        assert m.eac == 1000  # Falls back to BAC when CPI unavailable

    def test_eac_v3_enhanced_formula(self) -> None:
        """EAC must use V3 formula: AC + (BAC - EV) / (SPI × CPI).

        Example: PV=100, EV=80, AC=100, BAC=1000
        SPI = 80/100 = 0.8
        CPI = 80/100 = 0.8
        EAC = 100 + (1000 - 80) / (0.8 × 0.8) = 100 + 920/0.64 = 100 + 1437.5 = 1537.5
        """
        m = EVMCalculator.calculate(pv=100, ev=80, ac=100, bac=1000)
        assert m.spi == 0.8
        assert m.cpi == 0.8
        expected_eac = 100 + (1000 - 80) / (0.8 * 0.8)
        assert m.eac == round(expected_eac, 2)
        assert m.eac > 1000  # Over budget projection

    def test_vac_calculation(self) -> None:
        """VAC = BAC - EAC. Negative when over budget."""
        m = EVMCalculator.calculate(pv=100, ev=100, ac=125, bac=1000)
        assert m.vac < 0  # Negative = projected overrun

    def test_vac_positive_under_budget(self) -> None:
        """VAC > 0 when project is under budget."""
        m = EVMCalculator.calculate(pv=100, ev=100, ac=80, bac=1000)
        assert m.vac > 0

    def test_sv_cv_computation(self) -> None:
        """SV = EV - PV, CV = EV - AC must be computed."""
        m = EVMCalculator.calculate(pv=200, ev=150, ac=180, bac=1000)
        assert m.sv == -50.0   # 150 - 200
        assert m.cv == -30.0   # 150 - 180

    def test_tcpi_computation(self) -> None:
        """TCPI = (BAC - EV) / (BAC - AC) per §6.2."""
        m = EVMCalculator.calculate(pv=100, ev=100, ac=100, bac=1000)
        # TCPI = (1000 - 100) / (1000 - 100) = 1.0
        assert m.tcpi == 1.0

    def test_tcpi_when_over_budget(self) -> None:
        """TCPI > 1 when project is currently over budget."""
        m = EVMCalculator.calculate(pv=500, ev=400, ac=500, bac=1000)
        # TCPI = (1000 - 400) / (1000 - 500) = 600/500 = 1.2
        assert m.tcpi == 1.2

    def test_tcpi_none_when_bac_equals_ac(self) -> None:
        """TCPI should be None when BAC = AC (denominator = 0)."""
        m = EVMCalculator.calculate(pv=500, ev=500, ac=1000, bac=1000)
        assert m.tcpi is None

    def test_planned_percent_interpolation(self) -> None:
        """Test linear interpolation of planned percent per §6.2."""
        # Before task start
        pct = EVMCalculator.interpolate_planned_percent(5, 10, 20)
        assert pct == 0.0

        # At task midpoint
        pct = EVMCalculator.interpolate_planned_percent(15, 10, 20)
        assert pct == 50.0

        # After task finish
        pct = EVMCalculator.interpolate_planned_percent(25, 10, 20)
        assert pct == 100.0

    def test_status_thresholds_per_v3_spec(self) -> None:
        """Verify V3 thresholds: SPI < 0.95 = at_risk, SPI < 0.8 = critical."""
        # On track: SPI >= 0.95, CPI >= 0.90
        m = EVMCalculator.calculate(pv=100, ev=96, ac=100, bac=1000)
        assert m.status == "on_track"

        # At risk: SPI < 0.95
        m = EVMCalculator.calculate(pv=100, ev=94, ac=100, bac=1000)
        assert m.status == "at_risk"

        # Critical: SPI < 0.8
        m = EVMCalculator.calculate(pv=100, ev=79, ac=100, bac=1000)
        assert m.status == "critical"
