import MapAnalyzer
from sc2.position import Point2, Point3

from basebot import BaseBot

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class BaseInfo:
    def __init__(self, townhalls, bot: BaseBot):
        self.townhalls = townhalls
        self.bot = bot
        self.region = bot.map_data.where_all(self.townhalls[0].position)[0]

    def __repr__(self):
        return str(self.region) + ' ' + str(len(self.townhalls))


class PickleRick(BaseBot):

    def __init__(self):
        super().__init__(loglevel="INFO")
        self.bases = []

    async def on_start(self):
        await super().on_start()

    async def on_step(self, iteration: int):
        self.logger.info(f"Minerals : {self.minerals}, Gas : {self.vespene}")
        self.logger.info(f"TownHalls : {self.townhalls}")
        if len(self.bases) == 0:
            self.set_base(townhalls=self.townhalls)
        self.logger.info(f"Bases : {self.bases}")
        ramp = self.bases[0].region.region_ramps[0]
        th = self.bases[0].townhalls[0]
        await self.draw_wallof_points(townhall=th, ramp=ramp)

    def set_base(self, townhalls):
        base = BaseInfo(townhalls=townhalls, bot=self)
        self.bases.append(base)

    async def draw_wallof_points(self, townhall, ramp: MapAnalyzer.MDRamp):
        points = ramp.buildables.points
        for p in points:
            h = self.get_terrain_z_height(p)
            th = self.get_terrain_z_height(townhall.position)
            if h < th:
                continue
            pos = Point3((p.x, p.y, h))
            box_r = 0.5
            color = GREEN
            p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
            p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
            self.client.debug_box_out(p0, p1, color=color)

    async def walloff(self, townhall, choke: MapAnalyzer.ChokeArea):
        if choke.is_ramp:
            build_points = choke.buildables.points
