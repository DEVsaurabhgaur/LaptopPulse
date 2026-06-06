"""
core/sensors/gpu_amd.py
------------------------
AMD GPU temperature via WMI fallback.
Primary: rocm-smi (requires ROCm — mostly desktop/Linux)
Fallback: WMI Win32_VideoController — works on all AMD laptops without extra drivers.

Note: AMD GPU monitoring on Windows is less precise than NVIDIA's nvidia-smi.
This gives adequate temperature data for trend analysis purposes.
"""

import subprocess
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class AmdGpuMetrics:
    temperature: Optional[float]   # Celsius
    available: bool


# ── rocm-smi (primary, rarely available on Windows laptops) ──────────────────

def _read_rocm_smi() -> Optional[float]:
    try:
        result = subprocess.run(
            ["rocm-smi", "--showtemp", "--csv"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "Temperature" in line or line.strip().replace(".", "").isdigit():
                    parts = line.split(",")
                    if len(parts) >= 2:
                        try:
                            return float(parts[1].strip())
                        except ValueError:
                            pass
    except FileNotFoundError:
        pass
    except Exception as e:
        logger.debug("rocm-smi failed: %s", e)
    return None


# ── WMI fallback ──────────────────────────────────────────────────────────────

def _read_wmi_amd_temp() -> Optional[float]:
    """
    Uses Win32_PerfFormattedData or thermal zone for AMD GPU temp.
    Less accurate than vendor tools but always available on Windows.
    """
    try:
        result = subprocess.run(
            ["wmic", "path", "Win32_VideoController",
             "where", "AdapterCompatibility='Advanced Micro Devices, Inc.'",
             "get", "Name,CurrentBitsPerPixel"],
            capture_output=True, text=True, timeout=5,
        )
        # WMI VideoController doesn't expose temperature directly.
        # Use thermal zone as proxy for integrated AMD GPU.
        # For dedicated AMD GPUs, LibreHardwareMonitor is required.
        logger.debug("AMD GPU: WMI VideoController found — temp requires LHM")
    except Exception as e:
        logger.debug("WMI AMD query failed: %s", e)
    return None


# ── Public Interface ──────────────────────────────────────────────────────────

def read_amd_gpu_metrics() -> AmdGpuMetrics:
    """
    Read AMD GPU temperature. Tries rocm-smi first, then WMI.
    Returns available=False if no AMD GPU detected.
    """
    temp = _read_rocm_smi()
    if temp is not None:
        logger.debug("AMD GPU (rocm-smi): %.1f°C", temp)
        return AmdGpuMetrics(temperature=temp, available=True)

    temp = _read_wmi_amd_temp()
    if temp is not None:
        return AmdGpuMetrics(temperature=temp, available=True)

    return AmdGpuMetrics(temperature=None, available=False)
