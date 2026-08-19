# Code review — area `engine` (engine/ + tests/engine/)

Reviewer track: code-up (structure, correctness, determinism, tests, measured behaviour). Read-only.
Repo: /Users/danielkeinan/projects/AiLibi @ main (b809b19c). Python 3.11 via `uv run`. Load during timings: `load averages: 6.35 6.51 9.42` (10-core box shared with other reviewers) — absolute µs are indicative, ratios are reliable.

Scratch/evidence scripts: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/engine/` (`probe_rules.py`, `probe_map.py`, `probe_dupkey.py`, `det_bench.py`, `invariants.py`, `micro.py`, `micro2.py`, `prose.py`).

---

## 1. Executive read (10 lines)

1. The engine is small (2,299 LOC incl. prose; ~1,650 SLOC across 9 modules) and genuinely does what the project claims: `advance_tick` is a pure `(state, actions) -> (state', events)` function over frozen dataclasses with defensively-copied read-only mappings. [VERIFIED]
2. Determinism holds: a 3-seed × 400-tick scripted run produced byte-identical per-tick state-hash chains under `PYTHONHASHSEED=1` and `=4242`; every set/dict iteration that reaches output is `sorted()`. No wall-clock, no unseeded randomness. [VERIFIED]
3. Structural invariants hold under fuzz: 300 games / 28,362 ticks / 447 kills with a random kill/vent/sabotage/repair/task policy — 0 violations across 12 invariants (bodies↔dead, task keys, dead-owner tasks, cooldown reset, win-condition-vs-phase, etc.). [VERIFIED]
4. `mypy --strict engine/` clean; radon average CC = A (2.9), worst C(16); 95% line coverage from `tests/engine` alone; 137 tests in 3.5 s. [VERIFIED]
5. Biggest correctness gap: the rule layer forgets `in_vent` for `kill`, `report` and `sabotage`. An impostor sitting inside a vent (invisible to everyone, still with full sight) can kill and report while staying vented. Only agent-policy code prevents it today. [VERIFIED, P1]
6. Biggest design/perf smell: ~47% of every tick is spent JSON-round-tripping a 625-word Mersenne state whose draw value is discarded (`_, next_rng_state = rng.randint(...)`) — an explicitly FROZEN no-op that also puts a 13 KB hex blob into every `state_hash`. [VERIFIED, P1-maintainability]
7. Several engine invariants live outside the engine: the orchestrator re-implements the "player died" transition for ejection, deletes reported bodies because `resolve_report` accepts already-discovered bodies, and enforces one-action-per-actor that `advance_tick` itself does not check (a duplicate `do_task` progresses twice). [VERIFIED]
8. Map loader is strict and well-tested for the documented failure modes, but: two vents in one room passes load and then raises `MapValidationError` from *inside* `advance_tick`; duplicate YAML keys silently collapse (so the documented "ids are unique" assertion cannot be met); ~7 loaded/validated fields are never read by the engine. [VERIFIED]
9. DESIGN.md is stale relative to the engine (3 win conditions vs 4 in code; "dropped" dead-task rule vs canonical `redistribute`; "lights only / no reactor" vs shipped `reactor` sabotage; "6 rooms" vs 10). [VERIFIED]
10. Agent-authored code signature is present but mild here: history-restating docstrings (rng.py is 60% prose; 15 task/phase citations in tick.py), a 100-line `event_to_dict` used only by tests, duplicated helpers/aliases, and rule validation split inconsistently between rules.py and tick.py.

---

## 2. Findings (ranked)

### P1

**F1. Kill / report / sabotage are allowed from inside a vent — invisible killer.** [VERIFIED] confidence: high that behaviour exists; medium-high that it is unintended.
- `engine/rules.py:56 resolve_kill`, `:182 resolve_report`, `:225 resolve_sabotage` never check `actor.in_vent`, whereas `move` (tick.py:243), `do_task` (tick.py:280), `emergency` (rules.py:209) and `repair` (rules.py:254) all reject it.
- Evidence (`probe_rules.py`): impostor `p-3` with `in_vent=True` in REACTOR, crewmate `p-1` in REACTOR:
  ```
  == 1. kill from inside a vent ==     ['Killed', 'TickAdvanced'] p-3 in_vent after: True p-1 alive: False
  == 2. report from inside a vent ==   ['MeetingTriggered'] phase: MEETING
  == 3. sabotage from inside a vent == ['SabotageStarted', 'TickAdvanced']
  ```
- Why it matters: `visibility._visible_player_ids` hides in-vent players, `_witnesses_in_room` excludes them, and `test_in_vent_observer_still_receives_normal_visibility` pins that a vented observer still sees the room. Combined: a vented impostor sees, kills, stays hidden, and can even open the meeting. The only guard is the FSM/ES option menu (`agents/tactical/impostor_policy.py:304`, `agents/tactical/learned/forward.py` "VENT_EXIT ... ONLY exit options"). The engine is supposed to be the authoritative rule layer (DESIGN §3.6, "single source of truth"); the ML program trains policies against this engine, so any future option-menu change exposes it. Sabotage-from-vent may be intentional (remote action) — kill/report are not defensible.
- Fix: add `if actor.in_vent: raise ActionRejectedError(...)` in `resolve_kill` and `resolve_report` (and decide explicitly for sabotage). Note this changes engine behaviour only for batches no current policy emits, so committed replays should stay byte-identical — but verify with the replay-hash gate.

**F2. The FROZEN "discard-the-draw" RNG apparatus costs ~half of each tick and bloats every state hash.** [VERIFIED] confidence: high on the numbers; the design cost is a judgment.
- `engine/tick.py:638-651`: `rng = EngineRng.from_state(state.rng_state); _, next_rng_state = rng.randint(...)`. `orchestrator/game.py:1285` does the same on the meeting path. Nothing in the repo consumes the value (grep: no other `randint`/`EngineRng` consumer).
- Micro-benchmarks (`micro2.py`): `from_state(FULL json)` 54.8 µs + `snapshot FULL` 35.9 µs ≈ 91 µs; the whole tick for a 9p/2i state averaged 192 µs (`det_bench.py bench`, 1,856 ticks). FAST codec: 25.5 + 12.4 µs, tick 144 µs. So the no-op draw is ~47% (FULL) / ~26% (FAST) of engine time, matching the doc's "~43%" claim. `rng_state` is 6,726 bytes of JSON → 13,452 hex chars inside every `_state_hash` input (`orchestrator/replay.py:1222`), which itself costs 168 µs/tick — as much as the tick.
- Why it matters: `WorldState.rng_state`/`seed` exist to support randomness the engine does not have. The 15.8.1 fast path added a second codec, a policy enum, self-describing markers and ~80 lines of prose to speed up something whose only function is "advance a cursor so hashes chain". A 64-bit counter or `sha256(prev)` would be equivalent for byte-identity, ~1 µs, and shrink state hashes. It is frozen by policy (replay byte-identity), which is legitimate — but it should be on the list for the next re-record (each re-record already re-anchors every hash).

**F3. Death/eject and body-consumption invariants are split between engine and orchestrator; the engine alone does not enforce them.** [VERIFIED] confidence: high.
- `orchestrator/game.py:1140-1260 apply_meeting_result` re-implements `_apply_kill`'s "player died" transition (alive=False, last_action=None, drop/redistribute tasks, pop cooldown) — and is *not* symmetric (kill does not pop the victim's cooldown; eject does). `redistribute_dead_tasks` is exported from `tick.py:314` solely for this.
- `resolve_report` (rules.py:182) accepts a body whose `discovered_by` is already set → orchestrator deletes the triggering body after each meeting with a comment admitting the engine gap (`game.py` "resolve_report does not reject already-discovered bodies"). Probe: `== 4. re-report an already-discovered body == ['MeetingTriggered'] phase: MEETING`.
- `advance_tick` accepts duplicate actors: `[do_task, do_task]` for the same actor → `progress: 2` in one tick (probe #5). DESIGN §3.1 says the orchestrator enforces it; the engine's docstring says nothing, and the property tests dedupe by hand (`_unique_actions_per_actor`) — i.e. the tests know the engine is unsafe here.
- Why it matters: "engine = single source of truth" is the architectural claim; three of its invariants are only true when a specific caller wraps it. A one-line `_validate_unique_actors` (already exists in `orchestrator/action_ordering.py:20`) and a `discovered_by is not None → reject` belong in the engine; an `apply_death(state, player_id, game_map)` primitive would let ejection reuse the kill path.

### P2

**F4. DESIGN.md contract drift vs. the engine.** [VERIFIED]
- §3.5 lists 3 win conditions; `engine/win_conditions.py` has 4 (`CREWMATE_EJECT` inserted before tasks; the code comment cites "DESIGN.md §3, §8.1" which say nothing of it).
- §3.5 describes only the "dropped" dead-task rule; `engine/maps/canonical_1.yaml:41 dead_task_rule: redistribute` is the shipped rule; `grep redistribute DESIGN.md` → 0 hits. `tick.py:378` comment still says "DESIGN.md §3.5 (dropped)".
- §8.1 "1 fixed map: 6 rooms" (map has 10), "sabotage (lights only)"; §8.3 "No reactor / O2" — `reactor` sabotage with `gates_tasks` shipped in Phase 11.
- yaml header "Balanced for 5–7 agents, 1 impostor" vs canonical 9p/2i; yaml says rooms may declare a per-room `visibility:` block, but `Room` is `extra="forbid"` with no such field → the loader would reject it.

**F5. Map loader: gaps vs. the yaml VALIDATION EXPECTATIONS block.** [VERIFIED]
- Two vents in one room load fine, then `Map.vent_for_room` (world.py:306-311) raises `MapValidationError` from inside `advance_tick` when the impostor tries to exit: `2. advance_tick raised MapValidationError : room has multiple vents: REACTOR` (probe_map.py). Load-time check missing; the runtime check is a `ValueError` subclass, not `ActionRejectedError`, so it crashes the game loop.
- Duplicate YAML mapping keys silently collapse in `yaml.safe_load` (probe_dupkey.py: canonical map with a duplicated `swipe_card:` key → `tasks loaded: 11`, no error). The block's "All room/vent/task IDs are unique" cannot be asserted with `safe_load`; needs a duplicate-key-detecting loader or a documented caveat.
- `_validate_disjoint_namespaces` (world.py:314) has no test (coverage: lines 328-329 never hit) and is mostly unreachable (task ids `^[a-z]`, room/vent `^[A-Z]`; only room∩vent can collide).
- `_validate_room_graph` hard-codes `"CAFETERIA"` as the BFS root (world.py:338) instead of `spawn.room` — a generic loader with a canonical-map constant.
- Loaded+validated but never read by the engine: `visibility_defaults.lights_sabotage` (world.py:115 — the sabotage's own `affected_visibility` is used), `Edge.kind`, `Edge.door_id`, `Edge.traversal_ticks`, `Vent.traversal_ticks` (only echoed into events; traversal is instantaneous), `TaskDefinition.weight`, `task_type`. Today all traversal values are 1 so no observable drift, but a map with `traversal_ticks: 2` would silently behave as 1.
- Untested rejection strings (0 hits in tests/): "only impostors can vent", "only impostors can sabotage", "cannot move while in vent", "cannot do task while in vent", "task requires actor in task room", "report requires actor and body in same room" — DESIGN §11 promises "unit tests in tests/engine/ for every rule".

**F6. Actions after a meeting trigger in the same batch are silently dropped (no `ActionRejected`).** [VERIFIED] `tick.py:599` returns as soon as phase flips; probe #6: `['MeetingTriggered'] p-2 room: CAFETERIA (no ActionRejected for p-2)`. Deterministic (id-ordered) and replay-safe, but DESIGN §3.1 says every non-applied action yields an `ActionRejected` event; here a higher-id impostor's kill vanishes without trace in the event stream. Document or emit rejections.

**F7. Dead / test-only code.** [VERIFIED]
- `engine/events.py:193 event_to_dict` (100 lines, CC 13) — referenced only from tests; `EventType` (events.py:9) unused anywhere.
- `PlayerState.position` / `BodyState.position` (entities.py:28,47) — seeded to `(index, 0.0)`, never mutated or read; still serialized into every state hash as floats.
- `rules.py:268 resolve_win_conditions` is a pass-through alias of `evaluate_win_conditions`.
- Defensive unreachable branches: `_apply_action` phase check (tick.py:543, already checked at :577), `body id already exists` (tick.py:375, id embeds tick+target), `_advance_tasks` "continuing task references no owned instance" (tick.py:174).

**F8. Duplication / accidental structure.** [VERIFIED]
- `_get_live_player` defined twice, identically (rules.py:47, tick.py:206).
- `RoomId`/`TaskId` aliases defined in both entities.py and world.py; actions.py imports one from each.
- Task-progress arithmetic duplicated (`tick.py:189` and `:301`).
- Rule validation split: kill/vent/report/emergency/sabotage/repair validate in `rules.py`; move/do_task/wait validate inline in `tick.py`. Return shapes differ (`resolve_kill` → (body, event); `resolve_repair_sabotage` → None; others → event).
- `_resolve_owned_task_instance` (tick.py:117) linear-scans `tasks` although the key is `f"{actor}:{map_task_id}"` by construction — and `redistribute_dead_tasks` (tick.py:352) *does* rely on the composite key. 0.32 µs vs 0.05 µs; trivial cost, but two truths about the same invariant.
- Every `replace(state, ...)` re-wraps 5 mappings via `WorldState.__post_init__` (3.6 µs each; ~10 per tick). Fine at 9 players; a per-tick builder would remove it if training rollouts ever matter.
- `Map.room_neighbors` scans all edges + sorts on every call (0.8 µs; 12 call sites repo-wide); a precomputed adjacency on the frozen model is the obvious shape.

**F9. Prose sprawl / history restating.** [VERIFIED via `prose.py`]
- rng.py: 165 lines, 56 code, 83 doc/comment (60%); "Task 15.8.1" appears 9×. tick.py: 15 task/phase/audit citations; `_validate_state_map` still says "unsupported map id for Phase 1 engine". win_conditions.py 37% prose, visibility.py 25%. The `redistribute_dead_tasks` docstring is 25 lines for a 20-line function and cites an experiments/lab script as its validation.

**F10. Test-suite smells.** [VERIFIED]
- `tests/engine/test_rules.py:149` runs 8 full `HeadlessGame`s (orchestrator + agents + meeting runner) inside the engine unit dir — an integration test by another name; the slowest test in the dir (0.72 s).
- `test_advance_tick_uses_supplied_map_without_loading_canonical_map` monkeypatches `engine.world.load_canonical_map` — pins an implementation non-choice.
- Property tests only assert "does not raise / phase valid / rooms exist"; no state invariants (my `invariants.py` shows how cheap that is).
- Fixture inconsistency: `test_meeting_trigger_interrupts_tick...` builds a body for `p-2` while `p-2` is alive.
- History-named tests (`..._unchanged`, `..._legacy_shape`) and audit citations in test prose.
- `test_events.py` exists only to pin the shape of dead code (F7).

**F11. No import contract protects the engine's own boundary.** [VERIFIED] `.importlinter` forbids agents→engine etc., but nothing forbids engine→{orchestrator,agents,observation,...}. Today `engine/` imports only stdlib/pydantic/yaml/engine (verified by grep) — cheap to lock in.

---

## 3. Architecture / design assessment

**Well designed**
- Pure-function tick over frozen dataclasses; `WorldState.__post_init__` + `SabotageState.__post_init__` wrap every mapping in `MappingProxyType(dict(...))`, and tests prove in-place mutation raises. Immutability is real, not aspirational.
- Rejections-as-events: `ActionRejectedError` is caught at the batch loop and turned into `ActionRejectedEvent`; hard `ValueError`s are reserved for state corruption. Total function in practice (fuzz + hypothesis).
- All ordering is explicit: `sorted(state.players)` in `_advance_tasks`, sorted witnesses, sorted neighbours, lowest-id recipient in redistribute. Determinism was verified, not assumed.
- Data-driven gating (`SabotageDefinition.gates_tasks`) instead of string-matching sabotage kinds; `_tasks_gated` is a single source of truth for both task paths.
- Win-condition ordering is explicit, documented, and pinned by same-tick tests (kill reaching parity + last task; repair vs timeout same tick).
- Map loader: pydantic `extra="forbid"`, clear error strings, parametrized negative tests over the documented failure list; `attach_ids` keeps YAML mapping keys and embedded ids consistent.
- The engine's dependency surface is tiny and downward-only.

**Accidental complexity**
- The RNG threading (F2): two codecs, a policy enum threaded through `advance_tick` and `apply_meeting_result`, self-describing markers — all to serialize a value nobody reads.
- Rules split across two modules with inconsistent shapes (F8); "engine invariants" that only hold under the orchestrator's wrapper (F3).
- Denormalized state: `TaskState.id` duplicates the dict key; `TaskState.room` duplicates `game_map.tasks[map_task_id].room`; `SabotageState.affected_rooms` is actually `repair_rooms`; `position` is dead weight in the hash.
- `event_to_dict` hand-serializes 14 dataclasses for a consumer that no longer exists.

**What I would refactor (in order)**
1. Add `in_vent` guards to kill/report (and decide sabotage) — 3 lines + 3 tests.
2. Move death semantics into one engine primitive (`apply_player_death`) used by `_apply_kill` and by the orchestrator's ejection; reject already-discovered bodies in `resolve_report`; assert unique actors in `advance_tick`.
3. Consolidate `rules.py`: every action gets `validate_X(state, map, action) -> None` and `apply_X`; delete the duplicated `_get_live_player`, aliases and progress arithmetic; make `_resolve_owned_task_instance` a dict lookup.
4. At the next planned re-record (hashes re-anchor anyway): replace the Mersenne payload with a cheap chained counter, drop `position` from hashed state, drop `event_to_dict`/`EventType`.
5. Loader: validate one-vent-per-room and consumed-vs-declared fields; root BFS at `spawn.room`; detect duplicate YAML keys.

---

## 4. Test assessment

- 137 tests / 3.5 s / 95% line coverage of `engine/` from `tests/engine` alone; `test_tick.py` (1,634 lines, 41 tests) is large but mostly behavioural (kill→body/cooldown/event, redistribute rules, gating, same-tick orderings). Good.
- Gaps: 6 core rejection rules never asserted anywhere (F5 list); no test for `in_vent` on kill/report because the behaviour is undefined; no duplicate-actor test; no load-time multi-vent test; no namespace-disjoint test; property tests are shallow.
- Pinning: `test_events.py` and parts of `test_rng_fast_path.py` pin encodings of dead/frozen machinery; the monkeypatch test pins an implementation non-choice; test names/comments carry audit ids and "unchanged" history.
- Layering: `test_rules.py` drags orchestrator/agents/meetings into `tests/engine`.
- Missing entirely from `tests/engine`: a cheap determinism/hash-stability test at engine level (the repo relies on committed-replay verification elsewhere; that is fine but a 20-line PYTHONHASHSEED-independent chain test would localize regressions).

---

## 5. Recommendations (prioritized)

1. **Close the vent hole** (F1): reject `kill` and `report` when `actor.in_vent`; write the rule down in DESIGN §3.4; add tests. Verify committed replays still hash-verify (they should — no shipped policy emits these).
2. **Make the engine own its invariants** (F3): unique-actor assertion in `advance_tick`; `discovered_by is not None` → reject in `resolve_report`; a shared `apply_player_death` used by kill and ejection (removes the drift between the two paths, e.g. cooldown pop).
3. **Truth-up DESIGN.md §3.4/§3.5/§8.1/§8.3** (F4): four win conditions and their order, `redistribute` as canonical, reactor sabotage, room count, roster; fix stale comments (`tick.py:378`, "Phase 1 engine", yaml header).
4. **Loader hardening** (F5): one-vent-per-room at load; BFS root = `spawn.room`; duplicate-key detection or an explicit caveat in the VALIDATION EXPECTATIONS block; either consume or delete `lights_sabotage`/`door_id`/`traversal_ticks`/`weight`/`task_type`; add the 6 missing rule-rejection unit tests.
5. **Schedule the RNG payload retirement for the next re-record** (F2): swap the 6.7 KB Mersenne blob for a chained counter, delete the FAST codec + policy enum, drop `position` from hashed state. Halves engine tick time and shrinks every state hash; zero gameplay change.
6. **De-duplicate and consolidate rules** (F8): one `_get_live_player`, one alias home, one progress helper, all validation in `rules.py` with a uniform shape; dict-lookup for task instances.
7. **Trim dead code and prose** (F7, F9): delete `event_to_dict`/`EventType`/`resolve_win_conditions` alias; cut history-restating docstrings to the rule + a single audit pointer.
8. **Add an import-linter contract** `engine` may import only `engine` (F11), and move `test_rules.py::test_no_resolved_kill_targets_an_impostor_across_seeds` to `tests/orchestrator`.

---

## Appendix — evidence log

- `uv run pytest tests/engine -q` → 137 passed in 3.48 s (load 7.5).
- `uv run mypy --strict engine/` → Success: no issues found in 10 source files.
- `radon cc -a engine/` → 132 blocks, average A (2.91); C-rated: `event_to_dict` 13, `evaluate_win_conditions` 16, `_advance_tasks` 11, `redistribute_dead_tasks` 11, `_apply_action` 11.
- Coverage (`pytest-cov`, tests/engine only): 95% total; uncovered = validation branches listed in F5 + defensive branches in F7.
- Determinism: `det_bench.py det` seeds 1/2/3 → chains `c7af34b271a7d920 / f96d5e25f28a997c / 0ffdc27c119331a9` identical under `PYTHONHASHSEED=1` and `4242`.
- Fuzz invariants: `invariants.py` → `games=300 ticks=28362 kills=447 violations=none`.
- Bench (`det_bench.py bench`, 20 seeds, 9p/2i, 1,856 ticks, load ~6.4): FULL engine 192 µs/tick, TRAINING_FAST 144 µs/tick; 9-observer visibility 21 µs; orchestrator `_state_hash` 168 µs.
- Micro (`micro2.py`): from_state FULL 54.8 µs / FAST 25.5 µs; snapshot FULL 35.9 µs / FAST 12.4 µs; raw `randint` 0.28 µs; `getstate` 5.4 µs.
- Prose ratio (`prose.py`): rng.py 60%, win_conditions.py 37%, visibility.py 25%, tick.py 16%.
