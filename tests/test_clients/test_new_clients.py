"""
Tests for new client adapters: Mistral Vibe, Zed, Crush, Cherry Studio
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest

from mcpm.clients.managers.cherry_studio import CherryStudioManager
from mcpm.clients.managers.crush import CrushManager
from mcpm.clients.managers.mistral_vibe import MistralVibeManager
from mcpm.clients.managers.zed import ZedManager


@pytest.fixture
def temp_json_config():
    """Create a temporary JSON config file for testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as f:
        config = {
            "mcpServers": {
                "test-server": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-test"],
                }
            }
        }
        f.write(json.dumps(config).encode("utf-8"))
        temp_path = f.name

    yield temp_path
    os.unlink(temp_path)


class TestMistralVibeManager:
    """Tests for MistralVibeManager"""

    def test_initialization(self):
        manager = MistralVibeManager()
        assert manager.client_key == "mistral-vibe"
        assert manager.display_name == "Mistral Vibe"
        assert ".mistral/vibe/mcp.json" in manager.config_path

    def test_initialization_with_override(self, temp_json_config):
        manager = MistralVibeManager(config_path_override=temp_json_config)
        assert manager.config_path == temp_json_config

    def test_get_empty_config(self):
        manager = MistralVibeManager()
        config = manager._get_empty_config()
        assert config == {"mcpServers": {}}

    def test_get_client_info(self):
        manager = MistralVibeManager()
        info = manager.get_client_info()
        assert info["name"] == "Mistral Vibe"
        assert "download_url" in info
        assert "config_file" in info
        assert "description" in info

    def test_is_client_installed(self):
        manager = MistralVibeManager()
        with patch("shutil.which", return_value="/usr/local/bin/vibe"):
            assert manager.is_client_installed()
        with patch("shutil.which", return_value=None):
            assert not manager.is_client_installed()


class TestZedManager:
    """Tests for ZedManager"""

    def test_initialization(self):
        manager = ZedManager()
        assert manager.client_key == "zed"
        assert manager.display_name == "Zed Editor"

    def test_initialization_with_override(self, temp_json_config):
        manager = ZedManager(config_path_override=temp_json_config)
        assert manager.config_path == temp_json_config

    def test_config_path_platform(self):
        with patch("platform.system", return_value="Darwin"):
            manager = ZedManager()
            assert "Library/Application Support/Zed/mcp.json" in manager.config_path

        with patch("platform.system", return_value="Linux"):
            manager = ZedManager()
            assert ".config/zed/mcp.json" in manager.config_path

        with patch("platform.system", return_value="Windows"):
            manager = ZedManager()
            assert "Zed" in manager.config_path and "mcp.json" in manager.config_path

    def test_get_empty_config(self):
        manager = ZedManager()
        config = manager._get_empty_config()
        assert config == {"mcpServers": {}}

    def test_get_client_info(self):
        manager = ZedManager()
        info = manager.get_client_info()
        assert info["name"] == "Zed Editor"
        assert "download_url" in info
        assert "config_file" in info

    def test_is_client_installed(self):
        manager = ZedManager()
        with patch("shutil.which", return_value="/usr/local/bin/zed"):
            assert manager.is_client_installed()
        with patch("shutil.which", return_value=None):
            assert not manager.is_client_installed()


class TestCrushManager:
    """Tests for CrushManager"""

    def test_initialization(self):
        manager = CrushManager()
        assert manager.client_key == "crush"
        assert manager.display_name == "Crush"
        assert ".crush/mcp.json" in manager.config_path

    def test_initialization_with_override(self, temp_json_config):
        manager = CrushManager(config_path_override=temp_json_config)
        assert manager.config_path == temp_json_config

    def test_get_empty_config(self):
        manager = CrushManager()
        config = manager._get_empty_config()
        assert config == {"mcpServers": {}}

    def test_get_client_info(self):
        manager = CrushManager()
        info = manager.get_client_info()
        assert info["name"] == "Crush"
        assert "download_url" in info
        assert "config_file" in info
        assert "description" in info

    def test_is_client_installed(self):
        manager = CrushManager()
        with patch("shutil.which", return_value="/usr/local/bin/crush"):
            assert manager.is_client_installed()
        with patch("shutil.which", return_value=None):
            assert not manager.is_client_installed()


class TestCherryStudioManager:
    """Tests for CherryStudioManager"""

    def test_initialization(self):
        manager = CherryStudioManager()
        assert manager.client_key == "cherry-studio"
        assert manager.display_name == "Cherry Studio"

    def test_initialization_with_override(self, temp_json_config):
        manager = CherryStudioManager(config_path_override=temp_json_config)
        assert manager.config_path == temp_json_config

    def test_config_path_platform(self):
        with patch("platform.system", return_value="Darwin"):
            manager = CherryStudioManager()
            assert "Library/Application Support/cherry-studio/mcp.json" in manager.config_path

        with patch("platform.system", return_value="Linux"):
            manager = CherryStudioManager()
            assert ".config/cherry-studio/mcp.json" in manager.config_path

        with patch("platform.system", return_value="Windows"):
            manager = CherryStudioManager()
            assert "cherry-studio" in manager.config_path and "mcp.json" in manager.config_path

    def test_get_empty_config(self):
        manager = CherryStudioManager()
        config = manager._get_empty_config()
        assert config == {"mcpServers": {}}

    def test_get_client_info(self):
        manager = CherryStudioManager()
        info = manager.get_client_info()
        assert info["name"] == "Cherry Studio"
        assert "download_url" in info
        assert "config_file" in info

    def test_is_client_installed(self):
        manager = CherryStudioManager()
        with patch("shutil.which", return_value="/usr/local/bin/cherry-studio"):
            assert manager.is_client_installed()
        with patch("shutil.which", return_value=None):
            assert not manager.is_client_installed()


class TestNewClientsServerOperations:
    """Test server operations for all new clients"""

    def test_mistral_vibe_server_operations(self, temp_json_config):
        manager = MistralVibeManager(config_path_override=temp_json_config)

        # Test list servers
        servers = manager.list_servers()
        assert "test-server" in servers

        # Test get server
        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_zed_server_operations(self, temp_json_config):
        manager = ZedManager(config_path_override=temp_json_config)

        servers = manager.list_servers()
        assert "test-server" in servers

        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_crush_server_operations(self, temp_json_config):
        manager = CrushManager(config_path_override=temp_json_config)

        servers = manager.list_servers()
        assert "test-server" in servers

        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_cherry_studio_server_operations(self, temp_json_config):
        manager = CherryStudioManager(config_path_override=temp_json_config)

        servers = manager.list_servers()
        assert "test-server" in servers

        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_add_and_remove_server(self, temp_json_config):
        """Test adding and removing servers"""
        manager = MistralVibeManager(config_path_override=temp_json_config)

        from mcpm.core.schema import STDIOServerConfig

        new_server = STDIOServerConfig(
            name="new-server",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
        )

        # Add server
        success = manager.add_server(new_server)
        assert success

        # Verify server was added
        server = manager.get_server("new-server")
        assert server is not None
        assert server.name == "new-server"

        # Remove server
        success = manager.remove_server("new-server")
        assert success

        # Verify server was removed
        server = manager.get_server("new-server")
        assert server is None
