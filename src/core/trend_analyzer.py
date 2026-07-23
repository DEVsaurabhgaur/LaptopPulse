from typing import List
def calculate_rolling_average(values: List[float]) -> float:
    if not values: return 0.0
    return round(sum(values) / len(values), 2)
