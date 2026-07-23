from typing import List
def detect_spike(values: List[float], threshold_multiplier: float = 2.0) -> bool:
    if len(values) < 5: return False
    avg = sum(values[:-1]) / (len(values) - 1)
    return values[-1] > avg * threshold_multiplier
