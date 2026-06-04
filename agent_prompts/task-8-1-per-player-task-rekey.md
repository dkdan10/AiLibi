# Agent Prompt — 8.1 Per-player task re-key (engine core)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.1 — Per-player task re-key (engine core), anchored to DESIGN.md §3.2 (state model — per-player tasks), §3.3 (Task entity), §3.5 (win count over instances); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.1, §5 decisions 1–5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-per-player-task-rekey`
**Depends on:** none (the R-0 DESIGN.md rewrite is merged; this is the substrate root)
**Section refs:** DESIGN.md §3.2 (state model — per-player tasks), §3.3 (Task entity), §3.5 (win count over instances); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.1, §5 decisions 1–5
**Complexity:** Integration

Re-key `WorldState.tasks` from a single `Mapping[TaskId, TaskState]` (the engine asserts `TaskState.id == <dict key>`) to per-player instances keyed by the stable string `"{owner}:{map_task_id}"`, so multiple crewmates hold the same map task with independent progress (DESIGN.md §3.2). `TaskState` keeps `owner` and gains `map_task_id` (its anchor room is `game_map.tasks[map_task_id]`), with the instance `id` equal to the composite key. The agent-facing id stays the MAP id: the engine resolves `(action.actor, map_task_id)` to the actor's own instance, so no observation / policy / prompt change is needed here (that propagation is 8.3) and the scripted `do_task` payloads keep their map ids. This is the root reset vector — it changes `_serialize_world_state` and therefore every game's per-tick `state_hash`.

This task is engine-only: it lands with the engine unit suites green plus a new same-map-task two-owners progress-isolation case, but it does NOT touch the seeder (8.2), the observation / agent layer (8.3), or re-record committed data (8.12). Because the `state_hash` changes, the committed-set reconstruction tests can no longer reconstruct the old bytes; they are skipped here with a reason pointing at the 8.12 re-record (mirroring Task 7.9). `eval/determinism_test.py` re-records two fresh games and stays green.

**Files in scope:**
- engine/world.py (`WorldState.tasks` re-keyed to per-instance `"{owner}:{map_task_id}"`; the disjoint-namespace check re-confirmed)
- engine/entities.py (`TaskState` gains `map_task_id`; instance `id` equals the composite key; `owner` retained)
- engine/tick.py (`_advance_tasks` and `_apply_do_task` resolve the ACTOR's own instance via `(actor, map_task_id)`; `_apply_kill` owner-filter; `_task_progress_event` carries the MAP id)
- engine/events.py (`event_to_dict` Task* branch carries the map id; `actor` disambiguates owners)
- engine/win_conditions.py (`evaluate_win_conditions` task-complete count over live instances; rule unchanged, magnitude scales)
- tests/engine/test_tick.py + tests/engine/test_world_state.py + tests/engine/test_win_conditions.py (per-instance keying; a same-map-task two-owners progress-isolation case; dead-owner instance drop; win count)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (SKIP the committed-set reconstruction cases with a reason referencing the 8.12 re-record — the state_hash change invalidates the old bytes)

**Files NOT in scope:**
- orchestrator/seeder.py (the cap removal + instance minting is 8.2)
- observation/, agents/, meetings/ (the agent-facing id is the map id — the propagation triad is 8.3; meetings are Track B)
- replays/samples/ (no re-record here; that is the combined 8.12 gate, which re-enables the skipped recon tests)
- engine/maps/canonical_1.yaml (the 12-task map is unchanged; per-player overlap carries 9p/2i — DESIGN.md §3.5)

**Definition of done:**
- [ ] `WorldState.tasks` is keyed by the per-player instance string `"{owner}:{map_task_id}"`; `TaskState` carries `owner` + `map_task_id` + an instance `id` equal to the key; two crewmates can hold the same map task with independent progress.
- [ ] `do_task` resolves `(action.actor, payload.task_id)` → the actor's own instance: a two-owners progress-isolation test proves one owner's progress never advances the other's, and a foreign/out-of-pool map id fails loud.
- [ ] `_apply_kill` drops only the victim's incomplete instances; `engine/win_conditions.py` counts completion over live instances; the dead-crewmate rule (DESIGN.md §3.5) holds per-instance-owner.
- [ ] `TaskProgressed` / `TaskCompletedEvent` carry the MAP id (owner via `actor`), so `game_map.tasks[event.task_id]` room lookups are unchanged.
- [ ] The committed-set reconstruction tests (`test_replay_loader.py` committed 4p/1i + 7p/2i; `test_win_condition_selfcheck.py` committed cases) are skipped with an explicit reason referencing the 8.12 re-record; `eval/determinism_test.py` (fresh recordings) stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The composite key keeps `WorldState.tasks` a flat str-keyed dict (`orchestrator/replay.py::_to_jsonable` requires str keys), so serialization stays shape-compatible — only the bytes change. Read `engine/tick.py::_advance_tasks` (`tasks.get(task_id)` + the `task.id != task_id` assert) and `_apply_do_task` (`state.tasks.get(payload.task_id)` + `tasks[task.id]=replace(...)`): both must resolve `f"{actor}:{map_task_id}"`, not the bare map id. The win count in `engine/win_conditions.py` iterates the dict — unchanged logic, larger denominator. Keep the engine pure (no RNG) so replay stays deterministic. The committed-recon skips are time-bound — 8.12 re-records and re-enables them; do not leave them skipped beyond the phase.

## Integration risk

This is the root state-hash reset vector for the whole phase; every other task and the combined re-record build on its keyspace. The map-id-agent-facing decision is what keeps the blast radius engine-local — preserve it (do NOT leak the instance id into actions or observations). The committed-recon test skips are intentional and time-bound (8.12 un-skips them); `eval/determinism_test.py` must stay green throughout as the running guard.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "from engine.world import WorldState; from engine.entities import TaskState"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
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
Open a PR from branch `phase-8-per-player-task-rekey` with a title like `task 8.1: per-player task re-key (engine core)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.2 (state model — per-player tasks), §3.3 (Task entity), §3.5 (win count over instances); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.1, §5 decisions 1–5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
