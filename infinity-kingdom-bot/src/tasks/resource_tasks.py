"""
Resource Collection Tasks
Handles resource gathering and collection
"""

import time
from typing import List, Optional, Tuple
from datetime import datetime

from src.tasks.base_task import BaseTask
from src.game_state import GameScreen, MarchStatus


class CollectResourcesTask(BaseTask):
    """
    Collect resources from production buildings
    (Farms, Lumber Mills, Iron Mines, etc.)
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Collect Resources"
        self.description = "Collect resources from all production buildings"
        
        # Buildings to collect from
        self.resource_buildings = [
            'buildings.farm_1',
            'buildings.farm_2',
            'buildings.lumber_mill_1',
            'buildings.lumber_mill_2',
            'buildings.iron_mine_1',
            'buildings.stone_quarry_1',
        ]
    
    def execute(self) -> bool:
        """Collect from all resource buildings"""
        self.logger.resource("Starting resource collection...")
        
        collected_count = 0
        
        # Make sure we're on the main city screen
        self.navigate_to_main()
        self.wait(1.0, "Loading main screen")
        
        # Method 1: Try to find and click "Collect All" button if available
        if self.find_and_click('collect_all_button'):
            self.logger.resource("Used Collect All button")
            self.wait(2.0, "Collecting all resources")
            return True
        
        # Method 2: Click on each building individually
        for building in self.resource_buildings:
            try:
                self.logger.debug(f"Collecting from {building}")
                
                # Click on the building
                self.click_button(building)
                self.wait(0.8, "Opening building")
                
                # Look for collect button
                if self.find_and_click('collect_button', threshold=0.7):
                    collected_count += 1
                    self.wait(0.5)
                
                # Close the building menu
                self.close_popup()
                self.wait(0.3)
                
            except Exception as e:
                self.logger.debug(f"Could not collect from {building}: {e}")
        
        self.logger.resource(f"Collected from {collected_count} buildings")
        
        # Update stats
        self.bot.state.increment_stat('tasks_completed')
        
        return collected_count > 0
    
    def can_run(self) -> bool:
        """Check if we can run collection"""
        # Don't run if we're in battle
        if self.bot.state.is_in_battle:
            return False
        
        return True


class GatherResourcesTask(BaseTask):
    """
    Send troops to gather resources on the world map
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Gather Resources"
        self.description = "Send marches to gather resources on world map"
        
        # Configuration
        self.config = bot_engine.config.get('tasks', {}).get('gathering', {})
        self.priority = self.config.get('priority', ['gold', 'food', 'wood', 'iron'])
        self.max_marches = self.config.get('max_marches', 3)
        self.min_troops = self.config.get('min_troops', 10000)
        
        # Resource tile types and their template names
        self.resource_templates = {
            'gold': 'tile_gold',
            'food': 'tile_food',
            'wood': 'tile_wood',
            'iron': 'tile_iron',
            'gems': 'tile_gems',
        }
    
    def execute(self) -> bool:
        """Find and send troops to gather resources"""
        self.logger.resource("Starting resource gathering...")
        
        # Check available marches
        available_marches = self.bot.state.get_available_marches()
        
        if not available_marches:
            self.logger.info("No available march slots")
            return True  # Not a failure, just nothing to do
        
        marches_sent = 0
        
        # Navigate to world map
        if not self._navigate_to_world_map():
            self.logger.warning("Could not navigate to world map")
            return False
        
        # Send marches based on priority
        for resource_type in self.priority:
            if marches_sent >= len(available_marches):
                break
            
            if marches_sent >= self.max_marches:
                break
            
            # Try to find a resource tile
            tile_pos = self._find_resource_tile(resource_type)
            
            if tile_pos:
                march = available_marches[marches_sent]
                
                if self._send_gather_march(tile_pos, march.march_id, resource_type):
                    marches_sent += 1
                    self.wait(2.0, "March sent, waiting before next")
        
        # Return to city
        self._return_to_city()
        
        self.logger.resource(f"Sent {marches_sent} gathering marches")
        return marches_sent > 0 or len(available_marches) == 0
    
    def _navigate_to_world_map(self) -> bool:
        """Navigate to the world map"""
        self.logger.debug("Navigating to world map")
        
        # Click world map button
        self.click_button('main_screen.world_map')
        self.wait(2.0, "Loading world map")
        
        # Verify we're on world map
        self.bot.state.set_screen(GameScreen.WORLD_MAP)
        return True
    
    def _return_to_city(self) -> bool:
        """Return to city view"""
        self.logger.debug("Returning to city")
        
        # Click castle button to return
        self.click_button('main_screen.castle')
        self.wait(2.0, "Loading city")
        
        self.bot.state.set_screen(GameScreen.MAIN_CITY)
        return True
    
    def _find_resource_tile(self, resource_type: str) -> Optional[Tuple[int, int]]:
        """
        Search for a resource tile on the map
        
        Args:
            resource_type: Type of resource to find
        
        Returns:
            (x, y) coordinates of tile or None
        """
        template_name = self.resource_templates.get(resource_type)
        if not template_name:
            return None
        
        # Search visible map area
        screen = self.capture_screen()
        if screen is None:
            return None
        
        # Try to find resource tile
        result = self.bot.matcher.find_template(screen, template_name, threshold=0.75)
        
        if result:
            x, y, confidence = result
            self.logger.debug(f"Found {resource_type} tile at ({x}, {y})")
            return (x, y)
        
        # If not found, try scrolling the map
        for direction in ['up', 'down', 'left', 'right']:
            self._scroll_map(direction)
            self.wait(1.0)
            
            screen = self.capture_screen()
            if screen is not None:
                result = self.bot.matcher.find_template(screen, template_name, threshold=0.75)
                if result:
                    x, y, confidence = result
                    return (x, y)
        
        return None
    
    def _scroll_map(self, direction: str):
        """Scroll the map in a direction"""
        screen_width = self.bot.config['device']['resolution']['width']
        screen_height = self.bot.config['device']['resolution']['height']
        
        center_x = screen_width // 2
        center_y = screen_height // 2
        
        scroll_distance = 200
        
        if direction == 'up':
            self.bot.input.swipe(center_x, center_y, center_x, center_y + scroll_distance)
        elif direction == 'down':
            self.bot.input.swipe(center_x, center_y, center_x, center_y - scroll_distance)
        elif direction == 'left':
            self.bot.input.swipe(center_x, center_y, center_x + scroll_distance, center_y)
        elif direction == 'right':
            self.bot.input.swipe(center_x, center_y, center_x - scroll_distance, center_y)
    
    def _send_gather_march(
        self,
        tile_pos: Tuple[int, int],
        march_id: int,
        resource_type: str
    ) -> bool:
        """
        Send a march to gather at a tile
        
        Args:
            tile_pos: (x, y) position of tile
            march_id: ID of march slot to use
            resource_type: Type of resource being gathered
        
        Returns:
            True if march was sent successfully
        """
        self.logger.action(f"Sending march {march_id} to gather {resource_type}")
        
        # Click on the tile
        self.click(tile_pos[0], tile_pos[1])
        self.wait(1.0, "Tile menu opening")
        
        # Look for gather button
        if not self.find_and_click('gather_button'):
            self.logger.debug("Gather button not found")
            self.close_popup()
            return False
        
        self.wait(1.0, "Troop selection")
        
        # Select troops (use max)
        if self.find_and_click('max_troops_button'):
            self.wait(0.5)
        
        # Click march/send button
        if not self.find_and_click('march_button'):
            self.logger.debug("March button not found")
            self.close_popup()
            return False
        
        self.wait(1.5, "March sent")
        
        # Update game state
        self.bot.state.start_march(
            march_id=march_id,
            status=MarchStatus.GATHERING,
            target=f"{resource_type}_tile",
            troops=self.min_troops,
            duration_seconds=3600  # Estimated 1 hour
        )
        
        return True
    
    def can_run(self) -> bool:
        """Check if we can send gathering marches"""
        # Need available march slots
        available = self.bot.state.get_available_marches()
        if not available:
            return False
        
        # Don't gather if under attack
        if self.bot.state.is_under_attack:
            return False
        
        return True


