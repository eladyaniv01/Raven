import random
from typing import TYPE_CHECKING

from loguru import logger
from sc2 import UnitTypeId
from sc2.position import Point2

from MapAnalyzer import ChokeArea
from Raven.managers.ManagerBase import BaseManager
from Raven.structures.TerranBase import TerranHQ

if TYPE_CHECKING:
    from Raven.base.basebot import BaseBot

BASE_RAX_RATIO = 2


class QueryLocations(list):
    def __init__(self):
        super().__init__()

    def add(self, item):
        if item not in self:
            self.append(item)
        else:
            logger.warning(f"repeating item {item}")

    def remove(self, item):
        if item in self:
            self.remove(item)
        else:
            logger.warning(f"not in list  {item}")

    def is_in(self, point):
        for item in self:
            if point == item.location:
                return True
        return False

    def get(self, point):
        if self.is_in(point):
            for item in self:
                if item.location == point:
                    return item

    @property
    def good_points(self):
        return {item.location for item in self if item.is_valid}

    @property
    def bad_points(self):
        return {item.location for item in self if not item.is_valid}

    def __repr__(self):
        return f"<{len(self)}QueryLocations>"


class QueryLocation:
    def __init__(self, location: tuple, attempts=3):
        import traceback
        assert len(location) == 2, f"location we got is {location}, {traceback.print_stack()}"
        self.location = location
        self.attempts = attempts
        self.attempts_counter = 0

    @property
    def is_valid(self):
        return self.attempts_counter < self.attempts

    def __repr__(self):
        if self.is_valid:
            text = 'Valid'
        else:
            text = 'Invalid'
        return f"<QueryLocation[{text}]{self.location}, {self.attempts_counter / self.attempts}>"


