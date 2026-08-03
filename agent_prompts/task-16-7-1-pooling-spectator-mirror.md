# Agent Prompt — 16.7.1 Spectator mirror: the pooling/citation surface end-to-end

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.7.1 — Spectator mirror: the pooling/citation surface end-to-end, anchored to tasks/phase-15.md 15.4.1 (the mirror precedent); api/schemas.py (the observation-view union + ballot DTO); api/replay_loader.py (the exhaustive claim-view mapping that raises on unknown types); frontend/src/types/api.ts (generated) + the ObservationLine renderer. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-pooling-spectator-mirror`
**Depends on:** 16.5, 16.7
**Section refs:** tasks/phase-15.md 15.4.1 (the mirror precedent); api/schemas.py (the observation-view union + ballot DTO); api/replay_loader.py (the exhaustive claim-view mapping that raises on unknown types); frontend/src/types/api.ts (generated) + the ObservationLine renderer
**Complexity:** Medium

The 15.4.1 lesson, applied on schedule this time: the replay API's observation-claim mapping is
exhaustive-with-raise by doctrine, so any recording that contains a `WhereaboutsClaim` — or a
ballot carrying `primary_reason_observation_id` — would crash or silently drop in the spectator
path unless the mirror lands BEFORE the first such recording (16.17). Mirror `WhereaboutsClaim`
through the API view union, the loader mapping, the regenerated frontend types, and the
`ObservationLine` renderer; surface the ballot's observation-citation field in the ballot DTO
(display-only). Committed sets serve byte-identically.

**Files in scope:**
- api/schemas.py (WhereaboutsClaimView + ballot citation field region)
- api/replay_loader.py (claim-view mapping region — the exhaustive raise stays exhaustive)
- frontend/src/types/api.ts (regenerated — generator output)
- frontend/src/components/ (ObservationLine + ballot-panel render regions)
- tests/api/test_replay_loader_pooling_views.py (new)

**Files NOT in scope:**
- meetings/ (schema source of truth is 16.5/16.7's; the mirror consumes)
- replays/samples/ (served bytes unchanged — pinned)

**Definition of done:**
- [ ] A fixture replay entry carrying a `WhereaboutsClaim` and an observation-cited ballot serves through the full API path and renders (view mapped, types regenerated, renderer displays); the unknown-type raise still fires on a genuinely unknown claim (the doctrine survives).
- [ ] Both committed sets load, serve, and byte-verify unchanged; the frontend type generation is clean (`tsc` green via check.sh).
- [ ] The second observation-rendering switch (the MemoryPanel path the 15-midwave review flagged as a dormant trap) either renders the new kind or is proven structurally unreachable for it — no silent blank.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone 15.4.1's commit shape: schema view → loader mapping → regenerate types → renderer → tests,
in that order. The ballot citation field is display-only — resist any spectator-side validation
logic; the manager already validated.

## Public types this task introduces
- `api.schemas.WhereaboutsClaimView`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`

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
Open a PR from branch `phase-16-pooling-spectator-mirror` with a title like `task 16.7.1: spectator mirror: the pooling/citation surface end-to-end`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-15.md 15.4.1 (the mirror precedent); api/schemas.py (the observation-view union + ballot DTO); api/replay_loader.py (the exhaustive claim-view mapping that raises on unknown types); frontend/src/types/api.ts (generated) + the ObservationLine renderer), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
