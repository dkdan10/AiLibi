# Agent Prompt — 2.10.5 Phase 2 tournament balance

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.10.5 — Phase 2 tournament balance, anchored to DESIGN.md §3.5, DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-tournament-balance`
**Depends on:** 2.10 merged
**Section refs:** DESIGN.md §3.5, DESIGN.md §11.3
**Complexity:** Medium

Close R-1 from `audits/audit-2026-05-15-0225-reconciled.md`. PR #30 (Task
2.10) closed R-3 and R-5 and unblocked the six-seed sweep (R-2), but
discovered that the tactical fix alone is insufficient for the 100-game
tournament merge criterion: with current canonical parameters
(`kill_cooldown_ticks=10`, one task per crewmate, 90-tick lights
sabotage), the impostor cannot reach a second kill before the alive
crewmates finish their tasks. The tournament now terminates at
`CREWMATES=87% IMPOSTORS=0%` instead of the required `>20%/>20%`. R-1's
original recommended action (in `audits/audit-2026-05-15-0225-reconciled.md:190-195`)
assumed the fix lived in tactics; it did not. This task addresses the
remaining structural imbalance.

The repair is split into a bounded parameter-tuning attempt (Path A) and
a merge-criterion amendment fallback (Path D). Try Path A first; fall
back to Path D only if no candidate config in the Path A search space
satisfies the criterion. This task is **not** a feature task — it does
not add crewmate sabotage repair, impostor sabotage tactics, or ghost
mechanics. Those are deferred to Phase 4+.

This task also documents one consequence of the R-5 `dropped` rule that
PR #30's review surfaced but did not address: an impostor kill that
removes the last incomplete task from `state.tasks` triggers the crew
win condition on that tick. This is structural — the alternative rules
(kill-tick suppression, ghost mechanics) either delay the outcome by one
tick without changing it or re-introduce the `still-required` problem
that R-5 explicitly rejected. The consequence is documented as expected
behavior in DESIGN.md §3.5 alongside the `dropped` rule.

**Files in scope:**
- engine/maps/canonical_1.yaml
- orchestrator/seeder.py
- DESIGN.md
- tests/eval/test_balance_eval.py
- tests/orchestrator/test_seeder.py
- tests/orchestrator/test_game.py
- tests/engine/test_map_loader.py
- tests/engine/test_world_state.py
- tasks/phase-2.md
- tasks/phase-3.md

**Files NOT in scope:**
- engine/tick.py
- engine/win_conditions.py
- engine/rules.py
- engine/world.py
- engine/actions.py
- engine/events.py
- engine/visibility.py
- engine/rng.py
- engine/entities.py
- observation/
- agents/
- orchestrator/game.py
- orchestrator/replay.py
- orchestrator/scheduler.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- eval/leak_test.py
- eval/determinism_test.py
- eval/balance_eval.py
- scripts/
- llm/
- api/
- frontend/
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/engine/test_actions.py
- tests/engine/test_events.py
- tests/engine/test_rng.py
- tests/engine/test_tick.py
- tests/engine/test_tick_properties.py
- tests/engine/test_visibility.py
- tests/agents/
- tests/observation/
- tests/orchestrator/test_action_ordering.py
- tests/orchestrator/test_boundary.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **Path A — search space documented:** A short subsection added to DESIGN.md §3.5 (or a new §11.3 sub-bullet) names the Phase 2 tuning levers and the mechanical search order. The order is: (1) `kill_cooldown_ticks ∈ {6, 5, 4, 3}` only, all other parameters held at canonical defaults; (2) `tasks_per_crewmate ∈ {2, 3}` paired with `kill_cooldown_ticks ∈ {6, 4}`; (3) `sabotages.lights.duration_ticks ∈ {60, 30}` paired with `kill_cooldown_ticks=4` and `tasks_per_crewmate=2`. After each candidate config, run the 100-game tournament. The first config that satisfies the criterion (see next bullet) is the answer.
- [ ] **Path A — acceptance criterion:** A candidate config "balances" if a 100-game tournament against that config produces both `CREWMATES%` > 20% and `IMPOSTORS%` > 20% of decisive games (the existing Phase 2 Merge Criterion at `tasks/phase-2.md:1389`). Record the full search trace (every config tried, the tournament's four-bucket counts, the decisive split) in the PR description's `## Decisions` block — do not summarize.
- [ ] **Path A — committed config:** If Path A succeeded, commit the balancing config: `engine/maps/canonical_1.yaml` for cooldown / sabotage changes, and `orchestrator/seeder.py::_build_tasks` for tasks-per-crewmate changes. If the seeder is changed, add a `tasks_per_crewmate: int = N` parameter to `seed_initial_state` (default = the balancing value) so all existing call sites inherit the new default without explicit threading. The default must match the chosen config; document the default in DESIGN.md.
- [ ] **Path A — regression test:** If Path A succeeded, `tests/eval/test_balance_eval.py` adds a regression test that runs a small-N (≥ 10-game) tournament at the committed config and asserts both decisive buckets are non-empty (`crew_wins > 0 AND impostor_wins > 0`). Test name: `test_canonical_balance_keeps_both_sides_alive` or equivalent. The N-game test is not a full 100-game gate (that lives in the merge criterion); it is a fast canary.
- [ ] **Path A → Path D trigger:** If no config in the Path A search space satisfies the criterion after running every candidate exhaustively, do NOT continue tuning. Stop at Path A's last candidate, record the full search trace as documented above, and proceed to the Path D bullets below.
- [ ] **Path D — Phase 2 Merge Criteria amended:** `tasks/phase-2.md` Phase 2 Merge Criteria block (lines ~1389-1392, after the Task 2.10/2.10.5/2.11/2.12 entries) is replaced with: *"Games reach a decisive outcome (`CREWMATES`, `IMPOSTORS`) or `MEETING_PHASE_REACHED` in > 90% of seeds in a 100-game tournament; `TICK_BUDGET_REACHED` < 10% of games. Leak test passes across all games. The `both decisive sides > 20%` rule is deferred to Phase 3, when meetings and voting introduce additional win paths."* The 100-game tournament against the canonical config must satisfy the new criterion; record the four-bucket counts in the PR description.
- [ ] **Path D — Phase 3 inherits the strict balance criterion:** `tasks/phase-3.md` Merge Criteria block gains a new bullet (or the existing block is extended): *"100-game tournament after Phase 3 meeting / voting integration: both decisive sides (`CREWMATES`, `IMPOSTORS`) win > 20% of decisive games."* This makes the deferral explicit so Phase 3.12's DoD inherits the criterion.
- [ ] **`dropped` rule consequence documented:** DESIGN.md §3.5 "Dead-crewmate task rule" subsection gains a one-paragraph note acknowledging that an impostor kill that drops the last incomplete task in `state.tasks` triggers the crew win condition on that tick. State that this is intended behavior: the impostor's optimal play is to kill early (before crewmates complete tasks); a late kill that hands crew the win reflects the impostor losing the race, not an engine bug. Reference the implementation anchor at `engine/tick.py::_apply_kill`.
- [ ] **Determinism preserved:** `tests/orchestrator/test_game.py:139-155` (default-agent byte-identical replay over 20 ticks) and `eval/determinism_test.py` both continue to pass against the committed config. If the cooldown / seeder change alters replay byte content, the existing tests must still compare two live runs of the same fixture against each other byte-for-byte; verify explicitly with `uv run pytest tests/orchestrator/test_game.py eval/determinism_test.py -v`.
- [ ] **Test cascades resolved:** Any test under `tests/engine/test_map_loader.py`, `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`, or `tests/orchestrator/test_game.py` that asserts a specific tuned value (cooldown, sabotage duration, tasks-per-crewmate count) is updated to the new canonical value. If a test asserts the *shape* of these values (e.g. "cooldown is a positive int"), no update is needed. Enumerate every updated test in `## Decisions`.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The search space is bounded and mechanical. Iterate it in the order documented in DoD bullet 1 — do not try other parameter combinations, do not try other parameter values. The point of the bounded sweep is reviewability: the PR `## Decisions` block must enumerate every config tested. A larger search would be a feature, not a fix.

