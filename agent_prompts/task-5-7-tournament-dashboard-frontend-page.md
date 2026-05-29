# Agent Prompt — 5.7 Tournament dashboard frontend page

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-5.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 5.7 — Tournament dashboard frontend page, anchored to DESIGN.md §11.3, DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-5.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-5-tournament-dashboard-frontend-page`
**Depends on:** 5.6 merged
**Section refs:** DESIGN.md §11.3, DESIGN.md §7
**Complexity:** Integration

Add a Tournament Dashboard view to the spectator frontend that renders the
`eval.meeting_quality.TournamentEvalReport` (the artifact Task 5.6 emits as
`tournament-eval-report.json`): the four Phase 5 metrics (vote correctness,
accusation calibration, alibi fabrication, cost dashboard) plus the balance
outcome summary. The Phase 4 app is a single-page replay viewer; this task adds
a SECOND top-level view, reached by tab navigation, backed by its own store and
a new read endpoint. This is a full-stack slice (backend read endpoint →
typed client → store → component), so its scope is wider than the other Phase 5
tasks; that is expected for the dashboard.

The merged data shape it renders (`eval/meeting_quality.py`):
`TournamentEvalReport { report: TournamentReport, vote_correctness:
VoteCorrectnessReport, accusation_calibration: AccusationCalibrationReport,
alibi_fabrication: AlibiFabricationReport, cost_dashboard: CostDashboard }`. All
five are frozen Pydantic models that round-trip through JSON.

**Decisions resolved (record any deviation in the PR's `## Decisions` block):**
- **Navigation: tabs, not a router.** Add tab state to `App.tsx`
  ("Replay Viewer" | "Tournament Dashboard"); render one view at a time. No
  `react-router-dom` dependency (the app is single-page; a router is dead
  weight for two views).
- **Store: a sibling `useTournamentStore`, NOT an extension of
  `useReplayStore`.** The Phase 4 store is explicitly frozen (its header says
  adding a field requires touching all consumers). The dashboard's state is
  independent (one fetched report, no playback), so it gets its own Zustand
  store.
- **Report source: a new read endpoint** `GET /api/tournament-report` (in
  `api/routes/eval.py`, mirroring the existing `/cost-summary` thin-adapter
  pattern) serving the latest `tournament-eval-report.json` from the configured
  replay/eval directory via `ReplayLoader`. Returns 404 when no report is
  present. This matches the replay-viewer architecture (frontend fetches typed
  JSON via `api/client.ts`); a committed static asset would go stale. The
  endpoint is privileged like the rest of the spectator API and intentionally
  exposes `roles` ground truth for the dashboard.
- **Rendering: plain React + CSS/SVG, NOT PixiJS.** The metric views are tables,
  bars, a calibration curve (rate-vs-confidence), and a cost breakdown — data
  widgets, not a spatial canvas. PixiJS is the map renderer; do not pull it into
  a data view. No new charting dependency unless a clear need is documented.

**Files in scope:**
- frontend/src/components/TournamentDashboard.tsx (and small co-located subcomponents if needed)
- frontend/src/store/tournamentStore.ts (new sibling Zustand store)
- frontend/src/api/client.ts (add `getTournamentReport()`)
- frontend/src/types/api.ts (add the `TournamentEvalReport` TS types mirroring the Pydantic models)
- frontend/src/App.tsx (tab navigation between the replay viewer and the dashboard)
- api/routes/eval.py (add `GET /tournament-report`)
- api/replay_loader.py (add a method that reads the eval-report JSON from the configured dir, mirroring `cost_summary()`)
- tests/api/ (a test for the new endpoint: present → 200 + valid body; absent → 404)

