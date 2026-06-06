"""
core/sensors/fan.py
-------------------
Fan RPM reader.
Win32_Fan WMI class is rarely populated on laptops — ASUS TUF FA506QM
has an EC-locked fan controller that Windows can't access without a
vendor kernel driver.
Returns available=False gracefully — dashboard shows
"N/A — sensor restricted by OS" instead of crashing.
"""
import logging
from dataclasses import dataclass
from typing import Optional

import wmi as _wmi

logger = logging.getLogger(__name__)


@dataclass
class FanMetrics:
    cpu_fan_rpm: Optional[int]   # RPM, or None if unavailable
    gpu_fan_rpm: Optional[int]   # RPM, or None if unavailable
    available: bool              # False on most laptops — expected, not an error


# ── Public Interface ──────────────────────────────────────────────────────────

def read_fan_metrics() -> FanMetrics:
    """
    Attempt to read fan RPM via Win32_Fan WMI class.
    On ASUS TUF FA506QM (and most gaming laptops) this will return
    available=False — that is expected behaviour, not a bug.
    Never raises.
    """
    try:
        w = _wmi.WMI()
        fans = w.Win32_Fan()
        if fans:
            rpms = [
                int(f.DesiredSpeed)
                for f in fans
                if f.DesiredSpeed and f.DesiredSpeed > 0
            ]
            if rpms:
                return FanMetrics(
                    cpu_fan_rpm=rpms[0],
                    gpu_fan_rpm=rpms[1] if len(rpms) > 1 else None,
                    available=True,
                )
    except Exception as e:
        logger.debug("Win32_Fan read failed (expected on most laptops): %s", e)

    return FanMetrics(cpu_fan_rpm=None, gpu_fan_rpm=None, available=False)


if __name__ == "__main__":
    m = read_fan_metrics()
    if m.available:
        print(f"Fan RPM: CPU={m.cpu_fan_rpm}, GPU={m.gpu_fan_rpm}")
    else:
        print("Fan RPM: N/A — sensor restricted by OS (normal on ASUS TUF FA506QM)")
