"""
JARVIS Permission Manager
Safe execution with permission levels.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from jarvis_core.logger import get_logger


logger = get_logger()


@dataclass
class Permission:
    """Permission level."""
    level: str  # low, medium, high, blocked
    description: str
    requires_confirmation: bool


class PermissionManager:
    """Manage permissions for actions."""
    
    # Default permissions
    DEFAULT_PERMISSIONS = {
        # Low risk - no confirmation
        "open_app": Permission("low", "Open app", False),
        "click": Permission("low", "Click", False),
        "list_dir": Permission("low", "List directory", False),
        "search_files": Permission("low", "Search files", False),
        "get_system_info": Permission("low", "Get system info", False),
        "get_volume": Permission("low", "Get volume", False),
        
        # Medium risk - confirmation sometimes
        "close_app": Permission("medium", "Close app", False),
        "create_file": Permission("medium", "Create file", False),
        "create_folder": Permission("medium", "Create folder", False),
        "type_text": Permission("medium", "Type text", False),
        "set_volume": Permission("medium", "Set volume", False),
        
        # High risk - always confirmation
        "delete": Permission("high", "Delete file", True),
        "run_command": Permission("high", "Run command", True),
        "shutdown": Permission("high", "Shutdown", True),
        "restart": Permission("high", "Restart", True),
        "kill_process": Permission("high", "Kill process", True),
        
        # Blocked
        "format_drive": Permission("blocked", "Format drive", False),
    }
    
    def __init__(self):
        self.mode = "auto"  # safe, auto, beast
        self.custom_rules = {}
        self.blocked_actions = set()
    
    def check(self, action: str) -> tuple[bool, str]:
        """
        Check if action is allowed.
        
        Returns:
            (allowed, reason)
        """
        # Check blocked
        if action in self.blocked_actions:
            return False, "Action is blocked"
        
        # Get permission
        perm = self.DEFAULT_PERMISSIONS.get(action)
        
        if not perm:
            # Unknown action - use default
            if self.mode == "safe":
                return False, f"Unknown action: {action}"
            return True, "Allowed"
        
        # Check blocked
        if perm.level == "blocked":
            return False, "Action is blocked"
        
        # Check confirmation
        if self.mode == "safe" and perm.requires_confirmation:
            return False, f"Confirmation required for {action}"
        
        if self.mode == "auto" and perm.requires_confirmation:
            # Confirm for high risk
            if perm.level == "high":
                return False, f"Confirmation required for {action}"
        
        # beast mode - allow all
        if self.mode == "beast":
            return True, "Allowed (beast mode)"
        
        return True, "Allowed"
    
    def allow(self, action: str):
        """Allow an action."""
        if action in self.blocked_actions:
            self.blocked_actions.remove(action)
        logger.info(f"Allowed: {action}")
    
    def block(self, action: str):
        """Block an action."""
        self.blocked_actions.add(action)
        logger.info(f"Blocked: {action}")
    
    def set_mode(self, mode: str):
        """Set permission mode."""
        if mode in ["safe", "auto", "beast"]:
            self.mode = mode
            logger.info(f"Permission mode: {mode}")


# Global permission manager
_permission_manager = None


def get_permission_manager() -> PermissionManager:
    """Get or create permission manager."""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager