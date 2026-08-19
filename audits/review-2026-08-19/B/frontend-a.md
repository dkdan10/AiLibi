# Code review — `frontend/src/components` + `hooks` + `lib` (label: **frontend-a**)

Reviewer track: CODE-UP (structure, tests, measured behaviour). Read-only; nothing in the repo was
modified. All commands run from `/Users/danielkeinan/projects/AiLibi`. Machine load recorded with each
timing (`uptime` load ≈ 4.5–6.9 throughout — other reviewers were running concurrently).

Scratch artefacts (probes, dumped fixtures):
`/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/frontend-a/`

---

## 1. Executive read (10 lines)

1. This is **good frontend code by the standards of AI-authored codebases** — strict TS with
   `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes`, **zero `any`, zero `@ts-ignore`**, tokens
   instead of hex, and exactly **two** `exhaustive-deps` suppressions in ~12 k lines.
2. `lib/playback.ts` is the standout: one tick↔frame resolver, pure, and it survived a fuzz over all 50
   committed 9p2i replays with **0 invariant failures** (§2 G1).
3. `EventTicker` is the model component: firewall-aware pure projection, memoized once per
   replay/perspective, O(1) per frame, 759 lines of behaviour tests.
4. The one real correctness bug I found is in the map: **`MapView` paints corpses the engine has already
   consumed**, on **1182 / 1769 frames (67 %) of every one of the 50 committed replays** (§2 F1) — and it
   does so by re-deriving a body set the DTO already serves.
5. A second real bug: `TournamentDashboard` hand-rolls a `fetch` for `/eval/rubric` and thereby **bypasses
   the view-model-version guard** that `api/client` exists to enforce — for one of the only two stamped
   payloads (§2 F2).
6. A third: two focus traps stacked (GuidedTour over an open MeetingView) **pin Tab to one element and make
   the tour's "Back" button unreachable by keyboard** — reproduced (§2 F3).
7. Structure is the weak axis: five files ≥ 690 lines, `TournamentDashboard.tsx` at 1085 lines with 30
   top-level declarations; `MindInspector.tsx` and `MapView.tsx` at 938 each.
8. Duplication is real and already **divergent** in one case: `playerColor` ×3, `scoreBucketOf` +
   thresholds ×2 (both copies documented as "a SHARED contract"), two evidence style tables that already
   disagree on a label.
9. Testing is the biggest structural gap: **`vitest.config.ts` pins `environment: "node"` as a "CONTRACT"**,
   so there is not one component render test. 30 of 32 components and both hooks have no unit test at all;
   the 4-test Playwright journey is the only coverage of every effect, trap, and ARIA decision.
10. Perf is fine *at current data scale* (measured: 0.022 ms per hover-move on the longest real replay) but
    the Pixi layer has avoidable per-frame churn and the hover path is O(markers × ticks) (§2 F6, F12).

---

## 2. Findings

Severity: **P0** correctness/security/data-loss · **P1** real defect or serious maintainability/perf ·
**P2** quality/cleanup. Tags: **[VERIFIED]** = I ran/observed it · **[JUDGMENT]** = reasoned from code.

### F1 — P1 · [VERIFIED] · confidence **high** — the Omniscient map paints bodies that no longer exist

`frontend/src/components/MapView.tsx:227-264` (`buildBodyStatesByTick`), consumed at `:570`, `:591`,
`:734-735`.

