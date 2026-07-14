# Agent Prompt — 17.1 The VJ provenance gauge learns the J1 clamp-exemption

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

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
Open a PR from branch `phase-17-vj-gauge-clamp-exemption` with a title like `task 17.1: the vj provenance gauge learns the j1 clamp-exemption`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §8 (routed contract (a)) + §2 (the five by-design clamped rows); eval/vj_instruments.py `_cross_check_graphs` (the gauge with no J1 exemption); tests/eval/test_vj_instruments.py:375 (the live-pinned wrong cell: `provenance_sum_breaches == 5`); agents/memory/beliefs.py (the graduated J1 clamp semantics the gauge must mirror)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
