# Phase 4 — Spectator UI

## Goal
Browser-based replay viewer. A non-technical viewer can follow a saved
game end-to-end without reading logs. API payloads use sanitized DTOs,
not raw engine state or replay internals.

**Scope decisions (lock these before dispatching any task):**

- **Replay-only MVP.** No live game streaming, no WebSocket, no
  tick-callback hook on `HeadlessGame`. The UI reads saved JSONL
  replays via REST. Live game broadcast is deferred to a post-Phase-4
  task (or Phase 5) once the replay path is proven.
- **Vertical slice first.** Tasks 4.1 → 4.2 → 4.3 → 4.4 build a
  minimal end-to-end path (one replay rendering one room with agents
  visibly moving). The mid-phase DTO audit fires here. Only after the
  audit lands do 4.4.5–4.8 fan out.
- **Mid-phase DTO audit, no real-provider analog.** Single-tool audit
  (Claude or Codex), no reconciliation. Focused on DTO/leak coverage
  after the substrate exists. The phase-closing acceptance gate is a
  manual UX session (a non-technical viewer follows a replay end-to-
  end without reading logs).

## Parallelism
4.1 → 4.2 → 4.3 → 4.4 in series. Mid-phase DTO audit runs after 4.4.
Then 4.4.5, 4.5, 4.6, 4.7, 4.8 can run in parallel once the audit
confirms the substrate is leak-free.

## Tasks

### Task 4.1 — FastAPI app skeleton and spectator DTOs
**Branch:** `phase-4-fastapi-app-skeleton`
**Depends on:** Phase 3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

`api/main.py`, REST routes for replay listing / fetch, and sanitized
spectator DTOs per §7. No WebSocket in MVP (live game streaming
deferred per phase scope decision above).

**Files in scope:**
- api/main.py
- api/schemas.py
- api/routes/replays.py
- api/routes/eval.py
- api/routes/__init__.py
- tests/api/test_schemas.py
- tests/api/test_routes.py

**Files NOT in scope:**
- engine/ core logic
- agents/
- llm/
- frontend/
- api/ws.py (deferred — no WebSocket in MVP)
- api/routes/games.py (live game streaming deferred)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] FastAPI app skeleton exists with REST routes registered per DESIGN.md §7 (replays, eval; games-live deferred).
- [ ] `api/schemas.py` defines the concrete DTO inventory (the elaboration of this task — to be filled before dispatch — must list every DTO with its fields and explicitly mark fields that exist in the engine but are deliberately excluded).
- [ ] DTO leak tests prove role, kill attribution, private cooldowns, observation-firewall internals, and raw replay JSONL internals are not exposed.
- [ ] Replay listing endpoint returns sanitized replay metadata; replay fetch endpoint returns a sanitized tick + meeting timeline for a single saved replay.
- [ ] API remains a thin adapter — no engine logic in `api/`.
- [ ] Relevant API tests pass.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

See DESIGN.md §7. FastAPI app gains `/replays` (list + fetch) and `/eval` routes. DTOs in `api/schemas.py` are sanitized — never embed raw `WorldState`, raw `ReplayEntry`, or engine-internal types. Mirror the firewall pattern from `observation/` — DTOs are a sanitized view over engine state, never the state itself.

**Ready-to-paste prompt:** `agent_prompts/task-4-1-fastapi-app-skeleton.md`

### Task 4.2 — Replay listing + fetch endpoint
**Branch:** `phase-4-replay-endpoint`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7, DESIGN.md §11.4
**Complexity:** Small

REST endpoints that read saved JSONL replays from disk and return
sanitized DTOs. No WebSocket; no live game stream. This is the
substrate the entire frontend consumes.

