# Agent Prompt — 4.11 ReplayControls (scrubber, speed, play/pause, snap-to-meeting)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.11 — ReplayControls (scrubber, speed, play/pause, snap-to-meeting), anchored to DESIGN.md §7, DESIGN.md §11.4. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-replaycontrols`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.10 merged** (App.tsx slot ordering — ReplayControls is the last component to integrate)
**Section refs:** DESIGN.md §7, DESIGN.md §11.4
**Complexity:** Medium

The primary playback control surface. Replaces TickStepper (from
4.4) as the main control bar: scrubber for arbitrary seek, speed
selector for playback rate, play/pause for auto-advance, fine-grained
step buttons for single-tick movement, and snap-to-meeting buttons
for fast navigation between meetings. The component drives the
Zustand store's `currentTick`, `isPlaying`, `playbackSpeed`, and
`selectedMeetingId`; every other component re-renders against the
store.

**Why this is a UX cornerstone.** The Phase 4 merge gate is "a
non-technical viewer can follow a saved replay end-to-end without
reading logs." Without ReplayControls, the viewer is stepping
tick-by-tick through 1000+ ticks via TickStepper — unwatchable.
ReplayControls is what turns the spectator UI into a watchable
artifact.

**TickStepper transition.** 4.4 shipped TickStepper as a minimal
prev/next + label. ReplayControls subsumes it. The implementing
agent picks one of two paths:

1. **Replace TickStepper** with ReplayControls in App.tsx. Delete
   the TickStepper component file. Cleaner long-term.
2. **Keep TickStepper as a fine-control widget** inside
   ReplayControls (e.g. a "single-tick" pair of buttons distinct
   from the scrubber). Preserves the existing component as a
   building block.

Recommendation: Path 1. The "step ±1 tick" affordance is in
ReplayControls per the DoD; a duplicated TickStepper is bloat.
Document the choice in `## Decisions`.

**Out of scope** (explicit decisions deferred):

- **Keyboard shortcuts.** Spacebar to play/pause, arrows to step,
  etc., are nice-to-have but not required for the merge gate.
  Polish task if the UX session calls for it.
- **Per-tick thumbnails / scrubber preview.** Hovering the scrubber
  doesn't show a mini-MapView preview. That'd require pre-rendering
  the map at every tick; out of MVP scope.
- **Loop / repeat playback.** No "loop" button. Playback stops at
  the last tick.
- **Bookmarking arbitrary ticks.** Snap-to-meeting is the only
  bookmark; user-defined bookmarks are out of scope.
- **Variable-speed slider.** The speed control is a discrete
  4-button selector (0.5×, 1×, 2×, 4×). A continuous slider would
  invite interaction churn without UX gain at this stage.

**Files in scope:**
- frontend/src/components/ReplayControls.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (already has all needed state + actions from 4.3)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen)
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx (lands in 4.6)
- frontend/src/components/ThoughtStream.tsx (lands in 4.8)
- frontend/src/components/BeliefMatrix.tsx (lands in 4.10)
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx (delete if subsumed; otherwise leave frozen)
- frontend/package.json (locked)
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- scripts/
- tests/

