"""
Workspace Directory Layout Manager for WinAlter Project
"""

import os
import shutil
import logging
from typing import Dict

logger = logging.getLogger("WinAlter.Workspace")

class WorkspaceManager:
    def __init__(self, root_dir: str = "project_workspace"):
        self.root_dir = os.path.abspath(root_dir)
        self.source_dir = os.path.join(self.root_dir, "source")
        self.mount_dir = os.path.join(self.root_dir, "mount")
        self.packages_dir = os.path.join(self.root_dir, "packages")
        self.drivers_dir = os.path.join(self.root_dir, "drivers")
        self.apps_dir = os.path.join(self.root_dir, "apps")
        self.themes_dir = os.path.join(self.root_dir, "themes")
        self.scripts_dir = os.path.join(self.root_dir, "scripts")
        self.registry_dir = os.path.join(self.root_dir, "registry")
        self.config_dir = os.path.join(self.root_dir, "config")
        self.build_dir = os.path.join(self.root_dir, "build")

    def initialize_workspace(self) -> Dict[str, str]:
        """
        Creates all standard directory nodes for a WinAlter project.
        """
        dirs = [
            self.root_dir, self.source_dir, self.mount_dir, self.packages_dir,
            self.drivers_dir, self.apps_dir, self.themes_dir, self.scripts_dir,
            self.registry_dir, self.config_dir, self.build_dir
        ]
        for d in dirs:
            os.makedirs(d, exist_ok=True)
        return {
            "root": self.root_dir,
            "source": self.source_dir,
            "mount": self.mount_dir,
            "build": self.build_dir
        }

    def clean_mount_dir(self):
        """
        Cleans mount directory.
        """
        if os.path.exists(self.mount_dir):
            shutil.rmtree(self.mount_dir, ignore_errors=True)
        os.makedirs(self.mount_dir, exist_ok=True)
