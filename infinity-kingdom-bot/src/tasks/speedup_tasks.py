"""
Speed-Up Tasks Module
Automatic speed-up management for buildings, research, training, and dragons
"""

import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from src.tasks.base_task import BaseTask
from src.game_state import GameScreen
from src.speedup_manager import (
    SpeedUpManager,
    SpeedUpTarget,
    DragonSpeedUpManager
)


class AutoSpeedUpTask(BaseTask):
    """
    Automatically check and apply speed-ups to all active timers
    
    Checks:
    - Building construction
    - Research/Technology
    - Troop training
    - Hospital healing
    - Dragon timers
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Auto Speed-Up"
        self.description = "Automatically use speed-ups on active timers"
        
        # Initialize speed-up manager
        self.speedup_manager = SpeedUpManager(bot_engine)
        self.dragon_speedup = DragonSpeedUpManager(self.speedup_manager)
        
        # Track what we've sped up
        self.speedups_used = 0
    
    def execute(self) -> bool:
        """Check all timers and apply speed-ups where appropriate"""
        self.logger.task("Checking for timers to speed up...")
        self.speedups_used = 0
        
        # Navigate to main city first
        self.navigate_to_main()
        self.wait(1.0)
        
        # Check each category
        self._check_building_timers()
        self._check_research_timers()
        self._check_training_timers()
        self._check_healing_timers()
        self._check_dragon_timers()
        
        if self.speedups_used > 0:
            self.logger.success(f"Used speed-ups on {self.speedups_used} timers")
        else:
            self.logger.info("No timers needed speed-ups")
        
        return True
    
    def _check_building_timers(self):
        """Check for active building construction"""
        self.logger.debug("Checking building timers...")
        
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Look for construction timer on main screen
        result = self.bot.matcher.find_template(screen, 'building_timer')
        
        if result:
            x, y, _ = result
            self.logger.debug(f"Found building timer at ({x}, {y})")
            
            # Click on the timer
            self.click(x, y)
            self.wait(1.0)
            
            # Read remaining time (would use OCR)
            remaining = self._read_timer_from_screen()
            
            if remaining > 0:
                # Check for free speed-up first
                if self._try_free_speedup():
                    self.speedups_used += 1
                    self.logger.success("Used free building speed-up!")
                elif self.speedup_manager.use_speedup(SpeedUpTarget.BUILDING, remaining):
                    self.speedups_used += 1
            
            self.close_popup()
    
    def _check_research_timers(self):
        """Check for active research"""
        self.logger.debug("Checking research timers...")
        
        # Navigate to academy
        self.click_button('buildings.academy')
        self.wait(1.5)
        
        screen = self.capture_screen()
        if screen is None:
            self.close_popup()
            return
        
        # Look for research timer
        result = self.bot.matcher.find_template(screen, 'research_timer')
        
        if result:
            x, y, _ = result
            self.click(x, y)
            self.wait(1.0)
            
            remaining = self._read_timer_from_screen()
            
            if remaining > 0:
                if self._try_free_speedup():
                    self.speedups_used += 1
                    self.logger.success("Used free research speed-up!")
                elif self.speedup_manager.use_speedup(SpeedUpTarget.RESEARCH, remaining):
                    self.speedups_used += 1
            
            self.close_popup()
        
        self.close_popup()  # Close academy
    
    def _check_training_timers(self):
        """Check for active troop training"""
        self.logger.debug("Checking training timers...")
        
        # Navigate to barracks
        self.click_button('buildings.barracks')
        self.wait(1.5)
        
        screen = self.capture_screen()
        if screen is None:
            self.close_popup()
            return
        
        # Look for training timer
        result = self.bot.matcher.find_template(screen, 'training_timer')
        
        if result:
            x, y, _ = result
            self.click(x, y)
            self.wait(1.0)
            
            remaining = self._read_timer_from_screen()
            
            if remaining > 0:
                if self._try_free_speedup():
                    self.speedups_used += 1
                    self.logger.success("Used free training speed-up!")
                elif self.speedup_manager.use_speedup(SpeedUpTarget.TRAINING, remaining):
                    self.speedups_used += 1
            
            self.close_popup()
        
        self.close_popup()  # Close barracks
    
    def _check_healing_timers(self):
        """Check for active hospital healing"""
        self.logger.debug("Checking healing timers...")
        
        # Navigate to hospital
        self.click_button('buildings.hospital')
        self.wait(1.5)
        
        screen = self.capture_screen()
        if screen is None:
            self.close_popup()
            return
        
        # Look for healing timer
        result = self.bot.matcher.find_template(screen, 'healing_timer')
        
        if result:
            x, y, _ = result
            self.click(x, y)
            self.wait(1.0)
            
            remaining = self._read_timer_from_screen()
            
            if remaining > 0:
                if self._try_free_speedup():
                    self.speedups_used += 1
                    self.logger.success("Used free healing speed-up!")
                elif self.speedup_manager.use_speedup(SpeedUpTarget.HEALING, remaining):
                    self.speedups_used += 1
            
            self.close_popup()
        
        self.close_popup()  # Close hospital
    
    def _check_dragon_timers(self):
        """Check all dragon-related timers"""
        self.logger.debug("Checking dragon timers...")
        
        count = self.dragon_speedup.auto_speedup_dragons()
        self.speedups_used += count
    
    def _try_free_speedup(self) -> bool:
        """Try to use free speed-up button"""
        screen = self.capture_screen()
        if screen is None:
            return False
        
        # Look for free speed-up button
        free_buttons = [
            'free_speedup_button',
            'free_complete_button',
            'instant_free_button',
            'help_speedup_button',  # Alliance help speed-up
        ]
        
        for template in free_buttons:
            result = self.bot.matcher.find_template(screen, template, threshold=0.8)
            if result:
                x, y, _ = result
                self.click(x, y)
                self.wait(1.0)
                
                # Confirm if needed
                self.find_and_click('confirm_button')
                self.wait(0.5)
                
                return True
        
        return False
    
    def _read_timer_from_screen(self) -> int:
        """
        Read timer value from current screen
        
        Returns:
            Remaining seconds or 0 if not found
        """
        screen = self.capture_screen()
        if screen is None:
            return 0
        
        # Look for timer display
        # This would use OCR to read the actual value
        # For now, return a placeholder
        
        # Try to find timer text region
        result = self.bot.matcher.find_template(screen, 'timer_display')
        
        if result:
            x, y, _ = result
            # Crop region around timer
            # Use OCR to read
            # Parse time format (HH:MM:SS or similar)
            
            # Placeholder - would implement actual OCR
            return 3600  # 1 hour default
        
        return 0


class DragonManagementTask(BaseTask):
    """
    Manage dragon upgrades, skills, and hatching
    with automatic speed-up support
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Dragon Management"
        self.description = "Manage dragons with auto speed-up"
        
        # Initialize speed-up managers
        self.speedup_manager = SpeedUpManager(bot_engine)
        self.dragon_speedup = DragonSpeedUpManager(self.speedup_manager)
    
    def execute(self) -> bool:
        """Manage all dragon-related activities"""
        self.logger.task("Managing dragons...")
        
        # Navigate to dragon lair
        if not self._open_dragon_lair():
            return False
        
        # Check for eggs to hatch
        self._check_dragon_eggs()
        
        # Check for upgrades available
        self._check_dragon_upgrades()
        
        # Check for skill upgrades
        self._check_dragon_skills()
        
        # Apply speed-ups to active timers
        self.dragon_speedup.auto_speedup_dragons()
        
        # Close dragon lair
        self.close_popup()
        
        return True
    
    def _open_dragon_lair(self) -> bool:
        """Navigate to dragon lair"""
        self.navigate_to_main()
        self.wait(1.0)
        
        # Click on dragon lair
        self.click_button('buildings.dragon_lair')
        self.wait(2.0)
        
        # Verify we're in dragon lair
        screen = self.capture_screen()
        if screen is None:
            return False
        
        result = self.bot.matcher.find_template(screen, 'dragon_lair_header')
        return result is not None
    
    def _check_dragon_eggs(self):
        """Check for eggs ready to hatch or being incubated"""
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Look for egg slot
        result = self.bot.matcher.find_template(screen, 'dragon_egg_slot')
        
        if result:
            x, y, _ = result
            self.click(x, y)
            self.wait(1.0)
            
            screen = self.capture_screen()
            if screen is None:
                return
            
            # Check if ready to hatch
            if self.bot.matcher.find_template(screen, 'hatch_button'):
                self.find_and_click('hatch_button')
                self.wait(2.0)
                self.logger.success("Hatched a dragon egg!")
            
            # Check for timer to speed up
            elif self.bot.matcher.find_template(screen, 'egg_timer'):
                remaining = self._read_timer()
                if remaining > 0:
                    self.dragon_speedup.speedup_dragon_hatching(remaining)
            
            self.close_popup()
    
    def _check_dragon_upgrades(self):
        """Check for dragon level upgrades"""
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Look for dragon that can be upgraded
        result = self.bot.matcher.find_template(screen, 'dragon_upgrade_available')
        
        if result:
            x, y, _ = result
            self.click(x, y)
            self.wait(1.0)
            
            # Start upgrade
            if self.find_and_click('upgrade_dragon_button'):
                self.wait(1.5)
                self.logger.action("Started dragon upgrade")
                
                # Try to speed up
                remaining = self._read_timer()
                if remaining > 0:
                    self.dragon_speedup.speedup_dragon_upgrade(remaining)
            
            self.close_popup()
    
    def _check_dragon_skills(self):
        """Check for dragon skill upgrades"""
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Look for skill upgrade indicator
        result = self.bot.matcher.find_template(screen, 'dragon_skill_available')
        
        if result:
            x, y, _ = result
            self.click(x, y)
            self.wait(1.0)
            
            # Upgrade skill
            if self.find_and_click('upgrade_skill_button'):
                self.wait(1.5)
                self.logger.action("Started dragon skill upgrade")
                
                # Try to speed up
                remaining = self._read_timer()
                if remaining > 0:
                    self.dragon_speedup.speedup_dragon_skill(remaining)
            
            self.close_popup()
    
    def _read_timer(self) -> int:
        """Read timer from current screen"""
        # Would use OCR - placeholder
        return 3600


