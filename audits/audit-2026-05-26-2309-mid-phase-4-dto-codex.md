# Mid-Phase-4 DTO Audit — Codex — 2026-05-26 23:09 EDT

## 1. Verdict

**Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8.**

No blocking DTO leakage, endpoint response-model drift, TypeScript/Pydantic drift,
frontend-store/component leak, or replay-loader determinism defect was found.

## 2. Environment

- **HEAD:** `934986d`
- **Branch:** `main`
- **Audit report:** `audits/audit-2026-05-26-2309-mid-phase-4-dto-codex.md`
- **Toolchain note:** first `bash scripts/check.sh` hit stale local frontend
  dependencies (`rolldown` optional native binding missing). Per `AGENTS.md`, I
  ran `bash scripts/setup_env.sh` with the bundled Node runtime, which restored
  ignored dependency files only; `git status --short` remained clean.
- **Full gate:** `env PATH=/Users/danielkeinan/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$PATH bash scripts/check.sh`
  passed: `768 passed, 12 skipped`; frontend `tsc:check` and Vite production
  build passed.
- **API slice:** `uv run pytest tests/api/ -v` passed: `63 passed`.
- **No real provider calls:** the audit loaded existing replay JSONL files and
  ran local tests only; it did not invoke Anthropic or any other live LLM
  provider.

`git log --oneline -5`:

```text
934986d update audit strat
b38cb61 Merge pull request #60 from dkdan10/claude/mapview-vertical-slice-sM1Bf
0a1c091 task 4.4: mapview vertical slice
21fb947 Merge pull request #59 from dkdan10/claude/react-vite-tailwind-pixijs-esDMb
af26e60 task 4.3: address third Codex review (store, scripts, client)
```

Audit-window note: the prompt's literal command,
`git log --oneline --name-status $(git merge-base main HEAD)..HEAD`, produced
no rows because this checkout is already on `main`. I adjusted by inspecting
recent `main` history; Tasks 4.1–4.4 are present via PRs #57–#60:

- Task 4.1: `b887f48 task 4.1: fastapi app skeleton and spectator dto inventory`
- Task 4.2: `7409a1d task 4.2: replay loader + endpoint implementation`, plus
  follow-ups `bf982e2`, `b40480a`, `7830cb1`
- Task 4.3: `b3830b1 task 4.3: react + vite + tailwind + pixijs frontend skeleton`,
  plus follow-ups `4ed9b26`, `8606709`, `af26e60`
- Task 4.4: `0a1c091 task 4.4: mapview vertical slice`

## 3. Class A — DTO Field Leakage Findings

**No findings in this class.**

Evidence: `api/schemas.py` defines frozen, `extra="forbid"` DTOs in
`__all__` at `api/schemas.py:526`; `tests/api/test_leak.py` pins the inventory
and forbids backend/internal field annotations at `tests/api/test_leak.py:43`,
`tests/api/test_leak.py:85`, and `tests/api/test_leak.py:183`. The API leak
tests passed in both `uv run pytest tests/api/ -v` and the full gate.

Per-DTO/source review:

