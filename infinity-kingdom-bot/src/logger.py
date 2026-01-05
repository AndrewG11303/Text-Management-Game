"""
Logging module for Infinity Kingdom Bot
Provides colored console output and file logging
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from rich.console import Console
    from rich.logging import RichHandler
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False


class BotLogger:
    """Custom logger for the Infinity Kingdom Bot"""
    
    def __init__(
        self,
        name: str = "IKBot",
        level: str = "INFO",
        log_dir: str = "logs",
        file_logging: bool = True,
        console_logging: bool = True
    ):
        self.name = name
        self.level = getattr(logging, level.upper(), logging.INFO)
        self.log_dir = Path(log_dir)
        self.file_logging = file_logging
        self.console_logging = console_logging
        
        # Create log directory
        if file_logging:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        self.logger.handlers = []  # Clear existing handlers
        
        # Setup handlers
        if console_logging:
            self._setup_console_handler()
        if file_logging:
            self._setup_file_handler()
    
    def _setup_console_handler(self):
        """Setup colored console output"""
        if RICH_AVAILABLE:
            # Use Rich for beautiful console output
            console = Console()
            handler = RichHandler(
                console=console,
                show_time=True,
                show_path=False,
                markup=True,
                rich_tracebacks=True
            )
            handler.setLevel(self.level)
            self.logger.addHandler(handler)
        elif COLORLOG_AVAILABLE:
            # Fallback to colorlog
            handler = colorlog.StreamHandler()
            handler.setFormatter(colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S',
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            ))
            handler.setLevel(self.level)
            self.logger.addHandler(handler)
        else:
            # Basic console handler
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s [%(levelname)s] %(message)s',
                datefmt='%H:%M:%S'
            ))
            handler.setLevel(self.level)
            self.logger.addHandler(handler)
    
    def _setup_file_handler(self):
        """Setup file logging"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"bot_{timestamp}.log"
        
        handler = logging.FileHandler(log_file, encoding='utf-8')
        handler.setFormatter(logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        handler.setLevel(self.level)
        self.logger.addHandler(handler)
        
        self.log_file = log_file
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)
    
    def success(self, message: str):
        """Log a success message (info level with special formatting)"""
        self.logger.info(f"✅ {message}")
    
    def task(self, message: str):
        """Log a task message"""
        self.logger.info(f"📋 {message}")
    
    def action(self, message: str):
        """Log an action message"""
        self.logger.info(f"🎯 {message}")
    
    def resource(self, message: str):
        """Log a resource collection message"""
        self.logger.info(f"💰 {message}")
    
    def battle(self, message: str):
        """Log a battle message"""
        self.logger.info(f"⚔️ {message}")
    
    def alert(self, message: str):
        """Log an alert message"""
        self.logger.warning(f"🚨 {message}")


# Global logger instance
_logger: Optional[BotLogger] = None


def get_logger(
    name: str = "IKBot",
    level: str = "INFO",
    **kwargs
) -> BotLogger:
    """Get or create a logger instance"""
    global _logger
    if _logger is None:
        _logger = BotLogger(name=name, level=level, **kwargs)
    return _logger


def setup_logger(config: dict) -> BotLogger:
    """Setup logger from configuration"""
    global _logger
    log_config = config.get('logging', {})
    _logger = BotLogger(
        name="IKBot",
        level=log_config.get('level', 'INFO'),
        log_dir=log_config.get('log_dir', 'logs'),
        file_logging=log_config.get('file_logging', True),
        console_logging=log_config.get('console_logging', True)
    )
    return _logger
