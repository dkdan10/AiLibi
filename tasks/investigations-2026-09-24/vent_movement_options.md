# Vent movement options: waiting, travelling, and what the recordings say

Investigator memo, Stage B, topic `vent_movement_options`, 2026-09-24. Read-only on `main` at `e886b663`
(baseline 9). No commit, no edit to a tracked file, no provider call, no recorder, no held-out band, no prompt
printed. Every census is count-only over the four committed sets, rebuilt through the state-hash-verified
replay walk. Scripts and outputs live outside the tree (see Reproduction).

## The answer to the owner's question

Yes. I tested waiting for a clear exit, travelling inside the vent network, a better exit choice, a remote
peek, and narrower sight from inside, all against the positions the crew actually held in the 512 recorded
vent trips that ended in an exit.

- **Waiting alone buys almost nothing.** An impostor that waits in the vent it entered is sitting under its
  own corpse, and from there it cannot see the exit room of 4 of the 6 vent links. Waiting only lets it
  re-read rooms it could already read. A look-first exit with waiting avoids 139 of the 313 seen exits; the
  same rule without waiting avoids 128. Under the physical witness rule (R7) waiting never triggers at all.
- **Travelling is what removes the seen exits.** If the impostor can move vent to vent unseen and come out
  only at the vent it is at, every exit becomes an exit into a room it has just looked at. On the recorded
  positions that leaves about 14 seen exits before the next meeting instead of 313 (a first-order upper
  bound; see Limits). This is also how the genre works.
- **Recommended:** hidden vent travel as a new default-OFF engine arm, a look-then-surface impostor policy,
  venting only after the impostor's own fresh kill, and a hard stay cap of 4 play ticks.
- **The price is balance.** The vent tell survives, mostly as crew walking in on an entry, but it shrinks
  from about 2 trips in 3 to about 1 in 6. Vent proof decides 88% of impostor ejections today, so the crew
  would lose its main way to win. That is the owner's call, and the record measures it; the fake-provider
  lab cannot, because its fake votes eject nobody.

---

## Part 1. The engine as it is

### The three facts that decide everything

**1. Waiting inside is legal today, but nothing waits.**
- The engine accepts `wait` from inside a vent and the actor stays inside (`engine/tick.py:551`
  `_apply_wait` checks only that the actor is alive). `vent` and `wait` are the only legal in-vent actions:
  move, task, kill, report, emergency, sabotage and repair all raise (`engine/rules.py:67`, `:197`, `:222`,
  `:249`, `:276`; `engine/tick.py:248`, `:294`). The table is pinned by
  `tests/engine/test_rules.py:307` `test_in_vent_actor_may_only_vent_or_wait`.
- There is no time limit, no vent cooldown and no forced exit. The kill cooldown keeps running inside
  (`engine/tick.py:61` decrements every player). Probe: an impostor entered with cooldown 3, waited one tick,
  and read 2 then 1.
- A meeting does not pull it out under the default `meeting_reset="preserve"`; `hub_with_grace` does
  (`engine/meeting_reset.py:10-41`).
- The shipped policy never waits. `VENT_EXIT` is the first branch whenever `in_vent` is set
  (`agents/tactical/impostor_policy.py:402`), and it always picks a connected vent (`:1340-1385`). Measured:
  493 of 512 exits came one tick after entry; the other 19 are trips where a meeting opened before the
  impostor's exit action, and it left the tick after.

**2. Hopping inside is impossible today.**
- Any vent action by an actor already inside is an exit. `resolve_vent` sets `is_exit = True` for every
  in-vent action (`engine/rules.py:125-138`), to the current vent or a connected one, and `_apply_vent`
  flips `in_vent` (`engine/tick.py:449`, `in_vent=not actor.in_vent`).
- So a trip is exactly enter, then surface at the current or a neighbouring vent. Probe: a second vent
  action toward a connected vent emitted `VentExited` and was witnessed by the crewmate standing there.
- The map loader also refuses multi-tick vent links (`engine/world.py:172-180`, `traversal_ticks` must be 1).

**3. An impostor inside a vent sees its vent's room and every adjacent room, fresh each tick.**
- `compute_visibility_for_player` never checks the observer's own `in_vent`; only vented SUBJECTS are hidden
  (`engine/visibility.py:78`, `:130-168`). An impostor keeps the base `same_room_and_adjacent` sight
  (`:98-127`). Pinned by `tests/engine/test_visibility.py:73`.
- Baseline 9 runs with `temporal_observations` off, so the snapshot path builds the packet
  (`observation/service.py:332-460`): visible players and bodies in those rooms, moves whose departure room
  it can see, and task stamps. Probe: an impostor hidden in STORAGE's vent saw both crewmates in ENGINEERING.
