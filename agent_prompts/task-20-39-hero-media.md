# Agent Prompt — 20.39 The hero image: one tick, two truths — and a ten-second clip

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-20.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 20.39 — The hero image: one tick, two truths — and a ten-second clip, anchored to audits/review-2026-08-19/C/collated-portfolio.md §A3 (the GIF finding, VERIFIED by frame sheet + layout math) + §F4 (the media list: keep the meeting still, re-record the walk, optionally ship MP4/WebM) + §D1 (the ruling: "re-record"); audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the measurement: at the 1000×640 recording viewport the fixed bottom dock covers the PixiJS canvas entirely — canvas top 311 px vs dock top 308 px, page height 1078 px — over all 20 sampled frames; "I never see the map or an agent move"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.3 + §7 "The one image"; audits/review-2026-08-19/B/frontend-a.md §F1 (the phantom-body layer the map still would otherwise show); README.md:12 + :14 (the GIF and its caption — the review's quoted "the map" promise is GONE, rewritten by 20.12/20.36/20.38; the caption now reads "pick a featured game, play it, watch the transport stop itself when a meeting starts", and the alt text is the neutral "The spectator playing a featured replay"), :7 + :9 (the meeting still, PROMOTED to first image, and its caption — "One meeting, seed 2", no longer "tick 7"), :10 (the ANCHOR comment a sibling left standing for this task: "a later contract swaps this hero for a side-by-side still, omniscient beside one crewmate's fog-of-war"); docs/media/README.md:6-10 (the asset table — THREE rows since 20.20 added the `architecture.svg` row at :10), :30-32 ("a screenshot is a claim about the product, and a stale one is a false claim"), :36-39 (the harness deliberately NOT committed), :50-56 (the recorded walk and the 1000×640 recording viewport), :57-69 (the stripped ffmpeg + the Pillow palette note), :71-73 (the size budget); docs/artifacts.md:108 (the registry row `docs/media/` — now "the README captures + the as-built architecture picture", "1.7 MB / 4 files" since 20.20 committed `architecture.svg`) enforced against `git ls-files docs/media` by scripts/verify_ml_evidence.py:2348 (the `_IN_TREE_INVENTORY["docs/media/"]` scope) and :2359-2388 (`inventory_problems`, the count-parity check), pinned by tests/scripts/test_verify_ml_evidence.py:1500-1526 and :1529-1546; frontend/e2e/journey.spec.ts:563-655 (the fog firewall walk and its controls — the "As-agent" button, "Exit fog", the "Perspective agent" picker, the `perspective=p-N` URL key), :657-693 (the reduced-motion probe), :217-270 (`mapAndDockGeometry` / `settledGeometry` — 20.3's map-vs-dock geometry helpers, with `.map-canvas-fill` named as the map's stable on-screen handle) + :505-561 (20.3's "the transport dock leaves the map on screen at laptop heights" — the overlap assertion this task's capture re-uses rather than reinvents); frontend/e2e/bundle.spec.ts:63-80 (`buildBundle` + the `AILIBI_DEMO_BUNDLE_DIR` reuse env), :88-114 (`serveStatic`), :158-198 (the `bundle` fixture); frontend/playwright.config.ts (testDir `./e2e`, `video: "off"`, one worker, `outputDir: "./e2e/.artifacts"`); frontend/src/lib/playback.ts:380-387 (the eight round-tripping URL keys — set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting / reveal), :423 (`parsePlaybackParams`); frontend/src/components/MapView.tsx:105-108 (`prefersReducedMotion` gates the tween, the kill flash and the vent dive), :546 (the body layer, called through `bodyStatesByTick` — 20.1 extracted it to frontend/src/lib/bodies.ts:82; there is no `buildBodyStatesByTick` symbol at HEAD), :418 (`KillFlash`); frontend/src/components/MapToolbar.tsx:133-196 (the Omniscient ↔ As-agent group and the agent picker); frontend/src/App.tsx:310-331 (the perspective banner and "Exit fog"; `PerspectiveBanner` opens at :255), :1144-1152 (`data-transport-region`); frontend/src/components/ReplayPicker.tsx:103-146 (`FEATURED_GAMES` — still seven curated games, but RE-CURATED by 20.36: 9p2i seeds 2, 23, 13, 46 and 4p1i seeds 29, 2, 11). Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-20.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-20-hero-media`
**Depends on:** 20.1, 20.3, 20.36, 20.38 (four edges, in the order the ids are listed: the body layer must read engine truth before a still of the map becomes the front door, or the hero paints corpses the engine already deleted; the dock must stop covering the canvas before any capture can contain the map at all, which is the measured cause of the current failure; the adopting record moves the bytes and re-curates the featured list, so the seed, the tick, the agent and the accusation this still names cannot be chosen before it exists; and the README results prose lands first, so this task swaps images into a finished page instead of racing another writer for the same file)
**Section refs:** audits/review-2026-08-19/C/collated-portfolio.md §A3 (the GIF finding, VERIFIED by frame sheet + layout math) + §F4 (the media list: keep the meeting still, re-record the walk, optionally ship MP4/WebM) + §D1 (the ruling: "re-record"); audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the measurement: at the 1000×640 recording viewport the fixed bottom dock covers the PixiJS canvas entirely — canvas top 311 px vs dock top 308 px, page height 1078 px — over all 20 sampled frames; "I never see the map or an agent move"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.3 + §7 "The one image"; audits/review-2026-08-19/B/frontend-a.md §F1 (the phantom-body layer the map still would otherwise show); README.md:12 + :14 (the GIF and its caption — the review's quoted "the map" promise is GONE, rewritten by 20.12/20.36/20.38; the caption now reads "pick a featured game, play it, watch the transport stop itself when a meeting starts", and the alt text is the neutral "The spectator playing a featured replay"), :7 + :9 (the meeting still, PROMOTED to first image, and its caption — "One meeting, seed 2", no longer "tick 7"), :10 (the ANCHOR comment a sibling left standing for this task: "a later contract swaps this hero for a side-by-side still, omniscient beside one crewmate's fog-of-war"); docs/media/README.md:6-10 (the asset table — THREE rows since 20.20 added the `architecture.svg` row at :10), :30-32 ("a screenshot is a claim about the product, and a stale one is a false claim"), :36-39 (the harness deliberately NOT committed), :50-56 (the recorded walk and the 1000×640 recording viewport), :57-69 (the stripped ffmpeg + the Pillow palette note), :71-73 (the size budget); docs/artifacts.md:108 (the registry row `docs/media/` — now "the README captures + the as-built architecture picture", "1.7 MB / 4 files" since 20.20 committed `architecture.svg`) enforced against `git ls-files docs/media` by scripts/verify_ml_evidence.py:2348 (the `_IN_TREE_INVENTORY["docs/media/"]` scope) and :2359-2388 (`inventory_problems`, the count-parity check), pinned by tests/scripts/test_verify_ml_evidence.py:1500-1526 and :1529-1546; frontend/e2e/journey.spec.ts:563-655 (the fog firewall walk and its controls — the "As-agent" button, "Exit fog", the "Perspective agent" picker, the `perspective=p-N` URL key), :657-693 (the reduced-motion probe), :217-270 (`mapAndDockGeometry` / `settledGeometry` — 20.3's map-vs-dock geometry helpers, with `.map-canvas-fill` named as the map's stable on-screen handle) + :505-561 (20.3's "the transport dock leaves the map on screen at laptop heights" — the overlap assertion this task's capture re-uses rather than reinvents); frontend/e2e/bundle.spec.ts:63-80 (`buildBundle` + the `AILIBI_DEMO_BUNDLE_DIR` reuse env), :88-114 (`serveStatic`), :158-198 (the `bundle` fixture); frontend/playwright.config.ts (testDir `./e2e`, `video: "off"`, one worker, `outputDir: "./e2e/.artifacts"`); frontend/src/lib/playback.ts:380-387 (the eight round-tripping URL keys — set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting / reveal), :423 (`parsePlaybackParams`); frontend/src/components/MapView.tsx:105-108 (`prefersReducedMotion` gates the tween, the kill flash and the vent dive), :546 (the body layer, called through `bodyStatesByTick` — 20.1 extracted it to frontend/src/lib/bodies.ts:82; there is no `buildBodyStatesByTick` symbol at HEAD), :418 (`KillFlash`); frontend/src/components/MapToolbar.tsx:133-196 (the Omniscient ↔ As-agent group and the agent picker); frontend/src/App.tsx:310-331 (the perspective banner and "Exit fog"; `PerspectiveBanner` opens at :255), :1144-1152 (`data-transport-region`); frontend/src/components/ReplayPicker.tsx:103-146 (`FEATURED_GAMES` — still seven curated games, but RE-CURATED by 20.36: 9p2i seeds 2, 23, 13, 46 and 4p1i seeds 29, 2, 11)
**Complexity:** Small
**Record impact:** post-record — both assets are captures OF the baseline-7 bytes and cannot honestly be shot before the record lands; this task moves no recorded byte and no production source file.
**Measurement:** `cd frontend && AILIBI_CAPTURE_MEDIA=1 npx playwright test e2e/media.spec.ts` regenerates both assets from the committed bytes — two consecutive runs produce a byte-identical `spectator-two-truths.png` and a clip with identical frame dimensions and a duration equal within one recorded frame (the spec prints both), the still is ≤ 400 kB and the clip ≤ 3 MB; `cd frontend && npm run e2e` and `npm run tsc:check` stay green with the media spec reported SKIPPED; `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` green (the `docs/media/` registry row still equals `git ls-files docs/media`); the README rendered on the PR branch shows the still and the clip.

The single asset the most people will ever see does not show the product. The
review verified it by extracting twenty frames and re-measuring the layout at
three viewports: at the 1000×640 viewport `docs/media/README.md:54-56` records as
the recording viewport, the fixed bottom dock covers the PixiJS canvas entirely —
canvas top 311 px against dock top 308 px on a 1078 px page — so
`spectator-journey.gif` shows a picker, a timeline dock, a modal and a finale card,
and never a map or a moving token (audits/review-2026-08-19/C/p3-frontend-product-engineer.md;
collated as §A3 of audits/review-2026-08-19/C/collated-portfolio.md). The GIF's
caption has since been rewritten — README.md:14 now reads only "pick a featured
game, play it, watch the transport stop itself when a meeting starts", so the
review's quoted "the map" promise is ALREADY GONE, and 20.36/20.38 demoted the GIF
below the meeting still, which is now the first image at README.md:7. The finding
survives the rewrite intact: the ASSET is untouched since 19.13 and still shows a
picker, a dock, a modal and a finale card and never a map or a moving token — a
walk-through GIF that never contains the product is a weaker front door, not a
truer one, and it is still the only motion asset the page has. By
`docs/media/README.md`'s own standard at :30-32 — a screenshot is a claim about the
product, and a stale one is a false claim — the committed recipe still encodes the
cause.

The endorsed replacement is not a better GIF. It is a still of ONE tick shown
twice: the omniscient map on the left, the same tick under one crewmate's
As-agent fog on the right, captioned in the shape "Left: what happened. Right:
everything <that crewmate> was allowed to know when it voted", with the
accusation card that crewmate actually wrote at the following meeting composited
underneath (audits/review-2026-08-19/D/FINAL-synthesis.md §7 "The one image").
That frame states all four of this project's stories at once — the observation
firewall, the product, the research premise, and, beside the byline, the
authorship — and it needs no new UI: both halves already render, and
`frontend/e2e/journey.spec.ts:563-655` already pins the firewall behaviour the
right half is a picture of. Beside it goes an 8–10 s clip at ≥1440×900 carrying
the four beats a still cannot: a token moving between rooms, a kill flash, the
transport stopping ITSELF when a meeting starts, and the perspective flipping into
fog (audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.3). The meeting
still stays — every persona called it the money shot (§F4, §D1) — but it stops
being the only picture that shows anything.

Three of this task's four edges are the reason it is last rather than first. The
dock had to stop covering the canvas before any capture could contain the map;
the omniscient body layer had to start reading engine truth before a front-door
still could be trusted not to paint corpses the engine already deleted
(audits/review-2026-08-19/B/frontend-a.md §F1); and the adopting record both moves
the bytes and re-curates `FEATURED_GAMES` (frontend/src/components/ReplayPicker.tsx:103-146 — 20.36 has now done so: 9p2i seeds 2, 23, 13, 46 and 4p1i seeds 29, 2, 11),
so the seed, the tick, the fog subject and the quoted accusation can only be
chosen from the recorded corpus that will actually ship. Choosing them earlier
would publish a caption about a game the repository no longer contains — which is
exactly the failure mode now LIVE at README.md:7-9. The committed
`spectator-meeting.png` was shot at 19.13 from the baseline-6 bytes of 9p2i seed 2,
and 20.36 re-recorded that seed on 2026-08-25 (replays/samples/9p2i, Qwen/Qwen3.6-27B,
prompt set v4, $0), so the front door's first image now renders a game whose bytes
the repository no longer holds. The caption's "tick 7" is already gone; the stale
CAPTURE is not.

This task also reverses one earlier call, deliberately and with its reason
recorded. Phase 19 chose NOT to commit the capture harness
(`docs/media/README.md:36-39`: "a dozen lines of throwaway Playwright"), and the
consequences are now measurable — an asset nobody can regenerate, a recipe that
silently encodes a broken viewport, and no way to re-shoot the hero when the bytes
move. A composite of two perspectives of one tick is not a dozen lines: it must
prove the two halves are the same tick, it must name the fog subject, and its
provenance is load-bearing to the caption's truth. So the walk becomes a committed,
re-runnable script — gated OFF in the default gate, so the standing Playwright leg
(`npm run e2e`, and the `frontend-e2e` CI job that runs it) costs exactly what it
costs today.

Two honesty constraints ride along. First, the clip's README reference is
verify-then-write: check what GitHub actually renders for the committed reference
form on the PR branch and record the answer; if inline playback does not render
from a repository-relative path, the README falls back to the still linking to
the clip and the regenerated GIF stays as the motion asset — the choice recorded
in `docs/media/README.md`, never assumed. Second, the `docs/media/` row of the
artifact registry states a file count that a test compares against `git ls-files`
at HEAD (docs/artifacts.md:108, today "1.7 MB / 4 files", against
scripts/verify_ml_evidence.py:2359-2388 and tests/scripts/test_verify_ml_evidence.py:1500-1546),
so changing this directory's file set without restating that row turns
`uv run pytest` red — the count moves in this PR or the PR is not green.

**Files in scope:**
- frontend/e2e/media.spec.ts; (new: a Playwright script that opens the featured seed at the chosen tick in both perspectives, screenshots at 1440×900, and records the clip — re-runnable against the built bundle)
- docs/media/spectator-two-truths.png; (new)
- docs/media/spectator-journey.mp4; (new — the clip, with the GIF retired or regenerated at the correct viewport)
- docs/media/README.md; (asset provenance: seed, tick, viewport, the command)
- README.md; (the hero swap + caption)
- docs/artifacts.md; (the docs/media/ registry row count)
- docs/media/spectator-meeting.png; (re-shot from the re-recorded featured seed so the hero still pictures a game the repository contains)

**Files NOT in scope:**
- frontend/src (no UI change: the body layer, the dock and the fog switcher all landed earlier in this phase — if the capture wants a UI change to look good, the capture is wrong)
- replays/ (reads the committed bytes; nothing re-records here)
- docs/media/architecture.svg (committed by 20.20 after this contract was authored, and pinned by tests/scripts/test_check_doc_facts.py:2182 — its bytes and its asset-table row are untouched here; it is why the registry row reads 4 files rather than the 3 this contract was written against)
- frontend/playwright.config.ts + frontend/package.json (the capture opts itself out from inside the spec; the shared browser config, the worker count and the npm scripts are untouched)
Orchestrator ruling (2026-08-26): the scope contradiction on spectator-meeting.png resolves to RE-SHOOT — the NOT-in-scope line is struck; the still is re-shot from the recorded baseline-7 9p2i seed 2 with its provenance tuple recorded in docs/media/README.md (the front door's first image must picture a game the repository holds).

**Definition of done:**
- [ ] `frontend/e2e/media.spec.ts` is committed, typechecks under `cd frontend && npm run tsc:check` (the `e2e/tsconfig.json` leg), and is INERT in the default gate: the whole file skips unless the capture is explicitly requested, so `npm run e2e` and the `frontend-e2e` CI job report the same passing counts as before this PR plus the skip — the PR quotes both run summaries.
- [ ] The still is one PNG of ONE tick shown twice — omniscient left with the map, rooms and tokens in frame; the same tick under one crewmate's As-agent fog right, lit only where that crewmate could see — with the caption naming the ACTUAL fog subject and the actual moment (not the review's illustrative "p-3"), and the accusation card that crewmate wrote composited underneath. The spec ASSERTS both halves came from the same `tick=` deep-link value and the same `game_id`, so "the same tick" is a checked claim rather than a caption.
- [ ] Each half is captured at ≥1440×900 with the map canvas fully uncovered — the spec asserts the canvas rect is not overlapped by `[data-transport-region]` before it shoots — reusing the shape 20.3 already landed at frontend/e2e/journey.spec.ts:217-270 (`mapAndDockGeometry` / `settledGeometry` over the `.map-canvas-fill` wrapper, which is the map's stable handle) and asserts at :505-561 — and the committed PNG is ≤ 400 kB.
- [ ] The clip is ≤ 10 s and ≤ 3 MB and contains, in order, an agent token moving between rooms, a kill flash, the transport pausing itself at a meeting, and the perspective flipping into As-agent fog; it is recorded at ≥1440×900, and the spec asserts each beat happened (a room change between two frames, a kill event at the flashed tick, the pause state, the `perspective=p-N` URL key) rather than trusting the walk.
- [ ] Determinism, pinned by the measurement: two consecutive capture runs produce a byte-identical `spectator-two-truths.png`, and a clip whose frame dimensions are identical and whose duration differs by at most one recorded frame; the spec prints the digests, the dimensions and the duration so the PR can quote them.
- [ ] `docs/media/README.md` states the exact one-line command that regenerates both assets from the committed bytes, plus the full provenance tuple for each (set, seed, game id, engine tick, viewport, fog subject, the bundle build command, and the baseline the bytes come from), and its asset table lists exactly the files committed under `docs/media/` — no row for a retired asset, no asset without a row.
- [ ] README's hero is swapped: the two-truths still leads with a one-sentence caption, the clip replaces the GIF, and every remaining sentence about the media describes what the asset actually shows — the review's "the map" promise is already gone from the caption, so the bar here is the stronger one: the new asset actually SHOWS the map, and the ANCHOR comment left for this task at README.md:10 is consumed — acted on and removed — rather than left standing over a swapped hero. The clip's reference form is VERIFIED against the rendered README on the PR branch and the PR states what rendered; if inline playback does not render from a repository-relative path, the recorded fallback ships instead.
- [ ] The artifact registry's `docs/media/` row states the committed file set (count and size) for the new inventory, so `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` and `uv run python scripts/verify_ml_evidence.py --complete` stay green — the file-count comparison at scripts/verify_ml_evidence.py:2359-2388 (`inventory_problems`, pinned by tests/scripts/test_verify_ml_evidence.py:1500-1526 and :1529-1546) reads `git ls-files docs/media` and fails otherwise; the row's inventory scope is `_IN_TREE_INVENTORY["docs/media/"]` at scripts/verify_ml_evidence.py:2348, and the count at HEAD is 4 — README.md, architecture.svg, the GIF and the meeting PNG.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import check_doc_facts"`
- `uv run python -c "import eval.leak_scan"`
- `uv run python -c "import eval.evidence_honesty"`
- `uv run python -c "import eval.solvability"`
- `uv run python -c "import tests._helpers.committed"`
- `uv run python -c "import eval.validity"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import meetings.render_contract"`
- `uv run python -c "import agents.strategic.prompts.loader"`
- `uv run python -c "import agents.memory.store"`
- `uv run python -c "import meetings.transcript"`
- `uv run python -c "import meetings.constants"`
- `uv run python -c "import meetings.schemas"`
- `uv run python -c "import meetings.manager"`
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
Open a PR from branch `phase-20-hero-media` with a title like `task 20.39: the hero image: one tick, two truths — and a ten-second clip`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing audits/review-2026-08-19/C/collated-portfolio.md §A3 (the GIF finding, VERIFIED by frame sheet + layout math) + §F4 (the media list: keep the meeting still, re-record the walk, optionally ship MP4/WebM) + §D1 (the ruling: "re-record"); audits/review-2026-08-19/C/p3-frontend-product-engineer.md (the measurement: at the 1000×640 recording viewport the fixed bottom dock covers the PixiJS canvas entirely — canvas top 311 px vs dock top 308 px, page height 1078 px — over all 20 sampled frames; "I never see the map or an agent move"); audits/review-2026-08-19/D/FINAL-synthesis.md §4 wave 3 row 3.3 + §7 "The one image"; audits/review-2026-08-19/B/frontend-a.md §F1 (the phantom-body layer the map still would otherwise show); README.md:12 + :14 (the GIF and its caption — the review's quoted "the map" promise is GONE, rewritten by 20.12/20.36/20.38; the caption now reads "pick a featured game, play it, watch the transport stop itself when a meeting starts", and the alt text is the neutral "The spectator playing a featured replay"), :7 + :9 (the meeting still, PROMOTED to first image, and its caption — "One meeting, seed 2", no longer "tick 7"), :10 (the ANCHOR comment a sibling left standing for this task: "a later contract swaps this hero for a side-by-side still, omniscient beside one crewmate's fog-of-war"); docs/media/README.md:6-10 (the asset table — THREE rows since 20.20 added the `architecture.svg` row at :10), :30-32 ("a screenshot is a claim about the product, and a stale one is a false claim"), :36-39 (the harness deliberately NOT committed), :50-56 (the recorded walk and the 1000×640 recording viewport), :57-69 (the stripped ffmpeg + the Pillow palette note), :71-73 (the size budget); docs/artifacts.md:108 (the registry row `docs/media/` — now "the README captures + the as-built architecture picture", "1.7 MB / 4 files" since 20.20 committed `architecture.svg`) enforced against `git ls-files docs/media` by scripts/verify_ml_evidence.py:2348 (the `_IN_TREE_INVENTORY["docs/media/"]` scope) and :2359-2388 (`inventory_problems`, the count-parity check), pinned by tests/scripts/test_verify_ml_evidence.py:1500-1526 and :1529-1546; frontend/e2e/journey.spec.ts:563-655 (the fog firewall walk and its controls — the "As-agent" button, "Exit fog", the "Perspective agent" picker, the `perspective=p-N` URL key), :657-693 (the reduced-motion probe), :217-270 (`mapAndDockGeometry` / `settledGeometry` — 20.3's map-vs-dock geometry helpers, with `.map-canvas-fill` named as the map's stable on-screen handle) + :505-561 (20.3's "the transport dock leaves the map on screen at laptop heights" — the overlap assertion this task's capture re-uses rather than reinvents); frontend/e2e/bundle.spec.ts:63-80 (`buildBundle` + the `AILIBI_DEMO_BUNDLE_DIR` reuse env), :88-114 (`serveStatic`), :158-198 (the `bundle` fixture); frontend/playwright.config.ts (testDir `./e2e`, `video: "off"`, one worker, `outputDir: "./e2e/.artifacts"`); frontend/src/lib/playback.ts:380-387 (the eight round-tripping URL keys — set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting / reveal), :423 (`parsePlaybackParams`); frontend/src/components/MapView.tsx:105-108 (`prefersReducedMotion` gates the tween, the kill flash and the vent dive), :546 (the body layer, called through `bodyStatesByTick` — 20.1 extracted it to frontend/src/lib/bodies.ts:82; there is no `buildBodyStatesByTick` symbol at HEAD), :418 (`KillFlash`); frontend/src/components/MapToolbar.tsx:133-196 (the Omniscient ↔ As-agent group and the agent picker); frontend/src/App.tsx:310-331 (the perspective banner and "Exit fog"; `PerspectiveBanner` opens at :255), :1144-1152 (`data-transport-region`); frontend/src/components/ReplayPicker.tsx:103-146 (`FEATURED_GAMES` — still seven curated games, but RE-CURATED by 20.36: 9p2i seeds 2, 23, 13, 46 and 4p1i seeds 29, 2, 11)), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
