"""
core/storage/baseline.py
-------------------------
Captures the 7-day baseline when LaptopPulse is first installed.
Baseline = the "healthy" reference point for all future trend comparisons.
Stored in baseline.json — never deleted, only updated manually.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import get_app_dir, cfg
from core.storage.logger import read_days

logger = logging.getLogger(__name__)


def _baseline_path() -> Path:
    return get_app_dir() / "baseline.json"


def baseline_exists() -> bool:
    return _baseline_path().exists()


def load_baseline() -> dict | None:
    path = _baseline_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Failed to load baseline: %s", e)
        return None


def _avg(values: list) -> float | None:
    valid = [v for v in values if v is not None]
    return round(sum(valid) / len(valid), 2) if valid else None


def compute_and_save_baseline() -> dict | None:
    """
    Compute baseline from first 7 days of logs and save to baseline.json.
    Called once after the first week of monitoring.
    Returns the computed baseline dict, or None if insufficient data.
    """
    readings = read_days(days=cfg.monitoring["baseline_days"])
    if len(readings) < 500:
        logger.warning("Not enough data for baseline (%d readings). Need ~500+.", len(readings))
        return None

    idle_limit = cfg.trend_detection["idle_cpu_load_max"]
    idle_readings = [r for r in readings if r.get("cpu_load", 100) < idle_limit]

    baseline = {
        "created_at":      datetime.now().isoformat(),
        "reading_count":   len(readings),
        "cpu_idle_avg":    _avg([r.get("cpu_temp") for r in idle_readings]),
        "cpu_load_avg":    _avg([r.get("cpu_temp") for r in readings]),
        "fan_rpm_avg":     _avg([r.get("fan_rpm") for r in readings if r.get("fan_rpm")]),
        "gpu_temp_avg":    _avg([r.get("gpu_temp") for r in readings if r.get("gpu_temp")]),
        "battery_health":  _avg([r.get("battery_health_pct") for r in readings if r.get("battery_health_pct")]),
    }

    try:
        _baseline_path().write_text(json.dumps(baseline, indent=2), encoding="utf-8")
        logger.info("Baseline saved: cpu_idle_avg=%.1f°C, fan_rpm_avg=%.0f",
                    baseline["cpu_idle_avg"] or 0, baseline["fan_rpm_avg"] or 0)
    except Exception as e:
        logger.error("Failed to save baseline: %s", e)
        return None

    return baseline
