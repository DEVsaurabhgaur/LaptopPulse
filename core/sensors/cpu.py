"""
core/sensors/cpu.py
-------------------
CPU metrics via Windows ACPI WMI thermal zones + psutil.
Zero external software dependency — Windows-native APIs only.
No LHM, no HWiNFO, no external software needed.
"""
import logging
from dataclasses import dataclass
from typing import Optional

import psutil
import wmi as _wmi

logger = logging.getLogger(__name__)


@dataclass
class CpuMetrics:
    temperature: Optional[float]    # Celsius
    load_percent: Optional[float]   # 0-100 %
    clock_mhz: Optional[float]      # Current clock speed in MHz
    is_throttling: bool             # True if running at < 50% of max frequency


# ── ACPI Thermal Zone (Windows-native, no external software) ─────────────────

def _read_acpi_temp() -> Optional[float]:
    """
    Read CPU temperature from Windows ACPI thermal zones.
    MSAcpi_ThermalZoneTemperature is built into Windows kernel.
    Works on AMD Ryzen + Intel — no LHM or HWiNFO required.
    """
    try:
        w = _wmi.WMI(namespace=r"root\wmi")
        zones = w.MSAcpi_ThermalZoneTemperature()
        if not zones:
            return None
        # MSAcpi reports in tenths-of-Kelvin → convert to Celsius
        # Filter: valid CPU temps are 20°C–120°C (garbage values outside this)
        temps = [
            (z.CurrentTemperature / 10.0) - 273.15
            for z in zones
            if z.CurrentTemperature > 2732   # > 0°C sanity check
        ]
        valid = [t for t in temps if 20.0 < t < 120.0]
        return round(max(valid), 1) if valid else None
    except Exception as e:
        logger.debug("ACPI temp read failed: %s", e)
        return None


# ── Public Interface ──────────────────────────────────────────────────────────

def read_cpu_metrics() -> CpuMetrics:
    """
    Read CPU temperature, load, clock speed, and throttling state.
    Never raises — all sensor errors return safe None/False defaults.
    Called by watcher.py every tick.
    """
    # Temperature: ACPI thermal zone (AMD Ryzen safe, no external software)
    temp = _read_acpi_temp()

    # Load: psutil cpu_percent (interval=None = non-blocking, uses last interval)
    try:
        load = psutil.cpu_percent(interval=None)
    except Exception:
        load = None

    # Clock + throttle detection
    clock_mhz = None
    is_throttling = False
    try:
        freq = psutil.cpu_freq()
        if freq:
            clock_mhz = round(freq.current, 1)
            if freq.max and freq.max > 0:
                # Throttling = running at less than 50% of rated max
                is_throttling = freq.current < (freq.max * 0.50)
    except Exception:
        pass

    logger.debug(
        "CPU: %s°C | Load: %s%% | Clock: %sMHz | Throttling: %s",
        temp, load, clock_mhz, is_throttling,
    )

    return CpuMetrics(
        temperature=temp,
        load_percent=load,
        clock_mhz=clock_mhz,
        is_throttling=is_throttling,
    )


if __name__ == "__main__":
    m = read_cpu_metrics()
    print(f"CPU: {m.temperature}°C | Load: {m.load_percent}% | "
          f"Clock: {m.clock_mhz}MHz | Throttling: {m.is_throttling}")
