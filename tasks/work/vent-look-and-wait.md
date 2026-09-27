# B1: impostors look before leaving a vent and vent only after their own fresh kill

**Status:** done

## Outcome

Two recorded values, both default OFF, give the experimental impostor policy the owner's B1: it
stops surfacing from a vent into rooms it can see are watched, and it stops diving into vents at
bodies that are not its own fresh kill.

- `vent_exit_policy = "look_and_wait"` (a new value of the existing field). On every tick inside,
  the impostor surfaces only when its vent room and every neighbour it can see hold no one but
  teammates: in place, or at a visibly clear connected vent that is strictly better by a fixed key.
  Otherwise it waits. At a cap of 4 play ticks inside, restarted at a meeting boundary, it must
  surface. It never surfaces into a room it cannot see before the cap, and it never consults the
  kill ranking while inside.
- `vent_entry_policy = "own_fresh_kill"` (a new field, default `"any_body"`). The impostor enters
  a vent only when a body in its room is its own victim, killed at most 3 ticks earlier with no
  meeting between. Any other body means today's walk-away move.

Both live only in `ExperimentalImpostorPolicy`. The default `ImpostorPolicy` is untouched, so every
committed recording, every decision reconstruction over it and every derived view stays byte
for byte what it is. Nothing records ON until the record card writes candidate round 1 into
`replays/candidates/stage-b-r1/9p2i/`.

The card also lands the lab attribution arms and their development rows, publishes (Evidence)
what a 50-game record of `replays/samples/9p2i` can and cannot resolve, and names hidden vent
travel as the priced escalation and the status-quo policy as the fallback. It reverses
`tasks/phase-11.md:65-68` (exit toward the best isolated target; a careless vent near a witness
as the deliberate tell), dated in the 2026-09-24 addendum to the direction's section 12.

## Evidence

Every `path:line` here is a citation at `e886b663`, labelled as such. Wave 1 and 2 cards move
lines, so the implementer re-anchors each by the named symbol at dispatch. The Stage-B memos are
in `~/.claude/projects/-Users-danielkeinan-projects-AiLibi/stage-b-2026-09-24/`:
`decision-memo.md`, `vent_witness_and_exit.md`, `vent_movement_options.md` and
`orchestrator-vent-ruling.md`.

**Owner rulings of 2026-09-24, verbatim.** "We should implement stage B". "B1. Add vent logic so
that imposters try to avoid being caught coming out of a vent." On the record: "When it's time to
record, record the smaller group of 50 seeds, assess if the implementations have been effective
and resulted in desired results. Also it is understood that updating the vent and body reset logic
will probably have a substantial effect on previous limits and statistics around the baseline
voting results, that is okay." And "Hold off on ML as D suggests until gameplay is finished." and
"Tour fix can be deferred to after gameplay is finished".

**Orchestrator rulings under the owner's delegation of 2026-09-24.** The vent ruling
(`orchestrator-vent-ruling.md`), verbatim in its load-bearing parts:

