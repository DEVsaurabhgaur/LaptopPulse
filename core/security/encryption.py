"""
core/security/encryption.py
----------------------------
AES-256-GCM encryption with machine-derived keys.
Key derivation uses motherboard serial + CPU ID via PBKDF2HMAC (SHA-256, 100k iterations).
The same machine always derives the same key — encrypted files are machine-bound.

THREAT MODEL: Protects against malware reading log files and API keys from disk.
              Does NOT protect against physical disk theft or nation-state actors.

Supports storing both Gemini (AIza...) and Claude (sk-ant-...) API keys.
"""

import os
import json
import ctypes
import subprocess
import logging
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

logger = logging.getLogger(__name__)

# Fixed app salt — changing this will invalidate all existing encrypted data
_APP_SALT = b"LaptopPulse_v1_salt_2026_saurabhgaur"


# ── Machine ID ────────────────────────────────────────────────────────────────

def _get_wmic_value(wmic_class: str, field: str) -> str:
    """Run a wmic command and return the value."""
    try:
        result = subprocess.run(
            ["wmic", wmic_class, "get", field],
            capture_output=True,
            text=True,
            timeout=5,
        )
        lines = [ln.strip() for ln in result.stdout.splitlines() if ln.strip()]
        return lines[1] if len(lines) > 1 else "UNKNOWN"
    except Exception as e:
        logger.warning("wmic failed for %s %s: %s", wmic_class, field, e)
        return "FALLBACK"


def get_machine_id() -> bytes:
    """
    Derive a machine-unique identifier from hardware serials.
    Uses: motherboard serial + CPU processor ID.
    Falls back to hostname if wmic unavailable (dev/non-Windows environments).
    """
    import platform
    if platform.system() != "Windows":
        # Dev fallback — on real Windows this uses hardware serials
        return platform.node().encode("utf-8")

    board_serial = _get_wmic_value("baseboard", "SerialNumber")
    cpu_id       = _get_wmic_value("cpu", "ProcessorId")
    machine_str  = f"{board_serial}|{cpu_id}"
    logger.debug("Machine ID components: %s", machine_str)
    return machine_str.encode("utf-8")


# ── Key Derivation ────────────────────────────────────────────────────────────

_derived_key: bytes | None = None


def get_encryption_key() -> bytes:
    """
    Return (and cache) the 256-bit AES key derived from this machine's hardware.
    Identical machine = identical key. Different machine = cannot decrypt files.
    """
    global _derived_key
    if _derived_key is not None:
        return _derived_key

    machine_id = get_machine_id()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,           # 256-bit key
        salt=_APP_SALT,
        iterations=100_000,  # Slow for attacker, fast enough for startup
    )
    _derived_key = kdf.derive(machine_id)
    return _derived_key


# ── Encrypt / Decrypt ─────────────────────────────────────────────────────────

def encrypt_data(data: dict) -> bytes:
    """
    Encrypt a dict as AES-256-GCM ciphertext.
    Returns: nonce (12 bytes) + ciphertext + auth tag.
    GCM mode provides BOTH confidentiality AND integrity — tampering raises InvalidTag.
    """
    key    = get_encryption_key()
    aesgcm = AESGCM(key)
    nonce  = os.urandom(12)          # 96-bit random nonce — NEVER reuse
    plain  = json.dumps(data).encode("utf-8")
    cipher = aesgcm.encrypt(nonce, plain, None)
    return nonce + cipher            # Store nonce prepended to ciphertext


def decrypt_data(blob: bytes) -> dict:
    """
    Decrypt AES-256-GCM blob produced by encrypt_data().
    Raises cryptography.exceptions.InvalidTag if data was tampered with.
    """
    key    = get_encryption_key()
    aesgcm = AESGCM(key)
    nonce  = blob[:12]
    cipher = blob[12:]
    plain  = aesgcm.decrypt(nonce, cipher, None)
    return json.loads(plain)


# ── Secure Memory Wipe ────────────────────────────────────────────────────────

def secure_wipe(data: bytearray) -> None:
    """
    Overwrite sensitive data in memory with zeros.
    Use after handling API keys or passwords.
    """
    try:
        ctypes.memset(
            ctypes.addressof((ctypes.c_char * len(data)).from_buffer(data)),
            0,
            len(data),
        )
    except Exception as e:
        logger.warning("secure_wipe failed: %s", e)


# ── API Key Storage ───────────────────────────────────────────────────────────

def save_api_key(api_key: str, config_path: Path) -> None:
    """
    Encrypt and persist the API key to disk.
    Works for both Gemini (AIza...) and Claude (sk-ant-...) keys.
    NEVER stores in plaintext. NEVER logs the value.
    """
    encrypted = encrypt_data({"api_key": api_key})
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_bytes(encrypted)
    logger.info("API key saved (encrypted) to %s", config_path)


def load_api_key(config_path: Path) -> str | None:
    """
    Load and decrypt the API key from disk.
    Falls back to environment variables:
      1. GEMINI_API_KEY   — Google Gemini (free tier)
      2. GOOGLE_API_KEY   — alternative Gemini env var name
      3. ANTHROPIC_API_KEY — Anthropic Claude (paid)
    Returns None if no key found anywhere.
    """
    if config_path.exists():
        try:
            blob = config_path.read_bytes()
            data = decrypt_data(blob)
            key = data.get("api_key")
            if key:
                return key
        except Exception as e:
            logger.error("Failed to load API key from file: %s", e)

    # Environment variable fallbacks (dev/CI/server mode)
    for env_var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ANTHROPIC_API_KEY"):
        key = os.environ.get(env_var)
        if key:
            logger.debug("Using API key from env var: %s", env_var)
            return key

    return None
