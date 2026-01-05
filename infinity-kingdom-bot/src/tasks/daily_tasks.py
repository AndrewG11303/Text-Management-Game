"""
Daily Tasks Module
Handles daily quests, mail, and routine activities
"""

import time
from typing import List, Optional
from datetime import datetime, timedelta

from src.tasks.base_task import BaseTask
from src.game_state import GameScreen


class DailyQuestsTask(BaseTask):
    """
    Complete and collect daily quest rewards
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Daily Quests"
        self.description = "Check and collect daily quest rewards"
    
    def execute(self) -> bool:
        """Check daily quests and collect rewards"""
        self.logger.task("Checking daily quests...")
        
        # Navigate to quests
        self.click_button('main_screen.quests')
        self.wait(1.5, "Opening quests")
        
        rewards_collected = 0
        
        # Look for completed quest indicators
        screen = self.capture_screen()
        if screen is None:
            self.close_popup()
            return False
        
        # Find all claimable rewards
        claimable = self.bot.matcher.find_all_templates(
            screen, 'quest_claim_button', threshold=0.75
        )
        
        for x, y, confidence in claimable:
            self.logger.debug(f"Found claimable quest reward at ({x}, {y})")
            self.click(x, y)
            self.wait(1.0, "Claiming reward")
            
            # Close reward popup
            self.close_popup()
            self.wait(0.5)
            
            rewards_collected += 1
        
        # Check for chest rewards (accumulated points)
        self._claim_chest_rewards()
        
        # Close quest menu
        self.close_popup()
        
        self.logger.task(f"Collected {rewards_collected} quest rewards")
        return True
    
    def _claim_chest_rewards(self):
        """Claim chest rewards from accumulated quest points"""
        # Look for chest buttons at bottom of quest screen
        chest_templates = ['quest_chest_1', 'quest_chest_2', 'quest_chest_3']
        
        for template in chest_templates:
            if self.find_and_click(template):
                self.wait(1.0)
                self.close_popup()
                self.wait(0.5)


class CollectMailTask(BaseTask):
    """
    Collect rewards from mail/inbox
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Collect Mail"
        self.description = "Collect rewards from mail"
    
    def execute(self) -> bool:
        """Open mail and collect all rewards"""
        self.logger.task("Checking mail...")
        
        # Navigate to mail
        self.click_button('main_screen.mail')
        self.wait(1.5, "Opening mail")
        
        # Click "Collect All" if available
        if self.find_and_click('mail_collect_all'):
            self.logger.task("Collected all mail rewards")
            self.wait(2.0, "Collecting")
            self.close_popup()
            return True
        
        # Manually collect each mail
        collected = 0
        screen = self.capture_screen()
        
        if screen is not None:
            # Find unread mail indicators
            unread_mails = self.bot.matcher.find_all_templates(
                screen, 'mail_unread', threshold=0.7
            )
            
            for x, y, _ in unread_mails[:10]:  # Limit to 10
                self.click(x, y)
                self.wait(0.8)
                
                # Collect if there's a collect button
                if self.find_and_click('mail_collect_button'):
                    collected += 1
                    self.wait(0.5)
                
                self.close_popup()
                self.wait(0.3)
        
        self.close_popup()
        self.logger.task(f"Collected {collected} mail rewards")
        return True


