# Agent Prompt — 18.15 The conviction-economy model: dataset, fit, fidelity, GO bar

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.15 — The conviction-economy model: dataset, fit, fidelity, GO bar, anchored to audits/audit-phase-18-planning.md §2.3 (the design + the honesty argument); training/surrogate/fidelity.py:213-243, 452-487 (the live-reconstructable channels + the voice-driven-share ceiling); training/surrogate/dataset.py (the table machinery to mirror); training/surrogate/runner.py:177-192 (what run_meeting-time state contains). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-conviction-model`
**Depends on:** 18.13
**Section refs:** audits/audit-phase-18-planning.md §2.3 (the design + the honesty argument); training/surrogate/fidelity.py:213-243, 452-487 (the live-reconstructable channels + the voice-driven-share ceiling); training/surrogate/dataset.py (the table machinery to mirror); training/surrogate/runner.py:177-192 (what run_meeting-time state contains)
**Complexity:** Integration

The training-signal instrument the phase was chartered around: a model
`g(pre-meeting typed state) → (expected contradiction flags minted, expected
testimony-backed conversion)` fit on the corpus's recorded triples, over ONLY channels a
training-time runner reconstructs at `run_meeting` time (vent-witness records, first-hand
sightings, body-proximity/seen-at-kill, belief scalars — never transcript-derived
features). Deterministic numpy fit, float-hex + sha artifact, its own staleness cap under
the ~143× rule, and a pre-stated population-relative GO bar: **held-out per-meeting
flag-count rank correlation (Spearman) ≥ 0.5 AND conversion-prediction fidelity ≥ 0.75 ×
(1 − voice_driven_share measured on the same population)** — with NO-GO pre-committed to
diagnostic-only (the fitness term does not ship, 18.16 integrates the pre-screen only as
advisory). If the 18.11 ruling was NONE (surgery path), this task binds to the standing
baseline-5 corpus and the contract's numbers re-read there.

**Files in scope:**
- training/conviction/ (new package: dataset.py, model.py, fidelity.py)
- training/artifacts/conviction/ (weights + sidecar + max-uses)
- training/reports/report-conviction-model.md (new)
- tests/training/test_conviction_model.py

**Files NOT in scope:**
- training/surrogate/ (independent artifact, untouched — the designer ruling)
- training/bakeoff/harness.py (18.16's integration)

**Definition of done:**
- [ ] The dataset walk re-validates against production folds before any fit (the 17.10 discipline: 0 raw mismatches, divergences measured and recorded); the fit is deterministic with the platform caveat documented; the artifact round-trips byte-stably.
- [ ] The verdict is taken on the FIRST held-out evaluation against the pre-stated bar, with the honest ceiling (voice-driven share) quoted as the structural denominator and the GO/NO-GO consequence machine-readable for 18.16.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror the surrogate package's shapes (table builder honoring `splits.json`, fidelity
report, `decide_*` verdict function, sha-keyed use counter) so the staleness/re-grounding
doctrine applies mechanically. The feature fence is the live-parity argument re-run: every
input must be derivable from `(trigger, state, agents)` at meeting time — write that test
(feature-by-feature provenance assertions), not just the docstring.

## Public types this task introduces
- `training.conviction.model.ConvictionEconomyModel`
- `training.conviction.dataset.build_conviction_table`
- `training.conviction.fidelity.decide_conviction_go`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The model's labels (flags minted, backed conversion) are exactly the quantities the referee
gates — the Goodhart-adjacent seam of the phase. The two structural guards: the model never
reads `eval/watchability.py` (AST-firewalled like the entrants), and 18.18 re-runs the
Goodhart probe with the conviction term live before any campaign selection leans on it.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`

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
Open a PR from branch `phase-18-conviction-model` with a title like `task 18.15: the conviction-economy model: dataset, fit, fidelity, go bar`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §2.3 (the design + the honesty argument); training/surrogate/fidelity.py:213-243, 452-487 (the live-reconstructable channels + the voice-driven-share ceiling); training/surrogate/dataset.py (the table machinery to mirror); training/surrogate/runner.py:177-192 (what run_meeting-time state contains)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
