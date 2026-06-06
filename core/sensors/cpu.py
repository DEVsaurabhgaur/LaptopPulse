"""
core/sensors/cpu.py
--------------------
CPU temperature and throttle detection.
Primary source: LibreHardwareMonitor via lhm_bridge (WMI query).
Fallback: WMI thermal zone (less accurate — ACPI zone, ~10-15 degrees low).

LibreHardwareMonitor must be running as Administrator for WMI access.
Download: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
"""

import logging
import subprocess
from dataclasses import dataclass
from typing import Optional

import psutil

logger = logging.getLogger(__name__)


@dataclass
class CpuMetrics:
    temperature:   Optional[float]  # Celsius - CPU Package temp
    load_percent:  float            # 0-100
    clock_mhz:     Optional[float]  # Current clock speed in MHz
    is_throttling: bool             # True if clock dropped > 30% from boost


# --- LibreHardwareMonitor (primary) -------------------------------------------

def _read_lhm_cpu_temp() -> Optional[float]:
    """
    Read CPU Package temperature from LibreHardwareMonitor via WMI.
    Delegates to lhm_bridge - no stub, no placeholder.
    Returns None if LHM is not running or WMI query fails.
    """
    try:
        from core.sensors.lhm_bridge import get_cpu_temp
        return get_cpu_temp()
    except Exception as exc:
        logger.debug("lhm_bridge.get_cpu_temp failed: %s", exc)
        return None


# --- WMI Fallback -------------------------------------------------------------

def _read_wmi_cpu_temp() -> Optional[float]:
    """
    WMI ACPI thermal zone fallback.
    Reports the Windows thermal zone temperature, not the CPU package sensor.
    Typically reads 10-15 degrees lower than actual package temp on most laptops.
    Always available without LHM; no elevation needed on Windows 10/11.
    """
    try:
        result = subprocess.run(
            [
                "wmic", "path",
                "Win32_PerfFormattedData_Counters_ThermalZoneInformation",
                "get", "Temperature",
            ],
            capture_output=True, text=True, timeout=5,
        )
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        if len(lines) > 1:
            # WMI returns temperature in tenths of Kelvin
            raw_dk = int(lines[1])
            celsius = (raw_dk / 10.0) - 273.15
            return round(celsius, 1)
    except Exception as exc:
        logger.debug("WMI CPU temp fallback failed: %s", exc)
    return None


# --- Throttle detection -------------------------------------------------------

def _detect_throttle(current_mhz: Optional[float], boost_mhz: float = 4400.0) -> bool:
    """
    Detect thermal throttling: current clock dropped more than 30%
    from the CPU boost frequency.
    Default boost_mhz = 4400 (Ryzen 7 5800H on ASUS TUF A15).
    """
    if current_mhz is None:
        return False
    drop_fraction = (boost_mhz - current_mhz) / boost_mhz
    return drop_fraction > 0.30


def _read_cpu_clock() -> Optional[float]:
    """Current CPU clock speed in MHz via psutil. No elevation needed."""
    try:
        freq = psutil.cpu_freq()
        if freq:
            return freq.current
    except Exception as exc:
        logger.debug("CPU freq read failed: %s", exc)
    return None


# --- Public interface ---------------------------------------------------------

def read_cpu_metrics() -> CpuMetrics:
    """
    Collect a complete CPU metrics snapshot.
    Temperature priority: LHM (package) -> WMI (ACPI zone) -> None.
    Load and clock always via psutil (no elevation needed).
    """
    # Temperature
    temp = _read_lhm_cpu_temp()
    if temp is None:
        temp = _read_wmi_cpu_temp()
        if temp is not None:
            logger.debug("CPU temp via WMI fallback (ACPI, ~10 degrees low): %.1f C", temp)
    else:
        logger.debug("CPU temp via LHM: %.1f C", temp)

    if temp is None:
        logger.warning("CPU temperature unavailable - is LHM running as admin?")

    # Load and clock
    load  = psutil.cpu_percent(interval=None)
    clock = _read_cpu_clock()

    # Throttle
    throttling = _detect_throttle(clock)

    if temp is not None:
        logger.debug(
            "CPU: %.1f C | Load: %.1f%% | Clock: %s MHz | Throttle: %s",
            temp, load, clock, throttling,
        )

    return CpuMetrics(
        temperature=temp,
        load_percent=load,
        clock_mhz=clock,
        is_throttling=throttling,
    )
