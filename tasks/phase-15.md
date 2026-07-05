# Phase 15 — Machine-learned tactical policies between meetings

> **STATUS: AUTHORING (2026-07-05).** Wave 1 + the PAUSE (Tasks 15.1–15.13) are contracted below and
> dispatchable. Wave 2 exists only as a prose sketch at the bottom of this file; its task contracts are
> authored BY Task 15.13 at the mid-phase pause, once the bake-off results and the owner's deployment
> decision exist (the Phase-7 precedent: later waves' contracts are appended only after earlier waves
> clear their gate).

Goal: give the agents machine-learned intelligence in the deterministic, LLM-free layer BETWEEN meetings —
kill timing, witness avoidance, cooldown stalking, cover/vent play, buddy/patrol movement — replacing or
augmenting the scripted FSMs in `agents/tactical/`. The LLM meeting layer is out of scope and stays frozen.
Phase 14 closed on baseline 2 (`replays/samples/{9p2i,4p1i}`, `Qwen/Qwen3-32B` Featherless $0,
`qwen3_32b.v4`, all five substrate levers unconditionally ON — `audits/audit-phase-14-close.md`) with the
tactical layer named as deferred structural work, and DESIGN.md §12 has rostered "Reinforcement learning
for tactical policies" since the MVP. The substrate is verified ML-ready: a learned policy is a drop-in
`agent_factory` (`orchestrator/game.py:93`, consumed at `:1447-1454`) with zero engine edits, replay
reconstruction re-feeds recorded actions and never re-invokes policies (so committed replays stay
byte-identical regardless of inference floats), and the prior feasibility spike
(`experiments/lab/ml_spike/`) proved injection, determinism, and $0 CPU self-play. What is NOT ready —
verified, not assumed — is the measurement-and-signal layer: the "validity gate" and "R-gate" the Phase-14
close audit cites by filename exist only as audit prose (`scripts/validity_gate.py` and
`scripts/measure_baseline.py` are committed by NO task in phases 0–14; `eval/` has no CLI entrypoint at
all), the interestingness referee is lab-tier and calibrated to baseline 1, and the spike's cheap-fitness
linchpin (the FO-6 physical suspicion-rank surrogate, reported top-1 64%) REGRESSED to top-1 26% / top-2
43% on the committed baseline-2 corpus. Wave 1 therefore builds the signal, the harness, the data, and a
rebuilt meeting surrogate FIRST, then runs a multi-method training bake-off; the PAUSE picks the winner on
measured numbers; Wave 2 productizes it.

The training-signal doctrine (from `audits/post-phase-14-ML-training-signal.md`, ratified by the owner
2026-07-05 — every Wave-1 contract below is shaped by it): the one word "R-score" is split into THREE
separate committed artifacts with three different jobs, and they are never conflated. (a) The only thing
any optimizer ever maximizes is the **tactically-reachable fitness** — measurable, side-specific competence
computed from engine events (impostor: resolved kills, un-witnessed-ness via `Killed.witnesses`, survival,
meetings survived, the win as terminal sparse reward; crew: task progress, survival, correctly-routed
reports, buddy/patrol coverage of last-seen suspects) plus potential-based shaping (policy-invariant, Ng
1999) plus a KL penalty toward the scripted-FSM **anchor** (the piKL/CICERO pattern: legibility comes from
staying near a reference that already produces contested, watchable play — never from scoring
"interestingness"). (b) The **HARD validity gate** and (c) the **selection referee** (data-grounded
evidence-supply floors + the D1–D4 floor-gated geomean) are applied AFTER training to accept or reject
champions, and are never rewards — "watchability" is not a trained metric anywhere in this phase. The
deepest known risk is a STRONG learner, not a weak one: a perfect-stealth impostor produces no flags, the
meetings starve of testimony, and the deduction game un-makes itself (the crew's entire deduction signal is
"the impostor was seen where it shouldn't be" — 112/112 committed contradictions are `alibi_vs_sighting`).
The gate/referee/anchor stack exists precisely to make that outcome un-selectable, and Task 15.9 red-teams
the referee itself before the pause is allowed to trust it.

Locked decisions (owner, 2026-07-05):
- **Dependency posture:** `numpy` is allowed as a pinned dependency for the training/surrogate core (the
  new `training/` package). `torch` is allowed ONLY as an experiment-tier probe under `experiments/lab/`
  via `uv run --with torch` — it does NOT enter `pyproject.toml`/`uv.lock` this wave; promotion to a real
  dependency is a PAUSE decision, taken only if the probe shows a large measured gain. Determinism may be
  loosened in small, documented, TRAINING-ONLY paths (e.g. the 15.3.1 hash fast path) when the project is
  better off for it; production inference and everything replay/recording-adjacent stays byte-deterministic.
  Production inference under `agents/` is pure-Python (no numpy/torch import — enforced by a firewall test
  and a new import-linter contract); candidate weights are float-hex JSON in Wave 1, with int-quantization
  decided at the PAUSE.
- **Watchability contract:** the gates ARE the contract. Any impostor win-rate movement from genuinely
  smarter tactical play is acceptable provided the validity gate and the selection referee pass (DESIGN.md
  §"balance is a finding, not a failure"). The referee is selection-only, never a reward.
- **Deployment end-state:** whether the champion ships as an opt-in factory beside the FSM default, or
  becomes the new default with a baseline-3 re-record, is DECIDED AT THE PAUSE. Both end-states are carried
  as Wave-2 options below; neither is presumed by any Wave-1 contract.
- **Sides:** both sides train in Wave 1; the impostor is the primary/deeper track (the bake-off compares
  methods on it), the crew track applies the shared machinery once in parallel. Crew task-ordering is
  EXCLUDED from Wave 1: the crewmate's set of owned unfinished tasks is not observable today (the packet
  carries a single engine-fed `pending_task_id`), so learning task order is structurally impossible without
  an observation-surface change — that change is owner-gated at the PAUSE, not smuggled in.
- **Meeting surrogate doctrine:** the no-LLM meeting model is a per-voter BALLOT predictor whose predicted
  ballots feed the REAL deterministic tally (`meetings/voting.py::tally_ballots`) — never a per-meeting
  ejection classifier (the FO-6 always-SKIP collapse). It is a moving target: it is re-calibrated after any
  mover or meeting-layer change, carries a staleness cap, and is never trained against indefinitely while
  frozen. Final champion numbers are always re-scored on a real meeting path, never surrogate-scored.
- **Co-evolution is DEFERRED to Wave 2**, and only if the PAUSE approves it: the naive two-population setup
  provably collapses here (FO-2, re-run on current HEAD), so any co-evolution runs behind the
  Hall-of-Fame/PFSP/reduced-virulence stabilizer stack or not at all.

Parallelism: three independent roots dispatch immediately: `15.1 ∥ 15.3 ∥ 15.4`. Then
`15.1 → 15.2`; `15.3 → (15.3.1 ∥ 15.5 ∥ 15.6)`; `(15.1, 15.4) → 15.8` [operator-run recording — dispatch as
early as its deps allow: it is the wall-clock bottleneck]; `(15.6, 15.8) → 15.7`; `(15.2, 15.5) → 15.9`;
`(15.3.1, 15.5, 15.7, 15.9) → 15.10`; `(15.5, 15.7, 15.9) → 15.11` (runs ∥ 15.10 — disjoint files, shared
ES core consumed read-only); `(15.3, 15.5) → 15.12`; `(15.8, 15.10, 15.11, 15.12) → 15.13`. The critical
path is `15.3 → 15.6 → 15.7 → 15.10 → 15.13`. Shared-file overlaps are all covered by dependency edges
(15.2→15.1 on `scripts/measure_baseline.py`; 15.3.1→15.3 on `training/env.py`; 15.7→15.6 on
`training/surrogate/fidelity.py`; 15.10→15.9 on `training/bakeoff/es.py`; 15.12→15.3 on `pyproject.toml`,
disjoint regions annotated).
Operator-run / spend gates: 15.8 (the corpus record — $0 marginal, ~7h wall with 2 Featherless seed
workers), 15.10/15.11 (local CPU training compute, $0, hours-scale), 15.12 (opt-in torch probe), and 15.13
(owner decisions + an operator-run real-LLM finalist evaluation). Everything else is agent-dispatchable and
CI-green on the fake provider.
Track with `python3 scripts/compute_next_task.py --phase 15`.

