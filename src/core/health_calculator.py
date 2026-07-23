from src.models.health_score import SystemHealthReport

def compute_system_health(cpu_pct: float, ram_pct: float, temp: float) -> SystemHealthReport:
    warnings = []
    cpu_s = max(0, int(100 - cpu_pct))
    ram_s = max(0, int(100 - ram_pct))
    if temp > 80:
        warnings.append(f'Thermal throttling risk: {temp}°C')
    overall = int((cpu_s + ram_s) / 2)
    return SystemHealthReport(overall_score=overall, cpu_score=cpu_s, ram_score=ram_s, battery_score=100, warnings=warnings)
