# Stage B, cards B0 and B1: the physical vent witness arm and the look-first vent exit

Investigator memo, 2026-09-24. Read-only on `main` at `e886b663` (worktree detached there, `uv sync --frozen`).
No tracked file was edited, nothing committed or pushed, no provider call, `.env` never read, no held-out band,
no recorder run against a provider. Every census below is count-only (ids, rooms, ticks, kinds). One
prototype was run in a scratch COPY of the source tree outside the repository (section 6); the worktree
stayed clean (`git status --short` empty before and after).

## 0. Recommendation in one paragraph

Build B0 as a new engine arm `vent_witness_rule: Literal["both_rooms", "physical"] = "both_rooms"` on
`RecordedExperimentConfig`, omitted from the serialized payload at its default so no historical byte moves;
under `"physical"` an EXIT is witnessed only by the room surfaced into (entries are already one-room). Build B1
as a new `vent_exit_policy` value `"look_first"` in `ExperimentalImpostorPolicy`: vent only right after its own
kill; never consult the kill ranking inside a vent; rank exits clear-visible-empty < unseen < visibly-occupied,
tie-break farther from the corpse room, then vent id; wait inside at most N = 2 ticks only when every exit is
visibly occupied (or, under the both-rooms rule, when the room being left is visibly occupied). Both ship
default-OFF with no committed recording byte moving. A scratch prototype on development seeds cut 9p2i crew-seen
exits from 16/29 (baseline) to 6/18 with both arms ON, with zero in-vent waits under the physical rule (as the
map predicts). The working hypothesis fails in one place that belongs to the record card: an arms-ON
recording written INTO `replays/samples/9p2i` is refused by eight replay-walk profiles and four instruments,
and a reader that forgets to thread B0 still passes every state-hash check. Record the 50 seeds as a candidate
run beside the committed sets (the `audits/deduction-candidate/run-2026-09-16/` precedent), or make every
reader of s9 thread-or-refuse each experiment field first.

## 1. Facts established (with citations at e886b663)

### 1.1 The current two-room rule

