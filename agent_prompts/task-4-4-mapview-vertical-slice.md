# Agent Prompt — 4.4 MapView vertical slice

You are working on AiLibi. Before starting, read AGENTS.md, DESIGN.md, and the task section in tasks/phase-4.md.

## Role and context
You are an AI coding agent working on the AiLibi project. Follow AGENTS.md exactly. DESIGN.md is the source of truth and the task contract below is the implementation contract for this PR. AGENT_IMPLEMENTATION.md is the provider-neutral build plan and is read once during onboarding (see AGENTS.md), not per task.

## Exact section reference
Implement Task 4.4 — MapView vertical slice, anchored to DESIGN.md §7. Do not implement work outside these references.

## Task contract
The authoritative task contract is copied below from tasks/phase-4.md. Follow it exactly, including branch, dependencies, section refs, files in scope, files not in scope, and definition of done.

**Branch:** `phase-4-mapview-vertical-slice`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Small

The vertical slice that ratifies the API → store → component contract.
Renders one PixiJS canvas showing rooms + agent tokens for a real
saved replay. Spectator picks a replay; sees the map; clicks "next
tick" and agents move. Nothing more. Polish (sabotage, vents, bodies,
tween) lands in 4.4.5 after the mid-phase DTO audit confirms the
substrate is leak-free.

**Acceptance criterion is visual.** This task's success is one
screenshot showing N agents in N rooms at tick 0, and another showing
them in their tick-100 rooms after clicking "next tick" 100 times.
Both attached to the PR. No screenshot = not done.

**Out of scope** (explicit decisions deferred to 4.4.5):

- Sabotage visualization (lights, etc.)
- Vent network rendering
- Body markers
- Smooth interpolation / tween between ticks
- Meeting overlay (MeetingView is 4.5)
- Belief matrix overlay (BeliefMatrix is 4.7)
- ThoughtStream (4.6)
- Replay scrubber / play-pause (4.8)
- Auto-advance on a timer (4.8)
- Camera zoom / pan
- Player labels (just colored tokens — labels in 4.4.5)
- Dead-agent rendering (just don't render is fine for the slice;
  body markers come in 4.4.5)

**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (consumed read-only via the hook from 4.3)
- frontend/src/api/client.ts (consumed read-only)
- frontend/src/types/api.ts (frozen at 4.3)
- frontend/package.json (locked at 4.3; no new deps unless absolutely necessary, documented in `## Decisions`)
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
- .github/workflows/ci.yml

**Definition of done:**
- [ ] **App boots, lists replays, lets user select one.** `ReplayPicker.tsx` reads `useReplayStore().replayList`; renders one button per replay (label: `seed N — winner X — ticks Y`); clicking calls `selectReplay(gameId)`. Loading + error states render meaningfully.
- [ ] **MapView renders rooms.** Each `RoomView` from `currentReplay.map.rooms` becomes a `RoomRect` PixiJS Graphics rect at `position.x / position.y` with size `width × height`. Rooms colored with a stable hash per room id (deterministic; same room = same color across renders). Room name rendered as PixiJS Text inside the rect.
- [ ] **MapView renders agent tokens.** Each `AgentTickStateView` in `currentReplay.ticks[currentTick].agent_states` with `is_alive=true` and `room_id != null` becomes an `AgentToken` PixiJS circle at the center of its room, offset by a deterministic per-agent jitter (so multiple agents in one room don't fully overlap). Token color = `PlayerView.color` for that agent. Dead agents and venting agents are not rendered in the slice.
- [ ] **TickStepper component.** Renders "← prev" / "next →" buttons + a "Tick: N / total" label. Buttons clamp at 0 and `currentReplay.ticks.length - 1`. Clicking calls `setCurrentTick(n)`; MapView re-renders.
- [ ] **App.tsx composition.** Top: ReplayPicker. Middle: MapView (PixiJS canvas, ~800×600). Bottom: TickStepper. Layout via Tailwind flexbox; no fancy CSS.
- [ ] **No direct engine/orchestrator/api imports from frontend.** Components only consume the store + types. The `api/client.ts` calls are isolated to the store actions defined in 4.3.
- [ ] **No new npm dependencies** unless absolutely necessary. If one is required (e.g. a color-hash utility), document the choice in `## Decisions` and pin the version. PixiJS, React, Zustand from 4.3 are sufficient for the slice.
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`. Run `npm run tsc:check`; passes.
- [ ] **Vite build succeeds.** `npm run build` exits 0 with no warnings about unused imports etc.
- [ ] **Screenshots attached to PR.** Two minimum: tick 0 and a later tick (e.g. tick 100) of the same replay, showing agents in different rooms. PR description includes the screenshots.
- [ ] **Manual visual smoke documented.** PR description states: "Tested with `replays/replay-seed-22.jsonl` (or equivalent real replay); clicked next-tick N times; agents visibly moved through M distinct rooms; no console errors."
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (Python tests unaffected).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally (includes frontend block from 4.3).

## Dependency contract check
Run these before editing. If any fail, stop and report — your dependencies are not where this task expects them.

- `uv run python -c "import frontend/src/types/api.ts::*` (every DTO from 4"`
- `uv run python -c "import frontend/src/api/client"`
- `uv run python -c "import api.replay_loader"`
- `uv run python -c "import api.schemas"`
- `uv run python -c "import api.main"`

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
Open a PR from branch `phase-4-mapview-vertical-slice` with a title like `task 4.4: mapview vertical slice`.
The PR description must follow `.github/pull_request_template.md` and include `## Summary` (1–3 bullets referencing DESIGN.md §7), `## Definition of done` (the checklist from this contract, ticked), `## Decisions` (every judgment call), and (only when blocking) `## Questions`.