- It gets no kill or vent action from others (witness lists exclude vented players, `engine/rules.py:28-43`)
  and no sound. The vent sound cue was retired; all that is left is the reserved zero feature slot
  `heard_vent_use` (`agents/tactical/features.py:150-164`, `:408`). The only audible event is the sabotage
  alarm (`observation/service.py:492-507`).
- The unadopted temporal-v2 path withholds event batches from a vented observer (`observation/temporal.py:71`,
  pinned by `tests/observation/test_temporal_v2.py:567`) but still delivers the snapshot.
- **So the exit decision is not made on entry-tick sightings.** The in-vent packet is built from the state
  after the entry tick resolved, so the exit tick's look is as fresh as any other decision. What the look
  cannot reach is the exit room itself on most links (next table), plus crew who walk in on the exit tick
  itself with a lower player id.

### The vent network, and what a hidden impostor can see from each vent

Six vents form a ring (`engine/maps/canonical_1.yaml:229-271`). Only two links join rooms that are next to
each other.

| vent room | connects to | exit rooms visible from inside | trips with an exit, by entry vent (pooled / 9p2i) |
|---|---|---|---|
| REACTOR | STORAGE, ADMIN | none | 112 / 96 |
| STORAGE | REACTOR, ENGINEERING | ENGINEERING | 117 / 103 |
| ENGINEERING | STORAGE, LABS | STORAGE | 122 / 84 |
| LABS | ENGINEERING, MEDBAY | MEDBAY | 22 / 22 |
| MEDBAY | LABS, ADMIN | LABS | 41 / 41 |
| ADMIN | MEDBAY, REACTOR | none | 98 / 89 |

Counts over the 512 trips with an exit:
- 210 started in REACTOR or ADMIN, where neither exit can be seen; 302 had one visible exit.
- 265 exits went into a room the impostor could not see; 134 went into a room it could see was occupied.
- At the first in-vent tick a blind exit room held crew 253 of 691 times (37%), a visible one 131 of 295
  (44%). A blind exit is a coin toss weighted against the impostor, and waiting does not change the odds.

### The rest of the mechanism

- **Witnesses.** The engine lists living, non-vented players in the room left and in the room surfaced into
  (`engine/rules.py:146-155`). An entry has the same room at both ends. The 62 exits seen only from the
  room left are what R7 removes.
- **Exit steering.** The exit takes the connected vent nearest the first target (`impostor_policy.py:1387-1418`).
  Right after a kill the cooldown zeroes every score (`:1271`), so targets re-sort by proximity
  (`:1013-1047`), and the impostor surfaces next to the nearest crewmate it saw.
- **Entry trigger.** The COVER branch fires for any body in the impostor's room (`:413`), vents if nobody
  but a teammate is in sight (`:1165-1199`, `:1293-1321`), and otherwise walks away.
- **The existing alternative.** `vent_exit_policy="observed_risk"` (`agents/tactical/experimental.py:35`,
  `:322-358`) scores rooms by first-hand sightings from the last 3 ticks, keeps the old choice on a tie, never
  waits and never checks the room being left. Blind rooms carry no sighting, so they score 0 and it picks
  them. Its fake-provider screen (`audits/tactical-gameplay/README.md:139`) moved held-out 9p witnessed exits
  from 32/53 to 33/61. That fits the geometry above: a better choice can only trade a visible crewmate for a
  blind gamble.
- **Design intent.** Phase 11 asked for an exit toward the best *isolated* target and accepted a careless vent
  near a witness as a catchable tell (`tasks/phase-11.md:63-68`). DESIGN.md makes vent use observable in both
  rooms (`DESIGN.md:351`), weights a seen vent +0.5 suspicion (`:691`), and limits in-vent actions to `vent`
  and `wait` (`:340-346`).

### Tests that pin vent behaviour today (blast radius)

- Engine: `tests/engine/test_rules.py:226-260`, `:307` (in-vent legality table); `tests/engine/test_tick.py:488`,
  `:932` (exit through a connected vent), `:990` (unconnected vent rejected), `:1345`;
  `tests/engine/test_visibility.py:63`, `:73`; `tests/engine/test_meeting_reset_experiment.py:17`;
  `tests/engine/test_tick_properties.py`, `tests/engine/test_world_state.py`.
- Observation and firewall: `tests/observation/test_service.py:273-440` (vent seen once, teammate gets no
  residue, non-witness gets nothing, vented player hidden, `in_vent` self channel);
  `tests/observation/test_temporal_v2.py:567`; `tests/observation/test_leak_property.py`; `tests/test_firewall.py`.
- Policy: `tests/agents/test_impostor_policy.py:1040-1104` (entry guard) and `:1121-1222` (exit branch; every
  exit test uses cooldown 0, which is why the steering defect was never pinned), `:1528`;
  `tests/agents/test_tactical_experiments.py:140`, `:176`, `:291` (observed_risk);
  `tests/orchestrator/test_experiment_config.py:84`.
