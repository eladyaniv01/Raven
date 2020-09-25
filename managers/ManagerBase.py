from abc import ABC, abstractmethod

from sc2 import BotAI


class BaseManager(ABC):
    def __init__(self, bot: BotAI) -> None:
        self.bot: BotAI = bot
        self.commander = None
        self.iteration = None

    @abstractmethod
    async def update(self, iteration: int) -> None:
        pass
