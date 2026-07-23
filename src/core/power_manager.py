def estimate_battery_wear(original_cap_mwh: float, current_cap_mwh: float) -> float:
    if original_cap_mwh <= 0: return 0.0
    return round((1 - current_cap_mwh / original_cap_mwh) * 100, 2)