**What is wrong.** `buildBodyStatesByTick` builds the body layer by *accumulating* `kill` events and never
removing anything: a `report_body` only flips `isDiscovered`. But `orchestrator/game.py:1256-1259`
**deletes** the reported corpse from `WorldState.bodies` when the body-report meeting resolves ("Consume the
corpse that triggered a body-report meeting"). The served DTO reflects that — `TickView.bodies`
(`api/replay_loader.py:2568 _bodies_view`) projects exactly the bodies still on the floor, with the
privileged `killed_by`. `MapView` never reads it.

So after the first body-report meeting the map keeps a marker — drawn with `BodyMarker`'s *discovered*
treatment, whose own comment calls it "Outer kill ring marks a **freshly reported** body"
(`BodyMarker.tsx:124-127`) — for the rest of the replay, on a tile where nothing is.

**Why it matters.** The file header calls this layer "Omniscient ground truth" (`MapView.tsx:227`) and the
Phase-12 design says the body layer should be sourced from `state.bodies`:

> `design/phase-12/stage-1-design.md:83` — "persistent body attribution via a new `killed_by` projection
> from `state.bodies`."

That projection was built (`TickView.bodies[].killed_by`), `BodyMarker.tsx:36-38` cites it as its source —
and **MapView re-derives `killedBy` from the kill event instead** (`MapView.tsx:258`), so the served field
is dead. This is doc-vs-code drift *and* a wrong render on the app's primary surface, in its default
perspective. It also corrupts the per-room layout logic downstream (`bodiesFit` / `BODY_CAP` collapse).

Note the As-agent path is **correct** (`MapView.tsx:736-745` reads `visibility.visible_bodies`), so
Omniscient and fog disagree about whether a body is on the floor — which reads as a fog artefact.

**Evidence** — probe over all 50 committed `replays/samples/9p2i` games, re-running MapView's derivation
verbatim against the served `TickView.bodies`
(`…/work/frontend-a/probe/probe.mjs`, `probe2.mjs`, `probe3.mjs`, `probe5.mjs`):

```
{ totalFrames: 1769, phantomFrames: 1182, missingFrames: 0,
  gamesWithPhantom: 50, gamesTotal: 50, maxPhantomRun: 57, phantomBodyInstances: 2426 }
worst games [game, framesWithPhantomBody, totalFrames]:
  [ 'headless-seed-21', 57, 69 ], [ 'headless-seed-17', 55, 63 ], [ 'headless-seed-8', 51, 61 ]

# every phantom is a consumed corpse — not one is unexplained:
{ phantomWithReport: 2426, phantomWithoutReport: 0 }

# downstream effect on the room-grid collapse:
{ total: 1769, framesWithInflatedRoomCount: 1182, framesWithFalseCollapse: 4 }
```

Concrete instance, `headless-seed-0` tick 18: served bodies `[]`, MapView draws `["p-2"]`.

**Fix.** Read `tick.bodies` (it already carries `victim_id` / `room_id` / `killed_by`) and delete
`buildBodyStatesByTick` (~45 lines) and the `NO_BODIES` / `BodySpec` scaffolding. If a persistent
crime-scene marker is *wanted*, keep it — but source it from `tick.bodies` for "on the floor now" and draw
the removed ones in a visibly different, clearly-not-a-body treatment, and stop calling the layer
"ground truth". Either way `isDiscovered` needs to stop meaning "freshly reported" forever.

---

### F2 — P1 · [VERIFIED] · confidence **high** — a raw `fetch` defeats the view-model version guard

`frontend/src/components/TournamentDashboard.tsx:1025-1060` (and, less severely,
`frontend/src/components/BeliefMatrix.tsx:33-49`).

**What is wrong.** `api/client.ts`'s `getJson` runs `assertViewModelVersion` before the `as T` cast — the
one runtime check standing between a version-skewed server and silently-wrong UI
(`api/client.ts:134-159`). Its own docstring names the two stamped payloads:

> `api/client.ts:103-112` — "The server stamps only the payloads whose DTO declares the field
> (`ReplayView`, `RubricView`)…"

`RubricView` is indeed stamped (`api/schemas.py:1291-1292`). `api/client.ts:319` exports `getRubric(set?)`.
**`GuidedTour.tsx:66` and `ReplayPicker.tsx:613` both call it. `TournamentDashboard.tsx:1028` re-implements
the same request with a bare `fetch(apiUrl("/eval/rubric", seedSet))`** and its own ad-hoc 404 handling —
skipping the version assertion, the `ApiError` typing and the "invalid JSON" branch.

**Why it matters.** One endpoint, three call sites, and the *only* one that skips the guard is the one that
renders 1000 lines of statistics. Against a server on a different `VIEW_MODEL_VERSION`, the tour and the
browser fail loud (as designed) while the dashboard renders whatever it gets. That is exactly the "silent
fallback" the repo's own AGENTS.md forbids.

`BeliefMatrix.fetchBeliefFrames` is the same shape (`/replays/{id}/beliefs`); that payload is *not* stamped,
so it only loses the shared error handling — P2 on its own, but it is the second of only two raw fetches.

**Evidence.**
```
$ grep -rn 'fetch(' frontend/src --include='*.tsx' --include='*.ts' | grep -v src/api/client | grep -v '.test.'
frontend/src/components/BeliefMatrix.tsx:42:  const res = await fetch(url, {
frontend/src/components/TournamentDashboard.tsx:1028:    fetch(apiUrl("/eval/rubric", seedSet), {
$ grep -n '^export function getRubric' frontend/src/api/client.ts
319:export function getRubric(set?: string): Promise<RubricView> {
```

**Fix.** Replace the dashboard's `fetch` with `getRubric(seedSet)` + `err instanceof ApiError && err.status === 404`
— i.e. copy `ReplayPicker.tsx:610-630`, which already does exactly this. Add a `getBeliefFrames` to the
client for the matrix. Then the guard is unbypassable by construction.

---

### F3 — P1 · [VERIFIED] · confidence **high** — two stacked focus traps lock the keyboard onto one control

`frontend/src/hooks/useFocusTrap.ts:32-67` (used by `MeetingView.tsx:571` and `BeliefMatrix.tsx:122`) and
`frontend/src/components/GuidedTour.tsx:325-372` (a verbatim inline copy of the same logic).

**What is wrong.** Both traps attach their `keydown` handler to **`window`**, and both are active
simultaneously when the tour is opened over an open meeting (the header "Tour" button explicitly "does NOT
reload the replay — it annotates whatever the user is already watching", `GuidedTour.tsx:298-300`; only
`BeliefMatrix` steps aside for a meeting, `BeliefMatrix.tsx:143-145`). On each Tab, the meeting's trap sees
focus outside *its* dialog and yanks it in; the tour's trap then sees focus outside *its* dialog and yanks
it back to the tour's **first** element. Net effect: Tab is a no-op that always lands on "Skip", Shift+Tab
always lands on "Next" — **"Back" is unreachable by keyboard**, and every keypress transiently moves focus
into the scrim-covered meeting.

**Evidence** — repro driving both handler bodies (copied verbatim) over a minimal DOM shim,
`…/work/frontend-a/probe/trap.mjs`:

```
Scenario: guided tour opened over an already-open meeting.
start focus: tour:Skip
  Tab       -> tour:Skip      (×4, never advances)
  Shift+Tab -> tour:Next      (×4, never advances)

Single trap (tour only, the intended behaviour):
  Tab -> tour:Skip / tour:Back / tour:Skip …   (cycles)
```

**Secondary finding, same code.** `useFocusTrap`'s own header says it was "Factored from GuidedTour's
inline trap (task 12.13 a11y) so the meeting + belief overlays share ONE implementation" — but
**GuidedTour still carries the original copy**, including a duplicated 1-line `FOCUSABLE` selector string
(`useFocusTrap.ts:15-16` vs `GuidedTour.tsx:346-348`). The extraction was done and the source never deleted.

**Fix.** (a) Delete GuidedTour's inline trap and call `useFocusTrap(stepRef, open)`. (b) Make the trap
yield: only the top-most open dialog should act — either scope the listener to the dialog element (Tab
bubbles) or gate on a small "top-most overlay" selector the same way Escape is already gated on
`guidedTourOpen` (`MeetingView.tsx:589`, `BeliefMatrix.tsx:110`). The Escape story is already correct; the
Tab story just never got the same treatment.

---

### F4 — P2 · [VERIFIED] · confidence **high** — "shared contract" constants are duplicated, and one table has already diverged

| symbol | copies |
|---|---|
| `playerColor(agentId, players)` | `MeetingView.tsx:43`, `TurnCard.tsx:53`, `BallotCard.tsx:108` (identical) |
| `scoreBucketOf` + `SCORE_BUCKET_LOW_MAX/HIGH_MIN` | `ReplayFilters.tsx:57-64` (**exported**), `TournamentDashboard.tsx:77-84` (private copy) |
| `EvidenceCategory` + `EVIDENCE_RANK` + the style table | `MeetingView.tsx:334-393`, `TurnCard.tsx:105-144` |
| `formatInt` | `CostChips.tsx:154`, `TournamentDashboard.tsx:65` |
| `Empty` | `MeetingView.tsx:70`, `MemoryPanel.tsx:45` |
| `Loading` / `EmptyState` | `ui/Loading.tsx` + `ui/EmptyState.tsx` **shadowed by** private copies in `BeliefPanel.tsx:747,768` |

The bucket case is the sharp one: **both copies carry a comment declaring the boundary a shared contract**
and neither shares it.

> `ReplayFilters.tsx:53-56` — "This boundary is a **shared contract**: 12.10's interestingness histogram
> deep-links into the reel with `scoreBucket=<bucket>`, so its bins MUST collapse onto the same split."
>
> `TournamentDashboard.tsx:70-72` — "The histogram's buckets ARE the deep-link units, so they map 1:1 onto
> `scoreBucket`."

`TournamentDashboard.highlightsHref()` builds a URL that `ReplayFilters` parses; the two thresholds are
currently equal only because nobody has edited one.

The evidence tables have **already diverged**: the same `weak_signal` category is labelled `"weak signal"`
in `MeetingView.tsx:381` and `"weak"` in `TurnCard.tsx:132`, on surfaces the reader sees side by side.

**Fix.** `lib/evidence.ts` (category rank + one style table), `lib/players.ts` (`playerColor`,
`playerName`), import the exported `scoreBucketOf`, delete `BeliefPanel`'s shadowing `Loading`/`EmptyState`.

---

### F5 — P2 · [VERIFIED] · confidence **high** — the ESLint "legacy ledger" disables whole rules for whole files

`frontend/eslint.config.js:80-125`. The ledger is a genuinely good idea (documented, reviewable, honest),
but it is implemented as `files: [<one file>], rules: { <rule>: "off" }` — so the rule is off for the
**entire file**, not for the one line the comment describes. `TurnCard.tsx` (381 lines) is blind to
`@typescript-eslint/no-unused-vars`; `BeliefMatrix.tsx` (205 lines, 3 effects) is blind to
`react-hooks/exhaustive-deps` though only the third effect is the documented exception.

**Evidence** — re-running the same rules from a scratch config with the ledger removed
(`…/work/frontend-a/probe/eslint.probe.mjs`, `eslint.hooks.mjs`; no repo file touched):

```
src/components/BeliefMatrix.tsx
  118:6  error  React Hook useEffect has a missing dependency: 'setOpen'.  react-hooks/exhaustive-deps
src/components/TurnCard.tsx
  196:3  error  'players' is defined but never used   @typescript-eslint/no-unused-vars
✖ 2 problems
```

The dead prop is exactly the one the ledger describes (`TurnCard.tsx:194-198` + its call site at `:329`) —
a genuinely 2-line fix that has now outlived the task that deferred it. Good news: **nothing else** is
hiding behind the ledger.

**Fix.** Both are one-line changes. Delete the `players` prop and its call site; add `setOpen` to the
`BeliefMatrix` dep array (it is a stable Zustand action, so it is a no-op). Then delete the ledger and the
~45 lines of comment justifying it.

---

### F6 — P2 · [VERIFIED mechanism / JUDGMENT impact] · confidence **high** — avoidable per-frame churn in the Pixi layer

Three separate issues on the 60 Hz path:

**(a) inline `useTick` callbacks re-register a ticker listener every render.** `@pixi/react`'s `useTick`
lists `callback` in its effect deps:

```js
// node_modules/@pixi/react/dist/pixi-react.mjs:29889-29910
useIsomorphicLayoutEffect(() => { … ticker.add(callback, context, priority);
  return () => { ticker?.remove(previousCallback, previousContext); }; },
  [app?.ticker, callback, context, isEnabled, isInitialised, priority]);
```

`AgentToken.tsx:145-164` does the right thing (`useCallback(advance, [])` → registered once).
`MapView.tsx:332` (`VentTraveler`) and `MapView.tsx:468` (`KillFlash`) pass **inline arrows** *and*
`setState` every frame — so each rendered frame is a `ticker.remove` + `ticker.add` pair. The correct
pattern is present in the same repo, three files away.

**(b) `KillFlash` never stops.** `MapView.tsx:466-476` calls `setAlpha(...)` on **every** tick with no
terminating condition, so parking the playhead on a kill tick drives a React render loop indefinitely; even
the reduced-motion branch (`:469-471`) calls `setAlpha(0.85)` every frame instead of bailing.

**(c) every `pixiText` allocates a new `TextStyle` per render.** All 8 `pixiText` nodes
(`AgentToken.tsx:207`, `RoomRect.tsx:129,162`, `BodyMarker.tsx:130,145`, `MapView.tsx:378,443`,
`SabotageOverlay.tsx:166`) pass an **object literal** as `style`. `@pixi/react` diffs object props by
**reference**:

```js
// pixi-react.mjs:536-555  isEqual(..., { arrays:"reference", objects:"reference", strict:true })
if (isInputAAnObject && objects === "reference") { return inputA === inputB; }
```

…so `style` is always "changed", and Pixi's setter then **constructs a new `TextStyle` and invalidates the
text**:

```js
// node_modules/pixi.js/lib/scene/text/AbstractText.js:179-189
set style(style) { … this._style = new this._styleClass(style); … this.onViewUpdate(); }
```

During a 9-token move tween that is ~540 `TextStyle` constructions + re-measures per second, all for
constant styles.

**Impact honesty.** I could not run a browser (no cached Playwright Chromium; installing one would touch
the network), so I have not measured frame time. At the shipped scale (10 rooms, 9 tokens, 1080×370) the
absolute cost is probably small — which is why this is P2, not P1. The mechanism is certain and the fix is
trivial.

**Fix.** Hoist the 8 style objects to module constants; wrap the two inline tick callbacks in
`useCallback([])`; give `KillFlash` a bail (`if (prefersReducedMotion) return;` once, and a
`Math.abs(next-prev) < 0.01` early-out).

---

### F7 — P2 · [VERIFIED] · confidence **high** — no component-level tests exist, by configuration

```
components:  32 .tsx,  2 test files
hooks:        2 .ts,   0 test files
lib:          2 .ts,   1 test file
```

`vitest.config.ts:11-24` pins `environment: "node"` and calls it "a CONTRACT, not a default we drifted
into", deferring every DOM-shaped test to Playwright. The two component tests
(`EventTicker.test.ts` 759 lines, `CostChips.test.ts` 236 lines) exercise **exported pure projections**,
never a render.

Consequence: everything React-shaped in this area is unit-untested — the focus traps (F3 found a real bug
there), the roving tabindex in `MindInspector.tsx:517-548`, the meeting/agent drawer effects in
`ThoughtStream.tsx:77-88`, the whole of `usePlaybackEngine` (the auto-advance timer, the meeting pause, URL
hydration and the debounced write-back — the most stateful code in the app), and every ARIA decision.
`lib/contradictions.ts` also has no test.

The Playwright journey is good (4 real-browser tests: featured replay → pause → ballots → finale; keyboard
transport; As-agent fog leak check; reduced motion) but it needs a browser download and two servers, so it
is not part of a routine local loop.

**Fix.** Add `jsdom`/`happy-dom` as a *second* vitest project (keep the fast node project as-is) and pin
the four things F3-class bugs live in: focus-trap composition, the tabs keyboard pattern, the
`usePlaybackEngine` timer/pause, and the URL round-trip through `mergePlaybackSearch`.

---

### F8 — P2 · [VERIFIED] · confidence **high** — God modules

```
1085  components/TournamentDashboard.tsx   (30 top-level declarations in one file)
 938  components/MindInspector.tsx         (panel + connected wrapper + 8 sub-components + 4 derivations)
 938  components/MapView.tsx               (5 sub-components + 5 pure derivations + the connected stage)
 784  components/BeliefPanel.tsx           (18 top-level declarations)
 769  components/ReplayPicker.tsx          (browser + highlights + featured strip + set selector + filters)
 687  components/MeetingView.tsx
 676  components/ReplayControls.tsx        (3 unrelated exported surfaces)
```

These are not accidental — each grew one Wave/Task at a time — but they are now where the duplication in F4
comes from (two evidence tables exist because the meeting file was already too big to open). The pure
derivations at the top of `MapView.tsx` (`computeTransform`, `buildVentEdges`, `buildVentSegments`,
`buildBodyStatesByTick`, `normalizeRoomKey`) are testable pure functions trapped in a `.tsx` the node-only
vitest project cannot import — which is precisely why F1 went unnoticed.

**Fix (highest value first).** Move `MapView`'s derivations to `lib/mapDerivations.ts` and test them (that
alone would have caught F1). Split `TournamentDashboard.tsx` into `components/dashboard/*` by section
(balance / vote-correctness / conversion / gate / deduction / calibration / cost / rubric). Split
`MindInspector.tsx` into `MindInspectorPanel.tsx` + `MindInspector.tsx` (connected) + `mind/tabs/*`.

