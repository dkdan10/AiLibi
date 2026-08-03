# Agent Prompt — 8.17 Kill-gifted win accounting in the eval report

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-8.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 8.17 — Kill-gifted win accounting in the eval report, anchored to DESIGN.md §3.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-8.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-8-kill-gifted-accounting`
**Depends on:** none (audit-repair root)
**Section refs:** DESIGN.md §3.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-4
**Complexity:** Medium

Audit gp-4, accounting half (the §3.5 drop rule itself is KEPT by owner decision): the dead-owner
instance drop means each kill advances the task clock too — 222/700 instances dropped, 12/37 crew
"task wins" proximately enabled by the impostor's own kill, all invisible in the report. Make the
artifact measurable so balance reads use the kill-gifted split, never the raw crew win rate alone.

**Files in scope:**
- eval/balance_eval.py (the `GameReport` assembly derives `kill_gifted` for CREWMATE_TASKS games — the final tick resolves a kill and completes no task instance — plus per-game `instances_dropped` and `instances_complete_at_win`)
- eval/report_schema.py (`GameReport`/`TournamentReport` additive fields with defaults; aggregates: kill-gifted win count, total instances dropped, mean complete-at-win; `CURRENT_FORMAT_VERSION` stays 2)
- tests/eval/test_report_schema.py + tests/eval/test_tournament_report.py (synthetic gifted and non-gifted fixtures assert flag + counts; a pre-fields v2 report still loads via defaults)
- tests/api/test_leak.py (`EXPECTED_EVAL_REPORT_FIELDS` updated in lockstep)

**Files NOT in scope:**
- engine/ (the §3.5 drop semantics are unchanged — owner decision)
- agents/tactical/impostor_policy.py (kill suppression is deferred to the post-Wave-1 impostor wave)
- replays/samples/** + the committed tournament-eval-report.json (regenerated in 8.18)

**Definition of done:**
- [ ] `GameReport` carries `kill_gifted` / `instances_dropped` / `instances_complete_at_win` (additive, defaulted); `TournamentReport` aggregates them; the format version stays 2; a committed pre-fields report still validates.
- [ ] The flag is deterministic from the replay: winner CREWMATE_TASKS AND the final tick resolves a kill AND no task instance completes on that tick. A final tick where a kill and a task completion both resolve is NOT kill-gifted — the task completion is treated as decisive (the alternative attribution is a Wave-1 priced question, not this task's).
- [ ] `EXPECTED_EVAL_REPORT_FIELDS` matches; the synthetic fixtures cover both endings.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The final-tick kill/completion facts need RESOLVED events — a recorded kill action can be
engine-rejected — so derive them with an engine walk (the win-condition-selfcheck pattern, or
api.replay_loader) rather than trusting raw action rows. instances_dropped = seeded instance count
minus `len(state.tasks)` at game end; instances_complete_at_win = completed count at end vs the
seeded total. Keep everything derived from the walk, deterministic. The schema is extra="forbid":
new fields must default so old reports load until 8.18 regenerates them.

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
Open a PR from branch `phase-8-kill-gifted-accounting` with a title like `task 8.17: kill-gifted win accounting in the eval report`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §3.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
