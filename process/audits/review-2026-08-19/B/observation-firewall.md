# Code review — observation firewall (observation/, agents/perception|runtime|base, leak suites, .importlinter)

Reviewer label: observation-firewall. Branch: main @ b809b19c. Read-only; all experiments ran from a scratch copy
(`scratchpad/work/observation-firewall/`). Machine load during timings: 4–9 (10-core, other reviewers concurrent).

Files reviewed in full: observation/{service,packet,public_map,action_intent,audit}.py (1107 lines), agents/{perception,runtime,base}.py
(614), eval/leak_test.py (775), eval/leak_scan.py (691), tests/observation/* (2867), tests/test_firewall.py (278), .importlinter, plus the
engine slices they depend on (engine/visibility.py, rules.resolve_kill/_witnesses_in_room, tick.advance_tick/_apply_kill/redistribute) and
the orchestrator loop that drives the service.

## 1. Executive read (10 lines)

1. The static firewall holds today: no `agents/` module imports `engine/` directly, transitively, via `TYPE_CHECKING`, or via `importlib`
   [VERIFIED by grep + lint-imports]; boundary schemas are engine-free Pydantic frozen/extra=forbid models; the service is the single boundary.
2. The dynamic firewall (packet contents) is sound on the classic channels: roles, cooldown, fellow ids, own_kill, kill/vent witness gating,
   rejected-kill suppression, in_vent, owner-scoped task ids. 16 hand-written mutations found **no hidden-role/attribution leak** in the real
   service — every mutation that would leak *was* a mutation I introduced.
3. BUT the enforcement is weaker than the docs claim, in three concrete places (all [VERIFIED]):
   (a) `eval/leak_test.py` — DESIGN.md's "most important test" and the only scan the ML champion gate runs — never checks *visibility gating*:
   a service that lists every alive player, every body, or every vented player passes it (mutations M1/M6/M10/M14 survive; M6 survives *all* suites).
   (b) import-linter is blind to `agents -> orchestrator|eval|api -> engine` because those are not root packages (a planted probe passes all 4 contracts).
   (c) The canonical `redistribute` dead-task rule makes `SelfView.owned_task_ids` grow at the exact kill tick for a far-away crewmate (13/16 kills in
   4 FSM games) and the memory layer, whose comment asserts "the owned set only ever shrinks", mints a **fabricated "You completed X"** line (~1/game).
4. Perception (`agents/perception.py`) is a clean pure function of the packet with deterministic ids, but it rescans the whole episodic store every
   tick (58 µs/tick at 100 ticks -> 249 µs/tick at 600) — quadratic per game.
5. The audit log is write-only (no reader; training deletes the sidecars), costs ~38 % of `build_packet`, and drives a bespoke serializer.
6. Prose is 33–55 % of the core files and is mostly task/PR/Codex history restated (service.py: 15 task refs, packet.py 9, perception 16); several
   docstrings now contradict each other (MovedPlayerView vs `_moved_players_for_agent`; store.py's shrink-only invariant; DESIGN §4.2 schema).
7. Tests are numerous (122 in-area) and mostly behavioural; the planted-leak "scanner bites" self-tests are exemplary. The Hypothesis sweeps
   however keep everyone co-located in CAFETERIA (two of three vocabularies never move), so their visibility coverage is vacuous.
8. Genuinely good engineering: witness gates read only *resolved* events; the pytest-free scanner split with a subprocess import-purity probe;
   role-blind consistency invariants (`pending ∈ owned`); frozen tuples sorted for replay; fail-loud seat lookup.
9. Two cross-area defects surfaced through the packets: the engine accepts a kill from *inside* a vent (and the learned action mask allows it),
   and kill-witness membership depends on player-id submission order.
10. Overall grade for the area: architecture B+, enforcement B-, tests B, prose hygiene C.

## 2. Findings (ranked)

### F1 [P1][VERIFIED] The leak test does not check visibility gating; body/room omniscience regressions pass every suite
- Where: `eval/leak_scan.py:610-650 assert_packet_is_leak_clean`, `eval/leak_test.py:229-275 test_no_observation_leaks_hidden_information`,
  `tests/observation/test_leak_property.py`.
- What: the scanners are field-name/role-string/witness-permission oriented. Nothing asserts `visible_players ⊆ compute_visibility(...).visible_player_ids ∪
  witnessed actors`, nothing asserts `visible_bodies == visible_body_ids`, and `assert_moved_players_are_witness_gated` is not part of
  `assert_packet_is_leak_clean` (so the champion gate never scans `moved_players`).
- Evidence (mutation probe over a scratch copy, `scratchpad/work/observation-firewall/mutate.py`; each row = which suite fails):

  | mutation | leak_test.py | test_service | test_leak_property | owned/firewall |
  |---|---|---|---|---|
  | M1 visible_players = every alive player | survives | BITES (incidental: vented test) | survives | survives |
  | M6 visible_bodies = every undiscovered body (engine/visibility) | **survives** | **survives** | **survives** | survives |
  | M10 vented players visible | survives | BITES | survives | survives |
  | M14 witnessed-vent PlayerView.room = actor's current room (destination leak) | **survives** | **survives** | **survives** | survives |
  | M2/M3 moved_players arrival-gated / ungated | survives | BITES | BITES | survives |
  | M12 BodyView.victim_id := killed_by | survives | BITES | survives | survives |
  | M4 unwitnessed kill surfaced | BITES | survives | BITES | – |
  | M8 fellow_impostor_ids to all / M9 cooldown to all / M16 last_action stamped | BITES | BITES | BITES(M8,M16) | – |
  | M5 rejected kill stamped "task" / M11 sabotage actor stamped "task" / M13 own_kill any actor | survives | BITES(M5) | BITES | BITES(M13) |
- Why it matters: DESIGN.md §11.2 calls this "the most important test" and §1.3 says it "asserts no field in any packet contains information the
  agent should not have". The most basic firewall property (room-gated sight) is not asserted anywhere by an engine-truth cross-check; the
  incidental catches in `test_service.py` are single-scenario unit tests. The ML champion gate (`scan_factory_packets`) would accept M1/M6/M10/M14.
- Root cause: the scanners were designed around *forbidden names/values* (role, killed_by, "impostor" substrings) plus a witness check for
  kill/vent; `assert_packet_is_leak_clean` takes only (packet, events), never the world state, so it *cannot* recompute visibility.
- Confidence: high.

### F2 [P1][VERIFIED] import-linter contract is blind to `agents -> orchestrator | eval | api -> engine`
- Where: `.importlinter` (`root_packages = agents engine llm meetings observation training`), `tests/test_firewall.py:150-165` (source scan
  restricted to `agents/tactical/learned/`).
- Evidence: in the scratch copy, `agents/_probe_orch.py` containing `import orchestrator.game`, `import api`, `import eval.leak_scan` (all three
  import `engine`) -> `lint-imports --no-cache` reports `Contracts: 4 kept, 0 broken`. The learned-package AST scan would catch it only under
  `agents/tactical/learned/`. `test_agents_cannot_reach_engine_through_observation` proves transitivity only through a *root* package.
- Why: the project's own comment (`agents/tactical/learned/__init__.py`, `test_firewall.py:150`) knows the `agents -> orchestrator -> engine` chain is
  invisible to lint-imports and fixed it for one subpackage only. Any future agent-authored task that adds `from orchestrator.game import ...` to
  a policy passes CI, mypy and the firewall tests.
- Confidence: high.

### F3 [P1][VERIFIED] Redistribute + "pending changed ⇒ completed" inference mints fabricated task-completion memories
- Where: `agents/memory/store.py:1157-1200` (comment: "Its owned set only ever shrinks -- a task completes; none is added mid-game"),
  `observation/service.py:_pending_task_id_for_agent` (lexicographic-min contract), `agents/perception.py:_self_state_payload` (does not carry
  `owned_task_ids`), `engine/tick.py:redistribute_dead_tasks`, `engine/maps/canonical_1.yaml:45 dead_task_rule: redistribute`.
- Repro (`exp_redistribute.py`): p-2 in ADMIN owns `upload_logs`; p-3 kills p-1 (owner of `align_engine_output`) in CAFETERIA. Next packet for p-2:
  `pending_task_id: upload_logs -> align_engine_output`, `owned_task_ids: ('align_engine_output','upload_logs')`; `render_for_prompt` then emits
  `[tick 2] You completed upload_logs (you were in ADMIN).` — false; upload_logs is untouched.
- Rate in real FSM games (`exp_redistribute_rate.py`, default factory, fake LLM, seeds 0-3): 16 kills, 13 owned-set growth events, **4 fabricated
  completions vs 43 real** (~9 % of the "completed" lines a crewmate could speak as an alibi are false).
- Why: a crewmate's rendered memory is the meeting evidence base (DESIGN §6.6); a false first-hand "I completed X" is exactly the fabricated-alibi
  class the impostor gate (PR #155) was written to prevent — but for the *crew*. Also the docstring invariant is simply stale since Task 13.12.
- Confidence: high (repro + measured).

### F4 [P2][VERIFIED] The self channel is an instantaneous kill side-channel under `redistribute`
- Same mechanics as F3: the lowest-id living crewmate not owning the victim's map task learns, on the kill tick and from anywhere on the map,
  that someone died and which task they held (13/16 kills in 4 games). `GlobalView.tasks_total` may also drop when no recipient exists.
  The leak suite deliberately asserts `owned_task_ids == engine truth`, so it blesses this by construction. Whether it is a "leak" is a modeling
  choice (nothing in DESIGN lists death-timing as hidden), but it is undocumented as a channel, unexploited by policies today, and available
  to any learned crew policy that reads `owned_task_ids` (crew_forward.py:728 does).

### F5 [P2][VERIFIED] The observer's own move rides `moved_players` (impostors only) and is papered over downstream twice
- `observation/service.py:_moved_players_for_agent` gates on `from_room ∈ visible_rooms` without `event.actor != agent_id`. Impostors see adjacent
  rooms, so their own departure room is visible post-move -> `moved_players` contains `id == agent_id` (`exp_selfmove.py`: p-3 packet
  `moved_players: [(p-1,…),(p-3,CAFETERIA,EAST_HALL)]`). Crewmates (same-room-only) never get it, so it is a role-correlated packet shape.
- Downstream, `agents/memory/store.py:_render_saw_player_move` self-suppresses and `agents/tactical/features.py:_roster_and_last_seen` documents and
  excludes the self row; `num_moved_players_norm` (features.py:406) still counts it. Fix at source (one predicate); note it is a substrate/byte change.

### F6 [P2][VERIFIED][cross-area: engine + training mask] Kill from inside a vent is legal; observation then surfaces a hidden killer
- `engine/rules.py:resolve_kill` has no `actor.in_vent` guard (move/do_task/emergency/repair all have one); `training/env.py:288-296` marks KILL legal
  while `in_vent`. `exp_ventkill.py`: p-3 in REACTOR_VENT kills p-1 -> `Killed`; p-2's packet: `visible_players [('p-3','REACTOR','kill')]` while
  p-3 stays `in_vent=True` and hidden. The FSM never does this (vent-exit branch is highest priority) but a learned policy can.

### F7 [P2][VERIFIED][cross-area: engine sequencing] Kill-witness membership depends on player-id submission order
- `advance_tick` applies actions in the orchestrator's sorted-id order; witnesses are computed at kill resolution. `exp_witness_order.py`: p-1 and p-5
  both move REACTOR->ENGINEERING on the tick p-3 kills p-2 in REACTOR; witnesses = `('p-5',)` only, and p-5's packet shows `('p-3','REACTOR','kill')`
  while p-5 stands in ENGINEERING. Deterministic but arbitrary; the same-tick semantics is documented for moves (leak_scan "tick-interior") but not
  for kills.

### F8 [P2][VERIFIED] Perception is O(store) per tick (quadratic per game)
- `agents/perception.py:ingest_packet` calls `MemoryStore.recent()` three times per packet (`seq` count, `_previously_seen_body_ids(since_tick=0)`,
  `_recent_co_presence`); `recent()` is a linear scan materialising a tuple (`episodic.py:119`). Bench (`bench_perception.py`, one agent, 5 visible +
  1 move + 1 body per tick): 58 µs/tick @100 ticks, 121 @300, 249 @600; ~70 % of ingest time is `recent()` genexpr. Per 9-agent 1000-tick game
  (DEFAULT_MAX_TICKS) that is ~2 s of pure rescanning; matters for training rollouts.

### F9 [P2][VERIFIED] The audit log is write-only overhead and drives a bespoke serializer
- `observation/audit.py` writes+flushes every packet; no production reader exists (grep: only `eval/leak_test.py` re-reads it to assert it equals the
  packets it just built; `training/crew/scorer.py:1622`, `bakeoff/harness.py:1693`, `goodhart.py:450,1577` *delete* the sidecars). The leak
  scan reconstructs packets from the replay instead. Cost: `bench_packet.py` — build_packet 38.6 µs (devnull) / 40.6 µs (file); cProfile:
  `record_packet` 0.050 s of 0.130 s (38 %). `packet.py:_serialize` exists only to keep this log's bytes stable (`moved_players` omit-when-empty vs
  `owned_task_ids` always-present: two conventions for one concern).

### F10 [P2][VERIFIED] `agents/runtime.py` is a dead scaffold with a keep-alive docstring
- 137 lines, imported only by `tests/agents/test_perception.py` and `tests/agents/test_beliefs_wiring.py`; `_choose_action` returns a hardcoded
  `WaitIntent`, `_update_memory` is a no-op; docstring: "do not delete it as dead code". Tests should target `ingest_packet` directly.

### F11 [P2][VERIFIED] Doc/docstring drift inside the area
- `observation/packet.py:MovedPlayerView` docstring: "WITNESS-gated exactly like a saw_player sighting (the actor is in visibility.visible_player_ids)"
  — contradicted by `service.py:_moved_players_for_agent` which gates on `from_room ∈ visible_rooms` and calls the visible_player_ids gate "wrong (Codex P2)".
  `agents/perception.py:76-83` repeats the stale claim.
- `agents/memory/store.py:1161-1163` "owned set only ever shrinks" — false since Task 13.12 (F3).
- `DESIGN.md §4.2` packet schema lacks `moved_players`, `owned_task_ids`, `fellow_impostor_ids`, `in_vent`, `own_kill`, sabotage repair fields;
  §1.3 describes the leak test as reading the audit trail (it reconstructs from replays).
- `docs/architecture.md:114-116` says the property test runs "every packet … through the eval/leak_test.py scanners" — true, but see F1 for what
  those scanners do not check.

### F12 [P2][VERIFIED] Prose sprawl restating history
- Comment+docstring share: service.py 34 % (238/691), packet.py 55 %, perception.py 33 %, runtime.py 42 %, leak_scan.py 34 %, test_leak_property.py 32 %.
  Task-number references: service 15, packet 9, perception 16, test_leak_property 17; PR/Codex review citations inline. Much of it narrates *why a
  previous version was wrong* (e.g. `_moved_players_for_agent` 25-line docstring; the module-level 50-line pretend-task essay in service.py).

### F13 [P2][JUDGMENT] Smaller cleanups
- `BodyId/PlayerId/RoomId/TaskId` and `_FrozenModel` are re-declared in `packet.py`, `action_intent.py`, `public_map.py` (3 copies).
- `SelfView.pending_task_id` is derivable from `owned_task_ids` for crewmates (head) and rotates for impostors; two service methods recompute the
  impostor roster and rescan `world_state.tasks` (`_pending_task_id_for_agent`, `_owned_task_ids_for_agent`).
- `eval/leak_scan.py` relies on `assert` for production gate verdicts and documents the `python -O` footgun instead of writing `raise AssertionError(...)`
  (identical contract, no footgun).
- `BodyView.id` = `body-{victim}-{tick}` puts the kill tick in every packet (leak-scan key-set pin allows it; the renderer does not print it; the
  test suite hardcodes the format at `test_leak_property.py:_ROSTER_BODY_ID_DRAWS`). Harmless today, but an id that is also a timestamp is a
  latent channel; a body sequence number would carry no time.
- `AudibleEvent(kind="vent_use_heard")` is emitted from the same same-room witness set as the `vent` PlayerView action — the audible channel is
  redundant with the visual one (DESIGN §4.2 hints at "heard", i.e. wider than seen).

### What is GOOD (deserves saying)
- Boundary discipline: schemas frozen + `extra="forbid"`; every collection a sorted tuple; the service is the only engine consumer; `agents/` imports
  only `observation.{packet,public_map,action_intent}` (24 imports, none of `observation.service`) [VERIFIED].
- Witness gates read only *resolved* engine events (`KilledEvent`, `Vent*Event`); `ActionRejectedEvent` is read for `do_task` only, so a rejected
  kill/vent/sabotage cannot leak intent; `own_kill` is populated by `event.actor == agent_id` only. All confirmed by mutations M4/M5/M13/M16 biting.
- The planted-leak self-tests ("a gate that cannot fail is not a gate") in `eval/leak_test.py` and `tests/test_firewall.py` are the right instinct;
  the subprocess import-purity probe with its negative control is well designed.
- Role-blind consistency invariants (`pending ∈ owned`, no ":" in ids, sorted/no-dup) are cheap and effective; the impostor camouflage window is
  seat-stable across deaths and fail-loud on a bad roster.
- `_visible_players` merges witnessed-but-now-hidden actors correctly (a venting impostor is shown at the witnessed room, not its vent).

## 3. Architecture / design assessment
- Well designed: a single privileged boundary object; engine-free agent-facing schemas; per-tick packet as a pure function of (state, events,
  observer); the "self channel vs crew-visible channel" split is a clear mental model that has scaled to 5 additive fields without a leak.
- Accidental complexity: (1) the audit-log byte-identity concern leaking into the packet schema (`_serialize`), (2) the impostor pretend-task
  machinery living in the *observation* service (a policy-camouflage concern encoded at the perception boundary; 130 lines + a 50-line essay),
  (3) `pending_task_id` + `owned_task_ids` as two fields with cross-invariants, (4) downstream self-suppression to compensate for the source
  gate (F5), (5) prose that documents diffs rather than the contract.
- Refactor sketch: `ObservationService.build_packet` -> pure `build_packet(state, events, observer, game_map)` module function + an optional
  `PacketSink` (audit) injected by the orchestrator; move pretend-task selection into `agents/tactical/impostor_policy` (it needs only the public
  map + seat index, which the self channel could carry as `fellow_impostor_ids`+own id) or at least out of the boundary module; collapse the two
  self-task fields into `owned_task_ids` (crewmate) with the policy computing its head; give `_moved_players_for_agent` the `actor != observer`
  predicate; add an engine-truth `assert_packet_matches_visibility(packet, state, game_map, events)` scanner and make every sweep call it.

## 4. Test assessment
- Coverage of channels: role/attribution names+values (strong), witness permission kill/vent (strong), self-channel misroute (fellow ids, cooldown,
  own_kill, in_vent) (strong via explicit asserts), owned-task ownership (strong, engine-truth cross-check), moved_players (property test only,
  not the CI leak test / champion gate), **visibility gating of players/bodies (absent)** (F1).
- Breadth: the two main Hypothesis sweeps never move anyone (all spawn in CAFETERIA) so every kill is witnessed by everyone; the movement sweep
  moves within the hub. Result: room-gated sight is exercised only by 3 scripted 4p/1i fixtures and unit tests.
- Pinning: `_SELF_STATE_KEY_SET`, PlayerView/BodyView key-set pins, and the omit-when-empty/always-serialize pins are implementation-shape pins,
  argued as "packet discipline"; acceptable but they will trip on every legitimate widening. `test_leak_property.py`'s expected pending is
  recomputed with `impostor_pretend_task_id` — the code under test — for impostors (tautological for that branch).
- Runtime: the in-area suites run in ~7 s; the mutation harness ran all five suites 16× in ~2 min. Property tests use `max_examples=50`.

## 5. Recommendations (prioritized)
1. **Add an engine-truth visibility scanner** (`visible_players ⊆ visible_player_ids ∪ witnessed actors`, `visible_bodies == visible_body_ids`,
   `moved_players` via the existing scanner) and call it from the scripted sweep, the factory reconstruction (it has `walk_event.state`) and the
   Hypothesis sweeps. Re-run the mutation harness as the acceptance test (M1/M6/M10/M14 must bite in `eval/leak_test.py`).
2. **Close the import-linter hole**: add `orchestrator`, `eval`, `api` to `root_packages` and forbid them from `agents` (or generalise the AST scan
   in `test_firewall.py` to all of `agents/`); keep the plant-detect test.
3. **Fix F3/F4 together**: carry `owned_task_ids` in the perception self_state payload and infer completion from set shrinkage (or emit an explicit
   self-channel `completed_task_ids`); decide and document the redistribute timing (defer inheritance to the next meeting resume if death timing is
   meant to be hidden). Update the store.py comment either way.
4. Engine/mask: reject `kill` (and probably `sabotage`) while `in_vent`; align `training/env.py`. Document (or fix) id-order witness semantics.
5. Exclude the observer from `moved_players` at source; delete the two downstream workarounds (a substrate change -> one combined re-record per doctrine).
6. Make the audit log opt-in (env/flag; default off in training), or delete it and drop `_serialize`; index `MemoryStore` (per-tick offsets, seen-body
   set) so perception is O(packet) per tick.
7. Prose diet + drift fixes: fix the MovedPlayerView/perception docstrings, DESIGN §4.2 schema, store.py invariant; move task/PR history to
   audits/; delete `agents/runtime.py` and point its two tests at `ingest_packet`; dedupe the TypeAliases/_FrozenModel.

Scratch artifacts: `scratchpad/work/observation-firewall/{mutate.py,exp_redistribute.py,exp_redistribute_rate.py,exp_selfmove.py,exp_ventkill.py,
exp_witness_order.py,bench_packet.py,bench_perception.py,prose_ratio.py}`; mutation sandbox `mut/` (repo copy, untouched original).
