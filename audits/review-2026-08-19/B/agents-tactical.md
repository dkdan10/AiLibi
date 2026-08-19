# Code-up review — `agents/tactical/` (label: agents-tactical)

Scope: `agents/tactical/{crewmate_policy,impostor_policy,features,pathing}.py`, `agents/tactical/learned/{forward,crew_forward,factory,weights}.py` (+ committed weight artifacts) and `tests/agents/test_{crewmate_policy,impostor_policy,pathing,features,learned_policy}.py` (+ `tests/training/test_learned_factory_acceptance.py` where it is the only test surface for `crew_forward.py`).
Method: read every file end-to-end (hot paths fully), ran the area's tests, mypy, radon, vulture, pylint duplicate-code, a BFS-vs-A* fuzz (18k queries), a decide() micro-benchmark + cProfile, three deterministic repro scripts, and two measurements over the committed `replays/samples/9p2i` set (54 replays, 2 198 impostor play-ticks). Scratch: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/work/agents-tactical/`. Machine load during timings: 4.5–7.3 (10 cores, other reviewers concurrent).

---

## 1. Executive read (10 lines)

1. The area is 5 683 lines / 8 modules; ~1 860 logical lines. Roughly 35–41 % of the two FSM files is prose (docstrings + comments), much of it task/audit history rather than behaviour contract.
2. **Pathing is correct and deterministic** — 18 000 random-graph queries: 0 length mismatches vs BFS, 0 order-dependence, every hop an edge [VERIFIED].
3. **Both FSMs are pure functions of the episodic log**, all tie-breaks are sorted-id, no RNG, no module state; mypy --strict clean; no `engine/` import. Determinism claims hold [VERIFIED].
4. **The impostor kill logic has a real defect**: the kill gate only re-validates `targets[0]`, so a lower-id (or stale) target elsewhere makes the impostor walk away from a free, zero-witness, co-located kill. In the committed 9p2i replay set **126 of 387 (33 %) ticks with a free kill available were wasted this way** [VERIFIED].
5. **The stalk logic ignores negative evidence**: 298 of 880 (34 %) stalk moves in the same set head for a room the impostor can currently see and where the target is verifiably absent, producing room ping-pong (seed-10 ticks 28–33; a 25-tick synthetic post-kill loop) [VERIFIED].
6. `agents/tactical/learned/` is a **verbatim ~960-line copy of training-side code** (`training/bakeoff/utility_es.py`, `training/crew/options.py`, `training/env.py`, `training/crew/scorer.py`) held together by "Q4 parity" tests; `.importlinter` allows `training → agents`, so the duplication is avoidable [VERIFIED].
7. `features.py` (923 lines: encoder v2/v3 + MLP + hex weights) has **no production consumer under `agents/`** — the shipped champions are 19/27-weight linear per-option scorers; the encoder is used only by `training/`, `experiments/`, tests [VERIFIED].
8. Weight loading is well done: sha256 sidecar verified on every load, lossless float-hex, genome-length check, stamp digest read from the verified artifact, byte-equality to `training/artifacts` pinned by test [VERIFIED].
9. Within the package the crew/impostor pair and the two learned surfaces duplicate helpers (self-state accessors, `_move_toward`, `_path_hops`×2, `_movement_step`×2, `_verified_payload`×2, `_vent_in_room`×2, twin Stamp/Factory/Scorer classes) and carry ~33 `raise ValueError` payload guards over an untyped `payload: Mapping[str, object]`.
10. Tests: 196 fast (2.8 s), behaviour-oriented through `decide()`, readable fixtures; but they **pin the defective tie-break**, redeclare map/event helpers in ≥7 files, and `crew_forward.py` is only covered indirectly via parity with its own duplicate.

---

## 2. Findings (ranked)

