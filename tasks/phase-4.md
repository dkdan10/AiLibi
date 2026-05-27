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
- **Mid-phase DTO audit, no real-provider analog.** Double-tool audit
  (Claude + Codex) with a separate reconciliation pass. The substrate
  gates five downstream PRs; a second opinion is worth the cost.
  Focused on DTO/leak coverage after the substrate exists. The
  phase-closing acceptance gate is a manual UX session (a non-
  technical viewer follows a replay end-to-end without reading logs).

## Parallelism
4.1 → 4.2 → 4.3 → 4.4 in series. Mid-phase DTO audit runs after 4.4.
Then 4.4.5, 4.5, 4.6, 4.7, 4.8 can run in parallel once the audit
confirms the substrate is leak-free.

## Tasks

### Task 4.1 — FastAPI app skeleton and spectator DTO inventory
**Branch:** `phase-4-fastapi-app-skeleton`
**Depends on:** Phase 3 merged
**Section refs:** DESIGN.md §7, DESIGN.md §1.3, DESIGN.md §11.4
**Complexity:** Medium

Establish the API substrate that every Phase 4 frontend task consumes:
a FastAPI app skeleton, the concrete sanitized DTO inventory in
`api/schemas.py`, route registration with placeholder handlers, and
leak tests that pin down which fields are intentionally exposed. The
DTO design IS the deliverable; routes return `501 Not Implemented` and
get their bodies in 4.2. This split keeps the design lift isolated
from the implementation lift.

**Spectator privilege model.** The replay viewer is a *post-game*
privileged spectator (the analog of a "GM view" in tabletop). Role,
kill attribution, vent network, and impostor-only state are
intentionally exposed because that's what makes a replay watchable.
The firewall (DESIGN.md §1.3) still applies to *agents*; spectator
DTOs are a separate surface. The leak test's purpose is NOT to redact
role — it's to assert that every DTO field is *intentional* and to
prevent accidentally embedding `WorldState`, raw `ReplayEntry`s, or
observation-firewall internals (which would couple frontend to engine
shape and re-introduce leakage paths via copy-paste).

