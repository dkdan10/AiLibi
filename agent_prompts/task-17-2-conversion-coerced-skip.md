# Agent Prompt — 17.2 The conversion report learns the coerced SKIP (a by-design bucket)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.2 — The conversion report learns the coerced SKIP (a by-design bucket), anchored to audits/audit-phase-16-close.md §8 (routed contract (b): 2 of 99 inversions on the baseline-5 samples are J2-coerced SKIPs); eval/meeting_quality.py `compute_conversion_report` (the SKIP partition + its invariant); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` (the literal + the `{x!r}` marker shape); the invalid-target/teammate by-design-bucket precedent in the same report. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-conversion-coerced-skip`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (routed contract (b): 2 of 99 inversions on the baseline-5 samples are J2-coerced SKIPs); eval/meeting_quality.py `compute_conversion_report` (the SKIP partition + its invariant); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` (the literal + the `{x!r}` marker shape); the invalid-target/teammate by-design-bucket precedent in the same report
**Complexity:** Medium

A J2-coerced ballot records `target="SKIP"` with the coercion marker prefixed to
`rationale_text`; the report's partition predates the marker and mis-files those
ballots as §4.6 threshold inversions. Add a by-design sub-bucket: a SKIP carrying
`UNCITED_ZERO_FLAG_EJECT_MARKER` is neither a missed skip nor an inversion — it is the
gate working. The partition invariant (every ballot lands in exactly one bucket)
extends to cover the new bucket; the report surfaces its count. This must land BEFORE
the corpus re-record (17.9's dep): every conversion read over baseline-5-era bytes is
over-counting inversions until it does.

**Files in scope:**
- eval/meeting_quality.py (the SKIP partition + invariant + report field)
- tests/eval/test_meeting_quality.py (the 2/99 committed-bytes pin moves to the new bucket; partition-invariant fixtures; a marker-stacked ballot fixture — coercion atop a 16.5 nulled-citation marker)

**Files NOT in scope:**
- meetings/manager.py (the marker literal is production truth — imported, never re-spelled)
- eval/vj_instruments.py (17.1's region)

**Definition of done:**
- [ ] On committed baseline-5 9p2i bytes the report shows the two previously-mis-filed ballots in the coerced-SKIP bucket, threshold inversions drop accordingly, and the partition invariant holds over every committed meeting (asserted).
- [ ] Marker detection uses the imported literal via the established `{x!r}` marker-parsing convention (the `api.replay_loader._marker_pattern` shape) — stacked markers (16.5 null + 16.6 coercion) parse correctly, fixture-pinned.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Follow the report's existing by-design buckets (invalid-target, teammate) for naming and
invariant wiring. The marker rides `rationale_text` as a PREFIX — strip-and-classify
before any prose-level reads, and remember 16.6's stacking order (gate prefix outside
the redirect marker).

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
Open a PR from branch `phase-17-conversion-coerced-skip` with a title like `task 17.2: the conversion report learns the coerced skip (a by-design bucket)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §8 (routed contract (b): 2 of 99 inversions on the baseline-5 samples are J2-coerced SKIPs); eval/meeting_quality.py `compute_conversion_report` (the SKIP partition + its invariant); meetings/manager.py `UNCITED_ZERO_FLAG_EJECT_MARKER` (the literal + the `{x!r}` marker shape); the invalid-target/teammate by-design-bucket precedent in the same report), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
