# Agent Prompt — 20.3 Layout and keyboard: the dock stops hiding the map; one owner for focus traps

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.3 — Layout and keyboard: the dock stops hiding the map; one owner for focus traps, anchored to audits/review-2026-08-19/B/frontend-a.md §2 F3 (register C-9; the row in audits/review-2026-08-19/B/collated-findings.md reads "two stacked focus traps lock the keyboard onto one control", repro `work/frontend-a/probe/trap.mjs` → `Tab -> tour:Skip (×4, never advances)`); audits/review-2026-08-19/A/ux-visual-pass-lead.md [VERIFIED — layout] (the fixed dock takes ~35% of a 900-px-tall viewport; the Mind Inspector is clipped behind it); audits/review-2026-08-19/C/p3-frontend-product-engineer.md §2 (canvas top 311 px vs dock top 308 px at the 1000×640 GIF recording viewport), §5 (map hidden at 1000×640, ~40 px clipped at 1280×800, clean at 1440×900), §7 item 10; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.3 and §1 RC8; register context C-79 and C-101 in audits/review-2026-08-19/B/collated-findings.md. Re-verified at HEAD by this contract: `frontend/src/hooks/useFocusTrap.ts:32-67` (the window-level Tab handler) with its `FOCUSABLE` string at :15-16; `frontend/src/components/GuidedTour.tsx:327-374` (the un-deleted inline copy — Escape and Tab in one effect; the duplicated selector string at :349; the review's 325-372 is the comment-inclusive span), its focus-on-open effect at :317-321, the re-open channel at :27 and :34, the dialog at :388 (`z-[90]`); `frontend/src/components/MeetingView.tsx:584` (`useFocusTrap(dialogRef, isOpen)`), its :581-583 comment stating the tour "runs its own trap", the Escape yield at :602, the modal at :653 (`z-50`); `frontend/src/components/BeliefMatrix.tsx:122` (the second consumer), :110 (Escape yield), :143-145 (it steps aside while a meeting is open), the dialog at :178 (`z-[80]`); the two launchers and the header gate in `frontend/src/App.tsx:250-261` (`aria-label="Open the guided tour"`, inside the nav), :353-382 (`aria-label="Open the Belief × Truth matrix"`, itself hidden while a meeting is open) and :1161 (the header, and with it the Tour button, is unmounted while a meeting is open); `frontend/src/App.tsx:1122-1138` (the fixed dock, `z-[70]`, with `MeetingPauseBar` / `AdvantageGraph` / `EventTimeline` in a `max-h-40` scroller / `ReplayControls`), :1027-1057 (`useTransportHeight` publishes `--transport-h`), the consumers at :1074, `frontend/src/components/MeetingView.tsx:654` and `frontend/src/components/ThoughtStream.tsx:131`, :601-612 (why `MeetingPauseBar` must stay the first child), :129-134 (the tour suppresses every transport accelerator), :145-165 (the activatable carve-out keyed on `[data-transport-region]`), :1-13 (the stale "WITHOUT ever editing this file" header claim); `frontend/src/index.css:14-100` (the generated `tokens:start`/`tokens:end` block), :162-166 (`.map-canvas-fill`, the map's only stable handle — `frontend/src/components/MapView.tsx:830`), :191-199 (the reduced-motion blanket); `frontend/vitest.config.ts:10-19` (`environment: "node"` declared a CONTRACT — a DOM test belongs in the journey); `frontend/playwright.config.ts:70` (the default 1440×960 viewport); `frontend/e2e/journey.spec.ts:29` and :48-50 (the tour-seen key), :63 and :67 (the `[data-transport-region]` and `canvas` handles), :254-300 (the keyboard-transport pins), :396-431 (the reduced-motion pins). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-dock-and-focus`
**Depends on:** 20.2 — the spectator copy pass settles the wording inside the same transport component, so this task moves that component's layout on top of a finished copy diff instead of racing it
**Section refs:** audits/review-2026-08-19/B/frontend-a.md §2 F3 (register C-9; the row in audits/review-2026-08-19/B/collated-findings.md reads "two stacked focus traps lock the keyboard onto one control", repro `work/frontend-a/probe/trap.mjs` → `Tab -> tour:Skip (×4, never advances)`); audits/review-2026-08-19/A/ux-visual-pass-lead.md [VERIFIED — layout] (the fixed dock takes ~35% of a 900-px-tall viewport; the Mind Inspector is clipped behind it); audits/review-2026-08-19/C/p3-frontend-product-engineer.md §2 (canvas top 311 px vs dock top 308 px at the 1000×640 GIF recording viewport), §5 (map hidden at 1000×640, ~40 px clipped at 1280×800, clean at 1440×900), §7 item 10; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.3 and §1 RC8; register context C-79 and C-101 in audits/review-2026-08-19/B/collated-findings.md. Re-verified at HEAD by this contract: `frontend/src/hooks/useFocusTrap.ts:32-67` (the window-level Tab handler) with its `FOCUSABLE` string at :15-16; `frontend/src/components/GuidedTour.tsx:327-374` (the un-deleted inline copy — Escape and Tab in one effect; the duplicated selector string at :349; the review's 325-372 is the comment-inclusive span), its focus-on-open effect at :317-321, the re-open channel at :27 and :34, the dialog at :388 (`z-[90]`); `frontend/src/components/MeetingView.tsx:584` (`useFocusTrap(dialogRef, isOpen)`), its :581-583 comment stating the tour "runs its own trap", the Escape yield at :602, the modal at :653 (`z-50`); `frontend/src/components/BeliefMatrix.tsx:122` (the second consumer), :110 (Escape yield), :143-145 (it steps aside while a meeting is open), the dialog at :178 (`z-[80]`); the two launchers and the header gate in `frontend/src/App.tsx:250-261` (`aria-label="Open the guided tour"`, inside the nav), :353-382 (`aria-label="Open the Belief × Truth matrix"`, itself hidden while a meeting is open) and :1161 (the header, and with it the Tour button, is unmounted while a meeting is open); `frontend/src/App.tsx:1122-1138` (the fixed dock, `z-[70]`, with `MeetingPauseBar` / `AdvantageGraph` / `EventTimeline` in a `max-h-40` scroller / `ReplayControls`), :1027-1057 (`useTransportHeight` publishes `--transport-h`), the consumers at :1074, `frontend/src/components/MeetingView.tsx:654` and `frontend/src/components/ThoughtStream.tsx:131`, :601-612 (why `MeetingPauseBar` must stay the first child), :129-134 (the tour suppresses every transport accelerator), :145-165 (the activatable carve-out keyed on `[data-transport-region]`), :1-13 (the stale "WITHOUT ever editing this file" header claim); `frontend/src/index.css:14-100` (the generated `tokens:start`/`tokens:end` block), :162-166 (`.map-canvas-fill`, the map's only stable handle — `frontend/src/components/MapView.tsx:830`), :191-199 (the reduced-motion blanket); `frontend/vitest.config.ts:10-19` (`environment: "node"` declared a CONTRACT — a DOM test belongs in the journey); `frontend/playwright.config.ts:70` (the default 1440×960 viewport); `frontend/e2e/journey.spec.ts:29` and :48-50 (the tour-seen key), :63 and :67 (the `[data-transport-region]` and `canvas` handles), :254-300 (the keyboard-transport pins), :396-431 (the reduced-motion pins)
**Complexity:** Medium
**Record impact:** none
**Measurement:** `cd frontend && npm run e2e` green with the two new steps, and each of them shown failing against the un-fixed code in the PR; `cd frontend && npm run test && npm run lint && npm run tsc:check && npm run build` green; the PR quotes the before/after `getBoundingClientRect` numbers at 1280×800 and 1000×640 beside the review's 311 px / 308 px.

Two defects meet on the one surface a stranger actually looks at. The first is a
keyboard lock: `useFocusTrap` and the inline copy `GuidedTour` never deleted both attach
their `keydown` listener to `window`, so whenever the tour is open over another overlay
BOTH run. On each Tab the lower dialog's trap sees focus outside itself and yanks it in;
the tour's trap then sees focus outside itself and yanks it back to its own FIRST
element. The review drove both handler bodies verbatim over a DOM shim and recorded
`Tab -> tour:Skip` four times running and `Shift+Tab -> tour:Next` four times running —
"Back" is unreachable by keyboard, and every keypress transiently parks focus inside the
scrim-covered overlay behind (audits/review-2026-08-19/B/frontend-a.md §2 F3). The
hook's own header says it was factored out of GuidedTour "so the meeting + belief
overlays share ONE implementation"; the extraction happened and the source was never
removed, down to a duplicated one-line `FOCUSABLE` selector. `MeetingView.tsx:581-583`
then documents the collision as if it were the design ("The guided tour, when open over
this, runs its own trap"). The Escape story is already correct — both overlays yield
Escape to the tour by reading `guidedTourOpen` — so this task gives Tab the same
single-owner treatment Escape already has.

The second is layout. The transport region is `fixed inset-x-0 bottom-0 z-[70]` and
stacks four surfaces inside it: the meeting pause bar, the advantage graph, a `max-h-40`
event-timeline scroller, and the transport proper. The visual pass measured it at ~35% of
a 900-px-tall viewport with the Mind Inspector clipped behind it; the product read
measured the map canvas starting at 311 px against a dock top of 308 px at 1000×640 —
the PixiJS map is entirely covered — and ~40 px clipped at 1280×800, clean only at
1440×900 (audits/review-2026-08-19/C/p3-frontend-product-engineer.md §2, §5). That is
why the README GIF, "the one asset most readers will ever see", shows a picker, a
timeline, a modal and a finale card, and never a moving agent. The dock earns its space
on a desktop and takes the whole product on a laptop, so the timeline half becomes a
disclosure that is closed by default below a documented viewport height.

The repair is cheaper than it looks because the measurement contract already exists:
`useTransportHeight` publishes the dock's real height as `--transport-h` via a
`ResizeObserver` (App.tsx:1027-1057) and three overlays consume it (App.tsx:1074,
MeetingView.tsx:654, ThoughtStream.tsx:131). Collapsing the timeline half shrinks the
measured height, and the map's padding, the meeting modal and the Mind rail all reflow
with no magic constants — which is also what un-clips the Mind Inspector the visual pass
complained about. Likewise the overlay z-order is already a stated contract (tour
`z-[90]` > belief `z-[80]` > transport `z-[70]` > finale `z-60` > mind rail `z-[55]` >
meeting `z-50`), so "which trap owns Tab" has a correct answer already written down; the
hook just has to read it.

Nothing here moves a recorded byte: no engine, agent, prompt or DTO code is touched, the
committed replays are untouched, and the four existing journey tests run at the config's
1440×960 viewport, which stays above the collapse threshold. Two constraints bound the
work. `frontend/vitest.config.ts:10-19` pins `environment: "node"` as a deliberate
contract and is out of scope, so the trap's pin is a Playwright keyboard step, not a
jsdom render test (this is exactly the gap C-101 names). And `frontend/src/index.css` is
GENERATED between its `tokens:start` (:14) and `tokens:end` (:100) markers from
`src/tokens.ts`, which is out of scope — a breakpoint written between the markers would
be erased by `npm run gen:tokens` and is read back off disk by `src/tokens.test.ts`, so
it goes in the hand-written region below :100.

**Files in scope:**
- frontend/src/hooks/useFocusTrap.ts; (the single-owner rule: only the top-most active overlay handles Tab)
- frontend/src/components/GuidedTour.tsx; (delete the inline trap copy; consume the hook or an overlay-stack owner)
- frontend/src/App.tsx; (the dock layout: collapsible / non-fixed below a height breakpoint)
- frontend/src/components/ReplayControls.tsx; (the collapsed-dock affordance)
- frontend/src/index.css; (breakpoint tokens only)
- frontend/e2e/journey.spec.ts; (a keyboard step: Tab reaches every tour control over an open meeting; map visible at 1280×800)

**Files NOT in scope:**
- frontend/src/components/MapView.tsx (20.1 owns it — the e2e addresses the map through the existing `.map-canvas-fill` class, never a new test id)
- any copy or tooltip string (20.2 owns the product wording; this task changes layout and keyboard behaviour, and the disclosure's label follows the vocabulary 20.2 landed — a plain inline label in ReplayControls.tsx beside its existing `aria-label`s, not a new key in `frontend/src/lib/copy.ts`; 20.2's dialect gate in `frontend/src/lib/copy.test.ts` now reads ReplayControls.tsx off disk, so `npm run test` bites on internal jargon in the new label)
- scripts/build_demo_bundle.py and frontend/e2e/bundle.spec.ts (20.7's bundle work — bundle.spec.ts asserts `[data-transport-region]` is visible and must stay green unchanged)
- frontend/src/components/MeetingView.tsx and BeliefMatrix.tsx (the two existing `useFocusTrap` call sites — they must keep compiling and behaving with no edit, which is the constraint on the hook's signature)
- frontend/src/store/replayStore.ts (no store field is added; the disclosure's state is component state in the workspace shell)
- frontend/vitest.config.ts and frontend/src/tokens.ts (the node-environment contract and the generated token source both stand)
- any Jinja prompt template, rendered prompt, replay or report byte (nothing this task touches reaches a recorded artifact)

**Definition of done:**
- [ ] Exactly one focus trap handles a Tab keypress at any moment: `useFocusTrap` acquires an explicit overlay ownership rule (top-most active overlay wins, matching the z-order contract the components already state) and the two existing call sites at `MeetingView.tsx:584` and `BeliefMatrix.tsx:122` compile and behave unchanged, with no edit to either file.
- [ ] `GuidedTour.tsx`'s inline Tab trap and its duplicated `FOCUSABLE` selector string are DELETED and the tour consumes `useFocusTrap`; the tour's Escape handling survives (both overlays still yield Escape to it via `guidedTourOpen`), and its redundant focus-on-open effect is removed rather than left beside the hook's.
- [ ] With the tour stacked over an already-open overlay, Tab cycles through every tour control including Back and Shift+Tab walks the same ring backwards, with focus never landing on a control inside the overlay behind — pinned by a new keyboard step in `frontend/e2e/journey.spec.ts` covering both stacks: the pointer-reachable Belief × Truth stack, and the meeting stack driven through the app's own re-open channel (the header carrying the Tour button is unmounted while a meeting is open, `App.tsx:1161`). The PR states which stack a user can reach by pointer today.
- [ ] The timeline half of the dock (the advantage graph and the event-timeline scroller) is CLOSED by default below a documented viewport-height breakpoint and open above it, toggled by a labelled disclosure control in `ReplayControls.tsx` with `aria-expanded`; the breakpoint value has ONE home in `frontend/src/index.css` below the `tokens:end` marker at :100, and the review's clean case (1440×900) stays expanded so the four existing journey tests are unaffected at the config's 1440×960 viewport.
- [ ] `MeetingPauseBar` remains the FIRST child of the measured column inside `[data-transport-region]` (App.tsx:601-612 makes that mount load-bearing for the ResizeObserver, the z-70 stacking and the accelerator carve-out), and `--transport-h` still measures the dock's real height in both states — asserted by the e2e reading the published property in the collapsed and expanded states.
- [ ] The map canvas is not covered by the dock at either measured viewport, asserted in the e2e from `getBoundingClientRect`: at 1280×800 the `.map-canvas-fill` box is entirely inside the viewport AND entirely above the dock's top edge; at 1000×640 it is entirely above the dock's top edge (the review measured canvas top 311 px against dock top 308 px there). The PR quotes both before and after numbers.
- [ ] Both new e2e steps are shown to BITE: the keyboard step fails against the un-fixed hook and the layout step fails against the un-collapsed dock, each demonstrated in the PR (craft rule 2).
- [ ] Reduced motion and the existing keyboard shortcuts are unchanged: `journey.spec.ts:254-300` and :396-431 pass untouched, the disclosure animates only through CSS transitions already collapsed by `index.css:191-199`, and the transport accelerators keep the same behaviour for a focused control inside `[data-transport-region]`.
- [ ] `App.tsx:1-13`'s claim that surfaces plug in "WITHOUT ever editing this file" is corrected to what is true now (craft rule 1, register C-79); no other restructuring of App.tsx is attempted.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — blast radius before scope (craft rule 6). `grep -rn "useFocusTrap" frontend/src`
returns exactly three sites at HEAD: the hook, `MeetingView.tsx:584`, and
`BeliefMatrix.tsx:122`. Both consumers are out of scope, so any parameter the hook grows
is OPTIONAL with a default and the two-argument calls keep compiling untouched. Grep
`--transport-h` and `data-transport-region` the same way before moving the dock — the
consumers are App.tsx:1074, MeetingView.tsx:654, ThoughtStream.tsx:131, the accelerator
carve-out at App.tsx:161, and both e2e specs.

Step 2 — the owner. The z-order is already written down in the components (tour 90 >
belief 80 > transport 70 > finale 60 > mind rail 55 > meeting 50), so give the hook an
optional overlay-layer argument defaulting to the base overlay layer, keep the set of
currently-active layers in one small explicit store created inside useFocusTrap.ts (a
zustand store or a useSyncExternalStore-backed registry — explicit state, not a mutable
module flag, the same reason GuidedTour's open state lives in the store), and let a
handler act only when its layer is the maximum active one. Ties break on registration
order, last registered wins, which matches DOM stacking for equal z; in practice a tie
cannot occur today because BeliefMatrix returns null while a meeting is open.

Step 3 — GuidedTour. Delete the Tab half of the :327-374 effect together with the
inline selector string at :349, keep the Escape half (it calls `finish()`, and both
overlays gate their own Escape on `guidedTourOpen`), and call the hook with the tour's
layer. The hook already focuses the dialog on open and restores focus on close, so the
separate focus effect at :317-321 goes too — except for the step-change dependency, which
is a one-line re-focus if the hook's open-only focus is not enough; do not reintroduce a
second listener to get it.

Step 4 — the dock. Only the advantage graph and the `max-h-40` timeline scroller
(App.tsx:1133-1136) move into the collapsible half; `MeetingPauseBar` stays first and
`ReplayControls` stays last. Own the open/closed flag as React state in `Workspace()`,
seeded once from `window.matchMedia`, and pass it plus a toggle callback down to
`ReplayControls` as props — replayStore.ts is out of scope and component state is the
smaller change. A user toggle wins over the media default for the rest of the session.
Nothing needs to touch `--transport-h`: the ResizeObserver republishes the smaller height
and every consumer reflows, which is the mechanism that un-clips the Mind Inspector.

Step 5 — the breakpoint. The review's own measurements bound it: clipped at 800 px tall,
clean at 900, so a threshold in between (around 860 px) collapses the broken cases and
leaves the clean one alone — and leaves the journey's 1440×960 default expanded, so the
four existing tests see today's layout. index.css is generated between :14 and :100 from
src/tokens.ts and is read back off disk by src/tokens.test.ts, so write the custom
property in the hand-authored region below :100 beside `.map-canvas-fill`, and read that
one value in the matchMedia query via `getComputedStyle(document.documentElement)` so the
number has a single home.

Step 6 — the journey. `openFeaturedReplay` suppresses the tour through
`localStorage` (:29, :48-50), so a stacked-trap step re-opens it deliberately. The
pointer-reachable stack is the Belief × Truth one: click the launcher
(`aria-label="Open the Belief × Truth matrix"`, App.tsx:362 — the journey already names
this control at :330) and then the nav's Tour button (`aria-label="Open the guided
tour"`, App.tsx:257). The meeting stack needs the tour's own re-open event
(GuidedTour.tsx:27, :34) because App.tsx:1161 unmounts the header, and the launcher gate
at App.tsx:353 hides the belief button, once a meeting is open. Both overlays and the
tour render `role="dialog"`, so disambiguate by a control each one owns — the tour's
`aria-label="Close the guided tour"` at GuidedTour.tsx:415 is stable across steps while
its `aria-labelledby` title is not. Read the focused control with
`page.evaluate(() => document.activeElement?.textContent)` after each Tab rather than
asserting on a locator's focus, and assert the whole visited ring, not just that Back is
reachable once. For the layout step use `setViewportSize` and the bounding boxes of
`.map-canvas-fill` and `[data-transport-region]`; no test id is added to MapView.tsx.

