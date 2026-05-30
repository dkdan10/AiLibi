# Agent Prompt — 6.3 Close the win-condition impostor-elimination gap

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-6.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 6.3 — Close the win-condition impostor-elimination gap, anchored to Audit J-J-8, I-I-3; DESIGN.md §3, §8.1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-6.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-6-win-condition-impostor-elimination`
**Depends on:** 6.2 merged
**Section refs:** Audit J-J-8, I-I-3; DESIGN.md §3, §8.1
**Complexity:** Integration

`evaluate_win_conditions` has no `alive_impostors == 0 → CREWMATES win` case
(`engine/win_conditions.py:17`). After the last impostor is ejected the game runs
on until tasks complete or the tick budget expires — a zombie game with no
possible loser, distorting the eval/balance numbers (games the crew effectively
won record as `TICK_BUDGET_REACHED` or `CREWMATE_TASKS`). Confirmed in
replay-seed-49 (audit J-J-8; memory `project_win_condition_impostor_elimination_
gap`). This is the deferred gap; closing it is a prerequisite for trustworthy
balance numbers before any Phase 7 agent-intelligence tuning.

Add a fourth condition evaluated BEFORE the task-completion check: if there are
zero alive impostors, the crew wins by ejection. Add the corresponding
`WinResultType` literal (the current type is at `engine/win_conditions.py:8`).
This changes the decisive outcome of any game where the last impostor is ejected
before tasks finish, so it alters replay determinism and the committed sample
fixtures — the fixtures must be regenerated and the change needs design-thread
sign-off (recorded here; the design thread approved closing the gap on
2026-05-30). Flip the Task 6.2 characterization test from asserting `None` to
asserting the crew elimination win.

Ordering check before fixture regeneration: this is the FIRST of the two
fixture-regenerating engine tasks (6.3 then 6.4). Regenerate fixtures exactly
once here, in this task, so the close-gate can attribute the resulting metric
delta to this single change. Do not also start Task 6.4's wiring in this branch.

**Files in scope:**
- engine/win_conditions.py
- tests/engine/test_win_conditions.py
- replays/samples/MANIFEST.md
- replays/samples/

**Files NOT in scope:**
- engine/ (other than win_conditions.py)
- meetings/
- agents/
- api/
- frontend/
- eval/
- DESIGN.md (reconciled in the design thread)

**Definition of done:**
- [ ] `engine/win_conditions.py` adds a condition: with zero alive impostors, return `WinResult(CREWMATES, reason="CREWMATE_EJECT")` (or the project's winner-enum equivalent), evaluated BEFORE the existing task-completion check and after the existing parity check ordering is preserved for all other cases.
- [ ] The `WinResultType` literal at line 8 gains the new `CREWMATE_EJECT` reason; the TypeScript mirror and any schema that enumerates win reasons are updated so `generate_prompts.py --check` and the schema-mirror tests stay green.
- [ ] The Task 6.2 characterization test in `tests/engine/test_win_conditions.py` is flipped from asserting `None` to asserting the crew elimination win for zero-impostor + incomplete-tasks; the co-located comment is updated to note the gap is now closed.
- [ ] All other win-condition orderings (impostor parity, sabotage, crew tasks) are unchanged and still tested.
- [ ] The committed `replays/samples/` fixtures are regenerated with the project's refresh-samples workflow and `replays/samples/MANIFEST.md` is updated; the determinism / byte-identical replay tests pass against the regenerated set.
- [ ] The PR `## Decisions` block records: design-thread sign-off to close the gap (2026-05-30); the new reason literal name; and that fixtures were regenerated exactly once in this task.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Read `engine/win_conditions.py` end-to-end (the `WinResultType` literal at
line 8, `WinResult` at line 14, `evaluate_win_conditions` and its ordering at
lines 17–22) and the win-reason mirror on the TypeScript side plus any schema
enum that lists reasons. The new case is a few lines, but ORDER matters: place
the zero-impostor crew win before the task-completion check so an
already-all-tasks-done-and-no-impostors game attributes to the ejection win per
design intent — confirm the intended precedence in the design thread note if
ambiguous. Use the existing refresh-samples workflow (do not hand-edit JSONL) to
regenerate fixtures, and re-run the determinism tests to confirm byte-identical
reconstruction of the new set. This is the first fixture-regenerating task;
Task 6.4 depends on it precisely so the two regenerations stay serial.

## Public types this task introduces
- `engine.win_conditions.WinResultType`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is a determinism-altering engine change with committed-fixture blast radius.

- **Fixture regeneration is the risk surface.** Regenerate exactly once, via the
  refresh-samples workflow, and verify the determinism + leak tests pass on the
  new set before committing. A hand-edited or partially-regenerated
  `replays/samples/` set will fail the byte-identical replay gate.
- **Serial with Task 6.4.** Both tasks rewrite `replays/samples/`. 6.4 depends on
  6.3 so the regenerations never interleave; do not begin 6.4's wiring here.
- **Mirror the new reason everywhere.** The win reason crosses the
  Python↔TypeScript schema mirror; a missed mirror edit fails the schema-sync
  gate. Grep for every enumeration of win reasons before finishing.
- **Eval numbers shift intentionally.** The balance aggregates (impostor win
  rate) will move because zombie games now resolve as crew ejection wins. That is
  the point; note the expected direction in the PR so the shift is not mistaken
  for a regression.

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
Open a PR from branch `phase-6-win-condition-impostor-elimination` with a title like `task 6.3: close the win-condition impostor-elimination gap`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing Audit J-J-8, I-I-3; DESIGN.md §3, §8.1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
