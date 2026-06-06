"""
save_gemini_key.py
-------------------
Guided setup for Google Gemini API key (AIza...) — the FREE tier option.
Run this ONCE to save your Gemini key securely to config.enc.

Usage:
    python save_gemini_key.py

Get your free Gemini key at: https://aistudio.google.com/apikey
Free tier: 1,500 requests/day — far more than LaptopPulse ever needs.

Place this file in your LaptopPulse root folder (same level as main.py).
"""

import sys
import getpass
from pathlib import Path

# ── Make sure project imports work ───────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    print("=" * 55)
    print("  LaptopPulse — Gemini API Key Setup (FREE)")
    print("=" * 55)
    print()
    print("Step 1: Go to https://aistudio.google.com/apikey")
    print("Step 2: Click 'Create API key'")
    print("Step 3: Copy the key (starts with AIza...)")
    print()

    # ── Import project modules ─────────────────────────────────────────────────
    try:
        from core.security.encryption import save_api_key
        from config.settings import get_app_dir
    except ImportError as e:
        print(f"[ERROR] Could not import project modules: {e}")
        print("Make sure you're running this from the LaptopPulse root folder.")
        sys.exit(1)

    # ── Get key from user ──────────────────────────────────────────────────────
    while True:
        key = getpass.getpass("Enter your Gemini API key (AIza...): ").strip()

        if not key:
            print("[ERROR] Key cannot be empty. Try again.\n")
            continue

        if not key.startswith("AIza"):
            confirm = input(
                "[WARNING] Key doesn't start with 'AIza' — are you sure this is a Gemini key? (y/n): "
            ).strip().lower()
            if confirm != "y":
                print("Try again.\n")
                continue

        break

    # ── Save key ───────────────────────────────────────────────────────────────
    config_path = get_app_dir() / "config.enc"

    try:
        # Correct argument order: save_api_key(api_key: str, config_path: Path)
        save_api_key(key, config_path)
        print()
        print(f"[OK] Key saved (encrypted) to: {config_path}")
        print()
        print("Test your setup:")
        print("  python main.py --report")
        print()
        print("Start monitoring:")
        print("  python main.py")
    except Exception as e:
        print(f"[ERROR] Failed to save key: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
