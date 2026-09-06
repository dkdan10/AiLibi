# The Phase-19 ML tier map — keep / freeze / retire, the freeze labels, and the reopening checklist

This file is the component-by-component ruling on the ML program's surfaces,
written down where the next agent will trip over it (Task 19.18). It records
**locked decision 2** (the evidence-first hybrid tier map) and **locked
decision 3** (the re-open fork: record the fork, decide later) from the
Phase-19 register (`tasks/phase-19.md` §Locked decisions, owner-ratified
2026-08-03), resolving the component boundary the two input audits disputed
(`audits/audit-phase-19-triage.md` §7 items 19+21, completeness-pass items
21–22 at `audits/audit-phase-19-triage.md:90-91` — the contract's "§8 rows
21–22" pointer resolves there; the §8 claim table itself ends at row 20).

Three rules of use:

1. **Every FROZEN header in the repo names this file.** The header registry in
   §5 is exhaustive; the grep there must match it exactly.
2. **Nothing here re-derives a number.** Every measured basis below quotes the
   committed reports/audits by line. Recompute nothing; cite.
3. **This map is documentation of a ruling, not new work.** The RETIRE column
   is implemented by Task 19.19 (consumer-verified deletions), the test-tier
   markers by 19.27, the artifact prune by 19.22. Labels and docs only landed
   with this map — zero behavior bytes.

**Start here.** The ML program itself — problem, environment, method, one results
table, the two behavioural findings, and the limitations — is
[`docs/ml-program.md`](../docs/ml-program.md). This file is the disposition ledger
for the surfaces that program left behind: what it positively learned (§1), the
keep/freeze/retire map (§2), the freeze label and its coverage registry (§3, §5),
and the checklist for reopening it (§7).

## Current model evidence boundary

The ledger below is historical. Current scoring and installation require a
version-two fit identity from `training/provenance.py`: replay, roster, split
and manifest bytes, plus the actual feature/label builders' local import
dependencies, canonical map, locked dependencies and installed numerical
runtime. Changed roster or derivation bytes fail the model loaders' identity
check. Unrelated reports are excluded.

Committed fit sidecars remain version one. Use `evidence_scope="historical"`
explicitly to restore diagnostics; that scope cannot install a training-time
surrogate or composed runner. Current use fails until a newly adopted corpus
supports a separately authorized fit. Synthetic unit-test weights use
`evidence_scope="synthetic-test"`, outside the source tree and without a
fabricated fit sidecar. `scripts/verify_ml_evidence.py` checks historical
identities under their original definition, not as current fit certificates.

A future fit must write `SurrogateFitCorpus(fingerprint_version=2, ...)` with
`fit_corpus_fingerprint(corpus_dir)` and the actual weights digest. Current
campaigns recompute their named `compute_substrate_sha.v2` or
`bakeoff_substrate_sha.v2` identity before work; founder loading checks both the
definition and its source bytes. Historical readers have separately named
`historical_*` fingerprint functions. Old reports, weights and corpus bytes
are never relabeled by rewriting their provenance.

Current campaigns refuse enabled ambient experiments and unbound custom meeting
factories before writing. Their recorded runtime profile uses the fake provider,
the current prompt family and all experimental gates OFF; it is explicitly
passed through fitness, benchmark and exploiter games. Later environment changes
cannot select another profile. Other arms need a separately bound campaign
definition and authorization.

The current conviction row calls its persisted count
`recorded_non_vent_flags`. Only `to_historical_json` and
`from_historical_json` use the original `rederived_flags` spelling.

## 1. What the program POSITIVELY learned (findings, not plumbing)

Recorded here so the tier map preserves results, not just machinery:

- **N1 — the learned mover kills into witnesses at ~3.3× the scripted rate.**
  Crew-witnessed-kill rate **30/197 = 0.15228** vs the FSM comparator's
  **8/174 = 0.04598**, **z = +3.370**, sign-reproduced 3/3
  (`audits/audit-phase-18-flip-emergence.md:466-471`; restated with the
  per-tranche triples at `audits/audit-phase-18-close.md:732-743`, §6.1 L4).
- **N2 — the learned mover emits a kill class the scripted FSM cannot:
  co-present kills.** **20/197 = 0.10152 vs 0/174**, **z = +4.321**, 3/3; the
  committed FSM kills only when alone — 0 co-present kills on all 863
  corpus-pinned kills (same anchors).
- Both are ruled **NOT-DEMONSTRATED under the registered discipline** — not
  because the effects are doubtful (both are selected-for, present on all
  eight learned-impostor arms) but because clause (c) is unsatisfiable by
  construction: no campaign lever enables them, so no ablation can be named
  (`audit-phase-18-flip-emergence.md:471-481`). A §6.c-satisfiable claim needs
  a lever-scoped training contract in a future campaign (close §6.1 L4).
- **The clean negatives, kept as results:** the crew stack's triple negative
  (§2, FREEZE); the torch PPO probe (`experiments/lab/torch_probe/`); the
  policy-ES real path (win edge collapsed to 0.02, Δ −0.34 —
  `report-finalist-eval.md:268-271`); FO-6's always-SKIP collapse (25.7%
  top-1 vs the 70.6% ceiling; binary accuracy 38.1% vs always-eject 78.4% —
  `report-meeting-table.md:173-187`, `:227-229`).
- **The statistical honesty note (19.20 owns the erratum):** the shipped
  champion's paired edge is statistically unresolved at n=50 — exact McNemar
  recomputed from `results-finalist-eval.jsonl`: ea4bc955 17/4 p=0.0072;
  bfd145cb 20/5 p=0.0041; **shipped 6d327dcb 15/9 p=0.3075 (n.s.)**; 7f73929d
  12/3 p=0.0352, fails Bonferroni α=0.0125
  (`audits/audit-phase-19-triage.md:196`, §8 row 4 — the report itself
  commits only the crew paired cell, `report-finalist-eval.md:1745-1761`).
