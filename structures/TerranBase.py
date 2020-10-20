import random

from sc2 import AbilityId, UnitTypeId
from sc2.position import Point2, Point3
from sc2.unit import Unit

from MapAnalyzer import ChokeArea
from Raven.base.constants import GREEN, RED


class Bases(list):
    # TODO easy filters for all OCs,  PFS  and CCs
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.morphing_bases = []
        self.iteration = None

    def add_base(self, base):
        self.append(base)

    def remove_base(self, base):
        self.remove(base)

    async def update(self, iteration):
        self.iteration = iteration
        for base in self.morphing_bases[:]:  # making a copy of the list inplace  otherwise we cant remove anything
            await base.update()
            if base.townhall.is_ready and (base.is_orbital or base.is_planetary):
                base.is_morphing = False
                base.tag = base.townhall.tag
                self.morphing_bases.remove(base)

    def __getitem__(self, base_name):
        for base in self:
            if base.name == base_name:
                return base
        index = base_name
        return super(Bases, self).__getitem__(index)

    def __repr__(self):
        return f"Bases({len(self)})"


class TerranHQ:
    def __init__(self, bot, townhall, name='Base'):
        self.name = name
        self.townhall: Unit = townhall
        self.tag = townhall.tag
        self.bot = bot
        self.region = bot.map_manager.map_data.where_all(self.townhall.position)[0]
        self.ramps = self.region.region_ramps
        self.chokes = self.region.region_chokes
        self.debug_loc = self.townhall.position
        self.structure_map = {}  # TODO base remembers structures  ,  and updates when structures are destroyed or fly
        self.is_morphing = False

    async def update(self):
        self.townhall = self.bot.structures.by_tag(self.tag)

    def set_morphing(self):
        if self.is_morphing:
            return
        self.is_morphing = True
        self.bot.bases.morphing_bases.append(self)

    @property
    def is_commandcenter(self):
        return self.townhall.type_id == UnitTypeId.COMMANDCENTER or \
               self.townhall.type_id == UnitTypeId.COMMANDCENTERFLYING

    @property
    def is_orbital(self):
        return self.townhall.type_id == UnitTypeId.ORBITALCOMMAND or \
               self.townhall.type_id == UnitTypeId.ORBITALCOMMANDFLYING

    @property
    def is_planetary(self):
        return self.townhall.type_id == UnitTypeId.PLANETARYFORTRESS

    def set_structure(self, unit: Unit):
        if self.structure_map.get(unit.type_id):
            self.structure_map[unit.type_id].append(unit.position)
        else:
            self.structure_map[unit.type_id] = []
            self.structure_map[unit.type_id].append(unit.position)

    def get_structure_position(self, unit_type: UnitTypeId):
        # TODO make this not stupid
        results = self.structure_map.get(unit_type)
        if results:
            return random.choice(results)

    def is_walled(self, choke):
        grid = self.bot.map_manager.map_data.get_pyastar_grid()
        valid_dummy_location = self.bot.worker_manager.get_builder(location=self.townhall).position.rounded
        behind_wall = self.region.connected_regions[0].center
        check_path = self.bot.map_manager.map_data.pathfind(start=valid_dummy_location, goal=behind_wall, grid=grid)
        if not check_path:
            return True
        return False

    def wall_off_points(self, choke: ChokeArea):
        h = self.bot.get_terrain_z_height(self.townhall)
        high_points = []
        for p in choke.buildables.points:
            if self.bot.get_terrain_z_height(p) == h:
                high_points.append(p)
        return list(map(Point2, high_points))

    def upgrade_orbital(self):
        if self.is_orbital:
            return
        orbital_tech_requirement: float = self.bot.tech_requirement_progress(UnitTypeId.ORBITALCOMMAND)
        if orbital_tech_requirement == 1:
            if self.townhall.is_constructing_scv:
                self.townhall(AbilityId.CANCEL_QUEUE1)
            self.townhall(AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND)
            self.set_morphing()

    # DEBUG methods
    def debug_box(self, pos, box_r, color, text=None):
        p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
        p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
        self.bot.client.debug_box_out(p0, p1, color=color)
        if text:
            self.bot.client.debug_text_world(
                    "\n".join([f"{text}", ]), pos, color=color, size=10,
            )

    async def draw_structures_from_cache(self):
        for k, v in self.structure_map.items():
            for p in v:
                h = self.bot.get_terrain_z_height(p)
                pos = Point3((p.x, p.y, h))
                box_r = 1
                color = RED
                text = str(k).lower().replace('unittypeid.', '')
                self.debug_box(pos=pos, box_r=box_r, color=color, text=text)

    async def draw_wallof_points(self, choke: ChokeArea):
        points = self.wall_off_points(choke=choke)
        for p in points:
            h = self.bot.get_terrain_z_height(p)
            th = self.bot.get_terrain_z_height(self.townhall.position)
            if h < th:
                continue
            pos = Point3((p.x, p.y, h))
            box_r = 0.5
            color = GREEN
            self.debug_box(pos=pos, box_r=box_r, color=color)

    async def draw(self):
        self.bot.client.debug_text_world(
                f"{self.name}",
                pos=self.debug_loc,
                size=13,
                color=(0, 255, 255),
        )
        await self.draw_wallof_points(self.ramps[0])

    def __repr__(self):
        return self.name + ' ' \
               + str(self.bot.bases.index(self)) + ' ' \
               + 'R[' + str(self.region.label) + '] T[' \
               + str(self.townhall) + ']'
