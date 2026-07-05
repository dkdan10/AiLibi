# Agent Prompt — 15.3.1 Training-only RNG hash fast path (opt-in; committed paths byte-unchanged)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.3.1 — Training-only RNG hash fast path (opt-in; committed paths byte-unchanged), anchored to audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-rng-fast-path`
**Depends on:** 15.3
**Section refs:** audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization)
**Complexity:** Medium

`engine/rng.py` re-serializes the full 625-int Mersenne state via `json.dumps` on every tick (~43% of
bare-engine cost) and the drawn value is discarded — but that serialization is hashed into every committed
`state_hash`, so it is load-bearing for replay byte-identity and must NEVER be changed in place. This task
adds an explicit, opt-in hash policy (a typed policy object threaded `HeadlessGame → engine`, no env-var
magic) that skips the per-tick rng-state serialization for non-recorded training rollouts only. The default
is byte-identical to today; anything that records or verifies a replay refuses the fast path loudly. The
RNG draws themselves are untouched — trajectories are identical under both modes, so training results
transfer to the recording path exactly.

**Files in scope:**
- engine/rng.py (the opt-in fast-path region; default behavior byte-identical)
- orchestrator/game.py (rng-hash policy plumbing region only)
- training/env.py (fast-path knob region — 15.3 owns the rest of the module)
- tests/engine/test_rng_fast_path.py (new)
- tests/training/test_env_fast_path.py (new)

**Files NOT in scope:**
- orchestrator/replay.py + api/replay_loader.py (recording/verification never accepts the fast path — refusal at construction, not silent downgrade)
- scripts/_verify_samples.py (unchanged; committed samples must keep verifying)
- replays/samples/ (untouched)

**Definition of done:**
- [ ] Default path byte-identical: `bash scripts/verify_samples.sh` reconstructs all 100 committed samples clean with the change merged.
- [ ] Fast path measurably faster: the engine-core speedup ratio is measured and documented (target ≥1.3×; report the actual).
- [ ] Constructing a recording/replay-writing game with the fast path active raises a descriptive error (tested); the training env exposes the knob and defaults it OFF.
- [ ] Trajectory equivalence proven: for a frozen policy on a fixed seed set, the full action/event streams are IDENTICAL under both modes (only hashing cost differs), asserted by test.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The loosening the owner approved is exactly this shape: skip the `json.dumps` snapshot of the Mersenne
state per tick, never the draws. Keep the policy object explicit in signatures (the repo's no-silent-
fallbacks doctrine): a recording constructor that receives a fast-path policy raises; nothing infers the
mode from the environment. The state-hash serializer in `orchestrator/replay.py` is not edited — the fast
path simply never reaches it, because recording refuses the policy up front.

## Public types this task introduces
- `engine.rng.RngStateHashPolicy`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`

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
Open a PR from branch `phase-15-rng-fast-path` with a title like `task 15.3.1: training-only rng hash fast path (opt-in; committed paths byte-unchanged)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
