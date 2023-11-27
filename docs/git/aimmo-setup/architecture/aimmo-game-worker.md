# aimmo-game-worker

The game worker is part of the `game_frontend`. Its responsibility is to run the player's code to get an action with any logs for a particular turn in the game.

The code for the worker is split up in two places:

* The `aimmo-game-worker` directory which holds the worker API source code for the player.
* The corresponding [Pyodide runner](https://github.com/ocadotechnology/aimmo/tree/development/game\_frontend/src/pyodide) which uses the worker API to run the player's code.

**How the Avatar Worker works**

![How the Avatar Worker works diagram](../../../.gitbook/assets/avatar\_worker\_diagram.svg)

The worker receives a game state of the current turn. It converts this into a representation of the world map and the avatar state. These are then passed to the player's `next_turn` function. We collect the action returned from that function call along with any logs produced (via print statements or errors for example) to produce a `ComputedTurnResult` for the next turn.

#### Responding to player's code changes

When the player changes the code for their avatar, we redefine the `next_turn` function in Pyodide and then recompute their `next_turn` action with the new code. In the case of syntax errors with their code, we don't compute their `next_turn` and return a `WaitAction` with the errors they had in the logs.