- Consumers: 35 test files mention `in_vent`, `VentIntent`, `VentEntered` or `VentExited`, including training,
  api and viewer fixtures.

---

## Part 2. The genre reference

Stated plainly, from general knowledge of the genre:

- Inside a vent the impostor is hidden, and it sees the area around the vent it is at.
- It can move between connected vents while staying hidden, and it comes out at the vent it is at.
- It can stay inside as long as it likes.
- Going in and coming out are visible to anyone who can see that vent at that moment.
- The kill cooldown keeps running inside. (I hold this one less firmly than the rest. Nothing below depends on
  it, because the engine already behaves this way.)
- Crew cannot use vents.
- A meeting brings everyone to the table, including anyone hidden in a vent.

| | engine today | genre |
|---|---|---|
| hidden inside | yes | yes |
| sight inside | the entry vent's room and adjacent rooms | the area around the vent it is at |
| move vent to vent unseen | no: every in-vent vent action surfaces | yes |
| where it comes out | the current vent or a neighbouring one, often into a room it cannot see | the vent it is at |
| time inside | unlimited by rule; the policy never waits | unlimited |
| who sees going in or out | the room left and the room entered (R7 makes it physical) | whoever sees that vent |
| kill cooldown inside | runs | runs |
| meeting pulls it out | only under `hub_with_grace` (B2) | yes |

The one mechanical gap that matters is the third row. The engine teleports the impostor out into a
neighbouring room; the genre lets it travel hidden and come out where it has looked.

---

## Part 3. The options

### How the projection works

`walk2.py` re-walks all 300 games and writes, per tick: player rooms, in-vent flags, the ordered actions with
their destinations, and body rooms. Nothing else. `proj.py` rebuilds each recorded exit's crew witnesses from
those positions and the id-ordered moves. It matches the engine's recorded witness set on **512 of 512** exits.

Each option is then replayed on every recorded trip against the recorded crew positions, from the tick after
entry until it surfaces, its stay cap forces it out, or a recorded meeting opens while it is still inside.
- **Upper bound, first order.** The crew are held to what they actually did, and in the recording they often
  reacted to the real, seen exit (a witness walking to the button). A real game will differ.
- **Classes.** A projected surfacing is *clear*, *seen by an arrival* (a lower-id crewmate walked in that
  tick, which no look can prevent), *seen blind* (a crewmate already stood in a room it could not see), or
  *seen knowingly* (every witness was already in sight; with a stay cap this is a forced exit).
- **Populations.** Pooled = 512 trips with an exit, 313 of them seen by crew today (251 under R7). On 9p2i,
  435 trips, 271 seen (226 under R7).

### The projection, pooled

"Avoided" counts the recorded seen exits that the option surfaces clear, or that are still inside when the
next recorded meeting opens. "Newly seen" counts exits unseen in the recording that the option would make seen.

| option | seen exits, today's rule | avoided of 313 | newly seen | seen exits, R7 | avoided of 251 | ticks inside per trip | trips inside at a meeting |
|---|---|---|---|---|---|---|---|
| status quo | 313 | - | - | 251 | - | 1 (19 trips: 2) | 0 |
| (f) better choice, no wait | 204 | 128 | 19 | 128 | 142 | 1 | 19 |
| (a) look-first + wait, cap 4 | 193 | 139 | 19 | 128 | 142 | 1; 19 trips wait 2-4 | 23 |
| (b) own-room sight + wait, cap 4 | 205 | 140 | 32 | 158 | 142 | as (a) | 23 |
| (g) remote peek + wait, cap 4 | 93 | 225 | 5 | 21 | 233 | 1: 384, 2: 38, 3: 51, 4: 34 | 68 |
| (c) hidden travel, cap 3 | 43 | 288 | 18 | 43 | 227 | 2-3 | 157 |
| (c) hidden travel, cap 4 | **14** | **307** | 8 | **14** | 245 | 2: 321, 3: 120, 4: 52 | 171 |
| (c) hidden travel, cap 6 | 11 | 308 | 6 | 11 | 246 | 2-6 | 172 |

On 9p2i the seen exits read, in the same order: 271, 175, 166, 177, 72, 41, 14, 11 under today's rule, and 226,
121, 121, 150, 20, 41, 14, 11 under R7.

What the rows say:
- **(a) against (f).** Waiting adds 11 avoided exits. Under R7 it adds none: the room it sits in is never the
  exit room, so the only trigger to wait is gone.
- **What (a) cannot reach.** Of its 193 seen exits, 107 are blind and 80 are walk-ins.
- **(c) with cap 4.** Of the 313: 160 surface clear, 142 are still inside when a recorded meeting opens, 5 are
  inside when the game ends, and 6 are still seen. Its 14 seen exits are 8 walk-ins and 6 forced.
