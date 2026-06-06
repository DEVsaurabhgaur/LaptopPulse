"""
service/install_service.py
---------------------------
Registers LaptopPulse as a Windows Service using pywin32.
Run as administrator: python install_service.py install
"""

import sys
import os
import logging

logger = logging.getLogger(__name__)

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    _WIN32_AVAILABLE = True
except ImportError:
    _WIN32_AVAILABLE = False


if _WIN32_AVAILABLE:
    class LaptopPulseService(win32serviceutil.ServiceFramework):
        _svc_name_        = "LaptopPulse"
        _svc_display_name_ = "LaptopPulse Hardware Monitor"
        _svc_description_  = "Silently monitors laptop hardware health and generates AI service reports."

        def __init__(self, args):
            win32serviceutil.ServiceFramework.__init__(self, args)
            self._stop_event = win32event.CreateEvent(None, 0, 0, None)
            self._running    = True

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            win32event.SetEvent(self._stop_event)
            self._running = False

        def SvcDoRun(self):
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, ""),
            )
            self._run()

        def _run(self):
            # Set up logging to Windows Event Log + file
            _setup_service_logging()
            from core.watcher import run_daemon
            try:
                run_daemon()
            except Exception as e:
                logger.error("Service crashed: %s", e, exc_info=True)
                servicemanager.LogErrorMsg(f"LaptopPulse crashed: {e}")


def _setup_service_logging():
    from pathlib import Path
    from config.settings import get_app_dir
    log_path = get_app_dir() / "service.log"
    logging.basicConfig(
        filename=str(log_path),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    )


def install():
    """Install the Windows Service."""
    if not _WIN32_AVAILABLE:
        print("ERROR: pywin32 not installed. Run: pip install pywin32")
        sys.exit(1)
    win32serviceutil.InstallService(
        pythonClassString = f"{__name__}.LaptopPulseService",
        serviceName       = LaptopPulseService._svc_name_,
        displayName       = LaptopPulseService._svc_display_name_,
        description       = LaptopPulseService._svc_description_,
        startType         = win32service.SERVICE_AUTO_START,
    )
    print("LaptopPulse service installed. Start with: sc start LaptopPulse")


def uninstall():
    if not _WIN32_AVAILABLE:
        return
    win32serviceutil.RemoveService(LaptopPulseService._svc_name_)
    print("LaptopPulse service removed.")


def start():
    if not _WIN32_AVAILABLE:
        return
    win32serviceutil.StartService(LaptopPulseService._svc_name_)
    print("LaptopPulse service started.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python install_service.py [install|uninstall|start|stop|debug]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "install":
        install()
    elif cmd == "uninstall":
        uninstall()
    elif cmd == "start":
        start()
    elif _WIN32_AVAILABLE:
        win32serviceutil.HandleCommandLine(LaptopPulseService)
