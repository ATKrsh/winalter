"""
WinAlter Distribution Compiler & AST Execution Planner
Compiles declarative WinAlterSpec into a validated, risk-assessed multi-layer execution AST.
"""

from typing import List, Dict, Any
from .config import WinAlterSpec
from .risk import RiskAssessor, RiskLevel

class ASTNode:
    def __init__(self, provider: str, action: str, params: Dict[str, Any], risk: Dict[str, Any]):
        self.provider = provider
        self.action = action
        self.params = params
        self.risk = risk

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider": self.provider,
            "action": self.action,
            "params": self.params,
            "risk_level": self.risk["level"].value,
            "risk_color": self.risk["color"],
            "risk_description": self.risk["description"]
        }

class ExecutionPlan:
    def __init__(self, layers: Dict[str, List[ASTNode]]):
        self.layers = layers

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            layer_name: [node.to_dict() for node in nodes]
            for layer_name, nodes in self.layers.items()
        }

class WinAlterCompiler:
    def __init__(self, spec: WinAlterSpec):
        self.spec = spec

    def compile(self) -> ExecutionPlan:
        """
        Compiles spec into ordered execution layers with risk assessment metadata.
        """
        layers = {
            "Layer 01: Core OS & Servicing": [],
            "Layer 02: Provisioning & Apps": [],
            "Layer 03: System Services": [],
            "Layer 04: Shell & Customization": [],
            "Layer 05: Setup & OOBE": []
        }

        # --- Layer 01: Drivers ---
        if self.spec.drivers.inject_dir:
            risk = RiskAssessor.assess_setting("drivers", "inject_dir", self.spec.drivers.inject_dir)
            layers["Layer 01: Core OS & Servicing"].append(
                ASTNode("DISMProvider", "add_drivers", {"driver_dir": self.spec.drivers.inject_dir}, risk)
            )

        # --- Layer 02: Apps & Provisioning ---
        if self.spec.apps.remove_packages:
            risk = RiskAssessor.assess_setting("apps", "remove_packages", self.spec.apps.remove_packages)
            layers["Layer 02: Provisioning & Apps"].append(
                ASTNode("DISMProvider", "remove_appx", {"packages": self.spec.apps.remove_packages}, risk)
            )

        # --- Layer 03: System Services ---
        services = self.spec.services
        if services.sysmain == "disabled":
            risk = RiskAssessor.assess_setting("services", "sysmain", "disabled")
            layers["Layer 03: System Services"].append(
                ASTNode("ServiceProvider", "configure_service", {"name": "SysMain", "start_type": "disabled"}, risk)
            )
        if services.diagtrack == "disabled":
            risk = RiskAssessor.assess_setting("services", "diagtrack", "disabled")
            layers["Layer 03: System Services"].append(
                ASTNode("ServiceProvider", "configure_service", {"name": "DiagTrack", "start_type": "disabled"}, risk)
            )

        # --- Layer 04: Shell & Customization ---
        # Explorer
        exp = self.spec.explorer
        risk_exp = RiskAssessor.assess_setting("explorer", "settings", exp.model_dump())
        layers["Layer 04: Shell & Customization"].append(
            ASTNode("ShellProvider", "apply_explorer_tweaks", exp.model_dump(), risk_exp)
        )

        # Taskbar
        tb = self.spec.taskbar
        risk_tb = RiskAssessor.assess_setting("taskbar", "settings", tb.model_dump())
        layers["Layer 04: Shell & Customization"].append(
            ASTNode("ShellProvider", "apply_taskbar_tweaks", tb.model_dump(), risk_tb)
        )

        # Start Menu & Security
        sec = self.spec.security
        risk_sec = RiskAssessor.assess_setting("security", "settings", sec.model_dump())
        layers["Layer 04: Shell & Customization"].append(
            ASTNode("RegistryProvider", "apply_security_tweaks", sec.model_dump(), risk_sec)
        )

        # --- Layer 05: Setup & OOBE ---
        oobe = self.spec.oobe
        risk_oobe = RiskAssessor.assess_setting("oobe", "settings", oobe.model_dump())
        layers["Layer 05: Setup & OOBE"].append(
            ASTNode("OOBEProvider", "generate_autounattend", oobe.model_dump(), risk_oobe)
        )

        return ExecutionPlan(layers)
