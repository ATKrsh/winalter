"""
Risk Classification System for WinAlter
Evaluates safety ratings and stability impact for every Windows customization operation.
"""

from enum import Enum
from typing import Dict, Any, List

class RiskLevel(Enum):
    SUPPORTED = "Supported (Low Risk)"
    CONFIGURATION = "Configuration (Medium Risk)"
    PROVISIONING = "Provisioning (Medium Risk)"
    ADVANCED = "Advanced (High Risk)"
    BINARY = "Binary Modification (Very High Risk)"
    KERNEL = "Kernel Level (Extreme Risk)"

class RiskAssessor:
    @staticmethod
    def get_badge_color(level: RiskLevel) -> str:
        colors = {
            RiskLevel.SUPPORTED: "#00ff87",      # Green
            RiskLevel.CONFIGURATION: "#00f2fe",  # Cyan
            RiskLevel.PROVISIONING: "#4facfe",    # Blue
            RiskLevel.ADVANCED: "#ffb703",       # Yellow/Orange
            RiskLevel.BINARY: "#ff007f",         # Pink/Red
            RiskLevel.KERNEL: "#ff0000"          # Bright Red
        }
        return colors.get(level, "#a0aec0")

    @staticmethod
    def assess_setting(category: str, key: str, value: Any) -> Dict[str, Any]:
        """
        Returns risk metadata for a given setting path.
        """
        # Supported / Low Risk
        if category in ["oobe", "drivers", "packages"]:
            return {"level": RiskLevel.SUPPORTED, "color": "#00ff87", "description": "Microsoft supported offline image servicing operation."}
        
        # Provisioning
        if category == "apps":
            return {"level": RiskLevel.PROVISIONING, "color": "#4facfe", "description": "Modifies provisioned store app packages."}

        # Services / Policies / Registry
        if category in ["services", "security", "behavior"]:
            return {"level": RiskLevel.CONFIGURATION, "color": "#00f2fe", "description": "System service and group policy state modification."}

        # Shell / Appearance
        if category in ["shell", "explorer", "appearance", "taskbar", "start_menu"]:
            return {"level": RiskLevel.ADVANCED, "color": "#ffb703", "description": "Deep Windows shell & desktop experience customization."}

        # Binary / Kernel overrides
        if category == "advanced":
            return {"level": RiskLevel.BINARY, "color": "#ff007f", "description": "Advanced system tweak. May affect future Windows servicing."}

        return {"level": RiskLevel.CONFIGURATION, "color": "#00f2fe", "description": "Standard configuration item."}
