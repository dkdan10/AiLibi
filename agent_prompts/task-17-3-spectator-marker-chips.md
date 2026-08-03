# Agent Prompt — 17.3 Spectator chips for the coercion + nulled-observation markers

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.3 — Spectator chips for the coercion + nulled-observation markers, anchored to audits/audit-phase-16-close.md §8 (routed contract (c)); api/replay_loader.py:2425 `_BALLOT_PREFIX_MARKERS` (the registration table + `_marker_pattern`); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` + `INVALID_OBSERVATION_ID_MARKER` (the two unregistered audit rewrites, both live on committed bytes); tasks/phase-15.md 15.4.1 (the mirror precedent). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-spectator-marker-chips`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (routed contract (c)); api/replay_loader.py:2425 `_BALLOT_PREFIX_MARKERS` (the registration table + `_marker_pattern`); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` + `INVALID_OBSERVATION_ID_MARKER` (the two unregistered audit rewrites, both live on committed bytes); tasks/phase-15.md 15.4.1 (the mirror precedent)
**Complexity:** Medium

Two ballot audit-trail rewrites now fire on committed bytes but are invisible in the
spectator's `BallotView.rewrite_reasons` chips: the 16.6 coercion marker and the 16.5
nulled-observation marker. Register both in `_BALLOT_PREFIX_MARKERS` with chip labels
following the table's existing label style, regenerate the frontend types if the label
union is typed, and render them through the existing chip surface. Committed sets serve
byte-identically (view-layer only).

**Files in scope:**
- api/replay_loader.py (`_BALLOT_PREFIX_MARKERS` — two rows; markers imported from meetings.manager)
- frontend/src/ (chip label handling if labels are enumerated; regenerated types)
- tests/api/ (chip extraction fixtures for both markers, incl. stacked)

**Files NOT in scope:**
- meetings/ (marker literals are production truth)
- replays/samples/ (served bytes unchanged — pinned)

**Definition of done:**
- [ ] A committed baseline-5 ballot carrying each marker serves with the corresponding chip in `rewrite_reasons` (the two live cases found on the committed sets are the fixtures); stacked markers yield both chips in stack order.
- [ ] Both committed sets load, serve, and byte-verify unchanged; frontend type generation clean (`tsc` green via check.sh).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone the existing marker rows — `_marker_pattern` already handles the `{x!r}` repr
interpolation. Chip label text follows the table's register (short snake_case labels);
if the frontend enumerates labels, extend the enum rather than widening to bare string.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-17-spectator-marker-chips` with a title like `task 17.3: spectator chips for the coercion + nulled-observation markers`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §8 (routed contract (c)); api/replay_loader.py:2425 `_BALLOT_PREFIX_MARKERS` (the registration table + `_marker_pattern`); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` + `INVALID_OBSERVATION_ID_MARKER` (the two unregistered audit rewrites, both live on committed bytes); tasks/phase-15.md 15.4.1 (the mirror precedent)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
