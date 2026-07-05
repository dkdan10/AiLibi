# Agent Prompt — 15.9 Tactical-policy provenance stamp (replay writer + MANIFEST + loader guard)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-15.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 15.9 — Tactical-policy provenance stamp (replay writer + MANIFEST + loader guard), anchored to audits/post-phase-14-ML-planning.md §7.2-7.3 (record-actions provenance; the stamp recommendation); orchestrator/replay.py (substrate_flag_snapshot :277-299, game_over stamping :434-441); api/replay_loader.py (the substrate mismatch guard :377-423); scripts/_manifest_writer.py. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-15.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-15-policy-provenance`
**Depends on:** none
**Section refs:** audits/post-phase-14-ML-planning.md §7.2-7.3 (record-actions provenance; the stamp recommendation); orchestrator/replay.py (substrate_flag_snapshot :277-299, game_over stamping :434-441); api/replay_loader.py (the substrate mismatch guard :377-423); scripts/_manifest_writer.py
**Complexity:** Integration

Answer "which tactical policy produced these bytes" the same way the repo already answers "which
substrate levers": a provenance stamp, mirrored across the three provenance surfaces.
`orchestrator/replay.py` stamps a `tactical_policy` block into the `game_over` entry — `{policy_id,
method, encoder_version, weights_sha256, anchor_policy}` (plain strings; no import of any training code)
— exactly beside the existing `substrate_flags` stamp; `scripts/_manifest_writer.py` adds a policy
column so every recorded set's MANIFEST attributes each seed; `api/replay_loader.py` gains a mismatch
guard mirroring `ReplaySubstrateMismatchError` that refuses to serve a stamped replay under a
conflicting policy claim. An ABSENT stamp means "scripted FSM default" and stays fully valid — the
committed canonical sets are untouched and must keep loading, byte-verifying, and serving with zero
edits (this holds across the 15.7 re-record: baseline 3 is recorded with the FSM default and may carry
the explicit stamp if this task lands first, or none — both are valid). Replay reconstruction re-feeds
recorded actions and never re-invokes a policy, so the stamp is provenance, not a replay input — this is
what keeps learned-policy replays byte-identical regardless of inference-float questions.

**Files in scope:**
- orchestrator/replay.py (tactical-policy stamp region, alongside the substrate-flags stamp — disjoint from 15.5's registration region and 15.7's graduation region)
- api/replay_loader.py (policy-stamp read + mismatch guard region)
- scripts/_manifest_writer.py (policy column)
- tests/orchestrator/test_replay_policy_stamp.py (new)
- tests/api/test_replay_loader_policy_stamp.py (new)
- tests/scripts/test_manifest_writer.py (extend: FSM-default rendering pinned)

**Files NOT in scope:**
- replays/samples/ (committed bytes untouched; absent stamp = FSM default)
- orchestrator/game.py + agents/ + training/ (no coupling: the stamp is strings, set by the recorder)
- scripts/refresh_samples.sh (the canonical-sample refresh flow is frozen; the corpus recorder 15.12 consumes the stamp)

**Definition of done:**
- [ ] The committed canonical sets load, byte-verify (`bash scripts/verify_samples.sh` clean), and serve with zero edits — absent stamp renders as the FSM default everywhere.
- [ ] A stamped recording round-trips writer → loader with all five fields intact; the stamp appears in the game_over entry beside `substrate_flags`.
- [ ] A deliberately mismatched stamp raises the new loader guard (fail-loud, mirroring the substrate guard's shape and error quality).
- [ ] The MANIFEST writer emits the policy column; existing manifest tests pin the FSM-default rendering for unstamped rows.
- [ ] The stamp schema is documented (module docstring) for 15.12 (corpus rows stamp the FSM default explicitly) and Wave 2 (champion weights hash).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Clone the substrate-flags pattern end to end: `substrate_flag_snapshot()` → the game_over stamp
(`orchestrator/replay.py:277-299`, `:434-441`) → the loader's `_assert_substrate_matches` guard
(`api/replay_loader.py:377-423`). The stamp is additive JSON in an existing entry — the risk surface is
serialization order/shape perturbing committed hashes, so add fields in a way the state-hash serializer
never sees (the state hash covers `WorldState`, not replay-entry metadata — verify with the
byte-identity suite, not by assumption).

## Public types this task introduces
- `orchestrator.replay.TacticalPolicyStamp`
- `api.replay_loader.ReplayPolicyMismatchError`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

The whole task is byte-compatibility: the committed samples are the regression fixture, and
`verify_samples.sh` green under a bare environment is the non-negotiable proof. Second risk: schema
creep — the stamp must stay plain strings so `orchestrator/` never imports training or agents code
(keeping the dependency direction clean for the import-linter contracts added this phase).

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
Open a PR from branch `phase-15-policy-provenance` with a title like `task 15.9: tactical-policy provenance stamp (replay writer + manifest + loader guard)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/post-phase-14-ML-planning.md §7.2-7.3 (record-actions provenance; the stamp recommendation); orchestrator/replay.py (substrate_flag_snapshot :277-299, game_over stamping :434-441); api/replay_loader.py (the substrate mismatch guard :377-423); scripts/_manifest_writer.py), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