### F1 — P1 [VERIFIED] Kill gate only checks the top-ranked target; free kills are abandoned
`agents/tactical/impostor_policy.py:336-361` (`decide`) and `:766-812` (`_kill_available_now`).
`_scored_targets` sorts by `(-score, player_id)`; the kill seam then re-validates **only `targets[0]`** with `_target_colocated_now`. Any other target with an equal score (isolation 1.0 is common) and a lower id — or a stale sighting still within the 30-tick window — outranks the co-located victim, and the branch falls to STALK.

Repro (`repro_kill_ranking.py`): impostor `p-9` in CAFETERIA, `p-5` alone with it, `p-2` alone in adjacent ADMIN, cooldown 0:
```
co-located=p-5 adjacent=p-2 -> move to_room='ADMIN'      # walks away from a free kill
co-located=p-2 adjacent=p-5 -> kill target='p-2'         # only the id order differs
```
Real-world frequency (`measure_missed_kills.py`, committed `replays/samples/9p2i`, 54 replays):
```
impostor_ticks=2198 cooldown0_ticks=1274 kill_available_ticks=387
intent_kill=233 MISSED_KILL=126 deferred=28 intent_wait=16 intent_sabotage=4
```
Example: seed-10 tick 30, `p-3` in ENGINEERING with only `p-5` visible there; targets = `[p-1@REACTOR(stale), p-5@ENGINEERING, ...]` all score 1.0 → `move REACTOR`.
Why it matters: this is the default production FSM (the anchor/BC oracle for the whole ML program) and the phase-13/18 baselines were recorded with it; a third of the impostor's kill opportunities evaporate for a sorting reason, not a design one. The learned menu (`forward.py`) enumerates `kill_now` for *every* co-located target, so the ES champion is not affected — the FSM is.
Fix: choose the kill target as `min` over co-located, zero-witness, non-fellow targets (or rank co-location above the score tie) and reuse that single computation for the sabotage guard (see F4). Confidence: high.

### F2 — P1 [VERIFIED] Stalk ignores negative evidence → chases refuted sightings, ping-pongs
`impostor_policy.py:937-1008` (`_scored_targets`, staleness only by age), `:361-368` (STALK).
The impostor sees own+adjacent rooms (`engine/visibility.py`), yet a sighting whose room is currently in view and whose player is absent is still the "best" lead until it is 30 ticks old.
Measurement (`measure_stale_stalk.py`, same set): `stalk_moves=880 stalk_toward_refuted_sighting=298` (34 %).
Repro (`repro_cover_pingpong.py`): after a kill with a stale sighting of another player in the kill room, the FSM alternates COVER-move-out / STALK-back-in for 25 consecutive ticks (t15–t40) until the sighting ages out. Seed-10 ticks 28–33 shows the same ENGINEERING↔REACTOR oscillation live.
Fix: in `_scored_targets` drop (or heavily de-rank) a latest sighting whose room ∈ visible rooms of the current tick while the player is not in this tick's `saw_player` set. Note the small all-adjacent test map means `test_stalk_prefers_more_isolated_target_over_witnessed_one` / `test_stalk_picks_alphabetically_first_id_when_scores_tie` currently pin the refuted-chase behaviour and would need re-fixturing. Confidence: high.

### F3 — P1 [VERIFIED] ~960 lines duplicated verbatim between `agents/tactical/learned/` and `training/`
`learned/crew_forward.py:99-716` ≡ `training/crew/options.py:106-695` (568 identical lines); `learned/forward.py:251-541` ≡ `training/bakeoff/utility_es.py:269-563` (286); `learned/crew_forward.py:910-1063` ≡ `training/env.py:206-367` (90); `crew_forward.py:1161-1195` ≡ `training/crew/scorer.py` (19). Total 963 identical lines (difflib), plus `intent_key` re-implemented "verbatim" from `training/bakeoff/harness.py:343`.
The module docstrings justify it by the firewall ("no training import"), but the firewall is one-directional: `.importlinter` forbids `agents → training`, not `training → agents`. The training modules already import `agents.tactical.impostor_policy`; they could import `agents.tactical.learned.forward.enumerate_options` etc. and the parity tests (`test_q4_gate_*`, `test_crew_build_action_mask_matches_the_training_side_mask`, `test_fixture_menu_and_scores_match_the_training_side_bit_for_bit`) would collapse to identity. Every future menu/mask change must currently be made twice and re-pinned. Confidence: high.