**Files in scope:**
- api/routes/replays.py
- api/replay_loader.py
- tests/api/test_replays.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- frontend/
- api/ws.py
- orchestrator/replay.py (consumed read-only; not modified)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] `GET /replays` returns sanitized metadata for every saved replay (game id, winner, total ticks, meeting count, total cost, prompt versions).
- [ ] `GET /replays/{id}` returns the full sanitized tick + meeting timeline for one replay.
- [ ] `GET /replays/{id}/meetings/{meeting_id}` returns a single meeting's sanitized transcript (reports, statements, ballots, contradiction flags, LLM cost metadata).
- [ ] Leak tests cover every endpoint: no role, kill attribution, private cooldowns, or raw `ReplayEntry` internals.
- [ ] Reader handles partial replays (no game-end record per Task 3.19) — surfaces `winner=null` cleanly, doesn't crash.
- [ ] Relevant API tests pass.
- [ ] `uv run ruff check .` passes.


**Implementation hint:**

`orchestrator/replay.py` already has `read_replay` / `compute_cost_usd` / `read_game_outcome` (post-3.19). Compose them into the replay loader. The endpoint is a thin shell: read JSONL → map each entry to its sanitized DTO → return list. Pagination can be added in Phase 5; MVP returns all entries.

**Ready-to-paste prompt:** `agent_prompts/task-4-2-replay-endpoint.md`

### Task 4.3 — React + Vite + Tailwind + PixiJS setup
**Branch:** `phase-4-react-vite-tailwind-setup`
**Depends on:** 4.2 merged
**Section refs:** DESIGN.md §7
**Complexity:** Small

`frontend/` skeleton, type-safe API client matching the DTOs from 4.1,
and a Zustand store interface that components consume. Use npm with
`package-lock.json` unless a frontend package manager has already been
chosen in the repo before this task starts.

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vite.config.ts
- frontend/tailwind.config.js
- frontend/postcss.config.js
- frontend/tsconfig.json
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/store/index.ts
- frontend/src/types/api.ts
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
- [ ] React + Vite + TypeScript + Tailwind + PixiJS skeleton compiles.
- [ ] Zustand store exposes a single `useReplayStore` (or equivalent) that holds the currently-loaded replay + a current-tick index.
- [ ] Type-safe API client (`frontend/src/api/client.ts`) consumes the DTOs from 4.1 via a generated or hand-authored TypeScript type module that mirrors the Pydantic schemas. Implementing agent picks: hand-authored is simpler; generated via `openapi-typescript` is more drift-resistant. Document the choice in `## Decisions`.
- [ ] `scripts/setup_env.sh` installs frontend dependencies once `frontend/package.json` exists, without changing Python setup behavior.
- [ ] `scripts/check.sh` runs the configured frontend `tsc --noEmit && vite build` (or equivalent), without changing Python check behavior.
- [ ] Frontend build/check command passes.

**Ready-to-paste prompt:** `agent_prompts/task-4-3-react-vite-tailwind-setup.md`

### Task 4.4 — MapView vertical slice
**Branch:** `phase-4-mapview-vertical-slice`
**Depends on:** 4.3 merged
**Section refs:** DESIGN.md §7
**Complexity:** Small

A minimal MapView wired end-to-end against a real saved replay. Goal:
prove the API → store → component contract works before fanning out to
five components. Renders one PixiJS canvas with rooms as colored
rectangles and agent tokens that advance position as the replay's
current-tick index changes. No sabotage, no body markers, no vent
animation, no meeting overlay — those are 4.4b.

**Files in scope:**
- frontend/src/components/MapView.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- api/
- frontend/src/store/index.ts (consumed read-only via the hook from 4.3)
- DESIGN.md
- AGENT_IMPLEMENTATION.md

**Definition of done:**
- [ ] App boots, lists available replays via the 4.2 endpoint, lets the user pick one.
- [ ] MapView renders rooms as PixiJS rectangles using room layout from the API DTO.
- [ ] Agent tokens render per-tick at the room they occupy in the current tick.
- [ ] A simple "next tick" / "previous tick" button advances the store's current-tick index; the canvas updates.
- [ ] Component consumes the shared store/API shape from 4.3. No direct engine/replay imports.
- [ ] Frontend build/check command passes.


