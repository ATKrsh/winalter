"""
Registry Abstraction Provider for WinAlter
Translates abstract customization concepts into offline registry hive modifications.
"""

import os
import subprocess
from typing import Dict, Any, Optional, Callable
from .base import BaseProvider

class RegistryProvider(BaseProvider):
    def __init__(self, mount_dir: str):
        super().__init__(mount_dir)
        self.software_hive = os.path.join(self.mount_dir, "Windows", "System32", "config", "SOFTWARE")
        self.system_hive = os.path.join(self.mount_dir, "Windows", "System32", "config", "SYSTEM")
        self.default_hive = os.path.join(self.mount_dir, "Windows", "System32", "config", "DEFAULT")
        self.ntuser_hive = os.path.join(self.mount_dir, "Users", "Default", "NTUSER.DAT")
        self.loaded_hives = {}

    def load_hives(self, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        hives = [
            ("OFFLINE_SOFTWARE", self.software_hive),
            ("OFFLINE_SYSTEM", self.system_hive),
            ("OFFLINE_DEFAULT", self.default_hive),
            ("OFFLINE_NTUSER", self.ntuser_hive),
        ]
        for key, path in hives:
            if not os.path.exists(path):
                continue
            if progress_callback:
                progress_callback(f"Registry Provider: Mounting offline hive HKLM\\{key}...")
            res = subprocess.run(["reg.exe", "load", f"HKLM\\{key}", path], capture_output=True, text=True)
            if res.returncode == 0:
                self.loaded_hives[key] = True
        return len(self.loaded_hives) > 0

    def unload_hives(self, progress_callback: Optional[Callable[[str], None]] = None):
        for key in list(self.loaded_hives.keys()):
            if progress_callback:
                progress_callback(f"Registry Provider: Unloading offline hive HKLM\\{key}...")
            subprocess.run(["reg.exe", "unload", f"HKLM\\{key}"], capture_output=True, text=True)
            del self.loaded_hives[key]

    def _reg_add(self, key: str, value_name: str, value_type: str, data: str) -> bool:
        cmd = ["reg.exe", "add", key, "/v", value_name, "/t", value_type, "/d", data, "/f"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    def _reg_add_default(self, key: str, data: str) -> bool:
        cmd = ["reg.exe", "add", key, "/ve", "/d", data, "/f"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        return res.returncode == 0

    def apply_security_tweaks(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        self.load_hives(progress_callback=progress_callback)
        try:
            if params.get("bypass_win11_checks", True):
                if progress_callback:
                    progress_callback("Registry Provider: Applying Windows 11 hardware check bypasses...")
                lab_key = r"HKLM\OFFLINE_SYSTEM\Setup\LabConfig"
                self._reg_add(lab_key, "BypassTPMCheck", "REG_DWORD", "1")
                self._reg_add(lab_key, "BypassRAMCheck", "REG_DWORD", "1")
                self._reg_add(lab_key, "BypassSecureBootCheck", "REG_DWORD", "1")
                self._reg_add(lab_key, "BypassCPUCheck", "REG_DWORD", "1")
                self._reg_add(lab_key, "BypassStorageCheck", "REG_DWORD", "1")
                self._reg_add(r"HKLM\OFFLINE_SOFTWARE\Microsoft\Windows\CurrentVersion\OOBE", "BypassNRO", "REG_DWORD", "1")

            if params.get("disable_telemetry", True):
                if progress_callback:
                    progress_callback("Registry Provider: Disabling diagnostic data & telemetry...")
                dc_pol = r"HKLM\OFFLINE_SOFTWARE\Policies\Microsoft\Windows\DataCollection"
                self._reg_add(dc_pol, "AllowTelemetry", "REG_DWORD", "0")
                self._reg_add(r"HKLM\OFFLINE_SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection", "AllowTelemetry", "REG_DWORD", "0")
        finally:
            self.unload_hives(progress_callback=progress_callback)
        return True
