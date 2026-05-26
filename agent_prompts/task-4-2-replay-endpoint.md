# Agent Prompt — 4.2 Replay listing + fetch endpoint

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.2 — Replay listing + fetch endpoint, anchored to DESIGN.md §7, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-replay-endpoint`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7, DESIGN.md §11.4
**Complexity:** Small

REST endpoints that read saved JSONL replays from disk and return
sanitized DTOs. No WebSocket; no live game stream. This is the
substrate the entire frontend consumes.

**Files in scope:**
- api/routes/replays.py
- api/replay_loader.py
- tests/api/test_replays.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- frontend/
- api/ws.py
- orchestrator/replay.py (consumed read-only; not modified)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `GET /replays` returns sanitized metadata for every saved replay (game id, winner, total ticks, meeting count, total cost, prompt versions).
- [ ] `GET /replays/{id}` returns the full sanitized tick + meeting timeline for one replay.
- [ ] `GET /replays/{id}/meetings/{meeting_id}` returns a single meeting's sanitized transcript (reports, statements, ballots, contradiction flags, LLM cost metadata).
- [ ] Leak tests cover every endpoint: no role, kill attribution, private cooldowns, or raw `ReplayEntry` internals.
- [ ] Reader handles partial replays (no game-end record per Task 3.19) — surfaces `winner=null` cleanly, doesn't crash.
- [ ] Relevant API tests pass.
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

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-4-replay-endpoint` with a title like `task 4.2: replay listing + fetch endpoint`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
