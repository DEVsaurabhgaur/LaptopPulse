def is_thermal_throttling(current_temp: float, max_temp: float = 95.0) -> bool:
    return current_temp >= max_temp
