"""
JARVIS Brain Module
Intent classification and reasoning engine.
"""

import json
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from jarvis_core.logger import get_logger


logger = get_logger()


@dataclass
class Intent:
    """Represents a parsed user intent."""
    intent: str
    confidence: float
    entities: Dict[str, str]
    raw_command: str
    risk_level: str = "low"
    needs_confirmation: bool = False


class IntentClassifier:
    """Classifies user commands into structured intents."""
    
    # Intent patterns - keyword-based for speed
    INTENT_PATTERNS = {
        "open_app": {
            "keywords": ["open", "launch", "start", "run"],
            "entities": {"app_name": r"(.+)"},
            "risk": "low"
        },
        "close_app": {
            "keywords": ["close", "quit", "exit", "kill"],
            "entities": {"app_name": r"(.+)"},
            "risk": "medium"
        },
        "create_file": {
            "keywords": ["create file", "new file", "make file"],
            "entities": {"path": r"(.+)"},
            "risk": "medium"
        },
        "create_folder": {
            "keywords": ["create folder", "new folder", "make folder", "create directory"],
            "entities": {"path": r"(.+)"},
            "risk": "medium"
        },
        "delete": {
            "keywords": ["delete", "remove", "erase"],
            "entities": {"path": r"(.+)"},
            "risk": "high"
        },
        "list_dir": {
            "keywords": ["list", "show", "display", "ls"],
            "entities": {"path": r"(.+)"},
            "risk": "low"
        },
        "search_files": {
            "keywords": ["search", "find", "look for"],
            "entities": {"pattern": r"(.+)"},
            "risk": "low"
        },
        "run_command": {
            "keywords": ["run", "execute", "cmd", "command"],
            "entities": {"command": r"(.+)"},
            "risk": "medium"
        },
        "get_system_info": {
            "keywords": ["system info", "cpu", "memory", "disk", "status"],
            "entities": {},
            "risk": "low"
        },
        "control_volume": {
            "keywords": ["volume", "mute", "unmute", "loud", "quiet"],
            "entities": {"action": r"(.+)"},
            "risk": "low"
        },
        "control_brightness": {
            "keywords": ["brightness", "bright", "dark", "dim"],
            "entities": {"level": r"(.+)"},
            "risk": "low"
        },
        "screenshot": {
            "keywords": ["screenshot", "capture screen", "take picture"],
            "entities": {},
            "risk": "low"
        },
        "shutdown": {
            "keywords": ["shutdown", "restart", "reboot", "sleep", "hibernate"],
            "entities": {},
            "risk": "high"
        },
        "help": {
            "keywords": ["help", "?"],
            "entities": {},
            "risk": "low"
        }
    }
    
    def classify(self, command: str) -> Intent:
        """Classify a command into an intent."""
        command_lower = command.lower().strip()
        
        # Check each intent pattern
        best_intent = "unknown"
        best_confidence = 0.0
        best_entities = {}
        best_risk = "low"
        
        for intent_name, pattern in self.INTENT_PATTERNS.items():
            for keyword in pattern["keywords"]:
                if keyword in command_lower:
                    # Found a match
                    confidence = 1.0  # Simple keyword match = 100%
                    
                    # Extract entities
                    entities = self._extract_entities(
                        command, 
                        keyword, 
                        pattern["entities"]
                    )
                    
                    if confidence > best_confidence:
                        best_intent = intent_name
                        best_confidence = confidence
                        best_entities = entities
                        best_risk = pattern["risk"]
        
        # Check if high risk
        needs_confirmation = best_risk == "high"
        
        return Intent(
            intent=best_intent,
            confidence=best_confidence,
            entities=best_entities,
            raw_command=command,
            risk_level=best_risk,
            needs_confirmation=needs_confirmation
        )
    
    def _extract_entities(self, command: str, keyword: str, entity_patterns: Dict[str, str]) -> Dict[str, str]:
        """Extract entities from command after keyword."""
        entities = {}
        
        # Find everything after the keyword
        command_lower = command.lower()
        keyword_pos = command_lower.find(keyword)
        
        if keyword_pos >= 0:
            after_keyword = command[keyword_pos + len(keyword):].strip()
            
            if after_keyword:
                # Try to extract as 'target' or 'path'
                entities["target"] = after_keyword
                entities["path"] = after_keyword
        
        return entities


class ResponseFormatter:
    """Format responses into structured JSON."""
    
    @staticmethod
    def format_success(intent: Intent, result: Dict[str, Any]) -> str:
        """Format a success response."""
        if "files" in result:
            files = result["files"]
            return f"✅ Found {len(files)} files:\n" + "\n".join([f"  - {f}" for f in files[:10]])
        elif "contents" in result:
            contents = result["contents"]
            lines = []
            for c in contents[:10]:
                icon = "📁" if c["type"] == "folder" else "📄"
                lines.append(f"  {icon} {c['name']}")
            return "✅ Contents:\n" + "\n".join(lines)
        elif "stdout" in result and result["stdout"]:
            return f"✅ {result['stdout'].strip()}"
        elif "action" in result:
            return f"✅ {result['action'].title()}"
        else:
            return "✅ Done"
    
    @staticmethod
    def format_error(error: str) -> str:
        """Format an error response."""
        return f"❌ Error: {error}"
    
    @staticmethod
    def format_json(intent: Intent, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format as JSON tool call response."""
        return {
            "intent": intent.intent,
            "confidence": intent.confidence,
            "risk_level": intent.risk_level,
            "confirmation_required": intent.needs_confirmation,
            "result": result,
            "success": result.get("success", False)
        }


# Global classifier
_classifier = None


def get_intent_classifier() -> IntentClassifier:
    """Get or create the intent classifier."""
    global _classifier
    if _classifier is None:
        _classifier = IntentClassifier()
    return _classifier


def classify_command(command: str) -> Intent:
    """Quickly classify a command."""
    return get_intent_classifier().classify(command)