# Agent Prompt — 2.1 Boundary contracts

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.1 — Boundary contracts, anchored to DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

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

## Implementation hint

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

## Public types this task introduces
- `observation.action_intent.ActionIntent`
- `observation.public_map.PublicMapView`
- `orchestrator.boundary.public_map_from_engine_map`
- `orchestrator.boundary.translate_action_intent`
- `orchestrator.boundary.translate_action_intents_for_tick`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-2-boundary-contracts` with a title like `task 2.1: boundary contracts`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
