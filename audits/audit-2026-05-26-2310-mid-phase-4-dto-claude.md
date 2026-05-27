# Mid-Phase-4 DTO Audit — 2026-05-26 23:10 (claude)

## 1. Verdict

**Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8.**

Zero Class A leaks, zero Class B response drift, zero Class C TS drift,
zero Class D component-level field invention, zero Class E determinism
breaks. Three informational findings are recorded (one stale docstring,
one substrate gap in [LLMCallView](api/schemas.py#L357) per-call agent
attribution, one semantically-loose `last_updated_tick` on
[BeliefEntryView](api/schemas.py#L403)). None block fan-out; each is
worth a one-line follow-up but not a repair task gate.

## 2. Environment

- HEAD: `934986d` ("update audit strat" — non-code; previous code-bearing
  commit is `b38cb61` PR #60 task 4.4 MapView vertical slice).
- [scripts/check.sh](scripts/check.sh) → **768 passed, 12 skipped**
  (Python gates: ruff, ruff format, lint-imports, validate_task_docs,
  generate_prompts --check, mypy, pytest). Frontend tsc:check passed
  after `npm install`; `npm run build` failed on the bundling step
  because the host Node is v20.2.0 and Vite requires ≥20.19 — this is
  an environment limitation, not a code defect, and tsc:check is the
  type-drift gate that matters for this audit.
- `uv run pytest tests/api/ -v` → **63 passed**.
- Live verification harness used throughout: a [TestClient](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
  pointed at a tmp replay dir built from [tests/api/fixtures/sample_replay.py](tests/api/fixtures/sample_replay.py)
  fixtures, plus one real run against `/tmp/eval-50/replay-seed-22.jsonl`
  to confirm engine playback on a real tournament artifact.
- `git log --oneline -5`:
  ```
  934986d update audit strat
  b38cb61 Merge pull request #60 from dkdan10/claude/mapview-vertical-slice-sM1Bf
  0a1c091 task 4.4: mapview vertical slice
  21fb947 Merge pull request #59 from dkdan10/claude/react-vite-tailwind-pixijs-esDMb
  af26e60 task 4.3: address third Codex review (store, scripts, client)
  ```
  All four foundation tasks (4.1 / 4.2 / 4.3 / 4.4) are merged into
  `main`; the substrate is complete for audit.

## 3. Class A — DTO field leakage findings

Methodology: for every entry in [api.schemas.__all__](api/schemas.py#L526)
I (a) located the source type the DTO shadows from its docstring,
(b) listed the source type's fields, (c) matched each source field to
either an intentional exposure, a deliberate omission, or a potential
leak. Verified at the wire level by inspecting JSON keys for every
endpoint and grepping the responses for forbidden field names
(`state_hash`, `state_hash_before`, `state_hash_after`, `raw_response`,
`prompt_length`, `rng_state`, `cooldown`). All forbidden names absent.

**No blocking findings in this class.** The DTO inventory is intentional
and the cited high-risk fields are correctly handled:

- `PlayerState.role` → [PlayerView.role](api/schemas.py#L128) —
  INTENTIONAL (privileged spectator); confirmed exposed.
- `PlayerState.kill_cooldown_ticks` / `vent_cooldown_ticks` — these
  fields do **not exist** on [PlayerState](engine/entities.py#L19-L26)
  (which has `id, role, alive, room, position, last_action, in_vent`).
  Cooldowns live on `WorldState.cooldowns: Mapping[PlayerId, int]`.
  [AgentTickStateView](api/schemas.py#L137) does not surface cooldowns;
  the DTO docstring's exclusion list is accurate in spirit (cooldowns
  excluded) even though the field names it cites are not the current
  engine attribute names.
- `WorldState.bodies` → not embedded; only the privileged kill /
  report-body markers in [KillEventView](api/schemas.py#L158) /
  [ReportBodyEventView](api/schemas.py#L168) reach the wire. Verified
  no `BodyState`-only field (e.g. `killed_by`, `discovered_by`) appears
  in either DTO.
- `ReplayEntry.state_hash` — not in any DTO field annotation
  (confirmed by [tests/api/test_leak.py::test_no_forbidden_types_in_field_annotations](tests/api/test_leak.py#L183));
  not in any response (confirmed by grep over `/replays/.../meetings/...`
  and `/replays/...` JSON).
- `MeetingReplayEntry.state_hash_before` / `state_hash_after` — DTO
  docstring [api/schemas.py:380](api/schemas.py#L380) declares the
  exclusion; loader at [api/replay_loader.py:596-612](api/replay_loader.py#L596-L612)
  constructs a fresh `MeetingView(...)` field-by-field rather than
  `model_dump()`-ing the source, so even if FastAPI tried to serialize
  extras they couldn't reach the wire. Grep over the live JSON for
  `state_hash_before` returns no matches.
- `LLMCallRecord.prompt` → [LLMCallView.prompt_text](api/schemas.py#L366)
  — INTENTIONAL exposure. This is the highest-risk exposure on the
  surface: the prompt body contains the calling agent's
  `rendered_memory_text` (including their role line). Cross-agent
  contamination test: spun up the API against `seed-1` fixture
  (impostor = `p-4`), curl'd `/replays/headless-seed-1/meetings/.../memory/{p-1..p-4}`,
  and confirmed each agent's `rendered_memory_text` begins with their
  own role:
  ```
  p-1 role=CREWMATE  first_line='## Your role: CREWMATE'  len=215
  p-2 role=CREWMATE  first_line='## Your role: CREWMATE'  len=351
  p-3 role=CREWMATE  first_line='## Your role: CREWMATE'  len=351
  p-4 role=IMPOSTOR  first_line='## Your role: IMPOSTOR'  len=382
  ```
  Per-agent scoping is enforced upstream in
  [api/replay_loader.py:466-471](api/replay_loader.py#L466-L471): each
  agent gets its own `AgentMemory()`, and `ObservationService.build_packet`
  applies the visibility firewall per agent before
  `ingest_packet(memory=memories[pid].episodic)`. ThoughtStream (4.6)
  must continue to address per-agent endpoints (it already does — there
  is no shared `memory` endpoint that could blur agents). **INFO,
  non-blocking.**
- `Statement.statement_id` / `Statement.speaker` — exposed verbatim
  via [StatementView](api/schemas.py#L319). These are the post-override
  canonical values; the meeting manager rewrites the LLM-emitted
  placeholder before `MeetingResult` is constructed
  ([meetings/manager.py](meetings/manager.py)), so what reaches
  `MeetingView.statements` is the canonical id/speaker, not the raw
  LLM string.

### Three informational notes (none block fan-out)

1. **[AgentTickStateView](api/schemas.py#L137) docstring references
   stale `PlayerState` attribute names.** The docstring claims to
   exclude `target_room` and `planned_path`; neither attribute exists
   on the current [PlayerState dataclass](engine/entities.py#L19-L26).
   This is a comment-only freshness issue, not a leak — the DTO field
   set is correct. Trivial fix.

2. **[BeliefEntryView.last_updated_tick](api/schemas.py#L410) is
   semantically the *meeting tick*, not a per-belief update timestamp.**
   The loader at [api/replay_loader.py:1113-1120](api/replay_loader.py#L1113-L1120)
   simply passes through the enclosing meeting's tick to every belief
   for that snapshot. The DTO docstring says "decay timestamps are
   excluded," but `PlayerBelief` ([agents/memory/beliefs.py:57-65](agents/memory/beliefs.py#L57-L65))
   has no decay timestamp to exclude. The field will mislead
   BeliefMatrix (4.7) if its consumer expects per-edge recency: every
   row in the snapshot will carry the same tick. Either rename the
   field to `snapshot_tick` or wire it to a real per-belief recency
   source before BeliefMatrix dispatches. Non-blocking, **but worth
   resolving before 4.7** to avoid the BeliefMatrix component baking
   a misinterpretation into its UI logic.

3. **[LLMCallView](api/schemas.py#L357) has no `agent_id` field —
   nor does the source [LLMCallRecord](orchestrator/replay.py#L51-L71).**
   ThoughtStream (4.6) wants per-agent attribution: "show me agent
   p-2's calls during this meeting." Today that information is
   recoverable only by parsing the rendered memory text inside
   `prompt_text` (fragile and template-dependent). The call site
   ([meetings/manager.py:555-565](meetings/manager.py#L555-L565))
   knows `participant.agent_id` but does not persist it. Not a *leak*
   — the opposite, a missing field — so it is out of strict Class A
   scope. Flagging because adding an `agent_id` to `LLMCallRecord`
   (and thus to `LLMCallView`) before 4.6 begins would save 4.6 from
   either inventing a brittle prompt-parser or inflating its scope to
   patch the replay format mid-stream. Non-blocking for fan-out as a
   class; informational for the 4.6 contract author.

## 4. Class B — Endpoint response vs response_model drift findings

Methodology: drove each of the six endpoints via `TestClient` and
inspected the top-level + first-level-nested JSON keys against the
declared `response_model`. Recorded a key for each nested DTO.

| Endpoint | response_model | Top-level keys observed |
|----------|----------------|--------------------------|
| `GET /replays` | `list[ReplayMetadataView]` | `[game_id, seed, total_ticks, winner, winner_reason, meeting_count, total_cost_usd, prompt_versions, created_at]` |
| `GET /replays/{game_id}` | `ReplayView` | `[metadata, map, players, ticks, meetings, failed_calls]` |
| `GET /replays/{game_id}/ticks/{tick}` | `TickView` | `[tick, agent_states, events, sabotage_active, tasks_completed_total, tasks_required_total]` |
| `GET /replays/{game_id}/meetings/{meeting_id}` | `MeetingView` | `[meeting_id, tick, triggered_by, trigger_kind, outcome, ejected_player_id, reports, statements, ballots, contradictions, llm_calls, prompt_versions, total_cost_usd]` |
| `GET /replays/{...}/memory/{agent_id}` | `AgentMemoryView` | `[agent_id, tick, role, tasks_completed, tasks_assigned, observations, beliefs, open_contradictions, rendered_memory_text]` |
| `GET /eval/cost-summary` | `EvalCostSummaryView` | `[total_replays, total_cost_usd, mean_cost_per_replay, max_cost_per_replay, decisive_split]` |

Every key matches the declared DTO 1:1. Nested DTOs also clean:
`meetings[0].llm_calls[0]` returns `[call_kind, model, prompt_template_id,
prompt_text, response_text, input_tokens, output_tokens, cost_usd]` (no
`agent_id`, no `prompt_length`, no `raw_response` — matches
[LLMCallView](api/schemas.py#L357) exactly). All handlers in
[api/routes/replays.py](api/routes/replays.py) and
[api/routes/eval.py](api/routes/eval.py) return `loader.<method>()`
results — never raw dicts or raw upstream Pydantic models — and the
loader builds each `…View` field-by-field rather than calling
`model_dump()` on a source type. **No findings in this class.**

## 5. Class C — TypeScript / Pydantic drift findings

Methodology: types are hand-authored, not generated (per the file
header at [frontend/src/types/api.ts:1-9](frontend/src/types/api.ts#L1-L9)).
Listed every Pydantic DTO field via `model_fields`; listed every
TypeScript interface field; compared name-by-name.

- **Interface inventory**: 33 TS `export interface` declarations.
  33 entries in `api.schemas.__all__` minus the three union aliases
  (`TickEventView`, `ObservationClaimView`, `StatementClaimView`),
  which are present in TS as `type X = …` aliases (lines 129-134,
  171-174, 199-202). 1:1 inventory match.
- **Field-by-field check**: every Pydantic field name in every DTO
  has a matching TS field, and every TS field has a matching Pydantic
  field. Nullability follows the documented convention: Pydantic
  `X | None` → TS `X | null` (required, nullable); Pydantic
  `tuple[X, ...]` → TS `X[]`. Confirmed for the high-risk DTOs:
  `MeetingView` (13 fields), `AgentMemoryView` (9 fields),
  `ReplayMetadataView` (9 fields), `LLMCallView` (8 fields),
  `AgentTickStateView` (6 fields), `BallotView` (6 fields). Spot-checked
  the remaining 27 — no drift.
- **`tsc --noEmit` (frontend/`npm run tsc:check`) passes** with zero
  errors against the current store + components, which proves no
  consumer is reading a non-existent TS field (TypeScript would flag
  it as `does not exist on type`).

**No findings in this class.**

## 6. Class D — Frontend store / component leak findings

Methodology: greped `frontend/src/components/*.tsx` and
`frontend/src/store/replayStore.ts` for every field access pattern
(`currentReplay\.`, `tick\.`, `replay\.`, `agent\.`, `player\.`,
`room\.`) and matched each access to a declared TS field.

| File | Accesses observed | Verdict |
|------|--------------------|---------|
| [MapView.tsx](frontend/src/components/MapView.tsx) | `currentReplay.{map.rooms, ticks, players}`, `tick.agent_states`, `agent.{is_alive, room_id, is_venting, agent_id}`, `player.{agent_id, color}`, `room.{id, position.{x,y}, size.{width,height}}` | All declared. |
| [AgentToken.tsx](frontend/src/components/AgentToken.tsx) | `room.position.{x,y}`, `room.size.{width,height}` | All declared. |
| [RoomRect.tsx](frontend/src/components/RoomRect.tsx) | `room.{id, name, position.{x,y}, size.{width,height}}` | All declared. |
| [ReplayPicker.tsx](frontend/src/components/ReplayPicker.tsx) | `replay.{game_id, seed, winner, total_ticks}`, `currentReplay.metadata.game_id` | All declared on [ReplayMetadataView](frontend/src/types/api.ts#L305). |
| [TickStepper.tsx](frontend/src/components/TickStepper.tsx) | `currentReplay.ticks.length`, `currentTick` | Pure store state + DTO field. |
| [replayStore.ts](frontend/src/store/replayStore.ts) | `replay.metadata.game_id` (in `fetchMemoryView`) | Declared. |

No component reads a field that isn't on the DTO. The store caches
`ReplayView` whole (which includes privileged content), but the
spectator surface is *intentionally* privileged — caching the same
shape the API serves is in-contract. No "raw replay internals" leak
through the store: it holds typed `ReplayView` / `AgentMemoryView`,
never raw fetch responses.

**No findings in this class.**

## 7. Class E — Determinism + state-hash findings

- `uv run pytest tests/api/test_replay_loader.py::test_state_hash_mismatch_raises_with_bad_tick`
  → **passed.** Fixture deliberately corrupts a recorded `state_hash`;
  the loader raises [ReplayStateMismatchError](api/replay_loader.py#L151)
  with the offending tick + game id.
- `uv run pytest tests/api/test_replays.py::test_get_replay_state_mismatch_returns_500`
  → **passed.** Confirms the app-level exception handler in
  [api/main.py:46-54](api/main.py#L46-L54) maps the mismatch to a 500
  with `{detail, tick, game_id}` in the body.
- Real-replay sanity: spun up the API with
  `AILIBI_REPLAY_DIR=/tmp/eval-50`, then:
  ```
  curl /replays/headless-seed-22                  → 200; metadata.game_id="headless-seed-22"; ticks=8; meetings=1; players=4
  curl /replays/headless-seed-22/ticks/0          → 200; agent_states len=4
  ```
  Player count is **4**, which matches `DEFAULT_NUM_PLAYERS=4` from
  [orchestrator/game.py](orchestrator/game.py) (not the audit prompt's
  "typically 5–7" — the eval-50 tournament was run with the default
  roster; the actor set in the recorded actions is `{p-1, p-2, p-3, p-4}`,
  confirmed by parsing the JSONL directly). The roster-inference logic
  at [api/replay_loader.py:824-848](api/replay_loader.py#L824-L848)
  correctly recovers 4 from the max `p-N` in the action stream. No
  500s, no mismatch errors — engine playback is byte-identical to the
  recorded tournament.

**No findings in this class.**

## 8. Repair task proposals

None. Three informational follow-ups (not repair tasks; one-line
hygiene that can ride along on the first 4.5-and-later PR that touches
each file):

- **(opt) docstring sync** — Update
  [AgentTickStateView docstring](api/schemas.py#L137-L146) to drop the
  stale `target_room` / `planned_path` references; replace with the
  actual current `PlayerState` attributes (`position`, `last_action`)
  that are excluded.

- **(opt, before 4.7) BeliefEntryView.last_updated_tick semantics** —
  Either rename to `snapshot_tick`, or wire the loader to capture a
  real per-belief recency from `PlayerBelief` (would require an upstream
  change to track per-edge update ticks). The current field is
  honest-by-accident — it is the only tick the loader has access to —
  but BeliefMatrix (4.7) will read it as a recency signal and that
  reading will be wrong.

- **(opt, before 4.6) Per-call agent attribution** — Add `agent_id`
  to [LLMCallRecord](orchestrator/replay.py#L51-L71) and surface it
  via [LLMCallView](api/schemas.py#L357). The call site
  ([meetings/manager.py:555-565, 615-625, 705-720](meetings/manager.py#L555-L565))
  already knows the agent. Without this, ThoughtStream (4.6) must
  either parse prompt bodies to attribute calls, or scope itself to
  the meeting level (losing per-agent granularity). Touches replay
  schema, so it carries a backward-compatibility consideration for
  existing replays — old logs would have `agent_id=None` and the DTO
  field would need to be `str | None`.

Each of the three is one DTO/dataclass field change plus a doc update.
None is a repair task, none blocks fan-out.

## 9. Required closing fields

- **Report path:** `audits/audit-2026-05-26-2310-mid-phase-4-dto-claude.md`
- **Verdict:** Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8.
- **Findings count by class:**
  - Class A: 0 blocking, 3 informational
  - Class B: 0
  - Class C: 0
  - Class D: 0
  - Class E: 0
- **Total findings:** 0 blocking, 3 informational.
