# Code review — frontend-b (stores, api client, types, shell, tests, config, build, demo bundle)

Reviewer label: frontend-b. Read-only. Repo: /Users/danielkeinan/projects/AiLibi @ main (b809b19c). Node v26.0.0 locally (CI pins Node 22), npm 12.0.1.
Machine load during timings: `uptime` load averages 4.4–8.5 on a 10-core box shared with other reviewers — timings are indicative only.

## 1. Executive read (10 lines)

1. This slice of the frontend is small, strictly typed and in good build health: `tsc --noEmit` ×3 projects (4.6 s), `eslint .` clean (2.2 s), `vitest run` 173 tests green in 0.86 s wall, `vite build` 3.4 s wall (rolldown), Storybook builds in 3.6 s. No `any`, no `@ts-ignore`, no `console.*`, two justified `eslint-disable` lines outside my area.
2. Type generation is real and un-drifted: `scripts/gen_frontend_types.py --check` passes on committed `types/api.ts` + `api.fidelity.ts` (0.4 s); the runtime `VIEW_MODEL_VERSION` gate in `client.ts` is unit-tested; the tokens→CSS generator is idempotent against the committed `index.css` (verified in scratch).
3. State design is a single Zustand store (`replayStore.ts`, 689 lines, ~394 code) plus a 71-line sibling; race handling is careful (monotonic tokens, game+set post-await guards, per-key error maps) and, unusually, actually tested by deterministic out-of-order promise settlement.
4. The biggest real defect is architectural, not local: the store "windows" the bulk replay payload AFTER download — 75–81 % of every `GET /replays/{id}` body (0.4–0.9 MB per 9p2i game, measured) is LLM prompt/response text that `windowReplay()` immediately discards and `fetchMeeting()` later re-downloads. The static demo bundle bakes the same bytes twice.
5. The API client's "one seam" claim is not honoured: two components bypass it with raw `fetch` (one re-implements `getRubric`, the other hits an endpoint the client does not have), skipping the version gate and `ApiError` typing.
6. Startup issues a redundant `GET /replays` (no set) before `/sets` resolves the default and the list is fetched again — observed live in the dev server (plus StrictMode doubling in dev).
7. Agent-authored comment sprawl is heavy in exactly the files that should be terse: 34–66 % comment lines in store/client/config files, 22 "Task N.N" citations in `replayStore.ts`, 24 in `App.tsx`; many comments narrate task history rather than the invariant.
8. `App.tsx` (1181 lines) has grown from "shell that is never edited" into a God module hosting six real components (RosterRail, PerspectiveBanner, MeetingPauseBar, FinaleCard, RecapRow, KeyboardTransport) — 20 commits despite its own header's no-edit doctrine.
9. Tests in this area are behavioural (store guards via `getState()`, client via stubbed `fetch`, tokens via disk scan) — genuinely good; gaps are the static-mode branches of `apiUrl/pathSegment` (only covered by a Playwright build-and-serve spec) and the fact that the local box has no Playwright browser installed, so e2e was not run here.
10. Dependencies are lean and deduped (24 top-level, no unused, one React copy); the lockfile is v3 and consistent. Minor: no `engines`, `@types/node@22` while local dev runs Node 26.

## 2. Findings (ranked)

