# AiLibi — System Design Document

**Status:** v0.1 draft
**Audience:** engineers implementing or maintaining the system
**Scope:** complete architecture and roadmap for a multi-agent social-deduction simulation platform

---

## 0. Design Stance (read this first)

Three load-bearing decisions shape everything else. If you disagree with these, the rest of the document needs to be re-derived.

1. **Tick-based deterministic engine with a strict observation firewall.** The engine ticks at a fixed rate (target 2 Hz). Agents never touch engine state directly — they receive `ObservationPacket`s filtered by visibility rules. Replays are bit-exact from a seed. This is non-negotiable: it is what makes the system testable, debuggable, and provably non-cheating.

2. **Two-tier agent reasoning.** Tactical decisions (move, do task, follow, vent) are rule-based and run every tick. Strategic decisions (meeting reports, voting, suspicion updates) use an LLM and run only at meetings or specific triggers (witnessing a kill, finding a body). A full game targets ≤ 100 LLM calls. Without this split, cost and latency make the system unviable.

3. **Memory is structured first, natural-language second.** Each agent maintains a typed event log and a derived belief state (trust scores, alibi map, suspicion graph). The LLM sees a *rendered view* of that structure during meetings — never raw chat history as the source of truth. This makes reasoning auditable, testable, and replayable.

The product is therefore not a "game with AI players bolted on." It is a **multi-agent reasoning testbed** whose game layer happens to look like Among Us.

---

## 1. System Architecture

### 1.1 Component diagram

```
                ┌──────────────────────────────────────────────┐
                │                ORCHESTRATOR                  │
                │  (game lifecycle, tick clock, seeded RNG,    │
                │   role assignment, replay persistence)       │
                └────────────────┬─────────────────────────────┘
                                 │ drives
        ┌────────────────────────┼────────────────────────┐
        │                        │                        │
┌───────▼────────┐    ┌──────────▼──────────┐    ┌────────▼────────┐
│  GAME ENGINE   │    │ OBSERVATION SERVICE │    │ MEETING MANAGER │
│  - world state │───▶│  - visibility rules │    │ - report intake │
│  - rules       │    │  - packet builder   │    │ - speech rounds │
│  - rng         │    │  - audit log        │    │ - voting        │
└───────┬────────┘    └──────────┬──────────┘    └────────┬────────┘
        │                        │                        │
        │              ┌─────────▼──────────┐             │
        │              │     AGENTS         │◀────────────┘
        │              │  - perception      │
        │              │  - memory          │
        │              │  - tactical policy │
        │              │  - strategic LLM   │
        │              └─────────┬──────────┘
        │                        │ Action / Statement / Ballot
        │                        ▼
        │                ┌───────────────┐
        │                │ ACTION QUEUE  │
        ▼                │  validated    │
   ┌─────────┐           └───────┬───────┘
   │ EVENT   │◀──────────────────┘
   │  BUS    │
   └────┬────┘
        │
        ├─────▶ Persistence  (Postgres: games, ticks, events, transcripts)
        ├─────▶ Spectator API (FastAPI + WebSocket, privileged view)
        └─────▶ Eval Harness  (offline replay analysis)
```

### 1.2 State ownership

| State                              | Owner               | Visibility                                 |
| ---------------------------------- | ------------------- | ------------------------------------------ |
| Player positions, roles, bodies    | Engine              | Engine only; spectator API after sanitize  |
| Kill cooldowns, sabotage timers    | Engine              | Engine only                                |
| Tasks completed (global counter)   | Engine              | Broadcast to all agents (per Agent)     |
| RNG state                          | Engine              | Engine only                                |
| Visibility config (radii, walls)   | Map (static)        | Public                                     |
| Per-agent memory & beliefs         | Agent               | That agent only; spectator UI may peek     |
| Active meeting transcript          | MeetingManager      | All agents during meeting                  |
| Replay log                         | Persistence         | Privileged                                 |

### 1.3 The observation firewall

This is the single most important architectural property. Enforced as follows:

- `engine/` and `agents/` are separate Python packages.
- `agents/` has no import path to `engine/`. A pre-commit hook + import-linter rule fails CI if `agents/` imports from `engine/`.
- Agent-visible boundary schemas are engine-free Pydantic models defined outside
  `engine/`: `ObservationPacket`, `PublicMapView`, and `ActionIntent`.
  Engine `Action` objects remain internal to `engine/`; the orchestrator
  translates validated `ActionIntent`s into engine actions.
- ObservationService logs every packet to an audit trail. The leak test (Section 11) replays games and asserts no field in any packet contains information the agent should not have.

### 1.4 Real-time vs turn-based

- **Gameplay phase:** tick-based, default 2 Hz. Agents are queried each tick for tactical actions; the budget per agent per tick is microseconds (rule-based, no LLM).
- **Meeting phase:** turn-based, async within turn. Each agent has a deadline (default 30 s) to submit a report, then the floor advances. Missed deadlines yield a default "no statement."
- **Triggered strategic calls:** when an agent witnesses a kill or finds a body, the next tick triggers an LLM call for that agent only, gated by per-agent and per-game budgets.

The tick clock is wall-clock-locked for live spectating but can run as fast as the slowest agent allows in headless mode (used for evals and tournaments).

---

## 2. Core Modules and File Structure

