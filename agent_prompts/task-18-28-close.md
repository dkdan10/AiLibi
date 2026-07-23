# Agent Prompt — 18.28 The mover record + the phase close (operator + owner, $0)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.28 — The mover record + the phase close (operator + owner, $0), anchored to tasks/phase-17.md 17.17 + audits/audit-phase-17-close.md (the close shape, both paths); the 18.12 record audit (the canary pre-registration source); tasks/post-phase-14-plan.md (the roadmap spine this close annotates). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-close`
**Depends on:** 18.23, 18.27, 18.29
**Section refs:** tasks/phase-17.md 17.17 + audits/audit-phase-17-close.md (the close shape, both paths); the 18.12 record audit (the canary pre-registration source); tasks/post-phase-14-plan.md (the roadmap spine this close annotates)
**Complexity:** Integration

The close, on whichever path 18.27 ruled. FLIP ⇒ record the mover baseline (baseline 7; or
6 under the NONE surgery) with the §0 pre-registered canary bands from the standing corpus
anchors, floors pinned from the record, the full instrument battery, ~6 h operator. NO-FLIP
⇒ no record, the battery re-run over existing bytes at HEAD (the 17.17 shape). Either way:
the close audit (findings-not-failures — the campaign findings, the emergence rulings, the
staleness rules for whatever Phase 19 inherits, routed contracts for anything deferred),
the banner/README/roadmap updates in the same PR, `compute_next_task.py --phase 18`
demonstrated complete, and the Q5 provenance arms stated honestly.

**Files in scope:**
- audits/audit-phase-18-close.md (new)
- replays/samples/; (FLIP path only: the mover record)
- eval/watchability.py; (FLIP path only: the mover baseline's floor block)
- orchestrator/game.py; (FLIP path only: `build_default_agent_factory` selects the productized champion — the default-selector graduation this record adopts)
- scripts/run_tournament.py; (FLIP path only: the default path follows the flipped factory)
- tests/scripts/test_champion_flip_ruling.py; (FLIP: the default-provably-flipped re-pins; NO-FLIP: re-run green unchanged)
- tasks/phase-18.md; (STATUS banner) + tasks/post-phase-14-plan.md (the spine annotation) + README.md (project status)
- tests/ (byte-coupled re-pins on the FLIP path; ruling pins re-run either way)

**Files NOT in scope:**
- training/ + agents/ (frozen at 18.27's ruling)
- replays/ml_corpus/ (a mover flip does not invalidate meeting-layer calibration data — the standing forward rule; champion-era caveat recorded)

**Definition of done:**
- [ ] The ruled path is executed exactly (record + gates + canaries pre-registered in §0 before the first seed, or the NO-record battery at HEAD), all four committed sets re-verified (validity 10/10, bare byte-identity), and the close audit quotes every number from committed artifacts via the committed CLIs.
- [ ] On the FLIP path the default-selector surfaces provably flip (every default-SELECTOR surface builds the productized champion; the absent-stamp fallback and opt-in surfaces stay coherent — the 17.16 pin suite inverted), and the record's bytes carry the champion stamp; on NO-FLIP the default provably does not move (pins re-run green).
- [ ] The banner, README, and roadmap record the close; the phase computes complete with the merged-title index; every deferred item is a named routed contract, never a silent gap.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 17.17 contract's "resist recording anything on the NO-FLIP path" discipline holds. One
outstanding re-anchor this close owns (the 18.13 verification flagged it): the canary-family
cells (R1 eject-decided share, the genuine-class successor, roll-call coverage,
whereabouts-lie mints, ejection accuracy, impostor win) were never re-anchored on the
restored baseline-6 corpus denominator — this close's §0 pre-registration derives its bands
from the baseline-6 corpus, computing the anchors fresh. The Phase-19 hand-off section
matters more than usual: Phase 19 is REVIEW-AND-REFRESH — the close audit should hand it
the dead-spot candidates this phase noticed (duplicated walks, retired seams, the
`episode_boundary` orphan, the three eval/ walk implementations, the recorder lock-race
and the un-unit-tested deadline_default freeze-guard branch, the unassigned validity-gate
deadline_default blindness, the unassigned validity-gate stamped-substrate question for
LLM-free meeting paths — every zero-LLM composed meeting fails `cost_and_provenance_exact`
for want of a model row, which is why composed-substrate probe reads are pinned
diagnostic-grade in `verdict.json.adoption_constraints` — the platform-sensitive `test_es`
hash pin that fails on non-Linux interpreters) as review inputs, not as contracts.

## Integration risk

Same as every close: the byte-coupled re-pin sweep on the FLIP path, and the two-owner-gate
compression (the flip ruled at 18.27, the close ratified here) — keep the close PR free of
any new evidence so the owner's merge ratifies a reading, never a surprise.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import training.composed_runner"`
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
- `uv run python -c "import training.conviction.serving"`
- `uv run python -c "import agents.tactical.features"`
- `uv run python -c "import training.coevo.factory"`
- `uv run python -c "import training.coevo.rollout"`
- `uv run python -c "import training.coevo.driver"`
- `uv run python -c "import training.coevo.hall_of_fame"`
- `uv run python -c "import training.bakeoff.map_elites"`
- `uv run python -c "import training.realpath"`
- `uv run python -c "import training.anchor_study"`
- `uv run python -c "import training.scenarios"`

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
Open a PR from branch `phase-18-close` with a title like `task 18.28: the mover record + the phase close (operator + owner, $0)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing tasks/phase-17.md 17.17 + audits/audit-phase-17-close.md (the close shape, both paths); the 18.12 record audit (the canary pre-registration source); tasks/post-phase-14-plan.md (the roadmap spine this close annotates)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
