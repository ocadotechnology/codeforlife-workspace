# aimmo-game-creator

## Game Creator

The game creator consists only of a few classes. The service runs a worker manager daemon which periodically updates the games. The list of the games is exposed through the game API.

The data is managed by a thread-safe class. The synchronisation is done using a lock over the set of running games. The games that are no longer running are removed. The updates are made in parallel by multiple threads, thus the need for synchronisation.

_This class will be removed soon. (15 July 2021)_