Step 7 — prove the gates bite before opening the PR. Stash the hook change and run the
keyboard step; stash the dock change and run the layout step; paste both failures. Then
quote the after numbers beside the review's 311 px canvas top / 308 px dock top so the
claim is verifiable-shaped rather than "the map is visible now".

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
Open a PR from branch `phase-20-dock-and-focus` with a title like `task 20.3: layout and keyboard: the dock stops hiding the map; one owner for focus traps`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/B/frontend-a.md §2 F3 (register C-9; the row in audits/review-2026-08-19/B/collated-findings.md reads "two stacked focus traps lock the keyboard onto one control", repro `work/frontend-a/probe/trap.mjs` → `Tab -> tour:Skip (×4, never advances)`); audits/review-2026-08-19/A/ux-visual-pass-lead.md [VERIFIED — layout] (the fixed dock takes ~35% of a 900-px-tall viewport; the Mind Inspector is clipped behind it); audits/review-2026-08-19/C/p3-frontend-product-engineer.md §2 (canvas top 311 px vs dock top 308 px at the 1000×640 GIF recording viewport), §5 (map hidden at 1000×640, ~40 px clipped at 1280×800, clean at 1440×900), §7 item 10; audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave-0 row 0.3 and §1 RC8; register context C-79 and C-101 in audits/review-2026-08-19/B/collated-findings.md. Re-verified at HEAD by this contract: `frontend/src/hooks/useFocusTrap.ts:32-67` (the window-level Tab handler) with its `FOCUSABLE` string at :15-16; `frontend/src/components/GuidedTour.tsx:327-374` (the un-deleted inline copy — Escape and Tab in one effect; the duplicated selector string at :349; the review's 325-372 is the comment-inclusive span), its focus-on-open effect at :317-321, the re-open channel at :27 and :34, the dialog at :388 (`z-[90]`); `frontend/src/components/MeetingView.tsx:584` (`useFocusTrap(dialogRef, isOpen)`), its :581-583 comment stating the tour "runs its own trap", the Escape yield at :602, the modal at :653 (`z-50`); `frontend/src/components/BeliefMatrix.tsx:122` (the second consumer), :110 (Escape yield), :143-145 (it steps aside while a meeting is open), the dialog at :178 (`z-[80]`); the two launchers and the header gate in `frontend/src/App.tsx:250-261` (`aria-label="Open the guided tour"`, inside the nav), :353-382 (`aria-label="Open the Belief × Truth matrix"`, itself hidden while a meeting is open) and :1161 (the header, and with it the Tour button, is unmounted while a meeting is open); `frontend/src/App.tsx:1122-1138` (the fixed dock, `z-[70]`, with `MeetingPauseBar` / `AdvantageGraph` / `EventTimeline` in a `max-h-40` scroller / `ReplayControls`), :1027-1057 (`useTransportHeight` publishes `--transport-h`), the consumers at :1074, `frontend/src/components/MeetingView.tsx:654` and `frontend/src/components/ThoughtStream.tsx:131`, :601-612 (why `MeetingPauseBar` must stay the first child), :129-134 (the tour suppresses every transport accelerator), :145-165 (the activatable carve-out keyed on `[data-transport-region]`), :1-13 (the stale "WITHOUT ever editing this file" header claim); `frontend/src/index.css:14-100` (the generated `tokens:start`/`tokens:end` block), :162-166 (`.map-canvas-fill`, the map's only stable handle — `frontend/src/components/MapView.tsx:830`), :191-199 (the reduced-motion blanket); `frontend/vitest.config.ts:10-19` (`environment: "node"` declared a CONTRACT — a DOM test belongs in the journey); `frontend/playwright.config.ts:70` (the default 1440×960 viewport); `frontend/e2e/journey.spec.ts:29` and :48-50 (the tour-seen key), :63 and :67 (the `[data-transport-region]` and `canvas` handles), :254-300 (the keyboard-transport pins), :396-431 (the reduced-motion pins)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