### F4 — P2 [VERIFIED] `_kill_available_now` duplicates the kill block; ladder ordering is inverted to compensate
`impostor_policy.py:766-812` mirrors `:336-357` line-for-line ("exactly the kill block's emission condition"). Because SABOTAGE is evaluated *before* KILL but must lose to it, a second copy of the kill predicate exists purely to peek ahead. Compute the kill target once, then order `kill → sabotage → hold/defer → stalk → idle`; delete `_kill_available_now`. This also removes the drift risk that F1's fix is applied to one copy only.

### F5 — P2 [VERIFIED] `features.py` encoder/MLP live under `agents/` with no production consumer
`agents/tactical/features.py:213-829` (`TacticalFeatureEncoder`, `TacticalFeatureEncoderV3`, `encode_features_v3`, `mlp_forward`, `mlp_genome_length`). grep: consumers are `training/bakeoff/*`, `training/determinism.py`, `training/coevo/*`, `experiments/lab/*`, tests only. Production imports from this file are `quantize_unit_interval`, `beliefs_suspicion`, `_episodic_last_seen`, `BELIEF_QUANT_LEVELS`, `weights_from_hex_json` (by `crew_forward.py`/`weights.py`). ~700 of 923 lines are "firewall-legal inference path" for a policy that never shipped; `TacticalFeatureEncoderV3.encode` also recomputes `_roster_and_last_seen` (a full episodic scan) a second time on top of `super().encode()`. Move to `training/` (or `agents/tactical/learned/encoders.py` clearly marked training-only) and keep the four small helpers.

### F6 — P2 [VERIFIED] Intra-package duplication
- `_latest_self_state`, `_room_from_self_state`, `_pending_task_from_self_state`: identical in `crewmate_policy.py:404-432` and `impostor_policy.py:404-432` (pylint R0801 `[422:468]≡[400:446]`).
- `_move_toward`: crew swallows `ValueError` → wait (`crewmate_policy.py:678`), impostor raises and each caller wraps (`impostor_policy.py:1159`, callers at `:363-368`, `:1250-1255`).
- `_repair_distance` ≡ `_vent_distance` ≡ `_path_hops` (×2 in `learned/forward.py:190`, `learned/crew_forward.py:237`); `_movement_step` ×2 (`forward.py:205`, `crew_forward.py:252`).
- `_verified_payload` ×2 (`learned/weights.py:33`, `crew_forward.py:1315`); `_vent_in_room` ≡ `_mask_vent_in_room`.
- `LearnedPolicyStamp` ≡ `LearnedCrewPolicyStamp` (same 5 fields); `LearnedAgentFactory`/`LearnedCrewAgentFactory`, `_LearnedAgent`/`_LearnedCrewAgent`, `LearnedImpostorScorer.score/evaluate` ≡ `LearnedCrewScorer.score/evaluate` (`forward.py:565-617` vs `crew_forward.py:1247-1302`, pylint-flagged).
A `_common.py` (accessors, hops/step, verified loader, `LinearOptionScorer[OptionT]`, one stamp model, one role-parameterised wrapper) would remove ~300 lines.

### F7 — P2 [VERIFIED] Defensive parsing sprawl over an untyped event payload; inconsistent policy for the same field
`impostor_policy.py`: 20 `isinstance` guards / 23 `raise ValueError` / 19 `payload.get`; `crewmate_policy.py`: 8 / 10 / 11. All defend against the project's own `agents.perception` producer (typed pydantic packet → `dict`). Same field, different policy: `crewmate_policy._seen_victim_ids` silently skips a missing `victim_id` (`:299-303`), `ImpostorPolicy._confirmed_dead_from_bodies` raises (`:833-836`). Typing the payload per event kind (TypedDict / frozen dataclass minted by perception) deletes ~150 lines and the inconsistency.