**Implementation hint:**

The success criterion is one screenshot: a saved replay's tick 0 shows N agents in their starting rooms; clicking "next tick" 100 times shows them in their tick-100 rooms. No animation interpolation needed; teleport is fine for the slice. Polish lands in 4.4b.

**Ready-to-paste prompt:** `agent_prompts/task-4-4-mapview-vertical-slice.md`

### Mid-phase DTO audit

After 4.4 merges, run the Phase 4 mid-phase DTO audit before
dispatching 4.4.5–4.8. The audit prompt lives at
`audits/prompts/mid-phase-4-dto-audit-prompt.md` (to be authored after
4.4 is in flight; do not author it prematurely against substrate that
doesn't exist yet).

**Audit scope:**
- Every DTO in `api/schemas.py` is reviewed against the engine /
  observation / replay surface it shadows. For each DTO field, the
  audit asserts whether it carries role, kill attribution, private
  cooldown, observation-firewall internal, or raw replay-entry state.
- Every endpoint in `api/routes/` is reviewed for what it serializes
  vs. what its DTO promises.
- The frontend TypeScript types (`frontend/src/types/api.ts`) are
  checked for drift from the Pydantic DTOs.

**Audit verdict shape:** "Mid-phase DTO audit passes — proceed to fan
out 4.4.5–4.8" OR "Mid-phase DTO audit blocks fan-out — repair tasks
required: …"

Single-tool, no reconciliation. Output: one Markdown audit at
`audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto.md`.

### Task 4.4.5 — MapView full
**Branch:** `phase-4-mapview-full`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §7
**Complexity:** Medium

Expand MapView from the vertical slice into the full spectator view:
sabotage state, vent network, body markers, smooth interpolation
between ticks.

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
- [ ] Sabotage visualization (lights-out reduces room visibility per DESIGN.md §8.1).
- [ ] Vent network rendered (static graph from the DTO).
- [ ] Body markers appear at the room where a kill was reported (the body's room is in the meeting trigger DTO, not the kill event itself — role/kill attribution stay in the engine, not the DTO).
- [ ] Smooth interpolation between adjacent ticks (configurable tween duration).
- [ ] Component consumes the shared store/API shape from 4.3. No raw engine imports.
- [ ] Frontend build/check command passes.


**Implementation hint:**

See DESIGN.md §7 (frontend). PixiJS canvas renders rooms by `position` + `size` from the sanitized layout DTO. Use PixiJS `Ticker` for the tween; tween targets are the next tick's room positions.

**Ready-to-paste prompt:** `agent_prompts/task-4-4-5-mapview-full.md`

### Task 4.5 — MeetingView
**Branch:** `phase-4-meetingview`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §5, DESIGN.md §7
**Complexity:** Medium

Transcript renderer for one meeting: reports + accusation rounds +
ballots + contradiction flags. Activated when the replay's current
tick is inside a meeting window.

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
- [ ] MeetingView renders the full transcript exposed by the API DTOs: per-speaker reports with structured claims, statements per round, ballots with rationale text, contradiction flags inline.
- [ ] Prose `rationale_text` and `free_text` are foregrounded; structured fields are secondary.
- [ ] Prompt version + per-call cost are surfaced (small metadata footer per meeting).
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes.


**Implementation hint:**

See DESIGN.md §5. React component for meeting transcript + ballots. The MeetingView is hidden when the current tick is outside any meeting; replace MapView (or overlay on top of it — implementing agent picks based on layout sketch). Document the choice in `## Decisions`.

**Ready-to-paste prompt:** `agent_prompts/task-4-5-meetingview.md`

### Task 4.6 — ThoughtStream
**Branch:** `phase-4-thoughtstream`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Per-agent memory + LLM call viewer for one selected agent. Spectator
selects an agent; sees that agent's `render_for_prompt`-style view +
the LLM call records (prompt + response + cost) attached to that
agent during meetings.

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
- [ ] ThoughtStream displays the selected agent's memory view (role, tasks-completed, salience-ordered observations, beliefs, contradictions) as exposed by the spectator API.
- [ ] LLM call records for the agent: prompt template id, model id, input/output tokens, cost in USD, prompt + response text (truncated with expand-on-click for long responses).
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Component renders prompt versions and cost metadata when present.
- [ ] Frontend build/check command passes.


**Implementation hint:**

See DESIGN.md §6.6. Per-agent memory + belief view. The agent's role is in this view per the firewall design — the spectator API exposes it because the spectator is privileged (post-game replay). For live-game spectator (deferred), role would be redacted.

**Ready-to-paste prompt:** `agent_prompts/task-4-6-thoughtstream.md`

### Task 4.7 — BeliefMatrix
**Branch:** `phase-4-beliefmatrix`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Heatmap of who suspects whom. Reads the suspicion graph DTO per tick;
renders a (N × N) grid with cell color encoding suspicion intensity.

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
- [ ] Frontend build/check command passes.


**Implementation hint:**

See DESIGN.md §6.3. Suspicion graph as a matrix view. Row = observer, column = subject, cell color = suspicion confidence. Diagonal is N/A (an agent doesn't suspect themselves).

**Ready-to-paste prompt:** `agent_prompts/task-4-7-beliefmatrix.md`

### Task 4.8 — ReplayControls
**Branch:** `phase-4-replaycontrols`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §7, DESIGN.md §11.4
**Complexity:** Medium

Scrubber + speed control. Drives the current-tick index in the Zustand
store; every component re-renders against the new tick.

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
- [ ] Scrubber lets the spectator seek to any tick in the replay.
- [ ] Speed control: 0.5×, 1×, 2×, 4× playback (1 tick advance per N ms).
- [ ] Pause / play / step-forward / step-backward buttons.
- [ ] Snap-to-meeting: a "next meeting" button skips to the next meeting trigger tick.
- [ ] Component consumes the shared store/API shape from 4.3.
- [ ] Frontend build/check command passes.


**Implementation hint:**

See DESIGN.md §11.4. Replay scrubber with seek-to-tick. The store owns the current-tick state; this component only emits store actions. No PixiJS, no per-tick rendering — pure React + Tailwind.

**Ready-to-paste prompt:** `agent_prompts/task-4-8-replaycontrols.md`

### Phase-closing UX acceptance session

After 4.4.5–4.8 all merge, run a manual UX acceptance session. A
non-technical viewer (not the developer, not Claude) loads a saved
replay in the browser and follows the game end-to-end without reading
any logs, terminal output, or task documents. Outcome:

- **Pass** — viewer narrates what happened (who got ejected, who won,
  what the impostor's tell was) with no developer help. Phase 4
  closes.
- **Conditional pass** — viewer mostly follows but is confused about a
  specific UI element. File one or more polish tasks against the
  specific findings.
- **Fail** — viewer cannot follow without help. Re-plan; the substrate
  isn't done.

This is the only Phase 4 acceptance gate that's not automated. There
is no real-provider-eval analog for the UI.

## Merge Criteria
- Non-technical viewer can follow a saved replay end-to-end without
  reading logs (UX acceptance session passes or conditionally passes).
- Spectator API payloads expose sanitized DTOs only — no role, kill
  attribution, private cooldowns, observation-firewall internals, or
  raw replay-entry state.
- Mid-phase DTO audit passed before 4.4.5–4.8 fan-out.
- Frontend `tsc --noEmit` + `vite build` passes in CI.
- All Phase 3 static gates still green (`bash scripts/check.sh`).
- Live game broadcast deferred to Phase 5 (or a post-Phase-4 task) is
  documented as out of scope.
