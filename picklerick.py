import datetime

from loguru import logger
from sc2 import UnitTypeId
from sc2.cache import property_cache_once_per_frame
from sc2.ids.upgrade_id import UpgradeId
from sc2.unit import Unit

from Raven.base.basebot import BaseBot
from Raven.base.Command_issuer import Commander
from Raven.base.hub import Hub
from Raven.managers.Evaluator import Evaluator
from Raven.managers.MapManager import TerranHQ


class PickleRick(BaseBot):

    def __init__(self):
        super().__init__(loglevel="INFO")
        self.hub = Hub(bot=self)
        logfile = datetime.datetime.now().isoformat().replace('.', '').replace(':', '')
        logger.remove()
        logger.add(f"Raven/logs/{logfile}", filter=self.log_filter)
        self.evaluator = Evaluator(bot=self)
        self.commander = None
        self.action_reporter = None
        self.initial_units = []

    async def on_start(self):
        await super().on_start()
        self.map_manager.set_base(townhall=self.townhalls[0], name='Main')
        self.commander = Commander(bot=self)
        # self.action_reporter = ActionReporter(bot=self)
        self.commander.set_commander(self.production_manager)
        self.commander.set_commander(self.construction_manager)

    async def on_step(self, iteration: int):
        try:
            await super().on_step(iteration=iteration)
            # points = [Point2(p.location) for p in self.construction_manager.cached_queries]
            # self.draw_point_list(point_list=points)
            # if iteration == 900:
            #     await self.client.leave()

            await self.map_manager.update(iteration=iteration)
            await self.production_manager.update(iteration=iteration)
            await self.distribute_workers()
            econ = self.evaluator.evaluate_economy()
            sup = self.evaluator.evaluate_supply()
            rax = self.evaluator.should_build_rax()
            base = self.map_manager.bases[0]
            if len(econ) > 0:
                await self.production_manager.build_worker(base=base)
            if len(sup) > 0:
                await self.construction_manager.build_supply()

            if rax and self.construction_manager.building_requirements_satisfied(UnitTypeId.BARRACKS):
                # logger.error(f"HERE - {base}")
                # logger.error(f"self.bases - {self.bases}")
                await self.construction_manager.build_rax(base=base)

            base.upgrade_orbital()
            if self.debug:
                self.hub.debug_draw()
        except Exception as e:
            import sys
            tb = sys.exc_info()[2]
            logger.error(e)
            logger.error(tb.tb_next.tb_frame.f_code)
            logger.error(tb.tb_next.tb_frame.f_locals)
            input()

    async def on_building_construction_complete(self, unit: Unit):
        if self.iteration < 30:
            return
        logger.info(f"Construction Complete {unit}")

        is_set = False
        # logger.warning(f"self.bases = {self.bases}")
        for base in self.map_manager.bases:
            if isinstance(base, TerranHQ):
                if unit.position.rounded in base.region.points:
                    base.set_structure(unit=unit)
                    is_set = True
                    break
        if not is_set:
            logger.warning("NO BASE FOUND")
            return
        suspected_builder = self.workers.closest_to(unit)
        sanity_check = self.commander.build_book.get(suspected_builder.tag)
        if sanity_check:
            # logger.info(f"len of build book BEFORE: {len(self.commander.build_book)}")
            del self.commander.build_book[suspected_builder.tag]
            # logger.info(f"len of build book AFTER: {len(self.commander.build_book)}")
        else:
            # logger.error(f"failed sanity check for {unit}")
            pass

        # assert unit.type_id in self.commander.build_book.values()

    async def on_unit_created(self, unit: Unit):
        if self.iteration < 30:
            return
        logger.info(f"Training Complete {unit}")
        closest_structure = self.structures.closest_to(unit)
        sanity_check = self.commander.train_book.get(closest_structure.tag)
        if sanity_check:
            del self.commander.train_book[closest_structure.tag]
        else:
            bug_unit = (closest_structure, unit)
            self.initial_units.append(bug_unit)
            # assert unit.type_id in self.commander.train_book.values()

    async def on_upgrade_complete(self, upgrade: UpgradeId):
        if self.iteration < 30:
            return
        logger.info(f"Upgrade Complete {upgrade}")

    async def on_end(self, game_result):
        logger.info(game_result)
        logger.info(f"self.commander.train_book : {self.commander.train_book}")
        logger.info(f"self.commander.build_book : {self.commander.build_book}")
        super().on_end(game_result)

    @property_cache_once_per_frame
    def known_enemy_expansions(self):  # intel
        townhall_names = {UnitTypeId.COMMANDCENTER, UnitTypeId.ORBITALCOMMAND,
                          UnitTypeId.PLANETARYFORTRESS, UnitTypeId.HATCHERY,
                          UnitTypeId.LAIR, UnitTypeId.HIVE,
                          UnitTypeId.NEXUS}
        enemy_townhalls = self.enemy_structures.filter(lambda x: x.type_id in townhall_names)

        expansions = {}
        for th in enemy_townhalls:
            expansions[th.position] = th

        return expansions
