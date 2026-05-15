# Agent Prompt — 2.10 Pre-Phase-3 tactical repair

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.10 — Pre-Phase-3 tactical repair, anchored to DESIGN.md §1.3, DESIGN.md §3.5, DESIGN.md §4.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-pre-phase-3-tactical-repair`
**Depends on:** 2.8.5 merged, 2.9 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.5, DESIGN.md §4.4
**Complexity:** Integration

Close the four critical/high findings in
`audits/audit-2026-05-15-0225-reconciled.md` that block Phase 3: R-5 (dead-
crewmate task rule decision), R-3 (impostor stale-target chase loop), R-2
(six-seed sweep yields zero decisive outcomes), and R-1 (100-game
tournament fails the merge criterion). These four form a causal chain:
R-5 is the prerequisite rule decision that makes crew victory reachable
after an early kill; R-3 is the tactical fix that stops the impostor from
oscillating between two rooms forever; once both are in, R-2 and R-1
become re-runnable acceptance gates. This is a single bundled PR because
splitting it leaves the seed sweep and tournament gates encoded against
unfixed code.

The R-5 rule is **dropped**: when a crewmate dies, their incomplete tasks
are removed from `state.tasks`, and the win condition counts only
alive-owned tasks. The rule and its rationale are documented at
`DESIGN.md` §3.5 "Win conditions". This task implements the rule and the
surrounding behavioural fixes; **do not re-litigate the choice**.
Implement the rule before fixing the impostor stale-target loop in R-3,
then re-run the seed sweep (R-2) and the 100-game tournament (R-1).

**Files in scope:**
- DESIGN.md
- engine/win_conditions.py
- engine/tick.py
- agents/tactical/impostor_policy.py
- tests/agents/test_impostor_policy.py
- tests/engine/test_tick.py
- tests/orchestrator/test_game.py

**Files NOT in scope:**
- engine/world.py
- engine/actions.py
- engine/events.py
- engine/visibility.py
- engine/rng.py
- engine/entities.py
- engine/maps/
- observation/
- orchestrator/game.py
- orchestrator/seeder.py
- orchestrator/replay.py
- orchestrator/scheduler.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- agents/base.py
- agents/runtime.py
- agents/perception.py
- agents/memory/
- agents/tactical/crewmate_policy.py
- agents/tactical/pathing.py
- eval/
- scripts/
- llm/
- api/
- frontend/
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
- tests/observation/
- tests/orchestrator/test_action_ordering.py
- tests/orchestrator/test_boundary.py
- tests/orchestrator/test_seeder.py
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-5 — `dropped` rule pinned in DESIGN.md:** `DESIGN.md` §3.5 already documents the `dropped` rule and its rationale (committed at design-decision time, before this task was dispatched). Verify the section reads correctly against the implementation; do not edit it unless wording needs minor cleanup. `engine/win_conditions.py` gains a one-line comment naming the §3.5 anchor (e.g. `# Dead-crewmate task rule lives in DESIGN.md §3.5 (dropped).`).
- [ ] **R-5 — `dropped` rule implemented and pinned:** `engine/tick.py`'s `KilledEvent` handler removes the killed player's incomplete tasks from `state.tasks` (entries where `owner == killed_player_id` and `completed is False`). Already-completed tasks remain so they continue to count toward `crew_tasks_done`. `engine/win_conditions.py` requires no change — it already compares `crew_tasks_done == total_tasks` against the current `state.tasks`, so upstream removal is sufficient. A regression test in `tests/engine/test_tick.py` constructs a state where a crewmate dies with an incomplete task and asserts (a) the dead crewmate's incomplete task is no longer in `state.tasks`, (b) any already-completed task owned by the dead crewmate remains in `state.tasks`, and (c) crew can reach `CREWMATE_TASKS` by completing the remaining alive-owned tasks. Test name: `test_dead_crewmate_incomplete_task_is_dropped_and_crew_can_still_win` or equivalent.
- [ ] **R-3 — staleness/dead-target pruning unit test:** `tests/agents/test_impostor_policy.py` adds a regression that drives `ImpostorPolicy.decide` with `EVENT_SAW_PLAYER` events whose target was last seen ≥ 30 ticks ago, plus an `EVENT_SAW_BODY` event naming the same target. The test asserts the policy does not produce a `MoveIntent` toward the stale-sighting room and does not select the dead/stale player as the scored target. The test must fail against the pre-fix `_scored_targets` and pass after the fix.
- [ ] **R-3 — staleness/dead-target pruning implementation:** `agents/tactical/impostor_policy.py::_scored_targets` filters out (a) players the impostor has observed as dead (via `EVENT_SAW_BODY`-derived inference or an equivalent belief signal — see Implementation hint) and (b) sightings older than a documented staleness threshold (tick-based; default ~30 ticks, tuned against seed 0). The threshold is a module-level constant with a one-line comment. Existing scored-target ordering (`(-score, player_id)`) is preserved when at least one valid target remains.
- [ ] **R-3 — default-agent integration regression:** `tests/orchestrator/test_game.py` adds a regression that runs `HeadlessGame` with seed 0 at default agents for ≥ 200 ticks and asserts the impostor's replayed actions do not contain the pre-fix `ENGINEERING → REACTOR → ENGINEERING → REACTOR` alternation pattern over any window of ≥ 30 consecutive ticks after a confirmed kill. The assertion may be expressed as: across any 30-tick window starting after the first `KilledEvent`, the impostor's distinct `MoveIntent.to_room` targets exceed 1.
- [ ] **R-2 — six-seed decisive sweep re-runs green:** After landing R-3 and R-5, run `for seed in 0 1 2 7 42 100; do uv run python scripts/run_game.py --seed $seed --replay-path /tmp/r-$seed.jsonl --max-ticks 1000; done`. At least one of the six seeds must end at `CREWMATES` or `IMPOSTORS`. Record each seed's outcome in the PR description's `## Decisions` block (six lines).
- [ ] **R-1 — 100-game tournament re-runs green:** Run `uv run python scripts/run_tournament.py --num-games 100 --start-seed 0 --output-dir /tmp/tournament-post-2.10 --max-ticks 1000`. Both decisive outcomes (`CREWMATES` and `IMPOSTORS`) must each be > 20% of decisive games per the Phase 2 merge criterion at `tasks/phase-2.md:959`. Record the four-bucket counts (`crew_wins`, `impostor_wins`, `tick_budget_reached`, `meeting_phase_reached`) and the decisive split in the PR description.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The R-5 rule is `dropped` (already documented at `DESIGN.md` §3.5). Implement it in `engine/tick.py`'s `KilledEvent` handler: on a crewmate kill, iterate `state.tasks` and remove entries whose `owner` equals the killed player and whose `completed` is `False`. Already-completed tasks remain — they count toward `crew_tasks_done`. Ship this before the R-3 staleness fix so the integration regressions (R-2, R-1) run against the new rule.

