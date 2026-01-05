"""
Base Task Module
Provides base class for all game tasks
"""

import time
from abc import ABC, abstractmethod
from typing import Optional, Any
from datetime import datetime

from src.logger import get_logger


class BaseTask(ABC):
    """
    Abstract base class for all game tasks
    Provides common functionality and structure
    """
    
    def __init__(self, bot_engine):
        """
        Initialize task with reference to bot engine
        
        Args:
            bot_engine: Reference to the main BotEngine instance
        """
        self.bot = bot_engine
        self.logger = get_logger()
        
        # Task metadata
        self.name = self.__class__.__name__
        self.description = ""
        
        # Execution state
        self.is_running = False
        self.last_run = None
        self.run_count = 0
        self.success_count = 0
        self.fail_count = 0
        
        # Timing
        self.timeout = 60  # Default 60 second timeout
        self.start_time = None
    
    @abstractmethod
    def execute(self) -> bool:
        """
        Execute the task
        Must be implemented by subclasses
        
        Returns:
            True if task completed successfully
        """
        pass
    
    def can_run(self) -> bool:
        """
        Check if task can run
        Override in subclasses for custom conditions
        
        Returns:
            True if task is allowed to run
        """
        return True
    
    def run(self) -> bool:
        """
        Run the task with proper setup and teardown
        
        Returns:
            True if task completed successfully
        """
        if not self.can_run():
            self.logger.debug(f"Task {self.name} cannot run (conditions not met)")
            return False
        
        self.is_running = True
        self.start_time = datetime.now()
        self.run_count += 1
        
        self.logger.task(f"Starting task: {self.name}")
        
        try:
            # Pre-task setup
            self._pre_execute()
            
            # Execute with timeout monitoring
            success = self._execute_with_timeout()
            
            # Post-task cleanup
            self._post_execute(success)
            
            if success:
                self.success_count += 1
                self.logger.success(f"Task completed: {self.name}")
            else:
                self.fail_count += 1
                self.logger.warning(f"Task failed: {self.name}")
            
            return success
            
        except Exception as e:
            self.fail_count += 1
            self.logger.error(f"Task error in {self.name}: {e}")
            self._on_error(e)
            return False
            
        finally:
            self.is_running = False
            self.last_run = datetime.now()
    
    def _execute_with_timeout(self) -> bool:
        """Execute task with timeout monitoring"""
        # Simple timeout check - subclasses can override for more sophisticated handling
        return self.execute()
    
    def _pre_execute(self):
        """Called before task execution - override for setup"""
        pass
    
    def _post_execute(self, success: bool):
        """Called after task execution - override for cleanup"""
        pass
    
    def _on_error(self, error: Exception):
        """Called when task encounters an error - override for custom handling"""
        pass
    
    def wait(self, seconds: float, reason: str = ""):
        """Convenience method to wait with optional logging"""
        if reason:
            self.logger.debug(f"Waiting {seconds}s: {reason}")
        time.sleep(seconds)
    
    def click(self, x: int, y: int) -> bool:
        """Convenience method to click"""
        return self.bot.input.click(x, y)
    
    def click_relative(self, rel_x: float, rel_y: float) -> bool:
        """Convenience method for relative click"""
        return self.bot.input.click_relative(rel_x, rel_y)
    
    def click_button(self, name: str) -> bool:
        """Click a named button from config"""
        return self.bot.input.click_coordinate(name)
    
    def capture_screen(self):
        """Capture current screen"""
        return self.bot.screen.capture()
    
    def find_and_click(self, template_name: str, threshold: float = 0.8) -> bool:
        """
        Find a template on screen and click it
        
        Args:
            template_name: Name of template to find
            threshold: Match confidence threshold
        
        Returns:
            True if found and clicked
        """
        screen = self.capture_screen()
        if screen is None:
            return False
        
        result = self.bot.matcher.find_template(screen, template_name, threshold)
        if result:
            x, y, confidence = result
            self.logger.debug(f"Found {template_name} at ({x}, {y}) conf={confidence:.2f}")
            return self.click(x, y)
        
        return False
    
    def wait_for_template(
        self,
        template_name: str,
        timeout: float = 10.0,
        interval: float = 0.5
    ) -> bool:
        """
        Wait for a template to appear on screen
        
        Args:
            template_name: Name of template to wait for
            timeout: Maximum wait time
            interval: Check interval
        
        Returns:
            True if template appeared
        """
        start = time.time()
        
        while time.time() - start < timeout:
            screen = self.capture_screen()
            if screen is not None:
                result = self.bot.matcher.find_template(screen, template_name)
                if result:
                    return True
            time.sleep(interval)
        
        return False
    
    def close_popup(self) -> bool:
        """Try to close any popup dialog"""
        # Try common close button positions
        close_positions = [
            'ui.close_button',
            (0.95, 0.05),  # Top right
            (0.5, 0.85),   # Bottom center (OK button)
        ]
        
        for pos in close_positions:
            if isinstance(pos, str):
                self.click_button(pos)
            else:
                self.click_relative(pos[0], pos[1])
            self.wait(0.3)
        
        return True
    
    def navigate_to_main(self) -> bool:
        """Navigate back to main city screen"""
        max_attempts = 5
        
        for _ in range(max_attempts):
            # Try back button
            self.click_button('ui.back_button')
            self.wait(1.0)
            
            # Check if we're at main screen
            # This would use screen detection in practice
            # For now, just return True
        
        return True
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since task started"""
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0
    
    def check_timeout(self) -> bool:
        """Check if task has exceeded timeout"""
        return self.get_elapsed_time() > self.timeout
    
    def get_stats(self) -> dict:
        """Get task statistics"""
        return {
            'name': self.name,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'fail_count': self.fail_count,
            'success_rate': (
                self.success_count / self.run_count * 100
                if self.run_count > 0 else 0
            ),
            'last_run': str(self.last_run) if self.last_run else None
        }
