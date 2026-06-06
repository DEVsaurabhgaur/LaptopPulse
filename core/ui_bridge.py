"""
core/ui_bridge.py
------------------
Bridge between the monitoring daemon and the UI layer (tray + dashboard).
Decoupled so the daemon can run headless as a Windows Service.

Two entry points:
  tick_update(metrics, alerts, health)  — called every 60-second daemon tick
  notify_alert(alert, report_path)      — called when a report is generated
"""

import logging
from pathlib import Path

from core.detector.rules import Alert, Severity

logger = logging.getLogger(__name__)

_severity_to_state = {
    Severity.IMMEDIATE: "red",
    Severity.URGENT:    "red",
    Severity.WARN:      "yellow",
    Severity.INFO:      "yellow",
}


# --- Tick update (every 60 s) -------------------------------------------------

def tick_update(metrics: dict, alerts: list, health) -> None:
    """
    Called once per daemon tick to keep the dashboard and tray in sync.

    Actions:
      1. Persist health state to SQLite (dashboard API reads this).
      2. Update tray icon color if the highest-severity alert changed.
      3. Record each new alert to the alerts table.

    health: HealthScore from core.health_score.compute()
    """
    # 1. SQLite dashboard state
    try:
        from core.storage import sqlite_store
        sqlite_store.update_dashboard_state(metrics, health, alerts)
    except Exception as exc:
        logger.debug("tick_update: sqlite write failed: %s", exc)

    # 2. Record new alerts (record_event handles cooldown tracking)
    for alert in alerts:
        try:
            from core.storage import sqlite_store
            sqlite_store.record_alert(alert)
            sev = alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity)
            sqlite_store.record_event(alert.rule_id, sev)
        except Exception as exc:
            logger.debug("tick_update: record_alert failed for %s: %s", alert.rule_id, exc)

    # 3. Update tray color to match highest severity
    if alerts:
        top = max(alerts, key=lambda a: list(Severity).index(a.severity))
        tray_state = _severity_to_state.get(top.severity, "yellow")
    else:
        tray_state = "green" if health.score >= 85 else "yellow"

    try:
        from ui.tray import set_tray_state
        tooltip = f"LaptopPulse — {health.band} ({health.score}/100)"
        set_tray_state(tray_state, tooltip=tooltip)
    except Exception as exc:
        logger.debug("tick_update: tray update failed: %s", exc)


# --- Alert notification (on report generation) --------------------------------

def notify_alert(alert: Alert, report_path: Path) -> None:
    """
    Called when an anomaly report has been generated.

    Actions:
      1. Push OS toast notification via tray icon.
      2. Record report path in SQLite reports table.
      3. Optionally open the dashboard browser if auto_open_on_alert is set.
    """
    # 1. OS toast via tray
    try:
        from ui.tray import set_tray_state, show_notification
        state = _severity_to_state.get(alert.severity, "yellow")
        set_tray_state(state, tooltip=f"LaptopPulse — {alert.title}")
        show_notification(
            title=f"LaptopPulse: {alert.title}",
            message="Click to view your health report.",
        )
        logger.info("Tray notified: %s (%s)", alert.rule_id, state)
    except Exception as exc:
        logger.debug("notify_alert: tray notification failed: %s", exc)

    # 2. Record report in SQLite
    try:
        from core.storage import sqlite_store
        sqlite_store.record_report(str(report_path), alert.rule_id)
    except Exception as exc:
        logger.debug("notify_alert: record_report failed: %s", exc)

    # 3. Auto-open dashboard if configured
    try:
        from config.settings import cfg
        if cfg.raw.get("dashboard", {}).get("auto_open_on_alert", False):
            from ui.dashboard_server import open_browser
            open_browser()
    except Exception as exc:
        logger.debug("notify_alert: auto-open dashboard failed: %s", exc)
