# Agent Prompt — 12.1 Foundation: design tokens, Storybook, CLAUDE.md, CI

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.1 — Foundation: design tokens, Storybook, CLAUDE.md, CI, anchored to design/phase-12/stage-1-design.md §6, §9, §9.5; design/phase-12/claude-design-brief.md; **the committed 0b token sheet `design/phase-12/tokens-seed.md`** (transcribe `tokens.ts` from it — it is the in-repo source of truth, NOT the Downloads mockup); the Playful visual reference `design/phase-12/playful-system/playful-render.png` (Storybook + the cream theme should match it). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-foundation`
**Depends on:** none
**Section refs:** design/phase-12/stage-1-design.md §6, §9, §9.5; design/phase-12/claude-design-brief.md; **the committed 0b token sheet `design/phase-12/tokens-seed.md`** (transcribe `tokens.ts` from it — it is the in-repo source of truth, NOT the Downloads mockup); the Playful visual reference `design/phase-12/playful-system/playful-render.png` (Storybook + the cream theme should match it)
**Complexity:** Integration
**Files in scope:**
- frontend/src/tokens.ts
- frontend/src/index.css
- frontend/CLAUDE.md
- frontend/package.json
- frontend/.storybook/main.ts
- frontend/.storybook/preview.ts
- frontend/src/lib/contradictions.ts
- frontend/src/ui/PlayerChip.tsx
- frontend/src/stories/Tokens.stories.tsx
- .github/workflows/ci.yml
**Files NOT in scope:**
- api/ and the loader — Task 12.2 owns the DTO/contract and the `_COLOR_PALETTE` change
- frontend/src/components/MapView.tsx and the Pixi render layer — Task 12.5
- any belief / meeting / dashboard component — Waves B and C
- data/store wiring — no new fetches; the Zustand store is untouched here

Stand up the Playful design system in the repo so every later chrome slice composes from one source. Build
`frontend/src/tokens.ts` as the single token source, transcribed from the accepted 0b token sheet: paper/ink ramps,
`suspicion[]` + buckets (low ≤ .35 / high > .72), `trust`/`distrust` (blue↔orange), `kill` (#E23B2F), `contradiction`
(#D6249E), `status` (alive / dead / sabotage + contradiction-weak dashed / contradiction-strong solid), the 9-colour
`identity[]` (greens/teals/purples `#5DA83A…#A94FC6`), `truth` (ground solid / belief ghosted / noBelief hatch), plus
`radius`/`space`/`elevation`/`motion`/`type`. Resolve the seed's pseudo-code self-references (`fill:'identity'`,
`ink[500]`) into real TS. The SAME object feeds DOM and Pixi: emit Tailwind v4 `@theme` tokens (CSS custom properties)
for the DOM layer and a `pixiHex(token)` number helper for the canvas — zero magic constants in either. Encode the
density rule from the seed: the hard 2.5px-border / offset-shadow `elevation` is CHROME-only, data surfaces use a 1px
hairline (`elevation.data`). Flip `index.css` from `color-scheme: dark` to the cream/ink Playful base and load Fredoka +
Space Mono (self-hosted woff2 to avoid a render-blocking fetch). Install `design/phase-12/claude-design-brief.md`
verbatim as `frontend/CLAUDE.md`. Stand up Storybook with a story-per-component scaffold and a Tokens story that renders
the full sheet. Split the utilities smuggled into `ContradictionBadge.tsx` (`findContradictions`, `dedupeContradictions`,
the `PlayerChip`/`ObservationLine`/`ClaimLine` primitives, the id helpers) into `frontend/src/lib/contradictions.ts` +
`frontend/src/ui/`, updating imports. Add a frontend job to CI (`npm run build` + `tsc --noEmit`) — today CI builds only
the Python side, so the 859 kB chunk and any TS error are invisible. Use the `frontend-design` skill for distinctive,
non-templated visual choices.
**Definition of done:** `tokens.ts` is the single colour/space/type source consumed by both Tailwind (`@theme`) and a
`pixiHex` helper; `index.css` is the Playful cream/ink base with no `color-scheme: dark`; Fredoka + Space Mono load;
Storybook runs and renders the Tokens sheet plus ≥ 1 component story; `frontend/CLAUDE.md` is the installed brief; the
`ContradictionBadge` utilities live in `lib/`/`ui/` with imports updated and the tree still compiling; CI runs
`npm run build` + `tsc --noEmit` for the frontend and passes.

## Implementation hint
transcribe `tokens.ts` directly from the committed seed `design/phase-12/tokens-seed.md` (already structured); keep the
hard-shadow / 2.5px-border tokens namespaced as `chrome` so dense components can opt into the 1px `data` treatment;
prefer self-hosted fonts over a Google Fonts `<link>`.

## Integration risk
Tailwind v4 `@theme` ↔ `tokens.ts` wiring is new; the `ContradictionBadge` split touches files
other components import from (keep the tree compiling); the new frontend CI job will surface the pre-existing > 500 kB
chunk warning — record it, do not chase the code-split here (that is 12.11).

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
Open a PR from branch `phase-12-foundation` with a title like `task 12.1: foundation: design tokens, storybook, claude.md, ci`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §6, §9, §9.5; design/phase-12/claude-design-brief.md; **the committed 0b token sheet `design/phase-12/tokens-seed.md`** (transcribe `tokens.ts` from it — it is the in-repo source of truth, NOT the Downloads mockup); the Playful visual reference `design/phase-12/playful-system/playful-render.png` (Storybook + the cream theme should match it)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