```
ailibi/
├── README.md
├── pyproject.toml                   # uv / poetry; pinned versions
├── docker-compose.yml               # postgres, redis, api, frontend
├── .env.example
│
├── engine/                          # pure simulation; no LLM, no network
│   ├── world.py                     # WorldState, Map, Room, Vent, Door
│   ├── entities.py                  # Player, Body, Task, Sabotage
│   ├── rules.py                     # kill, report, vent, sabotage rules
│   ├── win_conditions.py            # crew-task-complete, impostor-parity, sabotage-timeout
│   ├── actions.py                   # Action types + validators
│   ├── visibility.py                # room visibility, line-of-sight, lights-out
│   ├── rng.py                       # seeded numpy.random wrapper
│   └── tick.py                      # advance_tick(state, actions) -> state
│
├── observation/                     # information firewall
│   ├── service.py                   # ObservationService
│   ├── packet.py                    # ObservationPacket schema (Pydantic)
│   ├── public_map.py                # PublicMapView schema for agent pathing
│   ├── action_intent.py             # engine-free agent action intent schema
│   └── audit.py                     # records every packet for leak tests
│
├── agents/                          # agent runtimes (no engine imports!)
│   ├── base.py                      # AgentInterface protocol
│   ├── perception.py                # ObservationPacket -> episodic events
│   ├── tactical/
│   │   ├── crewmate_policy.py       # task selection, pathing, panic
│   │   ├── impostor_policy.py       # target selection, vent use, alibi
│   │   └── pathing.py               # A* over room graph
│   ├── strategic/
│   │   ├── reasoner.py              # LLM-driven meeting reasoning
│   │   ├── prompts/                 # versioned prompt templates (jinja2)
│   │   │   ├── crewmate_report.j2
│   │   │   ├── impostor_report.j2
│   │   │   ├── accusation_round.j2
│   │   │   └── vote_ballot.j2
│   │   └── output_schemas.py        # ReportDocument, VoteBallot, etc.
│   ├── memory/
│   │   ├── episodic.py              # timestamped observation events
│   │   ├── beliefs.py               # trust scores, suspicion graph
│   │   ├── working.py               # current goal, current path
│   │   ├── meeting_memo.py          # cross-meeting belief updates
│   │   └── store.py                 # serialization & retrieval
│   └── runtime.py                   # AgentRuntime ties tactical + strategic + memory
│
├── meetings/
│   ├── manager.py                   # MeetingManager state machine
│   ├── transcript.py                # structured + free-text turns
│   ├── voting.py                    # tally, ties, ejection
│   └── schemas.py                   # ReportDocument, Statement, VoteBallot
│
├── orchestrator/
│   ├── game.py                      # Game class: one full match
│   ├── scheduler.py                 # tick clock, agent deadlines
│   ├── seeder.py                    # role/spawn assignment
│   ├── boundary.py                  # PublicMapView/ActionIntent adapters
│   └── replay.py                    # ReplayLog write/read
│
├── llm/
│   ├── client.py                    # LLMClient protocol
│   ├── claude_provider.py           # Anthropic SDK adapter
│   ├── cache.py                     # prompt-hash cache
│   └── budget.py                    # token + dollar budget per game
│
├── api/                             # spectator + control plane
│   ├── main.py                      # FastAPI app
│   ├── ws.py                        # /ws/games/{id} broadcaster
│   ├── routes/
│   │   ├── games.py                 # POST /games (create), GET /games/{id}
│   │   ├── replays.py
│   │   └── eval.py
│   └── schemas.py                   # API DTOs (separate from engine schemas)
│
├── frontend/                        # spectator UI
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
│       ├── App.tsx
│       ├── components/
│       │   ├── MapView.tsx          # PixiJS canvas
│       │   ├── MeetingView.tsx
│       │   ├── ThoughtStream.tsx    # per-agent memory + LLM reasoning
│       │   ├── BeliefMatrix.tsx     # who suspects whom
│       │   └── ReplayControls.tsx
│       └── store/                   # zustand
│
├── eval/
│   ├── leak_test.py                 # asserts observation purity
│   ├── determinism_test.py          # same seed -> same game
│   ├── balance_eval.py              # win rates across N seeds
│   ├── meeting_quality.py           # vote-correctness, accusation accuracy
│   ├── report_schema.py             # tournament/eval JSON report DTOs
│   └── fixtures/                    # canonical replays
│
├── scripts/
│   ├── run_game.py                  # CLI: single headless game
│   ├── run_tournament.py            # CLI: N games, aggregate stats
│   └── render_replay.py             # produce inspectable HTML
│
└── tests/
    ├── engine/
    ├── observation/
    ├── agents/
    └── meetings/
```

Module responsibilities are intentionally narrow. `engine/` is a pure function over state. `agents/` is the only place that talks to LLMs. `api/` is a thin adapter. This separation is what allows the eval harness to run thousands of games headlessly without booting the API.

---

## 3. Game Engine Design

### 3.1 Game loop

Single tick (`engine/tick.py::advance_tick`):

