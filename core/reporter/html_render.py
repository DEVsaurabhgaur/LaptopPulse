"""
core/reporter/html_render.py
-----------------------------
Renders the AI report text as a standalone dark-themed HTML file.
Self-contained — no external CSS/JS dependencies.
Works offline. Looks professional. Opens in any browser.
"""

from datetime import datetime
from core.detector.rules import Alert, Severity

# Severity badge colors
_SEVERITY_COLORS = {
    Severity.IMMEDIATE: ("#ff4444", "#fff0f0"),
    Severity.URGENT:    ("#ff8800", "#fff8f0"),
    Severity.WARN:      ("#f5c518", "#fffbf0"),
    Severity.INFO:      ("#4caf50", "#f0fff4"),
}

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>LaptopPulse Health Report — {date}</title>
<style>
  :root {{
    --bg:       #0f1117;
    --surface:  #1a1d27;
    --border:   #2a2d3a;
    --text:     #e8eaf0;
    --muted:    #8890a4;
    --accent:   {accent_color};
    --accent-bg:{accent_bg};
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    padding: 0;
    margin: 0;
  }}
  .wrapper {{ max-width: 720px; margin: 0 auto; padding: 32px 24px 64px; }}

  /* Header */
  .header {{ border-bottom: 1px solid var(--border); padding-bottom: 24px; margin-bottom: 32px; }}
  .brand {{ font-size: 13px; font-weight: 600; letter-spacing: 0.12em;
            color: var(--muted); text-transform: uppercase; margin-bottom: 8px; }}
  .device {{ font-size: 15px; color: var(--muted); margin-top: 4px; }}
  .report-date {{ font-size: 13px; color: var(--muted); margin-top: 2px; }}

  /* Status badge */
  .status-badge {{
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--accent-bg); border: 1px solid var(--accent);
    color: var(--accent); border-radius: 6px;
    padding: 8px 16px; font-weight: 700; font-size: 14px;
    text-transform: uppercase; letter-spacing: 0.08em; margin: 16px 0 24px;
  }}
  .status-dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--accent); }}

  /* Sections */
  .section {{ margin-bottom: 28px; }}
  .section-title {{
    font-size: 11px; font-weight: 700; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--muted);
    margin-bottom: 10px; padding-bottom: 6px;
    border-bottom: 1px solid var(--border);
  }}
  .section-body {{ font-size: 15px; color: var(--text); white-space: pre-line; }}

  /* Metric cards */
  .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                   gap: 12px; margin: 16px 0; }}
  .metric-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 8px; padding: 14px 16px;
  }}
  .metric-label {{ font-size: 11px; color: var(--muted); text-transform: uppercase;
                   letter-spacing: 0.1em; margin-bottom: 4px; }}
  .metric-value {{ font-size: 22px; font-weight: 700; color: var(--text); }}
  .metric-unit  {{ font-size: 12px; color: var(--muted); }}

  /* Report body card */
  .report-card {{
    background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 28px; margin-top: 8px;
  }}
  .report-section {{ margin-bottom: 22px; }}
  .report-section:last-child {{ margin-bottom: 0; }}
  .report-section h3 {{
    font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--accent);
    margin-bottom: 8px;
  }}
  .report-section p {{ font-size: 15px; color: var(--text); line-height: 1.75; }}

  /* Footer */
  .footer {{
    margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border);
    font-size: 12px; color: var(--muted); text-align: center;
  }}
  .footer a {{ color: var(--muted); text-decoration: none; }}
  .footer a:hover {{ color: var(--text); }}
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <div class="brand">&#128297; LaptopPulse Health Report</div>
    <div class="device">{device_model} &nbsp;·&nbsp; {cpu}</div>
    <div class="report-date">Generated: {datetime_str}</div>
  </div>

  <div class="status-badge">
    <span class="status-dot"></span>
    {severity_label}
  </div>

  <div class="metrics-grid">
    {metric_cards}
  </div>

  <div class="report-card">
    {report_sections_html}
  </div>

  <div class="footer">
    <p>LaptopPulse v1.0 &nbsp;·&nbsp; All data stored locally on your machine &nbsp;·&nbsp;
    <a href="https://github.com/saurabhgaur/laptoppulse">github.com/saurabhgaur/laptoppulse</a></p>
  </div>

