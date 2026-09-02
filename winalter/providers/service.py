"""
Windows Services Provider for WinAlter
Configures system service start types (SysMain, Windows Search, DiagTrack) in offline SYSTEM hive.
"""

from typing import Dict, Any, Optional, Callable
from .registry import RegistryProvider

class ServiceProvider(RegistryProvider):
    def configure_service(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        svc_name = params.get("name")
        start_type = params.get("start_type", "disabled")
        if not svc_name:
            return False

        start_val = "4" if start_type == "disabled" else ("3" if start_type == "manual" else "2")
        self.load_hives(progress_callback=progress_callback)
        try:
            if progress_callback:
                progress_callback(f"Service Provider: Setting service '{svc_name}' start type to {start_type} (value={start_val})...")

            svc_key = rf"HKLM\OFFLINE_SYSTEM\ControlSet001\Services\{svc_name}"
            self._reg_add(svc_key, "Start", "REG_DWORD", start_val)
        finally:
            self.unload_hives(progress_callback=progress_callback)
        return True
