"""
service/uninstall.py
---------------------
Complete uninstaller — removes service, all logs, reports, and config.
Leaves no residual data. Called by the Windows installer uninstall action.
"""

import shutil
import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


def uninstall(confirm: bool = False):
    """
    Full uninstall: stop service, remove all app data.
    Pass confirm=True to skip interactive prompt (used by installer).
    """
    from config.settings import get_app_dir

    app_dir = get_app_dir()

    if not confirm:
        print(f"This will permanently delete ALL LaptopPulse data from:\n  {app_dir}")
        ans = input("Continue? [y/N]: ").strip().lower()
        if ans != "y":
            print("Uninstall cancelled.")
            return

    # 1. Stop and remove Windows Service
    try:
        from service.install_service import uninstall as remove_service
        remove_service()
    except Exception as e:
        logger.warning("Service removal failed (may not be installed): %s", e)

    # 2. Delete all app data
    if app_dir.exists():
        try:
            shutil.rmtree(app_dir)
            print(f"Deleted: {app_dir}")
        except Exception as e:
            print(f"WARNING: Could not fully delete {app_dir}: {e}")
            print("Please delete this folder manually.")

    print("LaptopPulse has been completely uninstalled.")
    print("Thank you for using LaptopPulse.")


if __name__ == "__main__":
    confirm = "--confirm" in sys.argv
    uninstall(confirm=confirm)
