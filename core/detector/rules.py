"""
core/detector/rules.py
-----------------------
All anomaly rule definitions and the Alert dataclass.
Single source of truth — threshold.py and trend.py both use these definitions.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional


class Severity(str, Enum):
    INFO      = "INFO"       # Informational — no urgent action needed
    WARN      = "WARN"       # Warning — plan maintenance soon
    URGENT    = "URGENT"     # Do within 1-2 weeks
    IMMEDIATE = "IMMEDIATE"  # Act now — risk of damage or data loss


class RuleType(str, Enum):
    THRESHOLD = "THRESHOLD"  # Instant: single reading exceeds limit
    TREND     = "TREND"      # Slow: change over days/weeks


@dataclass
class Alert:
    """Represents a detected anomaly."""
    rule_id: str                        # e.g. "CPU_CRITICAL"
    rule_type: RuleType
    severity: Severity
    title: str                          # Short title for report header
    message: str                        # Human-readable explanation
    value: float                        # The triggering value
    threshold: float                    # The limit that was crossed
    timestamp: datetime = field(default_factory=datetime.now)
    extra: Optional[dict] = None        # Additional context for AI prompt

    def to_dict(self) -> dict:
        return {
            "rule_id":    self.rule_id,
            "rule_type":  self.rule_type.value,
            "severity":   self.severity.value,
            "title":      self.title,
            "message":    self.message,
            "value":      self.value,
            "threshold":  self.threshold,
            "timestamp":  self.timestamp.isoformat(),
            "extra":      self.extra,
        }


# ── Rule Definitions ──────────────────────────────────────────────────────────
# Each rule: (rule_id, severity, title, message_template)

THRESHOLD_RULES = {
    "CPU_CRITICAL": {
        "severity": Severity.IMMEDIATE,
        "title": "CPU Temperature Critical",
        "message": "CPU temperature reached {value}°C — above safe limit of {threshold}°C. Immediate shutdown risk.",
    },
    "CPU_WARNING": {
        "severity": Severity.URGENT,
        "title": "CPU Temperature Warning",
        "message": "CPU temperature is {value}°C — sustained operation above {threshold}°C causes performance throttling.",
    },
    "GPU_CRITICAL": {
        "severity": Severity.IMMEDIATE,
        "title": "GPU Temperature Critical",
        "message": "GPU temperature reached {value}°C — above safe limit of {threshold}°C. Risk of permanent GPU damage.",
    },
    "GPU_WARNING": {
        "severity": Severity.URGENT,
        "title": "GPU Temperature Warning",
        "message": "GPU temperature is {value}°C — sustained operation above {threshold}°C reduces GPU lifespan.",
    },
    "FAN_DEAD": {
        "severity": Severity.IMMEDIATE,
        "title": "Fan May Have Failed",
        "message": "Fan speed dropped to {value} RPM under load — below minimum threshold of {threshold} RPM. Possible fan failure.",
    },
    "FAN_SLOW": {
        "severity": Severity.URGENT,
        "title": "Fan Running Slowly",
        "message": "Fan speed is {value} RPM under load — below expected {threshold} RPM. Bearing wear suspected.",
    },
    "CPU_THROTTLE": {
        "severity": Severity.URGENT,
        "title": "CPU Thermal Throttling Detected",
        "message": "CPU clock dropped {value}% below boost speed — the processor is throttling due to heat. Performance is degraded right now.",
    },
    "BATTERY_CRITICAL": {
        "severity": Severity.INFO,
        "title": "Battery Health Low",
        "message": "Battery holds only {value}% of its original capacity. Replacement recommended when below {threshold}%.",
    },
}

TREND_RULES = {
    "IDLE_TEMP_RISE_WARN": {
        "severity": Severity.WARN,
        "title": "CPU Temperature Rising (30-Day Trend)",
        "message": "CPU idle temperature has increased by {value}°C over the past 30 days. Early sign of dust buildup or thermal paste degradation.",
    },
    "IDLE_TEMP_RISE_CRITICAL": {
        "severity": Severity.URGENT,
        "title": "CPU Temperature Rising Fast",
        "message": "CPU idle temperature has increased by {value}°C over 30 days. Thermal paste failure or heavy dust buildup likely.",
    },
    "FAN_RPM_DECLINE": {
        "severity": Severity.WARN,
        "title": "Fan Speed Declining (60-Day Trend)",
        "message": "Fan RPM has decreased {value}% over 60 days compared to baseline. Fan bearing wear in progress.",
    },
    "TEMP_TREND_URGENT": {
        "severity": Severity.URGENT,
        "title": "Severe Temperature Increase Detected",
        "message": "CPU temperature has risen {value}°C over 45 days. Combined dust accumulation and thermal paste degradation likely.",
    },
}

ALL_RULES = {**THRESHOLD_RULES, **TREND_RULES}
