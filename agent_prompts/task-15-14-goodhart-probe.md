# Agent Prompt — 15.14 Adversarial Goodhart probe: red-team the referee, and the shared ES core

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.14 — Adversarial Goodhart probe: red-team the referee, and the shared ES core, anchored to audits/post-phase-14-ML-training-signal.md §3.2, §7.1.9 (the un-run charter guardrail); experiments/lab/ml-spike-charter.md (gap 3); experiments/lab/ml_spike/fo3_rubric_goodhart.py (the prior probe shape); audits/post-phase-14-ML-planning.md §12.2 (reward-hacking guards). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-goodhart-probe`
**Depends on:** 15.2, 15.7, 15.10
**Section refs:** audits/post-phase-14-ML-training-signal.md §3.2, §7.1.9 (the un-run charter guardrail); experiments/lab/ml-spike-charter.md (gap 3); experiments/lab/ml_spike/fo3_rubric_goodhart.py (the prior probe shape); audits/post-phase-14-ML-planning.md §12.2 (reward-hacking guards)
**Complexity:** Medium

Before the pause is allowed to use the 15.2 referee (with its baseline-3 floors from 15.7) as a
champion-selection gate, attack it: run evolution DIRECTLY on the referee score — the
deliberately-forbidden objective — and see what a genome can extract. This lands two artifacts. First,
the shared strict-typed ES core (`training/bakeoff/es.py`: seeded population loop, mutation, K-seed
fitness averaging, deterministic double-run behavior — ported from the spike's pure-Python loop, numpy
permitted) that 15.15/15.16 reuse, so every trainer in the phase shares one audited optimizer. Second,
the probe itself: ES on the full referee output (geomean × floors × supply floors) with the validity
gate as the only constraint, run on the training env with fake-provider meetings (and re-run under the
15.13 surrogate at 15.15 time, when meeting-controlled terms open to tactical pressure — the probe
report states this scoping explicitly). Every score gain is decomposed into which D-term or floor moved
and by what behavior; the deliverable is a trust verdict: exploits-found (each with the triggering
trajectory and a recommended floor/patch, routed to the PAUSE — this task does not edit the referee it
is attacking) or held-under-probe.

**Files in scope:**
- training/bakeoff/__init__.py (new)
- training/bakeoff/es.py (new: the shared ES core — 15.15 extends it behind its dependency edge)
- training/bakeoff/goodhart.py (new: the probe)
- training/reports/report-goodhart-probe.md (new: the trust verdict + exploit decompositions)
- tests/training/test_es.py (new)
- tests/training/test_goodhart_probe.py (new)

**Files NOT in scope:**
- eval/watchability.py (the referee is the SUBJECT under attack; patches route through the pause, never self-served here)
- training/env.py + training/rewards.py (consumed read-only)
- eval/validity.py (consumed as the constraint)

**Definition of done:**
- [ ] The ES core is deterministic under seed: two identical runs produce identical champion genomes and fitness traces (hash-pinned test), with K-seed fitness averaging and lexical tie-breaking built in.
- [ ] The probe runs a documented budget (generations × population × seeds, stated in the report) directly against the referee score on fixed seeds, validity-gated.
- [ ] Every fitness improvement in the probe's trace is decomposed to the moving D-term/floor with the behavioral cause named (e.g. meeting-farming D4, stall-to-clock D1) — no undecomposed gains in the report.
- [ ] The report ends in an explicit verdict: HELD (no exploit above a stated materiality bar) or EXPLOITS-FOUND (each with trajectory evidence + a recommended floor), and states the surrogate-path re-run obligation at 15.15.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

FO-3 already showed tactical play cannot move meeting-controlled rubric terms under fake meetings — so
the expected attack surface here is the physically-reachable terms (D4 contest via meeting-farming is
the known-tiny one) and the supply floors themselves; a null result on the meeting-dependent terms is
expected and must not be reported as "referee safe" without the surrogate-path caveat. Chaotic fitness
needs K-seed averaging (the spike's check-2 lesson). Cap the probe's budget honestly — the point is
cheap insurance against laundering a degenerate champion as "watchable," not an exhaustive search.

## Public types this task introduces
- `training.bakeoff.es.ESConfig`
- `training.bakeoff.goodhart.GoodhartProbeReport`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-15-goodhart-probe` with a title like `task 15.14: adversarial goodhart probe: red-team the referee, and the shared es core`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-training-signal.md §3.2, §7.1.9 (the un-run charter guardrail); experiments/lab/ml-spike-charter.md (gap 3); experiments/lab/ml_spike/fo3_rubric_goodhart.py (the prior probe shape); audits/post-phase-14-ML-planning.md §12.2 (reward-hacking guards)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
