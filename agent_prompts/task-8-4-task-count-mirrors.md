# Agent Prompt — 8.4 api/frontend task-count mirrors

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.4 — api/frontend task-count mirrors, anchored to DESIGN.md §3.2; audits/restructure-impact-map-2026-06-04-0223.md §2a (api), §2f (mirrors). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-task-count-mirrors`
**Depends on:** 8.1, 8.3
**Section refs:** DESIGN.md §3.2; audits/restructure-impact-map-2026-06-04-0223.md §2a (api), §2f (mirrors)
**Complexity:** Medium

Update the spectator task-count surface for the uncapped per-player denominator: `api/replay_loader.py` (`_task_progress`, `_tick_view` `tasks_*_total`, `_agent_memory_view` owned-task enumeration), the `api/schemas.py` task-count fields, and their 1:1 `frontend/src/types/api.ts` mirror. Display / count only — no engine or meeting logic — but the denominator is no longer capped at 12. The TS side is caught by `tsc --noEmit`, not pytest.

**Files in scope:**
- api/replay_loader.py (`_task_progress` / `_tick_view` `tasks_required_total`/`tasks_completed_total` / `_agent_memory_view` `owned=[t for t in state.tasks.values() if t.owner==pid]`)
- api/schemas.py (`AgentMemoryView` / `TickView` task-count fields — values change, shape stays int)
- frontend/src/types/api.ts (the 1:1 task-count mirror)
- tests/api/test_schemas.py (task-count field assertions over the instance denominator)

**Files NOT in scope:**
- api/schemas.py meeting DTOs + tests/api/test_leak.py snapshot (those move with the meeting reshape in 8.10)
- engine/, observation/, agents/ (8.1 / 8.3)

**Definition of done:**
- [ ] `api/replay_loader.py` computes per-agent and spectator task counts over per-player instances (`t.owner == pid` for per-agent; `len(state.tasks)` / instance count for totals); no count is capped at 12.
- [ ] `api/schemas.py` and `frontend/src/types/api.ts` task-count fields move in lockstep (the 1:1 type mirror); `tests/api/test_schemas.py` covers the new denominator.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally (incl. frontend `tsc:check`).

## Implementation hint

Pure follow-on from 8.1's keyspace: the loader already enumerates `state.tasks.values()` and filters by `owner`, so the logic survives — only the denominator scales. Keep the api/frontend type mirror in lockstep or the field-set checks fail. Do not touch meeting DTOs here (8.10 owns those + the `test_leak.py` snapshot).

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
Open a PR from branch `phase-8-task-count-mirrors` with a title like `task 8.4: api/frontend task-count mirrors`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.2; audits/restructure-impact-map-2026-06-04-0223.md §2a (api), §2f (mirrors)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
