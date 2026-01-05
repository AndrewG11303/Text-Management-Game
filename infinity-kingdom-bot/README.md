# Infinity Kingdom Automation Bot

This bot automates daily tasks in Infinity Kingdom using ADB (Android Debug Bridge).

## Prerequisites

1.  **Python 3.x**
2.  **ADB Installed**: Ensure `adb` is in your system PATH.
3.  **Android Device/Emulator**:
    *   Enable **Developer Options**.
    *   Enable **USB Debugging**.
    *   Connect via USB or TCP/IP.
    *   Resolution: The default coordinates in `config.py` are set for **1920x1080**. If your device differs, you must update `config.py`.

## Setup

1.  Install dependencies (standard libraries used, no pip install needed for basic version).
2.  Update `config.py`:
    *   Take screenshots of your game.
    *   Find the X, Y coordinates of buttons (Collect, Train, Upgrade, etc.).
    *   Update `BUTTONS` dictionary in `config.py`.

## Usage

Run the bot:

```bash
python main.py
```

## Features

*   **Auto-Collect Resources**: Taps the collection locations.
*   **Auto-Train Troops**: cycles through barracks.
*   **Auto-Upgrade**: Attempts to upgrade buildings.
*   **Anti-Detection**: Uses random sleep intervals and randomized coordinate tapping (human-like behavior).

## Project Structure

*   `main.py`: Entry point.
*   `bot.py`: Main logic loop.
*   `device.py`: Handles ADB commands (clicks, swipes, screenshots).
*   `config.py`: Stores coordinates and settings.
*   `utils.py`: Helper functions for math and time.
