# Agent Prompt — 2.14 Win-condition resolution order (impostor-win precedence)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.14 — Win-condition resolution order (impostor-win precedence), anchored to DESIGN.md §3.5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-win-condition-order`
**Depends on:** 2.13 merged
**Section refs:** DESIGN.md §3.5
**Complexity:** Small

Change the engine win-condition evaluation order so that impostor-side
conditions (parity, sabotage timeout) are checked **before** crew-side
conditions (task completion). The intent: when an impostor kill
simultaneously triggers parity (impostors_alive >= crewmates_alive) AND
removes the last incomplete task (so `crew_tasks_done == total_tasks`
post-drop), the impostor wins. The current order resolves that
same-tick collision as a crew victory, which is counter to the design
intent that an offensive action by the impostor should attribute the
end-of-game outcome to the offense.

This is the last Phase 2 engine-substrate change before Phase 3 begins.
It is bounded to the win-condition function plus its documentation and
test pins.

**Files in scope:**
- DESIGN.md
- engine/win_conditions.py
- tests/engine/test_tick.py

**Files NOT in scope:**
- engine/tick.py
- engine/rules.py
- engine/world.py
- engine/actions.py
- engine/events.py
- engine/visibility.py
- engine/rng.py
- engine/entities.py
- engine/maps/
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
- tests/agents/
- tests/eval/
- tests/observation/
- tests/orchestrator/
- tests/engine/test_actions.py
- tests/engine/test_events.py
- tests/engine/test_map_loader.py
- tests/engine/test_rng.py
- tests/engine/test_tick_properties.py
- tests/engine/test_visibility.py
- tests/engine/test_world_state.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **DESIGN.md §3.5 reordered.** The numbered list under "Checked in order each tick:" is updated to:
  1. `count(impostors_alive) >= count(crew_alive)` → impostor win.
  2. Active sabotage with `remaining_ticks == 0` → impostor win.
  3. `crew_tasks_done == total_tasks` → crew win.
  4. Otherwise: continue.
- [ ] **DESIGN.md §3.5 dropped-rule consequence paragraph updated.** The existing paragraph (added by Task 2.10.5) documenting that an impostor kill removing the last incomplete task can trigger crew victory on the kill tick is rewritten to reflect the new ordering: a kill that simultaneously satisfies impostor parity (or sabotage timeout) AND removes the last incomplete task now resolves as an impostor win. The "kill that hands crew the win reflects impostor losing the race" framing is replaced with: a kill that triggers impostor parity wins for the impostor on the same tick; a kill that drops the last incomplete task **without** reaching parity still resolves as a crew win on the same tick.
- [ ] **`engine/win_conditions.py::evaluate_win_conditions` reordered.** The three checks now fire in the order (1) impostor parity (2) sabotage timeout (3) crew tasks. The docstring's "strict DESIGN.md §3.5 order" reference is preserved (the docstring text does not need to change beyond the function body) but the `Dead-crewmate task rule` anchor comment above the crew-tasks check is updated to note the impostor-precedence ordering: dead-task removal is still performed by `engine/tick.py::_apply_kill`, but the win check now considers impostor conditions before the (possibly reduced) crew-task total.
- [ ] **New regression test: parity-on-kill yields impostor win.** `tests/engine/test_tick.py` gains one test named `test_kill_reaching_parity_with_last_task_completion_yields_impostor_win` or equivalent. Scenario: 1 impostor (p-3) alive, 2 crewmates alive (p-1 with an already-completed task, p-2 the victim with an incomplete task), no other tasks. Impostor kills p-2. Post-kill state has 1 impostor and 1 crewmate alive (parity), and `state.tasks` contains only p-1's completed task (`crew_tasks_done == total_tasks`). Assert the returned `events` contains exactly one `GameOverEvent` with `winner == "IMPOSTORS"` and `reason == "IMPOSTOR_PARITY"`. Manually verify the test fails against the pre-fix order (revert the reorder temporarily; the test should produce `winner == "CREWMATES"`).
- [ ] **Existing R-2 test stays correct without modification.** `test_kill_removing_last_incomplete_task_triggers_crew_win_same_tick` (`tests/engine/test_tick.py:991`) keeps its scenario (1 impostor + 4 crewmates pre-kill → 1 impostor + 3 crewmates post-kill); post-kill parity is `1 >= 3` (false), so the crew-tasks branch still fires and the test still asserts `winner == "CREWMATES"`. Re-run `uv run pytest tests/engine/test_tick.py -v -k "kill_removing_last_incomplete_task or kill_reaching_parity"` and confirm both pass.
- [ ] **Tournament balance verified at new rule.** Run `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/tournament-post-2.14 --max-ticks 1000`. Record the four-bucket counts and the decisive split in the PR description's `## Decisions` block. Both decisive sides must continue to exceed 20% of decisive games per the Phase 2 Merge Criterion. If either side falls below 20%, **stop and report** — the rule change has shifted balance outside the merge criterion and needs follow-up tuning (a Task 2.14.5 or similar), not a workaround inside this PR.
- [ ] **Determinism preserved.** `tests/orchestrator/test_game.py:139-155` (default-agent 20-tick byte-identical replay) and `eval/determinism_test.py` continue to pass. The win-condition reorder changes which seeds produce which outcome (crew vs impostor) for parity-on-kill cases, but byte identity of two runs of the same fixture against itself must still hold. Verify with `uv run pytest tests/orchestrator/test_game.py eval/determinism_test.py -v`.
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
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-2-win-condition-order` with a title like `task 2.14: win-condition resolution order (impostor-win precedence)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
