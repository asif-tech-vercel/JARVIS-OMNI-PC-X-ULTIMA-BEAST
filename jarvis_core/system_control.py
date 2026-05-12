"""
JARVIS Windows System Control
Volume, brightness, power, processes, registry control.
"""

import os
import subprocess
import ctypes
from ctypes import wintypes
from typing import Dict, Any, Optional

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

# Make pycaw optional
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    HAS_CAW = True
except ImportError:
    HAS_CAW = False

try:
    import winreg
    HAS_WINREG = True
except ImportError:
    HAS_WINREG = False

from jarvis_core.logger import get_logger


logger = get_logger()


class SystemControl:
    """Native Windows system control."""
    
    def __init__(self):
        self._init_audio()
    
    def _init_audio(self):
        """Initialize audio control."""
        self.audio_device = None
        if HAS_C.AW:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, ctypes.CLSCTX_ALL, None)
                self.audio_device = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))
            except:
                pass
    
    # ==================== POWER CONTROL ====================
    
    def shutdown(self, force: bool = False, timer: int = 0) -> Dict[str, Any]:
        """
        Shutdown the computer.
        
        Args:
            force: Force close apps
            timer: Seconds delay (0 = immediate)
        """
        try:
            cmd = ["shutdown", "/s"]
            if force:
                cmd.append("/f")
            if timer > 0:
                cmd.append(f"/t {timer}")
            
            subprocess.run(cmd, shell=True)
            logger.action("Shutdown", "SUCCESS", "high")
            return {"success": True, "action": "shutdown", "forced": force}
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return {"success": False, "error": str(e)}
    
    def restart(self, force: bool = False) -> Dict[str, Any]:
        """Restart the computer."""
        try:
            cmd = ["shutdown", "/r"]
            if force:
                cmd.append("/f")
            
            subprocess.run(cmd, shell=True)
            logger.action("Restart", "SUCCESS", "high")
            return {"success": True, "action": "restart"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sleep(self) -> Dict[str, Any]:
        """Put computer to sleep."""
        try:
            # Use PowerShell
            subprocess.run(
                'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState("Suspend", $false, $false)',
                shell=True
            )
            logger.action("Sleep", "SUCCESS", "medium")
            return {"success": True, "action": "sleep"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def lock(self) -> Dict[str, Any]:
        """Lock the computer."""
        try:
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            logger.action("Lock", "SUCCESS", "medium")
            return {"success": True, "action": "locked"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== VOLUME CONTROL ====================
    
    def get_volume(self) -> Dict[str, Any]:
        """Get current volume level."""
        try:
            if self.audio_device:
                volume = self.audio_device.GetMasterVolumeLevelScalar()
                return {"success": True, "volume": int(volume * 100)}
            else:
                # Fallback to PowerShell
                result = subprocess.run(
                    '[Audio]::Volume',
                    shell=True,
                    capture_output=True,
                    text=True,
                    powershell=True
                )
                return {"success": True, "volume": int(result.stdout.strip())}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def set_volume(self, level: int) -> Dict[str, Any]:
        """
        Set volume level (0-100).
        
        Args:
            level: Volume percentage
        """
        try:
            level = max(0, min(100, level))
            
            if self.audio_device:
                self.audio_device.SetMasterVolumeLevelScalar(level / 100.0, None)
                logger.action(f"Set volume: {level}%", "SUCCESS", "low")
                return {"success": True, "volume": level}
            else:
                # Fallback - might not work on all systems
                return {"success": False, "error": "Volume control not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def mute(self) -> Dict[str, Any]:
        """Mute audio."""
        try:
            if self.audio_device:
                self.audio_device.SetMute(True, None)
                logger.action("Mute audio", "SUCCESS", "low")
                return {"success": True, "muted": True}
            return {"success": False, "error": "Audio control not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def unmute(self) -> Dict[str, Any]:
        """Unmute audio."""
        try:
            if self.audio_device:
                self.audio_device.SetMute(False, None)
                logger.action("Unmute audio", "SUCCESS", "low")
                return {"success": True, "muted": False}
            return {"success": False, "error": "Audio control not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== BRIGHTNESS CONTROL ====================
    
    def set_brightness(self, level: int) -> Dict[str, Any]:
        """
        Set screen brightness (0-100).
        
        Note: Requires admin on some systems.
        """
        try:
            level = max(0, min(100, level))
            
            # Use WMI to set brightness
            result = subprocess.run(
                f'wmic /namespace:\\\\root\\wmi Path WmiMonitorBrightnessMethods call SetBrightness({level})',
                shell=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                logger.action(f"Set brightness: {level}%", "SUCCESS", "low")
                return {"success": True, "brightness": level}
            
            return {"success": False, "error": "Brightness control not available"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== PROCESS MANAGEMENT ====================
    
    def list_processes(self) -> Dict[str, Any]:
        """List running processes."""
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available"}
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu": proc.info['cpu_percent'],
                        "memory": round(proc.info['memory_percent'], 1)
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Sort by CPU usage
            processes.sort(key=lambda x: x['cpu'] or 0, reverse=True)
            
            return {
                "success": True,
                "processes": processes[:50],
                "count": len(processes)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def kill_process(self, pid: int, force: bool = False) -> Dict[str, Any]:
        """Kill a process by PID."""
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available"}
        
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()
            
            logger.action(f"Kill process: {pid}", "SUCCESS", "high")
            return {"success": True, "action": "killed", "pid": pid}
        except psutil.NoSuchProcess:
            return {"success": False, "error": f"Process {pid} not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def kill_process_by_name(self, name: str, force: bool = False) -> Dict[str, Any]:
        """Kill processes by name."""
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available"}
        
        try:
            killed = []
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if proc.info['name'].lower() == name.lower():
                        if force:
                            proc.kill()
                        else:
                            proc.terminate()
                        killed.append(proc.info['pid'])
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            logger.action(f"Kill {name}: {len(killed)} processes", "SUCCESS", "high")
            return {"success": True, "killed": killed}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== SYSTEM INFO ====================
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available"}
        
        try:
            cpu = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            battery = psutil.sensors_battery()
            
            info = {
                "success": True,
                "cpu": {
                    "usage": cpu,
                    "count": psutil.cpu_count()
                },
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": disk.percent
                }
            }
            
            if battery:
                info["battery"] = {
                    "percent": battery.percent,
                    "plugged": battery.power_plugged
                }
            
            return info
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_battery_status(self) -> Dict[str, Any]:
        """Get battery status."""
        if not HAS_PSUTIL:
            return {"success": False, "error": "psutil not available"}
        
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "success": True,
                    "percent": battery.percent,
                    "plugged": battery.power_plugged,
                    "time_left": battery.secsleft
                }
            return {"success": False, "error": "No battery"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # ==================== NETWORK ====================
    
    def get_wifi_networks(self) -> Dict[str, Any]:
        """Get available WiFi networks."""
        try:
            result = subprocess.run(
                'netsh wlan show networks mode=bssid',
                shell=True,
                capture_output=True,
                text=True
            )
            
            # Parse output
            lines = result.stdout.split('\n')
            networks = []
            for line in lines:
                if "SSID" in line:
                    networks.append(line.split(":", 1)[1].strip())
            
            return {
                "success": True,
                "networks": networks
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def connect_wifi(self, ssid: str, password: str = None) -> Dict[str, Any]:
        """Connect to WiFi network."""
        try:
            # First add profile
            if password:
                cmd = f'netsh wlan add profile filename=* interface=*'
                subprocess.run(cmd, shell=True)
            
            # Then connect
            cmd = f'netsh wlan connect name="{ssid}"'
            result = subprocess.run(cmd, shell=True, capture_output=True)
            
            if result.returncode == 0:
                logger.action(f"Connect WiFi: {ssid}", "SUCCESS", "medium")
                return {"success": True, "network": ssid}
            
            return {"success": False, "error": "Connection failed"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# Alias for backwards compatibility
class WindowsControl(SystemControl):
    """Alias for SystemControl."""
    pass