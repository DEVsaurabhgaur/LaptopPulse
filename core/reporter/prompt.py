"""
core/reporter/prompt.py
------------------------
Prompt templates for each anomaly category.
Designed to produce plain-language reports for NON-TECHNICAL users.
Always structured: What | Why | Urgency | DIY Fix | Service Option.
"""


SYSTEM_PROMPT = """You are a friendly laptop hardware technician writing a health report for a regular, non-technical user.

RULES:
- Write in plain English. Zero jargon. A 14-year-old must understand.
- Be honest but not alarmist. Explain calmly.
- Always include: what is happening, why it happened, how urgent it is, what to do.
- DIY steps must be specific — exact tool names, costs in Indian Rupees (INR).
- Keep total report under 400 words.
- Do NOT use markdown. Use plain text with clear sections.
- Output ONLY the report content. No preamble, no "Sure!" or "Here's the report:".
"""


def build_prompt(anomaly_type: str, system_info: dict, trends: dict, alert_message: str) -> str:
    """
    Build the full prompt for AI report generation.
    Injects real monitoring data — AI diagnoses, not guesses.
    """
    t30 = trends.get("30d", {})

    prompt = f"""Generate a laptop health report for the user below.

LAPTOP INFORMATION:
- Model      : {system_info.get('model', 'Unknown')}
- CPU        : {system_info.get('cpu', 'Unknown')}
- GPU        : {system_info.get('gpu', 'Unknown')}
- OS         : {system_info.get('os', 'Windows 11')}
- Age        : {system_info.get('age_months', 'Unknown')} months old

30-DAY MONITORING DATA:
- CPU idle temperature (avg) : {t30.get('cpu_idle_avg', 'N/A')}°C
- CPU load temperature (avg) : {t30.get('cpu_temp_avg', 'N/A')}°C
- GPU temperature (avg)      : {t30.get('gpu_temp_avg', 'N/A')}°C
- Fan speed (avg)            : {t30.get('fan_rpm_avg', 'N/A')} RPM
- CPU throttle events        : {t30.get('throttle_count', 0)} times in last 30 days
- Average CPU usage          : {t30.get('cpu_load_avg', 'N/A')}%

DETECTED PROBLEM:
{alert_message}

Write the report with these sections (use these exact headings):

WHAT IS HAPPENING
[2-3 sentences in plain English]

WHY THIS HAPPENED
[2-3 sentences — explain the root cause simply]

URGENCY
[One of: "Can Wait (next 1-2 months)" / "Do Soon (within 2 weeks)" / "Do Now (within 48 hours)"]
[One sentence explaining the consequence of waiting]

FIX IT YOURSELF
[Numbered steps. Be specific: tool names, cost in INR, time required]

SERVICE CENTER OPTION
[Estimated cost in INR. What service to ask for specifically.]

NEXT CHECK
[When LaptopPulse will re-evaluate this issue]
"""
    return prompt


# ── Offline fallback templates (no API key needed) ────────────────────────────

OFFLINE_TEMPLATES = {
    "CPU_CRITICAL": """WHAT IS HAPPENING
Your laptop's processor is running dangerously hot right now. This is causing it to slow down to protect itself from damage.

WHY THIS HAPPENED
The cooling system cannot remove heat fast enough. The most common causes are dust blocking the vents or dried-out thermal paste on the processor.

URGENCY
Do Now (within 48 hours)
Continuing to use the laptop at this temperature risks permanent CPU damage.

FIX IT YOURSELF
1. Stop heavy tasks immediately and let laptop cool for 30 minutes
2. Make sure laptop is on a hard flat surface — not on a bed or pillow
3. Buy compressed air can (Rs. 200-400) and spray into all vents
4. If problem continues, open bottom panel and clean fan blades

SERVICE CENTER OPTION
Full thermal cleaning + thermal paste replacement: Rs. 800-1,500
Ask for: "full internal cleaning and thermal paste reapplication"

NEXT CHECK
LaptopPulse will monitor temperatures over the next 7 days after cleaning.""",

    "IDLE_TEMP_RISE_CRITICAL": """WHAT IS HAPPENING
Your laptop is running hotter than it did when first monitored. The temperature has been slowly rising over the past month, even when the laptop is just sitting idle.

WHY THIS HAPPENED
Dust has built up inside your laptop's cooling vents. This is completely normal after 12-18 months of use. The dust acts like a blanket, trapping heat inside. The thermal paste between the processor and cooler may also be drying out.

URGENCY
Do Soon (within 2 weeks)
The temperature will keep rising if not addressed. Early action prevents more expensive damage.

FIX IT YOURSELF
1. Buy compressed air can — Rs. 200-400 (available at any computer accessories shop)
2. Power off laptop completely and unplug it
3. Hold can upright, spray into all vents for 5-10 seconds each
4. For deep cleaning: open bottom panel (usually 2 screws), carefully clean fan blades with a dry brush
5. Estimated time: 15-30 minutes

SERVICE CENTER OPTION
Full internal cleaning + thermal paste replacement: Rs. 800-1,500
Ask for: "full thermal service" at any local laptop repair shop

NEXT CHECK
LaptopPulse will check your temperature trend again in 30 days.""",

    "FAN_DEAD": """WHAT IS HAPPENING
Your laptop's cooling fan has stopped spinning or is barely moving, even when the laptop is working hard. Without the fan, heat builds up very quickly.

WHY THIS HAPPENED
Fan motors wear out over time. The fan bearing may have failed, or the fan may be physically blocked by dust.

URGENCY
Do Now (within 48 hours)
A laptop without cooling can reach damaging temperatures in minutes under load.

FIX IT YOURSELF
1. Power off laptop immediately
2. Do NOT use until fan is fixed
3. Try spraying compressed air into vents — sometimes removes a blockage

SERVICE CENTER OPTION
Fan replacement: Rs. 500-1,200 depending on laptop model
Ask for: "cooling fan replacement"

NEXT CHECK
After fan replacement, LaptopPulse will verify normal RPM within 24 hours.""",
}


def get_offline_report(rule_id: str) -> str:
    """Return a pre-written offline report for common rule types."""
    return OFFLINE_TEMPLATES.get(rule_id, OFFLINE_TEMPLATES["IDLE_TEMP_RISE_CRITICAL"])