For R-3, the staleness filter integrates into the existing `_scored_targets` loop. The current loop at `agents/tactical/impostor_policy.py:219-265` keeps every seen player in `latest_sighting`; the fix is to drop the stale and dead entries before they enter the bucket and score:

```python
# agents/tactical/impostor_policy.py — sketch only; pick the threshold
# against a regression seed and document it.
_STALENESS_THRESHOLD: Final[int] = 30  # ticks

@staticmethod
def _scored_targets(
    events: tuple[EpisodicEvent, ...],
    *,
    cooldown: int,
    current_tick: int,
    confirmed_dead: frozenset[PlayerId],
) -> tuple[_ScoredTarget, ...]:
    latest_sighting: dict[PlayerId, EpisodicEvent] = {}
    bucket: dict[tuple[int, RoomId], int] = {}
    for event in events:
        if event.type != EVENT_SAW_PLAYER:
            continue
        player_id = event.payload["player_id"]
        if not isinstance(player_id, str):
            raise ValueError(...)
        if player_id in confirmed_dead:
            continue
        if current_tick - event.tick > _STALENESS_THRESHOLD:
            continue
        # ... existing bucket / latest_sighting bookkeeping
```

`confirmed_dead` should be sourced from the agent's own memory — not from engine state. Two options for the implementing agent (pick one and pin with a comment):