1. **Apply queued actions** from the previous tick. Each action is re-validated against current state (positions could have changed by sabotage). Invalid actions become no-ops; an `ActionRejected` event is emitted.
2. **Resolve passive effects:** kill cooldown decrement, sabotage timer countdown, task progress on continuing tasks.
3. **Check victory:** crewmates win on all-tasks-done; impostors win on parity (impostors ≥ remaining crew) or sabotage-timeout. If a side has won, emit `GameOver` and return.
4. **Compute observations:** for each living agent, ObservationService renders an `ObservationPacket` for tick `t`.
5. **Solicit actions:** agents return engine-free `ActionIntent`s. The orchestrator validates and translates them into engine `Action`s before they enter the next tick's action queue. In live mode this is awaited with a per-agent deadline; in headless mode it is synchronous.
6. **Emit tick event** to event bus (full state, used by spectator API and replay log).
7. Increment tick counter; repeat.

A meeting interrupts the tick loop: when an agent submits a `ReportBody` or `EmergencyButton` intent that validates into an engine action, the engine transitions to `MEETING` phase. The MeetingManager owns the loop until a vote resolves and returns an engine-free `MeetingResult`; the orchestrator applies that result to engine-owned state and returns control to tick `t+1`.

### 3.2 State model

```python
@dataclass(frozen=True)
class WorldState:
    tick: int
    phase: Phase                      # PLAY | MEETING | GAME_OVER
    map: MapId                        # static; loaded once
    players: dict[PlayerId, PlayerState]
    bodies: dict[BodyId, BodyState]   # location, killed_by (hidden), discovered_by
    tasks: dict[TaskId, TaskState]    # location, owner, progress, completed
    sabotage: SabotageState | None
    cooldowns: dict[PlayerId, int]    # ticks remaining, impostor only
    rng_state: bytes                  # serialized RNG cursor
    seed: int

@dataclass(frozen=True)
class PlayerState:
    id: PlayerId
    role: Role                        # CREWMATE | IMPOSTOR
    alive: bool
    room: RoomId
    position: tuple[float, float]     # within-room coords
    last_action: Action | None
    in_vent: bool
```

Frozen dataclasses keep `advance_tick` a pure function: `(state, actions) -> (state', events)`. Replay is just `reduce(advance_tick, actions_log, initial_state)`.

### 3.3 Entities

- **Player**: position, role, alive flag. Role is hidden from observation.
- **Body**: where someone died, who killed (hidden until game-over), and who discovered it.
- **Task**: anchored to a room; "long" tasks take N ticks of standing in place. Tasks contribute to a global completion counter visible to all crewmates.
- **Sabotage**: a global timer that crewmates must resolve within N ticks or impostors win. Disables certain rooms (e.g., lights → reduces crew visibility radius).

### 3.4 Rules

- **Kill:** impostor and crewmate must be in the same room and within kill radius; cooldown must be 0. Kill spawns a `Body` and emits `Killed` event. Witnesses (other players in same room with line-of-sight) are recorded — used by ObservationService.
- **Report:** any living player in a room containing a body can `ReportBody`. Triggers meeting.
- **Vent:** impostor-only; vent network is per-map; entering and exiting are separate actions with a one-tick traversal. Vent use is observable to anyone in the source/destination room.
- **Emergency Meeting:** any player can call once per game (configurable). Triggers meeting.
- **Sabotage:** impostor-only; certain sabotages have global UI effects but the global task counter still progresses.

### 3.5 Win conditions

Checked in order each tick:

1. `crew_tasks_done == total_tasks` → crew win.
2. `count(impostors_alive) >= count(crew_alive)` → impostor win.
3. Active sabotage with `remaining_ticks == 0` → impostor win.
4. Otherwise: continue.

### 3.6 Hidden information

The engine is the single source of truth and *contains* hidden info (roles, kill attribution, vent use). Containment is fine; what matters is that this state never leaves the engine except through ObservationService, which is the only privileged consumer that strips hidden fields.

---

## 4. Agent System Design

### 4.1 Layered architecture

```
            ObservationPacket
                   │
                   ▼
            ┌──────────────┐
            │  PERCEPTION  │  ── normalize → Episodic Event
            └──────┬───────┘
                   │
         ┌─────────┴──────────┐
         │                    │
         ▼                    ▼
   ┌──────────┐         ┌──────────────┐
   │  MEMORY  │◀───────▶│ BELIEF STATE │ (suspicions, alibis, trust)
   └────┬─────┘         └──────┬───────┘
        │                      │
        ▼                      ▼
  ┌──────────────┐      ┌────────────────┐
  │ TACTICAL     │      │ STRATEGIC      │
  │ POLICY       │      │ POLICY (LLM)   │
  │ (rule-based) │      │ - meetings     │
  └──────┬───────┘      │ - voting       │
         │              │ - triggers     │
         ▼              └────────┬───────┘
       ActionIntent              │
                              Statement / Ballot
```

### 4.2 Perception

Per tick, the agent receives an `ObservationPacket`:

```python
class ObservationPacket(BaseModel):
    tick: int
    agent_id: PlayerId
    self_state: SelfView          # my room, my role, my pending task
    visible_players: list[PlayerView]    # id, room, action; only if visible
    visible_bodies: list[BodyView]
    audible_events: list[AudibleEvent]   # vent use heard, sabotage alarm
    global_state: GlobalView      # task completion %, sabotage status
    cooldown: int | None          # impostor only
```

Perception code converts this into `EpisodicEvent`s tagged with provenance. Crucially: **role is in `self_state`, never in `visible_players` for others.**

