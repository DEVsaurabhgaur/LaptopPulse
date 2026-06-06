# Contributing to LaptopPulse

Thanks for your interest in contributing! LaptopPulse is open source and welcomes PRs.

## Quick Setup

```bash
git clone https://github.com/saurabhgaur/laptoppulse
cd laptoppulse
pip install -r requirements.txt
pytest tests/ -v    # All tests should pass
python main.py --debug
```

## Development Rules

1. **Run tests before every commit:** `pytest tests/ -v`
2. **One function = one responsibility** (Single Responsibility Principle)
3. **No hardcoded paths** — use `config.settings.get_app_dir()`
4. **No secrets in code** — use `.env` and encryption module
5. **No debug print() statements** — use `logging` module
6. **Privacy first** — never log user identifiers, only numeric hardware data

## Adding a New Sensor

1. Create `core/sensors/your_sensor.py` with a `@dataclass` result and `read_*()` function
2. Add it to `core/watcher.py → collect_metrics()`
3. Add tests in `tests/test_sensors.py`
4. Update `core/storage/logger.py → _ALLOWED_KEYS` if storing new fields

## Adding a New Detection Rule

1. Add rule definition to `core/detector/rules.py → THRESHOLD_RULES` or `TREND_RULES`
2. Implement check function in `threshold.py` or `trend.py`
3. Add to `run_all_*_checks()` in the respective file
4. Add offline report template in `core/reporter/prompt.py → OFFLINE_TEMPLATES`
5. Write unit tests in `tests/test_detector.py`

## Submitting a PR

- One feature or fix per PR
- All tests passing
- Update CHANGELOG.md under `[Unreleased]`
- Screenshots for any UI changes