---

### F9 — P2 · [VERIFIED] · confidence **medium** — React-Compiler lint flags a real (if benign) hazard class

The repo enables only `rules-of-hooks` + `exhaustive-deps`. Running the rest of `eslint-plugin-react-hooks@7`
(already installed) from a scratch config surfaces 24 findings, of which two classes matter:

```
src/components/MapView.tsx:524,525  [react-hooks/refs] Cannot access refs during render
src/components/MapView.tsx:598,722,803,820  [react-hooks/refs]   (the same value flowing into JSX)
src/components/AgentToken.tsx:138   [react-hooks/set-state-in-effect]
src/components/BeliefMatrix.tsx:74,86 · GuidedTour.tsx:273 · ReplayPicker.tsx:611
src/components/ThoughtStream.tsx:78,86 · TournamentDashboard.tsx:1027 · App.tsx:846
```

- **`MapView.tsx:522-530`** implements "previous tick" by reading `prevTickRef.current` **during render**
  and writing it in an effect. Under concurrent rendering a discarded render can leave the ref
  inconsistent; the blast radius here is only a wrong `animate` flag (a snap instead of a tween), so it is
  cosmetic — but it is the pattern React's own tooling calls out. `useState`-based previous-value, or
  deriving `animate` from a `[prevTick, tick]` state pair, removes it.
