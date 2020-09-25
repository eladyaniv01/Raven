from sc2 import BotAI

from .ManagerBase import BaseManager


class MicroManager(BaseManager):

    def __init__(self, bot: BotAI) -> None:
        super().__init__(bot)

    async def update(self, iteration: int) -> None:
        pass
