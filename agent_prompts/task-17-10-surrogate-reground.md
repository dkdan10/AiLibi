# Agent Prompt — 17.10 Surrogate re-ground + re-verdict on the recorded bar

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.10 — Surrogate re-ground + re-verdict on the recorded bar, anchored to training/surrogate/ballots.py (the fit pipeline + `BALLOT_FEATURE_NAMES` — the 6-feature live-parity fence, kept by locked decision 4); training/surrogate/dataset.py (the reconstruction walk + the hand-mirrored belief pins); training/reports/report-ballot-surrogate.md (the baseline-3 report this regenerates end-to-end, incl. the three-axis bar + the always-eject anchor); training/artifacts/surrogate/ (the artifact bundle + max-uses.json). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-surrogate-reground`
**Depends on:** 17.9
**Section refs:** training/surrogate/ballots.py (the fit pipeline + `BALLOT_FEATURE_NAMES` — the 6-feature live-parity fence, kept by locked decision 4); training/surrogate/dataset.py (the reconstruction walk + the hand-mirrored belief pins); training/reports/report-ballot-surrogate.md (the baseline-3 report this regenerates end-to-end, incl. the three-axis bar + the always-eject anchor); training/artifacts/surrogate/ (the artifact bundle + max-uses.json)
**Complexity:** Integration

Rebuild the meeting table on the new corpus, re-fit the predictor, re-measure the
owner-ratified three-axis GO/NO-GO, re-commit the artifact bundle (weights + sha
sidecar + a max-uses cap RE-DERIVED from the recorded corpus's fit-side meeting count under
the ~143× rule — baseline 5), and regenerate the report end-to-end — every baseline-3 anchor
(honest ceiling, FO-6 re-baseline, always-eject constant 0.802) re-measured, never
copied. Three baseline-5-specific validations are load-bearing: (1) coerced-SKIP rows
are EXCLUDED from the fit and counted in the report (designer ruling — forced ejects
are not skip labels); (2) live-parity under graduated J1: the dataset's raw
`belief_suspicion` column vs the clamped rendered value the live runner would serve —
measure the divergence and state which side the fit uses and why; (3) the dataset walk
re-validates on corpus bytes that now carry whereabouts turns, observation-cited
ballots, and marker-prefixed rationales. A repeat NO-GO is a finding: the surrogate
stays diagnostic-only, its usage tier unchanged, and NOTHING downstream re-plans (the
bake-off consumes it as a training-time runner either way).

**Files in scope:**
- training/surrogate/dataset.py (baseline-5 re-validation + the coerced-row filter)
- training/surrogate/ballots.py (fit-side filter wiring; feature set UNCHANGED)
- training/artifacts/surrogate/ (ballot-predictor.json + .sha256 + max-uses.json)
- training/reports/report-ballot-surrogate.md (regenerated)
- tests/training/test_surrogate_dataset.py + test_surrogate_fidelity.py + test_surrogate_runner.py (re-pins + the stale baseline-3 docstrings corrected; 17.9 xfail'd six runner fit/fidelity/verdict tests "pending 17.10 re-ground" — REMOVE those markers and re-pin on the new artifact)

**Files NOT in scope:**
- training/bakeoff/ (17.11/17.12)
- replays/ (consumes 17.9's bytes)

**Definition of done:**
- [ ] The artifact bundle is re-committed with coherent provenance (new sha in the sidecar and the re-derived max-uses key; the fit corpus named); the report regenerates every cell from the new corpus with the three-axis verdict stated and the axis-by-axis arithmetic beside it.
- [ ] Coerced-SKIP handling pinned: fit-side rows carrying the coercion marker are dropped and counted (the count in the report); fidelity replay scores recorded bytes unfiltered.
- [ ] The J1 live-parity divergence is measured on committed bytes and recorded (raw vs clamped, which side the fit reads, the count of rows where it matters).
- [ ] The GO/NO-GO verdict and its consequences are stated in the report exactly as locked decision 4 defines them (promotion iff the bar passes; diagnostic-only otherwise; the bake-off is not blocked in either direction).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Sequence: re-validate the dataset walk on the new bytes FIRST (the fidelity cross-check),
then filter, then fit, then verdict — a fit on an unvalidated table wastes the session.
The report regeneration is mechanical once the cells exist; keep the three-axis
arithmetic in the same table shape as the Phase-15 report so the verdicts diff cleanly.

## Integration risk

The dataset's hand-mirrored perception→belief pins (`_WindowStats`) are unprotected by
state-hash verification — if any baseline-5 belief-rule nuance drifted them, the
`belief_suspicion` column corrupts SILENTLY. The re-validation must include at least one
end-to-end cross-check against the production fold on real corpus meetings (the 16.10
walk precedent: measure fidelity, don't assume it) before any fit is trusted.

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
Open a PR from branch `phase-17-surrogate-reground` with a title like `task 17.10: surrogate re-ground + re-verdict on the recorded bar`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing training/surrogate/ballots.py (the fit pipeline + `BALLOT_FEATURE_NAMES` — the 6-feature live-parity fence, kept by locked decision 4); training/surrogate/dataset.py (the reconstruction walk + the hand-mirrored belief pins); training/reports/report-ballot-surrogate.md (the baseline-3 report this regenerates end-to-end, incl. the three-axis bar + the always-eject anchor); training/artifacts/surrogate/ (the artifact bundle + max-uses.json)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