- **`AgentToken.tsx:128-143`** — the snap branch calls `setPos(target)` synchronously in an effect, forcing
  a second render on every mount and every `animate` flip (9 tokens × every scrub).
- **`BeliefMatrix.tsx:73-76`** is derived state in an effect (`setFrames(null)` on replay/set change); a
  `key={`${gameId}:${seedSet}`}` on the panel expresses it without the extra commit.

**Fix.** Consider adding `react-hooks/set-state-in-effect` + `react-hooks/refs` to `eslint.config.js` at
`warn`. They are already installed; there is no new dependency.

---

### F10 — P2 · [VERIFIED] · confidence **high** — accessibility gaps on the two interactive scrubbers, and none at all on the canvas

- **`ReplayControls.tsx:256-319`** puts `role="slider"` on a `<div>` that **contains `<button>`
  descendants** (`MarkerChip`, `:300-316`). ARIA `slider` takes presentational children — the marker
  buttons are not reliably exposed, and the composite is invalid. Split it: a real slider element plus a
  sibling, absolutely-positioned marker list.
- **`ReplayControls.tsx:368-390`** (`EventTimeline`) attaches `onClick` (seek) and `onMouseMove`
  (crosshair) to a plain `<div>` grid with **no role, no `tabIndex`, no keyboard handler**. Mouse-only.
  (The per-marker `MarkerChip` buttons *are* reachable, so this is a degraded path, not a total block.)