For each candidate config, the tournament command is mechanical:

```bash
uv run python scripts/run_tournament.py \
  --num-games 100 \
  --start-seed 0 \
  --output-dir "/tmp/tournament-2.10.5-${LABEL}" \
  --max-ticks 1000
```

where `${LABEL}` encodes the config (e.g. `cd5`, `cd4-tpc2`, `cd4-tpc2-sab60`). After each run, read the printed summary and check both decisive percentages against 20%. The full output goes verbatim into `## Decisions`; do not summarize.

If you reach Path D, the wording in DoD bullet 5 is the literal replacement text. Quote it verbatim into `tasks/phase-2.md`. The Phase 3 bullet (DoD 6) is also literal — quote it verbatim into `tasks/phase-3.md` Merge Criteria. Do not paraphrase.

For the `tasks_per_crewmate` parameter (Path A step 2 onward), the seeder change is minimal:

```python
# orchestrator/seeder.py

def seed_initial_state(
    *,
    seed: int,
    game_map: Map,
    num_players: int,
    num_impostors: int = 1,
    tasks_per_crewmate: int = N,  # N = the balancing value
) -> WorldState: ...

def _build_tasks(
    *,
    seed: int,
    game_map: Map,
    crewmate_ids: tuple[PlayerId, ...],
    tasks_per_crewmate: int,
) -> dict[TaskId, TaskState]:
    rng = random.Random(seed)
    map_task_ids = sorted(game_map.tasks)
    rng.shuffle(map_task_ids)
    tasks: dict[TaskId, TaskState] = {}
    cursor = 0
    for crewmate_id in crewmate_ids:
        for _ in range(tasks_per_crewmate):
            task_id = map_task_ids[cursor % len(map_task_ids)]
            cursor += 1
            # Edge case: if tasks_per_crewmate * num_crewmates > len(map_task_ids),
            # the modulo cycles and a crewmate could be assigned the same task
            # twice. The 12-task canonical map plus 3 crewmates supports
            # tasks_per_crewmate up to 4 cleanly; bounds-check in the implementation.
            ...
    return tasks
```

The edge case in the comment matters: the canonical map has 12 tasks; 3 crewmates × 4 tasks each fills the map without repeats. Beyond 4, the modulo cycles. Stay within bounds; this task does not authorize widening the map's task set.

> Historical note (added 2026-05-15 by Task 2.11): the merged PR for this
> task (commit `d278829`) also updated two cooldown-value literal
> assertions in `tests/engine/test_tick.py` at lines 110 and 117
> (`== 10` → `== 4`, `== 9` → `== 3`) as mechanical fallout of the
> `kill_cooldown_ticks` 10 → 4 retune. The Task 2.10.5 `Test cascades
> resolved` DoD bullet enumerated four cascade test files but missed
> `tests/engine/test_tick.py`; the file is retroactively considered in
> scope for that historical PR. The literal-value updates did not change
> behavior.

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
Open a PR from branch `phase-2-tournament-balance` with a title like `task 2.10.5: phase 2 tournament balance`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5, DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
