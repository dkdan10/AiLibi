# Agent Prompt — 8.2 Seeder cap removal + deterministic instance minting

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.2 — Seeder cap removal + deterministic instance minting, anchored to DESIGN.md §3.2 (per-player tasks), §3.5 (no seed cap); audits/restructure-impact-map-2026-06-04-0223.md §2a (seeder), §4 coupling 1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-seeder-instance-minting`
**Depends on:** 8.1
**Section refs:** DESIGN.md §3.2 (per-player tasks), §3.5 (no seed cap); audits/restructure-impact-map-2026-06-04-0223.md §2a (seeder), §4 coupling 1
**Complexity:** Medium

Remove the fail-loud cap in `orchestrator/seeder.py::_build_tasks` (`required = num_crewmates × tasks_per_crewmate > len(game_map.tasks)`) and mint per-player task instances deterministically so multiple crewmates hold the same map task with independent progress (the keyspace landed by 8.1). The seeder's current "each crewmate owns `tasks_per_crewmate` DISTINCT map ids via a flat cursor" contract is replaced by "each crewmate owns `tasks_per_crewmate` instances, drawn with overlap allowed, minted from a seed-shuffled deal so the assignment stays a pure function of the seed." `scripts/_manifest_writer.py::_validate_roster_is_seedable` mirrors the same cap and must drop it in lockstep, or it rejects a 9p/2i sidecar (`7×2=14 > 12`). This unblocks 9p/2i seeding (8.5).

**Files in scope:**
- orchestrator/seeder.py (`_build_tasks` / `_assign_tasks` / `seed_initial_state` — remove the cap, mint instance ids deterministically; the byte-identity-prefix docstring contract is rewritten)
- scripts/_manifest_writer.py (`_validate_roster_is_seedable` — drop/relax the mirrored 12-cap so a 9p/2i descriptor validates)
- tests/orchestrator/test_seeder.py (invert the task-pool-exhausted test; replace the distinct-global-id + flat-cursor + golden `(owner,task_id)` contracts with a per-player-instance + new-golden contract; a same-map-task two-owners case)

**Files NOT in scope:**
- engine/ (the keyspace + resolution are 8.1)
- orchestrator/game.py (the 9p/2i roster preset is 8.5)
- replays/samples/ (no re-record; that is 8.12)

**Definition of done:**
- [ ] `_build_tasks` no longer caps `num_crewmates × tasks_per_crewmate` against `len(game_map.tasks)`; it mints per-player instances deterministically (a pure function of the seed; no new RNG draw beyond the existing seeded shuffle), allowing overlap so two crewmates can hold the same map task.
- [ ] A 9p/2i roster at `tasks_per_crewmate=2` seeds successfully (14 instances over the 12 map tasks); the flat 4p/1i at 1 task seeds the same instances as before (only their key shape changes).
- [ ] `scripts/_manifest_writer.py::_validate_roster_is_seedable` accepts a 9p/2i descriptor (the mirrored cap is gone).
- [ ] `tests/orchestrator/test_seeder.py` is rewritten: the exhausted-pool test is inverted/removed, and the distinct-id / flat-cursor / golden-tuple contracts are replaced with per-player-instance contracts incl. a two-owners-same-map-task case.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Keep the deal a pure function of the seed: shuffle once, then for each crewmate take `tasks_per_crewmate` map ids *with replacement allowed across crewmates* (e.g. `map_task_ids[i % len(map_task_ids)]` over a global cursor, or a per-crewmate independent slice) and mint `TaskState(id=f"{owner}:{map_task_id}", owner=..., map_task_id=...)`. The 4p/1i flat path must mint the same instances it dealt before (so only the key shape, not the assignment, changes for that roster) — pin it with a golden test. Grep `_manifest_writer.py` for the seedable check so the two cap sites drop together. Confirm `engine/maps/canonical_1.yaml` stays at 12 tasks (no map growth — DESIGN.md §3.5); the cap removal, not a bigger pool, is what carries 9p/2i.

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
Open a PR from branch `phase-8-seeder-instance-minting` with a title like `task 8.2: seeder cap removal + deterministic instance minting`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.2 (per-player tasks), §3.5 (no seed cap); audits/restructure-impact-map-2026-06-04-0223.md §2a (seeder), §4 coupling 1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
