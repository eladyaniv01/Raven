from Raven.basebot import BaseBot


class PickleRick(BaseBot):

    def __init__(self, debug=True):
        super().__init__(loglevel="INFO")
        self.debug = debug
        # logger = logging.getLogger(__name__)
        # self.logger = logger
        # saved_stdout = sys.__stdout__
        # import os
        # curdir = os.getcwd()
        # sys.__stdout__ = open(f"log1.log", 'w+')
        #
        # self.logger.add(sys.__stdout__, format=self.log_format, filter=self.log_filter, enqueue=True)
        # sys.__stdout__ = saved_stdout
        # sys.stdout.close()

    def get_log_file(self):
        return 'somelog.log.1'

    async def on_start(self):
        await super().on_start()
        main_townhall = self.townhalls[0]
        self.map_manager.set_base(townhall=main_townhall)

    async def on_end(self, game_result):
        self.logger.info(game_result)
        self.logger.info("buh buh")

    async def on_step(self, iteration: int):
        await self.map_manager.update(iteration=iteration)

    # async def walloff(self, townhall, choke: MapAnalyzer.ChokeArea):
    #     if choke.is_ramp:
    #         build_points = choke.buildables.points
