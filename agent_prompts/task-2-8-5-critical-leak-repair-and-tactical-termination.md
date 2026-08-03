# Agent Prompt — 2.8.5 Critical leak repair and tactical termination

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.8.5 — Critical leak repair and tactical termination, anchored to DESIGN.md §1.3, DESIGN.md §3.3, DESIGN.md §4.4, DESIGN.md §11.2. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-critical-leak-and-termination`
**Depends on:** 2.7.5 merged, 2.8 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.3, DESIGN.md §4.4, DESIGN.md §11.2
**Complexity:** Medium

Address the blocking findings from the post-2.8 Codex cross-audit before
Task 2.9 begins generating tournament data. This is a single bundled PR that:

- replaces role-bearing player ids (`player-N` / `impostor-N`) with
  role-neutral ids across the seeder, helpers, fixtures, and tests
  (**Critical** — both prior Claude audits missed that a crewmate's
  `ObservationPacket.visible_players[].id` literally names the impostor
  on tick 0),
- adds a value-scanning pass to `eval/leak_test.py` that rejects role-bearing
  substrings inside any packet value, so the leak above could not happen
  again silently (**Critical** regression protection),
- fixes the crewmate FSM bug that prevents tasks from completing in default
  headless games (`tasks_completed` stays at `0` through 1000 ticks across
  six tested seeds despite crewmates reaching their task rooms) (**High**),
- documents the `TICK_BUDGET_REACHED` outcome contract in Task 2.9 so the
  tournament harness has a defined bucket for non-terminal games (**High**).

No agent-visible behaviour change beyond those documented fixes. Determinism
is preserved: the determinism test compares two runs of the same fixture
byte-for-byte, and both runs use the renamed ids, so byte-identity holds.

**Files in scope:**
- orchestrator/seeder.py
- agents/tactical/crewmate_policy.py
- eval/leak_test.py
- tests/_helpers/world_state.py
- tests/fixtures/scripted_game_basic_tasks.json
- tests/fixtures/scripted_game_kill_report_meeting.json
- tests/fixtures/scripted_game_vent_and_emergency.json
- tests/agents/test_crewmate_policy.py
- tests/agents/test_impostor_policy.py
- tests/agents/test_runtime.py
- tests/agents/test_perception.py
- tests/engine/test_tick.py
- tests/engine/test_tick_properties.py
- tests/engine/test_visibility.py
- tests/observation/test_service.py
- tests/observation/test_boundary_contracts.py
- tests/orchestrator/test_boundary.py
- tests/orchestrator/test_action_ordering.py
- tests/orchestrator/test_game.py
- tasks/phase-2.md

**Files NOT in scope:**
- engine/
- observation/packet.py
- observation/service.py
- observation/audit.py
- observation/action_intent.py
- observation/public_map.py
- orchestrator/game.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- orchestrator/replay.py
- orchestrator/scheduler.py
- agents/runtime.py
- agents/base.py
- agents/perception.py
- agents/memory/
- agents/tactical/impostor_policy.py
- agents/tactical/pathing.py
- llm/
- api/
- AGENTS.md
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- audits/
- open_issues.md
- README.md

**Definition of done:**
- [ ] `orchestrator/seeder.py` generates role-neutral player ids. New convention: ids are `p-1`, `p-2`, ..., `p-{num_players}`, assigned in fixed lexical order; role assignment to ids is randomized by the seed-shuffled permutation, so the id substring never encodes role. Roles continue to live on `PlayerState.role` only.
- [ ] `tests/_helpers/world_state.py::scripted_initial_world_state` is updated to use the same `p-N` ids. The shape pinned by this helper is what the scripted fixtures consume; the helper and the seeder must stay in lockstep.
- [ ] All three `tests/fixtures/scripted_game_*.json` files reference the new ids consistently. Verify with `eval/determinism_test.py` and `eval/leak_test.py` after the rename.
- [ ] Every test file under `tests/` that hardcodes `player-N` or `impostor-N` is updated to the new convention. Use `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" tests/` to enumerate before editing and after; the post-fix grep must be empty.
- [ ] `eval/leak_test.py` gains a recursive value-scanner pass alongside the existing field-name scanner. The new pass walks every emitted packet, lowercases every string value, and fails if any contains `impostor`, `crewmate`, or `crew` (with the existing `self_state.role` allow-list still respected). The scanner runs against all three scripted fixtures.
- [ ] `agents/tactical/crewmate_policy.py` is fixed so default headless games can complete tasks. The current symptom: across `seeds {0, 1, 2, 7, 42, 100}`, `tasks_completed` stays at `0` through `DEFAULT_MAX_TICKS=1000` even though crewmates reach their assigned task rooms. Diagnose first; the fix may live in the FSM (e.g. `DoTaskIntent` never emitted), in the perception → memory wiring (task-arrival event not recognized), or in the policy ↔ `engine/tick.py::_advance_tasks` interaction (continuing-task progress dropped). Do not touch `engine/`, `observation/`, or `agents/perception.py` — the fix must live in the policy.
- [ ] `tests/agents/test_crewmate_policy.py` adds a regression test that drives at least one full task-completion cycle through `CrewmatePolicy.decide`: place the crewmate at the task's room, feed memory events that pin self-state and a pending task, and assert that consecutive `decide` calls yield `DoTaskIntent` for the matching `task_id` until completion. The test must fail today and pass after the fix.
- [ ] After the policy fix, run `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/r-$seed.jsonl --max-ticks 200; done` and confirm at least one seed reaches `CREWMATES` or `IMPOSTORS` outcome (not all `TICK_BUDGET_REACHED`). Record the seeds and outcomes in the PR description's `## Decisions` block.
- [ ] `tasks/phase-2.md` Task 2.9 contract's Definition of done adds a bullet stating that `TICK_BUDGET_REACHED` is a first-class outcome bucket in the tournament report, reported alongside `CREWMATES` and `IMPOSTORS`. Phase 2 Merge Criteria text is updated to read "Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); `TICK_BUDGET_REACHED` games are reported separately and do not count toward decisive totals."
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

