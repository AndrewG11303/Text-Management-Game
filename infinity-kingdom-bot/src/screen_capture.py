"""
Screen Capture Module for Infinity Kingdom Bot
Handles capturing screenshots from emulator/device
"""

import time
from typing import Optional, Tuple, List
from pathlib import Path

import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    from PIL import Image, ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

try:
    from ppadb.client import Client as AdbClient
    ADB_AVAILABLE = True
except ImportError:
    ADB_AVAILABLE = False

from src.logger import get_logger


class ScreenCapture:
    """
    Screen capture handler supporting multiple capture methods:
    - MSS (fastest, recommended for desktop/emulator)
    - PIL ImageGrab (fallback)
    - ADB (for Android devices)
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = get_logger()
        self.device_config = config.get('device', {})
        self.device_type = self.device_config.get('type', 'emulator')
        
        # Screen dimensions
        resolution = self.device_config.get('resolution', {})
        self.width = resolution.get('width', 1920)
        self.height = resolution.get('height', 1080)
        
        # Capture region (will be set when window is found)
        self.capture_region = None
        
        # ADB client
        self.adb_client = None
        self.adb_device = None
        
        # Initialize capture method
        self._init_capture_method()
    
    def _init_capture_method(self):
        """Initialize the appropriate capture method"""
        if self.device_type == 'adb':
            self._init_adb()
        else:
            self._init_desktop_capture()
    
    def _init_adb(self):
        """Initialize ADB connection for Android device capture"""
        if not ADB_AVAILABLE:
            self.logger.error("ADB not available. Install with: pip install pure-python-adb")
            return
        
        adb_config = self.device_config.get('adb', {})
        host = adb_config.get('host', '127.0.0.1')
        port = adb_config.get('port', 5037)
        
        try:
            self.adb_client = AdbClient(host=host, port=port)
            devices = self.adb_client.devices()
            
            if devices:
                self.adb_device = devices[0]
                self.logger.info(f"Connected to ADB device: {self.adb_device.serial}")
            else:
                self.logger.warning("No ADB devices found")
        except Exception as e:
            self.logger.error(f"Failed to connect to ADB: {e}")
    
    def _init_desktop_capture(self):
        """Initialize desktop capture for emulator"""
        window_name = self.device_config.get('window_name', 'BlueStacks')
        
        # Try to find the emulator window
        try:
            self.capture_region = self._find_window(window_name)
            if self.capture_region:
                self.logger.info(f"Found window '{window_name}' at {self.capture_region}")
            else:
                self.logger.warning(f"Window '{window_name}' not found, using full screen")
        except Exception as e:
            self.logger.warning(f"Could not find window: {e}")
    
    def _find_window(self, window_name: str) -> Optional[dict]:
        """
        Find window by name and return its region
        Returns: dict with 'left', 'top', 'width', 'height' or None
        """
        try:
            import pyautogui
            
            # Try to locate window (platform-specific)
            import platform
            
            if platform.system() == 'Windows':
                try:
                    import win32gui
                    
                    def callback(hwnd, windows):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if window_name.lower() in title.lower():
                                rect = win32gui.GetWindowRect(hwnd)
                                windows.append({
                                    'left': rect[0],
                                    'top': rect[1],
                                    'width': rect[2] - rect[0],
                                    'height': rect[3] - rect[1]
                                })
                        return True
                    
                    windows = []
                    win32gui.EnumWindows(callback, windows)
                    
                    if windows:
                        return windows[0]
                except ImportError:
                    pass
            
            elif platform.system() == 'Linux':
                try:
                    import subprocess
                    result = subprocess.run(
                        ['xdotool', 'search', '--name', window_name],
                        capture_output=True, text=True
                    )
                    if result.stdout.strip():
                        window_id = result.stdout.strip().split('\n')[0]
                        geo = subprocess.run(
                            ['xdotool', 'getwindowgeometry', window_id],
                            capture_output=True, text=True
                        )
                        # Parse geometry output
                        # This is a simplified parser
                        return None  # Would need proper parsing
                except Exception:
                    pass
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Window search failed: {e}")
            return None
    
    def capture(self) -> Optional[np.ndarray]:
        """
        Capture the current screen/window
        Returns: numpy array (BGR format for OpenCV) or None on failure
        """
        if self.device_type == 'adb' and self.adb_device:
            return self._capture_adb()
        else:
            return self._capture_desktop()
    
    def _capture_desktop(self) -> Optional[np.ndarray]:
        """Capture screen using MSS or PIL"""
        try:
            if MSS_AVAILABLE:
                return self._capture_mss()
            elif PIL_AVAILABLE:
                return self._capture_pil()
            else:
                self.logger.error("No screen capture library available")
                return None
        except Exception as e:
            self.logger.error(f"Screen capture failed: {e}")
            return None
    
    def _capture_mss(self) -> Optional[np.ndarray]:
        """Capture using MSS (fastest method)"""
        with mss.mss() as sct:
            if self.capture_region:
                monitor = self.capture_region
            else:
                # Use primary monitor
                monitor = sct.monitors[1]
            
            screenshot = sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Convert BGRA to BGR
            if img.shape[2] == 4:
                img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
    
    def _capture_pil(self) -> Optional[np.ndarray]:
        """Capture using PIL ImageGrab"""
        if self.capture_region:
            bbox = (
                self.capture_region['left'],
                self.capture_region['top'],
                self.capture_region['left'] + self.capture_region['width'],
                self.capture_region['top'] + self.capture_region['height']
            )
            screenshot = ImageGrab.grab(bbox=bbox)
        else:
            screenshot = ImageGrab.grab()
        
        # Convert to numpy array
        img = np.array(screenshot)
        
        # Convert RGB to BGR for OpenCV
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        
        return img
    
    def _capture_adb(self) -> Optional[np.ndarray]:
        """Capture screen from ADB device"""
        if not self.adb_device:
            return None
        
        try:
            # Get screenshot bytes
            screenshot_bytes = self.adb_device.screencap()
            
            # Convert to numpy array
            nparr = np.frombuffer(screenshot_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return img
        except Exception as e:
            self.logger.error(f"ADB capture failed: {e}")
            return None
    
    def save_screenshot(self, filename: str = None, directory: str = "screenshots") -> str:
        """Save current screenshot to file"""
        if filename is None:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
        
        # Create directory if needed
        Path(directory).mkdir(parents=True, exist_ok=True)
        filepath = Path(directory) / filename
        
        # Capture and save
        img = self.capture()
        if img is not None:
            cv2.imwrite(str(filepath), img)
            self.logger.debug(f"Screenshot saved: {filepath}")
            return str(filepath)
        
        return ""
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the current screen/window size"""
        if self.capture_region:
            return (self.capture_region['width'], self.capture_region['height'])
        return (self.width, self.height)
    
    def set_capture_region(self, left: int, top: int, width: int, height: int):
        """Manually set the capture region"""
        self.capture_region = {
            'left': left,
            'top': top,
            'width': width,
            'height': height
        }
        self.logger.info(f"Capture region set to: {self.capture_region}")


