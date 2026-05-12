"""
JARVIS Automation Core - Mouse and Keyboard Control
Click, type, drag, hotkeys, window management.
"""

import time
import random
from typing import Tuple, Optional
from dataclasses import dataclass

try:
    import pyautogui
    HAS_PYAUTOGUI = True
    # Configure PyAutoGUI
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
except ImportError:
    HAS_PYAUTOGUI = False

try:
    import keyboard
    HAS_KEYBOARD = True
except ImportError:
    HAS_KEYBOARD = False

try:
    import mouse
    HAS_MOUSE = True
except ImportError:
    HAS_MOUSE = False

try:
    import pygetwindow as gw
    HAS_PYWIN = True
except ImportError:
    HAS_PYWIN = False

from jarvis_core.logger import get_logger


logger = get_logger()


@dataclass
class Point:
    """Represents a screen point."""
    x: int
    y: int


class AutomationCore:
    """Core automation for mouse and keyboard."""
    
    def __init__(self):
        self.typing_speed = config.VoiceConfig.TYPING_SPEED if hasattr(config, 'VoiceConfig') else 0.05
        self.safe_mode = True
        self.last_position = None
    
    # ==================== MOUSE CONTROL ====================
    
    def move_to(self, x: int, y: int, duration: float = 0.5):
        """Move mouse to position."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            pyautogui.moveTo(x, y, duration=duration)
            self.last_position = (x, y)
            logger.action(f"Move mouse to ({x}, {y})", "SUCCESS", "low")
            return {"success": True, "position": (x, y)}
        except Exception as e:
            logger.error(f"Failed to move mouse: {e}")
            return {"success": False, "error": str(e)}
    
    def click(self, x: int = None, y: int = None, button: str = "left", clicks: int = 1):
        """
        Click at position or current position.
        
        Args:
            x, y: Position (None = current)
            button: left, right, middle
            clicks: number of clicks
        """
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, button=button)
            else:
                pyautogui.click(clicks=clicks, button=button)
            
            logger.action(f"Click ({x}, {y}) button={button}", "SUCCESS", "medium")
            return {"success": True, "clicked": (x, y)}
        except Exception as e:
            logger.error(f"Failed to click: {e}")
            return {"success": False, "error": str(e)}
    
    def double_click(self, x: int = None, y: int = None):
        """Double click."""
        return self.click(x, y, clicks=2)
    
    def right_click(self, x: int = None, y: int = None):
        """Right click."""
        return self.click(x, y, button="right")
    
    def click_at_image(self, image: str, confidence: float = 0.8) -> dict:
        """
        Click at image location on screen.
        
        Args:
            image: Path to template image
            confidence: Match confidence threshold
        """
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            # Try to locate image on screen
            position = pyautogui.locateCenterOnScreen(image, confidence=confidence)
            
            if position:
                pyautogui.click(position)
                logger.action(f"Click at image: {image}", "SUCCESS", "medium")
                return {"success": True, "position": position}
            else:
                return {"success": False, "error": f"Image not found: {image}"}
        except Exception as e:
            logger.error(f"Failed to click image: {e}")
            return {"success": False, "error": str(e)}
    
    def mouse_down(self, button: str = "left"):
        """Hold mouse button down."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            pyautogui.mouseDown(button=button)
            logger.action(f"Mouse down: {button}", "SUCCESS", "medium")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mouse_up(self, button: str = "left"):
        """Release mouse button."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            pyautogui.mouseUp(button=button)
            logger.action(f"Mouse up: {button}", "SUCCESS", "medium")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def drag_to(self, x: int, y: int, duration: float = 0.5):
        """Drag mouse to position."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            pyautogui.dragTo(x, y, duration=duration)
            logger.action(f"Drag to ({x}, {y})", "SUCCESS", "medium")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def scroll(self, clicks: int = 1):
        """Scroll vertically."""
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            pyautogui.scroll(clicks)
            logger.action(f"Scroll {clicks} clicks", "SUCCESS", "low")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        if not HAS_PYAUTOGUI:
            return (0, 0)
        return pyautogui.position()
    
    # ==================== KEYBOARD CONTROL ====================
    
    def type(self, text: str, speed: float = None):
        """
        Type text with human-like speed.
        
        Args:
            text: Text to type
            speed: Seconds per character (None = use default)
        """
        if not HAS_PYAUTOGUI:
            return {"success": False, "error": "pyautogui not available"}
        
        try:
            typing_speed = speed or self.typing_speed
            
            # Type with delay for human-like feel
            for char in text:
                pyautogui.write(char, interval=typing_speed)
            
            logger.action(f"Type: {text[:20]}...", "SUCCESS", "medium")
            return {"success": True, "typed": text}
        except Exception as e:
            logger.error(f"Failed to type: {e}")
            return {"success": False, "error": str(e)}
    
    def press(self, key: str):
        """
        Press a key or key combination.
        
        Args:
            key: Key name (e.g., 'enter', 'ctrl+c', 'alt+tab')
        """
        if not (HAS_KEYBOARD or HAS_PYAUTOGUI):
            return {"success": False, "error": "No keyboard library available"}
        
        try:
            if HAS_KEYBOARD:
                keyboard.send(key)
            else:
                pyautogui.press(key)
            
            logger.action(f"Press key: {key}", "SUCCESS", "medium")
            return {"success": True, "key": key}
        except Exception as e:
            logger.error(f"Failed to press key: {e}")
            return {"success": False, "error": str(e)}
    
    def hold(self, key: str):
        """Hold a key down."""
        if not HAS_KEYBOARD:
            return {"success": False, "error": "keyboard not available"}
        
        try:
            keyboard.press(key)
            logger.action(f"Hold key: {key}", "SUCCESS", "medium")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def release(self, key: str):
        """Release a held key."""
        if not HAS_KEYBOARD:
            return {"success": False, "error": "keyboard not available"}
        
        try:
            keyboard.release(key)
            logger.action(f"Release key: {key}", "SUCCESS", "medium")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def write_hotkey(self, *keys):
        """Press a key combination (e.g., ctrl+c)."""
        if not HAS_KEYBOARD:
            return {"success": False, "error": "keyboard not available"}
        
        try:
            keyboard.call("send_hotkey", *keys)
            logger.action(f"Hotkey: {'+'.join(keys)}", "SUCCESS", "medium")
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== WINDOW CONTROL ====================
    
    def get_active_window(self) -> dict:
        """Get the currently active window."""
        if not HAS_PYWIN:
            return {"success": False, "error": "pygetwindow not available"}
        
        try:
            window = gw.getActiveWindow()
            if window:
                return {
                    "success": True,
                    "window": {
                        "title": window.title,
                        "x": window.left,
                        "y": window.top,
                        "width": window.width,
                        "height": window.height
                    }
                }
            return {"success": False, "error": "No active window"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def activate_window(self, title: str) -> dict:
        """Activate a window by title."""
        if not HAS_PYWIN:
            return {"success": False, "error": "pygetwindow not available"}
        
        try:
            windows = gw.getWindowsWithTitle(title)
            if windows:
                window = windows[0]
                window.activate()
                logger.action(f"Activate window: {title}", "SUCCESS", "low")
                return {"success": True}
            return {"success": False, "error": f"Window not found: {title}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def minimize_window(self, title: str = None) -> dict:
        """Minimize a window."""
        if not HAS_PYWIN:
            return {"success": False, "error": "pygetwindow not available"}
        
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].minimize()
                    logger.action(f"Minimize window: {title}", "SUCCESS", "low")
                    return {"success": True}
            elif title is None:
                # Minimize active window
                gw.getActiveWindow().minimize()
                return {"success": True}
            return {"success": False, "error": f"Window not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def maximize_window(self, title: str = None) -> dict:
        """Maximize a window."""
        if not HAS_PYWIN:
            return {"success": False, "error": "pygetwindow not available"}
        
        try:
            if title:
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    windows[0].maximize()
                    logger.action(f"Maximize window: {title}", "SUCCESS", "low")
                    return {"success": True}
            gw.getActiveWindow().maximize()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== DELAY & UTILITY ====================
    
    def wait(self, seconds: float):
        """Wait for specified seconds."""
        time.sleep(seconds)
        return {"success": True, "waited": seconds}
    
    def random_delay(self, min_sec: float = 0.1, max_sec: float = 0.5):
        """Wait for random duration (human-like)."""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
        return {"success": True, "waited": delay}


# Global automation instance
_automation = None


def get_automation() -> AutomationCore:
    """Get or create the automation core."""
    global _automation
    if _automation is None:
        _automation = AutomationCore()
    return _automation


# Convenience functions
def click(x=None, y=None, button="left"):
    """Quick click."""
    return get_automation().click(x, y, button)

def double_click(x=None, y=None):
    """Quick double click."""
    return get_automation().double_click(x, y)

def type_text(text: str, speed: float = None):
    """Quick type."""
    return get_automation().type(text, speed)

def press_key(key: str):
    """Quick press key."""
    return get_automation().press(key)