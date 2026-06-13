# Lab report — Decay sweep + emergence census (Tier 1)

**Decisions informed:** the deferred decay-rate revisit (verdict: stays deferred, now with
a mechanism reason); R6 upside hunt + Wave-2 inputs. **Date:** 2026-06-13.
**Inputs:** W0 facts (clean 9.8 semantics) + Wave-1 attempt-1 facts (directional only —
pre-vote folds conflate its transitions). Raw: `results-decay-emergence.json`.

## Decay sweep — a clean negative finding

Method: validate the §6.3 single-step model (decay 25% + 0.05 accused-bump) against every
observed (crew voter, subject) consecutive-meeting transition; sweep d ∈ {0.10, 0.25,
0.40} on the VALIDATED subset only (82 transitions on W0; 49% excluded as
involving other rules — Rule 3 etc. — excluded, never mis-modeled).

Result: **decay rate is INERT at current runway.** From-below 0.60-crossings: 0 at every
d. Carry survival ≥ 0.55: 36/82 at every d — identical. The 0.05 quantization lattice
swallows one-step decay differences entirely (a 0.55 carry dies to ~0.53–0.545 under any
d; a 0.60 survives under any d). Decay choice only opens up over 3+ COMPOUNDING quiet
meetings, which current pacing almost never supplies.

**Decision input:** the deferred decay decision stays deferred on mechanism, not taste —
it physically cannot matter until 10.8's pacing delivers 3+ meeting chains. Revisit after
the fresh 10.9 bytes with a chained re-fold model; until then any decay tuning would be
unmeasurable.

## Emergence census (v1)

- **E2 — impostor self-accusation is a recurring class: 8–9 per set, impostor-spoken in
  the sampled cites** (seed 12 m0 p-1 — the same meeting as PR #147's F2: the impostor
  self-accused in the opening, crew adopted the target, ejected him 3-2-2). The old
  seed-40 class never died; it has game-deciding consequences and the 10.9.2 target guard
  does NOT touch it (a self-accusation adopted by over-gate voters is graph-unconstrained
  target adoption — F2's seam). Watch on the fresh bytes.
- **E3 — impostor reporters: 0 on both sets.** Confirms the structural finding: the
  report channel is policy-unreachable for impostors. Wave-2's self-report affordance is
  greenfield, not a tuning.
- **E1 — impostor over-gate skips: ~44 raw rows per set, PROVISIONAL** — the census
  filter needs the living-target restriction before this is comparable to the standing
  missed_skip partition (28/33, all impostor voters). The confirmed STRATEGIC instance
  remains the seed-10 pair (skipping to protect a steered wrong target). Refine filter at
  the next census pass.
- **E4 — accusation-less openings: 2–3 per set** (the known lost-opening residue).

**Net for the rubric:** R6's confirmed-class list grows to two (strategic skips,
impostor self-accusation — one strategic, one artifact-with-consequences), with E3's zero
as the structural baseline Wave-2 will move.
