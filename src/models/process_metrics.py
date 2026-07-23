from dataclasses import dataclass

@dataclass
class ProcessMetrics:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
