# Agent Prompt — 12.4 Playback backbone

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-12.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 12.4 — Playback backbone, anchored to design/phase-12/stage-1-design.md §4 (the time model), §2.3 (workspace layout), slice 2; design/phase-12/stage-0-understand.md §0.5. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-12.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-12-playback`
**Depends on:** 12.2
**Section refs:** design/phase-12/stage-1-design.md §4 (the time model), §2.3 (workspace layout), slice 2; design/phase-12/stage-0-understand.md §0.5
**Complexity:** Integration
**Files in scope:**
- frontend/src/store/replayStore.ts
- frontend/src/hooks/usePlayback.ts
- frontend/src/lib/playback.ts
- frontend/src/components/ReplayControls.tsx
- frontend/src/App.tsx
**Files NOT in scope:**
- the map / belief / meeting / inspector surfaces — Waves B/C mount into the shell slots + read the transport
- api/ and the loader — the advantage series + per-tick events already ship from 12.2
- frontend/src/tokens.ts and the design system — 12.1

A hand-coded frontend-state task (no Claude Design — the handoff bundle cannot carry state/interaction). Lift playback out
of `ReplayControls.tsx` into the store plus a `usePlayback` hook so every surface derives from **one source of truth — the
engine tick**. Today the tick↔array-index mapping is re-derived in several spots (the
`ReplayControls` comment already flags "compare against the engine tick NUMBER, not the array index"); collapse it into
**one derived selector** and treat the loader-injected `tick = -1` Start as a real pre-game value, not a sentinel. Build
the full transport: scrub · play/pause · speed (0.5–4×, the existing `PlaybackSpeed`) · **step ±N** · **jump prev/next
event** (kill / meeting / vent / sabotage, from the per-tick `events`) · **jump prev/next meeting** · **next key
moment**. Add the **advantage graph as a clickable second scrubber** from the 12.2 `AdvantageView` per-tick series
(crew-vs-impostor, kills/meetings/ejections as inflection points; click to seek) and a shared hover **crosshair** across
the advantage graph + the event-timeline lanes (one lane per agent). **"Next key moment"** seeks to the next
advantage-graph **inflection** — the next tick carrying a kill, a body-report / meeting, an ejection, or a sabotage start
(the drama beats), ranked kill → meeting → ejection — distinct from the raw step / jump-event controls. Stand up the
**app shell** with pre-declared mount points at **two** levels so *every* Wave-B surface plugs in **without ever editing
`App.tsx`**: **(a)** a top-level view container (view state in the store, URL-synced; no router dependency) for
**Replays** + **Highlights** (→ 12.9), **Tournament** (→ 12.10), and the **Replay Workspace**; and **(b)** within the
workspace, named slots per stage-1 §2.3 — perspective banner, roster rail, **stage** (map↔meeting morph → 12.5 / 12.7),
**mind** panel (→ 12.8), a **belief-panel** mount (overlay / full-screen toggle → 12.6), the **advantage graph**, the
**event-timeline** lanes, and the **transport**. Confirm with a slot↔surface checklist that all of 12.5–12.10 (+
transport / advantage / timeline) have a mount; the slots ship as empty placeholders the Wave-B PRs fill (each owns its
component, never the shell). Add **URL sync** of
`set / game_id / tick / perspective / beliefView / selectedAgent / selectedMeeting` via `history.replaceState` +
`URLSearchParams` (there is no router today) so every moment is shareable + reload-stable — which means adding
`perspective` + `beliefView` to the store now (consumed later by 12.5 / 12.6). Meetings are **time spans**: the stage
morphs to the meeting table when `tick ∈ meeting.span`, and **auto-follow** (pan to the next event) is **interruptible**
(never yank the camera). Keep the existing payload windowing, lazy meeting bodies, and async-ordering guards intact.
**Definition of done:** all playback state lives in `replayStore` + a `usePlayback` hook (not in `ReplayControls`); the
tick↔index mapping is one derived selector with `tick = -1` handled and no off-by-one; the transport supports scrub /
play / speed / step ±N / jump-event / jump-meeting / next-key-moment; the advantage graph seeks on click and shares the
crosshair; the URL round-trips all seven keys (reload restores the exact moment); auto-follow is interruptible; the
shell exposes a pre-declared mount (slot or route) for **every** one of 12.5–12.10 plus transport / advantage / timeline,
verified by a slot↔surface checklist, so no Wave-B PR needs to touch `App.tsx`; windowing + lazy bodies + async-ordering
guards are preserved;
`npm run tsc:check` + `npm run build` pass and `scripts/check.sh` is green.

## Implementation hint
the store already holds `currentTick` / `isPlaying` / `playbackSpeed` / `selectedMeetingId` / `selectedAgentId` — extend
it with `perspective` / `beliefView` plus the single derived tick selector rather than starting fresh, and move the
auto-advance timer out of `ReplayControls` into `usePlayback`. Drive jump-event / jump-meeting off the per-tick `events`
list and the meetings list, comparing engine tick numbers, never array indices. Do the URL sync with `replaceState` +
`URLSearchParams` (no router dependency) and debounce it so scrubbing does not thrash history.

## Integration risk
the off-by-one is the trap — the current index/tick conflation is re-derived in multiple places; the single selector must
treat `tick = -1` as real and stay consistent across transport, events, meetings, and the advantage scrubber, or
surfaces disagree. The shell-slot layout is load-bearing for Wave 3: define stable mount points now so the parallel
chrome PRs do not collide in `App.tsx`. Preserve the store's async-ordering guards + payload windowing — a naive rewrite
reintroduces the race and the payload inflation they already fixed. Finally, 12.3 regenerates
`frontend/src/types/api.ts` in parallel (it adds `AgentVisibilityView`); 12.4 only *reads* `AdvantageView` and never
writes that file, so there is no scope conflict — but whichever of 12.3 / 12.4 merges second should rebase and recompile
against the regenerated types.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas"`

## Pre-flight checklist
- Read AGENTS.md, the architecture routing it names, and the task section before editing.
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
Open a PR from branch `phase-12-playback` with a title like `task 12.4: playback backbone`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing design/phase-12/stage-1-design.md §4 (the time model), §2.3 (workspace layout), slice 2; design/phase-12/stage-0-understand.md §0.5), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
