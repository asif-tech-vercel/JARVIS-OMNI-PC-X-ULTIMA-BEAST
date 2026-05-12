"""JARVIS Window Manager Skill - Window control.""""

try:
    import pygetwindow as gw
    HAS_GW = True
except ImportError:
    HAS_GW = False

from jarvis_core.logger import get_logger

logger = get_logger()

def get_active_window() -> dict:
    if not HAS_GW: return {"success": False, "error": "Not available"}
    win = gw.getActiveWindow()
    return {"success": True, "title": win.title, "x": win.left} if win else {"success": False}

def list_windows() -> list:
    if not HAS_GW: return []
    wins = gw.getAllTitles()
    return [{"title": w} for w in wins if w]

def focus(title: str) -> dict:
    if not HAS_GW: return {"success": False}
    wins = gw.getWindowsWithTitle(title)
    if wins:
        wins[0].activate()
        return {"success": True}
    return {"success": False, "error": "Not found"}

def minimize(title: str = None) -> dict:
    if not HAS_GW: return {"success": False}
    wins = gw.getWindowsWithTitle(title) if title else [gw.getActiveWindow()]
    if wins:
        wins[0].minimize()
        return {"success": True}
    return {"success": False}

def maximize(title: str = None) -> dict:
    if not HAS_GW: return {"success": False}
    wins = gw.getWindowsWithTitle(title) if title else [gw.getActiveWindow()]
    if wins:
        wins[0].maximize()
        return {"success": True}
    return {"success": False}