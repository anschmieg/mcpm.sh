"""
Mistral Vibe integration utilities for MCP
"""

import logging
import os
import shutil
from typing import Any, Dict

import tomli
import tomli_w

from mcpm.clients.base import JSONClientManager
from mcpm.core.schema import ServerConfig, STDIOServerConfig

logger = logging.getLogger(__name__)


class MistralVibeManager(JSONClientManager):
    """Manages Mistral Vibe MCP server configurations"""

    # Client information
    client_key = "mistral-vibe"
    display_name = "Mistral Vibe"
    download_url = "https://mistral.ai/"
    configure_key_name = "mcp_servers"

    def __init__(self, config_path_override: str | None = None):
        """Initialize the Mistral Vibe client manager

        Args:
            config_path_override: Optional path to override the default config file location
        """
        super().__init__(config_path_override=config_path_override)

        if config_path_override:
            self.config_path = config_path_override
        else:
            # Vibe stores MCP settings in TOML under the .vibe directory
            self.config_path = os.path.expanduser("~/.vibe/config.toml")

    def _get_empty_config(self) -> Dict[str, Any]:
        """Get empty config structure for Mistral Vibe"""
        return {self.configure_key_name: []}

    def _load_config(self) -> Dict[str, Any]:
        """Load Mistral Vibe TOML configuration."""
        try:
            if not os.path.exists(self.config_path):
                return self._get_empty_config()

            with open(self.config_path, "rb") as f:
                config = tomli.load(f)

            if self.configure_key_name not in config or not isinstance(config[self.configure_key_name], list):
                config[self.configure_key_name] = []

            return config
        except Exception as e:
            logger.error(f"Error loading Mistral Vibe config: {e}")
            return self._get_empty_config()

    def _save_config(self, config: Dict[str, Any]) -> bool:
        """Save Mistral Vibe TOML configuration."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "wb") as f:
                tomli_w.dump(config, f)
            return True
        except Exception as e:
            logger.error(f"Error saving Mistral Vibe config: {e}")
            return False

    def get_servers(self) -> Dict[str, Any]:
        """Get all configured MCP servers keyed by server name."""
        config = self._load_config()
        servers = config.get(self.configure_key_name, [])
        result: Dict[str, Any] = {}

        for server in servers:
            name = server.get("name")
            if not name:
                continue
            normalized = {k: v for k, v in server.items() if k != "name"}
            result[name] = normalized

        return result

    def add_server(self, server_config: ServerConfig) -> bool:
        """Add or update a server in the Vibe config list."""
        config = self._load_config()
        servers = config.get(self.configure_key_name, [])

        server_name = server_config.name
        client_config = self.to_client_format(server_config)
        client_config["name"] = server_name

        updated = False
        for i, server in enumerate(servers):
            if server.get("name") == server_name:
                servers[i] = client_config
                updated = True
                break

        if not updated:
            servers.append(client_config)

        config[self.configure_key_name] = servers
        return self._save_config(config)

    def remove_server(self, server_name: str) -> bool:
        """Remove a server from the Vibe config list."""
        config = self._load_config()
        servers = config.get(self.configure_key_name, [])
        filtered = [server for server in servers if server.get("name") != server_name]

        if len(filtered) == len(servers):
            logger.warning(f"Server {server_name} not found in {self.display_name} config")
            return False

        config[self.configure_key_name] = filtered
        return self._save_config(config)

    def to_client_format(self, server_config: ServerConfig) -> Dict[str, Any]:
        """Convert ServerConfig to Mistral Vibe format."""
        if isinstance(server_config, STDIOServerConfig):
            result = {
                "transport": "stdio",
                "command": server_config.command,
                "args": server_config.args,
            }

            non_empty_env = server_config.get_filtered_env_vars(os.environ)
            if non_empty_env:
                result["env"] = non_empty_env
            return result

        return super().to_client_format(server_config)

    @classmethod
    def from_client_format(cls, server_name: str, client_config: Dict[str, Any]) -> ServerConfig:
        """Convert Vibe server entry to ServerConfig."""
        normalized = {k: v for k, v in client_config.items() if k != "transport"}
        return super().from_client_format(server_name, normalized)

    def is_client_installed(self) -> bool:
        """Check if Mistral Vibe is installed

        Returns:
            bool: True if vibe command is available, False otherwise
        """
        return shutil.which("vibe") is not None

    def get_client_info(self) -> Dict[str, str]:
        """Get information about this client

        Returns:
            Dict: Information about the client including display name, download URL, and config path
        """
        return {
            "name": self.display_name,
            "download_url": self.download_url,
            "config_file": self.config_path,
            "description": "Mistral's Vibe coding agent",
        }