For the id rename, the smallest faithful change is to keep ids in a single
lexical order and randomize role assignment underneath:

```python
# orchestrator/seeder.py
def _build_player_ids(num_players: int) -> tuple[PlayerId, ...]:
    return tuple(f"p-{i + 1}" for i in range(num_players))

def _assign_roles(
    *, seed: int, player_ids: tuple[PlayerId, ...], num_impostors: int,
) -> dict[PlayerId, Role]:
    rng = random.Random(seed)
    permutation = list(player_ids)
    rng.shuffle(permutation)
    impostor_ids = set(permutation[:num_impostors])
    return {pid: ("IMPOSTOR" if pid in impostor_ids else "CREWMATE")
            for pid in player_ids}
```

Audit log values for a crewmate then look like
`{"id": "p-3", "room": "CAFETERIA"}` with no role-bearing substring.

For the value-scanning leak test, add a helper alongside
`_assert_no_recursive_hidden_fields`:

```python
_FORBIDDEN_ID_SUBSTRINGS = ("impostor", "crewmate", "crew")
_ALLOWED_VALUE_PATHS = frozenset({("self_state", "role")})

def _assert_no_role_bearing_values(packet_dump: JsonValue) -> None:
    for path, value in _walk_json(packet_dump):
        if not isinstance(value, str):
            continue
        if path in _ALLOWED_VALUE_PATHS:
            continue
        lowered = value.lower()
        for forbidden in _FORBIDDEN_ID_SUBSTRINGS:
            if forbidden in lowered:
                raise AssertionError(
                    f"role-bearing value {value!r} leaked at "
                    f"{_format_json_path(path)}"
                )
```

Wire it into `test_no_observation_leaks_hidden_information` so every
packet across every fixture is scanned. Add a self-test similar to
`test_recursive_hidden_field_scanner_reports_nested_path` that proves the
scanner trips on a planted role-bearing value.

For the crewmate task-completion bug, the diagnostic loop is short:

```
uv run python scripts/run_game.py --seed 0 --replay-path /tmp/r0.jsonl
python -c "
import json
for line in open('/tmp/r0.jsonl'):
    e = json.loads(line)
    for a in e['actions']:
        if a['actor'] == 'p-1':  # whichever id is a crewmate after rename
            print(e['tick'], a['type'], a.get('payload'))
" | head -40
```

If `p-1` (the crewmate in LABS for seed=0) submits `DoTaskIntent` but the
engine never emits `TaskCompleted`, the bug is in
`engine/tick.py::_advance_tasks` and out of this task's scope — escalate.
If `p-1` submits `MoveIntent` or `WaitIntent` even after reaching the
task's room, the bug is in `CrewmatePolicy` and in scope here.

> Historical note (added 2026-05-15 by Task 2.11): the merged PR for this
> task (commit `e3b2a60`) also touched `eval/determinism_test.py`,
> `tests/engine/test_actions.py`, `tests/engine/test_events.py`,
> `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`,
> and `agent_prompts/task-2-9-headless-tournament-harness.md` as
> mechanical fallout of the `p-N` id rename. Those files are retroactively
> considered in scope for that historical PR; the rename did not change
> behavior.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-2-critical-leak-and-termination` with a title like `task 2.8.5: critical leak repair and tactical termination`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §3.3, DESIGN.md §4.4, DESIGN.md §11.2), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