- **Meetings.** Letting the stay continue through a meeting under `preserve`, with the cap counted from the
  meeting, adds 36 clear and 7 seen surfacings. Another 128 cannot be projected: 70 impostors were ejected at
  that recorded meeting and 58 games ended, both driven by the recorded seen exit.
- **Under R7, (c) is unchanged.** It always surfaces from the vent it is at, so the room left and the room
  entered are the same room.

### Option (a): wait-then-exit with a look first (the B1 sketch)

- **What changes.** Tactical policy only: a new `vent_exit_policy` value on today's engine.
  - Never come out into a room seen holding a non-teammate or a body.
  - Under today's rule, do not come out while a non-teammate stands in the room above the vent.
  - Prefer a visibly clear exit, then a blind one, then the one farther from the body.
  - Wait otherwise, up to a cap, then take the least-watched exit.
- **Sight.** The look uses the current in-vent packet, not what it saw before entering. As Part 1 shows, the
  sight is already there. A rule that used only pre-entry sightings would have no reason to wait, because it
  could never learn that a room had cleared.
- **Arm or lever.** An arm value on `vent_exit_policy`, default `target_distance`.
- **Determinism and replay.** Pure function of memory and the public map; no RNG; ties by room hops then vent
  id. It changes recorded actions, so it can only ride the samples/9p2i re-record. The other sets are
  untouched.
- **Firewall.** Reads only `saw_player`, `saw_body` and `self_state` rows; no new channel.
- **Projection.** 139 of 313 avoided; 19 newly seen; 193 seen (R7: 128). Realized gains are likely smaller:
  `observed_risk`, which does most of this, moved held-out 9p exposure only from 60% to 54%.
- **Cost.** About 5 files: `experimental.py`, `experiment_config.py`, `game.py` option mapping,
  `experiments/tactical_gameplay.py`, plus tests and docs. No engine, event, viewer or pin change.
- **Risk.** Low to the proof channel (seen exits fall by about a third) and modest to balance. It reverses
  `tasks/phase-11.md:63-68`.

### Option (b): in-vent sight of the vent's room, with waiting

- **The premise.** As written, the change is not needed. The in-vent impostor already sees its vent's room,
  and more: the adjacent rooms too. So a look is already a look, and (b) is (a).
- **The one real variant is narrowing sight** to the vent's own room, the literal genre reading without
  travel. It makes every exit blind.
  - Projection: 140 avoided but 32 newly seen (R7: 49); 205 seen.
  - Cost: a visibility arm keyed on the observer being in a vent (`engine/visibility.py`), threaded to every
    `compute_visibility_for_player` caller, including move witnesses in `engine/tick.py:271-281`.
- **Rejected.** It is worse than (a) and costs more.

### Option (c): hidden multi-hop travel

- **Engine rule.** New arm on `advance_tick`. For an impostor already inside:
  - a vent action to its current vent surfaces there, with room left and room entered the same;
  - a vent action to a connected vent moves it to that vent's room and keeps it inside, one hop per tick;
  - the hop emits a new witness-free event.
  Entry is unchanged.
- **Sight.** Unchanged code: sight follows the player's room, so after a hop it sees the new vent's room
  and adjacent rooms. This is exactly the genre's "see around the vent you are at".
- **Policy.** Hop away from watched rooms and the corpse, come out only where it sees the room is clear, and
  surface where it is at the stay cap.
- **Arm or lever.** Two coupled arm values, both default OFF: the engine arm and the policy value. Neither is
  valid without the other. The old policy under hidden hops would hop forever; the new policy under the old
  engine would teleport out.
- **Determinism and replay.**
  - No RNG, and resolution stays in id order; the per-tick RNG draw is unchanged.
  - The hop changes the player's room while inside, which is in the state hash. A replay consumer that
    forgets the arm therefore fails loudly at the first hop. That is safer than R7, where a forgotten arm
    passes every hash check (census_and_record F5).
  - Every `advance_tick` caller must thread the arm: `orchestrator/game.py:2566`, `eval/replay_walk.py:636`,
    `api/replay_loader.py:1633`, and the lab and rubric extractor the census memo already lists.
  - With the arm absent, the new branch is unreachable, so the other three sets verify byte-identically.
- **Firewall.**
  - A hop has no witnesses by construction.
  - The observation service handles only `KilledEvent` and `Vent*Event`, so the new event reaches no packet;
    a vented subject is already excluded from every `visible_players`.
  - The temporal-v2 path, which is off, must raise on a hop rather than guess (`observation/temporal.py:120-150`).
  - `agents/` keeps reading only `SelfView.room`, `in_vent`, sightings and `PublicMapView.vent_graph`.
