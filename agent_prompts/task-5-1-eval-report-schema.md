# Agent Prompt — 5.1 Eval report schema (with format versioning)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.1 — Eval report schema (with format versioning), anchored to DESIGN.md §11.3, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-eval-report-schema`
**Depends on:** 4.16 merged, 4.17 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §11.4
**Complexity:** Small

Define the typed tournament/eval JSON report schema consumed by all Phase 5
metrics and the dashboard. Includes a `format_version` field (carryover
from Phase 4's deferred replay-format-versioning item) so future schema
evolution is explicit rather than relying on Pydantic default-on-missing
backward compatibility.

**Files in scope:**
- eval/report_schema.py
- orchestrator/replay.py (add `format_version` field to ReplayLogEntry variants if the implementing agent decides report and replay should share a version namespace; otherwise leave replay.py untouched and version the report only)
- tests/eval/test_report_schema.py

**Files NOT in scope:**
- engine/
- agents/
- llm/ provider behavior
- api/
- frontend/
- scripts/run_tournament.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Eval report schema represents game outcomes, replay references, meeting artifacts, prompt versions, LLM cost metadata, and metric inputs.
- [ ] Schema includes a top-level `format_version: int` field, current value 1. Pydantic validator rejects unknown future versions.
- [ ] Schema supports adding Phase 5 metric outputs without changing raw replay records.
- [ ] Decision documented in `## Decisions`: whether `format_version` is namespaced to the report only OR shared across report + replay JSONL records. Either is defensible; pick and document.
- [ ] Relevant schema tests pass.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-5-eval-report-schema` with a title like `task 5.1: eval report schema (with format versioning)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