**Definition of done:**
- [ ] **Scrubber.** `<input type="range">` (or a custom range slider) with `min=0`, `max=currentReplay.ticks.length - 1`, `value=currentTick`, `onChange → setCurrentTick(value)`. Use `onInput` for live-update during drag, `onChange` for final commit. Styled with Tailwind to fit the control bar.
- [ ] **Speed selector.** Four buttons: `0.5×`, `1×`, `2×`, `4×`. Clicking sets `setPlaybackSpeed(speed)`. The active speed's button is visually highlighted (different background or ring).
- [ ] **Play / Pause toggle.** Single button that flips `isPlaying`. When playing: button shows pause icon (or "Pause" text). When paused: shows play icon ("Play"). Disabled when at the last tick.
- [ ] **Step backward / Step forward.** Two buttons that call `setCurrentTick(currentTick - 1)` / `setCurrentTick(currentTick + 1)`. Clamped at 0 and `ticks.length - 1`. Active regardless of `isPlaying`.
- [ ] **Snap to next meeting / Snap to previous meeting.** Two buttons. "Next meeting" finds the next entry in `currentReplay.meetings` with `tick > currentTick`; if found, calls `setCurrentTick(meeting.tick)` AND `selectMeeting(meeting.meeting_id)`. "Previous meeting" symmetric (largest tick < currentTick). Disabled (visibly greyed) when no such meeting exists in the given direction.
- [ ] **Auto-advance on play.** When `isPlaying === true`, advance `currentTick` by 1 every `BASE_TICK_INTERVAL_MS / playbackSpeed` (e.g. `BASE=500`, so 1× = 500 ms/tick, 2× = 250 ms/tick, 4× = 125 ms/tick, 0.5× = 1000 ms/tick). Use `setInterval` registered in a `useEffect` keyed on `[isPlaying, playbackSpeed]`; clean up on unmount or dependency change. At the last tick, set `isPlaying = false` (don't loop).
- [ ] **Tick label.** Text like `Tick 247 / 999` displayed near the scrubber. If the current tick is also a meeting tick, append a small chip "(meeting)".
- [ ] **Layout.** Bottom of the App as a fixed or sticky control bar. Single row on wide screens; wraps responsibly on narrow. Tailwind for layout — no fancy CSS.
- [ ] **TickStepper removal (if Path 1).** If subsuming, delete `frontend/src/components/TickStepper.tsx` and remove the import + render call from App.tsx. Document the deletion in PR description.
- [ ] **No new npm dependencies.**
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: (a) the ReplayControls bar at rest with a mid-replay tick selected, (b) the bar mid-play with a non-1× speed highlighted, (c) the snap-to-meeting button used and the resulting MeetingView open (proves the selectMeeting integration works).
- [ ] **Manual smoke documented.** PR description states the replay used, confirms: (1) scrubbing seeks immediately; (2) play/pause works; (3) each of the 4 speeds advances at visibly different rates; (4) snap-to-meeting opens the right meeting; (5) no console errors during a full play-through from tick 0 to last tick.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.

## Implementation hint

Pure React + Tailwind. No PixiJS. The store from 4.3 already exposes every action this component needs.

Auto-advance pattern:

```tsx
const BASE_TICK_INTERVAL_MS = 500;

export function ReplayControls() {
  const replay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);
  const isPlaying = useReplayStore((s) => s.isPlaying);
  const playbackSpeed = useReplayStore((s) => s.playbackSpeed);
  const setCurrentTick = useReplayStore((s) => s.setCurrentTick);
  const setIsPlaying = useReplayStore((s) => s.setIsPlaying);
  const setPlaybackSpeed = useReplayStore((s) => s.setPlaybackSpeed);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);

  // Auto-advance
  useEffect(() => {
    if (!isPlaying || !replay) return;
    const intervalMs = BASE_TICK_INTERVAL_MS / playbackSpeed;
    const id = setInterval(() => {
      const lastTick = replay.ticks.length - 1;
      const nextTick = useReplayStore.getState().currentTick + 1;
      if (nextTick > lastTick) {
        setIsPlaying(false);
      } else {
        setCurrentTick(nextTick);
      }
    }, intervalMs);
    return () => clearInterval(id);
  }, [isPlaying, playbackSpeed, replay, setCurrentTick, setIsPlaying]);

  // ... render scrubber + buttons ...
}
```

Note the `useReplayStore.getState().currentTick` read inside the interval — reading from the closure-captured `currentTick` would freeze the value at interval-registration time. The `useEffect` dependency on `currentTick` would re-register the interval on every tick (causing drift); reading fresh from the store avoids both bugs.

Snap-to-meeting helpers:

```typescript
function findNextMeeting(meetings: MeetingView[], currentTick: number) {
  return meetings.find((m) => m.tick > currentTick) ?? null;
}
function findPrevMeeting(meetings: MeetingView[], currentTick: number) {
  for (let i = meetings.length - 1; i >= 0; i--) {
    if (meetings[i].tick < currentTick) return meetings[i];
  }
  return null;
}
```

`meetings` is already sorted by tick per the loader contract.

Scrubber as range input:

```tsx
<input
  type="range"
  min={0}
  max={replay.ticks.length - 1}
  value={currentTick}
  onChange={(e) => setCurrentTick(Number(e.target.value))}
  className="w-full"
/>
```

For the meeting-tick chip in the label, scan `replay.meetings` for an entry matching `currentTick`:

```tsx
const isAtMeeting = replay.meetings.some((m) => m.tick === currentTick);
return <span>Tick {currentTick} / {replay.ticks.length - 1}{isAtMeeting && " (meeting)"}</span>;
```

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import api.schemas.BeliefEntryView"`
- `uv run python -c "import orchestrator.replay"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-replaycontrols` with a title like `task 4.11: replaycontrols (scrubber, speed, play/pause, snap-to-meeting)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §11.4), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
