# Phase-14 close — baseline 2: the measured-defect batch landed; the railroad is gone, the dialogue defects collapsed, ejection accuracy held flat on the untouched non-flag channel

**Date:** 2026-07-03
**Task:** 14.12 — baseline 2 (atomic re-record on the 14.10 evidence-quality lever + the qwen3_32b v4 prompt
set) + the PHASE CLOSE.
**Set:** `replays/samples/9p2i` (50 games / 142 meetings / 844 ballots) + `replays/samples/4p1i`
(50 games / 39 meetings), this re-record.
**Model:** `Qwen/Qwen3-32B` (Featherless, both call kinds, non-thinking, `fail_loud`, `json_object`, $0).
**Substrate:** all five levers unconditionally ON — the four Phase-13.5 levers (unconditional since 14.9)
and the Task-14.10 `evidence_quality_lift` lever (made unconditional in this PR, retiring its env gate) —
stamped into MANIFEST `flags` + each replay's `game_over.substrate_flags`; prompt set `qwen3_32b.v4`.
**Recording:** 2 parallel Featherless seed workers (a 32B request = 2 of the 4 permitted units, so 2 workers
saturate the plan); measured wall **231 min (~3.85h)** for both sets. One transient `httpx.ConnectError`
auto-recovered on retry (the re-record's new per-seed crash-retry).
**Grounding:** every number below is a fold over the committed baseline-2 artifacts via the same methods
14.8 documented (`scripts`-side `measure_baseline.py` / `validity_gate.py` reproduce every baseline-1
characterization number EXACTLY before applying identically to baseline 2 — no number retrofit).
**Verdict in one line:** the two specified fixes hit their targets — the crew railroad is ELIMINATED
(5→0, the tripwire is restored) and all six v4 dialogue defects fell sharply — while R1 held near its honest
railroad-discounted anchor and genuine conviction did NOT collapse; the one metric that did NOT improve is
9p2i ejection accuracy (0.566→0.525, flat within run-to-run variance), because the fixes thinned the
FLAG-driven mis-ejects (31→25) but the zero-flag / voice-driven channel (audit §7, untouched by 14.10 BY
DESIGN) rose (22→31) and now dominates the residual — the clean Phase-15 target.

---

## 1. HARD validity gate — PASS (both sets)

`validity_gate.py` over both committed sets, cross-checked by `bash scripts/check.sh`:

| criterion | 9p2i | 4p1i |
|---|---|---|
| every game reaches game_over | 50/50 | 50/50 |
| friendly-fire (engine guard; leak suite green both sets) | 0 | 0 |
| betrayal ballots/accusations (§7.12 firewall) | 0 | 0 |
| meeting_rate / resolved meetings (bar ≥0.60 / ≥30) | 1.00 / 142 | 0.78 / 39 |
| tick-1 kills | 0 | 0 |
| dangling `primary_reason_id` | 0 | 0 |
| cost rows ($0 Featherless flat-rate) | 0 | 0 |
| provenance rows (`Qwen/Qwen3-32B`, `qwen3_32b.v4`, lever + 4 levers stamped) | exact | exact |
| parse-success / 1024-truncations | 99.21% / 1 | 100% / 0 |

Byte-identical reconstruction holds BARE: `verify_samples.sh` reconstructs all 50+50 samples clean under a
bare environment (roster.json present, no `AILIBI_*` lever export). The 14.10 lever was made UNCONDITIONAL
in this PR (§6) — the same 14.9 move applied to the 13.5 levers — so, exactly like the four 13.5 levers,
the committed set serves without any env flag. Because baseline 2 was recorded lever-ON, the resolver now
returning a constant `True` keeps the belief fold byte-identical to the recorded stamp.

## 2. The railroad TRIPWIRE — RESTORED (zero rows)

Baseline 1 carried 5 crew rows at a clamped 1.0 off ≥2 same-meeting contradiction flags (3 innocent ejects;
the regression-pin era). Baseline 2, recorded with the 14.10 certain-guilt-exclusion lever ON, renders
**0 such rows**. `tests/meetings/test_manager.py::test_no_crew_row_is_railroaded_to_certain_guilt` is
restored to its original `railroaded == set()` assertion — the regression-pin era ends WITH the defect.

The lever is **load-bearing on the committed bytes**, not cosmetic (the belief-fold counterfactual, re-derived
via the 14.8 analysis-only override): re-derived lever-OFF, exactly one crew row (seed-16 m0 p-6, 2 flags)
still clamps to the 1.0 railroad; lever-ON it ceils at `CONTRADICTION_RENDER_CEIL` (0.97). The other four
baseline-1 railroad coordinates no longer clamp even lever-OFF — v4's alibi discipline thinned their flag
density below the prior+cap certain-guilt path. Lever-ON reproduces the recorded vote-prompt rows 3046/3046
(the harness is the production fold; baseline 2 was recorded with the lever ON).

## 3. R-gate re-measured — measurement, not a gate (9p2i, vs the honest anchors)

Per the charter the R-gate is a MEASUREMENT on a valid baseline. The honest R1 anchor is the
RAILROAD-DISCOUNTED baseline-1 figure (25/50, audit §2 — the pinned rows were only 2 of the 24-game lift),
and the stacked-flag signature is role-blind, so "fewer stacked convictions" alone is NOT a success metric.

| term | 9B | baseline 1 (railroad-disc.) | **baseline 2** | read |
|---|---|---|---|---|
| R1 eject-decided win share | 3/50 | 27/50 (**25/50**) | **24/50** | held near the 25 anchor — NOT collapsed |
| ejection accuracy | — | 0.566 | **0.525** | flat within variance (the honest nuance, §4) |
| R4 wrong-ejection games | 4 | 39 | **38** | ~flat |
| impostor win (floor ≥0.14) | 0.84 | 0.32 | **0.40** | floor holds |
| genuine-class conversion | — | 0.667 | **0.625** | held — the over-damping canary did NOT fire |

Supporting rows: ejection_accuracy 0.525 = 62 impostor / 56 crew of 118 ejections; win split CREW 30 / IMP
20; reason histogram `{CREWMATE_EJECT: 24, IMPOSTOR_PARITY: 20, CREWMATE_TASKS: 6}`. **4p1i improved cleanly**:
ejection accuracy **0.788 → 0.923** (12 imp / 1 crew of 13), conversion 4/4, zero railroad, R4 wrong-eject
games 1.

**Neither defined failure mode triggered.** R1 held near 25 (not collapsed → 14.10 not over-damped);
genuine-class conversion 0.625 held and the seed-44-m0-style genuine catches still convict (the canary);
zero new railroad rows (14.10 not under-fixed). This is a VALID close.

## 4. The one honest nuance — 9p2i ejection accuracy held flat, and WHY

The contract's aspirational win condition was "R1 near 25 with ejection accuracy UP from 0.566." R1 held (24),
but ejection accuracy did NOT rise (0.566 → 0.525; a 0.041 point estimate, within the run-to-run variance of
two independent hosted re-records at n≈120 ejections). The composition explains it exactly:

| crew mis-eject channel | baseline 1 | baseline 2 |
|---|---|---|
| flag-driven (≥1 same-meeting flag on the ejectee) | 31 | **25** ↓ (the fixes' channel) |
| zero-flag (prior-carry / voice-driven — audit §7) | 22 | **31** ↑ (untouched by 14.10 BY DESIGN) |
| total crew mis-ejects | 53 | 56 |

The 14.10 lever and v4's alibi discipline reduced the FLAG channel (and eliminated its worst form, the
railroad), exactly as specified. But the ZERO-FLAG channel — convictions on accumulated/carried suspicion and
persuasive voice, which 14.10's lever explicitly does not touch (audit §7) and which v4's calibration did not
move — rose and now dominates the residual. Net crew mis-ejects held roughly flat, so aggregate accuracy did
too. Per the charter ("a flat or down R1 closes as a finding, not a failure"), a flat ejection accuracy with
the railroad eliminated and every specified defect fixed is a **finding**, not a phase failure — and the
zero-flag channel is the clean, evidenced Phase-15 target. There is no in-scope (record-only) iteration that
raises it; it needs new belief/prompt source work.

## 5. Per-defect deltas vs baseline 1 (the 14.11 v4 targets — all hit)

9p2i committed bytes (measurement definitions identical to 14.8 §4; each reproduced baseline-1's number
exactly before folding baseline 2):

| # | defect | baseline 1 | **baseline 2** | Δ |
|---|---|---|---|---|
| 1 | self-contradicted self-alibis | 30/295 (10.2%) | **10/339 (2.9%)** | ↓ 7.3pp |
| 2+3 | guard-normalized ballots (invalid target + reason-id) | 47 (27+20) | **10 (4+6)** | ↓ 37 |
| 4 | confidence-1.0 accusations | 64/505 (12.7%) | **27/491 (5.5%)** | ↓ 7.2pp |
| 6 | template-rationale share ("p-N's alibi …" family) | 293/891 (32.9%) | **125/844 (14.8%)** | ↓ 18.1pp |
| 6' | alibi-contradiction phrasing family (secondary) | 441/891 (49.5%) | **164/844 (19.4%)** | ↓ 30.1pp |
| — | missed-deadline turn markers | 23 | **6** | ↓ 17 |

4p1i moves the same direction (self-contra 3/59, guard 1, conf-1.0 6, template 3/117, missed-deadline 0).
Every measured v4 target improved; none regressed.

## 6. Decisions

- **The 14.10 lever is now UNCONDITIONAL — baseline 2 reconstructs BARE.** The lever shipped default-OFF at
  14.10; this PR retired its `AILIBI_EVIDENCE_QUALITY_LIFT` env gate (the resolver returns a constant `True`;
  the flag graduated from `_TOGGLEABLE_LEVER_RESOLVERS` to `_RETIRED_ALWAYS_ON_LEVERS`), the exact 14.9 move
  applied to the four 13.5 levers. Because baseline 2 was recorded lever-ON, the resolver's constant `True`
  keeps the belief fold byte-identical to the recorded stamp, so the committed set now reconstructs and serves
  under a bare environment — no `AILIBI_*` export required (`verify_samples.sh` clean bare on both 50+50 sets;
  §1). The spectator launcher (`run_spectator.sh`) and the byte-coupled tests were re-pinned to the bare form.
  This resolves the review's flag-aware-serving follow-up in-PR; no lever env remains for an operator to forget.
- **The R-gate is reported as a measurement, not gated.** No number was retrofit; the folds reproduce
  baseline-1's characterization exactly before folding baseline 2.

## 7. Phase 15 recommendation (with the evidence)

- **Persona / voice layer, and the zero-flag mis-eject channel.** §4's residual (22→31 zero-flag crew
  mis-ejects) is the concrete, measured next target: crew convict on accumulated suspicion + persuasive voice
  outside the flag channel any belief-fold lever touches. A persona/voice layer (owner's Phase-15 note) plus a
  belief-side treatment of prior-carry / voice-driven conviction is where ejection accuracy rises next.
  Impostor concealment (the 14.4 tell) is unchanged by this phase by design — the ceiling on concealment
  stands as the REVISED hypothesis's surviving half; a persona layer is also the lever on it.
- **Tactical / ML between-meeting play + structural information.** The Phase-13 information ceiling
  (single-room vision → ~45% detector precision) still bounds detection; structural information levers
  (vents/sabotage/wider vision) + learned between-meeting play are the deferred structural work. The kill-scene
  witnessed-kill detector remains effectively unmeasured (n=1 firing, audit §5) — it needs a richer scenario a
  Phase-15 information lever would produce.

## 8. Method + reproduction (all $0, offline, committed bytes)

- R-gate + per-defect folds: `measure_baseline.py` (ejection accuracy / genuine-class conversion / accusation
  calibration / self-alibi self-contradiction / guard-marker census / template clustering / missed-deadline
  census) — validated to reproduce every baseline-1 characterization number exactly, then folded over
  baseline 2.
- Validity gate: `validity_gate.py` (all-game_over / meeting-rate+resolved / betrayal / tick-1 kills /
  dangling reason-id / cost / provenance incl. the lever stamp) + `verify_samples.sh` (bare-env
  reconstruction) + `bash scripts/check.sh`.
- The lever counterfactual (§2): the production vote-time fold re-derived lever-ON vs lever-OFF over the
  committed bytes via the Task-14.8 `allow_substrate_mismatch` analysis-only override (lever-ON 3046/3046
  reproduces the recorded rows; lever-OFF resurrects the seed-16 m0 p-6 railroad).
