# Agent Prompt — 16.10 The V&J instruments: pooling folds + judgment metrics + deterministic voice tier

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-16.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 16.10 — The V&J instruments: pooling folds + judgment metrics + deterministic voice tier, anchored to eval/funnel.py (the three-stage instrument this extends); audits/post-phase-14-Voice-and-Judgment-planning.md §2 (the measurement harness design: zero-flag channel, claim-ECE, voice metrics); scripts/measure_baseline.py (the CLI the folds surface through); audits/audit-phase-15-close.md §11 (the conversion-seam finding these instruments must make measurable). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-16.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-16-vj-instruments`
**Depends on:** 16.3, 16.5, 16.7
**Section refs:** eval/funnel.py (the three-stage instrument this extends); audits/post-phase-14-Voice-and-Judgment-planning.md §2 (the measurement harness design: zero-flag channel, claim-ECE, voice metrics); scripts/measure_baseline.py (the CLI the folds surface through); audits/audit-phase-15-close.md §11 (the conversion-seam finding these instruments must make measurable)
**Complexity:** Medium

The phase's own before/after instrument, committed BEFORE the levers turn on (the 15.1/15.3
lesson: the instrument lands first, the close reads it). Three groups. (a) **Pooling folds**
(`eval/funnel.py` extension region): roll-call coverage (share of living players publicly placed
per meeting), vouch rate and GROUNDED-vouch rate, absence-set size distribution, and
whereabouts-lie detection rate (claims contradicted by grounded sightings). (b) **Judgment
metrics** (new `eval/vj_instruments.py`): the zero-flag conviction rate with its soft/hard split
read off 16.3's TYPED provenance (replacing the planning doc's rendered-value proxy — the
instrument upgrade the foundation makes possible), citation-compliance rate (ballots citing turn
or observation, valid vs dangling), and ballot-confidence calibration (Brier/ECE against
conviction correctness — the 15.11 harness pattern applied to the recorded ballots). (c) **The
deterministic voice tier**: within-meeting echo rate, response-skeleton share, distinct-n
diversity — the cheap, deterministic slice of the planning doc's voice metrics (the LLM-judged
tier is explicitly out: $0 discipline). All folds run on any replay-set directory and surface
through a `scripts/measure_baseline.py --vj` region; committed baseline-3 bytes are the
reproduction fixture wherever a figure already exists (the close audit's zero-flag and conversion
cells), and every new fold ships with a synthetic fixture proving it can move.

**Files in scope:**
- eval/funnel.py (pooling-folds extension region — additive; the 15.3 folds untouched)
- eval/vj_instruments.py (new: judgment metrics + voice tier + report types)
- scripts/measure_baseline.py (the --vj fold region — this task is the phase's ONLY measure_baseline toucher)
- tests/eval/test_vj_instruments.py (new: reproduction pins where figures exist + synthetic movement fixtures)
- tests/eval/test_funnel_pooling.py (new)

**Files NOT in scope:**
- eval/watchability.py (the referee is 16.11's; instruments here are diagnostics, never gates)
- eval/validity.py (no gate change)
- meetings/ + agents/ (read-only reconstruction — the folds observe, never touch)

**Definition of done:**
- [ ] On committed baseline-3 bytes, the zero-flag conviction rate and citation-compliance folds reproduce the close audit's cells where they exist, and the soft/hard split cross-checks against 16.3's provenance sums (the typed upgrade is consistent with the rendered-value proxy within documented tolerance).
- [ ] Every pooling fold reads zero/empty on committed bytes where the mechanism doesn't exist yet (no roll-call → coverage 0, absence set = unplaced share as-is) and moves on a synthetic fixture — an instrument that cannot move is not an instrument.
- [ ] The voice tier is deterministic (double-run identical) and $0; its per-meeting rows join the same report as the judgment metrics so 16.17 reads voice ALONGSIDE zero-flag (the phase's named NO-GO pairing).
- [ ] `scripts/measure_baseline.py --vj` emits the machine-readable report the 16.17 close consumes; the JSON shape is documented in the module docstring.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Reuse the 15.3 walk (the folds are meeting-scoped reconstructions over the same replay stream);
the provenance cross-check is the one novel join — read 16.3's decomposition off the
reconstructed belief state at pre-vote, exactly where the render reads it. Keep gate-shaped
language out of this module: these are diagnostics the close QUOTES; the referee alone gates.

## Public types this task introduces
- `eval.vj_instruments.VJInstrumentReport`
- `eval.vj_instruments.compute_vj_instruments`

These are the symbols downstream tasks will import. Keep their signatures stable.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import agents.memory.beliefs"`
- `uv run python -c "import agents.memory.episodic"`
- `uv run python -c "import agents.memory.store"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-16-vj-instruments` with a title like `task 16.10: the v&j instruments: pooling folds + judgment metrics + deterministic voice tier`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing eval/funnel.py (the three-stage instrument this extends); audits/post-phase-14-Voice-and-Judgment-planning.md §2 (the measurement harness design: zero-flag channel, claim-ECE, voice metrics); scripts/measure_baseline.py (the CLI the folds surface through); audits/audit-phase-15-close.md §11 (the conversion-seam finding these instruments must make measurable)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
