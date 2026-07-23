from src.core.power_manager import estimate_battery_wear
def test_battery():
    assert estimate_battery_wear(100, 80) == 20.0
