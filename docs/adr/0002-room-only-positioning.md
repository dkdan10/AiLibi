# ADR 0002: Room-only positioning for MVP

- **Status:** Accepted
- **Date:** 2026-05-03
- **Author:** Daniel Keinan
- **Section reference:** DESIGN.md §3.2, DESIGN.md §8.3

## Context

DESIGN.md §3.2 declares `PlayerState.position: tuple[float, float]`
("within-room coords"), but §8.3 says "agents are 'in' a room" — the spatial
granularity for MVP is the room graph, not within-room coords. The two
statements are in tension.

The kill-radius check at `engine/rules.py` enforced
`dist(actor.position, target.position) <= _KILL_RADIUS`, but the move action
only updates `room`, never `position`. As soon as players moved, positions
went stale and the radius check became meaningless — kills would silently
become impossible after the first move because every player's position is
the spawn position.

## Decision

For MVP, gameplay granularity is **room-only**:

- Co-presence in a room is sufficient for kill, vent witness, and visibility.
- The `_KILL_RADIUS` check is removed. A kill is valid when actor and target
  are in the same room, the target is alive, the actor is an impostor, and
  the kill cooldown is zero.
- The `PlayerState.position` and `BodyState.position` fields are retained as
  vestigial type-stable placeholders for the eventual pixel-level rendering
  path; they are not authoritative for any rule.

## Consequences

- Phase 2 pathing operates on the room graph; A* edges are room-to-room.
- Phase 4 spectator UI may continue to use `position` for layout rendering
  only.
- Should we ever introduce within-room rules (e.g., line-of-sight occlusion
  within a room), we will write a follow-up ADR overriding this one.