**Files NOT in scope:**
- engine/
- agents/
- llm/
- eval/ (consume `TournamentEvalReport`'s JSON shape; do not modify the metric or schema modules)
- frontend/src/store/replayStore.ts (frozen Phase 4 store — do not extend it)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `GET /api/tournament-report` returns the `TournamentEvalReport` JSON for the configured eval dir (200) or 404 when no `tournament-eval-report.json` exists; the loader method mirrors `ReplayLoader.cost_summary()` and reads the same configured directory.
- [ ] `frontend/src/types/api.ts` carries TS types mirroring `TournamentEvalReport` + its four nested metric models (and the `TournamentReport` fields the dashboard reads); `getTournamentReport()` in `api/client.ts` fetches `/tournament-report` and returns the typed shape, raising `ApiError` on failure like the sibling methods.
- [ ] `useTournamentStore` (new) holds the fetched report + load/error state; it does not import or mutate `useReplayStore`.
- [ ] `App.tsx` renders tab navigation; selecting "Tournament Dashboard" mounts `TournamentDashboard`, which renders: the balance summary (crew/impostor/tick-budget from `report` winners), vote-correctness rate, the accusation-calibration curve (per-bin actual-impostor-rate vs confidence, claim and ballot curves shown separately), the alibi-fabrication survival rate, and the cost dashboard (total, mean-per-game, per-`(template, version)` breakdown, per-model). Each metric's `None`/empty states render without crashing (e.g. `vote_correctness_rate === null` shows "n/a", not NaN).
- [ ] The dashboard does NOT pull in PixiJS or a new charting dependency (or, if one is genuinely needed, the choice is justified in `## Decisions`).
- [ ] `npm run build` (tsc + vite build) and any configured `tsc`/lint check pass; `bash scripts/check.sh` passes (backend gates green for the new endpoint).
- [ ] `uv run mypy --strict` on the API surface it touches passes; `uv run ruff check .` passes.

## Implementation hint

Backend: `api/routes/eval.py` already exposes `GET /cost-summary` as a thin
adapter over `ReplayLoader`. Add `GET /tournament-report` the same way — a new
`ReplayLoader` method reads `<replay_dir>/tournament-eval-report.json` (the file
`scripts/run_tournament.py` writes), validates it against
`eval.meeting_quality.TournamentEvalReport`, and returns it; missing file → a
404 (`HTTPException`). Serve the model directly as `response_model` rather than
re-modeling a parallel DTO — the structure is deep and the dashboard is
privileged. Generate a sample `tournament-eval-report.json` for local testing
with `uv run python scripts/run_tournament.py --num-games 5 --output-dir /tmp/tdash`
(fake provider, no network).

Frontend: model the tab on the existing single-page layout in `App.tsx`; the
dashboard view is a sibling of the replay-viewer `<main>`. The calibration curve
can be a simple inline SVG or styled divs (per-bin bar whose height is
`actual_impostor_rate`, x = bin midpoint). Mirror `api/client.ts`'s `getJson`
helper for the fetch.

## Integration risk

- **Scope is full-stack.** Unlike 5.8 (which is parallel-safe in `eval/` +
  `tests/`), this task touches `api/` and `frontend/`. It does not touch any
  file 5.8 touches, so the two still fan out in parallel — but this one is the
  larger PR.
- **Privileged exposure is intentional.** The endpoint serves `roles` ground
  truth. That is consistent with the spectator API's privileged model (the
  replay viewer already exposes role), but note it explicitly so a future DTO
  audit does not flag it as an accidental leak.
- **Do not extend the frozen replay store.** Adding fields to `useReplayStore`
  would force edits across every Phase 4 component; the sibling store keeps the
  blast radius to this task.
- **TypeScript/Pydantic drift.** The TS types are hand-mirrored from the
  Pydantic models; keep them faithful (especially nullable fields like
  `vote_correctness_rate: number | null` and the empty-bin
  `actual_impostor_rate: number | null`) or the dashboard silently renders
  `undefined`.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import eval.meeting_quality"`
- `uv run python -c "import eval.balance_eval"`
- `uv run python -c "import eval.cost_dashboard"`
- `uv run python -c "import eval.report_schema"`
- `uv run python -c "import orchestrator.replay.ReplayLog"`
- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`
- `uv run python -c "import eval.alibi_fabrication"`
- `uv run python -c "import eval.accusation_calibration"`
- `uv run python -c "import eval.vote_correctness"`

## Pre-flight checklist
- Read AGENTS.md, DESIGN.md, and the task section before editing.
- Inspect the current implementation before editing.
- Identify the existing local patterns for the files in scope and follow them.

## Constraints and non-goals
Do not modify DESIGN.md.
Do not modify AGENT_IMPLEMENTATION.md.
Do not modify tasks/phase-*.md unless this task explicitly lists those files in scope.
Do not implement work outside this task.

## Verification checklist
- Run every command listed in the Definition of done.
- Run `git diff --name-only` and confirm the diff stays within scope.
- If any Definition of done item is unchecked, report it explicitly in the PR description instead of declaring the task complete.

## Decisions vs questions
- If something is **ambiguous and blocking** (you cannot make a reasonable choice without further information): stop, open a draft PR, add a `## Questions` section, request review.
- If something is **ambiguous but resolvable by judgment** (a default value, a tie-break, a naming choice): document the choice in a `## Decisions` section in the PR description and proceed.

## Output expectation
Open a PR from branch `phase-5-tournament-dashboard-frontend-page` with a title like `task 5.7: tournament dashboard frontend page`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §11.3, DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
