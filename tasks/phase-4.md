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
  audit lands do 4.5–4.11 fan out.
- **Mid-phase DTO audit, no real-provider analog.** Double-tool audit
  (Claude + Codex) with a separate reconciliation pass. The substrate
  gates five downstream PRs; a second opinion is worth the cost.
  Focused on DTO/leak coverage after the substrate exists. The
  phase-closing acceptance gate is a manual UX session (a non-
  technical viewer follows a replay end-to-end without reading logs).

## Parallelism
4.1 → 4.2 → 4.3 → 4.4 in series. Mid-phase DTO audit runs after 4.4.
After the audit passes, seven downstream tasks dispatch with this
dependency graph:

- **First wave (parallel after audit):** 4.5 (MapView full),
  4.6 (MeetingView), 4.7 (R-3 LLMCallRecord agent_id substrate).
  None depends on another. 4.5 doesn't touch `App.tsx` or the
  DTO substrate. 4.6 is first to touch `App.tsx`. 4.7 is the
  first DTO-substrate change.
- **Second wave (after first-wave deps clear):**
  4.8 (ThoughtStream) — needs `4.6` (App.tsx slot order) + `4.7`
  (per-call agent_id).
  4.9 (R-2 BeliefEntryView snapshot_tick) — needs `4.7` (shared
  DTO/loader/TS/fixture file scope; serialized to avoid merge
  churn, not a logical prereq).
- **Third wave:** 4.10 (BeliefMatrix) — needs `4.8` (App.tsx) +
  `4.9` (DTO rename).
- **Fourth wave:** 4.11 (ReplayControls) — needs `4.10` (App.tsx;
  ReplayControls is the last component to integrate).

R-3 (4.7) and R-2 (4.9) are mid-phase audit follow-ups; they exist
as standalone repair tasks rather than baked into the consuming
components so that the consumer tasks stay scoped to
`frontend/src/components/`.

The serial `4.6 → 4.8 → 4.10 → 4.11` chain exists because all four
edit `frontend/src/App.tsx` to mount their component. Without the
chain, four PRs would race on the same file. The cost is ~3 extra
serial merges instead of full parallel dispatch; the benefit is
zero merge-conflict resolution in dispatched sessions. Phase 5 can
revisit if a build-out task ever needs maximal frontend
parallelism.

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
dispatching 4.5–4.11. The audit is double-tool (Claude + Codex)
followed by a reconciliation pass — the substrate gates seven
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
out 4.5–4.11" OR "Mid-phase DTO audit blocks fan-out — repair tasks
required: …"

**Audit outcome (2026-05-26 23:16):** Passes. Zero blocking findings.
Three Class A informational notes from Claude (Codex silent), all
Unique-but-verified by the reconciler. R-1 (`AgentTickStateView`
docstring stale) is a ride-along on any PR touching `api/schemas.py`.
R-2 and R-3 land as repair tasks **4.9** and **4.7** respectively
because they're prerequisites for **4.10** (BeliefMatrix) and **4.8**
(ThoughtStream). Reconciled report:
[audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md](audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md).

**Outputs:**
- `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-claude.md`
- `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-codex.md`
- `audits/audit-YYYY-MM-DD-HHMM-mid-phase-4-dto-reconciled.md` —
  the one the project acts on.

### Task 4.5 — MapView full (sabotage, vents, bodies, tween)
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


**Implementation hint:**

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

**Public types introduced:**
None.

**Integration risk:**

This task adds rendering polish on top of a working vertical slice. The risk is in tween correctness and PixiJS lifecycle hygiene.

- **Tween cleanup under HMR.** `useTick` registrations must unregister on unmount or HMR will accumulate Tickers. Verify with `app.ticker.count` in the browser console after multiple HMR cycles.
- **Tween + scrubber interaction.** When 4.11's scrubber jumps by >1 tick, the tween should snap, not animate through intermediate ticks. The `useEffect` reset on `targetRoom.id` handles single-tick changes; multi-tick changes need `progress.current = 1` (immediate completion). Test against 4.11 once it lands.
- **Body marker O(N·T) scan.** Scanning all events from 0..currentTick on every render is fine for 1000-tick games (≤2000 events) but inefficient for longer. If profiling flags it, memoize the visible-bodies derivation keyed on `(gameId, currentTick)`. Not a launch blocker.
- **Sabotage tint as full-canvas overlay.** A simple translucent rect is fine; if it visually clashes with a vignette / radial-gradient approach the implementing agent prefers, that's a styling choice — document. The behavior is "user sees lights are out at a glance," not "user can see only same-room agents" (the spectator is privileged).
- **No backend changes.** Every DTO field consumed here already exists per the 4.1 inventory. If a missing field surfaces, that's a backend gap — file a follow-up, don't widen this task's scope.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-5-mapview-full.md`

### Task 4.6 — MeetingView (reports, statements, ballots, contradictions)
**Branch:** `phase-4-meetingview`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §5, DESIGN.md §7
**Complexity:** Medium

Transcript renderer for one meeting: reports + accusation-round
statements + ballots + contradiction flags + a small metadata footer
(prompt versions, total cost). Activated when the spectator selects
a meeting via the store's `selectedMeetingId`. The store already
holds `selectMeeting(id | null)` from 4.3; this task wires the UI.

**Layout choice — overlay vs replace.** The MeetingView is a focused
reading surface — there's no reason to render alongside the map at
small viewport widths. Recommendation: render as a modal-style
overlay (full-canvas dim + centered panel) when `selectedMeetingId
!== null`, with a close button that clears the selection. This keeps
MapView's PixiJS canvas un-touched (no unmount cost) and gives the
reading surface the screen real estate it needs. The implementing
agent may pick the side-by-side split-view alternative if the
viewport calculation justifies it; document the choice in `##
Decisions`.

**Meeting-trigger discovery.** A "Meeting" pill / button appears
next to TickStepper when `currentReplay.meetings.some(m => m.tick
=== currentTick)`. Clicking it calls `selectMeeting(m.meeting_id)`.
This is the primary UI affordance for opening a meeting; users can
also scroll to a meeting tick first (via TickStepper) and then click
the pill. 4.11 (ReplayControls) adds a "next meeting" snap-to button
that calls both `setCurrentTick(m.tick)` and `selectMeeting(m.id)`
in one action.

**Out of scope** (explicit decisions deferred):

- **Meeting search / filter UI.** N meetings per game is typically
  ≤ 3 in MVP scope; pagination / search would be premature.
- **Inline LLM call drilldown.** The meeting metadata footer lists
  `total_cost_usd` and `llm_call` count; the actual prompt / response
  text drilldown happens in 4.8 (ThoughtStream), keyed by
  `selectedAgentId`. Don't duplicate the LLM call rendering here.
- **Contradiction graph view.** Contradictions render as inline
  badges inside the affected statements / reports; a separate
  contradiction-network visualization is out of scope.
- **Editable / interactive transcript.** Read-only render. The
  spectator does not vote, accuse, or annotate.
- **Translations / TTS.** Free text renders as-is.

