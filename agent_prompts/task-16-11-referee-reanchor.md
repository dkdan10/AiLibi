# Agent Prompt — 16.11 The referee re-anchor: population-relative testimony-backed conversion

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.11 — The referee re-anchor: population-relative testimony-backed conversion, anchored to audits/audit-phase-15-close.md §10 (the owner ruling this implements) + §11 (the conversion-seam finding); eval/watchability.py (the per-baseline floors block + the subject-aware backing definition 15.19 landed); training/reports/results-champion-close.jsonl (the committed calibration fixture). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-referee-reanchor`
**Depends on:** none
**Section refs:** audits/audit-phase-15-close.md §10 (the owner ruling this implements) + §11 (the conversion-seam finding); eval/watchability.py (the per-baseline floors block + the subject-aware backing definition 15.19 landed); training/reports/results-champion-close.jsonl (the committed calibration fixture)
**Complexity:** Medium

Implement the owner-ratified recalibration (2026-07-11): the `testimony_backed_conversion` floor
stops being the FSM baseline's absolute constant (0.6636 — the value the champion close FAILED
against, first non-FSM population ever measured) and becomes POPULATION-RELATIVE: the floor
derives from the scored population's own evidence supply and backing base-rate, so a candidate is
judged on whether its games CONVERT the testimony they actually contain, not on whether they
reproduce another population's ratio. The starvation catch must stay sharp: a synthetic
evidence-starved set (high meeting rate, zero backed accusations) fails regardless of population.
The committed champion-close row is the calibration fixture: under the new definition it must
read as the intended non-blocking outcome (the owner's close-over ruling, now derived rather than
ruled), documented in the module with the derivation. The other two supply floors
(witnessed-event rate, flags-per-meeting) keep their per-baseline pinned form — this task
re-anchors exactly the one gauge the close contracted forward.

**Files in scope:**
- eval/watchability.py (the conversion-floor definition + the per-baseline floors block region — ahead of 16.14/16.17's pins)
- tests/eval/test_watchability_reanchor.py (new: the champion-close fixture reproduction + the synthetic-starved FAIL + the FSM-baseline consistency check)

**Files NOT in scope:**
- eval/validity.py + eval/vj_instruments.py (gate definitions only here; diagnostics are 16.10's)
- training/reports/ (the fixture is read, never rewritten)
- scripts/measure_baseline.py (16.10 owns the CLI region this phase; the referee's existing --watchability surface is unchanged in shape)

**Definition of done:**
- [ ] The population-relative definition is implemented with its derivation documented (what "the scored population's own achievable conversion" means, mechanically), and the per-baseline floors block carries it for baseline-3 (existing sets re-measured, values pinned with the derivation in comments).
- [ ] The champion-close fixture reproduces: `results-champion-close.jsonl`'s recorded gauges, re-scored under the new definition, yield the non-blocking outcome the owner ruling anticipated — with the old-definition FAIL preserved in the test as the historical contrast.
- [ ] A synthetic starved set still FAILS (the floor's reason to exist survives the re-anchor), and the FSM baseline itself still PASSES at equality (self-consistency).
- [ ] The referee's module docstring records the ruling's provenance (close audit §10, owner 2026-07-11) and the Q1-precedent rationale.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The honest derivation ties the floor to the population's own backing supply: of the accusations
its games produce, what share is subject-aware-backed (the 15.19 definition), and what conversion
does that supply support — the floor is a function of measured supply, not a constant. Keep the
function pure and the derivation quotable (the 16.17 close audit will print it). Resist widening
scope: one gauge re-anchors; the geomean, the other floors, and the integrity floor are untouched.

## Public types this task introduces
- `eval.watchability.population_relative_conversion_floor`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-16-referee-reanchor` with a title like `task 16.11: the referee re-anchor: population-relative testimony-backed conversion`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-close.md §10 (the owner ruling this implements) + §11 (the conversion-seam finding); eval/watchability.py (the per-baseline floors block + the subject-aware backing definition 15.19 landed); training/reports/results-champion-close.jsonl (the committed calibration fixture)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