- **The Pixi canvas has no accessible representation at all** — `MapView.tsx:895-960` renders `<Application>`
  with no `aria-label`, no `role`, no text alternative, and Pixi's accessibility system is not enabled;
  agent tokens are reachable only by pointer (`AgentToken.tsx:172-176`). The `AgentSelector` and the
  `EventTicker`'s `role="status"` live region (`EventTicker.tsx:626-631`) partially compensate, which is
  why this is P2 rather than P1 — but the app's central surface is invisible to assistive tech.
- `MindInspector.tsx:663-664` hardcodes `id="mind-tabpanel"` / `id={`mind-tab-${id}`}`, which collide if
  two inspectors ever mount (the panel is exported and used by Storybook).

**Good, for balance:** the roving-tabindex tabs (`MindInspector.tsx:517-548`), the `aria-pressed` toggles,
the `role="meter"` suspicion bars (`MindInspector.tsx:203-209`), the `sr-only` live region scoped to *only
the arriving frame* (`EventTicker.tsx:600-631` — a genuinely thoughtful decision), and the `inert` gate on
the collapsed drawer (`ThoughtStream.tsx:109,130`) are all above-average work.

---

### F11 — P2 · [VERIFIED] · confidence **high** — served DTO fields the frontend never reads

```
$ grep -rn '\.bodies\b|sabotage_active' frontend/src --include='*.tsx' --include='*.ts' | grep -v types/api | grep -v test | grep -v stories
(no results)
```

`TickView.bodies` and `TickView.sabotage_active` are computed, serialized on every one of ~1769 frames per
set, shipped in a ~930 kB payload, and read by nothing outside fixtures. `TickView.bodies` should become
live (F1); `sabotage_active` is superseded by `TickView.sabotage` and is a candidate for deletion on the
API side. Worth flagging to the api/ reviewer.

---

### F12 — P2 · [VERIFIED] · confidence **high** — the hover crosshair is O(markers × ticks); fine now, latent later

`AdvantageGraph` and `EventTimeline` both subscribe to `hoverTick`, so **every pointer move over either
re-renders both**, rebuilding the full polyline string and calling `frameIndexForTick` (a linear scan) once
per marker.

