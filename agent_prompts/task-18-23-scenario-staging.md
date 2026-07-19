# Agent Prompt — 18.23 Scenario staging: state injection + the skill-scenario library

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.23 — Scenario staging: state injection + the skill-scenario library, anchored to audits/audit-phase-18-planning.md §4 (#12) + the dive findings (both entry points hardwire `seed_initial_state` — orchestrator/game.py:1508-1514, 1570 (post-18.7 anchors); `WorldState` hand-construction precedent at tests/training/test_env.py:531-543; dense terms score truncated episodes — training/rewards.py:250-256); orchestrator/seeder.py:29-133. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-scenario-staging`
**Depends on:** 18.16, 18.21, 18.22
**Section refs:** audits/audit-phase-18-planning.md §4 (#12) + the dive findings (both entry points hardwire `seed_initial_state` — orchestrator/game.py:1508-1514, 1570 (post-18.7 anchors); `WorldState` hand-construction precedent at tests/training/test_env.py:531-543; dense terms score truncated episodes — training/rewards.py:250-256); orchestrator/seeder.py:29-133
**Complexity:** Integration

The training-grounds instrument: an `initial_state` injection seam on the headless game
(bypassing `seed_initial_state`, with the rng-snapshot discipline that keeps injected
episodes deterministic and hash-coherent), and a scenario library of constructed mid-game
skill situations with per-scenario dense fitness from tactical facts only — first four:
kill-with-witness-nearby-then-survive-the-meeting, vent-unseen-under-patrol,
force-parity-endgame, body-discovery-latency. Scenario episodes are truncated by
construction and score through the dense terms (never `compute_shaped_reward`'s terminal
gate); scenarios feed FITNESS pressure, and the standing gates/referee never move. The
campaign consumes scenarios ONLY through 18.21's additive scenario-provider seam — this
task implements a provider conforming to that seam (no driver edit); watchability
quantities never appear in scenario fitness.

**Files in scope:**
- orchestrator/game.py; (the additive `initial_state` seam)
- training/env.py (the env-side plumbing + no-replay path integration)
- training/scenarios.py (new: builders + per-scenario fitness)
- tests/training/test_scenarios.py + tests/training/test_env.py (the seam's determinism + hash-coherence fixtures)

**Files NOT in scope:**
- orchestrator/seeder.py (bypassed, never edited)
- training/rewards.py (dense terms consumed as-is)
- engine/ (already accepts any valid state)

**Definition of done:**
- [ ] An injected-state episode runs deterministically (same scenario + seed ⇒ identical digest twice), its rng snapshot is canonical, and the default seeded path is byte-identical everywhere with the seam unused (pinned across the replay/recording suites).
- [ ] All four scenarios construct valid states (engine-accepted, hash-coherent), each with a documented fitness definition from tactical facts, and a miniature ES leg on one scenario runs end-to-end in tests.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The injection must ride the no-replay live-assembly path (reconstruction verifies recorded
hashes an injected episode does not have). Scenario states set `rng_state` to a canonical
`EngineRng.from_seed(...)` snapshot; `advance_tick` is then a pure function and the
determinism story is inherited, not re-invented.

## Public types this task introduces
- `training.scenarios.ScenarioSpec`
- `training.scenarios.build_scenario_state`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

`orchestrator/game.py` is the most byte-adjacent file in the tree; the seam must be
provably inert when unused (the full replay/recording byte-identity suites are the gate —
run them before and after). Scenario fitness definitions are the Goodhart-adjacent part:
each must name what it deliberately does NOT reward (e.g. discovery-latency must not reward
meeting suppression — the FO-2 lesson).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.tactical.features"`
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
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`

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
Open a PR from branch `phase-18-scenario-staging` with a title like `task 18.23: scenario staging: state injection + the skill-scenario library`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#12) + the dive findings (both entry points hardwire `seed_initial_state` — orchestrator/game.py:1508-1514, 1570 (post-18.7 anchors); `WorldState` hand-construction precedent at tests/training/test_env.py:531-543; dense terms score truncated episodes — training/rewards.py:250-256); orchestrator/seeder.py:29-133), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
