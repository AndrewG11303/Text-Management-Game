#!/usr/bin/env python3
"""
Template Capture Tool
Helps capture and save UI element templates for the bot

Usage:
    python tools/capture_template.py
    python tools/capture_template.py --name button_collect
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import cv2
    import numpy as np
    from PIL import Image
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("OpenCV not installed. Run: pip install opencv-python")

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False


class TemplateCapturer:
    """Interactive template capture tool"""
    
    def __init__(self, output_dir: str = "assets/templates"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.screenshot = None
        self.selection_start = None
        self.selection_end = None
        self.selecting = False
        self.window_name = "Template Capture - Click and drag to select"
    
    def capture_screen(self) -> np.ndarray:
        """Capture the current screen"""
        if MSS_AVAILABLE:
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                # Convert BGRA to BGR
                if img.shape[2] == 4:
                    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                return img
        else:
            print("MSS not available for screen capture")
            return None
    
    def mouse_callback(self, event, x, y, flags, param):
        """Handle mouse events for region selection"""
        if event == cv2.EVENT_LBUTTONDOWN:
            self.selection_start = (x, y)
            self.selecting = True
        
        elif event == cv2.EVENT_MOUSEMOVE and self.selecting:
            self.selection_end = (x, y)
            # Redraw with selection rectangle
            display = self.screenshot.copy()
            cv2.rectangle(
                display,
                self.selection_start,
                self.selection_end,
                (0, 255, 0),
                2
            )
            cv2.imshow(self.window_name, display)
        
        elif event == cv2.EVENT_LBUTTONUP:
            self.selection_end = (x, y)
            self.selecting = False
    
    def run(self, template_name: str = None):
        """Run the interactive capture tool"""
        if not CV2_AVAILABLE:
            print("OpenCV required for this tool")
            return
        
        print("\n=== Template Capture Tool ===")
        print("1. Position the game window")
        print("2. Press ENTER to capture screen")
        print("3. Click and drag to select template region")
        print("4. Press 'S' to save, 'R' to retry, 'Q' to quit")
        print("================================\n")
        
        input("Press ENTER when ready to capture...")
        
        # Capture screen
        self.screenshot = self.capture_screen()
        
        if self.screenshot is None:
            print("Failed to capture screen")
            return
        
        # Create window and set callback
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(self.window_name, self.mouse_callback)
        
        # Resize for display if too large
        h, w = self.screenshot.shape[:2]
        if w > 1920:
            scale = 1920 / w
            display_size = (int(w * scale), int(h * scale))
            display = cv2.resize(self.screenshot, display_size)
        else:
            display = self.screenshot.copy()
        
        cv2.imshow(self.window_name, display)
        
        while True:
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('s') or key == ord('S'):
                # Save template
                if self.selection_start and self.selection_end:
                    self._save_template(template_name)
                else:
                    print("No region selected!")
            
            elif key == ord('r') or key == ord('R'):
                # Retry capture
                cv2.destroyAllWindows()
                input("\nPress ENTER to capture new screenshot...")
                self.screenshot = self.capture_screen()
                cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
                cv2.setMouseCallback(self.window_name, self.mouse_callback)
                cv2.imshow(self.window_name, self.screenshot)
                self.selection_start = None
                self.selection_end = None
            
            elif key == ord('q') or key == ord('Q') or key == 27:
                # Quit
                break
        
        cv2.destroyAllWindows()
    
    def _save_template(self, name: str = None):
        """Save the selected region as a template"""
        if not self.selection_start or not self.selection_end:
            return
        
        # Get selection bounds
        x1 = min(self.selection_start[0], self.selection_end[0])
        y1 = min(self.selection_start[1], self.selection_end[1])
        x2 = max(self.selection_start[0], self.selection_end[0])
        y2 = max(self.selection_start[1], self.selection_end[1])
        
        # Crop template
        template = self.screenshot[y1:y2, x1:x2]
        
        # Get name
        if not name:
            name = input("Enter template name: ").strip()
            if not name:
                name = f"template_{len(list(self.output_dir.glob('*.png')))}"
        
        # Ensure .png extension
        if not name.endswith('.png'):
            name += '.png'
        
        # Save
        filepath = self.output_dir / name
        cv2.imwrite(str(filepath), template)
        
        print(f"\n✅ Template saved: {filepath}")
        print(f"   Size: {x2-x1}x{y2-y1} pixels")
        
        # Reset selection for next capture
        self.selection_start = None
        self.selection_end = None


def main():
    parser = argparse.ArgumentParser(description='Capture UI templates')
    parser.add_argument(
        '--name', '-n',
        help='Template name (without extension)'
    )
    parser.add_argument(
        '--output', '-o',
        default='assets/templates',
        help='Output directory'
    )
    
    args = parser.parse_args()
    
    capturer = TemplateCapturer(args.output)
    capturer.run(args.name)


if __name__ == '__main__':
    main()
