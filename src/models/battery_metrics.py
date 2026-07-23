from dataclasses import dataclass
from typing import Optional

@dataclass
class BatteryMetrics:
    percent: float
    power_plugged: bool
    time_left_seconds: Optional[int]