| DTO(s) | Source field review and exposure decision |
|---|---|
| `PositionView`, `SizeView` | Source `engine.world.Position` has `x`, `y`; `Size` has `width`, `height` at `engine/world.py:79` and `engine/world.py:90`. DTOs expose only those geometry fields, widened to floats for rendering at `api/schemas.py:51` and `api/schemas.py:59`. |
| `RoomView` | Source `Room` fields are `id`, `name`, `kind`, `position`, `size`, `notes` at `engine/world.py:106`. DTO exposes `id`, `name`, `position`, `size` and documents `kind`/`notes` omission at `api/schemas.py:67`; loader constructs only those fields at `api/replay_loader.py:700`. |
| `VentView` | Source `Vent` fields are `id`, `room`, `connects_to`, `traversal_ticks` at `engine/world.py:140`. DTO exposes id, room, connected rooms and documents `traversal_ticks` omission at `api/schemas.py:80`; loader maps vent ids to connected room ids at `api/replay_loader.py:713`. |
| `EdgeView` | Source `Edge` fields are `from_room`, `to_room`, `kind`, `traversal_ticks`, `door_id` at `engine/world.py:122`. DTO exposes endpoints and `is_door`, omitting traversal/door internals; loader derives `is_door` from `kind` at `api/replay_loader.py:724`. |
| `MapLayoutView` | Source `Map` includes static config, rooms, edges, vents, tasks, sabotages, emergency/spawn/meeting settings at `engine/world.py:222`. DTO intentionally exposes only rooms, vents, and edges at `api/schemas.py:104`; loader constructs that map slice at `api/replay_loader.py:699`. |
| `PlayerView` | Source `PlayerState` fields are `id`, `role`, `alive`, `room`, `position`, `last_action`, `in_vent` at `engine/entities.py:18`. DTO exposes static identity plus privileged spectator `role` and derived color at `api/schemas.py:116`; loader uses the seeded initial state's `role` at `api/replay_loader.py:688`. Dynamic fields are not embedded here. |
| `AgentTickStateView` | Dynamic `PlayerState` slice exposes `agent_id`, `room_id`, `is_alive`, `is_venting`, derived `task_progress`, and derived `current_action` at `api/schemas.py:137`; loader maps from `WorldState.players` at `api/replay_loader.py:498`. High-risk cooldown fields are absent: `WorldState.cooldowns` exists at `engine/world.py:54`, but `_agent_tick_state` does not serialize it at `api/replay_loader.py:500`. |
| `KillEventView` | Source `KilledEvent` fields include `actor`, `target`, `room`, and `witnesses` at `engine/events.py:65`. DTO intentionally exposes privileged `killer_id`, `victim_id`, and room, and omits witnesses at `api/schemas.py:158`; loader maps only those fields at `api/replay_loader.py:529`. |
| `ReportBodyEventView` | Source body state has `id`, `player_id`, `room`, `position`, `killed_by`, `discovered_by` at `engine/entities.py:38`. DTO exposes only reporter, body victim, and room at `api/schemas.py:168`; loader reads body victim/room without serializing raw `BodyState` fields at `api/replay_loader.py:577`. |
| `SabotageEventView` | Source `SabotageStartedEvent` includes `kind`, `duration_ticks`, `affected_rooms` at `engine/events.py:109`. DTO exposes `kind`, `actor_id`, and nullable `room_id`, omitting duration/affected-room internals at `api/schemas.py:179`; loader emits only MVP `lights` events at `api/replay_loader.py:549`. |
| `TaskCompletedEventView` | Source `TaskCompletedEvent` fields include actor, task id, progress, and required ticks at `engine/events.py:55`. DTO exposes actor, task id, and room at `api/schemas.py:190`; loader derives room from the map and omits progress counters at `api/replay_loader.py:539`. |
| `MeetingTriggeredEventView` | Source `MeetingTriggeredEvent` has actor, trigger, and optional `body_id` at `engine/events.py:141`. DTO exposes meeting id, triggering actor, and body/emergency kind at `api/schemas.py:200`; loader omits raw body id at `api/replay_loader.py:560`. |
| `TickView` | Source `ReplayEntry` has `kind`, `game_id`, `tick`, raw `actions`, and `state_hash` at `orchestrator/replay.py:74`. DTO exposes tick state and event summaries only at `api/schemas.py:220`. Loader verifies `entry.state_hash` at `api/replay_loader.py:360` but constructs `TickView` without state hashes or raw actions at `api/replay_loader.py:489`. |
| `SawPlayerView`, `CompletedTaskObsView`, `FoundBodyObsView` | These mirror meeting observation claim variants at `meetings/schemas.py:45`, `meetings/schemas.py:55`, and `meetings/schemas.py:64`. DTO fields match at `api/schemas.py:240`, `api/schemas.py:250`, and `api/schemas.py:259`; loader projection is direct at `api/replay_loader.py:957`. |
| `AlibiClaimView`, `AccusationClaimView`, `CorroborationClaimView` | These mirror meeting claim variants at `meetings/schemas.py:84`, `meetings/schemas.py:112`, and `meetings/schemas.py:121`. DTO fields match at `api/schemas.py:274`, `api/schemas.py:285`, and `api/schemas.py:294`; loader projection is direct at `api/replay_loader.py:985`. |
| `ReportView` | Source `ReportDocument` fields are `agent_id`, `tick`, `observations`, `claims`, `free_text` at `meetings/schemas.py:141`. DTO exposes exactly those fields at `api/schemas.py:309`; loader maps directly at `api/replay_loader.py:1014`. |
| `StatementView` | Source `Statement` fields are `statement_id`, `speaker`, `tick`, `round_index`, `target`, `claims`, `free_text` at `meetings/schemas.py:151`. DTO exposes exactly those at `api/schemas.py:319`; loader maps the canonical persisted statement at `api/replay_loader.py:1024`. The meeting manager overwrites LLM-emitted identity fields with canonical values at `meetings/manager.py:646`, and `tests/meetings/test_manager.py:695` verifies this. |
| `ContradictionView` | Source `ContradictionRef` fields are `contradiction_id`, `kind`, `event_a_id`, `event_b_id`, `subjects`, `description` at `meetings/schemas.py:190`. DTO exposes exactly those at `api/schemas.py:331`; loader maps directly at `api/replay_loader.py:1036`. |
| `BallotView` | Source `VoteBallot` fields are `voter`, `target`, `confidence`, `primary_reason_id`, `considered_alternatives`, `rationale_text` at `meetings/schemas.py:169`. DTO exposes the same fields, flattening `target` to string at `api/schemas.py:342`; loader maps directly at `api/replay_loader.py:1047`. |
| `LLMCallView` | Source `LLMCallRecord` fields are `call_kind`, `model`, `prompt`, `response_text`, `input_tokens`, `output_tokens`, `cost_usd` at `orchestrator/replay.py:51`. DTO intentionally exposes prompt text as `prompt_text` plus derived `prompt_template_id` at `api/schemas.py:357`; loader maps from captured calls at `api/replay_loader.py:1069`. This is privileged spectator exposure, not an accidental raw replay embedding. |
| `MeetingView` | Source `MeetingReplayEntry` fields include `kind`, `game_id`, meeting metadata, transcript, ballots, contradictions, `llm_calls`, `prompt_versions`, and `state_hash_before`/`state_hash_after` at `orchestrator/replay.py:86`. DTO exposes the meeting artifact fields and total cost at `api/schemas.py:373`, explicitly excluding state hashes. Loader constructs a `MeetingView` and never returns `MeetingReplayEntry` directly at `api/replay_loader.py:591`. |
| `BeliefEntryView` | Source `agents.memory.beliefs.PlayerBelief` is summarized as subject, suspicion, derived confidence, and tick at `api/schemas.py:403`; loader derives it via `_belief_entry_view` at `api/replay_loader.py:1113`. No raw belief store object is embedded. |
| `AgentMemoryView` | DTO exposes meeting-boundary memory only at `api/schemas.py:413`. Loader snapshots per-agent memory by `(meeting_id, pid)` at `api/replay_loader.py:401` and renders that same per-agent memory via `render_for_prompt` at `api/replay_loader.py:649`. A TestClient check against `/tmp/eval-50` returned `p-2 CREWMATE ## Your role: CREWMATE contains_IMPOSTOR False`, `p-3 CREWMATE ... False`, and `p-4 IMPOSTOR ## Your role: IMPOSTOR contains_IMPOSTOR True`, confirming each memory view carries only that agent's role line. |
| `SuspicionEntryView`, `SuspicionGraphView` | DTOs expose only observer, subject, suspicion, and tick at `api/schemas.py:435` and `api/schemas.py:444`; no raw memory/belief store object is embedded. There is no Phase 4.4 endpoint returning this graph yet. |
| `ReplayMetadataView` | Source `GameEndReplayEntry` has `kind`, `game_id`, optional tick, winner, and reason at `orchestrator/replay.py:122`; DTO adds derived seed, tick count, meeting count, total cost, prompt versions, and mtime at `api/schemas.py:457`. Loader constructs metadata from replay reductions at `api/replay_loader.py:663`. |
| `FailedCallView` | Source `FailedCallReplayEntry` contains prompt length, raw response, token counts, and error fields at `orchestrator/replay.py:145`. DTO exposes meeting id, tick, model, cost, error type, and a 200-char error message at `api/schemas.py:478`; loader truncates the message and omits raw response/prompt length at `api/replay_loader.py:1058`. |
| `ReplayView` | DTO nests metadata, map, players, ticks, meetings, and failed calls at `api/schemas.py:494`. Loader constructs it from DTO builders at `api/replay_loader.py:286`; it does not embed raw `WorldState`, `ReplayEntry`, or `MeetingReplayEntry`. |
| `EvalCostSummaryView` | DTO exposes aggregate replay cost/outcome fields at `api/schemas.py:515`; loader computes it from replay reductions at `api/replay_loader.py:225`. |

