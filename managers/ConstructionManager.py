import random
from typing import TYPE_CHECKING

from loguru import logger
from sc2 import UnitTypeId

from .ManagerBase import BaseManager

if TYPE_CHECKING:
    from Raven.base.basebot import BaseBot

BASE_RAX_RATIO = 2


class ConstructionManager(BaseManager):

    def __init__(self, bot: "BaseBot") -> None:
        super().__init__(bot)
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

    def get_best_depot_placement(self, base):
        choke = base.chokes[0]
        if not base.is_walled(choke=choke):
            # todo logic for picking choke
            return base.wall_off_points(choke=choke)

    async def build_rax(self):
        pass


    async def build_supply(self):  # construction
        depot_count = self.bot.structures.of_type([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]).amount
        # pick base
        base = self.bot.bases['Main']
        # pick location in base
        base_location = base.townhall
        builder = self.bot.worker_manager.get_builder(location=base_location)
        logger.info(f"Builder picked for supply : {builder}")

        # need to wall off ?  todo logic for that

        walloff_positions = self.get_best_depot_placement(base=base)
        if walloff_positions:
            _loc = random.choice(walloff_positions)
            loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, near=_loc, placement_step=1, max_distance=2)
            if loc:
                if self.commander.build_book.get(builder.tag) is None and not self.bot.already_pending(
                        unit_type=UnitTypeId.SUPPLYDEPOT):
                    self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, loc)
                    return
            else:
                self.counter += 1
                logger.error(
                        f"[{self.counter}] Could not find placement ,  tried _loc : {_loc} ")  # TODO make this a generic exception

        elif base.region.buildables.points:
            _loc = random.choice(base.region.buildables.points)
        else:
            logger.error(f"Base {base} has no Buildable Points")
            return
        loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, near=_loc, placement_step=1, max_distance=2)
        if loc:
            if self.commander.build_book.get(builder.tag) is None and not self.bot.already_pending(
                    unit_type=UnitTypeId.SUPPLYDEPOT):
                self.commander.issue_build_command(builder, UnitTypeId.SUPPLYDEPOT, loc)
        else:
            self.counter += 1
            logger.error(
                    f"[{self.counter}] Could not find placement ,  tried _loc : {_loc} ")  # TODO make this a generic exception

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
