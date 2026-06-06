# Changelog

All notable changes to LaptopPulse are documented here.

---

## [1.1.0] — 2026-06-04 — Dual API + Bug Fixes

### Added
- **Dual AI API support**: Auto-detects key type and uses Gemini (free) or Claude (paid)
  - Google Gemini 1.5 Flash: Free tier, 1500 req/day
  - Anthropic Claude Sonnet: Paid fallback (~₹0.25/report)
- `save_gemini_key.py` — guided setup wizard for Gemini free tier
- `--setup-key` now accepts both Gemini (`AIza...`) and Claude (`sk-ant-...`) keys
- Environment variable fallbacks: `GEMINI_API_KEY`, `GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`
- `config/defaults.json`: added `api_provider: "auto"` and `gemini_model` fields

### Fixed
- **Critical**: `save_api_key()` argument order bug in Gemini key setup (was reversed)
- `load_api_key()` now checks both Gemini and Claude env vars (previously Claude only)
- `config_path.parent.mkdir()` added to `save_api_key()` to prevent path errors

### Changed
- `main.py` version bumped to 1.1.0
- `.env.example` updated with both API key options documented
- `requirements.txt` now includes both `anthropic` and `google-generativeai`

---

## [1.0.0] — 2026-06-03 — Initial Release

### Added
- Silent background monitoring daemon (CPU, GPU, fan, battery)
- Threshold detection: CPU/GPU critical temps, fan failure, thermal throttle
- Trend detection: 30/45/60-day rolling averages vs baseline
- AI report generation via Anthropic Claude API
- Offline fallback templates (no API key required)
- AES-256-GCM encrypted API key storage (machine-bound)
- Dark-themed standalone HTML health reports
- System tray icon (green/yellow/red status)
- Windows Service installer/uninstaller
- pytest test suite
