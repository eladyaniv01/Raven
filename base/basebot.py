from typing import Any, Dict, List

import sc2
import yaml
from loguru import logger
from sc2.position import Point2, Point3

from Raven.game_version import VersionManager
from Raven.managers.ConstructionManager import ConstructionManager
from Raven.managers.MapManager import MapManager
from Raven.managers.ProductionManager import ProductionManager
from Raven.managers.WorkerManager import WorkerManager

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))

LOG_FORMAT = "<w><bold>{time:YY:MM:DD:HH:mm:ss}|" \
             "<level>{level: <8}</level>|<green>{name: ^15}</green>|" \
             "{function: ^15}|" \
             "{line: >4}|" \
             "<level> {level.icon}  {message}</level></bold></w>"


class LogFilter:
    def __init__(self, module_name: str, level: str = "ERROR") -> None:
        self.module_name = module_name
        self.level = level

    def __call__(self, record: Dict[str, Any]) -> bool:
        # return True
        if "raven" in record["name"].lower():
            levelno = logger.level(self.level).no
            return record["level"].no >= levelno
        return False


CONFIG_FILE = 'Raven/config.yaml'


class BaseBot(sc2.BotAI):

    def __init__(self, loglevel=None):
        super().__init__()
        self.iteration = 0
        self.loglevel = loglevel or "ERROR"
        self.map_manager = MapManager(self, loglevel=self.loglevel)
        self.construction_manager = ConstructionManager(self)
        self.version_manager = VersionManager()
        self.production_manager = ProductionManager(bot=self)
        self.worker_manager = WorkerManager(bot=self)
        self.log_filter = LogFilter(module_name='picklerick', level=self.loglevel)
        self.log_format = LOG_FORMAT
        with open(CONFIG_FILE, "r") as config_file:
            self.config = yaml.safe_load(config_file)
        self.debug = self.config["Debug"]
        # logger.add(sys.stderr,  filter=self.log_filter)

    def on_end(self, game_result):
        super().on_end(game_result)

    async def on_start(self):
        await self.version_manager.handle_game_version(self.client)
        self.map_manager.initialize()

    async def on_step(self, iteration: int):
        self.client.game_step = int(self.config["GameStep"])
        self.iteration = iteration
        # logger.info(f"{iteration}")
        pass

    def get_builder(self, location):
        return self.worker_manager.get_builder(location=location)

    def _draw_point_list(self, point_list: List = None, color=None, text=None, box_r=None) -> bool:
        if not color:
            color = GREEN
        for p in point_list:
            p = Point2(p)
            h = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h))
            if box_r:
                p0 = Point3((pos.x - box_r, pos.y - box_r, pos.z + box_r)) + Point2((0.5, 0.5))
                p1 = Point3((pos.x + box_r, pos.y + box_r, pos.z - box_r)) + Point2((0.5, 0.5))
                self.client.debug_box_out(p0, p1, color=color)
            if text:
                self.client.debug_text_world(
                        "\n".join([f"{text}", ]), pos, color=color, size=30,
                )