- `engine/rules.py:111-188` `resolve_vent`. For an EXIT (actor already `in_vent`, `:125-138`) the source room is
  the current vent's room (the room left) and the destination is the connected vent's room. For an ENTRY
  (`:139-144`) source room and destination room are the same room (the actor's own room).
- `engine/rules.py:146-156`: `source_witnesses` = living non-vented occupants of the source room,
  `destination_witnesses` = of the destination room, `witnesses` = their union. So an exit is "seen" by crew in
  the room the impostor LEFT, while the impostor was invisible inside that room's vent. Entries are already
  physical (one room). `engine/rules.py:29-44` is the shared room-occupant helper.
- The rule's documented source is DESIGN.md:351 ("observable ... in the source/destination room").
- `engine/events.py:82-113`: both vent events carry `witnesses`, `source_witnesses`, `destination_witnesses`.
- The state hash is `WorldState` only (`orchestrator/replay.py:2043-2045`); witness lists live on events, never
  in state. Consequence: `scripts/verify_samples.sh` cannot see the witness rule at all.

### 1.2 Where the rule is consumed or re-derived (every site the arm must reach)

Readers of the engine's lists (correct automatically if the engine emits physical lists):
`observation/service.py:652-664` (legacy snapshot and temporal v1 at `:290-300`), `eval/leak_scan.py:139-148`
and `:853-862`, `eval/funnel.py:436`, `training/surrogate/dataset.py:808`, `:823`,
`experiments/tactical_gameplay.py:467-475`.

Independent re-derivations of the two-room rule (must take the rule explicitly):
- `observation/temporal.py:123-150` (temporal v2 delivery: `observer.room in (event.source_room,
  event.destination_room)` at `:132-135`). This contradicts `docs/observation-contract.md:12` ("Engine event's
  actual witness set") the moment the engine rule changes.
- `eval/witness_entitlement.py:93-110` (independent oracle: asserts source and destination lists by room).
- `eval/temporal_entitlement.py:116-139` (v2 oracle: `room in {source_room, destination_room}` at `:131`).

Engine re-simulation call sites that must thread the arm (they already thread `redistribution_policy`):
`orchestrator/game.py:2566-2576` (live tick), `api/replay_loader.py:1633-1640` (loader),
`eval/replay_walk.py:636-642` (walk). `eval/leak_scan.py:1006-1011` must pass the recorded rule to the oracle.
Instruments that re-simulate but refuse experimental recordings (safe by refusal): `eval/off_menu.py:357-361`,
`training/anchor_study.py:441-445`, `training/surrogate/dataset.py:1026`, `experiments/tactical_gameplay.py:194`.

### 1.3 What an in-vent impostor observes

- `engine/visibility.py:130-168` has NO branch on the OBSERVER being in a vent; only vented SUBJECTS are hidden
  (`:64-80`). An impostor at base visibility sees its own room plus adjacent rooms (`:98-127`, Task 13.8
  asymmetry); under lights everyone including the impostor sees its own room only (`engine/maps/canonical_1.yaml`
  lights -> `same_room_only`).
- The snapshot packet is built from that visibility with no in-vent guard (`observation/service.py:340-400`),
  so the in-vent impostor gets `saw_player` rows for its own (corpse) room and the adjacent rooms. In temporal v2
  a vented observer receives no event rows (`observation/temporal.py:71`, pinned by
  `tests/observation/test_temporal_v2.py:567`), but the snapshot still resolves.
- The agent does not receive its visible-room list (`observation/packet.py` has no visible_rooms field) and
  `PublicMapView` carries no sabotage visibility (`observation/public_map.py:14-32`). It can infer "visible" as
  own room plus `room_neighbors` when no sabotage is active (conservative: treat any active sabotage as
  own-room-only).
- Canonical vent graph (computed from the map): every vent has exactly two connections; at most ONE exit room is
  visible from any vent, and it is always the adjacent (1-hop) one. ENGINEERING->STORAGE (1 hop, visible) or
  LABS (5, blind); LABS->MEDBAY (1, visible) or ENGINEERING (5, blind); MEDBAY->LABS (1, visible) or ADMIN (2,
  blind); STORAGE->ENGINEERING (1, visible) or REACTOR (2, blind); ADMIN->MEDBAY (2) or REACTOR (3), both blind;
  REACTOR->STORAGE (2) or ADMIN (3), both blind. 4 of 12 connections are visible.
- So look-first IS possible without an engine change for the visible exit; the blind exit can only be judged
  unknown. No retired sound cue remains: audio is the sabotage alarm only (`observation/service.py:492-507`,
  `observation/packet.py:135-136`); the learned feature `heard_vent_use` is a reserved zero
  (`agents/tactical/features.py:150-152`); `agents/memory/store.py:94` still names "heard vent" in a comment
  (stale, Stage A3 material).

### 1.4 The current exit and entry policy

- Priority: in-vent exit first (`agents/tactical/impostor_policy.py:402-406`), then COVER-or-vent for any body in
  own room (`:413-417`, `:1293-1321`), then sabotage, kill, stalk, idle.
- Entry: vents when a vent is in the room and no non-teammate is sighted there this tick
  (`:1314-1321`, witness scan `:1165-1199`). ANY body triggers it, not only its own kill.
- Exit: body-free connected vents (`:1376-1381`), then `_choose_exit_vent` picks the vent nearest
  `targets[0].room` (`:1404-1418`). With cooldown > 0 every score is multiplied by 0 (`:1271`), so the ranking
  falls back to `(-0, proximity_rank, player_id)` (`:1013-1047`): the nearest crewmate it saw. That is the
  steering defect.
- `observed_risk` (`agents/tactical/experimental.py:192-202`, `:322-358`, `_recent_players` `:74-95`): picks the
  body-free exit with least recent (2-tick) first-hand non-teammate sighting weight, ties to the anchor; never
  waits, never checks the room left, cannot tell "unseen" from "empty".
- Cooldown timeline (kill cooldown 4, `engine/maps/canonical_1.yaml:34`; kill tick skips the decrement,
  `engine/tick.py:639-640`, `:665-668`): kill at k, entry at k+1, first exit decision at k+2 (cooldown 3), then
  k+3 (2), k+4 (1); a kill is first legal at k+5.

### 1.5 Count-only re-measure (my re-run; `walk.json` byte-identical to the synthesis walk)

Commands in section 9. Scopes: pooled = 4 sets / 300 games; 9p2i = s9 + c9; s9 = samples/9p2i (the set the
owner will re-record).

| cell | pooled | 9p2i | s9 |
|---|---|---|---|
| vent exits | 512 | 435 | 85 |
| crew-seen exits, current rule | 313 | 271 | 62 |
| crew-seen exits, physical rule (destination only) | 251 | 226 | 53 |
| exits seen ONLY from the room left | 62 | 45 | 9 |
| vent convictions (impostor ejected carrying a vent flag) | 326 | 281 | 70 |
| ... resting only on room-left exit witnesses | 50 | 37 | 8 |
| ... of those, with another flag on the ejected | 4 | - | - |

Memo figures 62 and 50 reproduce exactly. The rule change alone removes 62 of 313 seen exits and at most 50 of
326 vent convictions (upper bound; the game diverges after the first changed exit).

Exit choice at the time of each exit (pre-tick positions; the impostor's visible set taken as the vent room
plus neighbours, lights ignored):

| option pattern at the exit | n (pooled) | policy chose | destination-seen |
|---|---|---|---|
| one blind exit + one visible OCCUPIED exit | 137 | occupied 134 times | 125 |
| one blind exit + one visible EMPTY exit | 165 | empty 113, blind 52 | 13 of 113; 20 of 52 |
| two blind exits (ADMIN, REACTOR vents) | 210 | - | 93 |

The memo's "134 of 137" reproduces. Base rate: a blind option room held a crewmate before the tick in 268 of
722 cases (37%); for the 134 occupied choices the blind alternative was occupied in 54 (40%).

Decomposition of the 251 destination-seen exits (the population B1 can still act on once B0 is ON): 116 every
witness already standing in a VISIBLE exit room (avoidable by looking), 107 every witness already in a BLIND
exit room (needs a peek; not proposed), 21 arrivals only, 7 mixed. (The memo's 116/99/98 split is over the
313 current-rule exits and counts room-left witnesses; it is a different population.)

Entries (587 pooled / 501 9p2i / 105 s9): 487 / 403 / 92 came the tick right after the impostor's own kill in
that room. The other 100 / 98 / 13: 47 at a body with no own kill in the room (a teammate's victim), 22 own kill
two ticks earlier with a meeting in between, 17 own kill 4+ ticks earlier without a meeting (walked away, came
back), 14 own kill 5+ ticks earlier across a meeting. 17 of the 100 were seen. The memo's "62 (34 teammate +
28 older own)" does not reproduce under my definitions; I report mine and name them.

## 2. B0 design: `vent_witness_rule`

- Name and values: `vent_witness_rule: Literal["both_rooms", "physical"] = "both_rooms"` on
  `RecordedExperimentConfig` (`orchestrator/experiment_config.py:29-47`), with a matching engine alias
  `VentWitnessRule` beside `RedistributionPolicy` (`engine/tick.py:58`). Default = the current rule.
- Engine: `advance_tick(..., vent_witness_rule="both_rooms")` validates the value (raise on unknown, as
  `:615-616` does for redistribution) and threads it through `_apply_action` (`:560-590`) and `_apply_vent`
  (`:442-450`) into `resolve_vent(..., witness_rule=...)`. Under `"physical"`: for an EXIT whose destination
  room differs from the room left, `source_witnesses = ()`; `destination_witnesses` unchanged; `witnesses =
  destination_witnesses`. Entries and exit-in-place are unchanged (one room). Event shape is unchanged, so the
  list readers in 1.2 need no edit.
- Serialization: in `_preserve_version_one_bytes` (`:96-107`) delete `vent_witness_rule` when it equals
  `"both_rooms"`. Required: 100 committed audit recordings (`audits/deduction-candidate/run-2026-09-16/*.jsonl`)
  carry format-2 configs; a naively added field would appear in any re-serialization of them. `is_default`
  (`:116-122`) and `normalize_experiment_config` (`:137-142`) need no change. `has_tactical_changes`
  (`:124-134`) must NOT include it (engine arm).
- How the stamp replays old recordings under the old rule: the four committed sets carry no experiment config
  (0 of 300 files) and the audit files carry configs without the key, so every reader resolves `"both_rooms"`
  and emits today's lists. A physical recording stamps the key on every tick row and the footer, checked for
  agreement by `validate_recorded_experiment_config` (`:145-165`). An older build refuses it loudly
  (`extra="forbid"`): the prototype's unpatched API view refused 8 of 8 physical games with a ValidationError.
- Readers: introduce one helper that maps a recorded config to the `advance_tick` keyword arguments and use it
  at `orchestrator/game.py:2566`, `api/replay_loader.py:1633`, `eval/replay_walk.py:636`, so a future engine arm
  cannot be threaded at one site and forgotten at another. `observation/temporal.py:132-135` switches to
  membership in the event's own witness lists (byte-identical under both_rooms: same alive / not-in-vent /
  event-local-room predicate, and it then matches `docs/observation-contract.md:12`).
  `eval/witness_entitlement.py:93-110` and `eval/temporal_entitlement.py:131` take the rule as a parameter and
  stay independent oracles; `eval/leak_scan.py:1006-1011` passes the recorded rule.
- API and generated output: `api/schemas.py:1430-1447` `ExperimentConfigView` gains the field; the eval-field
  allow-list in `tests/api/test_leak.py:497-500` gains `vent_witness_rule`; `frontend/src/types/api.ts:68`
  regenerates.
- Docs: `docs/architecture.md:143-150` lists the arm; DESIGN.md:351 gets a dated note that the physical rule is
  an explicit arm; `docs/glossary.md` defines "physical vent witness rule" if user-facing copy names it.
- Import boundary: engine, orchestrator, observation, eval, api only. Nothing under `agents/` changes for B0,
  and no agent learns the rule except through the engine-free option in 3.1.

### 2.1 B0 planted tests

1. Exit difference (the defect-proving pair): the existing `tests/engine/test_tick.py:931-987` (p-2 in ADMIN,
   p-4 in REACTOR, exit ADMIN_VENT -> REACTOR_VENT) stays as the both_rooms pin (witnesses p-2, p-4); its twin
   under `"physical"` asserts witnesses (p-4,), source (), destination (p-4,). Room-left crewmate does NOT
   witness under physical and DOES under the default.
2. Entry is one-room under both rules: a crewmate in the entry room witnesses; a crewmate standing in a
   connected vent's room (REACTOR while entering ADMIN_VENT) witnesses under neither; the two rules produce equal
   events (`tests/engine/test_tick.py:505-537` pattern).
3. Exit in place under physical: occupants of that one room witness.
4. Unknown value raises in `advance_tick`; `resolve_vent` default equals today's bytes (property test over
   random vent scenes: default-rule events equal the pre-change events).
