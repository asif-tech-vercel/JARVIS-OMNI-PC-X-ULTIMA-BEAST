"""
JARVIS App Control Skill
Open/close apps, focus windows, manage processes.
"""

import os
import subprocess
import sys
from typing import Dict, Any

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

try:
    import pygetwindow as gw
    HAS_PYWIN = True
except ImportError:
    HAS_PYWIN = False

from jarvis_core.logger import get_logger


logger = get_logger()


def get_skill():
    """Return the app control skill functions."""
    return {
        "open_app": open_app,
        "close_app": close_app,
        "list_processes": list_processes,
        "kill_process": kill_process,
        "focus_window": focus_window,
    }


def open_app(app_path: str, args: list = None) -> Dict[str, Any]:
    """
    Open an application.
    
    Args:
        app_path: Path to the application or app name
        args: Optional command-line arguments
    
    Returns:
        Dict with success status and details
    """
    try:
        # Try as direct path first
        if os.path.exists(app_path):
            subprocess.Popen([app_path] + (args or []))
            logger.action(f"Open app: {app_path}", "SUCCESS", "low")
            return {"success": True, "action": "opened", "app": app_path}
        
        # Try as command
        result = subprocess.run(
            [app_path] + (args or []),
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 or result.returncode is None:
            logger.action(f"Open app: {app_path}", "SUCCESS", "low")
            return {"success": True, "action": "opened", "app": app_path}
        else:
            return {"success": False, "error": result.stderr}
            
    except FileNotFoundError:
        # Try using 'start' command on Windows
        try:
            subprocess.run(["start", app_path], shell=True, check=True)
            logger.action(f"Open app (start): {app_path}", "SUCCESS", "low")
            return {"success": True, "action": "opened", "app": app_path}
        except Exception as e:
            logger.error(f"Failed to open app: {e}")
            return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Failed to open app: {e}")
        return {"success": False, "error": str(e)}


def close_app(app_name: str) -> Dict[str, Any]:
    """
    Close an application by name.
    
    Args:
        app_name: Name of the application
    
    Returns:
        Dict with success status and details
    """
    if not HAS_PSUTIL:
        return {"success": False, "error": "psutil not available"}
    
    try:
        # Find process by name
        for proc in psutil.process_iter(['name']):
            try:
                if app_name.lower() in proc.info['name'].lower():
                    proc.kill()
                    logger.action(f"Close app: {app_name}", "SUCCESS", "medium")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {"success": True, "action": "closed", "app": app_name}
    except Exception as e:
        logger.error(f"Failed to close app: {e}")
        return {"success": False, "error": str(e)}


def list_processes() -> Dict[str, Any]:
    """
    List running processes.
    
    Returns:
        Dict with list of processes
    """
    if not HAS_PSUTIL:
        return {"success": False, "error": "psutil not available"}
    
    try:
        processes = []
        for proc in psutil.process_iter(['name', 'pid', 'cpu_percent']):
            try:
                processes.append({
                    "name": proc.info['name'],
                    "pid": proc.info['pid'],
                    "cpu": proc.info['cpu_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return {
            "success": True,
            "processes": processes[:50]  # Limit to 50
        }
    except Exception as e:
        logger.error(f"Failed to list processes: {e}")
        return {"success": False, "error": str(e)}


def kill_process(pid: int) -> Dict[str, Any]:
    """
    Kill a process by PID.
    
    Args:
        pid: Process ID
    
    Returns:
        Dict with success status
    """
    if not HAS_PSUTIL:
        return {"success": False, "error": "psutil not available"}
    
    try:
        proc = psutil.Process(pid)
        proc.kill()
        logger.action(f"Kill process: {pid}", "SUCCESS", "high")
        return {"success": True, "action": "killed", "pid": pid}
    except Exception as e:
        logger.error(f"Failed to kill process: {e}")
        return {"success": False, "error": str(e)}


def focus_window(title: str = None) -> Dict[str, Any]:
    """
    Focus a window by title.
    
    Args:
        title: Window title (partial match)
    
    Returns:
        Dict with success status
    """
    if not HAS_PYWIN:
        return {"success": False, "error": "pygetwindow not available"}
    
    try:
        windows = gw.getWindowsWithTitle(title)
        if windows:
            window = windows[0]
            window.activate()
            logger.action(f"Focus window: {title}", "SUCCESS", "low")
            return {"success": True, "action": "focused", "window": title}
        else:
            return {"success": False, "error": f"Window not found: {title}"}
    except Exception as e:
        logger.error(f"Failed to focus window: {e}")
        return {"success": False, "error": str(e)}


# Convenience function for intent-based commands
def handle_intent(intent: str, **kwargs) -> Dict[str, Any]:
    """Handle app control intents."""
    intent_lower = intent.lower()
    
    if "open" in intent_lower or "launch" in intent_lower or "start" in intent_lower:
        app = kwargs.get("app", kwargs.get("query", ""))
        return open_app(app)
    
    elif "close" in intent_lower or "quit" in intent_lower or "exit" in intent_lower:
        app = kwargs.get("app", "")
        return close_app(app)
    
    elif "list" in intent_lower and "process" in intent_lower:
        return list_processes()
    
    elif "kill" in intent_lower:
        pid = kwargs.get("pid")
        if pid:
            return kill_process(pid)
        return {"success": False, "error": "PID required"}
    
    elif "focus" in intent_lower or "activate" in intent_lower:
        title = kwargs.get("window", kwargs.get("title", ""))
        return focus_window(title)
    
    return {"success": False, "error": "Unknown intent"}