### F1 — P1 [VERIFIED] Bulk replay payload is "windowed" on the wrong side of the wire
- `frontend/src/store/replayStore.ts:239-256` (`windowReplay`) strips `prompt_text`/`response_text` from every `llm_calls` entry *after* `api.getReplay()` returns; `api/routes/replays.py:45-50` serves the full `ReplayView` unmodified. `fetchMeeting` (`replayStore.ts:560-610`) then re-downloads the whole `MeetingView` (bodies included) on first LLMCallCard expand.
- Measured with `api.replay_loader.ReplayLoader` on the committed 9p2i sample set (scratch script `work/frontend-b/payload_size.py`): total ReplayView JSON 0.40–0.86 MB per game, of which bodies are 74.7–81.2 % (e.g. `headless-seed-2`: 0.72 MB total, 0.57 MB bodies, ticks 0.10 MB). 4p1i: 0.07–0.09 MB, bodies 56–69 %.
- Observed live in the dev server via the browser pane: `GET /api/replays/headless-seed-2?set=9p2i` transferred 718 181 bytes (`transferSize == decodedBodySize` — no gzip on the API side either; API is another reviewer's area, noted for them).
- `scripts/build_demo_bundle.py:298-317` bakes `replays/<gid>.json` with the bodies AND `meetings/<mid>.json` with the same bodies — every featured game's LLM text is on disk twice in the demo artifact.
- Why it matters: the store comment (`replayStore.ts:239-247`) claims windowing "windows the bulk payload (DESIGN.md §11.4)"; in reality it only bounds retained memory. First-open latency and bundle size pay ~4× what the UI needs. Fix belongs at the DTO/route (a `?bodies=0`/lean ReplayView, or a server-side strip that the client's `windowReplay` merely mirrors) — the client change is a one-liner once the server does it.
- Confidence: high.

### F2 — P1 [VERIFIED] The API client is not the single seam it claims to be
- `frontend/src/api/client.ts:8-14` ("there is no parallel client … nothing downstream of `apiUrl()` knows which mode it is in") vs:
  - `frontend/src/components/TournamentDashboard.tsx:1028-1055` — raw `fetch(apiUrl("/eval/rubric", seedSet))` re-implementing 404/err handling that `api.getRubric()` (`client.ts:319`) already provides and that `ReplayPicker.tsx:604-625` uses correctly. `RubricView` carries `viewModelVersion`, so this path silently skips the `assertViewModelVersion` gate that Task 19.24 added — a drifted server mis-renders the dashboard rubric while the browser tab fails loudly.
  - `frontend/src/components/BeliefMatrix.tsx:33-49` — raw `fetch` of `/replays/{id}/beliefs`; there is no `getBeliefFrames` in `client.ts` at all, while `client.ts` exports two dead methods (`getTick` :257, `getEvalCostSummary` :295 — zero call sites outside the store test's `vi.mock` list).
- Why it matters: the version gate and `ApiError` typing are the client's whole reason to exist; two of the seven live endpoints escape it. Also duplicated fetch/error boilerplate.
- Confidence: high.

### F3 — P2 [VERIFIED] Redundant startup fetch + list flash
- `App.tsx:1153-1155` fires `loadReplayList()` on mount (set = null → server default); `ReplayPicker.tsx:596-641` fires `loadSets()` then, once `seedSet` resolves, `loadReplayList()` again — which first sets `replayList: null` (`replayStore.ts:337`), so the browser flashes "Loading" after having shown cards. Live network log at `http://localhost:5173/`: `/api/replays` ×2, `/api/sets` ×2 (StrictMode dev doubling), then `/api/replays?set=9p2i`. In prod: 3 requests where 2 suffice, and one visible list reset.
- Fix: drop the App-level mount fetch (or make `loadReplayList` a no-op until `seedSet` is resolved) — one owner of the initial fetch.

### F4 — P2 [VERIFIED] No in-flight de-duplication in `fetchMemoryView` / `fetchMeeting`
- `replayStore.ts:475-479, 562-566` de-duplicate only *completed* cache entries. Scratch probe (`work/frontend-b/inflight.test.ts`, run with a scratch vitest config): 3 overlapping `fetchMemoryView("m-0","p-1")` → `api.getMemory` called 3×; 2 overlapping `fetchMeeting("m-0")` → 2×.
- The store's own comments (`:497-507`, `:590-596`) acknowledge the overlap ("the inspector re-runs its fetch effect…", "a Prompt → Belief → Prompt tab switch … issuing a second request while the first is still in flight") and paper over it with ~30 lines of "stale same-key failure" guards + 4 tests. A `Map<key, Promise>` of in-flight requests would delete both the duplicate network calls and that guard class. Accidental complexity, not a correctness bug.

### F5 — P2 [VERIFIED] Dead code in the store/client surface
- `replayStore.ts:615-622 clearError()` and `tournamentStore.ts:67-69 clearError()` — no callers outside their own tests (`grep -rn "clearError\b" src` → only stores + replayStore.test.ts).
- `client.ts:257 getTick`, `:295 getEvalCostSummary`, and `lib/playback.ts isStartIndex` — used only by tests / the `vi.mock` list.
- `import { VIEW_MODEL_VERSION }` fixture mismatch: `replayStore.test.ts:78` stamps `viewModelVersion: "1.0"` while the generated constant is `"1"` (harmless — the mocked client never runs the gate — but a stale fixture).

### F6 — P2 [VERIFIED] `App.tsx` is a God module contradicting its own header
- 1181 lines / ~850 code, defining `KeyboardTransport` (:120), `TopNav` (:221), `PerspectiveBanner` (:270, ~130 lines), `RosterRail` (:398, ~180), `MeetingPauseBar` (:616, ~100), `RecapRow`/`FinaleCard` (:741-1020, ~280), `useTransportHeight`, `Workspace`, `App`. Header (:1-48) still explains at length that Wave-B surfaces plug in "WITHOUT ever editing this file", then narrates why Phase 12.11 and Phase 19 edited it anyway; `git log` shows 20 commits.
- Fix: move the four real components into `components/` (they are ordinary store consumers) and cut the header to the slot table.

### F7 — P2 [VERIFIED] Comment/docstring sprawl restating task history
- Comment-line share (grep of leading `//`/`*` lines): `replayStore.ts` 34 %, `client.ts` 38 %, `vite.config.ts` 45 %, `eslint.config.js` 46 %, `playwright.config.ts` 54 %, `vitest.config.ts` 66 %, `e2e/journey.spec.ts` 39 %. "Task N.N" citations: 22 in `replayStore.ts`, 24 in `App.tsx`, 9 in `usePlayback.ts`, 8 in `client.ts`.
- Representative: `replayStore.ts:74-113` (40 lines explaining why three error fields exist and how the old single field failed — history, not contract); `selectReplay`'s two 17-line reset blocks (`:388-404`, `:437-453`) are byte-identical except `currentReplay`/`replayLoadError`/`view` and should be one `REPLAY_SCOPED_RESET` const; `errorMessage()` is duplicated in both stores.
- Why it matters: the load-bearing invariants (perspective↔selectedAgent firewall, token guards) are buried under narration; reviewers stop reading.

### F8 — P2 [VERIFIED] ESLint "legacy ledger" widens the blind spot beyond the finding
- `eslint.config.js:96-127` turns `react-hooks/exhaustive-deps` OFF for all of `BeliefMatrix.tsx`, `no-useless-assignment` OFF for all of `GuidedTour.tsx` + `MindInspector.tsx`, and `@typescript-eslint/no-unused-vars` OFF for all of `TurnCard.tsx` — to avoid four one-line edits in files a task contract declared out of scope. I verified all four findings still exist (`TurnCard.tsx:194-200` `players` unused; `GuidedTour.tsx:264`, `MindInspector.tsx:524`; `BeliefMatrix.tsx:109-111`). Any *new* unused var in TurnCard or missing dep in BeliefMatrix now passes lint. Fix: inline `eslint-disable-next-line` at the four sites (which `reportUnusedDisableDirectives: "error"` will keep honest) and delete the ledger.

### F9 — P2 [JUDGMENT] Demo-bundle builder scrapes editorial data out of TSX with regexes
- `scripts/build_demo_bundle.py:92-95, 153-191` parses `FEATURED_GAMES` from `ReplayPicker.tsx` with two regexes plus a brace-count heuristic (and `tests/api/test_sets.py` does the same). `tsconfig.json` already has `resolveJsonModule: true`; a `frontend/src/data/featured.json` imported by the picker and read by Python removes the parser, the heuristic and the failure-mode paragraph.

### F10 — P2 [VERIFIED] Small doc/config drift
- `frontend/.storybook/main.ts:3-5` says stories are "co-located … `src/ui/*.stories.tsx`"; they live in `src/stories/*.stories.tsx` (none in `src/ui/`).
- `frontend/CLAUDE.md` is the Phase-12 *Claude Design paste brief* ("`tokens.ts` is the canonical source of truth once it exists", "installed … in task 12.0"), not a package guide — nothing about `npm run test/lint/e2e`, the `/api` proxy, the static-data seam or the generated files. `README.md:217` says check.sh runs "frontend tsc + build" — it runs lint+tsc+test+build.
- `playwright.config.ts` boots uvicorn + Vite `webServer`s for *every* spec, including `bundle.spec.ts` which serves its own build and asserts zero `/api` traffic; locally `reuseExistingServer: true` will happily reuse a stale :8000 with a different `AILIBI_REPLAY_DIR`.
- `package.json` has no `engines`; `@types/node@^22` while local dev is on Node 26 (CI pins 22 — consistent there).
- `index.css:6-8` imports the all-subsets `@fontsource/*/400.css` (hebrew/vietnamese/latin-ext .woff+.woff2 = 192 kB emitted); unicode-range keeps downloads to latin, so this is cosmetic — `/latin-400.css` would trim dist by ~150 kB.

### F11 — P2 [JUDGMENT] Client static-mode branches lack unit tests
- `client.ts pathSegment()/apiUrl()` static branches (`STATIC_DATA_MODE`) are only exercised by `e2e/bundle.spec.ts`, which needs a Playwright browser + a full `build_demo_bundle.py` run (~minutes). `import.meta.env` is a module-load constant, so a vitest run with `env: { VITE_AILIBI_STATIC_DATA: "1" }` in a second tiny config (or `vi.stubEnv` + `vi.resetModules`) would give the seam a 50 ms unit test. The `u`-flag code-point argument at `client.ts:176-183` is exactly the kind of claim a two-line test should pin.

### What is GOOD (worth keeping)
- [VERIFIED] Type generation pipeline: `gen_frontend_types.py --check` clean; the fidelity fixture (`api.fidelity.ts`) type-checks a *real* served payload and forces exhaustive union narrowing; `VIEW_MODEL_VERSION` is emitted as a runtime constant and enforced in `getJson` (`client.ts:113-131`) with 6 focused tests. This is the right way to kill hand-mirrored DTOs.
- [VERIFIED] Store race handling: newest-wins tokens for list/sets/select, game+set post-await guards for keyed caches, per-key error maps with identity-preserving `withoutKey`; the firewall invariant (fog subject ↔ inspected agent) is enforced *in the store* (`selectAgent`/`setPerspective`) rather than in each UI entry point — good place for it. Tests drive these with hand-settled deferreds (`replayStore.test.ts:44-59`) — deterministic, behavioural, not implementation-pinning.
- [VERIFIED] Build health: strict TS (`noUncheckedIndexedAccess`, `exactOptionalPropertyTypes`), lint on with `reportUnusedDisableDirectives: "error"`, zero `any`/`ts-ignore`, one React copy, no unused deps; code-split works as documented (initial route ≈ 122 kB gz: index 35 + react-vendor 60 + css 21 + ReplayPicker 6; Pixi/MapView +113 kB gz only when a replay opens; every chunk < 500 kB).
- [VERIFIED] The static-data seam is genuinely compiled out of normal builds — `grep './data' dist/assets/*.js` finds nothing — so the builder's positive marker check is sound.
- [VERIFIED] Tokens are a real single source: `gen-tokens-css.ts` regenerated in scratch is byte-identical to the committed `index.css`; `tokens.test.ts` scans components for undeclared token utilities.
- [JUDGMENT] `usePlaybackEngine` isolates the timer/URL side effects in a render-null leaf; the URL round-trip is parse/serialize pure functions with 20+ tests. Playwright config decisions (pinned browser, IPv4 literal, no sleeps, one retry in CI) are sensible.

## 3. Architecture / design assessment

Well-designed: one store, actions colocated with invariants, view-model types generated, a single `apiUrl()` seam for the two data sources, lazy route boundaries, `lib/playback.ts` as a pure-function layer under the hook. The overall shape is right for an app of this size.

Accidental complexity: (a) client-side windowing that should be server-side (F1) — the DTO firewall already exists in `api/schemas.py`, so a lean `ReplayView` is cheap; (b) the "no in-flight dedup + guard against the consequences" pattern (F4); (c) `App.tsx` absorbing components because the task contracts forbade touching other files (F6); (d) the ESLint ledger and the regex-scraped featured list — both are workarounds for task-scope boundaries that outlived the tasks (F8, F9); (e) prose volume — config files with 45–66 % comments and 22–24 task citations per module.

What I would refactor: 1) lean `ReplayView` on the server + drop `windowReplay`; 2) `client.ts` gains `getBeliefFrames`, loses `getTick`/`getEvalCostSummary`, and the two raw `fetch`es go through it; 3) `fetchMemoryView`/`fetchMeeting` share one `cachedFetch(key, loader, cacheField, errorField)` with an in-flight map (removes ~80 lines and 4 tests of guard logic); 4) extract `RosterRail`/`PerspectiveBanner`/`MeetingPauseBar`/`FinaleCard` from `App.tsx`; 5) one initial-fetch owner; 6) a comment diet: keep invariants, delete history (task numbers belong in git/audits).

