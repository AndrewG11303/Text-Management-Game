"""
Building Tasks Module
Handles building upgrades, troop training, and research
"""

import time
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from src.tasks.base_task import BaseTask
from src.game_state import GameScreen


class BuildingUpgradeTask(BaseTask):
    """
    Manage building upgrades
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Building Upgrade"
        self.description = "Check and start building upgrades"
        
        # Priority order for upgrades
        self.upgrade_priority = [
            'castle',           # Main building - unlocks others
            'barracks',         # Troop training
            'academy',          # Research
            'hospital',         # Troop healing
            'wall',             # Defense
            'watchtower',       # Intel
            'farm_1',           # Resources
            'lumber_mill_1',
            'iron_mine_1',
            'stone_quarry_1',
        ]
    
    def execute(self) -> bool:
        """Check for available upgrades and start one"""
        self.logger.task("Checking building upgrades...")
        
        # Check if builder is available
        if not self._is_builder_available():
            self.logger.info("No builder available")
            return True
        
        # Find a building to upgrade
        for building_name in self.upgrade_priority:
            if self._can_upgrade_building(building_name):
                if self._start_upgrade(building_name):
                    self.logger.task(f"Started upgrade for {building_name}")
                    return True
        
        self.logger.info("No buildings ready for upgrade")
        return True
    
    def _is_builder_available(self) -> bool:
        """Check if a builder is free"""
        # Look for builder indicator on screen
        screen = self.capture_screen()
        if screen is None:
            return False
        
        # Check for "builder available" indicator
        result = self.bot.matcher.find_template(screen, 'builder_available')
        return result is not None
    
    def _can_upgrade_building(self, building_name: str) -> bool:
        """Check if a specific building can be upgraded"""
        # Click on the building
        self.click_button(f'buildings.{building_name}')
        self.wait(1.0)
        
        # Look for upgrade button (not greyed out)
        screen = self.capture_screen()
        if screen is None:
            self.close_popup()
            return False
        
        # Check for active upgrade button
        result = self.bot.matcher.find_template(
            screen, 'upgrade_button_active', threshold=0.8
        )
        
        self.close_popup()
        return result is not None
    
    def _start_upgrade(self, building_name: str) -> bool:
        """Start upgrading a building"""
        self.logger.action(f"Starting upgrade for {building_name}")
        
        # Click on building
        self.click_button(f'buildings.{building_name}')
        self.wait(1.0)
        
        # Click upgrade button
        if not self.find_and_click('upgrade_button'):
            self.close_popup()
            return False
        
        self.wait(1.0)
        
        # Check for free speed up
        if self.find_and_click('free_speedup_button'):
            self.logger.task("Used free speed up!")
            self.wait(0.5)
        
        # Confirm upgrade
        if self.find_and_click('confirm_button'):
            self.wait(1.5)
            
            # Update game state
            building = self.bot.state.buildings.get(building_name)
            if building:
                self.bot.state.start_building_upgrade(
                    building_name,
                    duration_seconds=3600  # Estimate, would read from screen
                )
            
            self.close_popup()
            return True
        
        self.close_popup()
        return False
    
    def _use_speedup(self, building_name: str):
        """Use speed up items on a building"""
        # This would select and use speed up items
        pass


class TrainTroopsTask(BaseTask):
    """
    Automatically train troops in barracks
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Train Troops"
        self.description = "Train troops in barracks"
        
        # Configuration
        training_config = bot_engine.config.get('tasks', {}).get('training', {})
        self.troop_type = training_config.get('troop_type', 'cavalry')
        self.batch_size = training_config.get('batch_size', 100)
        self.auto_queue = training_config.get('auto_queue', True)
        
        # Troop type templates
        self.troop_templates = {
            'infantry': 'troop_infantry',
            'cavalry': 'troop_cavalry',
            'archer': 'troop_archer',
            'mage': 'troop_mage',
        }
    
    def execute(self) -> bool:
        """Train troops"""
        self.logger.task("Checking troop training...")
        
        # Navigate to barracks
        self.click_button('buildings.barracks')
        self.wait(1.5, "Opening barracks")
        
        # Check queue status
        queue_full = self._is_queue_full()
        
        if queue_full:
            self.logger.info("Training queue is full")
            self.close_popup()
            return True
        
        # Select troop type
        if not self._select_troop_type():
            self.close_popup()
            return False
        
        # Start training
        success = self._start_training()
        
        self.close_popup()
        
        if success:
            self.bot.state.increment_stat('troops_trained', self.batch_size)
        
        return success
    
    def _is_queue_full(self) -> bool:
        """Check if training queue is full"""
        screen = self.capture_screen()
        if screen is None:
            return True
        
        # Look for "queue full" indicator
        result = self.bot.matcher.find_template(screen, 'queue_full')
        return result is not None
    
    def _select_troop_type(self) -> bool:
        """Select the troop type to train"""
        template = self.troop_templates.get(self.troop_type)
        if not template:
            return False
        
        return self.find_and_click(template)
    
    def _start_training(self) -> bool:
        """Start training the selected troop type"""
        self.wait(0.5)
        
        # Set quantity
        self._set_training_quantity()
        
        # Click train button
        if self.find_and_click('train_button'):
            self.logger.task(f"Training {self.batch_size} {self.troop_type}")
            self.wait(1.0)
            return True
        
        return False
    
    def _set_training_quantity(self):
        """Set the number of troops to train"""
        # Try clicking max button
        if self.find_and_click('max_quantity_button'):
            return
        
        # Or use slider/input
        # This would need more sophisticated handling


