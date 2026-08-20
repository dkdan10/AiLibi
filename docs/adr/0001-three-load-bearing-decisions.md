# ADR 0001: Three Load-Bearing Decisions

- **Status:** Accepted
- **Date:** 2026-05-01
- **Author:** Codex
- **Section reference:** DESIGN.md §0

## Context

This ADR records the three load-bearing decisions from DESIGN.md §0 verbatim.

## Decision

1. **Tick-based deterministic engine with a strict observation firewall.** The engine ticks at a fixed rate (target 2 Hz). Agents never touch engine state directly — they receive `ObservationPacket`s filtered by visibility rules. Replays are bit-exact from a seed. This is non-negotiable: it is what makes the system testable, debuggable, and provably non-cheating.

2. **Two-tier agent reasoning.** Tactical decisions (move, do task, follow, vent) are rule-based and run every tick. Strategic decisions (meeting reports, voting, suspicion updates) use an LLM and run only at meetings or specific triggers (witnessing a kill, finding a body). A full game targets ≤ 100 LLM calls. Without this split, cost and latency make the system unviable.

3. **Memory is structured first, natural-language second.** Each agent maintains a typed event log and a derived belief state (trust scores, alibi map, suspicion graph). The LLM sees a *rendered view* of that structure during meetings — never raw chat history as the source of truth. This makes reasoning auditable, testable, and replayable.

## Consequences

All architecture and implementation work must conform to these decisions.

## Note — 2026-08-19: what decision 3's belief state holds at HEAD

Additive note on a 2026-05-01 record: nothing above is rewritten. Decision 3 names
three channels; two are written in production and one is not, so a reader who
quotes the parenthetical gets a claim the tree does not support.

- **`trust` is present but never written outside tests.** `BeliefState.adjust_trust`
  (`agents/memory/beliefs.py`) is defined and covered, and every caller of it in the
  tree is under `tests/`. A live agent's trust score therefore never leaves its
  initial value, and no rendered memory view has ever shown a moved one.
- **The contradictions list is written, but not where it is read from.**
  `apply_contradiction_rule` does call `record_contradiction` — on the derived
  `BeliefState` it returns, not on the agent's persistent store — so the
  `## Open contradictions:` block in `agents/memory/store.py` appeared in **0 of the
  1,656 replay renders** the 2026-08-19 review sampled.
- The **alibi map** is written in production (`agents.memory.store` calls
  `record_alibi` from each public alibi claim), and the suspicion channel is the one
  the deterministic fold carries between meetings.

This note records the gap. Repairing the substrate is a separate contract; until one
lands, "trust scores" above is a design intent, not a description of HEAD.
