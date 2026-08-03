# Agent Prompt — 8.3 Task-id propagation: observation + agents + memory

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.3 — Task-id propagation: observation + agents + memory, anchored to DESIGN.md §3.2 (agent-facing map id), §1.3 (observation firewall); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.2, §4 coupling 5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-task-id-propagation`
**Depends on:** 8.1
**Section refs:** DESIGN.md §3.2 (agent-facing map id), §1.3 (observation firewall); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.2, §4 coupling 5
**Complexity:** Integration

Thread the per-player task model through the observation / agent / memory layer so the render-field-reader **triad** agrees that the agent-facing id is the MAP id resolving to the acting agent's own instance (DESIGN.md §3.2). The list the impact map names must move in lockstep: `observation/packet.py::SelfView.pending_task_id` (the field — stays a map id, own-task only), `agents/perception.py::_self_state_payload` (the render into prompt JSON), and `agents/memory/store.py` (the reader). Plus `observation/service.py::_pending_task_id_for_agent` (stays owner-scoped — the leak guarantee) and `_global_view` (the `tasks_total` / `task_completion_percent` denominator over live instances), `observation/public_map.py::task_locations` (map-keyed, unchanged), the DoTask payload (`observation/action_intent.py` + `engine/actions.py`), and the `do_task` round-trip in `agents/tactical/{crewmate,impostor}_policy.py`. A drift here silently targets the wrong owner's instance.

**Files in scope:**
- observation/service.py (`_pending_task_id_for_agent` owner-scoped under the new keyspace; `_global_view` denominator + `task_completion_percent`)
- observation/packet.py (`SelfView.pending_task_id` stays the map id, own-task only; `GlobalView.tasks_total` count over instances)
- observation/public_map.py (`PublicMapView.task_locations` keyed by map id — confirm unchanged)
- observation/action_intent.py + engine/actions.py (`DoTask` payload `task_id` stays the map id; engine resolution agrees)
- agents/perception.py (`_self_state_payload` render of `pending_task_id`; `_global_state_payload` task counts)
- agents/memory/store.py (the pending-task completion-inference reader works on the map id)
- agents/tactical/crewmate_policy.py + agents/tactical/impostor_policy.py (the `task_locations.get(pending_task_id)` → `do_task(task_id=...)` round-trip)
- tests/agents/ + tests/observation/test_service.py + tests/fixtures/memory_rendering/* (the triad agrees; a crewmate never sees another's ownership; do_task targets the right owner; memory-render goldens regenerate)

**Files NOT in scope:**
- engine/tick.py, engine/world.py (the keyspace + resolution are 8.1)
- api/, frontend/ (the spectator task-count mirrors are 8.4)
- meetings/ (Track B)

**Definition of done:**
- [ ] `SelfView.pending_task_id` is the agent's own map task id (never another player's task or any ownership); `_pending_task_id_for_agent` is owner-scoped by construction.
- [ ] The render-field-reader triad (`SelfView.pending_task_id` ↔ `agents/perception.py::_self_state_payload` ↔ `agents/memory/store.py`) and the `DoTask` round-trip in both tactical policies all agree the map id resolves to the ACTOR's own instance; a do_task targeting test proves the right owner advances.
- [ ] `_global_view.task_completion_percent` / `GlobalView.tasks_total` count over live instances; the value equals the engine's instance total.
- [ ] The memory-rendering golden fixtures regenerate (`tasks_total`, the "You completed {task}" line); `tests/observation/test_service.py` covers a multi-impostor packet whose crewmate-recipients carry no foreign task ownership.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The agent-facing id is the MAP id (8.1's decision), so most of this layer is a re-confirm, not a rewrite: `task_locations` stays keyed by map id, the DoTask payload stays a map id, and the engine (8.1) resolves `(actor, map_task_id)`. The real edits are (a) `_pending_task_id_for_agent` returning the agent's own map task under the new keyspace, and (b) the `tasks_total` denominators counting instances. Keep `agents/` free of engine imports (lint-imports). Regenerate the memory-render goldens rather than hand-editing them.

## Integration risk

The leak firewall is load-bearing: a crewmate's packet must never carry another player's task ownership. The render/field/reader legs must move together — a drift makes `do_task` silently advance the wrong owner's instance (a determinism + correctness bug invisible to the type checker). Land the do_task round-trip test + the leak coverage together.

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-8-task-id-propagation` with a title like `task 8.3: task-id propagation: observation + agents + memory`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.2 (agent-facing map id), §1.3 (observation firewall); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.2, §4 coupling 5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
