"""
Game State Module for Infinity Kingdom Bot
Tracks and manages the current state of the game
"""

import time
from enum import Enum, auto
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from src.logger import get_logger


class GameScreen(Enum):
    """Enum for different game screens"""
    UNKNOWN = auto()
    LOADING = auto()
    LOGIN = auto()
    MAIN_CITY = auto()
    WORLD_MAP = auto()
    BATTLE = auto()
    BUILDING_MENU = auto()
    RESOURCE_BUILDING = auto()
    BARRACKS = auto()
    ACADEMY = auto()
    ALLIANCE = auto()
    INVENTORY = auto()
    SHOP = auto()
    MAIL = auto()
    QUESTS = auto()
    EVENTS = auto()
    CHAT = auto()
    SETTINGS = auto()
    PROFILE = auto()
    IMMORTAL_SELECTION = auto()
    MARCH_SCREEN = auto()


class MarchStatus(Enum):
    """Status of a march"""
    IDLE = auto()
    MARCHING = auto()
    GATHERING = auto()
    ATTACKING = auto()
    RETURNING = auto()
    REINFORCING = auto()


@dataclass
class Resources:
    """Track current resources"""
    gold: int = 0
    food: int = 0
    wood: int = 0
    iron: int = 0
    gems: int = 0
    vip_points: int = 0
    
    def to_dict(self) -> dict:
        return {
            'gold': self.gold,
            'food': self.food,
            'wood': self.wood,
            'iron': self.iron,
            'gems': self.gems,
            'vip_points': self.vip_points
        }
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class March:
    """Represents a single march/army"""
    march_id: int
    status: MarchStatus = MarchStatus.IDLE
    target: Optional[str] = None
    troops: int = 0
    immortals: List[str] = field(default_factory=list)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    def time_remaining(self) -> Optional[timedelta]:
        """Get remaining time for march"""
        if self.end_time:
            remaining = self.end_time - datetime.now()
            if remaining.total_seconds() > 0:
                return remaining
        return None
    
    def is_available(self) -> bool:
        """Check if march slot is available"""
        return self.status == MarchStatus.IDLE


@dataclass
class Building:
    """Represents a building in the city"""
    name: str
    level: int = 1
    is_upgrading: bool = False
    upgrade_end_time: Optional[datetime] = None
    position: tuple = (0, 0)
    
    def time_remaining(self) -> Optional[timedelta]:
        if self.upgrade_end_time:
            remaining = self.upgrade_end_time - datetime.now()
            if remaining.total_seconds() > 0:
                return remaining
        return None


@dataclass
class QueueItem:
    """Represents an item in a production queue"""
    item_type: str
    amount: int
    end_time: Optional[datetime] = None


