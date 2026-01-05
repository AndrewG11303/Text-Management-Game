"""
Configuration file for Infinity Kingdom Bot.
Contains button positions, game constants, and settings.
Assumes a specific resolution (e.g., 1920x1080).
"""

# Screen Resolution
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# Time settings (seconds)
DEFAULT_SLEEP = 1.0
LONG_SLEEP = 3.0

# Button Positions (x, y)
# These are placeholder coordinates. You should update them with actual values from your device.
BUTTONS = {
    "main_menu": {
        "world_map": (100, 900),
        "inventory": (200, 900),
        "alliance": (300, 900),
        "mail": (400, 900),
        "profile": (50, 50),
    },
    "resources": {
        "collect_all": (960, 540),  # Center of screen?
        "search": (50, 800),
    },
    "upgrade": {
        "upgrade_btn": (1500, 900),
        "speed_up": (1300, 900),
        "use_gems": (1400, 900),
    },
    "troops": {
        "train": (1600, 800),
        "barracks": (500, 500),
    }
}

# Thresholds
RESOURCE_THRESHOLDS = {
    "food": 10000,
    "wood": 10000,
    "stone": 5000,
    "iron": 2000,
}

# Logic Settings
ENABLE_AUTO_GATHER = True
ENABLE_AUTO_TRAIN = True
ENABLE_AUTO_UPGRADE = True
