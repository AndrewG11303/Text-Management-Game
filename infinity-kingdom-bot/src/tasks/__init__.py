# Game Tasks Module
# Contains all game-specific automation tasks

from src.tasks.base_task import BaseTask
from src.tasks.resource_tasks import (
    CollectResourcesTask,
    GatherResourcesTask,
)
from src.tasks.battle_tasks import (
    AttackGnomesTask,
    AutoBattleTask,
)
from src.tasks.daily_tasks import (
    DailyQuestsTask,
    CollectMailTask,
    AllianceHelpTask,
    FreeChestTask,
)
from src.tasks.building_tasks import (
    BuildingUpgradeTask,
    TrainTroopsTask,
    ResearchTask,
)
from src.tasks.speedup_tasks import (
    AutoSpeedUpTask,
    DragonManagementTask,
    SpeedUpInventoryTask,
)

__all__ = [
    'BaseTask',
    'CollectResourcesTask',
    'GatherResourcesTask',
    'AttackGnomesTask',
    'AutoBattleTask',
    'DailyQuestsTask',
    'CollectMailTask',
    'AllianceHelpTask',
    'FreeChestTask',
    'BuildingUpgradeTask',
    'TrainTroopsTask',
    'ResearchTask',
    'AutoSpeedUpTask',
    'DragonManagementTask',
    'SpeedUpInventoryTask',
]
