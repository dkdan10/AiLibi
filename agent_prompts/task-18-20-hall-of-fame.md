# Agent Prompt — 18.20 The hall of fame + PFSP-lite opponent sampler

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.20 — The hall of fame + PFSP-lite opponent sampler, anchored to audits/audit-phase-18-planning.md §4 (#8) + §6 (the AlphaStar/PSRO transfer: frozen pool + hardness-weighted sampling); training/bakeoff/harness.py:843-868 (the artifact layout); training/surrogate/runner.py:88-131 (the sha-keyed use-counter doctrine the opponent bookkeeping mirrors); the 18.6 cell artifacts (a seed source). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-hall-of-fame`
**Depends on:** 18.6, 18.19
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + §6 (the AlphaStar/PSRO transfer: frozen pool + hardness-weighted sampling); training/bakeoff/harness.py:843-868 (the artifact layout); training/surrogate/runner.py:88-131 (the sha-keyed use-counter doctrine the opponent bookkeeping mirrors); the 18.6 cell artifacts (a seed source)
**Complexity:** Medium

The frozen opponent pool: a `hall_of_fame.json`-indexed artifact store
(`training/artifacts/coevo/<side>/gen-<N>/`) holding frozen genomes with provenance
(generation, sha, trained-against sha), a deterministic PFSP-lite sampler (opponents
weighted toward currently-hard members — hardness from the exact deterministic payoff
entries, re-normalized each generation, seeded RNG), ingestion from the 18.6 MAP-Elites
cells as behaviorally-diverse founders, and opponent-staleness bookkeeping (a capped
generation count per frozen opponent before refresh, sha-keyed). Pure numpy/stdlib;
everything reloadable bit-exactly.

**Files in scope:**
- training/coevo/hall_of_fame.py (new)
- tests/training/test_hall_of_fame.py

**Files NOT in scope:**
- training/coevo/factory.py + rollout.py (18.19's modules — consumed)
- training/bakeoff/map_elites.py (its cell artifacts are read via 18.6's public loader)

**Definition of done:**
- [ ] The store round-trips frozen genomes with sha verification (fail-loud on drift), the index carries full provenance, and MAP-Elites cells ingest as founders through 18.6's loader — with the founder's SUBSTRATE sha verified against the current campaign substrate at the ingest point: a mismatch refuses ingestion loudly pending the cheap deterministic re-run at the adopted substrate (the stale-seed fence moves here from 18.24, BEFORE the pool is built or sampled).
- [ ] The sampler is deterministic under its seed, its hardness weighting is computed from supplied payoff entries (no hidden state), and the staleness cap raises loudly at exhaustion — all fixture-pinned.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Deterministic evals make the payoff matrix exact — the sampler needs no win-rate estimation
machinery, just the recorded per-pair fitness cells. Keep the weighting function small and
documented (the survey's lesson: a ≤30-member pool with win-weighted sampling captures the
benefit; resist meta-Nash solvers).

## Public types this task introduces
- `training.coevo.hall_of_fame.HallOfFame`
- `training.coevo.hall_of_fame.sample_opponents`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import eval.off_menu"`
- `uv run python -c "import eval.kill_craft"`
- `uv run python -c "import eval.deception_instruments"`
- `uv run python -c "import training.bakeoff.map_elites"`

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
Open a PR from branch `phase-18-hall-of-fame` with a title like `task 18.20: the hall of fame + pfsp-lite opponent sampler`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#8) + §6 (the AlphaStar/PSRO transfer: frozen pool + hardness-weighted sampling); training/bakeoff/harness.py:843-868 (the artifact layout); training/surrogate/runner.py:88-131 (the sha-keyed use-counter doctrine the opponent bookkeeping mirrors); the 18.6 cell artifacts (a seed source)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
