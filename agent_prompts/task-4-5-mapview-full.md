# Agent Prompt — 4.5 MapView full (sabotage, vents, bodies, tween)

You are working on AiLibi. Before starting, read AGENTS.md, the architecture routing it names, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly; it names the authoritative architecture routing. The task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.5 — MapView full (sabotage, vents, bodies, tween), anchored to DESIGN.md §7, DESIGN.md §8.3. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-mapview-full`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §7, DESIGN.md §8.3
**Complexity:** Medium

Expand MapView from the vertical slice into the full spectator
rendering: sabotage state overlay, vent network as static edges,
body markers from past `KillEventView`s, and smooth interpolation
between adjacent ticks. The vertical slice (4.4) ships rooms and
agent tokens snapping to room centers; this task adds everything
that makes the map watchable.

**Privileged spectator reminder.** `KillEventView` exposes
`killer_id`, `victim_id`, and `room_id` (the mid-phase DTO audit
confirmed this is intentional — the replay viewer is post-game
privileged). Body markers therefore render directly from kill
events; no derivation from `MeetingTriggeredEventView` is needed.
The original 4.4.5 sketch said the kill room was not in the DTO —
that was wrong; the substrate audit confirmed it is.

**Out of scope** (explicit decisions deferred):

- **Live game streaming.** Replay-only, same as 4.4.
- **Sabotage kinds other than lights.** MVP scope per DESIGN.md
  §8.3; the DTO's `sabotage_active: tuple[str, ...]` already
  encodes "lights" as the only literal today, but the rendering
  should branch on the string so future kinds don't crash.
- **Animated body discovery.** A body appears in its kill room
  from the kill tick onward; once a `ReportBodyEventView` fires for
  that body, the marker is replaced by a "discovered" variant (a
  one-time CSS class swap, not an animation).
- **Vent traversal animation.** Vents render as static edges. An
  agent who's `is_venting=true` is hidden (per the 4.4 filter); no
  animated traversal between vent endpoints.
- **Camera zoom / pan / click-to-focus.** Static fit-to-canvas as
  in 4.4. Camera controls land in a polish task if the UX session
  flags them.

**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/VentEdge.tsx
- frontend/src/components/BodyMarker.tsx
- frontend/src/components/SabotageOverlay.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/src/types/api.ts
- frontend/package.json (locked at 4.3; no new deps without `## Decisions` justification)
- frontend/src/components/RoomRect.tsx (frozen — vertical slice's room rendering still applies)
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
- frontend/src/App.tsx
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
- [ ] **Vent network rendering.** Each `VentView` in `currentReplay.map.vents` becomes a `VentEdge` for every `(room_id, connected_room_id)` pair — a thin gray line from one room's center to the other's center, dashed or low-opacity to distinguish from doors. Edges are deduplicated (vent A↔B and vent B↔A produce one edge).
- [ ] **Body markers from kill events.** Scan `currentReplay.ticks[0..currentTick].events` for every event with `type === "kill"`. For each, render a `BodyMarker` (e.g. an X glyph or skull) at the room center indicated by `room_id`, offset deterministically so a body doesn't overlap living agents in the same room. When a subsequent `ReportBodyEventView` exists for the same `body_of`, swap the marker style to "discovered" (CSS class change or color shift).
- [ ] **Sabotage overlay.** When `currentReplay.ticks[currentTick].sabotage_active` includes `"lights"`, a `SabotageOverlay` renders a translucent dark tint over the canvas (or a subtle vignette). When the array is empty, the overlay renders nothing. The implementation branches on string kind so unknown kinds are silently skipped (no crash).
- [ ] **Smooth interpolation between ticks.** When `currentTick` advances by 1 (via TickStepper or future ReplayControls), agent tokens tween from their previous-tick room center to their new-tick room center over a configurable duration (default 250 ms). Use PixiJS `Ticker` registered inside `AgentToken` (or a shared tween coordinator in `MapView`). When `currentTick` jumps by more than 1 (scrubber, snap-to-meeting), tweens snap immediately (no multi-tick interpolation).
- [ ] **Tween is interruptible.** Mid-tween tick change cancels the in-progress tween and starts a new one from the current interpolated position. Test by spamming next-tick; tokens should never desync from their room.
- [ ] **No PixiJS leaks on unmount or HMR.** `useEffect` cleanup destroys PixiJS objects (Ticker, Graphics) on component unmount. Verify under Vite HMR by editing MapView mid-dev session and confirming the canvas doesn't multiply or leak Tickers (`app.ticker.count` stays stable).
- [ ] **No new npm dependencies.** PixiJS 8, `@pixi/react` 8, React 19, Zustand 5 from 4.3 are sufficient. If a tween utility is genuinely required, justify in `## Decisions` and pin the version.
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`. `npm run tsc:check` passes.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Three minimum: (a) vertical-slice-equivalent state for comparison (tick 0 of a real replay), (b) a tick with bodies + sabotage visible, (c) mid-tween state (capture during animation if possible — otherwise document the tween duration setting).
- [ ] **Manual visual smoke documented.** PR description states the replay used (e.g. `replays/replay-seed-22.jsonl` if it has a kill + meeting; otherwise the next real replay that does); the tick sequence stepped through; confirms vents visible, body appears at kill tick, sabotage tint visible if any `lights` sabotage fired; no console errors.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (Python tests unaffected).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally (includes frontend block from 4.3).

## Implementation hint

The 4.4 vertical slice uses `@pixi/react` v8 declarative with an `extend({ Container, Graphics, Text })` registration (see `frontend/src/components/MapView.tsx` lines 22, 116-132). Stay on that pattern; do not pivot to vanilla PixiJS + `useEffect` mount.

Vent edge rendering pattern:

```tsx
function VentEdge({ from, to, transform }: VentEdgeProps) {
  return (
    <pixiGraphics
      draw={(g) => {
        g.clear();
        g.moveTo(from.x, from.y);
        g.lineTo(to.x, to.y);
        g.stroke({ width: 2, color: 0x555555, alpha: 0.5 });
      }}
    />
  );
}
```

For deduplication, build a `Set<string>` of `min(a,b)|max(a,b)` keys before mapping to `<VentEdge>` elements.

Body marker derivation pattern:

```typescript
function visibleBodies(ticks: TickView[], currentTick: number) {
  const kills = new Map<string, KillEventView>(); // body_of → kill
  const discovered = new Set<string>();           // body_of ids
  for (let t = 0; t <= currentTick; t++) {
    for (const ev of ticks[t].events) {
      if (ev.type === "kill") kills.set(ev.victim_id, ev);
      if (ev.type === "report_body") discovered.add(ev.body_of);
    }
  }
  return [...kills.values()].map(k => ({
    ...k,
    isDiscovered: discovered.has(k.victim_id),
  }));
}
```

For the tween, the simplest pattern in `@pixi/react` v8 is per-token interpolation state stored in a `useRef` with progress tracked via `useTick`. Sketch:

```tsx
function AgentToken({ targetRoom, prevRoom, color, jitter }: Props) {
  const progress = useRef(0);
  const [pos, setPos] = useState(roomCenter(prevRoom));
  useTick((delta) => {
    if (progress.current >= 1) return;
    progress.current = Math.min(1, progress.current + delta / TWEEN_TICKS);
    setPos(lerp(roomCenter(prevRoom), roomCenter(targetRoom), progress.current));
  });
  // Reset progress when targetRoom changes
  useEffect(() => { progress.current = 0; }, [targetRoom.id]);
  return <pixiGraphics draw={(g) => drawCircle(g, pos, color)} />;
}
```

Document the exact tween-duration constant in `## Decisions` so 4.11 (ReplayControls) can coordinate speed if needed.

For the sabotage overlay, a single full-canvas `<pixiGraphics>` with a fill at `alpha=0.3` covering the entire bounding box is the simplest. Render last in the tree so it sits above rooms/agents.

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.schemas"`
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
Open a PR from branch `phase-4-mapview-full` with a title like `task 4.5: mapview full (sabotage, vents, bodies, tween)`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7, DESIGN.md §8.3), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
