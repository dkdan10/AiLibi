# Phase 2 — Tactical Agents

## Goal
Rule-based crewmate and impostor agents complete headless games without
crashing. Agents remain behind the observation firewall: they consume
`ObservationPacket` + `PublicMapView` and return `ActionIntent`, never engine
state or engine `Action`.

## Parallelism
Sequential through 2.5. Tasks 2.6 and 2.7 can run in parallel after 2.5. Task
2.8 runs after both policies merge. Task 2.9 runs after 2.8.

## Status

Task 2.1 (Boundary contracts) is already merged on `main`. The
in-scope files (`observation/action_intent.py`, `observation/public_map.py`,
`orchestrator/boundary.py`, `orchestrator/action_ordering.py`,
`tests/observation/test_boundary_contracts.py`,
`tests/orchestrator/test_boundary.py`,
`tests/orchestrator/test_action_ordering.py`, `tests/test_firewall.py`) exist and
the corresponding tests pass. Subsequent Phase 2 tasks build on them.

## Tasks

### Task 2.1 — Boundary contracts
**Branch:** `phase-2-boundary-contracts`
**Depends on:** Phase 1 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1
**Complexity:** Medium

Define the engine-free schemas and adapters that let agents act without
importing engine types.

**Files in scope:**
- observation/action_intent.py
- observation/public_map.py
- orchestrator/boundary.py
- orchestrator/action_ordering.py
- tests/observation/test_boundary_contracts.py
- tests/orchestrator/test_boundary.py
- tests/orchestrator/test_action_ordering.py
- tests/test_firewall.py

**Files NOT in scope:**
- agents/tactical/
- agents/strategic/
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `ActionIntent` is a Pydantic discriminated union for move, do_task, kill, vent, report, emergency, sabotage, repair_sabotage, and wait.
- [ ] `PublicMapView` exposes only public map topology needed by agents: map id, room ids, room neighbors, vent graph, vent rooms, task locations, spawn room, meeting room, and emergency button room.
- [ ] Orchestrator boundary helpers translate `PublicMapView` from an engine map and translate valid `ActionIntent` values into engine `Action` values.
- [ ] Orchestrator boundary helpers reject duplicate actor submissions before actions enter `advance_tick`.
- [ ] Invalid intents raise during translation; there are no silent fallbacks.
- [ ] `agents/` has no imports from `engine/`, directly or transitively.
- [ ] Relevant boundary and firewall tests pass.
- [ ] `uv run mypy --strict engine observation agents orchestrator` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# observation/action_intent.py
class ActionIntent(BaseModel):
    """Discriminated union over move | do_task | kill | vent |
    report | emergency | sabotage | repair_sabotage | wait."""

# orchestrator/boundary.py
def public_map_from_engine_map(game_map: Map) -> PublicMapView: ...
def translate_action_intent(intent: ActionIntent) -> Action: ...
def translate_action_intents_for_tick(
    intents: Sequence[ActionIntent],
) -> tuple[Action, ...]: ...
```

Reject duplicate-actor batches in the orchestrator boundary, not in
the engine. The engine assumes one action per actor per tick already.

**Public types introduced:**
- `observation.action_intent.ActionIntent`
- `observation.public_map.PublicMapView`
- `orchestrator.boundary.public_map_from_engine_map`
- `orchestrator.boundary.translate_action_intent`
- `orchestrator.boundary.translate_action_intents_for_tick`

**Ready-to-paste prompt:** `agent_prompts/task-2-1-boundary-contracts.md`

### Task 2.2 — Agent base + runtime
**Branch:** `phase-2-agent-base-runtime`
**Depends on:** 2.1 merged
**Section refs:** DESIGN.md §4.1
**Complexity:** Medium

agents/base.py and agents/runtime.py per §4.1. Runtime consumes
`ObservationPacket` and `PublicMapView`, updates memory, and returns
`ActionIntent`.

**Files in scope:**
- agents/base.py
- agents/runtime.py
- tests/agents/test_runtime.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- agents/strategic/
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `AgentInterface` protocol and `AgentRuntime` wiring match DESIGN.md §4.1.
- [ ] Runtime consumes `ObservationPacket` and `PublicMapView`, not engine state.
- [ ] Runtime returns `ActionIntent`, not engine `Action`.
- [ ] Memory wiring is stubbed only where later tasks own the implementation.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant agent runtime tests pass.
- [ ] `uv run mypy --strict agents observation` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# agents/base.py
class AgentInterface(Protocol):
    def decide(
        self,
        packet: ObservationPacket,
        public_map: PublicMapView,
    ) -> ActionIntent: ...

# agents/runtime.py
class AgentRuntime:
    """Glue: perception (2.4) -> memory (2.3) -> tactical (2.6/2.7).
    For 2.2 the memory/perception/tactical methods are stubs that the
    later tasks fill in. Do not import engine."""
    def decide(self, packet, public_map) -> ActionIntent: ...
```

