"""
Decision Engine for Infinity Kingdom Bot
Smart decision-making for building upgrades, research, and resource allocation
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum, auto
from datetime import datetime, timedelta

from src.logger import get_logger


class PlayStyle(Enum):
    """Player playstyle preferences"""
    BALANCED = auto()      # Equal focus on all areas
    AGGRESSIVE = auto()    # Focus on military/combat
    ECONOMIC = auto()      # Focus on resource production
    DEFENSIVE = auto()     # Focus on defense/protection
    SPEEDRUN = auto()      # Rush castle level as fast as possible


class GamePhase(Enum):
    """Current phase of the game"""
    EARLY_GAME = auto()    # Castle 1-10
    MID_GAME = auto()      # Castle 11-20
    LATE_GAME = auto()     # Castle 21-30
    END_GAME = auto()      # Castle 30+


@dataclass
class BuildingInfo:
    """Information about a building"""
    name: str
    category: str  # 'military', 'economy', 'development', 'defense'
    current_level: int = 1
    max_level: int = 30
    is_upgrading: bool = False
    upgrade_time: int = 0  # seconds
    
    # Resource costs for next level
    gold_cost: int = 0
    food_cost: int = 0
    wood_cost: int = 0
    iron_cost: int = 0
    
    # Requirements
    castle_requirement: int = 1
    prerequisites: List[str] = field(default_factory=list)
    
    # Value metrics
    power_gain: int = 0
    production_gain: int = 0  # Resources per hour
    unlock_value: int = 0     # What it unlocks


@dataclass
class ResearchInfo:
    """Information about a research technology"""
    name: str
    category: str
    current_level: int = 0
    max_level: int = 10
    is_researching: bool = False
    research_time: int = 0
    
    # Costs
    gold_cost: int = 0
    
    # Requirements
    academy_requirement: int = 1
    prerequisites: List[str] = field(default_factory=list)
    
    # Benefits
    bonus_type: str = ""  # 'attack', 'defense', 'gathering_speed', etc.
    bonus_value: float = 0.0


class DecisionEngine:
    """
    Intelligent decision-making engine for upgrades and research
    
    Considers:
    - Current game phase
    - Player's playstyle preference
    - Resource availability
    - Prerequisites and dependencies
    - Return on investment (ROI)
    - Current bottlenecks
    - Time efficiency
    """
    
    def __init__(self, config: dict, game_state):
        self.config = config
        self.state = game_state
        self.logger = get_logger()
        
        # Get decision settings
        decision_config = config.get('decision_engine', {})
        
        # Playstyle preference
        style_name = decision_config.get('playstyle', 'balanced').upper()
        self.playstyle = PlayStyle[style_name] if style_name in PlayStyle.__members__ else PlayStyle.BALANCED
        
        # Weights for different factors (can be customized)
        self.weights = decision_config.get('weights', {
            'power_gain': 1.0,
            'production_gain': 1.0,
            'unlock_value': 1.5,
            'time_efficiency': 0.8,
            'prerequisite_value': 1.2,
        })
        
        # Building database
        self.buildings = self._init_building_database()
        
        # Research database  
        self.research = self._init_research_database()
        
        self.logger.info(f"Decision Engine initialized (playstyle: {self.playstyle.name})")
    
    def _init_building_database(self) -> Dict[str, BuildingInfo]:
        """Initialize building information database"""
        # This would ideally be loaded from game data
        # Here's a representative sample
        return {
            'castle': BuildingInfo(
                name='Castle',
                category='development',
                unlock_value=100,  # Unlocks everything
                power_gain=500,
            ),
            'barracks': BuildingInfo(
                name='Barracks',
                category='military',
                power_gain=200,
                prerequisites=['castle'],
            ),
            'academy': BuildingInfo(
                name='Academy',
                category='development',
                unlock_value=50,  # Unlocks research
                prerequisites=['castle'],
            ),
            'hospital': BuildingInfo(
                name='Hospital',
                category='military',
                power_gain=100,
                prerequisites=['castle'],
            ),
            'wall': BuildingInfo(
                name='Wall',
                category='defense',
                power_gain=150,
                prerequisites=['castle'],
            ),
            'watchtower': BuildingInfo(
                name='Watchtower',
                category='defense',
                unlock_value=30,  # Intel gathering
                prerequisites=['castle'],
            ),
            'farm_1': BuildingInfo(
                name='Farm',
                category='economy',
                production_gain=100,  # Food per hour
                prerequisites=['castle'],
            ),
            'lumber_mill_1': BuildingInfo(
                name='Lumber Mill',
                category='economy',
                production_gain=100,
                prerequisites=['castle'],
            ),
            'iron_mine_1': BuildingInfo(
                name='Iron Mine',
                category='economy',
                production_gain=80,
                prerequisites=['castle'],
            ),
            'stone_quarry_1': BuildingInfo(
                name='Stone Quarry',
                category='economy',
                production_gain=80,
                prerequisites=['castle'],
            ),
            'trading_post': BuildingInfo(
                name='Trading Post',
                category='economy',
                production_gain=50,
                unlock_value=20,
                prerequisites=['castle'],
            ),
            'embassy': BuildingInfo(
                name='Embassy',
                category='military',
                unlock_value=40,  # Alliance features
                prerequisites=['castle'],
            ),
        }
    
    def _init_research_database(self) -> Dict[str, ResearchInfo]:
        """Initialize research information database"""
        return {
            # Military research
            'infantry_attack': ResearchInfo(
                name='Infantry Attack',
                category='military',
                bonus_type='attack',
                bonus_value=2.0,  # 2% per level
            ),
            'cavalry_attack': ResearchInfo(
                name='Cavalry Attack',
                category='military',
                bonus_type='attack',
                bonus_value=2.0,
            ),
            'archer_attack': ResearchInfo(
                name='Archer Attack',
                category='military',
                bonus_type='attack',
                bonus_value=2.0,
            ),
            'troop_health': ResearchInfo(
                name='Troop Health',
                category='military',
                bonus_type='health',
                bonus_value=2.0,
            ),
            'march_speed': ResearchInfo(
                name='March Speed',
                category='military',
                bonus_type='march_speed',
                bonus_value=3.0,
            ),
            
            # Economy research
            'food_production': ResearchInfo(
                name='Food Production',
                category='economy',
                bonus_type='production',
                bonus_value=5.0,
            ),
            'wood_production': ResearchInfo(
                name='Wood Production',
                category='economy',
                bonus_type='production',
                bonus_value=5.0,
            ),
            'gathering_speed': ResearchInfo(
                name='Gathering Speed',
                category='economy',
                bonus_type='gathering_speed',
                bonus_value=3.0,
            ),
            'load_capacity': ResearchInfo(
                name='Load Capacity',
                category='economy',
                bonus_type='load',
                bonus_value=5.0,
            ),
            
            # Development research
            'construction_speed': ResearchInfo(
                name='Construction Speed',
                category='development',
                bonus_type='build_speed',
                bonus_value=3.0,
            ),
            'research_speed': ResearchInfo(
                name='Research Speed',
                category='development',
                bonus_type='research_speed',
                bonus_value=3.0,
            ),
            'training_speed': ResearchInfo(
                name='Training Speed',
                category='development',
                bonus_type='train_speed',
                bonus_value=3.0,
            ),
            
            # Defense research
            'wall_defense': ResearchInfo(
                name='Wall Defense',
                category='defense',
                bonus_type='wall_hp',
                bonus_value=5.0,
            ),
            'trap_attack': ResearchInfo(
                name='Trap Attack',
                category='defense',
                bonus_type='trap_damage',
                bonus_value=3.0,
            ),
        }
    
    def get_game_phase(self) -> GamePhase:
        """Determine current game phase based on castle level"""
        castle = self.buildings.get('castle')
        if castle:
            level = castle.current_level
            if level <= 10:
                return GamePhase.EARLY_GAME
            elif level <= 20:
                return GamePhase.MID_GAME
            elif level <= 30:
                return GamePhase.LATE_GAME
            else:
                return GamePhase.END_GAME
        return GamePhase.EARLY_GAME
    
    def get_playstyle_weights(self) -> Dict[str, float]:
        """Get category weights based on playstyle"""
        weights = {
            'military': 1.0,
            'economy': 1.0,
            'development': 1.0,
            'defense': 1.0,
        }
        
        if self.playstyle == PlayStyle.AGGRESSIVE:
            weights['military'] = 2.0
            weights['economy'] = 0.8
            weights['defense'] = 0.6
            
        elif self.playstyle == PlayStyle.ECONOMIC:
            weights['economy'] = 2.0
            weights['military'] = 0.7
            weights['development'] = 1.2
            
        elif self.playstyle == PlayStyle.DEFENSIVE:
            weights['defense'] = 2.0
            weights['military'] = 1.0
            weights['economy'] = 0.8
            
        elif self.playstyle == PlayStyle.SPEEDRUN:
            weights['development'] = 2.5
            weights['economy'] = 1.5
            weights['military'] = 0.5
            weights['defense'] = 0.3
        
        return weights
    
    def get_phase_weights(self) -> Dict[str, float]:
        """Get category weights based on game phase"""
        phase = self.get_game_phase()
        
        if phase == GamePhase.EARLY_GAME:
            # Focus on development and economy early
            return {
                'military': 0.6,
                'economy': 1.5,
                'development': 2.0,
                'defense': 0.4,
            }
        elif phase == GamePhase.MID_GAME:
            # Balanced with slight military focus
            return {
                'military': 1.2,
                'economy': 1.0,
                'development': 1.0,
                'defense': 0.8,
            }
        elif phase == GamePhase.LATE_GAME:
            # Military and defense become important
            return {
                'military': 1.5,
                'economy': 0.8,
                'development': 0.7,
                'defense': 1.2,
            }
        else:  # END_GAME
            # Max everything, focus on what's behind
            return {
                'military': 1.0,
                'economy': 1.0,
                'development': 1.0,
                'defense': 1.0,
            }
    
    def calculate_building_score(self, building: BuildingInfo) -> float:
        """
        Calculate priority score for a building upgrade
        
        Higher score = higher priority
        """
        if building.is_upgrading:
            return -1  # Already upgrading
        
        if building.current_level >= building.max_level:
            return -1  # Already maxed
        
        # Check prerequisites
        if not self._check_prerequisites(building.prerequisites):
            return -1  # Prerequisites not met
        
        # Check castle requirement
        castle = self.buildings.get('castle')
        if castle and building.castle_requirement > castle.current_level:
            return -1  # Castle level too low
        
        # Check resource availability
        if not self._can_afford_building(building):
            return 0  # Can't afford, but keep in consideration
        
        # Calculate base score
        score = 0.0
        
        # Power gain value
        score += building.power_gain * self.weights.get('power_gain', 1.0)
        
        # Production gain value
        score += building.production_gain * self.weights.get('production_gain', 1.0)
        
        # Unlock value (what does this building enable?)
        score += building.unlock_value * self.weights.get('unlock_value', 1.5)
        
        # Time efficiency (short upgrades are more efficient early)
        if building.upgrade_time > 0:
            time_factor = 3600 / max(building.upgrade_time, 60)  # 1 hour baseline
            score *= (1 + time_factor * self.weights.get('time_efficiency', 0.8) * 0.1)
        
        # Apply playstyle weights
        style_weights = self.get_playstyle_weights()
        score *= style_weights.get(building.category, 1.0)
        
        # Apply game phase weights
        phase_weights = self.get_phase_weights()
        score *= phase_weights.get(building.category, 1.0)
        
        # Bonus for buildings that are behind
        avg_level = self._get_average_building_level()
        if building.current_level < avg_level - 2:
            score *= 1.3  # 30% bonus for catching up
        
        # Castle always gets priority (required for other upgrades)
        if building.name == 'Castle':
            score *= 2.0
        
        return score
    
    def calculate_research_score(self, research: ResearchInfo) -> float:
        """
        Calculate priority score for a research technology
        """
        if research.is_researching:
            return -1
        
        if research.current_level >= research.max_level:
            return -1
        
        # Check prerequisites
        if not self._check_prerequisites(research.prerequisites):
            return -1
        
        # Check academy requirement
        academy = self.buildings.get('academy')
        if academy and research.academy_requirement > academy.current_level:
            return -1
        
        # Calculate base score
        score = 0.0
        
        # Bonus value per level
        score += research.bonus_value * 10
        
        # Apply playstyle weights
        style_weights = self.get_playstyle_weights()
        score *= style_weights.get(research.category, 1.0)
        
        # Apply game phase weights
        phase_weights = self.get_phase_weights()
        score *= phase_weights.get(research.category, 1.0)
        
        # Prioritize speed bonuses in early game
        if self.get_game_phase() == GamePhase.EARLY_GAME:
            if 'speed' in research.bonus_type:
                score *= 1.5
        
        return score
    
    def _check_prerequisites(self, prerequisites: List[str]) -> bool:
        """Check if all prerequisites are met"""
        for prereq in prerequisites:
            building = self.buildings.get(prereq)
            if building and building.current_level < 1:
                return False
        return True
    
    def _can_afford_building(self, building: BuildingInfo) -> bool:
        """Check if we can afford to upgrade a building"""
        resources = self.state.resources
        
        return (
            resources.gold >= building.gold_cost and
            resources.food >= building.food_cost and
            resources.wood >= building.wood_cost and
            resources.iron >= building.iron_cost
        )
    
    def _get_average_building_level(self) -> float:
        """Get average level of all buildings"""
        levels = [b.current_level for b in self.buildings.values()]
        return sum(levels) / len(levels) if levels else 1
    
    def get_best_building_to_upgrade(self) -> Optional[str]:
        """
        Determine the best building to upgrade next
        
        Returns:
            Building name or None
        """
        scores = {}
        
        for name, building in self.buildings.items():
            score = self.calculate_building_score(building)
            if score > 0:
                scores[name] = score
        
        if not scores:
            return None
        
        # Sort by score (highest first)
        sorted_buildings = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        best_name, best_score = sorted_buildings[0]
        
        self.logger.debug(f"Building scores: {sorted_buildings[:5]}")
        self.logger.info(f"Best building to upgrade: {best_name} (score: {best_score:.1f})")
        
        return best_name
    
    def get_best_research(self) -> Optional[str]:
        """
        Determine the best research to start next
        
        Returns:
            Research name or None
        """
        scores = {}
        
        for name, research in self.research.items():
            score = self.calculate_research_score(research)
            if score > 0:
                scores[name] = score
        
        if not scores:
            return None
        
        sorted_research = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        best_name, best_score = sorted_research[0]
        
        self.logger.debug(f"Research scores: {sorted_research[:5]}")
        self.logger.info(f"Best research: {best_name} (score: {best_score:.1f})")
        
        return best_name
    
    def get_upgrade_recommendations(self, count: int = 5) -> List[Tuple[str, float, str]]:
        """
        Get top N upgrade recommendations with reasons
        
        Returns:
            List of (name, score, reason) tuples
        """
        recommendations = []
        
        # Score all buildings
        for name, building in self.buildings.items():
            score = self.calculate_building_score(building)
            if score > 0:
                reason = self._get_upgrade_reason(building)
                recommendations.append((name, score, reason))
        
        # Sort and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:count]
    
    def _get_upgrade_reason(self, building: BuildingInfo) -> str:
        """Generate human-readable reason for upgrade recommendation"""
        reasons = []
        
        if building.unlock_value > 50:
            reasons.append("unlocks important features")
        
        if building.power_gain > 200:
            reasons.append("high power gain")
        
        if building.production_gain > 80:
            reasons.append("boosts resource production")
        
        avg_level = self._get_average_building_level()
        if building.current_level < avg_level - 2:
            reasons.append("catching up to other buildings")
        
        style_weights = self.get_playstyle_weights()
        if style_weights.get(building.category, 1.0) > 1.5:
            reasons.append(f"matches {self.playstyle.name.lower()} playstyle")
        
        if not reasons:
            reasons.append("general progression")
        
        return ", ".join(reasons)
    
    def update_building_info(self, name: str, **kwargs):
        """Update building information from game state"""
        if name in self.buildings:
            building = self.buildings[name]
            for key, value in kwargs.items():
                if hasattr(building, key):
                    setattr(building, key, value)
    
    def update_research_info(self, name: str, **kwargs):
        """Update research information from game state"""
        if name in self.research:
            research = self.research[name]
            for key, value in kwargs.items():
                if hasattr(research, key):
                    setattr(research, key, value)
    
    def get_strategy_summary(self) -> str:
        """Get a summary of current strategy"""
        phase = self.get_game_phase()
        
        summary = f"""
=== Strategy Summary ===
Playstyle: {self.playstyle.name}
Game Phase: {phase.name}

Current Focus:
"""
        # Get top priorities
        style_weights = self.get_playstyle_weights()
        phase_weights = self.get_phase_weights()
        
        combined = {
            cat: style_weights.get(cat, 1) * phase_weights.get(cat, 1)
            for cat in ['military', 'economy', 'development', 'defense']
        }
        
        sorted_focus = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        
        for i, (category, weight) in enumerate(sorted_focus, 1):
            priority = "HIGH" if weight > 1.5 else "MEDIUM" if weight > 0.8 else "LOW"
            summary += f"  {i}. {category.title()}: {priority}\n"
        
        # Top recommendations
        recommendations = self.get_upgrade_recommendations(3)
        if recommendations:
            summary += "\nTop Upgrade Recommendations:\n"
            for name, score, reason in recommendations:
                summary += f"  - {name}: {reason}\n"
        
        return summary
