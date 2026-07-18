# Agent Prompt — 18.21 The alternating-freeze driver + stabilizers

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.21 — The alternating-freeze driver + stabilizers, anchored to audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-alternating-driver`
**Depends on:** 18.20
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams)
**Complexity:** Integration

The campaign engine: an alternating-freeze loop — evolve one side's population (the
standing ES) against a PFSP-sampled slate of frozen opponents while the other side is
frozen, freeze the champion into the hall of fame, swap sides, repeat — with the full
stabilizer instrumentation emitted per generation: the absolute anchor benchmark (champion
vs scripted FSM, both directions — the cycling detector: oscillating co-matchup with a flat
anchor = cycling, monotone anchor = progress), a per-side short-horizon exploiter probe (a
small ES bred purely to beat the current champion; its found exploits join the hall of
fame), and the anchor-CE term retained toward the FIXED scripted FSM on both sides (never
toward the moving opponent). One side moves at a time, always — the barred simultaneous
form is structurally unreachable. Deterministic end-to-end on the fake/surrogate path;
machine-readable campaign rows.

**Files in scope:**
- training/coevo/driver.py (new)
- tests/training/test_coevo_driver.py; (a miniature two-swap campaign on tiny budgets: freeze/swap mechanics, HoF growth, benchmark emission, exploiter integration, determinism digest)

**Files NOT in scope:**
- training/coevo/hall_of_fame.py + factory.py + rollout.py (consumed)
- training/bakeoff/es.py (the optimizer is imported unchanged)

**Definition of done:**
- [ ] A miniature campaign (2 swaps, tiny budgets) runs deterministically twice with identical digests, grows the hall of fame with full provenance, emits the absolute-benchmark and exploiter rows per generation, and never updates both sides in one step (structurally asserted).
- [ ] The campaign row schema carries everything 18.24's report needs (per-gen fitness, anchor benchmarks both directions, opponent slate shas, exploiter outcomes, conviction/surrogate consumption).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The driver owns ALL the meters (surrogate + conviction use counters threaded once,
cumulative) — a campaign that exhausts a cap must stop loudly at a swap boundary, which is
the natural re-grounding point. The exploiter probe is the standing ES at a tiny budget
(e.g. 5×6) with fitness = beat-the-champion only.

## Public types this task introduces
- `training.coevo.driver.run_alternating_freeze`
- `training.coevo.driver.CoevoCampaignRow`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is where compounding budgets can silently explode: population × generations × seeds ×
opponent-slate size. The driver must compute and log its total game count up front and
refuse a configuration whose fake-path game count exceeds a stated ceiling without an
explicit override flag — no accidental week-long runs.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.bakeoff.harness"`
- `uv run python -c "import training.conviction.model"`
- `uv run python -c "import training.conviction.dataset"`
- `uv run python -c "import training.conviction.fidelity"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.manager"`
- `uv run python -c "import agents.tactical.learned.crew_forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
- `uv run python -c "import orchestrator.replay"`
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
Open a PR from branch `phase-18-alternating-driver` with a title like `task 18.21: the alternating-freeze driver + stabilizers`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#8) + §6 (the stabilizer kit); audits/audit-phase-15-pause.md decision 4 (the barred naive form; the entry condition this satisfies); experiments/lab/ml_spike/fo2_coevolution.py (the absolute-anchor cycling detector precedent); training/coevo/ (18.19/18.20's seams)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
