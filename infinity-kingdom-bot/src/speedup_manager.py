"""
Speed-Up Manager for Infinity Kingdom Bot
Automatically manages and uses speed-up items
"""

import time
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta

from src.logger import get_logger


class SpeedUpType(Enum):
    """Types of speed-up items"""
    UNIVERSAL = auto()      # Works on anything
    BUILDING = auto()        # Building construction only
    RESEARCH = auto()        # Research only
    TRAINING = auto()        # Troop training only
    HEALING = auto()         # Hospital healing only
    DRAGON = auto()          # Dragon related only


class SpeedUpTarget(Enum):
    """What can be sped up"""
    BUILDING = auto()
    RESEARCH = auto()
    TRAINING = auto()
    HEALING = auto()
    DRAGON_UPGRADE = auto()
    DRAGON_SKILL = auto()
    DRAGON_HATCHING = auto()


@dataclass
class SpeedUpItem:
    """Represents a speed-up item"""
    name: str
    duration_seconds: int      # How much time it removes
    item_type: SpeedUpType
    quantity: int = 0
    
    # Item identifiers for game
    template_name: str = ""    # Template for finding in inventory
    
    def total_time(self) -> int:
        """Total time reduction available"""
        return self.duration_seconds * self.quantity
    
    def __str__(self):
        return f"{self.name} ({self.quantity}x, {self.duration_seconds}s each)"


@dataclass 
class SpeedUpInventory:
    """Tracks available speed-up items"""
    items: Dict[str, SpeedUpItem] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    
    def add_item(self, item: SpeedUpItem):
        """Add or update an item"""
        self.items[item.name] = item
        self.last_updated = datetime.now()
    
    def get_items_for_target(self, target: SpeedUpTarget) -> List[SpeedUpItem]:
        """Get applicable items for a target type"""
        applicable = []
        
        # Map targets to item types
        type_map = {
            SpeedUpTarget.BUILDING: [SpeedUpType.BUILDING, SpeedUpType.UNIVERSAL],
            SpeedUpTarget.RESEARCH: [SpeedUpType.RESEARCH, SpeedUpType.UNIVERSAL],
            SpeedUpTarget.TRAINING: [SpeedUpType.TRAINING, SpeedUpType.UNIVERSAL],
            SpeedUpTarget.HEALING: [SpeedUpType.HEALING, SpeedUpType.UNIVERSAL],
            SpeedUpTarget.DRAGON_UPGRADE: [SpeedUpType.DRAGON, SpeedUpType.UNIVERSAL],
            SpeedUpTarget.DRAGON_SKILL: [SpeedUpType.DRAGON, SpeedUpType.UNIVERSAL],
            SpeedUpTarget.DRAGON_HATCHING: [SpeedUpType.DRAGON, SpeedUpType.UNIVERSAL],
        }
        
        valid_types = type_map.get(target, [SpeedUpType.UNIVERSAL])
        
        for item in self.items.values():
            if item.item_type in valid_types and item.quantity > 0:
                applicable.append(item)
        
        # Sort by duration (smallest first for efficiency)
        applicable.sort(key=lambda x: x.duration_seconds)
        
        return applicable
    
    def get_total_time_available(self, target: SpeedUpTarget) -> int:
        """Get total speed-up time available for a target"""
        items = self.get_items_for_target(target)
        return sum(item.total_time() for item in items)
    
    def use_item(self, item_name: str, count: int = 1) -> bool:
        """Record using an item"""
        if item_name in self.items:
            if self.items[item_name].quantity >= count:
                self.items[item_name].quantity -= count
                return True
        return False


class SpeedUpStrategy(Enum):
    """Speed-up usage strategies"""
    NEVER = auto()           # Never use speed-ups
    FREE_ONLY = auto()       # Only use free instant complete
    CONSERVATIVE = auto()    # Use sparingly, save for important
    MODERATE = auto()        # Use for long timers
    AGGRESSIVE = auto()      # Use frequently to progress fast
    ALWAYS = auto()          # Use on everything


