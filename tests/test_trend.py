from src.core.trend_analyzer import calculate_rolling_average
def test_trend():
    assert calculate_rolling_average([10.0, 20.0, 30.0]) == 20.0
