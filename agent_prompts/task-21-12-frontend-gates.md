# Agent Prompt — 21.12 The spectator's gates: the laptop sees the map, the meeting dialog asserts, the whereabouts badge renders

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-21.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 21.12 — The spectator's gates: the laptop sees the map, the meeting dialog asserts, the whereabouts badge renders, anchored to the 1440×900 arrival gap, routed to the phase-20 close ledger with 20.39's merge record `69255980` — audits/audit-phase-20-close.md:409 ("No standing gate asserts that a DEFAULT 1440×900 arrival shows the whole map"), restated in tasks/phase-20.md:6432; B-53 [ADJUSTED, P2] audits/review-2026-08-26/B/collated-findings.md:2801 (row at :61) — the meeting dialog's transcript/evidence half carries no assertion in any standing gate, with the verifier's two corrections BINDING this contract: "zero e2e assertions" is true only of the standing gate (frontend/e2e/media.spec.ts:836-838 does assert a TurnCard, but its whole describe is skipped without `AILIBI_CAPTURE_MEDIA=1`), and the served census denominator is 144 on the default-served set, not 164; B-22 [ADJUSTED, P2] audits/review-2026-08-26/B/collated-findings.md:1318 (row at :30) — a re-report of still-open C-120 (audits/review-2026-08-19/B/collated-findings.md:185), whose fix was already prescribed at audits/review-2026-08-19/B/meetings-transcript-voting.md:133, with the verifier's accent correction BINDING: 5 of the 7 half-blank turns are `weak_signal`, which Task 19.11's taxonomy already paints in the speaker identity colour, so exactly 2 turns lose a real contradiction accent. Anchors re-verified at HEAD `4002f19b` (clean tree): frontend/src/lib/contradictions.ts:12-18 (`turnClaimEventId` / `turnObsEventId` — two segments) and :8-11 (the comment claiming the module "mirrors `meetings/transcript.py` exactly"); frontend/src/components/TurnCard.tsx:291-294 (every observation mapped through `turnObsEventId`), :299-302 (`flagged`), :321-327 (the three-way accent: `role_proof` → ink, `cross_statement` → contradiction, else `playerColor`); frontend/src/components/MeetingView.tsx:312-323 (the sibling helper that WAS taught the segment, with its comment naming the class) and :322 (`/^turn:(.+):(?:claim|obs|whereabouts):\d+$/`), :283 (the transcript panel `Accusation chain & transcript`), :61-66 (`Panel` renders `<section aria-label={title}>`), :408-417 (`EvidenceSection` returns `null` on an empty flag list), :464-474 (the `Evidence (N)` heading and each group's `heading (n)`); meetings/transcript.py:4065 / :4069 / :4073 (`_turn_claim_id` / `_turn_observation_id` / `_turn_whereabouts_id`) and :3746-3753 (the exclusive per-observation branch), :2259 vs :2294 (the docstring still names `_turn_observation_id` where the code writes `_turn_whereabouts_id` — the second half of C-120, deliberately not in scope here); api/schemas.py:563 + :577 (`WhereaboutsClaimView`, `type: Literal["whereabouts"]`) and frontend/src/types/api.ts:281-282 + :747 (the discriminated union; the file is GENERATED per its :1 banner); frontend/e2e/journey.spec.ts:203-205 (`timelineDisclosure`), :224-245 (`mapAndDockGeometry`), :248-254 (`scrollMapToTop`), :262-270 (`settledGeometry`), :341-352 (the ONLY meeting assertions today: the dialog, its `aria-label`, the `Ballots (N)` region, the word "confidence", one `p-N`), :505-561 (the laptop-heights test — 1280×800 and 1000×640, both asserted with the drawer `aria-expanded="false"`), :554-561 (a deliberate toggle wins over the height default for the rest of the session); frontend/e2e/media.spec.ts:92 (`SHOT_VIEWPORT` 1440×900), :344-364 (`uncoverMap` collapses the Timeline drawer BEFORE it measures), :56 + :730-734 (the capture gate), :836 (`dialog.locator("article")` — the turn card's handle); frontend/playwright.config.ts:70 (default viewport 1440×960), :49 (`testDir: "./e2e"`), :82 (`AILIBI_REPLAY_DIR=replays/samples`, so both sets are served); frontend/src/index.css:157-168 (`--transport-expanded-min-height: 860px`, declared the ONE home for the threshold) and frontend/src/App.tsx:1049-1055 (`expandedHeightQuery` reads it back) + :1057-1073 (`useRoomyViewport`); frontend/vitest.config.ts:10-19 (`environment: "node"` as a stated contract) and frontend/src/lib/bodies.test.ts:17-25 + :25-77 (the committed-fixture rationale and the regeneration recipe carried in the header) + :441 + :466 + :507-511 (the digest assertion and the retired-rule perturbation leg); scripts/check.sh:51-56 + :66 (four frontend legs, e2e deliberately not among them) and .github/workflows/ci.yml:96-154 (the `frontend-e2e` job that does run `npm run e2e`).. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-21.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-21-frontend-gates`
**Depends on:** none (root)
**Section refs:** the 1440×900 arrival gap, routed to the phase-20 close ledger with 20.39's merge record `69255980` — audits/audit-phase-20-close.md:409 ("No standing gate asserts that a DEFAULT 1440×900 arrival shows the whole map"), restated in tasks/phase-20.md:6432; B-53 [ADJUSTED, P2] audits/review-2026-08-26/B/collated-findings.md:2801 (row at :61) — the meeting dialog's transcript/evidence half carries no assertion in any standing gate, with the verifier's two corrections BINDING this contract: "zero e2e assertions" is true only of the standing gate (frontend/e2e/media.spec.ts:836-838 does assert a TurnCard, but its whole describe is skipped without `AILIBI_CAPTURE_MEDIA=1`), and the served census denominator is 144 on the default-served set, not 164; B-22 [ADJUSTED, P2] audits/review-2026-08-26/B/collated-findings.md:1318 (row at :30) — a re-report of still-open C-120 (audits/review-2026-08-19/B/collated-findings.md:185), whose fix was already prescribed at audits/review-2026-08-19/B/meetings-transcript-voting.md:133, with the verifier's accent correction BINDING: 5 of the 7 half-blank turns are `weak_signal`, which Task 19.11's taxonomy already paints in the speaker identity colour, so exactly 2 turns lose a real contradiction accent. Anchors re-verified at HEAD `4002f19b` (clean tree): frontend/src/lib/contradictions.ts:12-18 (`turnClaimEventId` / `turnObsEventId` — two segments) and :8-11 (the comment claiming the module "mirrors `meetings/transcript.py` exactly"); frontend/src/components/TurnCard.tsx:291-294 (every observation mapped through `turnObsEventId`), :299-302 (`flagged`), :321-327 (the three-way accent: `role_proof` → ink, `cross_statement` → contradiction, else `playerColor`); frontend/src/components/MeetingView.tsx:312-323 (the sibling helper that WAS taught the segment, with its comment naming the class) and :322 (`/^turn:(.+):(?:claim|obs|whereabouts):\d+$/`), :283 (the transcript panel `Accusation chain & transcript`), :61-66 (`Panel` renders `<section aria-label={title}>`), :408-417 (`EvidenceSection` returns `null` on an empty flag list), :464-474 (the `Evidence (N)` heading and each group's `heading (n)`); meetings/transcript.py:4065 / :4069 / :4073 (`_turn_claim_id` / `_turn_observation_id` / `_turn_whereabouts_id`) and :3746-3753 (the exclusive per-observation branch), :2259 vs :2294 (the docstring still names `_turn_observation_id` where the code writes `_turn_whereabouts_id` — the second half of C-120, deliberately not in scope here); api/schemas.py:563 + :577 (`WhereaboutsClaimView`, `type: Literal["whereabouts"]`) and frontend/src/types/api.ts:281-282 + :747 (the discriminated union; the file is GENERATED per its :1 banner); frontend/e2e/journey.spec.ts:203-205 (`timelineDisclosure`), :224-245 (`mapAndDockGeometry`), :248-254 (`scrollMapToTop`), :262-270 (`settledGeometry`), :341-352 (the ONLY meeting assertions today: the dialog, its `aria-label`, the `Ballots (N)` region, the word "confidence", one `p-N`), :505-561 (the laptop-heights test — 1280×800 and 1000×640, both asserted with the drawer `aria-expanded="false"`), :554-561 (a deliberate toggle wins over the height default for the rest of the session); frontend/e2e/media.spec.ts:92 (`SHOT_VIEWPORT` 1440×900), :344-364 (`uncoverMap` collapses the Timeline drawer BEFORE it measures), :56 + :730-734 (the capture gate), :836 (`dialog.locator("article")` — the turn card's handle); frontend/playwright.config.ts:70 (default viewport 1440×960), :49 (`testDir: "./e2e"`), :82 (`AILIBI_REPLAY_DIR=replays/samples`, so both sets are served); frontend/src/index.css:157-168 (`--transport-expanded-min-height: 860px`, declared the ONE home for the threshold) and frontend/src/App.tsx:1049-1055 (`expandedHeightQuery` reads it back) + :1057-1073 (`useRoomyViewport`); frontend/vitest.config.ts:10-19 (`environment: "node"` as a stated contract) and frontend/src/lib/bodies.test.ts:17-25 + :25-77 (the committed-fixture rationale and the regeneration recipe carried in the header) + :441 + :466 + :507-511 (the digest assertion and the retired-rule perturbation leg); scripts/check.sh:51-56 + :66 (four frontend legs, e2e deliberately not among them) and .github/workflows/ci.yml:96-154 (the `frontend-e2e` job that does run `npm run e2e`).
**Complexity:** Small
**Record impact:** none
**Measurement:** `cd frontend && npm run test` green including the new `src/lib/contradictions.test.ts`, whose walk over the 100 committed served payloads resolves all 328 contradiction endpoints while the retired two-segment rule leaves 31 unresolved across 7 half-blank turns (the gate can fail); `cd frontend && npm run e2e` green with the new 1440×900 default-arrival test and the meeting transcript/evidence assertions, the geometry numbers from the FIRST run at HEAD pasted into the PR; `bash scripts/check.sh` green.

Three gaps on the viewer, all of the same shape: the surface a reader actually looks at is
guarded by nothing, so a defect in it ships green. Two are already written down — one routed
to the phase-20 close ledger, one filed twice — and the third is the defect that slipped
through the hole the other two leave.

THE ARRIVAL. `frontend/e2e/journey.spec.ts:505-561` proves the map survives the transport
dock at 1280×800 and at 1000×640. Both legs run against a COLLAPSED dock: 800 and 640 are
below `--transport-expanded-min-height` (860 px, frontend/src/index.css:168), so
`useRoomyViewport` (App.tsx:1057-1073) returns false and the spec asserts
`aria-expanded="false"` before it measures. No standing gate has ever measured the EXPANDED
dock, which is the state every visitor on a 900-px-tall laptop arrives in — 900 ≥ 860. The
close audit routed exactly this (audits/audit-phase-20-close.md:409), and the only place
1440×900 is exercised at all is the media capture, whose `uncoverMap`
(frontend/e2e/media.spec.ts:344-364) collapses the drawer first and whose whole describe is
skipped unless `AILIBI_CAPTURE_MEDIA=1` (:56, :730-734). So the product's most common desktop
arrival is unmeasured, and the one script that looks at it looks away first.

THE DIALOG. The meeting modal is the reconstruction surface — the accusation chain, the turn
cards, the evidence taxonomy, the verdict readout — and the standing gate stops at the ballots.
Today's whole meeting assertion is five lines (journey.spec.ts:341-352): the dialog is visible,
its `aria-label` matches, the `Ballots (N)` region contains "confidence" and one `p-N`, then
Escape. `grep -rn 'contradiction' frontend/e2e/*.ts` returns nothing; `find frontend/src -name
'*.test.ts*'` returns eight files and none of them covers `lib/contradictions.ts`
(44 lines, three exported pure functions). B-53's verifier re-ran both and got the same. The
one place a turn card IS asserted is the capture spec (media.spec.ts:836-838), which never runs
in the standing gate — a gate that only fires when an operator sets `AILIBI_CAPTURE_MEDIA=1`
cannot catch a regression, which is the honest and still-damning form of the finding.

THE DEFECT THAT FELL THROUGH. Task 16.7 gave a roll-call self-placement its own event-id
segment: `meetings/transcript.py:4073` mints `turn:<id>:whereabouts:<i>`, and :3746-3753 makes
the branch exclusive, so a `WhereaboutsClaim` observation is NEVER addressable as `:obs:`.
`MeetingView.tsx:312-323` was taught the third segment and says so in a comment naming the
class; `lib/contradictions.ts:12-18` was not, and `TurnCard.tsx:291-294` maps EVERY
observation through the two-segment helper. Re-measured at HEAD over the committed
`replays/samples` bytes through `api.replay_loader.ReplayLoader` (both sets, 100 games):
328 contradiction endpoints across 164 flags — 144 in 9p2i, 20 in 4p1i — of which 31 are
unresolvable under the shipped two-segment rule and 0 under the three-segment rule. All 31
sit in 9p2i, all are half-linked (no flag has whereabouts on both ends), and they fall
`weak_signal` 29 / `cross_statement` 2. Seven turns have NO other endpoint and therefore render
with zero flags and zero badges: seeds 1 (turns 4 and 6), 32, 33, 36, 44, 46. Per B-22's
verifier, five of those seven are `weak_signal`, which TurnCard.tsx:321-327 already paints in
the speaker's identity colour, so exactly two turns — `headless-seed-32:meeting-0:turn-3` and
`headless-seed-33:meeting-1:turn-3` — lose a real contradiction accent. The badge loss is the
larger half and it is total: 31 lines that should carry a flag do not.

This task closes all three, and closes them so that the next segment cannot repeat the bug: the
three-segment rule gets ONE home in `lib/contradictions.ts`, `MeetingView`'s regex is built
from that same list instead of a second hand-written literal, and a committed-fixture census
walks every served endpoint. The census is written the way `lib/bodies.test.ts` writes its own
— a `corpusSha256` recomputed from `replays/samples/<set>` on every run, so a re-recorded
corpus fails the suite instead of leaving it green over a detached snapshot, and a retired
reference implementation as the perturbation leg, because a zero-unresolved assertion is true
by construction once the fix lands and would otherwise be prose (AGENTS.md craft rule 2).

Two placement rulings, both load-bearing. The census belongs in TypeScript, not in a Python
test beside the minters: a `tests/api/` walk would have to spell the segment rule a THIRD time,
and a rule spelled twice is precisely what produced this defect. It reads a committed fixture
for the reason `bodies.test.ts` gives — the served DTO exists only after the Python loader's
engine re-walk, and re-deriving that in the frontend is the mistake the `lib/` split exists to
stop — and it stays a pure-function test, because `frontend/vitest.config.ts:10-19` declares
`environment: "node"` a contract and a test that needs a real DOM belongs in the journey. The
arrival gate, conversely, cannot be anything but a browser test: the thing being asserted is a
layout fact about a fixed dock, a `ResizeObserver`-published custom property and a lazily
mounted canvas, and no simulated document can produce it.

The arrival gate is written to assert the PROMISE, not the mechanism. What a visitor is owed is
that the whole map is on screen and clear of the dock at the position they land on, without
scrolling and without discovering a disclosure control. Whether that is delivered with the
timeline drawer open or closed is a layout ruling, and the contract does not pre-judge it: the
spec reads `--transport-expanded-min-height` back out of the sheet and asserts the drawer state
AGAINST it, so it stays true whichever side of the threshold 900 ends up on and it keeps that
threshold to one home. What the contract does fix is the posture. The spec is written and run
BEFORE any layout edit, and its first result is recorded either way. If it is red, the repair is
taken at the threshold — the cheapest change with the smallest blast radius, and the config's
1440×960 journey viewport must stay expanded so the six existing tests are untouched. If it is
green, the arrival was already correct and the finding was a missing gate rather than a missing
fix; the perturbation case is then the only thing keeping the new test honest, which is why it
is required in both branches. The assertion is never relaxed to match whatever the layout does.

Two boundaries. Nothing here moves recorded bytes: the served DTO and the minted ids are both
correct, this is a consumer defect, and the fixture is derived from the committed bytes rather
than recorded. But the fixture IS a byte-coupled pin, and the baseline-7 record's own audit
already warned that the census of such pins must start from a repo-wide grep rather than a
`tests/`-scoped one (audits/audit-phase-20-baseline-7.md:721-726, which names
`frontend/src/lib/bodies.test.ts` as the pin that census missed). The PR must name this
fixture as the second member of that class so the combined re-record regenerates it. Those
committed bytes are the baseline-7 record, which is canon by explicit owner override of the
record's FINDING verdict (bars 1 and 2 missed) — the numbers above are properties of those
bytes, not of any bar.

**Files in scope:**
- frontend/src/lib/contradictions.ts; (ONE observation-id rule, exported; the stale "mirrors transcript.py exactly" comment made true)
- frontend/src/lib/contradictions.test.ts; (new: the served-payload census + the retired-rule perturbation leg)
- frontend/src/lib/contradictions.fixture.json; (new: the committed dump of the 100 served meeting payloads the census walks)
- frontend/src/components/TurnCard.tsx; (the observation map dispatches on the discriminant)
- frontend/src/components/MeetingView.tsx; (`eventTurnId`'s regex is built from the shared segment list)
- frontend/e2e/journey.spec.ts; (the 1440×900 default-arrival test + the transcript/evidence assertions in the existing meeting step)
- frontend/src/index.css; (ONLY `--transport-expanded-min-height` and its comment, and only if the 1440×900 arrival measures red)

**Files NOT in scope:**
- frontend/src/types/api.ts (GENERATED — its :1 banner says so; `WhereaboutsClaimView` at :281-282 is already in the union and needs nothing)
- meetings/transcript.py, api/schemas.py, api/replay_loader.py (the backend mints the right ids and serves the right DTO; the docstring half of C-120 at transcript.py:2259 is read as evidence and NAMED in the PR as still open — it belongs to whichever task edits that module, not to a frontend gate task)
- frontend/e2e/media.spec.ts (its 1440×900 capture is gated on `AILIBI_CAPTURE_MEDIA=1` and collapses the drawer before measuring, so it can never be the standing gate; leave it)
- frontend/src/lib/bodies.test.ts, frontend/src/lib/bodies.fixture.json (the prose-truth task owns the narration line there; this task's fixture is a sibling file, not an edit)
- frontend/playwright.config.ts (the 1440×960 default viewport and the one-worker posture stay; the new test sets its own viewport, as the laptop-heights test already does)
- frontend/vitest.config.ts (its `include` glob already picks the new suite up, and `environment: "node"` is the right contract for a pure-function census — the new test renders nothing)
- frontend/src/App.tsx (the dock, `useTransportHeight` and `useRoomyViewport` are correct as built; if the arrival is red the fix belongs at the threshold's one home in `index.css`, not in the shell)
- replays/ (no re-record; the fixture is derived from committed bytes)

**Definition of done:**
- [ ] `frontend/src/lib/contradictions.ts` owns the observation-id rule once: an exported `observationEventId(turn, observation, index)` returns the `:whereabouts:` segment for an observation whose discriminant is `"whereabouts"` and `:obs:` otherwise, and an exported segment list names all three segments (`claim`, `obs`, `whereabouts`). No exported wrapper survives with no caller — if `turnObsEventId` has no remaining consumer after `TurnCard.tsx` moves, it is DELETED rather than kept as a pass-through (AGENTS.md craft rule 3). The module header comment at :8-11 states the three-segment rule and names `_turn_claim_id` / `_turn_observation_id` / `_turn_whereabouts_id` as the minters it mirrors, replacing today's two-helper claim.
- [ ] `frontend/src/components/TurnCard.tsx:291-294` builds each observation's id through `observationEventId`, so the 31 whereabouts-anchored flags resolve onto the line that made the claim; the claim path (:295-298), the `flagged` dedupe (:299-302) and the accent rule (:321-327) are unchanged — a `weak_signal`-only card still renders in the speaker's identity colour, which is Task 19.11's ruling and not this task's to revisit.
- [ ] `frontend/src/components/MeetingView.tsx`'s `eventTurnId` (:321-323) derives its pattern from the shared segment list instead of the hand-written literal at :322, so a fourth segment cannot be taught to one helper and not the other again; the comment at :316-320 is rewritten to state the current rule rather than the history of the miss.
- [ ] `frontend/src/lib/contradictions.fixture.json` is a committed dump of the served meeting payloads for all 100 games under `replays/samples/{9p2i,4p1i}` — per meeting: the contradiction ids with their `category`, `event_a_id`, `event_b_id`, and per turn the `turn_id` with its observation discriminants and claim count in served order — carrying a `corpusSha256` per set. The exact regeneration command lives in the test file's header comment, the way `frontend/src/lib/bodies.test.ts:25-77` carries its own.
- [ ] `frontend/src/lib/contradictions.test.ts` recomputes each set's digest from `replays/samples/<set>` on every run and asserts it equals the fixture's, so a re-recorded corpus fails this suite instead of passing over a detached snapshot; then it walks every fixture meeting, rebuilds the rendered id vocabulary through the shipped helpers, and asserts 0 of 328 endpoints unresolved, each resolving to exactly one rendered line.
- [ ] The same walk over a retired two-segment reference implementation, written inside the test file as the named perturbation leg, reads 31 unresolved endpoints, all in `9p2i`, `weak_signal` 29 / `cross_statement` 2, and 7 turns rendering zero flags (`headless-seed-1:meeting-0:turn-4` and `:turn-6`, plus seeds 32, 33, 36, 44, 46) — so the census demonstrably tells the two rules apart. The PR quotes the before/after as 31/328 → 0/328.
- [ ] The vocabulary itself is gated: the test asserts every endpoint segment observed in the fixture is a member of the module's exported segment list, and fails naming the unknown segment — so a fifth observation type minted with its own segment fails here rather than silently half-linking.
- [ ] `frontend/e2e/journey.spec.ts`'s existing meeting step (:341-352) gains the transcript half: the `Accusation chain & transcript` region is located by its accessible name, at least one turn card (`role="article"`) is visible inside it, every rendered evidence group heading is one of the three taxonomy headings, and the `Evidence (N)` count RECONCILES with the sum of its per-group counts. The empty case is covered by the same assertion rather than skipped — `EvidenceSection` returns `null` on an empty flag list (MeetingView.tsx:408-417), so "no Evidence heading" must imply "no group heading". The PR records that the assertion is non-vacuous today: the featured head is `9p2i` seed 2, whose single meeting has 7 turns and 3 flags, all `weak_signal` — `Evidence (3)` over `Weak signals (3)`.
- [ ] A new `journey.spec.ts` test opens the featured replay at 1440×900 and, with NO scrolling and NO toggling, asserts through `settledGeometry` that the whole map is on screen and clear of the dock: `mapTop >= 0`, `mapBottom <= viewportHeight`, `mapBottom <= dockTop`. It asserts the arrival state against the threshold's one home rather than hardcoding it — reading `--transport-expanded-min-height` back through `getComputedStyle` and asserting `aria-expanded` equals `900 >= threshold` — so the test stays true whichever side of the threshold 900 ends up on.
- [ ] That gate ships with a case proving it bites: the same geometry predicate is asserted FALSE at a viewport where the promise cannot hold — the drawer deliberately toggled expanded at a short viewport, using the deliberate-toggle-wins behaviour already pinned at :554-561 — so a green result at 1440×900 is a fact about the layout, not about a predicate that cannot return false.
- [ ] The HEAD result is recorded before any layout edit: the new test is run at HEAD FIRST and its `mapBottom` / `dockTop` / `viewportHeight` numbers pasted into the PR. If it is red, the repair is taken at the threshold's single home — raise `--transport-expanded-min-height` above 900 while keeping it at or below 960 so the config's 1440×960 default stays expanded and the six existing journey tests are unaffected — with the token's comment (index.css:157-166) rewritten to state the new threshold's reason. The assertion is never weakened to fit the layout, and no second home for the threshold is introduced.
- [ ] Blast radius stated from a fresh grep before anything is deleted: `grep -rn 'turnObsEventId\|turnClaimEventId\|findContradictions\|dedupeContradictions\|eventTurnId' frontend/src frontend/e2e` — at HEAD the only code consumers are `TurnCard.tsx:18-21` and `MeetingView.tsx`; if a hit appears outside the files in scope, stop and report it under Questions rather than widening scope.
- [ ] The PR names two things left open on purpose: the C-120 docstring half at `meetings/transcript.py:2259` (still naming `_turn_observation_id` where :2294 writes `_turn_whereabouts_id`), and `frontend/src/lib/contradictions.fixture.json` as a NEW byte-coupled pin that the combined re-record must regenerate — the second member of the class `audits/audit-phase-20-baseline-7.md:721-726` says the next sweep must find with a repo-wide grep.
- [ ] `cd frontend && npm run test`, `npm run lint`, `npm run tsc:check` and `npm run build` all pass.
- [ ] `cd frontend && npm run e2e` passes (both dev servers; the Playwright leg is deliberately outside `scripts/check.sh` per its :51-56 comment and runs as its own CI job at `.github/workflows/ci.yml:96-154`).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Public types this task introduces
- `frontend/src/lib/contradictions.ts::observationEventId`
- `frontend/src/lib/contradictions.ts::OBSERVATION_EVENT_SEGMENTS`

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
Open a PR from branch `phase-21-frontend-gates` with a title like `task 21.12: the spectator's gates: the laptop sees the map, the meeting dialog asserts, the whereabouts badge renders`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the 1440×900 arrival gap, routed to the phase-20 close ledger with 20.39's merge record `69255980` — audits/audit-phase-20-close.md:409 ("No standing gate asserts that a DEFAULT 1440×900 arrival shows the whole map"), restated in tasks/phase-20.md:6432; B-53 [ADJUSTED, P2] audits/review-2026-08-26/B/collated-findings.md:2801 (row at :61) — the meeting dialog's transcript/evidence half carries no assertion in any standing gate, with the verifier's two corrections BINDING this contract: "zero e2e assertions" is true only of the standing gate (frontend/e2e/media.spec.ts:836-838 does assert a TurnCard, but its whole describe is skipped without `AILIBI_CAPTURE_MEDIA=1`), and the served census denominator is 144 on the default-served set, not 164; B-22 [ADJUSTED, P2] audits/review-2026-08-26/B/collated-findings.md:1318 (row at :30) — a re-report of still-open C-120 (audits/review-2026-08-19/B/collated-findings.md:185), whose fix was already prescribed at audits/review-2026-08-19/B/meetings-transcript-voting.md:133, with the verifier's accent correction BINDING: 5 of the 7 half-blank turns are `weak_signal`, which Task 19.11's taxonomy already paints in the speaker identity colour, so exactly 2 turns lose a real contradiction accent. Anchors re-verified at HEAD `4002f19b` (clean tree): frontend/src/lib/contradictions.ts:12-18 (`turnClaimEventId` / `turnObsEventId` — two segments) and :8-11 (the comment claiming the module "mirrors `meetings/transcript.py` exactly"); frontend/src/components/TurnCard.tsx:291-294 (every observation mapped through `turnObsEventId`), :299-302 (`flagged`), :321-327 (the three-way accent: `role_proof` → ink, `cross_statement` → contradiction, else `playerColor`); frontend/src/components/MeetingView.tsx:312-323 (the sibling helper that WAS taught the segment, with its comment naming the class) and :322 (`/^turn:(.+):(?:claim|obs|whereabouts):\d+$/`), :283 (the transcript panel `Accusation chain & transcript`), :61-66 (`Panel` renders `<section aria-label={title}>`), :408-417 (`EvidenceSection` returns `null` on an empty flag list), :464-474 (the `Evidence (N)` heading and each group's `heading (n)`); meetings/transcript.py:4065 / :4069 / :4073 (`_turn_claim_id` / `_turn_observation_id` / `_turn_whereabouts_id`) and :3746-3753 (the exclusive per-observation branch), :2259 vs :2294 (the docstring still names `_turn_observation_id` where the code writes `_turn_whereabouts_id` — the second half of C-120, deliberately not in scope here); api/schemas.py:563 + :577 (`WhereaboutsClaimView`, `type: Literal["whereabouts"]`) and frontend/src/types/api.ts:281-282 + :747 (the discriminated union; the file is GENERATED per its :1 banner); frontend/e2e/journey.spec.ts:203-205 (`timelineDisclosure`), :224-245 (`mapAndDockGeometry`), :248-254 (`scrollMapToTop`), :262-270 (`settledGeometry`), :341-352 (the ONLY meeting assertions today: the dialog, its `aria-label`, the `Ballots (N)` region, the word "confidence", one `p-N`), :505-561 (the laptop-heights test — 1280×800 and 1000×640, both asserted with the drawer `aria-expanded="false"`), :554-561 (a deliberate toggle wins over the height default for the rest of the session); frontend/e2e/media.spec.ts:92 (`SHOT_VIEWPORT` 1440×900), :344-364 (`uncoverMap` collapses the Timeline drawer BEFORE it measures), :56 + :730-734 (the capture gate), :836 (`dialog.locator("article")` — the turn card's handle); frontend/playwright.config.ts:70 (default viewport 1440×960), :49 (`testDir: "./e2e"`), :82 (`AILIBI_REPLAY_DIR=replays/samples`, so both sets are served); frontend/src/index.css:157-168 (`--transport-expanded-min-height: 860px`, declared the ONE home for the threshold) and frontend/src/App.tsx:1049-1055 (`expandedHeightQuery` reads it back) + :1057-1073 (`useRoomyViewport`); frontend/vitest.config.ts:10-19 (`environment: "node"` as a stated contract) and frontend/src/lib/bodies.test.ts:17-25 + :25-77 (the committed-fixture rationale and the regeneration recipe carried in the header) + :441 + :466 + :507-511 (the digest assertion and the retired-rule perturbation leg); scripts/check.sh:51-56 + :66 (four frontend legs, e2e deliberately not among them) and .github/workflows/ci.yml:96-154 (the `frontend-e2e` job that does run `npm run e2e`).), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
