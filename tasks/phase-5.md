# Phase 5 — Eval And Polish

## Goal
Every prompt or rule change produces a measurable signal in a typed eval report.
Metric tasks stay parallel-safe by writing only their own modules and tests; one
integration task wires them into tournament JSON output.

## Parallelism
Task 5.1 is first. Tasks 5.2 through 5.5 can fan out after 5.1 because they
touch independent metric modules. Task 5.6 integrates them after 5.2 through
5.5 merge. Tasks 5.7 and 5.8 run after the report shape is stable.

## Tasks

### Task 5.1 — Eval report schema
**Branch:** `phase-5-eval-report-schema`
**Depends on:** Phase 4 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §11.4

Define the typed tournament/eval JSON report schema consumed by all Phase 5
metrics and the dashboard.

**Files in scope:**
- eval/report_schema.py
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- scripts/run_tournament.py
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Eval report schema represents game outcomes, replay references, meeting artifacts, prompt versions, LLM cost metadata, and metric inputs.
- [ ] Schema supports adding Phase 5 metric outputs without changing raw replay records.
- [ ] Relevant schema tests pass.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-1-eval-report-schema.md`

### Task 5.2 — Vote-correctness metric
**Branch:** `phase-5-vote-correctness-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Vote-correctness metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-2-vote-correctness-metric.md`

### Task 5.3 — Accusation-calibration metric
**Branch:** `phase-5-accusation-calibration-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Accusation-calibration metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-3-accusation-calibration-metric.md`

### Task 5.4 — Alibi-fabrication-rate metric
**Branch:** `phase-5-alibi-fabrication-rate-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Alibi-fabrication-rate metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-4-alibi-fabrication-rate-metric.md`

### Task 5.5 — Cost dashboard metric
**Branch:** `phase-5-cost-dashboard`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Per-prompt-version cost metric/dashboard data is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-5-cost-dashboard-per-prompt-version-cost.md`

### Task 5.6 — Tournament metric integration
**Branch:** `phase-5-tournament-metric-integration`
**Depends on:** 5.2 merged, 5.3 merged, 5.4 merged, 5.5 merged
**Section refs:** DESIGN.md §11.3

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Tournament JSON report includes outputs from vote correctness, accusation calibration, alibi fabrication, and cost metrics.
- [ ] Integration consumes metric module APIs rather than duplicating metric logic.
- [ ] `python scripts/run_tournament.py --N=200` produces a JSON report with all Phase 5 metrics.
- [ ] Relevant integration tests pass.
- [ ] `uv run mypy --strict eval scripts` passes if scripts are included by mypy config; otherwise `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-6-tournament-metric-integration.md`

### Task 5.7 — Tournament dashboard frontend page
**Branch:** `phase-5-tournament-dashboard-frontend-page`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §7

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Frontend dashboard renders the typed tournament JSON report.
- [ ] Dashboard includes metrics from 5.2 through 5.5.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-5-7-tournament-dashboard-frontend-page.md`

### Task 5.8 — Prompt regression test suite
**Branch:** `phase-5-prompt-regression-test-suite`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3

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
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Prompt regression tests exercise prompt versions against stable fixtures.
- [ ] Regression results are tagged by prompt version.
- [ ] Tests use recorded/fake LLM outputs and make no network calls.
- [ ] Relevant eval tests pass.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-8-prompt-regression-test-suite.md`

## Merge Criteria
- running `python scripts/run_tournament.py --N=200` produces a JSON report with all metrics.
- The frontend dashboard renders the report.
- Metric task parallelism does not require simultaneous edits to shared tournament files.
