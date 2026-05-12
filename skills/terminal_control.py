"""
JARVIS Terminal Control Skill
Run CMD/PowerShell commands and return output.
"""

import subprocess
from typing import Dict, Any, Optional, List

from jarvis_core.logger import get_logger


logger = get_logger()


def get_skill():
    """Return the terminal control skill functions."""
    return {
        "run": run_command,
        "run_powershell": run_powershell,
        "run_bash": run_bash,
    }


def run_command(
    command: str,
    shell: bool = True,
    timeout: int = 30,
    cwd: Optional[str] = None
) -> Dict[str, Any]:
    """
    Run a command in the terminal.
    
    Args:
        command: Command to run
        shell: Use shell (default True)
        timeout: Timeout in seconds
        cwd: Working directory
    
    Returns:
        Dict with output and status
    """
    try:
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd
        )
        
        logger.action(f"Run command: {command[:50]}", 
                   "SUCCESS" if result.returncode == 0 else "FAILED", "medium")
        
        return {
            "success": result.returncode == 0 or result.returncode is None,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
    except subprocess.TimeoutExpired:
        logger.error(f"Command timeout: {command[:50]}")
        return {
            "success": False,
            "error": "Command timed out",
            "command": command
        }
    except Exception as e:
        logger.error(f"Command failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "command": command
        }


def run_powershell(
    command: str,
    timeout: int = 30,
    admin: bool = False
) -> Dict[str, Any]:
    """
    Run a PowerShell command.
    
    Args:
        command: PowerShell command to run
        timeout: Timeout in seconds
        admin: Run as administrator
    
    Returns:
        Dict with output and status
    """
    # Build PowerShell command
    ps_command = command
    
    # Use powershell.exe directly
    cmd = ["powershell", "-NoProfile", "-Command", ps_command]
    
    if admin:
        cmd.append("-RunAsAdministrator")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        logger.action(f"PowerShell: {command[:50]}", 
                   "SUCCESS" if result.returncode == 0 else "FAILED", "high")
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
    except Exception as e:
        logger.error(f"PowerShell failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def run_bash(
    command: str,
    timeout: int = 30,
    shell: str = "/bin/bash"
) -> Dict[str, Any]:
    """
    Run a bash command.
    
    Args:
        command: Bash command to run
        timeout: Timeout in seconds
        shell: Shell to use
    
    Returns:
        Dict with output and status
    """
    try:
        result = subprocess.run(
            [shell, "-c", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        
        logger.action(f"Bash: {command[:50]}", 
                   "SUCCESS" if result.returncode == 0 else "FAILED", "medium")
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "command": command
        }
    except Exception as e:
        logger.error(f"Bash failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Convenience function for intent-based commands
def handle_intent(intent: str, **kwargs) -> Dict[str, Any]:
    """Handle terminal control intents."""
    intent_lower = intent.lower()
    
    command = kwargs.get("command", kwargs.get("query", ""))
    
    if "powershell" in intent_lower:
        return run_powershell(command)
    elif "bash" in intent_lower or "shell" in intent_lower:
        return run_bash(command)
    else:
        return run_command(command)