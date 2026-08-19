# Agent Prompt — 20.1 The map body layer reads engine truth (TickView.bodies) + the first MapView derivation test

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.1 — The map body layer reads engine truth (TickView.bodies) + the first MapView derivation test, anchored to C-7 / G-38 (body half) / C-80 / C-101 — audits/review-2026-08-19/B/frontend-a.md §2 F1 (the phantom-corpse census), §2 F7 (no component-level tests, by configuration), §2 F8 (the derivations trapped in `.tsx`), §2 F11 (`TickView.bodies` served to no consumer); audits/review-2026-08-19/B/collated-findings.md rows C-7 and C-80; audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/ux-visual-pass-lead.md bullet 6 (seed 2 t29: four corpses drawn, one in state); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.2; audits/review-2026-08-19/D/cross-track-map.md rows G-6 and G-38; design/phase-12/stage-1-design.md:83 (the body layer was specified to source from `state.bodies`). Anchors re-verified at HEAD `b809b19c`: frontend/src/components/MapView.tsx:85-92 (`BodySpec` / `NO_BODIES`), :226-264 (`buildBodyStatesByTick`), :569-572 (the `useMemo`), :591 (`bodyIndex` / `omniscientBodies`), :733-744 (`bodySpecs`; the fog branch already reads `visibility.visible_bodies`), :749-798 (`bodiesByRoom` + the `BODY_CAP` / `bodiesFit` collapse); frontend/src/components/BodyMarker.tsx:13-18 (the two-state truth grammar), :36-38 (the `TickView.bodies[].killed_by` provenance comment), :47 (`BODY_CAP = 3`), :60 (`bodiesFit`), :125 ("Outer kill ring marks a freshly reported body"); orchestrator/game.py:1247-1259 (the corpse consumption at meeting resolution); api/replay_loader.py:2568-2580 (`_bodies_view`); api/schemas.py:345-361 (`BodyView` — no `discovered` field is served), :457-461 (`TickView.bodies`); engine/tick.py:439 (`discovered_by` is written by the report action and nothing else); frontend/vitest.config.ts:10-25 (`environment: "node"` as a stated contract); frontend/tsconfig.json (`resolveJsonModule`, `include: ["src"]`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-map-body-layer`
**Depends on:** none (root)
**Section refs:** C-7 / G-38 (body half) / C-80 / C-101 — audits/review-2026-08-19/B/frontend-a.md §2 F1 (the phantom-corpse census), §2 F7 (no component-level tests, by configuration), §2 F8 (the derivations trapped in `.tsx`), §2 F11 (`TickView.bodies` served to no consumer); audits/review-2026-08-19/B/collated-findings.md rows C-7 and C-80; audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/ux-visual-pass-lead.md bullet 6 (seed 2 t29: four corpses drawn, one in state); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.2; audits/review-2026-08-19/D/cross-track-map.md rows G-6 and G-38; design/phase-12/stage-1-design.md:83 (the body layer was specified to source from `state.bodies`). Anchors re-verified at HEAD `b809b19c`: frontend/src/components/MapView.tsx:85-92 (`BodySpec` / `NO_BODIES`), :226-264 (`buildBodyStatesByTick`), :569-572 (the `useMemo`), :591 (`bodyIndex` / `omniscientBodies`), :733-744 (`bodySpecs`; the fog branch already reads `visibility.visible_bodies`), :749-798 (`bodiesByRoom` + the `BODY_CAP` / `bodiesFit` collapse); frontend/src/components/BodyMarker.tsx:13-18 (the two-state truth grammar), :36-38 (the `TickView.bodies[].killed_by` provenance comment), :47 (`BODY_CAP = 3`), :60 (`bodiesFit`), :125 ("Outer kill ring marks a freshly reported body"); orchestrator/game.py:1247-1259 (the corpse consumption at meeting resolution); api/replay_loader.py:2568-2580 (`_bodies_view`); api/schemas.py:345-361 (`BodyView` — no `discovered` field is served), :457-461 (`TickView.bodies`); engine/tick.py:439 (`discovered_by` is written by the report action and nothing else); frontend/vitest.config.ts:10-25 (`environment: "node"` as a stated contract); frontend/tsconfig.json (`resolveJsonModule`, `include: ["src"]`).
**Complexity:** Medium
**Record impact:** none
**Measurement:** `cd frontend && npm run test` green including the new `src/lib/bodies.test.ts`, whose phantom-frame count over the 50 committed `replays/samples/9p2i` served payloads reads 0 while the same walk over the retired accumulate rule reads 1,182 of 1,769 (the gate can fail); `npm run tsc:check`, `npm run lint` and `npm run build` green; `bash scripts/check.sh` green.

The map is the demo's central surface and it is wrong on two thirds of its frames.
`buildBodyStatesByTick` (MapView.tsx:229-264) builds the Omniscient body layer by
*accumulating* `kill` events and never removing anything — a `report_body` only flips
`isDiscovered`. But `orchestrator/game.py:1256-1259` deletes the reported corpse from
`WorldState.bodies` when the body-report meeting resolves, and the served DTO reflects
that exactly: `api/replay_loader.py:2568 _bodies_view` projects the bodies still on the
floor, with the privileged `killed_by`. MapView never reads it. Re-derived at HEAD
`b809b19c` over all 50 committed `replays/samples/9p2i` games (reproducing the review's
probe: audits/review-2026-08-19/B/frontend-a.md §2 F1): 1,182 of 1,769 frames (66.8 %)
paint at least one corpse the engine has already consumed, in 50 of 50 games, 2,426
phantom body instances, `missingFrames: 0`, `phantomWithoutReport: 0` — every phantom is
a consumed corpse, none is unexplained. Named instances, both re-confirmed:
`headless-seed-0` tick 18 serves `[]` and the map draws `["p-2"]`; `headless-seed-2`
tick 29 serves `["p-5"]` and the map draws `["p-1","p-2","p-5","p-6"]` (the UX lead's
"FOUR corpses while the engine state has one",
audits/review-2026-08-19/A/ux-visual-pass-lead.md bullet 6). The As-agent path is
already correct (MapView.tsx:738-744 reads `visibility.visible_bodies`), so Omniscient
and fog disagree about whether a body is on the floor — which reads to a viewer as a fog
artefact rather than as the bug it is.

The error is not only cosmetic. Phantoms are drawn with `BodyMarker`'s *discovered*
treatment, whose own comment (BodyMarker.tsx:125) calls the outer ring "a freshly
reported body" — so a corpse reported at tick 12 still wears the freshly-reported ring
at tick 60. They corrupt the per-room layout downstream: re-derived at HEAD, all 1,182
frames carry an inflated per-room body count, and on 4 frames a room's accumulated pile
exceeds `BODY_CAP = 3` while no served room does, firing a spurious "✕ ×N" collapse
marker over a room that holds nothing. And the served `killed_by` field — built for
exactly this layer, cited as its source at BodyMarker.tsx:36-38 — is dead, because
MapView re-derives the killer from the kill event instead (MapView.tsx:258). The file
header calls this layer "Omniscient ground truth" (MapView.tsx:226-227); the Phase-12
design specified sourcing it from `state.bodies` (design/phase-12/stage-1-design.md:83).
This is doc-vs-code drift and a wrong render on the default perspective of the app the
portfolio track calls the star-making asset.

The second half of the task is why nobody caught it. MapView's pure derivations live
inside a `.tsx` that the node-only vitest project cannot import (C-80;
audits/review-2026-08-19/B/frontend-a.md §2 F8: "which is precisely why F1 went
unnoticed"), and there are zero component-level tests by configuration (C-101; §2 F7).
`frontend/src/lib/` already holds the playback derivations and is the established home
for exactly this kind of code. Moving the body derivation there and pinning it against
the committed served bytes is what turns this class of defect into a caught regression
rather than a review finding — and it is the first brick of the `lib/` layer the review
asks for, without attempting the whole `lib/mapDerivations.ts` split (the other four
derivations stay where they are; this task moves one concern, not a file).

Three invariants the fix must preserve. First, the fog path: `visibility.visible_bodies`
continues to drive the As-agent layer with `isDiscovered: false` and `killedBy: null`
(the firewall — `VisibleBodyView` carries no killer), and that mapping becomes pinned
rather than merely asserted in a comment. Second, discovery: no `discovered` flag is
served (api/schemas.py:345-361 — `BodyView` carries `body_id` / `victim_id` / `room_id`
/ `killed_by` only), so `isDiscovered` stays derived from `report_body` events
accumulated forward; `engine/tick.py:439` shows `discovered_by` is written by the report
action alone, so the derivation and the engine agree by construction. Third, presence: a
body leaves the map on the frame the engine consumes it, and a body that is reported but
*not* consumed (only the meeting's triggering corpse is deleted) keeps rendering with
the discovered treatment. Re-derived at HEAD over `samples/9p2i`: 151 `report_body`
events, each of whose bodies is served on exactly one frame — its own report frame — and
none after; `samples/4p1i` reads 35/35 the same way. So after the fix the "freshly
reported" ring is literally true on the committed sets, which is the honest version of
the semantics BodyMarker already documents.

The DTO is correct and is not touched: no `api/schemas.py` change, no `viewModelVersion`
bump, no re-record. This task is RR-free and moves no committed bytes.

**Files in scope:**
- frontend/src/components/MapView.tsx; (the body layer reads `tick.bodies`; the pure derivations move out)
- frontend/src/lib/bodies.ts; (new: the pure body-layer derivation, importable by vitest)
- frontend/src/lib/bodies.test.ts; (new: walks the committed sample replays' served payloads and asserts zero phantom frames)
- frontend/src/components/BodyMarker.tsx; (the "freshly reported" ring semantics only if the reported body is still served)
- frontend/src/lib/bodies.fixture.json; (new: the committed dump of the 50 served samples/9p2i payloads the test walks — tick.bodies exists only after the Python loader's engine re-walk)

**Files NOT in scope:**
- api/ (the served `TickView.bodies` is already correct; no DTO field, no schema change, no `viewModelVersion` bump — a `discovered` flag on `BodyView` would be a DTO change and is explicitly refused here)
- frontend/src/components/AgentToken.tsx (the action glyphs and the `CurrentAction` enum belong to the DTO-fidelity task later in this phase)
- frontend/src/components/TournamentDashboard.tsx, MeetingView.tsx, ReplayPicker.tsx, ReplayControls.tsx (the product-copy pass owns those surfaces)
- frontend/src/App.tsx, frontend/src/hooks/, frontend/e2e/ (the dock/focus-trap task owns the layout and the Playwright journey)
- frontend/vitest.config.ts (its `include: ["src/**/*.test.ts"]` glob already picks the new suite up and `environment: "node"` is the right contract for a pure derivation; its header's enumeration of suites is illustrative — if the reviewer wants it refreshed, raise it under Questions rather than widening scope)
- MapView's other four pure derivations — `computeTransform`, `buildVentEdges`, `buildVentSegments`, `normalizeRoomKey` (the full `lib/mapDerivations.ts` split is a separate concern; this task moves the body layer only)
- replays/, orchestrator/, engine/ (the engine is correct — the corpse consumption at `orchestrator/game.py:1247-1259` is the truth this task starts obeying, not a defect)

**Definition of done:**
- [ ] `frontend/src/lib/bodies.ts` exists and owns the body-layer derivation as pure, importable functions: presence for the Omniscient layer comes from `tick.bodies` alone, `killedBy` is read from the served `tick.bodies[].killed_by` (the dead field revived — no re-derivation from the kill event), and `isDiscovered` is the forward-accumulated `report_body` set. The fog mapping from `AgentVisibilityView.visible_bodies` moves into the same module with `isDiscovered: false` / `killedBy: null` unchanged. `BodySpec` is exported from `lib/bodies.ts`; `buildBodyStatesByTick`, `BodySpec` and `NO_BODIES` are DELETED from `MapView.tsx` (retire means delete — no wrapper left behind), and `MapView.tsx` consumes the new module at the `useMemo` (:569-572) and at the `bodySpecs` branch (:733-744).
- [ ] `frontend/src/lib/bodies.test.ts` walks the served payloads of all 50 committed `replays/samples/9p2i` replays from a committed fixture and asserts the phantom-frame count is 0 — a phantom frame being one where the derivation renders a body absent from that tick's `tick.bodies`. The same walk over the retired accumulate rule, re-implemented inside the test as the perturbation leg, reads 1,182 phantom frames of 1,769 total across 50/50 games (2,426 phantom body instances), so the gate demonstrably bites; `missingFrames` is 0 on both legs.
- [ ] The `BODY_CAP` / `bodiesFit` collapse no longer fires on a phantom pile: pinned by the same walk, no frame has a room whose derived body count exceeds `BODY_CAP` while the served state has no such room (the retired rule produces 4 such frames; the scale-dependent `bodiesFit` half stays in `MapView.tsx` and is not re-implemented in `lib/`). Per-room served counts are asserted equal to per-room derived counts on every frame (the retired rule inflates 1,182 of them).
- [ ] Discovery semantics are pinned: over `samples/9p2i` exactly 151 frames carry a discovered body — one per `report_body` event, on the report frame itself — and none afterwards; a hand-built fixture covers the reported-but-unconsumed case (a body with a `report_body` event that is still present in a later tick's `tick.bodies` keeps the discovered treatment) and the unreported case (ghosted), so the rule holds independently of whether the committed sets happen to exercise it.
- [ ] The As-agent path is unchanged and pinned: a hand-built fixture asserts the fog mapping's output is byte-identical to today's — one `BodySpec` per `visible_bodies` entry, `isDiscovered: false`, `killedBy: null` — and that no served `tick.bodies` entry can reach the fog layer.
- [ ] `frontend/src/components/BodyMarker.tsx` states the true semantics: the outer kill ring marks a body reported and still on the floor, and the header's two-state grammar names `tick.bodies` as the presence source. Comment/prop-doc lines only — no rendering behaviour changes, no props added or removed (`BODY_CAP`, `bodiesFit`, `collapsedCount`, `killedBy` all keep their signatures). Provenance is at most one trailing line per docstring.
- [ ] `cd frontend && npm run test`, `npm run lint`, `npm run tsc:check` and `npm run build` all pass; the PR quotes the before/after phantom census (1,182/1,769 → 0/1,769).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Step 1 — verify before editing. Re-run the census yourself so the PR's before-number is
yours, not inherited: load each `replays/samples/9p2i` replay through
`api.replay_loader.ReplayLoader` (50 games, ~1.5 s total on this HEAD), re-implement
`buildBodyStatesByTick` in a throwaway Python script, and diff its per-tick victim set
against `{b.victim_id for b in tick.bodies}`. Expect exactly `totalFrames 1769,
phantomFrames 1182, missingFrames 0, gamesWithPhantom 50/50, phantomBodyInstances 2426`.
If any of those differ at your HEAD, stop and report it under Questions before writing
code — the contract's numbers are the bar.

Step 2 — the module. Two exports carry the Omniscient layer and one carries the fog
layer. A per-frame function — roughly
`bodiesForTick(tick, reportedVictimIds): BodySpec[]` — maps each `tick.bodies[]` row to
victimId `body.victim_id`, roomId `body.room_id`, isDiscovered
`reportedVictimIds.has(body.victim_id)`, killedBy `body.killed_by`: presence and
attribution both straight from the served row, nothing accumulated. A whole-replay pass
— roughly `bodyStatesByTick(ticks): BodySpec[][]` — threads the `report_body` set
forward and calls the per-frame function, preserving MapView's existing `useMemo` shape
so the call site at :569-572 is a one-line change and the `bodyIndex` clamp at :591
stays as it is. A third — roughly `visibleBodiesForTick(visibility): BodySpec[]` — is
the relocated fog mapping. Keep the sort, the `bodiesByRoom` grouping and the
`BODY_CAP` / `bodiesFit` collapse in `MapView.tsx`: they need `scale`, which is render
state, and a pure module should not take it.

Step 3 — the fixture. The committed replays are action-only
(`replays/samples/9p2i/replay-seed-0.jsonl` rows are
`{"actions":[…],"kind":"tick","state_hash":…}`), so `tick.bodies` exists only after the
Python loader's engine re-walk; the TypeScript test cannot derive it and must not try —
re-deriving engine state in the frontend is the exact mistake this task is undoing.
Commit a compact dump instead: per game, the tick index, the sorted served victim ids,
and the `kill` / `report_body` events. Minified that is about 72 KB for the whole 9p2i
set — smaller than several files already tracked under `frontend/` — and it is stable,
because `replays/` bytes never move. Generate it once with a short `uv run python`
snippet over `ReplayLoader`, record that exact command in the test file's header comment
so the fixture is re-derivable, and read it with `readFileSync` + `JSON.parse` rather
than a JSON `import`: `frontend/tsconfig.json` sets `resolveJsonModule` and includes
`src`, so importing a 72 KB literal would push a large inferred type through
`tsc --noEmit` for no benefit. `frontend/src/tokens.test.ts` is the precedent for reading a
real file off disk under `environment: "node"`. Parse the fixture through a narrow,
explicitly-typed reader function so `noUncheckedIndexedAccess` and
`exactOptionalPropertyTypes` stay honest.

Step 4 — the perturbation leg. The zero-phantom assertion is close to true by
construction once presence comes from `tick.bodies`, so on its own it is a gate nobody
can fail. Put the retired accumulate rule in the test file as a named reference
implementation, run the same walk over it, and assert it reads 1,182 — the test then
proves both that the new derivation is right and that the walk can tell them apart.
Optionally extend the fixture to `samples/4p1i` as a second set (adds ~28 KB; re-derived
at HEAD it reads 101 phantom frames of 682 across 25 of 50 games) — useful, not
required.

Step 5 — blast radius. Before deleting anything, run
`grep -rn 'BodySpec\|NO_BODIES\|buildBodyStatesByTick\|visible_bodies' frontend/src`;
at HEAD every hit is inside `MapView.tsx` plus the `types/api.ts` declaration, so the
deletion is contained. If a hit appears outside the files in scope, stop and report it
rather than widening scope.

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
Open a PR from branch `phase-20-map-body-layer` with a title like `task 20.1: the map body layer reads engine truth (tickview.bodies) + the first mapview derivation test`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing C-7 / G-38 (body half) / C-80 / C-101 — audits/review-2026-08-19/B/frontend-a.md §2 F1 (the phantom-corpse census), §2 F7 (no component-level tests, by configuration), §2 F8 (the derivations trapped in `.tsx`), §2 F11 (`TickView.bodies` served to no consumer); audits/review-2026-08-19/B/collated-findings.md rows C-7 and C-80; audits/review-2026-08-19/A/collated-findings.md §G-38; audits/review-2026-08-19/A/ux-visual-pass-lead.md bullet 6 (seed 2 t29: four corpses drawn, one in state); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 0.2; audits/review-2026-08-19/D/cross-track-map.md rows G-6 and G-38; design/phase-12/stage-1-design.md:83 (the body layer was specified to source from `state.bodies`). Anchors re-verified at HEAD `b809b19c`: frontend/src/components/MapView.tsx:85-92 (`BodySpec` / `NO_BODIES`), :226-264 (`buildBodyStatesByTick`), :569-572 (the `useMemo`), :591 (`bodyIndex` / `omniscientBodies`), :733-744 (`bodySpecs`; the fog branch already reads `visibility.visible_bodies`), :749-798 (`bodiesByRoom` + the `BODY_CAP` / `bodiesFit` collapse); frontend/src/components/BodyMarker.tsx:13-18 (the two-state truth grammar), :36-38 (the `TickView.bodies[].killed_by` provenance comment), :47 (`BODY_CAP = 3`), :60 (`bodiesFit`), :125 ("Outer kill ring marks a freshly reported body"); orchestrator/game.py:1247-1259 (the corpse consumption at meeting resolution); api/replay_loader.py:2568-2580 (`_bodies_view`); api/schemas.py:345-361 (`BodyView` — no `discovered` field is served), :457-461 (`TickView.bodies`); engine/tick.py:439 (`discovered_by` is written by the report action and nothing else); frontend/vitest.config.ts:10-25 (`environment: "node"` as a stated contract); frontend/tsconfig.json (`resolveJsonModule`, `include: ["src"]`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