**Replay seed recovery.** Replays are stored as JSONL files whose
filename encodes the seed (`replay-seed-{N}.jsonl`) and whose
`game_id` field is `headless-seed-{N}` (per
[orchestrator/game.py:874](orchestrator/game.py#L874)). Per-tick agent
positions are NOT persisted in the JSONL — only `state_hash` is, plus
the action stream. To produce per-tick position DTOs, the eventual
replay loader (4.2) will re-seed via `seed_initial_state(seed=N)` and
re-apply actions through `advance_tick`. This is a read-only engine
usage, not an engine modification, and is consistent with the "no
engine touches in Phase 4" scope guarantee — we re-use the determinism
contract, we don't change it.

**Out of scope** (explicit decisions deferred):

- **Endpoint bodies.** Task 4.1 registers routes and returns `501`.
  Task 4.2 wires the replay loader and returns real payloads. Splitting
  these keeps DTO review independent from loader implementation review.
- **Per-tick memory + suspicion snapshots.** The replay does not
  capture per-tick memory state; memory is reconstructed on-the-fly
  when `render_for_prompt` runs. The captured `LLMCallRecord.prompt`
  text holds rendered memory only at meeting boundaries. MVP DTOs
  expose `AgentMemoryView` ONLY at meeting boundaries (parsed from or
  paired with the meeting's LLM call records). Between-meeting memory
  is not exposed. Document this constraint in `## Decisions` so the
  ThoughtStream task (4.6) doesn't assume otherwise.
- **WebSocket / live game.** Deferred to Phase 5+ per phase scope.
- **Pagination / cursor APIs.** MVP returns all replay metadata in one
  shot. Pagination lands when there are enough replays for it to matter.
- **OpenAPI schema export tooling.** FastAPI emits OpenAPI by default;
  whether the frontend (4.3) consumes it via `openapi-typescript` or
  hand-authored types is the 4.3 implementing agent's call.

**Files in scope:**
- api/__init__.py
- api/main.py
- api/schemas.py
- api/routes/__init__.py
- api/routes/replays.py
- api/routes/eval.py
- tests/api/__init__.py
- tests/api/test_schemas.py
- tests/api/test_routes.py
- tests/api/test_leak.py

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- frontend/
- api/ws.py (deferred — no WebSocket in MVP)
- api/routes/games.py (live game streaming deferred)
- api/replay_loader.py (deferred to 4.2)
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
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/test_firewall.py

**Definition of done:**
- [ ] **FastAPI app skeleton.** `api/main.py` exposes a `create_app() -> FastAPI` factory plus a module-level `app = create_app()`. App registers `api/routes/replays.py` under `/replays` and `api/routes/eval.py` under `/eval`. App boots cleanly: `uv run uvicorn api.main:app --port 8000` returns 200 on `GET /` (return a minimal `{"service": "ailibi-api"}` response) and 404 on unknown paths. No CORS middleware needed for MVP (frontend served via Vite dev proxy in 4.3).
- [ ] **DTO inventory.** `api/schemas.py` defines every DTO listed in the Implementation hint below as a frozen Pydantic v2 model (`model_config = ConfigDict(frozen=True, extra="forbid")`). Each DTO carries a docstring naming its source (which engine/meetings/orchestrator type it shadows) and explicitly listing fields that exist in the source but are deliberately excluded. Discriminated unions use `Field(discriminator="type")` mirroring `meetings.schemas` patterns.
- [ ] **Route registration with placeholders.** `api/routes/replays.py` and `api/routes/eval.py` declare each endpoint with its response_model set to the appropriate DTO. Handler bodies raise `HTTPException(status_code=501, detail="Not implemented in 4.1; lands in 4.2")`. The endpoint signatures are final — 4.2 fills bodies without changing signatures.
- [ ] **Endpoint inventory (registered with 501 bodies):**
  - `GET /replays` → `list[ReplayMetadataView]`
  - `GET /replays/{game_id}` → `ReplayView`
  - `GET /replays/{game_id}/ticks/{tick}` → `TickView`
  - `GET /replays/{game_id}/meetings/{meeting_id}` → `MeetingView`
  - `GET /replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}` → `AgentMemoryView`
  - `GET /eval/cost-summary` → `EvalCostSummaryView`
- [ ] **Leak tests in `tests/api/test_leak.py`.** Static-import-based tests assert:
  - No DTO in `api/schemas.py` imports from `engine.*`, `observation.*`, or `orchestrator.*` (use `import_linter`-style assertions or a simple `inspect.getsource(api.schemas) | grep`).
  - No DTO has a field typed as `WorldState`, `PlayerState`, `BodyState`, `TaskState`, `SabotageState`, `ReplayEntry`, `MeetingReplayEntry`, `LLMCallRecord`, `MeetingResult`, `MeetingTrigger`, `Action`, or any other internal type that wasn't explicitly opted-in to the DTO surface.
  - The expected DTO inventory matches the actual `__all__` in `api/schemas.py` — i.e. someone adding a DTO has to update `__all__` AND a paired exposure-list fixture in the test, making accidental leakage visible in code review.
- [ ] **Round-trip serialization tests in `tests/api/test_schemas.py`.** For each top-level DTO (`ReplayView`, `TickView`, `MeetingView`, `AgentMemoryView`, `EvalCostSummaryView`, `ReplayMetadataView`), construct a fixture instance via direct constructor, `model_dump_json` it, `model_validate_json` it back, and assert equality. Discriminated unions need at least one fixture per variant.
- [ ] **Route registration tests in `tests/api/test_routes.py`.** Using FastAPI's `TestClient`, assert each endpoint above is registered (returns 501, not 404). Assert the OpenAPI schema (`GET /openapi.json`) reflects the documented DTOs (smoke-level: `ReplayMetadataView` appears in the components list, etc.).
- [ ] **API remains a thin adapter.** `api/routes/*.py` files contain ONLY route declarations + 501 placeholders. No business logic, no imports from `engine/`, `observation/`, or `orchestrator/`. (4.2 will need orchestrator import for the loader; that's fine because the loader lives in `api/replay_loader.py`, not in `api/routes/`.)
- [ ] **`Public types introduced` are documented** in the PR description AND in `## Decisions`.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes. (`api/` is not in the strict list yet; add it post-Phase-4 if discipline warrants.)
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

The DTO inventory below is the load-bearing artifact. Implement these exactly; do not invent additional fields. Every field maps to a real engine / meetings / replay source and exists because a downstream Phase 4 component (4.4–4.8) needs it. Fields deliberately excluded are listed under "Excludes" — the leak test enforces these.

**Map + roster DTOs** (loaded once, shared across all replays):

```python
class PositionView(BaseModel):
    x: float
    y: float

class SizeView(BaseModel):
    width: float
    height: float

class RoomView(BaseModel):
    # Shadows engine.world.Room
    id: str
    name: str
    position: PositionView
    size: SizeView
    # Excludes: visibility_defaults, internal task slot indices

class VentView(BaseModel):
    # Shadows engine.world.Vent
    id: str
    room_id: str
    connected_room_ids: tuple[str, ...]
    # Excludes: nothing — Vent is already minimal

class EdgeView(BaseModel):
    # Shadows engine.world.Edge (room adjacency for door rendering)
    from_room_id: str
    to_room_id: str
    is_door: bool

class MapLayoutView(BaseModel):
    rooms: tuple[RoomView, ...]
    vents: tuple[VentView, ...]
    edges: tuple[EdgeView, ...]
    # Excludes: tasks (task definitions are out of scope for the map view;
    # task completion is tracked in TickView/AgentMemoryView instead)

class PlayerView(BaseModel):
    # Shadows engine.entities.PlayerState (the static identity slice)
    agent_id: str
    display_name: str
    role: Literal["CREWMATE", "IMPOSTOR"]  # exposed: privileged spectator
    color: str  # hex color for rendering, assigned deterministically from agent_id
    # Excludes: dynamic state (position, alive, cooldowns) — those go in AgentTickStateView
```

**Per-tick state DTOs**:

```python
class AgentTickStateView(BaseModel):
    # Shadows the dynamic slice of engine.entities.PlayerState at one tick
    agent_id: str
    room_id: str | None  # None if dead (body has its own state via TickEventView)
    is_alive: bool
    is_venting: bool  # impostor-only state, ok in privileged replay
    task_progress: float | None  # None for impostors; 0.0-1.0 for crewmates
    current_action: Literal["IDLE", "MOVING", "TASK", "KILL", "VENT", "REPORT", "SABOTAGE"]
    # Excludes: target_room, planned_path, kill_cooldown_ticks, vent_cooldown_ticks

class KillEventView(BaseModel):
    type: Literal["kill"]
    tick: int
    killer_id: str
    victim_id: str
    room_id: str

class ReportBodyEventView(BaseModel):
    type: Literal["report_body"]
    tick: int
    reporter_id: str
    body_of: str
    room_id: str

class SabotageEventView(BaseModel):
    type: Literal["sabotage"]
    tick: int
    kind: Literal["lights"]  # MVP scope — DESIGN.md §8.3
    room_id: str | None  # None for global sabotage
    actor_id: str  # always the impostor in MVP

class TaskCompletedEventView(BaseModel):
    type: Literal["task_completed"]
    tick: int
    agent_id: str
    task_id: str
    room_id: str

class MeetingTriggeredEventView(BaseModel):
    type: Literal["meeting_triggered"]
    tick: int
    meeting_id: str
    triggered_by: str
    trigger_kind: Literal["body", "emergency"]

TickEventView = Annotated[
    KillEventView | ReportBodyEventView | SabotageEventView
    | TaskCompletedEventView | MeetingTriggeredEventView,
    Field(discriminator="type"),
]

class TickView(BaseModel):
    tick: int
    agent_states: tuple[AgentTickStateView, ...]
    events: tuple[TickEventView, ...]
    sabotage_active: tuple[str, ...]  # active sabotage kinds at this tick
    tasks_completed_total: int
    tasks_required_total: int
    # Excludes: state_hash, raw actions, raw ReplayEntry
```

**Meeting DTOs** (mirrors `meetings/schemas.py` with deliberate field re-exposure):

```python
class SawPlayerView(BaseModel):
    type: Literal["saw_player"]
    tick: int
    subject: str
    room: str
    co_present: tuple[str, ...]

class CompletedTaskObsView(BaseModel):
    type: Literal["completed_task"]
    tick: int
    task_id: str
    room: str

class FoundBodyObsView(BaseModel):
    type: Literal["found_body"]
    tick: int
    body_of: str
    room: str

ObservationClaimView = Annotated[
    SawPlayerView | CompletedTaskObsView | FoundBodyObsView,
    Field(discriminator="type"),
]

class AlibiClaimView(BaseModel):
    type: Literal["alibi"]
    subject: str
    from_tick: int
    to_tick: int
    room: str
    evidence: tuple[str, ...]

class AccusationClaimView(BaseModel):
    type: Literal["accusation"]
    against: str
    confidence: float
    reason: str

class CorroborationClaimView(BaseModel):
    type: Literal["corroboration"]
    supports: str
    on_tick: int
    reason: str

StatementClaimView = Annotated[
    AlibiClaimView | AccusationClaimView | CorroborationClaimView,
    Field(discriminator="type"),
]

class ReportView(BaseModel):
    agent_id: str
    tick: int
    observations: tuple[ObservationClaimView, ...]
    claims: tuple[StatementClaimView, ...]
    free_text: str

class StatementView(BaseModel):
    statement_id: str
    speaker: str
    tick: int
    round_index: int
    target: str | None
    claims: tuple[StatementClaimView, ...]
    free_text: str

class ContradictionView(BaseModel):
    contradiction_id: str
    kind: Literal["alibi_conflict", "alibi_vs_sighting"]
    event_a_id: str
    event_b_id: str
    subjects: tuple[str, ...]
    description: str

class BallotView(BaseModel):
    voter: str
    target: str  # "SKIP" or a player id; flatten Literal["SKIP"] to str for JSON simplicity
    confidence: float
    primary_reason_id: str | None
    considered_alternatives: tuple[str, ...]
    rationale_text: str

class LLMCallView(BaseModel):
    # Shadows orchestrator.replay.LLMCallRecord
    call_kind: Literal["meeting", "trigger"]
    model: str
    prompt_template_id: str  # derived from prompt_versions lookup
    prompt_text: str
    response_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float

class MeetingView(BaseModel):
    # Shadows orchestrator.replay.MeetingReplayEntry
    meeting_id: str
    tick: int
    triggered_by: str
    trigger_kind: Literal["body", "emergency"]  # derived from MeetingResult.trigger
    outcome: Literal["EJECTED", "SKIPPED"]
    ejected_player_id: str | None
    reports: tuple[ReportView, ...]
    statements: tuple[StatementView, ...]
    ballots: tuple[BallotView, ...]
    contradictions: tuple[ContradictionView, ...]
    llm_calls: tuple[LLMCallView, ...]
    prompt_versions: Mapping[str, str]
    total_cost_usd: float  # sum of llm_calls[*].cost_usd
    # Excludes: state_hash_before, state_hash_after (engine-internal)
```

**Memory + suspicion DTOs** (meeting-boundary only for MVP):

```python
class BeliefEntryView(BaseModel):
    subject: str
    suspicion: float
    confidence: float
    last_updated_tick: int

class AgentMemoryView(BaseModel):
    # Shadows agents.memory.store output at a meeting boundary
    agent_id: str
    tick: int  # the meeting tick this snapshot is paired with
    role: Literal["CREWMATE", "IMPOSTOR"]
    tasks_completed: int
    tasks_assigned: int
    observations: tuple[ObservationClaimView, ...]  # salience-ordered
    beliefs: tuple[BeliefEntryView, ...]
    open_contradictions: tuple[ContradictionView, ...]
    rendered_memory_text: str  # the raw render_for_prompt output, for ThoughtStream
    # Excludes: raw memory-store internals, decay timestamps

class SuspicionEntryView(BaseModel):
    observer: str
    subject: str
    suspicion: float

class SuspicionGraphView(BaseModel):
    tick: int
    entries: tuple[SuspicionEntryView, ...]
```

**Replay-level DTOs**:

```python
class ReplayMetadataView(BaseModel):
    # Shadows orchestrator.replay.{GameEndReplayEntry, compute_cost_usd output}
    game_id: str
    seed: int  # parsed from game_id; documented as derived not authoritative
    total_ticks: int
    winner: Literal["CREWMATES", "IMPOSTORS"] | None  # None for partial/unfinished
    winner_reason: str | None
    meeting_count: int
    total_cost_usd: float
    prompt_versions: Mapping[str, str]  # merged across meetings
    created_at: str | None  # ISO-8601 from file mtime; None if not derivable

class FailedCallView(BaseModel):
    # Shadows orchestrator.replay.FailedCallReplayEntry
    meeting_id: str
    tick: int
    model: str
    cost_usd: float
    error_type: str
    error_message: str  # truncated to first 200 chars at DTO layer
    # Excludes: raw_response (1KB blob), prompt_length

class ReplayView(BaseModel):
    metadata: ReplayMetadataView
    map: MapLayoutView
    players: tuple[PlayerView, ...]
    ticks: tuple[TickView, ...]  # one per tick from 0 to total_ticks
    meetings: tuple[MeetingView, ...]
    failed_calls: tuple[FailedCallView, ...]
    # Excludes: per-tick agent memory (only available via separate endpoint at
    # meeting boundaries), state hashes, raw replay entries
```

**Eval DTO** (single endpoint for now; expand in Phase 5):

```python
class EvalCostSummaryView(BaseModel):
    total_replays: int
    total_cost_usd: float
    mean_cost_per_replay: float
    max_cost_per_replay: float
    decisive_split: dict[str, float]  # {"CREWMATES": 0.62, "IMPOSTORS": 0.38}
```

For the leak test, the cleanest pattern is a paired fixture list:

```python
# tests/api/test_leak.py — illustrative
EXPECTED_DTOS: Final[frozenset[str]] = frozenset({
    "PositionView", "SizeView", "RoomView", "VentView", "EdgeView",
    "MapLayoutView", "PlayerView",
    "AgentTickStateView", "KillEventView", "ReportBodyEventView",
    "SabotageEventView", "TaskCompletedEventView", "MeetingTriggeredEventView",
    "TickView",
    "SawPlayerView", "CompletedTaskObsView", "FoundBodyObsView",
    "AlibiClaimView", "AccusationClaimView", "CorroborationClaimView",
    "ReportView", "StatementView", "ContradictionView", "BallotView",
    "LLMCallView", "MeetingView",
    "BeliefEntryView", "AgentMemoryView",
    "SuspicionEntryView", "SuspicionGraphView",
    "ReplayMetadataView", "FailedCallView", "ReplayView",
    "EvalCostSummaryView",
})

FORBIDDEN_TYPES: Final[frozenset[str]] = frozenset({
    "WorldState", "PlayerState", "BodyState", "TaskState", "SabotageState",
    "ReplayEntry", "MeetingReplayEntry", "LLMCallRecord", "GameEndReplayEntry",
    "FailedCallReplayEntry", "MeetingResult", "MeetingTrigger", "Action",
    "Statement", "ReportDocument", "VoteBallot", "ContradictionRef",
    "AlibiClaim", "AccusationClaim", "CorroborationClaim",
})

def test_dto_inventory_matches_expected() -> None:
    actual = frozenset(api.schemas.__all__)
    assert actual == EXPECTED_DTOS, (
        "Adding/removing a DTO requires updating EXPECTED_DTOS in this test "
        "AND documenting the change in the PR description's Public types "
        "introduced section."
    )

def test_no_forbidden_types_in_schemas_source() -> None:
    source = inspect.getsource(api.schemas)
    for forbidden in FORBIDDEN_TYPES:
        assert forbidden not in source, (
            f"DTO module references {forbidden!r}, which is an engine/"
            f"orchestrator-internal type. DTOs must shadow these, not embed them."
        )
```

The pattern surfaces accidental leakage on any PR that touches `api/schemas.py`: adding a new DTO that imports `WorldState` makes both tests fail; renaming an exposed DTO without updating the test makes the inventory test fail. CI catches it.

Route stub pattern:

```python
# api/routes/replays.py — illustrative
@router.get("/", response_model=list[ReplayMetadataView])
def list_replays() -> list[ReplayMetadataView]:
    raise HTTPException(
        status_code=501,
        detail="Not implemented in 4.1; lands in 4.2",
    )

@router.get("/{game_id}", response_model=ReplayView)
def get_replay(game_id: str) -> ReplayView:
    raise HTTPException(status_code=501, detail="Not implemented in 4.1; lands in 4.2")
```

The signatures are the contract; 4.2 swaps the body for the loader call.

**Public types introduced:**

- `api.schemas.PositionView`
- `api.schemas.SizeView`
- `api.schemas.RoomView`
- `api.schemas.VentView`
- `api.schemas.EdgeView`
- `api.schemas.MapLayoutView`
- `api.schemas.PlayerView`
- `api.schemas.AgentTickStateView`
- `api.schemas.KillEventView`
- `api.schemas.ReportBodyEventView`
- `api.schemas.SabotageEventView`
- `api.schemas.TaskCompletedEventView`
- `api.schemas.MeetingTriggeredEventView`
- `api.schemas.TickEventView`
- `api.schemas.TickView`
- `api.schemas.SawPlayerView`
- `api.schemas.CompletedTaskObsView`
- `api.schemas.FoundBodyObsView`
- `api.schemas.ObservationClaimView`
- `api.schemas.AlibiClaimView`
- `api.schemas.AccusationClaimView`
- `api.schemas.CorroborationClaimView`
- `api.schemas.StatementClaimView`
- `api.schemas.ReportView`
- `api.schemas.StatementView`
- `api.schemas.ContradictionView`
- `api.schemas.BallotView`
- `api.schemas.LLMCallView`
- `api.schemas.MeetingView`
- `api.schemas.BeliefEntryView`
- `api.schemas.AgentMemoryView`
- `api.schemas.SuspicionEntryView`
- `api.schemas.SuspicionGraphView`
- `api.schemas.ReplayMetadataView`
- `api.schemas.FailedCallView`
- `api.schemas.ReplayView`
- `api.schemas.EvalCostSummaryView`
- `api.main.create_app`
- `api.main.app`

**Integration risk:**

This task is design-heavy and implementation-light. The risk is in
getting the DTO contract right; once written, 4.2–4.8 build against it.

- **DTO drift between Pydantic and TypeScript.** The frontend (4.3)
  consumes these via either hand-authored types or generated types
  from `openapi-typescript`. Either way, a DTO field rename here means
  a frontend refactor. Bias toward stable field names from the start;
  don't pre-emptively rename engine field names "for clarity" in DTOs.
- **Privilege model surfaces in `role` and `is_venting`.** These
  fields are intentionally exposed. The leak test is the audit trail:
  a PR that adds a new DTO must reckon with whether each field is
  intentional. Reviewer checklist: every field has a stated source and
  exclusion list.
- **Per-tick position reconstruction is 4.2's responsibility.** This
  task only ships DTOs and route stubs. The "how do we get per-tick
  positions from the JSONL" architecture decision is documented here
  (engine playback) but implemented in 4.2.
- **`tuple[X, ...]` vs `list[X]` JSON serialization.** Pydantic v2
  serializes `tuple` as JSON array, same as `list`. Use `tuple` in DTO
  declarations for immutability matching the engine/meetings pattern;
  frontend sees arrays either way.
- **`Mapping[str, str]` for prompt_versions.** Use `Mapping` not
  `dict` for the field type to signal read-only intent; Pydantic
  resolves to `dict` at runtime. Same pattern as
  `MeetingReplayEntry.prompt_versions`.
- **OpenAPI emission.** FastAPI emits OpenAPI from response_model
  annotations. Use `response_model=` on every route declaration so the
  generated spec is accurate.
- **Mid-phase audit hook.** After 4.4 lands, the DTO audit will
  re-walk this inventory against actual usage in 4.2/4.4. Findings
  there land as 4.4.6 / 4.4.7 / etc. — repair tasks before fan-out.
- **No CI cost.** Static gates only. No real-provider tests.

**Ready-to-paste prompt:** `agent_prompts/task-4-1-fastapi-app-skeleton.md`

### Task 4.2 — Replay loader + endpoint implementation
**Branch:** `phase-4-replay-endpoint`
**Depends on:** 4.1 merged
**Section refs:** DESIGN.md §7, DESIGN.md §11.4, DESIGN.md §1.3
**Complexity:** Medium

Implement the replay loader and swap in real route handlers for the
DTOs defined in 4.1. The endpoint signatures from 4.1 are final; this
task only changes handler bodies and adds `api/replay_loader.py`. This
is the substrate the entire frontend (4.3–4.8) consumes.

**Engine-playback architecture.** Replays store `state_hash` per tick
but not positions ([orchestrator/replay.py:74-84](orchestrator/replay.py#L74)).
To produce per-tick `AgentTickStateView` DTOs the loader re-runs the
engine against the recorded action stream:

1. Read the first `ReplayEntry` from the JSONL; extract
   `game_id = "headless-seed-{N}"`; parse N.
2. `state = seed_initial_state(seed=N, map=load_canonical_map(), ...)`
   — same call shape as
   [orchestrator/game.py:674](orchestrator/game.py#L674).
3. For each `ReplayEntry` in order: deserialize the action list,
   call `state, events = advance_tick(state, actions, ...)`, snapshot
   `state` + `events` into a `TickView`.
4. After every meeting `ReplayEntry` (signalled by an interleaved
   `MeetingReplayEntry`), apply the meeting outcome to `state` —
   mirror the orchestrator pattern at
   [orchestrator/game.py](orchestrator/game.py#L770-L820)'s
   `_apply_meeting_result` (read-only re-use; do NOT modify that
   helper).
5. Verify the `state_hash` after each tick matches the recorded
   `ReplayEntry.state_hash`. Mismatch is a hard error (the determinism
   invariant is broken; surface as a 500 with the mismatching tick in
   the error body).

This is a read-only engine touch — the loader IMPORTS from `engine/`
and `orchestrator/` but does not MODIFY any of their code. Consistent
with the "no engine touches in Phase 4" scope guarantee, which is
about behavior change, not import boundaries.

**Loader caching.** Loading + replaying a 1000-tick game is non-
trivial CPU (~50-200 ms per game in headless tests). The loader
keeps an in-memory LRU cache keyed by `game_id`; default `maxsize=16`.
Invalidation happens on process restart (replays are immutable once
written). No cross-process cache (Redis) — that's Phase 5.

**Replay directory discovery.** A configured `replay_dir` path
(default: `$AILIBI_REPLAY_DIR` if set, else `./replays/` relative to
process cwd) is scanned for `replay-seed-*.jsonl` files. The pattern
is hard-coded — any file not matching is ignored. The endpoint never
recursively descends; subdirectories are out of scope for MVP.

**Out of scope** (explicit decisions deferred):

- **Pagination on `/replays`.** MVP returns all metadata in one shot.
  Add pagination when the replay count makes it matter (Phase 5+).
- **Replay deletion / management endpoints.** Read-only API. Replays
  are managed via filesystem; the API does not mutate.
- **Per-tick memory reconstruction between meetings.** Per the 4.1
  decision, `AgentMemoryView` is only available at meeting boundaries
  (where the `LLMCallRecord.prompt` text captures rendered memory).
  Between-meeting memory is NOT exposed — the endpoint returns 404
  for memory requests at non-meeting ticks. Document this in API docs.
- **Live game streaming via WebSocket.** Deferred phase-wide.
- **Persistent on-disk cache.** In-memory LRU only. Restart re-loads
  on first request.

**Files in scope:**
- api/replay_loader.py
- api/routes/replays.py
- api/routes/eval.py
- api/main.py
- tests/api/test_replay_loader.py
- tests/api/test_replays.py
- tests/api/test_eval.py
- tests/api/fixtures/__init__.py
- tests/api/fixtures/sample_replay.py

**Files NOT in scope:**
- engine/ (imported read-only; not modified)
- agents/
- llm/
- meetings/
- observation/
- orchestrator/ (imported read-only; not modified)
- frontend/
- api/schemas.py (DTOs are frozen at 4.1)
- api/ws.py
- api/routes/games.py
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
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/api/test_schemas.py (frozen at 4.1)
- tests/api/test_routes.py (frozen at 4.1; superseded by test_replays for body coverage)
- tests/api/test_leak.py (frozen at 4.1)
- tests/test_firewall.py

**Definition of done:**
- [ ] **`api/replay_loader.py` exposes `ReplayLoader`** with `list_replays() -> list[ReplayMetadataView]` and `load_replay(game_id: str) -> ReplayView`. Constructor takes `replay_dir: Path` and `map: Map`. The loader is the single source of truth for engine-playback; routes import it, never compose engine APIs directly.
- [ ] **Engine playback reproduces state byte-identically.** Every tick's reconstructed `state_hash` matches the recorded `ReplayEntry.state_hash`. Mismatch raises `ReplayStateMismatchError` (new exception in `api/replay_loader.py`) which routes catch and surface as `500 {"detail": "...", "tick": N, "game_id": "..."}`.
- [ ] **`GET /replays`** scans the configured replay directory and returns `list[ReplayMetadataView]`. Empty directory returns `[]`. Files not matching `replay-seed-*.jsonl` are silently skipped. Sorted by `seed` ascending.
- [ ] **`GET /replays/{game_id}`** returns the full `ReplayView`. Unknown `game_id` returns `404 {"detail": "replay not found: {game_id}"}`. Caches the result via the LRU cache.
- [ ] **`GET /replays/{game_id}/ticks/{tick}`** returns the `TickView` for one tick. Reuses the cached `ReplayView` if present; otherwise loads first. Tick out of range returns `404`.
- [ ] **`GET /replays/{game_id}/meetings/{meeting_id}`** returns one `MeetingView` derived from the corresponding `MeetingReplayEntry`. Unknown meeting returns `404`.
- [ ] **`GET /replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}`** returns the `AgentMemoryView` for one agent at one meeting boundary. The view is constructed from (a) the agent's role from the seeded roster, (b) the agent's `rendered_memory` extracted from that meeting's `LLMCallRecord.prompt` text, and (c) per-agent belief/contradiction state at that tick. Document the extraction strategy in `## Decisions` — depending on how cleanly the rendered memory parses, the implementing agent may need to either string-extract or re-render via `agents.memory.store.render_for_prompt` against the reconstructed engine state. Unknown agent returns `404`.
- [ ] **`GET /eval/cost-summary`** returns `EvalCostSummaryView` aggregated across every replay in the directory. Empty directory returns zero/null values, no crash.
- [ ] **Partial-replay handling.** Replays with no `GameEndReplayEntry` (per Task 3.19 the eval ran 27/50 before crashing; those 23 partial files are real artifacts) surface `winner=None` in `ReplayMetadataView` cleanly. The tick timeline is still readable up to the last recorded tick.
- [ ] **LRU cache.** `api/replay_loader.py` uses `functools.lru_cache` (or equivalent) with `maxsize=16` on `load_replay`. Cache is per-process. Cache hit shortcuts engine playback. Add a `clear_cache()` method called by a test fixture to keep tests hermetic.
- [ ] **Configuration via env.** `api/main.py` reads `AILIBI_REPLAY_DIR` env at startup; falls back to `./replays/`. Document the env var in `.env.example` (the only `.env.example` edit allowed by this task). The `ReplayLoader` is constructed once at app startup and injected via a FastAPI dependency.
- [ ] **No engine modification.** `engine/` and `orchestrator/` imports are read-only. `uv run lint-imports` still passes. The new module `api/replay_loader.py` IS allowed to import from `engine/` and `orchestrator/`; document this exception in `## Decisions` (the firewall forbids `agents/`, `llm/`, `meetings/` from importing `engine/`; `api/` is a privileged spectator surface, not part of the firewall).
- [ ] **Unit tests for `ReplayLoader`.** Construct a fixture JSONL (small 3-tick game with one meeting, written via `ReplayLog` in a test helper); load it; assert the resulting `ReplayView`'s `ticks`, `meetings`, and `metadata.winner` match expectations.
- [ ] **State-hash mismatch test.** Construct a JSONL where the recorded `state_hash` is wrong; assert `ReplayStateMismatchError` is raised with the bad tick number.
- [ ] **Partial-replay test.** Construct a JSONL with no `GameEndReplayEntry`; assert the loader returns `winner=None` and the tick timeline is intact up to the last recorded tick.
- [ ] **Endpoint tests via `TestClient`.** Cover all six endpoints + the 404/500 error paths.
- [ ] **Leak tests still pass.** The 4.1 leak tests run against the populated routes; no new DTO types leak through. The existing `tests/api/test_leak.py` must pass without modification.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/`. `uv run lint-imports` passes (it should already allow `api/` → `engine/` since `api/` isn't in the deny-list; verify in `pyproject.toml` import-linter config).
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

The loader's high-level shape (illustrative; pick exact names consistent with the module style):

```python
# api/replay_loader.py — illustrative
from functools import lru_cache
from pathlib import Path

from engine.world import Map, load_canonical_map
from orchestrator.game import _apply_meeting_result  # may need to be made public
from orchestrator.replay import (
    read_replay_entries, read_meeting_entries, read_game_outcome,
    read_failed_call_entries, compute_cost_usd,
)
from orchestrator.seeder import seed_initial_state
from engine.advance import advance_tick  # adjust import to actual location

from api.schemas import (
    ReplayMetadataView, ReplayView, TickView, MeetingView, AgentMemoryView,
    ...
)


class ReplayStateMismatchError(RuntimeError):
    """Raised when reconstructed state_hash diverges from the recorded one.
    Indicates a replay-determinism break; surfaced as HTTP 500."""
    def __init__(self, *, game_id: str, tick: int, expected: str, actual: str):
        ...


class ReplayLoader:
    def __init__(self, replay_dir: Path, *, map: Map | None = None) -> None:
        self._replay_dir = replay_dir
        self._map = map if map is not None else load_canonical_map()

    def list_replays(self) -> list[ReplayMetadataView]:
        out: list[ReplayMetadataView] = []
        for jsonl in sorted(self._replay_dir.glob("replay-seed-*.jsonl")):
            seed = self._parse_seed_from_filename(jsonl.name)
            out.append(self._metadata_view(jsonl, seed))
        return out

    @lru_cache(maxsize=16)
    def load_replay(self, game_id: str) -> ReplayView:
        path = self._resolve_path(game_id)
        if path is None:
            raise FileNotFoundError(game_id)
        seed = self._parse_seed_from_game_id(game_id)
        state = seed_initial_state(seed=seed, map=self._map)
        replay_entries = read_replay_entries(path)
        meeting_entries = read_meeting_entries(path)
        meeting_by_tick = {m.tick: m for m in meeting_entries}

        ticks: list[TickView] = []
        for entry in replay_entries:
            actions = self._deserialize_actions(entry.actions)
            state, events = advance_tick(state, actions)
            if entry.tick in meeting_by_tick:
                state = _apply_meeting_result(state, meeting_by_tick[entry.tick])
            self._assert_hash(entry, state)
            ticks.append(self._tick_view(entry.tick, state, events))

        return ReplayView(
            metadata=self._metadata_view(path, seed),
            map=self._map_view(),
            players=self._players_view(state),
            ticks=tuple(ticks),
            meetings=tuple(self._meeting_view(m) for m in meeting_entries),
            failed_calls=tuple(
                self._failed_call_view(f) for f in read_failed_call_entries(path)
            ),
        )

    # ... private helpers _metadata_view, _tick_view, _meeting_view, etc. ...
```

The `_apply_meeting_result` reuse point is the most fragile dependency. If it's currently private (leading underscore), the implementing agent can either (a) propose a one-line orchestrator change exposing a `apply_meeting_result_view` helper (small scope; defensible), or (b) inline the meeting-application logic locally. Document the choice in `## Decisions`. Bias toward (a) — single source of truth — if the orchestrator change is genuinely one line.

For the memory endpoint, the cleanest path is to re-render via `agents.memory.store.render_for_prompt` against the reconstructed engine state at that tick. This is determinism-preserving and avoids string-parsing the captured LLM prompt. Trade-off: requires the loader to maintain per-agent memory stores across the tick walk, which is more bookkeeping than the simpler "extract from LLMCallRecord.prompt" approach. The implementing agent picks; document the choice.

For the fixture JSONL, the cleanest pattern is a test helper that writes a small synthetic replay using the real `ReplayLog` API:

```python
# tests/api/fixtures/sample_replay.py — illustrative
def write_sample_replay(path: Path, *, seed: int = 0, ticks: int = 3) -> None:
    """Write a minimal real replay log. Used by api tests as ground truth."""
    log = ReplayLog(path=path, game_id=f"headless-seed-{seed}")
    state = seed_initial_state(seed=seed, map=load_canonical_map())
    for t in range(ticks):
        actions = []  # no-op tick
        state, events = advance_tick(state, actions)
        log.record_tick(tick=t, actions=actions, state=state)
    log.record_game_end(tick=ticks - 1, winner="CREWMATES", reason="all_tasks_complete")
```

This guarantees the fixture is a real replay (matches what `ReplayLog` actually writes), not a hand-authored mock that could drift from the real schema.

**Public types introduced:**

- `api.replay_loader.ReplayLoader`
- `api.replay_loader.ReplayStateMismatchError`

**Integration risk:**

This task imports broadly from `engine/`, `orchestrator/`, and (potentially) `agents/memory/`. Risk is in subtle determinism breaks and import-linter friction.

- **Determinism is the load-bearing invariant.** Every reconstructed `state_hash` must match the recorded one. Any divergence is either (a) non-determinism in `advance_tick` (would be a Phase 1-2 regression — escalate immediately), (b) wrong action deserialization, or (c) wrong meeting-result application. The state-hash assertion catches all three at test time.
- **`_apply_meeting_result` reuse.** Either expose it publicly in `orchestrator/game.py` or duplicate it. Document the choice. Duplication risks drift; exposure adds public API surface. Bias toward exposure with a stable name (`apply_meeting_result`).
- **LRU cache and concurrent requests.** `functools.lru_cache` is thread-safe but not async-safe; under heavy concurrent load on FastAPI's threadpool, eviction races could re-trigger loads. Acceptable for MVP single-user spectator; revisit if it ever becomes a service.
- **Engine playback CPU.** A 1000-tick game with one meeting is ~50-200 ms. The cache means repeat fetches are fast; first fetch pays the playback cost. Acceptable for MVP. Benchmark in `## Decisions` for a real `/tmp/eval-50/replay-seed-22.jsonl`.
- **Replay format compatibility.** This loader is pinned to the current `ReplayEntry` / `MeetingReplayEntry` / `GameEndReplayEntry` / `FailedCallReplayEntry` shape. Future replay-format changes need a corresponding loader update; pin replay version in `## Decisions` (e.g. "loader assumes replay format as of commit X").
- **Memory endpoint cost.** Reconstructing per-agent memory requires walking the agent's observation stream from tick 0 to the meeting tick. If we re-render via `render_for_prompt`, that's an additional per-request cost. Either cache memory views inside the `load_replay` cache (memory-heavy) or accept the recompute cost on every memory request. Implementing agent picks; document.
- **Leak surface widens.** The memory endpoint is the largest information-exposure point in the API. The mid-phase audit (after 4.4 merges) will specifically scrutinize this endpoint for whether `rendered_memory_text` accidentally embeds role-leaking lines or other-player private state. If the audit flags issues, expect a 4.4.6 repair task targeting memory-view sanitization.
- **No CI cost.** All tests are static / fixture-based. No real-provider, no engine modification.
- **`api/main.py` env-var addition** is the only `.env.example` edit allowed; document the `AILIBI_REPLAY_DIR` default precisely.

**Ready-to-paste prompt:** `agent_prompts/task-4-2-replay-endpoint.md`

### Task 4.3 — React + Vite + Tailwind + PixiJS setup
**Branch:** `phase-4-react-vite-tailwind-setup`
**Depends on:** 4.2 merged
**Section refs:** DESIGN.md §7
**Complexity:** Medium

`frontend/` skeleton, type-safe API client mirroring the 4.1 DTOs, and
a Zustand store contract that downstream components (4.4, 4.4.5, 4.5,
4.6, 4.7, 4.8) consume. This task establishes the second contract
boundary of Phase 4 — after the DTO inventory (4.1), the
store/component contract is the load-bearing artifact. Get it right
once; five components depend on it.

**Tooling decisions baked in.** Per DESIGN.md §7:

- **Package manager:** npm with `package-lock.json`. Yarn / pnpm are
  out unless an existing repo choice requires otherwise. (DESIGN.md
  doesn't dictate; npm wins on default familiarity.)
- **Build:** Vite. React + TypeScript template (`@vitejs/plugin-react`
  + `@vitejs/plugin-react-swc` — implementing agent picks; document).
- **Styling:** Tailwind CSS via `@tailwindcss/vite` (Tailwind v4 plug-in
  approach) OR PostCSS pipeline (Tailwind v3) — implementing agent
  picks the current LTS; document the version chosen.
- **State:** Zustand. One store: `useReplayStore`. No Redux, no
  Recoil, no context shenanigans.
- **Graphics:** PixiJS v8+ via `@pixi/react` for React integration
  (or vanilla PixiJS with a `useEffect` mount pattern — implementing
  agent picks; document).
- **TypeScript:** strict mode (`strict: true`, `noUncheckedIndexedAccess:
  true`, `exactOptionalPropertyTypes: true`).

**API type generation.** The Pydantic DTOs in `api/schemas.py` are the
source of truth; TypeScript types in `frontend/src/types/api.ts` MUST
match them. Two paths:

1. **Generated** via `openapi-typescript` against
   `http://localhost:8000/openapi.json` — drift-resistant, requires the
   API to be running at type-gen time. Add a `npm run gen:api`
   script that hits the running API and writes
   `frontend/src/types/api.ts`. Run it as part of `scripts/check.sh`
   when the API is reachable; skip with a warning when it isn't.
2. **Hand-authored** — direct re-implementation of the 4.1 DTOs as
   TypeScript types. Simpler, no codegen dependency. Drift risk:
   adding a DTO field requires editing both Python AND TypeScript.

Recommend path 1 (generated). Path 2 is fine if the implementing
agent finds `openapi-typescript` painful for some reason. Document
the choice in `## Decisions`.

**Store contract — frozen at this task.** The store shape that 4.4–4.8
consume:

```typescript
interface ReplayStoreState {
  // Available replays (loaded once via /replays on app mount)
  replayList: ReplayMetadataView[] | null;
  replayListError: string | null;

  // Currently-selected replay
  currentReplay: ReplayView | null;
  currentReplayError: string | null;

  // Playback state
  currentTick: number;           // index into currentReplay.ticks
  isPlaying: boolean;
  playbackSpeed: 0.5 | 1 | 2 | 4;

  // Selected meeting (for MeetingView overlay)
  selectedMeetingId: string | null;

  // Selected agent (for ThoughtStream)
  selectedAgentId: string | null;

  // Memory cache (sparse — only meeting-boundary snapshots)
  // keyed by `${meeting_id}:${agent_id}`
  memoryCache: Record<string, AgentMemoryView>;
}

interface ReplayStoreActions {
  loadReplayList(): Promise<void>;
  selectReplay(gameId: string): Promise<void>;
  setCurrentTick(tick: number): void;
  setIsPlaying(playing: boolean): void;
  setPlaybackSpeed(speed: 0.5 | 1 | 2 | 4): void;
  selectMeeting(meetingId: string | null): void;
  selectAgent(agentId: string | null): void;
  fetchMemoryView(meetingId: string, agentId: string): Promise<void>;
  clearError(): void;
}
```

Adding a field after 4.3 merges requires a follow-up task touching all
five consumer components. Implementing agent: do not invent fields
the consumer tasks don't explicitly need; the inventory above is
complete for MVP.

**Out of scope** (explicit decisions deferred):

- **Authentication / authorization.** API is local-dev only in MVP.
- **Routing (React Router etc.).** Single-page app; URL state is not
  load-bearing in MVP. Add when there's a second page.
- **Internationalization.** English-only in MVP.
- **Service worker / offline support.** Not in MVP scope.
- **Production build / deployment config.** `vite build` produces
  output but deployment infra (Docker, CDN, etc.) is Phase 5+.
- **Component implementations.** This task ships the skeleton ONLY —
  `App.tsx` renders a "loading replay list..." stub. MapView,
  MeetingView etc. land in 4.4+.

**Files in scope:**
- frontend/package.json
- frontend/package-lock.json
- frontend/vite.config.ts
- frontend/tailwind.config.js (or `tailwind.config.ts`)
- frontend/postcss.config.js (if Tailwind v3)
- frontend/tsconfig.json
- frontend/tsconfig.node.json
- frontend/index.html
- frontend/src/main.tsx
- frontend/src/App.tsx
- frontend/src/api/client.ts
- frontend/src/store/replayStore.ts
- frontend/src/types/api.ts
- frontend/src/index.css
- frontend/.gitignore
- scripts/setup_env.sh
- scripts/check.sh
- .gitignore

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/ (beyond consuming the contract)
- frontend/src/components/ (downstream tasks own these)
- .github/workflows/ci.yml (Phase 5 concern)
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- README.md
- open_issues.md
- tests/

**Definition of done:**
- [ ] **`frontend/` skeleton compiles.** `cd frontend && npm install && npm run build` succeeds. `npm run dev` boots Vite at `http://localhost:5173` and connects to API at `http://localhost:8000` via Vite proxy (`/api/*` proxied; CORS not needed in dev).
- [ ] **TypeScript strict mode.** `tsconfig.json` enables `strict: true`, `noUncheckedIndexedAccess: true`, `exactOptionalPropertyTypes: true`. No `// @ts-ignore` or `any` types in the codebase.
- [ ] **API client (`src/api/client.ts`).** Exposes typed methods matching each 4.1 endpoint: `listReplays() -> Promise<ReplayMetadataView[]>`, `getReplay(gameId) -> Promise<ReplayView>`, `getTick(gameId, tick)`, `getMeeting(gameId, meetingId)`, `getMemory(gameId, meetingId, agentId)`, `getEvalCostSummary()`. All return parsed-typed responses. Error handling: HTTP errors are surfaced as typed exceptions, not silently swallowed.
- [ ] **Type module (`src/types/api.ts`).** Either generated (via `openapi-typescript`) or hand-authored to mirror every 4.1 DTO. Choice documented in `## Decisions`. If generated, the `npm run gen:api` script is committed.
- [ ] **Zustand store (`src/store/replayStore.ts`).** Implements the `ReplayStoreState` + `ReplayStoreActions` interface above. Verify by importing it from a smoke test that all action methods exist and the state shape matches.
- [ ] **`App.tsx` stub renders meaningfully.** On mount: calls `loadReplayList()`; displays "Loading replays..." while pending; displays the list with clickable items when loaded; displays an error message on failure. No PixiJS, no MapView yet — those are 4.4. The acceptance is "user can see the API connection works" (a populated list or an error).
- [ ] **Tailwind classes work.** `App.tsx` uses at least three Tailwind utility classes; `tsc` + `vite build` produces CSS with those classes resolved.
- [ ] **PixiJS installs cleanly.** `@pixi/react` (or vanilla PixiJS — document) is listed in `package.json`; importing it from a smoke file compiles without TypeScript errors. No PixiJS usage in `App.tsx` yet.
- [ ] **`scripts/setup_env.sh` installs frontend deps.** Idempotent: re-running doesn't break anything. Detects if `frontend/package.json` exists; runs `npm install` from `frontend/` if so. Does not modify the Python setup behavior.
- [ ] **`scripts/check.sh` runs frontend checks.** Adds a frontend block that runs `cd frontend && npm run tsc:check && npm run build` (or equivalent). Failures cause `scripts/check.sh` to exit non-zero. Skipped with a warning if `frontend/package.json` doesn't exist (graceful degradation for branches that don't include 4.3 yet).
- [ ] **`frontend/.gitignore`** excludes `node_modules/`, `dist/`, `.vite/`, `coverage/`. Root `.gitignore` already excludes `node_modules/` from prior phases; verify no duplication.
- [ ] **`package-lock.json` committed.** No `yarn.lock` or `pnpm-lock.yaml`.
- [ ] No imports from `engine/`, `agents/`, `llm/`, `meetings/`, `observation/`, `orchestrator/` (the Python firewall doesn't extend to TypeScript but the architectural rule does). The frontend talks to the API, not to Python modules.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (Python tests unaffected).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally (including the new frontend block when `frontend/` exists).


**Implementation hint:**

`package.json` skeleton (illustrative; pin exact versions when implementing):

```json
{
  "name": "ailibi-frontend",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc --noEmit && vite build",
    "tsc:check": "tsc --noEmit",
    "gen:api": "openapi-typescript http://localhost:8000/openapi.json -o src/types/api.ts",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "pixi.js": "^8.0.0",
    "@pixi/react": "^8.0.0",
    "zustand": "^4.5.0"
  },
  "devDependencies": {
    "@types/react": "^18.3.0",
    "@types/react-dom": "^18.3.0",
    "@vitejs/plugin-react-swc": "^3.7.0",
    "openapi-typescript": "^7.4.0",
    "tailwindcss": "^4.0.0",
    "typescript": "^5.5.0",
    "vite": "^5.4.0"
  }
}
```

Resolve to the current LTS at task-execution time; the implementing agent should not pin to versions that are already stale. Document the resolved versions in `## Decisions`.

`vite.config.ts` proxy block (illustrative):

```typescript
// frontend/vite.config.ts
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
```

The proxy lets the frontend make requests to `/api/replays` which Vite forwards to `http://localhost:8000/replays`. No CORS configuration needed; production deployment can configure CORS at the API layer (Phase 5+).

Zustand store skeleton (illustrative):

```typescript
// frontend/src/store/replayStore.ts
import { create } from "zustand";
import * as api from "../api/client";

export const useReplayStore = create<ReplayStoreState & ReplayStoreActions>((set, get) => ({
  replayList: null,
  replayListError: null,
  currentReplay: null,
  currentReplayError: null,
  currentTick: 0,
  isPlaying: false,
  playbackSpeed: 1,
  selectedMeetingId: null,
  selectedAgentId: null,
  memoryCache: {},

  async loadReplayList() {
    try {
      const list = await api.listReplays();
      set({ replayList: list, replayListError: null });
    } catch (e) {
      set({ replayListError: e instanceof Error ? e.message : String(e) });
    }
  },

  // ... other actions ...
}));
```

For `scripts/check.sh`, the addition is a guarded block:

```bash
# scripts/check.sh — illustrative addition
if [ -f frontend/package.json ]; then
  echo "Running frontend checks..."
  ( cd frontend && npm run tsc:check && npm run build )
else
  echo "Skipping frontend checks (frontend/package.json not present)."
fi
```

This preserves existing Python check behavior for branches that don't include 4.3.

**Public types introduced:**

- `frontend/src/store/replayStore.ts::useReplayStore`
- `frontend/src/types/api.ts::*` (every DTO from 4.1, mirrored)
- `frontend/src/api/client.ts::listReplays`
- `frontend/src/api/client.ts::getReplay`
- `frontend/src/api/client.ts::getTick`
- `frontend/src/api/client.ts::getMeeting`
- `frontend/src/api/client.ts::getMemory`
- `frontend/src/api/client.ts::getEvalCostSummary`

**Integration risk:**

This task front-loads tooling decisions for the rest of Phase 4. Risk
is in picking patterns that downstream tasks find painful to work with.

- **Store-shape lock-in.** Once 4.4 builds against the store, changing
  the shape requires touching 4.4. Once 4.4.5–4.8 all consume, a shape
  change touches all five. Bias toward MORE state in the store
  interface above (it's easier to ignore a field than to add one).
- **PixiJS integration choice.** `@pixi/react` is the React-idiomatic
  path; vanilla PixiJS + `useEffect` mounting is more manual but
  avoids a dependency. Either works for the slice; 4.4's implementing
  agent will hit the choice harder than 4.3's.
- **Type generation drift.** If hand-authored, every API change is a
  two-file edit (Pydantic + TypeScript). Generated is safer but couples
  the dev loop to a running API. Recommend `npm run gen:api` as a
  pre-commit step or in `scripts/check.sh` when the API is up.
- **Tailwind v3 vs v4.** v4 introduced a Vite-first plugin and dropped
  PostCSS config; v3 still works fine. Pick the current LTS at
  execution time; document the version.
- **`scripts/check.sh` ordering.** Frontend checks should run AFTER
  Python checks (Python is the source of truth; frontend is
  downstream). Implementing agent: place the frontend block at the
  end of `scripts/check.sh`.
- **`uv run mypy .` and frontend.** Python type-checking is unaffected
  by `frontend/` — mypy ignores it by default. No new ignore rules
  needed.
- **No backend changes.** This task does NOT modify `api/`. If a
  frontend need surfaces a missing API field, file a 4.2 follow-up,
  don't modify the API here.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-3-react-vite-tailwind-setup.md`

### Task 4.4 — MapView vertical slice
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


**Implementation hint:**

MapView is a thin PixiJS-React component. Two rendering choices:

1. **`@pixi/react` v8 idiom** (declarative):

```tsx
// frontend/src/components/MapView.tsx — illustrative
import { Application, Graphics, Text } from "@pixi/react";
import { useReplayStore } from "../store/replayStore";

export function MapView() {
  const currentReplay = useReplayStore((s) => s.currentReplay);
  const currentTick = useReplayStore((s) => s.currentTick);

  if (!currentReplay) return <div>Select a replay to view.</div>;

  const tick = currentReplay.ticks[currentTick];
  const rooms = currentReplay.map.rooms;
  const players = currentReplay.players;

  return (
    <Application width={800} height={600}>
      {rooms.map((r) => <RoomRect key={r.id} room={r} />)}
      {tick.agent_states
        .filter((a) => a.is_alive && a.room_id !== null)
        .map((a) => (
          <AgentToken
            key={a.agent_id}
            agentState={a}
            room={rooms.find((r) => r.id === a.room_id)!}
            color={players.find((p) => p.agent_id === a.agent_id)!.color}
          />
        ))}
    </Application>
  );
}
```

2. **Vanilla PixiJS + `useEffect` mount**:

```tsx
// frontend/src/components/MapView.tsx — illustrative alternative
import { Application, Container, Graphics } from "pixi.js";
import { useEffect, useRef } from "react";

export function MapView() {
  const canvasRef = useRef<HTMLDivElement>(null);
  const appRef = useRef<Application | null>(null);

  useEffect(() => {
    if (!canvasRef.current) return;
    const app = new Application();
    app.init({ width: 800, height: 600, background: 0x1a1a1a }).then(() => {
      canvasRef.current!.appendChild(app.canvas);
      appRef.current = app;
      // ... render rooms + tokens ...
    });
    return () => {
      app.destroy(true);
    };
  }, []);

  return <div ref={canvasRef} />;
}
```

The implementing agent picks (1) or (2) based on which the 4.3 task chose; document. (1) is more React-idiomatic; (2) is more PixiJS-idiomatic.

Per-room jitter helper for placing multiple agents inside one room:

```typescript
// 6 deterministic offsets around a room center
const JITTER_OFFSETS = [
  { dx: -20, dy: -20 },
  { dx:  20, dy: -20 },
  { dx: -20, dy:  20 },
  { dx:  20, dy:  20 },
  { dx:   0, dy: -30 },
  { dx:   0, dy:  30 },
];

function agentPosition(agentIndex: number, room: RoomView) {
  const offset = JITTER_OFFSETS[agentIndex % JITTER_OFFSETS.length];
  return {
    x: room.position.x + room.size.width / 2 + offset.dx,
    y: room.position.y + room.size.height / 2 + offset.dy,
  };
}
```

`agentIndex` is the agent's index in `currentReplay.players` (stable across ticks).

For room colors, deterministic hash → HSL:

```typescript
function roomColor(roomId: string): number {
  let hash = 0;
  for (const ch of roomId) hash = (hash * 31 + ch.charCodeAt(0)) >>> 0;
  const hue = hash % 360;
  return parseInt(`hsl(${hue}, 30%, 25%)`.replace(/[^\d]/g, "").slice(0, 6), 16);
}
```

(Or use a small color library if dependencies allow; document.)

**Public types introduced:**
None.

**Integration risk:**

Lowest-risk task in Phase 4. The substrate is built; this task just exercises it.

- **PixiJS mount/unmount on hot reload.** Vite HMR can leave dangling PixiJS Applications if `useEffect` cleanup is wrong. Verify by editing MapView.tsx mid-dev and confirming the canvas doesn't multiply.
- **DTO-shape assumptions.** Components access `currentReplay.ticks[currentTick]` directly. If `ticks` is sparse (it isn't — every tick is recorded), this would crash. Confirm via the 4.3 store + 4.2 endpoint contract: `ticks` is dense from 0 to `metadata.total_ticks - 1`.
- **`room_id != null` filter.** Dead agents have `room_id=null`. Failing to filter would crash (`.find()` returning undefined on `players`). The DoD specifies the filter; the implementing agent must not skip it.
- **Audit blocks fan-out.** After 4.4 merges, the mid-phase DTO audit runs. If the audit flags issues with the substrate (DTO leaks, store shape problems), repair tasks land before 4.4.5–4.8 fan out. 4.4 itself is unlikely to be a repair target — it's the vertical slice that surfaces the issues.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-4-mapview-vertical-slice.md`

### Mid-phase DTO audit

After 4.4 merges, run the Phase 4 mid-phase DTO audit before
dispatching 4.4.5–4.8. The audit is double-tool (Claude + Codex)
followed by a reconciliation pass — the substrate gates five
downstream PRs, so a second opinion is worth the cost. Both auditors
run the same audit prompt in independent sessions; a third session
reconciles.

**Prompts:**
- `audits/prompts/mid-phase-4-dto-audit-prompt.md` — run by Claude
  and by Codex in two independent sessions.
- `audits/prompts/mid-phase-4-reconciliation-prompt.md` — run in a
  fresh session after both audits land. The reconciler does not read
  the audit prompt; only the two reports + the code.

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

**Outputs:**
- `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-claude.md`
- `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-codex.md`
- `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-reconciled.md` —
  the one the project acts on.

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
