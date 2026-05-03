# Agent Prompt — 2.1 Boundary contracts

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section in tasks/phase-2.md.

1. Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth, AGENT_IMPLEMENTATION.md is the provider-neutral build plan, and the task contract below is the implementation contract for this PR.

2. Exact section reference
Implement Task 2.1 — Boundary contracts, anchored to DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1. Do not implement work outside these references.

3. Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-boundary-contracts`
**Depends on:** Phase 1 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1

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
- [ ] `PublicMapView` exposes only public map topology needed by agents: map id, room ids, room neighbors, vent graph, task locations, spawn room, meeting room, and emergency button room.
- [ ] Orchestrator boundary helpers translate `PublicMapView` from an engine map and translate valid `ActionIntent` values into engine `Action` values.
- [ ] Orchestrator boundary helpers reject duplicate actor submissions before actions enter `advance_tick`.
- [ ] Invalid intents raise during translation; there are no silent fallbacks.
- [ ] `agents/` has no imports from `engine/`, directly or transitively.
- [ ] Relevant boundary and firewall tests pass.
- [ ] `uv run mypy --strict engine observation agents orchestrator` passes.
- [ ] `uv run ruff check .` passes.

4. Pre-flight checklist
- Read AGENTS.md, DESIGN.md, AGENT_IMPLEMENTATION.md, and the task section before editing.
- Inspect the current implementation before editing.
- Confirm the dependency listed in the task contract is present in the current branch.
- Identify the existing local patterns for the files in scope and follow them.

5. Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.
If something is ambiguous, stop and add a Questions section in the PR description rather than guessing.

6. Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

7. Output expectation
Open a PR from branch `phase-2-boundary-contracts` with a title like `task 2.1: boundary contracts`.
The PR description must reference DESIGN.md §1.3, DESIGN.md §3.1, DESIGN.md §4.1, list the definition-of-done checklist, and include a Questions section if anything is ambiguous.
