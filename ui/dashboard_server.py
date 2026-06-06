"""
ui/dashboard_server.py
-----------------------
Lightweight Flask API server for the local monitoring dashboard.
Runs on http://127.0.0.1:5747 in a background daemon thread.
Started automatically when the tray icon launches;
the tray "Open Dashboard" menu item calls open_browser().

Endpoints:
  GET /                          -> serves dashboard.html
  GET /api/status                -> current health + metrics (JSON)
  GET /api/alerts                -> last 50 alerts (JSON)
  GET /api/reports               -> report index (JSON)
  GET /api/report/<filename>     -> serve a specific HTML report file

The server never blocks the main daemon thread.
Port and host are configurable in defaults.json > dashboard.
"""

import logging
import os
import threading
import webbrowser
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Runtime state
_thread:   Optional[threading.Thread] = None
_started:  bool = False
_port:     int  = 5747
_host:     str  = "127.0.0.1"

_DASHBOARD_HTML = Path(__file__).parent / "dashboard.html"


# --- Flask app factory --------------------------------------------------------

def _make_app():
    from flask import Flask, jsonify, send_file, abort

    app = Flask("LaptopPulseDashboard")

    # Silence werkzeug request log in production
    logging.getLogger("werkzeug").setLevel(logging.ERROR)

    @app.route("/")
    def index():
        if _DASHBOARD_HTML.exists():
            return send_file(str(_DASHBOARD_HTML))
        return (
            "<h1 style='font-family:sans-serif;color:#00d4ff;"
            "background:#0a0a0a;padding:2rem'>LaptopPulse Dashboard</h1>"
            "<p style='color:#888;padding:0 2rem'>dashboard.html not found.</p>",
            500,
        )

    @app.route("/api/status")
    def api_status():
        try:
            from core.storage import sqlite_store
            status = sqlite_store.get_latest_status()
        except Exception as exc:
            logger.debug("api_status read failed: %s", exc)
            status = {"error": "SQLite unavailable", "health_score": 100, "health_band": "Unknown"}
        return jsonify(status)

    @app.route("/api/alerts")
    def api_alerts():
        try:
            from core.storage import sqlite_store
            alerts = sqlite_store.get_recent_alerts(50)
        except Exception as exc:
            logger.debug("api_alerts read failed: %s", exc)
            alerts = []
        return jsonify(alerts)

    @app.route("/api/reports")
    def api_reports():
        try:
            from core.storage import sqlite_store
            reports = sqlite_store.get_recent_reports(20)
        except Exception as exc:
            logger.debug("api_reports read failed: %s", exc)
            reports = []
        # Annotate each with whether the file still exists on disk
        for r in reports:
            r["exists"] = Path(r.get("path", "")).exists()
        return jsonify(reports)

    @app.route("/api/report/<path:filename>")
    def serve_report(filename):
        """Serve a generated HTML report by filename (not full path)."""
        try:
            from config.settings import get_reports_dir
            report_path = get_reports_dir() / filename
            if report_path.exists() and report_path.suffix == ".html":
                return send_file(str(report_path))
        except Exception as exc:
            logger.debug("serve_report failed: %s", exc)
        abort(404)

    return app


# --- Server lifecycle ---------------------------------------------------------

def start(port: int = None, host: str = None) -> None:
    """
    Start the dashboard server in a daemon thread.
    Idempotent — calling twice has no effect.
    Reads port/host from config if not explicitly provided.
    """
    global _thread, _started, _port, _host

    if _started:
        logger.debug("Dashboard server already running on %s:%d", _host, _port)
        return

    # Resolve config
    try:
        from config.settings import cfg
        dash_cfg = cfg.raw.get("dashboard", {})
        _port = port or dash_cfg.get("port", 5747)
        _host = host or dash_cfg.get("host", "127.0.0.1")
    except Exception:
        _port = port or 5747
        _host = host or "127.0.0.1"

    # Ensure SQLite is ready before first request
    try:
        from core.storage import sqlite_store
        sqlite_store.init_db()
    except Exception as exc:
        logger.warning("Dashboard: SQLite init failed: %s", exc)

    flask_app = _make_app()

    def _run():
        flask_app.run(
            host=_host,
            port=_port,
            debug=False,
            use_reloader=False,
            threaded=True,
        )

    _thread = threading.Thread(target=_run, name="LaptopPulseDashboard", daemon=True)
    _thread.start()
    _started = True
    logger.info("Dashboard server started — http://%s:%d", _host, _port)


def open_browser() -> None:
    """Open the dashboard in the system default browser."""
    url = f"http://{_host}:{_port}"
    webbrowser.open(url)
    logger.info("Opening dashboard in browser: %s", url)


def is_running() -> bool:
    return _started and (_thread is not None) and _thread.is_alive()
