"""
core/storage/logger.py
-----------------------
Writes one JSON line per reading to a daily JSONL log file.
Format: YYYY-MM-DD.jsonl — one file per day, ~4KB/day (1440 readings × 60s).
Auto-deletes files older than 90 days to keep storage at ~10MB max.

Privacy: Only numeric hardware data is logged. No usernames, serials, or env vars.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import get_log_dir, cfg

logger = logging.getLogger(__name__)


# ── Privacy filter ────────────────────────────────────────────────────────────

_ALLOWED_KEYS = {
    "ts", "cpu_temp", "gpu_temp", "fan_rpm", "cpu_load",
    "battery_percent", "battery_plugged", "battery_health_pct",
    "is_throttling", "clock_mhz",
}


def _sanitise(metrics: dict) -> dict:
    """
    Strip any keys not in the allowed set.
    Ensures no identifiable information ever enters the logs.
    """
    return {k: v for k, v in metrics.items() if k in _ALLOWED_KEYS}


# ── Log writer ────────────────────────────────────────────────────────────────

def write_reading(metrics: dict) -> None:
    """
    Append a single sanitised metric reading to today's JSONL log.
    Creates the log file if it doesn't exist.
    Never raises — log write failure must not crash the daemon.
    """
    try:
        log_dir  = get_log_dir()
        filename = datetime.now().strftime("%Y-%m-%d") + ".jsonl"
        log_file = log_dir / filename
        safe     = _sanitise(metrics)

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(safe) + "\n")

    except Exception as e:
        logger.error("Failed to write log reading: %s", e)


# ── Log reader ────────────────────────────────────────────────────────────────

def read_days(days: int = 30) -> list[dict]:
    """
    Load readings from the last N days of log files.
    Returns a flat list of reading dicts, sorted by timestamp.
    """
    log_dir  = get_log_dir()
    cutoff   = datetime.now() - timedelta(days=days)
    readings = []

    for log_file in sorted(log_dir.glob("*.jsonl")):
        try:
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                continue
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            readings.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
        except ValueError:
            pass  # Skip files with non-date names
        except Exception as e:
            logger.error("Error reading log file %s: %s", log_file, e)

    readings.sort(key=lambda r: r.get("ts", ""))
    return readings


# ── Auto-cleanup ──────────────────────────────────────────────────────────────

def cleanup_old_logs() -> int:
    """
    Delete log files older than the configured retention period.
    Returns count of deleted files.
    Called once per day from the watcher.
    """
    log_dir     = get_log_dir()
    retain_days = cfg.monitoring["log_retention_days"]
    cutoff      = datetime.now() - timedelta(days=retain_days)
    deleted     = 0

    for log_file in log_dir.glob("*.jsonl"):
        try:
            file_date = datetime.strptime(log_file.stem, "%Y-%m-%d")
            if file_date < cutoff:
                log_file.unlink()
                deleted += 1
                logger.info("Deleted old log: %s", log_file.name)
        except ValueError:
            pass
        except Exception as e:
            logger.error("Failed to delete %s: %s", log_file, e)

    if deleted:
        logger.info("Cleanup: deleted %d old log files", deleted)
    return deleted
