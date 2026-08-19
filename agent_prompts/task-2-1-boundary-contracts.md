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

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-2-boundary-contracts` with a title like `task 2.1: boundary contracts`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
