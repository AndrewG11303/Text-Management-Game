"""
Input Handler Module for Infinity Kingdom Bot
Handles mouse/keyboard input and touch simulation
"""

import time
import random
from typing import Optional, Tuple, List
from dataclasses import dataclass

try:
    import pyautogui
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    pyautogui.PAUSE = 0.1
    PYAUTOGUI_AVAILABLE = True
except ImportError:
    PYAUTOGUI_AVAILABLE = False

try:
    from pynput.mouse import Button, Controller as MouseController
    from pynput.keyboard import Key, Controller as KeyboardController
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

try:
    from ppadb.client import Client as AdbClient
    ADB_AVAILABLE = True
except ImportError:
    ADB_AVAILABLE = False

from src.logger import get_logger


@dataclass
class Point:
    """Represents a screen coordinate"""
    x: int
    y: int
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)
    
    def offset(self, dx: int, dy: int) -> 'Point':
        return Point(self.x + dx, self.y + dy)


class InputHandler:
    """
    Handles all input operations for the bot
    Supports multiple input methods:
    - PyAutoGUI (desktop automation)
    - Pynput (low-level input)
    - ADB (Android device)
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = get_logger()
        
        # Device settings
        self.device_config = config.get('device', {})
        self.device_type = self.device_config.get('type', 'emulator')
        
        # Timing settings
        timing = config.get('timing', {})
        self.click_delay = timing.get('click_delay', 0.3)
        self.action_delay = timing.get('action_delay', 1.0)
        self.random_delay_min = timing.get('random_delay_min', 0.1)
        self.random_delay_max = timing.get('random_delay_max', 0.5)
        
        # Safety settings
        safety = config.get('safety', {})
        self.human_like = safety.get('human_like_delays', True)
        self.random_offset = safety.get('random_click_offset', 5)
        
        # Screen dimensions
        resolution = self.device_config.get('resolution', {})
        self.screen_width = resolution.get('width', 1920)
        self.screen_height = resolution.get('height', 1080)
        
        # Window offset (for emulator)
        self.window_offset = Point(0, 0)
        
        # ADB device
        self.adb_device = None
        
        # Initialize input method
        self._init_input_method()
    
    def _init_input_method(self):
        """Initialize the appropriate input method"""
        if self.device_type == 'adb':
            self._init_adb()
        else:
            if not PYAUTOGUI_AVAILABLE and not PYNPUT_AVAILABLE:
                self.logger.error("No input library available!")
    
    def _init_adb(self):
        """Initialize ADB for Android input"""
        if not ADB_AVAILABLE:
            self.logger.error("ADB not available")
            return
        
        try:
            adb_config = self.device_config.get('adb', {})
            host = adb_config.get('host', '127.0.0.1')
            port = adb_config.get('port', 5037)
            
            client = AdbClient(host=host, port=port)
            devices = client.devices()
            
            if devices:
                self.adb_device = devices[0]
                self.logger.info(f"ADB input ready: {self.adb_device.serial}")
        except Exception as e:
            self.logger.error(f"ADB init failed: {e}")
    
    def set_window_offset(self, x: int, y: int):
        """Set the window offset for emulator clicks"""
        self.window_offset = Point(x, y)
        self.logger.info(f"Window offset set to: ({x}, {y})")
    
    def _add_human_variance(self, x: int, y: int) -> Tuple[int, int]:
        """Add small random offset to simulate human behavior"""
        if self.human_like and self.random_offset > 0:
            offset_x = random.randint(-self.random_offset, self.random_offset)
            offset_y = random.randint(-self.random_offset, self.random_offset)
            return (x + offset_x, y + offset_y)
        return (x, y)
    
    def _add_random_delay(self):
        """Add a small random delay"""
        if self.human_like:
            delay = random.uniform(self.random_delay_min, self.random_delay_max)
            time.sleep(delay)
    
    def _translate_coordinates(self, x: int, y: int) -> Tuple[int, int]:
        """Translate relative coordinates to actual screen coordinates"""
        return (x + self.window_offset.x, y + self.window_offset.y)
    
    def click(self, x: int, y: int, double: bool = False) -> bool:
        """
        Perform a click at the specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            double: Whether to double-click
        
        Returns:
            True if successful
        """
        try:
            # Add human-like variance
            x, y = self._add_human_variance(x, y)
            
            if self.device_type == 'adb' and self.adb_device:
                return self._adb_tap(x, y, double)
            else:
                return self._desktop_click(x, y, double)
        except Exception as e:
            self.logger.error(f"Click failed at ({x}, {y}): {e}")
            return False
    
    def _desktop_click(self, x: int, y: int, double: bool = False) -> bool:
        """Perform desktop click using PyAutoGUI"""
        # Translate coordinates
        x, y = self._translate_coordinates(x, y)
        
        if PYAUTOGUI_AVAILABLE:
            clicks = 2 if double else 1
            pyautogui.click(x, y, clicks=clicks)
            self._add_random_delay()
            self.logger.debug(f"Clicked at ({x}, {y})")
            return True
        elif PYNPUT_AVAILABLE:
            mouse = MouseController()
            mouse.position = (x, y)
            time.sleep(0.05)
            mouse.click(Button.left, 2 if double else 1)
            self._add_random_delay()
            self.logger.debug(f"Clicked at ({x}, {y})")
            return True
        
        return False
    
    def _adb_tap(self, x: int, y: int, double: bool = False) -> bool:
        """Perform ADB tap"""
        if not self.adb_device:
            return False
        
        try:
            self.adb_device.shell(f"input tap {x} {y}")
            if double:
                time.sleep(0.1)
                self.adb_device.shell(f"input tap {x} {y}")
            
            self._add_random_delay()
            self.logger.debug(f"ADB tap at ({x}, {y})")
            return True
        except Exception as e:
            self.logger.error(f"ADB tap failed: {e}")
            return False
    
    def click_relative(self, rel_x: float, rel_y: float, double: bool = False) -> bool:
        """
        Click at relative screen position (0.0 - 1.0)
        
        Args:
            rel_x: Relative X position (0.0 = left, 1.0 = right)
            rel_y: Relative Y position (0.0 = top, 1.0 = bottom)
        """
        x = int(rel_x * self.screen_width)
        y = int(rel_y * self.screen_height)
        return self.click(x, y, double)
    
    def click_coordinate(self, name: str) -> bool:
        """
        Click at a named coordinate from config
        
        Args:
            name: Coordinate name (e.g., 'main_screen.castle')
        """
        coords = self._get_coordinate(name)
        if coords:
            return self.click_relative(coords[0], coords[1])
        
        self.logger.warning(f"Unknown coordinate: {name}")
        return False
    
    def _get_coordinate(self, name: str) -> Optional[List[float]]:
        """Get coordinate from config by dot-notation path"""
        coordinates = self.config.get('coordinates', {})
        
        parts = name.split('.')
        current = coordinates
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        if isinstance(current, list) and len(current) == 2:
            return current
        
        return None
    
    def long_press(self, x: int, y: int, duration: float = 1.0) -> bool:
        """
        Perform a long press at the specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: How long to hold (seconds)
        """
        try:
            x, y = self._add_human_variance(x, y)
            
            if self.device_type == 'adb' and self.adb_device:
                # ADB long press using swipe with same start/end
                duration_ms = int(duration * 1000)
                self.adb_device.shell(f"input swipe {x} {y} {x} {y} {duration_ms}")
            else:
                x, y = self._translate_coordinates(x, y)
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.mouseDown(x, y)
                    time.sleep(duration)
                    pyautogui.mouseUp()
            
            self._add_random_delay()
            self.logger.debug(f"Long press at ({x}, {y}) for {duration}s")
            return True
        except Exception as e:
            self.logger.error(f"Long press failed: {e}")
            return False
    
    def swipe(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5
    ) -> bool:
        """
        Perform a swipe gesture
        
        Args:
            start_x, start_y: Starting coordinates
            end_x, end_y: Ending coordinates
            duration: Swipe duration in seconds
        """
        try:
            if self.device_type == 'adb' and self.adb_device:
                duration_ms = int(duration * 1000)
                self.adb_device.shell(
                    f"input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}"
                )
            else:
                start_x, start_y = self._translate_coordinates(start_x, start_y)
                end_x, end_y = self._translate_coordinates(end_x, end_y)
                
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.moveTo(start_x, start_y)
                    pyautogui.drag(
                        end_x - start_x,
                        end_y - start_y,
                        duration=duration
                    )
            
            self._add_random_delay()
            self.logger.debug(f"Swipe from ({start_x}, {start_y}) to ({end_x}, {end_y})")
            return True
        except Exception as e:
            self.logger.error(f"Swipe failed: {e}")
            return False
    
    def scroll(self, x: int, y: int, direction: str = "down", amount: int = 3) -> bool:
        """
        Perform a scroll action
        
        Args:
            x, y: Scroll position
            direction: 'up' or 'down'
            amount: Scroll amount
        """
        try:
            if self.device_type == 'adb' and self.adb_device:
                # Simulate scroll with swipe
                scroll_distance = 300 * amount
                if direction == "down":
                    end_y = y - scroll_distance
                else:
                    end_y = y + scroll_distance
                return self.swipe(x, y, x, end_y, duration=0.3)
            else:
                x, y = self._translate_coordinates(x, y)
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.moveTo(x, y)
                    scroll_amount = amount if direction == "up" else -amount
                    pyautogui.scroll(scroll_amount)
            
            self._add_random_delay()
            return True
        except Exception as e:
            self.logger.error(f"Scroll failed: {e}")
            return False
    
    def drag(
        self,
        start_x: int,
        start_y: int,
        end_x: int,
        end_y: int,
        duration: float = 0.5
    ) -> bool:
        """Alias for swipe - drag from one point to another"""
        return self.swipe(start_x, start_y, end_x, end_y, duration)
    
    def type_text(self, text: str, interval: float = 0.05) -> bool:
        """
        Type text character by character
        
        Args:
            text: Text to type
            interval: Delay between characters
        """
        try:
            if self.device_type == 'adb' and self.adb_device:
                # Escape special characters for shell
                escaped = text.replace(' ', '%s').replace("'", "\\'")
                self.adb_device.shell(f"input text '{escaped}'")
            else:
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.typewrite(text, interval=interval)
            
            self._add_random_delay()
            self.logger.debug(f"Typed: {text[:20]}...")
            return True
        except Exception as e:
            self.logger.error(f"Type text failed: {e}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Press a keyboard key
        
        Args:
            key: Key name (e.g., 'enter', 'escape', 'backspace')
        """
        try:
            if self.device_type == 'adb' and self.adb_device:
                # Map key names to Android key codes
                key_map = {
                    'enter': 'KEYCODE_ENTER',
                    'back': 'KEYCODE_BACK',
                    'home': 'KEYCODE_HOME',
                    'escape': 'KEYCODE_ESCAPE',
                    'backspace': 'KEYCODE_DEL',
                    'tab': 'KEYCODE_TAB',
                    'menu': 'KEYCODE_MENU',
                }
                keycode = key_map.get(key.lower(), f'KEYCODE_{key.upper()}')
                self.adb_device.shell(f"input keyevent {keycode}")
            else:
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.press(key)
            
            self._add_random_delay()
            return True
        except Exception as e:
            self.logger.error(f"Press key failed: {e}")
            return False
    
    def wait(self, seconds: float, reason: str = ""):
        """
        Wait for a specified duration
        
        Args:
            seconds: Time to wait
            reason: Optional reason for logging
        """
        if reason:
            self.logger.debug(f"Waiting {seconds}s: {reason}")
        time.sleep(seconds)
    
    def move_to(self, x: int, y: int) -> bool:
        """Move mouse to position without clicking"""
        try:
            if self.device_type != 'adb':
                x, y = self._translate_coordinates(x, y)
                if PYAUTOGUI_AVAILABLE:
                    pyautogui.moveTo(x, y)
                elif PYNPUT_AVAILABLE:
                    mouse = MouseController()
                    mouse.position = (x, y)
            return True
        except Exception as e:
            self.logger.error(f"Move to failed: {e}")
            return False


class GestureBuilder:
    """Helper class to build complex gesture sequences"""
    
    def __init__(self, input_handler: InputHandler):
        self.input = input_handler
        self.actions = []
    
    def click(self, x: int, y: int):
        """Add a click action"""
        self.actions.append(('click', x, y))
        return self
    
    def wait(self, seconds: float):
        """Add a wait action"""
        self.actions.append(('wait', seconds))
        return self
    
    def swipe(self, start_x: int, start_y: int, end_x: int, end_y: int):
        """Add a swipe action"""
        self.actions.append(('swipe', start_x, start_y, end_x, end_y))
        return self
    
    def execute(self) -> bool:
        """Execute all queued actions"""
        for action in self.actions:
            if action[0] == 'click':
                self.input.click(action[1], action[2])
            elif action[0] == 'wait':
                self.input.wait(action[1])
            elif action[0] == 'swipe':
                self.input.swipe(action[1], action[2], action[3], action[4])
        
        self.actions = []
        return True
