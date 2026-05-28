# Phase 5 — Eval And Polish

## Goal
Every prompt or rule change produces a measurable signal in a typed eval report.
Metric tasks stay parallel-safe by writing only their own modules and tests; one
integration task wires them into tournament JSON output. Phase closes when a
prompt-template change can be demonstrated to produce a measurable metric
delta — the regression test suite (5.8) IS the close gate.

**Scope decisions (lock these before dispatching any task):**

- **Hub + eager parallel fan-out.** Task 5.1 (eval report schema) is the hub;
  5.2–5.5 (the four independent metric modules) fan out in parallel after 5.1
  merges. Task 5.6 integrates them. After the mid-phase metric audit, 5.7
  (dashboard frontend) and 5.8 (regression suite) fan out in parallel.
- **Phase 4 carryover preludes: 4.16 and 4.17 land first.** Two
  post-Phase-4 hygiene tasks must merge BEFORE Phase 5 dispatch
  begins: Task 4.16 (ReplayLog fail-loud — fixes the silent doubled-
  files corruption pattern that would otherwise pollute every Phase 5
  metric output) and Task 4.17 (refresh-samples workflow + verify-
  samples + MANIFEST.md — provides the fixture-system substrate that
  Task 5.8's prompt regression suite needs). Format versioning is
  folded into Task 5.1 (eval report schema). The remaining Phase 4
  carryover items (belief rules 2/3/5, per-tick BeliefMatrix coverage,
  `BeliefEntryView.snapshot_tick` semantics tightening) stay
  deferred — they are not Phase 5 prerequisites and belong to a later
  agent-intelligence or UI-enrichment axis.
- **Mid-phase metric correctness audit** runs after 5.6 integrates, before
  5.7/5.8 fan out. Single-tool or two-tool with reconciliation (decide at
  audit-authoring time). Different from the Phase 4 DTO leak audit — the
  defect class is "does the metric compute what it claims?", not "does this
  DTO field leak?". Audit prompt lives at
  `audits/prompts/mid-phase-5-metric-audit-prompt.md` (to be authored after
  5.6 is in flight; do not author it prematurely against substrate that
  doesn't exist yet).
- **Performance pass deferred to 5.9.** DESIGN.md §9 names "≥ 1 game/min
  headless on a laptop" as Phase 5 scope. Lands as a discrete task AFTER the
  dashboard ships. The dashboard works at current rates; perf is polish.
- **Acceptance gate is automated, not manual.** Phase 4 closed on a manual
  UX session; Phase 5 closes on the regression suite (5.8) demonstrating
  one full prompt-change → metric-diff loop. No UX session needed.

## Parallelism
Preludes: Task 4.16 (ReplayLog fail-loud) merges first, then Task 4.17
(refresh-samples workflow + MANIFEST). Then Phase 5 begins at Task 5.1.
Tasks 5.2 through 5.5 fan out after 5.1 because they touch independent
metric modules. Task 5.6 integrates them after 5.2 through 5.5 merge.
Mid-phase metric audit runs after 5.6. Then 5.7 + 5.8 fan out in parallel.
Task 5.9 (performance pass) lands after 5.7 and 5.8.

## Tasks

### Task 5.1 — Eval report schema (with format versioning)
**Branch:** `phase-5-eval-report-schema`
**Depends on:** 4.16 merged, 4.17 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §11.4
**Complexity:** Small

Define the typed tournament/eval report schema in `eval/report_schema.py`.
This is the Phase 5 hub: every metric module (Tasks 5.2–5.5), the tournament
integration (Task 5.6), the dashboard (Task 5.7), and the regression suite
(Task 5.8) consume this one schema instead of scraping raw replay JSONL ad
hoc (DESIGN.md §11.3). It is the contract those six tasks build against, so
its field names and nesting are load-bearing — get them stable here.

The data this report must carry already exists as typed replay records
written per game during Phase 3/4 (DESIGN.md §11.4):

- `orchestrator.replay.GameEndReplayEntry` — decisive winner + reason per game.
- `orchestrator.replay.MeetingReplayEntry` — per meeting: `transcript`
  (`MeetingTranscript`), `ballots` (`tuple[VoteBallot, ...]`),
  `contradictions` (`tuple[ContradictionRef, ...]`), `outcome`
  (`MeetingOutcome`), `ejected_player_id`, `llm_calls`
  (`tuple[LLMCallRecord, ...]`), and `prompt_versions` (`Mapping[str, str]`).
- `orchestrator.replay.LLMCallRecord` — per call: `model`, `input_tokens`,
  `output_tokens`, `cost_usd`, `agent_id`, `call_kind`.
- `eval.balance_eval.BalanceReport` — current tournament-level outcome buckets
  (a frozen dataclass; see the BalanceReport decision below).

So 5.1 is largely an **aggregation + typing** task, not a from-scratch data
model: define a per-tournament Pydantic v2 artifact that composes these
existing per-game records into one typed object that downstream code reads
without re-parsing JSONL. Reuse the leaf meeting artifact types from
`meetings.schemas` (`MeetingTranscript`, `VoteBallot`, `ContradictionRef`,
`MeetingOutcome`, `PlayerId`) by import — do NOT redefine them. The `eval/`
package may import `meetings/`, `orchestrator/`, `engine/`, and `llm/`
freely; only `agents/` is firewalled from `engine/`, and this task touches
neither side of that boundary.

The schema carries a top-level `format_version: int` (carryover from Phase
4's deferred replay-format-versioning item) so future schema evolution is
explicit rather than relying on Pydantic's default-on-missing backward
compatibility. This task defines and versions the schema only. It does NOT
wire `scripts/run_tournament.py` to emit it and does NOT migrate
`run_balance_eval`'s return type — that integration is Task 5.6, which holds
`eval/balance_eval.py` and `scripts/run_tournament.py` in its scope.

**Files in scope:**
- eval/report_schema.py
- orchestrator/replay.py (add a `format_version` field to the replay entry models ONLY if the implementing agent resolves the format-version-namespace decision toward a shared namespace; the documented bias is report-only, which leaves replay.py untouched)
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/ (import its schemas; do not modify them)
- api/
- frontend/
- eval/balance_eval.py (BalanceReport migration is Task 5.6)
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- eval/meeting_quality.py
- scripts/run_tournament.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `eval/report_schema.py` defines a top-level tournament report model (Pydantic v2) that composes, per game: the decisive outcome/winner, a reference to the game's replay file, the per-meeting artifacts (transcript, ballots, contradictions, outcome, ejected player), the per-call LLM cost/usage/model metadata, and the prompt-template versions in play. These are the structured inputs Phase 5 metrics consume; the report does NOT itself compute metric outputs.
- [ ] Leaf meeting artifact types (`MeetingTranscript`, `VoteBallot`, `ContradictionRef`, `MeetingOutcome`, `PlayerId`) are imported from `meetings.schemas`, not redefined.
- [ ] The top-level model carries a `format_version: int` field whose current value is `1`. A Pydantic field validator rejects any value greater than the current version (an unknown future format) with a clear error; a value less than current is accepted only if a documented migration path exists — for v1 there is no prior version, so only `1` is valid.
- [ ] The schema is structured so Phase 5 metric outputs can be attached by downstream tooling (Task 5.6) WITHOUT changing the raw per-game replay records — i.e. metrics compose over the report, they do not mutate replay JSONL.
- [ ] All models are `extra="forbid"` and frozen, consistent with `orchestrator.replay` and `meetings.schemas` conventions.
- [ ] Decision recorded in the PR's `## Decisions` block: whether `format_version` is namespaced to the report only (bias) OR shared across report + replay JSONL records. If shared, the replay entry models in `orchestrator/replay.py` gain the field; if report-only, `replay.py` is untouched. State which and why.
- [ ] Decision recorded in the PR's `## Decisions` block: the relationship between the new Pydantic report schema and the existing `eval.balance_eval.BalanceReport` dataclass. The bias is that the Pydantic report supersedes `BalanceReport` as the typed tournament artifact (Pydantic is the project convention for cross-module DTOs per AGENTS.md), with the actual `run_balance_eval` migration deferred to Task 5.6. Confirm the report can represent everything `BalanceReport` does (outcome buckets, seeds used) so 5.6 can drop the dataclass without information loss. Do NOT edit `balance_eval.py` in this task.
- [ ] `tests/eval/test_report_schema.py` covers: round-trip serialize/deserialize of a fully populated report; the `format_version` validator accepting `1` and rejecting `2`; `extra="forbid"` rejecting an unknown field; and a report built from a realistic multi-game / multi-meeting fixture.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes (firewall preserved).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Read `orchestrator/replay.py` (the `LLMCallRecord`, `MeetingReplayEntry`,
`GameEndReplayEntry`, `FailedCallReplayEntry`, `ReplayLogEntry` models) and
`eval/balance_eval.py` (`BalanceReport`) before designing the schema. The
report is the aggregation layer over those per-game records.

A proposed model skeleton (the implementing agent may refine names, but keep
the three-level tournament → game → meeting nesting):

```python
CURRENT_FORMAT_VERSION: Final[int] = 1

class GameCostSummary(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    by_model: Mapping[str, float]  # model id -> cost_usd

class MeetingReport(BaseModel):
    # composes MeetingReplayEntry's structured payloads, reusing
    # MeetingTranscript / VoteBallot / ContradictionRef / MeetingOutcome
    ...

class GameReport(BaseModel):
    game_id: str
    seed: int
    winner: WinnerSide | None
    reason: str
    replay_ref: str            # e.g. "replay-seed-42.jsonl"
    meetings: tuple[MeetingReport, ...]
    prompt_versions: Mapping[str, str]
    cost: GameCostSummary

class TournamentReport(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    format_version: int = CURRENT_FORMAT_VERSION
    games: tuple[GameReport, ...]
    seeds_used: tuple[int, ...]

    @field_validator("format_version")
    @classmethod
    def _reject_unknown_version(cls, v: int) -> int:
        if v > CURRENT_FORMAT_VERSION:
            raise ValueError(f"unknown report format_version {v} ...")
        return v
```

Decide whether `replay_ref` is a bare filename or a relative path — match
how `run_balance_eval` names files (`replay-seed-{seed}.jsonl`). Do not
build a loader that reads JSONL into this schema in this task; that adapter
lands in Task 5.6. This task ships the schema + its validator + unit tests
only. Construct test fixtures by instantiating the models directly, not by
running a tournament.

**Public types introduced:**
- eval.report_schema.TournamentReport
- eval.report_schema.GameReport
- eval.report_schema.MeetingReport
- eval.report_schema.GameCostSummary
- eval.report_schema.CURRENT_FORMAT_VERSION

**Integration risk:**

This schema is the convergence point for all of Phase 5 — 5.2–5.8 build on
it. Breaking or reshaping it later breaks every downstream consumer.

- **Name stability is the real risk, not code volume.** The task is small to
  implement but high-leverage: a field rename after 5.2–5.5 ship forces a
  six-way edit. Get the nesting and field names right here; that is why this
  task carries the `format_version` field from day one.
- **Do not over-reach into integration.** The temptation is to also write the
  JSONL→report loader and wire `run_tournament.py`. That is Task 5.6 and is
  explicitly out of scope. A loader written here against an un-merged
  integration would be dead code the audit has to reconcile.
- **Reuse, don't fork, meeting artifact types.** Redefining
  `MeetingTranscript` / `VoteBallot` in `eval/` would create two
  drifting definitions of the same payload. Import from `meetings.schemas`.
- **The format-version validator must fail loud** (AGENTS.md "no silent
  fallbacks"): an unknown future version raises, it does not coerce or warn.
- **BalanceReport coexists until 5.6.** Leaving `balance_eval.py` untouched
  means `BalanceReport` and the new report briefly overlap. That is
  intentional — the migration is sequenced into 5.6 so this task stays a
  pure additive schema definition with no behavioral change to the tournament
  path.

**Ready-to-paste prompt:** `agent_prompts/task-5-1-eval-report-schema.md`

### Task 5.2 — Vote-correctness metric
**Branch:** `phase-5-vote-correctness-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

Vote-correctness metric.

**Files in scope:**
- eval/vote_correctness.py
- tests/eval/test_vote_correctness.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Vote-correctness metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §11.3. Vote correctness = ejected_player.role == "IMPOSTOR" AND ejection rationale cites a real contradiction or kill witness. Pure analyzer over eval/report_schema records — no engine or LLM dependencies.

**Ready-to-paste prompt:** `agent_prompts/task-5-2-vote-correctness-metric.md`

### Task 5.3 — Accusation-calibration metric
**Branch:** `phase-5-accusation-calibration-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

Accusation-calibration metric.

**Files in scope:**
- eval/accusation_calibration.py
- tests/eval/test_accusation_calibration.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/vote_correctness.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Accusation-calibration metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §11.3. Bin accusations by confidence and compute actual-impostor-rate per bin. Calibrated when high-confidence accusations are correct more often than low-confidence ones.

**Ready-to-paste prompt:** `agent_prompts/task-5-3-accusation-calibration-metric.md`

### Task 5.4 — Alibi-fabrication-rate metric
**Branch:** `phase-5-alibi-fabrication-rate-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

Alibi-fabrication-rate metric.

**Files in scope:**
- eval/alibi_fabrication.py
- tests/eval/test_alibi_fabrication.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Alibi-fabrication-rate metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §11.3. Count impostor alibis that survive the contradiction detector. Pure analyzer over meeting transcripts.

**Ready-to-paste prompt:** `agent_prompts/task-5-4-alibi-fabrication-rate-metric.md`

### Task 5.5 — Cost dashboard metric
**Branch:** `phase-5-cost-dashboard`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

Cost metric data by prompt version.

**Files in scope:**
- eval/cost_dashboard.py
- tests/eval/test_cost_dashboard.py

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- scripts/run_tournament.py
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Per-prompt-version cost metric/dashboard data is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §10.4. Aggregate `llm.budget` records by prompt version × game; emit cost-per-game and cost-per-prompt-version.

**Ready-to-paste prompt:** `agent_prompts/task-5-5-cost-dashboard-per-prompt-version-cost.md`

### Task 5.6 — Tournament metric integration
**Branch:** `phase-5-tournament-metric-integration`
**Depends on:** 5.2 merged, 5.3 merged, 5.4 merged, 5.5 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Integration

Wire Phase 5 metric modules into the tournament JSON report after the parallel
metric tasks have merged.

**Files in scope:**
- eval/meeting_quality.py
- eval/balance_eval.py
- scripts/run_tournament.py
- tests/eval/test_tournament_report.py

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- eval/vote_correctness.py
- eval/accusation_calibration.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Tournament JSON report includes outputs from vote correctness, accusation calibration, alibi fabrication, and cost metrics.
- [ ] Integration consumes metric module APIs rather than duplicating metric logic.
- [ ] `python scripts/run_tournament.py --N=200` produces a JSON report with all Phase 5 metrics.
- [ ] Relevant integration tests pass.
- [ ] `uv run mypy --strict eval scripts` passes if scripts are included by mypy config; otherwise `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §11.3. Read all metric outputs from 5.2–5.5 and fold them into the unified `eval.report_schema` artifact emitted by `scripts/run_tournament.py`.

**Integration risk:**

Convergence point for Phase 5 metrics. Each metric module ships independently; this task wires them. Risk: breaking the report_schema breaks every downstream consumer (dashboard, regression tests). Add the schema-version field early.

**Ready-to-paste prompt:** `agent_prompts/task-5-6-tournament-metric-integration.md`

### Mid-phase metric correctness audit

After 5.6 merges, run the Phase 5 mid-phase metric correctness audit
before dispatching 5.7 and 5.8. The audit prompt lives at
`audits/prompts/mid-phase-5-metric-audit-prompt.md` (to be authored
after 5.6 is in flight; do not author it prematurely against substrate
that doesn't exist yet).

**Audit scope:**
- For each metric in `eval/` (`vote_correctness`, `accusation_calibration`,
  `alibi_fabrication`, `cost_dashboard`): does the computed number match
  the docstring claim? Construct a synthetic fixture replay where the
  ground-truth metric value is known by inspection; confirm the metric
  matches.
- Partial-replay robustness: does each metric handle replays with no
  meetings, ejected impostors, partial runs (no `game_over` record)?
- Schema integrity: does the `eval.report_schema` artifact emitted by
  `scripts/run_tournament.py` validate against the 5.1 schema? Are
  there fields populated that the schema doesn't promise, or schema
  fields that the integration leaves empty?
- Prompt-version provenance: does the report correctly attribute each
  metric value to the prompt-template versions in play?

**Audit verdict shape:** "Mid-phase metric audit passes — proceed to
fan out 5.7 + 5.8" OR "Mid-phase metric audit blocks fan-out —
repair tasks required: ..."

Two-tool with reconciliation (per the Phase 4 pattern) is the
recommended shape; single-tool is acceptable if the audit surface is
small. Output: one Markdown audit at
`audits/audit-YYYY-MM-DD-HHMM-mid-phase-5-metric.md`.

### Task 5.7 — Tournament dashboard frontend page
**Branch:** `phase-5-tournament-dashboard-frontend-page`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §7
**Complexity:** Medium

Tournament dashboard frontend page.

**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/ unless a read endpoint already exists and needs wiring
- eval/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Frontend dashboard renders the typed tournament JSON report.
- [ ] Dashboard includes metrics from 5.2 through 5.5.
- [ ] Frontend build/check command passes if configured.


**Implementation hint:**

See DESIGN.md §7. React + PixiJS dashboard reading the eval report.

**Ready-to-paste prompt:** `agent_prompts/task-5-7-tournament-dashboard-frontend-page.md`

### Task 5.8 — Prompt regression test suite
**Branch:** `phase-5-prompt-regression-test-suite`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Integration

Prompt regression test suite.

**Files in scope:**
- eval/prompt_regression.py
- tests/fixtures/prompt_regression/
- tests/eval/test_prompt_regression.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- llm/ provider behavior
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Prompt regression tests exercise prompt versions against stable fixtures.
- [ ] Regression results are tagged by prompt version.
- [ ] Tests use recorded/fake LLM outputs and make no network calls.
- [ ] Relevant eval tests pass.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §11.3. For each prompt version × fixed seed set, compare metric deltas against a baseline. Block merge on regression > X%.

**Integration risk:**

Determinism is essential — flaky tests destroy the regression signal. Use the fake LLM provider with recorded outputs; never call a real model in CI.

**Ready-to-paste prompt:** `agent_prompts/task-5-8-prompt-regression-test-suite.md`

### Task 5.9 — Performance pass
**Branch:** `phase-5-performance-pass`
**Depends on:** 5.7 merged, 5.8 merged
**Section refs:** DESIGN.md §9
**Complexity:** Medium

Hit the DESIGN.md §9 Phase 5 target: ≥ 1 headless game per minute on a
laptop. Measure current rate; identify bottlenecks; apply targeted
fixes (engine hot paths, observation packet construction, replay-write
cadence, LLM-call concurrency limits). The performance pass is polish
work — the dashboard and regression suite ship at the current rate.

**Files in scope:**
- engine/ (hot paths only; no behavior change)
- orchestrator/ (concurrency tuning)
- eval/ (benchmark harness if needed)
- tests/eval/test_performance.py (or similar benchmark recording)
- scripts/run_tournament.py (only if perf surfaces a tuning knob)

**Files NOT in scope:**
- agents/ behavior (FSM or strategic prompt changes)
- llm/ provider behavior
- api/, frontend/ (perf affects engine + orchestrator, not the spectator UI which is read-only)
- meetings/ behavior (cap raises etc. are Phase 3 territory)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Benchmark recorded showing the BEFORE rate (game/min on the target laptop hardware).
- [ ] Bottlenecks identified via profiling (cProfile or py-spy output captured in `## Decisions`).
- [ ] Targeted fixes applied; no behavior change (determinism tests still pass byte-identically).
- [ ] Benchmark recorded showing the AFTER rate; meets or exceeds ≥ 1 game/min.
- [ ] No regression in any existing test, including determinism + leak tests.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes.


**Implementation hint:**

DESIGN.md §9 names "≥ 1 game/min headless on a laptop" as the target. The current rate is unmeasured; the implementing agent's first action is to record a baseline. Profile with `cProfile` or `py-spy`; the hot paths are likely (a) observation packet construction (called per agent per tick), (b) replay JSONL serialization (per-tick write), (c) state-hash computation. Avoid premature optimization — only target paths that appear in the profile output.

**Integration risk:**

- **Determinism must hold.** Any change to engine hot paths risks breaking byte-identical replay determinism. Determinism tests are the load-bearing gate.
- **Single-laptop variance.** Benchmarks on different hardware will differ. Pin the BEFORE and AFTER runs to the same hardware; document the hardware in `## Decisions`.
- **No behavior change.** This task does NOT modify agent reasoning, prompt content, FSM rules, or LLM behavior. Perf-only.

**Ready-to-paste prompt:** `agent_prompts/task-5-9-performance-pass.md`

## Merge Criteria
- **Preludes landed:** Tasks 4.16 (ReplayLog fail-loud) and 4.17 (refresh-samples workflow + MANIFEST) merged before any Phase 5 task.
- **Schema-driven reporting:** running `python scripts/run_tournament.py --N=200` produces a JSON report with all Phase 5 metrics (5.2–5.5) validated against the 5.1 schema.
- **Dashboard renders:** the frontend tournament dashboard renders the report end-to-end.
- **Mid-phase metric audit passes** before 5.7/5.8 fan-out.
- **Close gate:** the prompt regression suite (5.8) demonstrates one full loop — a prompt-template change produces a measurable metric delta in the tournament report. This is the Phase 5 acceptance criterion; no manual UX session.
- **Performance target met:** ≥ 1 headless game/min on the target laptop (Task 5.9).
- **Metric task parallelism preserved:** 5.2–5.5 do not require simultaneous edits to shared tournament files; 5.7/5.8 do not require simultaneous edits to shared frontend files.
- **All Phase 4 static + behavioral gates still green:** `bash scripts/check.sh`, determinism tests, leak tests, frontend `tsc:check` + `vite build`.
