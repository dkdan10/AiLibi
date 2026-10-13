# Phase 15 — Evidence substrate, then machine-learned tactical policies (Wave 0: cleanup → baseline 3; Wave 1: ML signal, harness, bake-off → PAUSE → Wave 2: productize)

> **STATUS: CLOSED 2026-07-11 on the branch-A end-state (Task 15.23).** Phase 15 ships the
> `utility-es` champion — weights sha256
> `6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`, 19-weight utility scorer,
> encoder `impostor-option-features-v1` — as a pure-Python OPT-IN factory
> (`agents/tactical/learned/`, `scripts/run_tournament.py --agent-factory learned-champion`) beside
> the untouched FSM default; `replays/samples/` + `replays/ml_corpus/` are byte-untouched (branch A
> records no baseline 4, baseline 3 stays canonical; the baseline-2 bytes survive in git history at
> `adca07f`) and byte-verify bare on the close HEAD. The close recording (seeds 0–49, 9p2i, real
> provider, committed as `training/reports/results-champion-close.jsonl`) **PASSES the HARD validity
> gate** 10/10 with the champion stamp proven from bytes on all 50 games; the hardened 15.19 referee
> reads it **FAIL** on the subject-aware `testimony_backed_conversion` floor (0.5743 vs 0.6636, both
> supply gauges passing wide) — **closed over by owner ruling (2026-07-11, close audit §10)**:
> the floor is the FSM baseline's own measured value, champion gameplay legitimately shifts crew
> conversion, and the starvation failure mode the floors exist for is absent; the floor
> recalibration is a Phase-16/17 contract input, and the default flip stays un-blessed (decision 2).
> Full close: `audits/audit-phase-15-close.md`. Wave 0 closed on baseline 3
> (`audits/audit-phase-15-wave0-close.md`); the pause locked the seven decisions
> (`audits/audit-phase-15-pause.md`); torch experiment-tier (decision 3), co-evolution NO-GO
> (decision 4), and the surrogate re-grounding cadence (decision 7) stand as the permanent record.
> Phase-16 (Voice & Judgment) scoping inputs: pause audit §9 + close audit §11. Roadmap context:
> `tasks/post-phase-14-plan.md`.

Goal: give the agents machine-learned intelligence in the deterministic, LLM-free layer BETWEEN meetings
— kill timing, witness avoidance, cooldown stalking, cover/vent play, buddy/patrol movement — replacing
or augmenting the scripted FSMs in `agents/tactical/`, **on top of a first-fixed evidence substrate**.
The LLM meeting layer's protocol stays frozen; Wave 0 repairs two measured holes in what that layer can
SEE, because a policy optimizer farms whatever holes the fitness landscape contains. Phase 14 closed on
baseline 2 (`Qwen/Qwen3-32B` Featherless $0, `qwen3_32b.v4`, all five substrate levers unconditionally
ON — `audits/audit-phase-14-close.md`; those bytes lived in `replays/samples/{9p2i,4p1i}` until the
15.7 re-record and survive in git history at `adca07f`). A first-principles measurement
of those committed bytes (2026-07-05, reproduced by Task 15.3; full table in
`tasks/post-phase-14-clean-up.md` §2) found the game is information-RICH but aggregation-LOSSY: pooled
crew sightings narrow ~8 suspects to a median of 3 (narrowed to one candidate in 38/129 report
meetings under the ±1-tick window), hard clues exist in 76% of report meetings — yet witnessed impostor vents (the most abundant hard evidence, 74/129
meetings) have NO structured representation and reach the transcript only 36/74 times, votes land
outside the pooled-knowledge candidate set 54% of the time when that set is ≤3, and 22 of 106 ejections
removed the meeting's own (always innocent) reporter. Wave 0 closes those holes and records **baseline
3**. Wave 1 then builds the ML measurement harness, training environment, calibration corpus (recorded
AT baseline-3 config), a rebuilt meeting surrogate, and runs a multi-method training bake-off; the PAUSE
picks the winner on measured numbers; Wave 2 productizes. The substrate for ML is verified ready: a
learned policy is a drop-in `agent_factory` (`orchestrator/game.py:93`, consumed at `:1447-1454`) with
zero engine edits, replay reconstruction re-feeds recorded actions and never re-invokes policies, and
the prior feasibility spike (`experiments/lab/ml_spike/`) proved injection, determinism, and $0 CPU
self-play. What was NOT ready — and what Wave 0/1's early tasks commit — is the measurement layer: the
"validity gate" and "R-gate" the Phase-14 close audit cites by filename exist only as audit prose, the
interestingness referee is lab-tier and baseline-1-anchored, and the spike's cheap-fitness linchpin
(FO-6) REGRESSED top-1 64% → 26% on the baseline-2 corpus.

The training-signal doctrine (from `audits/post-phase-14-ML-training-signal.md`, ratified by the owner
2026-07-05 — every Wave-1 contract below is shaped by it): the one word "R-score" is split into THREE
separate committed artifacts with three different jobs, and they are never conflated. (a) The only thing
any optimizer ever maximizes is the **tactically-reachable fitness** — measurable, side-specific
competence computed from engine events (impostor: resolved kills, un-witnessed-ness via
`Killed.witnesses`, survival, meetings survived, the win as terminal sparse reward; crew: task progress,
survival, correctly-routed reports, buddy/patrol coverage — REWARDED against engine-truth impostor
co-location, a deliberate proxy (owner-ratified 2026-07-09, mid-wave review Q6): a belief-keyed
coverage term would be self-referential (the policy influences its own beliefs — rewarding belief
manipulation, the exact Goodhart class this phase avoids), while the engine-truth term is privileged
but structurally ungameable since the policy cannot see roles, so gradient pressure can only select
observable behaviors that correlate with shadowing impostors) plus potential-based
shaping (policy-invariant, Ng 1999) plus a KL penalty toward the scripted-FSM **anchor** (the
piKL/CICERO pattern: legibility comes from staying near a reference that already produces contested,
watchable play — never from scoring "interestingness"). (b) The **HARD validity gate** and (c) the
**selection referee** (data-grounded evidence-supply floors + the D1–D4 geomean) are applied AFTER
training to accept or reject champions, and are never rewards — "watchability" is not a trained metric
anywhere in this phase. The deepest known risk is a STRONG learner, not a weak one: a perfect-stealth
impostor produces no flags, the meetings starve of testimony, and the deduction game un-makes itself.
The gate/referee/anchor stack exists precisely to make that outcome un-selectable, and Task 15.14
red-teams the referee itself before the pause is allowed to trust it.

Locked decisions (owner, 2026-07-05):
- **Evidence-before-training.** Nothing that records training data or trains a policy runs against the
  pre-Wave-0 meeting layer: Tasks 15.12+ bind to baseline 3. Rationale (measured, not speculative): the
  two Wave-0 holes are exactly the gradients a learned impostor would climb — evidence that evaporates
  (vents) and a free-win vote channel (frame the reporter) — and the ~7h calibration corpus plus the
  ballot surrogate are meeting-layer snapshots that a later fix would invalidate (the FO-6 regression,
  already paid once). One layer per baseline (`tasks/post-phase-14-plan.md` §4).
- **Dependency posture:** `numpy` is allowed as a pinned dependency for the training/surrogate core (the
  new `training/` package). `torch` is allowed ONLY as an experiment-tier probe under `experiments/lab/`
  via `uv run --with torch` — it does NOT enter `pyproject.toml`/`uv.lock` this wave; promotion to a
  real dependency is a PAUSE decision, taken only if the probe shows a large measured gain. Determinism
  may be loosened in small, documented, TRAINING-ONLY paths (e.g. the 15.8.1 hash fast path) when the
  project is better off for it; production inference and everything replay/recording-adjacent stays
  byte-deterministic. Production inference under `agents/` is pure-Python (no numpy/torch import —
  enforced by a firewall test and a new import-linter contract); candidate weights are float-hex JSON in
  Wave 1, with int-quantization decided at the PAUSE.
- **Watchability contract:** the gates ARE the contract. Any impostor win-rate movement from genuinely
  smarter tactical play is acceptable provided the validity gate and the selection referee pass
  (DESIGN.md §"balance is a finding, not a failure"). The referee is selection-only, never a reward.
- **Deployment end-state:** whether the champion ships as an opt-in factory beside the FSM default, or
  becomes the new default with a baseline-4 re-record, is DECIDED AT THE PAUSE. Both end-states are
  carried as Wave-2 options below; neither is presumed by any Wave-1 contract.
- **Sides:** both sides train in Wave 1; the impostor is the primary/deeper track (the bake-off compares
  methods on it), the crew track applies the shared machinery once in parallel. Crew task-ordering is
  EXCLUDED from Wave 1: the crewmate's set of owned unfinished tasks is not observable today (the packet
  carries a single engine-fed `pending_task_id`), so learning task order is structurally impossible
  without an observation-surface change — that change is owner-gated at the PAUSE, not smuggled in.
- **Meeting surrogate doctrine:** the no-LLM meeting model is a per-voter BALLOT predictor whose
  predicted ballots feed the REAL deterministic tally (`meetings/voting.py::tally_ballots`) — never a
  per-meeting ejection classifier (the FO-6 always-SKIP collapse). It is a moving target: it is
  re-calibrated after any mover or meeting-layer change, carries a staleness cap, and is never trained
  against indefinitely while frozen. Final champion numbers are always re-scored on a real meeting path,
  never surrogate-scored.
- **Wave-0 scope discipline:** Wave 0 makes held evidence SPEAKABLE and closes the reporter hole; the
  pooling/elicitation levers (ballot-whereabouts, in-meeting roll-call) are Phase-16 Voice & Judgment
  work and are NOT pulled forward (`tasks/post-phase-14-clean-up.md` §4).
- **Co-evolution is DEFERRED to Wave 2**, and only if the PAUSE approves it: the naive two-population
  setup provably collapses here (FO-2, re-run on current HEAD), so any co-evolution runs behind the
  Hall-of-Fame/PFSP/reduced-virulence stabilizer stack or not at all.

