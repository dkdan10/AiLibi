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

### Task 2.8.5 — Critical leak repair and tactical termination
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

**Implementation hint:**

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

**Integration risk:**

This task is large in line count because the id rename cascades through
many test files. Treat the rename as mechanical find-and-replace; every
*non-rename* change should appear in one of `orchestrator/seeder.py`,
`agents/tactical/crewmate_policy.py`, `eval/leak_test.py`, or the new
regression tests.

- The id rename changes the byte content of `tests/fixtures/scripted_game_*.json`.
  Determinism is preserved because `eval/determinism_test.py` compares
  two runs of the *same* fixture against each other (not against a
  recorded reference); both runs use the renamed fixtures, so byte-
  identity holds. Verify explicitly:
  `uv run pytest eval/determinism_test.py -v`.
- The new value-scanning leak test will fail against the *current* code
  but should pass once the id rename is complete. Land both pieces in
  the same commit so CI never sees an intermediate broken state.
- The crewmate task-completion fix must not break any existing
  `tests/agents/test_crewmate_policy.py` test. Run the full crewmate
  suite before and after the fix; the only expected new failure is your
  newly authored regression test failing on the pre-fix code and
  passing on the post-fix code.
- `agents/tactical/impostor_policy.py` is explicitly out of scope.
  Tests under `tests/agents/test_impostor_policy.py` are in scope only
  for the id rename — no behavioural changes there. If you find a
  hardcoded id in the policy source itself (not the tests), stop and
  flag it as a separate finding.
- `audits/*` are read-only artifacts. Do not edit any audit report; this
  task addresses findings, it does not amend the records of those
  findings.

**Ready-to-paste prompt:** `agent_prompts/task-2-8-5-critical-leak-repair-and-tactical-termination.md`

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
- [ ] Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); `TICK_BUDGET_REACHED` games are reported separately and do not count toward decisive totals.
- [ ] `TICK_BUDGET_REACHED` is a first-class outcome bucket in the tournament report, reported alongside `CREWMATES` and `IMPOSTORS` (and `MEETING_PHASE_REACHED` when the meeting manager has not landed). Non-decisive outcomes must not be silently dropped or coerced into the decisive buckets.
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
    tick_budget_reached: int
    seeds_used: tuple[int, ...]

