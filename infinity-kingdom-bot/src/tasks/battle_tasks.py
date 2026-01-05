"""
Battle Tasks Module
Handles combat-related automation
"""

import time
import random
from typing import List, Optional, Tuple
from datetime import datetime

from src.tasks.base_task import BaseTask
from src.game_state import GameScreen, MarchStatus


class AttackGnomesTask(BaseTask):
    """
    Auto-attack gnomes (PvE enemies) on the world map
    Good for leveling up and getting rewards
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Attack Gnomes"
        self.description = "Find and attack gnomes on the world map"
        
        # Configuration
        battle_config = bot_engine.config.get('tasks', {}).get('battle', {})
        self.max_gnome_level = battle_config.get('max_gnome_level', 10)
        self.auto_heal = battle_config.get('auto_heal', True)
        self.min_army_power = battle_config.get('min_army_power', 50000)
        
        # Gnome level templates
        self.gnome_templates = [f'gnome_level_{i}' for i in range(1, 21)]
    
    def execute(self) -> bool:
        """Find and attack gnomes"""
        self.logger.battle("Starting gnome hunt...")
        
        # Check if we have available marches
        available_marches = self.bot.state.get_available_marches()
        
        if not available_marches:
            self.logger.info("No available march slots for gnome hunting")
            return True
        
        # Navigate to world map
        self._navigate_to_world_map()
        
        # Find a gnome to attack
        gnome_pos = self._find_gnome()
        
        if not gnome_pos:
            self.logger.info("No suitable gnomes found nearby")
            self._return_to_city()
            return True
        
        # Attack the gnome
        march = available_marches[0]
        success = self._attack_gnome(gnome_pos, march.march_id)
        
        # Return to city
        self._return_to_city()
        
        if success:
            self.bot.state.increment_stat('battles_won')
        
        return success
    
    def _navigate_to_world_map(self) -> bool:
        """Navigate to world map"""
        self.click_button('main_screen.world_map')
        self.wait(2.0, "Loading world map")
        self.bot.state.set_screen(GameScreen.WORLD_MAP)
        return True
    
    def _return_to_city(self) -> bool:
        """Return to city"""
        self.click_button('main_screen.castle')
        self.wait(2.0, "Loading city")
        self.bot.state.set_screen(GameScreen.MAIN_CITY)
        return True
    
    def _find_gnome(self) -> Optional[Tuple[int, int]]:
        """
        Search for a gnome within acceptable level range
        
        Returns:
            (x, y) position of gnome or None
        """
        screen = self.capture_screen()
        if screen is None:
            return None
        
        # Search for gnomes by level (highest first, but within limit)
        for level in range(self.max_gnome_level, 0, -1):
            template_name = f'gnome_level_{level}'
            result = self.bot.matcher.find_template(screen, template_name, threshold=0.75)
            
            if result:
                x, y, confidence = result
                self.logger.debug(f"Found level {level} gnome at ({x}, {y})")
                return (x, y)
        
        # Also try generic gnome template
        result = self.bot.matcher.find_template(screen, 'gnome_generic', threshold=0.7)
        if result:
            x, y, confidence = result
            return (x, y)
        
        return None
    
    def _attack_gnome(self, gnome_pos: Tuple[int, int], march_id: int) -> bool:
        """
        Execute attack on a gnome
        
        Args:
            gnome_pos: Position of gnome
            march_id: March slot to use
        
        Returns:
            True if attack was initiated successfully
        """
        self.logger.battle(f"Attacking gnome at {gnome_pos}")
        
        # Click on gnome
        self.click(gnome_pos[0], gnome_pos[1])
        self.wait(1.0, "Gnome menu opening")
        
        # Click attack button
        if not self.find_and_click('attack_button'):
            self.logger.debug("Attack button not found")
            self.close_popup()
            return False
        
        self.wait(1.0, "Troop selection")
        
        # Select immortals/heroes for battle
        self._select_immortals()
        
        # Select troops
        if self.find_and_click('max_troops_button'):
            self.wait(0.5)
        
        # Start march
        if not self.find_and_click('march_button'):
            self.logger.debug("March button not found")
            self.close_popup()
            return False
        
        self.wait(1.5, "March starting")
        
        # Update state
        self.bot.state.start_march(
            march_id=march_id,
            status=MarchStatus.ATTACKING,
            target="gnome",
            troops=10000,
            duration_seconds=60  # Gnome attacks are usually quick
        )
        
        self.logger.battle("Attack march sent!")
        return True
    
    def _select_immortals(self):
        """Select immortals for battle"""
        # Click on immortal slots to select best heroes
        immortal_slots = [
            'battle.immortal_slots.slot_1',
            'battle.immortal_slots.slot_2',
            'battle.immortal_slots.slot_3',
        ]
        
        for slot in immortal_slots:
            self.click_button(slot)
            self.wait(0.3)
    
    def can_run(self) -> bool:
        """Check if we can hunt gnomes"""
        # Need available march
        if not self.bot.state.get_available_marches():
            return False
        
        # Don't hunt if under attack
        if self.bot.state.is_under_attack:
            return False
        
        # Check cooldown
        if self.bot.state.is_on_cooldown('gnome_hunt'):
            return False
        
        return True


class AutoBattleTask(BaseTask):
    """
    Automatic battle handling
    Manages ongoing battles and retreats if needed
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Auto Battle"
        self.description = "Monitor and manage active battles"
        
        # Configuration
        battle_config = bot_engine.config.get('tasks', {}).get('battle', {})
        self.target_types = battle_config.get('target_types', ['gnome', 'rebel'])
        self.auto_heal = battle_config.get('auto_heal', True)
    
    def execute(self) -> bool:
        """Check and manage active battles"""
        self.logger.battle("Checking active battles...")
        
        # Get active marches
        active_marches = self.bot.state.get_active_marches()
        
        battles_managed = 0
        
        for march in active_marches:
            if march.status == MarchStatus.ATTACKING:
                self._manage_battle(march)
                battles_managed += 1
        
        # Check for battle results
        self._check_battle_results()
        
        # Auto heal if enabled
        if self.auto_heal:
            self._heal_troops()
        
        return True
    
    def _manage_battle(self, march):
        """Monitor a specific battle"""
        remaining = march.time_remaining()
        
        if remaining:
            self.logger.debug(
                f"March {march.march_id}: {remaining.total_seconds():.0f}s remaining"
            )
        else:
            # Battle should be complete
            self.bot.state.complete_march(march.march_id)
    
    def _check_battle_results(self):
        """Check for battle result notifications"""
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Look for victory screen
        if self.bot.matcher.find_template(screen, 'victory_screen'):
            self.logger.battle("Victory!")
            self.bot.state.increment_stat('battles_won')
            self.close_popup()
            return
        
        # Look for defeat screen
        if self.bot.matcher.find_template(screen, 'defeat_screen'):
            self.logger.battle("Defeat!")
            self.bot.state.increment_stat('battles_lost')
            self.close_popup()
            return
    
    def _heal_troops(self):
        """Heal injured troops in hospital"""
        # Navigate to hospital if needed
        self.click_button('buildings.hospital')
        self.wait(1.0, "Opening hospital")
        
        # Check for wounded troops
        screen = self.capture_screen()
        if screen is None:
            return
        
        # Look for heal button
        if self.find_and_click('heal_all_button'):
            self.logger.battle("Healing troops...")
            self.wait(1.0)
        
        # Close hospital
        self.close_popup()
    
    def can_run(self) -> bool:
        """Always can check battles"""
        return True


