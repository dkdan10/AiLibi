# Agent Prompt — 8.5 9p/2i roster knobs + CLI/script threading

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.5 — 9p/2i roster knobs + CLI/script threading, anchored to DESIGN.md §3.5 (9p/2i canonical roster), §8.1; audits/restructure-impact-map-2026-06-04-0223.md §2c, §5 decision 11. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-9p2i-roster`
**Depends on:** 8.2
**Section refs:** DESIGN.md §3.5 (9p/2i canonical roster), §8.1; audits/restructure-impact-map-2026-06-04-0223.md §2c, §5 decision 11
**Complexity:** Medium

Make 9p/2i a first-class roster (decision 11: rename `7p2i`→`9p2i`, presets `{4p1i, 9p2i}`). Add/rename `orchestrator/game.py::ROSTER_PRESETS['9p2i'] = RosterPreset(9, 2, 2)` and remove `7p2i`; thread it through `scripts/run_tournament.py` (`--roster-preset` choices auto-surface from `sorted(ROSTER_PRESETS)`), `scripts/run_game.py` (which is missing a `--tasks-per-crewmate` flag — add it and pass to `HeadlessGame`), and the `scripts/refresh_samples.sh` env block. `DEFAULT_NUM_PLAYERS`/`DEFAULT_NUM_IMPOSTORS`/`DEFAULT_TASKS_PER_CREWMATE` stay 4/1/2 (the flat baseline is the harness default, not the eval roster). Needs 8.2's cap removal so a 9p/2i roster can seed.

**Files in scope:**
- orchestrator/game.py (`ROSTER_PRESETS` — add `9p2i=RosterPreset(9,2,2)`, remove `7p2i`; defaults unchanged)
- scripts/run_tournament.py (`--roster-preset` choices from `sorted(ROSTER_PRESETS)`)
- scripts/run_game.py (add the missing `--tasks-per-crewmate` flag; pass to `HeadlessGame`)
- scripts/refresh_samples.sh (the documented env block updates to the 9p/2i values)
- tests/orchestrator/test_game.py + tests/scripts/test_run_tournament.py + tests/scripts/test_refresh_samples.py + tests/scripts/test_manifest_writer.py + tests/engine/test_rules.py (the roster-preset set-equality + `RosterPreset` tuples + 7→9 literals)

**Files NOT in scope:**
- orchestrator/seeder.py (cap removal is 8.2)
- replays/samples/ + roster.json + dir rename (the re-record + `7p2i/`→`9p2i/` rename is 8.12)

**Definition of done:**
- [ ] `ROSTER_PRESETS` is `{4p1i, 9p2i}` with `9p2i=RosterPreset(num_players=9, num_impostors=2, tasks_per_crewmate=2)`; `7p2i` is removed; `DEFAULT_*` stay 4/1/2.
- [ ] `run_tournament.py --roster-preset 9p2i` and `run_game.py --num-players 9 --num-impostors 2 --tasks-per-crewmate 2` both seed and run a game; `refresh_samples.sh`'s env block documents the 9p/2i routing.
- [ ] `refresh_samples.sh --dry-run` (9p/2i routing) echoes `roster: num_players=9 num_impostors=2 tasks_per_crewmate=2` — the resolved-roster preview reflects the new preset, not just the doc'd env block.
- [ ] `tests/orchestrator/test_game.py` roster-preset set-equality + tuple assertions, and the script/rules tests pinning 7p/2i, are updated to 9p/2i.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

`run_game.py` exposes `--num-players`/`--num-impostors` but not `--tasks-per-crewmate` — add it (default `DEFAULT_TASKS_PER_CREWMATE`) so a single 9p/2i game runs at the eval count. The `7p2i`→`9p2i` directory rename + `roster.json` rewrite is NOT here; this task only changes the in-code preset + CLI knobs (the committed-data move is 8.12). Grep for `7p2i` / `RosterPreset(7` across tests to find every pin.

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
Open a PR from branch `phase-8-9p2i-roster` with a title like `task 8.5: 9p/2i roster knobs + cli/script threading`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5 (9p/2i canonical roster), §8.1; audits/restructure-impact-map-2026-06-04-0223.md §2c, §5 decision 11), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
