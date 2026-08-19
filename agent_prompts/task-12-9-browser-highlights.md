# Agent Prompt — 12.9 Replay browser + Highlights reel

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.9 — Replay browser + Highlights reel, anchored to design/phase-12/stage-1-design.md §3.1, §2.1, slice 7; the firewall rules in `design/phase-12/claude-design-brief.md`. No converge screen exists for this top-level surface — it needs a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-browser-highlights`
**Depends on:** 12.1, 12.2
**Section refs:** design/phase-12/stage-1-design.md §3.1, §2.1, slice 7; the firewall rules in `design/phase-12/claude-design-brief.md`. No converge screen exists for this top-level surface — it needs a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/HighlightCard.tsx
- frontend/src/components/ReplayFilters.tsx
- frontend/src/stories/ReplayBrowser.stories.tsx
**Files NOT in scope:**
- frontend/src/App.tsx — the Replays + Highlights routes already mount `<ReplayPicker/>`; rebuild the component, don't edit the shell (Wave-B mount discipline)
- api/ and the loader — the `/replays` list + `/eval/rubric` (`RubricView` / `RubricGameView`) already ship from 12.2; no DTO change, no re-record
- the map / belief / meeting / inspector surfaces — other slices

Rebuild the two top-level views the App.tsx routes mount through `<ReplayPicker/>`: the **Replays browser** and the
**Highlights reel**. A **HighlightCard** (from `RubricGameView`): a 0–100 **score** badge (decoupled from who won), the
**win-shape** tag, a **drama** line (n_meetings · accused / ejected impostors · survived-accused), and a 4-spoke mini
**sub-score** bar (R1 / R2 / R3 / R7). The **Highlights** reel defaults to the rubric's `interestingness` `per_game[]`
sorted best-first (**9p2i**). A **filter bar** that is **URL-driven** — it reads + syncs the shared query keys `set` · `winner` · `winShape` ·
`scoreBucket` (low/med/high) · `hasEjection` (the same URLSearchParams pattern as 12.4, so a filtered reel is shareable +
reload-stable and 12.10's histogram deep-links land on the right filter — 12.10 builds links with exactly these keys).
**Clicking a card opens that replay** — it sets the 12.4 store's `game_id` (which loads the replay) and switches to the
Replay Workspace at tick 0. And **first-class
empty / zero-meeting states** — the default-served **4p1i** set has no rubric and is mostly zero-meeting, so an empty /
zero-meeting card is the COMMON case there, not an edge: render a real state, never a broken panel. Firewall: identity ≠
guilt, and outcomes stay role-neutral (the card keys on drama / score, never on who won). Data-bound — wire to `/replays`
(the list) + `/eval/rubric` (`RubricView`, respecting its staleness guard). The chrome (HighlightCard, filter bar, empty
state) comes from a NEW Claude-Design pass: *"Design the replay browser + highlights reel: a HighlightCard (0–100 score
badge, win-shape tag, drama stats, a 4-spoke mini sub-score bar), a filter bar, and a prominent empty / zero-meeting
state; states loading / list / empty / error; identity ≠ guilt, outcomes role-neutral; presentational only, tokens
only"* → Share → Handoff to Claude Code → integrate.
**Definition of done:** the Replays browser + Highlights reel render via the existing `ReplayPicker` slot; HighlightCards
show score / win-shape / drama / 4-spoke sub-scores from `RubricGameView`; the reel sorts by `interestingness` (9p2i); the
filter bar is URL-driven over the shared keys `set` / `winner` / `winShape` / `scoreBucket` / `hasEjection` (reads + syncs them — shareable / reload-stable); clicking a card opens that replay (sets the 12.4 store `game_id`, switches to the Workspace at tick 0); a first-class empty / zero-meeting state handles the
4p1i + single-meeting cases; loading / list / empty / error states render; identity ≠ guilt and outcomes role-neutral; a
Storybook story covers loading / list / empty / error; `npm run tsc:check` + `npm run build` pass and `scripts/check.sh`
is green; `App.tsx` is untouched.

## Implementation hint
rebuild `ReplayPicker` in place; build `HighlightCard` from `RubricGameView` (`score`, `win_shape`, `n_meetings`, the
four sub-scores). The reel is `RubricView.per_game` (already sorted best-first); the browser list is `/replays`. Respect
the `RubricView` staleness guard (banner when `git_head` mismatches; never render stale scores as fresh), and build the
zero-meeting / 4p1i empty state first — do not assume rubric data exists.

## Integration risk
the 4p1i default set has no rubric and is mostly zero-meeting, so the empty / zero-meeting state is the COMMON path there,
not an afterthought. Score is decoupled from the winner — never colour a card by who won (outcomes are role-neutral, a
firewall rule). `RubricView` can be stale (a `git_head` mismatch) — show the staleness banner rather than passing stale
scores off as fresh. No converge screen — verify the chrome against the brief, not a screenshot. Don't edit `App.tsx`
(mount discipline).

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
Open a PR from branch `phase-12-browser-highlights` with a title like `task 12.9: replay browser + highlights reel`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §3.1, §2.1, slice 7; the firewall rules in `design/phase-12/claude-design-brief.md`. No converge screen exists for this top-level surface — it needs a NEW Claude-Design pass (a focused prompt → Handoff, grounded on the brief + `tokens-seed`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
