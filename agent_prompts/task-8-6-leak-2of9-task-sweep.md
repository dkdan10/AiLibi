# Agent Prompt — 8.6 Leak firewall at 2-of-9 + per-player-task sweep fixture

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.6 — Leak firewall at 2-of-9 + per-player-task sweep fixture, anchored to DESIGN.md §1.3, §11.2 (the leak test); audits/restructure-impact-map-2026-06-04-0223.md §2e, §3.2, §5 decision 13. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-leak-2of9-task-sweep`
**Depends on:** 8.1, 8.3, 8.5
**Section refs:** DESIGN.md §1.3, §11.2 (the leak test); audits/restructure-impact-map-2026-06-04-0223.md §2e, §3.2, §5 decision 13
**Complexity:** Medium

Extend the project's strongest leak guard to the new substrate (decision 13). The DESIGN §11.2 property sweep (`tests/observation/test_leak_property.py`) hard-codes a 7-player roster (`range(1,8)`) and builds `tasks={}` — so it never exercises `SelfView.pending_task_id` under the per-player keyspace. Widen it to **9 players**, keep **multi-impostor** coverage (2 and 3 impostors), and add a fixture **with per-player tasks** so the own-task-only invariant is actually swept. Re-confirm the `eval/leak_test.py` crew-empty `fellow_impostor_ids` invariant holds at 2-of-9. (The `tests/api/test_leak.py` `EXPECTED_*` snapshot tripwires move with the schema in 8.10, not here.)

**Files in scope:**
- tests/observation/test_leak_property.py (`_ROSTER_PLAYER_IDS` `range(1,8)`→9; `_VALID_IMPOSTOR_COUNTS` keeps ≥2; a per-player-task fixture so `pending_task_id` is exercised under the new keyspace; the crew-empty `fellow_impostor_ids` assertion per packet)
- eval/leak_test.py (re-confirm the `_assert_no_role_bearing_values` + crew-empty invariant over the scripted games; no behavior change)

**Files NOT in scope:**
- tests/api/test_leak.py (its `EXPECTED_DTOS` / `EXPECTED_EVAL_REPORT_FIELDS` snapshots update with the schema in 8.10)
- observation/, agents/ (the leak-safe wiring is 8.1 / 8.3 — this task tests it)

**Definition of done:**
- [ ] The property sweep runs at 9 players and at 2 (and 3) impostors, asserting `self_state.fellow_impostor_ids == ()` for every crewmate-recipient packet and no role-bearing value in any agent-visible field.
- [ ] A per-player-task fixture makes the sweep exercise `SelfView.pending_task_id` under the new keyspace (no longer `tasks={}`), proving a crewmate sees only its own task and no ownership of others.
- [ ] `eval/leak_test.py`'s crew-empty `fellow_impostor_ids` + no-role-leak invariants pass unchanged at 2-of-9.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The sweep's `_roster_initial_state` builds `tasks={}` — add per-player task instances (via the 8.2 seeder or a hand-built fixture) so `pending_task_id` is non-empty and the own-task-only path is actually swept. Widen `_ROSTER_PLAYER_IDS` and keep `_VALID_IMPOSTOR_COUNTS` covering 2 and 3. This task TESTS the firewall; it does not change `observation/` (that is 8.1/8.3).

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
Open a PR from branch `phase-8-leak-2of9-task-sweep` with a title like `task 8.6: leak firewall at 2-of-9 + per-player-task sweep fixture`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, §11.2 (the leak test); audits/restructure-impact-map-2026-06-04-0223.md §2e, §3.2, §5 decision 13), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
