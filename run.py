import lzma
import pickle

from MapAnalyzer.MapData import MapData
from MapAnalyzer.utils import import_bot_instance

map_file = "AbyssalReefLE.xz"
# noinspection PyUnboundLocalVariable
with lzma.open(map_file, "rb") as f:
    raw_game_data, raw_game_info, raw_observation = pickle.load(f)

bot = import_bot_instance(raw_game_data, raw_game_info, raw_observation)
map_data = MapData(bot, loglevel="DEBUG")
# map_data.plot_map()
# map_data.show()
base = map_data.bot.townhalls[0]
home = reg_start = map_data.where(base.position_tuple)
reg_end = map_data.where(map_data.bot.enemy_start_locations[0].position)
p0 = reg_start.center
p1 = reg_end.center
# influence_grid = map_data.get_pyastar_grid()
influence_grid = map_data.get_air_vs_ground_grid(default_weight=100)
map_data.plot_influenced_path(start=p0,goal=p1, weight_array=influence_grid)
map_data.show()
# ramps = reg_end.region_ramps
#
# if len(ramps) > 1:
#     if map_data.distance(ramps[0].top_center, reg_end.center) < map_data.distance(ramps[1].top_center, reg_end.center):
#         ramp = ramps[0]
#     else:
#         ramp = ramps[1]
# else:
#     ramp = ramps[0]
#
# # position = map_data.closest_towards_point(points=home.polygon.perimeter, target=ramp.center)
# # position = (position[0], position[1]) # into tuple
# logger.info(f"type ramp.center = {type(ramp.center)}")
# logger.info(f"ramp.center = {ramp.center}")
# home.plot()
# import matplotlib.pyplot as plt
#
# placement_arr = map_data.placement_arr.T
# # logger.info(position)
# # plt.text(position[0], position[1], '?', fontsize=40)
# # logger.info(f"buildability [ps] [{position}]:  {map_data.placement_arr[position[0]][position[1]]}")
# # buildable_indices = np.where(home.polygon.array.T == map_data.placement_arr, 1, 0)
# parr = map_data.points_to_numpy_array(home.points)
# buildable_indices = np.where(parr == 1)
# logger.debug(np.unique(parr))
# logger.debug(f"len buildable_indices = {len(buildable_indices)}")
# # # plt.imshow(buildable_indices, origin="lower")
# # # plt.text(position[0], position[1], '$$$', fontsize=40)
# # # plt.show()
# buildable_points = []
# _points = list(map_data.indices_to_points(buildable_indices))
# for i, p in enumerate(_points):
#     if placement_arr[p] == 1:
#         # print( i, p )
#         buildable_points.append(p)
# # buildable_points = [Point2((p[0], p[1])) for p in buildable_points if map_data.placement_arr[p] == 1]
# if len(buildable_indices) > 0 and len(buildable_points) > 0:
#     logger.debug(f"len buildable points = {len(buildable_points)}")
#
#     # logger.debug(f"len buildable points = {len(buildable_points)}")
#     # build_point = map_data.closest_towards_point(target=(ramp.center), points=buildable_indices)
#     pos = int(ramp.top_center[0]), int(ramp.top_center[1])
#     build_point = map_data.closest_towards_point(target=pos, points=buildable_points)
#
#     area = map_data.where(build_point)
#     logger.debug(repr(area))
#     plt.text(build_point[0], build_point[1], '$', c='r', fontsize=40)
#     logger.info(f"buildability [bp] [{build_point}]:  {placement_arr[build_point]}")
#     x, y = zip(*buildable_points)
#     # plt.imshow(map_data.placement_arr.T, origin="lower")
#     plt.scatter(x, y, c='r', s=1)
#
#     plt.show()
# else:
#     logger.warning("Warning")