class RallyTask(BaseTask):
    """
    Join or create alliance rallies
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Rally Task"
        self.description = "Join alliance rallies"
    
    def execute(self) -> bool:
        """Check and join available rallies"""
        self.logger.battle("Checking for alliance rallies...")
        
        # Navigate to alliance war screen
        self.click_button('main_screen.alliance')
        self.wait(1.5)
        
        # Look for rally button
        if self.find_and_click('rally_join_button'):
            self.logger.battle("Joining rally...")
            self.wait(1.0)
            
            # Select troops
            self.find_and_click('max_troops_button')
            self.wait(0.5)
            
            # Confirm join
            self.find_and_click('confirm_button')
            self.wait(1.0)
            
            self.logger.battle("Joined rally!")
        
        self.close_popup()
        return True


class ScoutTask(BaseTask):
    """
    Scout enemy targets before attacking
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Scout Target"
        self.description = "Scout targets before attacking"
    
    def execute(self) -> bool:
        """Scout a target"""
        # This would be called with target coordinates
        return True
    
    def scout_target(self, x: int, y: int) -> dict:
        """
        Scout a specific target
        
        Args:
            x, y: Target coordinates
        
        Returns:
            Scout report data
        """
        self.logger.battle(f"Scouting target at ({x}, {y})")
        
        # Navigate to world map
        self.click_button('main_screen.world_map')
        self.wait(2.0)
        
        # Click on target
        self.click(x, y)
        self.wait(1.0)
        
        # Click scout button
        self.find_and_click('scout_button')
        self.wait(1.0)
        
        # Wait for scout to return
        self.wait(30, "Waiting for scout report")
        
        # Parse scout report (would need OCR)
        return {
            'power': 0,
            'troops': 0,
            'resources': {}
        }


