"""
OCR Module for Infinity Kingdom Bot
Handles text recognition from game screenshots
"""

import re
from typing import Optional, List, Tuple, Dict
from pathlib import Path

import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from src.logger import get_logger


class OCREngine:
    """
    OCR engine for reading text from game screenshots
    Supports both Tesseract and EasyOCR
    """
    
    def __init__(self, engine: str = "auto"):
        """
        Initialize OCR engine
        
        Args:
            engine: 'tesseract', 'easyocr', or 'auto'
        """
        self.logger = get_logger()
        self.engine = None
        self.engine_name = None
        
        # Initialize engine
        if engine == "auto":
            self._init_best_engine()
        elif engine == "tesseract":
            self._init_tesseract()
        elif engine == "easyocr":
            self._init_easyocr()
        else:
            self.logger.warning(f"Unknown OCR engine: {engine}")
            self._init_best_engine()
    
    def _init_best_engine(self):
        """Initialize the best available engine"""
        if EASYOCR_AVAILABLE:
            self._init_easyocr()
        elif TESSERACT_AVAILABLE:
            self._init_tesseract()
        else:
            self.logger.warning("No OCR engine available!")
    
    def _init_tesseract(self):
        """Initialize Tesseract OCR"""
        if not TESSERACT_AVAILABLE:
            self.logger.warning("Tesseract not available")
            return
        
        self.engine_name = "tesseract"
        self.logger.info("OCR: Using Tesseract")
    
    def _init_easyocr(self):
        """Initialize EasyOCR"""
        if not EASYOCR_AVAILABLE:
            self.logger.warning("EasyOCR not available")
            return
        
        try:
            self.engine = easyocr.Reader(['en'], gpu=False)
            self.engine_name = "easyocr"
            self.logger.info("OCR: Using EasyOCR")
        except Exception as e:
            self.logger.error(f"Failed to initialize EasyOCR: {e}")
    
    def read_text(
        self,
        image: np.ndarray,
        preprocess: bool = True
    ) -> str:
        """
        Read text from an image
        
        Args:
            image: Image as numpy array
            preprocess: Whether to preprocess image
        
        Returns:
            Extracted text
        """
        if self.engine_name is None:
            return ""
        
        # Preprocess image
        if preprocess:
            image = self._preprocess_image(image)
        
        # Use appropriate engine
        if self.engine_name == "tesseract":
            return self._read_tesseract(image)
        elif self.engine_name == "easyocr":
            return self._read_easyocr(image)
        
        return ""
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        """
        if not CV2_AVAILABLE:
            return image
        
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply threshold
        _, binary = cv2.threshold(
            gray, 0, 255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        
        # Denoise
        denoised = cv2.medianBlur(binary, 3)
        
        return denoised
    
    def _read_tesseract(self, image: np.ndarray) -> str:
        """Read text using Tesseract"""
        try:
            # Configure Tesseract for game text
            config = '--psm 7 -c tessedit_char_whitelist=0123456789KMB:/ '
            text = pytesseract.image_to_string(image, config=config)
            return text.strip()
        except Exception as e:
            self.logger.debug(f"Tesseract error: {e}")
            return ""
    
    def _read_easyocr(self, image: np.ndarray) -> str:
        """Read text using EasyOCR"""
        if self.engine is None:
            return ""
        
        try:
            results = self.engine.readtext(image)
            # Combine all detected text
            text = " ".join([r[1] for r in results])
            return text.strip()
        except Exception as e:
            self.logger.debug(f"EasyOCR error: {e}")
            return ""
    
    def read_number(self, image: np.ndarray) -> Optional[int]:
        """
        Read a number from an image
        
        Args:
            image: Image containing a number
        
        Returns:
            Extracted number or None
        """
        text = self.read_text(image)
        return self._parse_number(text)
    
    def _parse_number(self, text: str) -> Optional[int]:
        """
        Parse a number from text, handling K/M/B suffixes
        """
        if not text:
            return None
        
        # Clean text
        text = text.upper().strip()
        text = re.sub(r'[^0-9.KMB]', '', text)
        
        if not text:
            return None
        
        try:
            # Handle suffixes
            multiplier = 1
            if text.endswith('K'):
                multiplier = 1000
                text = text[:-1]
            elif text.endswith('M'):
                multiplier = 1000000
                text = text[:-1]
            elif text.endswith('B'):
                multiplier = 1000000000
                text = text[:-1]
            
            # Parse number
            if '.' in text:
                return int(float(text) * multiplier)
            else:
                return int(text) * multiplier
        except ValueError:
            return None
    
    def read_timer(self, image: np.ndarray) -> Optional[int]:
        """
        Read a timer/duration from an image
        
        Args:
            image: Image containing timer text
        
        Returns:
            Duration in seconds or None
        """
        text = self.read_text(image)
        return self._parse_timer(text)
    
    def _parse_timer(self, text: str) -> Optional[int]:
        """
        Parse timer text like "02:30:15" or "1d 5h"
        
        Returns:
            Duration in seconds
        """
        if not text:
            return None
        
        text = text.strip().lower()
        
        # Try HH:MM:SS format
        match = re.match(r'(\d+):(\d+):(\d+)', text)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            return hours * 3600 + minutes * 60 + seconds
        
        # Try MM:SS format
        match = re.match(r'(\d+):(\d+)', text)
        if match:
            minutes, seconds = map(int, match.groups())
            return minutes * 60 + seconds
        
        # Try "1d 5h 30m" format
        total = 0
        
        days = re.search(r'(\d+)\s*d', text)
        if days:
            total += int(days.group(1)) * 86400
        
        hours = re.search(r'(\d+)\s*h', text)
        if hours:
            total += int(hours.group(1)) * 3600
        
        minutes = re.search(r'(\d+)\s*m', text)
        if minutes:
            total += int(minutes.group(1)) * 60
        
        seconds = re.search(r'(\d+)\s*s', text)
        if seconds:
            total += int(seconds.group(1))
        
        return total if total > 0 else None


class ResourceReader:
    """
    Specialized reader for game resources
    """
    
    def __init__(self, ocr_engine: OCREngine):
        self.ocr = ocr_engine
        self.logger = get_logger()
        
        # Resource display regions (relative coordinates)
        # These need to be calibrated for the specific game resolution
        self.resource_regions = {
            'gold': (0.1, 0.02, 0.08, 0.03),
            'food': (0.25, 0.02, 0.08, 0.03),
            'wood': (0.40, 0.02, 0.08, 0.03),
            'iron': (0.55, 0.02, 0.08, 0.03),
            'gems': (0.70, 0.02, 0.08, 0.03),
        }
    
    def read_resources(
        self,
        screenshot: np.ndarray,
        screen_size: Tuple[int, int]
    ) -> Dict[str, int]:
        """
        Read all resource values from screenshot
        
        Args:
            screenshot: Game screenshot
            screen_size: (width, height) of screen
        
        Returns:
            Dict of resource name to value
        """
        resources = {}
        width, height = screen_size
        
        for resource_name, region in self.resource_regions.items():
            # Convert relative to absolute coordinates
            x = int(region[0] * width)
            y = int(region[1] * height)
            w = int(region[2] * width)
            h = int(region[3] * height)
            
            # Crop region
            cropped = screenshot[y:y+h, x:x+w]
            
            # Read number
            value = self.ocr.read_number(cropped)
            
            if value is not None:
                resources[resource_name] = value
                self.logger.debug(f"Read {resource_name}: {value}")
        
        return resources
    
    def read_single_resource(
        self,
        screenshot: np.ndarray,
        region: Tuple[int, int, int, int]
    ) -> Optional[int]:
        """
        Read a single resource value from a specific region
        
        Args:
            screenshot: Game screenshot
            region: (x, y, width, height) pixel coordinates
        
        Returns:
            Resource value or None
        """
        x, y, w, h = region
        cropped = screenshot[y:y+h, x:x+w]
        return self.ocr.read_number(cropped)


class TimerReader:
    """
    Specialized reader for game timers
    """
    
    def __init__(self, ocr_engine: OCREngine):
        self.ocr = ocr_engine
        self.logger = get_logger()
    
    def read_timer(
        self,
        screenshot: np.ndarray,
        region: Tuple[int, int, int, int]
    ) -> Optional[int]:
        """
        Read a timer value from a specific region
        
        Args:
            screenshot: Game screenshot
            region: (x, y, width, height) pixel coordinates
        
        Returns:
            Time remaining in seconds or None
        """
        x, y, w, h = region
        cropped = screenshot[y:y+h, x:x+w]
        return self.ocr.read_timer(cropped)
    
    def find_and_read_timer(
        self,
        screenshot: np.ndarray,
        template_name: str,
        matcher
    ) -> Optional[int]:
        """
        Find a timer element by template and read its value
        
        Args:
            screenshot: Game screenshot
            template_name: Name of timer template
            matcher: ImageMatcher instance
        
        Returns:
            Time remaining in seconds or None
        """
        result = matcher.find_template(screenshot, template_name)
        
        if result:
            x, y, _ = result
            # Assume timer text is to the right of the icon
            timer_region = (x + 50, y - 10, 100, 30)
            return self.read_timer(screenshot, timer_region)
        
        return None