**Files in scope:**
- frontend/src/components/MeetingView.tsx
- frontend/src/components/ReportCard.tsx
- frontend/src/components/StatementCard.tsx
- frontend/src/components/BallotCard.tsx
- frontend/src/components/ContradictionBadge.tsx
- frontend/src/components/MeetingPill.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (frozen)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen)
- frontend/src/components/MapView.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/RoomRect.tsx
- frontend/src/components/VentEdge.tsx (lands in 4.5)
- frontend/src/components/BodyMarker.tsx (lands in 4.5)
- frontend/src/components/SabotageOverlay.tsx (lands in 4.5)
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
- frontend/package.json (locked at 4.3)
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
- [ ] **MeetingPill in TickStepper-adjacent slot.** When the current replay has a meeting at `currentTick`, a button labeled `Meeting @ tick N` is visible and clickable. Click → `selectMeeting(meeting_id)`. When no meeting is at currentTick, the pill is hidden (not greyed-out).
- [ ] **MeetingView mounts iff `selectedMeetingId !== null`.** The view fetches the meeting from `currentReplay.meetings.find(m => m.meeting_id === selectedMeetingId)`. If the meeting isn't found (e.g. stale selection after replay switch), call `selectMeeting(null)` and render nothing. Renders an overlay with a close button (`selectMeeting(null)`) and the transcript.
- [ ] **Reports section.** One `ReportCard` per item in `meeting.reports`. Card header: `agent_id` + reporter color swatch (from `currentReplay.players[].color`) + tick. Body: `free_text` foregrounded in a larger / readable font. Below: collapsed-by-default structured detail — observations list (one row per `ObservationClaimView`, discriminated render: `saw_player` shows subject + room + co_present; `completed_task` shows task_id + room; `found_body` shows body_of + room) and claims list (one row per `StatementClaimView`, similarly discriminated).
- [ ] **Statements section, grouped by round.** Group `meeting.statements` by `round_index`. Render rounds in numeric order. Within a round, statements in their original order (one per speaker per round). Each `StatementCard` shows: speaker (with color swatch), target (if non-null, as a chip; if null, "general" or omitted), `free_text` foregrounded, claims collapsed-by-default. Contradictions reference a `contradiction_id` — render a small `ContradictionBadge` inline next to any claim implicated.
- [ ] **Ballots section.** One `BallotCard` per item in `meeting.ballots`. Voter color swatch + voter id; target (player id with color swatch, or the literal text "SKIP" with neutral styling); confidence rendered as a horizontal bar (0.0–1.0 width); `rationale_text` foregrounded. Tally summary at the section header: e.g. `p-2: 2 votes · p-5: 1 vote · SKIP: 0 votes`.
- [ ] **Contradictions inline + summary.** Each `ContradictionView` renders as a `ContradictionBadge` (small chip with `kind` color-coded). The badge appears (a) inline next to any report / statement whose `event_a_id` or `event_b_id` matches, and (b) in a `Contradictions` summary section at the bottom of the meeting overlay, listing all contradictions with their `description` text and involved `subjects`.
- [ ] **Outcome banner.** Top of the overlay: large prominent banner showing `outcome` (`EJECTED` or `SKIPPED`) and, if ejected, the player name + color. Includes triggered-by (`triggered_by` agent + `trigger_kind`).
- [ ] **Metadata footer.** Small footer (collapsible / muted styling): `meeting_id`, `tick`, `total_cost_usd` (formatted as `$0.0123`), `prompt_versions` rendered as a `key: value` list (e.g. `crewmate_report: crewmate_report.v1`, one per line). `llm_call` count rendered as `N LLM calls (drill into ThoughtStream for details)`.
- [ ] **App.tsx layout updated.** Pill rendered near TickStepper. Overlay mounted at the App root (above all other content via z-index or React Portal). Pre-existing MapView / ReplayPicker / TickStepper remain intact.
- [ ] **No new npm dependencies.** React 19, Zustand 5, Tailwind v4 from 4.3 are sufficient. No PixiJS in this component (it's pure DOM).
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: (a) MeetingPill visible on the map view at a meeting tick, (b) the open MeetingView overlay for that meeting showing at least one report, statements across both rounds, ballots with a clear tally, and the outcome banner.
- [ ] **Manual smoke documented.** PR description states the replay used (any of `replays/replay-seed-{22,24,26,49}.jsonl` from the Phase 3 eval — those are the 4 games with meetings; pick whichever is in `$AILIBI_REPLAY_DIR`), the meeting opened, and confirms all four card types render without console errors.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

MeetingView is pure React + Tailwind — no PixiJS. The overlay pattern:

```tsx
export function MeetingView() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const selectMeeting = useReplayStore((s) => s.selectMeeting);
  if (!meetingId || !replay) return null;
  const meeting = replay.meetings.find((m) => m.meeting_id === meetingId);
  if (!meeting) {
    selectMeeting(null);
    return null;
  }
  return (
    <div className="fixed inset-0 bg-black/70 z-50 overflow-auto">
      <div className="max-w-4xl mx-auto my-8 bg-neutral-900 rounded p-6">
        <OutcomeBanner meeting={meeting} players={replay.players} />
        <ReportsSection reports={meeting.reports} players={replay.players} />
        <StatementsSection statements={meeting.statements} contradictions={meeting.contradictions} players={replay.players} />
        <BallotsSection ballots={meeting.ballots} players={replay.players} />
        <ContradictionsSection contradictions={meeting.contradictions} />
        <MetadataFooter meeting={meeting} />
      </div>
    </div>
  );
}
```

Grouping statements by round:

```tsx
function StatementsSection({ statements, contradictions, players }: Props) {
  const byRound = new Map<number, StatementView[]>();
  for (const s of statements) {
    if (!byRound.has(s.round_index)) byRound.set(s.round_index, []);
    byRound.get(s.round_index)!.push(s);
  }
  const rounds = [...byRound.keys()].sort((a, b) => a - b);
  return rounds.map((r) => (
    <RoundSection key={r} round={r} statements={byRound.get(r)!} ... />
  ));
}
```

Contradiction-to-statement linking: build a `Set<string>` of contradiction event ids; check each statement's `statement_id` against `event_a_id` / `event_b_id`.

Color swatch helper — re-use the deterministic-hash pattern from 4.4's `RoomRect`:

```typescript
function playerColor(agentId: string, players: PlayerView[]) {
  return players.find((p) => p.agent_id === agentId)?.color ?? "#888";
}
```

Discriminated-union render for ObservationClaimView:

```tsx
function ObservationLine({ obs }: { obs: ObservationClaimView }) {
  switch (obs.type) {
    case "saw_player": return <span>saw {obs.subject} in {obs.room} (with {obs.co_present.join(", ")})</span>;
    case "completed_task": return <span>completed {obs.task_id} in {obs.room}</span>;
    case "found_body": return <span>found body of {obs.body_of} in {obs.room}</span>;
  }
}
```

TypeScript's discriminated union narrowing makes this exhaustive.

**Public types introduced:**
None.

**Integration risk:**

This task introduces six new components plus an App.tsx edit. The risk is in coupling MapView and MeetingView state through the store correctly.

- **MeetingPill click does NOT change currentTick.** The pill only sets `selectedMeetingId`. The map continues to display the current tick. The user can choose to scrub to the meeting tick separately; auto-seek is a UX choice owned by 4.11.
- **Selection cleared on replay switch.** When `selectReplay` is called (4.3 store action), `selectedMeetingId` already resets to null per the existing store implementation. Verify by switching replays mid-overlay: the overlay should close.
- **z-index ordering vs PixiJS canvas.** The MeetingView overlay must stack above the PixiJS canvas. PixiJS renders into a `<canvas>` element which is a regular DOM child; standard `z-index` works.
- **Outcome banner color choice.** EJECTED in green when the ejected player was an impostor (a "good" outcome for crew) might encode role information at the banner level. Recommended: outcome color is neutral; only the ejected player's color swatch shows their role coloring. Document in `## Decisions`.
- **Ballot tally calculation.** Compute client-side from `meeting.ballots` — the DTO doesn't include a pre-computed tally. Group by `target`, count entries. A skipped vote has `target === "SKIP"`; treat as a distinct bucket.
- **Long free_text scroll.** Some report `free_text` runs 200+ chars; ensure cards don't overflow the overlay panel. Use Tailwind `whitespace-pre-wrap` and a sensible `max-w` per card.
- **No backend changes.** All consumed fields exist per the 4.1 DTO inventory + 4.2 endpoint coverage.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-6-meetingview.md`

### Task 4.7 — LLMCallRecord agent_id propagation (R-3 substrate)
**Branch:** `phase-4-llmcall-agent-id`
**Depends on:** 4.4 merged + mid-phase DTO audit passed
**Section refs:** DESIGN.md §5, DESIGN.md §11.4, mid-phase DTO audit R-3
**Complexity:** Medium

Mid-phase DTO audit R-3 informational finding (Unique-but-verified):
`orchestrator.replay.LLMCallRecord` carries no `agent_id` field;
therefore neither does `api.schemas.LLMCallView`. ThoughtStream
(4.8) needs per-call attribution; today the only recovery path is
parsing rendered_memory text inside `prompt_text` — fragile and
template-dependent. This task threads `agent_id` from the meeting
manager through the LLM client protocol into the captured record
and out to the DTO layer + TS types. Reconciler explicitly flagged
this as a prerequisite for 4.8 dispatch.

**Scope is wider than the audit hinted.** The audit cited
`participant.agent_id` as "in scope at `meetings/manager.py:555-565`"
but the recording client in `orchestrator/game.py:223-231` is
stateless — it sees only the prompt + response from `LLMClient.
complete()`. To capture `agent_id` at record time, the `LLMClient`
protocol must take an `agent_id` parameter; every implementation
(claude provider, fake) passes through; every call site in
`meetings/manager.py` populates the parameter. The call chain
covered:

```
meetings/manager.py call site
   ↓ (passes agent_id=participant.agent_id)
LLMClient.complete(prompt, *, agent_id=...)
   ↓
_RecordingLLMClient.complete in orchestrator/game.py
   ↓ (stores agent_id on the constructed LLMCallRecord)
LLMCallRecord (gains optional agent_id field)
   ↓ (JSONL persistence; backward-compat for old replays)
api/replay_loader.py _llm_call_view
   ↓
api.schemas.LLMCallView (gains optional agent_id field)
   ↓
frontend/src/types/api.ts (mirror)
```

**Backward-compatibility decision.** `agent_id: str | None`, not
`str`. Reason: existing replay JSONLs (the Phase 3 eval's
`/tmp/eval-50/replay-seed-{22,24,26,49}.jsonl` and anything else on
disk) were written before this task. Deserializing those with a
required-string field would crash. With `str | None` defaulting to
`None`, old replays still load and ThoughtStream gracefully shows
`agent_id: unknown` for those calls. Pinning the field as required
later is a one-line tightening once we're confident no old replays
matter — that's a Phase 5 hygiene call, not this task's.

**Out of scope** (explicit decisions deferred):

- **Replay format versioning.** No `format_version` field on
  `ReplayLog`. Adding versioning is a Phase 5 concern; this task
  relies on Pydantic's default-on-missing behavior.
- **Retroactive backfill of old replays.** The audit asked us to
  "decide between patch existing replays and leave at None." We
  leave at None. No migration script is written; if a Phase 5 task
  decides to backfill, that's a separate effort.
- **`agent_id` for non-meeting triggered calls.** The
  `call_kind="trigger"` case (per-agent LLM triggers per
  DESIGN.md §4.4 #3) similarly knows the calling agent; the
  parameter propagates there too. If a future call kind is genuinely
  agentless (system-level), `None` remains a valid value.
- **Renaming `LLMCallRecord.prompt` → `prompt_text`.** Already
  named `prompt` on the source type and `prompt_text` on the DTO
  per 4.1's deliberate mapping. Don't rename.

**Files in scope:**
- llm/client.py
- llm/claude_provider.py
- llm/fake.py
- orchestrator/game.py
- orchestrator/replay.py
- meetings/manager.py
- api/schemas.py
- api/replay_loader.py
- frontend/src/types/api.ts
- tests/llm/test_client.py (or equivalent — match existing test naming)
- tests/orchestrator/test_game.py
- tests/orchestrator/test_replay.py
- tests/meetings/test_manager.py
- tests/api/test_schemas.py
- tests/api/test_replays.py
- tests/api/test_replay_loader.py
- tests/api/fixtures/sample_replay.py

**Files NOT in scope:**
- engine/
- agents/
- observation/
- frontend/src/components/
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/package.json
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
- tests/engine/
- tests/agents/
- tests/observation/
- tests/test_firewall.py

**Definition of done:**
- [ ] **`LLMClient.complete()` protocol extended.** [llm/client.py](llm/client.py)'s `LLMClient.complete()` signature gains `agent_id: str | None = None` as a keyword-only parameter (use `*,` to enforce keyword). Existing positional parameters unchanged. Docstring updated to describe the field's purpose ("identifies which game-agent originated this call; None for system-level calls").
- [ ] **All implementations updated to accept the parameter.** [llm/claude_provider.py](llm/claude_provider.py)'s adapter, [llm/fake.py](llm/fake.py) (or whatever the fake / recording client is named), and the `_RecordingLLMClient` in [orchestrator/game.py:204-233](orchestrator/game.py#L204) accept `agent_id` as a kwarg. The Anthropic adapter does NOT pass it to the upstream SDK (it's metadata, not provider-relevant); the fake stores it on its captured-call history for assertions.
- [ ] **`_RecordingLLMClient` captures `agent_id` on `LLMCallRecord`.** [orchestrator/game.py:223-231](orchestrator/game.py#L223) populates `agent_id=agent_id` on the constructed record.
- [ ] **`LLMCallRecord` gains the field.** [orchestrator/replay.py:51-71](orchestrator/replay.py#L51) adds `agent_id: str | None = None` (default-None for backward-compat). Pydantic `model_config` remains `frozen=True, extra="forbid"`. Schema validates a JSONL line that omits `agent_id` as `agent_id=None`; verify with a test.
- [ ] **Every call site in `meetings/manager.py` passes `agent_id`.** Audit with `grep -n "complete(" meetings/manager.py`. Each surfaced call passes `agent_id=<the speaking agent's id>`. The participant context object already carries `agent_id` per the audit reference; this is a parameter pass-through, not new bookkeeping. If a call genuinely has no agent (e.g. a manager-level system call), pass `agent_id=None` explicitly and add a code comment explaining why.
- [ ] **DTO exposure.** [api/schemas.py](api/schemas.py)'s `LLMCallView` (lines 357-370) gains `agent_id: str | None` as a new field. Update the `EXPECTED_DTOS` and `FORBIDDEN_TYPES` fixtures in [tests/api/test_leak.py](tests/api/test_leak.py) IF they reference the field set — but only if they do; the leak test is field-agnostic by design.
- [ ] **Loader propagation.** [api/replay_loader.py:1069-1081](api/replay_loader.py#L1069)'s `_llm_call_view` passes `agent_id=call.agent_id` (mapping the `LLMCallRecord.agent_id` straight through).
- [ ] **Frontend types mirror.** [frontend/src/types/api.ts:240-249](frontend/src/types/api.ts#L240) adds `agent_id: string | null` to the `LLMCallView` interface.
- [ ] **Backward-compat test.** A test in [tests/api/test_replay_loader.py](tests/api/test_replay_loader.py) writes a fixture JSONL that omits the `agent_id` field on `LLMCallRecord` entries (use `model_dump(mode="json", exclude={"agent_id"})` or hand-write a minimal valid JSON line); loads it; asserts the resulting `LLMCallView.agent_id is None`.
- [ ] **Round-trip test.** A test asserts that constructing an `LLMCallRecord(agent_id="p-2", ...)`, JSONL-roundtripping it, and loading it through the DTO yields `LLMCallView.agent_id == "p-2"`.
- [ ] **Manager call-site test.** A test in [tests/meetings/test_manager.py](tests/meetings/test_manager.py) uses the fake LLM client to assert that for a meeting with N participants, the fake's captured calls each carry the correct `agent_id` matching the speaking participant.
- [ ] **Sample replay fixture updated.** [tests/api/fixtures/sample_replay.py](tests/api/fixtures/sample_replay.py)'s helper that constructs synthetic LLM calls populates `agent_id` so downstream loader tests use the new field naturally.
- [ ] **No firewall change.** `agents/` still does not import from `engine/`. The `LLMClient` protocol lives in `llm/`, which `agents/` may import. Firewall preserved.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

Order the work to minimize broken intermediate states:

Step 1 — Add the field to `LLMCallRecord` with `default=None`. This is backward-compatible at the schema layer immediately. Existing replays continue to load.

Step 2 — Extend the `LLMClient` protocol. Add `agent_id: str | None = None` as a keyword-only parameter. Update all implementers to accept it (no-ops for the real provider; capture-and-store for fakes).

Step 3 — In `_RecordingLLMClient.complete`, pass `agent_id` through to the `LLMCallRecord` constructor.

Step 4 — Walk every call site in `meetings/manager.py` and add `agent_id=<...>` to each. Use the participant or speaker context object already in scope.

Step 5 — Add the field to `LLMCallView` and propagate in the loader. Add to TS types.

Step 6 — Write the backward-compat test (fixture JSONL without `agent_id`) and the round-trip test (with `agent_id`).

Step 7 — Run full check suite; fix any captured assertions in existing tests that need to be aware of the new field (likely few since field is None-defaulted).

Pydantic v2 default-None pattern for `LLMCallRecord`:

```python
class LLMCallRecord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    call_kind: Literal["meeting", "trigger"]
    model: str
    prompt: str
    response_text: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    agent_id: str | None = None
```

`extra="forbid"` still allows missing optional fields (Pydantic distinguishes "extra unknown field" from "missing optional field with default"). Verify by loading a JSONL line that lacks `agent_id` — should validate cleanly.

The protocol extension:

```python
class LLMClient(Protocol):
    def complete(
        self,
        prompt: str,
        *,
        call_kind: Literal["meeting", "trigger"] = "meeting",
        agent_id: str | None = None,
    ) -> LLMResponse: ...
```

Keep keyword-only via the `*,` separator; positional `agent_id` would be too easy to miswire.

**Public types introduced:**
None — these are field additions on existing types. The schema deltas are:

- `orchestrator.replay.LLMCallRecord` gains field `agent_id: str | None`
- `api.schemas.LLMCallView` gains field `agent_id: str | None`
- `LLMClient.complete()` protocol gains keyword parameter `agent_id`

**Integration risk:**

This task modifies a load-bearing protocol and a load-bearing replay schema. The risk is in subtle test breakage and in pre-existing replays' behavior under the new schema.

- **Protocol change ripple.** Every `LLMClient` implementation must accept the new kwarg. If a test fake uses a `Callable` instead of a `Protocol` instance, that fake also needs the kwarg. `grep -rn "def complete" llm/ tests/` to find every implementation.
- **Pydantic missing-vs-extra distinction.** Confirm that `extra="forbid"` does NOT reject a JSON line that omits a defaulted field. Pydantic v2 behavior is "forbid" applies only to unknown extra fields, not to missing-with-default fields. Verify with the backward-compat test.
- **Old replays' `LLMCallView.agent_id` is None everywhere.** ThoughtStream (4.8) consumes this; the 4.8 contract assumes None-handling. Document in 4.7's `## Decisions` so 4.8's implementing agent doesn't get blindsided.
- **`call_kind="trigger"` calls.** DESIGN.md §4.4 #3 describes triggered strategic calls (e.g., on body discovery). If those are wired today (verify with grep), the trigger call site also needs `agent_id=<the witnessing agent>`. If they're not wired today (Phase 3 may have only implemented meeting calls), skip them — but document in `## Decisions`.
- **No DTO leak surface widening.** `agent_id` is the game-internal agent id (e.g. `p-2`), which is already exposed via `PlayerView.agent_id`, `BallotView.voter`, etc. No new privilege surface; reviewer should confirm.
- **No real-provider call needed.** The protocol change is metadata-only; the Anthropic adapter ignores `agent_id`. Static tests + fake-LLM tests cover the change.
- **mypy strict reminder.** `llm/`, `meetings/`, `orchestrator/` are all in the strict list. The new parameter must be properly typed everywhere.
- **No CI cost.** No real-provider calls added.

**Ready-to-paste prompt:** `agent_prompts/task-4-7-llmcall-agent-id.md`

### Task 4.8 — ThoughtStream (per-agent memory + LLM call viewer)
**Branch:** `phase-4-thoughtstream`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.6 merged** (for App.tsx slot ordering) + **4.7 merged** (for per-call `agent_id` attribution)
**Section refs:** DESIGN.md §6, DESIGN.md §7
**Complexity:** Medium

Per-agent reasoning viewer. Spectator selects an agent (in addition
to a meeting); sees that agent's rendered memory view + every LLM
call that agent originated during the selected meeting. Memory comes
from the existing `AgentMemoryView` endpoint (cached in the store);
LLM calls come from `MeetingView.llm_calls` filtered by `agent_id`
(which 4.7 added).

**Privileged spectator note.** Per the 4.1 privilege model and the
mid-phase audit's Class A summary, the agent's `role` is
intentionally exposed in `AgentMemoryView.role` because the
spectator IS privileged (post-game replay). The `rendered_memory_
text` correctly carries only the *selected* agent's role, not other
agents' roles (cross-agent contamination check passed in both
audits). ThoughtStream therefore renders the role badge without
guarding — it's an authorized view by design.

**Meeting + agent selection coupling.** ThoughtStream is meaningful
only when BOTH `selectedMeetingId !== null` and `selectedAgentId
!== null`. When either is null, the panel renders a hint ("Open a
meeting and pick an agent to see their reasoning"). The
`AgentSelector` is the new affordance for picking — a button row
showing every player in `currentReplay.players` keyed by color
swatch + agent_id. Clicking selects that agent.

**Out of scope** (explicit decisions deferred):

- **Between-meeting memory.** MVP exposes `AgentMemoryView` only at
  meeting boundaries (4.1 decision). ThoughtStream therefore only
  shows memory snapshots paired with the currently-selected meeting.
  Per-tick memory streams are a Phase 5 concern.
- **Diff view between meetings.** "How did p-2's beliefs change
  between meeting 1 and meeting 2?" is a compelling feature but out
  of MVP scope — it would need cross-meeting state coordination.
- **LLM call rerun / replay.** No "re-run this prompt" button. The
  view is read-only.
- **Inline prompt-template source view.** The prompt_template_id is
  shown as text (e.g. `crewmate_report.v1`); a link to the
  underlying jinja2 template is out of scope.
- **Filter / search over many LLM calls.** A typical meeting has 12
  LLM calls (3 reports + 6 statements + 3 votes); too few to warrant
  search.

**Files in scope:**
- frontend/src/components/ThoughtStream.tsx
- frontend/src/components/AgentSelector.tsx
- frontend/src/components/MemoryPanel.tsx
- frontend/src/components/BeliefRow.tsx
- frontend/src/components/LLMCallCard.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (already has selectAgent + fetchMemoryView)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen — 4.7 added agent_id; 4.8 only consumes)
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx (lands in 4.6)
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
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
- [ ] **AgentSelector visible when `selectedMeetingId !== null`.** Renders one button per `currentReplay.players` entry. Each button: color swatch + `display_name` + `agent_id` + a small "(IMPOSTOR)" / "(CREWMATE)" badge in muted text (role is privileged-spectator info). Click → `selectAgent(agent_id)`. The selected button is visually highlighted. When `selectedMeetingId === null`, the selector is hidden.
- [ ] **ThoughtStream panel visible when both selections present.** Layout: AgentSelector at top, then MemoryPanel, then a divider, then the LLM call list. Panel docks to a side (right rail, ~30% viewport width) so MapView + MeetingView remain visible if open. Implementing agent picks layout; document.
- [ ] **MemoryPanel renders `AgentMemoryView`.** Fetched via `fetchMemoryView(meetingId, agentId)`; loading state shows a spinner; error state shows the cached error. Fields rendered: role badge, `tasks_completed / tasks_assigned` (formatted `7 / 12`), observations as a list (newest first, discriminated by `type`), beliefs as a `BeliefRow` per `BeliefEntryView` (subject + suspicion bar + confidence pill), open_contradictions as inline `ContradictionBadge` entries (component shared with 4.6 — implementing agent: if 4.6 already merged, reuse; otherwise define locally and refactor in a follow-up).
- [ ] **`rendered_memory_text` collapsible.** Below the structured memory: a `<details>` block (closed by default) labeled "Raw rendered memory (sent to LLM)". When expanded, shows the raw `rendered_memory_text` in a monospace preformatted block. Useful for debugging prompt-render decisions.
- [ ] **LLM call list filtered to agent.** `meeting.llm_calls.filter(c => c.agent_id === selectedAgentId)` — depends on 4.7. Render each remaining call as an `LLMCallCard`.
- [ ] **`LLMCallCard` content.** Header: `call_kind` chip + `model` + `prompt_template_id`. Stats row: input tokens, output tokens, `cost_usd` (formatted `$0.0042`). Prompt section: collapsible (closed by default), monospace preformatted, no truncation when expanded — first 200 chars shown when collapsed with a "show more" hint. Response section: same pattern.
- [ ] **Fallback for old replays without `agent_id`.** When `selectedAgentId !== null` but `meeting.llm_calls` contains entries with `agent_id === null` (pre-4.7 replays), render a single "Older replay — per-call agent attribution unavailable" notice instead of an empty list. Do not crash.
- [ ] **No new npm dependencies.** Reuse what 4.3/4.4/4.5/4.6 already pinned.
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: (a) AgentSelector visible with one agent highlighted, (b) ThoughtStream panel populated showing role badge, beliefs, and at least one expanded LLM call card with prompt + response visible.
- [ ] **Manual smoke documented.** PR description states the replay used (any of `replays/replay-seed-{22,24,26,49}.jsonl`), the meeting + agent selected, and confirms memory loads + at least 3 LLM calls render attributed to the picked agent.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

Memory fetch pattern using the existing store:

```tsx
export function ThoughtStream() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const agentId = useReplayStore((s) => s.selectedAgentId);
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);
  const replay = useReplayStore((s) => s.currentReplay);

  useEffect(() => {
    if (meetingId && agentId) fetchMemoryView(meetingId, agentId);
  }, [meetingId, agentId, fetchMemoryView]);

  if (!meetingId || !agentId) {
    return <Hint>Open a meeting and pick an agent to see their reasoning.</Hint>;
  }
  const memory = memoryCache[`${meetingId}:${agentId}`];
  if (!memory) return <Spinner />;
  const meeting = replay?.meetings.find((m) => m.meeting_id === meetingId);
  const calls = meeting?.llm_calls.filter((c) => c.agent_id === agentId) ?? [];

  return (
    <aside className="...">
      <RoleBadge role={memory.role} />
      <TaskProgress completed={memory.tasks_completed} assigned={memory.tasks_assigned} />
      <ObservationsList observations={memory.observations} />
      <BeliefsList beliefs={memory.beliefs} />
      <ContradictionsList contradictions={memory.open_contradictions} />
      <RenderedMemoryDetails text={memory.rendered_memory_text} />
      <LLMCallList calls={calls} agentId={agentId} meeting={meeting} />
    </aside>
  );
}
```

Belief row visualization — suspicion as a horizontal bar:

```tsx
function BeliefRow({ belief }: { belief: BeliefEntryView }) {
  return (
    <div className="flex items-center gap-2">
      <span className="font-mono">{belief.subject}</span>
      <div className="flex-1 h-2 bg-neutral-700 rounded">
        <div
          className="h-full rounded"
          style={{
            width: `${belief.suspicion * 100}%`,
            background: belief.suspicion > 0.5 ? "var(--color-red)" : "var(--color-green)",
          }}
        />
      </div>
      <span className="text-xs text-neutral-400">{belief.suspicion.toFixed(2)}</span>
    </div>
  );
}
```

LLM call collapsible content — use native `<details>` to avoid managing open/closed state:

```tsx
function LLMCallCard({ call }: { call: LLMCallView }) {
  return (
    <div className="border rounded p-2 my-2">
      <header>...stats...</header>
      <details>
        <summary>Prompt ({truncate(call.prompt_text, 80)})</summary>
        <pre className="whitespace-pre-wrap">{call.prompt_text}</pre>
      </details>
      <details>
        <summary>Response ({truncate(call.response_text, 80)})</summary>
        <pre className="whitespace-pre-wrap">{call.response_text}</pre>
      </details>
    </div>
  );
}
```

For the contradiction badge shared with 4.6: if 4.6's `ContradictionBadge` component already exists at merge time, import and reuse. If 4.6 has not yet merged, define a local copy and note in `## Decisions` that a refactor follow-up will deduplicate. Don't block on inter-task ordering — both tasks can dispatch in parallel after 4.7 and the audit clear.

**Public types introduced:**
None.

**Integration risk:**

This task adds five components and depends on 4.7 having landed. The risks are around the AgentMemoryView fetch lifecycle and the LLM-call filtering.

- **`fetchMemoryView` race.** The store already guards against stale responses (per 4.3's third Codex review). If the user rapidly switches agents, the latest fetch wins; the cache only holds the winning result. Verify by selecting agents in quick succession.
- **Hard dependency on 4.7.** If 4.7 is not merged when 4.8 dispatches, LLM call filtering produces an empty list for every agent. The "fallback for old replays" UI catches this case too — but the contract dependency is real. Confirm in `## Decisions` that 4.7 was merged before this PR opens.
- **Contradiction badge duplication.** If 4.6 also defines a `ContradictionBadge`, both tasks ship one. The first one merged wins; the second's PR review should flag the conflict and refactor in-PR. Acceptable churn for parallel dispatch.
- **Role badge in privileged view.** Showing "IMPOSTOR" badges in the AgentSelector reveals roles to the spectator — that's intentional per the 4.1 privilege model. Document in PR description that this is a known-and-authorized leak for the post-game spectator surface.
- **Long prompt_text rendering.** Some prompts are 8k+ characters. `<pre>` with `whitespace-pre-wrap` handles wrap; ensure a `max-h` + scroll on the expanded `<details>` so a single prompt doesn't crowd out the rest of the panel.
- **No backend changes.** All fields consumed exist post-4.7.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-8-thoughtstream.md`

### Task 4.9 — BeliefEntryView snapshot_tick rename (R-2 substrate)
**Branch:** `phase-4-belief-snapshot-tick`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.7 merged** (shared edits to `api/schemas.py`, `api/replay_loader.py`, TS types, and DTO test fixtures — serialize to avoid merge churn)
**Section refs:** DESIGN.md §6.3, mid-phase DTO audit R-2
**Complexity:** Small

Mid-phase DTO audit R-2 informational finding (Unique-but-verified):
`api.schemas.BeliefEntryView.last_updated_tick` is the enclosing
meeting boundary tick, not a per-belief mutation timestamp. Every
row in a snapshot carries the same value, which will mislead
`BeliefMatrix` (4.10) if its component reads `last_updated_tick`
as a recency signal. The audit reconciler explicitly framed this as
"before Task 4.10 dispatch" — this task is the prereq.

**Why a rename, not a real recency wire.** Two options were on the
table:

1. **Rename `last_updated_tick` → `snapshot_tick`.** Cheap, honest,
   one PR. Documents the field's actual semantics (the tick at
   which the spectator API took the snapshot). Does NOT change
   `agents.memory.beliefs.PlayerBelief` — beliefs remain immutable
   snapshots that don't carry per-mutation timestamps.

2. **Wire a real per-belief recency** through `PlayerBelief`.
   Requires adding `last_updated_tick` to the belief store,
   threading a tick parameter through every mutation site
   (`adjust_suspicion`, `adjust_trust`, `record_alibi`,
   `record_contradiction`, `decay_suspicion`), updating all callers
   in `agents/` and `meetings/`, plus the loader propagation.
   Multi-file repair task, ~5x the surface area.

This task picks Option 1. The semantic question that motivated R-2
("a BeliefMatrix shouldn't claim per-cell recency it doesn't have")
is fully resolved by the rename — 4.10's contract notes that
`snapshot_tick` is per-meeting, not per-cell, and renders it once
in the footer ("all beliefs as of meeting tick N") rather than
per-cell. If Phase 5 decides per-belief recency adds product
value, that's a separate scoped task — not this one.

**Out of scope** (explicit decisions deferred):

- **`PlayerBelief` schema changes.** No change. The belief store
  stays timeless.
- **Belief mutation tick parameter threading.** Not done. See
  rationale above.
- **`AgentMemoryView` tick semantics.** Already clear (`tick` is
  the meeting boundary tick). No change.
- **TypeScript codegen.** Frontend types are hand-authored; this
  task hand-edits one line in `frontend/src/types/api.ts`.

**Files in scope:**
- api/schemas.py
- api/replay_loader.py
- frontend/src/types/api.ts
- tests/api/test_schemas.py
- tests/api/test_replay_loader.py
- tests/api/test_replays.py
- tests/api/fixtures/sample_replay.py

**Files NOT in scope:**
- engine/
- agents/ (PlayerBelief is NOT modified)
- llm/
- meetings/
- observation/
- orchestrator/
- frontend/src/components/
- frontend/src/store/replayStore.ts
- frontend/src/api/client.ts
- frontend/package.json
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

**Definition of done:**
- [ ] **`BeliefEntryView.last_updated_tick` renamed to `snapshot_tick`.** [api/schemas.py:410](api/schemas.py#L410). Docstring updated to: "Meeting boundary tick at which this belief snapshot was taken. Beliefs themselves are timeless; this field timestamps when the spectator API observed the belief, not when the belief mutated. All BeliefEntryView entries within one AgentMemoryView share the same snapshot_tick."
- [ ] **Loader updated.** [api/replay_loader.py:1119](api/replay_loader.py#L1119) constructs `BeliefEntryView(snapshot_tick=tick, ...)` — field-name rename only; the `tick` parameter pass-through is unchanged.
- [ ] **Frontend types mirror.** [frontend/src/types/api.ts:275](frontend/src/types/api.ts#L275) renames `last_updated_tick: number` → `snapshot_tick: number`.
- [ ] **Test updates.** Every test that references `last_updated_tick` is updated. Grep `grep -rn "last_updated_tick" tests/` to find them; expect them in [tests/api/test_schemas.py](tests/api/test_schemas.py), [tests/api/test_replay_loader.py](tests/api/test_replay_loader.py), [tests/api/test_replays.py](tests/api/test_replays.py), and possibly [tests/api/fixtures/sample_replay.py](tests/api/fixtures/sample_replay.py).
- [ ] **No code outside the files-in-scope references `last_updated_tick`.** Confirm with `grep -rn "last_updated_tick" .` after edits; only `audits/` (historical) and possibly `tasks/phase-4.md` (this task's own description) should still contain the string.
- [ ] **`extra="forbid"` confirms strict rejection.** A test asserts that constructing `BeliefEntryView(last_updated_tick=5, ...)` (the OLD field name) raises a Pydantic validation error. This documents the rename.
- [ ] **DTO leak test updated if it references the field.** [tests/api/test_leak.py](tests/api/test_leak.py)'s `EXPECTED_DTOS` is field-list-agnostic per the 4.1 design — no edit expected. Confirm by running.
- [ ] **No backend semantics change.** No new endpoint; no new field elsewhere; the loader still pulls from the same per-meeting tick.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

Step 1 — Rename in `api/schemas.py`. Update the docstring to describe the semantics clearly.

Step 2 — Rename in `api/replay_loader.py`. The constructor call is the only loader site touching this field.

Step 3 — Rename in `frontend/src/types/api.ts`. One-line edit.

Step 4 — Search-and-update tests:

```bash
grep -rln "last_updated_tick" tests/ frontend/
```

Step 5 — Add the strict-rejection test:

```python
def test_belief_entry_rejects_old_field_name() -> None:
    with pytest.raises(ValidationError):
        BeliefEntryView(
            subject="p-2",
            suspicion=0.7,
            confidence=0.4,
            last_updated_tick=5,  # old name
        )
```

This guards against any consumer that didn't get the rename memo.

Step 6 — Verify no leftover references outside `audits/` and the task contract:

```bash
grep -rn "last_updated_tick" . --exclude-dir=audits --exclude-dir=node_modules
```

**Public types introduced:**
None — this is a field rename on an existing type. The schema delta:

- `api.schemas.BeliefEntryView.snapshot_tick` (renamed from `last_updated_tick`)

**Integration risk:**

The smallest task in Phase 4. Risk is in missing a reference.

- **Old replays in the cache.** Replays are loaded fresh on process restart, so a renamed field doesn't break the cache — but any process running the OLD code reading a NEW JSONL produced by NEW code wouldn't see the field. Since the field is constructed at DTO-build time (not persisted to JSONL), this isn't a concern: the rename touches only the in-memory DTO shape.
- **4.10's dependency.** BeliefMatrix (4.10) reads `snapshot_tick` per the elaborated 4.10 contract. Confirm 4.10 dispatches after 4.9 merges (already encoded in the dependency line).
- **Documentation consistency.** The `## Decisions` section of the PR should explicitly state "We chose rename over per-belief recency wiring; rationale in tasks/phase-4.md Task 4.9."
- **No backend behavior change.** No new endpoint. No engine touch. No observation-firewall implication.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-9-belief-snapshot-tick.md`

### Task 4.10 — BeliefMatrix (who-suspects-whom heatmap)
**Branch:** `phase-4-beliefmatrix`
**Depends on:** 4.4 merged + mid-phase DTO audit passed + **4.8 merged** (App.tsx slot ordering) + **4.9 merged** (for `snapshot_tick` field rename)
**Section refs:** DESIGN.md §6.3, DESIGN.md §7
**Complexity:** Medium

N×N heatmap of who suspects whom at a meeting boundary. Rows are
observers, columns are subjects, cell color encodes suspicion
intensity (green→yellow→red). Derived client-side from per-agent
`AgentMemoryView` snapshots; the BeliefMatrix is visible only when
a meeting is selected, mirroring ThoughtStream's meeting-boundary
constraint.

**Why meeting-boundary-only, not per-tick.** The mid-phase DTO
audit's Section 6 substrate report confirmed `SuspicionGraphView`
is a declared DTO with NO endpoint today. Two paths existed:

1. **Add a backend endpoint** (`GET /replays/{game_id}/suspicion/
   {tick}`) that walks all agents' belief stores per-tick and
   serializes the graph. Widens 4.10 into a backend-and-frontend
   task; adds a loader method; touches `api/routes/`, `api/replay_
   loader.py`, and `api/schemas.py` (the SuspicionGraphView DTO
   already exists). Costs: ~3x the task surface; introduces
   per-tick memory reconstruction outside meeting boundaries
   (currently the loader only reconstructs at meeting boundaries
   per the substrate audit).

2. **Derive client-side from per-agent `AgentMemoryView`** fetched
   at the currently-selected meeting boundary. Each agent's
   `AgentMemoryView.beliefs[*]` already carries `(subject,
   suspicion, confidence, snapshot_tick)`. Aggregating N agents'
   beliefs gives the full N×N matrix at that meeting. No backend
   changes; reuses the existing `fetchMemoryView` action and
   memory cache.

This task picks Option 2 — keeps the scope at
`frontend/src/components/`, no backend touch. Per-tick coverage is
a Phase 5 expansion if the UX session shows it matters; meeting-
boundary coverage is sufficient for the merge gate (a non-technical
viewer following a game can see the suspicion landscape at every
decision point — i.e., every meeting).

**Out of scope** (explicit decisions deferred):

- **Per-tick suspicion graphs.** Per the design choice above.
- **Trust matrix variant.** DESIGN.md §6.3 distinguishes trust and
  suspicion as separate scores. The MVP heatmap renders suspicion
  only; a trust matrix is a Phase 5 expansion if useful.
- **Belief-edge animation between meetings.** A "watch beliefs
  shift from meeting 1 to meeting 2" view is compelling but out of
  scope.
- **Cell click → ThoughtStream pivot.** Clicking a cell could
  select the row agent and jump to ThoughtStream. Nice-to-have; out
  of MVP scope. Pivot via existing AgentSelector + BeliefMatrix
  side-by-side is fine.

**Files in scope:**
- frontend/src/components/BeliefMatrix.tsx
- frontend/src/components/BeliefCell.tsx
- frontend/src/App.tsx

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/
- frontend/src/store/replayStore.ts (uses existing fetchMemoryView)
- frontend/src/api/client.ts (frozen)
- frontend/src/types/api.ts (frozen — 4.9 already renamed the field)
- frontend/src/components/MapView.tsx
- frontend/src/components/MeetingView.tsx (lands in 4.6)
- frontend/src/components/ThoughtStream.tsx (lands in 4.8)
- frontend/src/components/AgentSelector.tsx (lands in 4.8 — reuse if available)
- frontend/src/components/RoomRect.tsx
- frontend/src/components/AgentToken.tsx
- frontend/src/components/ReplayPicker.tsx
- frontend/src/components/TickStepper.tsx
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
- [ ] **BeliefMatrix visible when `selectedMeetingId !== null`.** When the selection is null, the panel renders nothing (or a small hint similar to ThoughtStream's). Mounted in App.tsx alongside (or below) MeetingView / ThoughtStream depending on layout.
- [ ] **Per-agent memory fetch on mount + selection change.** For every `agent_id` in `currentReplay.players`, call `fetchMemoryView(selectedMeetingId, agent_id)` via the existing store action. The store caches and dedupes; subsequent renders hit the cache. Use a single `useEffect` keyed on `selectedMeetingId`.
- [ ] **Render the N×N matrix.** Rows: each player in `currentReplay.players`. Columns: same. Top row + left column: player color swatch + agent_id labels. Diagonal cell (observer = subject): blank or muted (an agent has no belief about itself).
- [ ] **Cell color encodes suspicion.** For row `i`, column `j` (i ≠ j): look up the row agent's `AgentMemoryView.beliefs.find(b => b.subject === players[j].agent_id)`. If found: cell color = a deterministic mapping of `suspicion ∈ [0,1]` to a heat scale. Recommended: HSL with hue = `120 - 120*suspicion` (green at 0, yellow at 0.5, red at 1.0); lightness adjustable by `confidence`. If not found (no belief recorded): cell is grey/empty.
- [ ] **Cell hover tooltip.** Hovering a cell shows `observer → subject: suspicion=0.72 (confidence=0.44)`. Use a simple title attribute or a Tailwind tooltip pattern (no new dependency).
- [ ] **Snapshot footer.** Below the matrix: a single line "All beliefs as of meeting tick N" derived from the snapshot_tick (4.9). All snapshot_tick values across all rendered cells are identical by construction; assert this in a defensive check (`new Set(allTicks).size === 1`) and log a warning if violated (data integrity hint).
- [ ] **Loading + partial states.** Until all N memory fetches resolve, render a loading state (e.g. "Loading agent memories..."). If any fetch errors, render the matrix with grey cells for missing rows and an error chip near the affected agent's label.
- [ ] **No new npm dependencies.** React 19, Zustand 5, Tailwind v4 are sufficient.
- [ ] **TypeScript strict.** No `any`, no `// @ts-ignore`.
- [ ] **`npm run build` succeeds** with zero warnings.
- [ ] **Screenshots attached to PR.** Minimum: BeliefMatrix populated for a meeting from a real replay, showing varied suspicion across cells (green/yellow/red distribution) and the snapshot tick footer.
- [ ] **Manual smoke documented.** PR description states the replay used and the meeting selected, and confirms the matrix populates with no console errors. Mention any cells that were grey (no belief recorded) so reviewers know that's the expected sparse state.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

The matrix is a CSS grid (or a simple table). Pure React + Tailwind; no PixiJS.

Fetching pattern — orchestrate N parallel fetches via the store:

```tsx
export function BeliefMatrix() {
  const meetingId = useReplayStore((s) => s.selectedMeetingId);
  const replay = useReplayStore((s) => s.currentReplay);
  const memoryCache = useReplayStore((s) => s.memoryCache);
  const fetchMemoryView = useReplayStore((s) => s.fetchMemoryView);

  const players = replay?.players ?? [];

  useEffect(() => {
    if (!meetingId) return;
    for (const p of players) fetchMemoryView(meetingId, p.agent_id);
  }, [meetingId, players, fetchMemoryView]);

  if (!meetingId) return null;
  const memories = players.map((p) => memoryCache[`${meetingId}:${p.agent_id}`]);
  if (memories.some((m) => !m)) return <Loading />;

  return <Matrix players={players} memories={memories} />;
}
```

Cell rendering with HSL heat:

```tsx
function BeliefCell({ observer, subject, belief }: Props) {
  if (observer.agent_id === subject.agent_id) {
    return <div className="bg-neutral-800" />;  // diagonal
  }
  if (!belief) {
    return <div className="bg-neutral-700" title="no belief recorded" />;
  }
  const hue = 120 - 120 * belief.suspicion;          // 120=green, 0=red
  const lightness = 30 + 20 * belief.confidence;     // more confident → lighter
  return (
    <div
      className="w-8 h-8 cursor-help"
      style={{ background: `hsl(${hue}, 70%, ${lightness}%)` }}
      title={`${observer.agent_id} → ${subject.agent_id}: suspicion=${belief.suspicion.toFixed(2)} (conf=${belief.confidence.toFixed(2)})`}
    />
  );
}
```

Belief lookup per `(observer, subject)` pair:

```typescript
function lookupBelief(memory: AgentMemoryView, subjectId: string) {
  return memory.beliefs.find((b) => b.subject === subjectId);
}
```

Defensive snapshot-tick check:

```typescript
const snapshotTicks = memories.flatMap((m) => m.beliefs.map((b) => b.snapshot_tick));
if (new Set(snapshotTicks).size > 1) {
  console.warn("BeliefMatrix: snapshot_tick values diverge across cells", snapshotTicks);
}
const footerTick = memories[0]?.tick ?? "?";
```

`memories[0].tick` is the AgentMemoryView's tick (always the meeting tick) — equivalent to snapshot_tick across all beliefs in this view; use it for the footer.

**Public types introduced:**
None.

**Integration risk:**

The risk is in the multi-agent fetch coordination and in unstated assumptions about belief population density.

- **Multi-agent fetch fan-out.** For N=4 players, 4 parallel API calls on meeting select. With the loader's LRU cache (4.2), repeat selections of the same meeting are instant. First-load cost scales with N.
- **Sparse belief data.** If an agent hasn't recorded a belief about another agent (e.g. early-game with no observation), the lookup returns undefined and the cell renders grey. Make sure the loading state distinguishes "not yet fetched" (still loading) from "fetched but empty" (sparse data). The `memoryCache[key] === undefined` check covers the former.
- **snapshot_tick semantics.** Per 4.9's clarification, snapshot_tick is per-snapshot not per-belief — all cells in the matrix carry the same value. The footer renders it once; cells don't repeat the tick in tooltips (it would be visual noise).
- **Color choice and accessibility.** Green→yellow→red is the conventional heat scale but is hostile to red-green colorblind viewers. Recommend including the numeric value in the tooltip (already in the DoD) so the color is supplementary, not load-bearing. If the UX session flags an issue, the polish task is a colorblind-safe palette swap.
- **Diagonal styling.** The diagonal must visibly differ from "no belief recorded" — both are empty cells but mean different things. Use a distinct styling (e.g. striped or darker shade) for the diagonal.
- **No backend changes.** Per the design choice; document the per-tick alternative in `## Decisions` as a flagged future direction.
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-10-beliefmatrix.md`

### Task 4.11 — ReplayControls (scrubber, speed, play/pause, snap-to-meeting)
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


**Implementation hint:**

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

**Public types introduced:**
None.

**Integration risk:**

The risk is in `setInterval` lifecycle bugs — the classic "stale closure" and "compound intervals" failure modes.

- **Stale closure on `currentTick`.** Reading `currentTick` from the React closure inside the interval freezes it. Use `useReplayStore.getState().currentTick` for fresh reads. The sketch above shows the pattern.
- **Compound intervals.** If the `useEffect` deps include `currentTick` and the effect re-registers on every tick, two intervals end up running. The DoD's deps list `[isPlaying, playbackSpeed, replay]` deliberately omits `currentTick`. Verify by toggling play and watching the network tab or console (advance should be steady, not accelerating).
- **Cleanup on unmount.** Always return the `clearInterval` cleanup. React Strict Mode double-renders the effect in dev; cleanup must be idempotent.
- **Scrubber + auto-advance race.** If the user scrubs while playing, the next interval tick may advance from the new position immediately (which is correct). Pause-on-scrub is a UX call — recommend NOT pausing on scrub (the user can pause explicitly). Document the choice.
- **Snap-to-meeting also-selects-meeting interaction.** The "next meeting" button calls both `setCurrentTick` and `selectMeeting`. The latter opens MeetingView (from 4.6). If 4.6 hasn't merged when 4.11 dispatches, `selectMeeting` is a no-op visually — but the store action is still safe (no-op on undefined component). Test order doesn't matter.
- **Last-tick play stop.** When playback reaches the last tick, `setIsPlaying(false)` fires. The play button then shows "play" again and clicking it tries to advance from the last tick — which the auto-advance immediately stops again (correct). UX-wise, consider showing the play button as disabled when at the last tick.
- **Range input native styling.** Tailwind's `range` plugin is optional; without it, native browser styling shows. Acceptable for MVP. If the UX session flags it as ugly, that's a polish PR.
- **No backend changes.**
- **No CI cost.** Static gates only.

**Ready-to-paste prompt:** `agent_prompts/task-4-11-replaycontrols.md`

### Task 4.12 — Easy setup for non-technical users
**Branch:** `phase-4-easy-setup-script`
**Depends on:** 4.11 merged
**Section refs:** DESIGN.md §7, DESIGN.md §9
**Complexity:** Small

Phase 4 is structurally complete: API + DTO inventory + replay loader +
React/Vite/Tailwind/PixiJS frontend + MapView (slice + full) +
MeetingView + ThoughtStream + BeliefMatrix + ReplayControls all
merged, mid-phase DTO audit passed, two audit-derived substrate fixes
(4.7, 4.9) landed clean. The only thing standing between the current
state and the Phase-closing UX acceptance session is the setup
friction: today a non-technical viewer needs to type three commands
across two terminals plus one env var to see the dashboard. This task
collapses that to one command and commits real-provider sample replays
so cloning the repo gives immediate viewable substrate.

Current flow (today):

```bash
bash scripts/setup_env.sh                                           # 1
AILIBI_REPLAY_DIR=./replays uv run uvicorn api.main:app             # 2 (terminal A)
cd frontend && npm run dev                                          # 3 (terminal B)
# then manually open http://localhost:5173
```

Target flow (after this task):

```bash
bash scripts/setup_env.sh                                           # 1 (one-time)
bash scripts/run_spectator.sh                                       # 2 (every time)
# browser opens automatically to a populated replay list
```

The single-command path is the load-bearing UX claim of Phase 4 —
"non-technical viewer can follow a saved replay end-to-end without
reading logs." If setup itself requires reading logs, the claim is
weaker. This task removes that contradiction.

**Real-provider sample replays.** The 50 `replay-seed-*.jsonl` files
at `/tmp/eval-50/` are the actual Phase 3 closing eval evidence (50/50
games, 38% impostor win rate, $0.018 mean cost, $0.886 total spend).
They cannot be cheaply regenerated — re-running the tournament costs
~$1 against the live Anthropic API, and Sonnet 4.6 may drift over
time, so the recorded transcripts are a frozen historical artifact.
Committing them to `replays/samples/` preserves the evidence and gives
cloners immediate substrate without paying for regeneration. Total
size: ~1.6 MB across 50 files; well under any GitHub threshold.

**Out of scope** (explicit decisions deferred):

- **Docker / docker-compose.** DESIGN.md §7 names docker-compose as
  a future option for "Postgres + api + frontend up with one command."
  Adding it would be ~2 hours additional lift and a new dependency
  surface. Defer to Phase 5+ if non-tech users hit native-dependency
  install friction with `uv` and `npm`.
- **Windows support.** macOS + Linux only for this script. Windows
  has different shell, different process management, different
  package manager idioms; bash script targeting cmd/PowerShell is
  a different task. Document Windows as unsupported in the script's
  leading comment.
- **Auto-install of dependencies.** If `uv` or `frontend/node_modules`
  is missing, the script prints a one-line pointer to
  `bash scripts/setup_env.sh` and exits non-zero. It does NOT
  auto-invoke setup_env.sh — installing dependencies without explicit
  consent is a footgun. (User-decided default 2026-05-27 in the
  design thread.)
- **Including `.audit.jsonl` files in the commit.** Those are internal
  leak-test packet logs from the observation firewall infrastructure,
  not user-facing artifacts. Excluded from `replays/samples/` and
  globally gitignored via `**/*.audit.jsonl`.
- **Process supervisor / systemd / launchd integration.** This is a
  dev-loop convenience script, not a production runner. Foreground
  bash with trap-on-EXIT cleanup is sufficient.

**Files in scope:**
- scripts/run_spectator.sh
- api/main.py
- tests/api/test_replay_dir_fallthrough.py
- README.md
- .gitignore
- replays/samples/replay-seed-0.jsonl … replays/samples/replay-seed-49.jsonl (50 files copied from /tmp/eval-50/; do NOT regenerate them — copy the existing artifacts to preserve their real-provider provenance)

**Files NOT in scope:**
- engine/
- agents/
- llm/
- meetings/
- observation/
- orchestrator/
- api/schemas.py (DTOs frozen at 4.1)
- api/replay_loader.py (loader behavior frozen at 4.2; only the env-var resolution in main.py changes)
- api/routes/
- frontend/
- DESIGN.md
- AGENT_IMPLEMENTATION.md
- AGENTS.md
- pyproject.toml
- uv.lock
- tasks/
- agent_prompts/
- audits/
- open_issues.md
- scripts/setup_env.sh (consumed; not modified)
- scripts/check.sh (consumed; not modified)
- scripts/run_game.py
- scripts/run_tournament.py
- scripts/generate_prompts.py
- scripts/validate_task_docs.py
- tests/agents/
- tests/engine/
- tests/llm/
- tests/meetings/
- tests/observation/
- tests/orchestrator/
- tests/eval/
- tests/api/test_schemas.py
- tests/api/test_routes.py
- tests/api/test_leak.py
- tests/api/test_replay_loader.py
- tests/api/test_replays.py
- tests/api/test_eval.py
- tests/test_firewall.py
- frontend/src/
- frontend/package.json (locked at 4.3; no new deps)

**Definition of done:**
- [ ] **`replays/samples/` committed.** All 50 `replay-seed-*.jsonl` files copied from `/tmp/eval-50/`. NO `.audit.jsonl` files committed.
- [ ] **If `/tmp/eval-50/` is missing, do NOT regenerate.** Stop and report to the user. The artifacts must be located elsewhere (other scratch dir, backup, or the user's archive). Re-running the tournament against the live Anthropic API costs ~$1 AND produces non-identical transcripts (Sonnet 4.6 temperature > 0 + possible model drift), which destroys the Phase 3 evidence chain documented in [audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md](audits/audit-2026-05-26-0325-pre-phase-4-real-provider-eval.md). This is the most expensive failure mode for this task; treat the guardrail seriously.
- [ ] **`.gitignore` updated.** Three additions: `replays/*.jsonl` (user-generated replays in the parent dir are ignored), `!replays/samples/` (negation so committed samples survive), `**/*.audit.jsonl` (internal leak-test logs ignored everywhere).
- [ ] **`api/main.py` fallthrough resolution.** The `AILIBI_REPLAY_DIR` resolution at [api/main.py:16-17](api/main.py#L16) falls through in this priority order: (1) `$AILIBI_REPLAY_DIR` if set and non-empty, (2) `./replays/` if exists and contains at least one `replay-seed-*.jsonl` file, (3) `./replays/samples/` if exists and contains at least one matching file. If none resolve, fail with a clear startup error naming all three paths and suggesting `bash scripts/run_spectator.sh` or `uv run python scripts/run_game.py`.
- [ ] **Startup log of the resolved replay dir.** On successful resolution, `api/main.py` logs one line to stderr (or stdout via the FastAPI/uvicorn logger): `Serving replays from <resolved-path> (<N> replay-seed-*.jsonl found).`. This makes the slot-that-won visible whenever the developer mixes locally-generated replays in `./replays/` with the committed samples in `./replays/samples/` — without it, "why is the UI showing different replays than I expected?" is a silent guessing game.
- [ ] **Unit test `tests/api/test_replay_dir_fallthrough.py`** covers all four resolution paths: env var set, env var unset with `./replays/` populated, env var unset with only `./replays/samples/` populated, all three empty (asserts the error message). Uses pytest `tmp_path` + `monkeypatch` for filesystem isolation.
- [ ] **`scripts/run_spectator.sh` exists and is executable** (`chmod +x` recorded in the commit; verify with `git ls-files --stage scripts/run_spectator.sh`). The script does all of:
  - Print platform check: macOS + Linux supported; print warning and exit on other uname output.
  - Check `command -v uv >/dev/null` and `[ -d frontend/node_modules ]`. If either fails, print `Run bash scripts/setup_env.sh first.` and exit 1. Do NOT invoke setup_env.sh.
  - Check ports 8000 and 5173 are free (`lsof -nP -iTCP:8000 -sTCP:LISTEN`). If bound, print the PID and a `kill <pid>` suggestion, exit 1.
  - Start the API in the background: `uv run uvicorn api.main:app --port 8000 2>&1 | sed 's/^/[api] /' &` and capture the PID.
  - Start the frontend in the background: `(cd frontend && npm run dev) 2>&1 | sed 's/^/[ui] /' &` and capture the PID.
  - Trap on EXIT / INT / TERM: kill both PIDs.
  - Health-check loop: poll `curl -fsS http://localhost:8000/ >/dev/null 2>&1` until 200 or ~30s elapsed. Same for frontend at `http://localhost:5173/`. Print one progress line per second to stderr.
  - On both healthy: print `Open http://localhost:5173 in your browser.` Then attempt platform browser-open: `open` (macOS), `xdg-open` (Linux), fall back to printing-only on failure.
  - Print `Press Ctrl-C to stop.` on the line immediately after the open-in-browser message. Many users won't realize the script is foregrounded and will wonder why their terminal "froze" — this one line removes the confusion.
  - Wait on both child PIDs so the script stays in the foreground until Ctrl-C.
- [ ] **README "Watch a replay" section rewritten.** Collapse the 4-step block to 1 command. Add one paragraph describing what the user will see (50 sample replays from the Phase 3 closing eval, scrubber for ticks, meeting transcripts with ballots and contradictions, per-agent memory snapshots, suspicion heatmap). Keep the existing "Reproduce a game" determinism section unchanged.
- [ ] **Fresh-clone smoke test.** In a sibling directory: `git clone . ../ailibi-smoke && cd ../ailibi-smoke && bash scripts/setup_env.sh && bash scripts/run_spectator.sh`. Confirm the browser opens to a populated replay list with 50 entries. Paste terminal output (last ~30 lines) into `## Decisions` of the PR description.
- [ ] No imports from `engine/` under `agents/`, `llm/`, or `meetings/` (firewall preserved). `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (new fallthrough test included).
- [ ] `uv run mypy .` passes.
- [ ] `uv run mypy --strict agents observation orchestrator engine llm meetings` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `bash scripts/check.sh` passes locally.


**Implementation hint:**

The script's tricky part is process lifecycle. Naive backgrounding leaves orphan API/frontend processes when the user hits Ctrl-C; ports stay bound; next run fails the port-in-use check. The pattern that works:

```bash
#!/usr/bin/env bash
# scripts/run_spectator.sh — illustrative

set -euo pipefail

# Platform check
case "$(uname -s)" in
  Darwin|Linux) ;;
  *) echo "Unsupported platform: $(uname -s). macOS + Linux only." >&2; exit 1 ;;
esac

# Dependency check
if ! command -v uv >/dev/null 2>&1 || [ ! -d frontend/node_modules ]; then
  echo "Run bash scripts/setup_env.sh first." >&2
  exit 1
fi

# Port check
for port in 8000 5173; do
  if lsof -nP -iTCP:"$port" -sTCP:LISTEN >/dev/null 2>&1; then
    pid=$(lsof -nP -iTCP:"$port" -sTCP:LISTEN -t)
    echo "Port $port already in use by PID $pid. Run: kill $pid" >&2
    exit 1
  fi
done

# Process tracking
api_pid=""
ui_pid=""
cleanup() {
  [ -n "$api_pid" ] && kill "$api_pid" 2>/dev/null || true
  [ -n "$ui_pid" ] && kill "$ui_pid" 2>/dev/null || true
  wait 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Start API + frontend with prefixed logs
uv run uvicorn api.main:app --port 8000 2>&1 | sed 's/^/[api] /' &
api_pid=$!
(cd frontend && npm run dev) 2>&1 | sed 's/^/[ui] /' &
ui_pid=$!

# Health check loop
wait_for() {
  local url="$1" name="$2" elapsed=0
  while [ "$elapsed" -lt 30 ]; do
    if curl -fsS "$url" >/dev/null 2>&1; then return 0; fi
    sleep 1
    elapsed=$((elapsed + 1))
    echo "  waiting for $name ($elapsed s)..." >&2
  done
  echo "$name failed to respond at $url within 30s" >&2
  return 1
}

wait_for "http://localhost:8000/" "api" || exit 1
wait_for "http://localhost:5173/" "ui" || exit 1

echo "Open http://localhost:5173 in your browser."
echo "Press Ctrl-C to stop."
case "$(uname -s)" in
  Darwin) open "http://localhost:5173" 2>/dev/null || true ;;
  Linux)  xdg-open "http://localhost:5173" 2>/dev/null || true ;;