5. Observation: a room-left crewmate's legacy packet carries no `vent` action under physical and does under the
   default; same for temporal v2 (`observation/temporal.py`).
6. Oracles: `assert_event_witnesses_match_source_state(rule="physical")` rejects a planted event whose
   `source_witnesses` include the room-left occupant and accepts it under `"both_rooms"`, and vice versa
   (`tests/eval/test_witness_entitlement.py:31-62` poisoned-event pattern). Same for the temporal oracle.
7. Reader gate (necessary, see 6.2): record one fake physical game, load it through `ReplayLoader` with memory
   collection and through `walk_replay`; assert the room-left crewmate's memory holds no vent observation. A
   planted variant with the helper bypassed at one call site must fail this test (state hashes alone pass).
8. Serialization: every committed audit JSONL row's `experiment_config` re-serializes to its on-disk keys; a
   physical config round-trips; `ExperimentConfigView` accepts it.
9. `bash scripts/verify_samples.sh` and the leak scans pass unchanged on the four committed sets.

## 3. B1 design: `vent_exit_policy = "look_first"`

A new value, not a re-scope of `observed_risk`: re-scoping would silently change the recorded lab verdict rows
(`audits/tactical-gameplay/README.md:85,99,113,127,139`; craft rule 7 "preserve earlier experiment verdicts").
Literal extended at `orchestrator/experiment_config.py:38`, `agents/tactical/experimental.py:35`,
`api/schemas.py:1439`. Implemented as an override in `ExperimentalImpostorPolicy.decide`
(`agents/tactical/experimental.py:182-276`); the default `ImpostorPolicy` is untouched, so every committed
decision reconstruction stays byte-identical.

