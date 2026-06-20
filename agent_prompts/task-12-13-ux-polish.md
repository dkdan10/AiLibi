# Agent Prompt — 12.13 UX-polish (close-audit backlog)

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.13 — UX-polish (close-audit backlog), anchored to the Phase-12 UX close-audit (two multi-agent passes + a manual composed-app pass, 2026-06-20); design/phase-12/stage-1-design.md; design/phase-12/tokens-seed.md; `frontend/CLAUDE.md`.. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-ux-polish`
**Depends on:** 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9, 12.10, 12.11, 12.12
**Section refs:** the Phase-12 UX close-audit (two multi-agent passes + a manual composed-app pass, 2026-06-20); design/phase-12/stage-1-design.md; design/phase-12/tokens-seed.md; `frontend/CLAUDE.md`.
**Complexity:** Integration
**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx
- frontend/src/components/MindInspector.tsx
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/BeliefPanel.tsx
- frontend/src/components/ReplayControls.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TournamentDashboard.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/App.tsx
- frontend/src/tokens.ts
- frontend/src/index.css
- frontend/src/ui/
- api/replay_loader.py
- api/schemas.py
**Files NOT in scope:**
- the engine + recorded replays — no re-record (a `tasks_required_total` is a loader projection, not an engine change)
- the six P1s ALREADY fixed pre-dispatch (palette restyle, BeliefCell contrast, perspective banner, focus-trap, highlights /sets dead-end, narrow meeting nav-bleed) — do NOT redo or revert them

The Phase-12 UX close-audit backlog, hand-coded + design-system-first. Build and verify every change in the COMPOSED
running app (`scripts/run_spectator.sh`), not isolated Storybook stories — the audit's recurring lesson is that the
overlay / composition / data-populate bugs only show composed. Severity in brackets.

Remaining P1s — each needs an owner decision or map-render iteration:
- **[P1] Task-meter denominator drifts.** `App.tsx:379` shows `adv.tasks_completed`/`adv.tasks_required`; `tasks_required`
  is recomputed per tick (living-crew), so "tasks 0/14 → 7/10" shrinks mid-game and reads as misleading progress. If the
  per-tick living-crew total is intended, expose the FIXED game-start total as a loader projection (`api/replay_loader.py`
  + `api/schemas.py`, e.g. `tasks_required_total`) and show that as the stable, monotonic denominator; otherwise relabel
  so the shrinking total is legible. Make the arithmetic reconcile.
- **[P1] Agent inspection only reachable inside a meeting.** Map tokens (`MapView`/`AgentToken`) and roster rows
  (`App.tsx` RosterRail) have no click → `selectAgent`. Wire a Pixi pointer handler + a roster-row onClick; since
  prompt/response/memory are per-meeting, decide what the inspector shows BETWEEN meetings (latest snapshot / belief tab /
  jump to next meeting) rather than nothing.
- **[P1] Belief × Truth hides during a meeting and its launcher overlaps the Reactor room.** Let the hero coexist with an
  open meeting (dock it in the meeting's reserved right gutter) or keep a discoverable launcher; re-anchor the launcher
  into chrome (a tab by the perspective toggle / a roster entry) so it never overlaps a room cell or corridor.
- **[P1] Admin dead-body cluster collision** (`MapView`): multiple bodies in one room garble the room title and the
  oversized kill-flash ring clips stacked labels. Reserve the title band, lay bodies in a non-overlapping grid with bottom
  padding, cap the kill-flash ring to the cell, collapse to "✕ ×N" past capacity.
- **[P1] Sabotage marker** renders as a solid warm-orange disc — make it the hazard treatment (ink/neutral fill + stripe +
  ⚡ glyph) per `tokens.ts` `status.sabotage`, off the reserved warm hue (it currently collides with the red kill disc and
  distrust-orange). `MapView` event markers.

P2 polish — the bulk:
- **[P2] Debug annotation leaks into the transcript** — `[emergency opening: fabricated found_body stripped]` renders
  inline (`MeetingView`/`TurnCard`); render a role-neutral "FABRICATED" chip instead and drop the dev-jargon string.
- **[P2] Muted-text + label contrast sweep** — `text-ink-400` (3.79:1) → `text-ink-500` for informational text, and
  distrust-strong orange label TEXT → `ink-900` (keep the orange edge/arrow as the channel) across `TurnCard`,
  `MeetingView`, `MindInspector`, `ReplayControls`, `BeliefPanel`, `MapToolbar` (matrix numerals + error glyph already fixed).
- **[P2] Type + spacing scale** — add a `type.size` scale to `tokens.ts` (+ `--text-*` utilities), map the ~88 ad-hoc
  `text-[9/10/11px]` onto named steps; round off-scale `px-2.5`/`py-2.5`/`gap-1.5`/`py-0.5` to `tokens.space` stops.
- **[P2] Incomplete ARIA widgets** — `MindInspector` tablist (`aria-controls` + `role="tabpanel"`/`aria-labelledby` +
  Left/Right roving-tabindex) and the `AdvantageGraph` slider (`ReplayControls`: its own Arrow/Home/End `onKeyDown`).
- **[P2] Cross-surface consistency** — one panel radius (`MeetingView`/`GuidedTour` `rounded-2xl` → the `rounded-lg`
  majority); shared `ui/SectionLabel` (eyebrow) + `ui/PlayerSwatch`; extract `ui/EmptyState`/`ui/Banner`/`ui/Loading`
  (with `role="status"`) and adopt them in `ReplayPicker`/`TournamentDashboard`/`App`; delete the dead `ui/PlayerChip`.
- **[P2] Map legibility** — draw the vent endpoints (the "6-vent ring" subtitle promises them) or drop the claim; enlarge
  the impostor-reveal badge + add an Omniscient-only legend; align the advantage-graph and event-timeline to a shared
  left plot origin so the tick crosshair lines up.
- **[P2] Narrow-820** — inset the seek-marker track so the last-tick marker isn't clipped + give 16px markers a ≥24px
  hitbox; tighten the ~200px dead space below the map card; keep a compact crew/imp/tasks summary on the collapsed roster
  bar; inset the clipped "Mind inspector" drawer tab.
- **[P2] Feedback + edge states** — an in-flight "Loading <set>…" cue on set switch; render `availableSetsError` as an
  inline retry chip where `SetSelector` would be; give the replay-load error Banner a dismiss (`clearError()`); grey the
  "0 mtg" Belief launcher with a tooltip; hoist the repeated 4p1i "Not scored" note to ONE Banner when
  `rubricStatus === "absent"`; fill the mind-inspector default empty column (default-select / how-to-read).
- **[P2] Misc** — verify the dashboard "interestingness distribution" section populates (it shows an empty card below the
  fold); add a baseline/value to the Highlights R1/R2/R3/R7 mini-bars; mark/disable dead agents in the fog agent picker;
  add a tour step for opening a mind; delete the dead `BeliefRow` MemoBar branch (off-token neutral ramps).
**Definition of done:** the five remaining P1s are addressed (task-meter denominator stable or relabelled per the owner
decision; agent inspection reachable from the map + roster; the belief hero discoverable during a meeting with its
launcher off the room cells; the Admin body-cluster and sabotage-marker fixed); the P2 backlog is worked through; every
change verified in the composed running app; no firewall regression (the leak test still passes — fog suppresses roles,
the matrix stays Omniscient-only); `npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green.

## Implementation hint
build + test in the running spectator, not isolated stories — the overlay / composition / populate bugs only show
composed. Group edits by file to minimise churn (most map items are `MapView`; the contrast sweep is largely a
find-replace of `text-ink-400` + the distrust-orange label text). The task-meter likely needs a small loader/DTO
projection for the fixed total (then regenerate the TS types). Reuse the `useFocusTrap` hook + the cream/ink primitive
pattern the pre-dispatch P1 fixes established.

## Integration risk
broad surface area — regression-check each surface in the composed app and re-run the firewall leak test. This builds ON
the six pre-dispatch P1 fixes (committed first); do not redo or revert them. The task-meter touches `api/` — keep it a
loader projection, no engine change, no re-record. Dispatch this AFTER the pre-dispatch P1 fixes land on main.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

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
Open a PR from branch `phase-12-ux-polish` with a title like `task 12.13: ux-polish (close-audit backlog)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing the Phase-12 UX close-audit (two multi-agent passes + a manual composed-app pass, 2026-06-20); design/phase-12/stage-1-design.md; design/phase-12/tokens-seed.md; `frontend/CLAUDE.md`.), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
