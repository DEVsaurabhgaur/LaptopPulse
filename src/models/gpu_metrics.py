from dataclasses import dataclass
from typing import Optional

@dataclass
class GpuMetrics:
    name: str
    usage_percent: float
    temp_celsius: Optional[float]
