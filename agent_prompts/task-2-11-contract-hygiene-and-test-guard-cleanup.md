# Agent Prompt — 2.11 Contract hygiene and test-guard cleanup

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-2.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 2.11 — Contract hygiene and test-guard cleanup, anchored to DESIGN.md §1.3, DESIGN.md §11.2, DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-2.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-2-contract-hygiene-cleanup`
**Depends on:** 2.10 merged, 2.10.5 merged, 2.8.5 merged, 2.9 merged
**Section refs:** DESIGN.md §1.3, DESIGN.md §11.2, DESIGN.md §11.3
**Complexity:** Medium

Close the four documentation, test-fixture, and task-contract findings in
`audits/audit-2026-05-15-0225-reconciled.md` that are pure hygiene: R-4
(the Task 2.8.5 old-id grep guard cannot be used as written because the
literal hits are planted scanner self-tests), R-7 (Task 2.8.5's
`Files in scope` list omits files the implementing PR touched), R-8 (Task
2.9 DoD wording at `tasks/phase-2.md:927` disagrees with the Phase 2
Merge Criterion at `:959`), and R-14 (`tests/observation/test_service.py`
helper ids still use role-bearing strings outside the value-scanner
harness). None of these touches runtime code. The four diffs do not
overlap.

**Files in scope:**
- eval/leak_test.py
- tests/eval/test_balance_eval.py
- tests/observation/test_service.py
- tasks/phase-2.md

**Files NOT in scope:**
- engine/
- observation/
- orchestrator/
- agents/
- llm/
- api/
- frontend/
- scripts/
- eval/balance_eval.py
- eval/determinism_test.py
- DESIGN.md
- AGENTS.md
- AGENT_IMPLEMENTATION.md
- audits/
- README.md
- open_issues.md
- tests/agents/
- tests/engine/
- tests/meetings/
- tests/orchestrator/
- tests/observation/test_boundary_contracts.py
- tests/_helpers/
- tests/fixtures/
- tests/test_firewall.py

**Definition of done:**
- [ ] **R-4 — old-id grep guard cleared:** Replace the planted role-bearing-id strings in `eval/leak_test.py:181`, `eval/leak_test.py:228`, and `tests/eval/test_balance_eval.py:258` with sentinels that still trip the value-scanner (i.e. contain one of `impostor` / `crewmate` / `crew`) but do not match the legacy regex `["'](player|impostor)-[0-9]+["']`. After the edit, `git grep -nE "['\"](player|impostor)-[0-9]+['\"]" eval/ tests/` must return empty. The negative-test semantics (scanner trips, allow-list permits `self_state.role`, nested-path message format) must remain unchanged — verify with `uv run pytest eval/leak_test.py tests/eval/test_balance_eval.py -v`. The Task 2.8.5 DoD bullet `Use \`git grep ... tests/\` ... the post-fix grep must be empty` is then satisfiable as written.
- [ ] **R-7 — Task 2.8.5 file-scope drift recorded retroactively:** Append a short prose note after the Task 2.8.5 Implementation hint and before the Integration risk block, stating that the merged PR (commit `e3b2a60`) also touched `eval/determinism_test.py`, `tests/engine/test_actions.py`, `tests/engine/test_events.py`, `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`, and `agent_prompts/task-2-9-headless-tournament-harness.md` as mechanical fallout of the `p-N` id rename. The note must state that these files are retroactively considered in scope for that historical PR and that the rename did not change behavior. Do not edit the Task 2.8.5 `Files in scope` list — the historical contract stays as merged; the note documents the actual diff.
- [ ] **[Optional] Task 2.10.5 file-scope drift recorded retroactively:** Same pattern as R-7, applied to Task 2.10.5. Append a short prose note after the Task 2.10.5 Implementation hint and before the Integration risk block, stating that the merged PR (commit `<PR #31 merge commit sha>`) also updated two cooldown-value literal assertions in `tests/engine/test_tick.py:110, 117` (`== 10` → `== 4`, `== 9` → `== 3`) as mechanical fallout of the `kill_cooldown_ticks` 10 → 4 retune. The Task 2.10.5 `Test cascades resolved` DoD bullet enumerated four cascade test files but missed `tests/engine/test_tick.py`; this note states the file is retroactively considered in scope for that historical PR and that the literal-value updates did not change behavior. Do not edit the Task 2.10.5 `Files in scope` or `Files NOT in scope` lists — the historical contract stays as merged. **Skip without penalty** if the existing `## Decisions` record in PR #31 is judged sufficient.
- [ ] **R-8 — Task 2.9 DoD wording aligned with merge criterion:** Replace the line at `tasks/phase-2.md:927` (`Both sides win > 20% of games.`) with the exact wording from `tasks/phase-2.md:959`: `Both decisive sides win > 20% of decisive games (CREWMATES and IMPOSTORS outcomes); \`TICK_BUDGET_REACHED\` games are reported separately and do not count toward decisive totals.` The `## Merge Criteria` block at the file's tail must not move; the criterion text there stays identical to the post-edit Task 2.9 bullet.
- [ ] **R-14 — observation test helper ids renamed:** Rewrite the role-bearing helper ids in `tests/observation/test_service.py:49-58` (`"victim"`, `"observer"`, `"crew-2"`, `"impostor"`) to the role-neutral `p-N` convention from `orchestrator/seeder.py`. Update every downstream reference in the same file, including `cooldowns`, action `actor`, action `target`, `agent_id` arguments, `_visible_player` lookups, and assertion strings. The scenarios under test (kill-witnessed adjacency, body-after-discovery filter, cooldown emission, witness rules) must keep their existing semantics; the rewrite is purely id substitution.
- [ ] After the Task 2.9 DoD edit, run `uv run python scripts/generate_prompts.py`. The diff to `agent_prompts/task-2-9-headless-tournament-harness.md` is expected as mechanical fallout from the contract edit and is the only out-of-scope file the PR is permitted to touch.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

For R-4, the smallest faithful change is to swap the role-bearing literals for sentinels that still contain one of the forbidden substrings (so the value-scanner still trips) but no longer match the legacy id regex. Example:

```python
# eval/leak_test.py:228 (test body) — before
{"id": "impostor-1", "room": "STORAGE", "action": None},
# after
{"id": "crew_role_leak_fixture", "room": "STORAGE", "action": None},
```

The scanner regex `_FORBIDDEN_VALUE_SUBSTRINGS = ("impostor", "crewmate", "crew")` still trips on `crew_role_leak_fixture` (substring `crew`). The grep pattern `['"]((player|impostor)-[0-9]+)['"]` no longer matches. Update the docstring at `eval/leak_test.py:181` analogously — replace the example strings inside the comment with the same sentinel form. The `match=` regex in the `pytest.raises` blocks is keyed on JSON path (`$.visible_players[0].id`), not on value text, so it does not need to change.

For R-7, model the historical note on the language already in Task 2.7.5's narrowing note (`tasks/phase-2.md:371-376`) — short, factual, marked with a date so future readers know it is a retroactive amendment:

```markdown
> Historical note (added 2026-05-15 by Task 2.11): the merged PR for this
> task (commit `e3b2a60`) also touched `eval/determinism_test.py`,
> `tests/engine/test_actions.py`, `tests/engine/test_events.py`,
> `tests/engine/test_world_state.py`, `tests/orchestrator/test_seeder.py`,
> and `agent_prompts/task-2-9-headless-tournament-harness.md` as
> mechanical fallout of the `p-N` id rename. Those files are retroactively
> considered in scope for that historical PR; the rename did not change
> behavior.
```

For R-8, the edit is a single-line replacement at `tasks/phase-2.md:927`. The Phase 2 Merge Criteria block at `:959` already has the correct wording; copy it verbatim. Do not edit the Merge Criteria block — the goal is to make the two locations agree, and the criterion is the authoritative phrasing.

For R-14, a clean substitution mapping keeps the rewrite mechanical and easy to review:

| Old | New |
| --- | --- |
| `"victim"` | `"p-1"` |
| `"observer"` | `"p-2"` |
| `"crew-2"` | `"p-3"` |
| `"impostor"` | `"p-4"` |

Apply globally inside `tests/observation/test_service.py` only. After the rewrite, `git grep -nE "['\"](player|impostor|victim|observer|crew-[0-9]+)['\"]" tests/observation/test_service.py` should be empty. The witness/visibility scenarios continue to read naturally because the rooms (`STORAGE`, `REACTOR`, `ADMIN`) and the `cooldowns` dictionary still encode the same setup.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.balance_eval"`
- `uv run python -c "import orchestrator.game"`
- `uv run python -c "import orchestrator.seeder"`
- `uv run python -c "import orchestrator.scheduler"`
- `uv run python -c "import agents.tactical.impostor_policy"`
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
- `uv run python -c "import agents.tactical.crewmate_policy"`

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
Open a PR from branch `phase-2-contract-hygiene-cleanup` with a title like `task 2.11: contract hygiene and test-guard cleanup`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §1.3, DESIGN.md §11.2, DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
