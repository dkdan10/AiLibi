# Game shape

Five rules shape every game the default configuration plays. Each section names
the code that enforces its rule. An experiment can change one of them only
through a recorded experiment field, and none of those experiments has been
adopted. [The architecture note](architecture.md) links here;
[the observation contract](observation-contract.md) defines what each player is
entitled to see.

## Venting is visible

Only impostors vent. `engine.rules.resolve_vent` lists every living player
standing in the room the impostor leaves, and in the room it arrives in, as a
witness to the vent, and the observation layer shows each witness the vent as
that player's action. At a meeting, a spoken vent claim that matches the
speaker's own witness record becomes a public `vent_sighting`
[flag](glossary.md#flag-minting-stamping-a-contradiction-into-the-transcript)
(`meetings.transcript.detect_contradictions`). A vent claim with no matching
record raises no flag.

## Impostors never report

The default impostor policy, `agents.tactical.impostor_policy.ImpostorPolicy`,
never asks to report a body or to call an emergency meeting. When a body lies in
its room it walks away, or vents away when the room has a vent and nobody but a
teammate is there to see. Impostor self-report exists only as an experiment
(`self_report`), off by default.

## Actions resolve in player-id order

`orchestrator.action_ordering.order_actions_for_tick` sorts each tick's actions
by player id, and `engine.tick.advance_tick` applies them in that order. When an
action opens a meeting, `advance_tick` returns at once: the actions of players
later in the order are dropped for that tick, and the end-of-tick updates (kill
cooldowns, sabotage timers and task progress) do not run.

## Meetings pause the world

Until the coherent meeting-reset experiment (`meeting_reset`, default
`preserve`) is adopted, a meeting changes the map in two ways only: it removes
the reported body and, on an ejection, the ejected player.
`orchestrator.game.apply_meeting_result` removes only the body that was
reported, so every other corpse stays where it fell, and players resume where
they stood.
Kill cooldowns do not count down across a meeting: `engine.tick._decrement_cooldowns`
runs only among the end-of-tick updates of a play tick, which neither the tick
that opened the meeting nor the meeting itself runs.

## Crewmates see one room

At the map's base visibility, `engine.visibility._resolve_observer_visibility_mode`
limits a crewmate to its own room, while an impostor also sees the adjacent
rooms. An active lights sabotage limits everyone to their own room. The map
file's comment that visibility is uniform across the map describes its base
setting, not what each role sees.