esac

# Wait for foreground exit
wait "$api_pid" "$ui_pid"
```

For the API fallthrough in `api/main.py`, the current state at [api/main.py:16-17](api/main.py#L16) is a simple env-or-default. The new shape (illustrative):

```python
# api/main.py — illustrative
ENV_REPLAY_DIR: Final[str] = "AILIBI_REPLAY_DIR"
_FALLBACK_PATHS: Final[tuple[Path, ...]] = (
    Path("./replays"),
    Path("./replays/samples"),
)


def _resolve_replay_dir() -> Path:
    explicit = os.environ.get(ENV_REPLAY_DIR, "").strip()
    if explicit:
        return _announce(Path(explicit))

    for candidate in _FALLBACK_PATHS:
        if candidate.is_dir() and any(candidate.glob("replay-seed-*.jsonl")):
            return _announce(candidate)

    raise RuntimeError(
        f"No replays found. Tried: ${ENV_REPLAY_DIR}, "
        f"{_FALLBACK_PATHS[0]!s}, {_FALLBACK_PATHS[1]!s}. "
        f"Run `bash scripts/run_spectator.sh` or "
        f"`uv run python scripts/run_game.py --seed 0 --replay-path replays/replay-seed-0.jsonl`."
    )


def _announce(path: Path) -> Path:
    count = sum(1 for _ in path.glob("replay-seed-*.jsonl"))
    print(f"Serving replays from {path} ({count} replay-seed-*.jsonl found).",
          file=sys.stderr)
    return path
