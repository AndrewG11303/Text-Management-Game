import time
from device import DeviceController
from utils import random_sleep, timestamp
import config

class InfinityKingdomBot:
    def __init__(self):
        self.device = DeviceController()
        self.state = "IDLE"

    def run(self):
        print(f"[{timestamp()}] Bot started.")
        try:
            while True:
                self.game_loop()
                # Sleep between loops to avoid spamming
                random_sleep(config.LONG_SLEEP)
        except KeyboardInterrupt:
            print(f"[{timestamp()}] Bot stopped by user.")

    def game_loop(self):
        """Main decision loop."""
        
        # Ensure we are at base
        self.go_to_main_menu()
        random_sleep(1)

        # 1. Collect Resources
        if config.ENABLE_AUTO_GATHER:
            self.collect_resources()
            random_sleep(2)

        # 2. Train Troops
        if config.ENABLE_AUTO_TRAIN:
            self.train_troops()
            random_sleep(2)

        # 3. Upgrade Buildings
        if config.ENABLE_AUTO_UPGRADE:
            self.upgrade_building()
            random_sleep(2)

    def collect_resources(self):
        print(f"[{timestamp()}] Checking resources...")
        # Logic: Tap a location where resource collection bubbles appear
        # Assuming we are at main base
        
        # Example: Tap "Collect All" button if it exists or specific resource tiles
        # Using config coordinates
        pos = config.BUTTONS["resources"]["collect_all"]
        self.device.tap(*pos)
        print(" -> Tapped Collect All")

    def train_troops(self):
        print(f"[{timestamp()}] Checking troops...")
        # Logic: Go to barracks -> Train
        # This is simplified. Real logic needs state awareness (are we in base? is menu open?)
        
        # 1. Tap Barracks
        barracks_pos = config.BUTTONS["troops"]["barracks"]
        self.device.tap(*barracks_pos)
        random_sleep(1)
        
        # 2. Tap Train button
        train_pos = config.BUTTONS["troops"]["train"]
        self.device.tap(*train_pos)
        print(" -> Issued Train command")
        
        # 3. Return to map/base (press back or close)
        self.device.press_back()

    def upgrade_building(self):
        print(f"[{timestamp()}] Checking upgrades...")
        # Simplified logic
        # 1. Tap building to upgrade (using a known location or searching)
        # For now, just tap a placeholder location
        upgrade_pos = config.BUTTONS["upgrade"]["upgrade_btn"]
        self.device.tap(*upgrade_pos)
        print(" -> Tapped Upgrade")
        
        self.device.press_back()

    def go_to_main_menu(self):
        # Logic to ensure we are at the main screen
        # A simple strategy is to press back a few times
        print(" -> Resetting to Main Menu")
        for _ in range(3):
            self.device.press_back()
            random_sleep(0.5)
