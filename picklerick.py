import datetime

from loguru import logger
from sc2 import UnitTypeId
from sc2.cache import property_cache_once_per_frame
from sc2.unit import Unit

from Raven.base.basebot import BaseBot
from Raven.base.Command_issuer import Commander
from Raven.base.hub import Hub
from Raven.managers.Evaluator import Evaluator


class PickleRick(BaseBot):

    def __init__(self):
        super().__init__(loglevel="INFO")
        self.hub = Hub(bot=self)
        logfile = datetime.datetime.now().isoformat().replace('.', '').replace(':', '')
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
        await super().on_step(iteration=iteration)
        if iteration == 900:
            await self.client.leave()

        await self.map_manager.update(iteration=iteration)
        await self.distribute_workers()
        await self.production_manager.update(iteration=iteration)
        econ = self.evaluator.evaluate_economy()
        sup = self.evaluator.evaluate_supply()
        if len(econ) > 0:
            await self.production_manager.build_worker()
        if len(sup) > 0:
            await self.construction_manager.build_supply()
        # logger.info(f"{self.commander.counter}")
        if self.debug:
            self.hub.debug_draw()

    async def on_building_construction_complete(self, unit: Unit):
        suspected_builder = self.workers.closest_to(unit)
        sanity_check = self.commander.build_book.get(suspected_builder.tag)
        if sanity_check:
            logger.info(f"len of build book BEFORE: {len(self.commander.build_book)}")
            del self.commander.build_book[suspected_builder.tag]
            logger.info(f"len of build book AFTER: {len(self.commander.build_book)}")
        else:
            logger.error(f"failed sanity check for {unit}")

        # assert unit.type_id in self.commander.build_book.values()

    async def on_unit_created(self, unit: Unit):
        closest_structure = self.structures.closest_to(unit)
        sanity_check = self.commander.train_book.get(closest_structure.tag)
        if sanity_check:
            del self.commander.train_book[closest_structure.tag]
        else:
            bug_unit = (closest_structure, unit)
            self.initial_units.append(bug_unit)
            # assert unit.type_id in self.commander.train_book.values()



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


