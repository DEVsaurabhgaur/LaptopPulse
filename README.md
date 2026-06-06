# LaptopPulse

**Lightweight AI health monitor for your laptop.**  
Runs silently in the background. Tells you when to service it.  
No cloud. No data collection. 100% local.

![Status](https://img.shields.io/badge/status-beta-blue)
![Platform](https://img.shields.io/badge/platform-Windows%2010%2F11-0078d4)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11%2B-yellow)

---

## Why LaptopPulse?

Your laptop is slowly degrading and you don't know it. Dust builds up, thermal paste dries out, fan bearings wear — most laptops fail not because they're old, but because nobody serviced them. LaptopPulse monitors your laptop 24/7 using almost zero resources and generates a plain-language AI report when it detects a problem. No technical knowledge required.

## Features

- Silent background monitoring — uses **< 0.3% CPU**
- **Trend-based detection** — catches problems 30–60 days before failure
- **AI health reports** in plain language via Gemini (free) or Claude
- **Local dashboard** at `http://localhost:5747` — live metrics, health score, alerts
- **0–100 health score** with component breakdown (CPU, fan, battery, throttle)
- Works on **all Windows 10/11 laptops** — not brand-locked
- **100% local** — your data never leaves your machine
- Encrypted API key storage (AES-256-GCM)

## Quick Start

### 1 — Download & Install
Download `LaptopPulse-Setup.exe` from [Releases](../../releases).  
Run the installer. LaptopPulse starts automatically with Windows.

### 2 — Add a Free API Key (Gemini)
LaptopPulse uses Gemini Flash (free tier) by default.  
Get your key at <https://aistudio.google.com/apikey> — takes 30 seconds.

```
python save_gemini_key.py
```

Or enter it in **tray icon → Settings**.

> **Also supports Claude** — if a Claude key (`sk-ant-...`) is detected,  
> the app switches to Claude Sonnet automatically. Gemini is recommended  
> for cost (free tier covers ~500 reports/month).

### 3 — Install LibreHardwareMonitor
LaptopPulse reads CPU and fan temperatures via LibreHardwareMonitor (LHM).

1. Download from <https://github.com/LibreHardwareMonitor/LibreHardwareMonitor>
2. Run `LibreHardwareMonitor.exe` **as Administrator**
3. Enable: Options → Start Minimized + Run On Windows Startup

> Without LHM, the app falls back to the Windows ACPI thermal zone (less accurate).

## Dashboard

Open your live monitoring dashboard in any browser:

```
http://localhost:5747
```

Or right-click the tray icon → **Open Dashboard**.

The dashboard shows:
- Live health score (0–100) with colour band
- Real-time CPU temp, GPU temp, fan RPM, battery health
- Score breakdown by component
- Recent alerts and generated report links

## Build from Source

```bash
git clone https://github.com/saurabhgaur/laptoppulse
cd laptoppulse
pip install -r requirements.txt
python main.py
```

Run tests:
```bash
pytest tests/ -v
```

## Privacy

All data is stored locally at:
```
C:\Users\<you>\AppData\LocalLow\LaptopPulse\
```

No analytics. No telemetry. No accounts required.  
The only network call is to the AI API when a fault is detected —  
data sent: CPU model, GPU model, temperature deltas (no serials, no usernames).  
See [PRIVACY.md](PRIVACY.md) for the complete policy.

## Supported Hardware

| Component | Supported |
|---|---|
| CPU | Intel Core (all gen) / AMD Ryzen (all gen) |
| GPU Temperature | NVIDIA GeForce (nvidia-smi) / AMD via LHM |
| Fan RPM | All laptops with LHM support |
| OS | Windows 10 / Windows 11 (64-bit) |

## Architecture

Four-layer event-driven design — see [docs/architecture.md](docs/architecture.md).

| Layer | Runs | CPU Cost | Role |
|---|---|---|---|
| Silent Watcher | Always on | < 0.3% | Reads sensors every 60 s |
| Anomaly Detector | Always on | ~0% | Rules + trend engine |
| Log Store | Always on | ~0% | JSONL daily logs + SQLite events |
| AI Report Generator | Event only | 2–5% | Fires once on anomaly, then sleeps |

## License

MIT — free for personal use. See [LICENSE](LICENSE).

---

*Built by Saurabh Gaur — ASUS TUF A15 owner who got tired of surprise shutdowns.*
