# Agent Prompt — 4.1 FastAPI app skeleton and spectator DTOs

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.1 — FastAPI app skeleton and spectator DTOs, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-fastapi-app-skeleton`
**Depends on:** Phase 3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

api/main.py, basic routes, WebSocket endpoint registration, and sanitized API
DTO schemas per §7.

**Files in scope:**
- api/main.py
- api/schemas.py
- api/routes/games.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/__init__.py
- api/ws.py
- tests/api/test_schemas.py
- tests/api/test_routes.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] FastAPI app skeleton exists.
- [ ] Basic routes and WebSocket endpoint are registered per DESIGN.md §7.
- [ ] `api/schemas.py` defines sanitized spectator DTOs separate from engine schemas.
- [ ] DTO tests prove role, kill attribution, private cooldowns, and raw replay internals are not exposed.
- [ ] API remains a thin adapter.
- [ ] Relevant API tests pass.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §7. FastAPI app gains `/games`, `/replays`, `/eval` routes plus a WebSocket endpoint at `/ws/games/{id}`. DTOs in `api/schemas.py` are sanitized — never embed raw `WorldState`.

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
Open a PR from branch `phase-4-fastapi-app-skeleton` with a title like `task 4.1: fastapi app skeleton and spectator dtos`.
The PR description must reference DESIGN.md §7, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
