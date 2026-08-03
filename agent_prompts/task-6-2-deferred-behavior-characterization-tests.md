# Agent Prompt — 6.2 Pin known-deferred engine and firewall behavior with characterization tests

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.2 — Pin known-deferred engine and firewall behavior with characterization tests, anchored to Audit I-I-1, I-I-2, I-I-3; DESIGN.md §11.2, §6.5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-deferred-behavior-characterization-tests`
**Depends on:** none
**Section refs:** Audit I-I-1, I-I-2, I-I-3; DESIGN.md §11.2, §6.5
**Complexity:** Medium

Three load-bearing behaviors are currently unprotected by tests, so a future
refactor could silently break them (audit Class I). This task adds
characterization tests ONLY — no production code changes, no replay-byte changes.

First, lights-out sabotage — the sole MVP sabotage — reduces visibility to
same-room-only, but no test exercises the active-sabotage branch
(`engine/visibility.py:25`): `test_visibility.py` has only two tests, both with
`sabotage=None`, and all seven `test_service.py` world states are `sabotage=None`
(I-I-1). A bug dropping the `world_state.sabotage.active` check would pass the
whole suite while letting crewmates see through a blackout.

Second, DESIGN §11.2 calls the leak test "the most important test" and mandates a
many-seeds / property-based purity sweep, but the implementation
(`eval/leak_test.py:271`) walks exactly three hand-authored fixtures (I-I-2). A
leak that manifests only under an unseen packet shape would not be caught. Add a
property-based leak sweep reusing the role-aware Hypothesis strategy from
`tests/.../test_tick_properties.py`, running `ObservationService` over every
living agent each tick across many seeds and applying the EXISTING scanners.

Third, no test pins the all-impostors-eliminated outcome
(`engine/win_conditions.py:19`): `evaluate_win_conditions` returns `None` with
zero alive impostors and incomplete tasks (the deferred gap, repro seed 49), and
a future refactor of the parity comparison could flip the zero-impostor case in
either direction with nothing failing (I-I-3). Add a characterization test that
pins the CURRENT deferred behavior with a co-located comment referencing the
design-thread gap, so Task 6.3 can flip it when it closes the gap.

**Files in scope:**
- tests/engine/test_visibility.py
- tests/observation/test_leak_property.py
- tests/engine/test_win_conditions.py

**Files NOT in scope:**
- engine/ (no production change; tests only)
- observation/ (no production change)
- eval/leak_test.py (reuse, do not modify)
- agents/
- meetings/
- replays/ (no fixture regeneration)

**Definition of done:**
- [ ] `tests/engine/test_visibility.py` gains tests asserting that with an ACTIVE lights-out sabotage: (a) `resolve_visibility_mode` returns `same_room_only`, (b) `visible_rooms_for_player` collapses to the observer's own room, (c) a player in an adjacent room becomes invisible; plus a test that an unknown sabotage kind raises `ValueError` (I-I-1).
- [ ] `tests/observation/test_leak_property.py` adds a property-based test that reuses the role-aware Hypothesis strategy from the existing tick-properties test, runs `ObservationService` for every living agent on every tick across many seeds, and applies the existing leak scanners from `eval/leak_test.py`, asserting no role/kill/engine-state field leaks (I-I-2). It imports the scanners; it does not reimplement them.
- [ ] `tests/engine/test_win_conditions.py` adds a characterization test pinning the CURRENT behavior: zero alive impostors + incomplete tasks → `evaluate_win_conditions` returns `None`. A co-located comment states this is the deferred impostor-elimination gap (memory `project_win_condition_impostor_elimination_gap`) and is flipped by Task 6.3.
- [ ] No file under `engine/`, `observation/`, or `eval/` is modified; `git diff --name-only` shows test files only.
- [ ] No replay fixture bytes change.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `engine/visibility.py` (`resolve_visibility_mode`, `visible_rooms_for_
player`, the sabotage branch around line 25), the existing
`tests/engine/test_visibility.py` for the construction idiom, and
`eval/leak_test.py` (the scanner entry points around line 271) plus the
role-aware strategy in the existing tick-properties property test. Construct the
active-sabotage `WorldState` the same way the engine tests already build states;
do not invent a new fixture format. For the leak sweep, drive
`ObservationService` exactly as production does (one packet per living agent per
tick) and feed each packet through the imported scanner functions — the value is
breadth of inputs, not new assertions. The win-condition test must assert the
present `None` return so it goes RED the moment Task 6.3 adds the elimination
case; Task 6.3 owns flipping it to assert the crew win.

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
Open a PR from branch `phase-6-deferred-behavior-characterization-tests` with a title like `task 6.2: pin known-deferred engine and firewall behavior with characterization tests`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit I-I-1, I-I-2, I-I-3; DESIGN.md §11.2, §6.5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