def run_balance_eval(*, seeds: Sequence[int]) -> BalanceReport: ...
```

Reuse `HeadlessGame` from 2.8 — do NOT reinvent the single-game loop.

**Public types introduced:**
- `eval.balance_eval.BalanceReport`
- `eval.balance_eval.run_balance_eval`

**Ready-to-paste prompt:** `agent_prompts/task-2-9-headless-tournament-harness.md`

### Task 2.10 — Pre-Phase-3 tactical repair
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

**Implementation hint:**

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

**Public types introduced:**
None.

**Integration risk:**

This task is the convergence point for the Phase 2 acceptance gates. It changes engine win-condition behavior (R-5) and impostor tactical scoring (R-3), and re-runs the headless gates that the audit reproduces.

- **Determinism:** `tests/orchestrator/test_game.py:139-155` pins default-agent byte-identical replay over 20 ticks. R-5 and R-3 will change the byte content of those replays; re-record the baseline within this PR if the existing assertion compares against a frozen reference. If the test compares two live runs of the same fixture against each other, byte identity must still hold post-fix — verify explicitly with `uv run pytest tests/orchestrator/test_game.py -v`.
- **Engine purity:** `engine/win_conditions.py` and `engine/tick.py` remain pure functions of state and actions. Do not add agent imports, randomness, or hidden state. The R-5 rule must be expressible as a state-only function.
- **Observation firewall:** R-3's `confirmed_dead` set must be derived from agent-owned memory, not from engine state. If you choose Implementation-hint option 2, add `agents/memory/beliefs.py` to scope explicitly. Either way, run `uv run lint-imports` to confirm the firewall holds.
- **Leak scan:** R-3 may add new fields or values to belief state; if so, re-run `uv run pytest eval/leak_test.py` and confirm the value-scanner still passes against all three scripted fixtures and the 100-game tournament audit logs.
- **Merge-criterion text:** the R-5 rule is `dropped`, so no edit to the Phase 2 Merge Criteria wording is needed. Task 2.11's R-8 cleanup still owns the separate "games" vs "decisive games" wording fix.
- **Tournament re-run cost:** `scripts/run_tournament.py` against 100 games at max-ticks 1000 takes ~minutes on a default workstation. Budget for it; do not gate the merge on faster runs.
- **`audits/*` are read-only artifacts.** Do not edit the reconciled audit; this task addresses its findings, it does not amend the record.

**Ready-to-paste prompt:** `agent_prompts/task-2-10-pre-phase-3-tactical-repair.md`

### Task 2.10.5 — Phase 2 tournament balance
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

**Implementation hint:**

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

**Public types introduced:**
None. (`tasks_per_crewmate` is a new parameter on existing public `seed_initial_state`, not a new type.)

**Integration risk:**

This task changes the canonical game balance. It is config and seeder work only — no engine logic changes.

- **Test cascades:** Cooldown, sabotage, and tasks-per-crewmate changes will break any test that asserts the specific value. Identify the cascades with `git grep -nE "kill_cooldown_ticks|tasks_per_crewmate|duration_ticks.*90" tests/` before editing; update each as part of this PR; enumerate in `## Decisions`.
- **Determinism:** Replay byte content will change for every fixture that runs against the canonical map. The existing tests at `tests/orchestrator/test_game.py:139-155` and `eval/determinism_test.py` compare two live runs of the same fixture against each other (not against a frozen reference), so byte identity must still hold post-change. Verify explicitly; if any test compares against a frozen byte sequence, re-record within this PR and document.
- **Leak scan:** No leak scan content should change (no new packet fields). Re-run `uv run pytest eval/leak_test.py` as a defensive check.
- **Tournament cost:** Each Path A candidate takes ~minutes for the 100-game run. The full search space is up to 8 configs (4 cooldown values + 4 cooldown×tpc pairs + 4 cooldown×tpc×sab triples), so budget up to ~30-45 minutes of tournament runtime if Path A exhausts.
- **Phase 3 dependency:** Path D moves the strict balance criterion to Phase 3.12's Merge Criteria. Phase 3.12 (`tasks/phase-3.md`) currently does not contain this criterion; if Path D fires, the new bullet must be added cleanly without disrupting existing Phase 3 task contracts. Do not edit any Phase 3 task body — only the Phase 3 Merge Criteria block.
- **Search space discipline:** If the implementing agent finds that no documented config balances but a config outside the search space might, **do not extend the search** — fall back to Path D as contracted. Extending the search is a scope change that belongs to a different task. Record the suggestion as a `## Decisions` follow-up note.
- **`audits/*` are read-only artifacts.** Do not edit the reconciled audit; this task addresses R-1, it does not amend the record of R-1.

**Ready-to-paste prompt:** `agent_prompts/task-2-10-5-phase-2-tournament-balance.md`

### Task 2.11 — Contract hygiene and test-guard cleanup
**Branch:** `phase-2-contract-hygiene-cleanup`
**Depends on:** 2.10 merged, 2.10.5 merged, 2.8.5 merged, 2.9 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §11.2, DESIGN.md §11.3
**Complexity:** Medium

Close the four documentation, test-fixture, and task-contract findings in
`audits/audit-2026-05-15-0225-reconciled.md` that are pure hygiene: R-4
(the Task 2.8.5 old-id grep guard cannot be used as written because the
literal hits are planted scanner self-tests), R-7 (Task 2.8.5's
`Files in scope` list omits files the implementing PR touched), R-8 (Task
2.9 DoD wording at `tasks/phase-2.md:927` disagrees with the Phase 2
Merge Criterion at `:959`), and R-14 (`tests/observation/test_service.py`
helper ids still use role-bearing strings outside the value-scanner
harness). None of these touches runtime code. The four diffs do not
overlap.

**Files in scope:**
- eval/leak_test.py
- tests/eval/test_balance_eval.py
- tests/observation/test_service.py
- tasks/phase-2.md

**Files NOT in scope:**
- engine/
- observation/
- orchestrator/
- agents/
- llm/
- api/
- frontend/
- scripts/
- eval/balance_eval.py
- eval/determinism_test.py
- DESIGN.md
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/engine/
- tests/meetings/
- tests/orchestrator/
- tests/observation/test_boundary_contracts.py
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-4 — old-id grep guard cleared:** Replace the planted role-bearing-id strings in `eval/leak_test.py:181`, `eval/leak_test.py:228`, and `tests/eval/test_balance_eval.py:258` with sentinels that still trip the value-scanner (i.e. contain one of `impostor` / `crewmate` / `crew`) but do not match the legacy regex `["'](player|impostor)-[0-9]+["']`. After the edit, `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/` must return empty. The negative-test semantics (scanner trips, allow-list permits `self_state.role`, nested-path message format) must remain unchanged — verify with `uv run pytest eval/leak_test.py tests/eval/test_balance_eval.py -v`. The Task 2.8.5 DoD bullet `Use \`git grep ... tests/\` ... the post-fix grep must be empty` is then satisfiable as written.
- [ ] **R-7 — Task 2.8.5 file-scope drift recorded retroactively:** Append a short prose note after the Task 2.8.5 Implementation hint and before the Integration risk block, stating that the merged PR (commit `e3b2a60`) also touched `eval/determinism_test.py`, `tests/engine/test_actions.py`, `tests/engine/test_events.py`, `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`, and `agent_prompts/task-2-9-headless-tournament-harness.md` as mechanical fallout of the `p-N` id rename. The note must state that these files are retroactively considered in scope for that historical PR and that the rename did not change behavior. Do not edit the Task 2.8.5 `Files in scope` list — the historical contract stays as merged; the note documents the actual diff.
- [ ] **[Optional] Task 2.10.5 file-scope drift recorded retroactively:** Same pattern as R-7, applied to Task 2.10.5. Append a short prose note after the Task 2.10.5 Implementation hint and before the Integration risk block, stating that the merged PR (commit `<PR #31 merge commit sha>`) also updated two cooldown-value literal assertions in `tests/engine/test_tick.py:110, 117` (`== 10` → `== 4`, `== 9` → `== 3`) as mechanical fallout of the `kill_cooldown_ticks` 10 → 4 retune. The Task 2.10.5 `Test cascades resolved` DoD bullet enumerated four cascade test files but missed `tests/engine/test_tick.py`; this note states the file is retroactively considered in scope for that historical PR and that the literal-value updates did not change behavior. Do not edit the Task 2.10.5 `Files in scope` or `Files NOT in scope` lists — the historical contract stays as merged. **Skip without penalty** if the existing `## Decisions` record in PR #31 is judged sufficient.
- [ ] **R-8 — Task 2.9 DoD wording aligned with merge criterion:** Replace the line at `tasks/phase-2.md:927` (`Both sides win > 20% of games.`) with the exact wording from `tasks/phase-2.md:959`: `Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); \`TICK_BUDGET_REACHED\` games are reported separately and do not count toward decisive totals.` The `## Merge Criteria` block at the file's tail must not move; the criterion text there stays identical to the post-edit Task 2.9 bullet.
- [ ] **R-14 — observation test helper ids renamed:** Rewrite the role-bearing helper ids in `tests/observation/test_service.py:49-58` (`"victim"`, `"observer"`, `"crew-2"`, `"impostor"`) to the role-neutral `p-N` convention from `orchestrator/seeder.py`. Update every downstream reference in the same file, including `cooldowns`, action `actor`, action `target`, `agent_id` arguments, `_visible_player` lookups, and assertion strings. The scenarios under test (kill-witnessed adjacency, body-after-discovery filter, cooldown emission, witness rules) must keep their existing semantics; the rewrite is purely id substitution.
- [ ] After the Task 2.9 DoD edit, run `uv run python scripts/generate_prompts.py`. The diff to `agent_prompts/task-2-9-headless-tournament-harness.md` is expected as mechanical fallout from the contract edit and is the only out-of-scope file the PR is permitted to touch.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

For R-4, the smallest faithful change is to swap the role-bearing literals for sentinels that still contain one of the forbidden substrings (so the value-scanner still trips) but no longer match the legacy id regex. Example:

```python
# eval/leak_test.py:228 (test body) — before
{"id": "impostor-1", "room": "STORAGE", "action": None},
# after
{"id": "crew_role_leak_fixture", "room": "STORAGE", "action": None},
```

The scanner regex `_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")` still trips on `crew_role_leak_fixture` (substring `crew`). The grep pattern `['"]((player|impostor)-[0-9]+)['"]` no longer matches. Update the docstring at `eval/leak_test.py:181` analogously — replace the example strings inside the comment with the same sentinel form. The `match=` regex in the `pytest.raises` blocks is keyed on JSON path (`$.visible_players[0].id`), not on value text, so it does not need to change.

For R-7, model the historical note on the language already in Task 2.7.5's narrowing note (`tasks/phase-2.md:371-376`) — short, factual, marked with a date so future readers know it is a retroactive amendment:

```markdown
> Historical note (added 2026-05-15 by Task 2.11): the merged PR for this
> task (commit `e3b2a60`) also touched `eval/determinism_test.py`,
> `tests/engine/test_actions.py`, `tests/engine/test_events.py`,
> `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`,
> and `agent_prompts/task-2-9-headless-tournament-harness.md` as
> mechanical fallout of the `p-N` id rename. Those files are retroactively
> considered in scope for that historical PR; the rename did not change
> behavior.
```

For R-8, the edit is a single-line replacement at `tasks/phase-2.md:927`. The Phase 2 Merge Criteria block at `:959` already has the correct wording; copy it verbatim. Do not edit the Merge Criteria block — the goal is to make the two locations agree, and the criterion is the authoritative phrasing.

For R-14, a clean substitution mapping keeps the rewrite mechanical and easy to review:

| Old | New |
| --- | --- |
| `"victim"` | `"p-1"` |
| `"observer"` | `"p-2"` |
| `"crew-2"` | `"p-3"` |
| `"impostor"` | `"p-4"` |

Apply globally inside `tests/observation/test_service.py` only. After the rewrite, `git grep -nE "['\"](player|impostor|victim|observer|crew-[0-9]+)['\"]" tests/observation/test_service.py` should be empty. The witness/visibility scenarios continue to read naturally because the rooms (`STORAGE`, `REACTOR`, `ADMIN`) and the `cooldowns` dictionary still encode the same setup.

**Public types introduced:**
None.

**Ready-to-paste prompt:** `agent_prompts/task-2-11-contract-hygiene-and-test-guard-cleanup.md`

### Task 2.12 — Behavioral merge-criteria CI gates and remaining test hygiene
**Branch:** `phase-2-behavioral-ci-gates`
**Depends on:** 2.10 merged, 2.10.5 merged, 2.11 merged
**Section refs:** DESIGN.md §11.2, DESIGN.md §11.3, DESIGN.md §11.4
**Complexity:** Medium

Close the three test-coverage findings in
`audits/audit-2026-05-15-0225-reconciled.md` that prevent the Phase 2
acceptance gates from regressing silently: R-11 (no automated guard for
the decisive-outcome sweep or 100-game balance criterion — the repository
was green while those gates were failing live), R-13 (audit-log
append-mode regression absent — a future `"a"` → `"w"` change would slip
past current single-instance tests), and R-12 (property-test action
vocabulary intentionally limited to `move`/`wait`, leaving
kill/vent/report interleavings unexplored). All three are test-only
additions. None touches production code, and Task 2.10's behavioral
fixes must be merged first so the new gate encodes the passing outcome
rather than the pre-2.10 failing one.

**Files in scope:**
- tests/eval/test_balance_eval.py
- tests/observation/test_service.py
- tests/engine/test_tick_properties.py

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
- DESIGN.md
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- audits/
- tasks/
- agent_prompts/
- README.md
- open_issues.md
- tests/agents/
- tests/meetings/
- tests/orchestrator/
- tests/observation/test_boundary_contracts.py
- tests/engine/test_actions.py
- tests/engine/test_events.py
- tests/engine/test_map_loader.py
- tests/engine/test_rng.py
- tests/engine/test_tick.py
- tests/engine/test_visibility.py
- tests/engine/test_world_state.py
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-11 — decisive-outcome CI guard:** `tests/eval/test_balance_eval.py` gains a test that runs a small, documented set of default-agent seeds (e.g. three to five seeds chosen so at least one is known-decisive post-2.10) through `HeadlessGame`, counts decisive outcomes (`CREWMATES` or `IMPOSTORS`), and fails if zero seeds are decisive. The seed list, the post-2.10 expected outcome for each seed, and a comment naming this guard as the R-11 CI floor must be encoded in the test file. The test must run within the existing pytest budget (target ≤ ~5s; bound it with a low `max_ticks` if necessary, e.g. 200). This test must encode the passing outcome from Task 2.10's R-2 sweep; it must not encode the pre-2.10 failing outcome.
- [ ] **R-13 — audit-log append-mode regression:** `tests/observation/test_service.py` gains a test (e.g. named `test_audit_log_appends_across_two_instances`) that constructs one `ObservationService` (or its `ObservationAuditLog`) pointed at a tmp path, records at least one packet, discards the instance, opens a second instance pointed at the same path, records another packet, and asserts the file contains both packets in order (e.g. two JSON lines). The test must fail if `observation/audit.py:20-23` is ever changed from `"a"` to `"w"` and must not import from `engine/` directly (use existing test helpers).
- [ ] **R-12 — broadened property-test vocabulary:** `tests/engine/test_tick_properties.py` gains a second `hypothesis` strategy (or a parametrized expansion of the existing strategy) that draws batches mixing role-valid `kill`, `vent`, `report`, and `wait` actions, plus a property covering the new vocabulary (at minimum: `advance_tick` does not raise on any drawn batch where roles and aliveness allow the action). The existing `move`/`wait` strategy stays untouched; the comment at `tests/engine/test_tick_properties.py:6-10` is updated to record that the broader vocabulary now ships alongside.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

For R-11, lean on the seed list Task 2.10's R-2 bullet records. Pick a subset that is small enough to be CI-friendly (≤ 5 seeds, ≤ 200 ticks each) and that includes at least one seed Task 2.10 ended at `CREWMATES` or `IMPOSTORS`:

```python
# tests/eval/test_balance_eval.py
_R11_CI_GUARD_SEEDS: Final[tuple[int, ...]] = (0, 1, 2, 7, 42)
_R11_CI_GUARD_MAX_TICKS: Final[int] = 200

def test_default_agent_sweep_reaches_at_least_one_decisive_outcome(
    tmp_path: Path,
) -> None:
    """R-11 CI floor: after Task 2.10 the small seed sweep must yield at
    least one decisive outcome. If this test fails, the Phase 2 tactical
    fixes (R-1/R-2/R-3) have regressed; investigate before reverting."""
    decisive = 0
    for seed in _R11_CI_GUARD_SEEDS:
        result = HeadlessGame(
            seed=seed,
            game_map=load_canonical_map(),
            replay_path=tmp_path / f"r-{seed}.jsonl",
            max_ticks=_R11_CI_GUARD_MAX_TICKS,
        ).run()
        if result.outcome in {"CREWMATES", "IMPOSTORS"}:
            decisive += 1
    assert decisive >= 1, (
        "R-11 regression: zero decisive outcomes across the CI guard "
        "seeds; see audits/audit-2026-05-15-0225-reconciled.md §R-11."
    )
```

If the existing test file does not import `HeadlessGame` / `load_canonical_map` / `Path` yet, add only the imports needed for the new test — do not reorganize the file. The 100-game tournament gate remains a local-only check; do not put a 100-game run in CI.

For R-13, model the new test on the existing `test_audit_log_records_sanitized_packet` at `tests/observation/test_service.py:289`. The simplest form:

```python
def test_audit_log_appends_across_two_instances(tmp_path: Path) -> None:
    state = _base_world_state()
    service_one = _observation_service(tmp_path)
    service_one.build_packet(world_state=state, agent_id="p-1", engine_events=[])
    del service_one
    service_two = ObservationService(
        game_map=load_canonical_map(),
        audit_log_path=tmp_path / "observation_audit.jsonl",
    )
    service_two.build_packet(world_state=state, agent_id="p-2", engine_events=[])
    lines = (tmp_path / "observation_audit.jsonl").read_text().splitlines()
    assert len(lines) == 2
```

Use whichever player ids Task 2.11's R-14 rewrite settled on; do not re-introduce role-bearing helper ids. The path string must match `_observation_service`'s default.

For R-12, the existing strategy at `tests/engine/test_tick_properties.py:6-10` is the template. Add a sibling strategy (`hypothesis.strategies.composite`) that draws role-valid action tuples:

```python
@composite
def _role_aware_action_batches(draw, *, world_state):
    """Draw a batch mixing kill, vent, report, and wait actions, gated by
    the actor's role and aliveness. Used by the role-vocabulary property
    in addition to the existing move/wait property."""
    ...

@given(world_state=_world_states(), batch=_role_aware_action_batches(...))
def test_role_aware_action_batches_do_not_raise(world_state, batch):
    advance_tick(world_state, batch, game_map=load_canonical_map())
```

Keep the new property's invariant narrow: "does not raise" is enough; deeper invariants (e.g. role-correct event emission) can land later.

**Public types introduced:**
None.

**Ready-to-paste prompt:** `agent_prompts/task-2-12-behavioral-merge-criteria-ci-gates-and-remaining-test-hygiene.md`

### Task 2.13 — Pre-Phase-3 post-audit cleanup
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

**Implementation hint:**

For R-1, the current paragraph at `DESIGN.md:291` reads (paraphrased): `(2) tasks_per_crewmate ∈ {2, 3} (a parameter on orchestrator.seeder.seed_initial_state) paired with kill_cooldown_ticks ∈ {6, 4}` and `Current canonical default: kill_cooldown_ticks=4, tasks_per_crewmate=1, sabotages.lights.duration_ticks=90`. After the edit, the first line acknowledges the parameter does not yet exist while preserving the lever as a future option:

```markdown
(2) `tasks_per_crewmate ∈ {2, 3}` (would require parameterizing
`orchestrator.seeder.seed_initial_state`; currently hardcoded to one
task per crewmate by `_build_tasks`) paired with
`kill_cooldown_ticks ∈ {6, 4}`
```

And the canonical-default line becomes:

```markdown
Current canonical defaults: `kill_cooldown_ticks=4`,
`sabotages.lights.duration_ticks=90`.
```

For R-2, the test should re-use the existing tick-test scaffolding. The shape (illustrative; pick names consistent with the file's conventions):

```python
def test_kill_removing_last_incomplete_task_triggers_crew_win_same_tick() -> None:
    """R-2: documented in DESIGN.md §3.5 — an impostor kill that
    removes the last incomplete task in state.tasks triggers the
    crew win condition on the same tick. This pins the documented
    consequence so a future refactor of the tick loop cannot
    silently regress it.
    """
    # Build state: 1 incomplete task owned by p-2 (victim), 0 others.
    state = ...  # one alive impostor, one alive crewmate (victim)
    actions = (KillAction(actor="p-1", payload=...),)
    next_state, events = advance_tick(state, actions, game_map=game_map)
    game_over_events = [e for e in events if isinstance(e, GameOverEvent)]
    assert game_over_events, "expected GameOverEvent on same-tick kill"
    assert game_over_events[0].winner == "CREWMATES"
    assert game_over_events[0].reason == "CREWMATE_TASKS"
```

The existing `test_dead_crewmate_incomplete_task_is_dropped_and_crew_can_still_win` test at `tests/engine/test_tick.py:911-988` is the closest neighbor; model setup helpers on it.

For R-3, the malformed-payload test bypasses the helper's typing:

```python
def test_confirmed_dead_from_bodies_raises_on_missing_body_id() -> None:
    """R-3: the ValueError guard at impostor_policy.py:260-263 is
    the Phase-2 type-safety bridge while the body-id format is
    parsed as a string. Pin the branch so a future change to the
    saw_body payload shape cannot silently disable confirmed-dead
    pruning.
    """
    malformed = EpisodicEvent(
        tick=0,
        type=EVENT_SAW_BODY,
        payload={"room": "MEDBAY"},  # body_id missing
    )
    with pytest.raises(ValueError, match="body_id"):
        ImpostorPolicy._confirmed_dead_from_bodies((malformed,))
```

If the test file does not already import `EpisodicEvent` or `EVENT_SAW_BODY` at the top, add only the imports the new test needs.

For R-7 (optional), the rename is a literal find-and-replace within `tests/observation/test_service.py` at lines 343 and 358. After the rename, the test scenarios continue to read the same way because the body id is opaque to the filter logic. Skip if you prefer to leave the deviation in PR #33's audit trail.

**Public types introduced:**
None.

**Integration risk:**

This task adds two regression tests and one documentation edit. Low blast radius.

- **R-2 setup specificity:** The test must build a state whose initial `state.tasks` contains exactly one incomplete task (owned by the kill victim) and zero other tasks of any kind. If the seeder helper assigns multiple tasks per crewmate by default, you may need to construct the state directly rather than via `seed_initial_state`. Either approach is acceptable; the goal is the assertion, not the setup style.
- **R-3 helper bypass:** The `_saw_body_event` helper at `tests/agents/test_impostor_policy.py:101-106` types `body_id: str`. Bypassing it is intentional — the test exercises the malformed-payload branch the helper cannot reach. Do not modify the helper.
- **DESIGN.md edit scope:** Only the §3.5 tuning-lever paragraph at line 291 is in scope. Do not touch the surrounding `dropped`-rule paragraphs (those are correct as written) or any other section.
- **`audits/*` are read-only artifacts.** Do not edit the reconciled audit; this task addresses its findings, it does not amend the record.

**Ready-to-paste prompt:** `agent_prompts/task-2-13-pre-phase-3-post-audit-cleanup.md`

## Merge Criteria
- 100-game headless tournament completes without crashes.
- Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); `TICK_BUDGET_REACHED` games are reported separately and do not count toward decisive totals.
- Leak test still passes across all 100 games.
- `agents/` still has no direct or transitive imports from `engine/`.
