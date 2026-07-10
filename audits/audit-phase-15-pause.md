# Phase-15 pause — the mid-phase audit, the seven decisions, and the Wave-2 authorization

**Date:** 2026-07-10
**Author task:** 15.18 (`tasks/phase-15.md`) — the wave boundary the phase was designed around: tabulate
every Wave-1 entrant on the single protocol, run the ONE fresh measurement (the real-LLM finalist
evaluation), settle the Wave-0 watch items by data, re-verdict the referee, record the seven owner
decisions, and author Wave 2 into the phase file from evidence instead of forecasts.
**Method:** measurement-only. Code under `training/`, `eval/`, `agents/`, `engine/`, `orchestrator/` is
read-only for this task; every number below is regenerated from the committed CLIs
(`scripts/validity_gate.py`, `scripts/measure_baseline.py [--watchability|--funnel] --json`) or quoted
from a committed jsonl/report artifact, and each table names its source. Zero hand-computed figures —
the two derived statistics in §5 (a Wilson interval and a two-proportion z) are computed from committed
CLI outputs by the formula pre-registered in the 15.18 contract, and the inputs are quoted beside them.
The one fresh measurement is the operator-run real-LLM finalist evaluation (§3), committed as
`training/reports/results-finalist-eval.jsonl`. Decision sign-off follows the Task-14.6 precedent: the
locked-decision blocks below are the owner record, ratified by the merge of this task's PR.

**Label key:** **[RAN]** reproduced by a command on this checkout · **[VERIFIED]** read directly in a
committed source/artifact · **[INFERRED]** reasoned from verified facts · **[PROPOSED]** a
recommendation.

---

## 0. Verdict in one line

Wave 1 delivered exactly what the pause needed — four impostor methods, a crew probe, a torch probe, a
surrogate verdict, and a red-teamed referee, all on one committed protocol — and the evidence picks a
clear champion: **`utility-es`** wins on every selection-relevant axis but raw fitness (where it is 2%
behind a flagged entrant), and the real-LLM finalist evaluation (§3) confirms it on the real meeting
path; but the referee that would bless a default-flip is not yet trustworthy (one exploited channel +
an owner-ratified definition debt, both now contracted as Task 15.19), so the deployment decision is
**branch A — the opt-in factory** — with the default flip re-evaluated only behind the hardened
referee, and Wave 2 (Tasks 15.19–15.23) is authored, validated, and dispatching.

---

## 1. Mechanical health — what I ran, all green

Everything below is **[RAN]** on HEAD `525ce98` (branch `claude/phase-15-pause-audit-1yzemm`), before
this task's document edits.

