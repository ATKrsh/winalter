"""
DISM Servicing Provider for WinAlter
Handles AppX package removals, INF driver injection, and Windows feature toggles.
"""

import os
import subprocess
from typing import Dict, Any, List, Optional, Callable
from .base import BaseProvider

class DISMProvider(BaseProvider):
    def remove_appx(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        packages = params.get("packages", [])
        if not packages:
            return True

        if progress_callback:
            progress_callback(f"DISM: Processing AppX package removal ({len(packages)} targeted patterns)...")

        # Get installed packages
        cmd = ["dism", "/English", f"/Image:{self.mount_dir}", "/Get-ProvisionedAppxPackages"]
        res = subprocess.run(cmd, capture_output=True, text=True)

        installed = []
        for line in res.stdout.splitlines():
            line = line.strip()
            if line.startswith("PackageName :"):
                pkg_name = line.split(":", 1)[1].strip()
                installed.append(pkg_name)

        for pattern in packages:
            for full_pkg in installed:
                if pattern.lower() in full_pkg.lower():
                    if progress_callback:
                        progress_callback(f"Removing AppX package: {full_pkg}...")
                    rem_cmd = ["dism", "/English", f"/Image:{self.mount_dir}", "/Remove-ProvisionedAppxPackage", f"/PackageName:{full_pkg}"]
                    subprocess.run(rem_cmd, capture_output=True, text=True)

        return True

    def add_drivers(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        driver_dir = params.get("driver_dir")
        if not driver_dir or not os.path.exists(driver_dir):
            return False

        if progress_callback:
            progress_callback(f"DISM: Injecting INF drivers from {driver_dir}...")

        cmd = ["dism", "/English", f"/Image:{self.mount_dir}", "/Add-Driver", f"/Driver:{driver_dir}", "/Recurse"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0
