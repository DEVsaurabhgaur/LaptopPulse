"""
core/health_score.py
---------------------
Computes a 0-100 health score from live sensor metrics and active alerts.

Score composition (100 points total):
  cpu_temp  — 40 pts   fan_rpm  — 25 pts
  battery   — 20 pts   throttle — 15 pts

Alert penalties (applied after weighted score):
  IMMEDIATE: -20   URGENT: -10   WARN: -5

Score bands:
  85-100  Healthy        (green)
  65-84   Monitor        (yellow)
  45-64   Service Soon   (orange)
  0-44    Action Required(red)

All band thresholds are configurable via config/defaults.json
under the "health_score" key.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class HealthScore:
    score:       int              # 0-100
    band:        str              # "Healthy" | "Monitor" | "Service Soon" | "Action Required"
    band_color:  str              # "green" | "yellow" | "orange" | "red"
    factors:     dict             # per-component breakdown for dashboard
    penalties:   list[str]        # human-readable alert penalty reasons


# --- Band thresholds (defaults — overridden by cfg if available) --------------

_DEFAULT_WEIGHTS = {"cpu_temp": 40, "fan_rpm": 25, "battery": 20, "throttle": 15}
_DEFAULT_CPU_BANDS  = {"healthy": 70,   "warn": 80,  "urgent": 89}
_DEFAULT_FAN_BANDS  = {"healthy": 1200, "warn": 800, "critical": 200}
_DEFAULT_BAT_BANDS  = {"healthy": 80,   "warn": 60,  "critical": 40}
_DEFAULT_PENALTIES  = {"IMMEDIATE": 20, "URGENT": 10, "WARN": 5, "INFO": 0}
_DEFAULT_SCORE_BANDS = {"healthy": 85,  "monitor": 65, "service": 45}


def _load_cfg() -> dict:
    """Load health_score section from config. Falls back to defaults."""
    try:
        from config.settings import cfg
        return cfg.raw.get("health_score", {})
    except Exception:
        return {}


# --- Component scorers --------------------------------------------------------

def _score_cpu_temp(
    temp: Optional[float],
    weight: int,
    bands: dict,
) -> tuple[int, str]:
    """
    Returns (points_earned, description).
    Full weight if temp <= healthy band, zero if >= urgent band.
    """
    if temp is None:
        # Unknown — neutral penalty: award 80% to avoid unfair punishment
        pts = int(weight * 0.80)
        return pts, "N/A (sensor unavailable)"

    h, w, u = bands["healthy"], bands["warn"], bands["urgent"]
    t = float(temp)

    if t <= h:
        pts, desc = weight,          f"{t:.0f}°C (Normal)"
    elif t <= w:
        frac = 1.0 - 0.25 * (t - h) / (w - h)
        pts  = int(weight * frac)
        desc = f"{t:.0f}°C (Warm)"
    elif t <= u:
        frac = 0.75 - 0.62 * (t - w) / (u - w)
        pts  = max(0, int(weight * frac))
        desc = f"{t:.0f}°C (Hot)"
    else:
        pts, desc = 0, f"{t:.0f}°C (Critical)"

    return pts, desc


def _score_fan_rpm(
    rpm: Optional[int],
    weight: int,
    bands: dict,
) -> tuple[int, str]:
    """
    Returns (points_earned, description).
    Zero RPM under load is immediately critical (fan dead).
    """
    if rpm is None:
        pts = int(weight * 0.80)   # neutral — sensor not available
        return pts, "N/A (no fan sensor)"

    h, w, c = bands["healthy"], bands["warn"], bands["critical"]
    r = int(rpm)

    if r >= h:
        pts, desc = weight,          f"{r} RPM (Good)"
    elif r >= w:
        frac = 0.70 + 0.30 * (r - w) / (h - w)
        pts  = int(weight * frac)
        desc = f"{r} RPM (Low)"
    elif r >= c:
        frac = 0.30 * (r - c) / (w - c)
        pts  = int(weight * frac)
        desc = f"{r} RPM (Very Low)"
    else:
        pts, desc = 0, f"{r} RPM (Critical / Possible Fan Failure)"

    return pts, desc


def _score_battery(
    health_pct: Optional[float],
    weight: int,
    bands: dict,
) -> tuple[int, str]:
    """
    Returns (points_earned, description).
    Uses battery health percentage (capacity vs design capacity).
    """
    if health_pct is None:
        pts = int(weight * 0.85)
        return pts, "N/A (no battery data)"

    h, w, c = bands["healthy"], bands["warn"], bands["critical"]
    p = float(health_pct)

    if p >= h:
        pts, desc = weight,          f"{p:.0f}% capacity (Good)"
    elif p >= w:
        frac = 0.75 + 0.25 * (p - w) / (h - w)
        pts  = int(weight * frac)
        desc = f"{p:.0f}% capacity (Degraded)"
    elif p >= c:
        frac = 0.40 * (p - c) / (w - c)
        pts  = int(weight * frac)
        desc = f"{p:.0f}% capacity (Low)"
    else:
        pts, desc = 0, f"{p:.0f}% capacity (Replace Battery)"

    return pts, desc


def _score_throttle(
    is_throttling: bool,
    weight: int,
) -> tuple[int, str]:
    """Full weight when not throttling, zero when throttling."""
    if is_throttling:
        return 0, "Throttling detected (overheating)"
    return weight, "Not throttling"


# --- Band classifier ----------------------------------------------------------

def _classify(score: int, bands: dict) -> tuple[str, str]:
    """Returns (band_name, band_color) from a final score."""
    h, m, s = bands["healthy"], bands["monitor"], bands["service"]
    if score >= h:
        return "Healthy",          "green"
    elif score >= m:
        return "Monitor",          "yellow"
    elif score >= s:
        return "Service Soon",     "orange"
    else:
        return "Action Required",  "red"


# --- Public API ---------------------------------------------------------------

def compute(metrics: dict, alerts: list) -> HealthScore:
    """
    Compute a HealthScore from the current metrics dict and active alert list.

    metrics keys used:
      cpu_temp, fan_rpm, battery_health_pct, is_throttling

    alerts: list of Alert dataclass instances (from core.detector.rules).
    """
    hs_cfg     = _load_cfg()
    weights    = {**_DEFAULT_WEIGHTS,  **hs_cfg.get("weights", {})}
    cpu_bands  = {**_DEFAULT_CPU_BANDS, **hs_cfg.get("cpu_temp_bands", {})}
    fan_bands  = {**_DEFAULT_FAN_BANDS, **hs_cfg.get("fan_rpm_bands", {})}
    bat_bands  = {**_DEFAULT_BAT_BANDS, **hs_cfg.get("battery_health_bands", {})}
    penalties  = {**_DEFAULT_PENALTIES, **hs_cfg.get("alert_penalties", {})}
    sb         = {**_DEFAULT_SCORE_BANDS, **hs_cfg.get("score_bands", {})}

    # Component scores
    cpu_pts,  cpu_desc  = _score_cpu_temp(
        metrics.get("cpu_temp"),
        weights["cpu_temp"],
        cpu_bands,
    )
    fan_pts,  fan_desc  = _score_fan_rpm(
        metrics.get("fan_rpm"),
        weights["fan_rpm"],
        fan_bands,
    )
    bat_pts,  bat_desc  = _score_battery(
        metrics.get("battery_health_pct"),
        weights["battery"],
        bat_bands,
    )
    thr_pts,  thr_desc  = _score_throttle(
        bool(metrics.get("is_throttling", False)),
        weights["throttle"],
    )

    raw_score = cpu_pts + fan_pts + bat_pts + thr_pts

    # Alert penalties
    penalty_reasons: list[str] = []
    total_penalty = 0
    for alert in alerts:
        sev_name = alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity)
        pen = penalties.get(sev_name, 0)
        if pen > 0:
            total_penalty += pen
            penalty_reasons.append(f"-{pen}: {alert.title}")

    final_score = max(0, min(100, raw_score - total_penalty))
    band, color = _classify(final_score, sb)

    logger.debug(
        "HealthScore: %d (cpu=%d fan=%d bat=%d thr=%d penalty=%d) => %s",
        final_score, cpu_pts, fan_pts, bat_pts, thr_pts, total_penalty, band,
    )

    return HealthScore(
        score=final_score,
        band=band,
        band_color=color,
        factors={
            "cpu_temp":  {"points": cpu_pts,  "max": weights["cpu_temp"],  "detail": cpu_desc},
            "fan_rpm":   {"points": fan_pts,  "max": weights["fan_rpm"],   "detail": fan_desc},
            "battery":   {"points": bat_pts,  "max": weights["battery"],   "detail": bat_desc},
            "throttle":  {"points": thr_pts,  "max": weights["throttle"],  "detail": thr_desc},
        },
        penalties=penalty_reasons,
    )
