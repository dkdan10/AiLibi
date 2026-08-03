# Agent Prompt — 18.5 The anchor study: λ sweep + filtered-BC anchor refinement

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.5 — The anchor study: λ sweep + filtered-BC anchor refinement, anchored to audits/audit-phase-18-planning.md §2.4 (the two levers) + §6 (the piKL reading); training/bakeoff/harness.py `inner_episode_fitness` (:569-590, the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full budget: 285 s/run on the fake path); replays/ml_corpus/ (the filtered-BC source). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-anchor-study`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §2.4 (the two levers) + §6 (the piKL reading); training/bakeoff/harness.py `inner_episode_fitness` (:569-590, the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full budget: 285 s/run on the fake path); replays/ml_corpus/ (the filtered-BC source)
**Complexity:** Medium

The cheapest levers on the exact gauges the champion failed. (1) **λ sweep**: re-run the
utility-es training at a grid of anchor weights (e.g. 0.25/0.5/1.0/2.0/4.0), score each
champion through the standing fake-path protocol, and report the fitness/anchor-CE/
descriptor-footprint Pareto — the training-time dial that piKL says controls legibility.
(2) **Filtered-BC anchor refinement**: fit an alternative anchor policy over the FSM option
features from the corpus's crew-winning/high-flag games (numpy weighted logistic — the
corpus as a prior source, never a training environment), and evaluate it OFFLINE
(per-decision agreement with the FSM over the corpus decision stream; where it diverges and
toward what). The ES-leg-under-the-refined-anchor is deliberately NOT run here: the
harness's anchor-CE is computed against the FSM's own choice, and swapping the anchor needs
the additive anchor-policy seam 18.16 adds — the refined-anchor ES leg is a named campaign
entrant configuration at 18.24, which holds both the artifact (this task) and the seam
(18.16). Report-only: no champion ships from this task. Deterministic, $0, CPU. Substrate
provenance: every artifact this study freezes carries the corpus/floor substrate sha it was
fitted/selected against — the 18.24 campaign refuses stale-substrate seeds without the
cheap deterministic re-fit/re-run at the adopted substrate.

**Files in scope:**
- training/anchor_study.py (new: the sweep driver + the filtered-BC fit)
- training/artifacts/anchor_study/ (new: the frozen candidate genomes/anchors — float-hex weights + sha sidecars + a config carrying the substrate sha, the byte-addressable seeds 18.24 reloads)
- training/reports/report-anchor-study.md (new)
- tests/training/test_anchor_study.py

**Files NOT in scope:**
- training/bakeoff/harness.py + utility_es.py (consumed through their public seams)
- training/artifacts/impostor/ (the committed champions do not move)

**Definition of done:**
- [ ] The sweep reproduces the λ=1.0 committed champion byte-identically (the determinism cross-check), and every sweep row carries fitness, anchor-CE, win rate, take-rate, and descriptor footprint on the standing 30-seed protocol.
- [ ] The filtered-BC anchor's fit is deterministic (documented platform caveat per the surrogate precedent), its game filter is stated (which games, why), and its offline FSM-agreement/divergence evaluation is reported; the report names which candidates (if any) the 18.24 campaign should seed with, and every frozen artifact carries its substrate sha.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Full utility-es training is 285 s on the fake path, so the whole grid is under an hour of
CPU — resist any urge to subsample the protocol. The filtered-BC fit mirrors the
`Fo6Logistic` deterministic recipe (zeros init, fixed epochs/lr, no RNG).

## Public types this task introduces
- `training.anchor_study.AnchorStudyReport`
- `training.anchor_study.fit_filtered_bc_anchor`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-18-anchor-study` with a title like `task 18.5: the anchor study: λ sweep + filtered-bc anchor refinement`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §2.4 (the two levers) + §6 (the piKL reading); training/bakeoff/harness.py `inner_episode_fitness` (:569-590, the anchor penalty seam); training/bakeoff/utility_es.py:708-718 (the full budget: 285 s/run on the fake path); replays/ml_corpus/ (the filtered-BC source)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
