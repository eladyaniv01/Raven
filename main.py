import sc2
from sc2.player import Bot, Computer

from Raven.picklerick import PickleRick


def main():
    map = "GoldenWallLE"
    map = "GoldenWallLE"
    map = "AbyssalReefLE"
    sc2.run_game(
            sc2.maps.get(map),
            [Bot(sc2.Race.Terran, PickleRick()), Computer(sc2.Race.Zerg, sc2.Difficulty.VeryEasy)],
            realtime=True
    )


if __name__ == "__main__":
    main()
