"""
core/detector/threshold.py
---------------------------
Instant threshold detection — fires on a single reading.
No history needed. Checks every metric collection against configured limits.
"""

import logging
from typing import Optional

from config.settings import cfg
from core.detector.rules import Alert, RuleType, Severity, THRESHOLD_RULES

logger = logging.getLogger(__name__)

_t = cfg.thresholds   # shorthand


def check_cpu_temp(cpu_temp: Optional[float]) -> Optional[Alert]:
    if cpu_temp is None:
        return None
    if cpu_temp >= _t["cpu_temp_critical"]:
        r = THRESHOLD_RULES["CPU_CRITICAL"]
        return Alert(
            rule_id="CPU_CRITICAL", rule_type=RuleType.THRESHOLD,
            severity=r["severity"],
            title=r["title"],
            message=r["message"].format(value=cpu_temp, threshold=_t["cpu_temp_critical"]),
            value=cpu_temp, threshold=_t["cpu_temp_critical"],
        )
    if cpu_temp >= _t["cpu_temp_warning"]:
        r = THRESHOLD_RULES["CPU_WARNING"]
        return Alert(
            rule_id="CPU_WARNING", rule_type=RuleType.THRESHOLD,
            severity=r["severity"],
            title=r["title"],
            message=r["message"].format(value=cpu_temp, threshold=_t["cpu_temp_warning"]),
            value=cpu_temp, threshold=_t["cpu_temp_warning"],
        )
    return None


def check_gpu_temp(gpu_temp: Optional[float]) -> Optional[Alert]:
    if gpu_temp is None:
        return None
    if gpu_temp >= _t["gpu_temp_critical"]:
        r = THRESHOLD_RULES["GPU_CRITICAL"]
        return Alert(
            rule_id="GPU_CRITICAL", rule_type=RuleType.THRESHOLD,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=gpu_temp, threshold=_t["gpu_temp_critical"]),
            value=gpu_temp, threshold=_t["gpu_temp_critical"],
        )
    if gpu_temp >= _t["gpu_temp_warning"]:
        r = THRESHOLD_RULES["GPU_WARNING"]
        return Alert(
            rule_id="GPU_WARNING", rule_type=RuleType.THRESHOLD,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=gpu_temp, threshold=_t["gpu_temp_warning"]),
            value=gpu_temp, threshold=_t["gpu_temp_warning"],
        )
    return None


def check_fan_rpm(fan_rpm: Optional[int], cpu_load: float) -> Optional[Alert]:
    """Only check fan speed when laptop is under meaningful load (> 30%)."""
    if fan_rpm is None or cpu_load < 30:
        return None
    if fan_rpm < _t["fan_rpm_dead"]:
        r = THRESHOLD_RULES["FAN_DEAD"]
        return Alert(
            rule_id="FAN_DEAD", rule_type=RuleType.THRESHOLD,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=fan_rpm, threshold=_t["fan_rpm_dead"]),
            value=fan_rpm, threshold=_t["fan_rpm_dead"],
        )
    if fan_rpm < _t["fan_rpm_slow"]:
        r = THRESHOLD_RULES["FAN_SLOW"]
        return Alert(
            rule_id="FAN_SLOW", rule_type=RuleType.THRESHOLD,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=fan_rpm, threshold=_t["fan_rpm_slow"]),
            value=fan_rpm, threshold=_t["fan_rpm_slow"],
        )
    return None


def check_throttle(is_throttling: bool, clock_drop_pct: float = 0.0) -> Optional[Alert]:
    if not is_throttling:
        return None
    r = THRESHOLD_RULES["CPU_THROTTLE"]
    return Alert(
        rule_id="CPU_THROTTLE", rule_type=RuleType.THRESHOLD,
        severity=r["severity"], title=r["title"],
        message=r["message"].format(value=round(clock_drop_pct * 100), threshold=30),
        value=clock_drop_pct * 100, threshold=30,
    )


def check_battery_health(health_pct: Optional[float]) -> Optional[Alert]:
    if health_pct is None:
        return None
    limit = cfg.trend_detection["battery_health_warn_percent"]
    if health_pct < limit:
        r = THRESHOLD_RULES["BATTERY_CRITICAL"]
        return Alert(
            rule_id="BATTERY_CRITICAL", rule_type=RuleType.THRESHOLD,
            severity=r["severity"], title=r["title"],
            message=r["message"].format(value=round(health_pct, 1), threshold=limit),
            value=health_pct, threshold=limit,
        )
    return None


def run_all_threshold_checks(metrics: dict) -> list[Alert]:
    """
    Run all threshold checks on a single metrics snapshot.
    Returns list of triggered alerts (empty = all clear).
    """
    alerts = []
    checks = [
        check_cpu_temp(metrics.get("cpu_temp")),
        check_gpu_temp(metrics.get("gpu_temp")),
        check_fan_rpm(metrics.get("fan_rpm"), metrics.get("cpu_load", 0)),
        check_throttle(metrics.get("is_throttling", False)),
        check_battery_health(metrics.get("battery_health_pct")),
    ]
    for alert in checks:
        if alert is not None:
            logger.warning("ALERT [%s] %s — value=%.1f", alert.rule_id, alert.title, alert.value)
            alerts.append(alert)
    return alerts
