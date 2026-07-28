# Agent Prompt — 18.32 The crew re-rank arm: crew candidates, frozen-opponent seam, dual stamps

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.32 — The crew re-rank arm: crew candidates, frozen-opponent seam, dual stamps, anchored to training/realpath.py (`RealPathCandidate`, `_build_agent_factory`, `_verify_stamps` — the impostor-only surfaces this task widens); training/coevo/factory.py (`build_coevo_factory` + the 18.19 conflation guard, consumed not edited); scripts/run_tournament.py (`--crew-artifact` — the dual-stamp semantics this task mirrors, NOT edited); orchestrator/replay.py (`CrewTacticalPolicyStamp`). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-crew-rerank-arm`
**Depends on:** 18.31
**Section refs:** training/realpath.py (`RealPathCandidate`, `_build_agent_factory`, `_verify_stamps` — the impostor-only surfaces this task widens); training/coevo/factory.py (`build_coevo_factory` + the 18.19 conflation guard, consumed not edited); scripts/run_tournament.py (`--crew-artifact` — the dual-stamp semantics this task mirrors, NOT edited); orchestrator/replay.py (`CrewTacticalPolicyStamp`)
**Complexity:** Integration

The routed amendment 18.25's leg discipline demands (owner-ratified 2026-07-28, the
Amend + overlap ruling): the 18.25 contract requires per-generation real-path re-ranks
whose recordings are the first dual-stamped crew recordings, with ranking rows, native
leg-logs, resume, and tranche claims — but `run_realpath_rerank` was impostor-only end
to end, and the only committed dual-stamp recorder (`run_tournament.py --crew-artifact`)
produces none of that machinery. Six additions, all refuse-direction:
(1) crew candidate families — `RealPathCandidate` accepts `crew-option-features-v1` and
`crew-option-features-v2`; `hidden` refused for them (scorer family). (2) Factory
dispatch — crew families build through `build_crew_scorer` (basis per family) wrapped in
`build_coevo_factory`; the 18.19 conflation guard holds both directions at candidate
preflight, before any spend. (3) The frozen-opponent seam — keyword-only
`opponent_artifact` on `run_realpath_rerank`: a four-file loadable impostor artifact,
loaded + sha-verified + stamp-read before any spend, installed in the impostor slot for
EVERY candidate in the leg; a crew-family opponent refuses; an opponent with
impostor-family candidates refuses — legs stay homogeneous; None with crew candidates
records against the scripted FSM (the comparator cell); the opponent identity rides the
leg manifest, the leg-log `leg-start` event, and every row. (4) Dual-stamp verification
— the crew stamp is read back from bytes and verified sha == computed digest, with
crew-side verified/uniform/equals-computed row fields mirroring the impostor discipline;
row schema bumps `realpath-rerank-v2 → v3`, additive optional fields only, frozen
`-v1`/`-v2` history untouched. (5) Resume/drift — the protocol-drift check folds the
opponent identity and candidate families into the manifest comparison; a resumed leg
whose opponent or family moved refuses. (6) `scripts/generate_campaign_tables.py`
(`legs`, `stability`) accepts `-v3` beside `-v1`/`-v2`.

**Files in scope:**
- training/realpath.py (the crew arm: families, opponent seam, dual stamps, drift)
- training/coevo/hall_of_fame.py (the shared four-file artifact reader)
- scripts/generate_campaign_tables.py (v3 acceptance)
- tests/training/test_realpath.py + tests/training/test_hall_of_fame.py + tests/scripts/test_generate_campaign_tables.py (the arm's pins)

**Files NOT in scope:**
- training/coevo/driver.py + factory.py + rollout.py (consumed frozen)
- training/crew/ (consumed frozen)
- scripts/run_tournament.py (the finalist entry point stays the 18.26 invariant)
- training/artifacts/ (frozen history; committed recordings stay byte-identical)

**Definition of done:**
- [ ] A crew-candidate leg records end to end against a frozen-opponent artifact with both stamps verified (uniform, sha == computed digest per game), and each refusal path is fixture-pinned in both directions: crew hidden, crew-family opponent, opponent-with-impostor-candidates, missing/corrupt/sha-mismatched opponent artifact, resumed leg with a moved opponent.
- [ ] `realpath-rerank-v3` rows render through the table generator's `legs` and `stability` subcommands including mixed-version ranking sets, and impostor-only invocations keep their exact current row shape modulo the version string (the frozen `-v1`/`-v2` corpus reads unchanged).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The loader lives under training/ — lint-imports forbids training-imports-scripts, so the
`--crew-artifact` load semantics are mirrored from `run_tournament.py`, never imported.
Bias every ambiguity toward refusal: the false-accept direction in stamp verification
converts another campaign's bytes into this leg's evidence, which is the exact failure
class the 18.19 guards exist to kill. The opponent is leg-constant by design —
per-candidate opponents would make rows incomparable within one ranking.

## Public types this task introduces
- `training.coevo.hall_of_fame.read_loadable_artifact`
- `training.coevo.hall_of_fame.LoadableArtifact`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Integration risk

This library records 18.25's evidence within days of the merge; a defect lands directly
in the campaign's selection tables. Every existing realpath test must pass unchanged,
and the committed recordings and rankings under training/artifacts/coevo/ stay
byte-identical after the full suite.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.conviction.serving"`
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
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`

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
Open a PR from branch `phase-18-crew-rerank-arm` with a title like `task 18.32: the crew re-rank arm: crew candidates, frozen-opponent seam, dual stamps`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/realpath.py (`RealPathCandidate`, `_build_agent_factory`, `_verify_stamps` — the impostor-only surfaces this task widens); training/coevo/factory.py (`build_coevo_factory` + the 18.19 conflation guard, consumed not edited); scripts/run_tournament.py (`--crew-artifact` — the dual-stamp semantics this task mirrors, NOT edited); orchestrator/replay.py (`CrewTacticalPolicyStamp`)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
