# Security Policy — LaptopPulse

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x.x   | ✅ Yes    |
| < 1.0   | ❌ No     |

## Security Design

- All local data encrypted with **AES-256-GCM** (authenticated encryption)
- Machine-derived keys via **PBKDF2HMAC** (100,000 iterations) — no hardcoded secrets
- API keys never stored in plaintext, never logged, wiped from memory after use
- No network connections except: Anthropic Claude API (anomaly reports only, opt-in)
- All external inputs validated and sanitised before logging
- No third-party trackers, analytics SDKs, or crash reporters

## Reporting a Vulnerability

**DO NOT open a public GitHub issue for security vulnerabilities.**

Email: **security@laptoppulse.app** (or open a private GitHub security advisory)

**Expected response time:** 48 hours  
**Disclosure policy:** 90 days after fix is released

Please include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Your suggested fix (if any)

## Threat Model

LaptopPulse is designed to protect against:
- Malware reading log files or API keys from disk (→ AES-256-GCM encryption)
- Tampered executables distributed as fake LaptopPulse (→ SHA-256 hash on every release)
- Log file injection attacks (→ GCM authentication tag detects tampering)

LaptopPulse is NOT designed to protect against physical disk theft by sophisticated attackers.
The machine-derived key is a practical protection, not a cryptographic guarantee.