@dataclass
class SpeedUpRule:
    """Rule for when to use speed-ups"""
    target: SpeedUpTarget
    strategy: SpeedUpStrategy
    
    # Thresholds
    min_remaining_seconds: int = 0      # Only speed up if more than this remains
    max_remaining_seconds: int = 86400  # Only speed up if less than this remains
    
    # For CONSERVATIVE/MODERATE strategies
    use_if_under_minutes: int = 5       # Auto-complete if under X minutes
    use_percentage: float = 0.0         # Use speed-ups for X% of time
    
    # Item preferences
    prefer_specific_items: bool = True  # Prefer building speedups for buildings
    use_universal: bool = True          # Allow universal speed-ups
    
    # Limits
    max_items_per_use: int = 10         # Max items to use at once
    daily_limit: int = 0                # Max uses per day (0 = unlimited)


class SpeedUpManager:
    """
    Manages automatic speed-up usage
    
    Features:
    - Tracks speed-up inventory
    - Configurable strategies per target type
    - Smart item selection (use smallest first)
    - Free speed-up detection
    - Daily usage limits
    """
    
    def __init__(self, bot_engine):
        self.bot = bot_engine
        self.config = bot_engine.config
        self.logger = get_logger()
        
        # Speed-up inventory
        self.inventory = SpeedUpInventory()
        
        # Initialize default items
        self._init_default_items()
        
        # Load rules from config
        self.rules = self._load_rules()
        
        # Usage tracking
        self.daily_usage: Dict[str, int] = {}
        self.last_reset_date: Optional[datetime] = None
        
        # Free speed-up tracking
        self.free_speedup_available: Dict[SpeedUpTarget, bool] = {
            target: False for target in SpeedUpTarget
        }
        
        self.logger.info("SpeedUp Manager initialized")
    
    def _init_default_items(self):
        """Initialize default speed-up item definitions"""
        default_items = [
            # Universal speed-ups
            SpeedUpItem("1min_universal", 60, SpeedUpType.UNIVERSAL, 0, "speedup_1m"),
            SpeedUpItem("5min_universal", 300, SpeedUpType.UNIVERSAL, 0, "speedup_5m"),
            SpeedUpItem("15min_universal", 900, SpeedUpType.UNIVERSAL, 0, "speedup_15m"),
            SpeedUpItem("60min_universal", 3600, SpeedUpType.UNIVERSAL, 0, "speedup_60m"),
            SpeedUpItem("3hour_universal", 10800, SpeedUpType.UNIVERSAL, 0, "speedup_3h"),
            SpeedUpItem("8hour_universal", 28800, SpeedUpType.UNIVERSAL, 0, "speedup_8h"),
            SpeedUpItem("24hour_universal", 86400, SpeedUpType.UNIVERSAL, 0, "speedup_24h"),
            
            # Building specific
            SpeedUpItem("1min_building", 60, SpeedUpType.BUILDING, 0, "speedup_build_1m"),
            SpeedUpItem("5min_building", 300, SpeedUpType.BUILDING, 0, "speedup_build_5m"),
            SpeedUpItem("15min_building", 900, SpeedUpType.BUILDING, 0, "speedup_build_15m"),
            SpeedUpItem("60min_building", 3600, SpeedUpType.BUILDING, 0, "speedup_build_60m"),
            
            # Research specific
            SpeedUpItem("1min_research", 60, SpeedUpType.RESEARCH, 0, "speedup_research_1m"),
            SpeedUpItem("5min_research", 300, SpeedUpType.RESEARCH, 0, "speedup_research_5m"),
            SpeedUpItem("15min_research", 900, SpeedUpType.RESEARCH, 0, "speedup_research_15m"),
            SpeedUpItem("60min_research", 3600, SpeedUpType.RESEARCH, 0, "speedup_research_60m"),
            
            # Training specific
            SpeedUpItem("1min_training", 60, SpeedUpType.TRAINING, 0, "speedup_train_1m"),
            SpeedUpItem("5min_training", 300, SpeedUpType.TRAINING, 0, "speedup_train_5m"),
            SpeedUpItem("15min_training", 900, SpeedUpType.TRAINING, 0, "speedup_train_15m"),
            
            # Dragon specific
            SpeedUpItem("1min_dragon", 60, SpeedUpType.DRAGON, 0, "speedup_dragon_1m"),
            SpeedUpItem("5min_dragon", 300, SpeedUpType.DRAGON, 0, "speedup_dragon_5m"),
            SpeedUpItem("15min_dragon", 900, SpeedUpType.DRAGON, 0, "speedup_dragon_15m"),
            SpeedUpItem("60min_dragon", 3600, SpeedUpType.DRAGON, 0, "speedup_dragon_60m"),
        ]
        
        for item in default_items:
            self.inventory.add_item(item)
    
    def _load_rules(self) -> Dict[SpeedUpTarget, SpeedUpRule]:
        """Load speed-up rules from config"""
        rules = {}
        speedup_config = self.config.get('speedup', {})
        
        # Default rules
        default_strategy = speedup_config.get('default_strategy', 'moderate')
        strategy_map = {
            'never': SpeedUpStrategy.NEVER,
            'free_only': SpeedUpStrategy.FREE_ONLY,
            'conservative': SpeedUpStrategy.CONSERVATIVE,
            'moderate': SpeedUpStrategy.MODERATE,
            'aggressive': SpeedUpStrategy.AGGRESSIVE,
            'always': SpeedUpStrategy.ALWAYS,
        }
        
        default_strat = strategy_map.get(default_strategy.lower(), SpeedUpStrategy.MODERATE)
        
        # Create rules for each target
        for target in SpeedUpTarget:
            target_name = target.name.lower()
            target_config = speedup_config.get(target_name, {})
            
            strategy_name = target_config.get('strategy', default_strategy)
            strategy = strategy_map.get(strategy_name.lower(), default_strat)
            
            rules[target] = SpeedUpRule(
                target=target,
                strategy=strategy,
                min_remaining_seconds=target_config.get('min_remaining_seconds', 0),
                max_remaining_seconds=target_config.get('max_remaining_seconds', 86400),
                use_if_under_minutes=target_config.get('use_if_under_minutes', 5),
                use_percentage=target_config.get('use_percentage', 0.0),
                prefer_specific_items=target_config.get('prefer_specific_items', True),
                use_universal=target_config.get('use_universal', True),
                max_items_per_use=target_config.get('max_items_per_use', 10),
                daily_limit=target_config.get('daily_limit', 0),
            )
        
        return rules
    
    def should_use_speedup(
        self,
        target: SpeedUpTarget,
        remaining_seconds: int
    ) -> Tuple[bool, str]:
        """
        Determine if we should use speed-ups for a target
        
        Args:
            target: What we're speeding up
            remaining_seconds: Time remaining
        
        Returns:
            (should_use, reason)
        """
        rule = self.rules.get(target)
        if not rule:
            return False, "No rule defined"
        
        # Check strategy
        if rule.strategy == SpeedUpStrategy.NEVER:
            return False, "Strategy is NEVER"
        
        # Check thresholds
        if remaining_seconds < rule.min_remaining_seconds:
            return False, f"Below minimum ({rule.min_remaining_seconds}s)"
        
        if remaining_seconds > rule.max_remaining_seconds:
            return False, f"Above maximum ({rule.max_remaining_seconds}s)"
        
        # Check daily limit
        if rule.daily_limit > 0:
            self._check_daily_reset()
            key = f"{target.name}_count"
            current_count = self.daily_usage.get(key, 0)
            if current_count >= rule.daily_limit:
                return False, f"Daily limit reached ({rule.daily_limit})"
        
        # Check available inventory
        available_time = self.inventory.get_total_time_available(target)
        if available_time <= 0:
            # Check for free speed-up
            if self.free_speedup_available.get(target, False):
                return True, "Free speed-up available"
            return False, "No speed-ups available"
        
        # Strategy-specific logic
        if rule.strategy == SpeedUpStrategy.FREE_ONLY:
            if self.free_speedup_available.get(target, False):
                return True, "Free speed-up available"
            return False, "Only using free speed-ups"
        
        elif rule.strategy == SpeedUpStrategy.CONSERVATIVE:
            # Only use if under threshold
            threshold = rule.use_if_under_minutes * 60
            if remaining_seconds <= threshold:
                return True, f"Under {rule.use_if_under_minutes} minutes"
            return False, "Saving speed-ups"
        
        elif rule.strategy == SpeedUpStrategy.MODERATE:
            # Use for longer timers or if almost done
            threshold = rule.use_if_under_minutes * 60
            if remaining_seconds <= threshold:
                return True, f"Under {rule.use_if_under_minutes} minutes - completing"
            
            # Use if timer is very long (over 4 hours)
            if remaining_seconds > 14400:  # 4 hours
                return True, "Long timer - speeding up"
            
            return False, "Timer is manageable"
        
        elif rule.strategy == SpeedUpStrategy.AGGRESSIVE:
            # Use frequently
            return True, "Aggressive strategy - using speed-ups"
        
        elif rule.strategy == SpeedUpStrategy.ALWAYS:
            return True, "Always use speed-ups"
        
        return False, "Unknown strategy"
    
    def calculate_items_needed(
        self,
        target: SpeedUpTarget,
        remaining_seconds: int,
        complete_fully: bool = True
    ) -> List[Tuple[SpeedUpItem, int]]:
        """
        Calculate which items to use for optimal speed-up
        
        Args:
            target: What we're speeding up
            remaining_seconds: Time to reduce
            complete_fully: If True, ensure timer reaches 0
        
        Returns:
            List of (item, quantity) tuples
        """
        items_to_use = []
        time_remaining = remaining_seconds
        
        # Get available items
        available = self.inventory.get_items_for_target(target)
        
        if not available:
            return []
        
        rule = self.rules.get(target)
        max_items = rule.max_items_per_use if rule else 10
        total_items_used = 0
        
        # Sort by duration descending for efficiency (use big ones first)
        available.sort(key=lambda x: x.duration_seconds, reverse=True)
        
        for item in available:
            if time_remaining <= 0:
                break
            
            if total_items_used >= max_items:
                break
            
            if item.quantity <= 0:
                continue
            
            # Calculate how many of this item we need
            items_needed = min(
                (time_remaining + item.duration_seconds - 1) // item.duration_seconds,
                item.quantity,
                max_items - total_items_used
            )
            
            if items_needed > 0:
                items_to_use.append((item, items_needed))
                time_remaining -= items_needed * item.duration_seconds
                total_items_used += items_needed
        
        return items_to_use
    
    def use_speedup(
        self,
        target: SpeedUpTarget,
        remaining_seconds: int
    ) -> bool:
        """
        Use speed-ups on a target
        
        Args:
            target: What to speed up
            remaining_seconds: Current remaining time
        
        Returns:
            True if speed-ups were used
        """
        should_use, reason = self.should_use_speedup(target, remaining_seconds)
        
        if not should_use:
            self.logger.debug(f"Not using speed-up for {target.name}: {reason}")
            return False
        
        self.logger.action(f"Using speed-up for {target.name}: {reason}")
        
        # First try free speed-up
        if self._try_free_speedup(target):
            self.logger.success(f"Used free speed-up on {target.name}")
            self._record_usage(target)
            return True
        
        # Calculate items to use
        items_to_use = self.calculate_items_needed(target, remaining_seconds)
        
        if not items_to_use:
            self.logger.debug("No suitable items to use")
            return False
        
        # Use the items
        success = self._apply_speedup_items(target, items_to_use)
        
        if success:
            # Update inventory
            for item, count in items_to_use:
                self.inventory.use_item(item.name, count)
                self.logger.debug(f"Used {count}x {item.name}")
            
            self._record_usage(target)
        
        return success
    
    def _try_free_speedup(self, target: SpeedUpTarget) -> bool:
        """Try to use a free speed-up if available"""
        # Click on the timer/building
        # Look for free speed-up button
        screen = self.bot.screen.capture()
        if screen is None:
            return False
        
        # Check for free speed-up button
        result = self.bot.matcher.find_template(screen, 'free_speedup_button', threshold=0.8)
        
        if result:
            x, y, _ = result
            self.bot.input.click(x, y)
            time.sleep(1.0)
            
            # Confirm if needed
            self.bot.input.click_coordinate('ui.confirm_button')
            time.sleep(0.5)
            
            return True
        
        return False
    
    def _apply_speedup_items(
        self,
        target: SpeedUpTarget,
        items: List[Tuple[SpeedUpItem, int]]
    ) -> bool:
        """Apply speed-up items through the game UI"""
        # Open speed-up menu
        if not self._open_speedup_menu(target):
            return False
        
        time.sleep(0.5)
        
        for item, count in items:
            # Find the item in the menu
            screen = self.bot.screen.capture()
            if screen is None:
                continue
            
            result = self.bot.matcher.find_template(
                screen, item.template_name, threshold=0.75
            )
            
            if result:
                x, y, _ = result
                
                # Click to select item
                self.bot.input.click(x, y)
                time.sleep(0.3)
                
                # Set quantity if more than 1
                if count > 1:
                    self._set_item_quantity(count)
                
                # Confirm use
                if not self.bot.input.click_coordinate('ui.confirm_button'):
                    # Try finding use button
                    if self._find_and_click('use_button'):
                        time.sleep(0.5)
        
        # Close menu
        self.bot.input.click_coordinate('ui.close_button')
        time.sleep(0.3)
        
        return True
    
    def _open_speedup_menu(self, target: SpeedUpTarget) -> bool:
        """Open the speed-up menu for a target"""
        screen = self.bot.screen.capture()
        if screen is None:
            return False
        
        # Look for speed-up button on current screen
        templates = ['speedup_button', 'boost_button', 'accelerate_button']
        
        for template in templates:
            result = self.bot.matcher.find_template(screen, template)
            if result:
                x, y, _ = result
                self.bot.input.click(x, y)
                time.sleep(1.0)
                return True
        
        return False
    
    def _set_item_quantity(self, count: int):
        """Set the quantity of items to use"""
        # Try to find max button or +/- controls
        screen = self.bot.screen.capture()
        if screen is None:
            return
        
        # Try max button if we want a lot
        if count >= 10:
            result = self.bot.matcher.find_template(screen, 'max_button')
            if result:
                x, y, _ = result
                self.bot.input.click(x, y)
                return
        
        # Otherwise click + button multiple times
        result = self.bot.matcher.find_template(screen, 'plus_button')
        if result:
            x, y, _ = result
            for _ in range(count - 1):  # Already at 1
                self.bot.input.click(x, y)
                time.sleep(0.1)
    
    def _find_and_click(self, template_name: str) -> bool:
        """Find and click a template"""
        screen = self.bot.screen.capture()
        if screen is None:
            return False
        
        result = self.bot.matcher.find_template(screen, template_name)
        if result:
            x, y, _ = result
            self.bot.input.click(x, y)
            return True
        return False
    
    def _record_usage(self, target: SpeedUpTarget):
        """Record speed-up usage for daily tracking"""
        self._check_daily_reset()
        key = f"{target.name}_count"
        self.daily_usage[key] = self.daily_usage.get(key, 0) + 1
    
    def _check_daily_reset(self):
        """Reset daily counters if new day"""
        today = datetime.now().date()
        if self.last_reset_date != today:
            self.daily_usage.clear()
            self.last_reset_date = today
    
    def check_free_speedup(self, target: SpeedUpTarget) -> bool:
        """Check if free speed-up is available for a target"""
        screen = self.bot.screen.capture()
        if screen is None:
            return False
        
        # Look for free speed-up indicator
        result = self.bot.matcher.find_template(screen, 'free_speedup_available')
        available = result is not None
        
        self.free_speedup_available[target] = available
        return available
    
    def update_inventory_from_screen(self):
        """Update inventory by reading from game screen"""
        self.logger.debug("Updating speed-up inventory...")
        
        # This would navigate to inventory and read item counts
        # For now, this is a placeholder
        
        # Navigate to items/inventory
        self.bot.input.click_coordinate('main_screen.inventory')
        time.sleep(1.5)
        
        # Switch to speed-up tab
        if self._find_and_click('speedup_tab'):
            time.sleep(0.5)
        
        # Read item counts (would use OCR)
        # ...
        
        # Close inventory
        self.bot.input.click_coordinate('ui.close_button')
        
        self.inventory.last_updated = datetime.now()
    
    def get_inventory_summary(self) -> str:
        """Get a summary of speed-up inventory"""
        lines = ["=== Speed-Up Inventory ==="]
        
        # Group by type
        by_type: Dict[SpeedUpType, List[SpeedUpItem]] = {}
        for item in self.inventory.items.values():
            if item.quantity > 0:
                if item.item_type not in by_type:
                    by_type[item.item_type] = []
                by_type[item.item_type].append(item)
        
        for item_type, items in by_type.items():
            lines.append(f"\n{item_type.name}:")
            for item in sorted(items, key=lambda x: x.duration_seconds):
                duration = self._format_duration(item.duration_seconds)
                lines.append(f"  {duration}: {item.quantity}x")
        
        # Total time available
        lines.append("\nTotal Time Available:")
        for target in SpeedUpTarget:
            total = self.inventory.get_total_time_available(target)
            if total > 0:
                lines.append(f"  {target.name}: {self._format_duration(total)}")
        
        return "\n".join(lines)
    
    def _format_duration(self, seconds: int) -> str:
        """Format seconds into readable duration"""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m"
        elif seconds < 86400:
            hours = seconds // 3600
            mins = (seconds % 3600) // 60
            return f"{hours}h {mins}m" if mins else f"{hours}h"
        else:
            days = seconds // 86400
            hours = (seconds % 86400) // 3600
            return f"{days}d {hours}h" if hours else f"{days}d"