| Gate | Result |
|---|---|
| `bash scripts/check.sh` | green end-to-end |
| `ruff check .` / `ruff format --check .` | All checks passed |
| `mypy .` | Success: **no issues in 264 source files** (`strict = true`) |
| `pytest` | **3113 passed, 20 skipped, 3 xfailed** in 255 s |
| `validate_task_docs.py` / `generate_prompts.py --check` | 222 tasks, 222 prompts, all in sync (227/227 after this task's Wave-2 authoring) |
| `scripts/validity_gate.py replays/samples/9p2i --json --expected-model Qwen/Qwen3-32B --require-zero-cost` | **PASS** — all 10 checks |
| `scripts/validity_gate.py replays/samples/4p1i …` | **PASS** — all 10 checks |
| `scripts/validity_gate.py replays/ml_corpus/9p2i …` | **PASS** — all 10 checks (150 games) |
| `scripts/validity_gate.py replays/ml_corpus/4p1i …` | **PASS** — all 10 checks |
| `measure_baseline.py --watchability` on samples 9p2i / 4p1i | referee **PASS** / **PASS** (mean 39.83 / 9.07) |
| `measure_baseline.py --watchability` on corpus 9p2i / 4p1i | referee **PASS** (mean 45.57) / **FAIL** (mean 10.54 — see §5.1, the one-event floor degeneracy) |

The corpus-4p1i referee FAIL is not a corpus defect: the set fails only the `witnessed_event_rate`
supply floor (measured 0.0000 vs floor 0.0182), and that floor was pinned on a ONE-EVENT numerator
(1/55 on the 50-seed samples) — a rare-event gauge that a same-substrate set can miss by pure variance.
This is a referee-calibration finding, routed into Task 15.19 (§4), not a validity problem: the same
set passes the HARD validity gate and both other supply floors (flags 1.50 vs 1.077; backed conversion
0.722 vs 0.600). **[RAN]**

---

## 2. Every entrant on the single protocol

All rows below are quoted verbatim from the committed machine-readable artifacts; the protocol tuple is
15.15's (validity gate / referee / fitness real+surrogate / anchor-CE / determinism hash / leak), one
harness (`training/bakeoff/harness.py`), one eval seed set (the frozen corpus test split, seed % 5 == 4,
30 seeds). Meeting path: the fake-provider MeetingManager — the 15.13 surrogate landed **NO-GO**
(fallback (a), diagnostic-only), so no reported number is surrogate-scored; the real-meeting-path
correction is §3's job.

### 2.1 Impostor bake-off — source: `training/reports/results-impostor-bakeoff.jsonl` [VERIFIED]

| entrant | gate | referee mean/med (passed) | fitness real | fitness surrogate | anchor-CE (flag) | win rate | take-rate | det. | leak | genome | weights sha256 (prefix) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| bc-dagger | PASS | 1.02 / 0.20 (F) | 5.167 | 3.098 | 1.959 (–) | 0.067 | 0.473 | PASS | PASS | 1049 | `ddb1e706` |
| **utility-es** | PASS | **14.62 / 16.80** (F) | 18.671 | **11.315** | **0.995** (–) | **1.00** | 0.763 | PASS | PASS | **19** | `6d327dcb` |
| policy-es | PASS | 6.32 / 3.70 (F) | **19.066** | 7.258 | 2.016 (**FLAGGED**) | **1.00** | 0.759 | PASS | PASS | 1049 | `561e5ff3` |
| map-elites | PASS | 6.13 / 3.70 (F) | 18.198 | 7.857 | 1.974 (–) | 0.933 | 0.924 | PASS | PASS | 1049 | `b4469dec` |

Referee `(F)` on every row is the fake-provider structural artifact, not discrimination: all four fail
the same two meeting-driven supply floors (`flags_per_meeting` 0.0, `testimony_backed_conversion` null)
because fake meetings mint no evidence — the bake-off report's own §3 states the gate "does not yet
DISCRIMINATE among these candidates; its geomean column does." The scripted FSM measured through the
same protocol: shaped reward 20.33, take-rate 0.55, vent 7.3/game (report §8). [VERIFIED]

### 2.2 Crew track — source: `training/reports/results-crew-track.jsonl` [VERIFIED]

| entrant | gate | referee mean (passed) | fitness real | anchor-CE | crew win | meetings total | floor-trip | det. | leak | genome | sha256 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| crew-fsm-baseline | PASS | 7.96 (F) | 11.469 | 0.0 | 0.10 | 116 | 0.0 | PASS | PASS | 0 | `37517e5f` |
| crew-utility-es | **FAIL** (3 checks) | 0.00 (F) | 13.240 | 0.676 | 0.60 | **0** | **1.0** | PASS | PASS | 22 | `888046d0` |

(The crew rows carry no surrogate-fitness column: `inner_fitness_surrogate` is null in both rows — the
crew track post-dates the NO-GO and never metered the surrogate; every other tuple field is present.)

The trained crew scorer lifts win rate 3/30 → 18/30 by suppressing the report interrupt and starving
the meeting layer to zero — and the validity gate + referee both catch it (`validity_failing_checks`:
`all_games_reach_game_over`, `meeting_rate_and_resolution`, `cost_and_provenance_exact`; referee 0.00,
floor-trip 1.0). Fitness up, gates down: the selection-filter split did its job, the gate-valid crew
ceiling is still unmeasured, and that measurement is what decision 5 contracts (Task 15.22).

### 2.3 Torch probe + distilled student — source: `experiments/lab/torch_probe/results-torch-probe.jsonl` [VERIFIED]

| entrant | gate | referee mean (passed) | fitness real | fitness surrogate | anchor-CE (flag) | win rate | take-rate | det. (same-host) | leak | genome | sha256 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| torch-ppo-gru-s0 | PASS | 3.04 (F) | 10.963 | 6.899 | 2.035 (FLAGGED) | 0.267 | 1.00 | PASS | PASS | 33298 | `ae567f31` |
| torch-ppo-gru-s1 | PASS | 3.04 (F) | 11.050 | 6.977 | 1.937 (–) | 0.267 | 1.00 | PASS | PASS | 33298 | `3372f409` |
| torch-ppo-gru-s2 | PASS | 3.04 (F) | 10.971 | 6.917 | 2.023 (FLAGGED) | 0.267 | 1.00 | PASS | PASS | 33298 | `116c8e2c` |
| torch-distill-student | PASS | 1.04 (F) | **−2.580** | −5.098 | **11.715** (FLAGGED, 256 off-menu) | 0.067 | 1.00 | PASS | PASS | 1049 | `6302c474` |

The probe's one question answered **NO**: best torch fitness 11.05 sits 7.6 points and 0.73 win-rate
points below the ES ceiling at ~2× the training wall-clock, and all three seeds converge to the same
greedy take-rate-1.00 policy. The distillation hatch is mechanically real (attempt 2: 0.9709 held-out
student–teacher agreement vs the ≥ 0.90 bar) but capability-empty — the student collapses in
closed-loop rollouts (fitness −2.58, anchor-CE 11.72, 256 off-menu decisions): the classic BC
distribution shift, and there is no torch capability worth distilling this wave. [VERIFIED,
`experiments/lab/report-torch-probe.md`]

---

## 3. The real-LLM finalist evaluation — the one fresh measurement

The bake-off's §7 ranking is explicitly meeting-model-conditional ("the pause should not read rank 1 vs
rank 2 as significant without the real-LLM re-score"), and its two committed meeting models BRACKET the
real path from opposite sides (fake: 0/116 ejections, evidence-starved; surrogate: 92% ejections,
evidence-free ballots). So the pause re-recorded the top-2 finalists — **utility-es** and **policy-es**
(report §7 ranks 1–2) — on the real meeting path before deciding anything.

### 3.1 The recipe (full re-derivation; the Q5 provenance convention demonstrated)

**[RAN]** — recorded 2026-07-10 on checkout `525ce98` (the post-squash main sha of PR #243, named here
and back-filled into every committed measurement row as `recording.recording_git_sha` — the
back-fill arm of the owner-ratified provenance-durability convention, 2026-07-09 Q5, which every
operator record follows from this task onward; an annotated tag `git tag -a
phase-15-finalist-eval 525ce98` is the equivalent arm when the recording commit is not already a main
sha).

- **The seam.** `eval.balance_eval.run_tournament_eval(agent_factory=…, tactical_policy_stamp=…)` —
  `scripts/run_tournament.py` carries `--tactical-policy-stamp` but NO agent-factory flag, so the stamp
  CLI alone cannot drive a learned policy; a ~90-line Python driver (reproduced below in outline,
  fully documented for re-derivation) is the recording path. Task 15.21 closes this gap with the
  `--agent-factory` flag.
- **Per finalist:** reload the committed genome via
  `training.bakeoff.harness.load_candidate_weights("training/artifacts/impostor/<entrant>")` (raises on
  sidecar drift — the sha256 verification is in the loader); rebuild the exact inference policy
  (`training.bakeoff.utility_es.build_utility_scorer_policy(weights, game_map=load_canonical_map())`
  for utility-es; `training.bakeoff.policy_es.build_masked_mlp_policy(weights, game_map=…, hidden=8)`
  for policy-es); wrap with `training.bakeoff.harness.build_candidate_factory(policy, game_map=…)`
  (impostors run the candidate, crew delegate to the FSM, meeting protocol forwarded to the wrapped
  `TacticalAgent`); stamp with
  `TacticalPolicyStamp(policy_id=<entrant>, method="neuroevolution", encoder_version=policy.encoder_version,
  weights_sha256=<the sidecar digest>, anchor_policy="fsm-default")`.
- **The record:** seeds **0–49** (the canonical `replays/samples/9p2i` seed set), roster 9p/2i at
  `tasks_per_crewmate=2`, `max_ticks` default, `force=True`; environment
  `AILIBI_LLM_PROVIDER=featherless`, `AILIBI_PROMPT_SET=qwen3_32b` (turn/opening v5, `vote_ballot` v6 —
  the exact baseline-3 substrate), model `Qwen/Qwen3-32B`, $0 flat-rate; 2 parallel seed-shard workers
  (the 15.7/15.12 concurrency: 2 units per 32B request on a 4-unit plan), per-seed crash-retry ≤ 4;
  one finalist at a time. Wall-clock ≈ 2.5 h per finalist.
- **Scoring:** delete the `*.audit.jsonl` sidecars (they collide with the scorers' seed glob — the
  harness's own `_drop_audit_sidecars` precedent), write `roster.json` via
  `scripts/_manifest_writer.py roster --sample-dir <dir> --num-players 9 --num-impostors 2
  --tasks-per-crewmate 2`, then run the committed CLIs unchanged: `scripts/validity_gate.py <dir>
  --json --expected-model Qwen/Qwen3-32B --require-zero-cost`, `scripts/measure_baseline.py <dir>
  --json`, `… --watchability --json --baseline-id baseline-3`, `… --funnel --json`.
- **The proof that the learned factory produced the bytes:** the five-field `tactical_policy` stamp is
  read back from EVERY recording via `orchestrator.replay.read_tactical_policy_stamp` (never echoed
  from the launch config), asserted uniform across all 50 games, and asserted equal to the committed
  sidecar digest. Both the read-back stamp and the sidecar sha it was verified against are carried in
  every committed jsonl row, so a post-15.18 reviewer re-checks the equality from
  `results-finalist-eval.jsonl` + `training/artifacts/impostor/<entrant>/weights.json.sha256` alone.
- **Provenance separation:** the RAW recordings are pause working artifacts — they live outside the
  repo tree, do NOT join `replays/samples/` or `replays/ml_corpus/`, and are re-recordable from this
  recipe; what is committed is their measurement.

### 3.2 Results — source: `training/reports/results-finalist-eval.jsonl` [RAN]

| finalist | stamp==sidecar (50/50) | validity gate | referee mean/med (passed) | imp. win | ej. accuracy | genuine conv. | witnessed rate | flags/meeting | backed conv. |
|---|---|---|---|---|---|---|---|---|---|
| utility-es | @@UTIL_STAMP@@ | @@UTIL_GATE@@ | @@UTIL_REFEREE@@ | @@UTIL_WIN@@ | @@UTIL_EJACC@@ | @@UTIL_CONV@@ | @@UTIL_WITN@@ | @@UTIL_FLAGS@@ | @@UTIL_BACKED@@ |
| policy-es | @@POL_STAMP@@ | @@POL_GATE@@ | @@POL_REFEREE@@ | @@POL_WIN@@ | @@POL_EJACC@@ | @@POL_CONV@@ | @@POL_WITN@@ | @@POL_FLAGS@@ | @@POL_BACKED@@ |
| (baseline 3, FSM, same seeds) | fsm-default | PASS | 39.83 / 47.5 (PASS) | 0.30 | 0.697 | 0.769 | 0.0325 | 1.863 | 0.607 |

@@FINALIST_NARRATIVE@@

### 3.3 Divergence analysis — real path vs the fake/surrogate brackets

@@DIVERGENCE_ANALYSIS@@

---

## 4. The referee re-verdict — per channel, both probe runs

Rule (from the 15.18 contract): for each channel where EITHER probe run found an exploit, the
recommended floor is contracted into Wave 2 before any champion selection uses the referee; "cleared"
is available only where NEITHER run found one. The two runs: 15.14 fake-provider
(`training/reports/report-goodhart-probe.md`) and the 15.15 surrogate-path re-run
(`training/reports/report-impostor-bakeoff.md` §6). The surrogate run's composed verdict was **HELD**,
but held for a disqualifying structural reason (an over-ejecting, evidence-free meeting model —
ejection rate 0.924 vs the fake path's 0.000; the validity gate fail-closes every surrogate-path set) —
per the bake-off's own instruction it is NOT read as exploit-caught, and clears nothing on its own.

| channel (lever) | 15.14 fake-provider | 15.15 surrogate re-run | verdict | action |
|---|---|---|---|---|
| **`kill` / D2 separation** | **EXPLOIT: 6.51 → 16.62 (+155%)**, separation 0.20 → 0.84 with conversion pinned 0.00 | +7.5% (0.53 → 0.57), below the 25% bar — but the substrate is disqualified | **EXPLOITED** | **15.19**: conversion-coupled D2 floor — contracted regardless of the composed referee's HELD |
| ES random-init trace | +1.7% (6.51 → 6.63), below bar; both strict improvements decompose to the same D2-separation mover | champion 0.0 | covered | the same 15.19 floor closes the mover |
| `emergency` (meeting-farming) | null (6.10, −6% — D4 already saturated) | null | **cleared** | — |
| `report` | null (3.70, −43%) | null | **cleared** | — |
| `wait` (stall-to-clock) | self-defeating (0.10, −98%, validity FAIL) | null | **cleared** | — |
| `sabotage` | null (0.76, −88%) | null | **cleared** | — |
| 4p1i (all levers) | HELD (every gain ≤ baseline 1.45 — a null result under fake meetings, not "referee safe") | — | no exploit found | — |

The SAME Wave-2 contract (15.19) bundles the **subject-aware observation-backing re-anchoring**
(owner-ratified 2026-07-09, mid-wave review Q2): parity was correct for 15.2's cross-implementation
evidence, but a trained impostor can exploit subject-agnostic backing — utter a genuine vent sighting
of X in the turn that accuses innocent Y and the Y-accusation counts "backed." Floors are re-pinned
under the subject-aware definition on the same committed bytes so relative gates stay sound, the old
parity fixture is kept as a frozen historical pin, and 15.19 lands BEFORE any champion selection leans
on fine D2-conversion differences — the 15.21 deployment re-score and the 15.23 close gate both carry
the dependency edge. 15.19 also closes the §1 finding: supply floors whose baseline numerator is ≤ 1
(the 4p1i `witnessed_event_rate`, 1/55) become advisory rather than referee-failing.

Consistent with this ordering, decision 1 (§7) does NOT lean on fine referee differences: the champion
call rests on the gate, fitness, anchor-CE, the win/take shape, and the real-meeting-path §3 results,
with the referee used only at the coarse grain the un-hardened instrument supports.

One further referee-adjacent ask surfaced by the probe delta and recorded for Phase 17 (not Wave 2):
before the surrogate can ever serve as a referee-attack substrate, it needs a declared synthetic
provenance stamp or an explicit surrogate-path gate mode — today the validity gate correctly
fail-closes it (`cost_and_provenance_exact`), which is the right default and the reason the surrogate
runs stay diagnostic-only.

---

## 5. The Wave-0 §5 watch items — settled by data, not carried forward

### 5.1 The 4p1i eject-happiness uptick — the pre-registered adjudication

The Wave-0 close flagged: report-meeting ejections 10 → 22, accuracy 0.923 → 0.808 at the 15.7
re-record — variance or shift? The 15.18 contract pre-registered the test before the data was seen: a
two-proportion comparison of corpus-4p1i vs post-15.7 samples ejection accuracy, with a SHIFT verdict
only if the 95% CI excludes the compared value, and UNDERPOWERED recorded if the CI excludes neither
anchor.

Inputs, all **[RAN]** from the committed CLIs (`measure_baseline.py <set> --json`):

| cell | impostor ejections / total | accuracy |
|---|---|---|
| baseline-2 4p1i anchor (`audits/baseline2-final-measure.json`) | 12 / 13 | 0.9231 |
| post-15.7 samples 4p1i (`replays/samples/4p1i`) | 21 / 26 | 0.8077 |
| corpus 4p1i (`replays/ml_corpus/4p1i`) | 27 / 33 | 0.8182 |

The pre-registered computation (Wilson 95% CI on the corpus cell; two-proportion z corpus-vs-samples):

- Corpus 27/33 Wilson 95% CI = **[0.656, 0.914]**.
- vs the post-15.7 samples value 0.808: **inside** the CI (two-proportion z = 0.10, p = 0.92; diff CI
  [−0.190, +0.211]) — the two fresh, independent, same-substrate measurements AGREE.
- vs the baseline-2 anchor 0.923: **outside** the CI (upper bound 0.914 < 0.923).

On the rule's reading: the pre-registration's UNDERPOWERED arm is worded "if the CI excludes
*neither*" — defined over the two anchors the watch item names (the pre-Wave-0 0.923 and the post-15.7
0.808), which is how it is applied here: the corpus CI is checked against both, SHIFT if it excludes
the old anchor while agreeing with the fresh one, variance if the reverse, UNDERPOWERED if it excludes
neither.

**Verdict: SHIFT** — per the pre-registered CI rule, the fresh 33-ejection corpus evidence replicates
the 15.7 cell (~0.81–0.82) and excludes the old 0.923, so the uptick is a real substrate-level move of
the v5/v6 4p1i meeting layer, not run-to-run variance of one 50-seed record. Recorded honestly: the
exclusion is MARGINAL (0.914 vs 0.923), and a Fisher-exact sensitivity check against the tiny
baseline-2 cell (12/13, n=13) gives p = 0.65 — the pre-registered CI rule is the verdict of record, the
sensitivity note is why no alarm accompanies it. Direction and size: 4p1i ejects more (13 → 26/33
ejections per 50 games) at slightly lower accuracy (~0.81), while impostor win FELL (0.38 → 0.28
samples, 0.16 corpus) and innocent-reporter ejections stayed shut (1 and 3 of the two fresh sets vs 22
pre-Wave-0 on 9p2i) — an eject-happier but not railroading regime. **[RAN]**

**Wave-2 implication (recorded in the decisions):** no structural contract — the shift is a
reference-set calibration fact, not a defect. Its two consequences are already carried: (a) 4p1i
canaries move to corpus-scale denominators (the Q3 rule, §6); (b) the 4p1i one-event
`witnessed_event_rate` floor degeneracy exposed by the same data is fixed in 15.19 (§4).

### 5.2 The other two §5 items — dispositions

- **v5 impostor self-accusation (3/851 9p2i ballots).** A dialogue-quality artifact of the v5
  elicitation prompts; firewall-clean. No phase-15 action possible under record-only discipline —
  settled as a Phase-16 Voice & Judgment scoping input, restated in the hand-off (§9). [VERIFIED]
- **v5 vent uptake real but partial (53/73 mentioned, 18 unspoken).** Settled by corpus-scale data
  **[RAN]**: on the 3× corpus the same instrument measures vent_mentioned 188/255 = 0.737 vs the
  samples' 53/73 = 0.726, and structured vent observations 201/255 vs 55/73 — the uptake REPLICATES at
  scale; the residual unspoken tail is stable and is Phase 16's elicitation scope, not a phase-15
  regression.

---

## 6. Canary denominators — the Q3 rule applied

Owner-ratified rule (2026-07-09, Q3): canaries are judged on the LARGEST same-substrate,
validity-gated set available — today the corpus — with the 50-seed samples figure reported alongside
for ladder continuity; the samples sets remain the byte-identity/provenance anchor. All cells **[RAN]**
from `measure_baseline.py --json`:

| canary (9p2i) | corpus (judged) | samples (continuity) | baseline-2 anchor | read |
|---|---|---|---|---|
| genuine-class conversion | **34/52 = 0.654** | 10/13 = 0.769 | 0.625 | above anchor on both — the over-damping canary is quiet |
| R1 eject-decided win share | **109/150 = 0.727** | 34/50 = 0.68 | 24/50 = 0.48 | deduction-decided wins UP |
| ejection accuracy | 0.702 (252/107 of 359) | 0.697 (76/33 of 109) | 0.525 | UP, replicates at 3× |
| impostor win rate | 0.233 | 0.30 | 0.40 | eased; the floor question belongs to the referee, which passes |

Corollary recorded with decision 2: had the deployment landed on branch B, baseline 4 would require a
corpus-scale companion record before its canaries mean anything at n≈13 genuine-class opportunities per
50-seed set. Branch A ships no baseline 4, so the corollary stays dormant but recorded.

---

## 7. THE SEVEN DECISIONS

Each block follows the Task-14.6 locked-decision shape; sign-off is the owner's merge of this PR.
The NO paths — what was rejected and why — are inside each block.

### Decision 1 — winning method + champion candidate

**LOCKED DECISION (owner, 2026-07-10) — champion = `utility-es`:**
- **method = learned utility scorer over FSM-proposed options + (1+λ)-ES** (the bounded path: the menu
  is the FSM's own option ladder, so off-menu behavior is structurally unreachable).
- **champion artifact = `training/artifacts/impostor/utility-es/weights.json`**, sha256
  `6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`, encoder
  `impostor-option-features-v1`, 19-weight interpretable genome.
- **anchor-CE ceiling 2.0 is RATIFIED as a flag, never a drop rule** (the bake-off's documented choice,
  now audit-ratified; policy-es's 2.016 stands as a flag that counted against it in the tie-break, not
  a disqualification).
- **Rejected — `policy-es` (rank 2):** best fake-path fitness (19.066 vs 18.671, a 2% edge inside
  seed noise per the report's own ranking-stability caveat) but the one anchor-CE-FLAGGED candidate
  (2.016 > 2.0), the largest surrogate divergence (−11.81), the vent tell (20.3 vent
  submissions/game vs the FSM's 7.3, a channel fake meetings never punish), and @@POL_REJECT@@.
- **Rejected — `map-elites`:** the diversity instrument, not the champion — its champion converges on
  policy-es's low-exposure heavy-vent region (which is itself the finding: the monoculture direction),
  0.9 fitness behind the best entrant (18.198 vs policy-es's 19.066), take-rate 0.924.
- **Rejected — `bc-dagger`:** a measurement, not a candidate (held-out intent agreement 0.365 vs the
  0.90 bar); its value was as the ES warm start and the encoder-sufficiency finding.
- **Evidence:** §2.1 (the committed tuple), §3.2–3.3 (the real-LLM finalist evaluation this decision
  explicitly cites: @@DECISION1_EVIDENCE@@). Method-vs-method, one protocol, and the only entrant that
  is simultaneously gate-clean, KL-closest to the legible anchor, best under the referee's coarse
  grain, most robust to the meeting-model swap, and confirmed on the real meeting path.

### Decision 2 — deployment end-state

**LOCKED DECISION (owner, 2026-07-10) — branch A: the opt-in factory (Tasks 15.20 + 15.21):**
- **end-state = `build_learned_agent_factory()` beside the untouched FSM default**; recording/eval
  select it explicitly (config/CLI); `replays/samples/` stays byte-identical; the 15.9 stamp
  distinguishes every recording. Cheapest, fully reversible, A/B-hygienic.
- **Rejected — branch B (new default + baseline-4 re-record), for this wave:** (a) the referee that
  would bless a default is not yet hardened — 15.19's conversion-coupled D2 floor and subject-aware
  backing land AFTER this decision by design, and a default flip blessed by a known-exploitable
  instrument is exactly the self-certification trap this task exists to prevent; (b) the real-LLM
  evidence is one 50-seed measurement per finalist — enough to pick a champion among candidates, not
  enough to re-anchor the canonical baseline every downstream measurement stands on; (c) branch B's
  true cost includes the Q3 corollary (a corpus-scale companion record, ~7 h operator time) plus the
  full byte-coupled re-pin sweep of a 14.12-pattern re-record; (d) DESIGN.md's own constraints (§3.5
  A/B-hygiene freeze, §11.4 re-record scope) make opt-in the low-regret end-state. Re-evaluated at
  phase close / Phase 17 behind the hardened referee — the corollary stays recorded.

### Decision 3 — torch

**LOCKED DECISION (owner, 2026-07-10) — keep experiment-tier; promotion DECLINED; the Wave-2 torch
track is RETIRED:**
- **torch does NOT enter `pyproject.toml`/`uv.lock`** (the 2026-07-05 posture holds; nothing in the
  probe's evidence argues for the 4.5 GB overlay, the unverifiable cross-host determinism, or a CI
  story).
- **The probe stays in-tree** (`experiments/lab/torch_probe/`, mypy-excluded, opt-in via `uv run --with
  torch`) as the pre-registered instrument, re-runnable IFF a future phase re-opens impostor reward
  design — Wave 2 does not (§8), so no Wave-2 torch contract exists.
- **The distillation route is recorded as permanent doctrine:** distill-to-pure-Python is mechanically
  proven (student–teacher agreement 0.9709 ≥ the 0.90 bar on attempt 2), so even a future torch win
  ships without the dependency — and this wave it is capability-empty (student fitness −2.58, anchor-CE
  11.72, 256 off-menu decisions: closed-loop BC shift).
- **Rejected — promote:** measured gain absent (negative): best torch 11.05 vs ES 19.07 fitness, 0.267
  vs 1.00 win rate, ~2× train wall-clock, take-rate 1.00 greedy convergence on all three seeds.
- **Rejected — delete the probe now:** the reward-design confound is real (the objective, not the
  optimizer, may be what RL exploited better and played worse); the probe is the cheap instrument to
  re-run if that ever re-opens. Disposition re-stated at close (15.23).
- **Evidence:** §2.3; `experiments/lab/report-torch-probe.md` (its own recommendation, adopted).

### Decision 4 — Wave-2 co-evolution

**LOCKED DECISION (owner, 2026-07-10) — NO-GO for Wave 2:**
- **No co-evolution contract is authored**, stabilized or otherwise. The precondition every stabilizer
  assumes — an inner-loop meeting model both populations can actually move — does not exist at $0: the
  ballot surrogate landed NO-GO (SKIP-vs-eject 0.769 < the population's own always-eject constant
  0.802; diagnostic-only, fallback (a)), and the fake provider mints no evidence (0/116 ejections),
  under which the crew side already demonstrated the degenerate optimum (win-by-meeting-starvation,
  §2.2). Alternating populations against a dead meeting layer selects for exactly the starvation
  equilibria FO-2 collapsed into.
- **Rejected — GO with the full stabilizer stack (HoF/PFSP/reduced-virulence/per-generation gating):**
  the stack addresses opponent-population pathologies, not a meeting-model vacuum; it would stabilize
  convergence toward the wrong fixed point.
- **Deferred to Phase 17** (the roadmap's co-adaptation phase): re-ground the surrogate on the newest
  baseline, re-verdict it against the same population-relative bar, and only then revisit — with the
  stabilizer stack as the entry condition, never the naive two-population form.
- **Evidence:** `training/reports/report-ballot-surrogate.md` §5 (NO-GO), `report-crew-track.md` §4,
  `report-impostor-bakeoff.md` §6 (the bracket), FO-2 (re-run on current HEAD, per the phase preamble).

### Decision 5 — the crew observation-surface change (owned-task set)

**LOCKED DECISION (owner, 2026-07-10) — YES (Task 15.22):**
- **`SelfView` gains `owned_task_ids`** — the recipient's OWN unfinished task instances, the one field
  the crew report's ask names — behind the full four-item review (ObservationService scoping, leak-suite
  extension, byte-shape discipline, the encoder note), exactly as `training/reports/report-crew-track.md`
  §7 specifies. Firewall-clean by construction: a self-channel field that leaks no role bit (the
  impostor's view carries its camouflage set, mirroring `pending_task_id`).
- **The retrain is scoped WITH a structural guard:** the 15.16 failure mode (win-by-starvation) is made
  unreachable by an FO-8-style interrupt-preserving constraint (report is not suppressible), so the
  gate-valid crew ceiling — the number 15.16 could not measure — finally gets measured. Crew champion
  ADOPTION is explicitly not a Wave-2 goal; the numbers are Phase-17 scoping inputs.
- **Rejected — NO / defer the surface:** Phase 16 (Voice) and Phase 17 (co-adaptation) both consume the
  crew surface; landing the one-field widening now, behind the full leak review, de-risks both and is
  the only way to measure the ceiling decision 4's Phase-17 revisit will need. The measured case: the
  trained crew raised completion 0.759 → 0.919 while task PACE fell 35.08 → 29.80 tasks/100 ticks —
  nearest-of-N selection and same-room batching attack exactly the lever the closed surface hides.
- **Rejected — the emergency-uses-remaining rider:** the sketch offered it "if taken"; no measured need
  exists (the emergency channel was a Goodhart null in both probe runs, §4) — the widening stays
  minimal.
- **Evidence:** §2.2; `report-crew-track.md` §5 (the unmeasured ceiling), §6 (the Q6 diagnostic:
  cue-separation +0.10, credited-rate 0.137 — mostly un-cued coverage, i.e. training crowding, which the
  owned-task features give the optimizer a legitimate alternative to), §7 (the ask).

### Decision 6 — inference weight representation + the determinism-loosening census

**LOCKED DECISION (owner, 2026-07-10) — float-hex RETAINED; int-quantization DECLINED this wave:**
- **The committed representation stays float64-hex JSON** (the 15.10 contract). The champion's forward
  pass is a 19-weight LINEAR scorer — a float64 dot product with no transcendental — so the libm
  surface is empty by construction for the shipped policy.
- **The owner-ratified libm posture (2026-07-09, Q4) is recorded and contracted:** no libm-free forward
  pass is demanded; instead Wave-2 productization (15.20) MUST gate on bit-exact equality of the
  numpy-trained and pure-Python-shipped forward passes over the committed float-hex weights — a test,
  not an architecture change. Replay byte-identity is untouched by libm either way.
- **Same-host generation scope, documented and accepted:** the MLP family (policy-es / map-elites /
  bc-dagger) uses tanh; had an MLP candidate won, cross-host GENERATION determinism would rest on libm
  and int-quantization's LUT-tanh would have been the fix. The linear champion moots this; the trade is
  recorded so a future MLP champion re-opens it deliberately.
- **Rejected — int-quantize now:** its only measured benefit (cross-host generation nearly free via
  fixed-point + LUT tanh) does not apply to a linear champion, and it would add a quantization step to
  the exact cross-implementation equality 15.20 must prove.
- **The determinism-loosening census — every loosening now live [VERIFIED]:**
  1. `engine.rng.RngStateHashPolicy` fast path (15.8.1) — opt-in, threaded explicitly, accepted ONLY by
     no-replay constructions; every committed/recording path byte-unchanged (test-pinned).
  2. The no-replay training mode (`replay_path=None`, 15.8.1) — records nothing; refuses a policy stamp
     loudly.
  3. `episode_boundary="first_meeting"` (15.8) — the one deliberate truncation mode; truncated episodes
     are marked and never scored as full games.
  4. The torch probe (15.17) — experiment-tier: same-host double-run hash PASSES, cross-machine
     bit-identity unverifiable, quarantined outside `pyproject.toml` behind `uv run --with torch`.
  5. The surrogate meeting path (15.13) — synthetic ballots with empty LLM metadata; deliberately fails
     the validity gate's provenance check (fail-closed) and ships diagnostic-only.
  Production inference under `agents/` and every replay/recording-adjacent path remains
  byte-deterministic — enforced by the firewall test (no numpy/torch under `agents/`), the 15.10
  determinism harness, and the bare-environment byte-verification of all committed sets (§1).

### Decision 7 — the surrogate re-grounding cadence

**LOCKED DECISION (owner, 2026-07-10) — the report-§8 cadence is adopted as standing policy, plus a
per-baseline re-verdict:**
- **Mandatory re-ground** after (a) ANY mover (tactical-policy) change, (b) ANY meeting-layer/prompt
  change, (c) a staleness-cap hit (50,000 simulated meetings, sha-keyed, cumulative —
  `training/artifacts/surrogate/max-uses.json`).
- **Plus, at every new recorded baseline:** the surrogate is re-fit on the fresh corpus slice and
  re-verdicted against the SAME population-relative GO bar (Q1: top-1 ≥ 0.75 × ceiling AND > re-baselined
  FO-6 AND SKIP-vs-eject > the population's always-eject constant) before any training use. It remains
  **diagnostic-only until a future verdict GOes** — the NO-GO is not re-litigated between baselines.
- **First scheduled re-grounding: Phase 17** (the roadmap's co-adaptation re-run), or earlier if Wave
  2's 15.22 retrain would otherwise consume surrogate meetings (it does not — it trains on the
  fake-provider fallback (a), per the NO-GO's pre-committed consequence).
- **Rejected — a fixed calendar cadence:** every absolute number in this project's history moved when
  the population changed (the Q1 rationale); the cadence binds to CHANGE EVENTS and the cap, not the
  calendar.
- **Evidence:** `training/reports/report-ballot-surrogate.md` §5 (the verdict), §8 (the recipe adopted),
  `max-uses.json` (the cap artifact).

---

## 8. Wave 2 as authored — the skeleton mapping

Authored into `tasks/phase-15.md` (IDs 15.19–15.23), validator-green (**[RAN]**:
`validate_task_docs.py` — 227 tasks and 227 prompts; `generate_prompts.py --check` — all in sync; the
five new prompts are generator output). Every sketch bullet became a contract or is dropped with its
reason in the Wave-2 preamble:

| sketch bullet | disposition |
|---|---|
| Champion productization | **15.20** (`agents/tactical/learned/`, the Q4 bit-exact gate, the stamp accessor) |
| Deployment branch A | **15.21** (the `--agent-factory` CLI, auto-stamp, mis-stamp guard) — decision 2 |
| Deployment branch B | **dropped** — decision 2's NO path (rationale in the block) |
| Referee hardening | **15.19** (conversion-coupled D2 + subject-aware backing + advisory rare-event floors) — lands before any selection leans on the referee (edges from 15.21/15.23) |
| Bounded co-evolution | **dropped** — decision 4 NO-GO |
| Crew surface change | **15.22** (the SelfView widening + the gate-valid retrain) — decision 5 |
| Torch decision execution | **no contract** — decision 3 (keep experiment-tier = nothing to execute; permanent record here + re-stated by 15.23) |
| Hand-off to Phase 16 | authored as its own `tasks/phase-16.md` per the roadmap — §9 lists its scoping inputs |
| Phase close | **15.23** (the champion close recording through the 15.21 CLI, the hardened-referee pass-bar, the banner flip) |

The end-of-phase merge criteria placeholder is replaced with the branch-A criteria (the phase file's
"Merge criteria (end-of-phase — locked at the PAUSE, 2026-07-10 …)" block), and the STATUS banner
records the pause outcome and the Wave-2 dispatch.

---

## 9. Asks and hand-off inputs (owner-side; nothing here edits owner files)

- **[PROPOSED] DESIGN.md amendment ask (at close):** §12 frames the RL extension as "the FSM is
  replaced with a small neural policy"; the shipped end-state is subtler — the FSM stays the default,
  anchor, oracle, and fallback, with the learned scorer as an opt-in factory. One sentence in §12 (or
  §4.4) recording the coexistence posture would keep the doc honest. Owner-side; recorded here, not
  edited.
- **Phase-16 scoping inputs (for the future `tasks/phase-16.md` author):** v5 vent-elicitation uptake
  is real but partial and stable at scale (188/255 corpus, §5.2); the v5 impostor self-accusation
  artifact (3/851 ballots); the residual zero-flag conviction channel and the citation gate; the
  pooling levers deliberately not pulled in Wave 0; the subject-aware backing definition (15.19) as the
  citation-gate's natural referee counterpart.
- **Phase-17 inputs:** decision 4's entry condition (re-grounded, re-verdicted surrogate + stabilizer
  stack); decision 7's cadence; the 15.22 gate-valid crew ceiling; the surrogate synthetic-provenance
  ask (§4); the branch-B revisit with the Q3 corpus-companion corollary.

---

## 10. Prioritized punch list

**Dispatch now (Wave 2, in edge order):**
1. 15.19 referee hardening — the gate everything else's selection leans on (§4). *The single
   highest-leverage item.*
2. 15.20 champion productization — the Q4 bit-exact gate is the spine (§7 decision 6).
3. 15.21 opt-in deployment CLI — closes the finalist recipe's Python-driver gap (§3.1).
4. 15.22 crew owned-task surface + the gate-valid retrain (§7 decision 5).
5. 15.23 phase close — the hardened-referee pass-bar on a fresh champion recording (§8).

**Standing obligations (no contract needed):**
6. Every operator record from here on follows the Q5 provenance convention (§3.1 demonstrates it).
7. Canaries are read on corpus denominators with samples alongside (§6) — including by 15.23.
8. The surrogate use-counter stays sha-keyed and cumulative; any cap-hit triggers decision 7's cadence.

**Explicitly not done, on purpose:**
9. No baseline 4 (decision 2), no co-evolution (decision 4), no torch promotion (decision 3), no
   referee edit inside this task (15.19 owns it), no crew champion adoption (15.22 measures, Phase 17
   decides).

---

## 11. What I did not do / caveats

- **The finalist evaluation is one 50-seed recording per finalist** — no repeat-variance story on the
  real path (the fake-path determinism hashes cover the policy side; the LLM side varies by provider
  nondeterminism). Decision 1's margin should be read at that grain; decision 2 (opt-in) is the hedge.
- **The finalist recordings are uncommitted working artifacts by contract** — re-derivable from §3.1;
  the committed truth is `results-finalist-eval.jsonl`. They deliberately never joined
  `replays/samples/` or `replays/ml_corpus/`.
- **The referee numbers quoted anywhere in this audit are the UN-hardened instrument's** — that is why
  §4's ordering exists and why no selection above leaned on fine D2-conversion differences.
- **The 4p1i SHIFT verdict is marginal** (§5.1) — recorded per the pre-registered rule with the
  sensitivity note beside it, not as an alarm.
- **I did not re-run the Goodhart probe on the real-LLM path** (~the probe's full ES loop against paid
  meetings was never in scope); the real-path spot-check the bake-off asked for is §3's finalist
  measurement, and the exploit adjudication rests on the fake-path findings per its instruction.

---

## 12. Bottom line

The phase's design premise held: measure first, then decide. Four methods entered one harness; the
cheap, legible, menu-bounded one won and was confirmed on the real meeting path; the referee's one
exploited channel and its definition debt are contracted to land before anything leans on them; the
watch item is settled as a real-but-benign shift; torch and co-evolution each got a clean, evidenced
NO; and Wave 2 exists as five validator-green contracts that productize exactly what the evidence
supports — an opt-in champion beside an untouched baseline — while leaving every irreversible move
(default flip, baseline 4, crew adoption) behind the hardened gate that Wave 2 builds first.
