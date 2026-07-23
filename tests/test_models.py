from src.models.system_metrics import CpuMetrics
def test_cpu_model():
    m = CpuMetrics(15.5, 8, 3200.0)
    assert m.core_count == 8
