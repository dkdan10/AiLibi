# Agent Prompt — 2.13 Pre-Phase-3 post-audit cleanup

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.13 — Pre-Phase-3 post-audit cleanup, anchored to DESIGN.md §3.5, DESIGN.md §4.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-post-audit-cleanup`
**Depends on:** 2.12 merged
**Section refs:** DESIGN.md §3.5, DESIGN.md §4.4
**Complexity:** Small

Close the three actionable findings in
`audits/audit-2026-05-16-0036-reconciled.md` §10 that block a clean
DESIGN.md → code agreement and pin two documented-but-untested
behaviors before Phase 3 begins: R-1 (DESIGN.md §3.5 names
`tasks_per_crewmate` as a `seed_initial_state` parameter that does
not exist), R-2 (the `dropped` rule's same-tick crew-win consequence
is documented but unpinned), and R-3 (the
`_confirmed_dead_from_bodies` `ValueError` branch for malformed
`saw_body` payloads is uncovered). Optionally close R-7 (the
`"victim-body"` synthetic body-id string still appears at
`tests/observation/test_service.py:343, 358`). R-4, R-5, R-6 from
the same audit are explicitly out of scope — they are already wired
into Phase 3 task DoDs (3.3, 3.9, 3.12) for retirement or
enforcement during Phase 3 implementation.

No runtime code touched. The diff is one documentation edit, two
new regression tests, and (optionally) one mechanical rename of an
internal test-helper body-id string. None of the changes alter
behavior.

**Files in scope:**
- DESIGN.md
- tests/engine/test_tick.py
- tests/agents/test_impostor_policy.py
- tests/observation/test_service.py

**Files NOT in scope:**
- engine/
- observation/
- orchestrator/
- agents/
- llm/
- api/
- frontend/
- eval/
- scripts/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/agents/test_crewmate_policy.py
- tests/agents/test_memory.py
- tests/agents/test_pathing.py
- tests/agents/test_perception.py
- tests/agents/test_runtime.py
- tests/engine/test_actions.py
- tests/engine/test_events.py
- tests/engine/test_map_loader.py
- tests/engine/test_rng.py
- tests/engine/test_tick_properties.py
- tests/engine/test_visibility.py
- tests/engine/test_world_state.py
- tests/eval/
- tests/observation/test_boundary_contracts.py
- tests/orchestrator/
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-1 — DESIGN.md §3.5 `tasks_per_crewmate` drift resolved:** Edit the tuning-lever paragraph at `DESIGN.md:291` (the `(2) tasks_per_crewmate ∈ {2, 3}` line and the "Current canonical default" line that names `tasks_per_crewmate=1`). Replace the parenthetical "(a parameter on `orchestrator.seeder.seed_initial_state`)" with the explicit dependency: "(would require parameterizing `orchestrator.seeder.seed_initial_state`; currently hardcoded to one task per crewmate by `_build_tasks`)". Edit the "Current canonical default" line to drop `tasks_per_crewmate=1` and reflect only what is actually canonical: `kill_cooldown_ticks=4` and `sabotages.lights.duration_ticks=90`. The lever stays documented (preserves Path A search-space history); only the implementation claim is corrected.
- [ ] **R-2 — same-tick crew-win regression pinned:** `tests/engine/test_tick.py` gains one regression test (~20 lines) named `test_kill_removing_last_incomplete_task_triggers_crew_win_same_tick` or equivalent. The test constructs a `WorldState` with exactly one incomplete task owned by the kill victim and zero other incomplete tasks (i.e. all surviving alive-owned tasks are completed), advances through a `KillAction`, and asserts the returned `events` tuple contains a `GameOverEvent` with `winner == "CREWMATES"` and `reason == "CREWMATE_TASKS"`. The test must fail if `engine/tick.py::_apply_kill`'s task-drop logic is reverted (manually verify by temporarily commenting out the incomplete-task removal and confirming the test fails, then restoring).
- [ ] **R-3 — `_confirmed_dead_from_bodies` missing-payload branch pinned:** `tests/agents/test_impostor_policy.py` gains one unit test (~10 lines) named `test_confirmed_dead_from_bodies_raises_on_missing_body_id` or equivalent. The test constructs a `saw_body` `EpisodicEvent` whose `payload` either omits `body_id` (e.g. `payload={"room": "MEDBAY"}`) or sets `body_id` to a non-string (e.g. `payload={"body_id": None}`), and asserts `ImpostorPolicy._confirmed_dead_from_bodies` raises `ValueError`. Use the existing `_saw_body_event` test helper only if it can be invoked with the missing-payload shape; otherwise construct the `EpisodicEvent` directly to bypass the helper's `body_id: str` typing.
- [ ] **[Optional] R-7 — rename the `"victim-body"` synthetic body-id string:** `tests/observation/test_service.py` lines 343 and 358 use `"victim-body"` as the `BodyState.id` value in body-discovery filter tests. Rename to `"body-p-1-0"` (matches the canonical engine format from `engine/rules.py:69`'s `f"body-{target.id}-{state.tick}"`). The scenario semantics are unchanged. **Skip without penalty** if the existing PR #33 `## Decisions` acceptance is judged sufficient; the string does not match the post-2.11 grep guard or trip the leak scanner.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.balance_eval"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.seeder"`
- `uv run python -c "import orchestrator.scheduler"`
- `uv run python -c "import agents.tactical.impostor_policy"`
- `uv run python -c "import agents.tactical.pathing"`
- `uv run python -c "import agents.perception"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.working"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import agents.base"`
- `uv run python -c "import agents.runtime"`
- `uv run python -c "import observation.action_intent"`
- `uv run python -c "import observation.public_map"`
- `uv run python -c "import orchestrator.boundary"`
- `uv run python -c "import agents.tactical.crewmate_policy"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
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
Open a PR from branch `phase-2-post-audit-cleanup` with a title like `task 2.13: pre-phase-3 post-audit cleanup`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5, DESIGN.md §4.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