## 4. Test assessment (area)

- Unit (vitest, `environment: node`, 173 tests / 0.86 s): store guards (52 tests), client gate (6), tokens (20), playback lib (55), plus two component-logic suites owned by another track. Quality is high — behaviour-level, deterministic, no snapshotting of implementation. Store tests do restore state via `setState(PRISTINE, true)` — good.
- Gaps: static-mode `apiUrl/pathSegment` (F11); no test for the F3 double-fetch (would have caught it); `tournamentStore` untested (tiny); e2e not runnable on this box (no `~/Library/Caches/ms-playwright`) — I read but did not execute `journey.spec.ts`/`bundle.spec.ts`; the bundle spec's Python-side counterpart tests exist elsewhere.
- Test-file comment ratio: `journey.spec.ts` 39 %, `bundle.spec.ts` 30 % — the harness essays are longer than the assertions.

## 5. Recommendations (prioritised)

1. **Serve a lean `ReplayView`** (bodies stripped server-side; keep `GET /meetings/{id}` as the on-demand full transcript) and delete `windowReplay`; bake the lean form in the demo bundle. ~75 % smaller first-open payload, half the bundle's per-game bytes. (F1)
2. **Make `client.ts` the only fetcher**: add `getBeliefFrames`, route `TournamentDashboard`'s rubric through `getRubric`, delete `getTick`/`getEvalCostSummary`, and add a lint rule or test asserting `fetch(` appears only in `client.ts`. (F2, F5)
3. **One initial fetch owner** — remove `App.tsx`'s mount `loadReplayList`, let `ReplayPicker`'s `seedSet` effect own it (or gate `loadReplayList` on a resolved set). (F3)
4. **Collapse the keyed-cache pair** into one helper with an in-flight `Map<key, Promise>`; drop the "stale same-key failure" guards and their tests. (F4)
5. **Split `App.tsx`**: four components out to `components/`, header trimmed to the slot table; then a comment diet across store/client/config (target < 20 % comment lines, task numbers removed). (F6, F7)
6. **Replace the ESLint file-wide ledger** with four inline `eslint-disable-next-line` directives (already kept honest by `reportUnusedDisableDirectives`). (F8)
7. **Move `FEATURED_GAMES` to JSON** imported by both the picker and `build_demo_bundle.py`/`test_sets.py`. (F9)
8. Housekeeping: `engines` in `package.json`, fix `.storybook/main.ts` and `frontend/CLAUDE.md` (make it a real package guide), `@fontsource/*/latin-400.css`, a vitest static-mode config for the seam. (F10, F11)

