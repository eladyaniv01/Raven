from sc2 import BotAI

from .ManagerBase import BaseManager


class ProductionManager(BaseManager):
    def __init__(self, bot: BotAI) -> None:
        super().__init__(bot)
