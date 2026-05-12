# Agent Prompt — 5.6 Tournament metric integration

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.6 — Tournament metric integration, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

See DESIGN.md §11.3. Read all metric outputs from 5.2–5.5 and fold them into the unified `eval.report_schema` artifact emitted by `scripts/run_tournament.py`.

## Integration risk

Convergence point for Phase 5 metrics. Each metric module ships independently; this task wires them. Risk: breaking the report_schema breaks every downstream consumer (dashboard, regression tests). Add the schema-version field early.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-5-tournament-metric-integration` with a title like `task 5.6: tournament metric integration`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
