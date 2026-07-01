"""
config/settings.py
------------------
Centralized settings manager for LaptopPulse.
Loads defaults, overrides from .env, and manages encrypted API key storage.
"""

import sys
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ────────────────────────────────────────────────────────────────────

def get_app_dir() -> Path:
    """Returns the LaptopPulse data directory. Creates it if missing."""
    base = os.environ.get("LAPTOPPULSE_LOG_DIR")
    if base:
        path = Path(base)
    else:
        path = Path.home() / "AppData" / "LocalLow" / "LaptopPulse"
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_log_dir() -> Path:
    d = get_app_dir() / "logs"
    d.mkdir(parents=True, exist_ok=True)
    return d


def get_reports_dir() -> Path:
    d = get_app_dir() / "reports"
    d.mkdir(parents=True, exist_ok=True)
    return d


# ── Default config loading ────────────────────────────────────────────────────

def _get_config_dir() -> Path:
    """Returns config/ dir — works both as script and PyInstaller .exe."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "config"
    return Path(__file__).parent


_defaults_path = _get_config_dir() / "defaults.json"


def load_defaults() -> dict:
    """Load default configuration from defaults.json."""
    with open(_defaults_path, "r") as f:
        return json.load(f)


# ── Runtime config ────────────────────────────────────────────────────────────

class Config:
    """
    Singleton config object. Merges defaults with env overrides.
    Usage:
        from config.settings import Config
        cfg = Config()
        print(cfg.thresholds["cpu_temp_critical"])
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def __init__(self):
        if not self._loaded:
            self._data = load_defaults()
            self._apply_env_overrides()
            self._loaded = True

    def _apply_env_overrides(self):
        interval = os.environ.get("LAPTOPPULSE_INTERVAL")
        if interval:
            self._data["monitoring"]["interval_seconds"] = int(interval)

    def __getattr__(self, name: str):
        if name.startswith("_"):
            raise AttributeError(name)
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"Config has no section '{name}'")

    def get(self, section: str, key: str, default=None):
        return self._data.get(section, {}).get(key, default)

    def is_dev_mode(self) -> bool:
        return os.environ.get("LAPTOPPULSE_DEV_MODE", "false").lower() == "true"


# Convenient singleton access
cfg = Config()