class SpeedUpInventoryTask(BaseTask):
    """
    Update speed-up inventory by reading from game
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Update Speed-Up Inventory"
        self.description = "Scan and update speed-up item counts"
        
        self.speedup_manager = SpeedUpManager(bot_engine)
    
    def execute(self) -> bool:
        """Scan inventory for speed-up items"""
        self.logger.task("Updating speed-up inventory...")
        
        # Navigate to inventory
        self.click_button('main_screen.inventory')
        self.wait(1.5)
        
        # Switch to consumables/items tab
        if self.find_and_click('items_tab'):
            self.wait(0.5)
        
        # Look for speed-up items and count them
        self._scan_speedup_items()
        
        # Close inventory
        self.close_popup()
        
        # Log summary
        self.logger.info(self.speedup_manager.get_inventory_summary())
        
        return True
    
    def _scan_speedup_items(self):
        """Scan visible speed-up items"""
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Template names for speed-up items
        speedup_templates = [
            ('speedup_1m', '1min_universal'),
            ('speedup_5m', '5min_universal'),
            ('speedup_15m', '15min_universal'),
            ('speedup_60m', '60min_universal'),
            ('speedup_3h', '3hour_universal'),
            ('speedup_8h', '8hour_universal'),
            ('speedup_24h', '24hour_universal'),
            ('speedup_build_1m', '1min_building'),
            ('speedup_build_5m', '5min_building'),
            ('speedup_research_1m', '1min_research'),
            ('speedup_research_5m', '5min_research'),
            ('speedup_dragon_1m', '1min_dragon'),
            ('speedup_dragon_5m', '5min_dragon'),
        ]
        
        for template_name, item_name in speedup_templates:
            result = self.bot.matcher.find_template(screen, template_name)
            
            if result:
                x, y, _ = result
                
                # Click to see quantity
                self.click(x, y)
                self.wait(0.5)
                
                # Read quantity (would use OCR)
                quantity = self._read_quantity()
                
                if quantity > 0:
                    # Update inventory
                    if item_name in self.speedup_manager.inventory.items:
                        self.speedup_manager.inventory.items[item_name].quantity = quantity
                        self.logger.debug(f"Found {quantity}x {item_name}")
                
                self.close_popup()
                self.wait(0.3)
    
    def _read_quantity(self) -> int:
        """Read item quantity from popup"""
        # Would use OCR - placeholder
        return 10
