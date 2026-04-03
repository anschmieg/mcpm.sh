"""
Zed Editor integration utilities for MCP
"""

import logging
import os
import shutil
from typing import Any, Dict

from mcpm.clients.base import JSONClientManager

logger = logging.getLogger(__name__)


class ZedManager(JSONClientManager):
    """Manages Zed Editor MCP server configurations.

    Zed uses settings.json which may contain JSONC-style comments (//).
    This manager handles parsing such files by stripping comment lines.
    """

    # Client information
    client_key = "zed"
    display_name = "Zed Editor"
    download_url = "https://zed.dev/"
    configure_key_name = "context_servers"

    def __init__(self, config_path_override: str | None = None):
        """Initialize the Zed Editor client manager

        Args:
            config_path_override: Optional path to override the default config file location
        """
        super().__init__(config_path_override=config_path_override)

        if config_path_override:
            self.config_path = config_path_override
        else:
            # Zed uses ~/.config/zed/settings.json on all platforms (Linux and macOS)
            # Windows uses %APPDATA%/Zed/settings.json
            if self._system == "Windows":
                self.config_path = os.path.join(os.environ.get("APPDATA", ""), "Zed", "settings.json")
            else:
                # macOS and Linux both use ~/.config/zed/settings.json
                self.config_path = os.path.expanduser("~/.config/zed/settings.json")

    def _load_config(self) -> Dict[str, Any]:
        """Load Zed settings.json, handling JSONC comments."""
        import json
        import re

        empty_config = {self.configure_key_name: {}, "inputs": []}

        if not os.path.exists(self.config_path):
            return empty_config

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Strip JSONC-style comments (// ...) before parsing
            lines = content.splitlines()
            json_lines = []
            for line in lines:
                stripped = line.strip()
                if not stripped.startswith("//"):
                    json_lines.append(line)

            json_content = "\n".join(json_lines)
            config = json.loads(json_content)

            # Ensure context_servers exists
            if self.configure_key_name not in config:
                config[self.configure_key_name] = {}

            return config
        except json.JSONDecodeError:
            # Fallback: use regex to extract servers from context_servers block
            logger.warning(f"Full parse failed, using regex fallback")
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Find context_servers block in raw content
                start_marker = '"context_servers": {'
                start = content.find(start_marker)
                if start == -1:
                    return empty_config

                # Find matching closing brace
                pos = start + len(start_marker)
                brace_count = 1
                while pos < len(content) and brace_count > 0:
                    if content[pos] == '{':
                        brace_count += 1
                    elif content[pos] == '}':
                        brace_count -= 1
                    pos += 1

                # Extract the block (just the object content, not the key)
                block = content[start + len(start_marker):pos-1].strip()

                # Extract server names (keys at 4-space indentation)
                import re
                pattern = r'^    "([^"]+)": \{'
                matches = re.findall(pattern, block, re.MULTILINE)

                servers = {}
                for name in matches:
                    # Simple extraction - don't escape hyphens in server names
                    server_pattern = f'    "{name}": {{'
                    server_start = block.find(server_pattern)
                    if server_start >= 0:
                        # Find end of this server's block
                        server_content_start = server_start + len(server_pattern)
                        brace_count = 1
                        i = server_content_start
                        while i < len(block) and brace_count > 0:
                            if block[i] == '{':
                                brace_count += 1
                            elif block[i] == '}':
                                brace_count -= 1
                            i += 1
                        inner = block[server_start:i]
                        servers[name] = {"raw_config": inner[:50]}

                return {self.configure_key_name: servers}
            except Exception as e:
                import traceback
                logger.error(f"Regex extraction failed: {e}")
                logger.error(traceback.format_exc())

            return empty_config
        except Exception as e:
            logger.error(f"Error loading Zed config: {e}")
            return empty_config

    def _get_empty_config(self) -> Dict[str, Any]:
        """Get empty config structure for Zed Editor"""
        return {self.configure_key_name: {}}

    def is_client_installed(self) -> bool:
        """Check if Zed Editor is installed

        Returns:
            bool: True if zed CLI exists or settings.json exists, False otherwise
        """
        # Check CLI first
        if shutil.which("zed"):
            return True
        # Fallback: check if settings.json exists (Zed may not have CLI installed)
        return os.path.exists(self.config_path)

    def get_client_info(self) -> Dict[str, str]:
        """Get information about this client

        Returns:
            Dict: Information about the client including display name, download URL, and config path
        """
        return {
            "name": self.display_name,
            "download_url": self.download_url,
            "config_file": self.config_path,
            "description": "Zed Editor with MCP support",
        }
