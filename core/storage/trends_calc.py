"""
core/storage/trends_calc.py
----------------------------
Computes rolling averages (30/45/60/90 day) from JSONL logs.
Results cached in trends.json — updated once per day by the watcher.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from config.settings import get_app_dir
from core.storage.logger import read_days

logger = logging.getLogger(__name__)


def _trends_path() -> Path:
    return get_app_dir() / "trends.json"


def _avg(values: list) -> float | None:
    valid = [v for v in values if v is not None]
    return round(sum(valid) / len(valid), 2) if valid else None


def compute_trends() -> dict:
    """
    Compute all rolling averages and save to trends.json.
    Called once daily by the watcher loop.
    """
    r30  = read_days(30)
    r45  = read_days(45)
    r60  = read_days(60)

    def extract(readings, key):
        return [r.get(key) for r in readings if r.get(key) is not None]

    idle_30 = [r for r in r30 if r.get("cpu_load", 100) < 15]

    trends = {
        "updated_at": datetime.now().isoformat(),
        "30d": {
            "cpu_temp_avg":      _avg(extract(r30, "cpu_temp")),
            "cpu_idle_avg":      _avg([r.get("cpu_temp") for r in idle_30]),
            "gpu_temp_avg":      _avg(extract(r30, "gpu_temp")),
            "fan_rpm_avg":       _avg(extract(r30, "fan_rpm")),
            "cpu_load_avg":      _avg(extract(r30, "cpu_load")),
            "throttle_count":    sum(1 for r in r30 if r.get("is_throttling")),
            "reading_count":     len(r30),
        },
        "45d": {
            "cpu_temp_avg":      _avg(extract(r45, "cpu_temp")),
            "reading_count":     len(r45),
        },
        "60d": {
            "fan_rpm_avg":       _avg(extract(r60, "fan_rpm")),
            "reading_count":     len(r60),
        },
    }

    try:
        _trends_path().write_text(json.dumps(trends, indent=2), encoding="utf-8")
        logger.info("Trends updated — 30d cpu_idle_avg: %s°C",
                    trends["30d"]["cpu_idle_avg"])
    except Exception as e:
        logger.error("Failed to save trends: %s", e)

    return trends


def load_trends() -> dict | None:
    path = _trends_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error("Failed to load trends: %s", e)
        return None
