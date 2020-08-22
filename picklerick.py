from sc2.position import Point3

from Raven.basebot import BaseBot

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class PickleRick(BaseBot):

    def __init__(self):
        super().__init__(loglevel="INFO")

    async def on_start(self):
        await super().on_start()

    async def on_step(self, iteration: int):
        pass
