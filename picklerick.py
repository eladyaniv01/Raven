import datetime

from loguru import logger
from sc2 import UnitTypeId
from sc2.cache import property_cache_once_per_frame

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

    async def on_start(self):
        await super().on_start()
        self.map_manager.set_base(townhall=self.townhalls[0], name='Main')
        self.commander = Commander(bot=self)
        self.commander.set_commander(self.production_manager)
        self.commander.set_commander(self.construction_manager)

    async def on_step(self, iteration: int):
        if iteration == 300:
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
        logger.info(f"Economy evaluation: {econ},\nSupply evaluation: {sup}")
        if self.debug:
            self.hub.debug_draw()

    async def on_end(self, game_result):
        logger.info(game_result)
        logger.info("buh buh")
        logger.info(f"issued build_commands {self.commander.build_commands}")
        logger.info(f"issued train_commands {self.commander.train_commands}")
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


