"""
core/sensors/fan.py
--------------------
Fan RPM reading via LibreHardwareMonitor (WMI bridge).
Fallback: WMI Win32_Fan (OEM-dependent, absent on most laptops).

Fan RPM trend is the most reliable signal for bearing wear detection.
A 20% RPM decline over 60 days is a strong indicator of degradation
even if current RPM appears within range.

LHM must be running as Administrator for WMI access.
"""

import logging
import subprocess
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class FanMetrics:
    cpu_fan_rpm: Optional[int]   # Primary fan (CPU cooler)
    gpu_fan_rpm: Optional[int]   # GPU fan (None on most single-fan laptops)
    available:   bool            # False when no fan sensor could be read


# --- LibreHardwareMonitor (primary) -------------------------------------------

def _read_lhm_fan_rpm() -> tuple[Optional[int], Optional[int]]:
    """
    Read fan RPM values from LibreHardwareMonitor via WMI.
    Returns (cpu_fan_rpm, gpu_fan_rpm).
    Delegates to lhm_bridge - fully implemented, no TODO.
    Requires LHM running as Administrator.
    """
    try:
        from core.sensors.lhm_bridge import get_fan_rpms
        return get_fan_rpms()
    except Exception as exc:
        logger.debug("lhm_bridge.get_fan_rpms failed: %s", exc)
        return None, None


# --- WMI Fallback -------------------------------------------------------------

def _read_wmi_fan() -> Optional[int]:
    """
    WMI Win32_Fan query.
    Works on some Dell/Lenovo models. Not available on most ASUS/Acer laptops.
    Returns RPM as int, or None if OEM does not expose this sensor.
    """
    try:
        result = subprocess.run(
            ["wmic", "path", "Win32_Fan", "get", "DesiredSpeed,CurrentSpeed"],
            capture_output=True, text=True, timeout=5,
        )
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        if len(lines) > 1 and lines[1] != "":
            parts = lines[1].split()
            if parts:
                rpm = int(parts[0])
                if rpm > 0:
                    return rpm
    except Exception as exc:
        logger.debug("WMI Win32_Fan fallback failed: %s", exc)
    return None


# --- Public interface ---------------------------------------------------------

def read_fan_metrics() -> FanMetrics:
    """
    Read fan RPM data.

    Priority:
      1. LibreHardwareMonitor WMI  (accurate, both CPU + GPU fans)
      2. WMI Win32_Fan             (OEM-dependent, CPU fan only)
      3. unavailable               (available=False, watcher logs warning)
    """
    cpu_rpm, gpu_rpm = _read_lhm_fan_rpm()

    if cpu_rpm is None and gpu_rpm is None:
        # Try WMI fallback
        wmi_rpm = _read_wmi_fan()
        if wmi_rpm is not None:
            cpu_rpm = wmi_rpm
            logger.debug("Fan via WMI fallback: %d RPM", cpu_rpm)
        else:
            logger.debug(
                "Fan RPM unavailable - LHM not running and Win32_Fan returned nothing"
            )
            return FanMetrics(cpu_fan_rpm=None, gpu_fan_rpm=None, available=False)
    else:
        logger.debug("Fan via LHM: CPU=%s RPM, GPU=%s RPM", cpu_rpm, gpu_rpm)

    return FanMetrics(
        cpu_fan_rpm=cpu_rpm,
        gpu_fan_rpm=gpu_rpm,
        available=True,
    )
