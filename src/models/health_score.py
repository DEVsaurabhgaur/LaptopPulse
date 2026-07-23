from dataclasses import dataclass
from typing import List

@dataclass
class SystemHealthReport:
    overall_score: int
    cpu_score: int
    ram_score: int
    battery_score: int
    warnings: List[str]
