# Phase 2 — Tactical Agents

## Goal
Rule-based crewmate and impostor agents complete headless games without
crashing. Agents remain behind the observation firewall: they consume
`ObservationPacket` + `PublicMapView` and return `ActionIntent`, never engine
state or engine `Action`.

## Parallelism
Sequential through 2.5. Tasks 2.6 and 2.7 can run in parallel after 2.5. Task
2.8 runs after both policies merge. Task 2.9 runs after 2.8.

## Tasks

### Task 2.1 — Boundary contracts
**Branch:** `phase-2-boundary-contracts`
**Depends on:** Phase 1 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1

Define the engine-free schemas and adapters that let agents act without
importing engine types.

**Files in scope:**
- observation/action_intent.py
- observation/public_map.py
- orchestrator/boundary.py
- tests/observation/test_boundary_contracts.py
- tests/orchestrator/test_boundary.py
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
- [ ] `ActionIntent` is a Pydantic discriminated union for move, do_task, kill, vent, report, emergency, sabotage, and wait.
- [ ] `PublicMapView` exposes only public map topology needed by agents: map id, room ids, room neighbors, vent graph, task locations, spawn room, meeting room, and emergency button room.
- [ ] Orchestrator boundary helpers translate `PublicMapView` from an engine map and translate valid `ActionIntent` values into engine `Action` values.
- [ ] Invalid intents raise during translation; there are no silent fallbacks.
- [ ] `agents/` has no imports from `engine/`, directly or transitively.
- [ ] Relevant boundary and firewall tests pass.
- [ ] `uv run mypy --strict engine observation agents orchestrator` passes.
- [ ] `uv run ruff check .` passes.

**Ready-to-paste prompt:** `agent_prompts/task-2-1-boundary-contracts.md`

### Task 2.2 — Agent base + runtime
**Branch:** `phase-2-agent-base-runtime`
**Depends on:** 2.1 merged
**Section refs:** DESIGN.md §4.1

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

**Ready-to-paste prompt:** `agent_prompts/task-2-2-agent-base-runtime.md`

### Task 2.3 — Memory scaffolding (no LLM)
**Branch:** `phase-2-memory-scaffolding`
**Depends on:** 2.2 merged
**Section refs:** DESIGN.md §6.1

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

**Ready-to-paste prompt:** `agent_prompts/task-2-3-memory-scaffolding-no-llm.md`

### Task 2.4 — Perception ingestion
**Branch:** `phase-2-perception-ingestion`
**Depends on:** 2.3 merged
**Section refs:** DESIGN.md §4.2, DESIGN.md §6.2

Convert `ObservationPacket` into typed episodic events before tactical policies
read memory.

**Files in scope:**
- agents/perception.py
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

**Ready-to-paste prompt:** `agent_prompts/task-2-4-perception-ingestion.md`

### Task 2.5 — Pathing
**Branch:** `phase-2-pathing`
**Depends on:** 2.4 merged
**Section refs:** DESIGN.md §4.4

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

**Ready-to-paste prompt:** `agent_prompts/task-2-5-pathing.md`

### Task 2.6 — Crewmate FSM
**Branch:** `phase-2-crewmate-fsm`
**Depends on:** 2.5 merged
**Section refs:** DESIGN.md §4.4

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

**Ready-to-paste prompt:** `agent_prompts/task-2-6-crewmate-fsm.md`

### Task 2.7 — Impostor FSM
**Branch:** `phase-2-impostor-fsm`
**Depends on:** 2.5 merged
**Section refs:** DESIGN.md §4.4

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

**Ready-to-paste prompt:** `agent_prompts/task-2-7-impostor-fsm.md`

### Task 2.8 — Headless game orchestrator
**Branch:** `phase-2-headless-game-orchestrator`
**Depends on:** 2.6 merged, 2.7 merged
**Section refs:** DESIGN.md §1.4, DESIGN.md §3.1, DESIGN.md §11.4

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

**Ready-to-paste prompt:** `agent_prompts/task-2-8-headless-game-orchestrator.md`

### Task 2.9 — Headless tournament harness
**Branch:** `phase-2-headless-tournament-harness`
**Depends on:** 2.8 merged
**Section refs:** DESIGN.md §11.3

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

**Ready-to-paste prompt:** `agent_prompts/task-2-9-headless-tournament-harness.md`

## Merge Criteria
- 100-game headless tournament completes without crashes.
- Both sides win > 20% of games.
- Leak test still passes across all 100 games.
- `agents/` still has no direct or transitive imports from `engine/`.
