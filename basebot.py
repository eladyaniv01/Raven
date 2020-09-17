import sys
from typing import Any, Dict, List

import sc2
from loguru import logger
from sc2.position import Point2, Point3

from Raven.game_version import VersionManager
from Raven.managers.ConstructionManager import ConstructionManager
from Raven.managers.MapManager import MapManager

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))

LOG_FORMAT = "<w><bold>{time:YY:MM:DD:HH:mm:ss}|" \
             "<level>{level: <8}</level>|<green>{name: ^15}</green>|" \
             "{function: ^15}|" \
             "{line: >4}|" \
             "<level> {level.icon} {message}</level></bold></w>"


class LogFilter:
    def __init__(self, module_name: str, level: str = "ERROR") -> None:
        self.module_name = module_name
        self.level = level

    def __call__(self, record: Dict[str, Any]) -> bool:
        # return True
        levelno = logger.level(self.level).no
        return record["level"].no >= levelno


class BaseBot(sc2.BotAI):

    def __init__(self, loglevel=None):
        super().__init__()
        self.loglevel = loglevel or "DEBUG"
        self.map_manager = MapManager(self, loglevel=self.loglevel)
        self.construction_manager = ConstructionManager(self)
        self.version_manager = VersionManager()
        self.logger = sc2.main.logger
        self.log_filter = LogFilter(module_name='picklerick', level=self.loglevel)
        # self.logger.remove()
        self.log_format = LOG_FORMAT
        self.logger.add(sys.stderr, format=self.log_format, filter=self.log_filter)
        # self.logger.add(f"logs/log1.log", format=self.log_format, filter=self.log_filter)

    async def on_start(self):

        await self.version_manager.handle_game_version(self.client)
        self.map_manager.initialize()

    async def on_step(self, iteration: int):
        pass

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