- **Red-Queen context (close §6.1 L10):** the cycling-detector signature is
  PRESENT on the general-base impostor (flat anchor + oscillating
  co-matchup); the owned-task crew reads progress while its impostor
  plateaus — "Phase-19-visible context, not a contract"
  (`audits/audit-phase-18-close.md:769-771`).

## 2. The tier map

### KEEP — committed evidence and always-on gates still execute it

| Component | Measured basis (committed bytes, cited by line) | Where it lives / consumer boundary |
|---|---|---|
| Compact learned inference + train/serve parity gates | The always-on suite executes them on every gate run (parity, artifact-digest, determinism — the `bash scripts/check.sh` tier) | `agents/tactical/learned/` + its tests; consumed by the recording/replay paths |
| Corpus verifier + splits | The frozen baseline-6 corpus and its committed by-game splits are the substrate every instrument below was measured on: `replays/ml_corpus/{4p1i,9p2i}/splits.json`. The byte VERIFIER is `scripts/verify_samples.sh` (backed by `scripts/_verify_samples.py`): it reconstructs the recorded state-hash chain byte-identically under the current engine — bare it walks every `replays/samples/` set, and the corpus form is `scripts/verify_samples.sh replays/ml_corpus/<set>` (`replays/ml_corpus/README.md:522`; advertised at `scripts/record_ml_corpus.sh` §usage) | Split consumers: `training/surrogate/dataset.py::load_splits` reads `splits.json` beside whatever replay set it is handed (it is a reader, not the home); `training/bakeoff/harness.py` pins `CORPUS_SPLITS_PATH = replays/ml_corpus/9p2i/splits.json`. Recorded by the frozen Bash recorder (§4) |
| Conviction model (the WHETHER channel) | GO on its own pre-stated bar: flag-count Spearman **0.5782** (bar ≥ 0.5), conversion recall **45/47 = 0.9574** (bar 0.6375) — `training/reports/report-conviction-model.md:201-207`. Conversion accuracy **90/96 = 0.9375** (`report-conviction-model.md:196`) | `training/conviction/`; judged by `training/conviction/fidelity.py` (frozen evidence reader) |
| — the terminology ruling | **0.9375 is CONVERSION-LABEL accuracy, never a meeting decision number.** The label is testimony-backed conversion; re-used as an eject/skip gate it measures **0.8646** (`report-composed-runner.md:161-167`: "the 0.8646 is the honest measurement of that re-use … below the model's 0.9375 accuracy on its own conversion label"). The triage refuted the "decision accuracy 0.9375" phrasing (`audits/audit-phase-19-triage.md:211`, §8 row 19) | Applies everywhere the number is quoted (19.20 owns the report errata) |
| Surrogate RANKING channel (the WHO channel) | top-1 **76.7% (46/60)**, top-2 **91.7% (55/60)** on the held-out 30-game / 96-meeting split — `training/reports/report-ballot-surrogate.md:238-247`; ranking axes 1–2 PASS the GO bar (`:309-320`); reproduced exactly on the runner path (`:198-201`) | `training/surrogate/` (predictor, dataset, ballots); consumed by the composed runner and the bake-off harness (see the boundary, §2a) |
| ES core + champion acceptance | ES re-runs reproduce committed champions byte-identically (`report-impostor-bakeoff.md:28-37`; `report-crew-track.md:27-35`); the digest pin (`tests/training/test_es.py`) and the acceptance gates stay always-on. The acceptance RULING stands: champion stays **opt-in**, scripted FSM stays default — "Neither finalist satisfies referee-PASS AND retained-win-edge" (`report-finalist-eval.md:268-279`); "no arm on this table clears a referee-PASS AND retained-edge bar" (`:1082-1107`) | `training/bakeoff/` (LIVE — es.py, harness.py, utility_es); the harness is also the surrogate factory's principal functional consumer |

Always-on test families this map keeps un-marked (triage §7 item 19): champion
acceptance, ES, determinism, artifact-digest, train/serve-parity, the leak
property sweep, prompt byte-golden, and the prompt-regression close gate.
Campaign-only test families go behind opt-in markers in **19.27**, driven by
the FREEZE column below.

### 2a. The standalone-vs-dependency boundary (the one disputed component, stated explicitly)

The ballot surrogate has two channels and they get opposite rulings:

- **RANKING is kept** (46/60 top-1, above).
- **The standalone DECISION arm is retired** (19.19). Its committed census on
  the held-out split: **0 ejections · 96 skips** — the predictor "casts
  SKIP-heavy ballots whose tally skips **every** test meeting (0 correct
  ejects; all 60 true ejections called SKIP)", decision accuracy 36/96 =
  0.375 = the trivial always-SKIP constant, below the 0.625 always-eject
  bar — `report-ballot-surrogate.md:335-340`, verdict NO-GO `:309-320`,
  `surrogate_role="diagnostic-only"` `:322-325`. (The planning shorthand
  "96/96 held-out SKIP" — `audits/audit-phase-19-triage.md:169` — names this
  all-SKIP census.)

**What "retire" may touch, verified at HEAD (94d8809):** exactly three
production files import `training.surrogate.runner`, and only two names cross
the boundary —

- `training/bakeoff/harness.py:159` imports `SurrogateUseCounter` +
  `load_surrogate_runner_factory`; calls the factory at `:1763`
  (`evaluate_candidate`) and `:2072` (`run_goodhart_surrogate_rerun`) and
  USES the returned factory (AST call-site pins:
  `tests/training/test_bakeoff_harness.py:1742-1772`);
- `training/composed_runner.py` imports both names and calls the factory once
  inside `load_composed_components` purely as the sha/staleness
  **verification fence** (the returned factory is discarded — the comment
  above the call says so);
- `training/coevo/driver.py` imports `SurrogateUseCounter` alone.

