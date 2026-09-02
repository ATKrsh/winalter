"""
Base Abstraction Provider for WinAlter Engine
"""

import logging
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger("WinAlter.Providers")

class BaseProvider:
    def __init__(self, mount_dir: str):
        self.mount_dir = mount_dir

    def execute(self, action: str, params: Dict[str, Any], progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        method = getattr(self, action, None)
        if not method:
            raise NotImplementedError(f"Provider {self.__class__.__name__} does not support action: {action}")
        return method(params, progress_callback=progress_callback)
