# B1: impostors look before leaving a vent and vent only after their own fresh kill

**Status:** ready

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

- [ ] **A watched exit makes it wait.** In STORAGE_VENT at cooldown 3, with the own victim's body in
  STORAGE and a crewmate sighted this tick in ENGINEERING, `target_distance` surfaces at
  ENGINEERING_VENT, into the crewmate. `look_and_wait` waits. On the next tick, with ENGINEERING
  clear, it surfaces at ENGINEERING_VENT, which has no body and is not the room it fled. Mechanism:
  the all-clear gate. Red before.
- [ ] **The blind-exit contrast.** In REACTOR_VENT (neither exit visible) with a crewmate in
  ENGINEERING, `target_distance` surfaces blind at a connected vent; `look_and_wait` waits. With
  every visible room clear it surfaces in place and never at a room it cannot see. Mechanism: the
  candidate set is the current vent plus visible connected vents. Red before.
- [ ] **Who counts as a watcher.** A non-teammate in the own room forces a wait, even though the
  physical rule would not make it a witness of a connected exit. A teammate in the own room or a
  neighbour does not: from ADMIN_VENT it surfaces in place, where `target_distance` surfaces at a
  connected vent. A sighting that is not first-hand never counts. Mechanism: fellow ids from `self_state`
  and the observed-provenance filter. Red before.
- [ ] **The cap.** With a watcher still in view, inside-counts 1 to 3 wait and count 4 surfaces.
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
- [ ] **No steering inside.** Two memories that differ only in target sightings from earlier ticks
  give the same `look_and_wait` intent and different `target_distance` intents. Mechanism: the
  in-vent branch never calls `_scored_targets` or `_decision_targets`. Red before.
- [ ] **Sabotage makes neighbours unseen.** Under an active reactor sabotage, with the own room clear
  and a crewmate sighted in a neighbour the engine truly shows, it surfaces in place. The same holds
  under lights. The census predicate from `eval/gameplay_census.py`, fed this surfacing, reads no
  breach; fed a surfacing with the crewmate in the own room instead, it reads one.
- [ ] **The sight model is pinned to the engine.** For every canonical room, the inferred-visible
  set equals `engine.visibility.visible_rooms_for_player` for an impostor observer at base
  visibility, and equals the own room under lights. A test may import the engine; the policy may
  not (`lint-imports`). Perturbed: an adjacency fixture with one extra neighbour fails.
- [ ] **The entry gate.** Under `own_fresh_kill`, a teammate's victim in a room with a vent and no
  witness makes it walk away (`_cover`), where `any_body` vents. So does an own victim across a
  `meeting_boundary`, and an own victim killed 4 ticks before. An own victim killed 3 ticks before
  vents, and a fresh own kill vents exactly as `any_body` does (the control). A non-teammate in the
  room keeps today's walk-away under both values. The window counts from the engine's kill tick on
  the recorded observation path (temporal observations OFF): the two boundary memories come from
  engine ticks run through the observation service and perception, not hand-typed row ticks.
  Red before.
- [ ] **Never stuck, and deterministic** (Hypothesis). Over random in-vent memories (teammate and
  non-teammate sightings across the own room, neighbours and far rooms; bodies; sabotage on or off;
  in-vent streaks of 1 to 6 rows with or without a meeting boundary inside), every intent is `vent`
  or `wait`. At an inside-count of 4 or more it is `vent`. Repeated calls, and permuted
  `room_neighbors` and `vent_graph` listings, give the same intent. Perturbed: a copy with the cap
  check removed fails the property.
- [ ] **The default is untouched.** `git diff --stat main...HEAD -- agents/tactical/impostor_policy.py`
  is empty. `TestCommittedCorpusTargetingPins` in `tests/agents/test_impostor_policy.py` passes
  unedited: on s9, 1754 decisions reconstructed, 109 in-vent, 9/232 free kills declined, and 223
  recorded kills reproduced; these are measured at `e886b663` and re-measured at dispatch. The
  `observed_risk` tests in `tests/agents/test_tactical_experiments.py` pass unedited.
  `publish_process_scorecard.py --check` and `publish_gameplay_census.py --check` pass unchanged.
