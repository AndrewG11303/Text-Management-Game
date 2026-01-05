# Infinity Kingdom Bot 🏰

An automated grinding assistant for Infinity Kingdom. This bot helps automate repetitive tasks like resource collection, troop training, and daily quests.

## ⚠️ Disclaimer

This bot is for educational purposes only. Using automation tools may violate the game's Terms of Service and could result in account suspension. Use at your own risk.

## ✨ Features

- **Resource Management**
  - Auto-collect resources from buildings
  - Send marches to gather resources on world map
  - Track resource production

- **Combat Automation**
  - Auto-attack gnomes/monsters
  - Join alliance rallies
  - Battle power calculations

- **Daily Tasks**
  - Collect daily quest rewards
  - Claim mail rewards
  - Alliance help
  - Free chest collection

- **Building Management**
  - Auto-upgrade buildings
  - Train troops
  - Research technologies

- **Smart Features**
  - Human-like behavior (random delays, click offsets)
  - Priority-based task scheduling
  - Error recovery and logging
  - Pause on attack detection

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- An Android emulator (BlueStacks, LDPlayer, etc.) or ADB-connected device
- Infinity Kingdom installed and running

### Installation

1. **Clone or download this repository**
   ```bash
   cd infinity-kingdom-bot
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the setup wizard**
   ```bash
   python main.py --setup
   ```

5. **Start the bot**
   ```bash
   python main.py
   ```

## 📖 Usage

### Basic Commands

```bash
# Run with default settings
python main.py

# Run for a specific duration (4 hours)
python main.py --hours 4

# Run a single task
python main.py --task collect_resources

# Use a custom config file
python main.py --config my_config.yaml

# Enable debug mode
python main.py --debug

# Take a screenshot (for setup/debugging)
python main.py --screenshot
```

### Available Tasks

| Task | Description |
|------|-------------|
| `collect_resources` | Collect from production buildings |
| `gather_resources` | Send marches to gather on world map |
| `daily_quests` | Check and collect quest rewards |
| `collect_mail` | Collect mail rewards |
| `alliance_help` | Help alliance members |
| `free_chests` | Collect free chests and rewards |
| `attack_gnomes` | Auto-attack gnomes |
| `train_troops` | Train troops in barracks |
| `research` | Manage academy research |
| `build_upgrade` | Upgrade buildings |

## ⚙️ Configuration

The bot is configured via `config/settings.yaml`. Run `python main.py --setup` to create a config file interactively.

### Key Settings

```yaml
device:
  type: "emulator"           # 'emulator' or 'adb'
  window_name: "BlueStacks"  # Emulator window name
  resolution:
    width: 1920
    height: 1080

tasks:
  enabled:
    collect_resources: true
    gather_resources: true
    daily_quests: true
    auto_battle: false       # Disabled by default

timing:
  resource_collection_interval: 30  # minutes
  quest_check_interval: 15
  
safety:
  max_runtime_hours: 8       # Auto-stop after 8 hours
  pause_on_attack: true      # Pause if under attack
  human_like_delays: true    # Random delays
```

## 🖼️ Template Images

For the bot to recognize UI elements, you need to capture template images:

1. Take screenshots of your game
2. Crop button/UI element images
3. Save them in `assets/templates/` with descriptive names:
   - `collect_button.png`
   - `upgrade_button.png`
   - `gnome_level_5.png`
   - etc.

### Required Templates

| Template | Description |
|----------|-------------|
| `collect_button.png` | Resource collect button |
| `upgrade_button.png` | Building upgrade button |
| `march_button.png` | March/send troops button |
| `close_button.png` | Close/X button |
| `confirm_button.png` | OK/Confirm button |

## 📁 Project Structure

```
infinity-kingdom-bot/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config/
│   └── settings.yaml       # Configuration
├── src/
│   ├── bot_engine.py       # Main bot controller
│   ├── screen_capture.py   # Screen capture & image matching
│   ├── input_handler.py    # Mouse/keyboard input
│   ├── game_state.py       # Game state tracking
│   ├── task_scheduler.py   # Task scheduling
│   ├── logger.py           # Logging
│   └── tasks/
│       ├── base_task.py    # Base task class
│       ├── resource_tasks.py
│       ├── battle_tasks.py
│       ├── daily_tasks.py
│       └── building_tasks.py
├── assets/
│   └── templates/          # UI template images
└── logs/                   # Log files
```

## 🔧 Customization

### Adding New Tasks

1. Create a new task class extending `BaseTask`:

```python
from src.tasks.base_task import BaseTask

class MyCustomTask(BaseTask):
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "My Custom Task"
    
    def execute(self) -> bool:
        # Your task logic here
        self.click_button('some.button')
        self.wait(1.0)
        return True
```

2. Register it in `bot_engine.py`:

```python
self.scheduler.add_recurring_task(
    task_id='my_task',
    name='My Custom Task',
    callback=self._run_task,
    args=(MyCustomTask(self),),
    interval_minutes=30
)
```

### Adjusting Coordinates

Button positions are defined as relative coordinates (0.0-1.0) in `config/settings.yaml`:

```yaml
coordinates:
  main_screen:
    castle: [0.5, 0.5]    # Center of screen
    world_map: [0.95, 0.85]  # Bottom-right
```

## 🐛 Troubleshooting

### Bot can't find the game window
- Make sure the emulator is running
- Check `window_name` in config matches your emulator
- Try running with `--screenshot` to test screen capture

### Clicks aren't registering
- Verify screen resolution settings
- Check if emulator has any input blocking
- Try increasing `click_delay` in config

### Templates not matching
- Ensure template images match your screen resolution
- Try lowering the match threshold
- Capture new templates from your game

### Bot stops unexpectedly
- Check `logs/` directory for error logs
- Enable debug mode: `python main.py --debug`
- Increase `max_runtime_hours` if needed

## 📝 Logging

Logs are saved to `logs/bot_YYYYMMDD_HHMMSS.log`

Log levels:
- `DEBUG` - Detailed debugging info
- `INFO` - General operation info
- `WARNING` - Potential issues
- `ERROR` - Errors that need attention

## 🤝 Contributing

Feel free to submit issues and pull requests to improve the bot!

## 📜 License

This project is for educational purposes only. Use responsibly.

---

**Note:** This bot requires you to capture your own template images from the game. The effectiveness depends on proper configuration and template matching accuracy.
