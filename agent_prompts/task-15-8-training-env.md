# Agent Prompt — 15.8 The `training/` package: rollout env, legal-action mask, reward channel (numpy lands here)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.8 — The `training/` package: rollout env, legal-action mask, reward channel (numpy lands here), anchored to audits/post-phase-14-ML-planning.md §5, §7, §11 (action space, injection seam, env wrapper); orchestrator/game.py (AgentFactory :93, HeadlessGame :1121, MeetingAwareAgent :425-450); experiments/lab/ml_spike/core.py (the SpikeAgent interposition pattern :148-200); engine/rules.py + engine/tick.py (the legality predicates); engine/events.py (the reward-source event types). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-training-env`
**Depends on:** none
**Section refs:** audits/post-phase-14-ML-planning.md §5, §7, §11 (action space, injection seam, env wrapper); orchestrator/game.py (AgentFactory :93, HeadlessGame :1121, MeetingAwareAgent :425-450); experiments/lab/ml_spike/core.py (the SpikeAgent interposition pattern :148-200); engine/rules.py + engine/tick.py (the legality predicates); engine/events.py (the reward-source event types)
**Complexity:** Integration

Create the new top-level `training/` package (strict-typed from day one — no mypy exclusion) holding the
rollout environment every trainer in this phase rides. `TacticalRolloutEnv` drives the REAL production
loop — `HeadlessGame` with an injected `AgentFactory` built on the proven interposition pattern (wrap
the real `TacticalAgent`, override the chosen intent, delegate the full meeting protocol via
`__getattr__` — port the ml_spike pattern into typed code, do NOT import the mypy-excluded spike) —
never a bespoke "training game." Three capabilities: (1) a **legal-action mask** over the option/intent
space, derived from the pure legality predicates in `engine/rules.py`/`engine/tick.py`, with the two
documented caveats handled explicitly — emergency-uses-remaining and the map's sabotage kinds are NOT in
the observation surface, so the mask carries small policy-side trackers (the `EmergencyPacingTracker`
precedent) rather than widening the packet; and the mask distinguishes ENGINE-LEGAL resolved actions
from OBSERVATION-MEANINGFUL submissions, keeping the impostor's pretend `do_task` (engine-rejected,
rendered as `action="task"` camouflage to witnesses — 396 such submissions in the committed baseline-2
9p2i stream) in the impostor's submission vocabulary; (2) a **potential-based reward channel** exposing
the side-specific tactically-reachable terms from the typed event log (kills, witnessed-ness via
`Killed.witnesses`, task progress, survival, report/coverage events) so trainers never re-derive rewards
from replay bytes; (3) **per-episode rollout records** carrying the behavioral descriptors the QD
entrant and the pause audit need (kill-timing distribution, witness-exposure rate, vent usage,
meeting-trigger rate, do_task-emission cadence, win shape). `uv add numpy` (exact pin) lands in this
task, confined to `training/` by a new import-linter contract (`agents` must not import `training`) with
`training` added to the linter's root packages.

