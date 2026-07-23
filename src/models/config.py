from dataclasses import dataclass

@dataclass
class DaemonConfig:
    poll_interval_sec: float = 5.0
    max_log_history: int = 1000
    alert_temp_threshold: float = 85.0