class ConstructionManager(BaseManager):

    def __init__(self, bot: "BaseBot") -> None:
        super().__init__(bot)
        self.last_supply_try = None
        self.cached_queries = QueryLocations()
        self.counter = 0
        self.tech_tree = dict([
                (UnitTypeId.SUPPLYDEPOT, None),
                (UnitTypeId.COMMANDCENTER, None),
                (UnitTypeId.REFINERY, None),
                (UnitTypeId.BARRACKS,
                 [UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED, UnitTypeId.SUPPLYDEPOTDROP]),
                (UnitTypeId.BUNKER, [UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING]),
                (UnitTypeId.ORBITALCOMMAND, [UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING]),
                (UnitTypeId.FACTORY, [UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING]),
                (UnitTypeId.ARMORY, [UnitTypeId.FACTORY, UnitTypeId.FACTORYFLYING]),
                (UnitTypeId.STARPORT, [UnitTypeId.FACTORY, UnitTypeId.FACTORYFLYING]),
                (UnitTypeId.FUSIONCORE, [UnitTypeId.STARPORT, UnitTypeId.STARPORTFLYING]),
                (UnitTypeId.GHOSTACADEMY, [UnitTypeId.BARRACKS, UnitTypeId.BARRACKSFLYING]),
                (UnitTypeId.ENGINEERINGBAY,
                 [UnitTypeId.COMMANDCENTER, UnitTypeId.COMMANDCENTERFLYING, UnitTypeId.ORBITALCOMMAND,
                  UnitTypeId.ORBITALCOMMANDFLYING, UnitTypeId.PLANETARYFORTRESS]),
                (UnitTypeId.PLANETARYFORTRESS, [UnitTypeId.ENGINEERINGBAY]),
                (UnitTypeId.SENSORTOWER, [UnitTypeId.ENGINEERINGBAY]),
                (UnitTypeId.MISSILETURRET, [UnitTypeId.ENGINEERINGBAY])
        ])

        self.townhall_types = {
                UnitTypeId.COMMANDCENTER,
                UnitTypeId.ORBITALCOMMAND,
                UnitTypeId.PLANETARYFORTRESS,
                UnitTypeId.COMMANDCENTERFLYING,
                UnitTypeId.ORBITALCOMMANDFLYING
        }

    async def update(self, iteration: int) -> None:
        pass

    def building_requirements_satisfied(self, building_type: UnitTypeId) -> bool:
        return (self.tech_tree[building_type] is None
                or self.bot.structures.of_type(self.tech_tree[building_type]).ready.exists)

    def tech_needed(self, building_type: UnitTypeId) -> list:
        return self.bot.structures.of_type(self.tech_tree[building_type])

    def get_best_depot_placement(self, base: TerranHQ):
        # TODO  get all choke wall off spots,  and prioritize
        choke: ChokeArea = base.chokes[0]
        if choke.is_ramp and not base.is_walled(choke=choke):
            """
            if we want rax in middle do choke.ramp.corner_depots
            else do  + choke.ramp.depot_in_middle
            """

            pts = list(choke.ramp.corner_depots)
            if self.bot.structures(UnitTypeId.BARRACKS).exists:
                pts.append(choke.ramp.depot_in_middle)
            # pts.append(choke.ramp.depot_in_middle) # for now we assume we want rax in middle TODO logic for this
            points_ = [p.rounded for p in pts if p in base.region.buildables.points]  # fix me

            if len(points_) > 0:
                return points_

        points = list(map(Point2, base.region.perimeter_points))
        return points
        # if points:
        #     filtered = [p for p in points if (p not in self.cached_queries.bad_points and isinstance(p, tuple))]
        #     if len(filtered) == 0:
        #         if len(base.region.buildables.points):
        #             pt = random.choice(base.region.buildables.points)
        #             assert (pt[0] and pt[1]), f"WTF"
        #             return [pt]
        #     return filtered
        # else:
        #     logger.error("No Points")
        #     return []

    def get_best_production_placement(self, base: TerranHQ):  # production = rax,  fact,  starport
        choke: ChokeArea = base.chokes[0]
        if choke.is_ramp and not base.is_walled(choke=choke):
            # points_ = [p for p in choke.ramp.barracks_correct_placement if p in base.region.buildables.points]
            points_ = [p for p in choke.ramp.barracks_in_middle if p in base.region.buildables.points]
            if len(points_) > 0:
                return points_
        points = list(map(Point2, base.region.buildables.points))

        return points

    async def build_rax(self, base: TerranHQ):
        # logger.error(f"BASE {base}")
        if not base:
            return
        builder = self.bot.worker_manager.get_builder(location=base.townhall)  # what if there is no cc there yet?
        # logger.info(f"Builder picked for Rax : {builder}")
        points = self.get_best_production_placement(base=base)
        point = random.choice(points)
        # loc = await self.bot.find_placement(UnitTypeId.BARRACKS, near=point)
        # logger.error(f"loc for rax = {loc}")
        self.commander.issue_build_command(builder, UnitTypeId.BARRACKS, point)

    async def build_supply(self):  # construction
        # if not self.last_supply_try:
        #     self.last_supply_try = self.bot.time
        # if self.bot.already_pending(UnitTypeId.SUPPLYDEPOT):
        #     return
        # if self.bot.time - self.last_supply_try < 5:
        #     # logger.warning(self.bot.time - self.last_supply_try)
        #     return
        # self.last_supply_try = self.bot.time
        # depot_count = self.bot.structures.of_type([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]).amount
        # _loc = None
        # pick base
        base = self.bot.bases['Main']
        # pick location in base
        base_location = base.townhall
        builder = self.bot.worker_manager.get_builder(location=base_location)
        # logger.info(f"Builder picked for supply : {builder}")

        points = self.get_best_depot_placement(base=base)
        self.bot.draw_point_list(points)
        _loc = random.choice(points)

        self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, _loc)
        # loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, near=_loc)
        # # logger.error(f"LOC = {loc}")
        # if loc:
        #     if self.commander.build_book.get(builder.tag) is None and not self.bot.already_pending(
        #             unit_type=UnitTypeId.SUPPLYDEPOT):
        #         self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, loc)
        #         # logger.error(
        #         # f"[{self.counter}] Found placement ,  tried _loc : {_loc} ")
        #         return
        # else:
        #     self.counter += 1
        #     # logger.error(
        #     #         f"[{self.counter}] Could not find placement ,  tried _loc : {_loc} ")  # TODO make this a generic exception
        #     return

        # logger.error(
        #         f"Could not find placement ,  tried _loc : {_loc} ")
        return
        # walloff_positions = self.get_best_depot_placement(base=base)
        # if walloff_positions:
        #     _loc = random.choice(walloff_positions)
        #     loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, near=_loc, placement_step=1, max_distance=2)
        #     if loc:
        #         if self.commander.build_book.get(builder.tag) is None and not self.bot.already_pending(
        #                 unit_type=UnitTypeId.SUPPLYDEPOT):
        #             self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, loc)
        #             return
        #     else:
        #         self.counter += 1
        #         logger.error(
        #                 f"[{self.counter}] Could not find placement ,  tried _loc : {_loc} ")  # TODO make this a generic exception
        #
        # elif base.region.buildables.points:
        #     _loc = random.choice(base.region.buildables.points)
        # else:
        #     logger.error(f"Base {base} has no Buildable Points")
        #     return
        # loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, near=_loc, placement_step=1, max_distance=2)
        # if loc:
        #     if self.commander.build_book.get(builder.tag) is None and not self.bot.already_pending(
        #             unit_type=UnitTypeId.SUPPLYDEPOT):
        #         self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, loc)
        # else:
        #     self.counter += 1
        #     logger.error(
        #             f"[{self.counter}] Could not find placement ,  tried _loc : {_loc} ")  # TODO make this a generic exception

        # if depot_count == 0:
        #     loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT,
        #                                         list(self.bot.main_base_ramp.corner_depots)[0],
        #                                         placement_step=2, random_alternative=False)
        # elif depot_count == 1:
        #     loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT,
        #                                         list(self.bot.main_base_ramp.corner_depots)[1],
        #                                         placement_step=2, random_alternative=False)
        # else:
        #     loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, builder.position, placement_step=2,
        #                                         random_alternative=False)
        # if loc:
        #     if self.commander.build_book.get(builder.tag) is None and not self.bot.already_pending(
        #             unit_type=UnitTypeId.SUPPLYDEPOT):
        #         self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, loc)
