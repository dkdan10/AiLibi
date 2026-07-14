# Agent Prompt — 17.13 The crew track re-run (measurement-only)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.13 — The crew track re-run (measurement-only), anchored to tasks/phase-15.md 15.16 + 15.22 (the crew bases: the general track + the owned-task surface); training/crew/scorer.py (the referee import 17.11 flipped); locked decision 1 (measurement-only — no crew deployment surface this phase). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-crew-track-rerun`
**Depends on:** 17.10, 17.11
**Section refs:** tasks/phase-15.md 15.16 + 15.22 (the crew bases: the general track + the owned-task surface); training/crew/scorer.py (the referee import 17.11 flipped); locked decision 1 (measurement-only — no crew deployment surface this phase)
**Complexity:** Medium

Re-run both crew bases under the baseline-5 economy and floors, regenerate the crew
results and report. Measurement-only by locked decision: rankings, referee scores, and
findings are recorded; no crew artifact ships to a production surface (there is none —
`factory.py` wraps impostor decisions only). The interesting question the report must
answer: does the citation-era economy change what crew utility learns (e.g. does the
owned-task base's advantage move when convictions demand citations)?

**Files in scope:**
- training/reports/results-crew-track.jsonl + results-crew-owned-tasks.jsonl (regenerated)
- training/reports/report-crew-track.md (the re-run reading)
- training/artifacts/crew/ (candidate artifacts, measurement-tier)
- tests/training/test_crew_options.py (re-pins if rows move)

**Files NOT in scope:**
- agents/tactical/learned/ (no crew deployment — locked decision 1)
- training/bakeoff/harness.py (17.11/17.12's)

**Definition of done:**
- [ ] Both crew bases complete under the flipped floors; the report states the baseline-5 vs baseline-3 delta per base with the economy-grounded reading, and every artifact row carries provenance stamps.
- [ ] The measurement-only posture is stated in the report with the Phase-18 routing note (a crew deployment surface is heterogeneous-lobby work).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

This is a re-run, not a redesign — the 15.16/15.22 protocol verbatim on the new
substrate. Resist adding crew-side features; the value is the clean before/after.

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
Open a PR from branch `phase-17-crew-track-rerun` with a title like `task 17.13: the crew track re-run (measurement-only)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-15.md 15.16 + 15.22 (the crew bases: the general track + the owned-task surface); training/crew/scorer.py (the referee import 17.11 flipped); locked decision 1 (measurement-only — no crew deployment surface this phase)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
