"""
JARVIS Configuration
Global settings and configuration.
"""

import os
from pathlib import Path


# ==== PROJECT CONFIGURATION ====
PROJECT_NAME = "JARVIS-OMNI-PC-X-ULTIMA-BEAST"
VERSION = "1.0.0-master-blueprint-peak-edition"

# Paths
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

# Create directories
LOGS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)


# ==== EXECUTION MODE ====
class ExecutionMode:
    """Execution mode settings."""
    SAFE = "safe"      # Ask before every action
    AUTO = "auto"      # Auto-execute low-risk
    BEAST = "beast"    # Multi-step with minimal prompts

    @staticmethod
    def get_current():
        """Get current mode from environment."""
        return os.getenv("JARVIS_MODE", ExecutionMode.AUTO)


# ==== PERMISSION SETTINGS ====
class Permissions:
    """Permission levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


# ==== SAFETY RULES ====
# Actions that always require confirmation
ALWAYS_CONFIRM = [
    "delete system",
    "delete windows",
    "format drive",
    "uninstall software",
    "shutdown",
    "restart",
    "registry edit",
    "run unknown script",
]

# Actions that are always blocked
ALWAYS_BLOCK = [
    "delete windows/system32",
    "disable antivirus",
    "download unknown exe",
    "steal password",
    "keylogging",
    "bypass captcha",
]


# ==== TOOL PRIORITY ====
# Priority order for automation methods
TOOL_PRIORITY = [
    "native_win32",       # Win32/UIAutomation APIs
    "direct_command",   # PowerShell/CMD
    "browser",         # Playwright
    "vision",         # OCR + click
    "macro",          # Macro playback
]


# ==== VOICE SETTINGS ====
class VoiceConfig:
    """Voice input/output settings."""
    WAKE_WORD = "jarvis"
    VOICE_PERSONALITY = "professional"  # calm, professional, casual
    TTS_ENGINE = "pyttsx3"
    STT_ENGINE = "vosk"
    TYPING_SPEED = 0.05  # seconds per character


# ==== SYSTEM PATHS ====
# Common Windows paths
USER_HOME = os.path.expanduser("~")
DOWNLOADS_FOLDER = os.path.join(USER_HOME, "Downloads")
DOCUMENTS_FOLDER = os.path.join(USER_HOME, "Documents")
DESKTOP_FOLDER = os.path.join(USER_HOME, "Desktop")


# ==== MEMORY SETTINGS ====
MEMORY_FILE = DATA_DIR / "memory.json"
PREFERENCES_FILE = DATA_DIR / "preferences.json"
TASK_DB_FILE = DATA_DIR / "task_db.json"
MACROS_FILE = DATA_DIR / "macros.json"
APP_PATHS_FILE = DATA_DIR / "app_paths.json"


# ==== LOGGING ====
LOG_FILE = LOGS_DIR / "actions.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ==== EMERGENCY STOP ====
EMERGENCY_STOP_HOTKEY = "ctrl+shift+q"
EMERGENCY_STOP_ENABLED = True


# ==== API KEYS ====
# Set environment variables for external services
# Or use .env file (create if needed)
def load_env():
    """Load environment variables."""
    env_file = BASE_DIR / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value


# ==== DEFAULT SETTINGS ====
DEFAULT_SETTINGS = {
    "voice_enabled": False,
    "voice_wake_word": "jarvis",
    "typing_speed": 0.05,
    "execution_mode": ExecutionMode.AUTO,
    "default_browser": "chrome",
    "workspace_folder": str(BASE_DIR),
    "auto_organize_downloads": True,
    "language": "en",
    "theme": "dark",
}