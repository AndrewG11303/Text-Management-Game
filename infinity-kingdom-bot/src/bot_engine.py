"""
Main Bot Engine for Infinity Kingdom
Central coordinator for all bot functionality
"""

import time
import signal
import sys
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from src.logger import get_logger, setup_logger
from src.screen_capture import ScreenCapture, ImageMatcher
from src.input_handler import InputHandler
from src.game_state import GameState, StateDetector, GameScreen
from src.task_scheduler import TaskScheduler, TaskPriority, create_randomized_interval

# Import tasks
from src.tasks.resource_tasks import CollectResourcesTask, GatherResourcesTask
from src.tasks.battle_tasks import AttackGnomesTask, AutoBattleTask
from src.tasks.daily_tasks import (
    DailyQuestsTask, CollectMailTask, AllianceHelpTask, FreeChestTask
)
from src.tasks.building_tasks import BuildingUpgradeTask, TrainTroopsTask, ResearchTask


class BotEngine:
    """
    Main bot engine - coordinates all automation components
    """
    
    def __init__(self, config_path: str = "config/settings.yaml"):
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Setup logging
        self.logger = setup_logger(self.config)
        self.logger.info("=" * 50)
        self.logger.info("Infinity Kingdom Bot Starting...")
        self.logger.info("=" * 50)
        
        # Initialize components
        self.screen = ScreenCapture(self.config)
        self.matcher = ImageMatcher(self.config.get('assets_dir', 'assets/templates'))
        self.input = InputHandler(self.config)
        self.state = GameState(self.config)
        self.state_detector = StateDetector(self.state, self.matcher)
        self.scheduler = TaskScheduler(self.config)
        
        # Bot state
        self.running = False
        self.paused = False
        self.start_time = None
        
        # Safety settings
        safety = self.config.get('safety', {})
        self.max_runtime_hours = safety.get('max_runtime_hours', 8)
        self.pause_on_attack = safety.get('pause_on_attack', True)
        self.screenshot_on_error = safety.get('screenshot_on_error', True)
        
        # Statistics
        self.stats = {
            'start_time': None,
            'total_runtime': timedelta(0),
            'errors': 0,
            'tasks_completed': 0
        }
        
        # Register signal handlers
        self._setup_signal_handlers()
        
        # Initialize tasks
        self._setup_tasks()
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file"""
        path = Path(config_path)
        
        if not path.exists():
            # Use default config
            return self._get_default_config()
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _get_default_config(self) -> dict:
        """Return default configuration"""
        return {
            'device': {
                'type': 'emulator',
                'window_name': 'BlueStacks',
                'resolution': {'width': 1920, 'height': 1080}
            },
            'timing': {
                'click_delay': 0.3,
                'action_delay': 1.0,
                'screen_load_delay': 2.0
            },
            'tasks': {
                'enabled': {
                    'collect_resources': True,
                    'daily_quests': True,
                    'alliance_help': True
                }
            },
            'safety': {
                'max_runtime_hours': 8,
                'human_like_delays': True
            },
            'logging': {
                'level': 'INFO',
                'file_logging': True,
                'console_logging': True
            }
        }
    
    def _setup_signal_handlers(self):
        """Setup handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info("Shutdown signal received...")
        self.stop()
    
    def _setup_tasks(self):
        """Initialize and schedule all tasks"""
        tasks_config = self.config.get('tasks', {}).get('enabled', {})
        timing_config = self.config.get('timing', {})
        
        self.logger.info("Setting up automated tasks...")
        
        # Resource collection
        if tasks_config.get('collect_resources', True):
            interval = timing_config.get('resource_collection_interval', 30)
            self.scheduler.add_recurring_task(
                task_id='collect_resources',
                name='Collect Resources',
                callback=self._run_task,
                args=(CollectResourcesTask(self),),
                interval_minutes=interval,
                priority=TaskPriority.NORMAL
            )
            self.logger.info(f"  ✓ Resource collection (every {interval} min)")
        
        # Gather resources
        if tasks_config.get('gather_resources', True):
            self.scheduler.add_recurring_task(
                task_id='gather_resources',
                name='Gather Resources',
                callback=self._run_task,
                args=(GatherResourcesTask(self),),
                interval_minutes=60,
                priority=TaskPriority.NORMAL
            )
            self.logger.info("  ✓ Resource gathering (every 60 min)")
        
        # Daily quests
        if tasks_config.get('daily_quests', True):
            interval = timing_config.get('quest_check_interval', 15)
            self.scheduler.add_recurring_task(
                task_id='daily_quests',
                name='Daily Quests',
                callback=self._run_task,
                args=(DailyQuestsTask(self),),
                interval_minutes=interval,
                priority=TaskPriority.NORMAL
            )
            self.logger.info(f"  ✓ Daily quests (every {interval} min)")
        
        # Mail collection
        if tasks_config.get('collect_mail', True):
            interval = timing_config.get('mail_check_interval', 60)
            self.scheduler.add_recurring_task(
                task_id='collect_mail',
                name='Collect Mail',
                callback=self._run_task,
                args=(CollectMailTask(self),),
                interval_minutes=interval,
                priority=TaskPriority.LOW
            )
            self.logger.info(f"  ✓ Mail collection (every {interval} min)")
        
        # Alliance help
        if tasks_config.get('alliance_help', True):
            interval = timing_config.get('alliance_help_interval', 10)
            self.scheduler.add_recurring_task(
                task_id='alliance_help',
                name='Alliance Help',
                callback=self._run_task,
                args=(AllianceHelpTask(self),),
                interval_minutes=interval,
                priority=TaskPriority.LOW
            )
            self.logger.info(f"  ✓ Alliance help (every {interval} min)")
        
        # Free chests
        if tasks_config.get('free_chests', True):
            interval = timing_config.get('free_chest_interval', 5)
            self.scheduler.add_recurring_task(
                task_id='free_chests',
                name='Free Chests',
                callback=self._run_task,
                args=(FreeChestTask(self),),
                interval_minutes=interval,
                priority=TaskPriority.LOW
            )
            self.logger.info(f"  ✓ Free chests (every {interval} min)")
        
        # Auto battle (gnomes)
        if tasks_config.get('auto_battle', False):
            self.scheduler.add_recurring_task(
                task_id='auto_battle',
                name='Auto Battle',
                callback=self._run_task,
                args=(AttackGnomesTask(self),),
                interval_minutes=30,
                priority=TaskPriority.NORMAL
            )
            self.logger.info("  ✓ Auto battle (every 30 min)")
        
        # Training
        if tasks_config.get('train_troops', True):
            self.scheduler.add_recurring_task(
                task_id='train_troops',
                name='Train Troops',
                callback=self._run_task,
                args=(TrainTroopsTask(self),),
                interval_minutes=30,
                priority=TaskPriority.NORMAL
            )
            self.logger.info("  ✓ Troop training (every 30 min)")
        
        # Research
        if tasks_config.get('research', True):
            self.scheduler.add_recurring_task(
                task_id='research',
                name='Research',
                callback=self._run_task,
                args=(ResearchTask(self),),
                interval_minutes=60,
                priority=TaskPriority.NORMAL
            )
            self.logger.info("  ✓ Research (every 60 min)")
        
        # Building upgrades
        if tasks_config.get('build_upgrade', True):
            self.scheduler.add_recurring_task(
                task_id='build_upgrade',
                name='Building Upgrade',
                callback=self._run_task,
                args=(BuildingUpgradeTask(self),),
                interval_minutes=60,
                priority=TaskPriority.NORMAL
            )
            self.logger.info("  ✓ Building upgrades (every 60 min)")
        
        self.logger.info("Task setup complete!")
    
    def _run_task(self, task) -> bool:
        """Execute a task with error handling"""
        try:
            return task.run()
        except Exception as e:
            self.logger.error(f"Task error: {e}")
            self.stats['errors'] += 1
            
            if self.screenshot_on_error:
                self.screen.save_screenshot(directory="logs/errors")
            
            return False
    
    def start(self, duration_hours: Optional[float] = None):
        """
        Start the bot
        
        Args:
            duration_hours: Maximum runtime (None = use config)
        """
        if self.running:
            self.logger.warning("Bot is already running")
            return
        
        self.running = True
        self.start_time = datetime.now()
        self.stats['start_time'] = self.start_time
        
        # Determine max runtime
        max_hours = duration_hours or self.max_runtime_hours
        max_seconds = int(max_hours * 3600) if max_hours > 0 else None
        
        self.logger.info(f"Bot started at {self.start_time}")
        if max_seconds:
            self.logger.info(f"Maximum runtime: {max_hours} hours")
        
        # Initial state check
        self._check_initial_state()
        
        # Start the scheduler
        try:
            self.scheduler.run(duration_seconds=max_seconds)
        except Exception as e:
            self.logger.error(f"Bot error: {e}")
            if self.screenshot_on_error:
                self.screen.save_screenshot(directory="logs/errors")
        finally:
            self.stop()
    
    def _check_initial_state(self):
        """Check initial game state"""
        self.logger.info("Checking initial game state...")
        
        # Capture screen
        screen = self.screen.capture()
        
        if screen is None:
            self.logger.warning("Could not capture screen - is the game running?")
            return
        
        # Detect current screen
        self.state_detector.update_state(screen)
        
        self.logger.info(f"Current screen: {self.state.current_screen.name}")
        
        # Navigate to main city if not there
        if self.state.current_screen != GameScreen.MAIN_CITY:
            self._navigate_to_main()
    
    def _navigate_to_main(self):
        """Navigate to main city screen"""
        self.logger.info("Navigating to main city...")
        
        # Try closing any popups first
        for _ in range(3):
            self.input.click_coordinate('ui.close_button')
            time.sleep(0.5)
        
        # Click castle/home button
        self.input.click_coordinate('main_screen.castle')
        time.sleep(2.0)
    
    def stop(self):
        """Stop the bot gracefully"""
        if not self.running:
            return
        
        self.running = False
        self.scheduler.stop()
        
        # Calculate runtime
        if self.start_time:
            runtime = datetime.now() - self.start_time
            self.stats['total_runtime'] = runtime
        
        self._print_summary()
        self.logger.info("Bot stopped")
    
    def pause(self):
        """Pause bot execution"""
        self.paused = True
        self.scheduler.pause()
        self.logger.info("Bot paused")
    
    def resume(self):
        """Resume bot execution"""
        self.paused = False
        self.scheduler.resume()
        self.logger.info("Bot resumed")
    
    def _print_summary(self):
        """Print session summary"""
        self.logger.info("")
        self.logger.info("=" * 50)
        self.logger.info("SESSION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total runtime: {self.stats['total_runtime']}")
        self.logger.info(f"Tasks completed: {self.state.stats['tasks_completed']}")
        self.logger.info(f"Battles won: {self.state.stats['battles_won']}")
        self.logger.info(f"Errors: {self.stats['errors']}")
        self.logger.info("=" * 50)
    
    def run_single_task(self, task_name: str) -> bool:
        """
        Run a single task immediately
        
        Args:
            task_name: Name of task to run
        
        Returns:
            True if task succeeded
        """
        task_map = {
            'collect_resources': CollectResourcesTask,
            'gather_resources': GatherResourcesTask,
            'daily_quests': DailyQuestsTask,
            'collect_mail': CollectMailTask,
            'alliance_help': AllianceHelpTask,
            'free_chests': FreeChestTask,
            'attack_gnomes': AttackGnomesTask,
            'train_troops': TrainTroopsTask,
            'research': ResearchTask,
            'build_upgrade': BuildingUpgradeTask,
        }
        
        task_class = task_map.get(task_name)
        if not task_class:
            self.logger.error(f"Unknown task: {task_name}")
            return False
        
        task = task_class(self)
        return self._run_task(task)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status"""
        return {
            'running': self.running,
            'paused': self.paused,
            'uptime': str(datetime.now() - self.start_time) if self.start_time else '0:00:00',
            'current_screen': self.state.current_screen.name,
            'scheduler': self.scheduler.get_status(),
            'game_state': self.state.to_dict(),
            'stats': self.stats
        }


def create_bot(config_path: str = "config/settings.yaml") -> BotEngine:
    """
    Factory function to create a bot instance
    
    Args:
        config_path: Path to configuration file
    
    Returns:
        Configured BotEngine instance
    """
    return BotEngine(config_path)
