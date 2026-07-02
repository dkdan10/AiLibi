# Agent Prompt — 14.12 Baseline 2: atomic re-record on the evidence-quality lever + v4 prompts + phase close

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-14.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 14.12 — Baseline 2: atomic re-record on the evidence-quality lever + v4 prompts + phase close, anchored to tasks/phase-14.md §14.7 (the proven smoke → re-record → validity-gate shape + the landed stamp infra); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the targets baseline 2 must beat); scripts/refresh_samples.sh; tests/meetings/test_manager.py (the railroad pin to RESTORE to a tripwire). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-14.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-14-baseline-2-rerecord`
**Depends on:** 14.10, 14.11
**Section refs:** tasks/phase-14.md §14.7 (the proven smoke → re-record → validity-gate shape + the landed stamp infra); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the targets baseline 2 must beat); scripts/refresh_samples.sh; tests/meetings/test_manager.py (the railroad pin to RESTORE to a tripwire)
**Complexity:** Integration

Operator-run spend/time gate, and the PHASE CLOSE. Re-record BOTH committed sets (50 × 4p1i + 50 × 9p2i) on
the locked tuple + the v4 prompt set + the 14.10 evidence-quality lever ON (stamped; the four 13.5 levers are
unconditional after 14.9), in ONE atomic PR, exactly the 14.7 shape: smoke first (3–5 seeds at 9p2i; parse
≈ 100%, zero 1024-truncation, wall-time projection — measured 14.7 datapoint: ~5h for both sets with 2
parallel seed workers), STOP for operator go, then the full runs, the HARD validity gate, and byte-identical
flag-aware reconstruction. Baseline 2 replaces baseline 1 as canonical. BECAUSE the fixes were specified
against measured defects, this close also measures them: restore the railroad REGRESSION PIN to the original
TRIPWIRE (zero crew rows at 1.0 from same-meeting flag stacks), and report the per-defect deltas vs baseline 1
(ejection accuracy vs 0.566, self-contradicted alibis vs 10%, guard-normalized ballots vs 47, conf-1.0
accusations vs 64, template-rationale share vs 33%, missed-deadline vs 23) plus the re-measured R-gate. The
honest R1 anchor is the RAILROAD-DISCOUNTED baseline-1 figure (25/50, audit §2 — the pinned rows accounted
for only 2 of the 24-game lift), not raw 27/50; and per audit §2 the stacked-flag signature is role-blind
(46% of impostor ejections carry it too), so "fewer stacked-flag convictions" alone is NOT a success metric.
Better CONVICTIONS, not just more: R1 holding near 25 with ejection accuracy up from 0.566 is the win
condition; R1 collapsing means 14.10 over-damped (stop, iterate the weighting, re-smoke — never weaken the
gate). Also report whether the 22 zero-flag crew mis-ejects (audit §7, untouched by 14.10's lever) moved
under v4's calibration/curation fixes. Close the phase with the final audit + STATUS banner.

**Files in scope:**
- replays/samples/4p1i/ (50 replays + report + MANIFEST re-recorded; `flags` rows now stamp the 14.10 lever)
- replays/samples/9p2i/ (50 replays + report + MANIFEST re-recorded; roster sidecar unchanged)
- tests/meetings/test_manager.py (the railroad pin RESTORED to the zero-railroad tripwire on the new bytes)
- tests/ committed-bytes pins (the #213-style mechanical re-pin across the byte-coupled tests — value pins re-derived, coordinates re-anchored property-preservingly)
- scripts/refresh_samples.sh (the locked-substrate preflight guard updated to require the 14.10 lever ON alongside the existing tuple)
- audits/audit-phase-14-close.md (new: the phase-close audit — per-defect deltas, the re-measured R-gate, the honest verdict + Phase 15 recommendation)
- tasks/phase-14.md (final STATUS banner: phase CLOSED on baseline 2)

**Files NOT in scope:**
- engine/ + meetings/ + agents/ + llm/ + eval/ source (behavior landed in 14.10/14.11; this records + regenerates + re-pins only)
- meetings/manager.py token caps (FROZEN — turn 2048 / vote 1024, unchanged through the whole phase)
- agents/strategic/prompts/ (v4 landed in 14.11; recording only)
- tests/fixtures/prompt_regression/ (stays frozen — the self-contained two-version A/B harness, per the #213 decision)

**Definition of done:**
- [ ] Smoke first (3–5 seeds at 9p2i, lever ON + v4): thinking policy holds, parse-success ≈ 100%, zero ballot truncation, genuine-class conversion has NOT collapsed (the 14.10 over-damping check), wall-time projection reported; STOP for operator go.
- [ ] Both sets re-recorded in ONE atomic PR on the locked tuple + v4 + the 14.10 lever ON; MANIFESTs/reports regenerated; the `flags` stamp records the lever; byte-identical flag-aware reconstruction holds.
- [ ] HARD validity gate passes (the 14.7 criteria: friendly-fire 0, all game_over, betrayal 0, leak suite green, meeting_rate ≥ 0.60 with ≥ 30 resolved at 9p2i, zero tick-1 kills, zero dangling primary_reason_id, cost rows 0, provenance rows exact).
- [ ] The railroad TRIPWIRE is restored (zero crew rows at 1.0 from ≥2 same-meeting flags on the new bytes) — the regression-pin era ends with the defect, not around it.
- [ ] The close audit reports the per-defect deltas vs baseline 1 (ejection accuracy / self-contradicted alibis / guard-normalized ballots / conf-1.0 accusations / template-rationale share / missed-deadline count) and the re-measured R-gate vs baseline 1 AND the 9B — no number retrofit.
- [ ] The phase STATUS banner records the close; the audit recommends Phase 15 (persona/voice layer; tactical/ML between-meeting play) with the evidence for each.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The operator env is the 14.7 recipe plus the new lever: `AILIBI_LLM_PROVIDER=featherless` +
`FEATHERLESS_API_KEY` + `AILIBI_PROMPT_SET=qwen3_32b` + `AILIBI_EVIDENCE_QUALITY_LIFT=1` (the four 13.5 vars
are gone after 14.9 — the substrate is unconditional). Update the refresh-script preflight guard to require
the lever alongside the prompt set BEFORE any seed stages (the same fail-loud shape PR #209 added). Run the
two sets with 2 parallel seed workers — the measured 14.7 wall time was ~5h total; smoke-project anyway. The
per-defect delta measurements are cheap offline folds over the new bytes (the same greps/folds 14.8
documented); put them in the close audit next to their baseline-1 numbers. The #213 PR is the template for
the mechanical test re-pin — expect the same byte-coupled test files; re-anchor property-preservingly and say
so per test.

## Integration risk

The phase's final spend gate, with a two-sided failure mode: the railroad tripwire must be RESTORABLE (14.10
under-fixed if any new railroad row appears) AND genuine conviction must survive (14.10 over-damped if R1 or
genuine-class conversion collapses — the seed-44-m0-style true-impostor catches are the canary). Either
failure is a stop-and-iterate on 14.10's weighting (or 14.11's prompts), re-smoke, and only then the full
spend — never weaken the §4.6 gate, never raise the caps, never ship a baseline that papers a defect the
phase set out to fix.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import llm.featherless_client"`
- `uv run python -c "import llm.provider"`
- `uv run python -c "import agents.memory.beliefs"`

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
Open a PR from branch `phase-14-baseline-2-rerecord` with a title like `task 14.12: baseline 2: atomic re-record on the evidence-quality lever + v4 prompts + phase close`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-14.md §14.7 (the proven smoke → re-record → validity-gate shape + the landed stamp infra); audits/audit-2026-07-01-phase-14-baseline1-characterization.md (the targets baseline 2 must beat); scripts/refresh_samples.sh; tests/meetings/test_manager.py (the railroad pin to RESTORE to a tripwire)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
