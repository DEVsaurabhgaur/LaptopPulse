"""
ui/tray.py
-----------
System tray icon — the primary UI surface for LaptopPulse.
Uses pystray + Pillow. Runs in its own thread.

States:  green (healthy) | yellow (monitor/warn) | red (critical)
Menu:    Open Dashboard | View Latest Report | Settings | About | Exit
"""

import logging
import sys
import threading
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import pystray
    from PIL import Image, ImageDraw
    _PYSTRAY_OK = True
except ImportError:
    _PYSTRAY_OK = False
    logger.warning("pystray or Pillow not installed — tray icon disabled")

# Module state
_icon:  Optional[object] = None   # pystray.Icon
_state: str = "green"             # current visual state


# ── Icon image generation ──────────────────────────────────────────────────

def _load_icon_image(state: str) -> "Image.Image":
    """
    Load a branded .ico from assets/ if present, otherwise generate
    a coloured circle programmatically.
    """
    assets = Path(__file__).parent.parent / "assets"
    ico_map = {
        "green":  assets / "icon_green.ico",
        "yellow": assets / "icon_yellow.ico",
        "red":    assets / "icon_red.ico",
    }
    ico_path = ico_map.get(state)
    if ico_path and ico_path.exists():
        try:
            return Image.open(str(ico_path))
        except Exception:
            pass

    # Programmatic fallback — coloured circle on dark background
    size  = 64
    img   = Image.new("RGBA", (size, size), (10, 10, 10, 255))
    draw  = ImageDraw.Draw(img)
    color_map = {
        "green":  (34, 197, 94),
        "yellow": (245, 197, 24),
        "red":    (239, 68, 68),
    }
    fill = color_map.get(state, (0, 212, 255))
    pad  = 8
    draw.ellipse([pad, pad, size - pad, size - pad], fill=fill)
    return img


# ── State management ───────────────────────────────────────────────────────

def set_tray_state(state: str, tooltip: str = "") -> None:
    """Update tray icon color and tooltip. Thread-safe."""
    global _state
    _state = state
    if _icon is None or not _PYSTRAY_OK:
        return
    try:
        _icon.icon = _load_icon_image(state)
        if tooltip:
            _icon.title = tooltip
    except Exception as exc:
        logger.debug("set_tray_state failed: %s", exc)


def show_notification(title: str, message: str) -> None:
    """Show a Windows toast notification via pystray."""
    if _icon is None or not _PYSTRAY_OK:
        logger.info("Notification (no tray): %s — %s", title, message)
        return
    try:
        _icon.notify(message, title)
    except Exception as exc:
        logger.debug("show_notification failed: %s", exc)


# ── Menu actions ───────────────────────────────────────────────────────────

def _open_dashboard(_icon=None, _item=None) -> None:
    """Open the local dashboard in the default browser."""
    try:
        from ui.dashboard_server import open_browser, start, is_running
        if not is_running():
            start()
        open_browser()
    except Exception as exc:
        logger.error("Open dashboard failed: %s", exc)


def _view_latest_report(_icon=None, _item=None) -> None:
    """Open the most recently generated HTML report in the browser."""
    try:
        from core.storage import sqlite_store
        reports = sqlite_store.get_recent_reports(1)
        if reports:
            path = Path(reports[0]["path"])
            if path.exists():
                import webbrowser
                webbrowser.open(path.as_uri())
                return
        _show_info("No Reports", "No health reports have been generated yet.\n\nLaptopPulse will generate a report automatically when an issue is detected.")
    except Exception as exc:
        logger.error("View latest report failed: %s", exc)


