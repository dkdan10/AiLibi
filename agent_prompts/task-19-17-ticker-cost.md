# Agent Prompt — 19.17 The event ticker + cost chips (the gated tail)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-19.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 19.17 — The event ticker + cost chips (the gated tail), anchored to audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-19.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-19-ticker-cost`
**Depends on:** 19.10, 19.12, 19.13 (the last is frontend/e2e/ serialization — the bundle journey lands before the ticker extends it)
**Section refs:** audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side
**Complexity:** Small

The two cheap visible wins, landed deliberately LAST in the frontend chain (the
dependency edges are the point: narrative correctness shipped first). An event ticker
(kills, reports, meetings, ejections as they play) and cost/token chips. Both are
additive chrome — but the ticker touches PRIVILEGED data: the served event views carry
killer identity (`api/schemas.py` `KillEventView` — "privileged kill attribution") and
unwitnessed vent identity/routes (`VentEventView`), so unspoiled-mode gating alone is
NOT the firewall. The ticker renders through the SAME perspective projection the map and
roster enforce: in as-agent view only what that agent's fog admits (an unwitnessed kill
surfaces as body discovery, never as attribution; unwitnessed vents don't surface at
all), with fog tests pinning one witnessed and one unwitnessed case each for kills and
vents. Cost chips are FRAME-BOUNDED (cumulative-to-current-frame, never the game total —
a total is an outcome-shape leak under unspoiled mode). Neither surface may regress the
pause/finale flow, and both extend the existing test baseline.

**Files in scope:**
- frontend/src/components/EventTicker.tsx (new)
- frontend/src/components/CostChips.tsx (new)
- frontend/src/App.tsx; (mounting only)
- frontend/e2e/; (extend the journey's assertions)

**Files NOT in scope:**
- api/ (no new server data — client-side data only)
- frontend/src/hooks/usePlayback.ts (consumed, not edited)

**Definition of done:**
- [ ] Ticker and chips render from already-served data through the active perspective projection: the four fog cases (witnessed/unwitnessed × kill/vent) are test-pinned in as-agent view, unspoiled mode leaks no outcome, cost chips are frame-bounded, and the extended journey still passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.deduction_metrics"`
- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-19-ticker-cost` with a title like `task 19.17: the event ticker + cost chips (the gated tail)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/audit-phase-19-triage.md §7 item 18 + singleton 29 [S-Claude — "subordinate to pause/finale/temporal-coherence work, not silently discarded"]; the per-call token counts already recorded in replay bytes and served client-side), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
