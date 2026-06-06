# Installation Guide

See README.md for quick install. This doc covers advanced scenarios.

## Requirements
- Windows 10 or 11 (64-bit)
- Python 3.11+ (for source install only)
- LibreHardwareMonitor (for fan RPM + accurate CPU temp)

## LibreHardwareMonitor Setup
LaptopPulse uses LibreHardwareMonitor for the most accurate sensor readings.

1. Download from: https://github.com/LibreHardwareMonitor/LibreHardwareMonitor
2. Extract to `C:\Program Files\LibreHardwareMonitor\`
3. Run once as administrator to grant hardware access
4. Enable: Options → Run On Windows Startup → Run As Administrator

LaptopPulse works without LHM (falls back to WMI) but fan RPM data will be unavailable.

## Windows Service vs Task Scheduler
LaptopPulse can run as either:
- **Windows Service** (recommended): starts before login, survives user session changes
- **Task Scheduler** (fallback): simpler, no admin required

The installer handles this automatically.