class ResearchTask(BaseTask):
    """
    Manage academy research
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Research"
        self.description = "Manage academy research"
        
        # Research priority categories
        self.research_priority = [
            'military',     # Combat bonuses
            'economy',      # Resource production
            'development',  # Building/training speed
            'defense',      # Defensive bonuses
        ]
    
    def execute(self) -> bool:
        """Check and start research"""
        self.logger.task("Checking research...")
        
        # Navigate to academy
        self.click_button('buildings.academy')
        self.wait(1.5, "Opening academy")
        
        # Check if research slot is available
        if not self._is_research_available():
            self.logger.info("Research slot is busy")
            self.close_popup()
            return True
        
        # Find research to start
        for category in self.research_priority:
            if self._start_research_in_category(category):
                self.logger.task(f"Started research in {category}")
                self.close_popup()
                return True
        
        self.logger.info("No research available")
        self.close_popup()
        return True
    
    def _is_research_available(self) -> bool:
        """Check if research can be started"""
        screen = self.capture_screen()
        if screen is None:
            return False
        
        # Check for busy indicator
        result = self.bot.matcher.find_template(screen, 'research_busy')
        return result is None
    
    def _start_research_in_category(self, category: str) -> bool:
        """Start research in a specific category"""
        # Click on category tab
        if self.find_and_click(f'research_{category}_tab'):
            self.wait(1.0)
            
            # Find available research
            screen = self.capture_screen()
            if screen is None:
                return False
            
            # Look for researchable item (not locked, not maxed)
            result = self.bot.matcher.find_template(
                screen, 'research_available', threshold=0.75
            )
            
            if result:
                x, y, _ = result
                self.click(x, y)
                self.wait(1.0)
                
                # Click research button
                if self.find_and_click('start_research_button'):
                    self.wait(1.0)
                    
                    # Check for free speedup
                    if self.find_and_click('free_speedup_button'):
                        self.wait(0.5)
                    
                    return True
        
        return False


class QueueManager:
    """
    Utility class to manage building/training/research queues
    """
    
    def __init__(self, game_state):
        self.state = game_state
    
    def get_building_queue_time(self) -> timedelta:
        """Get remaining time for building queue"""
        total = timedelta(0)
        
        for item in self.state.building_queue:
            if item.end_time:
                remaining = item.end_time - datetime.now()
                if remaining.total_seconds() > 0:
                    total += remaining
        
        return total
    
    def get_training_queue_time(self) -> timedelta:
        """Get remaining time for training queue"""
        total = timedelta(0)
        
        for item in self.state.training_queue:
            if item.end_time:
                remaining = item.end_time - datetime.now()
                if remaining.total_seconds() > 0:
                    total += remaining
        
        return total
    
    def can_add_to_queue(self, queue_type: str, max_queue: int = 2) -> bool:
        """Check if more items can be added to a queue"""
        if queue_type == 'building':
            return len(self.state.building_queue) < max_queue
        elif queue_type == 'training':
            return len(self.state.training_queue) < max_queue
        elif queue_type == 'research':
            return len(self.state.research_queue) < max_queue
        return False


class SpeedUpManager:
    """
    Manage speed up item usage
    """
    
    def __init__(self, bot_engine):
        self.bot = bot_engine
        self.logger = bot_engine.logger
    
    def use_speedup(
        self,
        target_type: str,
        duration_minutes: int = None,
        use_gems: bool = False
    ) -> bool:
        """
        Use speed up items on a target
        
        Args:
            target_type: 'building', 'training', 'research', 'healing'
            duration_minutes: Minutes to speed up (None = complete)
            use_gems: Whether to use gems if items insufficient
        
        Returns:
            True if speed up was applied
        """
        # This would implement speed up logic
        return False
    
    def calculate_speedup_cost(self, duration_seconds: int) -> Dict[str, int]:
        """
        Calculate items/gems needed to speed up
        
        Returns:
            Dict with item counts needed
        """
        minutes = duration_seconds / 60
        
        # Simplified calculation
        return {
            '1_min': 0,
            '5_min': 0,
            '15_min': 0,
            '60_min': int(minutes / 60),
            'gems': int(minutes * 2)  # Example gem cost
        }
