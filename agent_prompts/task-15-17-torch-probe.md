# Agent Prompt — 15.17 The torch PPO+recurrent probe (experiment-tier, opt-in)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.17 — The torch PPO+recurrent probe (experiment-tier, opt-in), anchored to audits/post-phase-14-ML-training-signal.md §9 (the staged-escalation dependency posture); audits/post-phase-14-ML-planning.md §9 Option 3 (PPO/recurrent: strongest asymptotics, heavy costs); owner decision 2026-07-05 (torch as probe only; promotion is a pause decision). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-torch-probe`
**Depends on:** 15.8, 15.10, 15.15
**Section refs:** audits/post-phase-14-ML-training-signal.md §9 (the staged-escalation dependency posture); audits/post-phase-14-ML-planning.md §9 Option 3 (PPO/recurrent: strongest asymptotics, heavy costs); owner decision 2026-07-05 (torch as probe only; promotion is a pause decision)
**Complexity:** Medium

The owner's torch experiment, run where it cannot leak into the production posture: a PPO + recurrent
(GRU/LSTM) impostor-policy probe under `experiments/lab/torch_probe/`, executed via `uv run --with
torch` — torch never enters `pyproject.toml` dependencies or `uv.lock` this phase. The probe answers ONE
question for the pause: does gradient RL with real POMDP memory beat the pure-Python ES ceiling by
enough to justify torch's costs (dependency weight, cross-machine float determinism, CI story)?
Comparability is the design constraint: the probe trains through the SAME `TacticalRolloutEnv` and
encoder-v2 features, and evaluates through 15.15's COMMITTED harness protocol and fixed seed config,
consumed read-only (the 15.15 dependency edge exists so the protocol is real code the probe invokes,
never a hand-copied tuple shape or self-chosen seeds), reporting in the 15.15 metric-tuple shape —
with the honest exception that the determinism-harness hash is expected to FAIL for a torch policy, so
the probe reports a seeded-run variance story (N repeats, spread of every metric) instead of pretending.
It also measures the escape hatch: distillability — behavior-clone the torch policy into the pure-Python
inference net and report student-teacher agreement, so Wave 2 can take the capability without the
dependency if the owner wants it. The `experiments/lab/torch_probe/` directory joins the ml_spike mypy
exclusion (the pyproject exclude-regex edit is this task's ONLY pyproject touch — the dependencies
region is 15.8's).

**Files in scope:**
- experiments/lab/torch_probe/ (new: probe scripts + README; experiment-tier, mypy-excluded)
- experiments/lab/report-torch-probe.md (new)
- pyproject.toml (mypy exclude regex region only — dependencies untouched)
- tests/experiments/test_torch_probe_excluded.py (new: pins the exclusion + that no production package imports the probe)

**Files NOT in scope:**
- uv.lock (torch is NOT resolved into the project — `uv run --with` only)
- training/ (imported read-only; nothing ships into it)
- .github/ + CI workflow files (no CI job runs the probe)

**Definition of done:**
- [ ] The probe trains an impostor policy through `training.env.TacticalRolloutEnv` + `agents.tactical.features.TacticalFeatureEncoder` (same env, same features — comparability asserted in the report, with any deviation documented).
- [ ] Results are emitted through 15.15's committed harness protocol on its fixed eval seed config (the harness consumed read-only — asserted by the report naming the harness entrypoint + seed-config artifact it invoked), plus the reproducibility story: N seeded repeats with the spread of validity/referee/fitness/win-rate (no single-run claims).
- [ ] Distillability measured: a pure-Python student cloned from the torch policy, with student-teacher intent agreement and the student's own tuple row reported.
- [ ] `pyproject.toml` mypy exclude covers the probe dir; `uv run mypy .` is green WITHOUT torch installed; the test pins that no production package imports the probe.
- [ ] The report ends with a promotion recommendation for the pause — promote / keep experiment-tier / retire — priced against dependency weight, determinism doctrine, and the measured gain (or its absence), with wall-clock + hardware documented.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror the ml_spike posture: standalone scripts with `main()`, `sys.path` bootstrap acceptable, excluded
from strict typing, run by the operator with `uv run --with torch python experiments/lab/torch_probe/…`.
Masked action selection (the 15.8 mask) is mandatory — an unmasked PPO burns its budget on illegal
actions. Recurrence is the point of the probe (the POMDP memory the encoder carries explicitly, a GRU
carries latently) — if recurrent PPO cannot beat the utility-scorer+ES entrant on the same features,
that is a clean, valuable NO for torch promotion. Keep the run budget honest and documented; $0, local
CPU (or the operator's own GPU, documented).

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
Open a PR from branch `phase-15-torch-probe` with a title like `task 15.17: the torch ppo+recurrent probe (experiment-tier, opt-in)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-training-signal.md §9 (the staged-escalation dependency posture); audits/post-phase-14-ML-planning.md §9 Option 3 (PPO/recurrent: strongest asymptotics, heavy costs); owner decision 2026-07-05 (torch as probe only; promotion is a pause decision)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
