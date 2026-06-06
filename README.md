<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:00ff9f,50:00d4ff,100:0a0a14&height=180&section=header&text=LAPTOPPULSE&fontSize=56&fontFamily=Share%20Tech%20Mono&fontColor=ffffff&fontAlignY=40&desc=AI%20Health%20Monitor%20for%20Your%20Laptop&descAlignY=62&descSize=15&descColor=00d4ff&animation=fadeIn" width="100%"/>

[![Typing SVG](https://readme-typing-svg.demolab.com?font=Share+Tech+Mono&size=13&duration=3500&pause=800&color=00FF9F&center=true&vCenter=true&width=580&lines=Silent+background+monitoring+%E2%80%94+%3C+0.3%25+CPU.;Trend-based+detection+%E2%80%94+30-60+days+early+warning.;AI+health+reports+in+plain+language.;100%25+local.+No+cloud.+No+accounts.+No+BS.)](https://git.io/typing-svg)

<br>

![Status](https://img.shields.io/badge/STATUS-BETA-00ff9f?style=flat-square&labelColor=0d0d1a)
![Platform](https://img.shields.io/badge/PLATFORM-WINDOWS%2010%2F11-00d4ff?style=flat-square&labelColor=0d0d1a)
![License](https://img.shields.io/badge/LICENSE-MIT-00ff9f?style=flat-square&labelColor=0d0d1a)
![Python](https://img.shields.io/badge/PYTHON-3.10%2B-00d4ff?style=flat-square&labelColor=0d0d1a)
![CPU](https://img.shields.io/badge/CPU%20USAGE-%3C%200.3%25-00ff9f?style=flat-square&labelColor=0d0d1a)
![Privacy](https://img.shields.io/badge/PRIVACY-100%25%20LOCAL-00d4ff?style=flat-square&labelColor=0d0d1a)

<br>

</div>

---

```
╔══════════════════════════════════════════════════════════════╗
║  Your laptop is slowly degrading. You just don't know it.   ║
╚══════════════════════════════════════════════════════════════╝
```

Dust builds up. Thermal paste dries out. Fan bearings wear.
Most laptops fail not because they're old — but because **nobody serviced them**.

LaptopPulse monitors your system 24/7 and fires an **AI-generated plain-language report** the moment something looks wrong. No dashboards to check. No technical knowledge needed. Just a quiet daemon that tells you *before* it becomes a crisis.

---

<div align="center">

## `> CAPABILITIES`

</div>

| ◈ | Feature | Details |
|:---:|---|---|
| ◈ | **Silent Monitoring** | Runs invisibly in the background. Uses **< 0.3% CPU**. |
| ◈ | **Trend-Based Detection** | Flags problems **30–60 days** before actual failure. |
| ◈ | **AI Health Reports** | Plain-language reports via **Gemini (free)** or Claude. |
| ◈ | **Live Dashboard** | Real-time metrics at `http://localhost:5747`. No account. |
| ◈ | **0–100 Health Score** | Breakdown: CPU · Fan · Battery · Thermal throttle. |
| ◈ | **Universal Compatibility** | Works on **all Windows 10/11 laptops** — no extra software needed. |
| ◈ | **100% Local** | Your data never leaves your machine. Ever. |
| ◈ | **Encrypted Key Storage** | API keys secured with **AES-256-GCM** encryption. |

---

<div align="center">

## `> DEPLOYMENT PROTOCOL`

</div>

<details>
<summary><b>[ 01 ] — DOWNLOAD &amp; INSTALL</b></summary>
<br>

Download `LaptopPulse.exe` from [**Releases →**](../../releases)

Right-click → **Run as Administrator**. LaptopPulse starts silently in the system tray.

> Admin rights are required to read CPU thermal sensors via Windows ACPI WMI.

</details>

<details>
<summary><b>[ 02 ] — ADD FREE API KEY (GEMINI)</b></summary>
<br>

LaptopPulse uses **Gemini Flash** (free tier) by default.
Get your key at https://aistudio.google.com/apikey — takes 30 seconds.

```bash
python save_gemini_key.py
# or: tray icon → Settings → Paste key
```

> **Also supports Claude** — if a `sk-ant-...` key is detected, the app switches to
> Claude Sonnet automatically. Gemini is recommended for cost (~500 reports/month free).

</details>

<details>
<summary><b>[ 03 ] — OPEN DASHBOARD</b></summary>
<br>

```
http://localhost:5747
```

Or: right-click tray icon → **Open Dashboard**

Shows live health score, CPU/GPU temps, fan RPM, battery health, recent alerts, and generated report links.

</details>

---

<div align="center">

## `> SYSTEM ARCHITECTURE`

</div>

Four-layer **event-driven design** — always watching, only fires when needed.

| Layer | Runtime | CPU Cost | Role |
|---|---|:---:|---|
| 🟢 Silent Watcher | Always on | `< 0.3%` | Reads sensors every 60 s |
| 🟢 Anomaly Detector | Always on | `~0%` | Rules + trend engine |
| 🟢 Log Store | Always on | `~0%` | JSONL daily logs + SQLite events |
| 🟡 AI Report Generator | **Event only** | `2–5%` | Fires once on anomaly, then sleeps |

---

<div align="center">

## `> HARDWARE COMPATIBILITY`

</div>

| Component | Supported |
|---|---|
| CPU | ✅ Intel Core (all gen) / AMD Ryzen (all gen) |
| CPU Temperature | ✅ Windows ACPI WMI — **no external software needed** |
| GPU Temperature | ✅ NVIDIA GeForce (nvidia-smi, pre-installed with driver) |
| Fan RPM | ⚠️ Vendor EC-locked on most laptops — shown as N/A (expected) |
| OS | ✅ Windows 10 / Windows 11 (64-bit) |

---

<div align="center">

## `> DATA PROTOCOL`

</div>

```
◉  LOCAL STORAGE ONLY    →  C:\Users\<you>\AppData\LocalLow\LaptopPulse\
◎  ZERO ANALYTICS        →  No telemetry. No tracking. No accounts required.
◈  MINIMAL API PAYLOAD   →  CPU model, GPU model, temp deltas only. No serials.
⬡  ON-DEMAND CALLS ONLY  →  Network used only when a fault is detected.
```

See [PRIVACY.md](PRIVACY.md) for the complete policy.

---

<div align="center">

## `> BUILD FROM SOURCE`

</div>

```bash
# Clone repository
git clone https://github.com/DEVsaurabhgaur/LaptopPulse
cd LaptopPulse
pip install -r requirements.txt
python main.py
```

> Run as Administrator for full sensor access.

```bash
# Build .exe
python installer/build_exe.py

# Run test suite
pytest tests/ -v
```

---

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0a0a14,50:00d4ff,100:00ff9f&height=120&section=footer&text=MIT%20%E2%80%94%20Free%20for%20personal%20use&fontSize=16&fontFamily=Share%20Tech%20Mono&fontColor=ffffff&fontAlignY=60" width="100%"/>

<div align="center">
<sub>Built by <b>Saurabh Gaur</b> — ASUS TUF A15 owner who got tired of surprise shutdowns.</sub>
</div>
