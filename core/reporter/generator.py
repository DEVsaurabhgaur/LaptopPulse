"""
core/reporter/generator.py
---------------------------
Dual-API AI Report Generator — supports both Gemini and Anthropic Claude.
Auto-detects which API to use based on the saved key prefix:
  - AIza...  → Google Gemini 1.5 Flash (FREE tier — recommended)
  - sk-ant-  → Anthropic Claude Sonnet (paid, ~$0.003/report)

Priority: Gemini (free) → Claude (paid) → Offline template (no key)

Only fires when an anomaly is detected — not on every reading.
Enforces a 24-hour cooldown per rule to prevent report flooding.
Average usage: 1-2 reports/month for most laptops.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

from config.settings import cfg, get_app_dir, get_reports_dir
from core.detector.rules import Alert
from core.reporter.prompt import SYSTEM_PROMPT, build_prompt, get_offline_report
from core.reporter.html_render import render_html_report
from core.security.encryption import load_api_key

logger = logging.getLogger(__name__)


def _get_api_key() -> str | None:
    config_path = get_app_dir() / "config.enc"
    return load_api_key(config_path)


def _is_gemini_key(key: str) -> bool:
    """Google Gemini API keys start with 'AIza'."""
    return key.startswith("AIza")


def _is_claude_key(key: str) -> bool:
    """Anthropic Claude API keys start with 'sk-ant-'."""
    return key.startswith("sk-ant-")


# ── Gemini API ────────────────────────────────────────────────────────────────

def _call_gemini_api(system_prompt: str, user_prompt: str, api_key: str) -> str | None:
    """
    Call Google Gemini 1.5 Flash API.
    Free tier supports ~1500 requests/day — more than enough for LaptopPulse.
    Get your free key at: https://aistudio.google.com/apikey
    """
    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_prompt,
        )
        response = model.generate_content(user_prompt)

        # Safety check — response may be blocked by content filters
        if not response.parts:
            logger.error("Gemini returned empty response (possibly blocked by safety filter)")
            return None

        return response.text

    except ImportError:
        logger.error(
            "google-generativeai not installed. Run: pip install google-generativeai"
        )
        return None
    except Exception as e:
        logger.error("Gemini API call failed: %s", e)
        return None


# ── Claude API ────────────────────────────────────────────────────────────────

def _call_claude_api(system_prompt: str, user_prompt: str, api_key: str) -> str | None:
    """
    Call Anthropic Claude API (claude-sonnet-4-20250514).
    Cost: ~$0.003 per report. Fallback when Gemini key unavailable.
    Get your key at: https://console.anthropic.com
    """
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        model  = cfg.reporting.get("model", "claude-sonnet-4-20250514")
        tokens = cfg.reporting.get("max_tokens", 1500)

        message = client.messages.create(
            model=model,
            max_tokens=tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return message.content[0].text if message.content else None

    except ImportError:
        logger.error("anthropic not installed. Run: pip install anthropic")
        return None
    except Exception as e:
        logger.error("Claude API call failed: %s", e)
        return None


# ── Unified API caller ────────────────────────────────────────────────────────

def _call_ai_api(system_prompt: str, user_prompt: str, api_key: str) -> str | None:
    """
    Auto-detect and call the correct AI API based on the key prefix.
    Gemini (AIza...) → free tier, preferred.
    Claude (sk-ant-) → paid, fallback.
    Unknown prefix   → try Gemini first, then Claude.
    """
    if _is_gemini_key(api_key):
        logger.info("Using Gemini 1.5 Flash (free tier)")
        return _call_gemini_api(system_prompt, user_prompt, api_key)
    elif _is_claude_key(api_key):
        logger.info("Using Anthropic Claude API")
        return _call_claude_api(system_prompt, user_prompt, api_key)
    else:
        # Unknown key format — try both (Gemini first)
        logger.warning("Unknown API key format — trying Gemini then Claude")
        result = _call_gemini_api(system_prompt, user_prompt, api_key)
        if result:
            return result
        return _call_claude_api(system_prompt, user_prompt, api_key)


# ── Main report generator ─────────────────────────────────────────────────────

def generate_report(
    alert: Alert,
    system_info: dict,
    trends: dict,
) -> Path | None:
    """
    Generate an AI health report for the given alert.
    Saves as a dark-themed standalone HTML file in the reports/ directory.
    Returns the Path to the report file, or None on failure.

    Enforces cooldown: will not generate two reports for the same rule within 24 hours.
    If no API key is set, generates a quality offline templated report instead.
    """
    # ── Cooldown check ────────────────────────────────────────────────────────
    events_path = get_app_dir() / "events.json"
    events = _load_events(events_path)

    cooldown_h = cfg.reporting.get("report_cooldown_hours", 24)
    if _is_on_cooldown(events, alert.rule_id, cooldown_h):
        logger.info("Report cooldown active for %s — skipping", alert.rule_id)
        return None

    # ── Get report text (AI or offline) ──────────────────────────────────────
    api_key = _get_api_key()
    report_text = None

    if api_key:
        prompt = build_prompt(alert.rule_id, system_info, trends, alert.message)
        report_text = _call_ai_api(SYSTEM_PROMPT, prompt, api_key)
        if report_text:
            logger.info("AI report generated successfully (%d chars)", len(report_text))
        else:
            logger.warning("AI API call failed — falling back to offline template")
    else:
        logger.info("No API key set — using offline report template for %s", alert.rule_id)

    if not report_text:
        report_text = get_offline_report(alert.rule_id)

    # ── Render to HTML ────────────────────────────────────────────────────────
    report_path = _report_file_path(alert)
    html = render_html_report(
        report_text=report_text,
        alert=alert,
        system_info=system_info,
        trends=trends,
        generated_at=datetime.now(),
    )

    try:
        report_path.write_text(html, encoding="utf-8")
        logger.info("Report saved: %s", report_path)
    except Exception as e:
        logger.error("Failed to save report: %s", e)
        return None

    # ── Record event for cooldown tracking ────────────────────────────────────
    _record_event(events_path, events, alert)

    return report_path


# ── Helpers ───────────────────────────────────────────────────────────────────

def _report_file_path(alert: Alert) -> Path:
    date_str = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"{date_str}_{alert.rule_id.lower()}_report.html"
    return get_reports_dir() / filename


def _load_events(events_path: Path) -> list:
    if not events_path.exists():
        return []
    try:
        return json.loads(events_path.read_text(encoding="utf-8"))
    except Exception:
        return []


def _record_event(events_path: Path, events: list, alert: Alert) -> None:
    events.append({
        "rule_id":   alert.rule_id,
        "severity":  alert.severity.value,
        "timestamp": datetime.now().isoformat(),
    })
    events = events[-500:]  # Keep last 500 events only
    try:
        events_path.write_text(json.dumps(events, indent=2), encoding="utf-8")
    except Exception as e:
        logger.error("Failed to record event: %s", e)


def _is_on_cooldown(events: list, rule_id: str, cooldown_hours: int) -> bool:
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(hours=cooldown_hours)
    for event in reversed(events):
        if event.get("rule_id") == rule_id:
            try:
                ts = datetime.fromisoformat(event["timestamp"])
                if ts > cutoff:
                    return True
            except Exception:
                pass
            break
    return False
