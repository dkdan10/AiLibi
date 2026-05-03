# ADR 0003: Engine extensions beyond DESIGN.md §3.2 / Appendix A

- **Status:** Accepted
- **Date:** 2026-05-03
- **Author:** Daniel Keinan
- **Section reference:** DESIGN.md §3.2, DESIGN.md §3.4, DESIGN.md Appendix A

## Context

DESIGN.md §3.2 enumerates `WorldState` fields and Appendix A enumerates the
`Action` union. The Phase 1 implementation introduced two extensions not
listed there. This ADR records the rationale so future readers do not assume
spec drift.

## Decision

1. **`WorldState.emergency_uses: Mapping[PlayerId, int]`** — required to
   enforce the per-player emergency-button cap declared in DESIGN.md §3.4
   ("Emergency Meeting: any player can call once per game (configurable)").
   Without this field, the cap is unenforceable. The map YAML controls
   `emergency.uses_per_player`; the `WorldState` field is the live counter.

2. **`RepairSabotageAction`** — required to model the progressive repair
   mechanic. DESIGN.md §3.4 says "crewmates must resolve [sabotage] within N
   ticks"; the implementation models resolution as a per-tick repair action
   accumulating progress against a `repair_ticks` threshold defined per
   sabotage in the map YAML. Treating repair as a single binary action would
   not allow tests to exercise partial repairs or the same-tick-completion
   edge case. The action is impostor-illegal at runtime via the in-vent
   guard and the active-sabotage check; it is not visible to impostors as a
   strategic option in observation packets.

## Consequences

- DESIGN.md §3.2 and Appendix A should be treated as **minimum** contracts;
  the engine may carry additional fields and actions documented in this ADR
  or successors.
- If DESIGN.md is ever revised, fold these into §3.2 and Appendix A and
  retire this ADR.
- Phase 2 boundary contracts (`ActionIntent`) intentionally do **not**
  expose `RepairSabotageAction` to agents — repairs are derived from
  `do_task`-style policies once those are wired. This boundary keeps the
  agent vocabulary aligned with DESIGN.md Appendix A while the engine
  carries the richer action surface.
