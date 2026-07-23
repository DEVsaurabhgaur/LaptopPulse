from src.core.health_calculator import compute_system_health
def test_health():
    report = compute_system_health(20.0, 40.0, 65.0)
    assert report.overall_score == 70
    assert len(report.warnings) == 0
