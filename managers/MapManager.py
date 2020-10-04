import random

from sc2 import BotAI, UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit

import MapAnalyzer
from MapAnalyzer.MapData import MapData
# from Raven.basebot import BaseBot
from Raven.managers.ManagerBase import BaseManager

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class Bases(list):

    def __init__(self):
        super().__init__()

    def add_base(self, base):
        self.append(base)

    def remove_base(self, base):
        self.remove(base)

    def __getitem__(self, base_name):
        for base in self:
            if base.name == base_name:
                return base


class BaseInfo:
    def __init__(self, bot, townhall, name = 'Base'):
        self.name = name
        self.townhall = townhall
        self.bot = bot
        self.region = bot.map_manager.map_data.where_all(self.townhall.position)[0]
        self.ramps = self.region.region_ramps
        self.chokes = self.region.region_chokes
        self.debug_loc = self.townhall.position
        self.structure_map = {}  # TODO base remembers structures  ,  and updates when structures are destroyed or fly

    def set_structure(self, unit: Unit):
        if self.structure_map.get(unit.type_id):
            self.structure_map[unit.type_id].append(unit.position)
        else:
            self.structure_map[unit.type_id] = []
            self.structure_map[unit.type_id].append(unit.position)

    def get_structure_position(self, unit_type: UnitTypeId):
        results = self.structure_map.get(unit_type)
        if results:
            return random.choice(results)

    def is_walled(self, choke):
        available_points = self.wall_off_points(choke=choke)
        return not available_points

    def wall_off_points(self, choke: "MapAnalyzer.ChokeArea"):
        h = self.bot.get_terrain_z_height(self.townhall)
        high_points = []
        for p in choke.buildables.points:
            if self.bot.get_terrain_z_height(p) == h:
                high_points.append(p)
        return list(map(Point2, high_points))

    async def draw_structures_from_cache(self):
        for k, v in self.structure_map.items():
            for p in v:
                h = self.bot.get_terrain_z_height(p)
                pos = Point3((p.x, p.y, h))
                box_r = 1
                color = RED
                p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
                p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
                self.bot.client.debug_box_out(p0, p1, color=color)
                text = str(k).lower().replace('unittypeid.', '')
                self.bot.client.debug_text_world(
                        "\n".join([f"{text}", ]), pos, color=color, size=30,
                )

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
        return self.name + ' ' + str(self.region) + ' ' + str((self.townhall))


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
        self.bot.bases = self.bases
        if self.main:
            await self.main.draw_structures_from_cache()

    def set_base(self, townhall, name):
        base = BaseInfo(townhall=townhall, bot=self.bot, name=name)
        if name == 'Main':
            self.main = base
        self.bases.add_base(base)
        self.bot.bases = self.bases
