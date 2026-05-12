# Agent Prompt — 2.3 Memory scaffolding (no LLM)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.3 — Memory scaffolding (no LLM), anchored to DESIGN.md §6.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

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

## Public types this task introduces
- `agents.memory.episodic.EpisodicEvent`
- `agents.memory.episodic.MemoryStore`
- `agents.memory.working.WorkingMemory`
- `agents.memory.beliefs.BeliefState`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-2-memory-scaffolding` with a title like `task 2.3: memory scaffolding (no llm)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §6.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
