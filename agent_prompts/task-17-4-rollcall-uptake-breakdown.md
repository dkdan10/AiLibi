# Agent Prompt — 17.4 Roll-call uptake breakdown (who is not answering)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-17.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 17.4 — Roll-call uptake breakdown (who is not answering), anchored to audits/audit-phase-16-close.md §6 (roll-call coverage 0.363 — the aggregate the gate cannot rule on) + §0.1.4 (the calibration question the breakdown answers); eval/funnel.py (the 16.10 pooling-folds region — `_roll_call_placed` and the whereabouts census); meetings/schemas.py `WhereaboutsClaim`. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-17.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-17-rollcall-uptake-breakdown`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-16-close.md §6 (roll-call coverage 0.363 — the aggregate the gate cannot rule on) + §0.1.4 (the calibration question the breakdown answers); eval/funnel.py (the 16.10 pooling-folds region — `_roll_call_placed` and the whereabouts census); meetings/schemas.py `WhereaboutsClaim`
**Complexity:** Small

The absence gate needs to know whether the 0.363 coverage is uniform silence or
structured refusal: extend the pooling folds with a per-role (crew vs impostor) and
per-surface (opening vs reply vs info-share) whereabouts-uptake breakdown, plus a
per-meeting answered/asked census. Additive fields on the existing pooling report —
no fold semantics change; committed-bytes cells pinned. This is 17.7's evidence, so it
reads the committed baseline-5 sets as-is.

**Files in scope:**
- eval/funnel.py (additive breakdown fields in the pooling-folds region)
- tests/eval/test_funnel_pooling.py (committed-bytes pins + a synthetic role-split fixture)

**Files NOT in scope:**
- eval/vj_instruments.py + eval/meeting_quality.py (17.1/17.2's regions)
- meetings/ (measurement only)

**Definition of done:**
- [ ] The pooling report carries whereabouts uptake split by speaker role and by template surface, with the committed baseline-5 cells pinned (the aggregate must still reproduce 0.363 on 9p2i — the new cells decompose it, never move it).
- [ ] A synthetic fixture proves the role attribution (an impostor's whereabouts claim counts under impostor, never crew).
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
Open a PR from branch `phase-17-rollcall-uptake-breakdown` with a title like `task 17.4: roll-call uptake breakdown (who is not answering)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-16-close.md §6 (roll-call coverage 0.363 — the aggregate the gate cannot rule on) + §0.1.4 (the calibration question the breakdown answers); eval/funnel.py (the 16.10 pooling-folds region — `_roll_call_placed` and the whereabouts census); meetings/schemas.py `WhereaboutsClaim`), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