### F8 — P2 [VERIFIED] Docstring/comment sprawl and factual drift
- Prose share: crewmate 35 %, impostor 41 %, features 40 %, factory 38 % (docstring+comment lines / total). `impostor_policy.py` alone carries 36 `Task N.M` refs, 13 audit refs, 4 "Codex review" notes; the 165-line module docstring is a change-log.
- Wrong: `impostor_policy.py:86-89` "co-present witnesses keep the score at zero" — score = `1/(1+c)²` (0.25 with one witness), never zero. Also `isolation` and `1 − witness_risk` are the same number, so the "hint" `isolation × (1 − witness_risk)` is `isolation²`; in `learned/forward.py` `isolation`/`witness_risk` are collinear features (harmless, one redundant weight).
- `DESIGN.md §4.4` lists 2 of the crew's 4 interrupts and omits impostor VENT_EXIT/SABOTAGE; `DESIGN.md:642-643` says "`current goal` / `current path` are written by the tactical policy but never read back" — no production writer exists (`grep set_goal|set_path` → tests only) and `record_sighting` *is* called (`agents/memory/store.py:1589`).

### F9 — P2 [VERIFIED] `decide()` is O(history) per tick with 4 full-log scans
Bench (`bench_decide.py`, canonical map, 8 visible players/tick):
```
ticks=  10 events=  110 impostor.decide=0.036 ms  crew.decide=0.009 ms
ticks= 300 events= 3300 impostor.decide=0.426 ms  crew.decide=0.123 ms
ticks=1000 events=11000 impostor.decide=1.364 ms  crew.decide=0.388 ms
```
cProfile: 70 % in `_scored_targets` (scans the whole log although only the last 30 ticks can survive the staleness filter), then `MemoryStore.recent(since_tick=0)` re-tupling the log, `_confirmed_dead_from_bodies`, `_min_remaining_under_gating_sabotage`. Irrelevant for live play (µs budget met at realistic sizes), relevant for ES rollouts where decide() is the inner loop across thousands of games. Fix: `recent(since_tick=latest-30)` for scoring; incremental min-remaining.

### F10 — P2 [VERIFIED] Dead-in-package mask surface
`learned/crew_forward.py:884-1137` ports the *whole* `training/env.py` mask "so the fixture pins can assert full equality" — impostor branches (kill/vent/sabotage) plus `is_engine_legal` / `submission_legal` have no caller under `agents/` (only `is_submission_legal` for crew overrides). Cost is negligible (`_build_action_mask` 0.019 ms/call, 14 entries) — the issue is 250 lines of code that exists for a test in another package.

### F11 — P2 [JUDGMENT] Latent config drift in the emergency tracker
`crewmate_policy.py:224` `call_available = self._own_calls_used == 0` hardcodes one press per game; the map is parametric (`engine/maps/canonical_1.yaml:430 uses_per_player: 1`, `engine/world.py:224`) and the learned crew wrapper already injects `emergency_uses_per_player`. Not a bug today.

### F12 — P2 [VERIFIED] Private-API coupling across modules
`learned/forward.py` and `learned/crew_forward.py` call `ImpostorPolicy._scored_targets/_confirmed_dead_from_bodies/_body_visible_rooms/_target_colocated_now/_non_teammate_witness_present/_crew_near_task_win/_sabotage_window_open/_active_sabotage/_vent_in_room`, `CrewmatePolicy._first_visible_body/_kill_witnessed/_active_gating_sabotage/_walk_to_button/_walk_to_repair/_return_to_hub/_move_toward/_do_task/_report`, `_seen_victim_ids`, `features._episodic_last_seen`, and construct `ImpostorPolicy(agent_id=actor)` just to call `_defers_to_colocated_fellow`. Documented as "zero reimplementation drift", but it makes the underscore API load-bearing; promote the helpers to a small public `impostor_facts` / `crew_facts` module.