class AllianceHelpTask(BaseTask):
    """
    Help alliance members with their requests
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Alliance Help"
        self.description = "Help alliance members"
    
    def execute(self) -> bool:
        """Give help to alliance members"""
        self.logger.task("Helping alliance members...")
        
        # Navigate to alliance
        self.click_button('main_screen.alliance')
        self.wait(1.5, "Opening alliance")
        
        # Look for help button (usually shows count of available helps)
        if self.find_and_click('alliance_help_button'):
            self.wait(0.5)
            
            # Click "Help All" if available
            if self.find_and_click('help_all_button'):
                self.logger.task("Helped all alliance members!")
                self.wait(1.0)
        
        # Also check alliance gifts
        self._collect_alliance_gifts()
        
        self.close_popup()
        return True
    
    def _collect_alliance_gifts(self):
        """Collect alliance gift boxes"""
        # Navigate to gifts section
        if self.find_and_click('alliance_gifts_tab'):
            self.wait(1.0)
            
            # Collect available gifts
            if self.find_and_click('collect_gifts_button'):
                self.wait(1.0)
                self.logger.task("Collected alliance gifts!")


class FreeChestTask(BaseTask):
    """
    Collect free chests and rewards
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Free Chests"
        self.description = "Collect free chests and daily rewards"
        
        # Chest cooldown tracking
        self.last_chest_times = {}
    
    def execute(self) -> bool:
        """Collect all available free chests"""
        self.logger.task("Checking for free chests...")
        
        chests_collected = 0
        
        # Check various free chest locations
        chest_checks = [
            self._check_daily_login,
            self._check_free_summon,
            self._check_vip_chest,
            self._check_event_rewards,
            self._check_achievement_rewards,
        ]
        
        for check_func in chest_checks:
            try:
                if check_func():
                    chests_collected += 1
            except Exception as e:
                self.logger.debug(f"Chest check failed: {e}")
        
        self.logger.task(f"Collected {chests_collected} free rewards")
        return True
    
    def _check_daily_login(self) -> bool:
        """Check for daily login reward"""
        # Look for daily login popup
        if self.find_and_click('daily_login_claim'):
            self.wait(1.5)
            self.close_popup()
            self.logger.task("Claimed daily login reward!")
            return True
        return False
    
    def _check_free_summon(self) -> bool:
        """Check for free summon availability"""
        # Navigate to summon area
        if self.find_and_click('summon_button'):
            self.wait(1.5)
            
            # Check for free summon indicator
            if self.find_and_click('free_summon_button'):
                self.wait(2.0, "Summoning")
                self.close_popup()
                self.logger.task("Used free summon!")
                return True
            
            self.close_popup()
        return False
    
    def _check_vip_chest(self) -> bool:
        """Check for free VIP chest"""
        # VIP chests usually available every few hours
        if self.find_and_click('vip_chest_button'):
            self.wait(1.5)
            
            if self.find_and_click('vip_free_chest'):
                self.wait(1.5)
                self.close_popup()
                self.logger.task("Claimed VIP chest!")
                return True
            
            self.close_popup()
        return False
    
    def _check_event_rewards(self) -> bool:
        """Check for event rewards"""
        # Open events
        self.click_button('main_screen.events')
        self.wait(1.5)
        
        # Look for claimable event rewards
        screen = self.capture_screen()
        if screen is not None:
            claimable = self.bot.matcher.find_all_templates(
                screen, 'event_claim_button', threshold=0.75
            )
            
            for x, y, _ in claimable[:5]:
                self.click(x, y)
                self.wait(1.0)
                self.close_popup()
        
        self.close_popup()
        return len(claimable) > 0 if screen else False
    
    def _check_achievement_rewards(self) -> bool:
        """Check for achievement rewards"""
        # This would navigate to achievements and collect
        return False


class DailyResetHandler:
    """
    Handles daily reset timing and planning
    """
    
    def __init__(self, reset_hour: int = 0, timezone_offset: int = 0):
        """
        Initialize reset handler
        
        Args:
            reset_hour: Hour of daily reset (0-23)
            timezone_offset: Timezone offset from UTC
        """
        self.reset_hour = reset_hour
        self.timezone_offset = timezone_offset
    
    def time_until_reset(self) -> timedelta:
        """Get time remaining until next reset"""
        now = datetime.now()
        
        # Calculate next reset time
        today_reset = now.replace(
            hour=self.reset_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        if now >= today_reset:
            # Next reset is tomorrow
            next_reset = today_reset + timedelta(days=1)
        else:
            next_reset = today_reset
        
        return next_reset - now
    
    def is_near_reset(self, minutes_threshold: int = 30) -> bool:
        """Check if we're near daily reset"""
        remaining = self.time_until_reset()
        return remaining.total_seconds() < minutes_threshold * 60
    
    def get_reset_time(self) -> datetime:
        """Get the next reset datetime"""
        now = datetime.now()
        today_reset = now.replace(
            hour=self.reset_hour,
            minute=0,
            second=0,
            microsecond=0
        )
        
        if now >= today_reset:
            return today_reset + timedelta(days=1)
        return today_reset


class WeeklyTasksTask(BaseTask):
    """
    Handle weekly tasks and rewards
    """
    
    def __init__(self, bot_engine):
        super().__init__(bot_engine)
        self.name = "Weekly Tasks"
        self.description = "Check and collect weekly rewards"
    
    def execute(self) -> bool:
        """Check weekly tasks"""
        self.logger.task("Checking weekly tasks...")
        
        # Similar to daily quests but for weekly
        self.click_button('main_screen.quests')
        self.wait(1.5)
        
        # Switch to weekly tab
        if self.find_and_click('weekly_tab'):
            self.wait(1.0)
            
            # Collect any available rewards
            screen = self.capture_screen()
            if screen is not None:
                claimable = self.bot.matcher.find_all_templates(
                    screen, 'quest_claim_button', threshold=0.75
                )
                
                for x, y, _ in claimable:
                    self.click(x, y)
                    self.wait(1.0)
                    self.close_popup()
        
        self.close_popup()
        return True
