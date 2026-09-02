"""
Declarative Configuration Schema & Model Definition for WinAlter
Defines the structure of winalter.yaml / winalter.json distribution specifications.
"""

import json
import yaml
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class MetaSpec(BaseModel):
    name: str = "Custom Windows Distribution"
    version: str = "1.0.0"
    author: str = "WinAlter Architect"
    target_edition: str = "Windows 11 Pro"
    edition_index: int = 1
    architecture: str = "x64"

class AppearanceSpec(BaseModel):
    theme: str = "dark"
    accent_color: str = "#8B5CF6"

class ExplorerSpec(BaseModel):
    show_file_extensions: bool = True
    show_hidden_files: bool = True
    compact_mode: bool = False
    open_to: str = "this_pc"
    classic_context_menu: bool = True

class TaskbarSpec(BaseModel):
    alignment: str = "center"  # left or center
    search_mode: str = "hidden" # hidden, icon, or box
    widgets: bool = False
    copilot: bool = False

class StartMenuSpec(BaseModel):
    disable_bing_search: bool = True

class ServicesSpec(BaseModel):
    sysmain: str = "disabled"       # disabled or auto
    windows_search: str = "manual"  # manual or disabled
    diagtrack: str = "disabled"     # disabled or auto

class AppsSpec(BaseModel):
    remove_packages: List[str] = Field(default_factory=lambda: [
        "Microsoft.XboxApp",
        "Microsoft.BingWeather",
        "Microsoft.BingNews",
        "Microsoft.WindowsFeedbackHub",
        "Microsoft.Getstarted"
    ])
    install_apps: List[str] = Field(default_factory=list)

class DriversSpec(BaseModel):
    inject_dir: Optional[str] = None

class SecuritySpec(BaseModel):
    disable_telemetry: bool = True
    bypass_win11_checks: bool = True

class OOBESpec(BaseModel):
    username: str = "Admin"
    password: str = ""
    computer_name: str = "WinAlter-PC"
    language: str = "en-US"
    timezone: str = "UTC"
    skip_oobe: bool = True
    auto_logon: bool = True

class WinAlterSpec(BaseModel):
    meta: MetaSpec = Field(default_factory=MetaSpec)
    appearance: AppearanceSpec = Field(default_factory=AppearanceSpec)
    explorer: ExplorerSpec = Field(default_factory=ExplorerSpec)
    taskbar: TaskbarSpec = Field(default_factory=TaskbarSpec)
    start_menu: StartMenuSpec = Field(default_factory=StartMenuSpec)
    services: ServicesSpec = Field(default_factory=ServicesSpec)
    apps: AppsSpec = Field(default_factory=AppsSpec)
    drivers: DriversSpec = Field(default_factory=DriversSpec)
    security: SecuritySpec = Field(default_factory=SecuritySpec)
    oobe: OOBESpec = Field(default_factory=OOBESpec)

    def to_yaml(self) -> str:
        return yaml.dump(self.model_dump(), sort_keys=False, default_flow_style=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "WinAlterSpec":
        data = yaml.safe_load(yaml_str) or {}
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.model_dump(), indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> "WinAlterSpec":
        data = json.loads(json_str)
        return cls(**data)
