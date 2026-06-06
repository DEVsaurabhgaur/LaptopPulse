"""
core/sensors/gpu_nvidia.py
---------------------------
NVIDIA GPU temperature, utilization, and fan speed via nvidia-smi.
nvidia-smi is pre-installed with every NVIDIA driver — no extra dependencies.
Compatible with all GeForce / Quadro / RTX laptops.

ASUS TUF A15 FA506QM: RTX 3060 Laptop GPU — tested and confirmed working.
"""

import subprocess
import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class GpuMetrics:
    temperature: Optional[int]      # Celsius
    utilization: Optional[int]      # 0-100 %
    fan_speed: Optional[int]        # 0-100 % (or RPM depending on nvidia-smi version)
    memory_used_mb: Optional[int]   # VRAM used in MB
    power_draw_w: Optional[float]   # Power draw in Watts
    available: bool                 # False if NVIDIA GPU/driver not found


# ── nvidia-smi Query ──────────────────────────────────────────────────────────

_NVIDIA_SMI_QUERY = ",".join([
    "temperature.gpu",
    "utilization.gpu",
    "fan.speed",
    "memory.used",
    "power.draw",
])


def _run_nvidia_smi() -> Optional[str]:
    """
    Run nvidia-smi and return CSV output.
    Returns None if nvidia-smi not found (no NVIDIA GPU or driver).
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                f"--query-gpu={_NVIDIA_SMI_QUERY}",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        logger.debug("nvidia-smi not found — no NVIDIA GPU or driver not installed")
    except subprocess.TimeoutExpired:
        logger.warning("nvidia-smi timed out")
    except Exception as e:
        logger.debug("nvidia-smi error: %s", e)
    return None


def _parse_value(raw: str) -> Optional[int | float]:
    """Parse a CSV field — return None for '[N/A]' or empty values."""
    raw = raw.strip()
    if not raw or raw in ("[N/A]", "N/A", "Unknown Error"):
        return None
    try:
        val = float(raw)
        return int(val) if val == int(val) else val
    except ValueError:
        return None


# ── Public Interface ──────────────────────────────────────────────────────────

def read_gpu_metrics() -> GpuMetrics:
    """
    Read NVIDIA GPU metrics via nvidia-smi.
    Returns GpuMetrics with available=False if NVIDIA GPU not present.
    Never raises — all errors return safe defaults.
    """
    output = _run_nvidia_smi()

    if output is None:
        return GpuMetrics(
            temperature=None,
            utilization=None,
            fan_speed=None,
            memory_used_mb=None,
            power_draw_w=None,
            available=False,
        )

    parts = output.split(",")
    if len(parts) < 5:
        logger.warning("Unexpected nvidia-smi output: %r", output)
        return GpuMetrics(None, None, None, None, None, available=True)

    temp       = _parse_value(parts[0])
    util       = _parse_value(parts[1])
    fan        = _parse_value(parts[2])
    mem_used   = _parse_value(parts[3])
    power      = _parse_value(parts[4])

    logger.debug(
        "GPU: %s°C | Util: %s%% | Fan: %s%% | VRAM: %sMB | Power: %sW",
        temp, util, fan, mem_used, power,
    )

    return GpuMetrics(
        temperature=temp,
        utilization=util,
        fan_speed=fan,
        memory_used_mb=mem_used,
        power_draw_w=power,
        available=True,
    )


def is_nvidia_available() -> bool:
    """Quick check — returns True if nvidia-smi is accessible."""
    return _run_nvidia_smi() is not None
