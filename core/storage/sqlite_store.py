"""
core/storage/sqlite_store.py
-----------------------------
SQLite persistence layer for events, alerts, report index, and the
single-row dashboard state that the Flask API reads.

The daily JSONL sensor logs remain unchanged (4 KB/day, direct append,
zero overhead). This module handles only:
  - alerts      — fired anomaly records, queryable by time / rule
  - events      — lightweight cooldown tracking (rule_id + timestamp)
  - reports     — index of generated HTML report files
  - dashboard_state — singleton row read by GET /api/status

Database location: {AppData}/LaptopPulse/laptoppulse.db
Configurable via defaults.json > sqlite_db.filename
"""

import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Module-level connection cache (one per thread via check_same_thread=False)
_db_path: Optional[Path] = None
_init_lock = threading.Lock()
_initialized = False


# --- Path resolution ----------------------------------------------------------

def _get_db_path() -> Path:
    global _db_path
    if _db_path is not None:
        return _db_path
    try:
        from config.settings import cfg, get_app_dir
        filename = cfg.raw.get("sqlite_db", {}).get("filename", "laptoppulse.db")
        _db_path = get_app_dir() / filename
    except Exception:
        # Fallback for tests / environments without config
        _db_path = Path.home() / "AppData" / "LocalLow" / "LaptopPulse" / "laptoppulse.db"
    _db_path.parent.mkdir(parents=True, exist_ok=True)
    return _db_path


def _conn() -> sqlite3.Connection:
    """Open (or reuse) a connection to the database."""
    c = sqlite3.connect(str(_get_db_path()), check_same_thread=False)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")   # allows concurrent reads during writes
    c.execute("PRAGMA synchronous=NORMAL") # good durability, better throughput
    return c


