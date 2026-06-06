"""
core/watcher.py
----------------
The heart of LaptopPulse — the silent monitoring daemon.
Wakes every 60 seconds, reads all sensors, writes to log,
runs anomaly checks, computes health score, updates dashboard,
and triggers report generation if needed.
Target CPU overhead: < 0.3% at idle. Memory: < 30 MB after 24 h.
"""

import json
import logging
import platform
import time
from datetime import datetime, timedelta
from pathlib import Path

from config.settings import cfg, get_app_dir
from core.sensors.cpu        import read_cpu_metrics
from core.sensors.gpu_nvidia import read_gpu_metrics
from core.sensors.fan        import read_fan_metrics
from core.sensors.battery    import read_battery_metrics
from core.storage.logger     import write_reading, cleanup_old_logs
from core.storage.baseline   import baseline_exists, compute_and_save_baseline, load_baseline
from core.storage.trends_calc import compute_trends, load_trends
from core.detector.threshold import run_all_threshold_checks
from core.detector.trend     import run_all_trend_checks
from core.detector.rules     import Severity
from core.storage.logger     import read_days

logger = logging.getLogger(__name__)


# --- System info (collected once at startup) ----------------------------------

def _collect_system_info() -> dict:
    """Collect laptop model, CPU, GPU info. Cached to system_info.json."""
    info_path = get_app_dir() / "system_info.json"
    if info_path.exists():
        try:
            return json.loads(info_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    import subprocess
    info = {
        "collected_at": datetime.now().isoformat(),
        "os":    f"Windows {platform.version()}",
        "model": "Unknown",
        "cpu":   platform.processor() or "Unknown CPU",
        "gpu":   "Unknown",
        "age_months": "Unknown",
    }

    try:
        r = subprocess.run(
            ["wmic", "computersystem", "get", "Model"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        if len(lines) > 1:
            info["model"] = lines[1]
    except Exception:
        pass

    try:
        r = subprocess.run(
            ["wmic", "path", "Win32_VideoController", "get", "Name"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [l.strip() for l in r.stdout.splitlines() if l.strip()]
        if len(lines) > 1:
            info["gpu"] = lines[1]
    except Exception:
        pass

    # LHM is optional — ACPI WMI is the primary sensor method, no external software needed
    try:
        from core.sensors.lhm_bridge import is_lhm_available
        info["lhm_available"] = is_lhm_available()
        if info["lhm_available"]:
            logger.info("LibreHardwareMonitor WMI bridge: ACTIVE (optional enhancement)")
        else:
            logger.info("Running in standalone mode — Windows ACPI WMI sensors active.")
    except Exception:
        info["lhm_available"] = False

    try:
        info_path.write_text(json.dumps(info, indent=2), encoding="utf-8")
    except Exception as exc:
        logger.error("Failed to save system_info: %s", exc)

    return info


# --- Single metric collection tick -------------------------------------------

def collect_metrics(system_info: dict) -> dict:
    """Collect all sensor readings in one tick. Never raises."""
    cpu = read_cpu_metrics()
    gpu = read_gpu_metrics()
    fan = read_fan_metrics()
    bat = read_battery_metrics()

    return {
        "ts":               datetime.now().isoformat(),
        "cpu_temp":         cpu.temperature,
        "gpu_temp":         gpu.temperature if gpu.available else None,
        "fan_rpm":          fan.cpu_fan_rpm if fan.available else None,
        "cpu_load":         cpu.load_percent,
        "clock_mhz":        cpu.clock_mhz,
        "is_throttling":    cpu.is_throttling,
        "battery_percent":  bat.percent,
        "battery_plugged":  bat.is_plugged,
        "battery_health_pct": bat.health_percent,
    }


# --- Scheduling state ---------------------------------------------------------

_last_trend_update   = datetime.min
_last_cleanup        = datetime.min
_last_baseline_check = datetime.min


def _maybe_compute_baseline():
    global _last_baseline_check
    if (datetime.now() - _last_baseline_check).total_seconds() < 3600:
        return
    _last_baseline_check = datetime.now()
    if not baseline_exists():
        baseline = compute_and_save_baseline()
        if baseline:
            logger.info("Baseline computed and saved.")


def _maybe_update_trends() -> dict:
    global _last_trend_update
    if (datetime.now() - _last_trend_update).total_seconds() < 86400:
        return load_trends() or {}
    _last_trend_update = datetime.now()
    return compute_trends()


def _maybe_cleanup():
    global _last_cleanup
    if (datetime.now() - _last_cleanup).total_seconds() < 86400:
        return
    _last_cleanup = datetime.now()
    cleanup_old_logs()


# --- Main daemon loop ---------------------------------------------------------

def run_daemon():
    """
    Main entry point for the LaptopPulse monitoring daemon.
    Runs indefinitely. Registered as a Windows Service via service/.
    """
    logger.info("LaptopPulse daemon starting...")
    interval    = cfg.monitoring["interval_seconds"]
    system_info = _collect_system_info()
    logger.info(
        "System: %s | CPU: %s | GPU: %s",
        system_info["model"], system_info["cpu"], system_info["gpu"],
    )

    # Initialise SQLite store once at startup
    try:
        from core.storage import sqlite_store
        sqlite_store.init_db()
    except Exception as exc:
        logger.warning("SQLite init failed (dashboard will be unavailable): %s", exc)

    # Lazy imports — avoid Windows-only errors in CI
    try:
        from core.reporter.generator import generate_report
        from core.ui_bridge import notify_alert, tick_update
    except ImportError:
        generate_report = None
        notify_alert    = None
        tick_update     = None

    while True:
        tick_start = time.monotonic()

        try:
            # 1. Collect all sensor readings
            metrics = collect_metrics(system_info)
            write_reading(metrics)

            # 2. Threshold checks (every tick)
            alerts = run_all_threshold_checks(metrics)

            # 3. Trend checks (once per day with 30/45/60-day windows)
            trends   = _maybe_update_trends()
            baseline = load_baseline()
            if trends and baseline:
                r30 = read_days(30)
                r45 = read_days(45)
                r60 = read_days(60)
                alerts.extend(run_all_trend_checks(r30, r45, r60, baseline))

            # 4. Compute health score from current state
            try:
                from core import health_score as hs_module
                health = hs_module.compute(metrics, alerts)
            except Exception as exc:
                logger.debug("health_score.compute failed: %s", exc)
                health = _fallback_health()

            # 5. Update dashboard + tray every tick
            if tick_update:
                tick_update(metrics, alerts, health)

            # 6. Generate AI report for highest-severity alert (with cooldown)
            if alerts and generate_report:
                alerts.sort(
                    key=lambda a: list(Severity).index(a.severity)
                )
                top_alert = alerts[0]
                report_path = generate_report(top_alert, system_info, trends or {})
                if report_path and notify_alert:
                    notify_alert(top_alert, report_path)

            # 7. Daily housekeeping
            _maybe_compute_baseline()
            _maybe_cleanup()

        except Exception as exc:
            logger.error("Daemon tick error: %s", exc, exc_info=True)

        elapsed   = time.monotonic() - tick_start
        sleep_for = max(0, interval - elapsed)
        time.sleep(sleep_for)


# --- Fallback health (when health_score module unavailable) -------------------

class _FallbackHealth:
    score      = 100
    band       = "Healthy"
    band_color = "green"
    factors    = {}
    penalties  = []


def _fallback_health() -> _FallbackHealth:
    return _FallbackHealth()