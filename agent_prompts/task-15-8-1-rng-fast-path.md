# Agent Prompt — 15.8.1 Training-only RNG hash fast path (opt-in; committed paths byte-unchanged)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.8.1 — Training-only RNG hash fast path (opt-in; committed paths byte-unchanged), anchored to audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-rng-fast-path`
**Depends on:** 15.8, 15.9
**Section refs:** audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization)
**Complexity:** Medium

`engine/rng.py` re-serializes the full 625-int Mersenne state via `json.dumps` on every tick (~43% of
bare-engine cost) and the drawn value is discarded — but that serialization is hashed into every
committed `state_hash`, so it is load-bearing for replay byte-identity and must NEVER be changed in
place. This task adds an explicit, opt-in hash policy (a typed policy object threaded `HeadlessGame →
engine`, no env-var magic) that skips the per-tick rng-state serialization for non-recorded training
rollouts only. Two enabling facts make the scope wider than `engine/rng.py` alone: (a) the per-tick
snapshot is INVOKED from `engine.tick.advance_tick` (the `EngineRng.from_state(...).randint(...)` draw
that writes `next_rng_state`), so the policy threads through `engine/tick.py` — in scope, with the
default path pinned byte-identical there; and (b) `HeadlessGame` today REQUIRES a `replay_path` and
constructs a `ReplayLog` unconditionally, which would make "non-recorded rollouts" unreachable — so
this task also adds an explicit NO-REPLAY training mode (`replay_path=None` → no `ReplayLog`, nothing
written), which is the only construction that accepts the fast-path policy; any replay-writing
construction refuses it loudly, and a no-replay construction that receives 15.9's
`tactical_policy_stamp` also raises (a stamp with nothing to record it is a caller bug). This task
edits the SAME `HeadlessGame` constructor 15.9 stamps — the 15.9 dependency edge serializes the two,
so rebase on the stamped signature. The RNG draws themselves are untouched — trajectories are identical
under both modes, so training results transfer to the recording path exactly.

**Files in scope:**
- engine/rng.py (the opt-in fast-path region; default behavior byte-identical)
- engine/tick.py (the per-tick rng-snapshot invocation region — policy-aware, default byte-identical)
- orchestrator/game.py (rng-hash policy plumbing + optional no-replay training-mode region — disjoint from 15.4's registry/protocol regions and 15.5's vote entry; shares the `HeadlessGame` constructor with 15.9's stamp kwarg, serialized by this task's dependency edge on 15.9)
- training/env.py (fast-path + no-replay knob region — 15.8 owns the rest of the module)
- tests/engine/test_rng_fast_path.py (new)
- tests/training/test_env_fast_path.py (new)
- tests/orchestrator/test_no_replay_mode.py (new)

**Files NOT in scope:**
- orchestrator/replay.py + api/replay_loader.py (recording/verification never accepts the fast path — refusal at construction, not silent downgrade)
- scripts/_verify_samples.py (unchanged; committed samples must keep verifying)
- replays/samples/ (untouched)

**Definition of done:**
- [ ] Default path byte-identical: `bash scripts/verify_samples.sh` reconstructs all 100 committed samples clean with the change merged.
- [ ] Fast path measurably faster: the engine-core speedup ratio is measured and documented (target ≥1.3×; report the actual).
- [ ] The no-replay training mode is real: `replay_path=None` constructs a game that writes NOTHING to disk (asserted), runs to completion, and is the ONLY construction that accepts the fast-path policy; every replay-writing construction with the fast path active raises a descriptive error (tested); a no-replay construction combined with 15.9's `tactical_policy_stamp` raises (tested); the training env exposes both knobs and defaults them OFF.
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
mode from the environment. The state-hash serializer in `orchestrator/replay.py` is not edited — the
fast path simply never reaches it, because recording refuses the policy up front.

## Public types this task introduces
- `engine.rng.RngStateHashPolicy`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import training.env"`
- `uv run python -c "import training.rollout"`
- `uv run python -c "import training.rewards"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import meetings.schemas"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.
- Re-verify every file:line anchor the contract cites at HEAD before editing; if an anchor has moved, record the true location under `## Decisions` — never edit from a stale line number.
- Grep every consumer of each symbol, path, or constant you will change (the blast radius); if a hit lies outside the files in scope, stop and ask rather than widening scope silently.

## Craft rules (AGENTS.md "Craft rules" — non-negotiable for every file you touch)
- Lead with intent: a docstring or comment states what the code does and why, now; provenance (task ids, audit paths) is at most one trailing line. Do not narrate history in source.
- A gate must be able to fail: every new test or check that guards an invariant ships with a planted or perturbed case proving it bites, and checks the semantics it claims, not only the shape.
- Retire means delete: when a lever graduates or a branch dies, delete the resolver, the parameter, the branch and the tests that pin them; keep only the stamp key and one history line.
- No internal dialect on user-facing surfaces: UI copy, rendered game prompts, spoken text and README carry no task or audit ids, no threshold arithmetic, and no undefined jargon.
- Claims are verifiable-shaped: a doc claim names the mechanism that enforces it; a number is recomputed from committed bytes and its command goes in the PR.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- If the contract carries a `**Measurement:**` field, run that command and paste its output into the PR's `## Summary`; a Measurement that cannot be run is reported under `## Questions`, never asserted.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-15-rng-fast-path` with a title like `task 15.8.1: training-only rng hash fast path (opt-in; committed paths byte-unchanged)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §3.5, §11.2 (the 43% measurement + the training-only scoping); audits/post-phase-14-pause.md §4 (the "do not touch in place" verifier note); engine/rng.py:31-38; orchestrator/replay.py (state-hash serialization)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
