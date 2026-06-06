# LaptopPulse — System Architecture

## 4-Layer Design

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1: Silent Watcher Daemon              < 0.3% CPU │
│  core/watcher.py                                        │
│  • Wakes every 60 seconds                               │
│  • Reads CPU / GPU / Fan / Battery sensors              │
│  • Writes single JSON line to daily log                 │
│  • Sleeps until next tick                               │
└─────────────────────────────┬───────────────────────────┘
                              │ metrics dict
┌─────────────────────────────▼───────────────────────────┐
│  LAYER 2: Anomaly Detector                    ~0% CPU   │
│  core/detector/threshold.py + trend.py                  │
│  • Threshold rules: fires on single reading             │
│  • Trend rules: 30/60/90-day rolling average vs baseline│
│  • Returns list[Alert] — empty = all clear              │
└─────────────────────────────┬───────────────────────────┘
                              │ alerts[]
┌─────────────────────────────▼───────────────────────────┐
│  LAYER 3: Log Accumulator                     ~0% CPU   │
│  core/storage/ (logger, baseline, trends_calc)          │
│  • JSONL daily files (~4KB/day)                         │
│  • Auto-deletes files > 90 days                         │
│  • Baseline: first 7-day snapshot                       │
│  • Trends: daily rolling average update                 │
└─────────────────────────────┬───────────────────────────┘
                              │ triggers only on anomaly
┌─────────────────────────────▼───────────────────────────┐
│  LAYER 4: AI Report Generator           2-5% CPU briefly│
│  core/reporter/ (generator, prompt, html_render)        │
│  • Fires ONCE per anomaly (24h cooldown)                │
│  • Calls Claude API with sanitised hardware data        │
│  • Renders dark-themed standalone HTML report           │
│  • Notifies user via system tray + Windows notification │
└─────────────────────────────────────────────────────────┘
```

## Data Flow

```
nvidia-smi ──┐
LibreHWMon ──┤──► watcher.py ──► logger.py ──► 2026-06-01.jsonl
psutil     ──┘         │
                       ▼
                  threshold.py ──► Alert(CPU_CRITICAL)
                  trend.py     ──► Alert(IDLE_TEMP_RISE)
                       │
                       ▼
                  generator.py ──► Claude API ──► HTML report
                       │
                       ▼
                  tray.py (red icon + notification)
```

## Key Design Decisions

**Why JSONL not SQLite?**
Each day produces ~4KB. Python's built-in json reads it instantly.
No database overhead for a file that small. Simple, portable, debuggable.

**Why event-driven AI (not always-on)?**
Claude API costs ~$0.003/report. An always-on LLM would cost $0.003 × 1440 = $4.32/day.
Event-driven: ~$0.006-0.009/day (1-2 reports average). 99.8% cost reduction.

**Why AES-256-GCM not AES-256-CBC?**
GCM provides authenticated encryption — it detects tampering.
If malware modifies a log file, GCM decryption raises InvalidTag.
CBC only provides confidentiality, not integrity.
