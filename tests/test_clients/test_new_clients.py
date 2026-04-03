"""
Tests for new client adapters: Mistral Vibe, Zed, Crush, Cherry Studio
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest
import tomli

from mcpm.clients.managers.cherry_studio import CherryStudioManager
from mcpm.clients.managers.crush import CrushManager
from mcpm.clients.managers.mistral_vibe import MistralVibeManager
from mcpm.clients.managers.zed import ZedManager
from mcpm.core.schema import STDIOServerConfig


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


@pytest.fixture
def temp_toml_config():
    """Create a temporary TOML config file for Mistral Vibe testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as f:
        f.write(
            b"""
[[mcp_servers]]
name = "test-server"
transport = "stdio"
command = "npx"
args = ["-y", "@modelcontextprotocol/server-test"]
"""
        )
        temp_path = f.name

    yield temp_path
    os.unlink(temp_path)


class TestMistralVibeManager:
    """Tests for MistralVibeManager"""

    def test_initialization(self):
        manager = MistralVibeManager()
        assert manager.client_key == "mistral-vibe"
        assert manager.display_name == "Mistral Vibe"
        assert ".vibe/config.toml" in manager.config_path

    def test_initialization_with_override(self, temp_toml_config):
        manager = MistralVibeManager(config_path_override=temp_toml_config)
        assert manager.config_path == temp_toml_config

    def test_get_empty_config(self):
        manager = MistralVibeManager()
        config = manager._get_empty_config()
        assert config == {manager.configure_key_name: []}

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


