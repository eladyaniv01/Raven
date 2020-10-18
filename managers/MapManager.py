from sc2 import BotAI

from MapAnalyzer.MapData import MapData
# from Raven.basebot import BaseBot
from Raven.base.logistics import BaseInfo, Bases
from Raven.managers.ManagerBase import BaseManager


class MapManager(BaseManager):
    """
    """

    def __init__(self, bot: BotAI, loglevel) -> None:
        super().__init__(bot)
        self.bot = bot
        self.map_data = None
        self.loglevel = loglevel
        self.bases = Bases()
        self.main = None

    def initialize(self):
        self.map_data = MapData(self.bot, loglevel=self.loglevel)

    async def update(self, iteration: int) -> None:
        if iteration > 30:
            for base in self.bases:
                await base.update()
            self.bot.bases = self.bases
            if self.main:
                await self.main.draw_structures_from_cache()

    def set_base(self, townhall, name):
        base = BaseInfo(townhall=townhall, bot=self.bot, name=name)
        if name == 'Main':
            self.main = base
        self.bases.add_base(base)
        self.bot.bases = self.bases
