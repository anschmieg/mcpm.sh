"""
MCPM Client package

Provides client-specific implementations and configuration
"""

from mcpm.clients.base import BaseClientManager
from mcpm.clients.client_config import ClientConfigManager
from mcpm.clients.client_registry import ClientRegistry
from mcpm.clients.managers.claude_code import ClaudeCodeManager
from mcpm.clients.managers.claude_desktop import ClaudeDesktopManager
from mcpm.clients.managers.crush import CrushManager
from mcpm.clients.managers.cursor import CursorManager
from mcpm.clients.managers.mistral_vibe import MistralVibeManager
from mcpm.clients.managers.trae import TraeManager
from mcpm.clients.managers.windsurf import WindsurfManager
from mcpm.clients.managers.zed import ZedManager

__all__ = [
    "BaseClientManager",
    "ClaudeDesktopManager",
    "ClaudeCodeManager",
    "WindsurfManager",
    "CursorManager",
    "TraeManager",
    "ClientConfigManager",
    "ClientRegistry",
    "MistralVibeManager",
    "ZedManager",
    "CrushManager",
]
