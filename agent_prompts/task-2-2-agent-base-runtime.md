# Agent Prompt — 2.2 Agent base + runtime

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.2 — Agent base + runtime, anchored to DESIGN.md §4.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

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

## Public types this task introduces
- `agents.base.AgentInterface`
- `agents.runtime.AgentRuntime`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import observation.action_intent"`
- `uv run python -c "import observation.public_map"`
- `uv run python -c "import orchestrator.boundary"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

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
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-2-agent-base-runtime` with a title like `task 2.2: agent base + runtime`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §4.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
