# Agent Prompt — 8.15 Deadline-free headless recording + visible deadline defaults

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.15 — Deadline-free headless recording + visible deadline defaults, anchored to DESIGN.md §5.1, §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-deadline-free-recording`
**Depends on:** none (audit-repair root)
**Section refs:** DESIGN.md §5.1, §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-2
**Complexity:** Medium

Audit gp-2 (urgent): the headless recorder ran meetings with the interactive 30s per-turn/per-vote
deadlines, so slow local-Ollama calls silently defaulted 11 turns (9 of 91 openings) to
"(missed deadline; no turn submitted)" with no record of any kind — the report's failed_calls=0 was
true of the records and false of the run. Recording must never lose a turn to a wall-clock race, and
any default that does fire must be visible in the replay.

**Files in scope:**
- orchestrator/game.py (the headless recording path constructs `MeetingDeadlines(turn_seconds=None, vote_seconds=None)`; fired defaults route into the existing failed-call recording channel as `error_type="deadline_default"`)
- meetings/manager.py (surface a fired `_default_turn`/`_default_vote` to the caller; retry the opening turn once before defaulting)
- tests/meetings/test_manager.py + tests/orchestrator/test_game.py (default fires → surfaced + recorded; headless wiring passes None deadlines; the opening retry)

**Files NOT in scope:**
- meetings/schemas.py + orchestrator/replay.py (no DTO or record-kind change — `FailedCallReplayEntry.error_type` is a free string; reuse it)
- replays/samples/** (re-record is 8.18)
- llm/ (provider-level timeouts remain the fail-loud guard)

**Definition of done:**
- [ ] Headless recording runs meetings with `MeetingDeadlines(turn_seconds=None, vote_seconds=None)`; the interactive/API default stays 30s; the deadline choice is explicit at the construction site.
- [ ] A fired deadline default records a `FailedCallReplayEntry` with `error_type="deadline_default"` (meeting id, tick, defaulted phase in `error_message`) — no new replay record kind.
- [ ] The opening turn retries once before defaulting; tests cover the retry, the surfaced default, the recorded entry, and the headless None wiring.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

`MeetingDeadlines` already treats None as disabled — the work is wiring. Find where
`build_default_meeting_runner` / `DefaultMeetingRunner` construct the manager config on the headless
path and pass explicit None deadlines there. For visibility, mirror how failed LLM calls already
reach the replay log from the meeting path (the recording site in orchestrator/game.py) rather than
inventing a new channel; the manager only needs to expose enough for the orchestrator to write the
entry. Keep the `DEFAULT_TURN_FREE_TEXT` / `DEFAULT_VOTE_RATIONALE` marker strings unchanged — the
8.18 gate asserts zero of them in the new bytes.

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
Open a PR from branch `phase-8-deadline-free-recording` with a title like `task 8.15: deadline-free headless recording + visible deadline defaults`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §5.1, §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