- [ ] **Reconstructible from memory.** A fake 9p2i game recorded with both values ON is reconstructed
  by evidence honesty with the recorded policy with 0 decision mismatches (the capability the
  readers card lands); reconstructed with the default policy it shows more than 0. Tests in
  `tests/experiments/test_vent_look_and_wait_game.py` (new, this card only).
- [ ] **Wiring and determinism** (same file). `HeadlessGame` built with either value alone builds
  `ExperimentalImpostorPolicy`, and `has_tactical_changes` is true for `own_fresh_kill` alone. The
  fake game recorded twice is byte identical. It loads through the plain `ReplayLoader` with
  `outcome_verified` true, and its tick rows carry both keys. A default config serializes without
  them. The spine's refusal for these two values is deleted; building either value no longer
  raises. Planted: a config with only `vent_entry_policy="own_fresh_kill"` fails the test if the
  default `ImpostorPolicy` is built for it (patched into the factory), and a copy of the second
  recording with one tick row's state hash edited fails the byte comparison.
- [ ] **The census reads 0 on a game built with the arms** (same file). A fake 9p2i game on a
  development seed, with both values and the physical rule ON, reads 0 on the three B1 conformance
  cells of `eval/gameplay_census.py`: surfacings before the cap with a non-teammate in the
  inferred-visible set; trips longer than the cap; entries not after the impostor's own fresh kill.
  Their denominators are non-zero (at least one wait, one surfacing, one entry), so the test cannot
  pass vacuously. A perturbed copy of the carrier raises on each cell: one surfacing moved to a
  watched tick, one stay extended past the cap, one entry re-keyed to a teammate's victim. The
  policy's window (3) and cap (4) constants are pinned equal to the census's named constants.
- [ ] **The pending guard.** This card deletes exactly its two `WAVE_ARMS_PENDING` entries:
  `vent_exit_policy` `look_and_wait` and `vent_entry_policy` `own_fresh_kill`. Configs carrying
  them validate. The spine's refusal test, parametrized from the mapping's live contents, still
  refuses every value left pending at this card's head (the body-handle and ballot values,
  whichever have not merged), with no edit to `tests/orchestrator/test_experiment_arms.py`.
- [ ] **The lab arms.** `candidate_configs()` in `experiments/tactical_gameplay.py` gains
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
- [ ] **The two lab walk profiles declare their layers.** Mechanism: the profiles derived from
  `current-report` with `replace` (`experiments/tactical_gameplay.py:199`, `:363`) set the spine's
  `threaded_layers` explicitly, never inheriting `current-report`'s, to the layers the lab reads,
  named in Results; the spine names this card as their owner. Proof, per profile: it reads the
  spine's fake full-config recording (a copy of a fake recording on today's arms, its tick rows and
  footer rewritten to carry every wave field at its ON value, with the pending set patched empty)
  with every hash verified, and it refuses a planted unknown field (a stand-in added to the config
  model and `FIELD_LAYER` in a layer the profile does not declare) by name before its first
  advance. Perturbed: a profile with its layer declaration removed refuses the full-config copy.
- [ ] **The lab rows.** At this card's final head, which the harness's runtime fingerprint freezes
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
- [ ] **The projection is re-measured at dispatch.** The three commands in Evidence, re-run at the
  branch base with outputs outside the tree, reproduce 85, 62, 53 and 9; the ruled rows (7, 45, 33,
  8, and 7, 37, 32, 8); and the gate's 13 of 105. Any drift is recorded in Results with the command.
  If the scratch root is gone, the rule stated here rebuilds the wrapper, and the walk script is
  rewritten from the movement memo's description.
- [ ] **Publication neutral.** `git diff --name-only main...HEAD` names no path under `api/`,
  `frontend/`, `replays/` or `tests/fixtures/`, and leaves the featured list untouched. A demo bundle
  built at the base and at the head is byte identical (`diff -r`, Validation). Perturbed: the diff
  check flags a planted `frontend/` path in a scratch branch.
- [ ] **The registry row follows the audit bytes.** The `audits/` row of `docs/artifacts.md`
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

Not started. At delivery: each acceptance item's evidence, the re-measured projection, the lab
rows' fingerprint, the real `check.sh` exit code, the Decisions (the cap key, the registry row),
and the limitations (a first-order projection, fake-game mechanics, no temporal-path claim).