Agents also receive a `PublicMapView` containing only public topology needed for
pathing and tactical choice. Tactical policies return `ActionIntent`s, not
engine `Action`s. This keeps both directions of the agent boundary free of
engine imports while still allowing deterministic gameplay.

### 4.3 Memory

See Section 6 for the full memory architecture. At a glance:

- **Episodic store:** raw event log, append-only, indexed by tick and entity.
- **Working memory:** current goal, current path, current intent — overwritten frequently.
- **Belief state:** trust score, suspicion score, alibi map per other player; updated by perception and by meeting outcomes.
- **Meeting memos:** persistent across meetings; the running narrative the agent builds about who's likely impostor.

### 4.4 Reasoning

**Tactical policy** is a finite-state controller:

- *Crewmate FSM:* `IDLE → MOVE_TO_TASK → DO_TASK → IDLE`. Interrupts: `BODY_VISIBLE → REPORT`, `KILL_WITNESSED → FLEE_AND_REPORT`. Pathing is A* over the room graph.
- *Impostor FSM:* `IDLE → STALK → KILL_OPPORTUNITY → KILL → COVER`. Cover behavior: pretend-task in a different room, optionally vent. Target selection scores victims by isolation × witness-risk × kill-cooldown.

Tactical decisions are deterministic given memory state, which means agent behavior is replayable.

**Strategic policy** is LLM-driven and runs only at:

1. The start of each meeting → produce `ReportDocument`.
2. Each speech turn the agent has during meeting → produce `Statement`.
3. End of meeting → produce `VoteBallot`.
4. After meeting closes → optional belief-state update reflection.

Inputs to the LLM: a *rendered* view of memory (not raw chat; not raw events) plus the public meeting transcript so far. Output is constrained to a Pydantic schema (JSON mode / structured outputs). No free-form reasoning leaks into game state.

### 4.5 Role-specific behavior

