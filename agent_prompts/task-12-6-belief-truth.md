# Agent Prompt — 12.6 Belief × Truth (the hero, per-meeting)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.6 — Belief × Truth (the hero, per-meeting), anchored to design/phase-12/stage-1-design.md §3.3, slice 4; the rendered targets `design/phase-12/playful-system/screens/04-matrix-belief.png` / `04-matrix-ground-truth.png` / `04-matrix-error.png` and the `renderMatrix` code in `playful-system/playful-system.dc.html`; the firewall + "no belief yet ≠ 0" rules in `design/phase-12/claude-design-brief.md`. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-belief-truth`
**Depends on:** 12.1, 12.2, 12.4
**Section refs:** design/phase-12/stage-1-design.md §3.3, slice 4; the rendered targets `design/phase-12/playful-system/screens/04-matrix-belief.png` / `04-matrix-ground-truth.png` / `04-matrix-error.png` and the `renderMatrix` code in `playful-system/playful-system.dc.html`; the firewall + "no belief yet ≠ 0" rules in `design/phase-12/claude-design-brief.md`
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/components/BeliefCell.tsx
- frontend/src/components/BeliefPanel.tsx
- frontend/src/stories/BeliefMatrix.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the belief slot already mounts `<BeliefMatrix/>`; rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — `BeliefFrameView` + the per-meeting belief / signed-error projection already ship (12.2); no DTO change, no re-record
- the map / meeting / inspector surfaces — other Wave-B slices

Rebuild the **hero** surface the App.tsx slot mounts (`<BeliefMatrix/>`): a directed adjacency **matrix** (rows =
suspector, cols = suspected, cell = suspicion heat, bucketed Low / Med / High off `tokens.ts` `suspicionBucket`) with a
**Belief / Ground-Truth / Error** segmented toggle — same layout, swapped data, driven by the store's `beliefView`.
Ground-truth impostor markers are **Omniscient-only and suppressed in fog** (an icon, never a hue). The **Error** layer
(the DTO's signed `error` = Belief − Truth) renders confidently-wrong cells **LOUD** — fill + thick border + ✗ glyph, not
hue alone. Render **"no belief yet" ≠ 0** as a distinct hatched cell (the DTO flags it; never paint it as low suspicion —
a binding honesty rule). Granularity is **per-meeting snapshots** (`BeliefFrameView`) with a before → after **step
control** across the game's 2–4 meetings (small-multiples, not animation); click a cell → that pair's suspicion across
meetings + a "what changed this meeting" diff. Reserve a sparse **node-link** for "active accusations this meeting"
(signed edges blue = trust / orange = distrust). The matrix chrome — the segmented toggle, step control, and cell-detail
popover — comes from a focused Claude-Design prompt: *"Design the Belief × Truth matrix panel: an N×N suspicion matrix
(heat ramp, bucketed Low / Med / High), a Belief / Ground-Truth / Error segmented toggle, a meeting step control, a
cell-detail popover; states 1 meeting / multiple / no-meeting (empty); firewall — identity ≠ guilt, the ground-truth
marker is an icon that must be hideable (fog), Error cells LOUD via fill+border+glyph (not hue alone), 'no belief yet' ≠
0; presentational only, tokens only"* → Share → Handoff to Claude Code → wire to the per-meeting snapshots, then verify
the three toggle layers + the empty state + fog-suppression.
**Definition of done:** the matrix renders all three layers (Belief / Ground-Truth / Error) from `BeliefFrameView`, driven
by the store's `beliefView`; ground-truth markers are Omniscient-only and suppressed in fog; Error cells render LOUD (fill
+ border + glyph, never hue-only); "no belief yet" is a distinct hatched cell (≠ 0); the per-meeting step control,
cell-detail popover, and empty (no-meeting) state all work; the result matches the committed `04-matrix-belief` /
`04-matrix-ground-truth` / `04-matrix-error` renders; a Storybook story covers the three layers + empty state;
`npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green; `App.tsx` is untouched.

## Implementation hint
the slot already imports `<BeliefMatrix/>` — rebuild it plus its `BeliefRow` / `BeliefCell` children in place, and put the
toggle / step / popover chrome (from the handoff) in a `BeliefPanel` wrapper, all composed from `tokens.ts`. Drive the
three layers off the store's `beliefView` and the `BeliefFrameView` data (Belief = suspicion, Ground-Truth = the role
marker, Error = the signed `error` field), and suppress the ground-truth marker whenever perspective is As-agent. Match
the committed `04-matrix-belief` / `04-matrix-ground-truth` / `04-matrix-error` renders.

## Integration risk
the firewall lives in this surface — the ground-truth marker MUST vanish in fog (As-agent), and Error / correctness must
read by shape + glyph, not hue (role-neutral). Rendering "no belief yet" as 0 violates a binding honesty rule — key on the
DTO flag. Beliefs are per-MEETING (timeless), not per-tick, so the step control walks meetings, not ticks (a per-tick
sparkline would disagree with the recorded ballot). Don't edit `App.tsx` (mount discipline).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

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
Open a PR from branch `phase-12-belief-truth` with a title like `task 12.6: belief × truth (the hero, per-meeting)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §3.3, slice 4; the rendered targets `design/phase-12/playful-system/screens/04-matrix-belief.png` / `04-matrix-ground-truth.png` / `04-matrix-error.png` and the `renderMatrix` code in `playful-system/playful-system.dc.html`; the firewall + "no belief yet ≠ 0" rules in `design/phase-12/claude-design-brief.md`), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