Merge criteria (Wave 1 → PAUSE): (1) `scripts/validity_gate.py` + `scripts/measure_baseline.py` exist as
committed code, reproduce the Phase-14 close numbers from the committed baseline-2 bytes ($0, offline), and
are the single gate every later training artifact quotes; (2) the selection referee is committed in `eval/`
re-anchored to baseline 2 — evidence-supply floors + the D1–D4 geomean — and has survived the adversarial
Goodhart probe (or its found exploits are documented with recommended floors, routed to the pause); (3) the
`training/` rollout environment runs the REAL `HeadlessGame` loop through the `agent_factory` seam with a
proven-legal action mask and byte-deterministic frozen-policy episodes; (4) the ballot surrogate has a
measured fidelity verdict against its honest ceiling with an explicit pre-stated GO/NO-GO and a selected
fallback; (5) the ML-calibration corpus is recorded at baseline-2 config, validity-gated, byte-verified,
policy-stamped, and frozen with committed splits; (6) the impostor bake-off report ranks all entrants on
the single shared protocol (gate / referee / fitness / anchor-KL / determinism hash), and the crew-track
and torch-probe reports exist in the same metric shape; (7) Task 15.13's pause audit is committed, the
seven owner decisions are recorded, the Wave-2 contracts are authored into this file, prompts are
regenerated, and `bash scripts/check.sh` is green.

Merge criteria (end-of-phase): authored at the PAUSE by Task 15.13, per the chosen deployment end-state.
Invariant regardless of branch: the shipped end-state passes the validity gate + selection referee, every
committed replay byte-verifies, and provenance (policy stamp + MANIFEST) attributes every recorded game to
an exact policy identity.

## Wave 1 — signal, harness, data, surrogate, and the bake-off

### Task 15.1 — Validity gate + baseline measurement CLIs (make the audit-cited scripts real)
**Branch:** `phase-15-validity-gate`
**Depends on:** none
**Section refs:** audits/audit-phase-14-close.md §1, §3, §8 (the gate criteria + R-gate rows this task productizes); audits/post-phase-14-pause.md §2.1 (the missing-harness finding); audits/post-phase-14-ML-training-signal.md §3 (the three-artifact split); eval/vote_correctness.py; eval/meeting_quality.py; eval/balance_eval.py; scripts/_verify_samples.py
**Complexity:** Medium

Turn the measurement harness from audit prose into committed code. The Phase-14 close audit grounds every
number in `scripts/validity_gate.py` (the HARD validity gate) and `scripts/measure_baseline.py` (the R-gate
measurement) — neither exists in the tree, and `eval/` has no CLI entrypoint at all (no
`__main__`/`argparse` anywhere in the package). This task creates `eval/validity.py` (the library fold) and
the two CLIs under those exact audit-cited filenames, by WIRING the existing committed folds — ejection
accuracy and genuine-class conversion (`eval/vote_correctness.py:302`, `:558`), meeting rate
(`eval/meeting_quality.py::compute_meeting_rate`, `:426`), win counts and reason histogram
(`eval/balance_eval.py:893-894` + `load_tournament_report`), accusation calibration
(`eval/accusation_calibration.py`), win-condition self-check (`eval/win_condition_selfcheck.py`), and the
byte-identity walk (`scripts/_verify_samples.py`) — never re-implementing a metric that already has a
tested home. Both CLIs take ANY replay-set directory (not just `replays/samples/*`), so the 15.8 corpus and
every Wave-2 candidate recording are first-class inputs; `--json` emits the machine-readable report the
bake-off harness and the pause audit consume; a gate failure exits non-zero and names the failing check.

**Files in scope:**
- eval/validity.py (new: the composed validity checks + report types)
- scripts/validity_gate.py (new CLI: hard pass/fail over a replay-set dir)
- scripts/measure_baseline.py (new CLI: core R-gate folds region — the 15.2 watchability fold is a later, disjoint region)
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
- [ ] Both CLIs accept an arbitrary replay-set directory and emit `--json` machine-readable reports; the JSON schema is documented in the module docstring (the 15.10 harness and 15.13 audit consume it).
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
`mypy --strict`. Roles ground truth lives ONLY in each set's `tournament-eval-report.json` (raw replays are
role-free by firewall design; `scripts/build_sample_report.py` shows the re-seed recipe if a set lacks the
report). The R1 eject-decided share is the count of `CREWMATE_EJECT`-reason wins — the same fold
`audits/workflows/extract_gameplay_facts.py:611` emits as `r1_eject_decided_wins`; reproduce the number
from the tournament report's reason histogram rather than importing the 4392-line audit script. For the
byte-identity check, call into the machinery behind `scripts/_verify_samples.py` rather than shelling out.
Note `scripts/` is on `mypy_path` — both CLIs are strict-checked. Keep every check pure and offline: the
whole gate must run on a fresh clone with no network and no `AILIBI_*` env.

**Ready-to-paste prompt:** `agent_prompts/task-15-1-validity-gate.md`

### Task 15.2 — Selection referee: evidence-supply floors + the D1–D4 geomean, re-anchored to baseline 2
**Branch:** `phase-15-watchability-referee`
**Depends on:** 15.1
**Section refs:** experiments/lab/rubric_score.py (the D1–D4 geomean, weights :53, composition :823); experiments/lab/report-rubric-design.md; audits/post-phase-14-ML-training-signal.md §3.2, §4, §6 (referee-as-gate doctrine); audits/post-phase-14-ML-planning.md §12 (the perfect-stealth risk); eval/meeting_quality.py (supply/conversion gauges)
**Complexity:** Medium

Build the committed champion-selection referee — the artifact that decides whether a trained candidate's
games are still a deduction game. Two layers, both selection-only (the module docstring states the
doctrine: this is a gate, NEVER a training reward). Layer 1, **evidence-supply floors** — the sharp,
data-grounded catch for the perfect-stealth failure mode: witnessed-event rate (baseline 2: 6/160 kills =
3.75% crew-witnessed in 9p2i), contradiction-flag production per meeting, and testimony-backed conversion,
wired from the existing supply/conversion gauges in `eval/meeting_quality.py`. The task measures each on
baseline 2 and pins floors at documented fractions of the measured values — evidence starvation (a
candidate whose games produce no flags and no witnesses) fails the referee even when meeting-rate stays
high, because bodies still trigger meetings after testimony has died. Layer 2, the **D1–D4 floor-gated
weighted geomean** promoted from lab-tier `experiments/lab/rubric_score.py` (which self-labels "NOT a
shipped eval gate" and is calibrated to baseline 1) into `eval/watchability.py`: weights {D1 .40, D2 .25,
D3 .15, D4 .20}, ε=1e-3, `score = 100 · floor · geomean`, floor∈{0,1} on a firewall/determinism breach,
friendly-fire, or railroad ejection — multiplicative, so a meeting-starved game collapses to ~0 by
construction. Re-anchor to baseline 2 and fold both layers into `scripts/measure_baseline.py
--watchability`.

**Files in scope:**
- eval/watchability.py (new: supply floors + geomean referee)
- scripts/measure_baseline.py (watchability fold region — 15.1 owns the core-folds region)
- tests/eval/test_watchability.py (new: parity, floor-trip, and supply-floor tests)

**Files NOT in scope:**
- experiments/lab/rubric_score.py + experiments/lab/rubric.md + replays/samples/9p2i/results-rubric-score.json (lab artifacts frozen; the API keeps serving the committed rubric file unchanged)
- api/ (no DTO/route change)
- eval/meeting_quality.py (gauges consumed, never edited)

**Definition of done:**
- [ ] Geomean parity: on the committed 9p2i facts, `eval/watchability.py` reproduces the lab scorer's per-game D1–D4 and composed scores (a parity test pins them), then the re-anchor to baseline 2 is applied with every changed threshold documented in the module docstring.
- [ ] The floor trips on synthetic fixtures: a railroaded ejection, a friendly-fire kill, and a determinism breach each force score 0.
- [ ] Evidence-supply floors: witnessed-event rate, flags-per-meeting, and testimony-backed conversion are measured on baseline 2, pinned as named constants with the measured values in comments, and a synthetic evidence-starved set (high meeting rate, zero flags, zero witnesses) FAILS the referee.
- [ ] The referee runs on BOTH sets from bytes — including 4p1i, which has no committed rubric artifact (the 9p2i/4p1i asymmetry is handled, not assumed away).
- [ ] `scripts/measure_baseline.py --watchability` emits per-game + aggregate referee results in the `--json` report consumed by 15.10 and 15.13.
- [ ] The module docstring states the selection-only doctrine and cites the Goodhart probe (15.9) as the referee's own acceptance test.
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
(masking, passive-survival gradients, railroad reward) — the deltas are committed+strict-typed, baseline-2
anchors, and byte/tournament-report inputs instead of the audit-tier facts JSON (document exactly which
facts-extraction subset is inlined). The supply gauges already exist in `eval/meeting_quality.py` — wire,
don't re-derive. Set the floors from measured baseline-2 values, not invented targets: the referee's job is
"do not accept a champion whose games produce structurally less evidence than the baseline," not "hit a
number." The lab file `GEOMEAN_RESULTS_FILENAME` machinery stays untouched — the committed 9p2i artifact is
the parity fixture, not a dependency.

**Ready-to-paste prompt:** `agent_prompts/task-15-2-watchability-referee.md`

