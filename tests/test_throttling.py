from src.core.throttling_check import is_thermal_throttling
def test_throttling():
    assert is_thermal_throttling(96.0)
