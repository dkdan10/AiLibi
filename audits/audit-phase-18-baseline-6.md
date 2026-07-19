# Phase-18 adopting record — baseline 6: the meeting-layer graduation, the atomic re-record, the floor re-pin (Task 18.12)

**Date (pre-registration committed BEFORE the record — the 15.18 discipline):** 2026-07-19
**Task:** 18.12 — the adopting record: baseline 6 (operator, $0)
**Sets:** `replays/samples/9p2i` (canonical eval set, 50 seeds) + `replays/samples/4p1i` (50 seeds)
**Model:** `Qwen/Qwen3.6-27B` (Featherless, non-thinking; the owner-locked eval model since Task 16.2, audits/audit-phase-16-model-lock.md)
**Substrate:** the baseline-6 slate — the four meeting-layer levers graduated to unconditional ON (`roll_call_round`, `whereabouts_interior_flags`, `vent_placement_contradictions`, `absence_prior`) beside the nine already-retired levers; `impostor_roll_call` stays default-OFF (the CREW-ONLY ruling, audits/audit-phase-18-meeting-gate.md §9).
**Grounding:** the baseline-5 adopting-record runbook (audits/audit-phase-16-close.md, the template this reprises); the baseline-5 floor block (eval/watchability.py:755-762, the block the new baseline-6 block sits beside); the phase-17 close's corpus-denominator canary anchors (audits/audit-phase-17-close.md §3); the 18.11 ruling (which arms flip).
**Recording:** `scripts/refresh_samples.sh --full` per set, under the graduated bare environment (no `AILIBI_*` lever export — the substrate-lever preflight refuses one); validity-gated; MANIFEST + `tournament-eval-report.json` rebuilt per set.
**Verdict in one line:** [PENDING POST-RECORD — the validity gate PASS on both sets, the baseline-6 floor block pinned at self-consistent equality, and the §0.4 canaries read under band.]

---

## 0. PRE-REGISTRATION (committed BEFORE the record — the 15.18 discipline)

### 0.1 The GRADUATION SLATE (the owner gate — inherited from the 18.11 ruling)

The 18.11 meeting-layer gate ruled **CREW-ONLY** (audits/audit-phase-18-meeting-gate.md §9,
Ruling A). Exactly FOUR levers graduate to unconditional; the impostor-answer arm does NOT
ship. This record enacts that ruling — it does not re-decide it.

#### 0.1.1 The roll-call round (18.8): **GRADUATE-ON**
The turn-allocation surface (audits/audit-phase-17-absence-gate.md Ruling 3(a)). The 18.11
probe measured live crew roll-call coverage at **1.00** against the ratified **≥ 0.60** bar
(gate audit §7). It graduates: `meetings.manager.roll_call_round_enabled` → unconditional,
the round always inserted after the opt-in phase and before ballots.

#### 0.1.2 The endpoint-band whereabouts exemption (18.9 lever 1): **GRADUATE-ON**
The exemption that lets a single-tick self-alibi contradicted by a first-hand sighting mint a
STRONG `alibi_vs_sighting` flag (audits/audit-phase-18-planning.md §3.3). Graduates with the
package: `meetings.transcript.whereabouts_interior_flags_enabled` → unconditional.

