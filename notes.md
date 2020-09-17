http://satirist.org/ai/starcraft/steamhammer/1.3/

At the top level, the project has 2 parts.

BOSS - Build Order Search System for creating production plans, capable and easy to use but somewhat buggy. Used in StrategyManager for terran and protoss; not used for zerg.
Steamhammer - The bot proper.
Here are some of the important classes in the Steamhammer source. The entry point is UAlbertaBotModule, which sets things up and then passes control for each game event to GameCommander. Then GameCommander calls on the various other modules to do the work.

- BuildingManager - Keep a queue of buildings to construct, and construct them, solving any problems (“oops, that spot turned out to be blocked”). Takes its orders from ProductionManager.
- FAP - FastAPproximation combat simulator, to estimate whether a potential battle will be won or lost. Written by N00byEdge and included under its own MIT license.
- CombatCommander - In charge of squads and overall tactics. Passes orders to Squad objects.
- InformationManager - Keeps track of units (especially enemy units that have been seen), bases, and so on.
- MapGrid - Keeps track of the locations of units by grid square, for lookup by location. Also remembers when each part of the map is explored.
- Micro - Sends commands to units, being careful not to spam commands.
- MicroManager - Parent class for making unit-level decisions during play, like what target to attack. Child classes are MicroMelee, MicroRanged, MicroTransports, etc.
- ParseUtils - Read the configuration file and set configuration variables to match. If you want to add a new configuration variable, put it in Config.h and give it a default value in Config.cpp, then parse its configured value and set the variable in ParseUtils and you are done.
- ProductionManager - Given a queue of stuff to produce, produce it as possible.
- Squad - A squad of combat units, which accepts general orders from CombatCommander and passes more specific orders down to the various micro managers.
- StrategyManager - Decide how to spend minerals and gas: Build/research these things in this order, starting with the opening build order and continuing. Creates the queue that ProductionManager works through.
- WorkerManager - Responsible for most of the stuff that workers do, mining and building and repair.