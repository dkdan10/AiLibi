# Agent Prompt — 9.10 Failed-call telemetry de-dup

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-9.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 9.10 — Failed-call telemetry de-dup, anchored to DESIGN.md §11.4; audits/audit-2026-06-09-0347-gameplay-data.md gp-4 (MECH-B-1). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-9.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-9-failed-call-dedup`
**Depends on:** 9.9 (shares meetings/manager.py + orchestrator/game.py)
**Section refs:** DESIGN.md §11.4; audits/audit-2026-06-09-0347-gameplay-data.md gp-4 (MECH-B-1)
**Complexity:** Small

Code-certain telemetry bug. Seeds 8/36/39 each persist a byte-identical failed_call row TWICE,
double-counting 5,969 input + 6,144 output tokens and inflating total_failed_calls from a true 4
distinct defaults to a reported 7. Meeting outcomes are unaffected (the meeting count comes from
meeting records), so it is telemetry-accuracy, not eval-invalidating — but it must be fixed before
any per-game token A/B. The duplicate comes through the parse_failures branch: a single DefaultedCall
carries the same LLMCallFailure twice (a retry path appends, the deadline-default capture appends
again).

**Files in scope:**
- orchestrator/game.py (`_record_deadline_defaults` ~L1213-1226: the parse_failures population that writes each failure)
- meetings/manager.py (the DefaultedCall / `recovered_call_failures` plumbing that double-appends)
- orchestrator/replay.py (`record_failed_call` — the single-write guard, if dedup lands at the recording chokepoint)
- tests/orchestrator/test_replay.py + tests/meetings/test_manager.py (a defaulted turn whose parse failed records EXACTLY ONE failed_call row; the seed-8/36/39 shape no longer double-counts)

**Files NOT in scope:**
- the fail-soft default behavior itself (7.10 — unchanged; only the telemetry write is de-duplicated)
- agents/, eval/ (the report reads whatever is recorded; 9.6 already reframed the metric surface)
- replays/samples/** (re-record is 9.11; the existing committed dup is fixed-forward on the new bytes)

**Definition of done:**
- [ ] A defaulted-turn parse failure records exactly one failed_call row; de-duplicated by (model, raw_response, input_tokens, output_tokens) OR recorded on exactly one path, with the choice documented.
- [ ] Confirmed offline against seeds 8/36/39: the failed-call token aggregate drops by 5,969 in / 6,144 out and total_failed_calls reads the true 4 distinct.
- [ ] The single non-duplicated default (seed 5) is unaffected; legitimate distinct failures in one meeting still each record once.
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
Open a PR from branch `phase-9-failed-call-dedup` with a title like `task 9.10: failed-call telemetry de-dup`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.4; audits/audit-2026-06-09-0347-gameplay-data.md gp-4 (MECH-B-1)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
