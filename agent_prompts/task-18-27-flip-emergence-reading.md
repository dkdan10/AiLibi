# Agent Prompt — 18.27 THE FLIP + EMERGENCE READING (owner) + conditional productization

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.27 — THE FLIP + EMERGENCE READING (owner) + conditional productization, anchored to audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-flip-emergence-reading`
**Depends on:** 18.4, 18.18, 18.26
**Section refs:** audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables
**Complexity:** Integration

The phase's owner reading, two axes in one memo. **Axis 1 — the flip:** the champion
candidate read against the standing bar (referee PASS at the adopted baseline's floors AND
win ≥ the same-seed FSM comparator); PASS ⇒ productize the ARTIFACT surface (the champion
weights/stamp under `agents/tactical/learned/` swap to the ruled candidate) and pre-author
the selector flip — the DEFAULT-SELECTOR surfaces (`orchestrator/game.py::
build_default_agent_factory`, the `scripts/run_tournament.py` default path) flip at
18.28's adopting record, not here (adoption-at-record: a default graduates at the baseline
that adopts it); FAIL ⇒ the champion stays opt-in, the finding recorded, 18.28 closes
NO-FLIP. **Axis 2 — emergence:** every pre-registered instrument read against the
18.4 memo's four-part discipline (significance, split-reproducibility, ablation,
selected-for), each claim ruled EMERGENT / NOT-DEMONSTRATED with the evidence quoted. A
crew-adoption question, if the crew evidence supports one, is put to the owner here as its
own slot — never folded silently into either axis.

**Files in scope:**
- audits/audit-phase-18-flip-emergence.md (new: the two-axis memo + rulings)
- agents/tactical/learned/; (PASS branch only: the artifact-surface productization swap — the default-selector files flip at 18.28's record)
- tests/scripts/test_champion_flip_ruling.py; (the ruling pins, either branch)
- tasks/phase-18.md; (the ruling's banner note)

**Files NOT in scope:**
- eval/ + training/ (evidence is read, never regenerated here)
- replays/ (no record at the reading — 18.28 records)

**Definition of done:**
- [ ] The memo reads axis 1 against the bar with every floor cell + win edge quoted from the 18.26 committed rows, the ruling recorded verbatim, and the ruled branch implemented + pinned (PASS: the artifact surface swapped and the 18.28 selector flip pre-authored, with the default provably NOT yet moved — adoption-at-record; FAIL: the default provably unmoved).
- [ ] Axis 2 rules every pre-registered claim with its four-part evidence quoted (including the ablation runs' provenance), and any crew-adoption slot is put and recorded explicitly.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The 17.16 both-branches-pre-authored pattern: write the FAIL branch first (it is the
historical base rate), then the PASS branch's swap surface. The ablation evidence for axis
2 comes from the campaign reports — if an ablation was not run for a claimed behavior, the
claim reads NOT-DEMONSTRATED, honestly.

## Integration risk

Two owner rulings in one PR risks a stalled merge if one axis's evidence is contested —
keep the memo's axes separable so the owner can rule one and hold the other (the PR stays
open on the held axis, the 17.14 PENDING pattern).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
- `uv run python -c "import training.coevo.hall_of_fame"`
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
Do not add LLM calls inside agents/tactical/.
Do not import engine/ from agents/.
If the task mentions engine-free boundary schemas, keep agents/ free of engine imports and put engine translation only in orchestrator-owned code.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-18-flip-emergence-reading` with a title like `task 18.27: the flip + emergence reading (owner) + conditional productization`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-17-close.md §1.3 (the flip bar, verbatim); audits/audit-phase-18-emergence-preregistration.md (the ratified second axis); tasks/phase-17.md 17.16 (the evidence-gated flip shape, both branches); the 18.26 evidence tables), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