- **Projection.**
  - Cap 4: 307 of 313 avoided before the next meeting, 8 newly seen, 14 seen exits (8 walk-ins, 6 forced).
  - R7 changes nothing, for the reason above.
  - Cap 3 forces 37 knowing exits; cap 6 saves only 3 more than cap 4.
- **Cost.**
  - Engine: `engine/rules.py`, `engine/tick.py`, `engine/events.py` (new event, union and `event_to_dict`).
  - Config: `orchestrator/experiment_config.py` (fields, format gate, coherence validator) and
    `orchestrator/game.py` (threading and option mapping).
  - Consumers: `eval/replay_walk.py`, `api/replay_loader.py` (a third vent event kind), `api/schemas.py`,
    and the frontend types via `scripts/gen_frontend_types.py` plus the viewer's vent rendering.
  - Policy and lab: `agents/tactical/experimental.py`, `experiments/tactical_gameplay.py` (arm and counters).
  - Other: `training/env.py` (refuse the arm; ML is paused); docs (`DESIGN.md` 3.4 note,
    `docs/architecture.md`, `docs/glossary.md` "vent travel", the tactical-gameplay audit table).
  - About 15 files and 12 or more new tests. No existing pin is re-derived, because every current test runs
    the default arm; the in-vent legality table gains an arm parametrization.
- **Risk.** The highest to the proof channel and to balance; see "What it does to the vent proof channel"
  below. It adds a new engine mechanic beyond B1's literal text, so it needs an owner ruling.

### Option (d): vents as a general movement tool

- **Out of scope this wave**, and the orchestrator expects that.
- **What it would need.** New policy triggers: fleeing a pursuer, repositioning during cooldown, surfacing
  beside a lone target when the cooldown is 0.
- **What it would do.** Every added entry carries the same walk-in exposure (73 of 587 entries seen today),
  and it changes where kills happen. It would need its own screen.
- **Left open.** With (c) in place it becomes a policy change only.

### Option (e): vent cooldown, maximum time inside, forced exit

- **Today nothing stops camping.** The engine allows unlimited `wait` inside. Only the policy's
  exit-first branch keeps stays at one tick.
- **Recommended: a policy stay cap, not an engine cap.**
  - Cap at 4 play ticks, counted from the later of the entry and the last `meeting_boundary` memory row
    (`impostor_policy.py:212`, `:932`). When it is reached, the policy surfaces where it is.
  - 4 equals the canonical kill cooldown. The cooldown runs inside, so by the time the cap forces an exit the
    kill is ready, and staying longer only costs kills.
  - An engine cap would need a per-player in-vent counter in `PlayerState`. That changes the state bytes
    every committed hash covers, and it is not needed while the only actor inside is the rule-based policy
    (LLMs never act tactically; ML is paused).
- **No vent cooldown is needed.** Under (f) every trip starts from the impostor's own kill, and kills are at
  least 4 ticks apart.
- **Meetings.** B2 (`hub_with_grace`, in the Stage B slate) ends any stay at a meeting, as the genre does.
  Without B2 the stay continues through the meeting and the cap restarts at it.
- **Planted test:** a stay that reaches the cap surfaces.

### Option (f): exit and entry rules that need no engine change

- **No steering while on cooldown; prefer the exit away from the corpse.**
  - This is (a) without waiting: 128 of 313 avoided and 19 newly seen, in the projection.
  - It fixes the documented coding gap: into a visibly occupied room 134 times in 137 when a choice existed.
- **Vent only after the impostor's own fresh kill.**
  - Key the COVER vent on an own-kill memory row whose victim lies in the room (`EVENT_OWN_KILL`,
    `agents/perception.py:70`, `victim_id` at `:558`, matched against the `saw_body` victim at `:593`).
    Any other body means walk away.
  - Measured: 587 entries = 487 after an own kill the tick before + 38 two or three ticks after an own kill
    + 29 at an older own victim + 33 at a teammate's victim.
  - A 3-tick window drops the last two groups: 62 entries, 13 seen entries, 23 seen exits, 35 seen trips.
  - Cost: about 3 files; a new independent arm value; screenable alone on today's engine.
- **Recommended in every combination.**

### Option (g): other ideas from the tree and the genre

- **Remote peek.** An in-vent impostor would also see the rooms of the vents its vent connects to.
  - Numbers: nearly (c)'s under R7 (21 seen exits), with shorter stays (68 trips inside at a meeting against
    171).
  - Why not: it gives sight through the pipes, which the genre does not. It also changes the firewall's core
    function, `compute_visibility_for_player`, and every move-witness list built from it.
  - Keep it as the fallback if (c)'s engine change is refused.
- **Surface in place today.** Legal now (`engine/rules.py:129-135`), but useless right after a kill: the
  corpse is in that room.
