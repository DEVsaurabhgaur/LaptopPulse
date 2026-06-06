"""
tests/test_health_score.py
---------------------------
Unit tests for core/health_score.py.
All tests run on any OS (no Windows-only imports, no live sensors).
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

# Make core importable without installing
sys.path.insert(0, str(Path(__file__).parent.parent))


# ── Minimal stubs so health_score can import without config ──────────────────

class _MockSeverity(Enum):
    IMMEDIATE = "IMMEDIATE"
    URGENT    = "URGENT"
    WARN      = "WARN"
    INFO      = "INFO"

@dataclass
class _MockAlert:
    rule_id:  str
    severity: _MockSeverity
    title:    str = "Test alert"


# Patch cfg import used inside health_score
import types, unittest.mock as mock
_fake_cfg   = types.SimpleNamespace(raw={})
_fake_mod   = types.ModuleType("config.settings")
_fake_mod.cfg = _fake_cfg
sys.modules.setdefault("config",          types.ModuleType("config"))
sys.modules["config.settings"] = _fake_mod

from core import health_score as hs   # noqa: E402  — import after stub


# ── Helpers ──────────────────────────────────────────────────────────────────

def _alert(sev: str) -> _MockAlert:
    return _MockAlert(rule_id="TEST", severity=_MockSeverity(sev))


def _metrics(**kwargs) -> dict:
    base = dict(
        cpu_temp=55.0,
        gpu_temp=50.0,
        fan_rpm=1400,
        battery_percent=85.0,
        battery_health_pct=90.0,
        is_throttling=False,
    )
    base.update(kwargs)
    return base


# ── Tests ────────────────────────────────────────────────────────────────────

class TestHealthScoreBands:
    """Score falls in the correct named band."""

    def test_perfect_laptop_scores_100(self):
        result = hs.compute(_metrics(), alerts=[])
        assert result.score == 100
        assert result.band == "Healthy"
        assert result.band_color == "green"

    def test_warm_cpu_still_healthy(self):
        result = hs.compute(_metrics(cpu_temp=68.0), alerts=[])
        assert result.score >= 85
        assert result.band == "Healthy"

    def test_hot_cpu_enters_monitor_band(self):
        result = hs.compute(_metrics(cpu_temp=83.0), alerts=[])
        assert result.score < 85
        assert result.band in ("Monitor", "Service Soon")

    def test_critical_cpu_drops_score_severely(self):
        result = hs.compute(_metrics(cpu_temp=92.0), alerts=[])
        assert result.score < 65

    def test_dead_fan_zeroes_fan_component(self):
        result = hs.compute(_metrics(fan_rpm=50), alerts=[])
        fan_pts = result.factors["fan_rpm"]["points"]
        assert fan_pts == 0

    def test_throttling_zeroes_throttle_component(self):
        result = hs.compute(_metrics(is_throttling=True), alerts=[])
        thr_pts = result.factors["throttle"]["points"]
        assert thr_pts == 0

    def test_low_battery_health_reduces_battery_component(self):
        healthy_result  = hs.compute(_metrics(battery_health_pct=95), alerts=[])
        degraded_result = hs.compute(_metrics(battery_health_pct=45), alerts=[])
        assert degraded_result.factors["battery"]["points"] < \
               healthy_result.factors["battery"]["points"]

    def test_score_never_exceeds_100(self):
        result = hs.compute(_metrics(cpu_temp=30.0, fan_rpm=3000), alerts=[])
        assert result.score <= 100

    def test_score_never_below_zero(self):
        alerts = [_alert("IMMEDIATE")] * 10
        result = hs.compute(_metrics(cpu_temp=95.0, fan_rpm=0, is_throttling=True), alerts=alerts)
        assert result.score >= 0


class TestAlertPenalties:
    """Alert penalties reduce score correctly."""

    def test_immediate_alert_penalty(self):
        no_alert   = hs.compute(_metrics(), alerts=[])
        with_alert = hs.compute(_metrics(), alerts=[_alert("IMMEDIATE")])
        assert with_alert.score == no_alert.score - 20

    def test_urgent_alert_penalty(self):
        no_alert   = hs.compute(_metrics(), alerts=[])
        with_alert = hs.compute(_metrics(), alerts=[_alert("URGENT")])
        assert with_alert.score == no_alert.score - 10

    def test_warn_alert_penalty(self):
        no_alert   = hs.compute(_metrics(), alerts=[])
        with_alert = hs.compute(_metrics(), alerts=[_alert("WARN")])
        assert with_alert.score == no_alert.score - 5

    def test_info_alert_no_penalty(self):
        no_alert   = hs.compute(_metrics(), alerts=[])
        with_alert = hs.compute(_metrics(), alerts=[_alert("INFO")])
        assert with_alert.score == no_alert.score

    def test_multiple_alerts_stack(self):
        no_alert   = hs.compute(_metrics(), alerts=[])
        alerts     = [_alert("IMMEDIATE"), _alert("WARN")]
        with_alert = hs.compute(_metrics(), alerts=alerts)
        assert with_alert.score == no_alert.score - 25

    def test_penalty_reasons_populated(self):
        result = hs.compute(_metrics(), alerts=[_alert("URGENT")])
        assert len(result.penalties) == 1
        assert "-10" in result.penalties[0]


class TestNullSensorHandling:
    """None sensor values must not crash and must give neutral scores."""

    def test_none_cpu_temp_does_not_crash(self):
        result = hs.compute(_metrics(cpu_temp=None), alerts=[])
        assert isinstance(result.score, int)

    def test_none_fan_rpm_does_not_crash(self):
        result = hs.compute(_metrics(fan_rpm=None), alerts=[])
        assert isinstance(result.score, int)

    def test_none_battery_does_not_crash(self):
        result = hs.compute(_metrics(battery_health_pct=None), alerts=[])
        assert isinstance(result.score, int)

    def test_all_none_still_returns_valid_score(self):
        result = hs.compute(
            dict(cpu_temp=None, gpu_temp=None, fan_rpm=None,
                 battery_percent=None, battery_health_pct=None,
                 is_throttling=False),
            alerts=[],
        )
        assert 0 <= result.score <= 100

    def test_none_sensors_do_not_give_zero_score(self):
        """Unknown sensors should not be punished as if they're broken."""
        result = hs.compute(_metrics(cpu_temp=None, fan_rpm=None), alerts=[])
        assert result.score > 50


class TestFactorStructure:
    """HealthScore.factors dict has the right shape."""

    def test_all_four_factors_present(self):
        result = hs.compute(_metrics(), alerts=[])
        for key in ("cpu_temp", "fan_rpm", "battery", "throttle"):
            assert key in result.factors

    def test_each_factor_has_required_keys(self):
        result = hs.compute(_metrics(), alerts=[])
        for v in result.factors.values():
            assert "points" in v
            assert "max"    in v
            assert "detail" in v

    def test_factor_points_do_not_exceed_max(self):
        result = hs.compute(_metrics(), alerts=[])
        for v in result.factors.values():
            assert v["points"] <= v["max"]

    def test_factors_sum_equals_score_before_penalty(self):
        result = hs.compute(_metrics(), alerts=[])
        total = sum(v["points"] for v in result.factors.values())
        assert result.score == total   # no alerts → no penalty


# ── pytest runner ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
