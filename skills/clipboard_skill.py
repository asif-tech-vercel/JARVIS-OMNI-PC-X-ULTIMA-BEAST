"""
JARVIS Clipboard Skill
Clipboard monitoring and automation.
"""

import pyperclip
from jarvis_core.logger import get_logger


logger = get_logger()


def get_text() -> str:
    """Get clipboard text."""
    try:
        return pyperclip.paste()
    except:
        return ""


def set_text(text: str) -> bool:
    """Set clipboard text."""
    try:
        pyperclip.copy(text)
        logger.action("Set clipboard", "SUCCESS", "low")
        return True
    except Exception as e:
        logger.error(f"Clipboard error: {e}")
        return False


def clear() -> bool:
    """Clear clipboard."""
    return set_text("")


def copy_file(path: str) -> bool:
    """Copy file path to clipboard."""
    try:
        # On Windows, use file path
        import os
        if os.path.exists(path):
            # Use drag-drop format
            pyperclip.copy(os.path.abspath(path))
            return True
    except:
        pass
    return False