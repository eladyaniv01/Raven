from loguru import logger
from sc2 import BotAI

from MapAnalyzer.MapData import MapData
from Raven.base.constants import FAIL
from Raven.managers.ManagerBase import BaseManager
# from Raven.basebot import BaseBot
from Raven.structures.TerranBase import Bases, TerranHQ


class MapManager(BaseManager):
    """
    """

    def __init__(self, bot: BotAI, loglevel) -> None:
        super().__init__(bot)
        self.bot = bot
        self.map_data = None
        self.loglevel = loglevel
        self.bases = Bases(bot=self.bot)

    def initialize(self):
        self.map_data = MapData(self.bot, loglevel=self.loglevel)

    async def update(self, iteration: int) -> None:
        await self.bases.update(iteration=iteration)

    def get_base(self, name=None, index=None):
        if name:
            return self.bases[name]
        if index:
            return self.bases[index]
        logger.error(f"Failed to get base, name {name}, index {index}")
        return FAIL

    def set_base(self, townhall, name):
        base = TerranHQ(townhall=townhall, bot=self.bot, name=name)
        self.bases.add_base(base)
        self.bot.bases = self.bases
