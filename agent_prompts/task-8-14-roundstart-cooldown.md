# Agent Prompt — 8.14 Round-start kill cooldown

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.14 — Round-start kill cooldown, anchored to DESIGN.md §3.4; audits/audit-2026-06-06-0632-gameplay-data.md gp-1. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-roundstart-cooldown`
**Depends on:** none (audit-repair root)
**Section refs:** DESIGN.md §3.4; audits/audit-2026-06-06-0632-gameplay-data.md gp-1
**Complexity:** Small

Audit gp-1 (urgent): impostor kill cooldowns are seeded to 0, granting a free unwitnessed kill at
tick 1 in 26/50 committed games (impostor win 42.3% with it vs 8.3% without). Seed every impostor's
cooldown to `game_map.kill_cooldown_ticks` (4 on the canonical map) so the first kill obeys the same
cadence as every later one. The engine is already correct (`engine/tick.py` resets to the map value
after each kill and decrements per tick) — only the seeder's initial value changes.

**Files in scope:**
- orchestrator/seeder.py (`seed_initial_state` cooldown init `{pid: 0 ...}` → `{pid: game_map.kill_cooldown_ticks ...}`; the "initialised to 0" docstring)
- tests/orchestrator/test_seeder.py (round-start cooldown assertion; a kill queued at tick 1 from the seeded state is engine-rejected with the cooldown reason)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (skip-mark the committed-set reconstruction cases pending 8.18 — reuse the Task 8.1 marker pattern verbatim)

**Files NOT in scope:**
- engine/ (tick/rules already handle reset + decrement; no engine change)
- replays/samples/** + the committed tournament-eval-report.json (the wave re-record is 8.18)
- meetings/, agents/, observation/

**Definition of done:**
- [ ] `seed_initial_state` seeds every impostor cooldown to `game_map.kill_cooldown_ticks`; the docstring matches; a regression test asserts the round-start value and the tick-1 kill rejection, pinning the engine's literal rejection reason `"kill is on cooldown"` (engine/rules.py) exactly — audits' mechanical passes grep this string; do not match loosely.
- [ ] The committed-set reconstruction tests are skip-marked pending 8.18 (the 8.1 pattern), and `eval/determinism_test.py` (fresh-vs-fresh, no committed bytes) stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-8-roundstart-cooldown` with a title like `task 8.14: round-start kill cooldown`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.4; audits/audit-2026-06-06-0632-gameplay-data.md gp-1), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