The same `AgentRuntime` class is used for both roles; the role flag selects which prompt template, which tactical FSM, and which output schema. Impostor agents are explicitly told their role and that they should *not* reveal it; the prompt frames lying as a game rule, not a moral choice. (This is necessary — in practice frontier models will refuse or over-hedge if you don't.)

### 4.6 Uncertainty handling

Every belief in the belief state is stored with a confidence in [0, 1]. The LLM is given confidences in its rendered memory view. Voting weights uncertainty: the default voting heuristic does not vote-eject if max suspicion confidence < 0.6; instead it skips. This prevents one confident liar from cascading the table into a wrong eject.

### 4.7 Anti-cheating (defense in depth)

Three layers:

1. **Architectural:** agents cannot import engine state. They only see `ObservationPacket`.
2. **Schema:** `ObservationPacket` has no field for "other player's role" or "kill attribution." If a developer adds such a field by accident, the leak test fails.
3. **Prompt:** the LLM prompt is built from the rendered memory view, which is itself derived from the episodic store. There is no path from engine state to LLM prompt that bypasses memory.

---

## 5. Meeting & Communication System

### 5.1 Trigger and lifecycle

A meeting starts when a `ReportBody` or `EmergencyMeeting` action validates. The MeetingManager:

1. Freezes engine state (no movement, no kills, cooldowns paused).
2. Broadcasts `MeetingOpened` with the trigger info to all living agents.
3. Runs the protocol below.
4. Resolves voting and returns a `MeetingResult` containing the ejection/skip
   outcome, ballots, contradiction flags, and final transcript. The
   orchestrator applies the result to engine-owned state, emits
   `MeetingClosed`, records the meeting artifacts in replay, and resumes the
   engine.

### 5.2 Protocol

```
PHASE 1: REPORT INTAKE          (parallel, deadline T1)
  Each living agent submits a ReportDocument.

PHASE 2: ACCUSATION ROUNDS       (sequential, R rounds)
  Speaker order: round-robin starting from reporter.
  Each turn: agent reads transcript-so-far, submits one Statement.
  A Statement may target another agent ("I think X is impostor because...")
  or be defensive ("I was in Storage with Y at tick 145.")

PHASE 3: VOTING                  (parallel, deadline T2)
  Each agent submits a VoteBallot: target_id | SKIP, with rationale.

PHASE 4: RESOLUTION
  Tally votes. If a player has plurality and meets threshold, eject.
  If tie or below threshold, skip.
  Emit MeetingResult with all ballots and final transcript.
```

Default values for MVP: T1 = 30 s, R = 2 rounds, T2 = 30 s. In headless mode the deadlines are turned off and the protocol runs as fast as the LLM can respond.

### 5.3 Structured + natural-language layers

Every artifact has both:

- **Structured:** JSON schema, mechanically parseable. Used by belief tracking, contradiction detection, replay analytics.
- **Free text:** the agent's natural-language argument. Shown to the human spectator and given to other agents in subsequent rounds.

Example `ReportDocument`:

```json
{
  "agent_id": "p3",
  "tick": 412,
  "observations": [
    {"tick": 380, "type": "saw_player", "subject": "p5", "room": "Electrical", "with": ["p7"]},
    {"tick": 395, "type": "completed_task", "task_id": "wiring_admin"},
    {"tick": 410, "type": "found_body", "body_of": "p2", "room": "MedBay"}
  ],
  "claims": [
    {"type": "alibi", "for": "p3", "from_tick": 380, "to_tick": 410, "evidence": ["wiring_admin", "saw_player:p5"]},
    {"type": "accusation", "against": "p5", "confidence": 0.4, "reason": "near MedBay corridor minutes before kill"}
  ],
  "free_text": "I was doing wiring in Admin from tick 380. I saw p5 head toward Electrical with p7. p2's body was in MedBay; p5 was in the right corridor."
}
```

### 5.4 Contradiction detection

Implemented in `meetings/transcript.py`. After each turn, the transcript service:

1. Indexes all alibi claims by `(agent, tick_range, location)`.
2. Cross-references with publicly stated `saw_player` observations.
3. Flags inconsistencies (e.g., two agents both claiming to be in Storage during the same tick range with no third corroborator).

Flags are *information*, not a verdict — they are added to the rendered memory view that subsequent agents see. This lets the model reason about contradictions without us hard-coding "always vote the contradicting player."

### 5.5 Voting decision

Voting is LLM-driven with a structured output:

```json
{
  "target": "p5" | "SKIP",
  "confidence": 0.65,
  "primary_reason_id": "stmt_12",
  "considered_alternatives": ["p7"],
  "rationale_text": "p5's claim to be in Electrical is contradicted by p1's alibi..."
}
```

The voting prompt receives: rendered memory, full transcript, contradiction flags, and the agent's current suspicion graph. The output is parsed and tallied. Ballots are publicly logged after the meeting (post-hoc transparency for analysis; not visible to agents during the vote).

---

## 6. Memory Architecture

This is the heart of the project. A weak memory system is the most likely cause of weak agent reasoning.

### 6.1 Stores

```
┌──────────────────────────────────────────────────────────┐
│                     EPISODIC STORE                       │
│  Append-only log of typed events with provenance         │
│  Examples: SawPlayer, FoundBody, CompletedTask,          │
│            HeardSabotage, EnteredRoom                    │
└─────────────────────┬────────────────────────────────────┘
                      │ ingestion + summarization
                      ▼
┌──────────────────────────────────────────────────────────┐
│                  WORKING MEMORY                          │
│  Volatile: current goal, current path, last_seen[player] │
│  Rebuilt each tick from episodic + belief state          │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                   BELIEF STATE                           │
│  Per other player:                                       │
│    trust: float[0..1]                                    │
│    suspicion: float[0..1]                                │
│    alibi_map: list[AlibiClaim]                           │
│    inconsistencies: list[ContradictionRef]               │
│  Updated by: new observations, meeting outcomes,         │
│              post-meeting reflection                     │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│                  MEETING MEMO                            │
│  Persistent narrative across meetings.                   │
│  After each meeting the strategic policy may write       │
│  a short memo summarizing what changed.                  │
└──────────────────────────────────────────────────────────┘
```

### 6.2 Event abstraction (raw → summarized)

Raw `ObservationPacket`s would explode the prompt by mid-game. Two-stage compression:

1. **Per-tick coalescing:** consecutive `EnteredRoom` events for the same room collapse into a single "stayed in Room X from tick A to tick B."
2. **Salience filter at meeting time:** when rendering memory for an LLM call, the rendering function selects events by salience — kills witnessed, body discoveries, vent observations, contradicting claims — and elides routine task work unless explicitly relevant.

The full episodic log is kept on disk; only the rendered view goes into the prompt.

### 6.3 Belief tracking

Belief updates have explicit rules (no hidden ML model):

- `+0.2 suspicion` if seen near a body shortly before discovery.
- `+0.3 suspicion` if claimed alibi contradicts another agent's testimony.
- `−0.4 suspicion` (clamped) if a verifiable shared task is completed.
- `+0.5 suspicion` if observed venting (almost certain).
- Time decay: suspicion drifts toward 0.5 over rounds without new evidence.

These weights are config, not constants — they will be tuned against the eval harness.

### 6.4 Contradiction detection

Stored as `ContradictionRef` objects linking two events that cannot both be true. Examples:

- Two alibis placing the same agent in different rooms at the same tick.
- An alibi placing agent X in Room R, contradicted by another agent's `SawPlayer(X, in=Room S)` at the same tick.

The detector runs on every meeting transcript update and on the local belief state when memory is updated. Detected contradictions are added to the belief state and surfaced to the LLM in subsequent turns.

### 6.5 Storage format

For MVP: serialized Pydantic models in-process; persisted alongside replay log as JSONL (one event per line). Each event has `{tick, agent_id, type, payload, provenance}`.

For scale (later phase): switch episodic store to SQLite per agent, add embeddings for semantic recall. Not needed for MVP — the events-per-game count is small enough (< 2000) to fit comfortably in memory.

### 6.6 Rendering memory for the LLM

`memory/store.py::render_for_prompt(meeting_id)` produces a token-budgeted, structured view:

```
## Your role: CREWMATE
## Tasks completed (global): 7 / 12

## Recent observations (most salient first):
- [tick 410] You discovered p2's body in MedBay.
- [tick 395] You saw p5 enter Electrical with p7.
- [tick 380] You completed wiring_admin (you were in Admin tick 375-385).

## Your current beliefs:
- p5: suspicion 0.55 (saw entering corridor near body location)
- p7: suspicion 0.30 (was with p5 but possibly bystander)
- p1: trust 0.70 (completed shared task with you tick 200)

## Open contradictions:
- p4 claims to have been in Storage tick 400-410 but p6 reports seeing them in Cafeteria tick 405.
```

Token budget is enforced — events past the budget are dropped by salience.

---

## 7. Tech Stack

| Concern               | Choice                                        | Why                                                                                                       |
| --------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Engine + agents       | **Python 3.11**                               | One language across simulation, agent code, LLM SDK, eval. Pydantic for schemas, asyncio for parallelism. |
| Schemas               | **Pydantic v2**                               | Strict typing across the firewall; structured LLM outputs.                                                |
| Backend API           | **FastAPI**                                   | Async, OpenAPI, native WebSocket, low ceremony.                                                           |
| Real-time push        | **WebSockets** via FastAPI                    | One persistent connection per spectator; broadcast tick + meeting events.                                 |
| Process orchestration | **asyncio in single process** for MVP         | Avoids premature distribution. Move to multiple workers + Redis pubsub in scale phase.                    |
| Persistence           | **PostgreSQL 16**                             | Game records, replays, eval results. JSONB for event payloads.                                            |
| Cache / pubsub        | **Redis** (only when scaling beyond 1 worker) | Not in MVP.                                                                                               |
| LLM                   | **Anthropic Claude** via the official SDK     | Sonnet for meeting reasoning, Haiku for triggered checks; tight structured-output support; honest about uncertainty. Provider is abstracted behind `LLMClient` so OpenAI / local models are pluggable. |
| Frontend              | **React + Vite + TypeScript + PixiJS**        | React for layout, PixiJS for the map canvas (cheap 2D rendering). Zustand for state.                      |
| Styling               | **Tailwind**                                  | Default for rapid UI.                                                                                     |
| Testing               | **pytest + hypothesis**                       | Property-based tests for engine determinism and observation purity.                                       |
| Type checking         | **mypy strict** on `engine/`, `observation/`, `agents/` | The firewall depends on type discipline.                                                                  |
| Lint / boundaries     | **ruff + import-linter**                      | Enforces "agents must not import engine."                                                                 |
| Packaging             | **uv** (or poetry)                            | Fast resolution, pinned lockfile.                                                                         |
| Dev infra             | **docker-compose**                            | Postgres + api + frontend up with one command.                                                            |
| Observability         | **structlog + OpenTelemetry**                 | Structured logs of ticks, LLM calls, costs; traces are free debugging.                                    |

Two stack questions deserve explicit calls:

- **Why not a JS/TS engine?** The agent + LLM + eval ecosystem is meaningfully better in Python, and the engine has no realtime-graphics requirement (rendering happens in the browser). Single-language wins.
- **Why a structured-output LLM, not function calling agents?** Function calling implies tool use mid-reasoning; here the LLM produces a complete artifact (report, vote) that the system then acts on. Structured output with a strict schema is simpler, more testable, and cheaper.

---

## 8. MVP Scope

### 8.1 In scope

- 1 fixed map: ~10 rooms, 4 tasks per room slot, 6 vents, room graph hand-authored.
- 5–7 agents per game; 1 impostor at start. Configurable.
- Movement on a room graph (no pixel-perfect collision; agents are "in" a room).
- Tasks as visit-and-wait (configurable duration, no minigames).
- Kill, vent, sabotage (lights only), report body, emergency meeting.
- Meetings: structured reports + 2 accusation rounds + structured voting.
- Memory: episodic + working + belief + meeting memo, structured (no embeddings).
- LLM: Claude Sonnet for meetings; deterministic FSM for tactical.
- Replay log persisted to Postgres; rerunnable from seed.
- Spectator UI: top-down map (PixiJS), thought stream, belief matrix, replay controls.
- Eval harness: leak test, determinism test, balance eval (win rates over N seeds).
- Headless tournament script.

### 8.2 Out of scope (post-MVP)

- Multiple maps.
- Pixel-level movement and line-of-sight ray casting.
- Mini-game tasks (just visit-and-wait).
- Multiple impostors.
- Human player.
- Voice acting / TTS.
- Distributed multi-process simulation.
- Vector / semantic memory.
- Reinforcement-learned agents.

### 8.3 Simplifications

- Visibility = "same room or adjacent room with open door." No occlusion within a room.
- Sabotage limited to "lights" (reduces visibility to same-room only). No reactor / O2.
- Meeting deadlines off in headless mode; on with generous defaults in live mode.
- One LLM provider; one model for meetings; no dynamic routing.
- Vent network is a static graph, not a polygon.

This is realistic for a solo developer over ~10–14 weeks if they ship steadily.

---

## 9. Development Roadmap

### Phase 0 — Scaffolding (week 1)

- Repo, pyproject, docker-compose, CI (lint + test + import-linter).
- `engine/world.py` + `engine/entities.py` skeletons.
- `eval/leak_test.py` skeleton (red).
- Architecture decision records (ADRs) for the three load-bearing decisions in Section 0.

**Deliverables:** runnable `pytest` (mostly empty), `docker-compose up` boots an empty FastAPI.
**Success criteria:** CI green; import-linter blocks an intentional bad import in a smoke test.

### Phase 1 — Simulation core (weeks 2–3)

- Map data, room graph, visibility rules.
- `advance_tick`, action validation, kill/report/vent/sabotage rules.
- ObservationService with the strict packet schema.
- ReplayLog write/read.
- Determinism test: seeded scripted-action sequence reproduces byte-identically.

**Deliverables:** headless game runs from a scripted action log; replays are byte-identical.
**Success criteria:** `eval/determinism_test.py` passes; `eval/leak_test.py` passes against a stub agent that records every packet field.

### Phase 2 — Tactical agents (weeks 4–5)

- Crewmate FSM, impostor FSM, A* pathing.
- AgentRuntime wires perception → memory → tactical policy.
- Belief-state scaffolding (no LLM yet; rule-based suspicion only).
- Headless games end with a winner without crashing.

**Deliverables:** 100-game tournament runs unattended; balance eval reports win rates.
**Success criteria:** crewmates and impostors each win > 20% of games (i.e., not degenerate); zero observation leaks across 100 games.

### Phase 3 — Strategic agents (weeks 6–8)

- LLM client + Claude provider + budget/cache.
- Prompt templates (versioned).
- Meeting protocol: report intake → accusation rounds → voting.
- Memory rendering (`render_for_prompt`).
- Contradiction detection.
- Output schemas for reports, statements, ballots.

**Deliverables:** full game with LLM-driven meetings completes end-to-end.
**Success criteria:** 50-game eval shows impostor win rate in [25%, 65%] band; meeting transcripts are readable; LLM cost per game ≤ $0.30 with Sonnet.

### Phase 4 — Spectator UI (weeks 9–10)

- FastAPI WebSocket broadcaster.
- React frontend: MapView, MeetingView, ThoughtStream, BeliefMatrix, ReplayControls.
- Replay scrubber.

**Deliverables:** human can watch a live game and replay any saved one.
**Success criteria:** non-technical viewer can follow a game end-to-end without reading logs.

### Phase 5 — Eval & polish (weeks 11–12)

- Meeting-quality metrics (vote correctness, accusation accuracy).
- Tournament dashboard.
- Prompt regression tests.
- Performance pass: target ≥ 1 game/min headless on a laptop.

**Deliverables:** eval dashboard with per-version metrics.
**Success criteria:** prompt change ↔ measurable metric change; can ship prompt changes with confidence.

### Phase 6 — Human player (post-MVP)

- Human seat on the WebSocket: receives observations, sends actions through the UI.
- Human meeting input: free-text statements parsed against the structured schema.
- Pacing: tick rate slows or pauses for human latency tolerance.

**Deliverables:** human can play a game alongside agents.
**Success criteria:** humans win ~ as often as a tactical-only agent (sanity check on UI).

---

## 10. Risks and Complexity Analysis

### 10.1 Hardest technical problems

1. **Information leakage.** Any path from engine state to agent prompt that bypasses ObservationService is a correctness bug that invalidates every claim about the system. Mitigation: architectural firewall + leak test + every PR that changes `ObservationPacket` requires a new leak-test fixture.

2. **Memory rendering.** Agents will reason poorly if the rendered memory is bloated, stale, or imbalanced. There is no obvious right answer to "what should this LLM see right now?" Mitigation: treat the render function as a first-class component with its own tests and golden files.

3. **Impostor LLMs deceiving plausibly.** Frontier models are tuned against deception. They may refuse, over-hedge, or write transparent lies. Mitigation: prompt framing as "you are playing a game where your role is impostor; your job is to mislead within the game's rules"; structured outputs constrain to claim formats; track impostor win rate as a key metric.

4. **Determinism with async LLM calls.** LLM responses are non-deterministic; replay cannot byte-reproduce LLM-driven games. Mitigation: replay records LLM outputs alongside actions; replay re-uses recorded outputs instead of re-calling the model. Determinism is preserved for the engine; the LLM layer is "frozen."

### 10.2 Likely failure points

- **Cost overruns** during prompt iteration. Always run iterations with `claude-haiku` first; only run Sonnet on the final candidate. Budget cap per game enforced in `llm/budget.py`.
- **Meeting deadlock**: agents all skip; impostor wins by attrition. Handle by reducing skip threshold over rounds, or by capping consecutive skipped meetings.
- **Tactical FSM bugs** that look like AI failures. Build a "scripted impostor" baseline that always wins against scripted crewmates with bad FSMs to regression-test the FSM independently of LLM behavior.
- **Prompt drift** as templates evolve. Version every prompt; tag every game with prompt version; prompt regression tests run on every PR.

### 10.3 Scaling challenges

- **Multi-process simulation** if you ever want hundreds of concurrent games (eval throughput). Means moving game state to Redis and isolating engine workers. Cleanly factored already — orchestrator is the only piece that needs to know about it.
- **Vector memory** if games get longer than ~1000 ticks or agents need cross-game memory. Replace `memory/store.py` storage layer; render function changes; no other module affected.

### 10.4 LLM limitations

- **Latency:** Sonnet meeting calls take seconds; in live mode the meeting feels slow. Acceptable for spectators; less so for human players. Mitigate by parallelizing report intake (all agents at once) and showing typing animations.
- **Hallucination:** an agent may "remember" things that did not happen. Mitigation: structured output schema requires `tick` references for observations; the validator rejects any observation referencing a tick the agent has no episodic record of.
- **Cost:** target is ~$0.20 / game with Sonnet on the planned protocol. Eval at 1000 games = $200, manageable. Tournaments are the budget pressure, not single games.

---

## 11. Evaluation & Testing Strategy

### 11.1 Engine correctness

- **Unit tests** in `tests/engine/` for every rule (kill, vent, sabotage, win conditions).
- **Property tests (hypothesis):** for any sequence of valid actions, `advance_tick` is total and never produces invalid state.
- **Determinism test:** identical seed + identical action log produces byte-identical replay. Run on every CI build.

### 11.2 Information-leakage test (the most important test)

```python
def test_no_observation_leaks_role():
    game = run_headless_game(seed=42, agent_factory=PacketRecordingAgent)
    for packet in game.audit_log.all_packets():
        for visible in packet.visible_players:
            assert "role" not in visible.dict()
            assert "kill_attribution" not in visible.dict()
```

A more general version walks the schema and asserts no field whose value should be hidden ever appears in a packet for a non-self agent. This is run against many seeds and many phase transitions.

### 11.3 Agent behavior evaluation

- **Balance eval (`eval/balance_eval.py`):** N=200 games, report impostor / crew win rates, distribution of game length, distribution of correct ejections vs wrong ejections.
- **Eval report schema (`eval/report_schema.py`):** every tournament report is
  a typed JSON object containing game outcomes, replay references, meeting
  artifacts, prompt versions, LLM cost metadata, and metric inputs. Individual
  metric modules consume this schema rather than scraping raw logs ad hoc.
- **Meeting quality (`eval/meeting_quality.py`):**
  - *Vote correctness*: when an impostor is ejected, was the eject decision driven by correct evidence (did the rationale cite a real contradiction or kill witness)?
  - *Accusation calibration*: are high-confidence accusations more often correct than low-confidence ones?
  - *Alibi-fabrication rate*: how often do impostors produce alibis that survive contradiction detection?
- **Prompt regression:** for each prompt version, run a fixed seed set and compare metric deltas. Block merge if a metric regresses by > X%.

### 11.4 Replay & debug tooling

- `scripts/render_replay.py` produces a static HTML file with: per-tick map state, every observation packet (privileged), every LLM call with prompt and response, every belief-state mutation. Indispensable for debugging "why did the agent do that?"
- The spectator UI's "thought stream" panel surfaces the same data for live games.
- Replay/eval records must include meeting transcripts, ballots,
  `MeetingResult`s, prompt template versions, LLM usage/cost metadata, and the
  structured inputs needed by Phase 5 metrics. Engine determinism remains based
  on state hashes and recorded actions; LLM-layer determinism is achieved by
  replaying recorded LLM outputs.

---

## 12. Optional Advanced Extensions

- **Multiple maps** with procedural variation. Map authoring as YAML.
- **Agent personalities** — prompt-injected traits (cautious / aggressive / talkative) that bias tactical and strategic policies. Personality vector becomes a knob for tournament diversity.
- **Reinforcement learning for tactical policies.** The strategic LLM stays put; the FSM is replaced with a small neural policy trained against scripted opponents. Self-play tournaments become training data.
- **Tournament simulator** — run thousands of games across personalities, prompts, model versions. Output: an ELO-like ranking and a leaderboard. Strong portfolio piece.
- **Analytics dashboard** — Grafana on top of Postgres: win rates, cost per game, meeting-length distributions, contradiction rates. Drives prompt and rule iteration.
- **Adversarial prompt-injection probes.** Test what happens when an impostor agent embeds prompt-injection attempts in its meeting statements. Treat prompts as untrusted input; harden parsing.
- **Cross-game memory** — agents play a season, remember reputations. Belief state seeds carry between games. Excellent excuse to add the vector memory layer.
- **Mixed-model lobbies** — different agents use different models (Claude vs OpenAI vs local). Comparative reasoning quality shows up directly in win rates.
- **Voice + TTS** for meeting statements. Spectator UX upgrade; not a research add.
- **Human-in-the-loop annotation tool** for labeling "good" and "bad" reasoning to bootstrap a fine-tuning dataset later.

---

## Appendix A — Key Schemas (sketch)

```python
class Action(BaseModel):
    actor: PlayerId
    type: Literal["move","do_task","kill","vent","report","emergency","sabotage","wait"]
    payload: dict   # validated per type

class ObservationPacket(BaseModel):
    tick: int
    agent_id: PlayerId
    self_state: SelfView
    visible_players: list[PlayerView]
    visible_bodies: list[BodyView]
    audible_events: list[AudibleEvent]
    global_state: GlobalView

class ReportDocument(BaseModel):
    agent_id: PlayerId
    tick: int
    observations: list[ObservationClaim]   # each with tick reference
    claims: list[Claim]                    # alibi | accusation | corroboration
    free_text: str

class VoteBallot(BaseModel):
    voter: PlayerId
    target: PlayerId | Literal["SKIP"]
    confidence: float
    primary_reason_id: str | None
    rationale_text: str
```

## Appendix B — Open questions

- What is the right meeting deadline pacing for live spectator UX once Sonnet latency is measured end-to-end?
- Should the rule-based FSMs themselves be replaceable by small LLM calls (e.g., Haiku) for richer tactical behavior, given the cost budget?
- For multi-impostor games, do impostors get a private channel, or must they coordinate purely through public play? 
- Should belief weights (Section 6.3) be learned from replays rather than hand-tuned?

These are flagged for resolution before Phase 3.
