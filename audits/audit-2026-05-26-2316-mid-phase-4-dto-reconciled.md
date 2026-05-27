# Mid-Phase-4 DTO Audit — Reconciled — 2026-05-26 23:16

- **Date:** 2026-05-26 23:16 local
- **Audited HEAD:** `934986d` on `main`
- **Source audits reconciled:**
  - [audit-2026-05-26-2309-mid-phase-4-dto-codex.md](audit-2026-05-26-2309-mid-phase-4-dto-codex.md) — verdict: *passes*
  - [audit-2026-05-26-2310-mid-phase-4-dto-claude.md](audit-2026-05-26-2310-mid-phase-4-dto-claude.md) — verdict: *passes*
- **Reconciler stance:** read-only adjudication; no source/test/audit edits; the source audits' prompt was intentionally not read.

---

## 1. Verdict

**Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8.**

Both source audits agree. Zero Blocking, High, Medium, or Low findings reproduce against `HEAD`. Three Claude-only informational notes verify (one stale docstring; two forward-looking schema-gap notes for 4.6 ThoughtStream and 4.7 BeliefMatrix) but none gate fan-out.

## 2. Environment

- **HEAD:** `934986d` ("update audit strat" — docs only; last code-bearing commit is `b38cb61`, PR #60 Task 4.4 MapView vertical slice).
- **`bash scripts/check.sh`:** both audits report `768 passed, 12 skipped` (Codex with the bundled Node runtime on `PATH`; Claude with host Node v20.2.0 where Vite `npm run build` cannot run but `tsc:check` does). The type-drift gate that matters for this audit (`tsc:check`) passes in both reports.
- **`uv run pytest tests/api/ -v`:** re-run by the reconciler at HEAD — **63 passed in 1.68s**, matching both source audits.
- **No real-provider calls:** Phase 4 added no new LLM-call paths; both audits used recorded replay JSONL only.
- **`git log --oneline -5`:**
  ```
  934986d update audit strat
  b38cb61 Merge pull request #60 from dkdan10/claude/mapview-vertical-slice-sM1Bf
  0a1c091 task 4.4: mapview vertical slice
  21fb947 Merge pull request #59 from dkdan10/claude/react-vite-tailwind-pixijs-esDMb
  af26e60 task 4.3: address third Codex review (store, scripts, client)
  ```
  Tasks 4.1, 4.2, 4.3, 4.4 are all merged into `main`.

## 3. Class A — DTO field leakage findings

**No blocking findings.** Three Claude-only informational notes verified at HEAD (R-1, R-2, R-3 below). Codex performed a per-DTO source/sink table across every entry in [api.schemas.__all__](api/schemas.py#L526) and found zero leaks; Claude performed the same scan plus a wire-level forbidden-key grep (`state_hash`, `state_hash_before`, `state_hash_after`, `raw_response`, `prompt_length`, `rng_state`, `cooldown`) on live JSON and matched. The high-risk exposures are intentional and correctly scoped:

- `PlayerState.role` → `PlayerView.role` is privileged-spectator by design ([api/schemas.py:116](api/schemas.py#L116), [api/replay_loader.py:688](api/replay_loader.py#L688)).
- `WorldState.cooldowns` is **not** serialized by `AgentTickStateView` ([api/replay_loader.py:498-500](api/replay_loader.py#L498)).
- `ReplayEntry.state_hash` is verified but never embedded in any `TickView` ([api/replay_loader.py:360](api/replay_loader.py#L360), [api/replay_loader.py:489](api/replay_loader.py#L489)); `MeetingReplayEntry.state_hash_before/after` likewise excluded from `MeetingView` ([api/replay_loader.py:596-612](api/replay_loader.py#L596)).
- `LLMCallRecord.prompt` is intentionally exposed via `LLMCallView.prompt_text` (privileged spectator); per-agent memory firewall upstream means each agent's `rendered_memory_text` carries only that agent's role line (cross-agent contamination check passed in both audits against `/tmp/eval-50`).
- `Statement.statement_id` / `Statement.speaker` reach `StatementView` as post-override canonical values, not raw LLM placeholders ([meetings/manager.py:646](meetings/manager.py#L646), [tests/meetings/test_manager.py:695](tests/meetings/test_manager.py#L695)).

### R-1 — `AgentTickStateView` docstring cites attributes that no longer exist on `PlayerState`

**Informational.** The DTO docstring at [api/schemas.py:144-145](api/schemas.py#L144) declares it excludes `target_room` and `planned_path`. Verified against [engine/entities.py:18-26](engine/entities.py#L18): the current `PlayerState` dataclass has `id, role, alive, room, position, last_action, in_vent` — neither cited attribute exists. The DTO **field set** is correct; the docstring is a stale comment from an earlier dataclass shape. No leak.

### R-2 — `BeliefEntryView.last_updated_tick` is the meeting tick, not a per-belief recency

**Informational, worth resolving before 4.7.** [api/replay_loader.py:1113-1120](api/replay_loader.py#L1113) passes the enclosing meeting's tick to every `BeliefEntryView` in the snapshot. Verified against [agents/memory/beliefs.py:57-65](agents/memory/beliefs.py#L57): `PlayerBelief` carries no per-belief update tick — only `trust, suspicion, alibis, inconsistencies`. The DTO field is honest-by-accident (it is the only tick the loader can supply) but every row in a snapshot will carry the same value, which will mislead `BeliefMatrix` (Task 4.7) if its component reads it as a recency signal. Not a leak; a semantic-fidelity gap.

### R-3 — `LLMCallView` has no `agent_id` field; neither does `LLMCallRecord`

**Informational, worth resolving before 4.6.** Verified at [api/schemas.py:357-370](api/schemas.py#L357) (DTO) and [orchestrator/replay.py:51-71](orchestrator/replay.py#L51) (source). The call site in [meetings/manager.py](meetings/manager.py) knows the calling `participant.agent_id` but does not persist it on `LLMCallRecord`. ThoughtStream (Task 4.6) wants per-agent attribution; the only recovery path today is parsing the rendered memory text inside `prompt_text` — fragile and template-dependent. This is a *missing* field, not a leak, so it is outside strict Class A scope; Claude flagged it as forward-looking design feedback for the 4.6 contract author. Adding `agent_id: str | None` to `LLMCallRecord` carries a backward-compatibility consideration for replays recorded before the change.

## 4. Class B — Endpoint response drift findings

**No findings.** Both audits drove all six routes (`/replays`, `/replays/{id}`, `/replays/{id}/ticks/{tick}`, `/replays/{id}/meetings/{mid}`, `/replays/{id}/meetings/{mid}/memory/{aid}`, `/eval/cost-summary`) via `TestClient` and recorded matching top-level key sets identical to the declared `response_model`. Codex additionally ran a recursive grep for `state_hash`, `state_hash_before`, `state_hash_after`, `raw_response`, `prompt_length`, cooldown-key, `rng_state`, raw `actions` over `/replays/headless-seed-22`, `/ticks/0`, `/meetings/.../memory/p-2` against `/tmp/eval-50` and got zero hits. Every handler in [api/routes/replays.py](api/routes/replays.py) and [api/routes/eval.py](api/routes/eval.py) returns `loader.<method>()` output, never raw dicts or upstream Pydantic models, and the loader builds every `…View` field-by-field rather than `model_dump()`-ing a source.

## 5. Class C — TypeScript / Pydantic drift findings

**No findings.** Types in [frontend/src/types/api.ts](frontend/src/types/api.ts) are hand-authored, not generated. Both audits performed independent name-by-name comparisons across all 33 interfaces (Codex: empty `missing_interfaces` / `extra_interfaces` / `field_mismatches`; Claude: 1:1 inventory match across high-risk DTOs `MeetingView`, `AgentMemoryView`, `ReplayMetadataView`, `LLMCallView`, `AgentTickStateView`, `BallotView`). `tsc:check` passes with zero errors at HEAD — proves no consumer is reading a non-existent TS field. Nullability convention is consistent (`X | None` → `X | null`; `tuple[X, ...]` → `X[]`).

## 6. Class D — Frontend store / component leak findings

**No findings.** Both audits scanned [frontend/src/store/replayStore.ts](frontend/src/store/replayStore.ts) and `frontend/src/components/*.tsx` field-access patterns; every access resolves to a declared TS field. The store caches the same `ReplayView` / `AgentMemoryView` shapes the API serves (which is in-contract — the spectator surface is intentionally privileged). No component renders `role`, `prompt_text`, `rendered_memory_text`, raw hashes, or raw replay actions to the casual-user surface; the 4.4 vertical slice is map-only and reads only `RoomView`, `agent_states`, and player color/id.

## 7. Class E — Determinism + state-hash findings

**No findings.** [tests/api/test_replay_loader.py::test_state_hash_mismatch_raises_with_bad_tick](tests/api/test_replay_loader.py#L116) and [tests/api/test_replays.py::test_get_replay_state_mismatch_returns_500](tests/api/test_replays.py) both pass at HEAD; replay playback verifies every recorded tick hash via [api/replay_loader.py:360](api/replay_loader.py#L360) before constructing any DTO, and meeting post-application hashes are checked at [api/replay_loader.py:424](api/replay_loader.py#L424). Both audits also booted `uvicorn` against `AILIBI_REPLAY_DIR=/tmp/eval-50` and hit `headless-seed-22` end-to-end: 200, 8 ticks, 1 meeting, 4 agents (matches `DEFAULT_NUM_PLAYERS=4` at [orchestrator/game.py:94](orchestrator/game.py#L94); the audit prompt's "typically 5–7" was a stale assumption). No 500s, no mismatch errors — engine playback is byte-identical to the recorded tournament.

## 8. Repair task proposals

**None.** No Blocking findings. The three Class A informational notes (R-1, R-2, R-3) are not repair tasks — they ride along on the first PR that touches each file:

- **R-1 (any time):** when the next PR edits [api/schemas.py](api/schemas.py#L137), drop `target_room` / `planned_path` from the `AgentTickStateView` docstring and replace with the actual omitted attributes (`position`, `last_action`).
- **R-2 (before Task 4.7 dispatch):** rename `BeliefEntryView.last_updated_tick` → `snapshot_tick`, OR wire a real per-belief recency through `PlayerBelief`. The rename is the cheap path and unblocks 4.7's BeliefMatrix without scope creep.
- **R-3 (before Task 4.6 dispatch):** add `agent_id: str | None` to `LLMCallRecord` and propagate to `LLMCallView`; the call site in [meetings/manager.py:555-565](meetings/manager.py#L555) already knows the agent. Decide between "patch existing replays" and "leave old logs at `None`" before 4.6 begins so ThoughtStream's UI logic can rely on the field.

## 9. Reconciliation

### 9.1 Comparison table

| ID | Class | Title | Codex | Claude | Verified | Final severity | Disposition |
|---|---|---|---|---|---|---|---|
| R-1 | A | `AgentTickStateView` docstring cites attributes that don't exist on `PlayerState` | — | Info | yes (docstring @ [api/schemas.py:144](api/schemas.py#L144); fields @ [engine/entities.py:19-26](engine/entities.py#L19)) | Informational | Unique-but-verified |
| R-2 | A | `BeliefEntryView.last_updated_tick` is the meeting tick, not per-belief recency | — | Info | yes (loader @ [api/replay_loader.py:1119](api/replay_loader.py#L1119); `PlayerBelief` @ [agents/memory/beliefs.py:57-65](agents/memory/beliefs.py#L57)) | Informational | Unique-but-verified |
| R-3 | A | `LLMCallView` / `LLMCallRecord` carries no `agent_id`; per-call attribution unrecoverable | — | Info | yes (DTO @ [api/schemas.py:357-370](api/schemas.py#L357); source @ [orchestrator/replay.py:51-71](orchestrator/replay.py#L51)) | Informational | Unique-but-verified |

No Blocking, High, Medium, or Low findings exist in either audit. No findings were Dropped, Promoted, or Demoted. No New findings were surfaced during reconciler verification.

### 9.2 Disagreements and resolutions

The two audits do not actively disagree. Codex reports zero findings of any severity; Claude reports three Class A informational notes. The dispositions for R-1/R-2/R-3 are *Unique-but-verified*, not *Confirmed* — Codex's per-DTO table did not consider the docstring freshness of `AgentTickStateView` (R-1), the semantic-fidelity question on `last_updated_tick` (R-2), or the forward-looking absence of `agent_id` on `LLMCallRecord` (R-3) as in-scope items. Re-verification at HEAD reproduces each cited evidence chain. Severity is held at **Informational** for all three: none describes a leak, drift, or determinism break — the audit prompt's five-class scope. R-1 is a comment-only freshness issue (the field set is correct); R-2 and R-3 are forward-looking schema-shape notes for Tasks 4.7 and 4.6 respectively, both of which Claude explicitly framed as non-blocking. Neither auditor's grading was rejected; Codex was silent on these items and Claude graded them informational, so no severity tie-break was needed.

### 9.3 Verdict reconciliation

Both source audits adopt verbatim "Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8." No tie-break required; the reconciler adopts the same string.

## 10. Required closing fields

- **Report path:** `audits/audit-2026-05-26-2316-mid-phase-4-dto-reconciled.md`
- **Verdict:** Mid-phase DTO audit passes — proceed to fan out 4.4.5–4.8.
- **Findings count by class:**
  - Class A — DTO field leakage: 0 blocking, 3 informational
  - Class B — Endpoint response drift: 0
  - Class C — TypeScript / Pydantic drift: 0
  - Class D — Frontend store / component leak: 0
  - Class E — Determinism + state-hash: 0
- **Total findings:** 0 blocking, 3 informational.
- **Disposition counts:** Confirmed 0 / Unique-but-verified 3 / Promoted 0 / Demoted 0 / Dropped 0 / New 0.