class ImageMatcher:
    """
    Image matching utilities for finding UI elements
    Uses template matching with OpenCV
    """
    
    def __init__(self, templates_dir: str = "assets/templates"):
        self.templates_dir = Path(templates_dir)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: dict = {}
        self.logger = get_logger()
        
        # Load templates
        self._load_templates()
    
    def _load_templates(self):
        """Load all template images from directory"""
        if not self.templates_dir.exists():
            return
        
        for img_path in self.templates_dir.glob("*.png"):
            name = img_path.stem
            template = cv2.imread(str(img_path))
            if template is not None:
                self.templates[name] = template
                self.logger.debug(f"Loaded template: {name}")
    
    def add_template(self, name: str, image: np.ndarray):
        """Add a template image"""
        self.templates[name] = image
        
        # Save to disk
        filepath = self.templates_dir / f"{name}.png"
        cv2.imwrite(str(filepath), image)
    
    def find_template(
        self,
        screen: np.ndarray,
        template_name: str,
        threshold: float = 0.8,
        method: int = cv2.TM_CCOEFF_NORMED
    ) -> Optional[Tuple[int, int, float]]:
        """
        Find a template in the screen image
        
        Args:
            screen: Screenshot as numpy array
            template_name: Name of template to find
            threshold: Minimum match confidence (0-1)
            method: OpenCV template matching method
        
        Returns:
            Tuple of (x, y, confidence) or None if not found
        """
        if template_name not in self.templates:
            self.logger.warning(f"Template not found: {template_name}")
            return None
        
        template = self.templates[template_name]
        
        # Convert to grayscale for faster matching
        if len(screen.shape) == 3:
            screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        else:
            screen_gray = screen
        
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
        
        # Perform template matching
        result = cv2.matchTemplate(screen_gray, template_gray, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # For TM_SQDIFF methods, the minimum is the best match
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            confidence = 1 - min_val
            location = min_loc
        else:
            confidence = max_val
            location = max_loc
        
        if confidence >= threshold:
            # Return center of matched region
            h, w = template_gray.shape
            center_x = location[0] + w // 2
            center_y = location[1] + h // 2
            return (center_x, center_y, confidence)
        
        return None
    
    def find_all_templates(
        self,
        screen: np.ndarray,
        template_name: str,
        threshold: float = 0.8
    ) -> List[Tuple[int, int, float]]:
        """
        Find all occurrences of a template in the screen
        
        Returns:
            List of (x, y, confidence) tuples
        """
        if template_name not in self.templates:
            return []
        
        template = self.templates[template_name]
        
        # Convert to grayscale
        if len(screen.shape) == 3:
            screen_gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        else:
            screen_gray = screen
        
        if len(template.shape) == 3:
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        else:
            template_gray = template
        
        h, w = template_gray.shape
        
        # Perform template matching
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        # Find all locations above threshold
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            center_x = pt[0] + w // 2
            center_y = pt[1] + h // 2
            confidence = result[pt[1], pt[0]]
            matches.append((center_x, center_y, confidence))
        
        # Remove duplicates (matches that are too close together)
        if matches:
            matches = self._remove_duplicates(matches, min_distance=20)
        
        return matches
    
    def _remove_duplicates(
        self,
        matches: List[Tuple[int, int, float]],
        min_distance: int = 20
    ) -> List[Tuple[int, int, float]]:
        """Remove duplicate matches that are too close together"""
        if not matches:
            return []
        
        # Sort by confidence (highest first)
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
        
        filtered = []
        for match in matches:
            is_duplicate = False
            for existing in filtered:
                distance = ((match[0] - existing[0])**2 + (match[1] - existing[1])**2)**0.5
                if distance < min_distance:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                filtered.append(match)
        
        return filtered
    
    def find_color(
        self,
        screen: np.ndarray,
        color_bgr: Tuple[int, int, int],
        tolerance: int = 10
    ) -> List[Tuple[int, int]]:
        """
        Find pixels of a specific color
        
        Args:
            screen: Screenshot as numpy array (BGR)
            color_bgr: Target color in BGR format
            tolerance: Color tolerance
        
        Returns:
            List of (x, y) coordinates
        """
        lower = np.array([max(0, c - tolerance) for c in color_bgr])
        upper = np.array([min(255, c + tolerance) for c in color_bgr])
        
        mask = cv2.inRange(screen, lower, upper)
        locations = np.where(mask > 0)
        
        points = list(zip(locations[1], locations[0]))  # x, y format
        return points
    
    def crop_region(
        self,
        screen: np.ndarray,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> np.ndarray:
        """Crop a region from the screen"""
        return screen[y:y+height, x:x+width].copy()
