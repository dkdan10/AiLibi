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