```

The unit test isolates filesystem via `tmp_path` + `monkeypatch`:

```python
# tests/api/test_replay_dir_fallthrough.py — illustrative
def test_env_var_takes_precedence(tmp_path, monkeypatch):
    explicit = tmp_path / "custom"
    explicit.mkdir()
    monkeypatch.setenv("AILIBI_REPLAY_DIR", str(explicit))
    monkeypatch.chdir(tmp_path)
    assert _resolve_replay_dir() == explicit

def test_falls_through_to_replays_dir(tmp_path, monkeypatch):
    monkeypatch.delenv("AILIBI_REPLAY_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    replays = tmp_path / "replays"
    replays.mkdir()
    (replays / "replay-seed-0.jsonl").write_text("{}")
    assert _resolve_replay_dir() == Path("replays")

def test_falls_through_to_samples(tmp_path, monkeypatch):
    monkeypatch.delenv("AILIBI_REPLAY_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    samples = tmp_path / "replays" / "samples"
    samples.mkdir(parents=True)
    (samples / "replay-seed-22.jsonl").write_text("{}")
    assert _resolve_replay_dir() == Path("replays/samples")

def test_all_empty_raises(tmp_path, monkeypatch):
    monkeypatch.delenv("AILIBI_REPLAY_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(RuntimeError, match="No replays found"):
        _resolve_replay_dir()
```

For the README rewrite, the new "Watch a replay" section structure (illustrative — preserve the leading "The spectator UI reads saved replay JSONL files..." sentence if it still fits):

```markdown
## Watch a replay

```bash
bash scripts/setup_env.sh        # one-time dependency install
bash scripts/run_spectator.sh    # starts API + UI, opens browser
```

The repo ships with 50 sample replays from the Phase 3 closing
real-provider eval (`replays/samples/`). The dashboard renders each
game tick by tick: agents moving room to room, meeting transcripts
with reports + accusation rounds + ballots, contradiction flags
inline, per-agent memory snapshots at meeting boundaries, and a
suspicion heatmap. Scrub through ticks with the scrubber; click a
meeting marker to read the transcript.

The UI is intentionally minimal in MVP — a polish pass lands after
Phase 5.
```

Keep the existing "Reproduce a game" section above this verbatim. It's the determinism demo for a developer audience; "Watch a replay" is the spectator demo for everyone else.

**Public types introduced:**

None.

**Integration risk:**

Lowest-risk task in Phase 4. No new dependencies, no new abstractions, no engine changes.

- **Replay sample provenance.** The 50 JSONLs at `/tmp/eval-50/` are real Phase 3 closing eval artifacts. If they're gone (machine restart, /tmp cleaned), they cannot be regenerated identically — Sonnet 4.6 nondeterminism in temperature > 0 calls plus possible model-side updates mean a re-run produces different transcripts. The implementing agent MUST surface "samples not found" before any commit step, not silently regenerate.
- **The committed samples are pre-Task-4.7 replays.** Every `LLMCallRecord` in them has `agent_id=None` (the field didn't exist when the eval ran). They will exercise the `LLMCallRecord.agent_id: str | None = None` backward-compat path in production — the very path Task 4.7's contract designed for and Task 4.8's `LLMCallCard` fallback ("Older replay — per-call agent attribution unavailable") was written to handle. Two consequences: (1) the smoke-test criterion implicitly verifies that backward-compat actually works against real artifacts, not just synthetic fixtures, and (2) the UX viewer will see the muted "Unknown agent" fallback for every LLM call in the samples — that's expected, not a defect. Document this in `## Decisions` of the PR so reviewers and the UX viewer aren't surprised.
- **`.gitignore` ordering matters.** Negations (`!replays/samples/`) only work if the negated pattern comes AFTER the ignore pattern (`replays/*.jsonl`). Verify ordering when editing `.gitignore`.
- **Process lifecycle in bash is fragile.** The trap-on-EXIT pattern works for clean Ctrl-C but can leak processes if the parent dies via SIGKILL (kill -9). Acceptable for a dev-loop convenience script; non-tech users won't be SIGKILLing things.
- **Port hardcoding.** 8000 and 5173 are hardcoded in the script. If a user needs different ports (e.g. 8000 is bound to Postgres), they currently can't override. Acceptable for MVP; document the limitation in the script's leading comment. Env-var-driven port override is a follow-up if needed.
- **No CI cost.** Static gates only. The smoke test runs in the implementing agent's local checkout; no CI infrastructure needed.
- **The UX acceptance session can run only AFTER this lands.** The non-tech viewer in the acceptance session shouldn't be the first user to discover setup friction. Order: 4.12 merges → UX session runs → Phase 4 closes.

**Ready-to-paste prompt:** `agent_prompts/task-4-12-easy-setup-script.md`

### Phase-closing UX acceptance session

After 4.5–4.11 all merge, run a manual UX acceptance session. A
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
- Mid-phase DTO audit passed before 4.5–4.11 fan-out.
- Frontend `tsc --noEmit` + `vite build` passes in CI.
- All Phase 3 static gates still green (`bash scripts/check.sh`).
- Live game broadcast deferred to Phase 5 (or a post-Phase-4 task) is
  documented as out of scope.
