# Agent Prompt — 5.3 Accusation-calibration metric

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.3 — Accusation-calibration metric, anchored to DESIGN.md §11.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-accusation-calibration-metric`
**Depends on:** 5.1 merged
**Section refs:** DESIGN.md §11.3
**Complexity:** Medium

Accusation-calibration metric.

**Files in scope:**
- eval/accusation_calibration.py
- tests/eval/test_accusation_calibration.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/
- scripts/run_tournament.py
- eval/vote_correctness.py
- eval/alibi_fabrication.py
- eval/cost_dashboard.py
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] Accusation-calibration metric is implemented against eval report data.
- [ ] Metric module has focused unit tests using typed report fixtures.
- [ ] This task does not wire the metric into tournament JSON output.
- [ ] `uv run mypy --strict eval` passes.
- [ ] `uv run ruff check .` passes.

## Implementation hint

See DESIGN.md §11.3. Bin accusations by confidence and compute actual-impostor-rate per bin. Calibrated when high-confidence accusations are correct more often than low-confidence ones.

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
Open a PR from branch `phase-5-accusation-calibration-metric` with a title like `task 5.3: accusation-calibration metric`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