**Files in scope:**
- training/__init__.py (new)
- training/env.py (new: `TacticalRolloutEnv`, the interposition factory, the mask)
- training/rewards.py (new: potential-based shaping + side-specific reward terms)
- training/rollout.py (new: episode records + behavioral descriptors)
- pyproject.toml (project dependencies region — the numpy exact pin; the mypy exclude regex is 15.17's disjoint region)
- uv.lock (numpy resolution)
- .importlinter (training root + agents-must-not-import-training contract region)
- tests/training/__init__.py (new)
- tests/training/test_env.py (new)
- tests/training/test_rewards.py (new)
- tests/training/test_rollout.py (new)

**Files NOT in scope:**
- orchestrator/game.py (the seams already exist; zero orchestrator edits)
- engine/ (read-only; the RNG fast path is 15.8.1)
- agents/ (the encoder is 15.10; the FSMs are the anchor and stay untouched)
- experiments/lab/ml_spike/ (frozen reference — port, never import)
- eval/balance_eval.py (the surrogate-runner keyword is 15.13's)

**Definition of done:**
- [ ] The env runs full fake-provider games through an injected factory at or above the measured floor (≥5 games/s at 9p2i on the check host; the actual figure is documented in the module docstring).
- [ ] A meeting runner is ALWAYS installed: `meeting_runner=None` truncation (`MEETING_PHASE_REACHED`) is structurally unreachable from the env, asserted by test — truncation is never a fitness path.
- [ ] Mask legality is property-tested against the engine: across randomized seeds/ticks, every masked-legal engine action resolves without rejection and every unmasked action is engine-rejected — with the pretend-`do_task` camouflage carried in the impostor SUBMISSION set and excluded from the engine-legal set (both asserted).
- [ ] The reward channel is potential-based: a telescoping test shows shaping sums to Φ(terminal) − Φ(initial) over any episode, so shaping cannot change the optimal policy.
- [ ] A frozen-policy episode is byte-deterministic: same seed → identical per-tick state-hash sequence across two runs (the spike's check-1 reproduced inside the committed package).
- [ ] numpy imports are confined to `training/`: `uv run lint-imports` keeps every existing contract AND the new `agents ↛ training` contract; `training` is in root_packages.
- [ ] Episode records carry all named behavioral descriptors; a fixture pins their values on a scripted game.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

`HeadlessGame(seed=…, game_map=…, agent_factory=…, replay_path=…, meeting_runner=…)` is the whole wiring
surface (`orchestrator/game.py:1124-1163`); `max_ticks` rides the `TickScheduler`, not the constructor.
The wrapper agent must satisfy the FULL `MeetingAwareAgent` protocol (both properties + both render
methods — isinstance-checked at `game.py:863` before meetings build participants); wrapping the real
`TacticalAgent` and delegating via `__getattr__` gets all of it for free, plus the crew-only
`EmergencyPacingTracker` bookkeeping. Mask derivation: every legality predicate is a pure boolean of
`(state, map, actor)` with zero RNG — mirror them agent-side from the packet + trackers rather than
importing engine (the firewall forbids `agents → engine`, and `training/` should reach engine truth only
through the orchestrator loop). Default meeting runner for rollouts is `build_default_meeting_runner` on
the fake provider (`tests/conftest.py` pins `AILIBI_LLM_PROVIDER=fake` for all tests); the surrogate
slots in via the same parameter once 15.13 lands.

## Public types this task introduces
- `training.env.TacticalRolloutEnv`
- `training.env.ActionMask`
- `training.rollout.EpisodeRollout`
- `training.rewards.ShapedReward`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This is the seam every trainer rides; the failure mode is DRIFT from the production loop — a bespoke
training game would silently invalidate every fitness number and every determinism claim downstream. The
env must be the real `HeadlessGame`, the real observation firewall, the real meeting manager, with the
ONLY interposition at the factory. Second risk: numpy — BLAS reductions are not bit-stable across
machines/thread counts, which is exactly why numpy stays training-side and the production inference path
(15.10, Wave 2) stays pure-Python; the import-linter contract is the enforcement, not a convention.
Third: the mask must not delete the pretend-`do_task` camouflage lever — a strict engine-legal-only
vocabulary regresses the impostor's task-traffic mimicry, which is measured behavior on the committed
baseline.

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
Open a PR from branch `phase-15-training-env` with a title like `task 15.8: the `training/` package: rollout env, legal-action mask, reward channel (numpy lands here)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §5, §7, §11 (action space, injection seam, env wrapper); orchestrator/game.py (AgentFactory :93, HeadlessGame :1121, MeetingAwareAgent :425-450); experiments/lab/ml_spike/core.py (the SpikeAgent interposition pattern :148-200); engine/rules.py + engine/tick.py (the legality predicates); engine/events.py (the reward-source event types)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