- **Phase field on the witness record** (vents memo R4). Not a movement question; unchanged here.
- **A sound cue.** Retired for double counting and a teammate leak. Not revived.
- **Meeting pulls impostors out of vents.** That is B2; it complements (c).

### Which combinations are coherent

- **(c) requires its own policy.** The engine arm with `target_distance` or `observed_risk` would hop
  forever, and the travel policy on today's engine would teleport out. The config validator must require both
  or neither.
- **(c) with R7 is coherent but makes R7 moot.** Under (c) an exit's room left and room entered are the same
  room, and an entry's always were. R7's arm then changes no recorded witness set on samples/9p2i. Keep its
  planted test; do not expect a measured effect from it.
- **(c) with B2 is coherent and recommended.** Stays that reach a meeting end at the regroup, with no vent
  event, as in the genre. The projection has 144 of 464 trips reaching a recorded meeting.
- **(c) with R6 self-report ON is incoherent** (self-report changes the COVER branch). R6 is OFF this wave.
- **(f) fits everything.** (a) is subsumed by (c). (g) and (c) are redundant with each other. (b) is dominated.

---

## The recommended combination

### Arms

All are default-OFF fields on `RecordedExperimentConfig` and mirrored on `TacticalExperimentOptions`. The names
are proposals; the card fixes them.

| field | values, default first | layer |
|---|---|---|
| `vent_travel` | `"exit_on_move"` (today) / `"hidden_hops"` | engine, threaded into `advance_tick(..., vent_travel=)`; an unknown value raises |
| `vent_exit_policy` | adds `"travel_look"` | tactical; valid only with `hidden_hops`, and `hidden_hops` only with it |
| `vent_entry_trigger` | `"any_body"` (today) / `"own_fresh_kill"` | tactical; independent |

- **Format version.** New fields need a format gate that omits them below it, so older configs keep their
  bytes (the pattern at `orchestrator/experiment_config.py:97-107`).
- **Coordinate one format bump with the other Stage B arms.** Today format 3 is welded to evidence version 2,
  temporal v2 and policy reconstruction (`orchestrator/replay.py:767-773`, `orchestrator/policy_reconstruction.py:74`).
  The vent fields must not inherit those requirements.
- `has_tactical_changes` must include the new fields.

### The engine rule under `hidden_hops`

For an actor already inside:
- **`vent` to its current vent:** `VentExited` with room left = room entered = its room, witnesses = living,
  non-vented players there, and `in_vent` becomes False.
- **`vent` to a connected vent:** room becomes that vent's room, `in_vent` stays True, and a new `VentTraversed`
  event is emitted with actor, tick and the two vent ids, and no witness fields.
- **Anything else** raises `ActionRejectedError`, as today.

Entry and every other rule are unchanged, and there is no engine time limit.

### The exact policy

`ExperimentalImpostorPolicy`, a pure function of memory and the public map, with no RNG and no instance state.