class ResourceCalculator:
    """
    Utility class for resource calculations
    """
    
    @staticmethod
    def calculate_gather_time(
        resource_amount: int,
        gather_speed: float,
        troop_load: int,
        troop_count: int
    ) -> int:
        """
        Calculate time to gather resources
        
        Args:
            resource_amount: Amount to gather
            gather_speed: Gathering speed multiplier
            troop_load: Load capacity per troop
            troop_count: Number of troops
        
        Returns:
            Time in seconds
        """
        # Max gatherable based on troop capacity
        max_gather = troop_load * troop_count
        actual_gather = min(resource_amount, max_gather)
        
        # Base gather rate (resources per hour per troop)
        base_rate = 1000  # Example base rate
        
        hourly_rate = base_rate * troop_count * gather_speed
        
        if hourly_rate > 0:
            hours = actual_gather / hourly_rate
            return int(hours * 3600)
        
        return 3600  # Default 1 hour
    
    @staticmethod
    def calculate_resource_production(
        building_level: int,
        production_boost: float = 1.0
    ) -> int:
        """
        Calculate hourly resource production
        
        Args:
            building_level: Level of production building
            production_boost: Production boost multiplier
        
        Returns:
            Resources per hour
        """
        # Example formula - adjust based on actual game
        base_production = 100
        level_multiplier = building_level * 1.5
        
        return int(base_production * level_multiplier * production_boost)
    
    @staticmethod
    def resources_needed_for_upgrade(
        building_name: str,
        current_level: int
    ) -> dict:
        """
        Calculate resources needed for building upgrade
        
        Returns:
            Dict with resource requirements
        """
        # Example costs - would need actual game data
        base_costs = {
            'gold': 1000,
            'food': 500,
            'wood': 500,
            'iron': 200
        }
        
        level_multiplier = current_level ** 1.8
        
        return {
            resource: int(cost * level_multiplier)
            for resource, cost in base_costs.items()
        }
