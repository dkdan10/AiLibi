# Experiments Lab

Standing experiment program (owner-commissioned 2026-06-13, design thread): comprehensive
tests/experiments against the game's DESIRED behavior, so decisions moving forward are
informed — and to find upside the current design hasn't asked for.

## Governance

- Every experiment names, up front, the DECISION it informs (a wave contract, a parked
  owner call, a Phase-11 brief item). No decision named → not run.
- Every experiment ships a one-page report in this directory: hypothesis → method →
  result → decision input. Scored against `rubric.md` where applicable.
- Frozen production constants STAY FROZEN (§4.6 render/threshold, tally, token caps, 9.8
  accumulator constants). Experiments inform owner decisions; they never silently become
  them.
- No committed sample dir is ever touched. Live recordings go to scratch dirs and die with
  their branches. Counterfactual labs read committed bytes (or evidence-branch bytes via
  `git show`) and write only reports here.
- Live-model tiers respect the wave in flight: read-only probes run anytime;
  prototype-affordance scratch games (Tier 3) run only between measurement eras
  (freeze-during-measurement).
- Counterfactual caveat, stated in every report that applies: replayed-ballot/timeline
  counterfactuals do NOT propagate game state (an early ejection changes everything after
  it). They yield per-meeting/per-tick deltas, never re-simulated win splits.

## Tiers

- Tier 0 — `rubric.md`: the measurable desired-behavior spec everything scores against.
- Tier 1 — offline counterfactual labs on existing bytes ($0): tally variants, stopwatch
  sensitivity, decay-vs-cadence, emergence census.
- Tier 2 — live qwen probe batteries (`experiments/model_probe` extensions): deception
  battery (the 10.10 gate pulled forward), capability-ceiling probes, model-ceiling A/B.
- Tier 3 — scratch micro-sets: prototype affordances on throwaway branches, 5-10 games,
  rubric-scored. Held until the active measurement era closes.

Capstone: a synthesis memo feeding the Wave-2 contracts, the parked owner calls (gp-8
tally, decay rate, balance knobs), and the Phase-11 front-end brief.
