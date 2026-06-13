# Lab report — Tally counterfactuals (Tier 1)

**Decision informed:** gp-8 (parked owner call: SKIP-plurality / tie semantics). Secondary:
Wave-2 gate design, R1 conversion ceiling sizing.
**Rubric items:** R1 (deduction decides), R4 (no railroads — the cascade-cost column), R5.
**Date:** 2026-06-13. **Inputs:** W0 committed bytes (main, 78 meetings, facts via the audit
extractor) + Wave-1 attempt-1 evidence bytes (PR #147 @ 5fdba2c, 87 meetings, seed 8
excluded — aborted game). Ballot `confidence` added to the extractor's facts for this lab.

## Hypothesis

The strict SKIP-plurality bloc is the binding cap on conversion (the close audit's b1
finding: 1–3 over-gate voters lose to 4–7 mandatory skips). Relaxing the tally converts
parked over-gate ballots — the question is the innocent-ejection cost per impostor gained.

## Method

Replay every recorded meeting's ballots under tally variants; V0 (production rule,
SKIP competes + confident-leader prong) recomputed as a self-check — **V0 matched every
recorded outcome on both sets** (0 mismatches), so the variant deltas are exact.
Variants: V1 option-c (SKIPs abstain, floor 2), V2 non-SKIP majority (floor 2),
V3 skip-halfweight (soft bloc, floor 2). All variants are monotone relaxations — they can
only add ejections, never remove or swap one. **No game-state propagation** (per-meeting
yields, not re-simulated wins; an early flip changes everything after it in a real game).

## Results (SKIPPED→EJECTED flips, by ejected role)

| variant | W0 bytes: imp gained / innocent created | W1-attempt bytes: imp / innocent |
|---|---|---|
| V1 option-c | **+18 / 4** (4.5:1) | **+15 / 8** (1.9:1) |
| V2 non-SKIP majority | +17 / 4 | +15 / 8 |
| V3 skip-halfweight | **+8 / 0** | **+5 / 2** |

(Recorded V0 actuals for scale: W0 ejected 5 impostors / 7 innocents across 78 meetings;
W1-attempt 12 / 7 across 87.)

## Reading

1. **The bloc is real and large.** On the honest W0 bytes, option-c would have converted
   18 additional impostor meetings — 3.6× the 5 ejections that actually happened. The
   parked-listener mass the close audit identified is not a rounding error; it is the
   single largest unconverted store of correct suspicion in the system.
2. **But the cost curve moved after testimony ingestion.** On the W1-attempt bytes,
   option-c's impostor:innocent ratio collapses from 4.5:1 to 1.9:1 — the 10.7 fold
   already harvested the cleanest conversions into V0 itself AND lifted more innocents
   over the gate where a relaxed tally would eject them. **Tally relaxation and testimony
   ingestion compete for the same conversions, and the tally is the blunter instrument
   post-10.7.** Any analysis done on pre-Wave-1 bytes overstates the tally's appeal.
3. **If the bloc is ever revisited, the shape is V3, not option-c.** Skip-halfweight
   gains +8 impostors at ZERO innocent cost on W0 (+5/+2 on W1-attempt) — it preserves
   the bloc's anti-cascade function while letting a clear eject signal through. Option-c's
   floor-2 lets 2 confident voters override 6 skips, which is exactly the cascade shape
   the owner principle exists to prevent.
4. **R4 note:** every variant ejection is individually graph-consistent (only ballots
   that already passed §4.6 are re-weighed; no new signal classes) — the cost column is
   about VOLUME of honest-mistake ejections, not railroads.

## Decision input

Keep gp-8 PARKED, now with evidence instead of taste: 10.6+10.7 are eating the same
conversion mass with a finer tool. Re-run this lab on the fresh 10.9 bytes; revisit the
tally only if genuine/multi-signal conversion plateaus despite testimony + pacing — and
then start from the V3 shape. Detail rows for spot-checks: `results-tally-lab.json`.
