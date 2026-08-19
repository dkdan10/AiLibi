# Agent Prompt — 18.30 The live conviction serving path (kill/body accessors + the in-loop term wiring)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.30 — The live conviction serving path (kill/body accessors + the in-loop term wiring), anchored to training/reports/report-conviction-model.md §10 (the routed serving seam — the four kill/body features have no live accessor); orchestrator/game.py:2548 + :2584 (the vent-witness and sighting `*_for_meeting` accessor patterns to mirror); training/bakeoff/harness.py:892-929 (`inner_episode_fitness` + `ConvictionFitnessTerm` — the wired-but-dormant seam every in-repo loop passes `conviction=None` into); training/crew/scorer.py:933-975 (the crew twin); training/conviction/model.py (`CONVICTION_FEATURE_NAMES` + the provenance map the live path must satisfy feature-for-feature). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-conviction-serving`
**Depends on:** 18.16
**Section refs:** training/reports/report-conviction-model.md §10 (the routed serving seam — the four kill/body features have no live accessor); orchestrator/game.py:2548 + :2584 (the vent-witness and sighting `*_for_meeting` accessor patterns to mirror); training/bakeoff/harness.py:892-929 (`inner_episode_fitness` + `ConvictionFitnessTerm` — the wired-but-dormant seam every in-repo loop passes `conviction=None` into); training/crew/scorer.py:933-975 (the crew twin); training/conviction/model.py (`CONVICTION_FEATURE_NAMES` + the provenance map the live path must satisfy feature-for-feature)
**Complexity:** Medium

The 18.16 verification's finding, given an owner: the conviction gradient is wired and
pinned at the seam but DORMANT — no live accessor serves the four kill/body features, so
every training loop passes `conviction=None` and the pre-screen accepts only caller-built
vectors. Land the serving path: (1) the kill-witness and body-proximity `*_for_meeting`
accessor pair on the same surface as the vent-witness accessor, mirroring its pattern
verbatim (orchestrator-side engine reads — the firewall binds agents, not the trainer);
(2) a live feature assembler (`training/conviction/serving.py`) producing the exact
`CONVICTION_FEATURE_NAMES` vector from `run_meeting`-time state; (3) the term threaded
live through the entrant loops and the crew ES loop via `load_conviction_fitness_term()`
(GO ⇒ on by default; NO-GO structural absence preserved); (4) the pre-screen consuming
live-assembled vectors. The contract's heart is the parity pin: over the committed corpus
test split, the live-assembled vector equals the offline table's row feature-for-feature
— the live/offline semantics gap closes by measurement, not assertion.

**Files in scope:**
- training/conviction/serving.py (new: the live assembler)
- orchestrator/game.py; (the kill/body `*_for_meeting` accessor pair ONLY — mirror the :2548/:2584 pattern)
- training/bakeoff/harness.py; (the entrant-loop conviction threading ONLY)
- training/crew/scorer.py; (the crew-loop threading ONLY)
- tests/training/test_conviction_serving.py (new: the live/offline parity pin + accessor fixtures)
- tests/training/test_bakeoff_harness.py; (the loops-serve-live pins ONLY)

**Files NOT in scope:**
- training/conviction/{dataset,model,fidelity}.py (the fence and verdict are frozen; serving consumes them)
- agents/ (the accessors are orchestrator-side; nothing crosses the firewall)
- eval/ (untouched)

**Definition of done:**
- [ ] The accessor pair mirrors the vent-witness pattern (surface, naming, leak discipline) and is fixture-pinned; over the committed corpus test split the live-assembled feature vector equals the offline table row feature-for-feature (the parity pin, every `CONVICTION_FEATURE_NAMES` entry asserted).
- [ ] With the committed GO verdict the entrant and crew loops carry a non-None conviction term by default (rows say so), NO-GO structural absence is preserved (fixture), and the pre-screen accepts live-assembled vectors end-to-end on the fake-path harness.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Mirror the vent accessor verbatim — same wrapper surface, same record-snapshot semantics,
same teammate-firewall inheritance. The parity pin is the whole game: build it FIRST
against the offline table (`build_conviction_table` honors `splits.json`), then implement
until it passes; any feature that cannot be made live-equal is a stop-and-report, never an
approximation. Threading defaults follow the verdict bytes (`load_conviction_fitness_term`
already encodes GO/NO-GO); the loops' change is passing the loaded term, not new logic.

## Public types this task introduces
- `training.conviction.serving.assemble_live_conviction_features`
- `training.conviction.serving.LiveConvictionFeatureError`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-18-conviction-serving` with a title like `task 18.30: the live conviction serving path (kill/body accessors + the in-loop term wiring)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/reports/report-conviction-model.md §10 (the routed serving seam — the four kill/body features have no live accessor); orchestrator/game.py:2548 + :2584 (the vent-witness and sighting `*_for_meeting` accessor patterns to mirror); training/bakeoff/harness.py:892-929 (`inner_episode_fitness` + `ConvictionFitnessTerm` — the wired-but-dormant seam every in-repo loop passes `conviction=None` into); training/crew/scorer.py:933-975 (the crew twin); training/conviction/model.py (`CONVICTION_FEATURE_NAMES` + the provenance map the live path must satisfy feature-for-feature)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
