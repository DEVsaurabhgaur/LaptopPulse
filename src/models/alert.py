from dataclasses import dataclass
import time

@dataclass
class AlertNotification:
    alert_id: str
    severity: str
    message: str
    timestamp: float = time.time()