> RULING (under the owner's delegation; the owner may overrule before dispatch): B1 = the
> policy-only look-first WAIT-IN-PLACE exit on today's engine, paired with R7. Hidden travel is
> recorded as the priced alternative for a later wave, and if ever adopted it must cap hops at 1
> or 2 and drop the maximize-distance-from-body term (map intent).
>
> - policy: on each tick inside, if the vent's own room and every VISIBLE adjacent room hold no
>   non-teammate, surface in place (or at a visibly clear connected vent when the own room is clear
>   but a connected room is strictly better by the deterministic key: no body, not the room fled
>   from, then vent id); else wait; at the cap (4 play ticks inside, restarted at a meeting
>   boundary, which B2 clears anyway) surface at the connected vent with the fewest visible
>   non-teammates, then in place; never steer toward a player while the kill cooldown zeroes the
>   target scores; a teammate is never a witness;
> - entry: vent only when the body in the room is the impostor's OWN victim killed at most 3 ticks
>   ago (removes the 62 entries at a teammate's or an older victim);

The decision memo's further orchestrator rulings: the entry gate is its own field (0.3 item 3);
a recorded value's meaning is frozen once round 1 records, so a revision adds a value such as
`look_and_wait_2` (0.3 item 6); each arm card deletes its own `WAVE_ARMS_PENDING` entries (0.3
item 9); under any active sabotage a neighbour counts as unseen (2.2); the census predicate reads
the policy's own inputs, never engine-truth visibility (0.4). The ruling's "62 entries" is
superseded: the ruled gate removes 103 of 587 pooled entries, 13 of 105 on s9 (0.4, "Entry
gate"). The prototype headline (16/29 to 6/18) is withdrawn as evidence for B1 (2.2).

**What the tree does today** (citations at `e886b663`).

- Priority: `ImpostorPolicy.decide` runs the in-vent exit first
  (`agents/tactical/impostor_policy.py:402-408`), then COVER-or-vent for any body in its room
  (`:413-419`, `_cover_or_vent` `:1293-1321`). It vents whenever a vent is there and no
  non-teammate stands in its own room (`_non_teammate_witness_present` `:1165-1199`); a teammate's
  victim or an old victim triggers it too. The walk-away is `_cover` (`:1323-1338`).
- Exit: `_vent_exit` (`:1340-1385`) keeps body-free connected vents and `_choose_exit_vent`
  (`:1387-1418`) takes the one nearest `targets[0].room`. While cooling down `cooldown_factor`
  (`:1271`) zeroes every score, so the ranking falls back to proximity (`_decision_targets`
  `:1013`): the impostor surfaces next to the nearest crewmate it saw. It never waits: 493 of 512
  pooled exits came one tick after entry (movement memo, Part 1). Every existing exit test uses
  cooldown 0 (`tests/agents/test_impostor_policy.py:1121-1222`, the engineering refuter's finding),
  which is why the steering was never pinned.
- `observed_risk` (`agents/tactical/experimental.py:322-358`) never waits, never checks the room
  left and scores a room it cannot see as 0; its held-out 9p2i exposure moved from 32/53 to 33/61
  (`audits/tactical-gameplay/README.md:139`).
- Sight: an impostor inside a vent keeps its own room plus adjacent rooms, because
  `compute_visibility_for_player` never checks the observer's `in_vent` and the role rule in
  `_resolve_observer_visibility_mode` keeps the impostor's adjacent sight (`engine/visibility.py`);
  lights degrade everyone to the own room. The agent receives no visible-room list
  (`observation/public_map.py:14-32`), so the policy infers the set: own room plus
  `room_neighbors`, or own room alone while `ImpostorPolicy._active_sabotage`
  (`agents/tactical/impostor_policy.py:662`) is true.
- The vent ring: six vents with two links each; only STORAGE-ENGINEERING and LABS-MEDBAY join
  adjacent rooms, so 4 of 12 directed links lead to a room the impostor can see, and from REACTOR
  or ADMIN it sees neither exit (`engine/maps/canonical_1.yaml:229-271`; STORAGE keeps two links on
  purpose, `:220-226`). `wait` is legal inside (`tests/engine/test_rules.py`,
  `test_in_vent_actor_may_only_vent_or_wait`); the kill cooldown of 4 (`canonical_1.yaml:34`) runs
  inside.
- The spine lands the wiring first: both values on `RecordedExperimentConfig` and
  `TacticalExperimentOptions`, the mapping in `_tactical_experiment_options`
  (`orchestrator/game.py:4422-4433`), `has_tactical_changes` (`experiment_config.py:124-134`)
  counting the new field, and a named refusal to build a policy with either value until now.

**The s9 projection the ruling requires** (count-only, first order). Method: the movement memo's
walk (`walk2.py`, its Reproduction section) was re-run at `e886b663` into scratch and is byte
identical to the memo's walk; its witness rebuild matches the engine on 512 of 512 pooled exits.
The memo's classes (`proj.py`, `proj2.py`) score a card-author wrapper that implements the ruled
rule above and the ruled entry gate, holding crew to their recorded positions. So avoided counts
are upper bounds, and a trip inside when a recorded meeting opened may be inside a meeting its own
recorded seen exit caused. `s9` is `replays/samples/9p2i`, 50 games.

| s9, 50 games | trips | seen exits | surface clear | inside at a recorded meeting | forced at the cap |
|---|---:|---:|---:|---:|---:|
| today, both-rooms rule | 85 | 62 | - | - | 0 |
| today, seen from the exit room (what the physical rule leaves) | 85 | 53 | - | - | 0 |
| today, seen only from the room left (the physical rule removes) | 85 | 9 | - | - | 0 |
| ruled wait, exit field only, physical rule | 85 | 7 | 45 | 33 | 8 |
| ruled wait, exit field only, both-rooms rule | 85 | 8 | 44 | 33 | 8 |
| ruled wait and entry gate, physical rule | 76 | 7 | 37 | 32 | 8 |
| hidden travel, cap 4 (the escalation) | 85 | 1 | 50 | 34 | - |

- The 7 seen exits under the physical rule are 5 walk-ins (a crewmate with a lower id entered
  that tick, which no look prevents) and 2 blind surfacings at the cap. 48 of the 53 exit-room
  sightings are avoided; 2 exits unseen today become seen.
- Ticks inside per trip (exit field only): 1 tick 35, 2 ticks 23, 3 ticks 17, 4 ticks 10 (today 1
  tick on 80 of 85). In-place surfacings: 18, and on 6 of them a crewmate walks into the corpse
  room on the next tick before the impostor moves (the near-body cost).
- The entry gate keeps 92 of 105 s9 entries and removes 9 of the 85 exit trips.
- Pooled over the four sets, for scale: 36 seen exits of 426 trips (ruled wait and entry gate,
  physical rule) under the literal fewest-visible key. The orchestrator ruled the cap key on
  2026-09-24, before dispatch (Constraints): at the cap a visibly clear room ranks before a room the
  impostor cannot see, which ranks before a watched room. Under that key the pooled figure is 20
  seen exits (the engineering refuter's projection), and on s9 both keys give 7. Decision memo 2.2's
  "about 20 seen exits" is this ruled key's figure; the memo carries a dated note saying so.
- Reproduction, from the repo root with outputs outside the tree:

```sh
S=/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/cd3daac2-c664-44ef-918c-024def8b33b9/scratchpad
PYTHONPATH=. uv run --frozen python $S/ventopts/walk2.py $S/card_vlw/walk2.json
python3 $S/card_vlw/s9_ruled.py $S/card_vlw/walk2.json   # ruled wait and entry gate, s9 and pooled
python3 $S/refute_vent/r4.py $S/card_vlw/walk2.json      # hidden travel and the stricter wait, s9
```

**What a 50-game record can and cannot resolve.**

- It can read the pre-registered cell "exits seen from the exit room" (decision memo, section 4):
  today 53/85 = 0.62 (Wilson 0.52-0.72). The projection is 7 of 52 surfacings, 0.13 (Wilson
  0.07-0.25). With about 50 surfacings, a realized share near the projection separates the
  "effective" reading (0.30 or less) from "not effective" (0.52 or more); between them reads
  partial.
- It can read the conformance cells, which must be 0 by construction.
- It cannot attribute an outcome to this card alone: the physical rule, the reset and this policy
  share one record. The lab minus-one arms give mechanical attribution only.
- It cannot estimate the near-body cost (6 of 18 projected) or forced exits (8) as rates, cannot
  project kills within 2 ticks of a surfacing, and resolves balance only coarsely (impostor wins
  11/50 today, Wilson 0.13-0.35).
- Meetings opening with an impostor in a vent (29 of 145 today) should rise: 33 of 85 trips are
  projected still inside at a recorded meeting. Under the reset those stays end at the regroup
  with no exit event; play never resumes with an impostor inside.

**Escalation and fallback, named here and built by no card this wave.** If the record reads "not
effective", the escalation is hidden vent travel (option (c) of the movement memo): a new engine
mechanic of about 25 files by the engineering refuter's re-pricing, a new witness-free event type,
the physical witness rule made moot (every exit surfaces where the impostor is), hops capped at 1
or 2 per trip and no maximize-distance-from-body term, per the ruling and the map's intent. It
projects 1 seen exit on s9 and needs its own card and owner ruling. If balance collapses
(impostor win share above 0.60 in the non-gating envelope), the fallback is the status quo:
`target_distance` and `any_body`, adopted nowhere.

**The lab reproduces today.** At `e886b663` the development screen re-runs to the committed rows:
4p1i baseline 6/8 exposure, 22 waits, 48 calls; observed risk 5/8, 25, 48; 9p2i baseline 16/29,
96, 294; observed risk 14/34, 106, 308 (`audits/tactical-gameplay/README.md:81`, `:85`, `:95`,
`:99`; `vent_witness_and_exit.md` section 4). Exit-room-only exposure on 9p2i is 13/29 and 9/34.

## Acceptance

Unless an item names another file, its test lives in `tests/agents/test_vent_look_and_wait.py`
(new, this card only) over hand-built memories on the canonical public map. "Red before" means
the test fails on the tree this card starts from, where building the policy with either new value
raises the spine's named refusal. Each item also asserts the `target_distance` / `any_body`
behaviour it contrasts with, so it proves the defect it claims.

- [x] **A watched exit makes it wait.** In STORAGE_VENT at cooldown 3, with the own victim's body in
  STORAGE and a crewmate sighted this tick in ENGINEERING, `target_distance` surfaces at
  ENGINEERING_VENT, into the crewmate. `look_and_wait` waits. On the next tick, with ENGINEERING
  clear, it surfaces at ENGINEERING_VENT, which has no body and is not the room it fled. Mechanism:
  the all-clear gate. Red before.
- [x] **The blind-exit contrast.** In REACTOR_VENT (neither exit visible) with a crewmate in
  ENGINEERING, `target_distance` surfaces blind at a connected vent; `look_and_wait` waits. With
  every visible room clear it surfaces in place and never at a room it cannot see. Mechanism: the
  candidate set is the current vent plus visible connected vents. Red before.
- [x] **Who counts as a watcher.** A non-teammate in the own room forces a wait, even though the
  physical rule would not make it a witness of a connected exit. A teammate in the own room or a
  neighbour does not: from ADMIN_VENT it surfaces in place, where `target_distance` surfaces at a
  connected vent. A sighting that is not first-hand never counts. Mechanism: fellow ids from `self_state`
  and the observed-provenance filter. Red before.
- [x] **The cap.** With a watcher still in view, inside-counts 1 to 3 wait and count 4 surfaces.
  The key is the ruled one: each candidate (in place, or a connected vent) is classed by the
  impostor's own inferred sight this tick as clear (visible, no non-teammate sighted there), unseen
  (outside the inferred-visible set) or watched (visible, a non-teammate sighted there); clear ranks
  before unseen before watched; within a class, fewer sighted non-teammates first, then a room with
  no body, then a room other than the one fled from, then a connected vent before in place, then
  vent id. Planted: from a vent whose own room is clear while a neighbour is watched and the other
  exit is unseen, it surfaces in place; the literal fewest-visible key would take the unseen exit.
  The fixture is chosen so this pick differs from `target_distance`'s.
  A `meeting_boundary` row inside the streak restarts the count. Perturbed: counting from the entry
  alone fails the restart case. The count comes from memory rows, never from instance state.
- [x] **No steering inside.** Two memories that differ only in target sightings from earlier ticks
  give the same `look_and_wait` intent and different `target_distance` intents. Mechanism: the
  in-vent branch never calls `_scored_targets` or `_decision_targets`. Red before.
- [x] **Sabotage makes neighbours unseen.** Under an active reactor sabotage, with the own room clear
  and a crewmate sighted in a neighbour the engine truly shows, it surfaces in place. The same holds
  under lights. The census predicate from `eval/gameplay_census.py`, fed this surfacing, reads no
  breach; fed a surfacing with the crewmate in the own room instead, it reads one.
- [x] **The sight model is pinned to the engine.** For every canonical room, the inferred-visible
  set equals `engine.visibility.visible_rooms_for_player` for an impostor observer at base
  visibility, and equals the own room under lights. A test may import the engine; the policy may
  not (`lint-imports`). Perturbed: an adjacency fixture with one extra neighbour fails.
- [x] **The entry gate.** Under `own_fresh_kill`, a teammate's victim in a room with a vent and no
  witness makes it walk away (`_cover`), where `any_body` vents. So does an own victim across a
  `meeting_boundary`, and an own victim killed 4 ticks before. An own victim killed 3 ticks before
  vents, and a fresh own kill vents exactly as `any_body` does (the control). A non-teammate in the
  room keeps today's walk-away under both values. The window counts from the engine's kill tick on
  the recorded observation path (temporal observations OFF): the two boundary memories come from
  engine ticks run through the observation service and perception, not hand-typed row ticks.
  Red before.
- [x] **Never stuck, and deterministic** (Hypothesis). Over random in-vent memories (teammate and
  non-teammate sightings across the own room, neighbours and far rooms; bodies; sabotage on or off;
  in-vent streaks of 1 to 6 rows with or without a meeting boundary inside), every intent is `vent`
  or `wait`. At an inside-count of 4 or more it is `vent`. Repeated calls, and permuted
  `room_neighbors` and `vent_graph` listings, give the same intent. Perturbed: a copy with the cap
  check removed fails the property.
- [x] **The default is untouched.** `git diff --stat main...HEAD -- agents/tactical/impostor_policy.py`
  is empty. `TestCommittedCorpusTargetingPins` in `tests/agents/test_impostor_policy.py` passes
  unedited: on s9, 1754 decisions reconstructed, 109 in-vent, 9/232 free kills declined, and 223
  recorded kills reproduced; these are measured at `e886b663` and re-measured at dispatch. The
  `observed_risk` tests in `tests/agents/test_tactical_experiments.py` pass unedited.
  `publish_process_scorecard.py --check` and `publish_gameplay_census.py --check` pass unchanged.
- [x] **Reconstructible from memory.** A fake 9p2i game recorded with both values ON is reconstructed
  by evidence honesty with the recorded policy with 0 decision mismatches (the capability the
  readers card lands); reconstructed with the default policy it shows more than 0. Tests in
  `tests/experiments/test_vent_look_and_wait_game.py` (new, this card only).
- [x] **Wiring and determinism** (same file). `HeadlessGame` built with either value alone builds
  `ExperimentalImpostorPolicy`, and `has_tactical_changes` is true for `own_fresh_kill` alone. The
  fake game recorded twice is byte identical. It loads through the plain `ReplayLoader` with
  `outcome_verified` true, and its tick rows carry both keys. A default config serializes without
  them. The spine's refusal for these two values is deleted; building either value no longer
  raises. Planted: a config with only `vent_entry_policy="own_fresh_kill"` fails the test if the
  default `ImpostorPolicy` is built for it (patched into the factory), and a copy of the second
  recording with one tick row's state hash edited fails the byte comparison.
- [x] **The census reads 0 on a game built with the arms** (same file). A fake 9p2i game on a
  development seed, with both values and the physical rule ON, reads 0 on the three B1 conformance
  cells of `eval/gameplay_census.py`: surfacings before the cap with a non-teammate in the
  inferred-visible set; trips longer than the cap; entries not after the impostor's own fresh kill.
  Their denominators are non-zero (at least one wait, one surfacing, one entry), so the test cannot
  pass vacuously. A perturbed copy of the carrier raises on each cell: one surfacing moved to a
  watched tick, one stay extended past the cap, one entry re-keyed to a teammate's victim. The
  policy's window (3) and cap (4) constants are pinned equal to the census's named constants.
- [x] **The pending guard.** This card deletes exactly its two `WAVE_ARMS_PENDING` entries:
  `vent_exit_policy` `look_and_wait` and `vent_entry_policy` `own_fresh_kill`. Configs carrying
  them validate. The spine's refusal test, parametrized from the mapping's live contents, still
  refuses every value left pending at this card's head (the body-handle and ballot values,
  whichever have not merged), with no edit to `tests/orchestrator/test_experiment_arms.py`.
- [x] **The lab arms.** `candidate_configs()` in `experiments/tactical_gameplay.py` gains
  `vent_physical`, `vent_look_and_wait`, `vent_own_fresh_kill` and `stage_b_full`, plus four
  minus-one arms named after the value they drop: `stage_b_full_minus_look_and_wait`,
  `stage_b_full_minus_own_fresh_kill`, `stage_b_full_minus_physical` and
  `stage_b_full_minus_hub_with_grace`.
  - `stage_b_full` is the round-1 config's fields that act during play: `vent_witness_rule`
    physical, both vent values, `meeting_reset` `hub_with_grace`. The meeting-layer fields do not
    act on fake games, which eject nobody, so the README says they are left out.
  - `measure_replay` gains count-only counters: exit-room exposure (it exists), room-left-only
    exits, in-vent waits, trips by ticks inside, trips reaching the cap, in-place surfacings,
    entries not after an own fresh kill, and meetings opening with an impostor in a vent.
  - `tests/experiments/test_tactical_gameplay.py`'s parametrize gains the eight arms; each
    reconstructs in the API and repeats.
  - Mechanism: a test that each minus-one arm's config differs from `stage_b_full` in exactly the
    field its name drops, set back to its default. Perturbed: a minus-one arm that drops a
    different field, or equals `stage_b_full`, fails it.
- [x] **The two lab walk profiles declare their layers.** Mechanism: the profiles derived from
  `current-report` with `replace` (`experiments/tactical_gameplay.py:199`, `:363`) set the spine's
  `threaded_layers` explicitly, never inheriting `current-report`'s, to the layers the lab reads,
  named in Results; the spine names this card as their owner. Proof, per profile: it reads the
  spine's fake full-config recording (a copy of a fake recording on today's arms, its tick rows and
  footer rewritten to carry every wave field at its ON value, with the pending set patched empty)
  with every hash verified, and it refuses a planted unknown field (a stand-in added to the config
  model and `FIELD_LAYER` in a layer the profile does not declare) by name before its first
  advance. Perturbed: a profile with its layer declaration removed refuses the full-config copy.
- [x] **The lab rows.** At this card's final head, which the harness's runtime fingerprint freezes
  for the run, the development split only (seeds 1000-1007, both rosters, the lab's $0 limits)
  runs baseline, `vent_risk` and the eight arms, committed as
  `audits/tactical-gameplay/stage-b-development.json`. The record card re-runs the same arms at its
  frozen HEAD and adds its rows beside these, never replacing them. A new dated section of
  `audits/tactical-gameplay/README.md`, after the development tables, reports count-only rows with
  the runtime fingerprint and git head. The re-run baseline and `vent_risk` rows equal the committed
  rows at `:81`, `:85`, `:95` and `:99` in waits, exposure and calls; a mismatch means a default or
  `observed_risk` path moved and stops the card. A new dated "Decisions and limits" row says
  `observed_risk` loses its mechanism when `look_and_wait` is adopted and its rows stay. The
  existing "Vent choice" row and every earlier row stay unedited. The held-out split is not run.
- [x] **The projection is re-measured at dispatch.** The three commands in Evidence, re-run at the
  branch base with outputs outside the tree, reproduce 85, 62, 53 and 9; the ruled rows (7, 45, 33,
  8, and 7, 37, 32, 8); and the gate's 13 of 105. Any drift is recorded in Results with the command.
  If the scratch root is gone, the rule stated here rebuilds the wrapper, and the walk script is
  rewritten from the movement memo's description.
- [x] **Publication neutral.** `git diff --name-only main...HEAD` names no path under `api/`,
  `frontend/`, `replays/` or `tests/fixtures/`, and leaves the featured list untouched. A demo bundle
  built at the base and at the head is byte identical (`diff -r`, Validation). Perturbed: the diff
  check flags a planted `frontend/` path in a scratch branch.
- [x] **The registry row follows the audit bytes.** The `audits/` row of `docs/artifacts.md`
  (`:109`, 26,635,440 tracked bytes / 329 files at `e886b663`) is recomputed with `git ls-files`
  as the last step, after the new section and JSON land and after the final merge of `main`. The offline `scripts/verify_ml_evidence.py` passes. Perturbed: with
  the row left stale, it fails on the byte count.

## Constraints

**Wave and order.** Wave 3.

- Starts once these have merged: the dated direction addendum (the `docs:` commit before wave 1),
  `docs-truth-typed-trigger`, `stage-b-arm-spine`, `gameplay-census` (its B1 cells and named
  constants) and `vent-witness-physical` (the physical rule the lab arms and the end-to-end test
  set).
- Merges after `stage-b-readers`: the reconstruction item needs its recorded-policy
  reconstruction. If readers is still open when this card starts, every other item proceeds, and
  the branch merges `main` before that item runs.
- Merges before `report-body-handle` (pending removals land in the order B0, B1, B4, B6) and
  before `meeting-reset-coherence` (it follows this card in `audits/tactical-gameplay/README.md`).
  It runs in parallel with both, which touch this card's files only as the table below states.

**Shared files, one writer at a time** (decision memo 3.2):

| file | writers in order | this card's region |
|---|---|---|
| `agents/tactical/experimental.py` | spine, then this card | the in-vent and entry branches of `ExperimentalImpostorPolicy.decide`, their private helpers, and deleting the spine's not-built refusal for the two values |
| `experiments/tactical_gameplay.py` | spine, then this card | `candidate_configs`, the `measure_replay` counters and the two lab profiles' layers |
| `orchestrator/experiment_config.py` | spine owns it; declared exception | deleting its two `WAVE_ARMS_PENDING` entries, nothing else |
| `audits/tactical-gameplay/README.md` | this card, then `meeting-reset-coherence` | a new dated development section and a new dated decisions row |
| `docs/artifacts.md` | A1, readers, record plumbing, this card, the meeting reset, the record card, in merge order, each writing only its own row (3.2 as amended for this card set) | the `audits/` row only, recomputed with `git ls-files` after merging `main`; recorded under Decisions |

Single writer this wave: `tests/agents/test_vent_look_and_wait.py`,
`tests/experiments/test_vent_look_and_wait_game.py`,
`audits/tactical-gameplay/stage-b-development.json`, and the parametrize of
`tests/experiments/test_tactical_gameplay.py`. This card does not touch
`agents/tactical/impostor_policy.py`, `orchestrator/game.py`, `engine/`, `observation/`, `meetings/`,
`eval/` (the census belongs to its own card), `api/`, `frontend/`, `replays/`, `tests/fixtures/`,
the prompt set, `docs/architecture.md`, `docs/glossary.md`, `DESIGN.md` or `tasks/phase-11.md`
(historical; the reversal lives in the direction addendum).

**The partial-record principle binds this card.**

- Only `replays/samples/9p2i` seeds 0-49 are ever re-recorded, and only into the candidate
  directory, by the record card.
- Every switch is a `RecordedExperimentConfig` field, default OFF and omitted from the payload at
  its default. No `AILIBI_*` lever and no environment switch is added.
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying byte
  identically. There is no registry prompt bump; this card changes no prompt byte.
- Role-correctness is reported and never a gate.
- Nothing pushes an agent toward the correct answer: this card changes only how an impostor
  hides.
- The meeting layer labels and never rewrites; this card touches no meeting code.

**The cap key was ruled by the orchestrator on 2026-09-24, under the owner's delegation, before
dispatch.** The vent ruling's sentence "surface at the connected vent with the fewest visible
non-teammates, then in place" is read with a room the impostor cannot see ranked AFTER a visibly
clear room and BEFORE a watched room (the Acceptance cap item states the full key). Reason: a look
before leaving prefers a room seen to be clear over a blind gamble; the literal reading, under
which an unseen room counts as zero watchers and a connected vent beats in place, would take the
blind exit. On s9 both readings give 7 seen exits; pooled the ruled key gives 20 against 36 for the
literal one. After round 1 records, the value's meaning is frozen. The fresh-kill window of 3 and
the cap of 4 are named constants documented as the values' frozen meaning.

**Delivery.**

- Branch `work/vent-look-and-wait` from `main`; one PR into `main`, merged as a merge commit or a
  fast-forward, never squashed. Never amend a pushed commit; merge `main` in, never rebase.
- Every commit body ends with the trailer `Card: tasks/work/vent-look-and-wait.md`, immediately
  followed by the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs).
- The PR body has the sections Summary, Definition of done, Decisions and Questions
  (`docs/agent-procedures.md`, "PR description"), ending with the Claude Code attribution line.
- Agents post no PR comments. Every merge is the owner's.
- Fake provider and scripted clients only: no live call, no `.env`, no held-out prompt band, no ML
  fit or refit (ruling 12), no tour or featured-list change (ruling 11), no scorecard cell.

**Non-goals.** This card adds no hidden travel, engine change, new event type or visibility change.
It makes no template or prompt change and does not retire `observed_risk` (that happens at
adoption). It adds no refusal of other arms: `self_report` and contextual self-report stay
independent, because the entry gate replaces only a vent entry, after the self-report branches.
It makes no claim about the unadopted temporal observation path (the round records the bare
slate). It asks for no user-facing copy: no viewer label (the spine owns them), no model speech.
The README section names arms by recorded value and explains "look and wait" in plain words.

## Expected scope

- `agents/tactical/experimental.py` (the exit, the entry gate, the inferred-visible set, the
  inside-count from memory, the deleted not-built refusal); `orchestrator/experiment_config.py`
  (two pending entries); `experiments/tactical_gameplay.py` (eight arms, the counters, the two lab
  profiles' layers).
- Tests: `tests/agents/test_vent_look_and_wait.py` and
  `tests/experiments/test_vent_look_and_wait_game.py` (both new), and the parametrize of
  `tests/experiments/test_tactical_gameplay.py`.
- `audits/tactical-gameplay/README.md` (a section and a row), the new
  `audits/tactical-gameplay/stage-b-development.json`, and the `audits/` row of `docs/artifacts.md`.
- The card (Results at delivery) and `tasks/README.md`'s derived inventory sentence on a Status
  change. Follow-through inside these files is permitted and recorded under Decisions; anything
  else waits for its owning card or the owner.

## Record impact

- **Default OFF; nothing recorded moves.** No byte under `replays/` changes, and neither does
  `docs/process-scorecard.*`, `docs/gameplay-census.*`, a MANIFEST, a report gz, the golden, a
  prompt stamp or the c9 refit pins. The MANIFEST `policy` column stays `fsm-default`; a recorded
  tactical arm means `ExperimentalImpostorPolicy` (the spine's docstring rule).
- **What does move:** the lab audit gains a section, a JSON and a decisions row (class (b)). The
  `docs/artifacts.md` `audits/` row follows them.
- **When it records:** round 1 (`stage-b-record-r1`) is the first recording with these values ON,
  into `replays/candidates/stage-b-r1/9p2i/`. From then, `look_and_wait` and `own_fresh_kill` mean
  exactly what this card built.
- **At adoption:** a missing key keeps meaning `target_distance` and `any_body` for as long as a
  committed recording reads it; `observed_risk` retires with its rows kept. Adoption is the owner's
  decision after the round-1 assessment.
- **Balance:** the shift is accepted by the owner (the record paragraph, verbatim in Evidence).
  The impostor-win envelope is reported, non-gating, and names the status-quo fallback.
- **Publication:** a push to `main` republishes the demo bundle (`.github/workflows/pages.yml`).
  This card touches none of its inputs (`api/`, `frontend/`, `replays/samples`, the featured list),
  and the bundle rebuild in Validation proves it byte identical. Because neither `api/` nor
  `frontend/` changes, the frontend leg of `check.sh` suffices and no e2e run is needed.
- **Evaluation:** the lab rows measure mechanics on fake games and establish no reasoning quality.
  The 50-game record is the only balance measurement.

## Validation

In a clean worktree, from a bare shell with no `AILIBI_*` export, at the PR head:

```sh
bash scripts/check.sh; echo "check.sh exit=$?"          # the real exit code goes into Results
uv run pytest -m campaign                                  # the c9 refit pins' campaign half
uv run pytest tests/agents/test_vent_look_and_wait.py tests/experiments/test_vent_look_and_wait_game.py \
  tests/experiments/test_tactical_gameplay.py tests/agents/test_tactical_experiments.py \
  tests/agents/test_impostor_policy.py tests/orchestrator tests/meetings/test_prompt_byte_golden.py
for d in replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i; do
  bash scripts/verify_samples.sh "$d"                     # once per set directory
  uv run python scripts/build_sample_report.py --sample-dir "$d" --check
done
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py               # offline; never --complete
git diff --name-only main...HEAD                          # the publication-neutral scope check
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head   # and at main: <scratch>/bundle-base
diff -r <scratch>/bundle-base <scratch>/bundle-head
```

The lab rows are produced once, at the final head, into the committed path, and the harness refuses
to overwrite it:

```sh
uv run python -m experiments.tactical_gameplay --split development --arms baseline vent_risk \
  vent_physical vent_look_and_wait vent_own_fresh_kill stage_b_full \
  stage_b_full_minus_look_and_wait stage_b_full_minus_own_fresh_kill \
  stage_b_full_minus_physical stage_b_full_minus_hub_with_grace \
  --output audits/tactical-gameplay/stage-b-development.json
```

## Results

Implemented on `work/vent-look-and-wait` from `f98bfae9` (the wave-3 base: B0 #485, the readers
#486 and the record plumbing #487 merged). Commits: `5b6f9db3` (the policy, the two pending
removals, the emptied refusal, the unit tests and two follow-through test files), `74a205b6` (the
lab arms, counters and profiles, the game-level tests, the lab parametrize and three pinned lab
tests), `90d5f335` (the mutation pass's fixes: two redundant clauses removed, two lab predicates
made pure helpers with planted cases, more planted policy cases), `dec380e0` (the committed lab
rows, the README section and decisions row, the `audits/` registry row, the arm page's pending
sentence, one stale test docstring) and the Results commit. The validation below ran at
`dec380e0` in a bare shell (no `AILIBI_*` export) unless a line names another commit; the Results
commit changes only this card and `tasks/README.md`.

**Sections relied on.** `docs/architecture.md`: "Enforced boundaries" (the policy imports no
engine module; the tests do, which `lint-imports` allows), "Determinism and the substrate
ladder" (committed recordings stay byte-identical) and "Explicit cleanup experiments", which links
the arm page `docs/experiment-arms.md` (the tactical layer, omit-at-default, the pending guard,
walk-profile layers, frozen values). The decision memo `tasks/decision-2026-09-24-stage-b-wave.md`:
0.3 items 3, 6 and 9, 0.4 (the entry-gate count and the policy-side sight), section 1 (adoption
item 4, `observed_risk`), 2.2, 3.2 (the file map) and the card-7 brief in 3.4.
`tasks/investigations-2026-09-24/orchestrator-vent-ruling.md` and `vent_movement_options.md`. The
dated 2026-09-24 addendum to `tasks/direction-2026-09-19-process-over-outcome.md`, which records
the reversal of `tasks/phase-11.md:65-68`.

**What was built.**
- `agents/tactical/experimental.py`, `ExperimentalImpostorPolicy` only:
  - `vent_exit_policy = "look_and_wait"` is decided before the anchor, so nothing inside a vent
    calls `_scored_targets` or `_decision_targets`. `inferred_visible_rooms` is the own room and
    its map neighbours, or the own room alone while the freshest `global_status` reports any
    sabotage. A watcher is a first-hand (`observed`) `saw_player` at the latest tick, in that set,
    naming neither the impostor nor a fellow id from `self_state`. Before the cap: any watcher
    means wait; otherwise surface at the current vent or a visible connected vent, keyed (body
    there, the room fled from, vent id). At `IN_VENT_CAP_TICKS = 4`: surface by the ruled cap key,
    clear before unseen before watched, then fewer watchers, no body, not the fled room, connected
    before in place, vent id; body knowledge is limited to the inferred sight. The count is the
    trailing run of in-vent `self_state` rows back to the last `meeting_boundary` row, so it
    equals the census's ticks inside at the exit tick.
  - `vent_entry_policy = "own_fresh_kill"` replaces the cover vent with the default cover's move
    unless an `own_kill` row names a victim whose body is sighted in the own room this tick, in
    that room, with kill tick (row tick less one) at most `FRESH_KILL_WINDOW_TICKS = 3` before the
    entry and no `meeting_boundary` at or after the row's tick. An event-time `own_kill` row
    (temporal observations) raises rather than misdate the kill.
  - `UNBUILT_OPTION_VALUES` is now empty; the refusal mechanism stays for the spine's
    pending-equals-unbuilt test (Decision 3).
- `orchestrator/experiment_config.py`: the two `WAVE_ARMS_PENDING` rows deleted, nothing else.
- `experiments/tactical_gameplay.py`: the eight arms (`STAGE_B_FULL_SETTINGS`,
  `STAGE_B_MINUS_ONE`), the count-only counters (room-left-only exits, in-vent waits, trips by
  ticks inside, trips at the cap, in-place exits, entries not after an own fresh kill, meetings
  opening with an impostor in a vent) on the census's definitions, and the two walk profiles as
  named constants declaring `LAB_THREADED_LAYERS = {orchestrator, tactical, meeting}`: the lab
  counts recorded actions, engine events and applied meeting results under verified hashes and
  re-decides nothing, so every count keeps its meaning under any value in those layers.
  `measure_identity_effects` still refuses every experimental recording before it walks.

**Acceptance evidence** (tests in `tests/agents/test_vent_look_and_wait.py`, U, and
`tests/experiments/test_vent_look_and_wait_game.py`, G).
- Watched exit: U `test_a_watched_exit_makes_it_wait_then_it_surfaces_clear`
  (`target_distance` -> ENGINEERING_VENT; wait; next tick ENGINEERING_VENT).
- Blind exit: U `test_the_blind_exit_contrast` (from REACTOR_VENT, `target_distance` surfaces
  blind; `look_and_wait` waits, then with every visible room clear surfaces in place even with
  its own victim underfoot). Red on `target_distance`: with the look-and-wait branch disabled (a copy-edit-restore of
  `agents/tactical/experimental.py`) the test fails at the wait assertion (`'vent' == 'wait'`),
  and passes again once restored.
- Watchers: U `test_a_non_teammate_in_its_own_room_forces_a_wait`,
  `test_a_teammate_is_never_a_watcher` (ADMIN and its three neighbours; `target_distance` ->
  MEDBAY_VENT), `test_the_teammate_list_comes_from_self_state`,
  `test_a_sighting_that_is_not_first_hand_never_counts` (reported, inferred),
  `test_a_sighting_of_itself_is_not_a_watcher`, `test_a_sighting_outside_its_inferred_sight_is_not_read`.
- Cap: U `test_it_waits_before_the_cap_with_a_watcher_in_view[1-3]`,
  `test_at_the_cap_it_surfaces_by_the_ruled_key` (STORAGE clear, ENGINEERING watched, REACTOR
  unseen: in place; the literal key takes REACTOR_VENT; `target_distance` ENGINEERING_VENT), plus
  one planted case per key term (`..._unseen_room_beats_a_watched_one`,
  `..._fewer_watchers_win_within_the_watched_class`, `..._a_clear_room_without_a_body_beats_one_with`,
  `..._a_room_other_than_the_one_fled_wins`, `..._a_connected_vent_in_the_same_room_beats_in_place`,
  `..._two_unseen_rooms_fall_to_the_vent_id`; the fled-room, in-place and count terms use a small
  hand-built map because on the canonical map every vent links one unseen room).
  `test_a_meeting_boundary_inside_the_streak_restarts_the_count[1-3]`; perturbed:
  `test_counting_from_the_entry_alone_fails_the_restart_case`; memory, not instance state:
  `test_the_count_comes_from_memory_never_from_instance_state`, `test_an_earlier_trip_does_not_add_to_the_count`.
- No steering: U `test_stale_target_sightings_do_not_steer_the_exit` (same `look_and_wait`
  intent, `target_distance` REACTOR_VENT versus ENGINEERING_VENT) and
  `test_the_in_vent_branch_never_reads_the_kill_ranking` (both ranking methods patched to raise).
- Sabotage: U `test_under_a_sabotage_a_neighbour_counts_as_unseen[reactor|lights]` (in place
  where base visibility waits; the census fold of that surfacing reads 0 of 1, and with the
  crewmate in the own room raises the conformance error) and
  `test_under_a_sabotage_a_body_in_a_neighbour_is_not_read_at_the_cap`.
- Sight model: U `test_the_inferred_sight_equals_the_engines_at_base_and_under_lights` (every
  canonical room, an in-vent impostor observer through `compute_visibility_for_player`; under a
  reactor sabotage the inference is a strict subset); perturbed:
  `test_an_adjacency_with_one_extra_neighbour_fails_the_pin` returns `["STORAGE/None"]`.
- Entry gate: U teammate's victim, fresh control, across a meeting, a kill on the trigger tick
  (perceived on the resume tick, after the boundary), witness under both values, wrong room,
  victim's body next door, other body here, malformed rows, event-time row; the window through the
  engine: `test_the_fresh_kill_window_counts_from_the_engines_kill_tick` runs a kill through
  `advance_tick`, `ObservationService.build_packet` and `ingest_packet` and asserts a vent at kill
  ages 1-3 and the walk-away at age 4, where `any_body` vents at every age.
- Never stuck: U `test_it_is_never_stuck_and_always_deterministic` (`settings(deadline=None,
  max_examples=300)`): every intent is `vent` or `wait`; at a count of
  4 or more it is `vent`; before the cap it vents exactly when no non-teammate is sighted in the
  inferred sight, and only into a room in that sight; repeat calls and a rotated, reversed
  `room_neighbors`/`vent_graph` give the same intent. Perturbed:
  `test_a_policy_without_the_cap_fails_the_property`.
- Default untouched: `git diff --stat main...HEAD -- agents/tactical/impostor_policy.py` prints
  nothing; `tests/agents/test_impostor_policy.py` and `tests/agents/test_tactical_experiments.py`
  are unedited (`git diff --numstat` empty) and pass, `TestCommittedCorpusTargetingPins` included
  (1754 decisions, 109 in-vent, 9/232 declined, 223 kills reproduced, its own pins). Scorecard
  and census `--check` pass.
- Reconstructible: G `test_honesty_reconstructs_the_recorded_policy_with_no_mismatch`. On the
  seed-1003 recording (count-only, scratch script `b1_numbers.py`): recorded-arm fold 44 decisions,
  10 in-vent, 0 mismatches; the default policy 44, 10, 11 mismatches.
- Wiring: G `test_either_value_alone_builds_the_experimental_impostor[2]`, planted
  `test_a_config_whose_entry_value_builds_the_default_policy_fails_the_wiring` (the tactical
  layer blind to `vent_entry_policy`: the factory builds `ImpostorPolicy` and the check fails),
  `test_both_values_build_and_validate_with_no_refusal`,
  `test_the_b1_recording_repeats_byte_for_byte_and_loads_verified` (with the edited-hash copy),
  `test_a_default_config_serializes_without_the_new_key`.
- Census: G `test_the_census_reads_zero_on_the_b1_cells`: entries 0/4, surfacings before the cap
  in view 0/3, trips longer than the cap 0/2 (forced surfacings 1/3, room-left-only 0/3); the three
  perturbed carriers raise (`..._a_surfacing_moved_to_a_watched_tick_breaches`,
  `..._a_stay_extended_past_the_cap_breaches`, `..._an_entry_rekeyed_to_a_teammates_victim_breaches`);
  U `test_the_policys_window_and_cap_are_the_censuss`.
- Pending guard: the two rows deleted; `_WAVE_CONFIG`-style configs with both values validate.
  The spine's refusal tests (`test_validation_refuses_a_pending_value` and its siblings,
  parametrized from the live mapping) are unedited and now run on the three values left
  (report_body_handle_version 1, ballot_kill_row_version 1, impostor_ballot_version 1). See
  Deviation 1 for the one other edit in that file.
- Lab arms: `candidate_configs()` holds 17 arms; G `test_the_eight_arms_set_what_their_names_say`,
  `test_each_minus_one_arm_drops_exactly_the_field_it_names`, perturbed
  `test_a_minus_one_arm_that_drops_another_field_or_nothing_fails`; counters:
  `test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000|stage_b_full-1005]`,
  `test_an_entry_follows_its_own_fresh_kill_by_the_census_definition[10 cases]`,
  `test_a_living_player_in_a_vent_is_one_the_census_reads`,
  `test_measure_replay_hands_the_entry_check_the_kills_and_meetings_so_far`; the lab
  parametrize gains the eight arms (each reconstructs in the API and repeats).
- Lab profiles: both declare `{orchestrator, tactical, meeting}` (G
  `test_each_lab_profile_is_current_report_plus_its_own_layers`,
  `test_the_lab_profiles_never_inherit_the_current_report_layers` re-executes the module with a
  layerless current-report profile, `test_each_lab_consumer_walks_with_its_profile`); each reads
  the full-config copy (a fake 4p1i recording on physical, regroup and rebuttal, its rows and footer
  rewritten with look_and_wait, own_fresh_kill, the body handle and both ballot values, the
  pending set patched empty) with every hash verified and equal counts; each refuses a stand-in
  field by name before its first advance (engine layer: by the helper; each declared layer:
  once that layer is removed); perturbed: without its declaration each refuses the full-config
  copy with no advance.
- Lab rows: see the dated section of `audits/tactical-gameplay/README.md`. Runtime fingerprint
  `9b7be845343c4af343ed7caeef559b5b8a48657838820be6d05fe90e61e8dbcd`, git head `90d5f335`
  (recomputed at `dec380e0`: equal). 160 games, none aborted. Baseline and `vent_risk` equal the
  committed rows: 4p1i 22, 6/8, 48 and 25, 5/8, 48; 9p2i 96, 16/29, 294 and 106, 14/34, 308 (also
  re-run at the base `f98bfae9` before any change: equal). The README's changes are additions
  only (`git diff --numstat` 123 0). The held-out split was not run.
- Projection: re-measured at `f98bfae9` into scratch (below).
- Publication: `git diff --name-only main...HEAD` names no `api/`, `frontend/`, `replays/` or
  `tests/fixtures/` path; bundles built at the base (a `git archive` of `f98bfae9`, replay mtimes
  set to the worktree's, since the loader's `created_at` is the file mtime) and at the head are
  identical (`diff -r` exit 0). Before the mtime sync the only differences were 14
  `created_at` values in 9 files. Perturbed: the same check on a scratch branch carrying a
  planted `frontend/PLANTED_PROBE.txt` exits 1 and names it (branch deleted afterwards).
- Registry row: `audits/` 26,636,557 bytes / 329 files at `f98bfae9` -> 27,302,756 / 330 with the
  JSON and README staged (`git ls-files audits/`, sizes summed); `verify_ml_evidence.py` passes
  (63 checks: 51 OK, 0 FAIL, 7 ABSENT, 5 INFO); perturbed: the row left stale exits 1 ("promises
  329 files, the index tracks 330"; "promises 26,636,557 tracked bytes, the tracked files contain
  27,302,756 bytes").

**Red before.** On the base tree the two new test modules fail to import (`true_base_red.sh`:
the three production files swapped for `f98bfae9`'s, 2 collection errors, then restored from
copies and compared). With the head code and the spine's refusal planted back (a pytest plugin
restoring both values to `UNBUILT_OPTION_VALUES` and `WAVE_ARMS_PENDING`): U 56 failed, 4 passed
(the sight pin, its perturbation, the unknown-room refusal and the constant pin, which build no
policy), and G fails at collection (its module-level config is refused).

**The projection, re-measured at `f98bfae9`** (outputs in the scratch directory, never the tree):

```sh
S=/private/tmp/claude-501/-Users-danielkeinan-projects-AiLibi/cd3daac2-c664-44ef-918c-024def8b33b9/scratchpad
PYTHONPATH=. uv run --frozen python $S/ventopts/walk2.py $S/vlw-b1-impl/walk2.json
python3 $S/card_vlw/s9_ruled.py $S/vlw-b1-impl/walk2.json
python3 $S/refute_vent/r4.py $S/vlw-b1-impl/walk2.json
```

`walk2.json` is byte-identical to the card's and the memo's walks (sha256 `cff6b3b8...`).
s9: 85 trips, 62 seen under both rooms, 53 from the exit room (so 9 only from the room left);
ruled wait, exit field only: physical 7 seen, 45 clear, 33 inside at a meeting, 8 forced;
both-rooms 8, 44, 33, 8; ruled wait and entry gate, physical: 76 trips, 7, 37, 32, 8; the gate
keeps 92 of 105 entries (removes 13); pooled 103 of 587. Pooled ruled key (blind last at the cap)
20 seen exits, literal key 36; hidden travel on s9, 1 seen. No drift. Hidden travel stays the
priced escalation and the status quo (`target_distance`, `any_body`) the fallback, as Evidence
states.

**Neuter and mutation pass.** One harness (`run_mutants.py`, scratch) applies each edit to a
production file, runs the targeted suites (`tests/agents/test_vent_look_and_wait.py` and
`tests/experiments/test_vent_look_and_wait_game.py`; for the lab also
`tests/experiments/test_tactical_gameplay.py`; for the config also both
`tests/orchestrator/test_experiment_*` files) with `-x -n 4`, restores the file from an in-memory
copy and checks its sha256. Round 1 (at `74a205b6`, 122 mutants: 110 killed) first came back green on 11:
P33 (the gate's `anchor.type == "vent"`), P56 and P68 (the vent-id tie-break), L30 and L47 (the
counters' impostor-role clauses), L39, L40, L42, L43 and L44 (the entry count's killer, room,
upper-bound and meeting clauses and its meeting-tick collection) and L48 (the vent-at-open alive
clause); P43 had an ambiguous anchor. Fixes at `90d5f335`: P33, L30 and L47 were redundant and are
deleted; the entry count and the vent-at-open predicate became pure helpers with planted cases.
Round 2 (125 mutants, every file restored): 122 killed, 3 equivalent.

| id | class | edit | first red test |
| --- | --- | --- | --- |
| P01 | N | fresh-kill window 3 -> 2 | test_the_policys_window_and_cap_are_the_censuss |
| P02 | N | fresh-kill window 3 -> 4 | test_the_policys_window_and_cap_are_the_censuss |
| P03 | N | cap 4 -> 3 | test_it_waits_before_the_cap_with_a_watcher_in_view[3] |
| P04 | N | cap 4 -> 5 | test_the_policys_window_and_cap_are_the_censuss |
| P05 | N | boundary kind renamed | test_a_meeting_boundary_inside_the_streak_restarts_the_count[1] |
| P06 | N | own_kill row lag 1 -> 0 | test_the_fresh_kill_window_counts_from_the_engines_kill_tick |
| P07 | N | event-time key renamed | test_an_event_time_own_kill_row_is_refused |
| P08 | N | look_and_wait back in UNBUILT_OPTION_VALUES | test_a_watched_exit_makes_it_wait_then_it_surfaces_clear |
| P10 | M3 | unknown-room refusal disabled | test_an_unknown_room_has_no_inferred_sight |
| P11 | M5 | unknown-room message room -> constant | test_an_unknown_room_has_no_inferred_sight |
| P12 | M7 | sabotage sight branches swapped | test_at_the_cap_an_unseen_room_beats_a_watched_one |
| P13 | M1 | neighbours dropped from base sight | test_a_clear_connected_room_beats_the_room_it_fled |
| P14 | N | sabotage branch deleted | test_an_adjacency_with_one_extra_neighbour_fails_the_pin |
| P15 | M8 | map neighbours -> canonical literal | test_an_adjacency_with_one_extra_neighbour_fails_the_pin |
| P20 | M1 | watcher kind filter dropped | test_a_teammate_is_never_a_watcher[WEST_HALL] |
| P21 | M1 | provenance filter dropped | test_a_sighting_that_is_not_first_hand_never_counts[reported] |
| P22 | M1 | not-watcher filter dropped | test_a_teammate_is_never_a_watcher[ADMIN] |
| P23 | M1 | visible-room filter dropped | test_a_watched_exit_makes_it_wait_then_it_surfaces_clear |
| P24 | N | watcher count -> 1 | test_at_the_cap_fewer_watchers_win_within_the_watched_class |
| P25 | M4 | observed provenance -> reported | test_a_watched_exit_makes_it_wait_then_it_surfaces_clear |
| P30 | M3 | look_and_wait test inverted | test_a_watched_exit_makes_it_wait_then_it_surfaces_clear |
| P31 | N | in-vent test dropped | test_honesty_reconstructs_the_recorded_policy_with_no_mismatch |
| P32 | M3 | self_state None test inverted | test_memory_the_anchor_refuses_is_refused |
| P37 | M4 | entry tick -> 0 | test_the_fresh_kill_window_counts_from_the_engines_kill_tick |
| P38 | M4 | own room -> STORAGE | test_the_census_reads_zero_on_the_b1_cells |
| P40 | N | cooldown refusal deleted | test_an_in_vent_memory_without_a_cooldown_reading_raises |
| P41 | M3 | no-vent refusal disabled | test_an_in_vent_impostor_in_a_room_with_no_vent_raises |
| P42 | M5 | no-vent message room -> constant | test_an_in_vent_impostor_in_a_room_with_no_vent_raises |
| P44 | N | unmapped-vent refusal deleted | test_a_connected_vent_with_no_room_raises |
| P45 | M5 | unmapped message -> constant | test_a_connected_vent_with_no_room_raises |
| P46 | M4 | sabotage read -> False | test_under_a_sabotage_a_neighbour_counts_as_unseen[reactor] |
| P47 | M1 | fellow impostors dropped from not-watchers | test_a_teammate_is_never_a_watcher[WEST_HALL] |
| P48 | M1 | self dropped from not-watchers | test_a_sighting_of_itself_is_not_a_watcher |
| P49 | M1 | bodies not limited to sight | test_under_a_sabotage_a_body_in_a_neighbour_is_not_read_at_the_cap |
| P50 | M3 | cap >= -> > | test_the_count_comes_from_memory_never_from_instance_state |
| P51 | M4 | fled room -> STORAGE | test_at_the_cap_a_room_other_than_the_one_fled_wins |
| P52 | M7 | wait branch inverted | test_a_watched_exit_makes_it_wait_then_it_surfaces_clear |
| P53 | M1 | blind connected vents made candidates | test_the_blind_exit_contrast |
| P54 | M6 | clear key: body term dropped | test_a_clear_room_with_a_body_loses_to_one_without |
| P55 | M6 | clear key: fled term dropped | test_a_clear_connected_room_beats_the_room_it_fled |
| P56 | M6 | clear key: vent id dropped | equivalent: candidates are the current vent then sorted connected vents, and the current vent is its room's smallest id, so the first minimum found is the smallest id |
| P57 | M1 | in place dropped from candidates | test_a_clear_room_with_a_body_loses_to_one_without |
| P60 | M7 | clear and unseen classes swapped | test_at_the_cap_a_clear_room_without_a_body_beats_one_with |
| P61 | N | watched class -> 0 | test_under_a_sabotage_a_body_in_a_neighbour_is_not_read_at_the_cap |
| P62 | M3 | visible test inverted | test_at_the_cap_it_surfaces_by_the_ruled_key |
| P63 | M4 | sighted count -> 0 | test_under_a_sabotage_a_body_in_a_neighbour_is_not_read_at_the_cap |
| P64 | M6 | cap key: count term dropped | test_at_the_cap_fewer_watchers_win_within_the_watched_class |
| P65 | M6 | cap key: body term dropped | test_at_the_cap_a_clear_room_without_a_body_beats_one_with |
| P66 | M6 | cap key: fled term dropped | test_at_the_cap_a_room_other_than_the_one_fled_wins |
| P67 | M6 | cap key: in-place term dropped | test_at_the_cap_a_connected_vent_in_the_same_room_beats_in_place |
| P68 | M6 | cap key: vent id dropped | equivalent: same as P56 for the cap candidates |
| P69 | M6 | cap key: class term dropped | test_at_the_cap_a_clear_room_without_a_body_beats_one_with |
| P70 | M1 | in place dropped at the cap | test_at_the_cap_a_clear_room_without_a_body_beats_one_with |
| P80 | M1 | boundary stop dropped | test_a_meeting_boundary_inside_the_streak_restarts_the_count[1] |
| P81 | M1 | self_state filter dropped | test_at_the_cap_it_surfaces_by_the_ruled_key |
| P82 | M7 | out-of-vent row: break -> continue | test_an_earlier_trip_does_not_add_to_the_count |
| P83 | N | count + 1 | test_a_meeting_boundary_inside_the_streak_restarts_the_count[1] |
| P90 | M1 | boundary max over every row | test_a_fresh_own_kill_vents_exactly_as_any_body_does |
| P91 | M1 | victims not limited to own room | test_an_own_victim_sighted_in_a_neighbour_is_not_this_body |
| P92 | M4 | victim room -> STORAGE | test_the_census_reads_zero_on_the_b1_cells |
| P93 | M1 | own_kill kind filter dropped | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| P94 | N | event-time refusal disabled | test_an_event_time_own_kill_row_is_refused |
| P95 | M1 | malformed test: room clause dropped | test_a_malformed_own_kill_row_raises[payload1] |
| P96 | M1 | malformed test: victim clause dropped | test_a_malformed_own_kill_row_raises[payload0] |
| P97 | M5 | malformed message payload -> constant | test_a_malformed_own_kill_row_raises[payload0] |
| P98 | M4 | kill tick -> 0 | test_a_fresh_own_kill_vents_exactly_as_any_body_does |
| P99 | M3 | window > -> >= | test_the_fresh_kill_window_counts_from_the_engines_kill_tick |
| PA0 | M3 | boundary >= -> > | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| PA1 | M3 | boundary test -> is None | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| PA2 | M1 | kill-room clause dropped | test_an_own_kill_row_in_another_room_is_not_this_body |
| PA3 | M1 | victim clause dropped | test_an_own_victim_whose_body_is_not_here_is_not_this_body |
| PA4 | N | fresh match returns False | test_a_fresh_own_kill_vents_exactly_as_any_body_does |
| PA5 | M4 | own_kill room -> STORAGE | test_an_own_kill_row_in_another_room_is_not_this_body |
| C01 | N | vent_exit_policy back in WAVE_ARMS_PENDING | G at collection (its B1 config is refused) |
| C02 | N | vent_entry_policy back in WAVE_ARMS_PENDING | G at collection (its B1 config is refused) |
| L01 | M6 | orchestrator dropped from LAB_THREADED_LAYERS | test_each_lab_profile_is_current_report_plus_its_own_layers[tactical-mechanisms] |
| L02 | M6 | tactical dropped | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L03 | M6 | meeting dropped | test_each_lab_profile_is_current_report_plus_its_own_layers[tactical-mechanisms] |
| L04 | M5 | seat-effects profile renamed | test_each_lab_profile_is_current_report_plus_its_own_layers[tactical-seat-effects] |
| L05 | N | seat-effects layers inherited | test_the_lab_profiles_never_inherit_the_current_report_layers |
| L06 | N | mechanisms layers inherited | test_the_lab_profiles_never_inherit_the_current_report_layers |
| L07 | M5 | mechanisms profile renamed | test_each_lab_profile_is_current_report_plus_its_own_layers[tactical-mechanisms] |
| L08 | M2 | identity walk -> mechanisms profile | test_each_lab_consumer_walks_with_its_profile |
| L09 | M2 | mechanisms walk -> seat-effects profile | test_without_its_declaration_a_lab_profile_refuses_the_full_config_copy[tactical-mechanisms] |
| L10 | N | physical dropped from stage_b_full | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L11 | N | look_and_wait dropped from stage_b_full | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L12 | N | own_fresh_kill dropped from stage_b_full | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L13 | N | regroup dropped from stage_b_full | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L14 | N | minus-look arm drops the entry field | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L15 | N | minus-own arm drops the exit field | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L16 | N | minus-physical arm drops the reset | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L17 | N | minus-regroup arm drops the rule | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L18 | N | vent_physical -> default | test_the_eight_arms_set_what_their_names_say |
| L19 | N | vent_look_and_wait -> observed_risk | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L20 | N | vent_own_fresh_kill -> default | test_the_eight_arms_set_what_their_names_say |
| L21 | N | minus arms keep the value | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L22 | M1 | one minus arm dropped | test_each_minus_one_arm_drops_exactly_the_field_it_names |
| L33 | N | kills never collected | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L34 | M1 | room-left-only -> any source sighting | test_the_lab_counters_agree_with_the_census[stage_b_full-1005] |
| L35 | M4 | ticks inside -> 1 | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L36 | M3 | cap >= -> > | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L37 | M3 | in-place == inverted | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L38 | M4 | trip anchor -> 0 | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L44 | N | meeting ticks never collected | test_measure_replay_hands_the_entry_check_the_kills_and_meetings_so_far |
| L45 | N | trip anchor not moved at a meeting | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L49 | M4 | ticks key -> constant | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| P34 | M4 | entry-policy test -> True | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| P35 | N | fresh-kill test inverted | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| P36 | N | gate returns the anchor | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| P39 | M3 | entry-policy test inverted | test_a_kill_on_a_meeting_trigger_tick_is_across_that_meeting |
| P43 | M1 | sorted() dropped on connected vents | equivalent: both keys end in the vent id, so min() does not depend on the candidates' order |
| L31 | M4 | vent-wait kind test -> True | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L32 | N | vent-wait in_vent clause dropped | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L39 | M1 | entry check: killer clause dropped | test_an_entry_follows_its_own_fresh_kill_by_the_census_definition[kill4-meetings4-False] |
| L40 | M1 | entry check: room clause dropped | test_an_entry_follows_its_own_fresh_kill_by_the_census_definition[kill5-meetings5-False] |
| L41 | M1 | entry check: window floor dropped | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L42 | M3 | entry check: < -> <= | test_an_entry_follows_its_own_fresh_kill_by_the_census_definition[kill3-meetings3-False] |
| L43 | M1 | entry check: meeting clause dropped | test_an_entry_follows_its_own_fresh_kill_by_the_census_definition[kill6-meetings6-False] |
| L51 | M3 | entry check: meeting <= -> < | test_an_entry_follows_its_own_fresh_kill_by_the_census_definition[kill6-meetings6-False] |
| L46 | M1 | in_vent clause dropped | test_a_living_player_in_a_vent_is_one_the_census_reads |
| L48 | M1 | alive clause dropped | test_a_living_player_in_a_vent_is_one_the_census_reads |
| L52 | M4 | entry check gets no kills | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L53 | M4 | entry check gets no meetings | test_measure_replay_hands_the_entry_check_the_kills_and_meetings_so_far |
| L54 | N | entry count inverted | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |
| L55 | N | vent-at-open count deleted | test_the_lab_counters_agree_with_the_census[vent_look_and_wait-1000] |

Classes: N neuters an added line, row or argument; M1-M8 are the eight bounded operator classes
(drop a filter or wrapper; swap a collection; a comparison to a None test or its inverse; a
role, kind, room or tick read to a constant; a message argument to a constant; drop a tuple
member; swap adjacent branches; a loaded source to its canonical literal). No other class was run.

**Validation** (at `dec380e0`, exit codes captured directly):

```sh
bash scripts/check.sh; echo "check.sh exit=$?"   # check.sh exit=0: ruff, format, lint-imports, task docs,
                                                 # prompts, mypy; pytest 9394 passed, 20 skipped, 3 xfailed;
                                                 # frontend lint, tsc, vitest 559 passed, build
uv run pytest -m campaign                        # 336 passed, 9417 deselected
uv run pytest -n 6 --dist loadfile <the card's targeted list>   # 1018 passed, 3 xfailed
bash scripts/verify_samples.sh <set>             # samples/9p2i 50, samples/4p1i 50, ml_corpus/9p2i 150,
                                                 # ml_corpus/4p1i 50: all verified clean
uv run python scripts/build_sample_report.py --sample-dir <set> --check   # all four consistent
uv run python scripts/publish_process_scorecard.py --check   # consistent
uv run python scripts/publish_gameplay_census.py --check     # consistent
uv run python scripts/check_doc_facts.py                     # exit 0
uv run python scripts/validate_task_docs.py                  # exit 0 (390 phase tasks, 88 work cards)
uv run python scripts/verify_ml_evidence.py                  # exit 0: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO
git diff --name-only main...HEAD                             # 13 paths, none under api/, frontend/,
                                                             # replays/ or tests/fixtures/
```

Every exit code was written by the script itself right after each command (`validation.sh`,
scratch). On the Results commit `validate_task_docs.py` and `check_doc_facts.py` were re-run
(exit 0); `bash scripts/check.sh` at the pushed head is re-run and its exit code is recorded in the
pull request.

**Decisions.**
1. The cap key is the one ruled on 2026-09-24. Within the pre-cap clear case the key is (body,
   fled room, vent id); since an impostor never changes vents without surfacing, the fled room is
   the vent's own room, so a visible clear connected room wins unless only it holds a body.
2. Body knowledge at the cap is limited to the inferred sight, like the watchers: under a reactor
   sabotage a body the engine still shows next door is not read.
3. `UNBUILT_OPTION_VALUES` and its refusal stay, empty: `tests/orchestrator/test_experiment_arms.py`
   (which this card was not to edit for the refusal tests) imports it for the spine's
   pending-equals-unbuilt equality, and the card that deletes `WAVE_ARMS_PENDING` deletes it with
   that test. The two refusal tests in `tests/orchestrator/test_experiment_config.py` and the two in
   `tests/eval/test_recorded_arm_readers.py` now plant the spine's two values back, keeping each
   test's claim (the guard refuses a listed value; a walk hands the recorded value to the builder).
4. The own-fresh-kill gate refuses an event-time `own_kill` row: that path dates the row at the
   kill tick, so the snapshot lag would misdate it. The round records temporal observations OFF.
5. The lab profiles declare all three declarable layers, so an undeclared layer is proved on a
   copy of each profile with one layer removed; the engine layer is the helper's.
6. `stage_b_full` leaves out the round-1 rebuttal, body-handle and ballot fields (none acts on a
   fake game's play).
7. The registry row was recomputed with `git ls-files` after the section and JSON were staged, at
   `dec380e0`; `main` had not moved when the branch was pushed.

**Deviations.**
1. Follow-through outside Expected scope, each forced by an acceptance item:
   `tests/orchestrator/test_experiment_config.py` (the two unbuilt-refusal tests plant the values;
   the lab count 9 -> 17; the wave-settings test pins the nine pre-wave arms by name and
   `stage_b_full`'s three wave settings; one test renamed from "unbuilt" to "look_and_wait"),
   `tests/eval/test_recorded_arm_readers.py` (two refusal-reaching tests plant the values),
   `tests/orchestrator/test_experiment_arms.py` (`test_the_lab_candidates_are_all_arms_that_exist_today`
   asserted no lab arm dumps a Stage-B field, which the lab-arms item makes false; it now asserts no
   lab arm carries a pending value; and its module docstring no longer says no arm behaviour
   exists; the pending-guard refusal tests are unedited), and `docs/experiment-arms.md` (the
   pending guard's list). No test was skipped, weakened or deleted.
2. The Evidence's memo paths under `~/.claude/...` are read from `tasks/investigations-2026-09-24/`.

**Limitations.**
- The projection is first order: crew hold their recorded positions, so avoided counts are upper
  bounds, and it does not model the lights refinement.
- The lab rows are fake-game mechanics: fake meetings eject nobody, so impostors win almost every
  9p2i game and no balance reading is possible; the 50-game record is the only balance measurement.
- `look_and_wait` alone (with `any_body` entries) re-enters the vent after surfacing in place beside
  a body; the round records both values together, where the entry gate removes that loop.
- No claim about the unadopted temporal observation path; its event-time own-kill rows raise.
- The bundle comparison was built on macOS.