## Appendix — commands and numbers

- `uv run python scripts/gen_frontend_types.py --check` → exit 0, 0.44 s.
- `npm run test` → 6 files, 173 passed, 345 ms vitest / 0.86 s wall.
- `npm run lint` → clean, 2.2 s. `npm run tsc:check` → clean, 4.6 s. `npm run build` → 3.4 s wall (tsc + vite 273 ms). `npx storybook build` → 3.6 s.
- dist: JS 1.0 MB raw (index 133.7 kB/35.3 kB gz, react-vendor 193.3/60.3, MapView 378.2/113.0, TournamentDashboard 27.7/8.7, ReplayPicker 19.7/6.2, Pixi async pieces ≤101 kB), CSS 59 kB/21.3 kB gz, fonts 192 kB (15 files, all subsets, woff+woff2).
- Payload probe: `work/frontend-b/payload_size.py` (24 games, both sets). Live probe: dev server `/api/replays/headless-seed-2?set=9p2i` = 718 181 B transferred, uncompressed.
- In-flight probe: `work/frontend-b/inflight.test.ts` + `vitest.probe.config.mjs` → 3 identical concurrent `fetchMemoryView` → 3 `getMemory` calls; 2 `fetchMeeting` → 2 `getMeeting` calls.
- Tokens: `gen-tokens-css.ts` re-run in scratch copy → `diff -q` identical to committed `index.css`.
- Not run: Playwright e2e (no browser installed locally; would need a network download).
