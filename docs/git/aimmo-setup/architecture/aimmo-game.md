# aimmo-game

## Game Components

* Game Runner
* Simulation Runner
* Map Generator
* World Map
* Avatar
* Actions
* Pickups
* Interactables

**In Short**

* Maintains game state
* Simulates environment events
* Collects and runs player actions

**General Overview**

The game (aimmo-game) is responsible for maintaining the game state, the worker avatars for the game, fetching the actions from each worker, and applying those actions, as well as fetching game metadata from the Django API.

The game interacts with the rest of the components as follows:

* It is created by the game creator.
* Collects actions (see `turn_collector.py`) computed by the player's client (see [Workers](aimmo-game-worker.md))
* Sends game states once per turn to the clients

Once per turn it will:

* Inform all workers of the current game state and gets their actions.
* Perform conflict resolution on these actions and then apply them.
* Update the world with any other changes to produce the next game state.

## Game Runner

The `GameRunner` class is responsible for initialising the games' components in order to spawn a new game. It holds a reference to these objects and has some getter functions defined in order to spawn or delete new users.

More importantly, it contains the `update()` function which runs in a loop at 2 seconds intervals. This constantly uses the embedded communicator object to get the game metadata from our Django API url.

Once this information comes in it manages the changes in users that need to happen (i.e. finds users that need to be added or deleted). It then delegates the responsibility to the worker manager which handles the worker pods and their code. Finally the game state holds all new avatars for these users.

The `GameRunner` should be the **only** class which has interactions with both _simulation logic_ (avatar wrappers, game map etc) and _worker logic_ (`WorkerManager`). This is an important decoupling.

The `GameRunner` updates the avatars and the simulation.&#x20;

## Simulation Runner

The `SimulationRunner` updates the environment (through the `map_updaters.py`) and is responsible for running a turn in the simulation.

The `run_turn` method is called from `GameRunner`, and it runs as follows:

* Get the `AvatarWrapper`'s to deserialise and register their actions.
* Update the environment using the World Map.

The alternatives for pooling each avatar for its decisions are:

* SequentialTurnManager (used locally for testing) - get and apply each avatar's action in turn
* ConcurrentTurnManager - concurrently get the intended actions from all avatars and register them on the world map; then apply actions in order of priority

## Map Generators

The generators are map creation services. The Django application is exposed to different map creation service classes. There is a map generation service as part of the Django application which uses the default map generator: the class Main in the `map_generator.py` file.

A map generator is a class that inherits from BaseGenerator and has to implement the `get_map` method.

**The Main Map Generator**

The main map is supposed to be used for the generation of big worlds. This should be the only generator used at this time. The whole map is randomly generated, but the generation is regulated by the World Map settings.

Obstacles are filled according to the obstacle ratio. Once an obstacle is added we ensure that each habitable cell can reach each other, thus the map will be connected and each generated avatar can reach others.

## World Map

The World Map is the central component of the simulation. The class itself consists of a grid and a set of JSON settings. The grid consists of a dictionary of cells.

#### Cells

A cell has the following components:

* location - (x, y) pairs that can be added together, serialised, compared, etc.
* [avatar](aimmo-game.md#avatar)
* [interactable](aimmo-game.md#interactable)&#x20;
* obstacle (the avatar can't get to the obstacle cell)
* actions - a list where the intended actions of different avatars are registered and, afterwards, applied

## Avatar

This represents an avatar as part of the simulation.

**AvatarWrapper**

The avatar wrapper represents the application's view of a character. The main functionality is:

* decide action - given a serialised representation of an action, return a Python action object.
* clear action
* update effects - apply effects that come from getting a pickup
* add event - attaches an event (e.g. move, pick up) to the event setting
* backpack - a list of artefacts that it can carry

**AvatarManager**

This is responsible for adding and removing avatars and managing the list of avatars that the main game simulation has access to. It is kept in sync with the `Worker`s in `WorkerManager` by `GameRunner`.

## Actions

An action is a pair (avatar, location). The action is registered onto the WorldMap by being appended to a cell. The examples of actions are wait, move, and pick up.

The action is processed by calling the `apply` function only if the action is legal. Legal actions for `MoveAction` for instance:

* The square the avatar attempts to move to is on the map
* The square the avatar attempts to move to is not occupied (by e.g. another avatar or a wall)
* Another avatar is not attempting to move to the same square.

There's also a `reject` function, applied when the actions are illegal. The `PickupAction` for instance can be rejected if your backpack is full or if there's no artefact on the cell, and in this case error messages will be printed out to the player console.&#x20;

## Interactable

An `Interactable` is a dynamic object that exists in the `WorldMap`.

All Interactables follow the same basic logic: CONDITIONS → EFFECTS → TARGETS

This is to say that an `Interactable` has 1 or more conditions it's checking for. Once the **conditions** are met, it will apply any **effects** it has to 1 or more specified targets. Currently the only compatible target is an avatar.

**Conditions**

A condition can be thought of as a function, any and all conditions must be something that can evaluate to either `True` or `False`. Each turn, all of an Interactable's conditions are evaluated to see if its effects should trigger.

Conditions will typically need some kind of data to check. Conditions currently can only use information from the `WorldMap` for their checks.

**Effects**

An effect should have at least one target.

When an Interactable's conditions are met, the targets are gathered, and the effects are then given to them. Targets for an effect (such as avatar) must have an `effects` attribute with which to store its active effects.

An effect can last 1 or many turns, and can impart a temporary or permanent change to its target.

**Pickups**

Each pickup extends `Interactable`. It is an object that can be picked up by the avatar. When picked up, it  disappears from the map and generates an effect.

