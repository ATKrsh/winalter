"""
ISO Importer Module for WinAlter
Handles ISO extraction and location of install.wim / boot.wim images into workspace source directory.
"""

import os
import re
import shutil
import subprocess
import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("WinAlter.ISOImporter")

class ISOImporter:
    def __init__(self, source_dir: str):
        self.source_dir = os.path.abspath(source_dir)
        os.makedirs(self.source_dir, exist_ok=True)

    def import_iso(self, iso_path: str, progress_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Extracts ISO to project source directory using PowerShell Mount-DiskImage.
        """
        iso_path = os.path.abspath(iso_path)
        if not os.path.exists(iso_path):
            raise FileNotFoundError(f"ISO file not found: {iso_path}")

        if progress_callback:
            progress_callback(f"Mounting ISO: {iso_path}...")

        if os.path.exists(self.source_dir):
            if progress_callback:
                progress_callback("Cleaning workspace source directory...")
            shutil.rmtree(self.source_dir, ignore_errors=True)
        os.makedirs(self.source_dir, exist_ok=True)

        ps_cmd = f"""
        $iso = '{iso_path}'
        $target = '{self.source_dir}'
        $mountResult = Mount-DiskImage -ImagePath $iso -PassThru
        $driveLetter = ($mountResult | Get-Volume).DriveLetter
        if (-not $driveLetter) {{
            throw "Failed to mount ISO."
        }}
        $sourcePath = "$($driveLetter):\\*"
        Write-Host "Extracting files to workspace..."
        Copy-Item -Path $sourcePath -Destination $target -Recurse -Force
        Dismount-DiskImage -ImagePath $iso | Out-Null
        """

        p = subprocess.Popen(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        for line in p.stdout:
            line_str = line.strip()
            if line_str and progress_callback:
                progress_callback(line_str)

        p.wait()
        if p.returncode != 0:
            raise RuntimeError(f"ISO import failed with code {p.returncode}")

        if progress_callback:
            progress_callback("ISO extracted successfully to project workspace.")

        return self.source_dir

    def find_install_wim(self) -> str:
        """
        Locates install.wim or install.esd in sources directory.
        """
        sources_dir = os.path.join(self.source_dir, "sources")
        wim = os.path.join(sources_dir, "install.wim")
        esd = os.path.join(sources_dir, "install.esd")

        if os.path.exists(wim):
            return wim
        elif os.path.exists(esd):
            return esd
        raise FileNotFoundError("Neither install.wim nor install.esd found in ISO sources directory.")
