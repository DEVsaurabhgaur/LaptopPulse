"""
installer/build_exe.py
-----------------------
Build script: packages LaptopPulse into a single Windows .exe via PyInstaller.
Run from repo root: python installer/build_exe.py

Requirements:
  pip install pyinstaller
  Run on Windows machine (cross-compilation not supported)
"""

import subprocess
import sys
import hashlib
from pathlib import Path

REPO_ROOT   = Path(__file__).parent.parent
DIST_DIR    = REPO_ROOT / "dist"
BUILD_DIR   = REPO_ROOT / "build"
OUTPUT_NAME = "LaptopPulse"


def compute_sha256(file_path: Path) -> str:
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            sha.update(chunk)
    return sha.hexdigest()


def build():
    print("Building LaptopPulse.exe with PyInstaller...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--uac-admin",
        "--name",        OUTPUT_NAME,
        "--distpath",    str(DIST_DIR),
        "--workpath",    str(BUILD_DIR),
        "--icon",        str(REPO_ROOT / "assets" / "icon.ico"),
        # Include entire config folder (defaults.json + any future files)
        "--add-data",    f"{REPO_ROOT / 'config' / 'defaults.json'};config",
        # Include dashboard HTML and tray assets
        "--add-data",    f"{REPO_ROOT / 'ui' / 'dashboard.html'};ui",
        "--add-data",    f"{REPO_ROOT / 'ui' / 'assets'};ui/assets",
        # Hidden imports for Windows Service and tray
        "--hidden-import", "win32serviceutil",
        "--hidden-import", "win32service",
        "--hidden-import", "win32event",
        "--hidden-import", "servicemanager",
        "--hidden-import", "pystray",
        "--hidden-import", "pystray._win32",
        "--hidden-import", "PIL",
        "--hidden-import", "PIL.Image",
        "--hidden-import", "flask",
        "--hidden-import", "flask.templating",
        "--hidden-import", "google.generativeai",
        "--hidden-import", "cryptography",
        "--hidden-import", "wmi",
        "--hidden-import", "pythoncom",
        "--hidden-import", "pywintypes",
        str(REPO_ROOT / "main.py"),
    ]

    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    if result.returncode != 0:
        print("BUILD FAILED")
        sys.exit(1)

    exe_path = DIST_DIR / f"{OUTPUT_NAME}.exe"
    if not exe_path.exists():
        print("ERROR: .exe not found after build")
        sys.exit(1)

    sha256 = compute_sha256(exe_path)
    hash_file = DIST_DIR / f"{OUTPUT_NAME}.exe.sha256"
    hash_file.write_text(f"{sha256}  {OUTPUT_NAME}.exe\n")

    print(f"\nBuild complete: {exe_path}")
    print(f"SHA-256: {sha256}")
    print(f"Hash saved: {hash_file}")


if __name__ == "__main__":
    build()
