"""
Shell & UX Provider for WinAlter
Handles Explorer behavior, Taskbar alignment, Start Menu layout, and Appearance tweaks.
"""

from typing import Dict, Any, Optional, Callable
from .registry import RegistryProvider

class ShellProvider(RegistryProvider):
    def apply_explorer_tweaks(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        self.load_hives(progress_callback=progress_callback)
        try:
            if progress_callback:
                progress_callback("Shell Provider: Applying File Explorer behavior & classic context menu...")

            exp_adv = r"HKLM\OFFLINE_NTUSER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            if params.get("show_file_extensions", True):
                self._reg_add(exp_adv, "HideFileExt", "REG_DWORD", "0")
            if params.get("show_hidden_files", True):
                self._reg_add(exp_adv, "Hidden", "REG_DWORD", "1")
            if params.get("open_to") == "this_pc":
                self._reg_add(exp_adv, "LaunchTo", "REG_DWORD", "1")
            if params.get("classic_context_menu", True):
                ctx_key = r"HKLM\OFFLINE_NTUSER\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32"
                self._reg_add_default(ctx_key, "")
        finally:
            self.unload_hives(progress_callback=progress_callback)
        return True

    def apply_taskbar_tweaks(self, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        self.load_hives(progress_callback=progress_callback)
        try:
            if progress_callback:
                progress_callback("Shell Provider: Applying Taskbar alignment, search mode & Copilot settings...")

            exp_adv = r"HKLM\OFFLINE_NTUSER\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
            if params.get("alignment") == "left":
                self._reg_add(exp_adv, "TaskbarAl", "REG_DWORD", "0")
            elif params.get("alignment") == "center":
                self._reg_add(exp_adv, "TaskbarAl", "REG_DWORD", "1")

            search_user = r"HKLM\OFFLINE_NTUSER\Software\Microsoft\Windows\CurrentVersion\Search"
            if params.get("search_mode") == "hidden":
                self._reg_add(search_user, "SearchboxTaskbarMode", "REG_DWORD", "0")
            elif params.get("search_mode") == "icon":
                self._reg_add(search_user, "SearchboxTaskbarMode", "REG_DWORD", "1")

            if not params.get("copilot", False):
                copilot_pol = r"HKLM\OFFLINE_SOFTWARE\Policies\Microsoft\Windows\WindowsCopilot"
                self._reg_add(copilot_pol, "TurnOffWindowsCopilot", "REG_DWORD", "1")
        finally:
            self.unload_hives(progress_callback=progress_callback)
        return True