# --- Schema -------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS alerts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id    TEXT    NOT NULL,
    severity   TEXT    NOT NULL,
    title      TEXT    NOT NULL,
    message    TEXT    NOT NULL,
    value      REAL,
    threshold  REAL,
    timestamp  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS events (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_id    TEXT    NOT NULL,
    severity   TEXT    NOT NULL,
    timestamp  TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS reports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    path         TEXT    NOT NULL,
    alert_rule   TEXT    NOT NULL,
    generated_at TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS dashboard_state (
    id              INTEGER PRIMARY KEY CHECK (id = 1),
    health_score    INTEGER DEFAULT 100,
    health_band     TEXT    DEFAULT 'Healthy',
    health_color    TEXT    DEFAULT 'green',
    cpu_temp        REAL,
    gpu_temp        REAL,
    fan_rpm         INTEGER,
    battery_pct     REAL,
    battery_health  REAL,
    is_throttling   INTEGER DEFAULT 0,
    alert_count     INTEGER DEFAULT 0,
    score_factors   TEXT,
    updated_at      TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_timestamp  ON alerts(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_rule       ON alerts(rule_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_rule_time  ON events(rule_id, timestamp);
"""


def init_db() -> None:
    """Create all tables and the singleton dashboard_state row. Idempotent."""
    global _initialized
    with _init_lock:
        if _initialized:
            return
        try:
            with _conn() as c:
                c.executescript(_SCHEMA)
                # Ensure exactly one dashboard_state row exists
                c.execute("""
                    INSERT OR IGNORE INTO dashboard_state
                        (id, health_score, health_band, health_color, updated_at)
                    VALUES (1, 100, 'Healthy', 'green', ?)
                """, (datetime.now().isoformat(),))
            _initialized = True
            logger.info("SQLite store initialised at %s", _get_db_path())
        except Exception as exc:
            logger.error("SQLite init failed: %s", exc)
            raise


# --- Writes -------------------------------------------------------------------

def record_alert(alert) -> None:
    """
    Persist an Alert (from core.detector.rules) to the alerts table.
    Prunes to max_alerts (default 1000) after insert.
    """
    try:
        sev = alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity)
        ts  = alert.timestamp.isoformat() if hasattr(alert.timestamp, "isoformat") else str(alert.timestamp)
        with _conn() as c:
            c.execute("""
                INSERT INTO alerts (rule_id, severity, title, message, value, threshold, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.rule_id, sev,
                alert.title, getattr(alert, "message", ""),
                getattr(alert, "value", None),
                getattr(alert, "threshold", None),
                ts,
            ))
            # Prune oldest if over limit
            try:
                from config.settings import cfg
                limit = cfg.raw.get("sqlite_db", {}).get("max_alerts", 1000)
            except Exception:
                limit = 1000
            c.execute("""
                DELETE FROM alerts WHERE id NOT IN (
                    SELECT id FROM alerts ORDER BY id DESC LIMIT ?
                )
            """, (limit,))
    except Exception as exc:
        logger.warning("record_alert failed: %s", exc)


def record_event(rule_id: str, severity: str) -> None:
    """
    Record a lightweight event for cooldown tracking.
    Only rule_id + severity + timestamp — no heavy payload.
    """
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO events (rule_id, severity, timestamp) VALUES (?, ?, ?)",
                (rule_id, severity, datetime.now().isoformat()),
            )
    except Exception as exc:
        logger.warning("record_event failed: %s", exc)


def record_report(path: str, alert_rule: str) -> None:
    """Add a generated report to the index."""
    try:
        with _conn() as c:
            c.execute(
                "INSERT INTO reports (path, alert_rule, generated_at) VALUES (?, ?, ?)",
                (path, alert_rule, datetime.now().isoformat()),
            )
    except Exception as exc:
        logger.warning("record_report failed: %s", exc)


def update_dashboard_state(metrics: dict, health, alerts: list) -> None:
    """
    Update the singleton dashboard_state row every watcher tick.
    Called by core.ui_bridge.tick_update() after every sensor read.

    health: HealthScore dataclass from core.health_score
    """
    try:
        import json
        factors_json = json.dumps(health.factors) if hasattr(health, "factors") else "{}"
        with _conn() as c:
            c.execute("""
                UPDATE dashboard_state SET
                    health_score   = ?,
                    health_band    = ?,
                    health_color   = ?,
                    cpu_temp       = ?,
                    gpu_temp       = ?,
                    fan_rpm        = ?,
                    battery_pct    = ?,
                    battery_health = ?,
                    is_throttling  = ?,
                    alert_count    = ?,
                    score_factors  = ?,
                    updated_at     = ?
                WHERE id = 1
            """, (
                health.score,
                health.band,
                health.band_color,
                metrics.get("cpu_temp"),
                metrics.get("gpu_temp"),
                metrics.get("fan_rpm"),
                metrics.get("battery_percent"),
                metrics.get("battery_health_pct"),
                int(bool(metrics.get("is_throttling", False))),
                len(alerts),
                factors_json,
                datetime.now().isoformat(),
            ))
    except Exception as exc:
        logger.warning("update_dashboard_state failed: %s", exc)


# --- Reads (used by dashboard_server) ----------------------------------------

def get_latest_status() -> dict:
    """Return the current dashboard state row as a plain dict."""
    try:
        with _conn() as c:
            row = c.execute("SELECT * FROM dashboard_state WHERE id = 1").fetchone()
            if row:
                import json
                d = dict(row)
                try:
                    d["score_factors"] = json.loads(d.get("score_factors") or "{}")
                except Exception:
                    d["score_factors"] = {}
                return d
    except Exception as exc:
        logger.warning("get_latest_status failed: %s", exc)
    return {}


def get_recent_alerts(limit: int = 50) -> list[dict]:
    """Most recent `limit` alerts, newest first."""
    try:
        with _conn() as c:
            rows = c.execute(
                "SELECT * FROM alerts ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.warning("get_recent_alerts failed: %s", exc)
        return []


def get_recent_reports(limit: int = 20) -> list[dict]:
    """Most recent `limit` report records, newest first."""
    try:
        with _conn() as c:
            rows = c.execute(
                "SELECT * FROM reports ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as exc:
        logger.warning("get_recent_reports failed: %s", exc)
        return []


def is_on_cooldown(rule_id: str, cooldown_hours: int) -> bool:
    """
    Return True if rule_id has fired within the last cooldown_hours.
    Used by generator.py to prevent report spam.
    """
    try:
        cutoff = (datetime.now() - timedelta(hours=cooldown_hours)).isoformat()
        with _conn() as c:
            row = c.execute("""
                SELECT 1 FROM events
                WHERE rule_id = ? AND timestamp > ?
                LIMIT 1
            """, (rule_id, cutoff)).fetchone()
            return row is not None
    except Exception as exc:
        logger.warning("is_on_cooldown failed: %s", exc)
        return False