#### 0.1.3 The vent-placement flag variant (18.9 lever 2): **GRADUATE-ON**
The grounded-vent flag-minting arm (the 17.5 scope firewall's flag-minting side). Its FIRST
live yield in the shipping combination is measured on THIS record (§2). Graduates:
`meetings.transcript.vent_placement_contradictions_enabled` → unconditional.

#### 0.1.4 The absence prior (16.8): **GRADUATE-ON**
The Phase-16 slate's recorded STAY-OFF (audits/audit-phase-16-close.md §0.1.4), re-routed to
Phase 18 by audits/audit-phase-17-absence-gate.md Ruling 3 and gated on the ratified bar
measured beside the 18.8 roll-call elicitation. The 18.11 absence counterfactual on the probe
bytes read new-over-gate **3/75 = 0.040 ≤ 0.20** (the ratified ceiling), so it graduates:
`agents.memory.beliefs.absence_prior_enabled` → unconditional. The absence-prior graduation
component of the ruling is thereby EXECUTED (not stayed).

#### 0.1.5 The impostor-answer arm (18.10): **STAY-OFF**
The CREW-ONLY ruling did NOT ship it: probe impostor win **0.16 < 0.20** (the bright-line
miss) and the self-flag clause decided against it (gate audit §6). `impostor_roll_call` stays
a default-OFF toggle, the SOLE remaining live env-gated lever. Every "if the impostor-answer
arm ships" clause in this contract therefore reads FALSE — no `orchestrator.game` registry
flip, no `IMPOSTOR_ROLL_CALL_PROMPT_VERSION_SETS` fold, and the recorder
`REQUIRED_PROMPT_VERSIONS` re-lock is a no-op (the registry does not move).

#### 0.1.6 The slate, in one row

| lever | Task | baseline 5 | baseline 6 | mechanism |
|---|---|---|---|---|
| roll_call_round | 18.8 | off (env-gated) | **ON (unconditional)** | +roll-call turns |
| whereabouts_interior_flags | 18.9 | off (env-gated) | **ON (unconditional)** | STRONG alibi_vs_sighting on single-tick self-alibi |
| vent_placement_contradictions | 18.9 | off (env-gated) | **ON (unconditional)** | STRONG alibi_vs_physical on grounded vent |
| absence_prior | 16.8 | off (env-gated) | **ON (unconditional)** | pre-vote delta on the publicly-unplaced |
| impostor_roll_call | 18.10 | off (env-gated) | off (env-gated) | (not shipped) |

**Substrate-flags MUST match:** every recorded `game_over` stamp carries the thirteen retired
levers True and `impostor_roll_call` False; the MANIFEST `flags` column reads the thirteen ON
levers sorted:
`absence_prior, citation_gate, evidence_quality_lift, hard_evidence_gate, movement_perception, observation_id_rendering, reporter_exculpation, roll_call_round, testimony_as_content, unfreeze_memory, vent_placement_contradictions, whereabouts_interior_flags, witnessed_kill_evidence`.
A seed whose stamp disagrees is a FAILED recording and re-records.

### 0.2 Preflight — the meeting layer is the moving layer (proven on the pre-record tree)

- **Substrate snapshot:** `orchestrator.replay.substrate_flag_snapshot(env={})` stamps the
  thirteen retired levers True and `impostor_roll_call` False (verified; the reclassification
  moved the four graduated keys into `_RETIRED_ALWAYS_ON_LEVERS`).
- **Substrate-lever preflight:** `scripts/refresh_samples.sh` gains a positive check that the
  live lever slate equals the ruled baseline-6 state and refuses a stale `AILIBI_*` export
  (notably `AILIBI_IMPOSTOR_ROLL_CALL=1`) BEFORE any seed stages.
- **Registry unchanged:** `orchestrator.game.PROMPT_VERSION_SETS['qwen3_6_27b']` still resolves
  to the v3 map (`accusation_round/crewmate_report/impostor_report/vote_ballot .qwen3_6_27b.v3`);
  the recorder's `REQUIRED_PROMPT_VERSIONS` re-lock is a no-op.
- **Model lock:** the effective Featherless meeting model is `Qwen/Qwen3.6-27B`, registered in
  `llm.featherless_client._THINKING_KWARG_BY_MODEL`.
- **Reconstruction:** the committed baseline-5 bytes are now cross-substrate (the four levers
  are always-on), so the golden / verify_samples / replay-loader reconstruction tests are RED
  on the pre-record tree by design; the re-record on the graduated substrate restores them.

### 0.3 The BEFORE column

`audits/baseline5-final-measure.json` is captured on the committed baseline-5 bytes
immediately before the re-record replaces them (the four `measure_baseline.py` folds — core /
watchability / funnel / vj — over both canonical sets, offline, $0). The baseline-5 bytes
survive only in git history at the commit named in that file's `_meta`. This audit regenerates
its baseline-5 BEFORE column from that file — no hand-computed figures.

### 0.4 Pre-registered canary bands + the named NO-GO pairing (the close's pause arms)

The bands are pre-registered FROM the phase-17 close's corpus-denominator anchors
(audits/audit-phase-17-close.md §3, the Q3-restored canonical canary denominator), with the
50-seed samples as the continuity anchor. The REGRESSION arm fires on a pooled two-proportion
`|z| ≥ 1.96`.

| cell | corpus anchor | band-fire threshold | min detectable drop | 50-seed samples continuity |
|---|---|---|---|---|
| **R1 eject-decided win share** | 93/150 = 0.620 [0.540, 0.694] | **≤ 76/150 = 0.5067 (z = −1.979)** | 11.3 pp | 25/50 = 0.500 |
| **genuine-class successor** (named canary cell) | **211/241 = 0.8755** [0.828, 0.911] | **≤ 195/241 = 0.8091 (z = −2.000)** | 6.6 pp | 63/70 = 0.900 |
| zero-flag conviction rate | 19/242 = 0.0785 [0.051, 0.119] | — (monitored) | — | 2/70 = 0.0286 |
| ejection accuracy | 229/242 = 0.9463 [0.910, 0.968] | — (monitored) | — | 64/70 = 0.9143 |
| testimony-backed conversion | 228/421 = 0.5416 [0.494, 0.589] | — (monitored) | — | 64/135 = 0.4741 |
| citation compliance | 1303/1303 = 1.000 | — | — | 405/405 = 1.000 |
| impostor win rate | 49/150 = 0.3267 | — | — | 18/50 = 0.36 |
| roll-call coverage (crew / impostor) | 0.3723 (0.4743 / 0.0896) | — | — | 0.3629 (0.4624 / 0.0894) |
| whereabouts lies detected | 25 (0.0227) | — | — | 6 (0.0167) |
| provenance-sum breaches | 0 / 8105 rows | — | — | 0 / 2879 |

**The named NO-GO pairing (the close's pause arm):** a SIMULTANEOUS fire of BOTH banded
cells — R1 ≤ 0.5067 AND successor ≤ 0.8091 — on the baseline-6 record pauses the phase (the
substrate has degraded both the win economy and the conviction supply at once). Either alone
is reported and adjudicated; both together is the NO-GO. This is the meeting-layer graduation's
declared failure mode: the roll-call round adds turns that could dilute conviction, and the
absence prior + vent variant add flag pressure that could over-convict.

**§0 sanity-read expectations** (the gate §7 CREW-ONLY probe cells — NOT re-recorded; THIS
record is their first live measurement in the shipping combination): crew roll-call coverage
≈ **1.00**; impostor win ≈ **0.32**; testimony conversion ≈ **0.525**; the absence-prior
new-over-gate re-run on the new bytes ≤ **0.20** (the graduation clause); the vent-variant live
yield expected in the **[7, 28]** bracket.

**Three coordination corrections carried when quoting the gate's cells** (the 17.17 correction
pattern — the ratified memo is NOT rewritten, the corrections are recorded here):
- (a) the CREW-ONLY coverage z re-computes to **+7.07** on the stated n = 75 (the memo's quoted
  +6.93 back-solves to n = 72; conservative, verdict-neutral);
- (b) the impostor-win z **−2.08** is the memo's declared one-sample-vs-0.36 convention — the
  pooled two-proportion read vs 18/50 is **−1.79** (immaterial: the 0.16 < 0.20 bright-line
  miss and the self-flag clause decided the bar);
- (c) memo §6's "each bound to its home-module resolver by identity" holds for **3 of 4** — the
  `impostor_roll_call` entry is a deliberate LOCAL mirror in `orchestrator.replay` (loader
  import-cost isolation), with a CI equivalence pin standing in for the identity binding.

### 0.5 The recording plan (the 16.17 runbook, verbatim mechanics)

`scripts/refresh_samples.sh --full` per set, 2 Featherless seed-workers (4-unit plan, 2 units
per 27B request), per-seed staging + crash-retry (≤ 4 attempts), MANIFEST + eval-report rebuilt
per set. Record 4p1i first (validate the pipeline), then the 9p2i leg (the roll-call round adds
~36% meeting calls — the operator budget is ~6–7 h). Watch item: the validity gate's
`cost_and_provenance_exact` has a known blindness around the `(deadline_default)` synthetic
marker (routed by PR #299 to a future eval/ contract); a seed whose opening defaults is a
FAILED recording and re-records, per the standing rule. The Q5 provenance convention applies
(recording sha back-filled on merge).

---

## 1. HARD validity gate — [PENDING POST-RECORD]

`scripts/validity_gate.py <dir> --expected-model Qwen/Qwen3.6-27B --require-zero-cost` on both
sets: [PASS/FAIL, resolved-meeting counts, $0 provenance]. Byte-identical reconstruction under
a bare environment: [PENDING]. Substrate flags in the recorded bytes matching the ruling
exactly: [PENDING — the thirteen-ON / impostor-OFF stamp].

## 2. The close reading: the deception-instrument tier before/after (baseline 5 → baseline 6) — [PENDING POST-RECORD]

The Tier-A deception instruments (18.1 false-vouch / frame-jobs / teammate-immunity), the V&J
instruments, and the kill-craft fold (18.2), quoted before (from `baseline5-final-measure.json`)
and after (the re-recorded bytes). The vent-variant's first live yield in the shipping
combination reported against the [7, 28] bracket.

## 3. The information funnel re-measured (baseline 5 → baseline 6) — [PENDING POST-RECORD]

The funnel stages (meeting / oracle / possession / transmission) before/after, both sets.

## 4. R-gate + the §0.4 canaries under the pre-registered bands — [PENDING POST-RECORD]

R1 eject-decided win share and the genuine-class successor read against the §0.4 band-fire
thresholds; the NO-GO pairing adjudicated. The §0 sanity-read cells (crew coverage, impostor
win, conversion, absence new-over-gate, vent yield) reported against expectations.

## 5. Selection referee + baseline-6 floors — [PENDING POST-RECORD]

The baseline-6 floor block pinned from the recorded bytes with the 16.11
`population_relative_conversion_floor` derivation, referee PASS at exact floor==measured
equality on its own record (the self-consistency check). `_DEFAULT_BASELINE_ID` flipped to
`baseline-6`.

## 6. Uptake findings per elicitation ask — [PENDING POST-RECORD]

## 7. Provenance — [PENDING POST-RECORD]

MANIFEST provenance per seed (model / prompt versions / flags / $0 cost / winner); the
recording sha (Q5 back-filled on merge).

## 8. The permanent record: the staleness rule (re-stated) + routed contracts

Baseline 6 is the committed canonical SAMPLES set from this record; the corpus stays baseline-5
until the 18.13 re-record restores it as the canonical canary denominator. Every Phase-17
comparator number over `replays/samples/` is superseded by this record. The `(deadline_default)`
validity-gate blindness (PR #299) is inherited by the close if unclaimed.

## 9. Decisions — [PENDING POST-RECORD — see the PR `## Decisions` section]

## 10. Method + reproduction (all $0 against committed bytes, offline)

The re-record: `scripts/refresh_samples.sh --full` per set (real Featherless, $0 flat-rate).
Every measurement below is `$0`, offline, against the committed bytes:
`scripts/measure_baseline.py <dir> --watchability/--funnel/--vj --json`,
`scripts/build_sample_report.py --sample-dir <dir>`, `scripts/validity_gate.py <dir>`, and the
module folds (`eval.deception_instruments`, `eval.kill_craft`, `eval.off_menu`).