### F13 — P2 [VERIFIED] Test-suite structure
- Fixture helpers `_public_map`, `_self_state_event`, `_saw_player_event`, `_cooldown_event`, `_store_with` are re-declared in ≥7 test files (`tests/agents/test_{crewmate_policy,impostor_policy,learned_policy,runtime,perception,beliefs_wiring}.py`, `tests/training/test_bakeoff_methods.py`).
- `tests/agents/test_impostor_policy.py` has 12 direct calls to `ImpostorPolicy._*` (boundary-raise tests) — implementation pins.
- `test_stalk_picks_alphabetically_first_id_when_scores_tie` and `test_stalk_prefers_more_isolated_target_over_witnessed_one` pin F1/F2 behaviour (both target rooms are adjacent-and-visible-and-empty in the 4-room test map).
- No behaviour tests for `enumerate_crew_options` semantics (buddy/patrol/emergency reconstruction) under `tests/agents/`; coverage is parity-with-duplicate in `tests/training/`.

### What is GOOD [VERIFIED]
- `pathing.py`: 88 lines, correct, deterministic, `ValueError` contract honoured; the doc note that zero-heuristic A* is uniform-cost search is honest.
- Determinism discipline is uniform and real: sorted ids everywhere, `min(..., key=(dist, id))` totals, integer cross-multiplication for the 6/7 threshold, `math.fsum` with the hazard documented, `EmergencyButtonView` snapshot keeps `decide` pure while `EmergencyPacingTracker` owns time.
- Kill-emission re-validation against *this tick's* sightings (`_target_colocated_now`) means the producer never emits a cross-room kill.
- Weight artifacts: sidecar-verified loader, lossless float-hex, genome-length check, stamp digest read from the artifact actually loaded, byte-equality with `training/artifacts` pinned; the crew stamp namespace deliberately disjoint from the impostor's.
- The interrupt-preserving constraint in `enumerate_owned_task_options` (a visible body → menu of exactly one `report`) is a good structural guard rather than a penalty.
- The wrapper factories are engine-free by injection (`InnerAgentFactory`), and `_LearnedCrewAgent` fail-louds on an off-vocabulary override.
- Tests are fast (196 in 2.8 s), mostly exercise `decide()` end-to-end with hand-built episodic logs, and cover priority ordering exhaustively (body > kill > repair > suspicion; vent-exit > cover > sabotage > kill).
- mypy --strict clean; no `engine/`/`training/`/numpy import anywhere in the package.

---

## 3. Architecture / design assessment

**Well-designed.** The "FSM" is really a stateless priority ladder over an append-only log — a good choice: no hidden state, trivially replayable, testable with hand-built events. Splitting temporal bookkeeping into `EmergencyPacingTracker` + an immutable per-tick `EmergencyButtonView` is the right pattern. The learned layer's idea — FSM proposes the option menu, a tiny linear head arbitrates — is sound and keeps the learned policy on-vocabulary by construction. Firewall posture is enforced structurally (import-linter, injection) not by convention.

**Accidental complexity.**
1. Priority ladder written as an if-chain that needs a look-ahead predicate (`_kill_available_now`) because branches are ordered for prose reasons rather than evaluation order (F4).
2. Target scoring conflates "who to stalk" and "who to kill" into one ranking, and the kill seam trusts the ranking (F1). Two questions, one list.
3. Untyped `payload: Mapping[str, object]` pushes parsing + validation into every consumer (F7); the policies are ~25 % accessor boilerplate.
4. The learned package copies training code instead of being imported by it (F3), and parks a training-only encoder in the inference package (F5). The stated reason (firewall) is directionally wrong.
5. Two parallel class hierarchies for impostor/crew learned surfaces where one generic scorer/wrapper/stamp would do (F6).
6. Docstrings function as a change-log (F8); the behaviour contract is hard to find inside the history.

