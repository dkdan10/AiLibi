# Task 11.8 finalize — re-anchor era pins to the Wave-3 baseline

**Branch:** `phase-11-wave3-rerecord`. **Status:** the Wave-3 combined re-record is **DONE and committed on
this branch** (both sets, byte-clean determinism), with the reactor sabotage `duration_ticks` tuned 7→6.
**DO NOT re-run `refresh_samples.sh`.** Your job: **re-anchor the 15 era-pin tests** to the committed
baseline, run the 11.8 gates, get `bash scripts/check.sh` green, then open a PR to main.

## What landed (verified)
- `verify_samples.sh` + `verify_samples.sh replays/samples/9p2i` → **"All 50 samples verified clean"** ×2.
- The flat 4p/1i replays are **byte-identical** to before (sabotage never fires at 4p/1i — the 6/7 fraction
  keeps it out — so the Wave-3 code is additive there); only the **9p2i** set + manifests changed.
- **9p2i (50 games):** sabotage fires **30/50 (60%)**, `IMPOSTOR_SABOTAGE` wins **0/50** (pure stall, owner
  intent). The stall shifts `CREWMATE_TASKS` 40→37 into `IMPOSTOR_PARITY` 4→7: impostor win 8%→14%,
  task-stopwatch 80%→74%. **Rubric: R5 win-shape diversity 3→4** (impostor-win crossed 10%), interestingness
  mean 44.8→45.1, **R1 eject-decided held at 6/50**.

## Verdict: data-drift, NOT regression (verify per channel)
The substrate is byte-clean and the shifts track the intended Wave-3 behavior (the sabotage stall + the
win-mix change). This is the documented "re-anchor era pins after a re-record" cadence (account-don't-rule-
change) — **not** blind pin-swapping:
- **Value pins** (counts/rates): re-anchor to the new computed value (the assertion shows `actual == old`),
  after confirming the move is explained by Wave 3 (sabotage stall; more weak flags from richer meetings).
  Notably `flags 95→112` (still **0 strong** — vents intact), `do_task 378→380`, gate metrics ±1–2.
- **`tests/meetings/test_manager.py::...test_seed3_m0_defended_subject_corroborated_not_folded`** raises
  `IndexError` — seed-3 plays out differently now (the indexed turn/meeting moved), so this one is a
  STRUCTURAL re-anchor: re-derive the expectation from the new seed-3 bytes, don't just bump a number.
- **`tests/eval/test_gate_spec_metrics.py::...corrected_w2_baseline_matches_a_rederivation`** + the
  `ejections_decompose` dict: re-derive `tests/fixtures/phase10/corrected_w2_baseline.json` (and the decomp
  dict) by running the relevant analyzer over the new `replays/samples/9p2i` — the test shows the entry point.
- **INVARIANT checks must still hold** (verify, don't pin away): `threshold_inversions` 0, friendly-fire 0,
  betrayal 0, no railroads, firewall/leak clean. If a genuine invariant is violated, STOP and escalate.

## The 15 failing tests
- `tests/eval/test_gate_metrics.py` (×1), `tests/eval/test_vote_correctness.py` (×1),
  `tests/eval/test_wave2_metrics.py` (×3: conv-per-meeting, effective-deflection, indistinguishability),
  `tests/eval/test_gate_spec_metrics.py` (×4 incl. the `corrected_w2_baseline` re-derivation + the
  ejections-decompose dict): shipped gate/eval pins.
- `tests/meetings/test_manager.py` (×3: the seed-3 fold IndexError + single-witness-inform yield 64→63 /
  converts 8→7).
- `tests/meetings/test_transcript.py` (×3: artifact-input-classes 1→2, no-strong-flag-survives 95→112,
  no-spawn-window-corroboration 59→61).

Get the new expected values by running each failing test (the assertion shows `actual == old_pin`).

## 11.8 gates before the PR (most already green)
1. `bash scripts/check.sh` fully green (all 15 re-anchored).
2. `scripts/verify_samples.sh` + `…/9p2i` byte-clean — **already confirmed**.
3. `experiments/lab/rubric_score.py` on the new 9p2i facts → **already confirmed**: R5 3→4, R1 6/50, mean
   45.1 (report it in the PR).
4. Re-run the close audit (`audits/workflows/gameplay-data-audit-v2.workflow.js`) on the new 9p2i set →
   substrate HARD gate green (game_over 100%, ff 0, betrayal 0, inversions 0), verdict stays VALID; confirm
   no sabotage-spam degeneracy (sabotage is a stall, 0 cheese wins).
5. **Delete this `WAVE3_REANCHOR.md`** before the PR (handoff note, not a deliverable).

Then PR `phase-11-wave3-rerecord` → main. That closes Wave 3 and, with it, Phase 11 (the gameplay rework);
next is Phase 12 (the front-end rework). The clock retune remains the held-in-reserve final lever.