### 3.1 Rules

1. Entry: vent only right after its OWN kill. Predicate over memory only: the latest `own_kill` event names
   `own_room`; a `saw_body` this tick in `own_room` carries that `victim_id`; no `meeting_boundary` event
   follows the `own_kill`; no `self_state` after it places the impostor in another room or in a vent. Otherwise
   the COVER branch walks away (`impostor_policy.py:1323-1338`). Mode-independent (legacy stamps the own kill at
   the packet tick, temporal v2 at the source tick). Changes 100 of 587 pooled entries (13 of 105 on s9).
2. No steering inside the vent: the exit never consults the kill ranking. With the own-kill entry rule and the
   N = 2 cap, every in-vent decision has cooldown 3, 2 or 1 (1.4), so every score is already zero; dropping the
   ranking removes the nearest-crewmate fallback outright.
3. Exit classes, over body-free connected vents (the anchor's filter `:1376-1381` kept):
   CLEAR = the exit room is in the inferred visible set (own room plus neighbours, no active sabotage) and no
   non-teammate `saw_player` there this tick; UNSEEN = not in the visible set; WATCHED = a non-teammate
   `saw_player` there this tick. Rank CLEAR < UNSEEN < WATCHED. Data: visible-empty choices were
   destination-seen 13 of 113 times, blind choices 20 of 52 in the same pattern, visible-occupied 125 of 134.
4. Tie-break: larger hop distance from the corpse room (the vent's room), then vent id. On the canonical map the
   two exits always differ in distance, so this decides every same-class pair (the ADMIN and REACTOR vents).
5. Wait: emit `wait` (legal in a vent, `tests/engine/test_rules.py:289`) iff the best exit is WATCHED, or
   `room_left_watched` is set and a non-teammate is sighted in the vent's own room this tick, AND fewer than N
   in-vent ticks have already been waited. N = 2: inside-count = trailing `self_state` rows with `in_vent`
   (1 at the first exit decision), wait while inside-count <= 2, so the latest exit is k+4, surfacing with
   cooldown 0 for a legal kill at k+5, the earliest possible anyway. N = 2 is the largest wait that costs no kill
   tempo; pin `N == kill_cooldown_ticks - 2` against the canonical map in a test.
6. Every exit watched: wait up to N; then exit to the best by (class, -corpse distance, vent id). No connected
   vent: exit in place (anchor behaviour). Never stuck: after at most N waits a `VentIntent` is emitted.
7. `room_left_watched: StrictBool = True` on `TacticalExperimentOptions`, derived by the orchestrator as
   `config.vent_witness_rule == "both_rooms"` in `_tactical_experiment_options` (`orchestrator/game.py:4422-4433`),
   the precedent being `meeting_positions_preserved` at `:4431`. The agent learns a public rule as a bool and
   imports nothing new (`.importlinter` contracts at `:21-42` unchanged).
8. Teammates are never watchers (fellow ids from `self_state`); reported (non-observed) sightings never count.

What the map implies: with B0 ON, no canonical vent has two visible exits, so the wait branch can only fire
under the both-rooms rule (room left occupied). Expect ~0 in-vent waits in the combined record; that is a
correct outcome, not a dead-branch defect, and the prototype confirms it (6.1). If the owner prefers no branch
that is idle under the adopted rule, drop waiting at graduation; the cap stays as the never-stuck guarantee.

### 3.2 B1 planted tests

1. Occupied vs unseen (defect-proving pair): in STORAGE_VENT with cooldown 3 and a crewmate sighted in
   ENGINEERING this tick, the anchor (`target_distance`) exits to ENGINEERING_VENT and `look_first` to
   REACTOR_VENT.
2. Visible-empty vs unseen: `look_first` takes the visible empty exit (STORAGE from ENGINEERING_VENT).
3. Every exit watched (synthetic public map with two visible exits, `tests/agents/test_impostor_policy.py:62-65`
   fixture) -> `wait`; with `room_left_watched` and a crewmate in the vent room -> `wait`; with
   `room_left_watched=False` the same memory exits.
4. After N = 2 waits it exits (three trailing in-vent self_states -> `VentIntent`), to the farther watched exit.
5. A teammate sighted in the exit room is not a watcher; a reported sighting is not a watcher.
6. A teammate's victim (no own_kill) in own room with a vent and no witness: anchor vents, `look_first` walks
   away (proves the entry gate). An own victim across a `meeting_boundary`, and an own victim after leaving and
   returning: no vent. A fresh own kill: vents (control).
7. Invariance: two memories differing only in stale target sightings give the same `look_first` exit and
   different anchor exits (proves the steering is gone).
8. Away from the corpse: in ADMIN_VENT (both blind) it takes REACTOR_VENT (3 hops) over MEDBAY_VENT (2).
9. Lights (global_status sabotage active): a neighbour room without a sighting is UNSEEN, not CLEAR.
10. Hypothesis property: over random in-vent memories, every intent is `vent` or `wait`, a `vent` appears
    within N+1 consecutive in-vent decisions, and repeated calls and permuted `room_neighbors`/`vent_graph`
    listings give the same intent.
11. Wiring: a `HeadlessGame` with `look_first` builds `ExperimentalImpostorPolicy` with the derived option;
    its fake game repeats byte-identically; `tests/experiments/test_tactical_gameplay.py:27-68` parametrize gains
    the new arms; `lint-imports` passes.

## 4. Pins, bytes, and the lab protocol

- Default-OFF PR: no committed recording byte moves (engine default equals today; serializer omits the default;
  `ImpostorPolicy` untouched). Moving at that PR: the Literal inventories (`tests/orchestrator/test_experiment_config.py`),
  the API view and its leak allow-list, generated `frontend/src/types/api.ts`, the lab arm list.
- Pins that move when s9 is recorded with `look_first` (and would first REFUSE, see 5): the I-11 targeting
  cells `tests/agents/test_impostor_policy.py:2174-2215` (1754 decisions, 109 in-vent, 9/232 declined, 223
  recorded kills), the seed-20 exemplar `:2138-2155`, the ejected-ranking walk `:2035-2062`, and every s9 pin
  in the evidence-honesty, funnel, kill-craft, solvability, watchability and vote-tally suites. The
  reconstruction re-runs the DEFAULT policy (`eval/evidence_honesty.py:1238-1282`), so in-vent decisions on a
  look_first recording would count as mismatches, not reproduce.
- Lab protocol reproduced at e886b663 (development seeds 1000-1007, fake provider, `--arms baseline vent_risk`):
  exactly the README development rows (`audits/tactical-gameplay/README.md:81,85,95,99`): 4p1i baseline 6/8,
  waits 22, 48 calls; observed_risk 5/8, 25, 48. 9p2i baseline 16/29, waits 96, 294 calls; observed_risk 14/34,
  106, 308. Destination-only exposure, which the lab also records: 9p2i 13/29 -> 9/34. The card should require
  the same protocol for `vent_physical`, `vent_look_first` and one declared two-field interaction arm on both
  splits (the lab's held-out split is seeds 2000-2015, not the 2100-2999 prompt band), and report
  destination-only exposure, in-vent waits, entries not after an own kill, and meetings opening with an
  impostor in a vent. Fake meetings eject nobody; these rows measure mechanics only.

## 5. The partial-record hypothesis: where it holds and where it fails

Holds: both arms can be added default-OFF; missing config means the historical rule; the three other sets
keep their bytes, load, verify (state hashes are rule-independent) and feed their gates unchanged.

Fails, exactly here, if the 50 arms-ON seeds are written INTO `replays/samples/9p2i`:
1. Eight walk profiles refuse any experiment-stamped recording (`eval/replay_walk.py:355`, `:505-508`):
   `eval/evidence_honesty.py:2605`, `eval/funnel.py:254`, `eval/kill_craft.py:527`, `eval/solvability.py:698`,
   `eval/validity.py:508`, `eval/watchability.py:1544`, `eval/win_condition_selfcheck.py:205`,
   `eval/balance_eval.py:914`; plus `eval/off_menu.py:357-361`, `training/anchor_study.py:441-445`,
   `training/surrogate/dataset.py:1026`, `experiments/tactical_gameplay.py:194`. Their tests walk s9, so
   `scripts/check.sh` goes red. The synthesis census itself walks with the evidence-honesty profile
   (`synth0924/walk.py:15`) and would refuse the new bytes.
2. Verification is blind to B0: state hashes exclude witness lists, so a reader that forgets the arm passes
   `verify_samples.sh` while serving old-rule observations (measured in 6.2).
3. Adoption cannot simply flip B0's default while the other three sets stay at baseline-9 bytes: their missing
   config would then mean `physical`, silently changing every memory reconstruction of games recorded under
   both_rooms. B0 must either keep "missing = both_rooms" and stamp `physical` explicitly forever, or be adopted
   together with a re-record of every set that stays in use.
Recommended: record the 50 seeds as a candidate run in a new directory beside the committed sets, assess with
experiment-capable instruments (`eval/process_scorecard.py:782-787`, `eval/balance_eval.py:933-936`,
`eval/leak_scan.py:950-951`) and a census walk that threads-or-refuses each field; decide adoption after.

## 6. Prototype in a scratch copy (outside the repository)

A throwaway copy of the source tree (no `.git`, `.env`, `replays`, `audits`) was patched with a minimal B0
(`resolve_vent` rule, `advance_tick` threading, config field omitted at default, live and walk call sites) and
a minimal B1 (the rules in 3.1 without the lights refinement tests), then run with the lab's own
`run_candidate` and `measure_replay` on development seeds 1000-1007, fake provider, $0.

### 6.1 Counts (8 games per cell)

| arm | 4p1i seen exits | 9p2i seen exits (dest-only) | 9p2i entries | in-vent waits 9p | calls 9p |
|---|---|---|---|---|---|
| baseline | 6/8 | 16/29 (13) | 29 (10 not after own kill) | 0 | 294 |
| observed_risk | 5/8 | 14/34 (9) | 34 (17) | 0 | 308 |
| look_first (both_rooms) | 5/8 | 11/18 (6) | 18 (0) | 8 | 308 |
| physical only | 5/8 | 13/28 (13) | 28 (9) | 0 | 304 |
| physical + look_first | 2/8 | 6/18 (6) | 18 (0) | 0 | 308 |

The patched baseline arm reproduces the README rows exactly (default untouched). Both new arms re-ran to
identical replay digests. Under both_rooms the room-left channel persists (5 room-left-only exits with
look_first): most room-left witnesses walk in on the exit tick, which no look can prevent; B0 removes them.

### 6.2 Silent-reader measurement

8 physical-arm 9p2i games, 221 ticks re-simulated from their recorded actions with and without the arm:
state hashes equal on 221 of 221; vent-exit witness lists differ on 4 of 28 exits. The unthreaded API view
refused all 8 only because its schema lacked the key; once the view is updated that refusal disappears. This
is why planted test 2.1-7 and the single threading helper are necessary.

### 6.3 Static counterfactual on the committed bytes (one step, not a prediction)

Re-ranking each committed exit by the look-first order and counting a crewmate already standing in the new
room (arrivals and all later divergence ignored): destination-seen exits 251 -> 124 pooled, 226 -> 117 on
9p2i, 53 -> 23 on s9 (with an id tie-break instead of the corpse-distance one: 146 / 133 / 29).

## 7. What the 50-seed assessment should read (process first; role-correctness reported, never gated)

Mechanical invariants, asserted by count on the candidate run: 0 exits into a visibly occupied room when
another exit existed (baseline s9: 31 of 32); 0 entries not right after an own kill (baseline s9: 13 of 105);
0 room-left-only witnessed exits (baseline s9: 9); in-vent streak never above 3 ticks. Reported cells (the
census report, never the scorecard, per R13): crew-seen exits over exits, vent-proof ejections, meetings
without vent proof and their outcomes, impostor fate by vent exposure, meetings opening with an impostor in a
vent (0 expected with B2's hub reset).

## 8. Risks

- More impostor survival and more meetings without vent proof, where the table reasons worst; the owner has
  accepted the statistic shift.
- A missed reader call site serves wrong observations with green hash checks (6.2).
- Waiting in a vent lengthens the impostor's "a vent in ROOM" self-location span
  (`agents/memory/store.py:1554`) and can place it in a vent when a meeting opens; watch that cell.
- Visible-set inference is the agent's own sight model; any future map or visibility change must update it
  (pin it against `engine/visibility.py` in a test that may import the engine).
- Blind exits stay a 37-40% gamble on this map; closing that needs an engine peek (not proposed).

## 9. Reproduction

From the repo root at e886b663 (outputs outside the tree):

    PYTHONPATH=. uv run --frozen python <synth0924>/walk.py <scratch>/walk.json      # 300 games, verified walk
    python3 <synth0924>/an1.py <scratch>/walk.json; python3 <synth0924>/an4.py <scratch>/walk.json
    PYTHONPATH=. uv run --frozen python <stageb_vent>/vent_b0b1.py <scratch>/walk.json
    PYTHONPATH=. uv run --frozen python <stageb_vent>/vent_cf2.py <scratch>/walk.json
    PYTHONPATH=. uv run --frozen python -m experiments.tactical_gameplay --split development \
        --arms baseline vent_risk --output <scratch>/tactical-dev.json

`<synth0924>` = the synthesis scratchpad; `<stageb_vent>` =
`<session scratchpad>/stageb_vent`
(also holds `probe_patch.py`, `probe_run.py`, `probe_silent.py` and the patched `probe_tree/` for section 6).
