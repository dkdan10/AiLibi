# Agent Prompt — 18.2 The kill-craft fold: kill-timing vs witness density + action-stream entropy

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-18.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 18.2 — The kill-craft fold: kill-timing vs witness density + action-stream entropy, anchored to audits/audit-phase-18-planning.md §3.2 (the Tier-B gap rows); eval/watchability.py:1031 (`_reconstruct_kills`, the engine walk to extend); engine/events.py:76 (`KilledEvent.tick/room/witnesses`); eval/vj_instruments.py:704-719 (the lexical diversity cells this complements). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-18.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-18-kill-craft-fold`
**Depends on:** none (root)
**Section refs:** audits/audit-phase-18-planning.md §3.2 (the Tier-B gap rows); eval/watchability.py:1031 (`_reconstruct_kills`, the engine walk to extend); engine/events.py:76 (`KilledEvent.tick/room/witnesses`); eval/vj_instruments.py:704-719 (the lexical diversity cells this complements)
**Complexity:** Medium

Two new reconstruction folds, one module. **Kill-timing vs witness density**: per recorded
kill, the count of living crew co-present or one hop away at the kill tick (a per-tick
occupancy census added to the existing engine reconstruction walk), correlated with the
witnessed bit — the first byte-grounded gauge of kill-craft (does the mover kill into
witnesses or wait them out?). **Action-stream behavioral entropy**: per-agent entropy of
action-kind choices bucketed by coarse agent-state (room occupancy count, cooldown state),
the intent-level diversity metric beside the existing lexical one. Both offline over
committed bytes; both pinned on corpus + samples.

**Files in scope:**
- eval/kill_craft.py (new)
- tests/eval/test_kill_craft.py

**Files NOT in scope:**
- eval/watchability.py; (its walk is consumed via import or a faithful local walk — the referee itself does not move)
- engine/ (read-only reconstruction)

**Definition of done:**
- [ ] On committed corpus bytes the fold reports per-kill witness-density cells (co-present, one-hop) and the witnessed correlation, plus per-side action-entropy cells, all pinned; the occupancy census agrees with the engine walk's per-tick state (state-hash-verified reconstruction).
- [ ] The entropy bucketization is documented in the module docstring and deterministic (sorted, quantized) — no float-ordering hazards.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

The reconstruction walk (`re-seed + advance_tick` over recorded actions) already exists in
two places (`eval/watchability.py:1031`, `eval/funnel.py:287`); build the occupancy census
as a fold over that walk rather than a third walk implementation if a shared seam is
reachable without editing the referee — otherwise a local walk with the state-hash check is
acceptable and the duplication is noted for Phase 19's review.

## Public types this task introduces
- `eval.kill_craft.KillCraftReport`
- `eval.kill_craft.compute_kill_craft_report`

These are the symbols downstream tasks will import. Keep their signatures stable.

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
Open a PR from branch `phase-18-kill-craft-fold` with a title like `task 18.2: the kill-craft fold: kill-timing vs witness density + action-stream entropy`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-18-planning.md §3.2 (the Tier-B gap rows); eval/watchability.py:1031 (`_reconstruct_kills`, the engine walk to extend); engine/events.py:76 (`KilledEvent.tick/room/witnesses`); eval/vj_instruments.py:704-719 (the lexical diversity cells this complements)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
