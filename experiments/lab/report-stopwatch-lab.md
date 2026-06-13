# Lab report — Stopwatch sensitivity (Tier 1)

**Decision informed:** Wave-2 balance knobs + the 10.13 gate (model any clock change
before tuning it). **Rubric:** R1 (deduction decides), R5 (varied win paths).
**Date:** 2026-06-13. **Inputs:** W0 committed facts + Wave-1 attempt-1 facts (seed 8
excluded). Method: per task win, extrapolate impostor time-to-parity at the game's
observed kill cadence from the game-over tick; `flip_margin` = ticks of task-clock slack
before parity plausibly arrives; sweep slowdown Δ. **Upper bound on flips** — assumes
constant cadence and no added meetings/ejections in the window (Wave 1 exists to make
that assumption false), no game-state propagation.

## Results (near-identical across both sets)

- Flip-margin quartiles: ~[2.5, 6, 13, 21, 48–64] ticks (W0: 47 wins; W1a: 45).
- Plausible flips at task-clock slowdown Δ:

| Δ (ticks) | 2 | 4 | 6 | 8 | 12 | 16 | 24 |
|---|---|---|---|---|---|---|---|
| W0 flips (of 47) | 0 | 5 | 12 | 17 | 22 | 28 | 41 |
| W1a flips (of 45) | 0 | 8 | 10 | 15 | 22 | 24 | 39 |

## Reading

1. **The task clock is a hair-trigger balance knob.** One mean kill-interval of slowdown
   (~6 ticks) plausibly flips ~25% of ALL outcomes; 12 ticks flips ~half; 24 flips ~85%.
   Any Wave-2 balance change must move in 2–4-tick steps with the anti-railroad and
   conversion gates watching — and never be judged by the win split, which this curve
   shows can be bought wholesale.
2. **The photo-finish band is real but not universal:** ~quarter of wins sit within 6
   ticks of a flip, while the top quartile has 21+ ticks of slack. Tightening the race
   uniformly would overshoot the loose games before it touches the tight ones — a
   per-game pacing lever (more meetings, the 10.8 emergency channel) is finer-grained
   than a global clock change.
3. **Wave-1's counterweight matters:** every tick of added runway is also an ejection
   opportunity under the new conversion machinery, so realized flip rates will sit below
   this curve. Re-run on the fresh 10.9 bytes to see how much the conversion layer bends
   it.

Raw rows: `results-stopwatch-lab.json`.