class BattleCalculator:
    """
    Utility class for battle calculations
    """
    
    @staticmethod
    def estimate_battle_power(
        troops: dict,
        immortals: List[dict],
        tech_bonuses: dict = None
    ) -> int:
        """
        Estimate total battle power
        
        Args:
            troops: Dict of troop type to count
            immortals: List of immortal data
            tech_bonuses: Research/tech bonuses
        
        Returns:
            Estimated power value
        """
        # Base power per troop type
        troop_power = {
            'infantry': 10,
            'cavalry': 12,
            'archer': 11,
            'mage': 15
        }
        
        total = 0
        
        # Troop power
        for troop_type, count in troops.items():
            base = troop_power.get(troop_type, 10)
            total += base * count
        
        # Immortal power
        for immortal in immortals:
            total += immortal.get('power', 0)
        
        # Apply tech bonuses
        if tech_bonuses:
            multiplier = 1 + sum(tech_bonuses.values())
            total = int(total * multiplier)
        
        return total
    
    @staticmethod
    def should_attack(
        our_power: int,
        enemy_power: int,
        safety_margin: float = 1.3
    ) -> bool:
        """
        Determine if we should attack based on power comparison
        
        Args:
            our_power: Our battle power
            enemy_power: Enemy battle power
            safety_margin: Minimum power ratio (1.3 = 30% stronger)
        
        Returns:
            True if attack is advisable
        """
        if enemy_power == 0:
            return True
        
        ratio = our_power / enemy_power
        return ratio >= safety_margin
    
    @staticmethod
    def estimate_losses(
        our_power: int,
        enemy_power: int,
        our_troops: int
    ) -> int:
        """
        Estimate troop losses from battle
        
        Args:
            our_power: Our battle power
            enemy_power: Enemy battle power
            our_troops: Number of our troops
        
        Returns:
            Estimated troop losses
        """
        if our_power == 0:
            return our_troops
        
        power_ratio = enemy_power / our_power
        
        # Simplified loss calculation
        base_loss_rate = 0.1  # 10% minimum losses
        ratio_penalty = max(0, (power_ratio - 0.5) * 0.5)
        
        total_loss_rate = min(1.0, base_loss_rate + ratio_penalty)
        
        return int(our_troops * total_loss_rate)