def _open_settings(_icon=None, _item=None) -> None:
    """
    Settings dialog using tkinter.
    Allows the user to update their Gemini/Claude API key and
    override critical CPU/fan thresholds.
    """
    def _run_dialog():
        root = tk.Tk()
        root.withdraw()
        root.title("LaptopPulse Settings")

        try:
            from config.settings import cfg
            from core.security.encryption import load_api_key, save_api_key

            dialog = tk.Toplevel(root)
            dialog.title("LaptopPulse Settings")
            dialog.geometry("420x320")
            dialog.resizable(False, False)
            dialog.configure(bg="#111318")
            dialog.lift()
            dialog.focus_force()

            # Title
            tk.Label(
                dialog, text="LaptopPulse Settings",
                bg="#111318", fg="#00d4ff",
                font=("Segoe UI", 13, "bold"),
            ).pack(pady=(18, 4))

            tk.Label(
                dialog, text="Changes take effect on the next monitoring tick (60 s).",
                bg="#111318", fg="#64748b", font=("Segoe UI", 9),
            ).pack(pady=(0, 14))

            # --- API Key ---
            frame_key = tk.Frame(dialog, bg="#111318")
            frame_key.pack(fill="x", padx=24, pady=4)
            tk.Label(frame_key, text="AI API Key", bg="#111318", fg="#e2e8f0",
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
            tk.Label(frame_key,
                     text="Gemini key (AIza...) or Claude key (sk-ant-...)",
                     bg="#111318", fg="#64748b", font=("Segoe UI", 8)).pack(anchor="w")
            key_var = tk.StringVar(value="")
            key_entry = tk.Entry(frame_key, textvariable=key_var, show="*",
                                 bg="#1e2330", fg="#e2e8f0",
                                 insertbackground="#00d4ff",
                                 relief="flat", font=("Segoe UI", 9))
            key_entry.pack(fill="x", pady=(4, 0), ipady=5)

            # --- CPU Warning Threshold ---
            frame_thr = tk.Frame(dialog, bg="#111318")
            frame_thr.pack(fill="x", padx=24, pady=(12, 4))
            tk.Label(frame_thr, text="CPU Warning Threshold (°C)",
                     bg="#111318", fg="#e2e8f0",
                     font=("Segoe UI", 9, "bold"), anchor="w").pack(fill="x")
            current_warn = cfg.thresholds.get("cpu_temp_warning", 80)
            warn_var = tk.StringVar(value=str(current_warn))
            tk.Entry(frame_thr, textvariable=warn_var, bg="#1e2330", fg="#e2e8f0",
                     insertbackground="#00d4ff", relief="flat",
                     font=("Segoe UI", 9), width=8).pack(anchor="w", pady=(4, 0), ipady=5)

            # --- Buttons ---
            btn_frame = tk.Frame(dialog, bg="#111318")
            btn_frame.pack(side="bottom", fill="x", padx=24, pady=18)

            def _save():
                new_key = key_var.get().strip()
                if new_key:
                    try:
                        save_api_key(new_key)
                        logger.info("API key updated via settings dialog.")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save key:\n{e}", parent=dialog)
                        return

                new_warn = warn_var.get().strip()
                if new_warn.isdigit():
                    cfg.raw.setdefault("thresholds", {})["cpu_temp_warning"] = int(new_warn)

                messagebox.showinfo("Saved", "Settings saved successfully.", parent=dialog)
                dialog.destroy()
                root.destroy()

            def _cancel():
                dialog.destroy()
                root.destroy()

            tk.Button(btn_frame, text="Save", command=_save,
                      bg="#00d4ff", fg="#0a0a0a",
                      font=("Segoe UI", 9, "bold"),
                      relief="flat", padx=14, pady=5).pack(side="right", padx=(6, 0))
            tk.Button(btn_frame, text="Cancel", command=_cancel,
                      bg="#1e2330", fg="#e2e8f0",
                      font=("Segoe UI", 9),
                      relief="flat", padx=14, pady=5).pack(side="right")

            dialog.protocol("WM_DELETE_WINDOW", _cancel)
            dialog.wait_window()

        except Exception as exc:
            logger.error("Settings dialog error: %s", exc, exc_info=True)
            root.destroy()

    threading.Thread(target=_run_dialog, daemon=True).start()


def _show_about(_icon=None, _item=None) -> None:
    _show_info(
        "About LaptopPulse",
        "LaptopPulse v1.1.0\n\n"
        "Lightweight AI hardware health monitor for Windows.\n"
        "Monitors your laptop 24/7 using < 0.3% CPU.\n\n"
        "Dashboard: http://127.0.0.1:5747\n"
        "GitHub: github.com/saurabhgaur/laptoppulse\n\n"
        "© 2026 Saurabh Gaur — MIT License",
    )


def _show_info(title: str, message: str) -> None:
    def _run():
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo(title, message)
        root.destroy()
    threading.Thread(target=_run, daemon=True).start()


def _on_exit(_icon=None, _item=None) -> None:
    logger.info("Exit requested from tray.")
    if _icon:
        _icon.stop()
    sys.exit(0)


# ── Public launcher ────────────────────────────────────────────────────────

def start_tray(start_dashboard: bool = True) -> None:
    """
    Build the tray icon and menu, then start the pystray event loop.
    Blocks the calling thread — run in a dedicated daemon thread from main.py.
    Optionally starts the dashboard Flask server before the loop.
    """
    global _icon

    if not _PYSTRAY_OK:
        logger.warning("pystray unavailable — running without tray icon")
        return

    if start_dashboard:
        try:
            from ui.dashboard_server import start as start_dash
            start_dash()
        except Exception as exc:
            logger.warning("Dashboard server failed to start: %s", exc)

    menu = pystray.Menu(
        pystray.MenuItem("Open Dashboard",     _open_dashboard, default=True),
        pystray.MenuItem("View Latest Report", _view_latest_report),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Settings",           _open_settings),
        pystray.MenuItem("About",              _show_about),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit",               _on_exit),
    )

    _icon = pystray.Icon(
        name="LaptopPulse",
        icon=_load_icon_image("green"),
        title="LaptopPulse — Healthy",
        menu=menu,
    )
    logger.info("Tray icon starting (double-click to open dashboard).")
    _icon.run()
