"""
tests/test_detector.py
-----------------------
Unit tests for threshold and trend detection logic.
Uses mock data — no Windows sensors or hardware needed.
Run: pytest tests/ -v
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from core.detector.rules import Severity, RuleType
from core.detector.threshold import (
    check_cpu_temp, check_gpu_temp, check_fan_rpm,
    check_throttle, check_battery_health, run_all_threshold_checks,
)
from core.detector.trend import (
    check_idle_temp_trend, check_fan_rpm_trend,
)


# ── Threshold Tests ───────────────────────────────────────────────────────────

class TestCpuTempThreshold:
    def test_no_alert_below_warning(self):
        assert check_cpu_temp(75.0) is None

    def test_warning_at_80(self):
        alert = check_cpu_temp(80.0)
        assert alert is not None
        assert alert.rule_id == "CPU_WARNING"
        assert alert.severity == Severity.URGENT

    def test_critical_at_91(self):
        alert = check_cpu_temp(91.0)
        assert alert is not None
        assert alert.rule_id == "CPU_CRITICAL"
        assert alert.severity == Severity.IMMEDIATE

    def test_none_returns_none(self):
        assert check_cpu_temp(None) is None

    def test_exactly_at_threshold(self):
        alert = check_cpu_temp(90.0)
        assert alert is not None
        assert alert.rule_id == "CPU_CRITICAL"


class TestGpuTempThreshold:
    def test_no_alert_normal(self):
        assert check_gpu_temp(70.0) is None

    def test_critical_at_88(self):
        alert = check_gpu_temp(88.0)
        assert alert.rule_id == "GPU_CRITICAL"
        assert alert.severity == Severity.IMMEDIATE

    def test_none_safe(self):
        assert check_gpu_temp(None) is None


class TestFanRpmThreshold:
    def test_no_check_at_low_load(self):
        # Fan slow but CPU load < 30% — no alert
        assert check_fan_rpm(400, cpu_load=20.0) is None

    def test_fan_dead_under_load(self):
        alert = check_fan_rpm(100, cpu_load=70.0)
        assert alert.rule_id == "FAN_DEAD"
        assert alert.severity == Severity.IMMEDIATE

    def test_fan_slow_under_load(self):
        alert = check_fan_rpm(600, cpu_load=50.0)
        assert alert.rule_id == "FAN_SLOW"

    def test_healthy_fan(self):
        assert check_fan_rpm(2800, cpu_load=60.0) is None

    def test_none_fan_no_crash(self):
        assert check_fan_rpm(None, cpu_load=80.0) is None


class TestThrottleDetection:
    def test_not_throttling(self):
        assert check_throttle(False) is None

    def test_throttling_fires_alert(self):
        alert = check_throttle(True, clock_drop_pct=0.35)
        assert alert.rule_id == "CPU_THROTTLE"
        assert alert.severity == Severity.URGENT


class TestBatteryHealth:
    def test_healthy_battery(self):
        assert check_battery_health(85.0) is None

    def test_degraded_battery_warn(self):
        alert = check_battery_health(60.0)
        assert alert.rule_id == "BATTERY_CRITICAL"
        assert alert.severity == Severity.INFO

    def test_none_safe(self):
        assert check_battery_health(None) is None


class TestRunAllThresholdChecks:
    def test_healthy_metrics_no_alerts(self):
        metrics = {
            "cpu_temp": 65.0, "gpu_temp": 60.0, "fan_rpm": 2500,
            "cpu_load": 40.0, "is_throttling": False, "battery_health_pct": 90.0,
        }
        assert run_all_threshold_checks(metrics) == []

    def test_multiple_alerts_returned(self):
        metrics = {
            "cpu_temp": 92.0, "gpu_temp": 89.0, "fan_rpm": 150,
            "cpu_load": 80.0, "is_throttling": True, "battery_health_pct": 55.0,
        }
        alerts = run_all_threshold_checks(metrics)
        rule_ids = [a.rule_id for a in alerts]
        assert "CPU_CRITICAL" in rule_ids
        assert "GPU_CRITICAL" in rule_ids
        assert "FAN_DEAD"     in rule_ids


# ── Trend Tests ───────────────────────────────────────────────────────────────

def _make_readings(count: int, cpu_temp: float, cpu_load: float) -> list[dict]:
    base = datetime.now() - timedelta(days=30)
    return [
        {
            "ts":       (base + timedelta(minutes=i)).isoformat(),
            "cpu_temp": cpu_temp + (i % 3) * 0.1,
            "cpu_load": cpu_load,
            "fan_rpm":  2500,
        }
        for i in range(count)
    ]


class TestIdleTempTrend:
    def test_no_alert_normal_rise(self):
        baseline = {"cpu_idle_avg": 45.0}
        # Current avg = 50°C — delta = 5°C, below 8°C warning
        readings = _make_readings(500, cpu_temp=50.0, cpu_load=5.0)
        assert check_idle_temp_trend(readings, baseline) is None

    def test_warn_at_8c_rise(self):
        baseline = {"cpu_idle_avg": 45.0}
        readings = _make_readings(500, cpu_temp=53.5, cpu_load=5.0)
        alert = check_idle_temp_trend(readings, baseline)
        assert alert is not None
        assert alert.severity == Severity.WARN

    def test_critical_at_12c_rise(self):
        baseline = {"cpu_idle_avg": 45.0}
        readings = _make_readings(500, cpu_temp=57.5, cpu_load=5.0)
        alert = check_idle_temp_trend(readings, baseline)
        assert alert is not None
        assert alert.severity == Severity.URGENT

    def test_insufficient_readings_no_alert(self):
        baseline = {"cpu_idle_avg": 45.0}
        readings = _make_readings(50, cpu_temp=60.0, cpu_load=5.0)
        assert check_idle_temp_trend(readings, baseline) is None

    def test_missing_baseline_no_alert(self):
        readings = _make_readings(500, cpu_temp=60.0, cpu_load=5.0)
        assert check_idle_temp_trend(readings, {}) is None


class TestFanRpmTrend:
    def _make_fan_readings(self, count: int, fan_rpm: int):
        return [{"fan_rpm": fan_rpm + (i % 5)} for i in range(count)]

    def test_no_alert_stable_fan(self):
        baseline = {"fan_rpm_avg": 3000}
        readings = self._make_fan_readings(500, 2950)
        assert check_fan_rpm_trend(readings, baseline) is None

    def test_warn_at_20pct_decline(self):
        baseline = {"fan_rpm_avg": 3000}
        readings = self._make_fan_readings(500, 2350)  # ~21.7% decline
        alert = check_fan_rpm_trend(readings, baseline)
        assert alert is not None
        assert alert.rule_id == "FAN_RPM_DECLINE"

    def test_no_baseline_no_alert(self):
        readings = self._make_fan_readings(500, 2000)
        assert check_fan_rpm_trend(readings, {}) is None