**Refactor sketch (in order):**
- `impostor_policy.decide`: `kill_target = self._kill_target_now(...)` (min over co-located zero-witness non-fellow, non-deferring); ladder `vent_exit → cover → kill → sabotage → hold/defer → stalk → idle`; `_scored_targets` gains negative-evidence pruning and a 30-tick `recent()` window.
- `agents/tactical/_common.py`: self-state accessors, `path_hops`, `movement_step`, `verified_payload`, `Linear OptionScorer[OptionT]`, one `PolicyStamp`, one `LearnedWrapper(role=...)`.
- `training/bakeoff/utility_es.py`, `training/crew/options.py`, `training/env.py`, `training/bakeoff/harness.intent_key`: import from `agents.tactical.learned`; delete copies; parity tests → identity assertions or removal.
- `features.py`: keep `quantize_unit_interval`, hex weights, `beliefs_*`, `_episodic_last_seen`; move encoders + MLP to `training/`.
- Typed episodic payloads minted by `agents.perception`.

---

## 4. Test assessment

- **Coverage of behaviour**: good for the ladders (priority tests for every interrupt pair, teammate coordination, staleness, sabotage window re-arm/loop, vent enter/exit, blend). Pathing has 12 focused tests. Learned: loader/sidecar/basis/fsum/tie-break/Q4 parity/leak-test factory mode.
- **Gaps**: (a) no test for "co-located zero-witness target that is not `targets[0]`" — the F1 case; (b) no test for negative evidence — two tests pin the opposite; (c) `enumerate_crew_options`/`enumerate_owned_task_options` behaviour only via parity with the training duplicate; (d) no property/fuzz test on pathing (my 18k-query fuzz would be a cheap hypothesis test); (e) no replay-derived regression tests (the corpus walker exists in `test_features.py` and could feed FSM decision assertions).
- **Implementation pinning**: 12 `ImpostorPolicy._*` calls; `test_score_is_the_fsum_dot_product_plus_bias` / `_correctly_rounded_not_a_naive_sum` pin `fsum` (deliberate bit-exact contract — acceptable).
- **Hygiene**: helpers duplicated across ≥7 files, no `conftest.py` fixtures for `PublicMapView`/event builders; test files are 1.5–1.7 k lines each.
- **Speed**: excellent (196 tests / 2.8 s; corpus totality tests 1.6 s + 0.4 s; crew leak-test 7.9 s in `tests/training`).

---

## 5. Recommendations (prioritised)

1. **Fix F1 + F2 together** in `_scored_targets`/`decide` (kill target = min over co-located zero-witness targets; drop refuted sightings), add the two replay-derived regression tests (seed-10 tick 30; seed-12 tick 10) and re-fixture the two tie-break tests. Treat as a substrate change (one combined re-record per the cadence doctrine); expect a visible impostor-kill-rate shift, so record baseline deltas.
2. **Restructure the impostor ladder** so kill is evaluated before sabotage; delete `_kill_available_now` (F4). ~40 lines removed, one predicate to maintain.
3. **Single-source the learned menus/mask**: training imports `agents.tactical.learned`; delete `training/bakeoff/utility_es.enumerate_options`, `training/crew/options.enumerate_*`, `training/env.build_action_mask` bodies; convert Q4 tests to identity checks (F3). ~1 000 lines gone.
4. **Extract `_common.py`** and collapse the twin Stamp/Factory/Scorer classes into one generic each (F6). ~300 lines.
5. **Relocate encoder v2/v3 + MLP** out of `agents/tactical/features.py` into `training/` (F5); keep the four helpers.
6. **Type the episodic payloads** at the perception boundary and delete the isinstance/raise guards (F7); reconcile the `victim_id` policy.
7. **Docstring diet + drift fixes**: move task/audit narrative to `audits/`, fix "score at zero", update `DESIGN.md §4.4` and the working-memory HEAD note (F8).
8. **Bound the per-tick scans** (30-tick `recent()` window, incremental min-remaining) and add a `conftest.py` with the shared map/event fixtures (F9, F13).

Report path: `/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/d2f79696-15f2-4a2e-a7e2-cb7d5b023724/scratchpad/reports/B/agents-tactical.md`
