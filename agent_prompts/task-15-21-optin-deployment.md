# Agent Prompt — 15.21 Deployment, branch A: the opt-in learned factory across the recording/eval surfaces

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.21 — Deployment, branch A: the opt-in learned factory across the recording/eval surfaces, anchored to audits/audit-phase-15-pause.md decision 2 (branch A locked; branch B's rejection rationale) + the finalist recipe (the seam this task turns into a CLI); orchestrator/game.py (the `agent_factory` seam); scripts/run_tournament.py (the stamp flag that today has no factory counterpart); tasks/phase-15.md 15.9 (the provenance stamp this task auto-wires). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-optin-deployment`
**Depends on:** 15.19, 15.20
**Section refs:** audits/audit-phase-15-pause.md decision 2 (branch A locked; branch B's rejection rationale) + the finalist recipe (the seam this task turns into a CLI); orchestrator/game.py (the `agent_factory` seam); scripts/run_tournament.py (the stamp flag that today has no factory counterpart); tasks/phase-15.md 15.9 (the provenance stamp this task auto-wires)
**Complexity:** Medium

Make the champion selectable without a Python driver — the deployment end-state decision 2 locked:
opt-in, fully reversible, `replays/samples/` byte-untouched. `scripts/run_tournament.py` gains an
`--agent-factory {fsm-default,learned-champion}` flag (default `fsm-default`, byte-identical behavior
when absent): `learned-champion` builds `agents.tactical.learned.factory.build_learned_agent_factory()`
and AUTO-STAMPS the recording with the factory's own five-field stamp — the flag pair
(`--agent-factory learned-champion` + an explicit contradicting `--tactical-policy-stamp`) is rejected
loudly, so a learned recording can never carry an FSM label or vice versa (the 15.18 finalist-eval
proof, `stamp.weights_sha256 == committed sidecar`, becomes impossible to forget). `run_tournament_eval`
itself is unchanged (the seam already exists); this is CLI plumbing + the mis-stamp guard + tests. The
spectator path needs no change: recordings carry the stamp, `api/replay_loader.py`'s 15.9 policy guard
already distinguishes them, and the canonical samples stay FSM-stamped and byte-identical.

**Files in scope:**
- scripts/run_tournament.py (the `--agent-factory` flag, the auto-stamp wiring, the contradiction guard)
- tests/scripts/test_run_tournament_agent_factory.py (new: flag default byte-identity, auto-stamp correctness, contradiction rejection)

**Files NOT in scope:**
- eval/balance_eval.py (the `agent_factory` kwarg already exists — no seam change)
- agents/tactical/learned/ (15.20's artifact, consumed as-is)
- replays/samples/ + replays/ml_corpus/ (byte-untouched — the whole point of branch A)
- api/ (the 15.9 policy guard already serves stamped recordings)

**Definition of done:**
- [ ] `scripts/run_tournament.py` without the flag is byte-identical in behavior to today (default `fsm-default`; a test pins the parse + the default factory path).
- [ ] `--agent-factory learned-champion` records games whose read-back stamp (via `orchestrator.replay.read_tactical_policy_stamp`) equals the learned factory's stamp with `weights_sha256` equal to the committed sidecar digest — asserted from recorded bytes in a fake-provider test recording, never from the launch config.
- [ ] Passing `--agent-factory learned-champion` together with a contradicting `--tactical-policy-stamp` exits non-zero with a named error; `fsm-default` plus the explicit FSM stamp remains accepted (back-compat).
- [ ] The module docstring records the decision-2 posture: opt-in beside the FSM default, samples untouched, default flip re-evaluated at close/Phase 17 behind the hardened referee + a corpus-scale companion record (the Q3 corollary).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror the `--tactical-policy-stamp` flag's plumbing one block below it. The factory choice maps to a
tiny registry dict `{"fsm-default": build_default_agent_factory, "learned-champion":
build_learned_agent_factory}` resolved at parse time; the auto-stamp reads the learned factory's stamp
accessor (15.20's DoD guarantees it matches the sidecar) so this task never hard-codes a sha. The
contradiction guard compares the resolved stamp against an explicitly-passed one field-by-field and
names the differing field in the error.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import agents.tactical.learned.forward"`
- `uv run python -c "import agents.tactical.learned.factory"`
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
Open a PR from branch `phase-15-optin-deployment` with a title like `task 15.21: deployment, branch a: the opt-in learned factory across the recording/eval surfaces`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-15-pause.md decision 2 (branch A locked; branch B's rejection rationale) + the finalist recipe (the seam this task turns into a CLI); orchestrator/game.py (the `agent_factory` seam); scripts/run_tournament.py (the stamp flag that today has no factory counterpart); tasks/phase-15.md 15.9 (the provenance stamp this task auto-wires)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
