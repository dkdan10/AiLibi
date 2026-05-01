# Phase 5 — Eval And Polish

## Goal
Every prompt or rule change produces a measurable signal in the eval dashboard.

## Parallelism
Mostly parallel. 5.1 through 5.4 are independent files in eval/ and can fan out.

## Tasks
### Task 5.1 — Vote-correctness metric
**Branch:** `phase-5-vote-correctness-metric`
**Depends on:** Phase 4 merged
**Section refs:** DESIGN.md §11.3

Vote-correctness metric.

**Files in scope:**
- eval/TODO_REVIEW vote-correctness metric file

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Vote-correctness metric is implemented against replay/eval data.
- [ ] Metric is included in tournament JSON report.
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-1-vote-correctness-metric.md`

### Task 5.2 — Accusation-calibration metric
**Branch:** `phase-5-accusation-calibration-metric`
**Depends on:** Phase 4 merged
**Section refs:** DESIGN.md §11.3

Accusation-calibration metric.

**Files in scope:**
- eval/TODO_REVIEW accusation-calibration metric file

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Accusation-calibration metric is implemented against replay/eval data.
- [ ] Metric is included in tournament JSON report.
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-2-accusation-calibration-metric.md`

### Task 5.3 — Alibi-fabrication-rate metric
**Branch:** `phase-5-alibi-fabrication-rate-metric`
**Depends on:** Phase 4 merged
**Section refs:** DESIGN.md §11.3

Alibi-fabrication-rate metric.

**Files in scope:**
- eval/TODO_REVIEW alibi-fabrication-rate metric file

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Alibi-fabrication-rate metric is implemented against replay/eval data.
- [ ] Metric is included in tournament JSON report.
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-3-alibi-fabrication-rate-metric.md`

### Task 5.4 — Cost dashboard (per-prompt-version cost)
**Branch:** `phase-5-cost-dashboard`
**Depends on:** Phase 4 merged
**Section refs:** DESIGN.md §11.3

Cost dashboard per prompt-version cost.

**Files in scope:**
- eval/TODO_REVIEW cost dashboard metric file

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Per-prompt-version cost metric/dashboard data is implemented.
- [ ] Cost data is included in tournament JSON report.
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-4-cost-dashboard-per-prompt-version-cost.md`

### Task 5.5 — Tournament dashboard frontend page
**Branch:** `phase-5-tournament-dashboard-frontend-page`
**Depends on:** 5.1 merged, 5.2 merged, 5.3 merged, 5.4 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §7

Tournament dashboard frontend page.

**Files in scope:**
- frontend/src/TODO_REVIEW tournament dashboard page path

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/ unless a read endpoint already exists and needs wiring
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Frontend dashboard renders the tournament JSON report.
- [ ] Dashboard includes metrics from 5.1 through 5.4.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-5-5-tournament-dashboard-frontend-page.md`

### Task 5.6 — Prompt regression test suite
**Branch:** `phase-5-prompt-regression-test-suite`
**Depends on:** Phase 4 merged
**Section refs:** DESIGN.md §11.3

Prompt regression test suite.

**Files in scope:**
- eval/TODO_REVIEW prompt regression test file
- tests/TODO_REVIEW prompt regression fixtures path

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
- [ ] Relevant eval tests pass.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-5-6-prompt-regression-test-suite.md`

## Merge Criteria
- running python scripts/run_tournament.py --N=200 produces a JSON report with all metrics.
- The frontend dashboard renders the report.
