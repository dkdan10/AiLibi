# Task 11.4 finalize — re-anchor era pins to the Wave-1 baseline

**Branch:** `phase-11-wave1-rerecord`. **Status:** the Wave-1 combined re-record is **DONE and committed on
this branch** (both sets, byte-clean determinism). **DO NOT re-run `refresh_samples.sh`** — re-recording
would burn ~5h and risk a different (still-valid) baseline. Your job is to **re-anchor the era-pin tests**
to the committed baseline, run the 11.4 gates, and get `bash scripts/check.sh` green, then open a PR.

## What landed (the new baseline, verified)
- `verify_samples.sh` + `verify_samples.sh replays/samples/9p2i` both report **"All 50 samples verified
  clean"** — the recorded per-tick state-hash chain reconstructs byte-identically. The substrate is clean.
- **9p2i (50 games):** impostor win 2%→**8%** (CREW 46 / IMP 4), meeting_rate 1.00 (**112 meetings**),
  ejection_accuracy 0.89, effective_deflection 9/33 active (**75 survivals**), **flags 95 (95w / 0s)**,
  imp_do_task 378, conversion 0.33.

## Verdict: data-drift, NOT regression (verify, don't assume)
The 39 failures are committed-bytes tests pinning the **old W2 baseline**; the re-record changed the
sample-derived values *as intended* by Wave 1. The headline evidence: **0 strong flags (95w/0s)** — vents
(11.1) hide the impostor's post-kill sighting trail, so the `alibi_vs_sighting` strong/"genuine" flags the
old set relied on evaporate (the offline `report-vent-escape-lab.md` predicted −91% catchability; this is
that, live). The substrate is byte-clean and the win-rate move (8%) is a *guardrail, non-gate*.

**This is the documented "re-anchor era pins after a re-record" cadence step (account-don't-rule-change).**
It is **not** blind pin-swapping:
- For **value pins** (counts/rates/decompositions): re-anchor to the new computed value, after confirming
  the change is explained by Wave-1 behavior (vents → fewer sightings/flags; cover-on-reply → fewer self
  flags; kill-memory → legibility only).
- For **INVARIANT tests** (`test_win_condition_selfcheck`, any firewall/leak test, `threshold_inversions`,
  friendly-fire/betrayal): the invariant MUST still hold — verify it (inversions still 0, ff/betrayal 0,
  no railroads). If an invariant is genuinely violated, STOP and escalate — that would be a real
  regression, not a pin update.
- Re-run the close audit (below) as the independent check that the baseline is still substrate-VALID.

## The 39 failing tests (group by file; re-anchor each)
- `tests/scripts/test_manifest_writer.py` (×3) and `tests/scripts/test_refresh_samples.py` (×1): version
  pins **accusation_round.v7 → v8** (11.2) + the meetings-dry-run seed list (manifest changed). Mechanical.
- `tests/eval/test_gate_metrics.py` (×2), `tests/eval/test_vote_correctness.py` (×1),
  `tests/eval/test_wave2_metrics.py` (×4: conv-per-meeting, effective-deflection, indistinguishability
  do_task 378, single-witness-inform 10), `tests/eval/test_gate_spec_metrics.py` (×4 incl. the
  `corrected_w2_baseline.json` re-derivation), `tests/api/test_eval.py` (×1),
  `tests/eval/test_win_condition_selfcheck.py` (×1 — INVARIANT, verify): the shipped gate/eval pins.
- `tests/meetings/test_manager.py` (×5: `TestCommittedBytes107FoldPins` seed30/seed38/seed3,
  `TestSingleWitnessInformYieldOnCommittedBytes` ×2): testimony-fold + inform-yield pins.
- `tests/meetings/test_transcript.py` (×14: `TestCommittedBytesArtifactCollapse`,
  `TestCommittedBytesSeedPins` ×3, `TestCommittedBytes106Pins` ×3, `TestCommittedBytes1010Pins` ×4,
  `TestCommittedBytes107VoicePins` ×3): detector weak-banding + genuine-flag-survival + voice pins. The
  "genuine strong flag survives" pins now read 0 (no strong flags) — re-anchor to the post-vent reality,
  but confirm the weak-banding/firewall channels are still alive (they should be).
- `tests/agents/test_beliefs.py` (×2: `TestRelevanceGatedFoldOnCommittedBytes` seed13 trajectory): the
  §6.3 accumulator trajectory on the new seed-13 bytes — confirm it still RISES (the gate is load-bearing),
  just re-anchor the exact values.

Get the new expected values by running each failing test (the assertion shows `actual == old_pin`); the
`corrected_w2_baseline.json` and any dict/tuple pins are re-derived by running the relevant analyzer on the
new `replays/samples/9p2i` (the tests show the analyzer entry points).

## 11.4 gates to confirm before the PR
1. `bash scripts/check.sh` fully green (all 39 re-anchored, ruff/mypy/validate/generate/frontend pass).
2. `uv run python experiments/lab/rubric_score.py <new 9p2i facts>` → **R2 component UP** vs the W2 baseline
   (mean 38.2; `experiments/lab/report-rubric-interestingness.md`). Report the new mean + eject-decided
   share (R1 should be ~flat — Wave 1 is deception, not balance).
3. Re-run the close audit (`audits/workflows/gameplay-data-audit-v2.workflow.js`) on the new 9p2i set →
   substrate HARD gate green (game_over 100%, ff 0, betrayal 0, inversions 0), verdict stays VALID.
4. Delete this `WAVE1_REANCHOR.md` before the PR (it is a handoff note, not a deliverable).

Then PR `phase-11-wave1-rerecord` → main. This closes Wave 1; Wave 2 (the task-clock retune) is gated on
this new baseline.
