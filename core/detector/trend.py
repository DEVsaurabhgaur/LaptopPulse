"""
core/detector/trend.py
-----------------------
Trend-based anomaly detection — the core competitive advantage of LaptopPulse.

A single temperature reading is meaningless. An 8°C rise at idle over 30 days
is a near-certain sign of thermal paste degradation — regardless of absolute value.

This module compares current rolling averages against the initial 7-day baseline
captured when the user first installed LaptopPulse.
"""

import logging
from typing import Optional

from config.settings import cfg
from core.detector.rules import Alert, RuleType, TREND_RULES

logger = logging.getLogger(__name__)

_td = cfg.trend_detection   # shorthand


# ── Helper ────────────────────────────────────────────────────────────────────

def _avg(values: list[float]) -> Optional[float]:
    """Safe average — returns None for empty list."""
    valid = [v for v in values if v is not None]
    return sum(valid) / len(valid) if valid else None


def _idle_readings(readings: list[dict]) -> list[float]:
    """Filter to idle readings only: cpu_load < 15%."""
    return [
        r["cpu_temp"] for r in readings
        if r.get("cpu_load") is not None
        and r.get("cpu_temp") is not None
        and r["cpu_load"] < _td["idle_cpu_load_max"]
    ]


# ── Trend Checks ──────────────────────────────────────────────────────────────

def check_idle_temp_trend(
    readings_30d: list[dict],
    baseline: dict,
) -> Optional[Alert]:
    """
    Compare current 30-day idle CPU temp average to baseline idle average.
    Fires WARN at +8°C delta, URGENT at +12°C delta.
    """
    baseline_idle_avg = baseline.get("cpu_idle_avg")
    if baseline_idle_avg is None:
        return None

    idle_temps = _idle_readings(readings_30d)
    if len(idle_temps) < 100:   # Need at least ~2 days of idle readings
        logger.debug("Not enough idle readings for trend analysis (%d)", len(idle_temps))
        return None

    current_idle_avg = _avg(idle_temps)
    if current_idle_avg is None:
        return None

    delta = current_idle_avg - baseline_idle_avg
    logger.debug(
        "Idle temp trend: baseline=%.1f°C, current=%.1f°C, delta=+%.1f°C",
        baseline_idle_avg, current_idle_avg, delta,
    )

    critical_threshold = _td["idle_temp_rise_critical"]
    warn_threshold     = _td["idle_temp_rise_warn"]

    if delta >= critical_threshold:
        r = TREND_RULES["IDLE_TEMP_RISE_CRITICAL"]
        return Alert(
            rule_id="IDLE_TEMP_RISE_CRITICAL", rule_type=RuleType.TREND,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=round(delta, 1)),
            value=delta, threshold=critical_threshold,
            extra={"baseline_avg": baseline_idle_avg, "current_avg": current_idle_avg},
        )
    if delta >= warn_threshold:
        r = TREND_RULES["IDLE_TEMP_RISE_WARN"]
        return Alert(
            rule_id="IDLE_TEMP_RISE_WARN", rule_type=RuleType.TREND,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=round(delta, 1)),
            value=delta, threshold=warn_threshold,
            extra={"baseline_avg": baseline_idle_avg, "current_avg": current_idle_avg},
        )
    return None


def check_fan_rpm_trend(
    readings_60d: list[dict],
    baseline: dict,
) -> Optional[Alert]:
    """
    Detect declining fan RPM over 60 days.
    Fires WARN if RPM dropped more than 20% from baseline.
    """
    baseline_fan_avg = baseline.get("fan_rpm_avg")
    if baseline_fan_avg is None or baseline_fan_avg == 0:
        return None

    fan_rpms = [
        r["fan_rpm"] for r in readings_60d
        if r.get("fan_rpm") is not None and r["fan_rpm"] > 0
    ]
    if len(fan_rpms) < 100:
        return None

    current_fan_avg = _avg(fan_rpms)
    if current_fan_avg is None:
        return None

    decline_pct = (baseline_fan_avg - current_fan_avg) / baseline_fan_avg * 100
    threshold   = _td["fan_rpm_decline_warn_percent"]

    logger.debug(
        "Fan trend: baseline=%.0f RPM, current=%.0f RPM, decline=%.1f%%",
        baseline_fan_avg, current_fan_avg, decline_pct,
    )

    if decline_pct >= threshold:
        r = TREND_RULES["FAN_RPM_DECLINE"]
        return Alert(
            rule_id="FAN_RPM_DECLINE", rule_type=RuleType.TREND,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=round(decline_pct, 1)),
            value=decline_pct, threshold=threshold,
            extra={"baseline_rpm": baseline_fan_avg, "current_rpm": current_fan_avg},
        )
    return None


def check_temp_trend_45d(
    readings_45d: list[dict],
    baseline: dict,
) -> Optional[Alert]:
    """
    45-day temperature trend — catches combined dust + paste failure.
    Fires URGENT at +12°C delta (using all readings, not just idle).
    """
    baseline_avg = baseline.get("cpu_load_avg")
    if baseline_avg is None:
        return None

    all_temps = [
        r["cpu_temp"] for r in readings_45d
        if r.get("cpu_temp") is not None
    ]
    if len(all_temps) < 200:
        return None

    current_avg = _avg(all_temps)
    if current_avg is None:
        return None

    delta     = current_avg - baseline_avg
    threshold = _td["idle_temp_rise_critical"]

    if delta >= threshold:
        r = TREND_RULES["TEMP_TREND_URGENT"]
        return Alert(
            rule_id="TEMP_TREND_URGENT", rule_type=RuleType.TREND,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=round(delta, 1)),
            value=delta, threshold=threshold,
            extra={"baseline_avg": baseline_avg, "current_avg": current_avg},
        )
    return None


def run_all_trend_checks(
    readings_30d: list[dict],
    readings_45d: list[dict],
    readings_60d: list[dict],
    baseline: dict,
) -> list[Alert]:
    """
    Run all trend checks. Returns list of triggered trend alerts.
    """
    alerts = []
    checks = [
        check_idle_temp_trend(readings_30d, baseline),
        check_fan_rpm_trend(readings_60d, baseline),
        check_temp_trend_45d(readings_45d, baseline),
    ]
    for alert in checks:
        if alert is not None:
            logger.warning(
                "TREND ALERT [%s] %s — delta=%.1f",
                alert.rule_id, alert.title, alert.value,
            )
            alerts.append(alert)
    return alerts
