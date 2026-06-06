# Phase 8 — Deduction-substrate restructure

## Goal
Rebuild the game substrate so social deduction is viable, then re-record the
canonical eval set on it. Three coupled changes land as one new baseline:
per-player task instances (real Among-Us tasks; removes the 12-task seed cap), the
**9p/2i** canonical roster (parity at 5 crew deaths → longer games → more meetings),
and a reactive **accusation-chain** meeting protocol (fewer LLM calls, real
confrontation). This is a substrate/mechanics phase, distinct from Phase 7's agent
intelligence, which resumes on the new substrate after the Phase 8 close.

## Scope decisions (locked — DESIGN.md is the source of truth)
DESIGN.md was rewritten for these (§3.2/§3.3 task ownership, §3.5 win/balance,
§5.2/§5.3 + Appendix A chain protocol, §8 scope, §2 module map, §11.4 versioning).
The full code blast radius — every touchpoint cited by `file:symbol` — is in
`audits/restructure-impact-map-2026-06-04-0223.md`; each contract below lifts its
Files-in-scope from that map's §2a–2f inventory and its DoD guards from §3. The
load-bearing locks:
- **Tasks** keyed per-instance `"{owner}:{map_task_id}"`; the **agent-facing id
  stays the map id** (the engine resolves by `actor`), so the observation / policy /
  prompt layers and the scripted-fixture `do_task` payloads are unchanged.
- **9p/2i at `tasks_per_crewmate=2`**; the flat **4p/1i at 1 task** stays the
  descriptor-less determinism / leak reference.
- **Meeting** = one ordered `turns` list (opening → reactive chain → opt-in →
  vote); deterministic 3-condition termination; turn id `{meeting}:turn-{N}`.
- **Versioning:** no replay `format_version` field (the per-tick `state_hash` +
  `roster.json` reject old bytes); the report `CURRENT_FORMAT_VERSION` bumps 1→2.
- **Substrate reset (owner-confirmed):** both committed sets re-recorded in ONE
  combined re-record (8.12); the two byte-breakers (task re-key, meeting reshape)
  never split across PRs.

## Parallelism
Two independent tracks converge on the single combined re-record (8.12):
- **Track A (task model):** 8.1 → 8.2 → 8.5; 8.1 → 8.3 → 8.4; 8.6 after 8.1/8.3/8.5.
- **Track B (meeting):** 8.7 → 8.8 → 8.9; 8.7 → 8.10.
- **8.11** (versioning) after 8.1 + 8.7. **8.12** (re-record gate) after 8.1–8.11.
  **8.13** docs after 8.12.

`eval/determinism_test.py` (two fresh recordings, no committed bytes) is the running
determinism guard and stays green throughout; the committed-set reconstruction tests
are skipped from the first state-hash / record change (8.1, 8.7) until 8.12
re-records and re-enables them.

## Tasks

### Task 8.1 — Per-player task re-key (engine core)
**Branch:** `phase-8-per-player-task-rekey`
**Depends on:** none (the R-0 DESIGN.md rewrite is merged; this is the substrate root)
**Section refs:** DESIGN.md §3.2 (state model — per-player tasks), §3.3 (Task entity), §3.5 (win count over instances); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.1, §5 decisions 1–5
**Complexity:** Integration

Re-key `WorldState.tasks` from a single `Mapping[TaskId, TaskState]` (the engine asserts `TaskState.id == <dict key>`) to per-player instances keyed by the stable string `"{owner}:{map_task_id}"`, so multiple crewmates hold the same map task with independent progress (DESIGN.md §3.2). `TaskState` keeps `owner` and gains `map_task_id` (its anchor room is `game_map.tasks[map_task_id]`), with the instance `id` equal to the composite key. The agent-facing id stays the MAP id: the engine resolves `(action.actor, map_task_id)` to the actor's own instance, so no observation / policy / prompt change is needed here (that propagation is 8.3) and the scripted `do_task` payloads keep their map ids. This is the root reset vector — it changes `_serialize_world_state` and therefore every game's per-tick `state_hash`.

This task is engine-only: it lands with the engine unit suites green plus a new same-map-task two-owners progress-isolation case, but it does NOT touch the seeder (8.2), the observation / agent layer (8.3), or re-record committed data (8.12). Because the `state_hash` changes, the committed-set reconstruction tests can no longer reconstruct the old bytes; they are skipped here with a reason pointing at the 8.12 re-record (mirroring Task 7.9). `eval/determinism_test.py` re-records two fresh games and stays green.