</div>
</body>
</html>
"""


def _make_metric_card(label: str, value, unit: str = "") -> str:
    val_str = str(value) if value is not None else "N/A"
    return (
        f'<div class="metric-card">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value">{val_str}<span class="metric-unit"> {unit}</span></div>'
        f'</div>'
    )


def _parse_report_sections(report_text: str) -> str:
    """
    Parse the AI report text into styled HTML sections.
    Expects headings like: WHAT IS HAPPENING, WHY THIS HAPPENED, etc.
    """
    headings = [
        "WHAT IS HAPPENING",
        "WHY THIS HAPPENED",
        "URGENCY",
        "FIX IT YOURSELF",
        "SERVICE CENTER OPTION",
        "NEXT CHECK",
    ]

    sections_html = ""
    current_heading = None
    current_body = []

    for line in report_text.splitlines():
        stripped = line.strip()
        matched = next((h for h in headings if stripped.upper().startswith(h)), None)
        if matched:
            if current_heading and current_body:
                body = "\n".join(current_body).strip()
                sections_html += (
                    f'<div class="report-section">'
                    f'<h3>{current_heading}</h3>'
                    f'<p>{body}</p>'
                    f'</div>'
                )
            current_heading = matched
            current_body = []
        else:
            if current_heading and stripped:
                current_body.append(stripped)

    # Last section
    if current_heading and current_body:
        body = "\n".join(current_body).strip()
        sections_html += (
            f'<div class="report-section">'
            f'<h3>{current_heading}</h3>'
            f'<p>{body}</p>'
            f'</div>'
        )

    return sections_html if sections_html else f'<div class="report-section"><p>{report_text}</p></div>'


def render_html_report(
    report_text: str,
    alert: Alert,
    system_info: dict,
    trends: dict,
    generated_at: datetime,
) -> str:
    """
    Render a complete standalone HTML report.
    Returns the HTML string — caller writes it to disk.
    """
    accent_color, accent_bg = _SEVERITY_COLORS.get(alert.severity, ("#f5c518", "#fffbf0"))

    t30 = trends.get("30d", {})

    metric_cards = "".join([
        _make_metric_card("CPU Avg Temp",  t30.get("cpu_idle_avg"), "°C"),
        _make_metric_card("GPU Avg Temp",  t30.get("gpu_temp_avg"), "°C"),
        _make_metric_card("Fan Speed",     t30.get("fan_rpm_avg"),  "RPM"),
        _make_metric_card("Throttle Events", t30.get("throttle_count", 0), "/ 30d"),
    ])

    severity_labels = {
        Severity.IMMEDIATE: "⛔ IMMEDIATE ACTION REQUIRED",
        Severity.URGENT:    "⚠ ACTION NEEDED",
        Severity.WARN:      "⚡ WARNING — PLAN MAINTENANCE",
        Severity.INFO:      "ℹ INFO — MONITOR THIS",
    }

    return _HTML_TEMPLATE.format(
        date             = generated_at.strftime("%B %d, %Y"),
        datetime_str     = generated_at.strftime("%B %d, %Y at %I:%M %p"),
        device_model     = system_info.get("model", "Unknown Laptop"),
        cpu              = system_info.get("cpu", "Unknown CPU"),
        accent_color     = accent_color,
        accent_bg        = accent_bg,
        severity_label   = severity_labels.get(alert.severity, "STATUS"),
        metric_cards     = metric_cards,
        report_sections_html = _parse_report_sections(report_text),
    )
