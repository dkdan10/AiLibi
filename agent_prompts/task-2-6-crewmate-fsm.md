# Agent Prompt — 2.6 Crewmate FSM

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.6 — Crewmate FSM, anchored to DESIGN.md §4.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

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

## Public types this task introduces
- `agents.tactical.crewmate_policy.CrewmatePolicy`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-2-crewmate-fsm` with a title like `task 2.6: crewmate fsm`.
The PR description must reference DESIGN.md §4.4, list the definition-of-done checklist, and include `Decisions` and (if blocking) `Questions` sections.
