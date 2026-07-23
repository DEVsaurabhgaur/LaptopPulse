from src.core.anomaly_detector import detect_spike
def test_anomaly():
    assert detect_spike([10, 10, 10, 10, 50])