Additional high-risk checks:

- `PlayerState.role` is intentionally exposed via `PlayerView.role`
  (`api/schemas.py:116`, `api/replay_loader.py:688`).
- `AgentTickStateView` does not include `kill_cooldown_ticks`,
  `vent_cooldown_ticks`, `cooldowns`, or raw `last_action`
  (`api/schemas.py:137`, `api/replay_loader.py:498`).
- `WorldState.bodies` is not serialized as raw `BodyState`; the normal payload
  contains only kill/report DTO events (`api/replay_loader.py:529`,
  `api/replay_loader.py:577`).
- `ReplayEntry.state_hash` is verified but not serialized into `TickView`
  (`orchestrator/replay.py:79`, `api/replay_loader.py:360`,
  `api/replay_loader.py:489`).
- Statement identity fields are canonical post-manager values, not raw LLM
  placeholders (`meetings/manager.py:646`, `tests/meetings/test_manager.py:695`,
  `api/replay_loader.py:1024`).

## 4. Class B — Endpoint Response Drift Findings

**No findings in this class.**

Route declarations and actual return paths line up:

- `GET /replays` declares `response_model=list[ReplayMetadataView]` and returns
  `loader.list_replays()` at `api/routes/replays.py:32`; loader returns
  `ReplayMetadataView` instances at `api/replay_loader.py:210`.
