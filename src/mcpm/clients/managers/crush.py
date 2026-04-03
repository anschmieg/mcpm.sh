"""
Crush Coding Agent integration utilities for MCP
"""

import logging
import os
import shutil
from typing import Any, Dict

from mcpm.clients.base import JSONClientManager

logger = logging.getLogger(__name__)


class CrushManager(JSONClientManager):
    """Manages Crush Coding Agent MCP server configurations"""

    # Client information
    client_key = "crush"
    display_name = "Crush"
    download_url = "https://github.com/mariuswenzel/crush"

    def __init__(self, config_path_override: str | None = None):
        """Initialize the Crush client manager

        Args:
            config_path_override: Optional path to override the default config file location
        """
        super().__init__(config_path_override=config_path_override)

        if config_path_override:
            self.config_path = config_path_override
        else:
            self.config_path = os.path.expanduser("~/.crush/mcp.json")

    def _get_empty_config(self) -> Dict[str, Any]:
        """Get empty config structure for Crush"""
        return {"mcpServers": {}}

    def is_client_installed(self) -> bool:
        """Check if Crush is installed

        Returns:
            bool: True if crush command is available, False otherwise
        """
        return shutil.which("crush") is not None

    def get_client_info(self) -> Dict[str, str]:
        """Get information about this client

        Returns:
            Dict: Information about the client including display name, download URL, and config path
        """
        return {
            "name": self.display_name,
            "download_url": self.download_url,
            "config_file": self.config_path,
            "description": "Crush Coding Agent",
        }
