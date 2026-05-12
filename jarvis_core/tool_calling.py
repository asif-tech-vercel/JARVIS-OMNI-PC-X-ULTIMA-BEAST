"""
JARVIS Tool Call Protocol
Standard JSON format for tool calling.
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ToolCall:
    """Represents a tool call."""
    tool_name: str
    arguments: Dict[str, Any]
    description: str = ""


@dataclass
class Step:
    """Represents a single step in a plan."""
    step: int
    description: str
    tool: str
    arguments: Dict[str, Any]


@dataclass 
class ActionPlan:
    """Represents a complete action plan."""
    intent: str
    confidence: int
    risk_level: str
    confirmation_required: bool
    plan: List[Step]
    fallback_strategy: List[str]
    final_expected_output: str
    tools_to_use: List[ToolCall]
    safety_notes: str = ""


class ToolCallProtocol:
    """
    Standard JSON format for JARVIS tool calls.
    Used by the brain for multi-step planning.
    """
    
    # Tool definitions
    TOOLS = {
        "open_app": {
            "description": "Open an application",
            "parameters": ["app_path"],
            "risk": "low"
        },
        "close_app": {
            "description": "Close an application",
            "parameters": ["app_name"],
            "risk": "medium"
        },
        "click": {
            "description": "Click at coordinates or image",
            "parameters": ["x", "y", "image"],
            "risk": "medium"
        },
        "type_text": {
            "description": "Type text",
            "parameters": ["text"],
            "risk": "medium"
        },
        "press_key": {
            "description": "Press a key",
            "parameters": ["key"],
            "risk": "medium"
        },
        "create_file": {
            "description": "Create a file",
            "parameters": ["path", "content"],
            "risk": "medium"
        },
        "create_folder": {
            "description": "Create a folder",
            "parameters": ["path"],
            "risk": "medium"
        },
        "delete": {
            "description": "Delete file or folder",
            "parameters": ["path"],
            "risk": "high"
        },
        "run_command": {
            "description": "Run terminal command",
            "parameters": ["command"],
            "risk": "high"
        },
        "search_files": {
            "description": "Search for files",
            "parameters": ["directory", "pattern"],
            "risk": "low"
        },
        "list_dir": {
            "description": "List directory",
            "parameters": ["path"],
            "risk": "low"
        },
        "set_volume": {
            "description": "Set volume level",
            "parameters": ["level"],
            "risk": "low"
        },
        "screenshot": {
            "description": "Take screenshot",
            "parameters": [],
            "risk": "low"
        },
        "navigate_browser": {
            "description": "Navigate browser",
            "parameters": ["url"],
            "risk": "low"
        },
        "search_web": {
            "description": "Search the web",
            "parameters": ["query"],
            "risk": "low"
        }
    }
    
    @classmethod
    def get_risk_level(cls, tool_name: str) -> str:
        """Get risk level for a tool."""
        if tool_name in cls.TOOLS:
            return cls.TOOLS[tool_name].get("risk", "medium")
        return "medium"
    
    @classmethod
    def requires_confirmation(cls, tool_name: str) -> bool:
        """Check if tool requires confirmation."""
        return cls.get_risk_level(tool_name) in ["high"]
    
    @classmethod
    def create_plan(cls, intent: str, steps: List[Dict]) -> ActionPlan:
        """Create an action plan from steps."""
        plan_steps = [
            Step(step=i+1, description=s["description"], tool=s["tool"], arguments=s.get("arguments", {}))
            for i, s in enumerate(steps)
        ]
        
        # Determine overall risk
        max_risk = "low"
        for s in steps:
            risk = cls.get_risk_level(s.get("tool", ""))
            if risk == "high":
                max_risk = "high"
            elif risk == "medium" and max_risk != "high":
                max_risk = "medium"
        
        # Check if confirmation needed
        confirm = any(cls.requires_confirmation(s.get("tool", "")) for s in steps)
        
        return ActionPlan(
            intent=intent,
            confidence=90,
            risk_level=max_risk,
            confirmation_required=confirm,
            plan=plan_steps,
            fallback_strategy=["Try alternate method", "Use vision automation", "Ask user"],
            final_expected_output="Task completed successfully",
            tools_to_use=[]
        )
    
    @classmethod
    def to_json(cls, plan: ActionPlan) -> str:
        """Serialize plan to JSON."""
        return json.dumps(asdict(plan), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> ActionPlan:
        """Deserialize plan from JSON."""
        data = json.loads(json_str)
        return ActionPlan(**data)


class Planner:
    """Multi-step task planner."""
    
    def __init__(self):
        self.protocol = ToolCallProtocol()
    
    def plan(self, command: str) -> ActionPlan:
        """Create a plan for a command."""
        command_lower = command.lower()
        
        # Simple rule-based planning
        if "open" in command_lower and ("notepad" in command_lower or "editor" in command_lower):
            return self._plan_open_notepad(command)
        
        elif "search" in command_lower and "google" in command_lower:
            return self._plan_search_google(command)
        
        elif "download" in command_lower:
            return self._plan_download(command)
        
        elif "create" in command_lower and "project" in command_lower:
            return self._plan_create_project(command)
        
        else:
            # Default simple command
            return self._plan_simple(command)
    
    def _plan_open_notepad(self, command: str) -> ActionPlan:
        """Plan to open notepad with content."""
        steps = [
            {"tool": "open_app", "arguments": {"app_path": "notepad.exe"}, "description": "Open Notepad"},
            {"tool": "type_text", "arguments": {"text": ""}, "description": "Type content"}
        ]
        return self.protocol.create_plan("open_notepad", steps)
    
    def _plan_search_google(self, command: str) -> ActionPlan:
        """Plan to search Google."""
        # Extract query
        query = command.lower().replace("search", "").replace("google", "").strip()
        
        steps = [
            {"tool": "open_app", "arguments": {"app_path": "chrome.exe"}, "description": "Open Chrome"},
            {"tool": "navigate_browser", "arguments": {"url": f"https://google.com/search?q={query}"}, "description": "Search Google"}
        ]
        return self.protocol.create_plan("search_google", steps)
    
    def _plan_download(self, command: str) -> ActionPlan:
        """Plan for download."""
        steps = [
            {"tool": "list_dir", "arguments": {"path": "downloads"}, "description": "Open downloads"}
        ]
        return self.protocol.create_plan("download", steps)
    
    def _plan_create_project(self, command: str) -> ActionPlan:
        """Plan to create project folder."""
        steps = [
            {"tool": "create_folder", "arguments": {"path": "projects/new_project"}, "description": "Create project folder"},
            {"tool": "create_file", "arguments": {"path": "projects/new_project/README.md"}, "description": "Create README"}
        ]
        return self.protocol.create_plan("create_project", steps)
    
    def _plan_simple(self, command: str) -> ActionPlan:
        """Simple command plan."""
        steps = [
            {"tool": "run_command", "arguments": {"command": command}, "description": "Run command"}
        ]
        return self.protocol.create_plan("run_command", steps)


# Global planner
_planner = None


def get_planner() -> Planner:
    """Get or create the planner."""
    global _planner
    if _planner is None:
        _planner = Planner()
    return _planner


def create_plan(command: str) -> ActionPlan:
    """Quick plan creation."""
    return get_planner().plan(command)