**Public types introduced:**
- `agents.base.AgentInterface`
- `agents.runtime.AgentRuntime`

**Ready-to-paste prompt:** `agent_prompts/task-2-2-agent-base-runtime.md`

### Task 2.3 — Memory scaffolding (no LLM)
**Branch:** `phase-2-memory-scaffolding`
**Depends on:** 2.2 merged
**Section refs:** DESIGN.md §6.1
**Complexity:** Medium

agents/memory/episodic.py, working.py, beliefs.py per §6.1. Write paths only;
no prompt rendering yet.

**Files in scope:**
- agents/memory/episodic.py
- agents/memory/working.py
- agents/memory/beliefs.py
- tests/agents/test_memory.py

**Files NOT in scope:**
- engine/
- llm/
- agents/memory/store.py
- agents/tactical/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Episodic, working, and belief memory scaffolds exist per DESIGN.md §6.1.
- [ ] Write paths are implemented for typed agent-visible events.
- [ ] Prompt rendering is not implemented in this task.
- [ ] No raw `ObservationPacket` parsing is added to tactical policy files.
- [ ] No imports from engine/ under agents/.
- [ ] `uv run mypy --strict agents observation` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# agents/memory/episodic.py
@dataclass(frozen=True)
class EpisodicEvent:
    tick: int
    type: str
    payload: Mapping[str, Any]
    provenance: str  # e.g. 'observed', 'reported'

class MemoryStore:
    def append(self, event: EpisodicEvent) -> None: ...
    def recent(self, *, since_tick: int) -> tuple[EpisodicEvent, ...]: ...
```

Read paths and prompt rendering are out of scope here — they ship
in 3.3.

**Public types introduced:**
- `agents.memory.episodic.EpisodicEvent`
- `agents.memory.episodic.MemoryStore`
- `agents.memory.working.WorkingMemory`
- `agents.memory.beliefs.BeliefState`

**Ready-to-paste prompt:** `agent_prompts/task-2-3-memory-scaffolding-no-llm.md`

### Task 2.4 — Perception ingestion
**Branch:** `phase-2-perception-ingestion`
**Depends on:** 2.3 merged
**Section refs:** DESIGN.md §4.2, DESIGN.md §6.2
**Complexity:** Medium

Convert `ObservationPacket` into typed episodic events before tactical policies
read memory.

**Files in scope:**
- agents/perception.py
- agents/runtime.py
- tests/agents/test_perception.py

**Files NOT in scope:**
- engine/
- agents/tactical/
- agents/strategic/
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Perception converts visible players, visible bodies, audible events, self state, global state, and cooldown into typed episodic events with provenance.
- [ ] Agent runtime can call perception and write resulting events into episodic memory.
- [ ] Tactical policies are not responsible for parsing raw `ObservationPacket`s.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant perception tests pass.
- [ ] `uv run mypy --strict agents observation` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# agents/perception.py
def ingest_packet(
    *,
    packet: ObservationPacket,
    memory: MemoryStore,
) -> None:
    """Convert visible_players, visible_bodies, audible_events,
    self_state, global_state, and cooldown into typed EpisodicEvents
    appended to memory. Provenance must distinguish observed vs.
    inferred."""
```

Tactical policies must consume memory only — never raw
ObservationPacket. Keep parsing here.

**Public types introduced:**
- `agents.perception.ingest_packet`

