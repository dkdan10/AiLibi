# Agent Prompt — 18.19 Dual-role co-evo rollout + the two-identity stamp

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.19 — Dual-role co-evo rollout + the two-identity stamp, anchored to audits/audit-phase-18-planning.md §4 (#8) + the dive finding it cites (`rollout_candidate` hardwires the opposing side to the scripted FSM — harness.py:564-565, 630-636; scorer.py:850-857); training/bakeoff/harness.py:357-388 (`BakeoffPolicy`, the shared shape); orchestrator/replay.py (the stamp schema the crew stamp extends). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-coevo-rollout`
**Depends on:** 18.7, 18.16
**Section refs:** audits/audit-phase-18-planning.md §4 (#8) + the dive finding it cites (`rollout_candidate` hardwires the opposing side to the scripted FSM — harness.py:564-565, 630-636; scorer.py:850-857); training/bakeoff/harness.py:357-388 (`BakeoffPolicy`, the shared shape); orchestrator/replay.py (the stamp schema the crew stamp extends)
**Complexity:** Integration

The seam co-evolution has never had: a role-dispatching rollout in which EACH side is
independently the scripted FSM, a live candidate, or a frozen learned artifact — and an
honest two-identity provenance story: an additive crew-policy stamp beside the existing
`tactical_policy` stamp on recorded games, each read back from bytes, sha-verified, never
conflated. `rollout_coevo` scores both sides' fitness from one rollout (both reward sides
exist already); the recording path extends `scripts/run_tournament.py` with a
`--crew-artifact` arm mirroring `--candidate-artifact`, mutual-exclusion-guarded against
the single-side flags.

**Files in scope:**
- training/coevo/__init__.py + training/coevo/factory.py + training/coevo/rollout.py (new)
- orchestrator/replay.py; (the dual-stamp read-back coherence over 18.7's `CrewTacticalPolicyStamp` — games with zero, one, or two stamps round-trip; the schema field itself landed at 18.7)
- scripts/run_tournament.py; (the `--crew-artifact` arm + dual-stamp wiring)
- tests/training/test_coevo_rollout.py + tests/scripts/test_run_tournament_candidate_artifact.py (the dual-stamp guards)

**Files NOT in scope:**
- training/bakeoff/harness.py; (its wrappers are imported/mirrored, never rewired — the single-side paths stay byte-identical)
- agents/tactical/learned/; (18.7 shipped the surface; consumed here)

**Definition of done:**
- [ ] A rollout with learned policies on BOTH sides runs deterministically on the fake path, yields both sides' fitness from one trace, and a recorded eval carries both stamps read back from bytes with distinct sha-verified identities; every single-side path (existing flags, no factory) is byte-identical to before (pinned).
- [ ] Conflation is structurally impossible: a crew artifact in the impostor slot (or vice versa) fails loud before any game runs, fixture-pinned; the stamp reader round-trips games with zero, one, or two stamps.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Both existing wrappers (`_CandidateAgent`, `_CrewCandidateAgent`) already share the
`BakeoffPolicy` evaluate shape — the dual factory is a role branch over two of them, not a
new agent class. The stamp extension is additive on the replay schema (a game with no crew
stamp parses exactly as before — the 15.9 compatibility discipline).

## Public types this task introduces
- `training.coevo.factory.build_coevo_factory`
- `training.coevo.rollout.rollout_coevo`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

`orchestrator/replay.py` is byte-adjacent to every committed set: the additive field must
leave all committed replays parsing byte-identically (round-trip pins over the samples +
corpus). The CLI arm compounds with 17.14's guards — extend its test file rather than
forking a second guard suite.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-18-coevo-rollout` with a title like `task 18.19: dual-role co-evo rollout + the two-identity stamp`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §4 (#8) + the dive finding it cites (`rollout_candidate` hardwires the opposing side to the scripted FSM — harness.py:564-565, 630-636; scorer.py:850-857); training/bakeoff/harness.py:357-388 (`BakeoffPolicy`, the shared shape); orchestrator/replay.py (the stamp schema the crew stamp extends)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
