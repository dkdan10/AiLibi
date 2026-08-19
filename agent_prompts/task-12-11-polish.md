# Agent Prompt — 12.11 Accessibility, responsive, first-run, perf

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.11 — Accessibility, responsive, first-run, perf, anchored to design/phase-12/stage-1-design.md §8, §9, slice 9; the never-hue-only + reduced-motion a11y/firewall rules in `design/phase-12/claude-design-brief.md`; the holistic-visual-pass punch-list (in the body below).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-polish`
**Depends on:** 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.12
**Section refs:** design/phase-12/stage-1-design.md §8, §9, slice 9; the never-hue-only + reduced-motion a11y/firewall rules in `design/phase-12/claude-design-brief.md`; the holistic-visual-pass punch-list (in the body below).
**Complexity:** Integration
**Files in scope:**
- frontend/src/App.tsx
- frontend/vite.config.ts
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/components/GuidedTour.tsx
- frontend/src/index.css
- .github/workflows/ci.yml
**Files NOT in scope:**
- api/ and the loader — pure frontend polish; no DTO change, no re-record
- the engine / recorded replays — no re-record

The phase-close polish pass, hand-coded (no Claude Design). **This is the one task that legitimately edits `App.tsx`** —
the shell-level responsive / first-run / code-split — and it runs sequentially after every surface, so the Wave-B mount
discipline does not apply here. Scope:
- **A11y:** keyboard-operable transport (scrub / step / play / jump), focus management + `:focus-visible`, ARIA on the
  data panels (matrix, ballots, mind tabs, browser, dashboard, and 12.12's set selector), a **reduced-motion** variant (vent dive / kill flash /
  contradiction link-draw / map↔meeting morph respect `prefers-reduced-motion`), AA contrast, and a **never-hue-only
  audit** — every status / correctness / suspicion encoding must also read by shape or label (the firewall a11y rule).
- **Responsive:** rails collapse to drawers on narrow widths; the map + transport are the irreducible core.
- **First-run guided mode:** an annotated walkthrough on a high-interestingness 9p2i seed teaching the perspective switcher
  + the two-truth grammar (a new `GuidedTour`).
- **Perf / code-split:** `vite.config.ts` `manualChunks` (Pixi + react-dom vendor chunk) + `React.lazy` for Dashboard /
  Highlights → close the **859 kB single chunk** (the build's > 500 kB warning gone).
- **Holistic-pass visual nits:** (a) the **map token↔label overlap** — room-name labels (Admin / Storage / Reactor) sit
  under their centered player tokens; reposition the label clear of the token. (b) the **map dead-end cluster density** —
  at Reactor / Storage the kill ✕ + impostor dagger (†) + body marker + labels stack; de-conflict them. (c) the
  **overlay-composition bug** (the owner-reported "meeting overlap", confirmed from screenshots — it shows only in the
  *composed* app, not isolated stories). The MeetingView (`z-50`), BeliefMatrix (`z-55`), and MindInspector / ThoughtStream
  (`z-60`) are independent *fixed* overlays that stack and collide: the Mind-inspector rail covers the Ballots panel, and
  the background map / belief bleeds through the gaps. Coordinate them into one clean layout — an open meeting masks the
  workspace, the inspector never overlaps the ballots, no background bleed. (d) the **map does not fill its stage** — it
  renders small with large empty space; scale the canvas to fill the stage container, and fan out / de-overlap the
  Cafeteria spawn cluster (all 9 tokens pile on the room label at tick 0).
- Optional: a Playwright visual smoke in CI (needs the loader + a served 9p2i set; sequence after build / typecheck).
**Definition of done:** keyboard transport + ARIA on data panels + reduced-motion + AA contrast + a passing
never-hue-only audit; responsive rail→drawer; a first-run guided mode on a high-interestingness seed; the 859 kB chunk
split (the > 500 kB build warning gone); the map token↔label overlap + dead-end cluster + Cafeteria spawn-cluster
de-cluttered and the map fills its stage (no large empty space); the overlay-composition bug is fixed (the meeting /
belief / mind overlays no longer collide — the inspector doesn't cover the ballots and no background bleeds through);
every surface still renders correctly after the changes; `npm run tsc:check` +
`npm run build` pass and `scripts/check.sh` is green.

## Implementation hint
this task owns the shell, so editing `App.tsx` is expected (responsive layout, the `GuidedTour` mount, `React.lazy`
boundaries). Fix the map nits in `MapView` (offset the room label vs the centered token; de-conflict the Reactor /
Storage markers). For the meeting overlap, run the spectator and open a meeting over the live workspace to reproduce
before touching `MeetingView` — it is composition-level, not the isolated component. Code-split via `vite.config.ts`
`manualChunks` + `React.lazy`.

## Integration risk
a11y + responsive touch every surface — regression-check each (map fog, matrix layers, meeting verdict, dashboard
caveats) still renders after the reduced-motion / responsive / lazy changes. The never-hue-only audit is the firewall
a11y rule — don't let a colour-only status slip through. The code-split must not break Pixi or the lazy-loaded routes.
The overlay-composition bug is confirmed (owner screenshots) but shows only in the composed app — build + test it in the
running spectator, not isolated stories. This task owns the all-surface a11y, so it edits `ReplayPicker` /
`TournamentDashboard` (also 12.12's files) — that is why it `depends on 12.12` and runs sequentially after it; do not
dispatch them in parallel.

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
Open a PR from branch `phase-12-polish` with a title like `task 12.11: accessibility, responsive, first-run, perf`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §8, §9, slice 9; the never-hue-only + reduced-motion a11y/firewall rules in `design/phase-12/claude-design-brief.md`; the holistic-visual-pass punch-list (in the body below).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
