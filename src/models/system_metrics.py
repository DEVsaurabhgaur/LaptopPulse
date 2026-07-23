from dataclasses import dataclass
from typing import Optional

@dataclass
class CpuMetrics:
    usage_percent: float
    core_count: int
    frequency_mhz: float
    temp_celsius: Optional[float] = None
