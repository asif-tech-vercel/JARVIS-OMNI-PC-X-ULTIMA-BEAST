"""
JARVIS Memory Module
Short and long-term memory.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Memory:
    """JARVIS memory system."""
    
    def __init__(self, memory_file: str = "data/memory.json"):
        self.memory_file = Path(memory_file)
        self.data = {"preferences": {}, "context": {}, "history": []}
        self._load()
    
    def _load(self):
        """Load memory from file."""
        if self.memory_file.exists():
            try:
                with open(self.memory_file) as f:
                    self.data = json.load(f)
            except:
                pass
    
    def _save(self):
        """Save memory to file."""
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.memory_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from memory."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set value in memory."""
        self.data[key] = value
        self._save()
    
    def remember(self, key: str, value: Any):
        """Remember something."""
        self.set(key, value)
        self.data["history"].append({"key": key, "value": value})
        self._save()
    
    def forget(self, key: str):
        """Forget something."""
        if key in self.data:
            del self.data[key]
            self._save()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get preference."""
        return self.data.get("preferences", {}).get(key, default)
    
    def set_preference(self, key: str, value: Any):
        """Set preference."""
        if "preferences" not in self.data:
            self.data["preferences"] = {}
        self.data["preferences"][key] = value
        self._save()
    
    def get_context(self) -> Dict:
        """Get current context."""
        return self.data.get("context", {})
    
    def set_context(self, **kwargs):
        """Set context."""
        if "context" not in self.data:
            self.data["context"] = {}
        self.data["context"].update(kwargs)
        self._save()
    
    def add_history(self, action: str, result: str):
        """Add to history."""
        self.data["history"].append({
            "action": action,
            "result": result
        })
        # Keep last 100 items
        self.data["history"] = self.data["history"][-100:]
        self._save()
    
    def get_history(self, limit: int = 10) -> list:
        """Get action history."""
        return self.data.get("history", [])[-limit:]


# Global memory instance
_memory = None


def get_memory(memory_file: str = "data/memory.json") -> Memory:
    """Get or create memory."""
    global _memory
    if _memory is None:
        _memory = Memory(memory_file)
    return _memory