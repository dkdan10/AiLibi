# Phase 4 — Spectator UI

## Goal
Browser-based live spectator + replay viewer.

## Parallelism
4.1 -> 4.2 -> 4.3 in series. Then 4.4 through 4.8 can run in parallel once a shared store interface exists.

## Tasks
### Task 4.1 — FastAPI app skeleton
**Branch:** `phase-4-fastapi-app-skeleton`
**Depends on:** Phase 3 merged
**Section refs:** DESIGN.md §7

api/main.py, basic routes, WebSocket endpoint per §7.

**Files in scope:**
- api/main.py
- api/routes/TODO_REVIEW
- api/ws.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] FastAPI app skeleton exists.
- [ ] Basic routes and WebSocket endpoint are registered per DESIGN.md §7.
- [ ] API remains a thin adapter.
- [ ] Relevant API tests pass if present.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-4-1-fastapi-app-skeleton.md`

### Task 4.2 — Game broadcast
**Branch:** `phase-4-game-broadcast`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7

api/ws.py - broadcast tick events from a running game.

**Files in scope:**
- api/ws.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] WebSocket broadcaster streams tick events from a running game.
- [ ] Broadcast payloads are sanitized API DTOs, not raw engine internals.
- [ ] Relevant API/WebSocket tests pass if present.
- [ ] ruff check . passes.

**Ready-to-paste prompt:** `codex_prompts/task-4-2-game-broadcast.md`

### Task 4.3 — React + Vite + Tailwind setup
**Branch:** `phase-4-react-vite-tailwind-setup`
**Depends on:** 4.2 merged
**Section refs:** DESIGN.md §7

frontend/ skeleton, type-safe API client.

**Files in scope:**
- frontend/package.json
- frontend/vite.config.ts
- frontend/src/App.tsx
- frontend/src/TODO_REVIEW type-safe API client path
- frontend/src/store/TODO_REVIEW shared store interface path

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/ beyond API client contract needs
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] React, Vite, and Tailwind frontend skeleton exists.
- [ ] Type-safe API client exists.
- [ ] Shared store interface is defined before component fan-out.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-4-3-react-vite-tailwind-setup.md`

### Task 4.4 — MapView
**Branch:** `phase-4-mapview`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7

PixiJS canvas rendering rooms + players.

**Files in scope:**
- frontend/src/components/MapView.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/ unless TODO_REVIEW from 4.3 requires a compatible adapter
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] MapView renders rooms and players with PixiJS.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-4-4-mapview.md`

### Task 4.5 — MeetingView
**Branch:** `phase-4-meetingview`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §5, DESIGN.md §7

Transcript renderer.

**Files in scope:**
- frontend/src/components/MeetingView.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/ unless TODO_REVIEW from 4.3 requires a compatible adapter
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] MeetingView renders the meeting transcript.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-4-5-meetingview.md`

### Task 4.6 — ThoughtStream
**Branch:** `phase-4-thoughtstream`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §6, DESIGN.md §7

Per-agent memory + LLM call viewer.

**Files in scope:**
- frontend/src/components/ThoughtStream.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/ unless TODO_REVIEW from 4.3 requires a compatible adapter
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] ThoughtStream displays per-agent memory and LLM reasoning/call information exposed by the spectator API.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-4-6-thoughtstream.md`

### Task 4.7 — BeliefMatrix
**Branch:** `phase-4-beliefmatrix`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §6, DESIGN.md §7

Heatmap of who suspects whom.

**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/ unless TODO_REVIEW from 4.3 requires a compatible adapter
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] BeliefMatrix renders a heatmap of suspicion/trust relationships.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-4-7-beliefmatrix.md`

### Task 4.8 — ReplayControls
**Branch:** `phase-4-replaycontrols`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7, DESIGN.md §11.4

Scrubber, speed control.

**Files in scope:**
- frontend/src/components/ReplayControls.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/ unless TODO_REVIEW from 4.3 requires a compatible adapter
- DESIGN.md
- CODEX_IMPLEMENTATION.md

**Definition of done:**
- [ ] ReplayControls provides scrubber and speed controls.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `codex_prompts/task-4-8-replaycontrols.md`

## Merge Criteria
- Non-technical viewer can watch a live game and replay any saved one.
