# Phase 1 — Simulation Core

## Goal
The engine ticks deterministically, ObservationService produces packets that pass the leak test, replay is byte-exact.

## Parallelism
One foreground CLI agent on the engine. In parallel, a second agent can build determinism and leak test fixtures after schemas are stable.

## Tasks
### Task 1.1 — Static map data
**Branch:** `phase-1-static-map-data`
**Depends on:** Phase 0 merged
**Section refs:** DESIGN.md §3, DESIGN.md §8.1

engine/world.py::Map, room graph, vent network. One canonical map as YAML.

**Files in scope:**
- engine/world.py
- TODO_REVIEW canonical map YAML path

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Static map data exists as specified by the Phase 1 plan.
- [ ] Room graph and vent network are represented for one canonical MVP map.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-1-static-map-data.md`

### Task 1.2 — State model
**Branch:** `phase-1-state-model`
**Depends on:** 1.1 merged
**Section refs:** DESIGN.md §3.2

WorldState, PlayerState, BodyState, TaskState, SabotageState per §3.2.

**Files in scope:**
- engine/world.py
- engine/entities.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] WorldState, PlayerState, BodyState, TaskState, and SabotageState exist per DESIGN.md §3.2.
- [ ] Engine state models are immutable where required.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-2-state-model.md`

### Task 1.3 — Action types
**Branch:** `phase-1-action-types`
**Depends on:** 1.2 merged
**Section refs:** DESIGN.md Appendix A

engine/actions.py Pydantic union per §A. Validators.

**Files in scope:**
- engine/actions.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Action types are represented as a Pydantic union per DESIGN.md Appendix A.
- [ ] Validators reject invalid action payloads.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-3-action-types.md`

### Task 1.4 — Rules
**Branch:** `phase-1-rules`
**Depends on:** 1.3 merged
**Section refs:** DESIGN.md §3.4, DESIGN.md §3.5

engine/rules.py for kill, vent, report, sabotage, win conditions per §3.4 + §3.5.

**Files in scope:**
- engine/rules.py
- engine/win_conditions.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Kill, vent, report, emergency meeting, sabotage, and win-condition rules match DESIGN.md §3.4 and §3.5.
- [ ] Invalid actions raise or emit rejection as specified; no silent fallbacks.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-4-rules.md`

### Task 1.5 — advance_tick
**Branch:** `phase-1-advance-tick`
**Depends on:** 1.4 merged
**Section refs:** DESIGN.md §3.1

Pure function (state, actions) -> (state', events) per §3.1. RNG threaded through engine/rng.py.

**Files in scope:**
- engine/tick.py
- engine/rng.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] advance_tick follows the seven-step loop in DESIGN.md §3.1.
- [ ] RNG state is explicitly threaded through engine/rng.py.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-5-advance-tick.md`

### Task 1.6 — Visibility
**Branch:** `phase-1-visibility`
**Depends on:** 1.5 merged
**Section refs:** DESIGN.md §3.6, DESIGN.md §1.3

engine/visibility.py per §3.6 + §1.3 simplifications (room + adjacent room).

**Files in scope:**
- engine/visibility.py

**Files NOT in scope:**
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Visibility logic preserves hidden information per DESIGN.md §3.6.
- [ ] Room and adjacent-room simplifications are implemented as described in the Phase 1 plan.
- [ ] Relevant engine tests pass.
- [ ] mypy --strict passes on touched engine files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-6-visibility.md`

### Task 1.7 — ObservationService
**Branch:** `phase-1-observation-service`
**Depends on:** 1.6 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §4.2

observation/service.py and ObservationPacket schema per §1.3 + §4.2. Audit log to disk.

**Files in scope:**
- observation/service.py
- observation/packet.py
- observation/audit.py

**Files NOT in scope:**
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] ObservationPacket schema matches DESIGN.md §4.2.
- [ ] ObservationService is the only boundary crossing from engine truth to agent observations.
- [ ] Audit log records every packet.
- [ ] Relevant observation tests pass.
- [ ] mypy --strict passes on observation/.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-7-observationservice.md`

### Task 1.8 — Replay log
**Branch:** `phase-1-replay-log`
**Depends on:** 1.7 merged
**Section refs:** DESIGN.md §3.1, DESIGN.md §11.1, DESIGN.md §11.4

orchestrator/replay.py writes JSONL of (tick, actions, state-hash) per game.

**Files in scope:**
- orchestrator/replay.py

**Files NOT in scope:**
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Replay log writes JSONL entries containing tick, actions, and state hash per game.
- [ ] Replay output supports byte-identical determinism checks.
- [ ] Relevant replay/determinism tests pass.
- [ ] mypy --strict passes on touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-8-replay-log.md`

### Task 1.B1 — Test fixtures
**Branch:** `phase-1-test-fixtures`
**Depends on:** 1.3 merged
**Section refs:** DESIGN.md §11.1

Hand-author tests/fixtures/scripted_game_*.json short canned games used by the determinism test. Does not touch engine code.

**Files in scope:**
- tests/fixtures/scripted_game_*.json

**Files NOT in scope:**
- engine/
- agents/
- observation/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Short canned scripted game fixtures exist for determinism testing.
- [ ] Fixtures use the stable action schema from task 1.3.
- [ ] No engine code is modified.
- [ ] pytest fixture-loading tests pass if present.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-b1-test-fixtures.md`

### Task 1.B2 — Leak test implementation
**Branch:** `phase-1-leak-test-implementation`
**Depends on:** 1.7 merged
**Section refs:** DESIGN.md §11.2, DESIGN.md §1.3

Once ObservationPacket exists, implement the actual leak-test assertions. Can be done in parallel with task 1.8.

**Files in scope:**
- eval/leak_test.py

**Files NOT in scope:**
- engine/
- agents/
- api/
- frontend/
- llm/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] eval/leak_test.py asserts observation purity for hidden fields.
- [ ] Leak test runs against three scripted games.
- [ ] pytest eval/leak_test.py passes.
- [ ] No engine code is modified.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-1-b2-leak-test-implementation.md`

## Merge Criteria
- pytest tests/engine/ green.
- pytest eval/leak_test.py green against three different scripted games.
- pytest eval/determinism_test.py green: identical seed + actions -> identical replay log.
- mypy --strict engine/ observation/ green.