- `GET /replays/{game_id}` declares `ReplayView` and returns
  `loader.load_replay()` at `api/routes/replays.py:37`; loader constructs
  `ReplayView` at `api/replay_loader.py:286`.
- `GET /replays/{game_id}/ticks/{tick}` declares `TickView` and returns one
  `TickView` from the cached replay at `api/routes/replays.py:45`.
- `GET /replays/{game_id}/meetings/{meeting_id}` declares `MeetingView` and
  returns one `MeetingView` at `api/routes/replays.py:59`.
- `GET /replays/{game_id}/meetings/{meeting_id}/memory/{agent_id}` declares
  `AgentMemoryView` and returns `loader.get_meeting_memory()` at
  `api/routes/replays.py:71`.
- `GET /eval/cost-summary` declares `EvalCostSummaryView` and returns
  `loader.cost_summary()` at `api/routes/eval.py:23`.

TestClient evidence against `/tmp/eval-50`:

```text
/replays 200
keys ['created_at', 'game_id', 'meeting_count', 'prompt_versions', 'seed', 'total_cost_usd', 'total_ticks', 'winner', 'winner_reason']
extra []
/replays/headless-seed-22 200
keys ['failed_calls', 'map', 'meetings', 'metadata', 'players', 'ticks']
extra []
/replays/headless-seed-22/ticks/0 200
keys ['agent_states', 'events', 'sabotage_active', 'tasks_completed_total', 'tasks_required_total', 'tick']
extra []
/replays/headless-seed-22/meetings/headless-seed-22:meeting-0 200
keys ['ballots', 'contradictions', 'ejected_player_id', 'llm_calls', 'meeting_id', 'outcome', 'prompt_versions', 'reports', 'statements', 'tick', 'total_cost_usd', 'trigger_kind', 'triggered_by']
extra []
/replays/headless-seed-22/meetings/headless-seed-22:meeting-0/memory/p-2 200
keys ['agent_id', 'beliefs', 'observations', 'open_contradictions', 'rendered_memory_text', 'role', 'tasks_assigned', 'tasks_completed', 'tick']
extra []
/eval/cost-summary 200
keys ['decisive_split', 'max_cost_per_replay', 'mean_cost_per_replay', 'total_cost_usd', 'total_replays']
extra []
```

Recursive forbidden-key scan over `/replays/headless-seed-22`,
`/ticks/0`, `/meetings/headless-seed-22:meeting-0`, and
`/memory/p-2` found no `state_hash`, `state_hash_before`,
`state_hash_after`, `raw_response`, `prompt_length`, cooldown-key,
`rng_state`, or raw `actions` keys.

## 5. Class C — TypeScript / Pydantic Drift Findings

**No findings in this class.**

The frontend types are hand-authored, not generated, per the file header at
`frontend/src/types/api.ts:1`. I compared every Pydantic DTO in
`api.schemas.__all__` against every TypeScript `interface` field list.

Command output:

```text
missing_interfaces []
extra_interfaces []
field_mismatches []
```

Spot-check anchors:

- `AgentTickStateView` fields match between `api/schemas.py:137` and
  `frontend/src/types/api.ts:80`.
- `MeetingView` fields match between `api/schemas.py:373` and
  `frontend/src/types/api.ts:251`.
- `AgentMemoryView` fields match between `api/schemas.py:413` and
  `frontend/src/types/api.ts:278`.
