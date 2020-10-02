from sc2 import BotAI

from .ManagerBase import BaseManager


class WorkerManager(BaseManager):
    def __init__(self, bot: BotAI) -> None:
        super().__init__(bot)
        self.builder_tags = []
        self.builders = []

    async def update(self, iteration: int) -> None:
        pass

    def _set_builders(self):
        self.builders = self.bot.units.tags_in(self.builder_tags)

    def get_builder(self, location):
        self._set_builders()
        if len(self.builders) > 0:
            for builder in self.builders:
                if builder.is_idle:
                    return builder

        # no idle builder found,  need to assign a new one
        if self.bot.workers.idle.exists:  # we probably wouldn't want to pick an idle worker on the other side of the map
            builder = self.bot.workers.idle.closest_to(location)
            self.builder_tags.append(builder.tag)
            return builder
        else:
            builder = self.bot.workers.gathering.closest_to(location)
            self.builder_tags.append(builder.tag)
            return builder

        # some edge cases will be handled outside this class,
        # such as if we have only 2 workers,
        # we dont want to build stuff, we want to train more workers