**Measured** (`…/work/frontend-a/probe/probe4.mts`, node 26, `uptime` load 6.49):

```
real longest (9p2i seed-21): ticks=69  markers=21  advantageRender=0.015ms timelineRender=0.007ms
synthetic x10:               ticks=690 markers=210 advantageRender=0.114ms timelineRender=0.213ms
synthetic x40:               ticks=2760 markers=840 advantageRender=0.445ms timelineRender=2.292ms
```

At today's replay lengths (14–69 ticks; measured across all 50 games) this is **0.022 ms per hover move** —
a non-issue, and I want to be explicit that the memoization here is *not* currently load-bearing. At 40×
it is 2.7 ms per move, i.e. ~30 % of a core at a 120 Hz pointer. Cheap prophylactics: memoize
`points`/`fractions` on `[replay]`, and build a `Map<tick, index>` once instead of scanning.

---

### F13 — P2 · [VERIFIED] · confidence **high** — sub-`xs` type sizes bypass their own tokens in a third of uses

`tokens.ts:136` defines `size: { "4xs": 9, "3xs": 10, "2xs": 11 }` and `index.css:97-99` emits
`--text-4xs/3xs/2xs`. Yet:

```
arbitrary px that DUPLICATE a named token (text-[9px] / text-[10px] / text-[11px]): 34  in 12 files
named-token uses (text-4xs / text-3xs / text-2xs):                                  75
```

Same numbers, two spellings, in files that sit next to each other (`GuidedTour`, `BallotCard`,
`TurnCard`, `MemoryPanel`, `TournamentDashboard`, …). Everything else about the token discipline is
excellent — **zero raw hex in any component** — which makes this the one visible seam.

---

### F14 — P2 · [VERIFIED] · confidence **high** — smaller items

- **`MeetingView.tsx:128-135`** defines the `Disc` component *inside* `AccusationChainSummary`'s render, so
  it is a new component type on every render and React remounts the subtree. Impact is low (the parent
  re-renders rarely) but it is the canonical anti-pattern; hoist it.
- **`MindInspector.tsx:826-843`** (`ownKillsOf`) widens its parameter to
  `readonly { tick: number; events: readonly { type: string }[] }[]` specifically so it can do
  `(event as KillEventView).killer_id`. Passing `readonly TickView[]` and narrowing on
  `event.type === "kill"` is type-safe and shorter — this is the one place in the area that works *around*
  the strict config rather than with it.
- **`MapView.tsx:102-105`** evaluates `prefersReducedMotion` once at module load. A user toggling the OS
  setting mid-session gets no effect, and the value is captured whenever the lazy chunk first loads. A
  `matchMedia` `change` listener would be ~6 lines. (The e2e suite sets the emulated media before
  navigation, so the journey test passes regardless.)
- **Two independent debounced URL writers** — `usePlayback.ts:546-583` (250 ms) and
  `ReplayPicker.tsx:648-660` (150 ms) — each read `window.location.search` at flush time and merge. It is
  correct (sequential `setTimeout` callbacks), but "who owns the URL" is now split across two files with
  two comments explaining that the *other* one preserves your keys. One `lib/url.ts` owner would be
  simpler.
- **`ReplayControls.tsx:595-600`** wires both `onInput` and `onChange` to the same `seekToIndex` on the
  range input — one is redundant.
- **`lib/playback.ts:453`** — `isViewId(params.get("view")) ? (params.get("view") as ViewId) : null` calls
  `get` twice and then casts, defeating its own type guard. Hoist to a local.
- **Comment volume**: 2346 / 12330 lines (19 %) in this area are comments; `EventTicker.tsx` is 42 %,
  `CostChips.tsx` 36 %. Unusually, this is *mostly earned* — only 151 lines name a Task/PR/audit and 19 are
  past-tense archaeology; the rest encode real firewall and async-ordering invariants. I flag it only
  because several top-of-file blocks are design-doc excerpts that will drift (`MapView.tsx:1-26`,
  `EventTicker.tsx:1-69`) and because F1 shows a header can assert something the code does not do.

---

## 3. What is genuinely GOOD

- **G1 · `lib/playback.ts` is the best-designed file in the area** [VERIFIED]. One tick↔frame resolver pair
  replacing "the recurring off-by-one" re-derived in three components; pure, no React, no store. I fuzzed it
  over all 50 real replays (index↔tick round-trip for every frame, `nextAfter`/`prevBefore` strictness, full
  URL serialize→parse round-trip): **`{ roundTripFail: 0, nextAfterFail: 0, prevBeforeFail: 0 }`**.
- **G2 · `EventTicker` is the reference implementation** for this codebase. The projection is pure and
  exported, so it is testable in the node runner; it is memoized on `[replay, perspective]` with an O(1)
  slice per frame and an explicit comment about why depending on `frameIndex` would make autoplay quadratic
  (`EventTicker.tsx:539-560`); the firewall reasoning is spelled out case-by-case and pinned by 759 lines of
  behaviour tests. If the rest of the area looked like this file, most of §2 would not exist.
- **G3 · The store's async-ordering discipline is unusually rigorous** (`store/replayStore.ts`). Monotonic
  request tokens *plus* a `(game_id, set)` guard on every keyed fetch — because both committed sets reuse
  `headless-seed-*` ids, which is a real trap — plus per-key error maps instead of one shared error slot,
  plus a "never report a failure for a key that already succeeded" guard. That last one is a bug class most
  code never gets to.