class DragonSpeedUpManager:
    """
    Specialized speed-up manager for dragon-related timers
    
    Handles:
    - Dragon hatching
    - Dragon upgrades/leveling
    - Dragon skill upgrades
    - Dragon stamina recovery
    """
    
    def __init__(self, speedup_manager: SpeedUpManager):
        self.speedup = speedup_manager
        self.bot = speedup_manager.bot
        self.logger = get_logger()
    
    def speedup_dragon_hatching(self, remaining_seconds: int) -> bool:
        """Speed up dragon egg hatching"""
        return self.speedup.use_speedup(
            SpeedUpTarget.DRAGON_HATCHING,
            remaining_seconds
        )
    
    def speedup_dragon_upgrade(self, remaining_seconds: int) -> bool:
        """Speed up dragon level upgrade"""
        return self.speedup.use_speedup(
            SpeedUpTarget.DRAGON_UPGRADE,
            remaining_seconds
        )
    
    def speedup_dragon_skill(self, remaining_seconds: int) -> bool:
        """Speed up dragon skill upgrade"""
        return self.speedup.use_speedup(
            SpeedUpTarget.DRAGON_SKILL,
            remaining_seconds
        )
    
    def check_dragon_timers(self) -> Dict[str, int]:
        """Check all active dragon timers"""
        timers = {}
        
        # Navigate to dragon lair
        self.bot.input.click_coordinate('buildings.dragon_lair')
        time.sleep(1.5)
        
        # Check for active timers
        screen = self.bot.screen.capture()
        if screen is None:
            return timers
        
        # Look for timer indicators
        timer_templates = [
            ('dragon_hatching_timer', 'hatching'),
            ('dragon_upgrade_timer', 'upgrade'),
            ('dragon_skill_timer', 'skill'),
        ]
        
        for template, timer_type in timer_templates:
            result = self.bot.matcher.find_template(screen, template)
            if result:
                # Would use OCR to read the timer value
                timers[timer_type] = 3600  # Placeholder
        
        # Close dragon lair
        self.bot.input.click_coordinate('ui.close_button')
        
        return timers
    
    def auto_speedup_dragons(self) -> int:
        """
        Automatically speed up all dragon timers
        
        Returns:
            Number of timers sped up
        """
        self.logger.task("Checking dragon timers for speed-up...")
        
        timers = self.check_dragon_timers()
        sped_up = 0
        
        for timer_type, remaining in timers.items():
            target = {
                'hatching': SpeedUpTarget.DRAGON_HATCHING,
                'upgrade': SpeedUpTarget.DRAGON_UPGRADE,
                'skill': SpeedUpTarget.DRAGON_SKILL,
            }.get(timer_type)
            
            if target and self.speedup.use_speedup(target, remaining):
                sped_up += 1
        
        return sped_up
