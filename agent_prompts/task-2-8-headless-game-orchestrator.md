# Agent Prompt — 2.8 Headless game orchestrator

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.8 — Headless game orchestrator, anchored to DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-headless-game-orchestrator`
**Depends on:** 2.6 merged, 2.7 merged
**Section refs:** DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4
**Complexity:** Integration

Build the deterministic single-game loop spine. This task wires existing engine,
observation, agents, action-intent translation, and replay together, but does
not implement tournament aggregation.

**Files in scope:**
- orchestrator/game.py
- orchestrator/seeder.py
- orchestrator/scheduler.py
- scripts/run_game.py
- tests/orchestrator/test_game.py
- tests/orchestrator/test_seeder.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/ policy changes
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] A single headless game can run from a seed using deterministic role/spawn/task assignment.
- [ ] Each tick builds observations, dispatches agents, collects `ActionIntent`s, translates them to engine actions, advances the engine, and records replay entries.
- [ ] Meeting interruption and game-over states stop or pause the tick loop as appropriate for Phase 2.
- [ ] The orchestrator owns all engine imports; agents remain engine-free.
- [ ] Relevant orchestrator tests pass.
- [ ] `uv run mypy --strict engine observation agents orchestrator` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

```python
# orchestrator/seeder.py
def seed_initial_state(
    *, seed: int, game_map: Map, num_players: int, num_impostors: int = 1,
) -> WorldState: ...

# orchestrator/game.py
@dataclass(frozen=True)
class HeadlessGameResult:
    final_state: WorldState
    outcome: Literal["CREWMATES", "IMPOSTORS", "MEETING_PHASE_REACHED"]
    replay_path: Path

class HeadlessGame:
    def __init__(
        self,
        *,
        seed: int,
        game_map: Map,
        agent_factory: AgentFactory,
        replay_path: Path,
    ) -> None: ...

    def run(self) -> HeadlessGameResult:
        state = seed_initial_state(seed=self._seed, game_map=self._game_map, num_players=...)
        while state.phase == "PLAY":
            packets = {pid: self._observation_service.build_packet(...) for pid in alive(state)}
            intents = [self._agents[pid].decide(packets[pid], self._public_map) for pid in ...]
            actions = translate_action_intents_for_tick(intents)
            state, events = advance_tick(state, actions, game_map=self._game_map)
            self._replay.record_tick(state.tick, list(actions), state)
        return HeadlessGameResult(...)
```

Use `tests/_helpers/world_state.scripted_initial_world_state` as the
shape reference for `seed_initial_state`; the eval scripts will
switch to your seeder once it lands.

## Public types this task introduces
- `orchestrator.game.HeadlessGame`
- `orchestrator.game.HeadlessGameResult`
- `orchestrator.seeder.seed_initial_state`
- `orchestrator.scheduler.TickScheduler`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This task is the convergence point of Phase 2. It depends on tasks
2.1–2.7. Failure here invalidates Phase 2 merge criteria.

- Memory write paths from 2.3 must accept the typed events from 2.4.
  If they diverge, perception → memory wiring silently drops events.
  Verify with: `uv run pytest tests/agents/test_runtime.py`.
- The MEETING phase has no manager (Phase 3.8 owns it). When the
  engine returns `phase == "MEETING"`, the loop pauses and emits
  `MEETING_PHASE_REACHED` on the result. Do NOT mutate engine state
  to resume.
- The leak test (`eval/leak_test.py`) must continue to pass when
  driven by your orchestrator. Run it explicitly before declaring
  done.
- Add a regression test that pins today's body-visibility-after-discovery
  behaviour from `engine/visibility.py`: bodies whose `discovered_by` is
  set are filtered out of every observer's `visible_bodies`, including the
  reporter's own packet on the discovery tick.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-2-headless-game-orchestrator` with a title like `task 2.8: headless game orchestrator`.
The PR description must reference DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
