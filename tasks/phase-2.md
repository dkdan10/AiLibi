# Phase 2 — Tactical Agents

## Goal
Rule-based crewmate and impostor agents complete games headlessly without crashing. Win rates land in a believable band even without LLMs.

## Parallelism
Sequential through 2.3, then 2.4 and 2.5 can run in parallel. 2.6 runs after both policies merge.

## Tasks
### Task 2.1 — Agent base + runtime
**Branch:** `phase-2-agent-base-runtime`
**Depends on:** Phase 1 merged
**Section refs:** DESIGN.md §4.1

agents/base.py and agents/runtime.py per §4.1. Memory wiring stub.

**Files in scope:**
- agents/base.py
- agents/runtime.py

**Files NOT in scope:**
- engine/
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] AgentInterface protocol and AgentRuntime wiring match DESIGN.md §4.1.
- [ ] Runtime consumes ObservationPacket rather than engine state.
- [ ] No imports from engine/ under agents/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-2-1-agent-base-runtime.md`

### Task 2.2 — Memory scaffolding (no LLM)
**Branch:** `phase-2-memory-scaffolding`
**Depends on:** 2.1 merged
**Section refs:** DESIGN.md §6.1

agents/memory/episodic.py, working.py, beliefs.py per §6.1. Write paths only; no rendering yet.

**Files in scope:**
- agents/memory/episodic.py
- agents/memory/working.py
- agents/memory/beliefs.py

**Files NOT in scope:**
- engine/
- llm/
- agents/memory/store.py
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Episodic, working, and belief memory scaffolds exist per DESIGN.md §6.1.
- [ ] Write paths are implemented; prompt rendering is not implemented in this task.
- [ ] No imports from engine/ under agents/.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-2-2-memory-scaffolding-no-llm.md`

### Task 2.3 — Pathing
**Branch:** `phase-2-pathing`
**Depends on:** 2.2 merged
**Section refs:** DESIGN.md §4.4

agents/tactical/pathing.py - A* over room graph.

**Files in scope:**
- agents/tactical/pathing.py

**Files NOT in scope:**
- engine/
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] A* pathing over the room graph exists per DESIGN.md §4.4.
- [ ] Pathing remains deterministic for the same inputs.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant agent tests pass.
- [ ] mypy --strict agents/ passes for touched files.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-2-3-pathing.md`

### Task 2.4 — Crewmate FSM
**Branch:** `phase-2-crewmate-fsm`
**Depends on:** 2.3 merged
**Section refs:** DESIGN.md §4.4

agents/tactical/crewmate_policy.py per §4.4.

**Files in scope:**
- agents/tactical/crewmate_policy.py

**Files NOT in scope:**
- engine/
- llm/
- agents/tactical/impostor_policy.py
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Crewmate FSM implements IDLE -> MOVE_TO_TASK -> DO_TASK -> IDLE and listed interrupts.
- [ ] Tactical decisions are deterministic and rule-based.
- [ ] No LLM calls in agents/tactical/.
- [ ] No imports from engine/ under agents/.
- [ ] Relevant agent tests pass.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-2-4-crewmate-fsm.md`

### Task 2.5 — Impostor FSM
**Branch:** `phase-2-impostor-fsm`
**Depends on:** 2.3 merged
**Section refs:** DESIGN.md §4.4

agents/tactical/impostor_policy.py per §4.4.

**Files in scope:**
- agents/tactical/impostor_policy.py

**Files NOT in scope:**
- engine/
- llm/
- agents/tactical/crewmate_policy.py
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Impostor FSM implements IDLE -> STALK -> KILL_OPPORTUNITY -> KILL -> COVER.
- [ ] Target selection uses isolation, witness-risk, and kill-cooldown scoring as specified.
- [ ] Tactical decisions are deterministic and rule-based.
- [ ] No LLM calls in agents/tactical/.
- [ ] No imports from engine/ under agents/.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-2-5-impostor-fsm.md`

### Task 2.6 — Headless tournament harness
**Branch:** `phase-2-headless-tournament-harness`
**Depends on:** 2.4 merged, 2.5 merged
**Section refs:** DESIGN.md §11.3

scripts/run_tournament.py, eval/balance_eval.py per §11.3.

**Files in scope:**
- scripts/run_tournament.py
- eval/balance_eval.py

**Files NOT in scope:**
- engine/ core rule changes
- agents/tactical/ policy changes
- llm/
- api/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] Headless tournament harness runs multiple games.
- [ ] Balance eval reports win rates across seeds.
- [ ] 100-game headless tournament completes without crashes.
- [ ] Both sides win > 20% of games.
- [ ] Leak test still passes across all tournament games.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-2-6-headless-tournament-harness.md`

## Merge Criteria
- 100-game headless tournament completes without crashes.
- Both sides win > 20% of games.
- Leak test still passes across all 100 games.
