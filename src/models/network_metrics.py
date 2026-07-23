from dataclasses import dataclass

@dataclass
class NetworkMetrics:
    bytes_sent_sec: float
    bytes_recv_sec: float
