from dataclasses import dataclass

@dataclass
class DiskMetrics:
    read_bytes_sec: float
    write_bytes_sec: float
    free_space_gb: float
