# Agent Prompt — 17.12 The impostor bake-off re-run (full slate) + finalist selection

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.12 — The impostor bake-off re-run (full slate) + finalist selection, anchored to tasks/phase-15.md 15.15 (the recipe this re-runs verbatim); training/bakeoff/harness.py (the protocol: surrogate path + fake-provider real path, `--entrant all`); audits/audit-phase-15-pause.md (the decisions binding re-runs: methods in, torch out, stabilizers); the 16.11 referee floors via 17.11's constants. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-impostor-bakeoff-rerun`
**Depends on:** 17.10, 17.11
**Section refs:** tasks/phase-15.md 15.15 (the recipe this re-runs verbatim); training/bakeoff/harness.py (the protocol: surrogate path + fake-provider real path, `--entrant all`); audits/audit-phase-15-pause.md (the decisions binding re-runs: methods in, torch out, stabilizers); the 16.11 referee floors via 17.11's constants
**Complexity:** Integration

Re-run the Phase-15 recipe with the full slate (locked decision 1) against the
re-grounded surrogate and the baseline-5 selection floors: all four impostor methods
through the same seeds/compute protocol, results table regenerated, finalists chosen
by the same referee-gated ranking. The report must show FLOOR SENSITIVITY per finalist
(distance to each supply floor and the conversion floor) beside the ranking — the
designer ruling on selection-bar honesty: a starved-economy rejection must be legible
as the instrument working. Method ranking changes vs Phase 15 are findings to explain
(what about the baseline-5 economy moved them), not anomalies to smooth.

**Files in scope:**
- training/reports/results-impostor-bakeoff.jsonl (regenerated rows)
- training/reports/report-impostor-bakeoff.md (the re-run report + floor sensitivity)
- training/artifacts/impostor/ (candidate artifacts per method)
- tests/training/test_bakeoff_harness.py (protocol re-pins if rows move)

**Files NOT in scope:**
- agents/tactical/learned/ (productization is 17.16's, after the real-LLM eval)
- training/crew/ (17.13)

**Definition of done:**
- [ ] All four methods complete the protocol on the re-grounded substrate; the results table carries per-entrant referee scoring under the flipped floors with floor-sensitivity columns; finalists are named by the recorded ranking rule.
- [ ] The Phase-15 vs Phase-17 ranking delta is stated with a substrate-grounded explanation per mover; every artifact row stamps the 15.9 provenance (policy_id, method, encoder_version, weights sha, anchor).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

`--entrant all` re-runs the recorded protocol; the work is in the reading, not the
wiring. Budget the ES loops first (they dominated Phase 15); quote surrogate max-uses
consumption per entrant as you go so the cap never surprises the tail entrants.

## Integration risk

Operator compute: the ES/DAgger loops are the long pole after the corpus. If a method
fails to converge on the new economy, record the failure as a finding row (the Phase-14
doctrine) — the slate is full so the phase never hinges on one method. The surrogate's
staleness cap is live: the harness must respect the re-derived max-uses budget, and the
report quotes consumption.

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
Open a PR from branch `phase-17-impostor-bakeoff-rerun` with a title like `task 17.12: the impostor bake-off re-run (full slate) + finalist selection`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-15.md 15.15 (the recipe this re-runs verbatim); training/bakeoff/harness.py (the protocol: surrogate path + fake-provider real path, `--entrant all`); audits/audit-phase-15-pause.md (the decisions binding re-runs: methods in, torch out, stabilizers); the 16.11 referee floors via 17.11's constants), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
