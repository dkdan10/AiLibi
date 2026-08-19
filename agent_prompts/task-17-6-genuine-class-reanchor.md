# Agent Prompt — 17.6 The genuine-class instrument re-anchors on supplied channels

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.6 — The genuine-class instrument re-anchors on supplied channels, anchored to audits/audit-phase-16-close.md §8 (the NO-DATA routing: re-anchor "on channels this substrate actually supplies (vents, sightings, whereabouts-lies)") + §6 (the second consecutive 0/0); eval/vote_correctness.py (the genuine-class definition + `genuine_class_subjects`'s endpoint-band exclusion); audits/audit-phase-16-baseline-4.md §6 (the supply collapse anatomy: alibi flags 190 → 7). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-genuine-class-reanchor`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (the NO-DATA routing: re-anchor "on channels this substrate actually supplies (vents, sightings, whereabouts-lies)") + §6 (the second consecutive 0/0); eval/vote_correctness.py (the genuine-class definition + `genuine_class_subjects`'s endpoint-band exclusion); audits/audit-phase-16-baseline-4.md §6 (the supply collapse anatomy: alibi flags 190 → 7)
**Complexity:** Medium

The Phase-10 primary-progress instrument (genuine-class conversion: did the crew convert
a genuinely-contradicted subject into an ejection?) reads 0/0 on baselines 4 and 5 —
the bespoke model stopped volunteering checkable alibi lies, and roll-call placements are
endpoint-banded out of the class. Re-anchor: define the successor instrument over the
evidence classes this substrate supplies — witnessed vents, sighting contradictions, and
whereabouts-lies (the recorded contradiction event ids from 16.10's fold) — measuring
the same question (supplied hard evidence against a subject → conviction?). The old
alibi-anchored cell stays as a reported column (labeled starved, never a canary); the
successor becomes the canary-eligible cell. Definitions, denominators, and the
committed-bytes cells are pinned so 17.17's close (and any future canary bands) read
one unambiguous instrument.

**Files in scope:**
- eval/vote_correctness.py (the successor instrument beside the legacy cell)
- tests/eval/test_vote_correctness.py (committed-bytes pins for both cells; synthetic fixtures per supplied channel)

**Files NOT in scope:**
- meetings/transcript.py (detector semantics untouched — the endpoint-band relaxation is routed, never done here)
- eval/funnel.py (17.4's region)

**Definition of done:**
- [ ] The successor instrument is defined and pinned on committed baseline-5 bytes with a NON-ZERO denominator (the substrate supplies vents/sightings/whereabouts-lies — quoted in the PR), and the legacy alibi-anchored cell is preserved as a labeled reported column reading 0/0.
- [ ] Per-channel synthetic fixtures prove the numerator/denominator semantics (a witnessed-vent subject ejected counts; the same subject skipped counts the denominator only; an unsupplied channel contributes nothing).
- [ ] The instrument's docstring records the re-anchor decision and its provenance (the close §8 routing) so a future substrate that re-supplies alibi lies can re-examine the legacy cell.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Reuse 16.10's recorded-contradiction-id reads (never re-derive detection) and the
existing conviction census join. The design risk is denominator inflation — a vent
witnessed by the eventual voter is a different evidential position than one spoken
second-hand; split the denominator by witness-vs-testimony if the committed bytes make
the distinction measurable, and say so in the report either way.

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
Open a PR from branch `phase-17-genuine-class-reanchor` with a title like `task 17.6: the genuine-class instrument re-anchors on supplied channels`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §8 (the NO-DATA routing: re-anchor "on channels this substrate actually supplies (vents, sightings, whereabouts-lies)") + §6 (the second consecutive 0/0); eval/vote_correctness.py (the genuine-class definition + `genuine_class_subjects`'s endpoint-band exclusion); audits/audit-phase-16-baseline-4.md §6 (the supply collapse anatomy: alibi flags 190 → 7)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