**Entry (`own_fresh_kill`).** Vent only if all three hold:
- a vent is in the impostor's room;
- no non-teammate is seen in the room this tick (today's guard);
- a body seen in the room has the victim of one of its own `own_kill` rows at most 3 ticks old.
Otherwise it takes today's walk-away move, to the alphabetically first neighbour.

**Inside (`travel_look`), every tick, before any other branch:**
1. `here` = the vent in the impostor's room; raise if there is none.
   - `watched(room)` = a non-teammate `saw_player` row this tick in that room.
   - `body(room)` = a `saw_body` row this tick in that room.
2. If neither `watched(here's room)` nor `body(here's room)` holds, surface at `here`.
3. Otherwise, if `stay >= 4`, surface at `here` anyway: a forced exit.
   - `stay` counts consecutive in-vent `self_state` ticks since the later of the entry and the last
     `meeting_boundary`.
4. Otherwise hop to the connected vent with the smallest key: (watched, body, is the vent it just came from,
   minus route hops from the room it fled, vent id).
   - The room it fled is the room of the first in-vent `self_state` row.
   - Route hops use the existing A* helper, `_vent_distance`.
5. A vent with no connections surfaces in place, so the impostor is never stuck.

A fellow impostor is never `watched`.

**When every reachable exit is watched,** it keeps moving round the ring (never straight back, away from
watched rooms and the corpse) until the cap. Then it surfaces where it is, knowingly in view. That is the
deliberate, catchable mistake Phase 11 wanted. It never surfaces into a room it cannot see. On the recorded
positions this happens 6 times in 512 trips.

### Planted tests

Each test is red on the current code and green after, unless marked as a perturbation.

1. **A hop stays inside and unseen.** An impostor in STORAGE's vent, crew in STORAGE and REACTOR, arm on,
   `vent` to REACTOR_VENT: `in_vent` stays True, room is REACTOR, one `VentTraversed` event, no vent
   witnesses. Red today: the same action surfaces, and the REACTOR crewmate witnesses it.
2. **It surfaces only where it is.** Arm on: `vent` to the current vent gives `VentExited` with room left =
   room entered. With the arm off, the same fixture's connected-vent action surfaces next door, which proves
   the arm is what differs.
3. **A hop is never visible.** A leak-property sweep: across random positions, no observer's packet, sighting,
   move or vent action mentions a hopping impostor on a hop tick. Perturbation: route `VentTraversed` into
   `_observed_actions_for_agent` and the sweep goes red.
4. **No steering into a watched room while on cooldown.** Inside STORAGE's vent, cooldown 3, a crewmate seen
   in ENGINEERING: the policy does not pick ENGINEERING_VENT. Red today (the target-distance exit picks it:
   the 134 of 137 defect). This is the case the existing tests miss by using cooldown 0.
5. **A teammate in the exit room is not a witness.** Only a fellow impostor seen in the current room: the
   policy surfaces at the current vent. Red today (the current policy never surfaces in place).
6. **A teammate's victim does not trigger venting.** A body in a vent room with no own-kill row: the policy
   walks away. Red today (the current COVER vents).
7. **An older own victim does not trigger venting.** Own kill 5 ticks ago, body in the room: it walks away.
   Red today.
8. **An over-long stay is cut off.** A 4-tick in-vent streak with the room watched: it surfaces at the current
   vent. At 3 ticks, same room: it hops to the unwatched neighbour. Red today on both (the current exit
   always teleports to a connected vent).
9. **The stay counter restarts at a meeting.** A `meeting_boundary` row inside the streak resets `stay`.
   Perturbation: count from entry only and it goes red.
10. **Config coherence.** `hidden_hops` without `travel_look` raises, and the reverse raises. The default
    config serializes to today's bytes, and the three untouched committed sets verify byte-identically.
11. **Determinism.** A fake-provider game with the arms on, recorded twice, is byte-identical, and a hop
    consumes no RNG draw.
12. **Forgotten arm fails loudly.** Walking that game without threading `vent_travel` raises a state-hash
    mismatch at the first hop.

### Lab protocol the card must require

Fake provider, **development seeds 1000-1007 only**, both rosters (4p1i with one task, 9p2i with two), 8 paired
games per arm, the existing 96-tick, 256-call, 1M-input, 100k-output, 30-second, $0 limits:

```sh
uv run python -m experiments.tactical_gameplay --split development \
  --arms baseline vent_risk vent_trigger vent_look vent_travel vent_travel_trigger \
  --output <unused scratch path>
```

- `vent_trigger` = `own_fresh_kill` alone.
- `vent_look` = option (a).
- `vent_travel` = the coupled pair.
- `vent_travel_trigger` = the recommendation. It is the one arm that changes more than one field, because
  the pair is only valid together.

Keep the `observed_risk` row and its verdict unchanged. The fake votes eject nobody, so the lab measures the
tactical cells below and not balance. Balance is reported from the samples/9p2i record and never gates.

### Census cells

Reported, never gating, count-only, keyed by (set, game, trip) or (set, meeting). They extend the census
memo's C2-C10.
- **Seen exits per exit.** Split by the room surfaced into and the room left (C3, C4, C5). Under (c) they all
  read the same room.
- **Seen entries per entry (C2)**, still expected to be all same-tick walk-ins.
- **Hops per trip.** Projection for the recommendation: 1: 288, 2: 115, 3: 54, 4-5: 7.
- **Ticks inside per trip (C9).** Projection: 2: 202, 3: 169, 4: 62, 5 or more: 31. Today it is 1 for 493 trips.
- **Exits into a visibly occupied room (C6).** Today 134. Under (c) this equals the forced exits into view.
- **Forced exits** (stay cap reached). Today 0; projection 6-8.
- **Trips reaching a meeting inside a vent**, and trips ended by the B2 regroup with no exit event.
  Projection: 144.
- **Entries by trigger class (C10):** own kill the tick before, 2-3 ticks before, older own victim,
  teammate's victim. Today 487 / 38 / 29 / 33; expected 0 in the last two.

### What it does to the vent proof channel

The flag, the grounding and the ballot's proof line are unchanged. What changes is how often a vent is seen.
Projection for the recommendation, first-order:

| | today, pooled | after, pooled | today, 9p2i | after, 9p2i |
|---|---|---|---|---|
| vent entries | 587 | 525 | 501 | 441 |
| seen entries (walk-ins) | 73 | 60 | 64 | 52 |
| seen exits | 313 | about 17-23 | 271 | about 17-22 |
| seen trips | 384 (65%) | about 77-83 (15-16%) | 333 (66%) | about 69-75 (16-17%) |

- **How the seen exits are estimated.** 17 come from projectable surfacings: 11 before the next meeting and
  6 after it. The high end assumes the 124 trips that cannot be projected surface at the same 5% rate.
- **Yes, the game still has a vent tell.** It is the genre's: an impostor is caught when a crewmate walks in
  as it drops in, or when it gives up and comes out in view. It happens in about 1 trip in 6 instead of 2 in 3.
- **Rough scaling of vent convictions.** Scaling vent-band convictions by seen trips gives about 60 on 9p2i
  instead of 281, and about 70 pooled instead of 326.
- **What that means for the table.** Meetings without vent proof eject 24% of the time, at 52% impostor share.
  So impostor wins would rise steeply, and the crew task win is weak by design (`dead_task_rule: redistribute`).
- **That is the process value's trade.** Fewer foregone pile-ons, more meetings that must reason. Whether the
  result is showable is the owner's decision, and it is readable only from the record.

### Rulings the card needs

1. Hidden vent travel is a new engine mechanic, beyond B1's literal text. The owner's follow-up question
   invites it, but it needs an explicit yes.
2. It reverses the Phase 11 exit design (`tasks/phase-11.md:63-68`).
3. It adds levers against the direction's stop list.
4. The owner accepts the balance shift above.
5. Rendering hop events in the viewer is a publication decision: a push to `main` rebuilds the Pages demo
   from the re-recorded samples/9p2i.

---

## Part 4. Recommendation

**Adopt hidden vent travel as a default-OFF engine arm with a look-then-surface impostor policy, venting only
after the impostor's own fresh kill and a 4-tick stay cap, recorded only on samples/9p2i with B2 on, because
waiting alone cannot see 4 of the 6 exit rooms and avoids 11 more seen exits than a better choice rule, while
travel avoids about 307 of the 313 before the next meeting on the recorded positions, the way the genre does it.**

Ranked alternatives, and why they lost:
1. **(g) remote peek with waiting, plus (f).** About the same numbers under R7 (21 seen exits) with shorter
   stays. Lost because it is sight through the pipes, not the genre, and it changes the firewall's core
   visibility function and every move-witness list. It is the fallback if the engine rule is refused.
2. **(a) or (f), a look-first choice on today's engine.** Cheapest: policy only, about 5 files, no viewer or
   engine change. Lost because it leaves about 190-200 seen exits, blind exits and walk-ins it cannot see, and
   the `observed_risk` screen suggests the realized gain is smaller still. It is the right choice if the owner
   wants a modest shift rather than the genre.
3. **(f)'s entry trigger alone.** Removes 62 entries and 35 seen trips. Too small alone; included in every
   combination.
4. **(b) narrower in-vent sight.** Worse than (a): 32-49 more blind exits. Rejected.
5. **(e) an engine stay cap or vent cooldown.** Needs new per-player state inside every committed hash, and is
   unnecessary while the policy is the only actor. The policy cap does the job.
6. **(d) vents as general movement.** Out of scope this wave; it becomes a policy change once (c) exists.

---

## Limits

- **Every projection is first-order.** Crew positions are the recorded ones, shaped by the recorded (often
  seen) exits. The lab re-run and the record are the real measures.
- **Unprojectable trips.** 124 of the 464 recommended-combination trips cannot be projected past a recorded
  meeting: the impostor was ejected there, or the game ended.
- **The balance figures are proportional scaling**, not a model of the game.
- **The stay cap** of 4 against 6 differs by 3 seen exits in projection; the lab should confirm it.
- **Meeting speech.** Longer stays lengthen the "a vent in X" spans in the impostor's own location trail
  (`agents/memory/store.py:1554`). A self-incriminating slip is possible and is not measured here.
- **The genre claim about the kill cooldown** is held less firmly than the others and is not load-bearing.

## Reproduction

Scratch directory: `<session scratchpad>/ventopts`.

```sh
# from the repo root (worktree at e886b663)
PYTHONPATH=. uv run --frozen python <scratch>/ventopts/probe_sight.py        # in-vent sight, wait, second vent action
PYTHONPATH=. uv run --frozen python <scratch>/ventopts/walk2.py <scratch>/ventopts/walk2.json
cd <scratch>/ventopts
python3 proj.py walk2.json            # witness reconstruction check (512/512) and option sweeps
python3 proj2.py walk2.json           # the projection tables above
python3 proj2.py walk2.json through   # hidden travel continuing through meetings
python3 recommended.py walk2.json     # the recommended combination
python3 own_kill.py walk2.json        # entry trigger classes
python3 entry_rooms.py walk2.json     # entry rooms and exit visibility
python3 status_cells.py walk2.json    # status-quo census cells
```

`walk2.py` writes only player ids, room ids, in-vent flags, action types and destinations, body rooms, and
vent and kill ids and witnesses. `synth0924/an2.py` on the existing `walk.json` reproduces the 116 / 99 / 98
decomposition quoted in the brief.
