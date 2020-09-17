from sc2 import UnitTypeId, AbilityId
from sc2.cache import property_cache_once_per_frame
from sc2.unit import Unit

from Raven.basebot import BaseBot


class PickleRick(BaseBot):

    def __init__(self, debug=True):
        super().__init__(loglevel="INFO")
        self.debug = debug

    def building_requirements_satisfied(self, building_type: UnitTypeId) -> bool:
        return (self.construction_manager.tech_tree[building_type] is None
                or self.structures.of_type(self.construction_manager.tech_tree[building_type]).ready.exists)

    def base_is_depleted(self, th: Unit) -> bool:
        mfs = self.mineral_field.closer_than(15, th).filter(lambda x: x.mineral_contents > 0)
        return mfs.empty

    def should_build_scv(self) -> bool:
        room = 0
        for th in self.townhalls.filter(lambda x: not self.base_is_depleted(x)):
            room += th.surplus_harvesters

        for ref in self.structures(UnitTypeId.REFINERY).filter(lambda x: x.vespene_contents > 0):
            room += ref.surplus_harvesters

        # produce a few more harvesters than needed early on
        # so new bases can be saturated faster
        # don't build if orbitals should be prioritized first
        orbitals_needed = self.townhalls.ready.amount - (self.structures(UnitTypeId.ORBITALCOMMAND)
                                                         | self.structures(UnitTypeId.ORBITALCOMMANDFLYING)
                                                         | self.structures(UnitTypeId.PLANETARYFORTRESS)).amount
        if orbitals_needed > 0:
            for th in self.townhalls.filter(lambda x: not x.is_idle):
                if (th.orders[0].ability.id == AbilityId.UPGRADETOORBITAL_ORBITALCOMMAND
                        or th.orders[0].ability.id == AbilityId.UPGRADETOPLANETARYFORTRESS_PLANETARYFORTRESS):
                    orbitals_needed -= 1

        # make sure i build workers if i lose them in the beginning
        return self.workers.amount < 14 or (self.workers.amount < 75 and room < 16
                                            and (not self.building_requirements_satisfied(UnitTypeId.ORBITALCOMMAND) or orbitals_needed <= 0))

    def should_build_supply(self) -> bool:
        below_supply_cap = self.supply_cap < 200
        depots_in_production = self.already_pending(UnitTypeId.SUPPLYDEPOT)
        early_game_condition = self.supply_left < 6 and self.supply_used >= 13 and depots_in_production < 1
        later_game_condition = self.supply_left < 12 and self.supply_cap >= 40 and depots_in_production <= 2

        return below_supply_cap and (early_game_condition or later_game_condition)

    @property_cache_once_per_frame
    def known_enemy_expansions(self):
        townhall_names = {UnitTypeId.COMMANDCENTER, UnitTypeId.ORBITALCOMMAND,
                          UnitTypeId.PLANETARYFORTRESS, UnitTypeId.HATCHERY,
                          UnitTypeId.LAIR, UnitTypeId.HIVE,
                          UnitTypeId.NEXUS}
        enemy_townhalls = self.enemy_structures.filter(lambda x: x.type_id in townhall_names)

        expansions = {}
        for th in enemy_townhalls:
            expansions[th.position] = th

        return expansions

    async def build_depot(self):
        ws = self.workers.gathering
        depot_count = self.structures.of_type([UnitTypeId.SUPPLYDEPOT, UnitTypeId.SUPPLYDEPOTLOWERED]).amount
        if ws.exists:
            w = ws.closest_to(self.start_location)

            if depot_count == 0:
                loc = await self.find_placement(UnitTypeId.SUPPLYDEPOT, list(self.main_base_ramp.corner_depots)[0],
                                                placement_step=2, random_alternative=False)
            elif depot_count == 1:
                loc = await self.find_placement(UnitTypeId.SUPPLYDEPOT, list(self.main_base_ramp.corner_depots)[1],
                                                placement_step=2, random_alternative=False)
            else:
                loc = await self.find_placement(UnitTypeId.SUPPLYDEPOT, w.position, placement_step=2,
                                                random_alternative=False)
            if loc:
                w.build(UnitTypeId.SUPPLYDEPOT, loc)

    async def control_unit_production(self):
        if self.supply_used == 200:
            return

        # build depots when supply is needed soon
        if self.townhalls.exists and self.should_build_supply() and self.can_afford(UnitTypeId.SUPPLYDEPOT):
            await self.build_depot()
        # scv building is here to prioritize it together with economy
        # and not when army units are needed
        if self.townhalls.exists and self.should_build_scv() and self.can_afford(UnitTypeId.SCV):
            for th in self.townhalls.idle:
                th.train(UnitTypeId.SCV)
            for th in self.townhalls.filter(lambda x: (len(x.orders) == 1
                                                       and x.orders[0].ability.id == AbilityId.COMMANDCENTERTRAIN_SCV
                                                       and x.orders[0].progress >= 0.95)):
                th.train(UnitTypeId.SCV)

    def get_log_file(self):
        return 'somelog.log.1'

    async def on_start(self):
        await super().on_start()
        self.map_manager.set_base(townhall=self.townhalls[0], name='Main')

    async def on_end(self, game_result):
        self.logger.info(game_result)
        self.logger.info("buh buh")

    async def on_step(self, iteration: int):
        await self.map_manager.update(iteration=iteration)
        await self.control_unit_production()
        self._debug_draw()

    # async def walloff(self, townhall, choke: MapAnalyzer.ChokeArea):
    #     if choke.is_ramp:
    #         build_points = choke.buildables.points



    def _debug_draw(self) -> None:

        # left hand side
        self.client.debug_text_screen(
            f"Bot mode: ",
            pos=(0.2, 0.1),
            size=13,
            color=(0, 255, 255),
        )
        self.client.debug_text_screen(
            f"Army Comp: ",
            pos=(0.2, 0.1),
            size=13,
            color=(0, 255, 255),
        )
        self.client.debug_text_screen(
            f"Opening complete: ",
            pos=(0.2, 0.12),
            size=13,
            color=(0, 255, 255),
        )
        self.client.debug_text_screen(
            f"Workers per gas: ",
            pos=(0.2, 0.14),
            size=13,
            color=(0, 255, 255),
        )

        # eft hand side, bottom
        self.client.debug_text_screen(
            f"Priority queue: ",
            pos=(0.2, 0.14),
            size=13,
            color=(0, 255, 255),
        )

        # right hand side
        self.client.debug_text_screen(
            f"Enemy Army Value:",
            pos=(0.7, 0.1),
            size=13,
            color=(0, 255, 255),
        )
        self.client.debug_text_screen(
            f"Ready Army Value:",
            pos=(0.7, 0.13),
            size=13,
            color=(0, 255, 255),
        )
        self.client.debug_text_screen(
            f"Total Army Value: ",
            pos=(0.7, 0.15),
            size=13,
            color=(0, 255, 255),
        )

        self.client.debug_text_screen(
            f"Resources Lost: ",
            pos=(0.7, 0.17),
            size=13,
            color=(0, 255, 255),
        )
        self.client.debug_text_screen(
            f"Enemy Resources Lost: ",
            pos=(0.7, 0.19),
            size=13,
            color=(0, 255, 255),
        )

        self.client.debug_text_screen(
            f"Mineral collection rate: {self.state.score.collection_rate_minerals}",
            pos=(0.7, 0.21),
            size=13,
            color=(0, 255, 255),
        )

        self.client.debug_text_screen(
            f"Vespene collection rate: {self.state.score.collection_rate_vespene}",
            pos=(0.7, 0.23),
            size=13,
            color=(0, 255, 255),
        )