1. **Episodic inference**: walk `EVENT_SAW_BODY` events; the perception event payload at `agents/perception.py:138-146` already carries `body_id`. If the body→victim mapping is not directly recoverable from the event payload today, prefer option 2.
2. **Belief signal**: extend `agents/memory/beliefs.py::PlayerBelief` with a boolean (e.g. `is_confirmed_dead`) that perception sets when it ingests a `KilledEvent`-derived audible/visible event. This is the cleaner long-term fix but requires touching `agents/memory/beliefs.py` (currently out of scope) — if you choose this path, expand `Files in scope` to add `agents/memory/beliefs.py` and `tests/agents/test_memory.py`, justify the expansion in `## Decisions`, and confirm import-linter still passes.

For both R-2 and R-1, the commands are mechanical:

```bash
# R-2 — six-seed sweep
for seed in 0 1 2 7 42 100; do
  uv run python scripts/run_game.py \
    --seed "$seed" \
    --replay-path "/tmp/r-$seed.jsonl" \
    --max-ticks 1000
done

# R-1 — 100-game tournament
uv run python scripts/run_tournament.py \
  --num-games 100 \
  --start-seed 0 \
  --output-dir /tmp/tournament-post-2.10 \
  --max-ticks 1000
```

Both runs go in the PR description verbatim (the exact stdout summary for the tournament, the six outcome literals for the sweep). Do not summarize — paste the raw counts.

## Integration risk

This task is the convergence point for the Phase 2 acceptance gates. It changes engine win-condition behavior (R-5) and impostor tactical scoring (R-3), and re-runs the headless gates that the audit reproduces.

- **Determinism:** `tests/orchestrator/test_game.py:139-155` pins default-agent byte-identical replay over 20 ticks. R-5 and R-3 will change the byte content of those replays; re-record the baseline within this PR if the existing assertion compares against a frozen reference. If the test compares two live runs of the same fixture against each other, byte identity must still hold post-fix — verify explicitly with `uv run pytest tests/orchestrator/test_game.py -v`.
- **Engine purity:** `engine/win_conditions.py` and `engine/tick.py` remain pure functions of state and actions. Do not add agent imports, randomness, or hidden state. The R-5 rule must be expressible as a state-only function.
- **Observation firewall:** R-3's `confirmed_dead` set must be derived from agent-owned memory, not from engine state. If you choose Implementation-hint option 2, add `agents/memory/beliefs.py` to scope explicitly. Either way, run `uv run lint-imports` to confirm the firewall holds.
- **Leak scan:** R-3 may add new fields or values to belief state; if so, re-run `uv run pytest eval/leak_test.py` and confirm the value-scanner still passes against all three scripted fixtures and the 100-game tournament audit logs.
- **Merge-criterion text:** the R-5 rule is `dropped`, so no edit to the Phase 2 Merge Criteria wording is needed. Task 2.11's R-8 cleanup still owns the separate "games" vs "decisive games" wording fix.
- **Tournament re-run cost:** `scripts/run_tournament.py` against 100 games at max-ticks 1000 takes ~minutes on a default workstation. Budget for it; do not gate the merge on faster runs.
- **`audits/*` are read-only artifacts.** Do not edit the reconciled audit; this task addresses its findings, it does not amend the record.

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
Open a PR from branch `phase-2-pre-phase-3-tactical-repair` with a title like `task 2.10: pre-phase-3 tactical repair`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §3.5, DESIGN.md §4.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