- **G4 · TS strictness is real, not nominal.** `noUncheckedIndexedAccess` + `exactOptionalPropertyTypes` on;
  **zero `as any`, zero `@ts-ignore`/`@ts-expect-error`** in the entire `src/`; `npm run tsc:check` and
  `npm run lint` both clean (4.8 s / 2.1 s, load 6.5); `npm run test` 173 tests in 357 ms.
- **G5 · Hooks discipline is clean.** Re-running `exhaustive-deps` with the ledger stripped produced exactly
  **one** additional finding in the whole app — and it is a genuine no-op. Both existing suppressions are
  documented and both are correct.
- **G6 · The firewall is implemented consistently and never re-derived client-side.** Fog gating lives at
  three chokepoints (`MapView` reads `AgentVisibilityView`, `EventTicker` projects through it,
  `MindInspector` gates on omniscient-or-self) and the store enforces the invariant that selecting an agent
  re-aims the lens (`replayStore.ts:469-490`, mirrored in `setPerspective`). The `SabotageOverlay`'s
  fog/omniscient split (`SabotageOverlay.tsx:118-147`) is a small model of the pattern.
- **G7 · Real edge cases are handled, not hand-waved.** The unmatched vent dive (a meeting interrupting a
  traversal) has a degraded in-place path — and it **actually occurs**: my probe found **10 unmatched dives
  across the 50 committed games**. The traveller's tick-anchored position is also exactly right: across all
  125 vent segments, the room the traveller draws at the exit tick matched the recorded `agent_states` room
  **125/125** (`exitRoomMismatch: 0`), and `is_venting` held mid-route on every intermediate tick
  (`ventingFlagMismatch: 0`).
- **G8 · Build/tooling is thought through**: `manualChunks` carefully excludes `@pixi/react` from the react
  chunk with a comment saying why, Pixi rides behind a `React.lazy` boundary, `base: "./"` for the static
  demo bundle, and the Playwright config pins the browser *by pinning the exact `@playwright/test` version*
  with the reasoning written down.
- **G9 · Honest empty/loading/error states everywhere** — "No beliefs formed yet (**not 0 %** — this agent
  simply holds no belief)" (`MindInspector.tsx:243`), the `RedactedVerbatim` panel that says *why* it is
  hidden, `VerbatimGate` created specifically so a failed fetch cannot render as an eternal spinner.

---

## 4. Architecture / design assessment

**Well-designed.** The layering is right and mostly respected: `lib/` is the dependency sink (pure, no
React, no store), the store owns state and async ordering, `hooks/usePlayback` turns state into a
transport, components are presentational-plus-a-thin-connected-wrapper (`MindInspectorPanel` /
`MindInspector`, `TournamentDashboardView` / `TournamentDashboard`, `ReplayBrowserView` / `ReplayPicker` —
a consistent pattern that also gives Storybook a seam). The one-token-source rule (`tokens.ts` → generated
`@theme` → both Tailwind and `pixiHex`) is enforced in practice, not just documented. The
engine-tick-vs-array-index split is named once and resolved once. The firewall is a genuine architectural
constraint the code visibly obeys.

**Accidental complexity.**
1. **The derivation layer is half-built.** `lib/` holds the playback derivations, but `MapView`'s five pure
   derivations, `MeetingView`'s `buildDepths`/`tallyBallots`, `MindInspector`'s `buildTrail`/`ownKillsOf`
   and `ReplayPicker`'s `buildCards` all live inside `.tsx` files the unit runner cannot reach. F1 is the
   direct cost of that.
2. **Three data-fetching styles coexist**: the typed client (most calls), a raw `fetch` with `apiUrl`
   (`BeliefMatrix`, `TournamentDashboard`), and component-local `useState` caches next to the store's
   `memoryCache`/`meetingCache`. That is what let F2 happen.
3. **Overlay coordination is manual and cross-referential.** z-indexes (`z-50` meeting, `z-[55]` rail,
   `z-[56]` tab, `z-70` transport, `z-[80]` belief, `z-[90]` tour), the `xl:pr-[26rem]` gutter that must
   equal the rail's `max-w-[24rem]`, `--transport-h`, three Escape handlers each gated on
   `guidedTourOpen`, and three focus traps. Every file comments about the others. F3 is the bug this
   arrangement was always going to produce. **This is the single highest-leverage refactor**: one
   `OverlayStack` context that says which overlay is top-most, with Escape and the focus trap both reading
   it.
4. **`ReplayControls.tsx` exports three unrelated surfaces** (`AdvantageGraph`, `EventTimeline`,
   `ReplayControls`) because they share `MarkerChip`/`Crosshair`/`BarShell` — a file organised by shared
   private helpers rather than by concern.

**What I would refactor, in order.** (i) `lib/mapDerivations.ts` + fix F1 against `tick.bodies`.
(ii) One overlay-stack owner; delete GuidedTour's trap copy. (iii) Route every fetch through `api/client`.
(iv) `lib/evidence.ts` + `lib/players.ts` and delete the duplicate helpers. (v) Split
`TournamentDashboard` and `MindInspector`.

---

