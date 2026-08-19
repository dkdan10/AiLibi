# Agent Prompt — 17.1 The VJ provenance gauge learns the J1 clamp-exemption

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.1 — The VJ provenance gauge learns the J1 clamp-exemption, anchored to audits/audit-phase-16-close.md §8 (routed contract (a)) + §2 (the five by-design clamped rows); eval/vj_instruments.py `_cross_check_graphs` (the gauge with no J1 exemption); tests/eval/test_vj_instruments.py:375 (the live-pinned wrong cell: `provenance_sum_breaches == 5`); agents/memory/beliefs.py (the graduated J1 clamp semantics the gauge must mirror). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-vj-gauge-clamp-exemption`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §8 (routed contract (a)) + §2 (the five by-design clamped rows); eval/vj_instruments.py `_cross_check_graphs` (the gauge with no J1 exemption); tests/eval/test_vj_instruments.py:375 (the live-pinned wrong cell: `provenance_sum_breaches == 5`); agents/memory/beliefs.py (the graduated J1 clamp semantics the gauge must mirror)
**Complexity:** Small

The close found the defect and routed it here: `_cross_check_graphs` asserts
`0.5 + Σ(eight channels) == rendered suspicion`, but the graduated J1 gate CLAMPS the
rendered value for soft-only rows — so five by-design clamped rows on the baseline-5
9p2i bytes report as phantom `provenance_sum_breaches`. Teach the gauge the exemption:
a row whose typed decomposition is soft-only under the J1 predicate (the 16.4
classification, `SUSPICION_PROVENANCE_ATOL` tolerance) checks the clamp arithmetic
instead of the raw sum. The gauge must still catch REAL breaches — a fixture with a
genuinely broken sum on a clamped row must fail.

**Files in scope:**
- eval/vj_instruments.py (`_cross_check_graphs` — the exemption predicate)
- tests/eval/test_vj_instruments.py (the ==5 pin becomes ==0 with the exemption asserted per-row; a synthetic true-breach fixture)

**Files NOT in scope:**
- agents/memory/beliefs.py (the clamp is production truth; the gauge mirrors, never moves)
- eval/meeting_quality.py (17.2's region)

**Definition of done:**
- [ ] On committed baseline-5 bytes the gauge reports 0 provenance-sum breaches, with the five previously-phantom rows individually asserted as J1-clamp-exempt (their identities pinned); a synthetic genuinely-broken clamped row still counts as a breach.
- [ ] The exemption predicate is the 16.4 soft-only classification verbatim (shared or byte-equivalent logic, tolerance `SUSPICION_PROVENANCE_ATOL`) — never a looser re-derivation.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

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
Open a PR from branch `phase-17-vj-gauge-clamp-exemption` with a title like `task 17.1: the vj provenance gauge learns the j1 clamp-exemption`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §8 (routed contract (a)) + §2 (the five by-design clamped rows); eval/vj_instruments.py `_cross_check_graphs` (the gauge with no J1 exemption); tests/eval/test_vj_instruments.py:375 (the live-pinned wrong cell: `provenance_sum_breaches == 5`); agents/memory/beliefs.py (the graduated J1 clamp semantics the gauge must mirror)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