### Task 15.3 — The `training/` package: rollout env, legal-action mask, reward channel (numpy lands here)
**Branch:** `phase-15-training-env`
**Depends on:** none
**Section refs:** audits/post-phase-14-ML-planning.md §5, §7, §11 (action space, injection seam, env wrapper); orchestrator/game.py (AgentFactory :93, HeadlessGame :1121, MeetingAwareAgent :425-450); experiments/lab/ml_spike/core.py (the SpikeAgent interposition pattern :148-200); engine/rules.py + engine/tick.py (the legality predicates); engine/events.py (the reward-source event types)
**Complexity:** Integration

Create the new top-level `training/` package (strict-typed from day one — no mypy exclusion) holding the
rollout environment every trainer in this phase rides. `TacticalRolloutEnv` drives the REAL production loop
— `HeadlessGame` with an injected `AgentFactory` built on the proven interposition pattern (wrap the real
`TacticalAgent`, override the chosen intent, delegate the full meeting protocol via `__getattr__` — port
the ml_spike pattern into typed code, do NOT import the mypy-excluded spike) — never a bespoke "training
game." Three capabilities: (1) a **legal-action mask** over the option/intent space, derived from the pure
legality predicates in `engine/rules.py`/`engine/tick.py`, with the two documented caveats handled
explicitly — emergency-uses-remaining and the map's sabotage kinds are NOT in the observation surface, so
the mask carries small policy-side trackers (the `EmergencyPacingTracker` precedent) rather than widening
the packet; and the mask distinguishes ENGINE-LEGAL resolved actions from OBSERVATION-MEANINGFUL
submissions, keeping the impostor's pretend `do_task` (engine-rejected, rendered as `action="task"`
camouflage to witnesses — 396 such submissions in the committed 9p2i stream) in the impostor's submission
vocabulary; (2) a **potential-based reward channel** exposing the side-specific tactically-reachable terms
from the typed event log (kills, witnessed-ness via `Killed.witnesses`, task progress, survival,
report/coverage events) so trainers never re-derive rewards from replay bytes; (3) **per-episode rollout
records** carrying the behavioral descriptors the QD entrant and the pause audit need (kill-timing
distribution, witness-exposure rate, vent usage, meeting-trigger rate, do_task-emission cadence, win
shape). `uv add numpy` (exact pin) lands in this task, confined to `training/` by a new import-linter
contract (`agents` must not import `training`) with `training` added to the linter's root packages.

