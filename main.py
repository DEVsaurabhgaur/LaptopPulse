"""
main.py
--------
LaptopPulse — Entry Point

Usage:
  python main.py              → Start daemon + tray icon (normal user launch)
  python main.py --daemon     → Daemon only (no tray, for Windows Service mode)
  python main.py --tray-only  → Tray only (daemon running separately as service)
  python main.py --report     → Generate a test report immediately
  python main.py --setup-key  → Save API key (auto-detects Gemini or Claude)
  python main.py --version    → Print version and exit

API Key Setup:
  Gemini (FREE):  python main.py --setup-key  → enter AIza... key
                  Get free key at: https://aistudio.google.com/apikey
  Claude (paid):  python main.py --setup-key  → enter sk-ant-... key
                  Get key at: https://console.anthropic.com
  Quick setup:    python save_gemini_key.py   → guided Gemini setup only
"""

import argparse
import logging
import sys
import threading
from pathlib import Path

__version__ = "1.1.0"


# ── Logging setup ─────────────────────────────────────────────────────────────

def _setup_logging(level=logging.INFO):
    from config.settings import get_app_dir
    log_file = get_app_dir() / "laptoppulse.log"

    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        handlers.append(logging.FileHandler(str(log_file), encoding="utf-8"))
    except Exception:
        pass

    logging.basicConfig(
        level   = level,
        format  = "%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S",
        handlers= handlers,
    )


# ── CLI actions ───────────────────────────────────────────────────────────────

def cmd_setup_key():
    """
    Interactively save an API key (Gemini or Claude — auto-detected by prefix).
    Gemini keys (AIza...) → FREE tier, recommended.
    Claude keys (sk-ant-) → Paid, ~$0.003/report.
    """
    from config.settings import get_app_dir
    from core.security.encryption import save_api_key

    print("=" * 55)
    print("  LaptopPulse — AI Report API Key Setup")
    print("=" * 55)
    print()
    print("Choose your AI provider:")
    print()
    print("  [RECOMMENDED - FREE]")
    print("  Gemini 1.5 Flash — Get free key at:")
    print("  https://aistudio.google.com/apikey")
    print("  Key format: AIza...")
    print()
    print("  [ALTERNATIVE - PAID]")
    print("  Anthropic Claude — Get key at:")
    print("  https://console.anthropic.com")
    print("  Key format: sk-ant-...")
    print()

    import getpass
    while True:
        key = getpass.getpass("Enter your API key: ").strip()

        if not key:
            print("[ERROR] Key cannot be empty. Try again.\n")
            continue

        if key.startswith("AIza"):
            print("[OK] Gemini API key detected (free tier).")
        elif key.startswith("sk-ant-"):
            print("[OK] Anthropic Claude API key detected.")
        else:
            confirm = input(
                "[WARNING] Unrecognized key format. Save anyway? (y/n): "
            ).strip().lower()
            if confirm != "y":
                print("Try again.\n")
                continue

        break

    config_path = get_app_dir() / "config.enc"
    save_api_key(key, config_path)
    print()
    print(f"[OK] Key saved (encrypted) to: {config_path}")
    print()
    print("Test it now:  python main.py --report")
    print()


def cmd_generate_test_report():
    """Generate a test report using mock data — useful for demos and verification."""
    from datetime import datetime
    from core.detector.rules import Alert, RuleType, Severity
    from core.reporter.generator import generate_report
    from core.storage.trends_calc import compute_trends

    print("Generating test report...")
    alert = Alert(
        rule_id    = "IDLE_TEMP_RISE_CRITICAL",
        rule_type  = RuleType.TREND,
        severity   = Severity.URGENT,
        title      = "CPU Temperature Rising Fast",
        message    = "CPU idle temperature has increased by 12°C over 30 days.",
        value      = 12.0,
        threshold  = 12.0,
    )
    system_info = {
        "model":      "ASUS TUF Gaming A15 FA506QM",
        "cpu":        "AMD Ryzen 7 5800H",
        "gpu":        "NVIDIA GeForce RTX 3060 Laptop",
        "os":         "Windows 11 Pro",
        "age_months": "18",
    }
    mock_trends = {
        "30d": {
            "cpu_idle_avg":   62.4,
            "cpu_temp_avg":   74.1,
            "gpu_temp_avg":   68.2,
            "fan_rpm_avg":    3240,
            "throttle_count": 7,
            "cpu_load_avg":   28.4,
        }
    }
    path = generate_report(alert, system_info, mock_trends)
    if path:
        print(f"[OK] Report generated: {path}")
        try:
            import os
            os.startfile(str(path))
        except Exception:
            pass
    else:
        print("[ERROR] Report generation failed — check logs.")
        print("  If no API key is set, you still get an offline report.")
        print("  Check: python main.py --setup-key")


def cmd_run_daemon():
    from core.watcher import run_daemon
    run_daemon()


def cmd_run_full():
    """Run daemon + tray icon together in the same process."""
    daemon_thread = threading.Thread(target=cmd_run_daemon, daemon=True)
    daemon_thread.start()

    from ui.tray import start_tray
    start_tray()  # Blocks until user clicks Exit


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LaptopPulse v{} — AI-powered laptop health monitor".format(__version__),
    )
    parser.add_argument("--version",   action="store_true",  help="Print version")
    parser.add_argument("--daemon",    action="store_true",  help="Run daemon only (no tray)")
    parser.add_argument("--tray-only", action="store_true",  help="Tray icon only")
    parser.add_argument("--report",    action="store_true",  help="Generate test report now")
    parser.add_argument("--setup-key", action="store_true",  help="Save Gemini or Claude API key")
    parser.add_argument("--debug",     action="store_true",  help="Enable debug logging")
    args = parser.parse_args()

    if args.version:
        print(f"LaptopPulse v{__version__}")
        return

    _setup_logging(logging.DEBUG if args.debug else logging.INFO)

    if args.setup_key:
        cmd_setup_key()
    elif args.report:
        cmd_generate_test_report()
    elif args.daemon:
        cmd_run_daemon()
    elif args.tray_only:
        from ui.tray import start_tray
        start_tray()
    else:
        cmd_run_full()


if __name__ == "__main__":
    main()