**Files in scope:**
- engine/world.py (`WorldState.tasks` re-keyed to per-instance `"{owner}:{map_task_id}"`; the disjoint-namespace check re-confirmed)
- engine/entities.py (`TaskState` gains `map_task_id`; instance `id` equals the composite key; `owner` retained)
- engine/tick.py (`_advance_tasks` and `_apply_do_task` resolve the ACTOR's own instance via `(actor, map_task_id)`; `_apply_kill` owner-filter; `_task_progress_event` carries the MAP id)
- engine/events.py (`event_to_dict` Task* branch carries the map id; `actor` disambiguates owners)
- engine/win_conditions.py (`evaluate_win_conditions` task-complete count over live instances; rule unchanged, magnitude scales)
- tests/engine/test_tick.py + tests/engine/test_world_state.py + tests/engine/test_win_conditions.py (per-instance keying; a same-map-task two-owners progress-isolation case; dead-owner instance drop; win count)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (SKIP the committed-set reconstruction cases with a reason referencing the 8.12 re-record — the state_hash change invalidates the old bytes)

**Files NOT in scope:**
- orchestrator/seeder.py (the cap removal + instance minting is 8.2)
- observation/, agents/, meetings/ (the agent-facing id is the map id — the propagation triad is 8.3; meetings are Track B)
- replays/samples/ (no re-record here; that is the combined 8.12 gate, which re-enables the skipped recon tests)
- engine/maps/canonical_1.yaml (the 12-task map is unchanged; per-player overlap carries 9p/2i — DESIGN.md §3.5)

**Definition of done:**
- [ ] `WorldState.tasks` is keyed by the per-player instance string `"{owner}:{map_task_id}"`; `TaskState` carries `owner` + `map_task_id` + an instance `id` equal to the key; two crewmates can hold the same map task with independent progress.
- [ ] `do_task` resolves `(action.actor, payload.task_id)` → the actor's own instance: a two-owners progress-isolation test proves one owner's progress never advances the other's, and a foreign/out-of-pool map id fails loud.
- [ ] `_apply_kill` drops only the victim's incomplete instances; `engine/win_conditions.py` counts completion over live instances; the dead-crewmate rule (DESIGN.md §3.5) holds per-instance-owner.
- [ ] `TaskProgressed` / `TaskCompletedEvent` carry the MAP id (owner via `actor`), so `game_map.tasks[event.task_id]` room lookups are unchanged.
- [ ] The committed-set reconstruction tests (`test_replay_loader.py` committed 4p/1i + 7p/2i; `test_win_condition_selfcheck.py` committed cases) are skipped with an explicit reason referencing the 8.12 re-record; `eval/determinism_test.py` (fresh recordings) stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The composite key keeps `WorldState.tasks` a flat str-keyed dict (`orchestrator/replay.py::_to_jsonable` requires str keys), so serialization stays shape-compatible — only the bytes change. Read `engine/tick.py::_advance_tasks` (`tasks.get(task_id)` + the `task.id != task_id` assert) and `_apply_do_task` (`state.tasks.get(payload.task_id)` + `tasks[task.id]=replace(...)`): both must resolve `f"{actor}:{map_task_id}"`, not the bare map id. The win count in `engine/win_conditions.py` iterates the dict — unchanged logic, larger denominator. Keep the engine pure (no RNG) so replay stays deterministic. The committed-recon skips are time-bound — 8.12 re-records and re-enables them; do not leave them skipped beyond the phase.

**Integration risk:**

This is the root state-hash reset vector for the whole phase; every other task and the combined re-record build on its keyspace. The map-id-agent-facing decision is what keeps the blast radius engine-local — preserve it (do NOT leak the instance id into actions or observations). The committed-recon test skips are intentional and time-bound (8.12 un-skips them); `eval/determinism_test.py` must stay green throughout as the running guard.

**Dependency check:**
- `uv run python -c "from engine.world import WorldState; from engine.entities import TaskState"`

**Ready-to-paste prompt:** `agent_prompts/task-8-1-per-player-task-rekey.md`

### Task 8.2 — Seeder cap removal + deterministic instance minting
**Branch:** `phase-8-seeder-instance-minting`
**Depends on:** 8.1
**Section refs:** DESIGN.md §3.2 (per-player tasks), §3.5 (no seed cap); audits/restructure-impact-map-2026-06-04-0223.md §2a (seeder), §4 coupling 1
**Complexity:** Medium

Remove the fail-loud cap in `orchestrator/seeder.py::_build_tasks` (`required = num_crewmates × tasks_per_crewmate > len(game_map.tasks)`) and mint per-player task instances deterministically so multiple crewmates hold the same map task with independent progress (the keyspace landed by 8.1). The seeder's current "each crewmate owns `tasks_per_crewmate` DISTINCT map ids via a flat cursor" contract is replaced by "each crewmate owns `tasks_per_crewmate` instances, drawn with overlap allowed, minted from a seed-shuffled deal so the assignment stays a pure function of the seed." `scripts/_manifest_writer.py::_validate_roster_is_seedable` mirrors the same cap and must drop it in lockstep, or it rejects a 9p/2i sidecar (`7×2=14 > 12`). This unblocks 9p/2i seeding (8.5).

**Files in scope:**
- orchestrator/seeder.py (`_build_tasks` / `_assign_tasks` / `seed_initial_state` — remove the cap, mint instance ids deterministically; the byte-identity-prefix docstring contract is rewritten)
- scripts/_manifest_writer.py (`_validate_roster_is_seedable` — drop/relax the mirrored 12-cap so a 9p/2i descriptor validates)
- tests/orchestrator/test_seeder.py (invert the task-pool-exhausted test; replace the distinct-global-id + flat-cursor + golden `(owner,task_id)` contracts with a per-player-instance + new-golden contract; a same-map-task two-owners case)

**Files NOT in scope:**
- engine/ (the keyspace + resolution are 8.1)
- orchestrator/game.py (the 9p/2i roster preset is 8.5)
- replays/samples/ (no re-record; that is 8.12)

**Definition of done:**
- [ ] `_build_tasks` no longer caps `num_crewmates × tasks_per_crewmate` against `len(game_map.tasks)`; it mints per-player instances deterministically (a pure function of the seed; no new RNG draw beyond the existing seeded shuffle), allowing overlap so two crewmates can hold the same map task.
- [ ] A 9p/2i roster at `tasks_per_crewmate=2` seeds successfully (14 instances over the 12 map tasks); the flat 4p/1i at 1 task seeds the same instances as before (only their key shape changes).
- [ ] `scripts/_manifest_writer.py::_validate_roster_is_seedable` accepts a 9p/2i descriptor (the mirrored cap is gone).
- [ ] `tests/orchestrator/test_seeder.py` is rewritten: the exhausted-pool test is inverted/removed, and the distinct-id / flat-cursor / golden-tuple contracts are replaced with per-player-instance contracts incl. a two-owners-same-map-task case.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Keep the deal a pure function of the seed: shuffle once, then for each crewmate take `tasks_per_crewmate` map ids *with replacement allowed across crewmates* (e.g. `map_task_ids[i % len(map_task_ids)]` over a global cursor, or a per-crewmate independent slice) and mint `TaskState(id=f"{owner}:{map_task_id}", owner=..., map_task_id=...)`. The 4p/1i flat path must mint the same instances it dealt before (so only the key shape, not the assignment, changes for that roster) — pin it with a golden test. Grep `_manifest_writer.py` for the seedable check so the two cap sites drop together. Confirm `engine/maps/canonical_1.yaml` stays at 12 tasks (no map growth — DESIGN.md §3.5); the cap removal, not a bigger pool, is what carries 9p/2i.

**Ready-to-paste prompt:** `agent_prompts/task-8-2-seeder-instance-minting.md`

### Task 8.3 — Task-id propagation: observation + agents + memory
**Branch:** `phase-8-task-id-propagation`
**Depends on:** 8.1
**Section refs:** DESIGN.md §3.2 (agent-facing map id), §1.3 (observation firewall); audits/restructure-impact-map-2026-06-04-0223.md §2a, §3.2, §4 coupling 5
**Complexity:** Integration

Thread the per-player task model through the observation / agent / memory layer so the render-field-reader **triad** agrees that the agent-facing id is the MAP id resolving to the acting agent's own instance (DESIGN.md §3.2). The list the impact map names must move in lockstep: `observation/packet.py::SelfView.pending_task_id` (the field — stays a map id, own-task only), `agents/perception.py::_self_state_payload` (the render into prompt JSON), and `agents/memory/store.py` (the reader). Plus `observation/service.py::_pending_task_id_for_agent` (stays owner-scoped — the leak guarantee) and `_global_view` (the `tasks_total` / `task_completion_percent` denominator over live instances), `observation/public_map.py::task_locations` (map-keyed, unchanged), the DoTask payload (`observation/action_intent.py` + `engine/actions.py`), and the `do_task` round-trip in `agents/tactical/{crewmate,impostor}_policy.py`. A drift here silently targets the wrong owner's instance.

**Files in scope:**
- observation/service.py (`_pending_task_id_for_agent` owner-scoped under the new keyspace; `_global_view` denominator + `task_completion_percent`)
- observation/packet.py (`SelfView.pending_task_id` stays the map id, own-task only; `GlobalView.tasks_total` count over instances)
- observation/public_map.py (`PublicMapView.task_locations` keyed by map id — confirm unchanged)
- observation/action_intent.py + engine/actions.py (`DoTask` payload `task_id` stays the map id; engine resolution agrees)
- agents/perception.py (`_self_state_payload` render of `pending_task_id`; `_global_state_payload` task counts)
- agents/memory/store.py (the pending-task completion-inference reader works on the map id)
- agents/tactical/crewmate_policy.py + agents/tactical/impostor_policy.py (the `task_locations.get(pending_task_id)` → `do_task(task_id=...)` round-trip)
- tests/agents/ + tests/observation/test_service.py + tests/fixtures/memory_rendering/* (the triad agrees; a crewmate never sees another's ownership; do_task targets the right owner; memory-render goldens regenerate)

**Files NOT in scope:**
- engine/tick.py, engine/world.py (the keyspace + resolution are 8.1)
- api/, frontend/ (the spectator task-count mirrors are 8.4)
- meetings/ (Track B)

**Definition of done:**
- [ ] `SelfView.pending_task_id` is the agent's own map task id (never another player's task or any ownership); `_pending_task_id_for_agent` is owner-scoped by construction.
- [ ] The render-field-reader triad (`SelfView.pending_task_id` ↔ `agents/perception.py::_self_state_payload` ↔ `agents/memory/store.py`) and the `DoTask` round-trip in both tactical policies all agree the map id resolves to the ACTOR's own instance; a do_task targeting test proves the right owner advances.
- [ ] `_global_view.task_completion_percent` / `GlobalView.tasks_total` count over live instances; the value equals the engine's instance total.
- [ ] The memory-rendering golden fixtures regenerate (`tasks_total`, the "You completed {task}" line); `tests/observation/test_service.py` covers a multi-impostor packet whose crewmate-recipients carry no foreign task ownership.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The agent-facing id is the MAP id (8.1's decision), so most of this layer is a re-confirm, not a rewrite: `task_locations` stays keyed by map id, the DoTask payload stays a map id, and the engine (8.1) resolves `(actor, map_task_id)`. The real edits are (a) `_pending_task_id_for_agent` returning the agent's own map task under the new keyspace, and (b) the `tasks_total` denominators counting instances. Keep `agents/` free of engine imports (lint-imports). Regenerate the memory-render goldens rather than hand-editing them.

**Integration risk:**

The leak firewall is load-bearing: a crewmate's packet must never carry another player's task ownership. The render/field/reader legs must move together — a drift makes `do_task` silently advance the wrong owner's instance (a determinism + correctness bug invisible to the type checker). Land the do_task round-trip test + the leak coverage together.

**Ready-to-paste prompt:** `agent_prompts/task-8-3-task-id-propagation.md`

### Task 8.4 — api/frontend task-count mirrors
**Branch:** `phase-8-task-count-mirrors`
**Depends on:** 8.1, 8.3
**Section refs:** DESIGN.md §3.2; audits/restructure-impact-map-2026-06-04-0223.md §2a (api), §2f (mirrors)
**Complexity:** Medium

Update the spectator task-count surface for the uncapped per-player denominator: `api/replay_loader.py` (`_task_progress`, `_tick_view` `tasks_*_total`, `_agent_memory_view` owned-task enumeration), the `api/schemas.py` task-count fields, and their 1:1 `frontend/src/types/api.ts` mirror. Display / count only — no engine or meeting logic — but the denominator is no longer capped at 12. The TS side is caught by `tsc --noEmit`, not pytest.

**Files in scope:**
- api/replay_loader.py (`_task_progress` / `_tick_view` `tasks_required_total`/`tasks_completed_total` / `_agent_memory_view` `owned=[t for t in state.tasks.values() if t.owner==pid]`)
- api/schemas.py (`AgentMemoryView` / `TickView` task-count fields — values change, shape stays int)
- frontend/src/types/api.ts (the 1:1 task-count mirror)
- tests/api/test_schemas.py (task-count field assertions over the instance denominator)

**Files NOT in scope:**
- api/schemas.py meeting DTOs + tests/api/test_leak.py snapshot (those move with the meeting reshape in 8.10)
- engine/, observation/, agents/ (8.1 / 8.3)

**Definition of done:**
- [ ] `api/replay_loader.py` computes per-agent and spectator task counts over per-player instances (`t.owner == pid` for per-agent; `len(state.tasks)` / instance count for totals); no count is capped at 12.
- [ ] `api/schemas.py` and `frontend/src/types/api.ts` task-count fields move in lockstep (the 1:1 type mirror); `tests/api/test_schemas.py` covers the new denominator.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally (incl. frontend `tsc:check`).

**Implementation hint:**

Pure follow-on from 8.1's keyspace: the loader already enumerates `state.tasks.values()` and filters by `owner`, so the logic survives — only the denominator scales. Keep the api/frontend type mirror in lockstep or the field-set checks fail. Do not touch meeting DTOs here (8.10 owns those + the `test_leak.py` snapshot).

**Integration risk:**

The api↔frontend type mirror must stay 1:1 (a drift fails `tsc` while pytest stays green). Scope is display/count only — no behavior — so it cannot affect replay or determinism.

**Ready-to-paste prompt:** `agent_prompts/task-8-4-task-count-mirrors.md`

### Task 8.5 — 9p/2i roster knobs + CLI/script threading
**Branch:** `phase-8-9p2i-roster`
**Depends on:** 8.2
**Section refs:** DESIGN.md §3.5 (9p/2i canonical roster), §8.1; audits/restructure-impact-map-2026-06-04-0223.md §2c, §5 decision 11
**Complexity:** Medium

Make 9p/2i a first-class roster (decision 11: rename `7p2i`→`9p2i`, presets `{4p1i, 9p2i}`). Add/rename `orchestrator/game.py::ROSTER_PRESETS['9p2i'] = RosterPreset(9, 2, 2)` and remove `7p2i`; thread it through `scripts/run_tournament.py` (`--roster-preset` choices auto-surface from `sorted(ROSTER_PRESETS)`), `scripts/run_game.py` (which is missing a `--tasks-per-crewmate` flag — add it and pass to `HeadlessGame`), and the `scripts/refresh_samples.sh` env block. `DEFAULT_NUM_PLAYERS`/`DEFAULT_NUM_IMPOSTORS`/`DEFAULT_TASKS_PER_CREWMATE` stay 4/1/2 (the flat baseline is the harness default, not the eval roster). Needs 8.2's cap removal so a 9p/2i roster can seed.

**Files in scope:**
- orchestrator/game.py (`ROSTER_PRESETS` — add `9p2i=RosterPreset(9,2,2)`, remove `7p2i`; defaults unchanged)
- scripts/run_tournament.py (`--roster-preset` choices from `sorted(ROSTER_PRESETS)`)
- scripts/run_game.py (add the missing `--tasks-per-crewmate` flag; pass to `HeadlessGame`)
- scripts/refresh_samples.sh (the documented env block updates to the 9p/2i values)
- tests/orchestrator/test_game.py + tests/scripts/test_run_tournament.py + tests/scripts/test_refresh_samples.py + tests/scripts/test_manifest_writer.py + tests/engine/test_rules.py (the roster-preset set-equality + `RosterPreset` tuples + 7→9 literals)

**Files NOT in scope:**
- orchestrator/seeder.py (cap removal is 8.2)
- replays/samples/ + roster.json + dir rename (the re-record + `7p2i/`→`9p2i/` rename is 8.12)

**Definition of done:**
- [ ] `ROSTER_PRESETS` is `{4p1i, 9p2i}` with `9p2i=RosterPreset(num_players=9, num_impostors=2, tasks_per_crewmate=2)`; `7p2i` is removed; `DEFAULT_*` stay 4/1/2.
- [ ] `run_tournament.py --roster-preset 9p2i` and `run_game.py --num-players 9 --num-impostors 2 --tasks-per-crewmate 2` both seed and run a game; `refresh_samples.sh`'s env block documents the 9p/2i routing.
- [ ] `refresh_samples.sh --dry-run` (9p/2i routing) echoes `roster: num_players=9 num_impostors=2 tasks_per_crewmate=2` — the resolved-roster preview reflects the new preset, not just the doc'd env block.
- [ ] `tests/orchestrator/test_game.py` roster-preset set-equality + tuple assertions, and the script/rules tests pinning 7p/2i, are updated to 9p/2i.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

`run_game.py` exposes `--num-players`/`--num-impostors` but not `--tasks-per-crewmate` — add it (default `DEFAULT_TASKS_PER_CREWMATE`) so a single 9p/2i game runs at the eval count. The `7p2i`→`9p2i` directory rename + `roster.json` rewrite is NOT here; this task only changes the in-code preset + CLI knobs (the committed-data move is 8.12). Grep for `7p2i` / `RosterPreset(7` across tests to find every pin.

**Integration risk:**

Replacing (not adding alongside) the `7p2i` preset means the old committed 7p/2i set's loader path is retired in 8.12's re-record — keep the rename consistent across the preset, the scripts, and (in 8.12) the directory. The flat-4p/1i default must stay 4/1/2 or the descriptor-less baseline silently reseeds wrong.

**Ready-to-paste prompt:** `agent_prompts/task-8-5-9p2i-roster.md`

### Task 8.6 — Leak firewall at 2-of-9 + per-player-task sweep fixture
**Branch:** `phase-8-leak-2of9-task-sweep`
**Depends on:** 8.1, 8.3, 8.5
**Section refs:** DESIGN.md §1.3, §11.2 (the leak test); audits/restructure-impact-map-2026-06-04-0223.md §2e, §3.2, §5 decision 13
**Complexity:** Medium

Extend the project's strongest leak guard to the new substrate (decision 13). The DESIGN §11.2 property sweep (`tests/observation/test_leak_property.py`) hard-codes a 7-player roster (`range(1,8)`) and builds `tasks={}` — so it never exercises `SelfView.pending_task_id` under the per-player keyspace. Widen it to **9 players**, keep **multi-impostor** coverage (2 and 3 impostors), and add a fixture **with per-player tasks** so the own-task-only invariant is actually swept. Re-confirm the `eval/leak_test.py` crew-empty `fellow_impostor_ids` invariant holds at 2-of-9. (The `tests/api/test_leak.py` `EXPECTED_*` snapshot tripwires move with the schema in 8.10, not here.)

**Files in scope:**
- tests/observation/test_leak_property.py (`_ROSTER_PLAYER_IDS` `range(1,8)`→9; `_VALID_IMPOSTOR_COUNTS` keeps ≥2; a per-player-task fixture so `pending_task_id` is exercised under the new keyspace; the crew-empty `fellow_impostor_ids` assertion per packet)
- eval/leak_test.py (re-confirm the `_assert_no_role_bearing_values` + crew-empty invariant over the scripted games; no behavior change)

**Files NOT in scope:**
- tests/api/test_leak.py (its `EXPECTED_DTOS` / `EXPECTED_EVAL_REPORT_FIELDS` snapshots update with the schema in 8.10)
- observation/, agents/ (the leak-safe wiring is 8.1 / 8.3 — this task tests it)

**Definition of done:**
- [ ] The property sweep runs at 9 players and at 2 (and 3) impostors, asserting `self_state.fellow_impostor_ids == ()` for every crewmate-recipient packet and no role-bearing value in any agent-visible field.
- [ ] A per-player-task fixture makes the sweep exercise `SelfView.pending_task_id` under the new keyspace (no longer `tasks={}`), proving a crewmate sees only its own task and no ownership of others.
- [ ] `eval/leak_test.py`'s crew-empty `fellow_impostor_ids` + no-role-leak invariants pass unchanged at 2-of-9.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The sweep's `_roster_initial_state` builds `tasks={}` — add per-player task instances (via the 8.2 seeder or a hand-built fixture) so `pending_task_id` is non-empty and the own-task-only path is actually swept. Widen `_ROSTER_PLAYER_IDS` and keep `_VALID_IMPOSTOR_COUNTS` covering 2 and 3. This task TESTS the firewall; it does not change `observation/` (that is 8.1/8.3).

**Integration risk:**

This is the safety net for the whole substrate change — a leak introduced by 8.1/8.3 (a crewmate seeing another's task ownership) or by 9p multi-impostor routing must surface here. Do not weaken the assertions to make them pass; a failure means the wiring leaked.

**Ready-to-paste prompt:** `agent_prompts/task-8-6-leak-2of9-task-sweep.md`

### Task 8.7 — Meeting accusation-chain protocol + record schema
**Branch:** `phase-8-meeting-chain-protocol`
**Depends on:** none (the R-0 DESIGN.md meeting-protocol rewrite is merged; this is the meeting-track root)
**Section refs:** DESIGN.md §5.2 (chain protocol), §5.3 (turn record), §5.4 (contradictions), Appendix A (`MeetingTurn`); audits/restructure-impact-map-2026-06-04-0223.md §2b, §3.1, §5 decisions 6–9
**Complexity:** Integration

Replace the parallel-reports + fixed-`round_count` statement loop + vote with the reactive accusation chain (DESIGN.md §5.2): one ordered `turns` list — opening (accuse-or-unsure) → reactive chain (the accused responds; next speaker is the accused; deterministic 3-condition termination) → opt-in info-share (relevant non-speakers, terminal, no chain-extension) → vote. Reshape `meetings/schemas.py` (`Statement.round_index` → `turn_index` + `reply_to` + `turn_kind`; `MeetingTranscript` → an ordered `turns` tuple; `ReportDocument`'s observations/claims fold into the `opening` turn), rewrite `meetings/manager.py` (the sequencer, `_speaker_order` reactive turn-passing, `_collect_*` into chain + opt-in turns, `_statement_id` → a turn ordinal `{meeting_id}:turn-{N}`, the renderer Protocols, per-turn deadlines + a total cap), and rewrite `meetings/transcript.py::is_canonically_ordered` (the production C-3 impl keyed on `round_index`) to chain-turn order. The 7.12 teammate firewall guards (`exclude_teammate_accusation_claims` / `drop_teammate_statement_target` / `coerce_teammate_ballot_to_skip`) wrap EVERY turn-kind. Contradictions (§5.4) recompute once over the full transcript before voting. This changes `MeetingReplayEntry.transcript` (`extra='forbid'`), so committed meeting rows stop validating — the second byte-breaker.

**Files in scope:**
- meetings/manager.py (run sequencer; `_speaker_order` reactive turn-passing; `_collect_*` into chain + opt-in turns; `_statement_id` → `{meeting_id}:turn-{N}`; renderer Protocols + a per-turn/opt-in input; per-turn deadlines + total cap; the 7.12 guards on every turn)
- meetings/schemas.py (`Statement` → `MeetingTurn` with `turn_index`/`reply_to`/`turn_kind`; `MeetingTranscript` → ordered `turns`; `ReportDocument` observations/claims fold into the opening turn — keep `found_body`/`saw_player` queryable for vote_correctness)
- meetings/transcript.py (`is_canonically_ordered` rewritten from `round_index` to chain-turn order)
- meetings/voting.py (tally/plurality survive; confirm the candidate set over the final transcript)
- tests/meetings/test_manager.py + test_schemas.py + test_transcript.py + test_contradictions.py + test_voting.py (the chain sequencer, termination, turn ids, 7.12 guards on every turn, contradiction recompute, vote — rewritten green; a deterministic replay-walk-of-the-chain test)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (the committed-set meeting-recon cases stay SKIPPED pending 8.12 — idempotent with 8.1's skip; coordinate the trivial overlap at merge)

**Files NOT in scope:**
- agents/strategic/ (the prompts + reasoner producers are 8.8)
- eval/, api/, frontend/ (the metric re-pointing + meeting DTOs are 8.10)
- orchestrator/replay.py format_version (8.11); replays/samples/ (8.12)

**Definition of done:**
- [ ] `MeetingTranscript` is one ordered `turns` tuple of `MeetingTurn{turn_index, speaker, turn_kind ∈ {opening,reply,opt_in}, reply_to, observations, claims, free_text}`; turn ids are `{meeting_id}:turn-{N}` (unique across repeat speakers); `found_body`/`saw_player` observations live on the opening turn.
- [ ] The sequencer runs opening → reactive chain → opt-in → vote; the chain terminates deterministically (no new accusation / re-accusation cycle / turn-count == living-player-count) and a replay walks the recorded turn list without re-calling the LLM.
- [ ] Opt-in is limited to living non-speakers with a relevant observation, one terminal turn each, and an opt-in turn never extends the chain; contradictions recompute once over the full transcript before voting.
- [ ] The 7.12 teammate firewall guards wrap every turn-kind (an impostor never accuses/incriminates/votes a fellow impostor); `meetings/voting.py` tally + tie→SKIP are preserved.
- [ ] The meeting test suite is rewritten green incl. a deterministic chain-replay-walk test; the committed-set meeting-recon cases stay skipped pending 8.12; `eval/determinism_test.py` (fresh recordings) stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The chain's next speaker is a pure function of the prior turn's accusation target, and termination is a pure function of the recorded turns — keep both deterministic so replay reconstructs from the recorded turn list (no LLM re-call). Route the 7.12 guards through one per-turn chokepoint so every turn-kind inherits them. Keep the strict `AlibiClaim` chronology + the 7.10 fail-soft on a malformed turn. The committed-recon skip is shared with 8.1 (idempotent); 8.8 carries the prompts/reasoner that drive the turns, 8.10 the eval/api readers — do not touch those here.

**Integration risk:**

This is the second byte-breaker and the single biggest meeting-side change; its `MeetingTranscript` shape is consumed by the four §11.3 eval metrics (8.10), the api meeting views (8.10), and the LLM `format=` schema (8.8/8.9), so lock the schema first. The deterministic termination + replay-walk is load-bearing (a non-deterministic chain breaks replay). Do not relax `extra='forbid'` to absorb old rows — they are intentionally re-recorded in 8.12.

**Ready-to-paste prompt:** `agent_prompts/task-8-7-meeting-chain-protocol.md`

### Task 8.8 — Meeting prompts + reasoner chain producers + version bump
**Branch:** `phase-8-meeting-prompts-reasoner`
**Depends on:** 8.7
**Section refs:** DESIGN.md §4.4 (strategic policy turns), §5.2, §6.6 (prompt rendering); audits/restructure-impact-map-2026-06-04-0223.md §2b, §4 couplings 2 & 4
**Complexity:** Integration

Reshape the meeting prompts + the reasoner to produce chain turns against 8.7's schema. The four templates (`accusation_round.j2`, `crewmate_report.j2`, `impostor_report.j2`, `vote_ballot.j2`) become the opening / reactive-turn / opt-in / vote templates; the reasoner's `produce_report` (the opener), `produce_statement` (a chain/opt-in turn — gains a "who accused me / prior turn" input), and `produce_vote` re-sequence; the trigger labels + `_TRIGGER_CALL_KIND` route turns to the meeting tier; the leak-scan allowlist (the impostor's own `fellow_impostor_ids`) carries over. Bump the four prompt versions in lockstep (they all land in `MeetingReplayEntry.prompt_versions`) and `orchestrator/game.py::DEFAULT_PROMPT_VERSIONS` + `DefaultMeetingRunner`/`build_default_meeting_runner`. `impostor_report.j2` + `vote_ballot.j2` carry the 7.12 firewall block. Editing `Statement` (8.7) changes the LLM `format=` schema — the provider tests are 8.9.

**Files in scope:**
- agents/strategic/prompts/accusation_round.j2 + crewmate_report.j2 + impostor_report.j2 + vote_ballot.j2 (reshaped to opening / reactive-turn / opt-in / vote; the four versions bump in lockstep; 7.12 blocks preserved)
- agents/strategic/prompts/loader.py (the opening / turn / opt-in / vote loaders + the reactive-turn input; `StrictUndefined` fails loud on a missing kwarg)
- agents/strategic/reasoner.py (`produce_report`/`produce_statement`/`produce_vote` + trigger allow-lists + `_TRIGGER_CALL_KIND`; the leak-scan + 7.12 guards on every turn)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` bumped; `DefaultMeetingRunner` / `build_default_meeting_runner` wire the reshaped callables; the prompt imports)
- tests/agents/test_strategic_prompts.py + test_strategic_reasoner.py (render each reshaped template + the new version markers; the three producers + the 7.12 guard on the chain path)

**Files NOT in scope:**
- meetings/ (the protocol + schema are 8.7)
- tests/llm/ (the provider parse-tolerance is 8.9)
- eval/, api/, frontend/ (8.10)

**Definition of done:**
- [ ] The four meeting templates render the chain shapes (opening / reactive turn with the prior-turn input / opt-in / vote); a crewmate's prompts carry no teammate block; an impostor's carry the 7.12 firewall block.
- [ ] `reasoner.py` produces an opening `MeetingTurn`, a chain/opt-in `MeetingTurn` (with `reply_to`), and a `VoteBallot`; the deterministic teammate guard + the leak scan run on every turn; the trigger labels route to the meeting tier with correct cost attribution.
- [ ] The four prompt versions bump in lockstep and are recorded via `DEFAULT_PROMPT_VERSIONS` / `MeetingReplayEntry.prompt_versions`; `tests/agents/test_strategic_prompts.py` pins the new markers.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The reasoner already branches the opener on role and runs the 7.12 guard + leak scan per output — extend those to every chain/opt-in turn and feed the reactive-turn template the accusing turn. Bump all four template version headers AND `DEFAULT_PROMPT_VERSIONS` together (a stale marker fails the manifest/replay cross-check). Keep the leak-scan allowlist for an impostor's own `fellow_impostor_ids` (the `## Your role:` precedent). No metric/api change here (8.10).

**Integration risk:**

The four-template version bump is atomic — a partial bump fails the replay/manifest provenance cross-check. The 7.12 firewall must hold on every turn-kind (not just the old statement slot). The `Statement`→`MeetingTurn` schema edit changes the JSON the provider is constrained by, so 8.9 must land with/after this.

**Ready-to-paste prompt:** `agent_prompts/task-8-8-meeting-prompts-reasoner.md`

### Task 8.9 — LLM provider parse-tolerance under the new turn schema
**Branch:** `phase-8-provider-turn-schema`
**Depends on:** 8.7, 8.8
**Section refs:** DESIGN.md §7 (provider), §5.3; audits/restructure-impact-map-2026-06-04-0223.md §2e, §4 coupling 2
**Complexity:** Small

The meeting-record schema (`MeetingTurn`, 8.7) is also the structured-output schema fed to the provider (`reasoner.py schema=... → ollama_client.model_json_schema() → format=`), so the `tests/llm` parse-tolerance suite pins the old `Statement` shape and must move. Update the meeting-schema fixtures + the `format=schema` round-trips. `llm/report_normalize.py` is discriminator-**aware** (it keys off the union variant's discriminator literal), so verify the discriminator field name it keys off still matches `MeetingTurn` (and the observation/claim leaves) after 8.7's reshape — a small adjustment is OK if the discriminator field moved — then confirm it still no-ops valid turns and repairs near-misses.

**Files in scope:**
- llm/report_normalize.py (verify the discriminator field name it keys off matches `MeetingTurn`; a small adjustment is OK if 8.7's reshape moved it — no schema relaxation)
- tests/llm/test_provider.py (`_MEETING_SCHEMAS` set; the `round_index`-pinned bad-payload fixtures; the structured-output kinds set)
- tests/llm/test_report_normalize.py (the `Statement` payload fixtures → `MeetingTurn`)
- tests/llm/test_real_provider.py (the skip-gated Ollama round-trips against the reshaped templates/schema)

**Files NOT in scope:**
- meetings/, agents/strategic/ (8.7 / 8.8)

**Definition of done:**
- [ ] `tests/llm` validates against `MeetingTurn` (not `Statement`): the `format=schema` JSON the provider is constrained by matches the new turn shape, and the parse-tolerance + fence-strip round-trips pass.
- [ ] `llm/report_normalize.py`'s discriminator field still matches `MeetingTurn` (a small adjustment if 8.7's reshape moved it); it no-ops an already-valid turn and still repairs a near-miss (a discriminator-mismatched key); no schema relaxation.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Grep `tests/llm` for `round_index` and `Statement` — those are the pins. The normalizer runs in the shared extract→validate path, so a turn that validates needs no normalization; only confirm the near-miss repair still fires under the new discriminator. The real-provider tests are opt-in (`AILIBI_RUN_OLLAMA_TESTS`); keep them skip-gated.

**Ready-to-paste prompt:** `agent_prompts/task-8-9-provider-turn-schema.md`

### Task 8.10 — Meeting eval-metric re-pointing + api meeting DTOs + frontend
**Branch:** `phase-8-meeting-eval-api-frontend`
**Depends on:** 8.7, 8.4
**Section refs:** DESIGN.md §11.3 (eval metrics), §5.2; audits/restructure-impact-map-2026-06-04-0223.md §2b, §2f, §4 couplings 9 & 10
**Complexity:** Integration

Re-point everything that READS the meeting transcript to the chain `turns` shape (8.7): the four §11.3 metrics, the api meeting DTOs + loader views, and the frontend meeting render. `eval/vote_correctness.py` reads `transcript.reports[*].observations` (found_body + saw_player — if these silently vanish, evidence-backed ejections read as zero), `eval/accusation_calibration.py` walks `reports[*].claims` + `statements[*].claims`, `eval/alibi_fabrication.py` resolves the author from `ReportDocument.agent_id` + `Statement.speaker` — all re-point to iterate `transcript.turns` filtered by `turn_kind`/`observations`/`claims`/`speaker`. `api/schemas.py` (`StatementView`/`ReportView`/`MeetingView`) + `api/replay_loader.py` (`_statement_view`/`_report_view`/`_meeting_view`) + the shared `tests/api/fixtures/sample_replay.py` builder + the frontend meeting components move to the turn shape. This task also owns the `tests/api/test_leak.py` snapshot tripwires (both the per-player-task fields from 8.4 and the meeting-turn fields), updated in lockstep. The `tests/api/fixtures/sample_replay.py` builder hand-constructs the meeting record with **stubbed** `prompt_versions` (it does not consume 8.8's `DEFAULT_PROMPT_VERSIONS`), so 8.10 depends only on 8.7's schema + 8.4's task fields — not on 8.8.

**Files in scope:**
- eval/vote_correctness.py + eval/accusation_calibration.py + eval/alibi_fabrication.py (re-point the transcript readers to `turns`; preserve the observation/claim/author reads)
- eval/report_schema.py (`MeetingReport.transcript` flows the new `MeetingTranscript`)
- api/schemas.py (`StatementView` → turn view; `ReportView`/`MeetingView` reshaped to the turn list) + api/replay_loader.py (`_statement_view`/`_report_view`/`_meeting_view`/`_classify_template_id`)
- api/routes/replays.py + api/routes/eval.py (response models + the `TournamentEvalReport`/`MeetingReport` mirror)
- frontend/src/types/api.ts + frontend/src/components/MeetingView.tsx + StatementCard.tsx + ReportCard.tsx + ContradictionBadge.tsx + ThoughtStream.tsx + frontend/src/store/replayStore.ts (group by chain turn-order, not rounds)
- tests/api/fixtures/sample_replay.py (the shared meeting-replay builder → the turn record) + tests/eval/test_{vote_correctness,accusation_calibration,alibi_fabrication,report_schema,tournament_report}.py + tests/api/test_{schemas,replays,eval_routes}.py
- tests/api/test_leak.py (`EXPECTED_DTOS` + `EXPECTED_EVAL_REPORT_FIELDS` updated for the per-player-task fields (8.4) AND the turn fields; `test_eval_report_surface_exposes_no_engine_state_field` still passes)

**Files NOT in scope:**
- meetings/ (8.7), agents/strategic/ (8.8), tests/llm/ (8.9)
- eval/meeting_quality.py (`compute_meeting_rate` is meeting-granularity, not turn — re-baseline its expectations in 8.12, not here)

**Definition of done:**
- [ ] The four §11.3 metrics iterate `transcript.turns` and still read the observations (found_body/saw_player for the kill-witness chain), the accusation claims, and the author — `vote_correctness` evidence-backed ejections are NOT silently zeroed by a moved field.
- [ ] `api/schemas.py` meeting DTOs + `api/replay_loader.py` views + `frontend/src/types/api.ts` + the meeting components render the chain turn-order (no "Round N" grouping); the api↔frontend mirror stays 1:1 (`tsc`).
- [ ] The shared `tests/api/fixtures/sample_replay.py` builder constructs the turn record; the dependent api/eval suites are updated.
- [ ] `tests/api/test_leak.py`'s `EXPECTED_DTOS` + `EXPECTED_EVAL_REPORT_FIELDS` are updated for both the per-player-task fields and the turn fields (the deliberate tripwire), and `test_eval_report_surface_exposes_no_engine_state_field` still passes.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally (incl. frontend `tsc:check` + build).

**Implementation hint:**

Lock 8.7's `MeetingTranscript` first, then re-point. The risk metric is `vote_correctness` — its kill-witness chain reads `reports[*].observations`; ensure the opening turn's observations are where it looks. Mirror any new field through `eval/report_schema.py` → `api/routes/eval.py` → `frontend/src/types/api.ts` exactly as Task 7.3/7.11 did, and update the `test_leak.py` snapshot in the SAME PR (it depends on 8.4's task fields, hence the 8.4 dependency). The `sample_replay.py` builder fans out to several suites — update it once, centrally.

**Integration risk:**

This is the meeting reshape's largest reader surface and it owns the leak snapshot tripwires for BOTH the task-model and meeting changes — they must update in lockstep or a leaked field slips in silently. The api↔frontend mirror + `tsc` is a separate gate from pytest. A moved observation field silently zeroing `vote_correctness` is the subtle failure to test against.

**Ready-to-paste prompt:** `agent_prompts/task-8-10-meeting-eval-api-frontend.md`

### Task 8.11 — Replay/report versioning
**Branch:** `phase-8-versioning`
**Depends on:** 8.1, 8.7, 8.10
**Section refs:** DESIGN.md §11.4 (versioning); audits/restructure-impact-map-2026-06-04-0223.md §3.3, §5 decision 10
**Complexity:** Medium

Apply decision 10. The replay JSONL stays **unversioned** — the per-tick `state_hash` (changed by 8.1) + the per-set `roster.json` already reject any old replay, so no `format_version` field is added to the replay entry models. Bump the offline report `eval/report_schema.py::CURRENT_FORMAT_VERSION` 1→2 because the `MeetingReport.transcript` shape changed (8.7/8.10); its fail-loud `_validate_format_version` then rejects committed v1 reports, which is why 8.12 regenerates both committed reports + `baseline.json`. Land this before the re-record so the new bytes are stamped consistently.

**Files in scope:**
- eval/report_schema.py (`CURRENT_FORMAT_VERSION` 1→2; the version validator's message; confirm the bump rejects v1)
- orchestrator/replay.py (CONFIRM no `format_version` field is added — document the state_hash + roster.json rationale in a comment/docstring)
- tests/eval/test_report_schema.py (the version-gate tests: v2 is current, v1 rejected with the no-migration message)

**Files NOT in scope:**
- replays/samples/ + the committed reports/baseline regeneration (8.12)
- meetings/, eval metric logic (8.7 / 8.10)

**Definition of done:**
- [ ] `CURRENT_FORMAT_VERSION == 2`; `_validate_format_version` rejects a v1 report fail-loud (no migration), and the version-gate tests assert v2-current / v1-rejected.
- [ ] No `format_version` field is added to the replay entry models; a comment records that the `state_hash` + `roster.json` are the replay-side guard (decision 10).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes (the committed reports are regenerated to v2 in 8.12; until then, any test loading a committed v1 report stays skipped/deferred to 8.12).
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

This is a constant bump + a fail-loud message + a docstring — not a migration. The committed reports become v1-invalid the moment this lands, so 8.12 must regenerate them in the same re-record; any test that loads a committed report stays deferred to 8.12 (note it). Keep the replay entry models field-free for version (the hash already rejects mismatches).

**Integration risk:**

The report bump makes every committed report fail-loud until 8.12 regenerates them — sequence so 8.11 lands close to 8.12, and do not bump until 8.7/8.10's transcript shape is final.

**Ready-to-paste prompt:** `agent_prompts/task-8-11-versioning.md`

### Task 8.12 — Combined re-record of BOTH sets + regenerate reports/manifests/baseline
**Branch:** `phase-8-combined-rerecord`
**Depends on:** 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 8.10, 8.11
**Section refs:** DESIGN.md §11.4; audits/restructure-impact-map-2026-06-04-0223.md §3.1, §4 coupling 3 (the phase gate)
**Complexity:** Integration

The single coordinated re-record — the phase gate. Both byte-breakers (task re-key 8.1, meeting reshape 8.7) and the versioning (8.11) have landed; now re-record BOTH committed sets in ONE PR (never split): the flat **4p/1i** reference (re-recorded, still 4p/1i @ 1 task) and the canonical **9p/2i** set (re-recorded from the old 7p/2i, dir renamed `7p2i/`→`9p2i/`, `roster.json` → `{9,2,2}`). Regenerate both `tournament-eval-report.json` (now v2), both `MANIFEST.md`, and the prompt-regression `baseline.json` — the latter needs its `eval/prompt_regression.py` source edit (roster + meeting) to land with it. Re-enable + green the committed-set reconstruction tests (now 9p/2i) that 8.1/8.7 skipped, and re-run the $0 Ollama eval gate at 9p/2i. The re-record itself is an operator step (`refresh_samples.sh`); this contract is the source edits + the validity gate + the test re-enables.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded + report regenerated to v2)
- replays/samples/9p2i/ (the renamed-from-7p2i set: 50 replay JSONL + roster.json `{9,2,2}` + tournament-eval-report.json + MANIFEST.md) and the `7p2i`→`9p2i` path literals in the loader/tests
- eval/prompt_regression.py (`_seeded_roles` roster thread + `run_prompt_regression` over the new meeting seeds — the source edit that gates the baseline reset)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (RE-ENABLE the committed-set recon cases at 9p/2i; un-skip + green)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed bytes + provenance rows + the 9p/2i routing)

**Files NOT in scope:**
- engine/, meetings/, agents/, observation/ (all behavior landed in 8.1–8.11; this task records + regenerates, it does not change logic)

**Definition of done:**
- [ ] Both committed sets are re-recorded in ONE PR (4p/1i re-recorded; 7p2i→9p2i renamed + re-recorded at `{9,2,2}`); both `tournament-eval-report.json` regenerated to format v2; both `MANIFEST.md` carry the new git_sha + the bumped prompt versions; `baseline.json` + its `v_a`/`v_b` replays regenerated.
- [ ] The committed-set reconstruction tests skipped by 8.1/8.7 are re-enabled and green at 9p/2i (byte-identical reconstruction via the per-set loader); `_verify_samples` + `build_sample_report --check` are consistent.
- [ ] **Validity gate (HARD):** friendly-fire kills == 0; every game reaches `game_over`; the leak suite passes at 4p/1i and 2-of-9; the Stage-A floor holds at 9p/2i (`meeting_rate ≥ 0.60`, ≥ 30 resolved meetings); impostor betrayal ballots/accusations == 0. An impostor-favored split is reported, not gated.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Run the re-record via `refresh_samples.sh` at the 9p/2i env (Ollama, $0). Net meeting cost vs the old 7p/2i R=1 baseline is genuinely uncertain — the chain terminates early on convergence (fewer calls) but 9 players means deeper chains + more opt-in candidates — so iterate on a seed-subset smoke first and expect the full 50-seed run to possibly take noticeably longer than the 7p/2i one. The `eval/prompt_regression.py` source edit must land WITH the regenerated `baseline.json` (the source gates the fixture). The `7p2i`→`9p2i` rename cascades to the loader dir constants + ~3 path literals + both MANIFESTs — grep `7p2i`. The 8.3 memory-render goldens hold across the re-record (no behavior change between 8.3 and here), so they need no second regeneration. Re-enable the two committed-recon tests last, after the bytes are on disk. This is the SINGLE combined re-record — do not split the two byte-breakers across PRs (an intermediate commit would have un-reconstructable data).

**Integration risk:**

The whole phase converges here; it must be one atomic PR. The validity gate is a HARD stop — if friendly-fire ≠ 0, a game lacks `game_over`, reconstruction is not byte-identical, or the meeting floor fails at 9p/2i, STOP and fix upstream rather than papering the gate. The flat-4p/1i identity (descriptor-less default stays 4p/1i @ 1 task) must hold or the determinism reference silently reseeds wrong.

**Ready-to-paste prompt:** `agent_prompts/task-8-12-combined-rerecord.md`

### Task 8.13 — Docs + scope reconciliation
**Branch:** `phase-8-docs-reconciliation`
**Depends on:** 8.12
**Section refs:** DESIGN.md (the §-rewrite is R-0, done); audits/restructure-impact-map-2026-06-04-0223.md §2f
**Complexity:** Small

Reconcile the historical build-plan prose to the post-restructure reality (accuracy, not correctness): `AGENT_IMPLEMENTATION.md` Phase-3 meeting tasks + roster prose ("5-7 agents, 1 impostor"), `README.md`, and any `AGENTS.md` §-number references that shifted. DESIGN.md itself is already rewritten (R-0).

**Files in scope:**
- AGENT_IMPLEMENTATION.md (Phase-3 meeting + roster prose → chain + 9p/2i)
- README.md (the agents/impostors/meeting one-liner)
- AGENTS.md (any DESIGN.md §-reference whose number shifted; light touch)

**Files NOT in scope:**
- DESIGN.md (R-0, already done), tasks/phase-*.md (this file aside)
- any code or committed data (all landed in 8.1–8.12)

**Definition of done:**
- [ ] `AGENT_IMPLEMENTATION.md` + `README.md` describe the accusation chain + 9p/2i + per-player tasks (no "5-7 agents / 1 impostor / 2 accusation rounds" residue); `AGENTS.md` §-references resolve.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Pure prose accuracy after the substrate settles. Grep the three docs for `7p2i` / `1 impostor` / `accusation round` / `report intake` and reconcile to DESIGN.md's current §5.2 / §8 wording.

**Ready-to-paste prompt:** `agent_prompts/task-8-13-docs-reconciliation.md`

## Wave 8.75 — baseline-validity repairs (added 2026-06-06, post-close audit)

Phase 8 closed 13/13, but the first v2 gameplay audit
(audits/audit-2026-06-06-0632-gameplay-data.md, verdict SIGNIFICANT_ISSUES) found the substrate
rule-clean yet the baseline distorted by four structural defects, all spot-verified against the
committed bytes (report §12): the free tick-1 spawn kill (26/50 games), silent 30s meeting-deadline
defaults in headless recording (11 turns, zero failed_call records), dangling ballot
primary_reason_id values (24/78), and kill-gifted task wins (31.7% of instances dropped; 12/37 crew
wins kill-enabled). Tasks 8.14–8.18 repair and re-record; precedent is phase-7's Wave 0.5.

Locked owner decisions (2026-06-06): the repairs are a continuation of Phase 8, not a new phase;
the §3.5 dead-owner drop semantics are KEPT (visibility via eval accounting, not a rule change);
impostor kill-suppression (audit gp-4c) is DEFERRED to the post-Wave-1 impostor activation wave —
the impostor build stays frozen for A/B hygiene.

Parallelism: 8.14, 8.15, and 8.17 dispatch immediately in parallel; 8.16 follows 8.15 (shared
meetings/manager.py + orchestrator/game.py); 8.18 is the operator-run gate after all four.

### Task 8.14 — Round-start kill cooldown
**Branch:** `phase-8-roundstart-cooldown`
**Depends on:** none (audit-repair root)
**Section refs:** DESIGN.md §3.4; audits/audit-2026-06-06-0632-gameplay-data.md gp-1
**Complexity:** Small

Audit gp-1 (urgent): impostor kill cooldowns are seeded to 0, granting a free unwitnessed kill at
tick 1 in 26/50 committed games (impostor win 42.3% with it vs 8.3% without). Seed every impostor's
cooldown to `game_map.kill_cooldown_ticks` (4 on the canonical map) so the first kill obeys the same
cadence as every later one. The engine is already correct (`engine/tick.py` resets to the map value
after each kill and decrements per tick) — only the seeder's initial value changes.

**Files in scope:**
- orchestrator/seeder.py (`seed_initial_state` cooldown init `{pid: 0 ...}` → `{pid: game_map.kill_cooldown_ticks ...}`; the "initialised to 0" docstring)
- tests/orchestrator/test_seeder.py (round-start cooldown assertion; a kill queued at tick 1 from the seeded state is engine-rejected with the cooldown reason)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (skip-mark the committed-set reconstruction cases pending 8.18 — reuse the Task 8.1 marker pattern verbatim)

**Files NOT in scope:**
- engine/ (tick/rules already handle reset + decrement; no engine change)
- replays/samples/** + the committed tournament-eval-report.json (the wave re-record is 8.18)
- meetings/, agents/, observation/

**Definition of done:**
- [ ] `seed_initial_state` seeds every impostor cooldown to `game_map.kill_cooldown_ticks`; the docstring matches; a regression test asserts the round-start value and the tick-1 kill rejection.
- [ ] The committed-set reconstruction tests are skip-marked pending 8.18 (the 8.1 pattern), and `eval/determinism_test.py` (fresh-vs-fresh, no committed bytes) stays green.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

A one-line behavior change plus its blast radius: the re-seeded initial state changes every
committed `state_hash`, so the committed-set recon tests fail until 8.18 re-records — skip-mark them
exactly like Task 8.1 did (same files, same comment style, naming 8.18 as the re-enabler) and do NOT
touch the committed bytes. The map value is already threaded (`load_canonical_map().kill_cooldown_ticks == 4`);
read it off the `game_map` argument, never a literal.

**Integration risk:**

Byte-breaker. An unskipped recon test or a partial re-record here leaves main red or
un-reconstructable; the bytes move only in 8.18.

**Ready-to-paste prompt:** `agent_prompts/task-8-14-roundstart-cooldown.md`

### Task 8.15 — Deadline-free headless recording + visible deadline defaults
**Branch:** `phase-8-deadline-free-recording`
**Depends on:** none (audit-repair root)
**Section refs:** DESIGN.md §5.1, §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-2
**Complexity:** Medium

Audit gp-2 (urgent): the headless recorder ran meetings with the interactive 30s per-turn/per-vote
deadlines, so slow local-Ollama calls silently defaulted 11 turns (9 of 91 openings) to
"(missed deadline; no turn submitted)" with no record of any kind — the report's failed_calls=0 was
true of the records and false of the run. Recording must never lose a turn to a wall-clock race, and
any default that does fire must be visible in the replay.

**Files in scope:**
- orchestrator/game.py (the headless recording path constructs `MeetingDeadlines(turn_seconds=None, vote_seconds=None)`; fired defaults route into the existing failed-call recording channel as `error_type="deadline_default"`)
- meetings/manager.py (surface a fired `_default_turn`/`_default_vote` to the caller; retry the opening turn once before defaulting)
- tests/meetings/test_manager.py + tests/orchestrator/test_game.py (default fires → surfaced + recorded; headless wiring passes None deadlines; the opening retry)

**Files NOT in scope:**
- meetings/schemas.py + orchestrator/replay.py (no DTO or record-kind change — `FailedCallReplayEntry.error_type` is a free string; reuse it)
- replays/samples/** (re-record is 8.18)
- llm/ (provider-level timeouts remain the fail-loud guard)

**Definition of done:**
- [ ] Headless recording runs meetings with `MeetingDeadlines(turn_seconds=None, vote_seconds=None)`; the interactive/API default stays 30s; the deadline choice is explicit at the construction site.
- [ ] A fired deadline default records a `FailedCallReplayEntry` with `error_type="deadline_default"` (meeting id, tick, defaulted phase in `error_message`) — no new replay record kind.
- [ ] The opening turn retries once before defaulting; tests cover the retry, the surfaced default, the recorded entry, and the headless None wiring.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

`MeetingDeadlines` already treats None as disabled — the work is wiring. Find where
`build_default_meeting_runner` / `DefaultMeetingRunner` construct the manager config on the headless
path and pass explicit None deadlines there. For visibility, mirror how failed LLM calls already
reach the replay log from the meeting path (the recording site in orchestrator/game.py) rather than
inventing a new channel; the manager only needs to expose enough for the orchestrator to write the
entry. Keep the `DEFAULT_TURN_FREE_TEXT` / `DEFAULT_VOTE_RATIONALE` marker strings unchanged — the
8.18 gate asserts zero of them in the new bytes.

**Integration risk:**

Recording-side only (no reconstruction impact on committed bytes). The risk is a silent behavior
fork between headless and interactive paths — keep the deadline choice explicit at the construction
site, not a hidden global.

**Ready-to-paste prompt:** `agent_prompts/task-8-15-deadline-free-recording.md`

### Task 8.16 — Ballot primary_reason_id integrity
**Branch:** `phase-8-ballot-reason-integrity`
**Depends on:** 8.15
**Section refs:** DESIGN.md §5.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-3
**Complexity:** Medium

Audit gp-3: 24 of 78 non-null ballot `primary_reason_id`s reference turns that do not exist —
voters hallucinate ids or copy the vote prompt's hardcoded example (`m-7:turn-4` appears verbatim in
other meetings' ballots), and a teammate-coerced ballot keeps its stale reason id. This corrupts the
ballot-follows-chain instrument Wave 1 depends on. Validate and normalize at the collection seam,
and make the prompt example real.

**Files in scope:**
- meetings/manager.py (`_collect_one_ballot` validates `primary_reason_id` against the transcript's turn-id set; recoverable `:turn-{k}` suffix forms normalize to the canonical id; unresolvable ids are nulled with an audit marker in `rationale_text` — mirror `_normalize_ballot_target`; `coerce_teammate_ballot_to_skip` additionally nulls the stale reason id)
- agents/strategic/prompts/vote_ballot.j2 (the decision-rule example cites a REAL turn id from the rendered transcript, never a hardcoded one; version marker → `vote_ballot/v4`)
- orchestrator/game.py (`DEFAULT_PROMPT_VERSIONS` vote_ballot → v4)
- tests/meetings/test_manager.py (dangling → nulled + marker; suffix form → canonical; coercion nulls the reason) + tests/agents/test_strategic_prompts.py (the v4 marker; the example sourced from transcript ids)

**Files NOT in scope:**
- meetings/voting.py (tally semantics unchanged — any tally change is a Wave-1 priced decision)
- tests/fixtures/prompt_regression/** + baseline.json (the version bump regenerates them in 8.18, not here)
- replays/samples/**

**Definition of done:**
- [ ] `_collect_one_ballot` accepts canonical turn ids, normalizes recoverable suffix forms, and nulls unresolvable ids with an audit marker (mirroring the invalid-target precedent); `coerce_teammate_ballot_to_skip` nulls `primary_reason_id` on coercion.
- [ ] `vote_ballot.j2` shows a real turn id from the live transcript as its example; the template and `DEFAULT_PROMPT_VERSIONS` read `vote_ballot/v4` in lockstep.
- [ ] Any test pinning `vote_ballot/v3` updates; the prompt-regression fixture regeneration is explicitly deferred to 8.18 (skip-mark a fixture test only if it hard-pins the version against committed bytes).
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The transcript is in scope at ballot collection — build the valid-id set once per vote phase from
`transcript.turns`. A recoverable suffix form is one whose `:turn-{k}` ordinal exists in THIS
meeting (normalize to `{meeting_id}:turn-{k}`); anything else is nulled, never guessed. Match
`_normalize_ballot_target`'s marker style so downstream eval can count normalizations per game. The
j2 example should reference an id from the transcript the template already iterates, so it can never
dangle.

**Integration risk:**

Shares meetings/manager.py and orchestrator/game.py with 8.15 — dependency-ordered; rebase on it at
merge. The v4 bump invalidates the committed prompt-regression baseline; that regeneration belongs
to 8.18 (an intermediate regeneration here would churn the fixtures twice).

**Ready-to-paste prompt:** `agent_prompts/task-8-16-ballot-reason-integrity.md`

### Task 8.17 — Kill-gifted win accounting in the eval report
**Branch:** `phase-8-kill-gifted-accounting`
**Depends on:** none (audit-repair root)
**Section refs:** DESIGN.md §3.5; audits/audit-2026-06-06-0632-gameplay-data.md gp-4
**Complexity:** Medium

Audit gp-4, accounting half (the §3.5 drop rule itself is KEPT by owner decision): the dead-owner
instance drop means each kill advances the task clock too — 222/700 instances dropped, 12/37 crew
"task wins" proximately enabled by the impostor's own kill, all invisible in the report. Make the
artifact measurable so balance reads use the kill-gifted split, never the raw crew win rate alone.

**Files in scope:**
- eval/balance_eval.py (the `GameReport` assembly derives `kill_gifted` for CREWMATE_TASKS games — the final tick resolves a kill and completes no task instance — plus per-game `instances_dropped` and `instances_complete_at_win`)
- eval/report_schema.py (`GameReport`/`TournamentReport` additive fields with defaults; aggregates: kill-gifted win count, total instances dropped, mean complete-at-win; `CURRENT_FORMAT_VERSION` stays 2)
- tests/eval/test_report_schema.py + tests/eval/test_tournament_report.py (synthetic gifted and non-gifted fixtures assert flag + counts; a pre-fields v2 report still loads via defaults)
- tests/api/test_leak.py (`EXPECTED_EVAL_REPORT_FIELDS` updated in lockstep)

**Files NOT in scope:**
- engine/ (the §3.5 drop semantics are unchanged — owner decision)
- agents/tactical/impostor_policy.py (kill suppression is deferred to the post-Wave-1 impostor wave)
- replays/samples/** + the committed tournament-eval-report.json (regenerated in 8.18)

**Definition of done:**
- [ ] `GameReport` carries `kill_gifted` / `instances_dropped` / `instances_complete_at_win` (additive, defaulted); `TournamentReport` aggregates them; the format version stays 2; a committed pre-fields report still validates.
- [ ] The flag is deterministic from the replay: winner CREWMATE_TASKS AND the final tick resolves a kill AND no task instance completes on that tick.
- [ ] `EXPECTED_EVAL_REPORT_FIELDS` matches; the synthetic fixtures cover both endings.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

The final-tick kill/completion facts need RESOLVED events — a recorded kill action can be
engine-rejected — so derive them with an engine walk (the win-condition-selfcheck pattern, or
api.replay_loader) rather than trusting raw action rows. instances_dropped = seeded instance count
minus `len(state.tasks)` at game end; instances_complete_at_win = completed count at end vs the
seeded total. Keep everything derived from the walk, deterministic. The schema is extra="forbid":
new fields must default so old reports load until 8.18 regenerates them.

**Integration risk:**

The fields must land before the 8.18 regeneration that first emits them (the dependency direction
already enforces this). No other task shares these files.

**Ready-to-paste prompt:** `agent_prompts/task-8-17-kill-gifted-accounting.md`

### Task 8.18 — Wave re-record of BOTH sets + validity gate v3
**Branch:** `phase-8-wave875-rerecord`
**Depends on:** 8.14, 8.15, 8.16, 8.17
**Section refs:** DESIGN.md §11.4, §3.5; audits/audit-2026-06-06-0632-gameplay-data.md (the repair set + §12)
**Complexity:** Integration

The wave gate, mirroring Task 8.12's shape: with the four repairs merged, re-record BOTH committed
sets in ONE PR (the cooldown re-seed is a byte-breaker for every game; the vote_ballot/v4 bump
re-points prompt provenance), regenerate both `tournament-eval-report.json` (format v2 with the 8.17
fields now populated), both `MANIFEST.md`, and the prompt-regression fixtures + `baseline.json`.
Re-enable the 8.14-skipped recon tests last. The re-record itself is an operator step
(`refresh_samples.sh` on local Ollama, $0); this contract is the source-side pins + the gate.

**Files in scope:**
- replays/samples/*.jsonl + tournament-eval-report.json + MANIFEST.md (flat 4p/1i re-recorded; report v2 with the new accounting fields)
- replays/samples/9p2i/ (50 replays + roster.json {9,2,2} + report + MANIFEST re-recorded)
- tests/fixtures/prompt_regression/{v_a,v_b}/*.jsonl + baseline.json (regenerated at vote_ballot/v4)
- tests/api/test_replay_loader.py + tests/eval/test_win_condition_selfcheck.py (re-enable the 8.14 skips; byte-identical green)
- tests/scripts/test_build_sample_report.py + tests/scripts/test_verify_samples.py + tests/scripts/test_manifest_writer.py + tests/scripts/test_refresh_samples.py (committed-bytes pins: git_sha, vote_ballot/v4, cost 0)

**Files NOT in scope:**
- engine/, meetings/, agents/, observation/, eval/ source (all behavior landed in 8.14–8.17; this task records + regenerates, it does not change logic)
- audits/workflows/extract_gameplay_facts.py (run it read-only for the funnel numbers; do not modify it)

**Definition of done:**
- [ ] Both committed sets are re-recorded in ONE PR; both reports regenerate at format v2 with kill_gifted/instances fields populated; both MANIFESTs carry the new git_sha + vote_ballot/v4; prompt-regression fixtures + baseline.json regenerated.
- [ ] The 8.14 recon skips are re-enabled and green (byte-identical via the per-set loader); `_verify_samples` + `build_sample_report --check` are consistent on both sets.
- [ ] **Validity gate v3 (HARD):** friendly-fire kills == 0; every game reaches `game_over`; impostor betrayal ballots/accusations == 0; the leak suite passes at 4p/1i and 2-of-9; the Stage-A floor holds at 9p/2i (`meeting_rate ≥ 0.60`, ≥ 30 resolved meetings); AND the repair assertions: zero tick-1 kills, zero "(missed deadline" markers in any transcript, zero dangling `primary_reason_id`s across both sets.
- [ ] Funnel report ($0): run `audits/workflows/extract_gameplay_facts.py` over the new 9p/2i set and report in the PR body: win split + kill-gifted split, ejection count, accusation precision, accuser follow-through, persuasion rate. Reported, not gated — these are the Wave-1 control-arm anchors.
- [ ] `uv run mypy .` passes.
- [ ] `uv run ruff check .` and `uv run ruff format --check .` pass.
- [ ] `uv run lint-imports` passes.
- [ ] `uv run python scripts/generate_prompts.py --check` passes.
- [ ] `uv run python scripts/validate_task_docs.py` passes.
- [ ] `uv run pytest` passes.
- [ ] `bash scripts/check.sh` passes locally.

**Implementation hint:**

Operator-run local session like 8.12: Ollama up, the model pulled, and AILIBI_LLM_PROVIDER=ollama on
EVERY refresh invocation (it defaults to anthropic). Smoke a few seeds before each full 50 —
per-seed wall time changes (deadline-free meetings may run longer per call but lose nothing to
defaults). The 9p/2i env block is documented at the top of scripts/refresh_samples.sh. Expect the
win split to MOVE (no spawn kill means fewer early parities; the kill-gifted split contextualizes
the crew rate). Re-enable the recon tests only after the bytes are on disk. One atomic PR — an
intermediate commit is un-reconstructable.

**Integration risk:**

The wave converges here; the validity gate is a HARD stop — if any repair assertion fails (a tick-1
kill, a missed-deadline marker, a dangling reason id), STOP and fix the upstream task rather than
papering the gate. The flat-4p/1i descriptor-less identity must hold or the determinism reference
silently reseeds wrong.

**Ready-to-paste prompt:** `agent_prompts/task-8-18-wave875-rerecord.md`

## Merge Criteria (Phase 8 — substrate restructure)
- **Per-player tasks landed (8.1–8.4):** `WorldState.tasks` keyed per-instance `"{owner}:{map_task_id}"`; the agent-facing id is the map id (engine resolves by actor); two crewmates hold the same map task independently; the win count is over live instances; the observation/agent triad + api/frontend mirrors agree; no crewmate sees another's ownership.
- **Cap removed + 9p/2i seedable (8.2, 8.5):** the `crew × tasks_per_crewmate ≤ 12` seed cap (and its `_manifest_writer` mirror) is gone; `ROSTER_PRESETS == {4p1i, 9p2i}` with `9p2i=RosterPreset(9,2,2)`; the CLI/scripts thread it; the flat default stays 4/1/2.
- **Leak firewall holds at the new substrate (8.6):** the property sweep runs at 9 players, 2-of-9 (and 3), with a per-player-task fixture exercising `pending_task_id`; the crew-empty `fellow_impostor_ids` invariant holds; the api leak tripwires are updated.
- **Meeting accusation-chain landed (8.7–8.10):** `MeetingTranscript` is one ordered `turns` list; opening → reactive chain (deterministic termination, replay-walkable) → opt-in → vote; the 7.12 firewall wraps every turn; the four templates + provider schema + the four §11.3 metrics + api/frontend re-point to the turn shape; fewer LLM calls.
- **Versioning (8.11):** no replay `format_version` field (state_hash + roster.json reject old bytes); the report `CURRENT_FORMAT_VERSION` is 2.
- **Combined re-record validity gate (8.12) — HARD, numeric:** both sets re-recorded in ONE PR; byte-identical reconstruction via the per-set loader with the two skipped recon tests re-enabled + green; friendly-fire 0; all games reach `game_over`; impostor betrayal ballots/accusations 0; the Stage-A floor holds at 9p/2i (`meeting_rate ≥ 0.60`, ≥ 30 resolved meetings). An impostor-favored-but-valid split is reported, NOT gated.
- **All gates green:** `bash scripts/check.sh`, determinism + leak suites on BOTH committed sets, frontend `tsc:check` + `vite build`.
- **Close:** re-run the `gameplay-data-audit` workflow on the new 9p/2i baseline — its verdict + finding set is the anchor for the resumed agent-intelligence work (crew-intel gp-1/gp-2 re-anchored to the chain protocol, then the impostor toolkit gp-4). No agent-intelligence behavior lands in Phase 8.

Merge criteria for Wave 8.75 (8.14–8.18, audit-driven repairs):
- **Round-start cooldown (8.14):** every impostor's kill cooldown is seeded to `kill_cooldown_ticks`; a tick-1 kill is engine-rejected; the committed recon tests skip-mark cleanly until the wave re-record.
- **Recording integrity (8.15):** headless recording is deadline-free (`MeetingDeadlines(None, None)`); any fired default is recorded as `error_type="deadline_default"`; the opening turn retries once before defaulting.
- **Ballot reason integrity (8.16):** `primary_reason_id` is validated against the transcript (suffix forms normalized, unresolvable nulled with an audit marker, teammate-coerced ballots nulled); the vote prompt example is a real turn id; `vote_ballot/v4` everywhere in lockstep.
- **Kill-gift visibility (8.17):** the report carries `kill_gifted` / `instances_dropped` / `instances_complete_at_win` (additive, v2 retained); the §3.5 drop semantics themselves are unchanged.
- **Wave re-record validity gate v3 (8.18) — HARD, numeric:** both sets re-recorded in ONE PR; all 8.12 gates hold (friendly-fire 0, all `game_over`, betrayal 0, leak green, `meeting_rate ≥ 0.60` / ≥ 30 resolved, byte-identical recon); PLUS zero tick-1 kills, zero missed-deadline markers, zero dangling reason ids. The PR body reports the extractor funnel numbers (win + kill-gifted split, ejections, accusation precision, follow-through, persuasion rate) — the Wave-1 control-arm anchor. The win split is reported, NOT gated.
- **Impostor build frozen:** no impostor behavior change lands in Wave 8.75 (gp-4c kill-suppression and the gp-9 activation wave wait for post-Wave-1).