**Files in scope:**
- training/__init__.py (new)
- training/env.py (new: `TacticalRolloutEnv`, the interposition factory, the mask)
- training/rewards.py (new: potential-based shaping + side-specific reward terms)
- training/rollout.py (new: episode records + behavioral descriptors)
- pyproject.toml (project dependencies region — the numpy exact pin; the mypy exclude regex is 15.12's disjoint region)
- uv.lock (numpy resolution)
- .importlinter (add `training` to root_packages + the new `agents ↛ training` contract)
- tests/training/__init__.py (new)
- tests/training/test_env.py (new)
- tests/training/test_rewards.py (new)
- tests/training/test_rollout.py (new)

**Files NOT in scope:**
- orchestrator/game.py (the seams already exist; zero orchestrator edits)
- engine/ (read-only; the RNG fast path is 15.3.1)
- agents/ (the encoder is 15.5; the FSMs are the anchor and stay untouched)
- experiments/lab/ml_spike/ (frozen reference — port, never import)
- eval/balance_eval.py (the surrogate-runner keyword is 15.7's)

**Definition of done:**
- [ ] The env runs full fake-provider games through an injected factory at or above the measured floor (≥5 games/s at 9p2i on the check host; the actual figure is documented in the module docstring).
- [ ] A meeting runner is ALWAYS installed: `meeting_runner=None` truncation (`MEETING_PHASE_REACHED`) is structurally unreachable from the env, asserted by test — truncation is never a fitness path.
- [ ] Mask legality is property-tested against the engine: across randomized seeds/ticks, every masked-legal engine action resolves without rejection and every unmasked action is engine-rejected — with the pretend-`do_task` camouflage carried in the impostor SUBMISSION set and excluded from the engine-legal set (both asserted).
- [ ] The reward channel is potential-based: a telescoping test shows shaping sums to Φ(terminal) − Φ(initial) over any episode, so shaping cannot change the optimal policy.
- [ ] A frozen-policy episode is byte-deterministic: same seed → identical per-tick state-hash sequence across two runs (the spike's check-1 reproduced inside the committed package).
- [ ] numpy imports are confined to `training/`: `uv run lint-imports` keeps `agents ↛ engine` AND the new `agents ↛ training` contract; `training` is in root_packages.
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
surface (`orchestrator/game.py:1124-1163`); `max_ticks` rides the `TickScheduler`, not the constructor. The
wrapper agent must satisfy the FULL `MeetingAwareAgent` protocol (both properties + both render methods —
isinstance-checked at `game.py:863` before meetings build participants); wrapping the real `TacticalAgent`
and delegating via `__getattr__` gets all of it for free, plus the crew-only `EmergencyPacingTracker`
bookkeeping. Mask derivation: every legality predicate is a pure boolean of `(state, map, actor)` with zero
RNG — mirror them agent-side from the packet + trackers rather than importing engine (the firewall
forbids `agents → engine`, and `training/` should reach engine truth only through the orchestrator loop).
Default meeting runner for rollouts is `build_default_meeting_runner` on the fake provider
(`tests/conftest.py` pins `AILIBI_LLM_PROVIDER=fake` for all tests); the surrogate slots in via the same
parameter once 15.7 lands.

**Integration risk:**

This is the seam every trainer rides; the failure mode is DRIFT from the production loop — a bespoke
training game would silently invalidate every fitness number and every determinism claim downstream. The
env must be the real `HeadlessGame`, the real observation firewall, the real meeting manager, with the ONLY
interposition at the factory. Second risk: numpy — BLAS reductions are not bit-stable across
machines/thread counts, which is exactly why numpy stays training-side and the production inference path
(15.5, Wave 2) stays pure-Python; the import-linter contract is the enforcement, not a convention. Third:
the mask must not delete the pretend-`do_task` camouflage lever — a strict engine-legal-only vocabulary
regresses the impostor's task-traffic mimicry, which is measured behavior on the committed baseline.

**Ready-to-paste prompt:** `agent_prompts/task-15-3-training-env.md`

### Task 15.3.1 — Training-only RNG hash fast path (opt-in; committed paths byte-unchanged)
**Branch:** `phase-15-rng-fast-path`
**Depends on:** 15.3
**Section refs:** audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization)
**Complexity:** Medium

`engine/rng.py` re-serializes the full 625-int Mersenne state via `json.dumps` on every tick (~43% of
bare-engine cost) and the drawn value is discarded — but that serialization is hashed into every committed
`state_hash`, so it is load-bearing for replay byte-identity and must NEVER be changed in place. This task
adds an explicit, opt-in hash policy (a typed policy object threaded `HeadlessGame → engine`, no env-var
magic) that skips the per-tick rng-state serialization for non-recorded training rollouts only. The default
is byte-identical to today; anything that records or verifies a replay refuses the fast path loudly. The
RNG draws themselves are untouched — trajectories are identical under both modes, so training results
transfer to the recording path exactly.

**Files in scope:**
- engine/rng.py (the opt-in fast-path region; default behavior byte-identical)
- orchestrator/game.py (rng-hash policy plumbing region only)
- training/env.py (fast-path knob region — 15.3 owns the rest of the module)
- tests/engine/test_rng_fast_path.py (new)
- tests/training/test_env_fast_path.py (new)

**Files NOT in scope:**
- orchestrator/replay.py + api/replay_loader.py (recording/verification never accepts the fast path — refusal at construction, not silent downgrade)
- scripts/_verify_samples.py (unchanged; committed samples must keep verifying)
- replays/samples/ (untouched)

**Definition of done:**
- [ ] Default path byte-identical: `bash scripts/verify_samples.sh` reconstructs all 100 committed samples clean with the change merged.
- [ ] Fast path measurably faster: the engine-core speedup ratio is measured and documented (target ≥1.3×; report the actual).
- [ ] Constructing a recording/replay-writing game with the fast path active raises a descriptive error (tested); the training env exposes the knob and defaults it OFF.
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
mode from the environment. The state-hash serializer in `orchestrator/replay.py` is not edited — the fast
path simply never reaches it, because recording refuses the policy up front.

**Ready-to-paste prompt:** `agent_prompts/task-15-3-1-rng-fast-path.md`

### Task 15.4 — Tactical-policy provenance stamp (replay writer + MANIFEST + loader guard)
**Branch:** `phase-15-policy-provenance`
**Depends on:** none
**Section refs:** audits/post-phase-14-ML-planning.md §7.2-7.3 (record-actions provenance; the stamp recommendation); orchestrator/replay.py (substrate_flag_snapshot :277-299, game_over stamping :434-441); api/replay_loader.py (the substrate mismatch guard :377-423); scripts/_manifest_writer.py
**Complexity:** Integration

Answer "which tactical policy produced these bytes" the same way the repo already answers "which substrate
levers": a provenance stamp, mirrored across the three provenance surfaces. `orchestrator/replay.py` stamps
a `tactical_policy` block into the `game_over` entry — `{policy_id, method, encoder_version,
weights_sha256, anchor_policy}` (plain strings; no import of any training code) — exactly beside the
existing `substrate_flags` stamp; `scripts/_manifest_writer.py` adds a policy column so every recorded
set's MANIFEST attributes each seed; `api/replay_loader.py` gains a mismatch guard mirroring
`ReplaySubstrateMismatchError` that refuses to serve a stamped replay under a conflicting policy claim. An
ABSENT stamp means "scripted FSM default" and stays fully valid — the committed baseline-2 sets are
untouched and must keep loading, byte-verifying, and serving with zero edits. Replay reconstruction
re-feeds recorded actions and never re-invokes a policy, so the stamp is provenance, not a replay input —
this is what keeps learned-policy replays byte-identical regardless of inference-float questions.

**Files in scope:**
- orchestrator/replay.py (tactical-policy stamp region, alongside the substrate-flags stamp)
- api/replay_loader.py (policy-stamp read + mismatch guard region)
- scripts/_manifest_writer.py (policy column)
- tests/orchestrator/test_replay_policy_stamp.py (new)
- tests/api/test_replay_loader_policy_stamp.py (new)
- tests/scripts/test_manifest_writer.py (extend: FSM-default rendering pinned)

**Files NOT in scope:**
- replays/samples/ (committed bytes untouched; absent stamp = FSM default)
- orchestrator/game.py + agents/ + training/ (no coupling: the stamp is strings, set by the recorder)
- scripts/refresh_samples.sh (the canonical-sample refresh flow is frozen; the corpus recorder 15.8 consumes the stamp)

**Definition of done:**
- [ ] Committed 9p2i + 4p1i sets load, byte-verify (`bash scripts/verify_samples.sh` clean), and serve with zero edits — absent stamp renders as the FSM default everywhere.
- [ ] A stamped recording round-trips writer → loader with all five fields intact; the stamp appears in the game_over entry beside `substrate_flags`.
- [ ] A deliberately mismatched stamp raises the new loader guard (fail-loud, mirroring the substrate guard's shape and error quality).
- [ ] The MANIFEST writer emits the policy column; existing manifest tests pin the FSM-default rendering for unstamped rows.
- [ ] The stamp schema is documented (module docstring) for 15.8 (corpus rows stamp the FSM default explicitly) and Wave 2 (champion weights hash).
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
never sees (the state hash covers `WorldState`, not replay-entry metadata — verify with the byte-identity
suite, not by assumption).

**Integration risk:**

The whole task is byte-compatibility: the committed samples are the regression fixture, and
`verify_samples.sh` green under a bare environment is the non-negotiable proof. Second risk: schema creep —
the stamp must stay plain strings so `orchestrator/` never imports training or agents code (keeping the
dependency direction clean for the import-linter contracts added this phase).

**Ready-to-paste prompt:** `agent_prompts/task-15-4-policy-provenance.md`

### Task 15.5 — Encoder v2 (memory-carrying), the determinism harness, and the leak-test factory mode
**Branch:** `phase-15-encoder-v2`
**Depends on:** 15.3
**Section refs:** audits/post-phase-14-ML-planning.md §6 (observation surface, encoder shape, determinism hazards); observation/packet.py:159-188; observation/public_map.py:14-32; agents/memory/beliefs.py + agents/memory/working.py (the carried state); experiments/lab/ml_spike/core.py:60-83 (the 34-dim memoryless baseline); eval/leak_test.py; tests/test_firewall.py:64-75
**Complexity:** Integration

The spike's 34-dim encoder is memoryless — the structural reason its behavior clone capped below FSM parity
(the FSM's stalk is history-dependent). Build the versioned production encoder in
`agents/tactical/features.py`: pure-Python, deterministic, firewall-legal, consuming `ObservationPacket` +
`PublicMapView` + the agent's OWN memory (`MemoryStore` episodic recency, `WorkingMemory.last_seen`
(tick, room) ages, own `BeliefState` suspicion/trust floats — quantized to a fixed grid before they touch
any feature, per the §6.3 determinism hazard), with an `ENCODER_VERSION` constant that feeds the 15.4
stamp. Ship the two harnesses every candidate must pass: `training/determinism.py` (double-run SHA-256 over
the full (feature-vector, logits, chosen-intent) stream of a frozen policy across a fixed seed set, plus
frozen-genome full-game state-hash equality) and an agent-factory mode for `eval/leak_test.py` — today it
walks 3 scripted fixtures with no factory parameter, so a learned mover that drives the engine into regions
those fixtures never reach is unscanned; the extension runs factory-built agents through full games and
applies the existing recursive role-leak scanners to every packet the encoder consumes. Extend
`tests/test_firewall.py` with the pure-Python inference doctrine: no `numpy`/`torch` import anywhere under
`agents/`.

**Files in scope:**
- agents/tactical/features.py (new: the versioned encoder)
- training/determinism.py (new: the policy determinism harness)
- eval/leak_test.py (agent-factory mode region — the 3 scripted fixtures stay byte-identical)
- tests/test_firewall.py (extend: numpy/torch ban under agents/)
- tests/agents/test_features.py (new)
- tests/training/test_determinism.py (new)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py + agents/tactical/crewmate_policy.py (the FSMs are the anchor and the BC oracle — untouched)
- observation/ (NO packet surface change: the un-observable crew task-set stays un-observable pending the pause decision)
- agents/memory/ (read-only: the encoder consumes the stores, never mutates them)
- .importlinter (contracts landed in 15.3)

**Definition of done:**
- [ ] The encoder is engine-free (existing `agents ↛ engine` contract + the schema-file firewall test cover it) and total over every packet shape in the committed corpora: a sweep test feeds all 100 committed games' packets through it without error.
- [ ] Feature layout + dimension count are documented and pinned by a golden test; `ENCODER_VERSION` bumps are the only way the layout may change.
- [ ] Belief-derived features are integer-quantized with lexical tie-breaking documented — no raw-float comparison anywhere in the encoder (the residue-flips-argmax hazard).
- [ ] Determinism harness: two runs of a frozen policy over a fixed seed set produce identical SHA-256 over (features, logits, intents); the harness is a library any bake-off entrant invokes, and its report is the artifact 15.10 quotes.
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
episodic recency from `MemoryStore.recent()`. `moved_players` is omitted from the packet JSON when empty —
treat it as optional, never `[]`-assumed. Roster-dependent features need fixed-slot encoding sorted by
`player_id` (the repo's lexical-tie-break idiom). The crew side may only consume belief state the crew
agent legitimately holds — the same information that already reaches crew tactics through
`EmergencyPacingTracker._over_gate`; document any widening explicitly in the docstring so the leak review
has one place to look.

**Integration risk:**

The encoder is the one place role-blind observation and role-private memory meet: a feature that folds in
another agent's private state is a firewall breach the import-linter cannot see — which is why the
leak-test factory extension lands in the SAME task, not later. Second risk: determinism — belief floats
accumulate non-power-of-two deltas and `known_players()` is dict-insertion-ordered; quantize-then-compare
and sorted iteration are mandatory, and the harness hashes features+logits precisely so a violation is
caught at the artifact, not in a downstream replay.

**Ready-to-paste prompt:** `agent_prompts/task-15-5-encoder-v2.md`

### Task 15.6 — The meeting training table + surrogate fidelity harness (re-baseline FO-6 honestly)
**Branch:** `phase-15-meeting-table`
**Depends on:** 15.3
**Section refs:** audits/post-phase-14-ML-training-signal.md §2, §5.4-5.5, §7.2 (the table, the fidelity protocol, the honest ceiling); agents/memory/beliefs.py (the LLM-free belief fold); meetings/manager.py (derive_belief_evidence :2680; roster off result.ballots :2823); experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (the failed prior); replays/samples/ (the 142+39 committed meetings)
**Complexity:** Medium

Build the supervised substrate the ballot surrogate trains and is judged on. For every committed meeting,
reconstruct OFFLINE (LLM-free, replay-deterministic) the per-(meeting, voter) feature rows: the pre-meeting
belief-fold state (rendered suspicion/trust toward each candidate — the fold in `agents/memory/beliefs.py`
is deterministic over recorded events and needs no LLM), contradiction-flag structure, sighting/co-presence
reconstruction, reporter identity, kill-proximity and isolation, movement anomalies, and task-cadence
features — joined to the ACTUAL recorded ballots `{voter, target, confidence, primary_reason_id}` and to
roles ground truth from `tournament-eval-report.json` (raw replays carry no roles by firewall design). Ship
the fidelity harness the phase judges ALL meeting models with: by-GAME cross-validation (never by-meeting —
leakage), top-1/top-2 ejected-target ranking, SKIP-vs-eject decision accuracy, and Brier/ECE calibration on
ballot confidences — plus the HONEST CEILING: the measured voice-driven share of ejections a physical+belief
surrogate structurally cannot see (82% of zero-flag convictions sit in the soft band with no flag and no
body-proximity). Re-run the FO-6 logistic under this harness to pin the true prior baseline (its headline
top-1 64% collapsed to 26%/43% on baseline 2, and its binary head degenerates to always-SKIP), and mark the
stale spike conclusion at its source: `experiments/lab/report-ml-spike.md` gets a STALE banner pointing
here. The table builder takes any replay-set directory and reads the committed `splits.json` when present —
it re-runs unchanged on the 15.8 corpus.

**Files in scope:**
- training/surrogate/__init__.py (new)
- training/surrogate/dataset.py (new: the table builder + splits.json loader)
- training/surrogate/fidelity.py (new: CV protocol + metrics + the honest ceiling — the GO/NO-GO wiring is 15.7's region)
- training/reports/report-meeting-table.md (new: table stats, FO-6 re-baseline, the honest ceiling)
- experiments/lab/report-ml-spike.md (STALE banner only — no other edit)
- tests/training/test_surrogate_dataset.py (new)
- tests/training/test_surrogate_fidelity.py (new)

**Files NOT in scope:**
- agents/memory/beliefs.py + meetings/manager.py (the fold is consumed read-only)
- experiments/lab/ml_spike/fo6_learned_vote_surrogate.py (frozen probe; re-run, not edited)
- replays/ (read-only; the corpus lands in 15.8)

**Definition of done:**
- [ ] Table counts reproduce the committed bytes exactly: 9p2i 142 meetings (118 ejections / 24 skips), 4p1i 39 (13/26); every recorded ballot joins a feature row (100% join rate, asserted).
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
`audits/workflows/extract_gameplay_facts.py` and `ml_spike/core.py::reconstruct` for reconstruction
recipes, but import neither (one is audit-tier, the other mypy-excluded). Row grain is one row per
(meeting, voter) — the roster the cross-meeting fold uses is read off `result.ballots`, which fixes it.

**Ready-to-paste prompt:** `agent_prompts/task-15-6-meeting-table.md`

### Task 15.7 — The ballot-predictor surrogate MeetingRunner (GO/NO-GO + the fallback ladder)
**Branch:** `phase-15-ballot-surrogate`
**Depends on:** 15.6, 15.8
**Section refs:** audits/post-phase-14-ML-training-signal.md §5 (the rebuild design); orchestrator/game.py:402-422 (the MeetingRunner protocol), :905-943 (result validation); meetings/voting.py:120-213 (tally_ballots); meetings/manager.py:138 (DEFAULT_SKIP_CONFIDENCE_THRESHOLD), :2823 (roster off ballots); eval/balance_eval.py:227 (run_tournament_eval)
**Complexity:** Integration

The $0 inner-loop meeting model, rebuilt on the structural fix: predict each living voter's BALLOT
(target, confidence) from the 15.6 features, and let the REAL deterministic tally produce the outcome —
`tally_ballots(ballots, skip_confidence_threshold=DEFAULT_SKIP_CONFIDENCE_THRESHOLD)` (the threshold is a
required keyword with NO default; pass the manager constant explicitly). This eliminates FO-6's always-SKIP
collapse by construction (SKIP-vs-eject emerges from plurality + the confidence gate, not a mis-calibrated
binary head) and restores belief persistence (one ballot per living voter is exactly the roster the
cross-meeting fold reads). Train on the 15.8 corpus via the 15.6 table (numpy allowed); wrap as
`SurrogateMeetingRunner` conforming to the runtime-checkable `MeetingRunner` protocol: the returned
`MeetingArtifacts` echoes `meeting_id`/`triggered_by`/`trigger_tick` (validated at `game.py:905-943`),
carries a full-roster ballot set, and empty LLM metadata. The GO/NO-GO bar is written BEFORE training,
against the 15.6 honest ceiling; the fallback ladder is in-contract: (a) the fake-provider MeetingManager
as the training-time runner, (b) meeting-boundary episode truncation with meeting-free fitness terms,
(c) periodic real-LLM re-grounding recordings (operator, $0). Whatever the verdict, the staleness doctrine
ships: a use-counter/config cap the bake-off must respect, so no trainer optimizes indefinitely against a
frozen surrogate. Additively, `run_tournament_eval` gains an optional per-game meeting-runner factory
keyword (mirroring its existing per-game default-runner construction) so surrogate-driven tournaments
produce standard reports for diagnostics — final champion scoring still always uses a real meeting path.

**Files in scope:**
- training/surrogate/ballots.py (new: the predictor + training entry)
- training/surrogate/runner.py (new: the MeetingRunner implementation)
- training/surrogate/fidelity.py (GO/NO-GO wiring region — 15.6 owns the metrics core)
- eval/balance_eval.py (additive optional meeting-runner-factory keyword on run_tournament_eval)
- training/reports/report-ballot-surrogate.md (new: fidelity vs ceiling, the verdict, the chosen fallback, the re-grounding cadence)
- tests/training/test_surrogate_runner.py (new)
- tests/eval/test_balance_eval_meeting_runner.py (new)

**Files NOT in scope:**
- meetings/voting.py (the tally is consumed pure — reimplementing it would defeat the design)
- meetings/manager.py + llm/ (no meeting-layer change)
- orchestrator/game.py (the protocol is already injectable)

**Definition of done:**
- [ ] `SurrogateMeetingRunner` satisfies `isinstance(_, MeetingRunner)`; a full surrogate-driven `HeadlessGame` completes with valid artifacts — trigger echo validated, one ballot per living voter, and the cross-meeting belief fold consumes the result (asserted by test).
- [ ] The predicted-ballot path feeds the real `tally_ballots` with the explicit manager threshold; no re-implemented tally logic exists anywhere in `training/`.
- [ ] The GO/NO-GO bar is stated in the report and in code BEFORE training (e.g. GO ⇔ held-out top-1 ≥ 0.75 × the honest ceiling AND SKIP-vs-eject ≥ 0.80 — the implementer finalizes the exact bar, but it must be committed before the training run), and the verdict is reported against it with by-game-CV numbers from the 15.6 harness.
- [ ] The fallback path is exercised by test regardless of verdict: the training env runs under fallback (a) today, proving the bake-off cannot be blocked by a NO-GO.
- [ ] Surrogate inference is deterministic under a fixed weights artifact (double-run hash test); the weights artifact carries a sha256 the 15.4 stamp schema can reference.
- [ ] The staleness cap is real code the bake-off consumes (exceeding it raises), and the re-grounding recipe (record fresh real-LLM meetings, rebuild the table, re-fit, re-measure) is documented step-by-step in the report.
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

Keep the predictor simple and calibrated — a standardized multinomial logistic or tiny MLP over the 15.6
features is the determinism-safe default; gradient-boosted trees would need integer-threshold care and are
not worth it at this data size. `MeetingArtifacts(result=…, llm_calls=(), prompt_versions={})` is the shape
the orchestrator dereferences; a bare `MeetingResult` fails. Dead voters cast nothing: derive the living
roster from the trigger-time state the runner receives. The `run_tournament_eval` keyword must be
additive-optional with the default path byte-identical (existing balance-eval tests stay green untouched).

**Integration risk:**

Model exploitation is the known failure (MBPO/Dreamer): a trained mover shifts the sighting/contradiction
distribution and the surrogate's blind spot — voice-driven convictions it structurally cannot see — becomes
the attack surface. The mitigations are all structural and land here: the staleness cap, the pre-stated
GO/NO-GO with the honest ceiling as denominator, re-grounding as a documented operator recipe, and the
bake-off's rule that final numbers are never surrogate-scored. Do not weaken any of the four to make a
verdict look better.

**Ready-to-paste prompt:** `agent_prompts/task-15-7-ballot-surrogate.md`

### Task 15.8 — The ML-calibration corpus: record, validate, freeze (operator-run, $0)
**Branch:** `phase-15-ml-corpus`
**Depends on:** 15.1, 15.4
**Section refs:** audits/post-phase-14-ML-training-signal.md §5.6, §7.2 (the frozen-corpus doctrine + the data gap: 118 committed 9p2i ejections is thin); audits/audit-phase-14-close.md (the baseline-2 recording recipe: 2 seed workers, ~3.85h/100 games); scripts/refresh_samples.sh (the recording pattern to compose); api/replay_loader.py + api/main.py (set-discovery semantics the layout must not collide with)
**Complexity:** Medium

Record the frozen training/calibration corpus the surrogate and the bake-off consume, at EXACT baseline-2
config (`Qwen/Qwen3-32B` Featherless non-thinking `fail_loud` `json_object`, prompt set `qwen3_32b.v4`, all
five levers ON, $0 flat-rate): **9p2i × 150 seeds (1000–1149)** primary and **4p1i × 50 seeds (1000–1049)**
secondary — fresh seed ranges so a corpus game can never be confused with the canonical 0–49 sets
(~3× the committed 9p2i meeting/ejection data, ~7h wall with 2 Featherless seed workers). Layout:
`replays/ml_corpus/9p2i/` + `replays/ml_corpus/4p1i/`, each carrying `replay-seed-*.jsonl`, `MANIFEST.md`
(with the 15.4 policy column stamping the FSM default), `roster.json` where applicable,
`tournament-eval-report.json` (the roles ground truth), and a committed by-game `splits.json`
(train/val/test — data only; the loader is 15.6's). The two-level nesting is LOAD-BEARING: a set directory
placed directly under `replays/` would make the API's directory resolution treat `./replays` as the active
parent and SHADOW the canonical samples — a discovery non-collision test pins that `replays/ml_corpus/` is
invisible to default spectator resolution while an operator can still opt-in serve it explicitly. Freeze =
MANIFEST records git_sha + an explicit FROZEN line; acceptance = the 15.1 validity gate + byte-verification,
run per set before the PR merges.

**Files in scope:**
- scripts/record_ml_corpus.sh (new: thin wrapper composing scripts/run_tournament.py — contiguous seed ranges, per-seed crash-retry, MANIFEST + report + splits emission)
- replays/ml_corpus/9p2i/ (new artifact set)
- replays/ml_corpus/4p1i/ (new artifact set)
- tests/scripts/test_record_ml_corpus.py (new: dry-run/arg/splits-emission tests, no network)
- tests/api/test_set_discovery_ml_corpus.py (new: spectator discovery non-collision pinned)

**Files NOT in scope:**
- replays/samples/ (the canonical baseline is untouched — the corpus is a SEPARATE release artifact)
- scripts/refresh_samples.sh (frozen; the new wrapper composes the same underlying tooling, never edits it)
- api/replay_loader.py + api/main.py (discovery semantics are pinned by test, not changed)
- training/ (no Python here — the corpus must be recordable before 15.3/15.6 land)

**Definition of done:**
- [ ] Both corpus sets recorded at exact baseline-2 config; `scripts/validity_gate.py` PASSES on each corpus dir, and the state-hash chains byte-verify via the `_verify_samples.py` machinery pointed at the corpus.
- [ ] Every corpus replay carries the substrate flags AND the 15.4 FSM-default policy stamp; MANIFEST rows carry seed/model/prompt_versions/flags/git_sha/cost ($0)/winner plus the policy column, and the FROZEN line names the git_sha.
- [ ] `splits.json` per set: a documented deterministic by-game split (train/val/test) committed as data; no game appears in two splits (asserted by a test reading the file).
- [ ] Corpus stats reported in the PR description from the gate/measure CLIs: game count, meeting/ejection/skip counts (expect roughly 3× the committed 9p2i 142/118/24), win split — measured, not estimated.
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

Compose, don't fork: `scripts/run_tournament.py --num-games … --output-dir …` with the roster env/args per
set is the underlying recorder (the same one `refresh_samples.sh` drives); clone refresh_samples' worker
queue + crash-retry shape for the 2-worker Featherless saturation and its MANIFEST/report emission
patterns via `scripts/_manifest_writer.py` + `scripts/build_sample_report.py`. Hosted models do not
byte-reproduce FRESH generation — recordings replay byte-identically (the loosened contract baseline 2
already carries); the validity gate + byte-verify is the acceptance, not generation-replay equality.
Operator gate: requires `FEATHERLESS_API_KEY`; ~7h wall; commit is one atomic PR after the gate passes. A
deterministic split rule (e.g. seed mod 5 → {0,1,2}=train, {3}=val, {4}=test) documented in the MANIFEST
keeps the split auditable from the file alone.

**Ready-to-paste prompt:** `agent_prompts/task-15-8-ml-corpus.md`

### Task 15.9 — The adversarial Goodhart probe: red-team the referee, and the shared ES core
**Branch:** `phase-15-goodhart-probe`
**Depends on:** 15.2, 15.5
**Section refs:** audits/post-phase-14-ML-training-signal.md §3.2, §7.1.9 (the un-run charter guardrail); experiments/lab/ml-spike-charter.md (gap 3); experiments/lab/ml_spike/fo3_rubric_goodhart.py (the prior probe shape); audits/post-phase-14-ML-planning.md §12.2 (reward-hacking guards)
**Complexity:** Medium

Before the pause is allowed to use the 15.2 referee as a champion-selection gate, attack it: run evolution
DIRECTLY on the referee score — the deliberately-forbidden objective — and see what a genome can extract.
This lands two artifacts. First, the shared strict-typed ES core (`training/bakeoff/es.py`: seeded
population loop, mutation, K-seed fitness averaging, deterministic double-run behavior — ported from the
spike's pure-Python loop, numpy permitted) that 15.10/15.11 reuse, so every trainer in the phase shares one
audited optimizer. Second, the probe itself: ES on the full referee output (geomean × floors × supply
floors) with the validity gate as the only constraint, run on the training env with fake-provider meetings
(and re-run under the 15.7 surrogate at 15.10 time, when meeting-controlled terms open to tactical
pressure — the probe report states this scoping explicitly). Every score gain is decomposed into which
D-term or floor moved and by what behavior; the deliverable is a trust verdict: exploits-found (each with
the triggering trajectory and a recommended floor/patch, routed to the PAUSE — this task does not edit the
referee it is attacking) or held-under-probe.

**Files in scope:**
- training/bakeoff/__init__.py (new)
- training/bakeoff/es.py (new: the shared ES core — 15.10 extends it behind its dependency edge)
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
- [ ] The report ends in an explicit verdict: HELD (no exploit above a stated materiality bar) or EXPLOITS-FOUND (each with trajectory evidence + a recommended floor), and states the surrogate-path re-run obligation at 15.10.
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

FO-3 already showed tactical play cannot move meeting-controlled rubric terms under fake meetings — so the
expected attack surface here is the physically-reachable terms (D4 contest via meeting-farming is the
known-tiny one) and the supply floors themselves; a null result on the meeting-dependent terms is expected
and must not be reported as "referee safe" without the surrogate-path caveat. Chaotic fitness needs K-seed
averaging (the spike's check-2 lesson). Cap the probe's budget honestly — the point is cheap insurance
against laundering a degenerate champion as "watchable," not an exhaustive search.

**Ready-to-paste prompt:** `agent_prompts/task-15-9-goodhart-probe.md`

### Task 15.10 — The impostor bake-off: BC/DAgger, utility-scorer+ES, policy-net+ES, MAP-Elites
**Branch:** `phase-15-impostor-bakeoff`
**Depends on:** 15.3.1, 15.5, 15.7, 15.9
**Section refs:** audits/post-phase-14-ML-planning.md §5.2, §9 (the option vocabulary + paradigm comparison); audits/post-phase-14-ML-training-signal.md §4 (the objective spine: competence + anchor-KL + QD; referee as gate); agents/tactical/impostor_policy.py (_scored_targets :937-1009, the ladder :261); experiments/lab/ml_spike/check2_learnability.py + fo9_diversity.py (the ES priors)
**Complexity:** Integration

The wave's centerpiece: four training methods, one harness, one seed set, one report — so the pause
compares methods, not evaluation protocols. Entrants, all impostor-side: (1) **BC/DAgger** from the FSM
oracle — behavior-clone `ImpostorPolicy.decide` on encoder-v2 features with DAgger corrections (the FSM is
a free queryable expert), reported against a pre-stated intent-agreement bar; this is the
encoder-sufficiency test — if v2 features cannot reproduce the scripted ladder, the encoder gaps are the
finding; (2) **learned utility scorer over FSM-proposed options + ES** — the conservative bounded path:
keep the FSM's option generation and replace exactly the `_scored_targets` ranking (isolation ×
(1−witness_risk) × cooldown, lexical tie-break) plus the option-level choices (kill now / stalk-toward /
vent-exit choice / cover / fake-task / reposition-during-cooldown), structurally unable to emit illegal or
off-menu actions; (3) **direct masked policy net + ES** — the higher-ceiling path over the full masked
intent space; (4) **MAP-Elites** over the 15.3 behavioral descriptors with competence as cell quality —
diversity as measured archive coverage. Every ES/QD entrant optimizes the SAME fitness: the
tactically-reachable side-specific terms + potential shaping, with an anchor-KL penalty toward the frozen
FSM (measured as divergence from the FSM's choice distribution over the same states); the validity gate and
the 15.2 referee are SELECTION filters applied to candidates after training — never terms in any fitness.
The crew side stays the frozen scripted FSM throughout (no co-evolution this wave). Every candidate that
reaches the report passes the 15.5 determinism harness and the leak-test factory mode; fitness may use the
15.7 surrogate within its staleness cap, but every reported number is re-scored on a real meeting path
(fake-provider meetings on the fixed eval seed set). Also discharge the 15.9 obligation: re-run the
Goodhart probe under the surrogate meeting path and append the delta to the probe's findings in this
report.

**Files in scope:**
- training/bakeoff/harness.py (new: the entrant protocol, the fixed eval protocol, the report emitter)
- training/bakeoff/bc.py (new)
- training/bakeoff/utility_es.py (new)
- training/bakeoff/policy_es.py (new)
- training/bakeoff/map_elites.py (new)
- training/bakeoff/es.py (shared-core extensions — behind the 15.9 dependency edge)
- training/reports/report-impostor-bakeoff.md (new)
- training/reports/results-impostor-bakeoff.jsonl (new: the machine-readable per-entrant rows 15.13 consumes)
- training/artifacts/impostor/ (new: frozen candidate weights, float-hex JSON + sha256 sidecars)
- tests/training/test_bakeoff_harness.py (new)
- tests/training/test_bakeoff_methods.py (new: each entrant's train/eval loop on tiny budgets)

**Files NOT in scope:**
- agents/tactical/impostor_policy.py (the anchor and oracle is read-only — nothing ships into agents/ before the PAUSE)
- eval/ (gates consumed via the 15.1/15.2 JSON contracts)
- experiments/lab/ (the torch probe is 15.12)
- training/crew/ (15.11's parallel track)

**Definition of done:**
- [ ] One harness: every entrant trains and evaluates through `training/bakeoff/harness.py` on the same fixed seed set — entrants carry no private eval loops (asserted structurally: the harness is the only module that computes reported metrics).
- [ ] Every entrant row in `results-impostor-bakeoff.jsonl` carries the full tuple: validity-gate pass, referee result (score distribution + floor-trip rate + supply floors), inner fitness, anchor-KL, impostor win rate + take-rate (reported, never gated), determinism-harness hash, leak-test pass, surrogate-staleness usage, and wall-clock.
- [ ] The BC entrant reports held-out intent agreement with the FSM against its pre-stated bar (≥0.90 top-1 unless the contract PR documents a different bar BEFORE training) and names the encoder gaps if it misses.
- [ ] The utility-scorer entrant consumes exactly the FSM's option set (a test enumerates the options on fixture states and pins the menu) — the bounded path is real, not aspirational.
- [ ] The MAP-Elites entrant reports archive coverage over the named descriptors + best-per-cell quality; single-objective entrants report their descriptor footprint for comparison.
- [ ] No unregularized champion: anchor-KL is computed for every reported candidate; candidates above the documented KL ceiling are flagged in the report, not silently dropped.
- [ ] The Goodhart probe re-run under the surrogate path is appended with a delta verdict vs the 15.9 baseline.
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

Warm-start the ES entrants from the BC solution where shapes align (the spike's BC-then-ES lesson: BC alone
caps below FSM parity on a weak encoder; ES climbs from it). The anchor-KL is cheap in pure form: sample
states from rollouts, compare the candidate's choice distribution to the FSM's deterministic choice
(a log-loss against the anchor's action works as the piKL-style penalty at this scale). Respect the 15.7
staleness cap in the training loop config, and log every surrogate use into the jsonl rows. Tiny-budget CI
tests train for a handful of generations on 1–2 seeds — the full runs are operator-executed and their
budgets recorded in the report ($0, CPU, hours-scale).

**Integration risk:**

Two failure modes. (a) Protocol drift between entrants — the single-harness rule exists because one entrant
evaluating on different seeds or a different meeting path silently un-ranks the whole comparison; the
harness owning all metric computation is the enforcement. (b) Surrogate exploitation — a candidate that
looks strong on surrogate-scored fitness and collapses on the real meeting path is the expected shape of
failure; the re-score-on-real-path rule plus the staleness cap are the guards, and the report must show
both numbers where they diverge. Also: keep every candidate's weights + config committed under
`training/artifacts/impostor/` with sha256 — the pause's finalist evaluation and any Wave-2 productization
must be able to reload the exact artifact.

**Ready-to-paste prompt:** `agent_prompts/task-15-10-impostor-bakeoff.md`

### Task 15.11 — The crew track: a learned scorer over observable crew options
**Branch:** `phase-15-crew-track`
**Depends on:** 15.5, 15.7, 15.9
**Section refs:** audits/post-phase-14-ML-planning.md §4.1, §5.2 (crew FSM gaps + the observability blocker); audits/post-phase-14-ML-training-signal.md §3.2 (crew reward terms); agents/tactical/crewmate_policy.py (the ladder :343-423; EmergencyPacingTracker); experiments/lab/ml_spike/fo8_crew_buddy.py (the small-gain prior)
**Complexity:** Medium

The secondary track, run in parallel with 15.10 on the shared machinery: a learned utility scorer over a
FIXED, observable-only crew option set — continue-to-task, buddy-toward the nearest visible/belief-trusted
group (co-presence + low own-suspicion keyed, never role — roles are hidden), patrol-toward last-seen
suspect, report, emergency (through the existing `EmergencyPacingTracker` gate semantics, not bypassing
them), repair, hold. Trained with the 15.9 ES core against the frozen scripted impostor, anchored (KL) to
`CrewmatePolicy`, evaluated under the 15.10 protocol shape (gate/referee/fitness/determinism/leak) into its
own report + jsonl. Task-ordering is EXPLICITLY OUT: the packet exposes a single engine-fed
`pending_task_id` and no owned-task set, so ordering is un-observable — this track must not widen the
observation surface; instead its report states the precise surface ask (what field, what firewall
review, what expected gain) as an input to the pause's owner-gated decision. The honest prior is FO-8's
small gain (buddy/task gate: +1 game vs the FSM) — the deliverable is a clean measurement of what
observable-option learning buys the crew, not a mandated win.

**Files in scope:**
- training/crew/__init__.py (new)
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
- training/bakeoff/harness.py + training/bakeoff/es.py (consumed read-only; if the harness needs generalizing for crew, that change lands behind 15.10's edge, and this task documents the ask instead of editing)

**Definition of done:**
- [ ] The option set is proven observable-only: every per-option feature derives from the packet + the crew agent's own memory (a test sweeps committed-corpus packets; the leak-test factory mode passes for the crew wrapper).
- [ ] Emergency semantics preserved: the learned scorer routes emergency intent through the same `EmergencyPacingTracker` gate the FSM uses — a test proves the tracker's pacing/announce bookkeeping is untouched.
- [ ] The trained scorer vs the FSM crew is measured on the fixed eval seed set against the frozen scripted impostor: mis-eject-relevant deltas (meeting-trigger quality, correct-report rate), survival, task-completion pace, win rate — reported with gate/referee/determinism columns in the jsonl, same tuple shape as 15.10.
- [ ] Anchor-KL to `CrewmatePolicy` reported for every candidate; the FO-8 prior is quoted and the measured delta stated against it.
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
survival, correctly-routed reports, buddy/patrol coverage of last-seen suspects — through the 15.3 reward
channel, plus the terminal win. "Belief-trusted group" keys on the crew agent's OWN suspicion/trust floats
(quantized, via the encoder) — the same information class that already reaches crew tactics through the
emergency gate; nothing role-derived. Run truly parallel to 15.10: disjoint files by construction, the
shared ES core consumed read-only.

**Ready-to-paste prompt:** `agent_prompts/task-15-11-crew-track.md`

### Task 15.12 — The torch PPO+recurrent probe (experiment-tier, opt-in)
**Branch:** `phase-15-torch-probe`
**Depends on:** 15.3, 15.5
**Section refs:** audits/post-phase-14-ML-training-signal.md §9 (the staged-escalation dependency posture); audits/post-phase-14-ML-planning.md §9 Option 3 (PPO/recurrent: strongest asymptotics, heavy costs); owner decision 2026-07-05 (torch as probe only; promotion is a pause decision)
**Complexity:** Medium

The owner's torch experiment, run where it cannot leak into the production posture: a PPO + recurrent
(GRU/LSTM) impostor-policy probe under `experiments/lab/torch_probe/`, executed via `uv run --with torch` —
torch never enters `pyproject.toml` dependencies or `uv.lock` this phase. The probe answers ONE question
for the pause: does gradient RL with real POMDP memory beat the pure-Python ES ceiling by enough to justify
torch's costs (dependency weight, cross-machine float determinism, CI story)? Comparability is the design
constraint: the probe trains through the SAME `TacticalRolloutEnv` and encoder-v2 features, evaluates on
the SAME fixed seed set, and reports in the 15.10 metric-tuple shape — with the honest exception that the
determinism-harness hash is expected to FAIL for a torch policy, so the probe reports a seeded-run variance
story (N repeats, spread of every metric) instead of pretending. It also measures the escape hatch:
distillability — behavior-clone the torch policy into the pure-Python inference net and report
student-teacher agreement, so Wave 2 can take the capability without the dependency if the owner wants it.
The `experiments/lab/torch_probe/` directory joins the ml_spike mypy exclusion (the pyproject exclude-regex
edit is this task's ONLY pyproject touch — the dependencies region is 15.3's).

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
- [ ] Results reported in the 15.10 tuple shape on the same fixed eval seed set, plus the reproducibility story: N seeded repeats with the spread of validity/referee/fitness/win-rate (no single-run claims).
- [ ] Distillability measured: a pure-Python student cloned from the torch policy, with student-teacher intent agreement and the student's own tuple row reported.
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
Masked action selection (the 15.3 mask) is mandatory — an unmasked PPO burns its budget on illegal actions.
Recurrence is the point of the probe (the POMDP memory the encoder carries explicitly, a GRU carries
latently) — if recurrent PPO cannot beat the utility-scorer+ES entrant on the same features, that is a
clean, valuable NO for torch promotion. Keep the run budget honest and documented; $0, local CPU (or the
operator's own GPU, documented).

**Ready-to-paste prompt:** `agent_prompts/task-15-12-torch-probe.md`

## The PAUSE

### Task 15.13 — The pause: mid-phase audit, the seven decisions, and authoring Wave 2
**Branch:** `phase-15-pause-audit`
**Depends on:** 15.8, 15.10, 15.11, 15.12
**Section refs:** audits/post-phase-14-pause.md (the pause-audit shape); tasks/phase-14.md 14.6 (the lock-decision precedent) + the phase-7 wave precedent; owner decisions 2026-07-05 (deployment + torch deferred to this pause)
**Complexity:** Integration

The wave boundary the phase was designed around: measure, decide, then author Wave 2 from evidence instead
of forecasts. Inputs (all machine-readable, all reproducible by the committed CLIs):
`results-impostor-bakeoff.jsonl` + `results-crew-track.jsonl` + `report-torch-probe.md` (per-entrant
gate/referee/fitness/KL/determinism/cost), `report-ballot-surrogate.md` (fidelity vs honest ceiling +
verdict), `report-goodhart-probe.md` (+ the 15.10 surrogate-path re-run), the corpus MANIFESTs + gate
outputs. Plus ONE fresh measurement this task runs: the operator-run REAL-LLM finalist evaluation — the top
1–2 bake-off candidates re-recorded on the canonical 50-seed 9p2i set against `Qwen/Qwen3-32B` (Featherless
$0, ~2.5h per finalist), scored by `scripts/validity_gate.py` + `scripts/measure_baseline.py
--watchability`, so the method decision rests on at least one real-meeting-path measurement, not only
fake-provider/surrogate numbers (finalist recordings are working artifacts quoted in the audit — they do
NOT replace or join `replays/samples/`). The audit (`audits/audit-phase-15-pause.md`) tabulates every
entrant on the single protocol and records the SEVEN owner decisions with rationale: (1) winning method +
champion candidate; (2) deployment end-state — opt-in factory beside the FSM default vs new default +
baseline-3 re-record; (3) torch — promote / keep experiment-tier / retire, incl. the distillation route;
(4) Wave-2 co-evolution GO/NO-GO (scoped only if GO, with the full stabilizer stack); (5) the crew
observation-surface change (owned-task set) YES/NO; (6) inference weight representation — float-hex vs
int-quantized — plus an enumeration of every determinism loosening now live; (7) the surrogate re-grounding
cadence going forward. Then this task AUTHORS the Wave-2 contracts into this file (IDs 15.14+, every
validator rule honored: full contract fields, scope-overlap edges, the CI tail), regenerates prompts, and
replaces the end-of-phase merge-criteria placeholder with the real criteria for the chosen deployment
branch.

**Files in scope:**
- audits/audit-phase-15-pause.md (new)
- tasks/phase-15.md (Wave-2 contracts + STATUS banner update + end-of-phase merge criteria)
- agent_prompts/ (mechanically regenerated task-15-* prompts for the new Wave-2 contracts — generator output, never hand-edited)

**Files NOT in scope:**
- training/ + eval/ + agents/ + engine/ + orchestrator/ (measurement is read-only; any referee patch the Goodhart findings demand becomes a Wave-2 contract, never a pause edit)
- replays/samples/ + replays/ml_corpus/ (untouched; finalist recordings live outside both)
- DESIGN.md + AGENT_IMPLEMENTATION.md (owner-side; any design amendment the decisions imply is recorded as an ask in the audit)

**Definition of done:**
- [ ] The audit tabulates every entrant (bake-off, crew, torch, distilled student) on the single metric tuple, with every quoted number regenerated from the committed CLIs/jsonl — zero hand-computed figures (each table cites its source artifact).
- [ ] The real-LLM finalist evaluation is run, its gate + referee results quoted, and its divergence (if any) from the fake-provider/surrogate numbers analyzed — the method decision explicitly cites it.
- [ ] All seven decisions are recorded with owner sign-off and rationale, including the NO paths (what was rejected and why).
- [ ] The Wave-2 contracts are authored into this file per the chosen branch, `uv run python scripts/validate_task_docs.py` + `uv run python scripts/generate_prompts.py --check` pass with the new contracts, and the STATUS banner + end-of-phase merge criteria reflect the decisions.
- [ ] The pause explicitly re-verdicts the referee: the Goodhart probe's findings (both runs) either cleared or their floors are contracted into Wave 2 before any champion selection uses the referee.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Model the audit on `audits/post-phase-14-pause.md` (label discipline, verdict-in-one-line, punch list) and
the decision block on Task 14.6's LOCKED-DECISION shape. The Wave-2 sketch at the bottom of this file is
the authoring skeleton — each bullet becomes a contract or is explicitly dropped with a reason. When
authoring contracts, re-read `scripts/_task_parser.py`'s rules (header em-dash, ID grammar, contract field
order, scope-overlap semantics, globally-unique public types) — the validator is the gate, and the new
prompts must be generator output.

**Integration risk:**

Self-certification is the trap this task exists to prevent — every number must trace to a committed
artifact, and the referee cannot bless a champion until its own red-team verdict is resolved. The second
trap is validator-invalid Wave-2 contracts: a malformed `tasks/phase-15.md` breaks
`validate_task_docs.py` for the WHOLE repo (the parser aggregates all phases), so the authoring step must
run the full check locally before the PR. Third: the finalist recordings must stay out of
`replays/samples/` and `replays/ml_corpus/` — provenance separation between "the canonical baseline," "the
frozen training corpus," and "pause working artifacts" is what keeps every later claim attributable.

**Ready-to-paste prompt:** `agent_prompts/task-15-13-pause-audit.md`

## Wave 2 — productize (contracts authored at the PAUSE; sketch only — no task headers here by design)

The pause (15.13) turns this sketch into full contracts (IDs 15.14+) per the recorded decisions. The
skeleton, in likely dependency order:

- **Champion productization.** Promote the winning method's inference into `agents/tactical/learned/`:
  pure-Python forward pass (no numpy/torch — the 15.5 firewall test already enforces it), the committed
  weights artifact + sha256, `ENCODER_VERSION` pinned, a `build_learned_agent_factory()` beside the scripted
  default, full determinism-harness + leak-test + firewall coverage. The scripted FSM stays in-tree as the
  anchor, the BC oracle, and the fallback, whatever the deployment branch.
- **Deployment, branch A — opt-in factory.** Spectator/eval/recording select the learned factory
  explicitly (config/CLI); `replays/samples/` is untouched; the 15.4 policy stamp distinguishes every
  recording. Cheapest, fully reversible.
- **Deployment, branch B — new default + baseline 3.** The learned layer becomes
  `build_default_agent_factory()`; baseline 3 is recorded (both sets, 50 seeds, one atomic PR per the 14.12
  pattern) with policy stamps, passes the validity gate + referee + byte-verification, and replaces
  `replays/samples/` as the canonical baseline; the R-gate is re-measured on it as a finding.
- **Referee hardening.** Any floors/patches the Goodhart probe demanded land in `eval/watchability.py`
  (with the parity/floor tests extended), re-anchored if baseline 3 exists.
- **Bounded co-evolution (only if the pause said GO).** Alternating/population training with the full
  stabilizer stack — Hall-of-Fame snapshots, PFSP opponent mixing, reduced virulence, per-generation
  validity gating — never the naive two-population setup FO-2 collapsed.
- **Crew surface change (only if the pause said YES).** Expose the crewmate's owned-task set on
  `ObservationPacket` behind the full firewall/leak review, then retrain crew task-ordering on the widened
  surface; emergency-uses-remaining rides the same review if taken.
- **Torch decision execution.** Promote (`uv add torch`, CI story, the distill-to-pure-Python inference
  doctrine made permanent) or retire the probe with its findings recorded in the close audit.
- **Structural-information levers** (sabotage retune, vision changes, private-evidence aggregation) stay
  owner-gated OUTSIDE Phase 15 unless the pause explicitly pulls one in — they are the known
  detection-ceiling lift, but they are balance changes, not ML work.
- **Phase close.** `audits/audit-phase-15-close.md`: gates re-run on the shipped end-state, the R-gate
  measured and reported as a finding, provenance verified end-to-end, the STATUS banner flipped to CLOSED.
