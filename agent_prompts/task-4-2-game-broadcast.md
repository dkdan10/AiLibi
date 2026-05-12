# Agent Prompt — 4.2 Game broadcast

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.2 — Game broadcast, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-game-broadcast`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

api/ws.py - broadcast sanitized tick and meeting events from a running game.

**Files in scope:**
- api/ws.py
- tests/api/test_ws.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] WebSocket broadcaster streams tick and meeting events from a running game.
- [ ] Broadcast payloads are `api/schemas.py` DTOs, not raw engine internals.
- [ ] WebSocket tests prove private engine fields and replay internals are not exposed.
- [ ] Relevant API/WebSocket tests pass.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §7. WebSocket broadcaster fans out per-tick payloads to subscribers. Per-spectator view is privileged but sanitized via api/schemas.py DTOs.

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
Open a PR from branch `phase-4-game-broadcast` with a title like `task 4.2: game broadcast`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
