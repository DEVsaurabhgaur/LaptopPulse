# Privacy Policy — LaptopPulse

**Short version: Your hardware data never leaves your machine. No accounts. No analytics. No surprises.**

---

## What We Collect

| Data | Stored Where | Sent Anywhere? |
|------|-------------|---------------|
| CPU temperature (numbers only) | Local JSONL files | No |
| GPU temperature (numbers only) | Local JSONL files | No |
| Fan speed RPM | Local JSONL files | No |
| CPU load % | Local JSONL files | No |
| Battery health % | Local JSONL files | No |
| Laptop model + CPU/GPU name | Local system_info.json | To Claude API only when generating a report |
| AI-generated report text | Local reports/ folder | No |
| Your Anthropic API key (if added) | Encrypted config.enc | No |

## What We NEVER Collect

- Your name, email, or any account information
- Hardware serial numbers or unique identifiers
- Installed software or browser history
- Files, documents, or personal data of any kind
- Usage analytics or telemetry
- Crash reports sent to any server

## Where Your Data Lives

All data is stored at:
```
C:\Users\<YourName>\AppData\LocalLow\LaptopPulse\
├── logs/          ← Daily JSONL files (auto-deleted after 90 days)
├── reports/       ← AI-generated HTML reports
├── baseline.json  ← Your 7-day initial health baseline
├── trends.json    ← 30/60/90-day rolling averages
├── events.json    ← Anomaly event history
├── system_info.json ← Laptop model, CPU, GPU (no serials)
└── config.enc     ← Encrypted API key (if you added one)
```

## Network Requests

LaptopPulse makes exactly ONE type of network request — and only when you have an API key configured AND an anomaly is detected:

**To:** `api.anthropic.com` (Claude AI)  
**What is sent:** Laptop model, CPU name, GPU name, temperature averages, fan RPM averages  
**What is NOT sent:** Your username, serial numbers, file paths, or any identifying information  
**When:** Only when generating a health report (approximately 1-2 times per month)

If you have no API key, LaptopPulse works fully offline with pre-written report templates.

## How to Delete All Your Data

**One command:**
```bash
python service/uninstall.py
```

This permanently deletes all logs, reports, baseline data, and config. Nothing remains.

You can also manually delete the folder at:
`C:\Users\<YourName>\AppData\LocalLow\LaptopPulse\`

## Encryption

Your Anthropic API key is stored encrypted using AES-256-GCM with a key derived from your machine's hardware identifiers. The encrypted file (`config.enc`) cannot be read on a different machine.

---

*Last updated: June 2026*  
*Questions: Open a GitHub issue*
