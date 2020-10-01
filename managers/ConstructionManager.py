from sc2 import BotAI, UnitTypeId

from .ManagerBase import BaseManager


class ConstructionManager(BaseManager):

    def __init__(self, bot: BotAI) -> None:
        super().__init__(bot)
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

    async def build_supply(self):  # construction
        # TODO : move this to worker manager,  and request a worker,  logic for which should be there
        ws = self.bot.workers.idle
        depot_count = self.bot.structures.of_type([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]).amount
        if ws.exists:
            w = ws.closest_to(self.bot.start_location)
        else:
            ws = self.bot.workers.gathering
            if ws.exists:
                w = ws.closest_to(self.bot.start_location)
            else:
                return

            if depot_count == 0:
                loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT,
                                                    list(self.bot.main_base_ramp.corner_depots)[0],
                                                    placement_step=2, random_alternative=False)
            elif depot_count == 1:
                loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT,
                                                    list(self.bot.main_base_ramp.corner_depots)[1],
                                                    placement_step=2, random_alternative=False)
            else:
                loc = await self.bot.find_placement(UnitTypeId.SUPPLYDEPOT, w.position, placement_step=2,
                                                    random_alternative=False)
            if loc:
                if self.commander.build_book.get(w.tag) is None and not self.bot.already_pending(
                        unit_type=UnitTypeId.SUPPLYDEPOT):
                    self.commander.issue_build_command(w, UnitTypeId.SUPPLYDEPOT, loc)