Parallelism: three independent roots dispatch immediately: `15.1 ∥ 15.4 ∥ 15.9` (Wave 0's
measurement + evidence tracks run in parallel with Wave 1's layer-independent stamp plumbing; 15.8
follows 15.6 only because both edit the same `.importlinter` root_packages block — config
serialization, nothing semantic). Then
`15.1 → (15.2 ∥ 15.3)`; `15.4 → 15.6 → 15.5` (the meeting-layer chain — shared `meetings/manager.py`,
render-contract, and v5 prompt-set regions, serialized by design: vent observability first, then the
re-homing hygiene 15.5's render plumbing builds on, then the reporter lever); `15.4 → 15.4.1` (the
spectator mirror, ∥ the 15.6 → 15.5 chain — disjoint files);
`(15.1, 15.2, 15.3, 15.4, 15.4.1, 15.5, 15.6) → 15.7`
[operator: baseline-3 record]; `15.6 → 15.8` (the shared `.importlinter` root_packages block,
serialized); `(15.8, 15.9) → 15.8.1` (the shared `HeadlessGame` constructor — 15.9's stamp kwarg
lands first); `15.8 → 15.10`; `(15.7, 15.8) → 15.11`;
`(15.1, 15.7, 15.9) → 15.12` [operator: corpus record — may share the 15.7 operator session];
`(15.11, 15.12) → 15.13`; `(15.2, 15.7, 15.10) → 15.14`; `(15.8.1, 15.10, 15.13, 15.14) → 15.15`;
`(15.10, 15.13, 15.14, 15.15) → 15.16` (files disjoint from 15.15, but the shared bake-off harness
lands in 15.15 and is consumed read-only — the edge guarantees it exists);
`(15.8, 15.10, 15.15) → 15.17` (the probe consumes 15.15's committed eval protocol);
`(15.12, 15.13, 15.15, 15.16, 15.17) → 15.18`. The critical path is
`15.4 → 15.6 → 15.5 → 15.7 → 15.12 → 15.13 → 15.15 → 15.18`. Shared-file overlaps are all covered by
dependency edges or disjoint-region annotations (`scripts/measure_baseline.py` core/watchability/funnel
regions; `meetings/manager.py` validation/vote-surface/guard-band regions; `meetings/schemas.py`
vent-types vs docstring-pointer regions; `orchestrator/replay.py` registration/graduation/stamp
regions; `orchestrator/game.py` — 15.4's registry line + protocol/accessor region and 15.5's vote_ballot
entry (serialized by the 15.4 → 15.6 → 15.5 chain), plus the `HeadlessGame` constructor shared by
15.9's stamp kwarg and 15.8.1's no-replay mode, serialized by 15.8.1's edge on 15.9; `api/replay_loader.py`
observation-view (15.4.1) vs policy-guard (15.9) regions; `eval/balance_eval.py` stamp-kwarg (15.9) vs
meeting-runner-kwarg (15.13) regions; `training/env.py` between 15.8/15.8.1, plus 15.16's
emergency-canonicalization region (serialized behind 15.16's edge on 15.15; 15.14/15.15 consume env.py
read-only);
`training/surrogate/fidelity.py` between 15.11/15.13; `training/bakeoff/es.py` between 15.14/15.15;
`pyproject.toml` dependencies vs mypy-exclude regions; `.importlinter`'s shared root_packages
block, serialized by 15.8's edge on 15.6).
Operator-run / spend gates: **15.7** (baseline-3 record, $0, ~4h), **15.12** (corpus record, $0, ~7h),
**15.15/15.16** (local CPU training, $0, hours-scale), **15.17** (opt-in torch), **15.18** (owner
decisions + a real-LLM finalist evaluation). Everything else is agent-dispatchable and CI-green on the
fake provider.
Track with `python3 scripts/compute_next_task.py --phase 15`.

Merge criteria (Wave 0 → the ML tail): (1) `scripts/validity_gate.py` + `scripts/measure_baseline.py`
exist as committed code and reproduce the Phase-14 close numbers from the committed baseline-2 bytes
($0, offline); (2) the selection referee and the information-funnel diagnostics are committed in `eval/`
and reproduce the clean-up charter's figures; (3) vent evidence is structurally speakable end-to-end
(schema → turn → memory-GROUNDED hard flag → citable turn-id; an ungrounded spoken vent claim never
mints a flag) and the reporter-exculpation lever is proven byte-identical OFF with its offline
counterfactual reported; (4) the hygiene hazards (guard-band disagreement,
boundary sums, dead `StrategicReasoner`, the manager-homed constant + render-contract surface that
blocked the `agents ↛ meetings.manager` contract, missing import contracts, stale AGENTS.md) are
closed with pinning tests; (5) **baseline 3 is recorded, validity-gated, byte-verified,
and committed as the canonical sets**, with the funnel table re-measured before/after as the wave's
close finding (directions are findings, not pass bars — the Phase-14 doctrine).

Merge criteria (Wave 1 → PAUSE): (1) the training env runs the REAL `HeadlessGame` loop through the
`agent_factory` seam with a proven-legal action mask and byte-deterministic frozen-policy episodes;
(2) the ballot surrogate has a measured fidelity verdict against its honest ceiling with an explicit
pre-stated GO/NO-GO and a selected fallback; (3) the ML-calibration corpus is recorded at baseline-3
config, validity-gated, byte-verified, policy-stamped, and frozen with committed splits; (4) the referee
has survived the adversarial Goodhart probe (or its found exploits are documented with recommended
floors, routed to the pause); (5) the impostor bake-off report ranks all entrants on the single shared
protocol (gate / referee / fitness / anchor-KL / determinism hash), and the crew-track and torch-probe
reports exist in the same metric shape; (6) Task 15.18's pause audit is committed, the seven owner
decisions are recorded, the Wave-2 contracts are authored into this file, prompts are regenerated, and
`bash scripts/check.sh` is green.

Merge criteria (end-of-phase — locked at the PAUSE, 2026-07-10, per decision 2: deployment branch A,
the opt-in factory): (1) the champion (`utility-es`, weights sha256 `6d327dcb…`, the pause audit's
decision 1) ships as a pure-Python opt-in factory in `agents/tactical/learned/` beside the untouched
FSM default, with the numpy-trained and pure-Python-shipped forward passes proven BIT-EXACT over the
committed float-hex weights (the Q4 gate, 15.20); (2) `replays/samples/` and `replays/ml_corpus/` are
byte-untouched — branch A records no baseline 4 — and every committed replay byte-verifies bare at
close; (3) the hardened referee (15.19: the conversion-coupled D2 floor + subject-aware observation
backing, floors re-pinned on the same bytes) lands BEFORE the close's champion re-score, and the close
recording passes the validity gate + the hardened referee (the one pass-bar), with the R-gate, funnel
deltas, and canaries — judged on corpus denominators with the 50-seed figures alongside (Q3) —
reported as findings; (4) every recording is policy-stamped, the stamp's `weights_sha256` equality
with the committed artifact is machine-checked from recorded bytes, and operator records follow the
Q5 annotated-tag / back-filled-sha convention; (5) torch stays out of `pyproject.toml`/`uv.lock` and
production `agents/` stays numpy/torch-free (the firewall test); (6) `audits/audit-phase-15-close.md`
records all of the above and flips the STATUS banner to CLOSED (15.23).

## Wave 0 — evidence substrate & cleanup (charter: tasks/post-phase-14-clean-up.md)

### Task 15.1 — Validity gate + baseline measurement CLIs (make the audit-cited scripts real)
**Branch:** `phase-15-validity-gate`
**Depends on:** none
**Section refs:** tasks/post-phase-14-clean-up.md H1; audits/audit-phase-14-close.md §1, §3, §8 (the gate criteria + R-gate rows this task productizes); audits/post-phase-14-pause.md §2.1 (the missing-harness finding); audits/post-phase-14-ML-training-signal.md §3 (the three-artifact split); eval/vote_correctness.py; eval/meeting_quality.py; eval/balance_eval.py; scripts/_verify_samples.py
**Complexity:** Medium

Turn the measurement harness from audit prose into committed code. The Phase-14 close audit grounds
every number in `scripts/validity_gate.py` (the HARD validity gate) and `scripts/measure_baseline.py`
(the R-gate measurement) — neither exists in the tree, and `eval/` has no CLI entrypoint at all (no
`__main__`/`argparse` anywhere in the package). This task creates `eval/validity.py` (the library fold)
and the two CLIs under those exact audit-cited filenames, by WIRING the existing committed folds —
ejection accuracy and genuine-class conversion (`eval/vote_correctness.py:302`, `:558`), meeting rate
(`eval/meeting_quality.py::compute_meeting_rate`, `:426`), win counts and reason histogram
(`eval/balance_eval.py:893-894` + `load_tournament_report`), accusation calibration
(`eval/accusation_calibration.py`), win-condition self-check (`eval/win_condition_selfcheck.py`), and
the byte-identity walk (`scripts/_verify_samples.py`) — never re-implementing a metric that already has
a tested home. Both CLIs take ANY replay-set directory (not just `replays/samples/*`), so the Wave-0
close (15.7), the 15.12 corpus, and every Wave-2 candidate recording are first-class inputs; `--json`
emits the machine-readable report the later harnesses and audits consume; a gate failure exits non-zero
and names the failing check. This task executes against the baseline-2 bytes committed at task time;
15.7 re-runs the same CLIs unchanged on baseline 3.

**Files in scope:**
- eval/validity.py (new: the composed validity checks + report types)
- scripts/validity_gate.py (new CLI: hard pass/fail over a replay-set dir)
- scripts/measure_baseline.py (new CLI: core R-gate folds region — the 15.2 watchability and 15.3 funnel folds are later, disjoint regions)
- tests/eval/test_validity.py (new: per-check unit tests + synthetic violation fixtures)
- tests/scripts/test_validity_gate_cli.py (new)
- tests/scripts/test_measure_baseline_cli.py (new)

**Files NOT in scope:**
- eval/vote_correctness.py + eval/meeting_quality.py + eval/accusation_calibration.py + eval/balance_eval.py + eval/win_condition_selfcheck.py (consumed as-is, never edited)
- experiments/lab/rubric_score.py (the referee promotion is 15.2)
- audits/workflows/extract_gameplay_facts.py (audit-tier; mine its reconstruction recipes, do NOT import it)
- replays/samples/ (read-only input)

**Definition of done:**
- [ ] The gate checks, each named and individually reported: every game reaches `game_over`; meeting rate ≥ 0.60 with all triggered meetings resolved; zero tick-1 kills; zero friendly-fire kills; zero railroaded crew ejections (the restored 14.12 tripwire semantics); zero dangling `primary_reason_id`; cost and provenance rows exact (model, prompt set, substrate flags); the recorded state-hash chain reconstructs byte-identically.
- [ ] `uv run python scripts/validity_gate.py replays/samples/9p2i` and `.../4p1i` both PASS from committed bytes alone, reproducing the Phase-14 close verdict (9p2i meeting rate 1.00 / 142 resolved; 4p1i 0.78 / 39; zero violations on every other check).
- [ ] `uv run python scripts/measure_baseline.py` reproduces baseline 2 exactly from committed bytes: 9p2i R1 eject-decided win share 24/50, ejection accuracy 0.525 (62 impostor / 56 crew of 118 ejections), genuine-class conversion 0.625, impostor win 0.40, reason histogram `{CREWMATE_EJECT: 24, IMPOSTOR_PARITY: 20, CREWMATE_TASKS: 6}`; 4p1i ejection accuracy 0.923 (12/1 of 13). Any mismatch is a task failure, not a number to retrofit.
- [ ] Each gate check has a synthetic violation fixture proving it can FAIL (flips the CLI exit code) — a gate that cannot fail is not a gate.
- [ ] Both CLIs accept an arbitrary replay-set directory and emit `--json` machine-readable reports; the JSON schema is documented in the module docstring (the 15.15 harness and the 15.7/15.18 audits consume it).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- eval.validity.ValidityGateReport
- eval.validity.ValidityCheck
- eval.validity.run_validity_gate

**Implementation hint:**

This is composition, not metric-writing — roughly 80% wiring of folds that already exist, tested, under
`mypy --strict`. Roles ground truth lives ONLY in each set's `tournament-eval-report.json` (raw replays
are role-free by firewall design; `scripts/build_sample_report.py` shows the re-seed recipe if a set
lacks the report). The R1 eject-decided share is the count of `CREWMATE_EJECT`-reason wins — the same
fold `audits/workflows/extract_gameplay_facts.py:611` emits as `r1_eject_decided_wins`; reproduce the
number from the tournament report's reason histogram rather than importing the 4392-line audit script.
For the byte-identity check, call into the machinery behind `scripts/_verify_samples.py` rather than
shelling out. Note `scripts/` is on `mypy_path` — both CLIs are strict-checked. Keep every check pure
and offline: the whole gate must run on a fresh clone with no network and no `AILIBI_*` env.

**Ready-to-paste prompt:** `agent_prompts/task-15-1-validity-gate.md`

### Task 15.2 — Selection referee: evidence-supply floors + the D1–D4 geomean, committed to eval/
**Branch:** `phase-15-watchability-referee`
**Depends on:** 15.1
**Section refs:** tasks/post-phase-14-clean-up.md H2; experiments/lab/rubric_score.py (the D1–D4 geomean, weights :53, composition :823); experiments/lab/report-rubric-design.md; audits/post-phase-14-ML-training-signal.md §3.2, §4, §6 (referee-as-gate doctrine); eval/meeting_quality.py (supply/conversion gauges)
**Complexity:** Medium

Build the committed champion-selection referee — the artifact that decides whether a trained candidate's
games are still a deduction game. Two layers, both selection-only (the module docstring states the
doctrine: this is a gate, NEVER a training reward). Layer 1, **evidence-supply floors** — the sharp,
data-grounded catch for the perfect-stealth failure mode: witnessed-event rate (baseline 2: 6/160 kills
= 3.75% crew-witnessed in 9p2i), contradiction-flag production per meeting, and testimony-backed
conversion, wired from the existing supply/conversion gauges in `eval/meeting_quality.py`. The floors
are PARAMETERIZED PER BASELINE (a named per-baseline constants block, read by baseline id): this task
measures and pins the baseline-2 values; Task 15.7 pins the baseline-3 values when it lands — evidence
starvation (a candidate whose games produce no flags and no witnesses) fails the referee even when
meeting-rate stays high, because bodies still trigger meetings after testimony has died. Layer 2, the
**D1–D4 floor-gated weighted geomean** promoted from lab-tier `experiments/lab/rubric_score.py` (which
self-labels "NOT a shipped eval gate" and is calibrated to baseline 1) into `eval/watchability.py`:
weights {D1 .40, D2 .25, D3 .15, D4 .20}, ε=1e-3, `score = 100 · floor · geomean`, floor∈{0,1} on a
firewall/determinism breach, friendly-fire, or railroad ejection — multiplicative, so a meeting-starved
game collapses to ~0 by construction. Folded into `scripts/measure_baseline.py --watchability`.

**Files in scope:**
- eval/watchability.py (new: supply floors + geomean referee, per-baseline floor constants)
- scripts/measure_baseline.py (watchability fold region — 15.1 owns the core-folds region)
- tests/eval/test_watchability.py (new: parity, floor-trip, and supply-floor tests)

**Files NOT in scope:**
- experiments/lab/rubric_score.py + experiments/lab/rubric.md + replays/samples/9p2i/results-rubric-score.json (lab artifacts frozen; the API still serves the committed rubric file unchanged)
- api/ (no DTO/route change)
- eval/meeting_quality.py (gauges consumed, never edited)

**Definition of done:**
- [ ] Geomean parity: on the committed 9p2i facts, `eval/watchability.py` reproduces the lab scorer's per-game D1–D4 and composed scores (a parity test pins them), with every threshold/anchoring decision documented in the module docstring.
- [ ] The floor trips on synthetic fixtures: a railroaded ejection, a friendly-fire kill, and a determinism breach each force score 0.
- [ ] Evidence-supply floors: witnessed-event rate, flags-per-meeting, and testimony-backed conversion are measured on baseline 2, pinned in the per-baseline constants block with the measured values in comments, and a synthetic evidence-starved set (high meeting rate, zero flags, zero witnesses) FAILS the referee.
- [ ] The referee runs on BOTH sets from bytes — including 4p1i, which has no committed rubric artifact (the 9p2i/4p1i asymmetry is handled, not assumed away).
- [ ] `scripts/measure_baseline.py --watchability` emits per-game + aggregate referee results in the `--json` report consumed by 15.15 and the 15.7/15.18 audits.
- [ ] The module docstring states the selection-only doctrine and cites the Goodhart probe (15.14) as the referee's own acceptance test.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- eval.watchability.WatchabilityReport
- eval.watchability.compute_watchability

**Implementation hint:**

Promote, don't redesign: the geomean's structure already closed the known additive-rubric Goodhart traps
(masking, passive-survival gradients, railroad reward) — the deltas are committed+strict-typed,
per-baseline anchors, and byte/tournament-report inputs instead of the audit-tier facts JSON (document
exactly which facts-extraction subset is inlined). The supply gauges already exist in
`eval/meeting_quality.py` — wire, don't re-derive. Set the floors from measured values, not invented
targets: the referee's job is "do not accept a champion whose games produce structurally less evidence
than the baseline," not "hit a number." The lab file's `GEOMEAN_RESULTS_FILENAME` machinery stays
untouched — the committed 9p2i artifact is the parity fixture, not a dependency.

**Ready-to-paste prompt:** `agent_prompts/task-15-2-watchability-referee.md`

### Task 15.3 — Information-funnel diagnostics: commit the oracle / possession / transmission folds
**Branch:** `phase-15-funnel-diagnostics`
**Depends on:** 15.1
**Section refs:** tasks/post-phase-14-clean-up.md §2 (the charter measurement this task reproduces), H3; api/replay_loader.py:804-1035 (the `_walk` reconstruction recipe); orchestrator/seeder.py; engine/visibility.py:98-127 (crew same-room-only vision); meetings/manager.py:1821-1870 (the opt-in eligibility gate)
**Complexity:** Medium

Promote the clean-up charter's three-stage information measurement into committed, reusable `eval/`
folds, so Wave 0's effect is measured by the same instrument before and after, forever. Stage 1
(EXISTENCE): the pooled-testimony oracle — re-seed each game, replay recorded actions through
`advance_tick` + `apply_meeting_result` with per-tick state-hash verification, and compute, at each
body-report meeting, the killer-candidate set under perfect sharing of every living crew member's
legitimate same-room sightings (alibi-elimination at the kill tick, plus the ±1-tick window variant).
Stage 2 (POSSESSION): the held-clue census per meeting — kill witnessed, killer placed at scene, victim
last-seen-with-killer, impostor vent witnessed. Stage 3 (TRANSMISSION): what reached the meeting —
structured killer-placement observations, vent mentions, killer accused, speakers-vs-holders, votes
inside/outside the oracle candidate set, and the reporter-ejection census. Output: per-set + per-meeting
`--json` rows through a `scripts/measure_baseline.py --funnel` section. The charter's baseline-2 table
is this task's reproduction gate.

**Files in scope:**
- eval/funnel.py (new: the walk + the three-stage folds + report types)
- scripts/measure_baseline.py (funnel fold region — 15.1 owns core, 15.2 owns watchability)
- tests/eval/test_funnel.py (new: scripted-fixture unit tests + the reproduction pins)

**Files NOT in scope:**
- api/replay_loader.py (the walk recipe is mirrored, not imported — the loader is API-tier and carries serving concerns; mirror the seed/advance/apply/hash-verify loop directly against orchestrator/engine)
- engine/ + orchestrator/ (consumed read-only)
- replays/samples/ (read-only input)

**Definition of done:**
- [ ] On the committed baseline-2 9p2i bytes, the folds reproduce the charter §2 figures EXACTLY: oracle candidate-set median 3 (mean 2.86), ±1-tick-window mean 2.29 / single-candidate 38/129 (killer-unique 36/129) / ≤2 84/129, killer-in-set 122/129; hard clue held in 98/129 (vent 74, last-seen-with 37, scene 32, witnessed 6); vent mentioned 36/74; votes outside a ≤3 candidate set 37/68; reporter ejected 22/106 with 22 innocent. Any mismatch is a task failure. (Figures per the charter §2 as corrected 2026-07-07 — the one-off script's ±1/hard/votes cells were proven mutually inconsistent with its own exact-tick row; see the charter's §2 preamble.)
- [ ] Every recorded state hash is verified during the walk (a corrupted or drifted set fails loud, never silently mis-measures).
- [ ] The oracle's assumptions (upper bound: honest pooling, kill-time knowledge, crew-only witnesses) and the known same-tick move+kill frame artifact are documented in the module docstring — this is a diagnostic ceiling, not a claim about achievable play.
- [ ] The folds run on any replay-set directory and on both roster presets (4p1i included), keyed by the set's roster/report artifacts.
- [ ] `scripts/measure_baseline.py --funnel` emits the per-meeting rows + aggregates in the `--json` report; 15.7 consumes it for the before/after close finding.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- eval.funnel.InformationFunnelReport
- eval.funnel.compute_information_funnel

**Implementation hint:**

The reconstruction loop is: `seed_initial_state(seed=…, game_map=…, num_players=…, num_impostors=…,
tasks_per_crewmate=…)` (roster from the set's `roster.json`, defaults for the flat 4p1i set) →
`_deserialize`-equivalent of recorded actions → `advance_tick` → verify `state_hash` → on MEETING phase,
build the result from the meeting entry and `apply_meeting_result` (verify `state_hash_after`) — the
same loop `api/replay_loader.py::_walk` runs; mirror it against `orchestrator.replay` +
`orchestrator.seeder` + `engine.tick` directly. `MeetingTriggeredEvent.body_id` + `BodyState.player_id`
map the reported body to its `KilledEvent`. Crew vision is same-room-only
(`engine/visibility.py:98-127`); vents carry `source_witnesses`/`destination_witnesses` on the engine
event. Keep the folds pure and $0.

**Ready-to-paste prompt:** `agent_prompts/task-15-3-funnel-diagnostics.md`

### Task 15.4 — Vent observability: make the game's hardest evidence speakable end-to-end
**Branch:** `phase-15-vent-observability`
**Depends on:** none
**Section refs:** tasks/post-phase-14-clean-up.md H4; meetings/schemas.py:57-90 (the three-type observation union this task extends); meetings/transcript.py (contradiction detection + chain relevance); agents/memory/store.py:1239 (vent_witnessed is already remembered and rendered); audits/post-phase-14-Voice-and-Judgment-planning.md §3.4 (the C3/C8 private-evidence citation catches)
**Complexity:** Integration

Close the biggest measured transmission hole: witnessed impostor vents — role-PROVING evidence present
in 74/129 baseline-2 report meetings — have no structured representation in the meeting layer, so they
reach the transcript only 36/74 times as unciteable free text, invisible to the contradiction detector
and the ballot reason-id linkage. The substrate below the meeting layer already carries everything
needed (the engine witnesses vent events; the packet surfaces them witness-gated; `agents/memory/store`
records and renders them at high salience) — this task adds the missing top half: (a) a
`SawVentObservation` type in the turn observation union (subject, room, tick — deliberately NO
enter/exit phase field: the perception layer collapses both vent events into a single witnessed "vent"
action (`observation/service.py::_vent_observation_for_agent`) and memory persists only
player/room/action, so a phase field would be unobservable fabrication, and widening
`observation/`/`agents/memory/` stays out of scope), additive and backward-compatible so committed v4
transcripts still parse; (b) turn validation +
normalization in `meetings/manager.py` mirroring the existing observation paths; (c) a HARD
contradiction rule with a GROUNDING chokepoint: a structured vent observation naming a subject is
role-proving (only impostors can vent) — but speech alone must never mint hard evidence (a model that
hallucinates a vent sighting against an innocent would otherwise fabricate a STRONG flag, re-opening
the railroad class Phase 14 eliminated). The grounding input is TYPED, because the meeting boundary
today hands the manager only rendered-memory prose + a suspicion graph — nothing a validator could
check a vent claim against without parsing prompt text: the `MeetingAwareAgent` protocol gains ONE
self-channel accessor, `vent_witness_records_for_meeting() -> tuple[VentWitnessRecord, ...]` (the
agent's OWN witnessed-vent episodic records — subject, room, tick — typed in `meetings/schemas.py`
and implemented by `TacticalAgent` straight off episodic memory; firewall-clean, since an agent
reporting its own witnessed events leaks nothing). The STRONG flag fires only when the speaker's
spoken observation matches one of the speaker's own typed records (subject + room, tick within a
small tolerance) — the chokepoint NEVER parses rendered prose; a grounded observation feeds the same
strong-flag path a witnessed kill uses and is citable, since `primary_reason_id` already validates
against transcript turn ids and the observation now lives in a turn. An UNGROUNDED vent claim is
accepted as ordinary testimony (speech the voters may weigh) but raises NO flag; (d) the `qwen3_32b` set's turn/opening
templates edited IN PLACE to explicitly elicit the vent observations the rendered memory already
contains, with the version recorded by the single `PROMPT_VERSION_SETS` registry bump (`
_bespoke_versions("qwen3_32b", version="v4")` → `"v5"`) owned HERE (the Phase-14 C7 lesson: one shared
edit, owned by exactly one task; 15.5 layers onto v5 behind its dependency edge).

**Files in scope:**
- meetings/schemas.py (SawVentObservation + VentWitnessRecord + union registration; additive)
- meetings/transcript.py (vent hard-flag contradiction rule + chain/opt-in relevance treating a vent observation as relevant)
- meetings/manager.py (turn validation + observation normalization + grounding chokepoint seams region)
- agents/strategic/prompts/qwen3_32b/ (v5 set: turn/opening templates elicit structured vent observations)
- orchestrator/game.py (PROMPT_VERSION_SETS registry line — the v4 → v5 SET bump)
- orchestrator/game.py (MeetingAwareAgent protocol + TacticalAgent vent-witness accessor region — the typed grounding input; disjoint from the registry line above and from 15.8.1/15.9's regions)
- tests/meetings/test_schemas_vent.py (new)
- tests/meetings/test_transcript_vent_flag.py (new)
- tests/meetings/test_manager.py (validation-path extensions)
- tests/orchestrator/test_replay_meetings.py (meeting-double protocol completion — the delegating double gains the vent-witness accessor)
- tests/orchestrator/test_meeting_integration.py (meeting-double protocol completion — every double that crosses the `_build_participants` gate gains the accessor)

**Files NOT in scope:**
- observation/ + engine/ (the packet already carries witnessed vents; no firewall-surface change)
- agents/memory/ (already records + renders vent witnesses; consumed as-is)
- meetings/voting.py (the tally is untouched)
- replays/samples/ (the re-record is 15.7)
- eval/ (measurement is 15.3's instrument)

**Definition of done:**
- [ ] `SawVentObservation` round-trips through the turn schema; every committed v4 replay still parses (backward-compat pinned by a test loading a committed meeting entry).
- [ ] A fixture meeting where a voter's witnessed-vent episodic record exists produces an accepted structured vent observation through the validation path, the grounding chokepoint confirms it against the speaker's TYPED `vent_witness_records_for_meeting()` (never rendered prose), and the transcript layer raises the role-proving STRONG flag against the subject.
- [ ] Grounding is load-bearing: a fixture where a speaker FABRICATES a structured vent observation (no matching record in their own typed vent-witness channel) is accepted as testimony but raises NO flag and leaves the subject's hard-evidence state unchanged — speech alone cannot mint hard evidence.
- [ ] The `MeetingAwareAgent` protocol extension is implemented by `TacticalAgent` from episodic memory, is covered by the isinstance meeting-participant check, and is exercised by the leak suite (an agent reports only its OWN witnessed events). Because the protocol is `@runtime_checkable` and `_build_participants` gates on attribute presence, every meeting-enabled test double that crosses that gate gains the accessor (one-line delegation in `tests/orchestrator/test_replay_meetings.py` / `tests/orchestrator/test_meeting_integration.py`; `tests/orchestrator/test_game.py`'s doubles ride custom runners that never call `_build_participants` and need no change) — a green `uv run pytest` on the final tree proves the sweep found them all.
- [ ] The grounded flag feeds the belief fold exactly like the witnessed-kill strong flag (same cap semantics — no new stacking channel), and a ballot's `primary_reason_id` citing the vent turn validates.
- [ ] The v5 templates elicit vent observations (prompt-fixture test: memory-with-vent renders → template output contains the elicitation instruction); this task owns the v4 → v5 SET bump in `PROMPT_VERSION_SETS` — the only later registry edit is 15.5's single vote_ballot v6 entry.
- [ ] The opt-in eligibility path treats a spoken vent observation as a relevance source (a non-speaker who was placed at the vent scene becomes eligible), consistent with the existing co-presence gate.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- meetings.schemas.SawVentObservation
- meetings.schemas.VentWitnessRecord

**Implementation hint:**

Model the schema/validation/flag path on the witnessed-kill lever (Task 13.5.3) — it walked the same
route from engine event to STRONG flag, and its grounding posture is the template: the hard evidence
derives from what a witness's own deterministic memory holds, with the spoken observation as the public,
citable surface. The memory side is already done: `_SALIENCE_VENT_WITNESSED` renders witnessed vents
above routine sightings, so elicitation is a prompt-template ask, not a memory change. Template work:
the prompt-set layout is FLAT — the four `.j2` templates live directly in
`agents/strategic/prompts/qwen3_32b/` and the version is a REGISTRY property, not a directory; edit the
turn/opening templates in place and bump `_bespoke_versions("qwen3_32b", version=…)` to `"v5"` in
`PROMPT_VERSION_SETS` (exactly how 14.11 shipped v4). Keep `vote_ballot.j2` byte-identical here (15.5
owns its edit, under its own per-template v6 bump). The live behavioral effect (transmission 36/74 → ?) is measured at 15.7 by the 15.3
instrument — this task's DoD is the mechanism, fixture-proven, not the model's uptake.

**Integration risk:**

Three coupling points. (a) Prompt-version provenance: the v4 → v5 SET bump is a single registry edit
owned here (the 14.11 lesson: never double-write the same entry); 15.5's later vote_ballot v6 entry is
a DIFFERENT, deliberate per-template bump behind its dependency edge — the two edits never touch the
same registry value twice. (b) Schema compat: the observation union is
additive; a strict validator change that rejects unknown types would break committed-replay loading —
the backward-compat pin is the guard. (c) Flag semantics: the vent flag must ride the EXISTING strong-
contradiction cap (`MEETING_CONTRADICTION_LIFT_CAP` + the joint cap), not add a new uncapped lift
channel — otherwise Wave 0 reintroduces the railroad class Phase 14 just eliminated. (d) The grounding
chokepoint is the whole defense against evidence-minting: if it is skipped or made advisory, a single
hallucinated observation converts speech into role-proving hard evidence against an innocent — treat
the fabricated-observation fixture as the task's most important test, and make the grounding
comparison deterministic (reconstructed memory, not LLM judgment).

**Ready-to-paste prompt:** `agent_prompts/task-15-4-vent-observability.md`

### Task 15.4.1 — Spectator mirror for vent observations (API DTO + generated types + renderer)
**Branch:** `phase-15-vent-spectator-mirror`
**Depends on:** 15.4
**Section refs:** tasks/post-phase-14-clean-up.md H4; api/replay_loader.py:1890-1915 (`_observation_claim_view` raises TypeError on an unsupported claim); api/schemas.py (ObservationClaimView); scripts/gen_frontend_types.py (DTO → frontend type generation)
**Complexity:** Medium

Mirror 15.4's schema extension through the privileged spectator path — without this, the first
baseline-3 replay containing a structured vent turn CRASHES the replay API: `_observation_claim_view`
is deliberately exhaustive and raises `TypeError` on any observation type it does not know
(`api/replay_loader.py:1915` — the no-silent-fallbacks doctrine working as designed, which is exactly
why the mirror must land before the re-record). Add the vent variant to `api/schemas.py`'s
`ObservationClaimView` union, extend the loader's observation-claim view mapping, regenerate
`frontend/src/types/api.ts` via `scripts/gen_frontend_types.py`, and extend the meeting-transcript
observation renderer (the exhaustive ObservationLine switch) so a vent sighting displays in the
spectator UI. Committed v4 replays contain no vent observations and must serve byte-identically.

**Files in scope:**
- api/schemas.py (ObservationClaimView vent variant — additive)
- api/replay_loader.py (observation-claim view mapping region — disjoint from 15.9's policy-stamp guard region)
- frontend/src/types/api.ts (regenerated via scripts/gen_frontend_types.py — mechanical output)
- frontend/src/ (the meeting-transcript observation renderer — the exhaustive ObservationLine switch gains the vent variant)
- tests/api/test_replay_loader_vent_view.py (new: fixture replay with a structured vent turn serves end-to-end)

**Files NOT in scope:**
- meetings/ (the source schema landed in 15.4)
- scripts/gen_frontend_types.py (run, not edited)
- replays/samples/ (v4 sets untouched; the first real vent turns arrive with 15.7)

**Definition of done:**
- [ ] A fixture replay containing a structured `SawVentObservation` turn loads and serves through the replay API without error (the pre-fix TypeError is pinned by a regression test against the old behavior's input).
- [ ] `frontend/src/types/api.ts` is regenerated (not hand-edited) and committed; `npm run tsc:check` and the build pass with the renderer extension.
- [ ] The observation renderer displays the vent sighting (subject, room, tick) in the meeting transcript view; the three existing observation variants render byte-identically.
- [ ] Committed v4 sets still load, byte-verify, and serve unchanged.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- api.schemas.SawVentObservationView

**Implementation hint:**

Follow the existing three variants end-to-end as the template: `meetings.schemas` type →
`api.schemas.*View` → `_observation_claim_view` branch → generated TS type → renderer case. The
generator (`scripts/gen_frontend_types.py`) owns the TS file; run it and commit the output. Keep the
loader mapping exhaustive-with-raise (do not add a silent default branch — the TypeError doctrine
stays; this task just teaches it the fourth variant).

**Ready-to-paste prompt:** `agent_prompts/task-15-4-1-vent-spectator-mirror.md`

### Task 15.5 — Reporter exculpation: stop convicting the messenger (default-OFF lever)
**Branch:** `phase-15-reporter-exculpation`
**Depends on:** 15.4, 15.6
**Section refs:** tasks/post-phase-14-clean-up.md H5; audits/audit-phase-14-close.md §4 (the zero-flag channel this hole dominates); agents/memory/beliefs.py (the accumulator/cap structure); audits/post-phase-14-pause.md §4.3 (the boundary-sum IEEE hazard, pinned here before deltas are touched)
**Complexity:** Integration

Close the second measured hole: 22 of baseline-2's 106 report-meeting ejections removed the meeting's
own reporter — all 22 innocent (impostors essentially never self-report in the corpus; verify and cite
the measured rate in the PR). The mechanism is structural: proximity-at-discovery reads as guilt, and
the reporter is definitionally at the body. Ship a default-OFF `reporter_exculpation` lever in the
13.5/14.10 pattern with two coordinated parts: (a) BELIEF-side — during the meeting a body-report
triggered, cap/dampen accusation-driven suspicion lift against that meeting's REPORTER (the
testimony-spread and accusation-carry channels), while leaving hard-flag-backed lift fully intact — a
reporter caught by a real contradiction or a vent/kill flag is still convictable; no immunity, only
removal of the proximity prior; (b) RENDER-side — the vote surface names the reporter and states the
base rate ("p-N reported the body; self-report is weakly exculpatory in this game"), layered onto the
vote template — WITH its own per-template provenance bump: this task edits `vote_ballot.j2` after 15.4
already stamped the set v5 while keeping that template byte-identical, so without a distinct version
two different vote-prompt bodies would both stamp `vote_ballot.qwen3_32b.v5` and any recording made
between the two merges would be unattributable; this task therefore bumps ONLY the `vote_ballot`
registry entry to v6 (per-template versioning is exactly what the provenance mapping exists for). The
render plumbing is explicit and inert-when-OFF: the vote
renderer's contract (in `meetings/render_contract.py`, the leaf home 15.6 creates) and
`agents/strategic/prompts/loader.py` gain a DEFAULTED reporter/lever render input (the Voice-doc 15.0
widen-the-contract-inert pattern), and the template renders the annotation only when the lever supplies
it — so lever-OFF prompts stay byte-identical and no template edit leaks into the OFF path. Because
this task edits belief deltas' surroundings, it FIRST pins the boundary-sum hazard: tests asserting
every documented delta combination that is designed to cross the 0.60 gate actually crosses it (the
`0.5 + 0.05 + 0.05` IEEE-luck case), so a later retune cannot silently break the two-signal eject.

**Files in scope:**
- agents/memory/beliefs.py (reporter-damp rule + `reporter_exculpation_enabled` resolver)
- orchestrator/replay.py (lever registration region — `_TOGGLEABLE_LEVER_RESOLVERS` + `substrate_flag_snapshot`)
- meetings/manager.py (vote-surface reporter annotation region — reporter identity into the render inputs)
- meetings/render_contract.py (vote-renderer contract widening region — the DEFAULTED reporter/lever render input; 15.6 creates the module)
- agents/strategic/prompts/loader.py (vote-renderer reporter kwarg region — defaulted/inert pass-through)
- agents/strategic/prompts/qwen3_32b/ (vote_ballot template reporter line — layered on 15.4's v5 set)
- orchestrator/game.py (PROMPT_VERSION_SETS vote_ballot entry only — the v5 → v6 per-template bump; disjoint from 15.4's set-bump line)
- .env.example (the lever env)
- tests/agents/test_beliefs.py (boundary-sum pins + damp-rule tests)
- tests/orchestrator/test_replay.py (lever stamp)
- tests/meetings/test_manager_reporter_render.py (new)

**Files NOT in scope:**
- meetings/voting.py (tally untouched — this is a belief/render lever, not a tally change)
- replays/samples/ (the re-record is 15.7; OFF must be byte-identical)
- eval/ (the 22/106 instrument is 15.3's)
- orchestrator/game.py outside the single vote_ballot registry entry (15.4 owns the set bump; 15.8.1/15.9 own their plumbing regions)

**Definition of done:**
- [ ] Lever OFF = byte-identical: `bash scripts/verify_samples.sh` reconstructs both committed sets clean with the lever merged OFF.
- [ ] Boundary-sum pins land BEFORE the rule change (separate commits): every documented gate-crossing delta combination is asserted against the 0.60 gate.
- [ ] The offline counterfactual (the 14.8 `allow_substrate_mismatch` analysis-only machinery) reports, over the committed baseline-2 bytes: how many of the 22 innocent-reporter convictions' deciding lifts the damp keeps below the gate, and that ZERO hard-flag-backed convictions (vent/kill/contradiction-flagged subjects) change outcome — the over-damping canary.
- [ ] The measured impostor self-report rate on the committed corpus is computed and cited in the rule's docstring (the empirical justification for treating self-report as weakly exculpatory).
- [ ] The lever is registered and stamped (`substrate_flag_snapshot` + MANIFEST provenance path), and the vote-surface annotation renders ONLY lever-ON (OFF renders byte-identical prompts).
- [ ] The `vote_ballot` registry entry is bumped to v6 in this task (the other three templates stay v5), so the pre-15.5 and post-15.5 vote-prompt bodies can never share a provenance stamp.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.memory.beliefs.reporter_exculpation_enabled

**Implementation hint:**

Clone the 14.10 evidence-quality lever end-to-end: resolver + registration + stamp + offline
counterfactual + byte-coupled OFF tests — the pattern has shipped five times. The damp targets the
SOFT channels only (accusation spread / carry against the reporter within the triggered meeting); the
hard-flag path (`apply_contradiction_rule` strong flags) must be provably untouched. Reporter identity
already exists at meeting scope (`MeetingTriggeredEvent.actor` / the trigger the manager receives) —
thread it through the render inputs, do not re-derive it from the transcript.

**Integration risk:**

Over-damping is the real risk: an impostor who self-reports to launder suspicion would gain cover. The
measured base rate (~zero self-reports in 160 kills) says the prior is currently safe, but the
counterfactual canary (zero hard-flag outcome changes) is the contract's hard line, and the lever stays
default-OFF until 15.7 measures it live. Second risk: the joint suspicion cap (`_joint_capped_suspicion`)
interacts with any new damp — the damp must compose with the existing caps, not bypass them.

**Ready-to-paste prompt:** `agent_prompts/task-15-5-reporter-exculpation.md`

### Task 15.6 — Substrate hygiene: latent hazards, dead code, single-homed constants, firewall contracts
**Branch:** `phase-15-substrate-hygiene`
**Depends on:** 15.4
**Section refs:** tasks/post-phase-14-clean-up.md H6; audits/post-phase-14-pause.md §3 (dead StrategicReasoner, constant homing, import contracts), §4.1 (the raw-vs-rendered [0.595, 0.60) band); meetings/manager.py:2486-2498 (the redirect guard); eval/_suspicion_parse.py:54 (the deliberate re-declaration)
**Complexity:** Integration

Close the known latent hazards before the phase builds on the surfaces they sit in. Four items, each
small, bundled because they share files with each other and nothing else. (1) **The
raw-vs-rendered gate band:** the ballot-redirect guard recomputes the §4.6 verdict from RAW suspicion
floats while the prompt renders `"%.2f"` — a raw value in `[0.595, 0.60)` displays as 0.60 (the model
reads MUST-vote) while the guard reads MUST-skip; make guard and render agree (compare on the rendered
2dp value), pinned by fixtures across the band. (2) **Single-home the manager surface `agents/` imports:**
`DEFAULT_SKIP_CONFIDENCE_THRESHOLD` lives inside 3-KLoC `meetings/manager.py` and is imported UPWARD by
`agents/` (`crewmate_policy.py:86`) — and so are the render-contract types: `agents/strategic/prompts/
loader.py:76-81` imports `ReportPromptRenderer`, `StatementPromptRenderer`, `SuspicionEntry`, and
`VotePromptRenderer` from `meetings.manager`, so re-homing the constant alone would NOT make the
`agents ↛ meetings.manager` contract satisfiable. Move the constant to a new leaf
`meetings/constants.py` AND the four render-contract types to a new leaf `meetings/render_contract.py`
(pure typing/pydantic surface, no manager import), update both importers (`manager.py` re-exports may
remain for internal use; `agents/` must import only the leaves), and add the pin test the pause audit
asked for: eval's deliberately re-declared `SKIP_SUSPICION_THRESHOLD` must equal the threshold the
current baseline was recorded under. (3)
**Delete the dead `StrategicReasoner` island** (~2.7 KLoC: `agents/strategic/reasoner.py`,
`agents/strategic/output_schemas.py`, its 1820-line test) — instantiated only by its own test, never by
production, and it reads as a live alternate meeting path to every explorer; the triggered-LLM design
idea stays recorded in DESIGN.md §4 for a future phase, but the unwired code goes. (4) **Add the two
clean import contracts + de-stale AGENTS.md:** `observation ↛ agents/meetings/llm` and (now enabled by
item 2) `agents ↛ meetings.manager` in `.importlinter`; and fix AGENTS.md's stale doctrine — the
canonical eval provider is Featherless `Qwen/Qwen3-32B` (not Ollama `qwen3.5:9b`), and the GitHub-
tooling section's absolute claims are rewritten environment-neutral (the current text asserts `gh` is
always available and MCP GitHub tools always fail — false in at least one active dispatch environment).

**Files in scope:**
- meetings/constants.py (new: the gate constant's single home)
- meetings/render_contract.py (new: the render-Protocol + SuspicionEntry leaf home)
- meetings/manager.py (redirect-guard band region + constant/render-contract re-home — disjoint from 15.4's validation region and 15.5's vote-surface region)
- agents/strategic/prompts/loader.py (import the render contract from meetings.render_contract + scrub the stale StrategicReasoner docstring reference at :5; 15.5's kwarg region comes later)
- agents/strategic/prompts/__init__.py (scrub the stale StrategicReasoner docstring reference at :6)
- llm/budgeted_client.py (module docstring reference at :3 only — the last live `StrategicReasoner` mention outside the island and the two prompt-module docstrings)
- agents/tactical/crewmate_policy.py (import the constant from meetings.constants)
- agents/strategic/reasoner.py (DELETE)
- agents/strategic/output_schemas.py (DELETE)
- tests/agents/test_strategic_reasoner.py (DELETE)
- .importlinter (two firewall contracts + the root/config change they require — `meetings` and `llm` must become checkable via root_packages or include_external_packages, else lint-imports errors before evaluating the contracts; 15.8 extends the SAME root_packages block later, strictly behind its dependency edge on this task)
- meetings/schemas.py (stale output_schemas docstring pointer region at :20 — behind the 15.4 edge; the doc currently directs contributors to re-export new strategic types in the module this task deletes)
- AGENTS.md (provider + GitHub-tooling de-stale)
- tests/meetings/test_manager_gate_band.py (new: the [0.595, 0.60) fixtures)
- tests/eval/test_suspicion_parse_pin.py (new: the eval-constant pin)

**Files NOT in scope:**
- eval/_suspicion_parse.py (the re-declaration is deliberate and stays; it gets a PIN TEST, not an import)
- meetings/voting.py (tally untouched; it receives the threshold as a parameter already)
- DESIGN.md + AGENT_IMPLEMENTATION.md (owner-side; the generator bars task agents from them)
- agents/strategic/prompts/qwen3_32b/ and the other template-set directories (template text belongs to 15.4/15.5, and template bodies are provenance-versioned — the retired `qwen3_5_9b` set's stale prose comments (its vote_ballot.j2 mentions the deleted `output_schemas` module; its impostor_report.j2 says "strategic reasoner" in lowercase prose) stay frozen rather than forcing a pointless version bump on a retired set; the grep-zero DoD is on the literal `StrategicReasoner` symbol, which no template contains)

**Definition of done:**
- [ ] Guard-vs-render agreement: for raw suspicion values across `[0.55, 0.65]` including the
  `[0.595, 0.60)` band, the redirect guard's verdict equals the rendered-value verdict (fixture-pinned);
  committed sets still byte-verify (reconstruction re-feeds recorded actions, so OFF-path bytes are
  untouched — asserted by `verify_samples.sh`).
- [ ] `DEFAULT_SKIP_CONFIDENCE_THRESHOLD` has exactly one definition home (`meetings/constants.py`);
  `meetings/manager.py` and `agents/tactical/crewmate_policy.py` import it; the eval pin test fails if
  eval's re-declared threshold ever diverges from the constants home.
- [ ] The render-contract types (`ReportPromptRenderer`, `StatementPromptRenderer`, `SuspicionEntry`,
  `VotePromptRenderer`) live in `meetings/render_contract.py`; `agents/strategic/prompts/loader.py`
  imports NOTHING from `meetings.manager` (a grep-zero assertion in the test suite, plus the KEPT
  contract).
- [ ] The StrategicReasoner island is deleted; a repo-wide grep for `StrategicReasoner` returns zero
  references in LIVE code — imports, instantiations, and the stale docstring mentions in
  `agents/strategic/prompts/loader.py:5` / `agents/strategic/prompts/__init__.py:6` /
  `llm/budgeted_client.py:3` (historical mentions in closed task docs and audits stay, and the
  provenance-frozen template bodies contain only lowercase prose, never the symbol); the suite
  passes without it.
- [ ] `uv run lint-imports` reports every configured contract KEPT, including the two added here
  (`observation ↛ agents/meetings/llm`, `agents ↛ meetings.manager`) — three contracts alongside the
  pre-existing `agents ↛ engine`; 15.8 adds the fourth (`agents ↛ training`) strictly AFTER this task
  lands, behind the dependency edge that exists to serialize the shared root_packages
  block. The config change this requires is part of the task:
  today's root_packages (`agents, engine, observation`) cannot express a forbidden `meetings.manager` /
  `llm` target — lint-imports errors on external forbidden modules — so `meetings` and `llm` join
  root_packages (or `include_external_packages` is set), verified by the KEPT run.
- [ ] `meetings/schemas.py`'s module docstring no longer directs contributors to re-export strategic
  output types in the deleted `agents/strategic/output_schemas.py`.
- [ ] AGENTS.md names Featherless/`Qwen/Qwen3-32B` as the canonical eval provider and describes GitHub
  tooling capability-neutrally (try `gh`, fall back to the environment's GitHub integration; no absolute
  claims about either).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- meetings.constants.DEFAULT_SKIP_CONFIDENCE_THRESHOLD
- meetings.render_contract.ReportPromptRenderer
- meetings.render_contract.StatementPromptRenderer
- meetings.render_contract.SuspicionEntry
- meetings.render_contract.VotePromptRenderer

**Implementation hint:**

Keep both new modules leaves: `meetings/constants.py` stdlib-only, `meetings/render_contract.py`
typing/pydantic/schemas-only (Protocols and the `SuspicionEntry` DTO are pure surface — moving them is
mechanical; `meetings/manager.py` may import them back and re-export for internal callers, but the
dependency direction `agents → leaf` is what makes the `agents ↛ meetings.manager` contract
satisfiable). For the band fix, prefer quantize-then-compare (round the raw float to the rendered 2dp
grid before the gate comparison) over widening the gate — it makes guard and model read the same number
by construction. The deletion is mechanical but verify the island's edges first: `rg -n
"StrategicReasoner|output_schemas"` across the tree (ripgrep, per the repo tooling doctrine — not
recursive grep), including docs and task-doc Public-types claims
from old phases (historical claims in closed phase docs stay — only live code references must go to
zero).

**Integration risk:**

The band fix changes LIVE meeting behavior only inside the band (recorded replays reconstruct from
recorded actions, so committed bytes are safe), but any test that pins redirect-guard behavior on
synthetic mid-band values must be re-pinned deliberately, not silently. The manager edit sits in a file
15.4 also touches and 15.5 will touch after this task — the dependency chain (15.4 → this → 15.5)
serializes the three, so rebase on 15.4 and leave the vote-surface region clean for 15.5. Deleting
2.7 KLoC is low-risk precisely because nothing imports it — but confirm that with the grep, don't
assume it.

**Ready-to-paste prompt:** `agent_prompts/task-15-6-substrate-hygiene.md`

### Task 15.7 — Baseline 3: atomic re-record + the Wave-0 close finding (operator-run, $0)
**Branch:** `phase-15-baseline-3`
**Depends on:** 15.1, 15.2, 15.3, 15.4, 15.4.1, 15.5, 15.6
**Section refs:** tasks/post-phase-14-clean-up.md H7 + §3 (the target sheet); tasks/phase-14.md 14.12 (the atomic re-record + close pattern); audits/audit-phase-14-close.md §1 (the gate this record must pass); scripts/refresh_samples.sh (the recording harness)
**Complexity:** Integration

Record **baseline 3** — both canonical sets (50 + 50 seeds) on the unchanged model/provider
(`Qwen/Qwen3-32B`, Featherless, $0) with the Wave-0 substrate: the `qwen3_32b` set at v5 with
`vote_ballot` at v6 (15.4's vent elicitation + 15.5's reporter line; provenance rows render
`*.qwen3_32b.v5` for the three 15.4-owned templates and `vote_ballot.qwen3_32b.v6` — 15.5's
per-template bump) and the
`reporter_exculpation` lever ON — one atomic PR replacing `replays/samples/`, exactly the 14.12
pattern. Graduate the lever at the record — BOTH halves of the 14.9/14.12 move: the resolver itself
(`agents/memory/beliefs.py::reporter_exculpation_enabled`, 15.5's home) returns constant `True`, and
the registry entry moves `_TOGGLEABLE_LEVER_RESOLVERS` → `_RETIRED_ALWAYS_ON_LEVERS` in
`orchestrator/replay.py` — so the belief damp and the vote-surface annotation are UNCONDITIONAL under a
bare environment and the committed sets reconstruct BARE with no env export (this also discharges the
C6 recording-preflight hazard: no lever env for an operator to forget, and no gap between the stamped
flags and the code's bare behavior). Close the wave with
`audits/audit-phase-15-wave0-close.md`: the full validity gate, the R-gate measurement, and — the
wave's own instrument — the 15.3 funnel table re-measured against the charter's baseline-2 column
(vent transmission 36/74 → ?, structured vent observations 0 → ?, innocent-reporter ejections 22 → ?,
votes-outside-the-set 37/68 → ?), with the Phase-14 canaries (genuine-class conversion, R1) reported
alongside. Directions are findings, not pass bars; a regression on a canary is the one result that
pauses the phase for an owner call. Finally, pin the baseline-3 evidence-supply floor values into the
15.2 per-baseline constants block.

**Files in scope:**
- replays/samples/9p2i/ (the baseline-3 set: replays + MANIFEST + tournament-eval-report + rubric artifacts)
- replays/samples/4p1i/ (the baseline-3 set)
- agents/memory/beliefs.py (reporter-exculpation resolver graduation region — constant True; behind the 15.5 dependency edge)
- orchestrator/replay.py (lever graduation region — registry entry to retired-always-on; disjoint from 15.9's stamp region)
- eval/watchability.py (baseline-3 floor values in the per-baseline constants block region)
- audits/audit-phase-15-wave0-close.md (new: the close finding)
- audits/baseline2-final-measure.json (new: the committed BEFORE column — `measure_baseline.py --json` incl. `--watchability --funnel` captured on the baseline-2 bytes immediately before replacement)
- README.md (sample-provenance paragraph region — refresh recorded date / prompt set / measured win rates to baseline 3)
- tests/orchestrator/test_replay.py (graduation re-pins)
- tests/meetings/test_manager.py (byte-coupled re-pins to the new recorded bytes, where tests pin recorded rows)
- tests/scripts/test_manifest_writer.py (byte-coupled v4-row re-pins to the new recorded bytes)
- tests/api/test_eval.py (byte-coupled committed-report re-pins)

**Files NOT in scope:**
- scripts/refresh_samples.sh (drives the record as-is; graduation-at-record makes a lever export unnecessary)
- meetings/ + agents/ outside the named resolver-graduation region (all behavioral substrate changes landed in 15.4–15.6; this task graduates, records, and measures — no new behavior)
- replays/ml_corpus/ (that is 15.12's artifact, recorded against THIS baseline)

**Definition of done:**
- [ ] Both sets recorded at the Wave-0 config and committed in one atomic PR; `scripts/validity_gate.py`
  PASSES both sets from committed bytes; `bash scripts/verify_samples.sh` reconstructs all 100 samples
  clean under a BARE environment (lever graduated, no `AILIBI_*` export).
- [ ] MANIFEST provenance exact per seed: model, the mixed Wave-0 prompt versions (three templates at
  `qwen3_32b.v5`, `vote_ballot` at `qwen3_32b.v6` — 15.5's per-template bump), all six flags (five
  retired + the graduated reporter lever), git_sha, $0 cost, winner.
- [ ] The wave0-close audit reports the funnel before/after table (15.3's instrument on baseline 2 vs
  baseline 3), the R-gate measurement, and the canaries — every number regenerated by the committed
  CLIs, zero hand-computed figures. The BEFORE column regenerates from the committed
  `audits/baseline2-final-measure.json` (captured pre-replacement and named in the audit with the tip
  commit it was measured at — the baseline-2 bytes themselves survive only in git history).
- [ ] README's sample-provenance paragraph reflects baseline 3 (recorded date, the v5 prompt set with
  `vote_ballot` at v6, the measured impostor win rates) — the public quickstart never describes replaced samples.
- [ ] Every byte-coupled test that pins recorded rows or committed-report aggregates is re-pinned in
  this PR (`tests/scripts/test_manifest_writer.py`, `tests/api/test_eval.py`,
  `tests/meetings/test_manager.py`, `tests/orchestrator/test_replay.py` — plus a sweep for any other
  pin the replacement breaks); `bash scripts/check.sh` green on the final tree is the proof.
- [ ] Genuine-class conversion and R1 are reported against their baseline-2 anchors; a canary regression
  is flagged as the phase's NO-GO for an owner decision, not absorbed silently.
- [ ] The baseline-3 evidence-supply floors are pinned in `eval/watchability.py`'s per-baseline block
  with measured values in comments; `measure_baseline.py --watchability` runs clean against the new sets.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Follow 14.12's runbook: 2 parallel Featherless seed workers saturate the plan (~4h for both sets),
per-seed crash-retry, atomic staging, MANIFEST + report + rubric regeneration via the existing
refresh/build tooling. Graduation-at-record keeps the recorded stamp and the resolver's constant True
byte-consistent (the 14.12 §6 precedent explains why the committed set then serves bare). The operator
may run 15.12's corpus recording in the same session immediately after — same config, same workers —
but the artifacts land in separate PRs (canonical baseline vs training corpus provenance).

**Integration risk:**

This is a substrate re-record: every byte-coupled test that pins recorded rows must be re-pinned to the
new bytes deliberately (the 14.12 experience), and the one real NO-GO is a validity failure or a canary
regression — pause, don't paper. Prompt uptake risk is real and acceptable: v5's vent elicitation may
land below hopes (the model may under-report); that outcome is a FINDING that scopes Phase 16, not a
reason to iterate prompts inside this task (record-only discipline).

**Ready-to-paste prompt:** `agent_prompts/task-15-7-baseline-3.md`

## Wave 1 — ML signal, harness, data, surrogate, and the bake-off

### Task 15.8 — The `training/` package: rollout env, legal-action mask, reward channel (numpy lands here)
**Branch:** `phase-15-training-env`
**Depends on:** 15.6
**Section refs:** audits/post-phase-14-ML-planning.md §5, §7, §11 (action space, injection seam, env wrapper); orchestrator/game.py (AgentFactory :93, HeadlessGame :1121, MeetingAwareAgent :425-450); experiments/lab/ml_spike/core.py (the SpikeAgent interposition pattern :148-200); engine/rules.py + engine/tick.py (the legality predicates); engine/events.py (the reward-source event types)
**Complexity:** Integration

Create the new top-level `training/` package (strict-typed from day one — no mypy exclusion) holding the
rollout environment every trainer in this phase rides. `TacticalRolloutEnv` drives the REAL production
loop — `HeadlessGame` with an injected `AgentFactory` built on the proven interposition pattern (wrap
the real `TacticalAgent`, override the chosen intent, delegate the full meeting protocol via
`__getattr__` — port the ml_spike pattern into typed code, do NOT import the mypy-excluded spike) —
never a bespoke "training game." Three capabilities: (1) a **legal-action mask** over the option/intent
space, derived from the pure legality predicates in `engine/rules.py`/`engine/tick.py`, with the two
documented caveats handled explicitly — emergency-uses-remaining and the map's sabotage kinds are NOT in
the observation surface, so the mask carries small policy-side trackers (the `EmergencyPacingTracker`
precedent) rather than widening the packet; and the mask distinguishes ENGINE-LEGAL resolved actions
from OBSERVATION-MEANINGFUL submissions, keeping the impostor's pretend `do_task` (engine-rejected,
rendered as `action="task"` camouflage to witnesses — 396 such submissions in the committed baseline-2
9p2i stream) in the impostor's submission vocabulary; (2) a **potential-based reward channel** exposing
the side-specific tactically-reachable terms from the typed event log (kills, witnessed-ness via
`Killed.witnesses`, task progress, survival, report/coverage events) so trainers never re-derive rewards
from replay bytes; (3) **per-episode rollout records** carrying the behavioral descriptors the QD
entrant and the pause audit need (kill-timing distribution, witness-exposure rate, vent usage,
meeting-trigger rate, do_task-emission cadence, win shape). Episode horizon: a meeting runner is
always installed and episodes run FULL games by default; the env additionally exposes an explicit
`episode_boundary="first_meeting"` opt-in (the seam 15.13's fallback (b) rides) whose episodes end at
the meeting trigger and are MARKED truncated in the rollout record — silent truncation stays
structurally unreachable, and no fitness term ever reads a truncated episode as a full game. `uv add
numpy` (exact pin) lands in this task, confined to `training/` by a new import-linter contract
(`agents` must not import `training`) with `training` added to the linter's root packages — an edit
to the SAME root_packages block 15.6 rewrites, which is the whole reason for this task's 15.6
dependency edge (config serialization; nothing semantic).

**Files in scope:**
- training/__init__.py (new)
- training/env.py (new: `TacticalRolloutEnv`, the interposition factory, the mask)
- training/rewards.py (new: potential-based shaping + side-specific reward terms)
- training/rollout.py (new: episode records + behavioral descriptors)
- pyproject.toml (project dependencies region — the numpy exact pin; the mypy exclude regex is 15.17's disjoint region)
- uv.lock (numpy resolution)
- .importlinter (training root + agents-must-not-import-training contract — extends the root_packages block 15.6 rewrote; the dependency edge on 15.6 serializes the shared block)
- tests/training/__init__.py (new)
- tests/training/test_env.py (new)
- tests/training/test_rewards.py (new)
- tests/training/test_rollout.py (new)

**Files NOT in scope:**
- orchestrator/game.py (the seams already exist; zero orchestrator edits)
- engine/ (read-only; the RNG fast path is 15.8.1)
- agents/ (the encoder is 15.10; the FSMs are the anchor and stay untouched)
- experiments/lab/ml_spike/ (frozen reference — port, never import)
- eval/balance_eval.py (the surrogate-runner keyword is 15.13's)

**Definition of done:**
- [ ] The env runs full fake-provider games through an injected factory at or above the measured floor (≥5 games/s at 9p2i on the check host; the actual figure is documented in the module docstring).
- [ ] A meeting runner is ALWAYS installed and `meeting_runner=None` truncation (`MEETING_PHASE_REACHED`) is structurally unreachable from the DEFAULT env, asserted by test. The explicit `episode_boundary="first_meeting"` opt-in is the ONE deliberate boundary mode (15.13's fallback (b)): its episodes are marked truncated in the rollout record, and a test asserts the reward channel refuses to score a truncated episode as a full game — silent truncation is never a fitness path.
- [ ] Mask legality is property-tested against the engine: across randomized seeds/ticks, every masked-legal engine action resolves without rejection and every unmasked action is engine-rejected — with the pretend-`do_task` camouflage carried in the impostor SUBMISSION set and excluded from the engine-legal set (both asserted).
- [ ] The reward channel is potential-based: a telescoping test shows shaping sums to Φ(terminal) − Φ(initial) over any episode, so shaping cannot change the optimal policy.
- [ ] A frozen-policy episode is byte-deterministic: same seed → identical per-tick state-hash sequence across two runs (the spike's check-1 reproduced inside the committed package).
- [ ] numpy imports are confined to `training/`: `uv run lint-imports` keeps every existing contract (including 15.6's two, already landed behind the dependency edge) AND the new `agents ↛ training` contract; `training` is in root_packages.
- [ ] Episode records carry all named behavioral descriptors; a fixture pins their values on a scripted game.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.env.TacticalRolloutEnv
- training.env.ActionMask
- training.rollout.EpisodeRollout
- training.rewards.ShapedReward

**Implementation hint:**

`HeadlessGame(seed=…, game_map=…, agent_factory=…, replay_path=…, meeting_runner=…)` is the whole wiring
surface (`orchestrator/game.py:1124-1163`); `max_ticks` rides the `TickScheduler`, not the constructor.
The wrapper agent must satisfy the FULL `MeetingAwareAgent` protocol (both properties + both render
methods — isinstance-checked at `game.py:863` before meetings build participants); wrapping the real
`TacticalAgent` and delegating via `__getattr__` gets all of it for free, plus the crew-only
`EmergencyPacingTracker` bookkeeping. Mask derivation: every legality predicate is a pure boolean of
`(state, map, actor)` with zero RNG — mirror them agent-side from the packet + trackers rather than
importing engine (the firewall forbids `agents → engine`, and `training/` should reach engine truth only
through the orchestrator loop). Default meeting runner for rollouts is `build_default_meeting_runner` on
the fake provider (`tests/conftest.py` pins `AILIBI_LLM_PROVIDER=fake` for all tests); the surrogate
slots in via the same parameter once 15.13 lands.

**Integration risk:**

This is the seam every trainer rides; the failure mode is DRIFT from the production loop — a bespoke
training game would silently invalidate every fitness number and every determinism claim downstream. The
env must be the real `HeadlessGame`, the real observation firewall, the real meeting manager, with the
ONLY interposition at the factory. Second risk: numpy — BLAS reductions are not bit-stable across
machines/thread counts, which is exactly why numpy stays training-side and the production inference path
(15.10, Wave 2) stays pure-Python; the import-linter contract is the enforcement, not a convention.
Third: the mask must not delete the pretend-`do_task` camouflage lever — a strict engine-legal-only
vocabulary regresses the impostor's task-traffic mimicry, which is measured behavior on the committed
baseline.

**Ready-to-paste prompt:** `agent_prompts/task-15-8-training-env.md`

### Task 15.8.1 — Training-only RNG hash fast path (opt-in; committed paths byte-unchanged)
**Branch:** `phase-15-rng-fast-path`
**Depends on:** 15.8, 15.9
**Section refs:** audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization)
**Complexity:** Medium

`engine/rng.py` re-serializes the full 625-int Mersenne state via `json.dumps` on every tick (~43% of
bare-engine cost) and the drawn value is discarded — but that serialization is hashed into every
committed `state_hash`, so it is load-bearing for replay byte-identity and must NEVER be changed in
place. This task adds an explicit, opt-in hash policy (a typed policy object threaded `HeadlessGame →
engine`, no env-var magic) that skips the per-tick rng-state serialization for non-recorded training
rollouts only. Two enabling facts make the scope wider than `engine/rng.py` alone: (a) the per-tick
snapshot is INVOKED from `engine.tick.advance_tick` (the `EngineRng.from_state(...).randint(...)` draw
that writes `next_rng_state`), so the policy threads through `engine/tick.py` — in scope, with the
default path pinned byte-identical there; and (b) `HeadlessGame` today REQUIRES a `replay_path` and
constructs a `ReplayLog` unconditionally, which would make "non-recorded rollouts" unreachable — so
this task also adds an explicit NO-REPLAY training mode (`replay_path=None` → no `ReplayLog`, nothing
written), which is the only construction that accepts the fast-path policy; any replay-writing
construction refuses it loudly, and a no-replay construction that receives 15.9's
`tactical_policy_stamp` also raises (a stamp with nothing to record it is a caller bug). This task
edits the SAME `HeadlessGame` constructor 15.9 stamps — the 15.9 dependency edge serializes the two,
so rebase on the stamped signature. The RNG draws themselves are untouched — trajectories are identical
under both modes, so training results transfer to the recording path exactly.

**Files in scope:**
- engine/rng.py (the opt-in fast-path region; default behavior byte-identical)
- engine/tick.py (the per-tick rng-snapshot invocation region — policy-aware, default byte-identical)
- orchestrator/game.py (rng-hash policy plumbing + optional no-replay training-mode region — disjoint from 15.4's registry/protocol regions and 15.5's vote entry; shares the `HeadlessGame` constructor with 15.9's stamp kwarg, serialized by this task's dependency edge on 15.9)
- training/env.py (fast-path + no-replay knob region — 15.8 owns the rest of the module)
- tests/engine/test_rng_fast_path.py (new)
- tests/training/test_env_fast_path.py (new)
- tests/orchestrator/test_no_replay_mode.py (new)

**Files NOT in scope:**
- orchestrator/replay.py + api/replay_loader.py (recording/verification never accepts the fast path — refusal at construction, not silent downgrade)
- scripts/_verify_samples.py (unchanged; committed samples must keep verifying)
- replays/samples/ (untouched)

**Definition of done:**
- [ ] Default path byte-identical: `bash scripts/verify_samples.sh` reconstructs all 100 committed samples clean with the change merged.
- [ ] Fast path measurably faster: the engine-core speedup ratio is measured and documented (target ≥1.3×; report the actual).
- [ ] The no-replay training mode is real: `replay_path=None` constructs a game that writes NOTHING to disk (asserted), runs to completion, and is the ONLY construction that accepts the fast-path policy; every replay-writing construction with the fast path active raises a descriptive error (tested); a no-replay construction combined with 15.9's `tactical_policy_stamp` raises (tested); the training env exposes both knobs and defaults them OFF.
- [ ] Trajectory equivalence proven: for a frozen policy on a fixed seed set, the full action/event streams are IDENTICAL under both modes (only hashing cost differs), asserted by test.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- engine.rng.RngStateHashPolicy

**Implementation hint:**

The loosening the owner approved is exactly this shape: skip the `json.dumps` snapshot of the Mersenne
state per tick, never the draws. Keep the policy object explicit in signatures (the repo's no-silent-
fallbacks doctrine): a recording constructor that receives a fast-path policy raises; nothing infers the
mode from the environment. The state-hash serializer in `orchestrator/replay.py` is not edited — the
fast path simply never reaches it, because recording refuses the policy up front.

**Ready-to-paste prompt:** `agent_prompts/task-15-8-1-rng-fast-path.md`

### Task 15.9 — Tactical-policy provenance stamp (replay writer + MANIFEST + loader guard)
**Branch:** `phase-15-policy-provenance`
**Depends on:** none
**Section refs:** audits/post-phase-14-ML-planning.md §7.2-7.3 (record-actions provenance; the stamp recommendation); orchestrator/replay.py (substrate_flag_snapshot :277-299, game_over stamping :434-441); api/replay_loader.py (the substrate mismatch guard :377-423); scripts/_manifest_writer.py
**Complexity:** Integration

Answer "which tactical policy produced these bytes" the same way the repo already answers "which
substrate levers": a provenance stamp, mirrored across the three provenance surfaces.
`orchestrator/replay.py` stamps a `tactical_policy` block into the `game_over` entry — `{policy_id,
method, encoder_version, weights_sha256, anchor_policy}` (plain strings; no import of any training code)
— exactly beside the existing `substrate_flags` stamp; `scripts/_manifest_writer.py` adds a policy
column so every recorded set's MANIFEST attributes each seed; `api/replay_loader.py` gains a mismatch
guard mirroring `ReplaySubstrateMismatchError` that refuses to serve a stamped replay under a
conflicting policy claim. The stamp also needs a PRODUCTION injection seam, not just a writer-level
API: `HeadlessGame` constructs its `ReplayLog` internally and every recorder (run_tournament, the
corpus wrapper, Wave-2 champion recordings) reaches replay-writing only through that constructor — so
`HeadlessGame` gains an optional `tactical_policy_stamp` keyword (default `None` = absent = FSM)
passed through to the writer, `run_tournament_eval` gains the matching optional pass-through, and
`scripts/run_tournament.py` exposes it as a CLI flag (`--tactical-policy-stamp`, accepting the
literal `fsm-default` for the canonical scripted stamp or a JSON-file path for Wave-2 champion
stamps) — so a learned-policy recording can actually be stamped without a later out-of-scope edit,
and the 15.12 corpus wrapper (a shell composer of that CLI) can stamp explicitly. An ABSENT stamp means "scripted FSM default" and stays fully valid — the
committed canonical sets are untouched and must keep loading, byte-verifying, and serving with zero
edits (this holds across the 15.7 re-record: baseline 3 is recorded with the FSM default and may carry
the explicit stamp if this task lands first, or none — both are valid). Replay reconstruction re-feeds
recorded actions and never re-invokes a policy, so the stamp is provenance, not a replay input — this is
what keeps learned-policy replays byte-identical regardless of inference-float questions.

**Files in scope:**
- orchestrator/replay.py (tactical-policy stamp region, alongside the substrate-flags stamp — disjoint from 15.5's registration region and 15.7's graduation region)
- orchestrator/game.py (HeadlessGame tactical_policy_stamp pass-through kwarg region — disjoint from 15.4's registry/protocol regions and 15.5's vote entry; 15.8.1 later edits the same constructor behind its dependency edge on this task)
- eval/balance_eval.py (run_tournament_eval policy-stamp pass-through kwarg region — additive-optional; disjoint from 15.13's meeting-runner kwarg region, edge exists transitively via 15.12)
- api/replay_loader.py (policy-stamp read + mismatch guard region — disjoint from 15.4.1's observation-view region)
- scripts/_manifest_writer.py (policy column)
- scripts/run_tournament.py (the `--tactical-policy-stamp` CLI flag region — plumbed to `run_tournament_eval`'s new kwarg; no other CLI behavior changes)
- tests/orchestrator/test_replay_policy_stamp.py (new)
- tests/api/test_replay_loader_policy_stamp.py (new)
- tests/scripts/test_manifest_writer.py (extend: FSM-default rendering pinned)

**Files NOT in scope:**
- replays/samples/ (committed bytes untouched; absent stamp = FSM default)
- agents/ + training/ (no coupling: the stamp is strings, set by the recorder)
- scripts/refresh_samples.sh (the canonical-sample refresh flow is frozen; the corpus recorder 15.12 consumes the stamp)

**Definition of done:**
- [ ] The committed canonical sets load, byte-verify (`bash scripts/verify_samples.sh` clean), and serve with zero edits — absent stamp renders as the FSM default everywhere.
- [ ] A stamped recording round-trips writer → loader with all five fields intact; the stamp appears in the game_over entry beside `substrate_flags`.
- [ ] The production seam works end-to-end: a game recorded through `HeadlessGame(tactical_policy_stamp=…)`, one through `run_tournament_eval(..., tactical_policy_stamp=…)`, and one through the `scripts/run_tournament.py --tactical-policy-stamp fsm-default` CLI (the seam 15.12's shell wrapper drives) all land stamped on disk (not just a writer-level unit round-trip); omitting the kwarg/flag records absent-stamp = FSM default, byte-identical to today's path.
- [ ] A deliberately mismatched stamp raises the new loader guard (fail-loud, mirroring the substrate guard's shape and error quality).
- [ ] The MANIFEST writer emits the policy column; existing manifest tests pin the FSM-default rendering for unstamped rows.
- [ ] The stamp schema is documented (module docstring) for 15.12 (corpus rows stamp the FSM default explicitly) and Wave 2 (champion weights hash).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- orchestrator.replay.TacticalPolicyStamp
- api.replay_loader.ReplayPolicyMismatchError

**Implementation hint:**

Clone the substrate-flags pattern end to end: `substrate_flag_snapshot()` → the game_over stamp
(`orchestrator/replay.py:277-299`, `:434-441`) → the loader's `_assert_substrate_matches` guard
(`api/replay_loader.py:377-423`). The stamp is additive JSON in an existing entry — the risk surface is
serialization order/shape perturbing committed hashes, so add fields in a way the state-hash serializer
never sees (the state hash covers `WorldState`, not replay-entry metadata — verify with the
byte-identity suite, not by assumption).

**Integration risk:**

The whole task is byte-compatibility: the committed samples are the regression fixture, and
`verify_samples.sh` green under a bare environment is the non-negotiable proof. Second risk: schema
creep — the stamp must stay plain strings so `orchestrator/` never imports training or agents code
(keeping the dependency direction clean for the import-linter contracts added this phase).

**Ready-to-paste prompt:** `agent_prompts/task-15-9-policy-provenance.md`

### Task 15.10 — Encoder v2 (memory-carrying), the determinism harness, and the leak-test factory mode
**Branch:** `phase-15-encoder-v2`
**Depends on:** 15.8
**Section refs:** audits/post-phase-14-ML-planning.md §6 (observation surface, encoder shape, determinism hazards); observation/packet.py:159-188; observation/public_map.py:14-32; agents/memory/beliefs.py + agents/memory/working.py (the carried state); experiments/lab/ml_spike/core.py:60-83 (the 34-dim memoryless baseline); eval/leak_test.py; tests/test_firewall.py:64-75
**Complexity:** Integration

The spike's 34-dim encoder is memoryless — the structural reason its behavior clone capped below FSM
parity (the FSM's stalk is history-dependent). Build the versioned production encoder in
`agents/tactical/features.py`: pure-Python, deterministic, firewall-legal, consuming `ObservationPacket`
+ `PublicMapView` + the agent's OWN memory (`MemoryStore` episodic recency, `WorkingMemory.last_seen`
(tick, room) ages, own `BeliefState` suspicion/trust floats — quantized to a fixed grid before they
touch any feature, per the §6.3 determinism hazard), with an `ENCODER_VERSION` constant that feeds the
15.9 stamp. Ship the two harnesses every candidate must pass: `training/determinism.py` (double-run
SHA-256 over the full (feature-vector, logits, chosen-intent) stream of a frozen policy across a fixed
seed set, plus frozen-genome full-game state-hash equality) and an agent-factory mode for
`eval/leak_test.py` — today it walks 3 scripted fixtures with no factory parameter, so a learned mover
that drives the engine into regions those fixtures never reach is unscanned; the extension runs
factory-built agents through full games and applies the existing recursive role-leak scanners to every
packet the encoder consumes. Extend `tests/test_firewall.py` with the pure-Python inference doctrine: no
`numpy`/`torch` import anywhere under `agents/`.

**Files in scope:**
- agents/tactical/features.py (new: the versioned encoder)
- training/determinism.py (new: the policy determinism harness)
- eval/leak_test.py (agent-factory mode region — the 3 scripted fixtures stay byte-identical)
- tests/test_firewall.py (extend: numpy/torch ban under agents/)
- tests/agents/test_features.py (new)
- tests/training/test_determinism.py (new)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py + crewmate_policy.py (the FSMs are the anchor and the BC oracle — untouched)
- observation/ (NO packet surface change: the un-observable crew task-set stays un-observable pending the pause decision)
- agents/memory/ (read-only: the encoder consumes the stores, never mutates them)
- .importlinter (contracts landed in 15.6/15.8)

**Definition of done:**
- [ ] The encoder is engine-free (existing `agents ↛ engine` contract + the schema-file firewall test cover it) and total over every packet shape in the committed corpora: a sweep test feeds all committed games' packets through it without error.
- [ ] Feature layout + dimension count are documented and pinned by a golden test; `ENCODER_VERSION` bumps are the only way the layout may change.
- [ ] Belief-derived features are integer-quantized with lexical tie-breaking documented — no raw-float comparison anywhere in the encoder (the residue-flips-argmax hazard).
- [ ] Determinism harness: two runs of a frozen policy over a fixed seed set produce identical SHA-256 over (features, logits, intents); the harness is a library any bake-off entrant invokes, and its report is the artifact 15.15 quotes.
- [ ] Leak-test factory mode passes for the FSM default factory AND a learned-wrapper factory; a planted role-leak fixture trips it (the scanner still bites).
- [ ] The firewall test rejects a synthetic `import numpy` planted under `agents/` (asserted via the same source-scan mechanism as the engine-import check).
- [ ] Weights serialization is fixed for Wave 1: float64-hex JSON, exact round-trip pinned by test; the int-quantization decision is explicitly deferred to the PAUSE (stated in the module docstring).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.tactical.features.TacticalFeatureEncoder
- agents.tactical.features.ENCODER_VERSION
- training.determinism.PolicyDeterminismReport

**Implementation hint:**

The memory features already exist and are cheap: per-player `(suspicion, trust)` floats
(`agents/memory/beliefs.py:440-457`), `LastSeen(tick, room)` (`agents/memory/working.py:49-55`), and
episodic recency from `MemoryStore.recent()`. `moved_players` is omitted from the packet JSON when
empty — treat it as optional, never `[]`-assumed. Roster-dependent features need fixed-slot encoding
sorted by `player_id` (the repo's lexical-tie-break idiom). The crew side may only consume belief state
the crew agent legitimately holds — the same information that already reaches crew tactics through
`EmergencyPacingTracker._over_gate`; document any widening explicitly in the docstring so the leak
review has one place to look.

**Integration risk:**

The encoder is the one place role-blind observation and role-private memory meet: a feature that folds
in another agent's private state is a firewall breach the import-linter cannot see — which is why the
leak-test factory extension lands in the SAME task, not later. Second risk: determinism — belief floats
accumulate non-power-of-two deltas and `known_players()` is dict-insertion-ordered; quantize-then-compare
and sorted iteration are mandatory, and the harness hashes features+logits precisely so a violation is
caught at the artifact, not in a downstream replay.

**Ready-to-paste prompt:** `agent_prompts/task-15-10-encoder-v2.md`

### Task 15.11 — The meeting training table + surrogate fidelity harness (re-baseline FO-6 honestly)
**Branch:** `phase-15-meeting-table`
**Depends on:** 15.7, 15.8
**Section refs:** audits/post-phase-14-ML-training-signal.md §2, §5.4-5.5, §7.2 (the table, the fidelity protocol, the honest ceiling); agents/memory/beliefs.py (the LLM-free belief fold); meetings/manager.py (derive_belief_evidence :2680; roster off result.ballots :2823); experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (the failed prior)
**Complexity:** Medium

Build the supervised substrate the ballot surrogate trains and is judged on — against **baseline 3**
(this task runs after 15.7 so the table reflects the meeting layer the surrogate will simulate). For
every committed meeting, reconstruct OFFLINE (LLM-free, replay-deterministic) the per-(meeting, voter)
feature rows: the pre-meeting belief-fold state (rendered suspicion/trust toward each candidate — the
fold in `agents/memory/beliefs.py` is deterministic over recorded events and needs no LLM),
contradiction-flag structure (including the new vent flags), sighting/co-presence reconstruction,
reporter identity, kill-proximity and isolation, movement anomalies, and task-cadence features — joined
to the ACTUAL recorded ballots `{voter, target, confidence, primary_reason_id}` and to roles ground
truth from `tournament-eval-report.json` (raw replays carry no roles by firewall design). Ship the
fidelity harness the phase judges ALL meeting models with: by-GAME cross-validation (never by-meeting —
leakage), top-1/top-2 ejected-target ranking, SKIP-vs-eject decision accuracy, and Brier/ECE calibration
on ballot confidences — plus the HONEST CEILING: the measured voice-driven share of ejections a
physical+belief surrogate structurally cannot see. Re-run the FO-6 logistic under this harness to pin
the true prior baseline (its headline top-1 64% collapsed to 26%/43% on baseline 2, and its binary head
degenerates to always-SKIP), and mark the stale spike conclusion at its source:
`experiments/lab/report-ml-spike.md` gets a STALE banner pointing here. The table builder takes any
replay-set directory and reads a committed `splits.json` when present — it runs identically on the 15.12
corpus.

**Files in scope:**
- training/surrogate/__init__.py (new)
- training/surrogate/dataset.py (new: the table builder + splits.json loader)
- training/surrogate/fidelity.py (new: CV protocol + metrics + the honest ceiling — the GO/NO-GO wiring is 15.13's region)
- training/reports/report-meeting-table.md (new: table stats, FO-6 re-baseline, the honest ceiling)
- experiments/lab/report-ml-spike.md (STALE banner only — no other edit)
- tests/training/test_surrogate_dataset.py (new)
- tests/training/test_surrogate_fidelity.py (new)

**Files NOT in scope:**
- agents/memory/beliefs.py + meetings/manager.py (the fold is consumed read-only)
- experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (frozen probe; re-run, not edited)
- replays/ (read-only; the corpus lands in 15.12)

**Definition of done:**
- [ ] Table counts reproduce the ACTIVE committed sets exactly (meeting/ejection/ballot totals derived from the sets' tournament reports, not hardcoded — the sets are baseline 3 by this task's dependency order); every recorded ballot joins a feature row (100% join rate, asserted).
- [ ] Every feature column derives offline: no LLM call, no network, no engine import in `training/surrogate/` beyond the orchestrator-mediated reconstruction path; a determinism test rebuilds the table twice byte-identically.
- [ ] The fidelity harness enforces by-game CV (a leakage test proves two meetings of one game never split across folds) and reports top-1/top-2, SKIP-vs-eject accuracy, and Brier/ECE together — never a single headline number.
- [ ] The honest ceiling is computed from the committed bytes and stated in the report as the surrogate's maximum achievable top-1 — a measurement, not a target.
- [ ] The FO-6 re-baseline row appears in the report with its by-game-CV numbers and its always-SKIP failure made explicit.
- [ ] `experiments/lab/report-ml-spike.md` carries the STALE banner naming the regressed figure and pointing at the report this task commits.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.surrogate.dataset.MeetingTableRow
- training.surrogate.dataset.build_meeting_table
- training.surrogate.fidelity.SurrogateFidelityReport

**Implementation hint:**

The single biggest upgrade over FO-6's six raw counts is the belief-fold rendered suspicion — it already
integrates the accumulators the LLM votes on, and `derive_belief_evidence` (`meetings/manager.py:2680`)
re-derives the exact pre-meeting graph deterministically from recorded events. Mine
`audits/workflows/extract_gameplay_facts.py` and `eval/funnel.py` (15.3) for reconstruction recipes —
import the committed 15.3 folds where they fit; never import the audit script or the mypy-excluded
spike. Row grain is one row per (meeting, voter) — the roster the cross-meeting fold uses is read off
`result.ballots`, which fixes it.

**Ready-to-paste prompt:** `agent_prompts/task-15-11-meeting-table.md`

### Task 15.12 — The ML-calibration corpus at baseline-3 config: record, validate, freeze (operator-run, $0)
**Branch:** `phase-15-ml-corpus`
**Depends on:** 15.1, 15.7, 15.9
**Section refs:** audits/post-phase-14-ML-training-signal.md §5.6, §7.2 (the frozen-corpus doctrine + the data gap); tasks/post-phase-14-plan.md §4 (nothing trains against a layer scheduled to change); scripts/refresh_samples.sh (the recording pattern to compose); api/replay_loader.py + api/main.py (set-discovery semantics the layout must not collide with)
**Complexity:** Medium

Record the frozen training/calibration corpus the surrogate and the bake-off consume, at EXACT
**baseline-3** config (the 15.7 substrate: `Qwen/Qwen3-32B` Featherless non-thinking `fail_loud`
`json_object`, the `qwen3_32b` set at v5 with `vote_ballot` at v6, all levers unconditional, $0 flat-rate): **9p2i × 150 seeds
(1000–1149)** primary and **4p1i × 50 seeds (1000–1049)** secondary — fresh seed ranges so a corpus game
can never be confused with the canonical 0–49 sets (~3× the canonical 9p2i meeting/ejection volume, ~7h
wall with 2 Featherless seed workers; may share the 15.7 operator session, landing as a separate PR).
Layout: `replays/ml_corpus/9p2i/` + `replays/ml_corpus/4p1i/`, each carrying `replay-seed-*.jsonl`,
`MANIFEST.md` (with the 15.9 policy column stamping the FSM default), `roster.json` where applicable,
`tournament-eval-report.json` (the roles ground truth), and a committed by-game `splits.json`
(train/val/test — data only; the loader is 15.11's). The two-level nesting is LOAD-BEARING: a set
directory placed directly under `replays/` would make the API's directory resolution treat `./replays`
as the active parent and SHADOW the canonical samples — a discovery non-collision test pins that
`replays/ml_corpus/` is invisible to default spectator resolution while an operator can still opt-in
serve it explicitly. Freeze = MANIFEST records git_sha + an explicit FROZEN line; acceptance = the 15.1
validity gate + byte-verification, run per set before the PR merges.

**Files in scope:**
- scripts/record_ml_corpus.sh (new: thin wrapper composing scripts/run_tournament.py — contiguous seed ranges, per-seed crash-retry, MANIFEST + report + splits emission)
- replays/ml_corpus/9p2i/ (new artifact set)
- replays/ml_corpus/4p1i/ (new artifact set)
- tests/scripts/test_record_ml_corpus.py (new: dry-run/arg/splits-emission tests, no network)
- tests/api/test_set_discovery_ml_corpus.py (new: spectator discovery non-collision pinned)

**Files NOT in scope:**
- replays/samples/ (the canonical baseline is untouched — the corpus is a SEPARATE release artifact)
- scripts/refresh_samples.sh (frozen; the new wrapper composes the same underlying tooling, never edits it)
- scripts/run_tournament.py (consumed via the `--tactical-policy-stamp` flag 15.9 added, never edited)
- api/replay_loader.py + api/main.py (discovery semantics are pinned by test, not changed)
- training/ (no Python here — the splits loader is 15.11's)

**Definition of done:**
- [ ] Both corpus sets recorded at exact baseline-3 config; `scripts/validity_gate.py` PASSES on each corpus dir, and the state-hash chains byte-verify via the `_verify_samples.py` machinery pointed at the corpus.
- [ ] Every corpus replay carries the substrate flags AND the 15.9 FSM-default policy stamp; MANIFEST rows carry seed/model/prompt_versions/flags/git_sha/cost ($0)/winner plus the policy column, and the FROZEN line names the git_sha.
- [ ] `splits.json` per set: a documented deterministic by-game split (train/val/test) committed as data; no game appears in two splits (asserted by a test reading the file).
- [ ] Corpus stats reported in the PR description from the gate/measure CLIs: game count, meeting/ejection/skip counts, win split — measured, not estimated.
- [ ] The discovery test proves default spectator/API resolution ignores `replays/ml_corpus/` and that explicit opt-in serving of a corpus set still works.
- [ ] The recording script supports `--dry-run` (prints the plan, no network) and per-seed crash-retry; both covered by tests with no network access.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Compose, don't fork: `scripts/run_tournament.py --num-games … --output-dir … --tactical-policy-stamp
fsm-default` (the 15.9 CLI seam) with the roster env/args per set is the underlying recorder (the same one `refresh_samples.sh` drives); clone refresh_samples'
worker queue + crash-retry shape for the 2-worker Featherless saturation and its MANIFEST/report
emission patterns via `scripts/_manifest_writer.py` + `scripts/build_sample_report.py`. Hosted models do
not byte-reproduce FRESH generation — recordings replay byte-identically (the loosened contract the
canonical baselines already carry); the validity gate + byte-verify is the acceptance, not
generation-replay equality. Operator gate: requires `FEATHERLESS_API_KEY`; ~7h wall; commit is one
atomic PR after the gate passes. A deterministic split rule (e.g. seed mod 5 → {0,1,2}=train, {3}=val,
{4}=test) documented in the MANIFEST keeps the split auditable from the file alone.

**Ready-to-paste prompt:** `agent_prompts/task-15-12-ml-corpus.md`

### Task 15.13 — The ballot-predictor surrogate MeetingRunner (GO/NO-GO + the fallback ladder)
**Branch:** `phase-15-ballot-surrogate`
**Depends on:** 15.11, 15.12
**Section refs:** audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:420-440 (the MeetingRunner protocol), :942-979 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/constants.py (the gate constant home after 15.6); meetings/manager.py:2841 (roster off ballots); eval/balance_eval.py:228 (run_tournament_eval)
**Complexity:** Integration

The $0 inner-loop meeting model, rebuilt on the structural fix: predict each living voter's BALLOT
(target, confidence) from the 15.11 features, and let the REAL deterministic tally produce the outcome —
`tally_ballots(ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD)` (the threshold is
a required keyword with NO default; pass the constants-home value explicitly). This eliminates FO-6's
always-SKIP collapse by construction (SKIP-vs-eject emerges from plurality + the confidence gate, not a
mis-calibrated binary head) and restores belief persistence (one ballot per living voter is exactly the
roster the cross-meeting fold reads). Train on the 15.12 corpus via the 15.11 table (numpy allowed);
wrap as `SurrogateMeetingRunner` conforming to the runtime-checkable `MeetingRunner` protocol: the
returned `MeetingArtifacts` echoes `meeting_id`/`triggered_by`/`trigger_tick` (validated at
`game.py:905-943`), carries a full-roster ballot set, and empty LLM metadata. The GO/NO-GO bar is
written BEFORE training, against the 15.11 honest ceiling; the fallback ladder is in-contract: (a) the
fake-provider MeetingManager as the training-time runner, (b) the 15.8 env's explicit
`episode_boundary="first_meeting"` opt-in with meeting-free fitness terms (the env marks those
episodes truncated and no full-game term reads them — the deliberate boundary mode 15.8 contracts,
not silent truncation), (c) periodic real-LLM re-grounding recordings (operator, $0). Whatever the
verdict, the staleness doctrine ships: a use-counter/config cap the bake-off must respect, so no trainer
optimizes indefinitely against a frozen surrogate. Additively, `run_tournament_eval` gains an optional
per-game meeting-runner factory keyword (mirroring its existing per-game default-runner construction) so
surrogate-driven tournaments produce standard reports for diagnostics — final champion scoring still
always uses a real meeting path.

**Files in scope:**
- training/surrogate/ballots.py (new: the predictor + training entry)
- training/surrogate/runner.py (new: the MeetingRunner implementation)
- training/surrogate/fidelity.py (GO/NO-GO wiring region — 15.11 owns the metrics core)
- eval/balance_eval.py (additive optional meeting-runner-factory keyword on run_tournament_eval)
- training/artifacts/surrogate/ (new: the fitted ballot-predictor weights, float-hex JSON + sha256 sidecar — the exact artifact the bake-off reloads and the 15.9 stamp schema references)
- training/reports/report-ballot-surrogate.md (new: fidelity vs ceiling, the verdict, the chosen fallback, the re-grounding cadence)
- tests/training/test_surrogate_runner.py (new)
- tests/eval/test_balance_eval_meeting_runner.py (new)

**Files NOT in scope:**
- meetings/voting.py (the tally is consumed pure, never reimplemented — that is the point)
- meetings/manager.py + llm/ (no meeting-layer change)
- orchestrator/game.py (the Protocol is already injectable)

**Definition of done:**
- [ ] `SurrogateMeetingRunner` satisfies `isinstance(_, MeetingRunner)`; a full surrogate-driven `HeadlessGame` completes with valid artifacts — trigger echo validated, one ballot per living voter, and the cross-meeting belief fold consumes the result (asserted by test).
- [ ] The predicted-ballot path feeds the real `tally_ballots` with the explicit constants-home threshold; no re-implemented tally logic exists anywhere in `training/`.
- [ ] The GO/NO-GO bar is OWNER-RATIFIED (2026-07-09, mid-wave review Q1) and stated in the report and in code BEFORE training — population-relative on all three axes, no absolute constants (every absolute number in this project's history moved when the population changed: FO-6 64% → 26%; ceiling 65.1 → 70.6): **GO ⇔ held-out top-1 ≥ 0.75 × the honest ceiling MEASURED ON THE SAME scored population by the 15.11 harness (never the samples-set 70.6% figure) AND held-out top-1 > the corpus-re-baselined FO-6 logistic AND SKIP-vs-eject accuracy > the scored population's own `always_eject_baseline`** (on the corpus test split that trivial constant is ~0.82 — the samples-set 78.4% does not transfer). Pre-committed in the same breath: NO-GO ⇒ fallback (a) becomes the bake-off's training-time runner and the surrogate ships as a DIAGNOSTIC only (its fidelity report still lands; nothing trains against it). The verdict is reported against this bar with the held-out numbers from the 15.11 harness.
- [ ] The fallback path is exercised by test regardless of verdict: the training env runs under fallback (a) today, proving the bake-off cannot be blocked by a NO-GO.
- [ ] Surrogate inference is deterministic under a fixed weights artifact (double-run hash test); the fitted weights are COMMITTED under `training/artifacts/surrogate/` with a sha256 sidecar the 15.9 stamp schema can reference, and the bake-off reloads exactly that artifact (a round-trip test loads it and reproduces the reported fidelity numbers).
- [ ] The staleness cap is real code the bake-off consumes (exceeding it raises), with its unit and ownership pinned: a max-use integer committed beside the weights artifact, whose use-counter keys on the weights sha256 and is CUMULATIVE across a bake-off run — constructing a fresh runner instance never resets it. The re-grounding recipe (record fresh real-LLM meetings, rebuild the table, re-fit, re-measure) is documented step-by-step in the report.
- [ ] Fit/predict leakage is fenced by test: the predictor's side-channel into the 15.11 meeting table (the per-voter rows behind the meeting-collapsed `MeetingView`) reads label columns (`ballot_target`, `ejected_player_id`) ONLY for fit-side seeds; a committed test proves predict on a test meeting never touches a test row's labels, and fit never reads a row from outside the fit-side seed set.
- [ ] The report includes the surrogate's PREDICTED-ballot calibration (Brier/ECE of the predicted confidences vs whether the named target was ejected) as its own channel — the harness's committed `ballot_brier`/`ballot_ece` are the model-independent RECORDED-ballot reference and are never presented as surrogate calibration.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.surrogate.ballots.BallotPredictor
- training.surrogate.runner.SurrogateMeetingRunner

**Implementation hint:**

Keep the predictor simple and calibrated — a standardized multinomial logistic or tiny MLP over the
15.11 features is the determinism-safe default; gradient-boosted trees would need integer-threshold care
and are not worth it at this data size. `MeetingArtifacts(result=…, llm_calls=(), prompt_versions={})`
is the shape the orchestrator dereferences; a bare `MeetingResult` fails. Dead voters cast nothing:
derive the living roster from the trigger-time state the runner receives. The `run_tournament_eval`
keyword must be additive-optional with the default path byte-identical (existing balance-eval tests stay
green untouched).

**Integration risk:**

Model exploitation is the known failure (MBPO/Dreamer): a trained mover shifts the
sighting/contradiction distribution and the surrogate's blind spot — voice-driven convictions it
structurally cannot see — becomes the attack surface. The mitigations are all structural and land here:
the staleness cap, the pre-stated GO/NO-GO with the honest ceiling as denominator, re-grounding as a
documented operator recipe, and the bake-off's rule that final numbers are never surrogate-scored. Do
not weaken any of the four to make a verdict look better.

**Ready-to-paste prompt:** `agent_prompts/task-15-13-ballot-surrogate.md`

### Task 15.14 — Adversarial Goodhart probe: red-team the referee, and the shared ES core
**Branch:** `phase-15-goodhart-probe`
**Depends on:** 15.2, 15.7, 15.10
**Section refs:** audits/post-phase-14-ML-training-signal.md §3.2, §7.1.9 (the un-run charter guardrail); experiments/lab/ml-spike-charter.md (gap 3); experiments/lab/ml_spike/fo3_rubric_goodhart.py (the prior probe shape); audits/post-phase-14-ML-planning.md §12.2 (reward-hacking guards)
**Complexity:** Medium

Before the pause is allowed to use the 15.2 referee (with its baseline-3 floors from 15.7) as a
champion-selection gate, attack it: run evolution DIRECTLY on the referee score — the
deliberately-forbidden objective — and see what a genome can extract. This lands two artifacts. First,
the shared strict-typed ES core (`training/bakeoff/es.py`: seeded population loop, mutation, K-seed
fitness averaging, deterministic double-run behavior — ported from the spike's pure-Python loop, numpy
permitted) that 15.15/15.16 reuse, so every trainer in the phase shares one audited optimizer. Second,
the probe itself: ES on the full referee output (geomean × floors × supply floors) with the validity
gate as the only constraint, run on the training env with fake-provider meetings (and re-run under the
15.13 surrogate at 15.15 time, when meeting-controlled terms open to tactical pressure — the probe
report states this scoping explicitly). Every score gain is decomposed into which D-term or floor moved
and by what behavior; the deliverable is a trust verdict: exploits-found (each with the triggering
trajectory and a recommended floor/patch, routed to the PAUSE — this task does not edit the referee it
is attacking) or held-under-probe.

**Files in scope:**
- training/bakeoff/__init__.py (new)
- training/bakeoff/es.py (new: the shared ES core — 15.15 extends it behind its dependency edge)
- training/bakeoff/goodhart.py (new: the probe)
- training/reports/report-goodhart-probe.md (new: the trust verdict + exploit decompositions)
- tests/training/test_es.py (new)
- tests/training/test_goodhart_probe.py (new)

**Files NOT in scope:**
- eval/watchability.py (the referee is the SUBJECT under attack; patches route through the pause, never self-served here)
- training/env.py + training/rewards.py (consumed read-only)
- eval/validity.py (consumed as the constraint)

**Definition of done:**
- [ ] The ES core is deterministic under seed: two identical runs produce identical champion genomes and fitness traces (hash-pinned test), with K-seed fitness averaging and lexical tie-breaking built in.
- [ ] The probe runs a documented budget (generations × population × seeds, stated in the report) directly against the referee score on fixed seeds, validity-gated.
- [ ] Every fitness improvement in the probe's trace is decomposed to the moving D-term/floor with the behavioral cause named (e.g. meeting-farming D4, stall-to-clock D1) — no undecomposed gains in the report.
- [ ] The report ends in an explicit verdict: HELD (no exploit above a stated materiality bar) or EXPLOITS-FOUND (each with trajectory evidence + a recommended floor), and states the surrogate-path re-run obligation at 15.15.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.bakeoff.es.ESConfig
- training.bakeoff.goodhart.GoodhartProbeReport

**Implementation hint:**

FO-3 already showed tactical play cannot move meeting-controlled rubric terms under fake meetings — so
the expected attack surface here is the physically-reachable terms (D4 contest via meeting-farming is
the known-tiny one) and the supply floors themselves; a null result on the meeting-dependent terms is
expected and must not be reported as "referee safe" without the surrogate-path caveat. Chaotic fitness
needs K-seed averaging (the spike's check-2 lesson). Cap the probe's budget honestly — the point is
cheap insurance against laundering a degenerate champion as "watchable," not an exhaustive search.

**Ready-to-paste prompt:** `agent_prompts/task-15-14-goodhart-probe.md`

### Task 15.15 — The impostor bake-off: BC/DAgger, utility-scorer+ES, policy-net+ES, MAP-Elites
**Branch:** `phase-15-impostor-bakeoff`
**Depends on:** 15.8.1, 15.10, 15.13, 15.14
**Section refs:** audits/post-phase-14-ML-planning.md §5.2, §9 (the option vocabulary + paradigm comparison); audits/post-phase-14-ML-training-signal.md §4 (the objective spine: competence + anchor-KL + QD; referee as gate); agents/tactical/impostor_policy.py (_scored_targets :937-1009, the ladder :261); experiments/lab/ml_spike/check2_learnability.py + fo9_diversity.py (the ES priors)
**Complexity:** Integration

The wave's centerpiece: four training methods, one harness, one seed set, one report — so the pause
compares methods, not evaluation protocols. Entrants, all impostor-side, all trained and evaluated
against the baseline-3 substrate: (1) **BC/DAgger** from the FSM oracle — behavior-clone
`ImpostorPolicy.decide` on encoder-v2 features with DAgger corrections (the FSM is a free queryable
expert), reported against a pre-stated intent-agreement bar; this is the encoder-sufficiency test — if
v2 features cannot reproduce the scripted ladder, the encoder gaps are the finding; (2) **learned
utility scorer over FSM-proposed options + ES** — the conservative bounded path: keep the FSM's option
generation and replace exactly the `_scored_targets` ranking (isolation × (1−witness_risk) × cooldown,
lexical tie-break) plus the option-level choices (kill now / stalk-toward / vent-exit choice / cover /
fake-task / reposition-during-cooldown), structurally unable to emit illegal or off-menu actions; (3)
**direct masked policy net + ES** — the higher-ceiling path over the full masked intent space; (4)
**MAP-Elites** over the 15.8 behavioral descriptors with competence as cell quality — diversity as
measured archive coverage. Every ES/QD entrant optimizes the SAME fitness: the tactically-reachable
side-specific terms + potential shaping, with an anchor-KL penalty toward the frozen FSM (measured as
the anchor cross-entropy — the log-loss of the candidate's choice distribution at the FSM's
deterministic choice, the piKL-style penalty the hint names; a literal KL against a deterministic
anchor's delta distribution is degenerate); the validity gate and the 15.2
referee are SELECTION filters applied to candidates after training — never terms in any fitness. The
crew side stays the frozen scripted FSM throughout (no co-evolution this wave). Every candidate that
reaches the report runs the 15.10 determinism harness and the leak-test factory mode THROUGH ITS OWN
policy factory (the 15.10 `_IdleExploreAgent` reference wrapper runs no encoder and does not count); a
determinism-harness FAIL does not drop the row — it marks it experiment-tier and carries the full
`PolicyDeterminismReport` plus an N-repeat metric spread (the seam the 15.17 torch entrant reports
through); fitness may use
the 15.13 surrogate within its staleness cap, but every reported number is re-scored on a real meeting
path (fake-provider meetings on the fixed eval seed set — the frozen corpus test split,
`replays/ml_corpus/9p2i/splits.json` seed % 5 == 4). Also discharge the 15.14 obligation: re-run
the Goodhart probe under the surrogate meeting path and append the delta to the probe's findings in this
report.

**Files in scope:**
- training/bakeoff/harness.py (new: the entrant protocol, the fixed eval protocol, the report emitter)
- training/bakeoff/bc.py (new)
- training/bakeoff/utility_es.py (new)
- training/bakeoff/policy_es.py (new)
- training/bakeoff/map_elites.py (new)
- training/bakeoff/es.py (shared-core extensions — behind the 15.14 dependency edge)
- training/reports/report-impostor-bakeoff.md (new)
- training/reports/results-impostor-bakeoff.jsonl (new: the machine-readable per-entrant rows 15.18 consumes)
- training/artifacts/impostor/ (new: frozen candidate weights, float-hex JSON + sha256 sidecars)
- tests/training/test_bakeoff_harness.py (new)
- tests/training/test_bakeoff_methods.py (new: each entrant's train/eval loop on tiny budgets)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (the anchor and oracle is read-only — nothing ships into agents/ before the PAUSE)
- eval/ (gates consumed via the 15.1/15.2 JSON contracts)
- experiments/lab/ (the torch probe is 15.17)
- training/crew/ (15.16's parallel track)

**Definition of done:**
- [ ] One harness: every entrant trains and evaluates through `training/bakeoff/harness.py` on the same fixed eval seed set — the frozen corpus test split (`replays/ml_corpus/9p2i/splits.json`, seed % 5 == 4), asserted by a test — and entrants carry no private eval loops (ENFORCED, not asserted: a committed test AST-scans `training/bakeoff/{bc,utility_es,policy_es,map_elites}.py` for `eval.watchability`/`eval.validity` imports, the firewall-test pattern; the harness is the only module that computes reported metrics).
- [ ] Every entrant row in `results-impostor-bakeoff.jsonl` carries the full tuple: validity-gate pass, referee result (score distribution + floor-trip rate + supply floors), inner fitness (surrogate-scored AND real-rescored columns, both, where the two paths were used — divergence is data, never collapsed to one number), anchor-KL, impostor win rate + take-rate (reported, never gated), determinism-harness result (the double-run hash, or an explicit experiment-tier FAIL carrying the full `PolicyDeterminismReport` + N-repeat spread), leak-test pass (through the candidate's own factory), surrogate-staleness usage, and wall-clock.
- [ ] The BC entrant reports held-out intent agreement with the FSM against its pre-stated bar (≥0.90 top-1 unless the contract PR documents a different bar BEFORE training) and names the encoder gaps if it misses.
- [ ] The utility-scorer entrant consumes exactly the FSM's option set (a test enumerates the options on fixture states and pins the menu) — the bounded path is real, not aspirational.
- [ ] The MAP-Elites entrant reports archive coverage over the named descriptors + best-per-cell quality; single-objective entrants report their descriptor footprint for comparison.
- [ ] No unregularized champion: anchor-KL is computed for every reported candidate; candidates above the documented KL ceiling are flagged in the report, not silently dropped.
- [ ] The Goodhart probe re-run under the surrogate path invokes `run_goodhart_probe(meeting_runner_factory=…)` INCLUDING its forced single-tactic reachability sweep — the committed 15.14 ES budget alone only recovered to baseline (+1.7%); the sweep is what found the exploit — and reports the surrogate's ejection/SKIP rate alongside the verdict (an under-ejecting surrogate can hold the meeting-driven floors for the wrong reason, and a HELD must not be read as exploit-caught in that regime). The delta verdict vs the 15.14 baseline is appended.
- [ ] The report ends with a ranked recommendation + open risks FOR THE PAUSE — explicitly not a self-declared winner; every quoted number regenerates from the committed CLIs + jsonl.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.bakeoff.harness.BakeoffEntrant
- training.bakeoff.harness.BakeoffResult

**Implementation hint:**

Warm-start the ES entrants from the BC solution where shapes align (the spike's BC-then-ES lesson: BC
alone caps below FSM parity on a weak encoder; ES climbs from it). The anchor-KL is cheap in pure form:
sample states from rollouts, compare the candidate's choice distribution to the FSM's deterministic
choice (a log-loss against the anchor's action works as the piKL-style penalty at this scale). Respect
the 15.13 staleness cap in the training loop config, and log every surrogate use into the jsonl rows.
Tiny-budget CI tests train for a handful of generations on 1–2 seeds — the full runs are
operator-executed and their budgets recorded in the report ($0, CPU, hours-scale).

**Integration risk:**

Two failure modes. (a) Protocol drift between entrants — the single-harness rule exists because one
entrant evaluating on different seeds or a different meeting path silently un-ranks the whole
comparison; the harness owning all metric computation is the enforcement. (b) Surrogate exploitation —
a candidate that looks strong on surrogate-scored fitness and collapses on the real meeting path is the
expected shape of failure; the re-score-on-real-path rule plus the staleness cap are the guards, and the
report must show both numbers where they diverge. Also: keep every candidate's weights + config
committed under `training/artifacts/impostor/` with sha256 — the pause's finalist evaluation and any
Wave-2 productization must be able to reload the exact artifact.

**Ready-to-paste prompt:** `agent_prompts/task-15-15-impostor-bakeoff.md`

### Task 15.16 — The crew track: a learned scorer over observable crew options
**Branch:** `phase-15-crew-track`
**Depends on:** 15.10, 15.13, 15.14, 15.15
**Section refs:** audits/post-phase-14-ML-planning.md §4.1, §5.2 (crew FSM gaps + the observability blocker); audits/post-phase-14-ML-training-signal.md §3.2 (crew reward terms); agents/tactical/crewmate_policy.py (the ladder :343-423; EmergencyPacingTracker); experiments/lab/ml_spike/fo8_crew_buddy.py (the small-gain prior)
**Complexity:** Medium

The secondary track, run on 15.15's shared machinery (files disjoint from the bake-off; the harness +
ES core consumed strictly read-only — the 15.15 edge exists so the harness is present, not because
files collide): a learned utility scorer over a FIXED, observable-only crew option set — continue-to-task, buddy-toward the nearest
visible/belief-trusted group (co-presence + low own-suspicion keyed, never role — roles are hidden),
patrol-toward last-seen suspect, report, emergency (through the existing `EmergencyPacingTracker` gate
semantics, not bypassing them), repair, hold. Trained with the 15.14 ES core against the frozen scripted
impostor, anchored (KL) to `CrewmatePolicy`, evaluated under the 15.15 protocol shape
(gate/referee/fitness/determinism/leak) into its own report + jsonl. Task-ordering is EXPLICITLY OUT:
the packet exposes a single engine-fed `pending_task_id` and no owned-task set, so ordering is
un-observable — this track must not widen the observation surface; instead its report states the precise
surface ask (what field, what firewall review, what expected gain) as an input to the pause's
owner-gated decision. The honest prior is FO-8's small gain (buddy/task gate: +1 game vs the FSM) — the
deliverable is a clean measurement of what observable-option learning buys the crew, not a mandated win.

**Files in scope:**
- training/crew/__init__.py (new)
- training/env.py (build_action_mask emergency-intent canonicalization region ONLY — close the documented 15.8 exact-equality gap (`eval/leak_test.py:608-616`): the mask's emergency entry carries a default payload while the crew FSM stamps `reason='suspicion_accumulation'`/kill-witness, and `is_submission_legal` compares exact, so a scorer delegating the FSM emergency raises; a mask-legal crew emergency carrying the FSM's `reason` payload must validate as submission-legal; behind this task's 15.15 edge — 15.14/15.15 consume env.py read-only)
- training/crew/options.py (new: the observable option set + per-option features)
- training/crew/scorer.py (new: the learned scorer + training entry)
- training/reports/report-crew-track.md (new)
- training/reports/results-crew-track.jsonl (new)
- training/artifacts/crew/ (new: frozen candidate weights + sha256)
- tests/training/test_crew_options.py (new)
- tests/training/test_crew_scorer.py (new)

**Files NOT in scope:**
- agents/tactical/crewmate_policy.py (the anchor is read-only)
- observation/packet.py + observation/public_map.py (NO surface widening — the pause owns that decision)
- training/bakeoff/harness.py + training/bakeoff/es.py (consumed read-only; if the harness needs generalizing for crew, that change lands behind 15.15's edge, and this task documents the ask instead of editing)

**Definition of done:**
- [ ] The option set is proven observable-only: every per-option feature derives from the packet + the crew agent's own memory (a test sweeps committed-corpus packets; the leak-test factory mode passes for the crew wrapper).
- [ ] Emergency semantics preserved: the learned scorer routes emergency intent through the same `EmergencyPacingTracker` gate the FSM uses — a test proves the tracker's pacing/announce bookkeeping is untouched — AND the emitted emergency intent (with the FSM's `reason` payload) is proven `submission_legal` under `build_action_mask` by a button-room fixture (the 15.8 exact-equality gap this task's env.py region closes; today's `tests/training/test_env.py` emergency fixture only round-trips the mask's own default-payload object and cannot fail on it).
- [ ] The trained scorer vs the FSM crew is measured on the fixed eval seed set against the frozen scripted impostor: mis-eject-relevant deltas (meeting-trigger quality, correct-report rate), survival, task-completion pace, win rate — reported with gate/referee/determinism columns in the jsonl, same tuple shape as 15.15.
- [ ] Anchor-KL to `CrewmatePolicy` (the anchor cross-entropy — log-loss at the FSM's deterministic choice, as 15.15 defines it) reported for every candidate; the FO-8 prior is quoted and the measured delta stated against it.
- [ ] The crew report DISCLOSES the reward definition: `training/rewards.py`'s `patrol_coverage` measures co-location with an impostor's ACTUAL room — the engine-truth proxy is now the RATIFIED doctrine (owner, 2026-07-09, mid-wave review Q6: a belief-keyed term would reward belief manipulation; see the preamble), so no re-definition ask goes to the pause. The observable-only DoD above governs the POLICY's inputs, not the reward channel. In its place, ONE diagnostic is required: the report measures the correlation between earned coverage credit and the agent's own contemporaneous suspicion toward the shadowed player — if the trained crew's coverage is mostly UN-CUED (shadowing players it holds no suspicion about), the term is training crowding rather than patrol, and the pause revisits with that data.
- [ ] The report's final section is the crew-surface ask for the pause: the exact observation field proposed (owned-task set), the firewall/leak review it needs, and the expected-gain argument — with this track's measured ceiling as the evidence.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.crew.options.CrewOption
- training.crew.scorer.CrewOptionScorer

**Implementation hint:**

The crew reward terms are the tactically-reachable set from the training-signal doc: task progress,
survival, correctly-routed reports, buddy/patrol coverage (the engine-truth co-location proxy, per
the owner-ratified preamble doctrine) — through the 15.8 reward channel, plus the terminal win. "Belief-trusted group" keys on the crew agent's OWN
suspicion/trust floats (quantized, via the encoder) — the same information class that already reaches
crew tactics through the emergency gate; nothing role-derived. Files are disjoint from 15.15 by
construction; the harness and ES core are consumed strictly read-only, and any generalization the
harness needs for crew is documented as an ask, not edited here.

**Ready-to-paste prompt:** `agent_prompts/task-15-16-crew-track.md`

### Task 15.17 — The torch PPO+recurrent probe (experiment-tier, opt-in)
**Branch:** `phase-15-torch-probe`
**Depends on:** 15.8, 15.10, 15.15
**Section refs:** audits/post-phase-14-ML-training-signal.md §9 (the staged-escalation dependency posture); audits/post-phase-14-ML-planning.md §9 Option 3 (PPO/recurrent: strongest asymptotics, heavy costs); owner decision 2026-07-05 (torch as probe only; promotion is a pause decision)
**Complexity:** Medium

The owner's torch experiment, run where it cannot leak into the production posture: a PPO + recurrent
(GRU/LSTM) impostor-policy probe under `experiments/lab/torch_probe/`, executed via `uv run --with
torch` — torch never enters `pyproject.toml` dependencies or `uv.lock` this phase. The probe answers ONE
question for the pause: does gradient RL with real POMDP memory beat the pure-Python ES ceiling by
enough to justify torch's costs (dependency weight, cross-machine float determinism, CI story)?
Comparability is the design constraint: the probe trains through the SAME `TacticalRolloutEnv` and
encoder-v2 features, and evaluates through 15.15's COMMITTED harness protocol and fixed seed config,
consumed read-only (the 15.15 dependency edge exists so the protocol is real code the probe invokes,
never a hand-copied tuple shape or self-chosen seeds), reporting in the 15.15 metric-tuple shape —
with the honest exception that the determinism-harness hash is expected to FAIL for a torch policy, so
the probe reports a seeded-run variance story (N repeats, spread of every metric) instead of pretending.
It also measures the escape hatch: distillability — behavior-clone the torch policy into the pure-Python
inference net and report student-teacher agreement, so Wave 2 can take the capability without the
dependency if the owner wants it. The `experiments/lab/torch_probe/` directory joins the ml_spike mypy
exclusion (the pyproject exclude-regex edit is this task's ONLY pyproject touch — the dependencies
region is 15.8's).

**Files in scope:**
- experiments/lab/torch_probe/ (new: probe scripts + README; experiment-tier, mypy-excluded)
- experiments/lab/report-torch-probe.md (new)
- pyproject.toml (mypy exclude regex region only — dependencies untouched)
- tests/experiments/test_torch_probe_excluded.py (new: pins the exclusion + that no production package imports the probe)

**Files NOT in scope:**
- uv.lock (torch is NOT resolved into the project — `uv run --with` only)
- training/ (imported read-only; nothing ships into it)
- .github/ + CI workflow files (no CI job runs the probe)

**Definition of done:**
- [ ] The probe trains an impostor policy through `training.env.TacticalRolloutEnv` + `agents.tactical.features.TacticalFeatureEncoder` (same env, same features — comparability asserted in the report, with any deviation documented).
- [ ] Results are emitted through 15.15's committed harness protocol on its fixed eval seed config (the harness consumed read-only — asserted by the report naming the harness entrypoint + seed-config artifact it invoked), plus the reproducibility story: N seeded repeats with the spread of validity/referee/fitness/win-rate (no single-run claims).
- [ ] Distillability measured: a pure-Python student cloned from the torch policy, with student-teacher intent agreement reported against a bar PRE-STATED in the report before distillation (≥0.90 top-1 unless the report documents a different bar and why — mirroring the 15.15 BC bar discipline), and the student's own tuple row reported.
- [ ] A torch-free committed test binds the wiring: it drives the probe's entrant adapter with a tiny CPU stub policy and asserts it (a) constructs `TacticalRolloutEnv` + `TacticalFeatureEncoder` and (b) is accepted by the 15.15 harness's experiment-tier (determinism-FAIL-tolerant) row path — so `uv run pytest` exercises the comparability plumbing without torch installed.
- [ ] `pyproject.toml` mypy exclude covers the probe dir; `uv run mypy .` is green WITHOUT torch installed; the test pins that no production package imports the probe.
- [ ] The report ends with a promotion recommendation for the pause — promote / keep experiment-tier / retire — priced against dependency weight, determinism doctrine, and the measured gain (or its absence), with wall-clock + hardware documented.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Mirror the ml_spike posture: standalone scripts with `main()`, `sys.path` bootstrap acceptable, excluded
from strict typing, run by the operator with `uv run --with torch python experiments/lab/torch_probe/…`.
Masked action selection (the 15.8 mask) is mandatory — an unmasked PPO burns its budget on illegal
actions. Recurrence is the point of the probe (the POMDP memory the encoder carries explicitly, a GRU
carries latently) — if recurrent PPO cannot beat the utility-scorer+ES entrant on the same features,
that is a clean, valuable NO for torch promotion. Keep the run budget honest and documented; $0, local
CPU (or the operator's own GPU, documented).

**Ready-to-paste prompt:** `agent_prompts/task-15-17-torch-probe.md`

## The PAUSE

### Task 15.18 — The pause: mid-phase audit, the seven decisions, and authoring Wave 2
**Branch:** `phase-15-pause-audit`
**Depends on:** 15.12, 15.13, 15.15, 15.16, 15.17
**Section refs:** audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; tasks/post-phase-14-plan.md (the roadmap the decisions feed); owner decisions 2026-07-05 (deployment + torch deferred to this pause)
**Complexity:** Integration

The wave boundary the phase was designed around: measure, decide, then author Wave 2 from evidence
instead of forecasts. Inputs (all machine-readable, all reproducible by the committed CLIs):
`results-impostor-bakeoff.jsonl` + `results-crew-track.jsonl` + `report-torch-probe.md` (per-entrant
gate/referee/fitness/KL/determinism/cost), `report-ballot-surrogate.md` (fidelity vs honest ceiling +
verdict), `report-goodhart-probe.md` (+ the 15.15 surrogate-path re-run), the corpus MANIFESTs + gate
outputs, and the Wave-0 close audit (the funnel deltas the whole phase now stands on — including its
§5 watch items, which this audit must SETTLE, not re-flag: the 4p1i eject-happiness uptick
(report-meeting ejections 10 → 22, accuracy 0.923 → 0.808 at the 15.7 re-record) is adjudicated
variance-or-shift against the corpus's fresh 50-seed 4p1i evidence via the committed CLIs). Plus ONE fresh
measurement this task runs: the operator-run REAL-LLM finalist evaluation — the top 1–2 bake-off
candidates re-recorded on the canonical 50-seed 9p2i set against `Qwen/Qwen3-32B` (Featherless $0,
~2.5h per finalist), scored by `scripts/validity_gate.py` + `scripts/measure_baseline.py
--watchability --funnel`, so the method decision rests on at least one real-meeting-path measurement,
not only fake-provider/surrogate numbers. The RAW finalist recordings stay uncommitted working
artifacts (they do NOT replace or join `replays/samples/` or `replays/ml_corpus/`, and they are
re-recordable from the documented recipe); what IS committed is their measurement: the per-finalist
gate/referee/funnel CLI outputs land as `training/reports/results-finalist-eval.jsonl`, the artifact
every audit number traces to. The audit
(`audits/audit-phase-15-pause.md`) tabulates every entrant on the single protocol and records the SEVEN
owner decisions with rationale: (1) winning method + champion candidate; (2) deployment end-state —
opt-in factory beside the FSM default vs new default + baseline-4 re-record; (3) torch — promote / keep
experiment-tier / retire, incl. the distillation route; (4) Wave-2 co-evolution GO/NO-GO (scoped only if
GO, with the full stabilizer stack); (5) the crew observation-surface change (owned-task set) YES/NO;
(6) inference weight representation — float-hex vs int-quantized — plus an enumeration of every
determinism loosening now live; (7) the surrogate re-grounding cadence going forward. Then this task
AUTHORS the Wave-2 contracts into this file (IDs 15.19+, every validator rule honored: full contract
fields, scope-overlap edges, the CI tail), regenerates prompts, and replaces the end-of-phase
merge-criteria placeholder with the real criteria for the chosen deployment branch.

**Files in scope:**
- audits/audit-phase-15-pause.md (new)
- training/reports/results-finalist-eval.jsonl (new: the committed per-finalist gate/referee/funnel CLI outputs — measurement data, not code)
- tasks/phase-15.md (Wave-2 contracts + STATUS banner update + end-of-phase merge criteria)
- agent_prompts/ (mechanically regenerated task-15-* prompts for the new Wave-2 contracts — generator output, never hand-edited)

**Files NOT in scope:**
- training/ code + eval/ + agents/ + engine/ + orchestrator/ (measurement is read-only — the finalist jsonl above is CLI output data, not code; any referee patch the Goodhart findings demand becomes a Wave-2 contract, never a pause edit)
- replays/samples/ + replays/ml_corpus/ (untouched; finalist recordings live outside both)
- DESIGN.md + AGENT_IMPLEMENTATION.md (owner-side; any design amendment the decisions imply is recorded as an ask in the audit)

**Definition of done:**
- [ ] The audit tabulates every entrant (bake-off, crew, torch, distilled student) on the single metric tuple, with every quoted number regenerated from the committed CLIs/jsonl — zero hand-computed figures (each table cites its source artifact).
- [ ] The real-LLM finalist evaluation is run; its gate + referee + funnel results are committed as `training/reports/results-finalist-eval.jsonl` and quoted from there (the recording recipe — seeds, config, exact commands — documented in the audit for full re-derivation), and its divergence (if any) from the fake-provider/surrogate numbers is analyzed — the method decision explicitly cites it. The recipe names the Python seam (`run_tournament_eval(agent_factory=…, tactical_policy_stamp=…)` — `scripts/run_tournament.py` carries a stamp flag but NO agent-factory flag, so the stamp CLI alone cannot drive a learned policy), and the recorded games' `tactical_policy` stamp `weights_sha256` MUST equal the champion artifact's committed sha256 — the machine-checkable proof that the learned factory, not the FSM default wearing a champion label, produced the recorded bytes. Because the raw recordings stay uncommitted working artifacts, the proof must SURVIVE in the committed output: every `results-finalist-eval.jsonl` row carries the finalist's recorded five-field `tactical_policy` stamp (read back from the recording bytes at measurement time, never echoed from the launch config) plus the committed artifact sha it was verified against, so a post-15.18 reviewer re-checks the equality from the jsonl + the committed sidecar alone.
- [ ] All seven decisions are recorded with owner sign-off and rationale, including the NO paths (what was rejected and why).
- [ ] The Wave-2 contracts are authored into this file per the chosen branch, `uv run python scripts/validate_task_docs.py` + `uv run python scripts/generate_prompts.py --check` pass with the new contracts, and the STATUS banner + end-of-phase merge criteria reflect the decisions.
- [ ] The pause explicitly re-verdicts the referee: for each channel where EITHER probe run found an exploit, the recommended floor is contracted into Wave 2 before any champion selection uses the referee — "cleared" is available only for channels where neither run found an exploit (the 15.14 raw-geomean D2-separation exploit, 6.51 → 16.62, lands its conversion-coupled floor regardless of the composed referee's HELD). The SAME Wave-2 referee-hardening contract bundles the subject-AWARE observation-backing re-anchoring (owner-ratified 2026-07-09, mid-wave review Q2: parity was correct for 15.2's cross-implementation evidence, but a trained impostor can exploit subject-agnostic backing — utter a genuine vent sighting of X in the turn that accuses innocent Y and the Y-accusation counts "backed"): floors re-pinned under the subject-aware definition on the same bytes so relative gates stay sound, the old parity fixture kept as a frozen historical pin, landed before any champion selection leans on fine D2-conversion differences.
- [ ] Canary denominators follow the owner-ratified rule (2026-07-09, Q3): canaries are judged on the LARGEST same-substrate, validity-gated set available (today: the corpus — genuine-class conversion 34/52 = 0.654) with the 50-seed samples figure reported alongside for ladder continuity; the samples sets remain the byte-identity/provenance anchor. Corollary recorded in the decisions: if decision 2 lands on branch B, baseline 4 requires a corpus-scale companion record before its canaries mean anything at n≈13.
- [ ] Decision 6 (weight representation + determinism-loosening enumeration) records the owner-ratified libm posture (2026-07-09, Q4): no libm-free forward pass is demanded; instead the Wave-2 productization contract MUST gate on bit-exact equality of the numpy-trained and pure-Python-shipped forward passes over the committed float-hex weights (a test, not an architecture change); if decision 6 int-quantizes, a fixed-point forward pass makes tanh a table lookup and cross-host generation falls out nearly free — otherwise same-host generation scope is documented and accepted (replay byte-identity is untouched by libm either way).
- [ ] Provenance-durability convention (owner-ratified 2026-07-09, Q5), effective from this task onward: every operator record (the finalist recipe here, any baseline-4 or future corpus) creates an annotated git tag at the recording commit or back-fills the post-squash main sha into its MANIFEST; existing MANIFESTs are left as-is (byte-verification is the operative guarantee). The finalist recipe in this audit demonstrates the convention.
- [ ] The Wave-0 close audit's §5 watch items are settled by data, not carried forward: the 4p1i eject-happiness cell is re-measured on the corpus's 4p1i set (funnel + R-gate via the committed CLIs) with a PRE-REGISTERED adjudication — a two-proportion test (corpus-4p1i vs post-15.7 samples ejection accuracy) whose SHIFT verdict requires the 95% CI to exclude the compared value; if the CI excludes neither (the expected outcome at n≈33 ejections), the audit records UNDERPOWERED with the n rather than a judgment call; if a real shift, its Wave-2 implication (if any) is recorded in the decisions.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Model the audit on `audits/post-phase-14-pause.md` (label discipline, verdict-in-one-line, punch list)
and the decision block on Task 14.6's LOCKED-DECISION shape. The Wave-2 sketch at the bottom of this
file is the authoring skeleton — each bullet becomes a contract or is explicitly dropped with a reason.
When authoring contracts, re-read `scripts/_task_parser.py`'s rules (header em-dash, ID grammar,
contract field order, scope-overlap semantics, globally-unique public types) — the validator is the
gate, and the new prompts must be generator output.

**Integration risk:**

Self-certification is the trap this task exists to prevent — every number must trace to a committed
artifact, and the referee cannot bless a champion until its own red-team verdict is resolved. The second
trap is validator-invalid Wave-2 contracts: a malformed `tasks/phase-15.md` breaks
`validate_task_docs.py` for the WHOLE repo (the parser aggregates all phases), so the authoring step
must run the full check locally before the PR. Third: the finalist recordings must stay out of
`replays/samples/` and `replays/ml_corpus/` — provenance separation between "the canonical baseline,"
"the frozen training corpus," and "pause working artifacts" is what keeps every later claim
attributable.

**Ready-to-paste prompt:** `agent_prompts/task-15-18-pause-audit.md`

## Wave 2 — productize (contracts authored at the PAUSE per the recorded decisions, 2026-07-10)

Authored by Task 15.18 from `audits/audit-phase-15-pause.md` (the seven locked decisions). The
pause-era sketch mapped to contracts as follows — every bullet became a contract or is dropped here
with its reason: champion productization → 15.20; deployment branch A → 15.21 (decision 2: opt-in
factory); **deployment branch B — DROPPED** (decision 2 rejected the default flip this wave: the
referee that would bless a default is not yet hardened (15.19 lands the Goodhart floors), the
finalist evidence is one 50-seed real-LLM measurement, and branch B's baseline-4 cost includes the
Q3 corpus-scale companion record — re-evaluated at phase close / Phase 17); referee hardening →
15.19; **bounded co-evolution — DROPPED** (decision 4 NO-GO: no trustworthy $0 inner-loop meeting
model exists — the 15.13 surrogate is NO-GO/diagnostic-only and the fake provider mints no evidence
— so even the stabilized stack would optimize both sides against a meeting model neither side can
move; deferred to Phase 17 with the re-grounded surrogate); crew surface change → 15.22 (decision
5 YES); **torch decision execution — NO CONTRACT** (decision 3: keep the probe experiment-tier,
promotion declined, the Wave-2 torch track retired — nothing to execute; the findings are recorded
permanently in the pause audit and re-stated at close by 15.23); hand-off to Phase 16 — authored as
its own `tasks/phase-16.md` per the roadmap, never inside this file (the pause audit's findings are
its scoping inputs); phase close → 15.23.

### Task 15.19 — Referee hardening: conversion-coupled D2 separation + subject-aware observation backing
**Branch:** `phase-15-referee-hardening`
**Depends on:** 15.18
**Section refs:** audits/audit-phase-15-pause.md §4 (the per-channel re-verdict) + decision blocks; training/reports/report-goodhart-probe.md (the kill-lever D2-separation exploit, 6.51 → 16.62, and the recommended floor); training/reports/report-impostor-bakeoff.md §6 (the surrogate-path HELD-for-the-wrong-reason delta); audits/review-phase-15-midwave.md Q2 (the owner-ratified subject-aware re-anchoring, 2026-07-09); eval/watchability.py (`_observation_backed_conversion`, the per-baseline floor blocks)
**Complexity:** Medium

Land the two referee patches the pause contracted BEFORE any champion selection leans on the referee's
fine D2-conversion differences (the 15.21 deployment re-score and the 15.23 close-audit champion gate
both carry a dependency edge on this task). Patch 1, the **conversion-coupled D2 floor** (the 15.14
finding, exploited on the fake path regardless of the composed referee's HELD): gate the D2 separation
sub-term on backed conversion — separation without an ejection or a contradiction flag is suspicion
theater, not deduction — so the forced-kill trajectory (separation 0.20 → 0.84 with conversion pinned
at 0.00) can no longer lift `mean_score` 6.51 → 16.62; and document in the module docstring that
`mean_score` must NEVER be read without the supply-floor gate. Patch 2, the **subject-AWARE
observation-backing re-anchoring** (owner-ratified Q2): `_observation_backed_conversion` today counts
an accusation "backed" if the speaker's turn carries ANY grounded observation — a trained impostor can
utter a genuine vent sighting of X in the turn that accuses innocent Y and the Y-accusation counts
backed. Re-define backing as subject-aware (the grounded observation's subject must be the accused),
re-pin the per-baseline floors under the new definition ON THE SAME committed bytes (baseline-3
samples; the corpus figures reported alongside per the Q3 denominator rule), and keep the old
subject-agnostic parity fixture as a frozen historical pin (renamed, never deleted — 15.2's
cross-implementation evidence stays reproducible). Also close the 4p1i floor-degeneracy finding from
the pause audit: the 4p1i `witnessed_event_rate` floor is pinned to a one-event numerator (1/55 on the
samples), so the corpus-4p1i set FAILS it at 0.0 measured — rare-event floors whose baseline numerator
is ≤ 1 are marked advisory (reported, never referee-failing) with the rule documented and tested.

**Files in scope:**
- eval/watchability.py (the D2 conversion-coupling, the subject-aware backing definition, the re-pinned per-baseline floor blocks, the advisory rare-event floor rule)
- tests/eval/test_watchability.py (exploit-trajectory regression fixture, subject-aware backing tests, frozen subject-agnostic parity pin, advisory-floor tests)

**Files NOT in scope:**
- eval/meeting_quality.py (its gauges are consumed as-is; backing is computed inside eval/watchability.py)
- training/bakeoff/goodhart.py + training/reports/ (the probe and its findings are frozen evidence, never edited)
- scripts/measure_baseline.py (the CLI surface is unchanged — the fold's internals harden underneath it)

**Definition of done:**
- [ ] A synthetic exploit-trajectory fixture reproducing the 15.14 shape (high D2 separation, zero conversion, zero flags) scores ~0 on the D2 term under the hardened referee, with a regression test pinning it; the scripted-FSM baseline-3 sets still PASS the hardened referee end-to-end.
- [ ] Backing is subject-aware: a fixture where a speaker grounds a vent sighting of X while accusing Y counts the Y-accusation UNBACKED (test), and the old subject-agnostic fixture result is kept as a frozen, clearly-labeled historical pin.
- [ ] The per-baseline floor blocks are re-pinned under the subject-aware definition by re-measuring the SAME committed baseline-3 bytes with the committed CLIs, measured values in comments (corpus figures alongside per the Q3 rule); `scripts/measure_baseline.py --watchability` runs clean on all four committed sets with the new floors.
- [ ] Rare-event floors with a baseline numerator ≤ 1 (today: the 4p1i `witnessed_event_rate`, 1/55) are advisory — reported in the JSON but excluded from `supply_floors_passed` — and `replays/ml_corpus/4p1i` consequently PASSES the referee (its other gauges already clear); a test pins the advisory rule.
- [ ] The module docstring records the doctrine deltas: selection-only (unchanged), conversion-coupled D2, subject-aware backing, mean_score-never-without-floors, and cites the pause audit §4 as the re-verdict of record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Both patches live entirely in `eval/watchability.py` — `_observation_backed_conversion` is the backing
chokepoint and the D1–D4 composition is a few lines above the floor gate. Re-pin floors by RUNNING the
CLIs, never by editing constants freehand: the floor values are measured facts with the measurement in
a comment. Expect the subject-aware re-pin to LOWER `testimony_backed_conversion` floors (fewer
accusations count backed under the stricter definition) — direction is a finding, not a failure; what
matters is that relative gates stay sound because candidate and baseline are measured under the same
definition. The frozen parity pin should be a renamed test asserting the OLD definition's value on the
same fixture, marked as historical.

**Ready-to-paste prompt:** `agent_prompts/task-15-19-referee-hardening.md`

### Task 15.20 — Champion productization: `agents/tactical/learned/`, the pure-Python forward pass
**Branch:** `phase-15-champion-productization`
**Depends on:** 15.18
**Section refs:** audits/audit-phase-15-pause.md decisions 1 + 6 (champion = `utility-es`; float-hex retained; the Q4 bit-exact cross-implementation gate); training/artifacts/impostor/utility-es/ (the committed champion artifact, sha256 `6d327dcb…`); training/bakeoff/utility_es.py (the training-side reference the shipped pass must equal bit-exactly — itself pure-Python `math.fsum`; the Q4 ruling's "numpy-trained" is shorthand for training-side); training/bakeoff/harness.py::build_candidate_factory (the wrapper pattern being productized); tests/test_firewall.py (the no-numpy/torch-under-agents/ doctrine)
**Complexity:** Integration

Promote the pause's champion — the `utility-es` learned utility scorer over FSM-proposed impostor
options — into production inference: a new `agents/tactical/learned/` package holding (a) the champion
weights as a committed float-hex artifact + sha256 sidecar, value-identical to
`training/artifacts/impostor/utility-es/weights.json` (a test pins byte equality of the weights payload
and sha equality with the training-side sidecar); (b) a pure-Python forward pass — the 19-weight linear
scorer over the `impostor-option-features-v1` option-feature basis, ported from
`training/bakeoff/utility_es.py` with NO numpy/torch import (the champion's pass is a `math.fsum`
linear score; it contains no transcendental, so the decision-6 libm scope note is discharged by
construction); (c) `build_learned_agent_factory()` beside the scripted default — impostors run the
learned scorer, crew delegate to the FSM, meeting protocol forwarded to the wrapped `TacticalAgent`
exactly as `build_candidate_factory` does today, and the factory exposes its five stamp fields
(policy_id `utility-es`, method, encoder `impostor-option-features-v1`, the committed sha, the anchor)
as PLAIN STRINGS on an engine-free local record — importing `orchestrator.replay`'s
`TacticalPolicyStamp` from `agents/` would chain `agents → orchestrator → engine` and break the
firewall contract, so the real stamp object is constructed by 15.21's CLI in `scripts/`, which may
import orchestrator freely. The scripted FSM stays in-tree untouched as the
default, the anchor, the BC oracle, and the fallback. The Q4 gate is the task's spine: a committed test
drives BOTH implementations — the training-side scorer and the shipped pure-Python pass — over the
committed weights across a recorded decision stream (fixed seeds, full option menus) and asserts
BIT-EXACT equality of every score and every chosen intent; plus the full 15.10 acceptance stack through
the learned factory (determinism harness double-run, leak-test factory mode, firewall test extension).

**Files in scope:**
- agents/tactical/learned/ (new package: forward pass, weights loader + committed weights artifact + sha256 sidecar, factory)
- tests/agents/test_learned_policy.py (new: forward-pass unit tests, weights/sha parity pins, the Q4 bit-exact cross-implementation test)
- tests/training/test_learned_factory_acceptance.py (new: determinism-harness + leak-test runs through `build_learned_agent_factory()`)
- tests/test_firewall.py (extension region: `agents/tactical/learned/` explicitly swept by the no-numpy/torch check)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py + crewmate_policy.py (the FSM default is untouched — anchor, oracle, fallback)
- training/bakeoff/ (the numpy reference is consumed read-only by tests; porting means re-implementing, not importing, under agents/)
- training/artifacts/ (the training-side artifact is the frozen source of truth; the agents-side copy pins to it by test)
- orchestrator/game.py + scripts/ (the CLI/config selection surface is 15.21's)

**Definition of done:**
- [ ] `agents/tactical/learned/` imports nothing from `engine/`, `training/`, numpy, or torch (import-linter + the extended firewall test prove it), and `uv run python -c "import agents.tactical.learned.factory"` succeeds on a bare tree.
- [ ] The committed agents-side weights artifact is value-identical to `training/artifacts/impostor/utility-es/weights.json` and its sha256 sidecar equals the training-side sidecar (`6d327dcbde940a5ee1bb4f9e22ff91fbbc4d74c0ddb33797043fdff69fef71d0`) — both pinned by test.
- [ ] The Q4 bit-exact gate: over the committed float-hex weights and a fixed recorded decision stream, the training-side scorer and the shipped pure-Python pass produce bit-identical float64 scores and identical chosen intents (a test, not an architecture change — the owner-ratified libm posture, whose "numpy-trained" reads training-side: the reference is itself pure-Python `math.fsum`).
- [ ] The learned factory passes the 15.10 determinism harness (double-run hash equality over the (feature, score, intent) stream plus frozen-policy full-game state-hash equality) and the leak-test factory mode through `build_learned_agent_factory()` itself.
- [ ] The factory's stamp accessor returns the five stamp fields (policy_id, method, encoder_version, weights_sha256, anchor_policy) as plain strings on an engine-free record, with `weights_sha256` equal to the committed sidecar digest — 15.21 constructs the real `TacticalPolicyStamp` from them — so the recording surfaces cannot mis-stamp.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- agents.tactical.learned.forward.LearnedImpostorScorer
- agents.tactical.learned.factory.build_learned_agent_factory

**Implementation hint:**

The champion is deliberately the SMALL one: 19 float64 weights over 18 option features + bias, linear,
no activation — the reference forward pass is `math.fsum(weight*feature for …) + bias` per option
(`training/bakeoff/utility_es.py::_score`) and an argmax with the menu's deterministic tie-break. Port
the accumulation VERBATIM: `math.fsum` is correctly rounded and order-independent, so the bit-exact
hazard is not summation order — it is substituting a naive `sum()` loop (or numpy) for `fsum`, which
diverges in the last ULP. Two porting snags the faithful port must handle: (a) the reference module's
one live `engine.world` import feeds only `_sabotage_kinds`, which `enumerate_options` immediately
discards — drop it, or the firewall contract breaks; (b) the argmax tie-break uses
`training.bakeoff.harness.intent_key` (a pure `ActionIntent.model_dump` serialization) — reimplement it
agents-side, don't import it. The 18 feature names are in the committed `config.json`. Mirror
`build_candidate_factory`'s wrapper pattern (wrap the real `TacticalAgent`, override the impostor
intent, `__getattr__`-forward the meeting protocol) rather than inventing a new agent class.

**Integration risk:**

The one real hazard is silent divergence between the two forward passes — an `fsum` swapped for a
naive sum, a float32 intermediate, a quantization mismatch in a feature — which the Q4 bit-exact test
exists to make loud.
Keep the agents-side artifact a COPY pinned by test, not a cross-package import: `agents/` importing
`training/` would breach the dependency posture the firewall enforces. The determinism harness and leak
test must run through the REAL factory (`build_learned_agent_factory()`), not a test double — the
15.15 lesson that acceptance through one's own factory is what makes the result transferable.

**Ready-to-paste prompt:** `agent_prompts/task-15-20-champion-productization.md`

### Task 15.21 — Deployment, branch A: the opt-in learned factory across the recording/eval surfaces
**Branch:** `phase-15-optin-deployment`
**Depends on:** 15.19, 15.20
**Section refs:** audits/audit-phase-15-pause.md decision 2 (branch A locked; branch B's rejection rationale) + the finalist recipe (the seam this task turns into a CLI); orchestrator/game.py (the `agent_factory` seam); scripts/run_tournament.py (the stamp flag that today has no factory counterpart); tasks/phase-15.md 15.9 (the provenance stamp this task auto-wires)
**Complexity:** Medium

Make the champion selectable without a Python driver — the deployment end-state decision 2 locked:
opt-in, fully reversible, `replays/samples/` byte-untouched. `scripts/run_tournament.py` gains an
`--agent-factory {fsm-default,learned-champion}` flag (default `fsm-default`, byte-identical behavior
when absent): `learned-champion` builds `agents.tactical.learned.factory.build_learned_agent_factory()`
and AUTO-STAMPS the recording with a `TacticalPolicyStamp` constructed from the factory's five
plain-string stamp fields (the construction lives here in `scripts/`, which may import
`orchestrator.replay`; the factory itself stays engine-free per 15.20) — an explicit
`--tactical-policy-stamp` contradicting the SELECTED factory's stamp is rejected loudly in BOTH
directions (`learned-champion` + an FSM label, and `fsm-default` / the flag omitted + a non-FSM
label; the second direction is the owner-ratified PR-#248 review amendment, 2026-07-10, retiring the
15.9 champion-JSON surface on the FSM path that the auto-stamp obsoleted), so a learned recording can
never carry an FSM label or vice versa (the 15.18 finalist-eval
proof, `stamp.weights_sha256 == committed sidecar`, becomes impossible to forget). `run_tournament_eval`
itself is unchanged (the seam already exists); this is CLI plumbing + the mis-stamp guard + tests. The
spectator path needs no change: recordings carry the stamp, `api/replay_loader.py`'s 15.9 policy guard
already distinguishes them, and the canonical samples stay FSM-stamped and byte-identical.

**Files in scope:**
- scripts/run_tournament.py (the `--agent-factory` flag, the auto-stamp wiring, the contradiction guard)
- tests/scripts/test_run_tournament_agent_factory.py (new: flag default byte-identity, auto-stamp correctness, contradiction rejection)

**Files NOT in scope:**
- eval/balance_eval.py (the `agent_factory` kwarg already exists — no seam change)
- agents/tactical/learned/ (15.20's artifact, consumed as-is)
- replays/samples/ + replays/ml_corpus/ (byte-untouched — the whole point of branch A)
- api/ (the 15.9 policy guard already serves stamped recordings)

**Definition of done:**
- [ ] `scripts/run_tournament.py` without the flag is byte-identical in behavior to today (default `fsm-default`; a test pins the parse + the default factory path) — with ONE owner-ratified exception (PR-#248 review amendment, 2026-07-10): an explicit `--tactical-policy-stamp` contradicting the FSM default without `--agent-factory learned-champion` is rejected rather than recorded (the vice-versa mis-stamp guard).
- [ ] `--agent-factory learned-champion` records games whose read-back stamp (via `orchestrator.replay.read_tactical_policy_stamp`) equals the `TacticalPolicyStamp` constructed from the learned factory's plain-string stamp fields, with `weights_sha256` equal to the committed sidecar digest — asserted from recorded bytes in a fake-provider test recording, never from the launch config.
- [ ] Passing `--agent-factory learned-champion` together with a contradicting `--tactical-policy-stamp` exits non-zero with a named error; `fsm-default` plus the explicit FSM stamp remains accepted (back-compat); `fsm-default` (or the flag omitted) plus an explicit stamp contradicting the FSM default likewise exits non-zero with the differing field named (the vice-versa direction, same PR-#248 amendment).
- [ ] The module docstring records the decision-2 posture: opt-in beside the FSM default, samples untouched, default flip re-evaluated at close/Phase 17 behind the hardened referee + a corpus-scale companion record (the Q3 corollary).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Mirror the `--tactical-policy-stamp` flag's plumbing one block below it. The factory choice maps to a
tiny registry dict `{"fsm-default": build_default_agent_factory, "learned-champion":
build_learned_agent_factory}` resolved at parse time; the auto-stamp reads the learned factory's
plain-string stamp fields (15.20's DoD guarantees they match the sidecar) and constructs the
`TacticalPolicyStamp` here, so this task never hard-codes a sha. The contradiction guard compares the
resolved stamp against an explicitly-passed one field-by-field and names the differing field in the
error. The edge on 15.19 is sequencing, not file-driven: the champion-recording CLI should not ship
before the referee that will judge its recordings is hardened.

**Ready-to-paste prompt:** `agent_prompts/task-15-21-optin-deployment.md`

### Task 15.22 — Crew owned-task surface: the `SelfView` widening + the gate-valid crew retrain
**Branch:** `phase-15-crew-owned-tasks`
**Depends on:** 15.18, 15.19
**Section refs:** audits/audit-phase-15-pause.md decision 5 (YES, with the four-item review) ; training/reports/report-crew-track.md §5 (the unmeasured gate-valid ceiling) + §7 (the surface ask this task lands); observation/packet.py (`SelfView`, the privileged self channel); observation/service.py (the packet assembly this widening must scope); eval/leak_test.py (the suite the new field extends); DESIGN.md §1.3 (the observation firewall this rides behind)
**Complexity:** Integration

Execute decision 5: widen the crewmate's observation surface by exactly one self-channel field and
re-measure the crew track's gate-valid ceiling on it. Part 1, the surface (the 15.16 §7 ask, four-item
review honored): `SelfView` gains `owned_task_ids: tuple[TaskId, ...]` — the recipient's OWN unfinished
task instances as map task ids, assembled in `observation/service.py` strictly from the recipient's own
engine-side task state (never another player's, never impostor fake-task state — an impostor's view
carries its camouflage task ids exactly as `pending_task_id` does today, so the field leaks no role
bit); the leak suite gains the owned-task assertions (no cross-player task ids anywhere in any packet;
the field's byte shape is stable and versioned by the existing packet discipline); committed v4/v5
transcripts and all committed replays still parse and byte-verify (additive field, default-empty for
reconstruction of old bytes). Part 2, the retrain (the §5 ceiling measurement, run under the SAME
protocol shape as 15.16): re-run the crew utility-scorer ES with (a) the widened option basis —
nearest-of-N owned-task selection and same-room batching features over `owned_task_ids` — and (b) the
FO-8-style interrupt-preserving constraint the pause scoped: the `report` interrupt is NOT suppressible
by the learned scorer (a body sighting always routes to report, exactly the FSM's interrupt semantics),
so the 15.16 failure mode — win-by-meeting-starvation — is structurally unreachable and the gate-valid
ceiling finally gets a number. Evaluated under the 15.15 protocol (gate / hardened 15.19 referee /
fitness / anchor-CE / determinism / leak), reported in the same tuple shape to its own report + jsonl.
Crew champion adoption is NOT a goal of this task: the deliverable is the surface + the honest
gate-valid measurement; any crew deployment is a phase-close/Phase-17 call on this task's numbers.

**Files in scope:**
- observation/packet.py (`SelfView.owned_task_ids` — additive, engine-free)
- observation/service.py (own-task assembly + the impostor-camouflage scoping)
- eval/leak_test.py (owned-task leak assertions region)
- training/crew/options.py (owned-task option features + the interrupt-preserving constraint)
- training/crew/scorer.py (basis widening only — the ES loop is 15.14's core, consumed as-is)
- training/reports/report-crew-owned-tasks.md (new) + training/reports/results-crew-owned-tasks.jsonl (new)
- tests/observation/test_packet_owned_tasks.py (new) + tests/training/test_crew_owned_tasks.py (new)

**Files NOT in scope:**
- agents/tactical/ (the crew FSM and the learned impostor package are untouched; this is a training-track measurement over a widened surface)
- engine/ (task state is already engine-side; the widening is packet-assembly only)
- meetings/ (no meeting-layer change — one layer per baseline)
- replays/ (committed bytes untouched; old replays reconstruct with the default-empty field)

**Definition of done:**
- [ ] `SelfView.owned_task_ids` carries exactly the recipient's own unfinished map task ids; an impostor's packet carries its camouflage set (no role bit); the leak suite proves no packet ever contains another player's task ids, and all committed replays still byte-verify bare.
- [ ] The interrupt-preserving constraint is structural: a test proves the learned scorer CANNOT select away from `report` when a body is visible (the option is not offered for suppression, mirroring the FSM interrupt), and the retrained candidate's games consequently cannot reproduce the 15.16 meeting-starvation validity failure.
- [ ] The retrain reports in the 15.15 tuple shape (gate / referee / fitness / anchor-CE / determinism hash / leak) on the frozen corpus test split, referee scored under the HARDENED 15.19 definition, with the crew-fsm-baseline re-measured through the identical protocol as the comparator row.
- [ ] The report states the gate-valid ceiling finding — the win-rate/fitness delta that survives the validity gate and the hardened referee — and the task-pace cell (tasks/100 ticks) that decision 5 predicted the owned-task basis would move, each cited to the jsonl.
- [ ] The report ends with the deployment posture: no crew default change in this phase; the numbers are Phase-17 scoping inputs.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Public types introduced:**
- training.crew.options.OwnedTaskOptionBasis

**Implementation hint:**

The four-item review from the 15.16 §7 ask is the checklist: (1) `ObservationService` scoping — the
field is assembled from the recipient's own task state only; (2) leak-suite extension — assert absence
of foreign task ids in EVERY packet field, not just the new one; (3) byte-shape discipline — additive
Pydantic field with a default, so old bytes parse; (4) the encoder note — the crew option basis
consumes the field training-side (`crew-option-features` bumps its version string); the production
encoder (`agents/tactical/features.py`) is NOT touched this task. For the constraint, remove `report`
from the scorer's selectable set rather than penalizing it — structural unreachability, not a reward
term (the Goodhart lesson). Expect the honest outcome to be smaller than 15.16's 0.6 win rate — that
number was bought with the starvation exploit; the gate-valid delta is the real measurement.

**Integration risk:**

Two hazards. First, the leak surface: `owned_task_ids` is the first packet widening since the firewall
audit — the impostor-camouflage path must be scoped so the field is indistinguishable between roles
(the packet already solves this for `pending_task_id`; mirror it exactly). Second, byte-compatibility:
the additive field must default-parse for every committed replay and transcript — run the full
byte-verification walk locally before the PR, because a shape error here fails 100 committed samples at
once.

**Ready-to-paste prompt:** `agent_prompts/task-15-22-crew-owned-tasks.md`

### Task 15.23 — Phase close: gates on the shipped end-state, the close audit, the banner flip (operator-run, $0)
**Branch:** `phase-15-close`
**Depends on:** 15.19, 15.20, 15.21, 15.22
**Section refs:** audits/audit-phase-15-pause.md (the decisions this close verifies + the finalist recipe §3.1 re-run here through the CLI); tasks/phase-14.md 14.12 + audits/audit-phase-14-close.md (the close-audit pattern); audits/review-phase-15-midwave.md Q3 (corpus canary denominators) + Q5 (the provenance-durability convention this record follows)
**Complexity:** Integration

Close the phase on the shipped branch-A end-state. Record ONE fresh champion evaluation on the
canonical 50-seed 9p2i set against the real provider — now through the committed CLI
(`scripts/run_tournament.py --agent-factory learned-champion`, the 15.21 surface; no Python driver
needed anymore) — as an uncommitted working artifact per the pause's provenance separation, with the
Q5 convention honored (annotated tag at the recording commit, or the sha back-filled into the committed
measurement rows). Score it with the committed CLIs — validity gate, R-gate, the HARDENED 15.19
referee, funnel — and commit the measurement as `training/reports/results-champion-close.jsonl` (the
same row shape as `results-finalist-eval.jsonl`: the five-field stamp read back from the recording
bytes + the committed sidecar sha it was verified against). Write
`audits/audit-phase-15-close.md`: the gates re-run green on HEAD, the champion recording PASSES the
validity gate + the hardened referee (this is the one PASS-bar of the close; a failure here pauses for
an owner call rather than shipping), the R-gate and funnel deltas vs baseline 3 reported as FINDINGS,
canaries judged on the corpus denominators with the 50-seed figures alongside (Q3), every committed
replay byte-verified bare, provenance verified end-to-end (stamp + MANIFEST + sha equality), the torch
disposition (decision 3) re-stated as permanent record, and the Phase-16 hand-off inputs (v5
vent-elicitation uptake, the residual zero-flag channel, the funnel deltas) restated for the
`tasks/phase-16.md` author. Flip the STATUS banner to CLOSED with the end-state, the champion identity
+ sha, and the close-audit pointer.

**Files in scope:**
- audits/audit-phase-15-close.md (new: the close finding)
- training/reports/results-champion-close.jsonl (new: the committed champion-close measurement rows — CLI output data, not code)
- tasks/phase-15.md (STATUS banner flip region only)

**Files NOT in scope:**
- replays/samples/ + replays/ml_corpus/ (byte-untouched — branch A ships no baseline 4; the close recording is an uncommitted working artifact)
- eval/ + agents/ + training/ code (the close measures; any defect it finds becomes a Phase-16/17 contract, never a close edit)
- README.md (the samples provenance paragraph still describes baseline 3, which is still the canonical truth under branch A)

**Definition of done:**
- [ ] The champion close recording exists per the documented recipe (seeds 0–49, 9p2i, `Qwen/Qwen3-32B`, `--agent-factory learned-champion`), its read-back stamps are uniform with `weights_sha256` equal to the committed sidecar digest, and the Q5 provenance convention is demonstrably followed (tag or back-filled sha named in the audit).
- [ ] `training/reports/results-champion-close.jsonl` carries the full gate/core/referee/funnel CLI outputs + the read-back stamp + the committed sha it was verified against; every number the audit quotes traces to it or to the other committed artifacts (zero hand-computed figures).
- [ ] The champion recording PASSES the validity gate and the hardened referee — the close's one pass-bar; the R-gate, funnel deltas vs baseline 3, and canaries (corpus denominators, samples alongside) are reported as findings.
- [ ] Every committed replay byte-verifies bare on the close HEAD (`bash scripts/verify_samples.sh` + the corpus verification), and provenance is verified end-to-end (stamps, MANIFESTs, sidecar shas).
- [ ] The torch disposition, the co-evolution NO-GO, and the surrogate re-grounding cadence (decisions 3, 4, 7) are re-stated as the permanent close record, and the Phase-16 scoping inputs are handed off explicitly.
- [ ] The STATUS banner reads CLOSED with the end-state, champion identity + sha, and the close-audit filename.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Model the audit on `audits/audit-phase-14-close.md` (verdict-first, per-gate table, findings vs pass
bars kept separate) and reuse the pause's scoring shape verbatim — the close row is the finalist row
re-recorded through the 15.21 CLI on the hardened referee. The one deliberate asymmetry vs 14.12: no
re-record of the canonical sets (branch A), so there are NO byte-coupled test re-pins in this task; if
the close measurement disagrees with the pause's finalist numbers beyond seed noise, that is a FINDING
for the audit, not a reason to re-run until it agrees.

**Integration risk:**

Two ways this close can lie. First, self-agreement laundering: the close recording uses the same seeds
as the pause's finalist eval, so silently swapping in the pause's cached numbers would be invisible —
the audit must name its own recording timestamp + tag and quote only `results-champion-close.jsonl`.
Second, the pass-bar inversion: the hardened referee landing in 15.19 means the close referee is
STRICTER than the one the finalists were measured under; a champion that passed at the pause may fail
at close, and that outcome pauses for an owner call — it is the exact scenario the referee-before-
selection ordering exists to catch, not a defect in the close.

**Ready-to-paste prompt:** `agent_prompts/task-15-23-phase-close.md`
