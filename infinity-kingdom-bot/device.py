import subprocess
import os
from utils import randomize_coordinate, random_sleep

class DeviceController:
    def __init__(self, device_id=None):
        self.device_id = device_id
        self.connected = False
        self.connect()

    def connect(self):
        """Checks connection to ADB."""
        try:
            cmd = ["adb", "devices"]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "device" in result.stdout and (self.device_id is None or self.device_id in result.stdout):
                self.connected = True
                print("Device connected.")
            else:
                print("No device found via ADB. Running in simulation mode (clicks will be printed).")
                self.connected = False
        except FileNotFoundError:
            print("ADB not found in path. Running in simulation mode.")
            self.connected = False

    def tap(self, x, y):
        """Taps at coordinates x, y."""
        x, y = randomize_coordinate(x, y)
        if self.connected:
            cmd = ["adb", "shell", "input", "tap", str(x), str(y)]
            if self.device_id:
                cmd = ["adb", "-s", self.device_id, "shell", "input", "tap", str(x), str(y)]
            subprocess.run(cmd)
        else:
            print(f"[SIMULATION] Tapped at ({x}, {y})")

    def swipe(self, x1, y1, x2, y2, duration=500):
        """Swipes from (x1, y1) to (x2, y2) in duration ms."""
        if self.connected:
            cmd = ["adb", "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)]
            if self.device_id:
                cmd = ["adb", "-s", self.device_id, "shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(duration)]
            subprocess.run(cmd)
        else:
            print(f"[SIMULATION] Swiped from ({x1}, {y1}) to ({x2}, {y2}) duration {duration}ms")

    def screencap(self, filename="screen.png"):
        """Takes a screenshot and saves it to filename."""
        if self.connected:
            remote_path = "/sdcard/screen.png"
            cmd_cap = ["adb", "shell", "screencap", "-p", remote_path]
            cmd_pull = ["adb", "pull", remote_path, filename]
            if self.device_id:
                cmd_cap = ["adb", "-s", self.device_id, "shell", "screencap", "-p", remote_path]
                cmd_pull = ["adb", "-s", self.device_id, "pull", remote_path, filename]
            
            subprocess.run(cmd_cap)
            subprocess.run(cmd_pull)
        else:
            print(f"[SIMULATION] Screenshot saved to {filename} (fake)")
            # Create a dummy file or just do nothing
            with open(filename, "wb") as f:
                f.write(b"fake image data")

    def press_back(self):
        if self.connected:
            cmd = ["adb", "shell", "input", "keyevent", "4"]
            subprocess.run(cmd)
        else:
            print("[SIMULATION] Pressed BACK button")