class GameState:
    """
    Central game state manager
    Tracks all important game information
    """
    
    def __init__(self, config: dict):
        self.config = config
        self.logger = get_logger()
        
        # Current screen
        self.current_screen = GameScreen.UNKNOWN
        self.previous_screen = GameScreen.UNKNOWN
        
        # Resources
        self.resources = Resources()
        
        # Marches (typically 3-5 depending on VIP/research)
        self.max_marches = 3
        self.marches: Dict[int, March] = {
            i: March(march_id=i) for i in range(self.max_marches)
        }
        
        # Buildings
        self.buildings: Dict[str, Building] = {}
        
        # Production queues
        self.training_queue: List[QueueItem] = []
        self.research_queue: List[QueueItem] = []
        self.building_queue: List[QueueItem] = []
        
        # Timers and cooldowns
        self.cooldowns: Dict[str, datetime] = {}
        
        # Statistics
        self.stats = {
            'session_start': datetime.now(),
            'resources_collected': Resources(),
            'battles_won': 0,
            'battles_lost': 0,
            'troops_trained': 0,
            'buildings_upgraded': 0,
            'tasks_completed': 0
        }
        
        # Flags
        self.is_under_attack = False
        self.has_shield = False
        self.is_in_battle = False
        
        # Last update times
        self.last_resource_update = None
        self.last_state_update = None
    
    def set_screen(self, screen: GameScreen):
        """Update current screen"""
        if screen != self.current_screen:
            self.previous_screen = self.current_screen
            self.current_screen = screen
            self.logger.debug(f"Screen changed: {self.previous_screen.name} -> {screen.name}")
    
    def get_available_marches(self) -> List[March]:
        """Get list of available march slots"""
        return [m for m in self.marches.values() if m.is_available()]
    
    def get_active_marches(self) -> List[March]:
        """Get list of active marches"""
        return [m for m in self.marches.values() if not m.is_available()]
    
    def update_march(self, march_id: int, **kwargs):
        """Update march information"""
        if march_id in self.marches:
            march = self.marches[march_id]
            for key, value in kwargs.items():
                if hasattr(march, key):
                    setattr(march, key, value)
    
    def start_march(
        self,
        march_id: int,
        status: MarchStatus,
        target: str,
        troops: int,
        duration_seconds: int
    ):
        """Record a march starting"""
        if march_id in self.marches:
            march = self.marches[march_id]
            march.status = status
            march.target = target
            march.troops = troops
            march.start_time = datetime.now()
            march.end_time = datetime.now() + timedelta(seconds=duration_seconds)
            
            self.logger.info(
                f"March {march_id} started: {status.name} to {target} "
                f"with {troops} troops"
            )
    
    def complete_march(self, march_id: int):
        """Mark a march as complete"""
        if march_id in self.marches:
            march = self.marches[march_id]
            march.status = MarchStatus.IDLE
            march.target = None
            march.start_time = None
            march.end_time = None
            self.logger.info(f"March {march_id} completed")
    
    def update_resources(self, **kwargs):
        """Update resource counts"""
        self.resources.update(**kwargs)
        self.last_resource_update = datetime.now()
        self.logger.debug(f"Resources updated: {self.resources.to_dict()}")
    
    def add_building(self, name: str, level: int = 1, position: tuple = (0, 0)):
        """Add or update a building"""
        self.buildings[name] = Building(
            name=name,
            level=level,
            position=position
        )
    
    def start_building_upgrade(self, name: str, duration_seconds: int):
        """Record a building upgrade starting"""
        if name in self.buildings:
            building = self.buildings[name]
            building.is_upgrading = True
            building.upgrade_end_time = datetime.now() + timedelta(seconds=duration_seconds)
            self.logger.info(f"Building upgrade started: {name}")
    
    def set_cooldown(self, name: str, duration_seconds: int):
        """Set a cooldown timer"""
        self.cooldowns[name] = datetime.now() + timedelta(seconds=duration_seconds)
    
    def is_on_cooldown(self, name: str) -> bool:
        """Check if something is on cooldown"""
        if name in self.cooldowns:
            return datetime.now() < self.cooldowns[name]
        return False
    
    def get_cooldown_remaining(self, name: str) -> Optional[timedelta]:
        """Get remaining cooldown time"""
        if name in self.cooldowns:
            remaining = self.cooldowns[name] - datetime.now()
            if remaining.total_seconds() > 0:
                return remaining
        return None
    
    def increment_stat(self, stat_name: str, amount: int = 1):
        """Increment a statistic"""
        if stat_name in self.stats:
            if isinstance(self.stats[stat_name], int):
                self.stats[stat_name] += amount
    
    def get_session_duration(self) -> timedelta:
        """Get current session duration"""
        return datetime.now() - self.stats['session_start']
    
    def check_timers(self) -> List[str]:
        """
        Check all timers and return list of completed items
        Used to trigger actions when timers complete
        """
        completed = []
        
        # Check marches
        for march_id, march in self.marches.items():
            if march.end_time and datetime.now() >= march.end_time:
                completed.append(f"march_{march_id}")
        
        # Check buildings
        for name, building in self.buildings.items():
            if building.upgrade_end_time and datetime.now() >= building.upgrade_end_time:
                completed.append(f"building_{name}")
        
        # Check queues
        for queue in [self.training_queue, self.research_queue]:
            for item in queue:
                if item.end_time and datetime.now() >= item.end_time:
                    completed.append(f"queue_{item.item_type}")
        
        return completed
    
    def to_dict(self) -> dict:
        """Export state to dictionary"""
        return {
            'current_screen': self.current_screen.name,
            'resources': self.resources.to_dict(),
            'marches': {
                mid: {
                    'status': m.status.name,
                    'target': m.target,
                    'troops': m.troops
                }
                for mid, m in self.marches.items()
            },
            'is_under_attack': self.is_under_attack,
            'has_shield': self.has_shield,
            'stats': {
                k: str(v) if isinstance(v, (datetime, Resources)) else v
                for k, v in self.stats.items()
            }
        }
    
    def __str__(self) -> str:
        """String representation of game state"""
        return (
            f"GameState(screen={self.current_screen.name}, "
            f"gold={self.resources.gold}, "
            f"marches={len(self.get_active_marches())}/{self.max_marches})"
        )


class StateDetector:
    """
    Detects the current game state from screenshots
    Uses image recognition to identify screens and UI elements
    """
    
    def __init__(self, game_state: GameState, image_matcher):
        self.state = game_state
        self.matcher = image_matcher
        self.logger = get_logger()
        
        # Screen detection templates
        self.screen_templates = {
            GameScreen.MAIN_CITY: ['castle_icon', 'city_view'],
            GameScreen.WORLD_MAP: ['world_map_icon', 'map_view'],
            GameScreen.BATTLE: ['battle_ui', 'army_power'],
            GameScreen.MAIL: ['mail_header'],
            GameScreen.ALLIANCE: ['alliance_header'],
            GameScreen.QUESTS: ['quest_header'],
        }
    
    def detect_screen(self, screenshot) -> GameScreen:
        """
        Analyze screenshot to determine current screen
        
        Args:
            screenshot: numpy array of current screen
        
        Returns:
            Detected GameScreen enum value
        """
        # Try to match against known screen templates
        for screen, templates in self.screen_templates.items():
            for template in templates:
                result = self.matcher.find_template(screenshot, template, threshold=0.7)
                if result:
                    self.state.set_screen(screen)
                    return screen
        
        return GameScreen.UNKNOWN
    
    def detect_resources(self, screenshot) -> Dict[str, int]:
        """
        Use OCR or template matching to read resource values
        This is a placeholder - actual implementation would use OCR
        """
        # TODO: Implement OCR-based resource detection
        return {}
    
    def detect_popup(self, screenshot) -> Optional[str]:
        """
        Check if there's a popup dialog on screen
        """
        popup_templates = [
            'popup_reward',
            'popup_error',
            'popup_confirm',
            'popup_attack_warning'
        ]
        
        for template in popup_templates:
            result = self.matcher.find_template(screenshot, template)
            if result:
                return template
        
        return None
    
    def update_state(self, screenshot) -> GameState:
        """
        Full state update from screenshot
        """
        # Detect current screen
        self.detect_screen(screenshot)
        
        # Update resources if on main screen
        if self.state.current_screen == GameScreen.MAIN_CITY:
            resources = self.detect_resources(screenshot)
            if resources:
                self.state.update_resources(**resources)
        
        # Check for popups
        popup = self.detect_popup(screenshot)
        if popup:
            self.logger.debug(f"Popup detected: {popup}")
        
        self.state.last_state_update = datetime.now()
        
        return self.state
