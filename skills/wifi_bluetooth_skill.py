"""JARVIS WiFi/Bluetooth Skill."""

import subprocess
from jarvis_core.logger import get_logger

logger = get_logger()

def wifi_on() -> dict:
    try:
        subprocess.run("netsh wlan start hostednetwork", shell=True, check=True)
        return {"success": True, "action": "enabled"}
    except: return {"success": False, "error": "Failed"}

def wifi_off() -> dict:
    try:
        subprocess.run("netsh wlan stop hostednetwork", shell=True, check=True)
        return {"success": True, "action": "disabled"}
    except: return {"success": False, "error": "Failed"}

def wifi_status() -> dict:
    try:
        result = subprocess.run("netsh wlan show interfaces", shell=True, capture_output=True, text=True)
        return {"success": True, "output": result.stdout}
    except: return {"success": False, "error": "Failed"}

def bluetooth_on() -> dict:
    try:
        subprocess.run('powershell -Command "Get-PnpDevice -Class Bluetooth | Enable-PnpDevice -Confirm:$false"', shell=True)
        return {"success": True}
    except: return {"success": False, "error": "Failed"}

def bluetooth_off() -> dict:
    try:
        subprocess.run('powershell -Command "Get-PnpDevice -Class Bluetooth | Disable-PnpDevice -Confirm:$false"', shell=True)
        return {"success": True}
    except: return {"success": False, "error": "Failed"}