# Agent Prompt — 15.19 Referee hardening: conversion-coupled D2 separation + subject-aware observation backing

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.19 — Referee hardening: conversion-coupled D2 separation + subject-aware observation backing, anchored to audits/audit-phase-15-pause.md §4 (the per-channel re-verdict) + decision blocks; training/reports/report-goodhart-probe.md (the kill-lever D2-separation exploit, 6.51 → 16.62, and the recommended floor); training/reports/report-impostor-bakeoff.md §6 (the surrogate-path HELD-for-the-wrong-reason delta); audits/review-phase-15-midwave.md Q2 (the owner-ratified subject-aware re-anchoring, 2026-07-09); eval/watchability.py (`_observation_backed_conversion`, the per-baseline floor blocks). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-referee-hardening`
**Depends on:** 15.18
**Section refs:** audits/audit-phase-15-pause.md §4 (the per-channel re-verdict) + decision blocks; training/reports/report-goodhart-probe.md (the kill-lever D2-separation exploit, 6.51 → 16.62, and the recommended floor); training/reports/report-impostor-bakeoff.md §6 (the surrogate-path HELD-for-the-wrong-reason delta); audits/review-phase-15-midwave.md Q2 (the owner-ratified subject-aware re-anchoring, 2026-07-09); eval/watchability.py (`_observation_backed_conversion`, the per-baseline floor blocks)
**Complexity:** Medium

Land the two referee patches the pause contracted BEFORE any champion selection leans on the referee's
fine D2-conversion differences (the 15.21 deployment re-score and the 15.23 close-audit champion gate
both carry a dependency edge on this task). Patch 1, the **conversion-coupled D2 floor** (the 15.14
finding, exploited on the fake path regardless of the composed referee's HELD): gate the D2 separation
sub-term on backed conversion — separation without an ejection or a contradiction flag is suspicion
theater, not deduction — so the forced-kill trajectory (separation 0.20 → 0.84 with conversion pinned
at 0.00) can no longer lift `mean_score` 6.51 → 16.62; and document in the module docstring that
`mean_score` must NEVER be read without the supply-floor gate. Patch 2, the **subject-AWARE
observation-backing re-anchoring** (owner-ratified Q2): `_observation_backed_conversion` today counts
an accusation "backed" if the speaker's turn carries ANY grounded observation — a trained impostor can
utter a genuine vent sighting of X in the turn that accuses innocent Y and the Y-accusation counts
backed. Re-define backing as subject-aware (the grounded observation's subject must be the accused),
re-pin the per-baseline floors under the new definition ON THE SAME committed bytes (baseline-3
samples; the corpus figures reported alongside per the Q3 denominator rule), and keep the old
subject-agnostic parity fixture as a frozen historical pin (renamed, never deleted — 15.2's
cross-implementation evidence stays reproducible). Also close the 4p1i floor-degeneracy finding from
the pause audit: the 4p1i `witnessed_event_rate` floor is pinned to a one-event numerator (1/55 on the
samples), so the corpus-4p1i set FAILS it at 0.0 measured — rare-event floors whose baseline numerator
is ≤ 1 are marked advisory (reported, never referee-failing) with the rule documented and tested.

**Files in scope:**
- eval/watchability.py (the D2 conversion-coupling, the subject-aware backing definition, the re-pinned per-baseline floor blocks, the advisory rare-event floor rule)
- tests/eval/test_watchability.py (exploit-trajectory regression fixture, subject-aware backing tests, frozen subject-agnostic parity pin, advisory-floor tests)

**Files NOT in scope:**
- eval/meeting_quality.py (its gauges are consumed as-is; backing is computed inside eval/watchability.py)
- training/bakeoff/goodhart.py + training/reports/ (the probe and its findings are frozen evidence, never edited)
- scripts/measure_baseline.py (the CLI surface is unchanged — the fold's internals harden underneath it)

**Definition of done:**
- [ ] A synthetic exploit-trajectory fixture reproducing the 15.14 shape (high D2 separation, zero conversion, zero flags) scores ~0 on the D2 term under the hardened referee, with a regression test pinning it; the scripted-FSM baseline-3 sets still PASS the hardened referee end-to-end.
- [ ] Backing is subject-aware: a fixture where a speaker grounds a vent sighting of X while accusing Y counts the Y-accusation UNBACKED (test), and the old subject-agnostic fixture result is kept as a frozen, clearly-labeled historical pin.
- [ ] The per-baseline floor blocks are re-pinned under the subject-aware definition by re-measuring the SAME committed baseline-3 bytes with the committed CLIs, measured values in comments (corpus figures alongside per the Q3 rule); `scripts/measure_baseline.py --watchability` runs clean on all four committed sets with the new floors.
- [ ] Rare-event floors with a baseline numerator ≤ 1 (today: the 4p1i `witnessed_event_rate`, 1/55) are advisory — reported in the JSON but excluded from `supply_floors_passed` — and `replays/ml_corpus/4p1i` consequently PASSES the referee (its other gauges already clear); a test pins the advisory rule.
- [ ] The module docstring records the doctrine deltas: selection-only (unchanged), conversion-coupled D2, subject-aware backing, mean_score-never-without-floors, and cites the pause audit §4 as the re-verdict of record.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Both patches live entirely in `eval/watchability.py` — `_observation_backed_conversion` is the backing
chokepoint and the D1–D4 composition is a few lines above the floor gate. Re-pin floors by RUNNING the
CLIs, never by editing constants freehand: the floor values are measured facts with the measurement in
a comment. Expect the subject-aware re-pin to LOWER `testimony_backed_conversion` floors (fewer
accusations count backed under the stricter definition) — direction is a finding, not a failure; what
matters is that relative gates stay sound because candidate and baseline are measured under the same
definition. The frozen parity pin should be a renamed test asserting the OLD definition's value on the
same fixture, marked as historical.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.bakeoff.es"`
- `uv run python -c "import training.bakeoff.goodhart"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.determinism"`
- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import eval.funnel"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import eval.watchability"`
- `uv run python -c "import training.surrogate.ballots"`
- `uv run python -c "import training.surrogate.runner"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import training.surrogate.dataset"`
- `uv run python -c "import training.surrogate.fidelity"`
- `uv run python -c "import engine.rng"`
- `uv run python -c "import training.crew.options"`
- `uv run python -c "import training.crew.scorer"`

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
Open a PR from branch `phase-15-referee-hardening` with a title like `task 15.19: referee hardening: conversion-coupled d2 separation + subject-aware observation backing`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-pause.md §4 (the per-channel re-verdict) + decision blocks; training/reports/report-goodhart-probe.md (the kill-lever D2-separation exploit, 6.51 → 16.62, and the recommended floor); training/reports/report-impostor-bakeoff.md §6 (the surrogate-path HELD-for-the-wrong-reason delta); audits/review-phase-15-midwave.md Q2 (the owner-ratified subject-aware re-anchoring, 2026-07-09); eval/watchability.py (`_observation_backed_conversion`, the per-baseline floor blocks)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
