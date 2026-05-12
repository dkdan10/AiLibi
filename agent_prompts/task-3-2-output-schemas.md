# Agent Prompt — 3.2 Shared meeting/output schemas

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-3.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 3.2 — Shared meeting/output schemas, anchored to DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-3.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-3-output-schemas`
**Depends on:** 3.1 merged
**Section refs:** DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A
**Complexity:** Small

Centralize meeting artifacts in meetings/schemas.py. Agent strategic schemas may
re-export or wrap the shared schemas, but must not duplicate independent schema
definitions.

**Files in scope:**
- meetings/schemas.py
- agents/strategic/output_schemas.py
- tests/meetings/test_schemas.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `ReportDocument`, `Statement`, `VoteBallot`, `MeetingResult`, and contradiction/result DTOs match DESIGN.md §5.3 and §5.5.
- [ ] `agents/strategic/output_schemas.py` re-exports or wraps shared meeting schemas without duplicating them.
- [ ] Schemas are suitable for structured LLM output.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant schema tests pass.
- [ ] `uv run mypy --strict agents meetings` passes.
- [ ] `uv run ruff check .` passes.

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-3-output-schemas` with a title like `task 3.2: shared meeting/output schemas`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.3, DESIGN.md §5.5, DESIGN.md Appendix A), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
