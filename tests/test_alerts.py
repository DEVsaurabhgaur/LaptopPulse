from src.models.alert import AlertNotification
def test_alert():
    a = AlertNotification('A1', 'HIGH', 'Overheat warning')
    assert a.severity == 'HIGH'