`SurrogateMeetingRunner` itself has **no by-name production importer** — it is
constructed only through the factory. So the FACTORY, the CLASS, and the
COUNTER all **stay** where the composed runner's fence and the harness consume
them; what retires is only a surrogate-ONLY runner exposure that 19.19's
consumer grep proves free. A no-consumer-free-exposure outcome is a recorded
no-op, not a failure (`audits/audit-phase-19-planning.md` §6 correction 2).

### FREEZE — labeled, kept for evidence, no new search

| Component | Measured basis (cited by line) | Freeze reason on the header |
|---|---|---|
| Composed runner (`training/composed_runner.py`) | GO on its own bar — decision **83/96 = 0.8646** (bar > 0.625), exact-outcome **76/96 = 0.7917** (informational) — `report-composed-runner.md:118-127`, `:153-159`; Goodhart leg HELD, zero machinery blockers, champion scores −0.2269 BELOW the honest baseline (`:29-31`, `:202-206`) | **Optional-diagnostic.** Its substrate is the zero-LLM meeting path: every composed-path arm fails `cost_and_provenance_exact` structurally ("A composed meeting makes zero LLM calls … no model row exists to stamp — structural for ANY zero-LLM meeting path, not behavioral" — `:229-239`), so "composed-substrate probe reads are diagnostic-grade until the provenance check has a stamped-substrate answer for LLM-free meeting paths" (`:246-253`). It also lacks real transcript flags/model provenance (triage item 22, `audits/audit-phase-19-triage.md:91`) |
| Crew stack (`training/crew/`) | **The FREEZE column's clean negative.** Gate-valid ceiling ZERO: win 0/30 vs the FSM's 3/30 under a PASSING validity gate (`report-crew-owned-tasks.md:14-22`); "no crew candidate is any closer to the selection bar than Phase 15 left it" (`report-crew-track.md:269-273`); "No crew finalist clears the bars from this campaign's evidence" (`report-crew-campaign.md:608-613`) at 183% noise-to-threshold with 0 of 2 referee PASSes replicating (`:238-251`) | Clean negative, honestly measured; kept as evidence + the coevo opponent surface |
| Co-evolution / campaign machinery (`training/coevo/`, `training/scenarios.py`, `training/anchor_study.py`) | Concluded campaigns. Screening instability: win-rate swings ≥1 game for **10 of 22 arms** between tranches, referee PASSes 3 recorded / 1 retested / **0 replicated** (`report-impostor-campaign.md:415-430`, `:442-453`); "this report does not claim … that any candidate passes or fails the §1.3 flip bar" (`:455-465`). The anchor study is report-only — no champion ships; NO cell passes the supply floors (`report-anchor-study.md:19-24`, `:95`). The scenario selector seam was never exercised by a campaign (both campaigns' rows carry `scenario_labels: []` — `audits/audit-phase-18-close.md:1012`) | Campaign-only test families go behind opt-in markers (19.27) |
| The fidelity harnesses (`training/conviction/fidelity.py`, `training/surrogate/fidelity.py`) | The pre-stated GO bars above were judged through them; they re-run over committed bytes only | Evidence readers for frozen instruments |
| `eval/off_menu.py` | Its own docstring states the vacuity: the menu-bounded champion is on-menu by construction, "The instrument is therefore VACUOUS for the champion" (`eval/off_menu.py:12-34`); zero non-test consumers (grep-verified in-session; only `tests/eval/test_off_menu.py`, `tests/training/test_finalist_eval_pins.py`, `tests/scripts/test_champion_flip_ruling.py` reference it) | Vacuous for the champion; meaningful only for free-policy recordings that are not happening |
| `eval/deception_instruments.py` | No non-test consumer (grep-verified in-session: all code hits are the module itself + `tests/eval/test_deception_instruments.py`); by its own doctrine a pure offline Tier-A diagnostic that "never gate[s] a build" | No non-test consumer; Tier-A diagnostic over committed bytes |
| The rendered-prose metric sites (`eval/_suspicion_parse.py`; the suspicion-graph scrape in `eval/meeting_quality.py`; the weak-reason substring membership in `eval/vote_correctness.py`, `genuine_class_subjects` + `_SIGHTING_CHANNEL_EXCLUDED_MARKERS`) | The metrics regex-scrape rendered prompt text (silently skipping non-matches) or classify by English substrings in `ContradictionRef.description` (triage completeness item 18, `audits/audit-phase-19-triage.md:87`) | **Frozen — unreliable under prompt-shape change.** Ratified as labels, not code: nothing records again this phase (`audits/audit-phase-19-planning.md` §4.2); the typed-telemetry migration is backlogged (`§5`) |
| The watchability referee (`eval/watchability.py::compute_watchability`) | The champion-selection referee; it serves the frozen champion **opt-in** path (the acceptance ruling above) | Frozen WITH the opt-in path it serves. Its supply floors (`_BASELINE_SUPPLY_FLOORS` and the pinned measurement comments) are measured baseline pins and stay untouched — re-pricing them is the reopening checklist's route A, an owner decision (§7) |
| The Bash recorders (`scripts/record_ml_corpus.sh`, `scripts/refresh_samples.sh`) | They recorded the frozen corpus/samples; the Phase-19 NOT-list explicitly forbids porting them (`audits/audit-phase-19-triage.md:183`) | Recorders of frozen bytes; port explicitly out of scope |
| The engine RNG-draw apparatus (`engine/tick.py`, the discarded per-tick draw in `advance_tick`) | The draw's value is discarded; the draw exists to advance the RNG cursor so `state_hash` chains stay byte-identical across every committed replay | **Byte-frozen** — removing or consuming the draw would shift every state-hash chain and break replay byte-identity (a note, not a module freeze: the engine is live) |

### RETIRE — implemented by 19.19, each deletion consumer-grep-verified

| Component | Basis | Boundary |
|---|---|---|
| `training/realpath.py` (+ `tests/training/test_realpath.py`) | The one-shot campaign ops surface (4,470 LOC; wall-clock asserts in its test); campaigns concluded | 19.19 records the consumer greps; docstring references in surviving files are rewritten with the deletion |
| The standalone surrogate decision arm | All-SKIP census (§2a) | Only a surrogate-only runner exposure proven consumer-free; factory/class/counter stay (§2a) |
| Unused `first_meeting` episode boundary | "every production caller passes `full_game` explicitly … `first_meeting` is exercised only in tests — a deliberate truncation mode with no live consumer" (`audits/audit-phase-18-close.md:1004`, §7 item 4) | `training/env.py` boundary; 19.19 verifies the caller list |
| New-search machinery (one-shot probe/ops scaffolding) | Per 19.19's verified list: `scripts/record_meeting_gate_probe.py` (zero references), `llm/cache.py` (sole importer is a test), the stale crew-dir CLI advertisement in `scripts/run_tournament.py` | Consumer checks are mandatory; `eval/determinism_test.py` and the five bespoke prompt sets are NOT retired (both source-audit deletion candidacies REFUTED — `audits/audit-phase-19-planning.md` §6) |

## 3. The standard FROZEN header

One format, repeated verbatim (wrapped to the repo's 88-column width where
needed — the key `FROZEN (Phase 19 tier map, training/README.md):` always
stays on one line):

```
FROZEN (Phase 19 tier map, training/README.md): <one-line reason>. Bug fixes and
evidence readers only; no new search.
```

"Evidence readers" means code that reads the committed artifacts/reports
(fidelity harnesses, verifiers, tests over committed bytes). "No new search"
means no new training campaign, candidate search, floor change, or bar
re-pricing rides on a frozen surface — the reopening checklist (§7) is the
only door back in.

Coverage proof (the §5 registry must equal this grep's file list, one header
per file):

```
grep -rl "FROZEN (Phase 19 tier map" --include="*.py" --include="*.sh" .
```

## 4. The Bash recorders and the engine note

The two recorder scripts carry the FROZEN header plus the in-place ledger
labels (§6). `engine/tick.py` carries the byte-frozen RNG-apparatus note at
the discarded draw — the engine itself is live; only the draw apparatus is
byte-frozen.

## 5. The freeze-header coverage registry

The grep in §3 must return exactly these files (one header occurrence each).

**training/ (13):** `training/composed_runner.py`, `training/scenarios.py`,
`training/anchor_study.py`, `training/conviction/fidelity.py`,
`training/surrogate/fidelity.py`, `training/coevo/__init__.py`,
`training/coevo/driver.py`, `training/coevo/factory.py`,
`training/coevo/hall_of_fame.py`, `training/coevo/rollout.py`,
`training/crew/__init__.py`, `training/crew/options.py`,
`training/crew/scorer.py`.

**experiments/ (48 — every `.py` EXCEPT `experiments/lab/rubric_score.py`,
which is LIVE and owned by the 19.9 curation surface: `eval/watchability.py`
cites it by line as the promoted scorer's source):**
`experiments/__init__.py`;
`experiments/lab/`: `decay_emergence_lab.py`, `deception_battery.py`,
`deception_battery_2.py`, `deflection_probe.py`, `featherless_sweep.py`,
`forward_redesign_conversion_probe.py`, `forward_redesign_detector_sweep.py`,
`forward_redesign_probes.py`, `inference_feasibility_probe.py`,
`inference_testimony_probe.py`, `meeting_prompt_battery.py`,
`model_ceiling_probe.py`, `probe_backends.py`, `stopwatch_lab.py`,
`stopwatch_sweep.py`, `tally_lab.py`, `vent_escape_lab.py`,
`visibility_probe.py`, `visibility_resim.py`,
`visibility_resim_asymmetric.py`;
`experiments/lab/ml_spike/`: `check1_determinism.py`,
`check2_learnability.py`, `check2b_holdout.py`, `check3_surrogate.py`,
`core.py`, `fo1_sparse_lever.py`, `fo2_coevolution.py`,
`fo3_rubric_goodhart.py`, `fo4_determinism_scale.py`,
`fo5_faithful_surrogate.py`, `fo6_learned_vote_surrogate.py`,
`fo7_sabotage_lever.py`, `fo8_crew_buddy.py`, `fo9_diversity.py`;
`experiments/lab/torch_probe/`: `distill_probe.py`, `entrant.py`,
`ppo_gru.py`, `train_probe.py`;
`experiments/lab/qwen36_prompt_scratch/run_iteration.py`;
`experiments/model_probe/`: `__init__.py`, `conversation.py`, `corpus.py`,
`grade.py`, `optin.py`, `probe.py`, `reply.py`,
`variants/__init__.py`.

**eval/ (6):** `eval/off_menu.py`, `eval/deception_instruments.py` (module
headers); `eval/_suspicion_parse.py` (the frozen-metric label, above
`parse_rendered_max_suspicion`); `eval/meeting_quality.py` (the scrape-site
label at the suspicion-graph scrape, `_SUSPICION_GRAPH_HEADERS` /
`_SUSPICION_GRAPH_ROW_RE`); `eval/vote_correctness.py` (the scrape-site label
in `genuine_class_subjects`; its companion tuple
`_SIGHTING_CHANNEL_EXCLUDED_MARKERS` points to it); `eval/watchability.py`
(the referee label inside `compute_watchability`'s docstring — floors
untouched).

**scripts/ (2):** `scripts/record_ml_corpus.sh`, `scripts/refresh_samples.sh`.

**engine/ (1):** `engine/tick.py` (the byte-frozen RNG-apparatus note in
`advance_tick` — a note, not a module freeze).

Total: **70 files.** `training/realpath.py` deliberately carries NO label — it
is retired by 19.19 and a file being deleted is not labeled.

## 6. The Phase-18 ledger long tail, labeled in place

`audits/audit-phase-18-close.md` §7 hands Phase 19 a 14-row review-input
table ("review inputs, not contracts" — `:993-997`). Items 1–2 (the eval walk
duplication) are 19.25's; item 3 has no in-repo anchor (close `:1016-1022`);
item 4 (`first_meeting`) and item 9 (the ES hash pin) are 19.19's/19.3's. The
long tail — items 5–8 and 10–14 — is freeze-labeled in place, each label
naming its close-audit anchor:

| §7 item | Name | Close-audit anchor (as recorded at the close) | In-place label |
|---|---|---|---|
| 5 | Recorder lock-race | `scripts/record_ml_corpus.sh:966-999` (+ `audits/audit-2026-05-30-0059-mvp-close.md:96`) | `scripts/record_ml_corpus.sh`, at the mkdir-mutex DEAD-OWNER comment block |
| 6 | Un-unit-tested `deadline_default` freeze-guard branch | `scripts/record_ml_corpus.sh:581-600`; `tests/scripts/test_record_ml_corpus.py` has zero `deadline_default` occurrences | `scripts/record_ml_corpus.sh`, at the `error_type == "deadline_default"` branch (one label covers items 6+7) |
| 7 | Validity-gate `deadline_default` blindness (unassigned) | The anchor IS a grep absence: zero `deadline_default` in `scripts/validity_gate.py` and `eval/validity.py`; routed by PR #299, unclaimed by the close | No code site exists to label (an absence of code); recorded on item 6's label and here |
| 8 | Stamped-substrate question for LLM-free meeting paths | `eval/validity.py:864` `check_cost_and_provenance`; `training/artifacts/composed/verdict.json.adoption_constraints[0]` | `training/composed_runner.py`, in the module docstring beside the FROZEN header (the constraint is the composed runner's own) |
| 10 | `composed_artifact_dir` type-annotation-only escape | `training/coevo/driver.py:80-81`, `:426`, `:437`, consumed `:1531-1533`; the escape: `training/composed_runner.py:342` `Path \| None` with a live `None` branch | `training/coevo/driver.py`, at the `composed_artifact_dir: Path` config field; a pointer line at the `composed_runner` escape parameter |
| 11 | Silently-overwritable `campaign-plan.json` | `training/coevo/driver.py:323` `CAMPAIGN_PLAN_FILENAME`; the close's ":118 (the write)" cell is docstring prose — the actual unconditional `write_text` is in `_write_campaign_plan`-adjacent driver code | `training/coevo/driver.py`, at the `write_text` call |
| 12 | Scenario selector seam's unenforced delegation convention | Doc-anchored only: `tasks/phase-18.md:1823-1825`; `report-crew-campaign.md:86-88`; never exercised (`scenario_labels: []` on both campaigns) | `training/scenarios.py`, at the `ScenarioProvider` delegation-convention docstring (the fullest in-code statement; the audit lists no code anchor) |
| 13 | Resume refuses non-canonical maps (18.31 residual) | `training/realpath.py:4158-4167`; recorded `tasks/phase-18.md:2577-2578` | **No in-place label** — the only code anchor is `training/realpath.py`, which 19.19 retires (a file being deleted is not labeled). The residual retires with it: "custom-map campaigns have no resume path" describes machinery that will no longer exist. Recorded here so the item is not lost |
| 14 | Hand-maintained `WORK_DIR_OWNED_NAMES` (18.31 residual) | `training/coevo/driver.py:350`, consumers `:1202`/`:1223`, export `:2240`; twin: `scripts/generate_campaign_tables.py:105` `DEFAULT_RANKING_ROOTS` (close §6.3 C4) | `training/coevo/driver.py`, at the `WORK_DIR_OWNED_NAMES` declaration (the out-of-scope twin is named there, not labeled) |

## 7. THE REOPENING CHECKLIST (locked decision 3 — record the fork, decide later)

The frozen program has exactly two routes back to a training campaign, and
the owner picks between them **only against a concrete re-open proposal** —
never in the abstract, and not in Phase 19. The program stays frozen either
way (`tasks/phase-19.md` §Locked decisions, decision 3).

**The fork (both routes recorded, neither chosen):**

- **Route A — referee-floor re-pricing.** The witnessed-gauge rare-event
  floor's 25% noise ceiling (0.00847 against measured noise 0.01479–0.08671)
  is unclearable at n = 50 on all nine arms; "any bar re-pricing is an owner
  decision" (`audits/audit-phase-18-close.md:726-729`, §6.1 L2). Re-pricing
  means changing `eval/watchability.py`'s pinned floors — which is why they
  are frozen untouched until this decision.
- **Route B — real-path conviction signal.** Leave the floors alone and give
  training a meeting path where convictions actually occur (the crew
  deployment case "must be made on a meeting path where reports can
  convert" — `report-crew-owned-tasks.md:276-286`), i.e. real-path or a
  stamped-substrate composed path (§6 item 8).

**The four mandatory pre-campaign checks** (from
`audits/audit-phase-19-triage.md:90`, completeness-pass item 21 — quoted by
mechanism, not just name; ALL FOUR are prerequisites of ANY later selection
campaign, on either route):

1. **Interval-aware supply-floor decisions.** The referee supply floors are
   bare point-estimate comparisons despite existing Wilson/split-half
   machinery. A pre-campaign floor decision must carry intervals — a
   point-estimate pass/fail at campaign n is not a decision.
2. **The weak-flag Goodhart probe.** The population-relative conversion floor
   contains an unprobed weak-flag Goodhart channel *because weak flags count
   toward density* — a candidate can move the floor's denominator with weak
   flags it mints itself. Probe this channel before any selection rides the
   floor.
3. **Same-substrate run-variance / noisy-canary treatment.** Same-substrate
   recordings drift crew-ward on five metrics and showed roughly a
   seven-point impostor-win swing — the same scale as several bright-line
   rules. Any bright-line read must be sized against this measured
   run-to-run variance, not treated as signal.
4. **Adequate screening sample sizes and replication.** Screening instability
   changed wins for 10/22 arms between tranches, and the only retested
   screening referee PASS failed to replicate (`f280962f…` flags 1.80 → 0.40;
   "No referee PASS in this campaign has replicated" —
   `report-impostor-campaign.md:442-453`). Screens must be sized and
   replicated before any verdict-grade read; "the first non-replication …
   was read at the time as 'that candidate was noise' rather than 'this
   measurement is noise'" (`:455-465`) is the recorded lesson.

**Decide-at-proposal.** A re-open proposal must name its route (A or B), show
the four checks satisfied in its design, and route the choice to the owner.
Until such a proposal exists there is nothing to decide — that is the point
of recording the fork instead of resolving it.

## 8. APPENDIX — the recorded campaign invocations, repo-relative (Task 19.23)

The 18.25 crew campaign was launched from eight operator-authored harness
scripts, preserved verbatim as provenance under
`training/artifacts/coevo/provenance/harnesses/`. They are the record of what
actually ran, and they are **not runnable as written**: every one of them opens
with the same three lines —

```python
_REPO = "/Users/danielkeinan/projects/AiLibi"
os.chdir(_REPO)
sys.path.insert(0, _REPO)
```

— so the invocation only ever existed as folklore about one machine's home
directory (`provenance/harnesses/harness_run_c1.py.txt:11`). That `_REPO` literal
opens all eight; every one of them then derives a `REPO = Path(…)` from it (the
two `run-c1` files repeat the literal a second time, the other six spell it
`Path(_REPO)`), and the four campaign harnesses add an operator `CAMPAIGN_ROOT`
beside it. This appendix rewrites them **repo-relative**, so the exact
configuration survives the machine it was typed on. What it replaces is the
FOLKLORE, not the files: every provenance file stays where it is and stays the
record, and each is cited by name below beside the invocation that reproduces
it.

**Read this as a record, not an invitation.** The co-evolution machinery is
FROZEN (§2 FREEZE) and the program stays frozen: §7 is the only door back in,
and it needs an owner decision against a concrete proposal. Nothing here is a
campaign anyone should start.

**Three preconditions, stated because two of them changed after these runs.**

1. **Run from the repository root.** The `os.chdir` / `sys.path.insert` pair is
   replaced by the working directory itself. The forms below are written for
   `uv run python -` reading the script on **stdin**, because that puts the
   working directory (not a script's own directory) on `sys.path`.
2. **`training/realpath.py` is RETIRED** (Task 19.19, commit `4e8d533`), so the
   four **real-path leg** scripts below **do not import at HEAD**. Their
   configuration is recorded exactly as it ran; the module they call is in git
   history (`git show 4e8d533^:training/realpath.py`). This is stated rather
   than quietly omitted — the leg invocation is evidence about a concluded
   campaign, not a working entry point.
3. **The leg slates read hall artifacts the prune moved.** Each leg names a
   `gen-3` swap champion under `training/artifacts/coevo/<run>/crew/gen-3/…`,
   which Task 19.22 moved to the pinned evidence commit (the `gen-9` champions
   stayed in-tree — `EVIDENCE-MANIFEST.md` §3). `bash scripts/fetch_evidence.sh`
   restores them. Verify the whole picture — hashes, corpus, recomputation,
   availability — with `uv run python scripts/verify_ml_evidence.py`.

**The substrate fence still holds — on the four harnesses that carry it.** The
**campaign** harnesses (§8.1) each assert
`compute_substrate_sha().startswith("9bc00af0")` — the 18.24 composite the seed
was trained at, so that a moved substrate makes the seed re-run-before-use
rather than a config edit. The **four real-path leg scripts (§8.2) contain no
such assertion**: none of them imports `compute_substrate_sha`, so the legs ran
with no substrate fence of their own and inherited only whatever the campaign
that produced their candidates had checked. That is recorded rather than
smoothed over — it is a property of the evidence, not of this appendix.
Recomputed at this HEAD:

```
uv run python -c "from training.anchor_study import compute_substrate_sha; print(compute_substrate_sha())"
9bc00af0f9e76719cb78d66c5593ec178312716528715f4a580677fb519f04f4
```

### 8.1 The four campaign harnesses (fake-path, `$0`, deterministic)

The repo-relative form of `provenance/harnesses/harness_run_c1.py.txt`,
`harness_run_c1_ablation.py.txt`, `harness_run_c2.py.txt` and
`harness_run_c2_ablation.py.txt`. One body, four parameter sets — the recorded
files differ only in the rows of the table below. (`harness_run_c1_ablation`
carries `run_c1`'s docstring unedited; the run name and `conviction=None` are
what actually distinguish it. Recorded here rather than corrected there —
provenance files are records.)

```python
# uv run python - <<'PY'   (from the repository root)
from pathlib import Path

from training.anchor_study import compute_substrate_sha
from training.bakeoff.harness import load_candidate_weights, load_conviction_fitness_term
from training.bakeoff.utility_es import build_utility_scorer_policy
from training.coevo.driver import CoevoCampaignConfig, CoevoSideConfig, run_alternating_freeze
from training.crew.options import OwnedTaskOptionBasis
from training.crew.scorer import build_crew_scorer

REPO = Path.cwd()                       # was "/Users/danielkeinan/projects/AiLibi"
CAMPAIGN_ROOT = Path("/tmp/ailibi-campaign-1825")   # operator scratch root, outside
                                        # the tree by convention (docs/artifacts.md,
                                        # class REPO-EXTERNAL) — was
                                        # "/Users/danielkeinan/ailibi-campaign-1825"

# --- the row from the table below -----------------------------------------
RUN_NAME = "run-c1-crew-owned-tasks"
MASTER_SEED = 182501
CREW_SEED_ARTIFACT = REPO / "training/artifacts/crew/crew-owned-tasks-es"
CREW_GENOME_LENGTH = 27
CREW_ENCODER = "crew-option-features-v2"
CREW_BASIS = OwnedTaskOptionBasis()     # None on the run-c2 rows
USE_CONVICTION_TERM = True              # False on the two ablation rows
# ---------------------------------------------------------------------------

# The 18.24 hand-off seed (finalist 1a, pooled 6/6), re-frozen as a fresh lineage
# in this campaign's own hall by the driver's swap-boundary freeze. Retained
# in-tree by the 19.22 prune (EVIDENCE-MANIFEST.md §3).
SEED_ARTIFACT = (
    REPO
    / "training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2"
    / "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
)

composite = compute_substrate_sha()
# Stale-substrate honesty: the seed was trained at 18.24's recorded composite
# 9bc00af0… — a moved substrate makes the seed re-run-before-use, not a config edit.
assert composite.startswith("9bc00af0"), f"substrate moved since 18.24: {composite}"

impostor = CoevoSideConfig(
    side="impostor",
    genome_length=19,
    build_policy=build_utility_scorer_policy,
    encoder_version="impostor-option-features-v1",
    initial_genome=load_candidate_weights(SEED_ARTIFACT),
    # The seed's own provenance regime (config.json: anchor_weight 4.0, the λ=4 lineage).
    anchor_weight=4.0,
)
crew = CoevoSideConfig(
    side="crew",
    genome_length=CREW_GENOME_LENGTH,
    build_policy=lambda g: build_crew_scorer(g, basis=CREW_BASIS),
    encoder_version=CREW_ENCODER,
    initial_genome=load_candidate_weights(CREW_SEED_ARTIFACT),
)

config = CoevoCampaignConfig(
    work_dir=CAMPAIGN_ROOT / RUN_NAME / "work",
    substrate_sha256=composite,
    substrate_sha_kind="compute_substrate_sha",
    impostor=impostor,
    crew=crew,
    master_seed=MASTER_SEED,
    num_swaps=4,
    generations_per_swap=3,
    fitness_seeds=(1000, 1001, 1002, 1005, 1006, 1007),
    benchmark_seeds=(2000, 2001, 2002, 2003),
    payoff_seeds=(3000, 3001, 3002, 3003),
    # A FRESH ConvictionFitnessTerm per run (mutable use counter — the 18.24 §9 note).
    conviction=(
        load_conviction_fitness_term(REPO / "training/artifacts/conviction")
        if USE_CONVICTION_TERM
        else None
    ),
    first_side="crew",
    hall_root=REPO / "training/artifacts/coevo" / RUN_NAME,
    run_label=RUN_NAME,
)

result = run_alternating_freeze(config)
print(f"RUN DONE {RUN_NAME}")
print(f"rows: {config.work_dir / 'campaign-rows.jsonl'}")
print(f"digest: {result.digest()}")
print(f"gen_champions_dir: {result.gen_champions_dir}")
# PY
```

| provenance file (`provenance/harnesses/`) | `RUN_NAME` | `MASTER_SEED` | crew seed artifact | genome / encoder | `CREW_BASIS` | conviction term |
|---|---|---:|---|---|---|---|
| `harness_run_c1.py.txt` | `run-c1-crew-owned-tasks` | 182501 | `training/artifacts/crew/crew-owned-tasks-es` | 27 / `crew-option-features-v2` | `OwnedTaskOptionBasis()` | loaded |
| `harness_run_c1_ablation.py.txt` | `ablation-run-c1-conviction-term` | 182501 | `training/artifacts/crew/crew-owned-tasks-es` | 27 / `crew-option-features-v2` | `OwnedTaskOptionBasis()` | **`None`** |
| `harness_run_c2.py.txt` | `run-c2-crew-general` | 182502 | `training/artifacts/crew/crew-utility-es` | 22 / `crew-option-features-v1` | `None` | loaded |
| `harness_run_c2_ablation.py.txt` | `ablation-run-c2-conviction-term` | 182502 | `training/artifacts/crew/crew-utility-es` | 22 / `crew-option-features-v1` | `None` | **`None`** |

Where each run's output landed is the `PATHS.md` consolidation map, not a 1:1
mirror: `work/campaign-rows.jsonl` for the two main runs was concatenated into
`training/reports/results-crew-campaign.jsonl` (run-c1 rows 1–12, run-c2 rows
13–24); the ablation twins' rows and plan went to
`training/artifacts/coevo/ablation-<run-suffix>/`; `work/gen-champions/` to
`training/artifacts/coevo/gen-champions/<run>/`; and `hall_root` was written
in-tree by the driver (`training/artifacts/coevo/PATHS.md` §"The 18.25 crew
campaign").

### 8.2 The four real-path legs (`training/realpath.py` — RETIRED, see precondition 2)

The repo-relative form of `provenance/harnesses/leg_c1_t1.py.txt`,
`leg_c1_t2.py.txt`, `leg_c2_t1.py.txt` and `leg_c2_t2.py.txt`. The slate is
protocol-fixed (gen-0 control + the two crew swap champions), not
conviction-ordered, so no pre-screen quote set rides these legs;
`meeting_timeout_seconds=900.0` (F7 kept).

```python
# uv run python - <<'PY'   (from the repository root; needs the retired module —
# `git show 4e8d533^:training/realpath.py` — and `bash scripts/fetch_evidence.sh`
# for the gen-3 hall artifact the prune moved)
from pathlib import Path

from training.bakeoff.harness import load_candidate_weights
from training.coevo.hall_of_fame import read_loadable_artifact
from training.realpath import RealPathCandidate, RealPathRerankConfig, run_realpath_rerank

REPO = Path.cwd()                       # was "/Users/danielkeinan/projects/AiLibi"

# --- the row from the table below -----------------------------------------
LEG = "leg-c1-t1"
RUN = "run-c1-crew-owned-tasks"
SEEDS = (4000, 4001, 4002)
TRANCHE = "4000-4002"
GEN0_LABEL = "c1-gen0-owned-tasks-es"
GEN0_ARTIFACT = REPO / "training/artifacts/crew/crew-owned-tasks-es"
GEN0_POLICY_ID = "crew-owned-tasks-es"
ENCODER = "crew-option-features-v2"
SWAP0 = ("c1-swap0-champ-gen3", 3, "72adb41c9286d61d5a81ea4ed2bd347c0d7da52ad89ae6497f1dcbf2237ca4e5")
SWAP2 = ("c1-swap2-champ-gen9", 9, "0bf179b719a67c1b40f97377ba49bad6512d08932e0d944e4d024691f60e71df")
# ---------------------------------------------------------------------------

# WHERE THE ARCHIVED BYTES LIVE (read-only). As-recorded, this leg wrote to
# "/Users/danielkeinan/ailibi-campaign-1825/realpath/<run>/"; PATHS.md maps that
# prefix here, which is where the recordings and their manifest were archived
# (on the evidence commit since 19.22, restored by scripts/fetch_evidence.sh).
ARCHIVE = REPO / "training/artifacts/coevo/realpath-crew" / RUN

# WHERE A RERUN WRITES. Deliberately NOT the archive: `run_realpath_rerank`
# creates `recordings-<tranche>/` and `ranking-<tranche>.jsonl` under whatever it
# is handed, so pointing it at ARCHIVE would mix fresh output into immutable
# class-(c) evidence — or overwrite it. The original ran under an operator root
# outside the tree and this keeps that property (docs/artifacts.md: the archive
# is where the bytes ENDED UP, never a workspace).
ROOT = Path("/tmp/ailibi-campaign-1825/realpath") / RUN
HALL = REPO / "training/artifacts/coevo" / RUN / "crew"
OPPONENT = (
    REPO
    / "training/artifacts/coevo/intermediates/run-02-utility-lambda4/gen-2"
    / "ea4bc955dfe0beb8f82663d659e6c990083cebb26a1dab9600c6b68b7783d79f"
)


def hall_candidate(gen: int, sha: str, label: str) -> RealPathCandidate:
    art = read_loadable_artifact(HALL / f"gen-{gen}" / sha)
    return RealPathCandidate(
        label=label,
        genome=art.genome,
        encoder_version=art.encoder_version,
        hidden=None,
        policy_id=art.policy_id,
        method=art.method,
        anchor_policy=art.anchor_policy,
        generation_indices=(gen,),
    )


candidates = [
    RealPathCandidate(
        label=GEN0_LABEL,
        genome=load_candidate_weights(GEN0_ARTIFACT),
        encoder_version=ENCODER,
        hidden=None,
        policy_id=GEN0_POLICY_ID,
        method="crew-utility-scorer-es",
        anchor_policy="fsm-default",
        generation_indices=(),
    ),
    hall_candidate(SWAP0[1], SWAP0[2], SWAP0[0]),
    hall_candidate(SWAP2[1], SWAP2[2], SWAP2[0]),
]

print(f"[{LEG}] candidates: {[(c.label, c.encoder_version) for c in candidates]}", flush=True)
print(f"[{LEG}] opponent: ea4bc955 (the 18.24 frozen champion)  seeds={SEEDS}", flush=True)
print(f"[{LEG}] meeting_timeout_seconds=900.0 (F7 kept)  prescreen=None (protocol-fixed slate)", flush=True)
print(f"[{LEG}] writing to {ROOT}; the ARCHIVED run is at {ARCHIVE} (read-only)", flush=True)

result = run_realpath_rerank(
    candidates,
    seeds=SEEDS,
    work_dir=ROOT / f"recordings-{TRANCHE}",
    ranking_path=ROOT / f"ranking-{TRANCHE}.jsonl",
    config=RealPathRerankConfig(meeting_timeout_seconds=900.0),
    opponent_artifact=OPPONENT,
)

for row in result.rows:
    print(
        f"[{LEG}] rank {row.rank}: {row.label} selection={row.selection_score:.4f} "
        f"validity={row.validity_passed} referee={row.referee_passed} "
        f"win={row.core_impostor_win_rate:.3f} crew_stamped={row.crew_stamp_verified_games}",
        flush=True,
    )
print(f"[{LEG}] LEG DONE ranking={result.ranking_path}", flush=True)
# PY
```

| provenance file (`provenance/harnesses/`) | `LEG` | `RUN` | `SEEDS` / `TRANCHE` | gen-0 control | encoder | `SWAP0` (gen-3) | `SWAP2` (gen-9) |
|---|---|---|---|---|---|---|---|
| `leg_c1_t1.py.txt` | `leg-c1-t1` | `run-c1-crew-owned-tasks` | 4000–4002 | `crew-owned-tasks-es` | `crew-option-features-v2` | `72adb41c…` | `0bf179b7…` |
| `leg_c1_t2.py.txt` | `leg-c1-t2` | `run-c1-crew-owned-tasks` | 4003–4005 | `crew-owned-tasks-es` | `crew-option-features-v2` | `72adb41c…` | `0bf179b7…` |
| `leg_c2_t1.py.txt` | `leg-c2-t1` | `run-c2-crew-general` | 4000–4002 | `crew-utility-es` | `crew-option-features-v1` | `7fa59718…` | `515fc066…` |
| `leg_c2_t2.py.txt` | `leg-c2-t2` | `run-c2-crew-general` | 4003–4005 | `crew-utility-es` | `crew-option-features-v1` | `7fa59718…` | `515fc066…` |

Within a run the two tranche files are byte-identical apart from `LEG`, `SEEDS`
and `TRANCHE` (the c2 pair additionally sets `GEN0_LABEL = "c2-gen0-utility-es"`
and `GEN0_POLICY_ID = "crew-utility-es"`); the slate itself does not move between
tranches. The full sha of each swap champion is in the provenance file and in
`EVIDENCE-MANIFEST.md`.

The `gen-9` artifacts (`0bf179b7…`, `515fc066…`) are two of the eight genome
directories the 19.22 prune retained in-tree; the `gen-3` ones (`72adb41c…`,
`7fa59718…`) moved to the evidence commit with the rest of the unpinned halls.
