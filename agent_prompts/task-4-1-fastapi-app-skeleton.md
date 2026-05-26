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

`api/main.py`, REST routes for replay listing / fetch, and sanitized
spectator DTOs per §7. No WebSocket in MVP (live game streaming
deferred per phase scope decision above).

**Files in scope:**
- api/main.py
- api/schemas.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/__init__.py
- tests/api/test_schemas.py
- tests/api/test_routes.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- api/ws.py (deferred — no WebSocket in MVP)
- api/routes/games.py (live game streaming deferred)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] FastAPI app skeleton exists with REST routes registered per DESIGN.md §7 (replays, eval; games-live deferred).
- [ ] `api/schemas.py` defines the concrete DTO inventory (the elaboration of this task — to be filled before dispatch — must list every DTO with its fields and explicitly mark fields that exist in the engine but are deliberately excluded).
- [ ] DTO leak tests prove role, kill attribution, private cooldowns, observation-firewall internals, and raw replay JSONL internals are not exposed.
- [ ] Replay listing endpoint returns sanitized replay metadata; replay fetch endpoint returns a sanitized tick + meeting timeline for a single saved replay.
- [ ] API remains a thin adapter — no engine logic in `api/`.
- [ ] Relevant API tests pass.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §7. FastAPI app gains `/replays` (list + fetch) and `/eval` routes. DTOs in `api/schemas.py` are sanitized — never embed raw `WorldState`, raw `ReplayEntry`, or engine-internal types. Mirror the firewall pattern from `observation/` — DTOs are a sanitized view over engine state, never the state itself.

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
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
