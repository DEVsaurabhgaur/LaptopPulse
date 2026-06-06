"""
core/sensors/battery.py
------------------------
Battery health and charge status via psutil.
Extended health data (design capacity vs current capacity) via WMI.
"""

import subprocess
import logging
from dataclasses import dataclass
from typing import Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class BatteryMetrics:
    percent: Optional[float]           # Current charge 0-100
    is_plugged: Optional[bool]         # True if AC power
    health_percent: Optional[float]    # Current capacity / design capacity × 100
    design_capacity_mwh: Optional[int]
    full_charge_capacity_mwh: Optional[int]
    cycle_count: Optional[int]
    available: bool


# ── psutil: charge + plugged ──────────────────────────────────────────────────

def _read_psutil_battery() -> tuple[Optional[float], Optional[bool]]:
    try:
        bat = psutil.sensors_battery()
        if bat:
            return bat.percent, bat.power_plugged
    except Exception as e:
        logger.debug("psutil battery failed: %s", e)
    return None, None


# ── WMI: design vs full charge capacity ──────────────────────────────────────

def _read_wmi_battery_health() -> tuple[Optional[int], Optional[int], Optional[int]]:
    """
    Returns: (design_capacity_mwh, full_charge_capacity_mwh, cycle_count)
    WMI BatteryFullChargedCapacity vs BatteryStaticData gives health %.
    """
    try:
        # Design capacity
        r1 = subprocess.run(
            ["wmic", "path", "Win32_Battery", "get",
             "DesignCapacity,FullChargeCapacity"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [ln.strip() for ln in r1.stdout.splitlines() if ln.strip()]
        design = full = None
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 2:
                try:
                    design = int(parts[0])
                    full   = int(parts[1])
                except ValueError:
                    pass

        # Cycle count (not always available via WMI)
        r2 = subprocess.run(
            ["wmic", "path", "Win32_Battery", "get", "CycleCount"],
            capture_output=True, text=True, timeout=5,
        )
        lines2 = [ln.strip() for ln in r2.stdout.splitlines() if ln.strip()]
        cycles = None
        if len(lines2) > 1:
            try:
                cycles = int(lines2[1])
            except ValueError:
                pass

        return design, full, cycles

    except Exception as e:
        logger.debug("WMI battery health failed: %s", e)
    return None, None, None


# ── Public Interface ──────────────────────────────────────────────────────────

def read_battery_metrics() -> BatteryMetrics:
    """
    Read comprehensive battery metrics.
    Combines psutil (charge %) with WMI (health/capacity).
    """
    percent, plugged = _read_psutil_battery()
    design, full, cycles = _read_wmi_battery_health()

    health = None
    if design and full and design > 0:
        health = round((full / design) * 100, 1)

    if percent is not None:
        logger.debug(
            "Battery: %.1f%% | Plugged: %s | Health: %s%%",
            percent, plugged, health,
        )

    return BatteryMetrics(
        percent=percent,
        is_plugged=plugged,
        health_percent=health,
        design_capacity_mwh=design,
        full_charge_capacity_mwh=full,
        cycle_count=cycles,
        available=percent is not None,
    )
