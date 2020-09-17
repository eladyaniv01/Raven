import MapAnalyzer
from MapAnalyzer.MapData import MapData
from sc2 import BotAI
from sc2.position import Point2, Point3

# from Raven.basebot import BaseBot
from Raven.managers.ManagerBase import BaseManager

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class BaseInfo:
    def __init__(self, bot, townhall, name = 'Base'):
        self.name = name
        self.townhall = townhall
        self.bot = bot
        self.region = bot.map_manager.map_data.where_all(self.townhall.position)[0]
        self.ramps = self.region.region_ramps
        self.chokes = self.region.region_chokes
        self.debug_loc = self.townhall.position

    @staticmethod
    def wall_off_points(choke: "MapAnalyzer.ChokeArea"):
        return choke.buildables.points

    async def draw_wallof_points(self, choke: "MapAnalyzer.ChokeArea"):
        points = self.wall_off_points(choke=choke)
        for p in points:
            h = self.bot.get_terrain_z_height(p)
            th = self.bot.get_terrain_z_height(self.townhall.position)
            if h < th:
                continue
            pos = Point3((p.x, p.y, h))
            box_r = 0.5
            color = GREEN
            p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
            p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
            self.bot.client.debug_box_out(p0, p1, color=color)

    async def draw(self):
        self.bot.client.debug_text_world(
            f"{self.name}",
            pos=self.debug_loc,
            size=13,
            color=(0, 255, 255),
        )
        await self.draw_wallof_points(self.ramps[0])

    def __repr__(self):
        return self.name + ' ' + str(self.region) + ' ' + str(len(self.townhall))


class MapManager(BaseManager):
    """
    """

    def __init__(self, bot: BotAI, loglevel) -> None:
        super().__init__(bot)
        self.bot = bot
        self.map_data = None
        self.loglevel = loglevel
        self.bases = []
        self.main = None

    def initialize(self):
        self.map_data = MapData(self.bot, loglevel=self.loglevel)

    async def update(self, iteration: int) -> None:
        if self.main:
            await self.main.draw()

    def set_base(self, townhall, name):
        base = BaseInfo(townhall=townhall, bot=self.bot, name=name)
        if name == 'Main':
            self.main = base
        self.bases.append(base)


