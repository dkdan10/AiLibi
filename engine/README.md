# Simulation engine

The engine advances deterministic state from validated actions. See
[architecture](../docs/architecture.md) for the observation boundary, replay
contract, and package responsibilities.

Maps support **one tick per room edge or vent action**. `Edge` and `Vent`
validation rejects other traversal durations: the engine has no in-transit
state, and public pathing and meeting geometry use adjacency hops. Task,
sabotage, and cooldown durations remain independently configurable.

Load custom YAML through `engine.world.load_map` so unsupported timing and
invalid topology fail before a simulation begins. Supporting longer traversal
would require a coordinated engine, observation, pathing, reasoning, and
spectator change, with explicit recording compatibility.
