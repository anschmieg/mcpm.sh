"""
Cherry Studio integration utilities for MCP
"""

import logging
import os
import shutil
from typing import Any, Dict

from mcpm.clients.base import JSONClientManager

logger = logging.getLogger(__name__)


class CherryStudioManager(JSONClientManager):
    """Manages Cherry Studio MCP server configurations"""

    # Client information
    client_key = "cherry-studio"
    display_name = "Cherry Studio"
    download_url = "https://github.com/cherry-markets/cherry-studio"

    def __init__(self, config_path_override: str | None = None):
        """Initialize the Cherry Studio client manager

        Args:
            config_path_override: Optional path to override the default config file location
        """
        super().__init__(config_path_override=config_path_override)

        if config_path_override:
            self.config_path = config_path_override
        else:
            # Set config path based on detected platform
            if self._system == "Windows":
                self.config_path = os.path.join(os.environ.get("APPDATA", ""), "cherry-studio", "mcp.json")
            elif self._system == "Darwin":
                self.config_path = os.path.expanduser("~/Library/Application Support/cherry-studio/mcp.json")
            else:
                # Linux
                self.config_path = os.path.expanduser("~/.config/cherry-studio/mcp.json")

    def _get_empty_config(self) -> Dict[str, Any]:
        """Get empty config structure for Cherry Studio"""
        return {"mcpServers": {}}

    def is_client_installed(self) -> bool:
        """Check if Cherry Studio is installed

        Returns:
            bool: True if cherry-studio command is available, False otherwise
        """
        return shutil.which("cherry-studio") is not None

    def get_client_info(self) -> Dict[str, str]:
        """Get information about this client

        Returns:
            Dict: Information about the client including display name, download URL, and config path
        """
        return {
            "name": self.display_name,
            "download_url": self.download_url,
            "config_file": self.config_path,
            "description": "Cherry Studio MCP client",
        }
