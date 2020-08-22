import random
from typing import List

import sc2
from MapAnalyzer import MapData
from sc2.position import Point2, Point3

GREEN = Point3((0, 255, 0))
RED = Point3((255, 0, 0))
BLUE = Point3((0, 0, 255))
BLACK = Point3((0, 0, 0))


class BaseBot(sc2.BotAI):

    def __init__(self, loglevel=None):
        super().__init__()
        self.map_data: MapData = None
        self.logger = None
        self.loglevel = loglevel
        self.home = None

    async def on_start(self):
        if self.loglevel is not None:
            self.map_data = MapData(self, loglevel=self.loglevel)
        else:
            self.map_data = MapData(self, loglevel="DEBUG")
        self.logger = self.map_data.logger

    def get_random_point(self, minx, maxx, miny, maxy):
        return (random.randint(minx, maxx), random.randint(miny, maxy))

    def _get_random_influence(self, n, r):
        pts = []
        for i in range(n):
            pts.append(
                    (Point2(self.get_random_point(50, 130, 25, 175)), r))
        return pts

    def _plot_influence(self, points):
        for tup in points:
            p = tup[0]
            r = tup[1]
            h = self.get_terrain_z_height(p)
            pos = Point3((p.x, p.y, h))
            self.client.debug_sphere_out(p=pos, r=r - 1, color=RED)

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
