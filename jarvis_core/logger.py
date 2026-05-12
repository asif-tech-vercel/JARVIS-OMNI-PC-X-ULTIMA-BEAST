"""
JARVIS Logger Module
Handles logging for all JARVIS actions and events.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


class JarvisLogger:
    """Centralized logging for JARVIS."""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure the main logger."""
        self.logger = logging.getLogger("JARVIS")
        self.logger.setLevel(logging.DEBUG)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        # File handler (actions log)
        log_file = self.log_dir / "actions.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """Log info message."""
        self.logger.info(message)
    
    def debug(self, message: str):
        """Log debug message."""
        self.logger.debug(message)
    
    def warning(self, message: str):
        """Log warning message."""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Log error message."""
        self.logger.error(message)
    
    def action(self, action: str, result: str, risk_level: str = "low"):
        """Log an action with result."""
        self.logger.info(f"[{risk_level.upper()}] {action} -> {result}")
    
    def get_logger(self):
        """Get the logger instance."""
        return self.logger


# Global logger instance
_logger = None


def get_logger(log_dir: str = "logs") -> JarvisLogger:
    """Get or create the global logger."""
    global _logger
    if _logger is None:
        _logger = JarvisLogger(log_dir)
    return _logger


def log_action(action: str, result: str, risk_level: str = "low"):
    """Log an action quickly."""
    logger = get_logger()
    logger.action(action, result, risk_level)