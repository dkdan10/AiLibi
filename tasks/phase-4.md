# Phase 4 — Spectator UI

## Goal
Browser-based live spectator + replay viewer. API and WebSocket payloads use
sanitized DTOs, not raw engine state or replay internals.

## Parallelism
4.1 -> 4.2 -> 4.3 in series. Then 4.4 through 4.8 can run in parallel once the
shared store/API interface exists.

## Tasks

### Task 4.1 — FastAPI app skeleton and spectator DTOs
**Branch:** `phase-4-fastapi-app-skeleton`
**Depends on:** Phase 3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

api/main.py, basic routes, WebSocket endpoint registration, and sanitized API
DTO schemas per §7.

**Files in scope:**
- api/main.py
- api/schemas.py
- api/routes/games.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/__init__.py
- api/ws.py
- tests/api/test_schemas.py
- tests/api/test_routes.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] FastAPI app skeleton exists.
- [ ] Basic routes and WebSocket endpoint are registered per DESIGN.md §7.
- [ ] `api/schemas.py` defines sanitized spectator DTOs separate from engine schemas.
- [ ] DTO tests prove role, kill attribution, private cooldowns, and raw replay internals are not exposed.
- [ ] API remains a thin adapter.
- [ ] Relevant API tests pass.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §7. FastAPI app gains `/games`, `/replays`, `/eval` routes plus a WebSocket endpoint at `/ws/games/{id}`. DTOs in `api/schemas.py` are sanitized — never embed raw `WorldState`.

**Ready-to-paste prompt:** `agent_prompts/task-4-1-fastapi-app-skeleton.md`

### Task 4.2 — Game broadcast
**Branch:** `phase-4-game-broadcast`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

api/ws.py - broadcast sanitized tick and meeting events from a running game.

**Files in scope:**
- api/ws.py
- tests/api/test_ws.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] WebSocket broadcaster streams tick and meeting events from a running game.
- [ ] Broadcast payloads are `api/schemas.py` DTOs, not raw engine internals.
- [ ] WebSocket tests prove private engine fields and replay internals are not exposed.
- [ ] Relevant API/WebSocket tests pass.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §7. WebSocket broadcaster fans out per-tick payloads to subscribers. Per-spectator view is privileged but sanitized via api/schemas.py DTOs.

**Ready-to-paste prompt:** `agent_prompts/task-4-2-game-broadcast.md`

### Task 4.3 — React + Vite + Tailwind setup
**Branch:** `phase-4-react-vite-tailwind-setup`
**Depends on:** 4.2 merged
**Section refs:** DESIGN.md §7
**Complexity:** Small

frontend/ skeleton, type-safe API client, and shared store interface. Use npm
with package-lock.json unless a frontend package manager has already been
chosen in the repo before this task starts.

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vite.config.ts
- frontend/tailwind.config.js
- frontend/postcss.config.js
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/store/index.ts
- scripts/setup_env.sh
- scripts/check.sh

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/ beyond API client contract needs
- .github/workflows/ci.yml
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] React, Vite, and Tailwind frontend skeleton exists.
- [ ] Type-safe API client exists for the sanitized API DTOs from 4.1.
- [ ] Shared store interface is defined before component fan-out.
- [ ] Frontend package manager is npm with `package-lock.json`, unless an existing repo choice requires otherwise.
- [ ] scripts/setup_env.sh installs frontend dependencies once frontend/package.json exists, without changing Python setup behavior.
- [ ] scripts/check.sh runs the configured frontend build/check command, without changing Python check behavior.
- [ ] Frontend build/check command passes if configured.

**Ready-to-paste prompt:** `agent_prompts/task-4-3-react-vite-tailwind-setup.md`

### Task 4.4 — MapView
**Branch:** `phase-4-mapview`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

PixiJS canvas rendering rooms + players.

**Files in scope:**
- frontend/src/components/MapView.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] MapView renders rooms and players with PixiJS.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Component does not depend on raw engine state.
- [ ] Frontend build/check command passes if configured.


**Implementation hint:**

See DESIGN.md §7 (frontend). PixiJS canvas renders rooms by `position` + `size` from PublicMapView; player tokens move on tick.

**Ready-to-paste prompt:** `agent_prompts/task-4-4-mapview.md`

### Task 4.5 — MeetingView
**Branch:** `phase-4-meetingview`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §5, DESIGN.md §7
**Complexity:** Medium

Transcript renderer.

**Files in scope:**
- frontend/src/components/MeetingView.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] MeetingView renders meeting transcripts, ballots, and contradiction flags exposed by the API DTOs.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.


**Implementation hint:**

See DESIGN.md §5. React component for meeting transcript + ballots.

**Ready-to-paste prompt:** `agent_prompts/task-4-5-meetingview.md`

### Task 4.6 — ThoughtStream
**Branch:** `phase-4-thoughtstream`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Per-agent memory + LLM call viewer.

**Files in scope:**
- frontend/src/components/ThoughtStream.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] ThoughtStream displays per-agent memory and LLM reasoning/call information exposed by the spectator API.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Component renders prompt versions and cost metadata when present.
- [ ] Frontend build/check command passes if configured.


**Implementation hint:**

See DESIGN.md §6.6. Per-agent memory + belief view.

**Ready-to-paste prompt:** `agent_prompts/task-4-6-thoughtstream.md`

### Task 4.7 — BeliefMatrix
**Branch:** `phase-4-beliefmatrix`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Heatmap of who suspects whom.

**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] BeliefMatrix renders a heatmap of suspicion/trust relationships from sanitized spectator DTOs.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.


**Implementation hint:**

See DESIGN.md §6.3. Suspicion graph as a matrix view.

**Ready-to-paste prompt:** `agent_prompts/task-4-7-beliefmatrix.md`

### Task 4.8 — ReplayControls
**Branch:** `phase-4-replaycontrols`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7, DESIGN.md §11.4
**Complexity:** Medium

Scrubber, speed control.

**Files in scope:**
- frontend/src/components/ReplayControls.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] ReplayControls provides scrubber and speed controls for sanitized replay DTOs.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes if configured.


**Implementation hint:**

See DESIGN.md §11.4. Replay scrubber with seek-to-tick.

**Ready-to-paste prompt:** `agent_prompts/task-4-8-replaycontrols.md`

## Merge Criteria
- Non-technical viewer can watch a live game and replay any saved one.
- Spectator API and WebSocket payloads expose sanitized DTOs only.
