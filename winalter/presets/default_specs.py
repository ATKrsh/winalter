"""
Default Distribution Templates & Presets for WinAlter
"""

from typing import Dict, Any
from ..core.config import WinAlterSpec

PRESET_SPECS = {
    "minimal": WinAlterSpec(
        meta={"name": "WinAlter Minimalist Edition", "version": "1.0.0", "author": "WinAlter Engine"},
        explorer={"show_file_extensions": True, "show_hidden_files": True, "classic_context_menu": True},
        taskbar={"alignment": "left", "search_mode": "hidden", "widgets": False, "copilot": False},
        services={"sysmain": "disabled", "diagtrack": "disabled"},
        apps={"remove_packages": ["Microsoft.XboxApp", "Microsoft.BingNews", "Microsoft.BingWeather", "Microsoft.GetHelp"]},
        security={"disable_telemetry": True, "bypass_win11_checks": True}
    ),
    "gaming": WinAlterSpec(
        meta={"name": "WinAlter Gaming & Performance", "version": "1.0.0", "author": "WinAlter Engine"},
        explorer={"show_file_extensions": True, "show_hidden_files": True, "compact_mode": True, "classic_context_menu": True},
        taskbar={"alignment": "left", "search_mode": "icon", "widgets": False, "copilot": False},
        services={"sysmain": "disabled", "windows_search": "manual", "diagtrack": "disabled"},
        apps={"remove_packages": ["Microsoft.BingNews", "Microsoft.BingWeather", "Microsoft.WindowsFeedbackHub", "Microsoft.Getstarted"]},
        security={"disable_telemetry": True, "bypass_win11_checks": True}
    ),
    "enterprise": WinAlterSpec(
        meta={"name": "WinAlter Enterprise Workstation", "version": "1.0.0", "author": "WinAlter Engine"},
        explorer={"show_file_extensions": True, "show_hidden_files": True, "open_to": "this_pc", "classic_context_menu": True},
        taskbar={"alignment": "left", "search_mode": "hidden", "widgets": False, "copilot": False},
        services={"diagtrack": "disabled"},
        apps={"remove_packages": ["Microsoft.BingNews", "Microsoft.BingWeather", "Microsoft.MicrosoftSolitaireCollection"]},
        security={"disable_telemetry": True, "bypass_win11_checks": True}
    )
}