class TestMistralVibeLoadConfigEdgeCases:
    """Edge case tests for MistralVibeManager._load_config"""

    def test_load_config_missing_file(self, temp_toml_config):
        """Missing config file should return empty config and allow subsequent operations."""
        # Use a path that definitely doesn't exist
        import uuid
        non_existent_path = f"/tmp/mcpm_test_missing_{uuid.uuid4()}.toml"
        manager = MistralVibeManager(config_path_override=non_existent_path)

        config = manager._load_config()
        assert config == {manager.configure_key_name: []}

        # Should be able to add a server after missing file
        new_server = STDIOServerConfig(
            name="new-server",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-test"],
        )
        assert manager.add_server(new_server)

    def test_load_config_malformed_toml(self):
        """Malformed TOML should return empty config without raising."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as f:
            f.write(b"[[mcp_servers]]\nname = 'unclosed string")
            temp_path = f.name

        try:
            manager = MistralVibeManager(config_path_override=temp_path)
            config = manager._load_config()
            assert config == {manager.configure_key_name: []}
        finally:
            os.unlink(temp_path)

    def test_load_config_wrong_mcp_servers_type(self):
        """TOML where mcp_servers is not a list should normalize to empty list."""
        import tomli_w

        with tempfile.NamedTemporaryFile(delete=False, suffix=".toml") as f:
            config = {"mcp_servers": {"name": "test-server"}}
            tomli_w.dump(config, f)
            temp_path = f.name

        try:
            manager = MistralVibeManager(config_path_override=temp_path)
            config = manager._load_config()
            assert config == {manager.configure_key_name: []}
        finally:
            os.unlink(temp_path)

    def test_stdio_server_env_roundtrip(self, temp_toml_config):
        """STDIOServerConfig with env vars should round-trip correctly."""
        manager = MistralVibeManager(config_path_override=temp_toml_config)

        stdio_server = STDIOServerConfig(
            name="env-server",
            command="bash",
            args=["-lc", "echo 'hello'"],
            env={"FOO": "BAR", "BAZ": "QUX"},
        )

        # Persist the server
        assert manager.add_server(stdio_server)

        # Load raw TOML and verify serialized format
        with open(temp_toml_config, "rb") as f:
            config_data = tomli.load(f)

        servers = config_data.get(manager.configure_key_name, [])
        stdio_entry = next((s for s in servers if s.get("name") == "env-server"), None)
        assert stdio_entry is not None
        assert stdio_entry["transport"] == "stdio"
        assert stdio_entry["command"] == stdio_server.command
        assert stdio_entry["args"] == stdio_server.args
        assert stdio_entry["env"] == {"FOO": "BAR", "BAZ": "QUX"}

        # Reload and verify round-trip via get_server
        reloaded_manager = MistralVibeManager(config_path_override=temp_toml_config)
        reloaded_server = reloaded_manager.get_server("env-server")
        assert reloaded_server is not None
        assert reloaded_server.name == stdio_server.name
        assert reloaded_server.command == stdio_server.command
        assert reloaded_server.args == stdio_server.args
        # env should round-trip (transport field stripped by from_client_format)
        assert reloaded_server.env == {"FOO": "BAR", "BAZ": "QUX"}


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
            assert "Library/Application Support/Zed/settings.json" in manager.config_path

        with patch("platform.system", return_value="Linux"):
            manager = ZedManager()
            assert ".config/zed/settings.json" in manager.config_path

        with patch("platform.system", return_value="Windows"):
            manager = ZedManager()
            assert "Zed" in manager.config_path and "settings.json" in manager.config_path

    def test_get_empty_config(self):
        manager = ZedManager()
        config = manager._get_empty_config()
        assert config == {"context_servers": {}}

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

    def test_mistral_vibe_server_operations(self, temp_toml_config):
        manager = MistralVibeManager(config_path_override=temp_toml_config)

        # Test list servers
        servers = manager.list_servers()
        assert "test-server" in servers

        # Test get server
        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_zed_server_operations(self, temp_json_config):
        with open(temp_json_config, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "context_servers": {
                        "test-server": {
                            "command": "npx",
                            "args": ["-y", "@modelcontextprotocol/server-test"],
                        }
                    }
                },
                f,
            )

        manager = ZedManager(config_path_override=temp_json_config)

        servers = manager.list_servers()
        assert "test-server" in servers

        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_zed_add_and_remove_server(self, temp_json_config):
        """Test add/update/remove for Zed with context_servers key."""
        manager = ZedManager(config_path_override=temp_json_config)

        new_server = STDIOServerConfig(
            name="zed-new-server",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
        )

        # Add server
        assert manager.add_server(new_server)

        # Verify written to context_servers
        with open(temp_json_config, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "zed-new-server" in data[manager.configure_key_name]
        assert data[manager.configure_key_name]["zed-new-server"]["command"] == "npx"

        # Verify round-trip
        server = manager.get_server("zed-new-server")
        assert server is not None
        assert server.name == "zed-new-server"

        # Remove server
        assert manager.remove_server("zed-new-server")
        assert manager.get_server("zed-new-server") is None

        # Verify persisted removal
        with open(temp_json_config, "r", encoding="utf-8") as f:
            data_after = json.load(f)
        assert "zed-new-server" not in data_after.get(manager.configure_key_name, {})

    def test_crush_server_operations(self, temp_json_config):
        manager = CrushManager(config_path_override=temp_json_config)

        servers = manager.list_servers()
        assert "test-server" in servers

        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_crush_add_and_remove_server(self, temp_json_config):
        """Test add/update/remove for Crush with mcpServers key."""
        manager = CrushManager(config_path_override=temp_json_config)

        new_server = STDIOServerConfig(
            name="crush-new-server",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
        )

        # Add server
        assert manager.add_server(new_server)

        # Verify written to mcpServers
        with open(temp_json_config, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "crush-new-server" in data[manager.configure_key_name]

        # Verify round-trip
        server = manager.get_server("crush-new-server")
        assert server is not None
        assert server.name == "crush-new-server"

        # Remove server
        assert manager.remove_server("crush-new-server")
        assert manager.get_server("crush-new-server") is None

    def test_cherry_studio_server_operations(self, temp_json_config):
        manager = CherryStudioManager(config_path_override=temp_json_config)

        servers = manager.list_servers()
        assert "test-server" in servers

        server = manager.get_server("test-server")
        assert server is not None
        assert server.name == "test-server"

    def test_cherry_studio_add_and_remove_server(self, temp_json_config):
        """Test add/update/remove for Cherry Studio with mcpServers key."""
        manager = CherryStudioManager(config_path_override=temp_json_config)

        new_server = STDIOServerConfig(
            name="cherry-new-server",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem"],
        )

        # Add server
        assert manager.add_server(new_server)

        # Verify written to mcpServers
        with open(temp_json_config, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert "cherry-new-server" in data[manager.configure_key_name]

        # Verify round-trip
        server = manager.get_server("cherry-new-server")
        assert server is not None
        assert server.name == "cherry-new-server"

        # Remove server
        assert manager.remove_server("cherry-new-server")
        assert manager.get_server("cherry-new-server") is None

    def test_add_and_remove_server(self, temp_toml_config):
        """Test adding and removing servers"""
        manager = MistralVibeManager(config_path_override=temp_toml_config)

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

        # Ensure persisted in TOML list format
        with open(temp_toml_config, "rb") as f:
            config = tomli.load(f)
        assert isinstance(config.get(manager.configure_key_name), list)
