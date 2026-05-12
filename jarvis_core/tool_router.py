"""
JARVIS Tool Router
Routes commands to the correct skill module.
"""

import importlib
import os
from pathlib import Path
from typing import Any, Callable, Dict

from jarvis_core.logger import get_logger


class ToolRouter:
    """Routes commands to skills."""
    
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills = {}
        self.logger = get_logger()
        self._load_skills()
    
    def _load_skills(self):
        """Load all skill modules."""
        if not self.skills_dir.exists():
            self.logger.warning(f"Skills directory not found: {self.skills_dir}")
            return
        
        for py_file in self.skills_dir.glob("*.py"):
            if py_file.stem.startswith("_"):
                continue
            
            try:
                module_name = f"skills.{py_file.stem}"
                module = importlib.import_module(module_name)
                
                # Get the skill class or functions
                skill_name = py_file.stem
                if hasattr(module, "get_skill"):
                    self.skills[skill_name] = module.get_skill()
                elif hasattr(module, f"{skill_name}_skill"):
                    self.skills[skill_name] = getattr(module, f"{skill_name}_skill")
                elif hasattr(module, "handle_intent"):
                    # Allow skill to have handle_intent directly
                    self.skills[skill_name] = module.handle_intent
                
                self.logger.debug(f"Loaded skill: {skill_name}")
            except Exception as e:
                self.logger.error(f"Failed to load skill {py_file.stem}: {e}")
    
    def route(self, intent: str, **kwargs) -> dict:
        """Route a command to the appropriate skill."""
        # Parse intent to find the skill
        intent_lower = intent.lower()
        
        # Map intent to skill
        skill_map = {
            "open": "app_control",
            "close": "app_control",
            "launch": "app_control",
            "start": "app_control",
            "file": "file_manager",
            "folder": "file_manager",
            "create": "file_manager",
            "delete": "file_manager",
            "move": "file_manager",
            "copy": "file_manager",
            "search": "file_manager",
            "run": "terminal_control",
            "command": "terminal_control",
            "terminal": "terminal_control",
            "execute": "terminal_control",
            "bash": "terminal_control",
            "powershell": "terminal_control",
            "list": "file_manager",
        }
        
        # Find matching skill
        skill_name = None
        for key, skill in skill_map.items():
            if key in intent_lower:
                skill_name = skill
                break
        
        if not skill_name or skill_name not in self.skills:
            return {
                "success": False,
                "error": f"No skill found for intent: {intent}"
            }
        
        # Execute the skill
        try:
            skill = self.skills[skill_name]
            
            if callable(skill):
                # Call with intent and kwargs
                result = skill(intent, **kwargs)
            elif isinstance(skill, dict):
                # Skill is a dict of functions - try to find matching function
                intent_action = intent_lower.split()[0] if intent_lower.split() else "default"
                if intent_action in skill:
                    func = skill[intent_action]
                    result = func(**kwargs)
                else:
                    result = {"success": False, "error": f"No function found for {intent_action}"}
            else:
                result = {"success": False, "error": "Skill not callable"}
            
            return result
        except Exception as e:
            self.logger.error(f"Skill execution error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_skills(self) -> list:
        """List all available skills."""
        return list(self.skills.keys())


# Global router instance
_router = None


def get_router(skills_dir: str = "skills") -> ToolRouter:
    """Get or create the global router."""
    global _router
    if _router is None:
        _router = ToolRouter(skills_dir)
    return _router