**Ready-to-paste prompt:** `agent_prompts/task-2-4-perception-ingestion.md`

### Task 2.5 — Pathing
**Branch:** `phase-2-pathing`
**Depends on:** 2.4 merged
**Section refs:** DESIGN.md §4.4
**Complexity:** Medium

agents/tactical/pathing.py - deterministic A* over `PublicMapView`.

**Files in scope:**
- agents/tactical/pathing.py
- tests/agents/test_pathing.py

**Files NOT in scope:**
- engine/
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] A* pathing over `PublicMapView` exists per DESIGN.md §4.4.
- [ ] Pathing remains deterministic for the same inputs, including tie-breaking.
- [ ] Unknown rooms and disconnected destinations raise.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant agent tests pass.
- [ ] `uv run mypy --strict agents observation` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# agents/tactical/pathing.py
def find_path(
    *,
    public_map: PublicMapView,
    start: RoomId,
    goal: RoomId,
) -> tuple[RoomId, ...]:
    """Deterministic A* over public_map.room_neighbors. Tie-break
    on sorted room id. Raise on unknown or disconnected rooms.
    Return the inclusive path from start to goal."""
```

**Public types introduced:**
- `agents.tactical.pathing.find_path`

**Ready-to-paste prompt:** `agent_prompts/task-2-5-pathing.md`

### Task 2.6 — Crewmate FSM
**Branch:** `phase-2-crewmate-fsm`
**Depends on:** 2.5 merged
**Section refs:** DESIGN.md §4.4
**Complexity:** Medium

agents/tactical/crewmate_policy.py per §4.4.

**Files in scope:**
- agents/tactical/crewmate_policy.py
- tests/agents/test_crewmate_policy.py

**Files NOT in scope:**
- engine/
- llm/
- agents/tactical/impostor_policy.py
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Crewmate FSM implements IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE and listed interrupts.
- [ ] Policy consumes memory and `PublicMapView`; it does not parse raw engine state.
- [ ] Policy returns `ActionIntent`.
- [ ] Tactical decisions are deterministic and rule-based.
- [ ] No LLM calls in agents/tactical/.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant deterministic tactical tests pass.
- [ ] `uv run mypy --strict agents observation` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# agents/tactical/crewmate_policy.py
class CrewmatePolicy:
    """FSM: IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE.
    Interrupts: BODY_VISIBLE -> REPORT, KILL_WITNESSED -> FLEE_AND_REPORT.
    Must be deterministic given memory state."""
    def decide(
        self,
        memory: MemoryStore,
        public_map: PublicMapView,
    ) -> ActionIntent: ...
```

The `KILL_WITNESSED` interrupt deliberately fires only when the kill action
is reported in the agent's own room. This is narrower than the engine's
`same_room_and_adjacent` visibility window, which can surface a kill action
in an adjacent room. Restricting the interrupt to the agent's own room is an
intentional tactical choice — an adjacent kill is not a confirmed witness
event and would over-trigger emergency meetings — not a bug.

**Public types introduced:**
- `agents.tactical.crewmate_policy.CrewmatePolicy`

**Ready-to-paste prompt:** `agent_prompts/task-2-6-crewmate-fsm.md`

### Task 2.7 — Impostor FSM
**Branch:** `phase-2-impostor-fsm`
**Depends on:** 2.5 merged
**Section refs:** DESIGN.md §4.4
**Complexity:** Medium

agents/tactical/impostor_policy.py per §4.4.

**Files in scope:**
- agents/tactical/impostor_policy.py
- tests/agents/test_impostor_policy.py

**Files NOT in scope:**
- engine/
- llm/
- agents/tactical/crewmate_policy.py
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Impostor FSM implements IDLE -> STALK -> KILL_OPPORTUNITY -> KILL -> COVER.
- [ ] Target selection uses deterministic isolation, witness-risk, and kill-cooldown scoring.
- [ ] Policy consumes memory and `PublicMapView`; it does not parse raw engine state.
- [ ] Policy returns `ActionIntent`.
- [ ] Tactical decisions are deterministic and rule-based.
- [ ] No LLM calls in agents/tactical/.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant deterministic tactical tests pass.
- [ ] `uv run mypy --strict agents observation` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# agents/tactical/impostor_policy.py
class ImpostorPolicy:
    """FSM: IDLE -> STALK -> KILL_OPPORTUNITY -> KILL -> COVER.
    Target score: isolation * (1 - witness_risk) * (cooldown == 0)."""
    def decide(
        self,
        memory: MemoryStore,
        public_map: PublicMapView,
    ) -> ActionIntent: ...