- `ReplayView` fields match between `api/schemas.py:494` and
  `frontend/src/types/api.ts:326`.

## 6. Class D — Frontend Store / Component Leak Findings

**No findings in this class.**

The store caches API DTOs, not raw engine/replay internals:

- Store state is typed as `ReplayMetadataView[]`, `ReplayView`, and
  `AgentMemoryView` at `frontend/src/store/replayStore.ts:17`.
- `selectReplay()` writes the result of `api.getReplay(gameId)` directly into
  `currentReplay` and clears replay-scoped memory cache at
  `frontend/src/store/replayStore.ts:103`.
- `fetchMemoryView()` writes only `api.getMemory()` results into
  `memoryCache` at `frontend/src/store/replayStore.ts:157`.
- API client methods return only the TypeScript DTO types at
  `frontend/src/api/client.ts:60`.

Component field-access scan:

- `MapView` reads `currentReplay.map.rooms`, `currentReplay.ticks[currentTick]`,
  `currentReplay.players[*].agent_id/color`, and
  `tick.agent_states[*].agent_id/room_id/is_alive/is_venting` at
  `frontend/src/components/MapView.tsx:80`; every field exists in
  `frontend/src/types/api.ts:63`, `frontend/src/types/api.ts:69`,
  `frontend/src/types/api.ts:80`, and `frontend/src/types/api.ts:136`.
- `ReplayPicker` renders only replay metadata `game_id`, `seed`, `winner`, and
  `total_ticks` at `frontend/src/components/ReplayPicker.tsx:37`; all exist in
  `ReplayMetadataView` at `frontend/src/types/api.ts:305`.
- `TickStepper` reads only `currentReplay.ticks.length` and store playback state
  at `frontend/src/components/TickStepper.tsx:16`; `ticks` exists in
  `ReplayView` at `frontend/src/types/api.ts:326`.
- `RoomRect` uses `RoomView.id/name/position/size` at
  `frontend/src/components/RoomRect.tsx:66`; all exist at
  `frontend/src/types/api.ts:44`.
- `AgentToken` receives `RoomView`, color, and render-only props from `MapView`
  at `frontend/src/components/AgentToken.tsx:12`; it does not read replay
  internals.

The 4.4 components do not render `role`, `prompt_text`,
`rendered_memory_text`, raw hashes, raw replay actions, or any field absent
from `frontend/src/types/api.ts`.

## 7. Class E — Determinism + State-Hash Findings

**No findings in this class.**

Required API test slice:

```text
uv run pytest tests/api/ -v
...
tests/api/test_replay_loader.py::test_state_hash_mismatch_raises_with_bad_tick PASSED
...
============================== 63 passed in 1.91s ==============================
```

The state-hash mismatch test is anchored at
`tests/api/test_replay_loader.py:116`, and replay playback checks every
recorded tick hash before DTO construction at `api/replay_loader.py:360`.
Meeting post-application state hashes are also checked at
`api/replay_loader.py:424`.

Live local API sample:

- Started `uvicorn` with `AILIBI_REPLAY_DIR=/tmp/eval-50`.
- `curl -s -w '\nHTTP:%{http_code}\n' http://127.0.0.1:8000/replays/headless-seed-22`
  returned `HTTP:200`; the metadata at the start of the response was:

```json
{
  "game_id": "headless-seed-22",
  "seed": 22,
  "total_ticks": 8,
  "winner": "IMPOSTORS",
  "winner_reason": "IMPOSTOR_PARITY",
  "meeting_count": 1,
  "total_cost_usd": 0.20803499999999997
}
```

- `curl -s -w '\nHTTP:%{http_code}\n' http://127.0.0.1:8000/replays/headless-seed-22/ticks/0`
  returned `HTTP:200` and a `TickView` with 4 `agent_states`. This matches the
  current default player count of 4 at `orchestrator/game.py:94`.

No endpoint returned 500 or empty data for the sampled real replay.

## 8. Repair Task Proposals

None. No blocking findings were found.

## 9. Required Closing Fields

- **Report path:** `audits/audit-2026-05-26-2309-mid-phase-4-dto-codex.md`
- **Verdict:** Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8.
- **Findings count by class:**
  - Class A — DTO field leakage: 0
  - Class B — Endpoint response drift: 0
  - Class C — TypeScript / Pydantic drift: 0
  - Class D — Frontend store / component leak: 0
  - Class E — Determinism + state-hash: 0
- **Total findings:** 0