## 5. Test assessment (this area)

**Strengths.** What *is* tested is tested well — behaviour, not implementation. `playback.test.ts` (519
lines) states contracts in its test names ("nextAfter is STRICTLY greater (standing on a beat moves off
it)", "does not fire when already parked on the meeting tick — **Resume must work**") and covers clamping,
empty timelines, ranking collisions and full URL round-trips. `EventTicker.test.ts` (759 lines) pins the
firewall case-by-case, including the subtle ones (own kill must not resurface as a body discovery).
`CostChips.test.ts` pins monotonicity and the "incomplete tokens" predicate. `replayStore.test.ts` (805
lines) drives the store through `getState()` and specifically exercises the stale-completion races. I found
**no** tests that pin implementation details. The suite is fast (173 tests, 357 ms) — no reason not to run it.

**Gaps, in priority order.**
1. **No render tests at all** (F7). 30/32 components and 2/2 hooks are unit-untested.
2. **`usePlaybackEngine` is untested** — auto-advance, the meeting pause, URL hydration/write-back and
   auto-follow are ~250 lines of interacting effects with refs and timers, all covered only by one
   Playwright assertion.
3. **`lib/contradictions.ts` has no test** despite being the "split the smuggled utils into lib/" file.
4. **No test would have caught F1** — because the map derivations are not importable by the node runner and
   nothing compares any derived view against the served DTO. A ~20-line test that walks the committed
   sample replays and asserts `derivedBodies(t) == tick.bodies` would be a permanent guard, and would also
   have caught the design-doc drift.
5. **No a11y assertion anywhere** — no axe pass in the Playwright journey, so F3 and F10 are invisible to CI.

---

## 6. Recommendations (prioritized)

1. **Fix F1**: source the map body layer from `TickView.bodies`; delete `buildBodyStatesByTick`. Decide
   explicitly whether reported corpses persist as markers, and if so give them a distinct treatment and
   stop calling the layer "ground truth". *(P1, ~1 h, removes ~45 lines.)*
2. **Fix F2**: `TournamentDashboard` → `getRubric()`; add `getBeliefFrames()` to `api/client` for
   `BeliefMatrix`. Then no surface can bypass `assertViewModelVersion`. *(P1, ~30 min.)*
3. **Fix F3**: delete GuidedTour's duplicated trap, call `useFocusTrap`, and make the trap yield to the
   top-most overlay the same way Escape already does. *(P1, ~1 h.)*
4. **Extract `lib/mapDerivations.ts`** (`computeTransform`, `buildVentEdges`, `buildVentSegments`,
   body state, `normalizeRoomKey`) and add a test that walks `replays/samples/9p2i` and asserts the derived
   views equal the served DTO. This is the change that turns F1's class of bug into a caught regression.
5. **Add a jsdom vitest project** alongside the node one (keep node as the fast default) and cover: focus-trap
   composition, the `MindInspector` tabs keyboard pattern, `usePlaybackEngine`'s timer + meeting pause, and
   `mergePlaybackSearch`. *(Addresses F7; ~half a day.)*
6. **De-duplicate F4** into `lib/evidence.ts` and `lib/players.ts`, import the exported `scoreBucketOf`,
   drop `BeliefPanel`'s shadowing `Loading`/`EmptyState`. Reconcile the `"weak signal"`/`"weak"` divergence
   while you are there. *(P2, ~1 h.)*
7. **Clear the ESLint ledger** (F5) — both entries are one-line fixes — and delete the 45-line justification.
   Consider promoting `react-hooks/set-state-in-effect` and `react-hooks/refs` to `warn` (F9); the plugin is
   already installed.
8. **Pixi hygiene** (F6): hoist the 8 `pixiText` style literals to module constants, `useCallback` the two
   inline `useTick` callbacks, and give `KillFlash` a terminating condition. Then add an axe pass and an
   `aria-label` + off-canvas text summary for the map (F10). *(P2, ~2 h.)*

---

### Appendix — commands and artefacts

```
cd frontend && npm run test        # 173 passed / 6 files, 357 ms          (load 6.90)
cd frontend && npm run tsc:check   # clean, 4.8 s                          (load 6.49)
cd frontend && npm run lint        # clean, 2.1 s                          (load 6.49)

# fixtures: 50 real ReplayView payloads dumped offline via api.replay_loader (no network, no LLM)
work/frontend-a/dump_many.py            -> work/frontend-a/replays/*.json  (31 MB, 1769 frames)
work/frontend-a/probe/probe.mjs         -> body/vent invariants vs the served DTO
work/frontend-a/probe/probe2.mjs        -> phantom-body census (F1)
work/frontend-a/probe/probe3.mjs        -> every phantom is a reported corpse (F1)
work/frontend-a/probe/probe4.mts        -> playback fuzz + hover-render benchmark (G1, F12)
work/frontend-a/probe/probe5.mjs        -> downstream collapse-marker effect (F1)
work/frontend-a/probe/trap.mjs          -> double focus-trap repro (F3)
work/frontend-a/probe/eslint.*.mjs      -> lint runs with the ledger stripped (F5, F9)
```

Playwright was **not** run: no Chromium is cached locally and downloading one would touch the network,
which the review brief forbids. No real-provider LLM call was made; the replay fixtures were produced by
deterministic engine playback.