```

**Public types introduced:**
- `agents.tactical.impostor_policy.ImpostorPolicy`

**Ready-to-paste prompt:** `agent_prompts/task-2-7-impostor-fsm.md`

### Task 2.7.5 — Post-2.7 audit repair
**Branch:** `phase-2-post-audit-repair`
**Depends on:** 2.6 merged, 2.7 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.6, DESIGN.md §4.4
**Complexity:** Medium

Address the documented findings from
`audits/audit-2026-05-10-0721.md`, plus the PR-workflow gap surfaced in the
post-2.7 conversation (audit PR #25 shipped with an empty body because no
non-task-prompted PR has structured-body instructions), so the agent layer
and the contributor workflow are defensively sound before Task 2.8 wires
agents into a live game. This is a single bundled PR that:

- fixes one contract-scope drift (M-1),
- hardens one tactical policy against disconnected maps (L-2),
- documents one deliberate behavioural narrowing (L-3),
- pins one engine→perception enum coupling (L-4),
- ships the body-after-discovery regression test that the prior audit
  deferred from 2.8 (L-5),
- and closes the PR-template enforcement gap (PR-W1) by promoting the
  `.github/pull_request_template.md` shape into both `AGENTS.md` (so the
  template applies to every PR, task and ad-hoc alike) and
  `scripts/prompt_template.md.j2` (so generated task prompts agree with
  the template).

No agent-visible behaviour change beyond those documented fixes. The
prompt-template alignment will regenerate every existing `agent_prompts/*`
file via `scripts/generate_prompts.py`; the diff to those files is purely
mechanical (no task contract changes).

**Files in scope:**
- tasks/phase-2.md
- agents/tactical/crewmate_policy.py
- tests/agents/test_crewmate_policy.py
- tests/agents/test_perception.py
- tests/observation/test_service.py
- AGENTS.md
- scripts/prompt_template.md.j2

**Files NOT in scope:**
- engine/
- observation/
- orchestrator/
- agents/runtime.py
- agents/perception.py
- agents/memory/
- agents/tactical/impostor_policy.py
- agents/tactical/pathing.py
- agents/base.py
- llm/
- api/
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- audits/
- .github/pull_request_template.md
- scripts/generate_prompts.py
- scripts/_task_parser.py
- scripts/validate_task_docs.py

**Definition of done:**
- [ ] `tasks/phase-2.md` Task 2.4 `Files in scope` list includes `agents/runtime.py`, recording the historical scope of PR `908c6a3`.
- [ ] `tasks/phase-2.md` Task 2.6 records, in a short prose note after the implementation hint, that the `KILL_WITNESSED` interrupt deliberately fires only when the kill action is reported in the agent's own room (narrower than the engine's `same_room_and_adjacent` visibility window) and that this is an intentional tactical choice, not a bug.
- [ ] `agents/tactical/crewmate_policy.py` `_move_toward` and `_flee_and_report` wrap their `find_path` calls in `try / except ValueError`, falling back to `WaitIntent` when no path exists. Mirror the pattern already used in `agents/tactical/impostor_policy.py:145-149` and `:335-339`.
- [ ] `tests/agents/test_crewmate_policy.py` adds a regression test that builds a `PublicMapView` with a disconnected goal room and asserts the crewmate emits `WaitIntent` instead of raising.
- [ ] `tests/agents/test_perception.py` adds a regression test asserting that `agents.perception._AUDIBLE_EVENT_TYPES.keys()` equals the set of literals in the `AudibleEvent.kind` type from `observation/packet.py` (use `typing.get_args` on the Literal alias). The test must fail if a new `kind` is added to `AudibleEvent` without an accompanying entry in `_AUDIBLE_EVENT_TYPES`.
- [ ] `tests/observation/test_service.py` adds an integration test that pins today's body-after-discovery filter behaviour: build a `WorldState` with a body in the observer's room, build a packet and assert the body appears in `visible_bodies`, then mutate `state.bodies[body_id]` so `discovered_by` is non-`None` and assert the same observer's next packet omits the body (including for the reporter themselves on the discovery tick). Name the test `test_discovered_body_is_hidden_from_subsequent_packets` or equivalent.
- [ ] `AGENTS.md` gains a new top-level `## PR description` section that names `.github/pull_request_template.md` as the canonical body shape, requires every PR — task-driven and ad-hoc (audits, hygiene, hotfixes) alike — to populate `## Summary`, `## Definition of done`, `## Decisions`, and (only when blocking) `## Questions`, and explicitly forbids `gh pr create --body ""` or `--fill` without a structured body. The section must mention that passing `--body` overrides the template.
- [ ] `scripts/prompt_template.md.j2` `Output expectation` block is aligned with `.github/pull_request_template.md`: it references the template file by path and enumerates `## Summary` alongside the existing `## Definition of done`, `## Decisions`, and `## Questions` requirements. After the template edit, run `uv run python scripts/generate_prompts.py` so every `agent_prompts/task-*.md` is regenerated against the new template; the diff to those files must be purely mechanical (no task-contract content changes).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

For the crewmate `find_path` hardening, mirror the impostor's existing pattern exactly so the codebase reads consistently:

```python
# agents/tactical/crewmate_policy.py
def _move_toward(self, *, own_room: RoomId, goal: RoomId, public_map: PublicMapView) -> ActionIntent:
    try:
        path = find_path(public_map=public_map, start=own_room, goal=goal)
    except ValueError:
        return self._wait()
    ...
```

Apply the same guard to `_flee_and_report`. The fallback should be `WaitIntent`, not `MoveIntent` to a neighbour — `wait` is the only intent that is always safe regardless of map state.

For the `AudibleEvent` enum coupling test, extract the Literal members deterministically rather than hard-coding them:

```python
from typing import get_args
from observation.packet import AudibleEvent

# AudibleEvent.model_fields["kind"].annotation is the Literal alias.
expected_kinds = set(get_args(AudibleEvent.model_fields["kind"].annotation))
assert set(agents.perception._AUDIBLE_EVENT_TYPES) == expected_kinds
```

For the body-after-discovery test, build the state by reusing `tests/observation/test_service.py::_base_world_state` and `_observation_service`, then either run a `report` action through `advance_tick` or directly mutate the body via `dataclasses.replace` to set `discovered_by`. Both approaches are valid; the direct-mutation form is shorter and pins the engine-visibility behaviour without coupling to the report rule.

For the Task 2.4 scope fix and the Task 2.6 narrowing note, edit `tasks/phase-2.md` only; do not touch `agents/runtime.py` or `agents/tactical/crewmate_policy.py`'s kill-witnessed branch — the changes are documentation-only.

For the `AGENTS.md` PR-description section, model it on the existing `## Definition of done (always)` section: short, imperative, no examples. Suggested shape:

```markdown
## PR description (always)

Every PR — task-driven or ad-hoc (audits, hygiene, hotfixes) — must
populate the sections in `.github/pull_request_template.md`:

- `## Summary` — 1–3 bullets stating what changed and why.
- `## Definition of done` — copy the task's checklist and tick each item;
  for ad-hoc PRs, list the scope you actually executed.
- `## Decisions` — every judgment call resolved without human input.
  Write "None." if there were none.
- `## Questions` — blocking questions only; omit the section if none.

When creating the PR with `gh pr create`, pass `--body` with a here-doc
containing the populated template. `gh pr create --fill` and
`gh pr create --body ""` both ship empty bodies and are not permitted.
```

For `scripts/prompt_template.md.j2`, the existing `## Output expectation` block reads:

```
The PR description must reference {{ task.section_refs }}, list the
definition-of-done checklist, and include `Decisions` and (if blocking)
`Questions` sections.
```

Replace it with a version that names the template and adds `## Summary`:

```
The PR description must follow `.github/pull_request_template.md` and
include `## Summary` (1–3 bullets referencing {{ task.section_refs }}),
`## Definition of done` (the checklist from this contract, ticked),
`## Decisions` (every judgment call), and (only when blocking) `## Questions`.
```

After editing the template, run `uv run python scripts/generate_prompts.py`. Every `agent_prompts/task-*.md` will see the new wording; that is the expected mechanical diff. `scripts/generate_prompts.py --check` must then pass.

**Integration risk:**

This task touches one tactical policy and three test files, plus two task contracts in `tasks/phase-2.md`.

- Crewmate find_path hardening must not change the policy's existing happy-path behaviour. Verify with the full `tests/agents/test_crewmate_policy.py` suite before declaring done; the existing 19 tests must still pass without modification.
- The L-5 body-after-discovery test pins current engine/visibility.py behaviour. If a future task wants to widen visibility for the reporter, that test will need to be updated alongside.
- `tasks/phase-2.md` changes must keep the task-doc validator green. Run `scripts/validate_task_docs.py` and `scripts/generate_prompts.py --check` before commit. The Task 2.4 scope fix is the most important: missing it leaves the M-1 finding unresolved.
- Editing `scripts/prompt_template.md.j2` will mass-regenerate every `agent_prompts/task-*.md`. The diff is expected to be large (≥56 files) but every change must be the same mechanical wording shift in the `## Output expectation` section. If any prompt diff includes a non-template change (task contract content, section reordering, formatting drift), stop and investigate — that would be a generator bug, not an expected regeneration.
- The `AGENTS.md` PR-description section is the only place that binds ad-hoc PRs (audits, hygiene). Without it, the PR-template gap re-opens the next time someone runs an ad-hoc PR creation.
- `audits/audit-2026-05-10-0721.md` is the source of these findings. Do not edit the audit report; it is a snapshot of state at audit time.

**Ready-to-paste prompt:** `agent_prompts/task-2-7-5-post-2-7-audit-repair.md`

### Task 2.8 — Headless game orchestrator
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


**Implementation hint:**

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

**Public types introduced:**
- `orchestrator.game.HeadlessGame`
- `orchestrator.game.HeadlessGameResult`
- `orchestrator.seeder.seed_initial_state`
- `orchestrator.scheduler.TickScheduler`

**Integration risk:**

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

**Ready-to-paste prompt:** `agent_prompts/task-2-8-headless-game-orchestrator.md`

### Task 2.9 — Headless tournament harness
**Branch:** `phase-2-headless-tournament-harness`
**Depends on:** 2.8 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

scripts/run_tournament.py and eval/balance_eval.py per §11.3. This task
aggregates many headless games; it must not invent the single-game
orchestrator.

**Files in scope:**
- scripts/run_tournament.py
- eval/balance_eval.py
- tests/eval/test_balance_eval.py

**Files NOT in scope:**
- engine/ core rule changes
- orchestrator/game.py
- agents/tactical/ policy changes
- llm/
- api/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Headless tournament harness runs multiple orchestrated games.
- [ ] Balance eval reports win rates across seeds.
- [ ] 100-game headless tournament completes without crashes.
- [ ] Both sides win > 20% of games.
- [ ] Leak test still passes across all tournament games.
- [ ] `uv run pytest tests/eval/test_balance_eval.py` passes.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

```python
# eval/balance_eval.py
@dataclass(frozen=True)
class BalanceReport:
    games: int
    crew_wins: int
    impostor_wins: int
    seeds_used: tuple[int, ...]

def run_balance_eval(*, seeds: Sequence[int]) -> BalanceReport: ...
```

Reuse `HeadlessGame` from 2.8 — do NOT reinvent the single-game loop.

**Public types introduced:**
- `eval.balance_eval.BalanceReport`
- `eval.balance_eval.run_balance_eval`

**Ready-to-paste prompt:** `agent_prompts/task-2-9-headless-tournament-harness.md`

## Merge Criteria
- 100-game headless tournament completes without crashes.
- Both sides win > 20% of games.
- Leak test still passes across all 100 games.
- `agents/` still has no direct or transitive imports from `engine/`.
