from loguru import logger
from sc2 import AbilityId, BotAI, UnitTypeId

from .ManagerBase import BaseManager


class ProductionManager(BaseManager):
    def __init__(self, bot: BotAI) -> None:
        super().__init__(bot)
        self.bot = bot

    async def update(self, iteration: int) -> None:
        self.iteration = iteration

    async def build_worker(self):
        if self.bot.townhalls.exists and self.bot.can_afford(UnitTypeId.SCV):
            for th in self.bot.townhalls.idle:
                self.commander.issue_train_command(builder=th, to_build=UnitTypeId.SCV)
            for th in self.bot.townhalls.filter(lambda x: (len(x.orders) == 1
                                                           and x.orders[
                                                               0].ability.id == AbilityId.COMMANDCENTERTRAIN_SCV
                                                           and x.orders[0].progress >= 0.95)):
                self.commander.issue_train_command(builder=th, to_build=UnitTypeId.SCV)
        else:
            if self.iteration % 100 == 0:
                logger.warning(
                        f"Can't build worker \n self.bot.townhalls.exists: {self.bot.townhalls.exists}\n self.bot.can_afford(UnitTypeId.SCV):{self.bot.can_afford(UnitTypeId.SCV)}")

    async def control_unit_production(self):  # need to be broken down
        if self.bot.supply_used == 200:
            return

        # build depots when supply is needed soon
        # if self.bot.townhalls.exists and self.bot.can_afford(UnitTypeId.SUPPLYDEPOT):
        #     await self.bot.build_depot()
        # scv building is here to prioritize it together with economy
        # and not when army units are needed
