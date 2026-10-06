# Tactical and structural comparisons

All candidates remain explicit experiments. No default policy, map rule or
meeting protocol is adopted by this screen. The committed model recordings
establish historical mechanisms; the fresh games use a deterministic fake
provider and cannot establish model reasoning quality.

## Inputs and reproduction

The final runtime fingerprint is `d93f9d096e4b23572915e0ab128ee4ad266420bbbc266231eb7d49322d09bbd8`. Both captures use
exactly that source, including Python, templates, map/config inputs and locked
dependencies. Their JSON records carry UTC capture time, the checkout label,
machine/runtime details, source recording fingerprints and consumed roster
byte hashes. The working-tree source digest identifies the measured code even
when the later cleanup commit has a different commit label.

Development seeds are 1000–1007 and held-out seeds are 2000–2015, independently
for 4p1i/one task per crew member and 9p2i/two tasks. Each arm changes one
configuration field. All eight candidates were retained for the predeclared
held-out screen; no threshold or candidate was selected from held-out wins.
The scoped inert reverse guard had already been removed on development evidence.

Each game has a 96-tick, 256-call, 1,000,000-input-token, 100,000-output-token,
30-second and $0 limit. All 144 development and 288 held-out games completed;
none aborted or hit a limit. Recorded usage reconciles with the enforced
budget. The fake provider made 3,192 / 6,886 calls in the two splits, reporting
8,484,617 / 18,319,405 input tokens and 164,388 / 354,629 output tokens, at $0.
These are synthetic provider counters, not purchased generation.

Reproduce into unused output paths; the harness refuses replacement and refuses
publication when source/input bytes change during a screen:

```sh
uv run python -m experiments.tactical_gameplay --split development --include-samples --output /tmp/tactical-development.json
uv run python -m experiments.tactical_gameplay --split held_out --output /tmp/tactical-held-out.json
```

## Recorded-model baseline

All 100 canonical recordings reconstruct under strict chronology, state hashes
and outcomes. These counts reproduce the pre-change diagnostic. A task transfer
can exclude a crewmate who already owns a completed copy of the same map task.
Work below means remaining task ticks among eligible living crew, not distance.

| Mechanism | 4p1i, 50 recordings | 9p2i, 50 recordings |
| --- | ---: | ---: |
| Accepted finished-crew waits, all at hub | 128 | 457 |
| Longest consecutive finished wait | 9 ticks | 17 ticks |
| Transfers to a busier eligible recipient | 18/59 | 268/355 |
| Unfinished tasks dropped, no eligible recipient | 0 | 9 |
| Impostor move reversals / accepted moves | 14/241 | 71/699 |
| Crew-witnessed vent exits / exits | 18/39 | 62/97 |
| Crew-witnessed kills / kills | 1/62 | 3/182 |
| Resolved meetings, all called by crew | 39 | 151 |
| Unreported corpse instances left after meetings | 3 | 96 |
| Preserved survivor spatial states / nonterminal transitions | 45/45 | 631/631 |
| Reactor starts / repairs | 0/0 | 10/8 |
| Crew ejection wins / task wins / impostor wins | 20/12/18 | 35/0/15 |

Corpse counts are instances across meeting boundaries, not distinct victims.
The 4p set has 40 engine meeting triggers but 39 resolved meetings: one report
coincides with a terminal outcome. That extra trigger is not a duplicate report.
Report age uses the actual kill event, never a body ID or discovery-as-death
assumption; maxima are 8 and 29 ticks. Initially, mean per-game minimum/maximum
crew task work is 4.14/8.46 ticks in 4p and 8.00/16.88 in 9p. The three-task
roster cannot reach the baseline six-sevenths sabotage trigger while unfinished.

## Paired one-change screens

Waits are accepted actions by crew with no unfinished owned task. Reversals are
geometric consecutive A→B→A moves by impostors, including justified ones.
Exposure is crew-witnessed vent exits / all exits, including source witnesses.
Allocations count above-minimum-work recipients / all transferred instances.
Task wins below are fake-game outcomes; every other win is impostor parity.
The fake votes produced no ejections. A `0/0` exposure cell means no exits.

### Development: 4p1i, 8 games per arm

| Arm | Waits | Reversals | Exposure | Allocations | Reactor starts | Task wins | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 22 | 6 | 6/8 | 3/14 | 0 | 1 | 48 |
| Least-work allocation | 14 | 5 | 5/8 | 0/12 | 0 | 1 | 48 |
| Patrol | 0 | 4 | 6/7 | 3/15 | 0 | 1 | 54 |
| Brief accompaniment | 0 | 4 | 6/7 | 3/15 | 0 | 1 | 54 |
| Observed vent risk | 25 | 4 | 5/8 | 3/11 | 0 | 2 | 48 |
| Meeting follow-through | 28 | 6 | 6/8 | 3/17 | 0 | 1 | 60 |
| Regroup with grace | 34 | 3 | 6/8 | 3/15 | 0 | 1 | 48 |
| Self-report | 22 | 5 | 0/0 | 3/10 | 0 | 3 | 48 |
| Earlier sabotage | 18 | 3 | 6/8 | 3/15 | 5 | 0 | 48 |

### Development: 9p2i, 8 games per arm

| Arm | Waits | Reversals | Exposure | Allocations | Reactor starts | Task wins | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 96 | 30 | 16/29 | 59/73 | 1 | 0 | 294 |
| Least-work allocation | 0 | 22 | 12/18 | 0/67 | 0 | 0 | 318 |
| Patrol | 0 | 31 | 12/22 | 63/76 | 1 | 0 | 322 |
| Brief accompaniment | 0 | 34 | 12/22 | 62/75 | 1 | 0 | 312 |
| Observed vent risk | 106 | 12 | 14/34 | 58/70 | 1 | 0 | 308 |
| Meeting follow-through | 73 | 28 | 17/28 | 56/70 | 1 | 0 | 272 |
| Regroup with grace | 147 | 33 | 9/16 | 49/62 | 1 | 0 | 220 |
| Self-report | 78 | 17 | 0/0 | 55/65 | 1 | 0 | 406 |
| Earlier sabotage | 89 | 27 | 15/29 | 59/70 | 5 | 0 | 284 |

### Development: the Stage-B vent arms, 2026-09-26

These rows screen the vent arms of the Stage-B wave on fake games. Each arm is
named after the recorded value it sets
([the look-and-wait card](../../tasks/work/vent-look-and-wait.md)).

- **Look and wait** (`vent_exit_policy = look_and_wait`). An impostor inside a
  vent looks before it leaves. It surfaces only when nobody but a teammate stands
  in the rooms it can see from there: its own room and the rooms next to it, or
  its own room alone while any sabotage runs. Otherwise it waits. After four
  ticks inside it surfaces anyway. It then prefers a room it saw clear, then a
  room it cannot see, then a watched room.
- **Own fresh kill** (`vent_entry_policy = own_fresh_kill`). An impostor dives
  into a vent only beside its own victim, killed at most three ticks earlier with
  no meeting between. Any other body sends it walking away, as the default cover
  does.
- **Physical** (`vent_witness_rule = physical`). An exit into another room is
  seen only from the room surfaced into.
- **`stage_b_full`** sets the four round-1 fields that act during a fake game's
  play: the physical rule, both vent values and the regroup reset
  (`meeting_reset = hub_with_grace`). The round-1 rebuttal, body-handle and
  ballot fields change only a meeting's turns and prompts. A fake meeting
  ejects nobody, so they cannot change a fake game's play, and the lab leaves
  them out.
- **`stage_b_full_minus_<value>`** drops that one value back to its default.
  These arms give mechanical attribution only.

Inputs: the development split only, seeds 1000-1007 on both rosters, under the
lab's limits (96 ticks, 256 calls, 1,000,000 input and 100,000 output tokens, 30
seconds and $0 per game). The held-out split was not run. The rows are
`stage-b-development.json`. Its runtime fingerprint is `eac202d4f73db94c5daa511ce912fc76dfc8450ac6e5db326f691eacad1ec49e` and its git
head is `63980a00ace5336b901302552c20cdb39db1c95b`. All 160 games completed, and none aborted or hit a limit.
Reproduce into an unused path:

```sh
uv run python -m experiments.tactical_gameplay --split development --arms baseline vent_risk vent_physical vent_look_and_wait vent_own_fresh_kill stage_b_full stage_b_full_minus_look_and_wait stage_b_full_minus_own_fresh_kill stage_b_full_minus_physical stage_b_full_minus_hub_with_grace --output /tmp/stage-b-development.json
```

The re-run baseline and observed-risk rows equal the committed development rows
above in waits, exposure and calls: 22, 6/8, 48 and 25, 5/8, 48 on 4p1i, and 96,
16/29, 294 and 106, 14/34, 308 on 9p2i. So this card moved neither the default
policy nor `observed_risk`.

The columns are defined as follows.

- **Waits** and **Exposure** are defined as above.
- **Exit room** counts exits a crewmate saw from the room surfaced into.
- **Room left only** counts exits a crewmate saw only from the room left.
- **Not own fresh kill** counts entries with no victim of that impostor in that
  room, killed at most three ticks before, with no meeting between.
- **Vent waits** counts waits an impostor made inside a vent.
- **Ticks inside** counts surfaced trips by play ticks spent inside, restarting
  at a meeting. **At the cap** counts trips of four ticks.
- **In place** counts exits back into the room entered from.
- **Vent at open** counts meetings that opened with an impostor inside a vent,
  over all meetings.
- **Impostor wins** and **Calls** are read from each game's result.

Every count comes from the recordings the lab walked, with every tick and meeting
hash verified. The compact check at the end of this page, pointed at
`stage-b-development.json`, reproduces them from the JSON.

#### 4p1i, 8 games per arm

| Arm | Waits | Exposure | Exit room | Room left only | Entries | Not own fresh kill | Vent waits | Ticks inside 1/2/3/4 | At the cap | In place | Vent at open | Impostor wins | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 22 | 6/8 | 5/8 | 1/8 | 8 | 0/8 | 0 | 8/0/0/0 | 0 | 0 | 0/8 | 7/8 | 48 |
| `observed_risk` exit (`vent_risk`) | 25 | 5/8 | 3/8 | 2/8 | 8 | 0/8 | 0 | 8/0/0/0 | 0 | 0 | 0/8 | 6/8 | 48 |
| `vent_physical` | 22 | 5/8 | 5/8 | 0/8 | 8 | 0/8 | 0 | 8/0/0/0 | 0 | 0 | 0/8 | 7/8 | 48 |
| `vent_look_and_wait` | 25 | 4/7 | 2/7 | 2/7 | 8 | 0/8 | 20 | 3/0/0/4 | 4 | 1 | 4/8 | 5/8 | 48 |
| `vent_own_fresh_kill` | 22 | 6/8 | 5/8 | 1/8 | 8 | 0/8 | 0 | 8/0/0/0 | 0 | 0 | 0/8 | 7/8 | 48 |
| `stage_b_full` | 41 | 2/4 | 2/4 | 0/4 | 8 | 0/8 | 8 | 3/0/0/1 | 1 | 0 | 4/8 | 7/8 | 48 |
| `stage_b_full_minus_look_and_wait` | 34 | 5/8 | 5/8 | 0/8 | 8 | 0/8 | 0 | 8/0/0/0 | 0 | 0 | 0/8 | 7/8 | 48 |
| `stage_b_full_minus_own_fresh_kill` | 41 | 2/4 | 2/4 | 0/4 | 8 | 0/8 | 8 | 3/0/0/1 | 1 | 0 | 4/8 | 7/8 | 48 |
| `stage_b_full_minus_physical` | 41 | 3/4 | 2/4 | 1/4 | 8 | 0/8 | 8 | 3/0/0/1 | 1 | 0 | 4/8 | 7/8 | 48 |
| `stage_b_full_minus_hub_with_grace` | 25 | 2/7 | 2/7 | 0/7 | 8 | 0/8 | 20 | 3/0/0/4 | 4 | 1 | 4/8 | 5/8 | 48 |

#### 9p2i, 8 games per arm

| Arm | Waits | Exposure | Exit room | Room left only | Entries | Not own fresh kill | Vent waits | Ticks inside 1/2/3/4 | At the cap | In place | Vent at open | Impostor wins | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 96 | 16/29 | 13/29 | 3/29 | 29 | 11/29 | 0 | 29/0/0/0 | 0 | 0 | 3/24 | 8/8 | 294 |
| `observed_risk` exit (`vent_risk`) | 106 | 14/34 | 9/34 | 5/34 | 34 | 17/34 | 0 | 34/0/0/0 | 0 | 0 | 6/26 | 8/8 | 308 |
| `vent_physical` | 102 | 13/28 | 13/28 | 0/28 | 28 | 10/28 | 0 | 28/0/0/0 | 0 | 0 | 3/25 | 8/8 | 304 |
| `vent_look_and_wait` | 353 | 13/90 | 3/90 | 10/90 | 91 | 65/91 | 106 | 57/5/4/24 | 24 | 74 | 20/29 | 7/8 | 358 |
| `vent_own_fresh_kill` | 90 | 11/17 | 7/17 | 4/17 | 17 | 0/17 | 0 | 17/0/0/0 | 0 | 0 | 3/25 | 8/8 | 302 |
| `stage_b_full` | 304 | 2/17 | 2/17 | 0/17 | 28 | 0/28 | 29 | 10/1/0/6 | 6 | 13 | 11/20 | 8/8 | 244 |
| `stage_b_full_minus_look_and_wait` | 149 | 8/16 | 8/16 | 0/16 | 19 | 0/19 | 0 | 16/0/0/0 | 0 | 0 | 3/17 | 8/8 | 210 |
| `stage_b_full_minus_own_fresh_kill` | 304 | 3/24 | 3/24 | 0/24 | 43 | 15/43 | 32 | 17/1/0/6 | 6 | 18 | 14/20 | 8/8 | 244 |
| `stage_b_full_minus_physical` | 304 | 2/17 | 2/17 | 0/17 | 28 | 0/28 | 29 | 10/1/0/6 | 6 | 13 | 11/20 | 8/8 | 244 |
| `stage_b_full_minus_hub_with_grace` | 143 | 3/23 | 3/23 | 0/23 | 28 | 0/28 | 52 | 12/1/0/10 | 10 | 15 | 11/27 | 8/8 | 328 |

The readings below are count-only, from 16 fake games per arm. They show mechanics
and make no claim about model reasoning or game balance. A fake meeting ejects
nobody, so the impostors win almost every 9p2i game in every arm.

- **The full set of vent arms.** On 9p2i, `stage_b_full` shows crewmates 2 of
  17 exits, against 16 of 29 at baseline. No exit is seen only from the room
  left, and all 28 entries follow the impostor's own fresh kill. Of the 17
  surfaced trips, 6 end at the cap, and 13 of the 17 exits come back up in the
  room entered from.
- **Look and wait needs the entry gate.** With `vent_look_and_wait` alone the
  impostor still dives at any body. After it surfaces in place beside a body,
  the default cover vents again whenever no one watches. On 9p2i that raises
  entries from 29 to 91, and 65 of the 91 do not follow an own fresh kill; 74 of
  the 90 exits are in place. The minus-own-fresh-kill arm keeps part of this
  loop: 43 entries, 15 of them not after an own fresh kill. The entry gate
  bounds the loop but does not remove it. An impostor that surfaces in place
  beside its own victim may dive once more while the kill is at most three
  ticks old. A dive and a surfacing take two ticks, so that happens at most
  once per kill. A separate walk of the same games counts these re-entries
  (the look-and-wait card's Results give the command; the JSON does not carry
  this count). On 9p2i, 6 of the 28 entries under `stage_b_full` re-enter
  within three ticks of the same impostor's in-place exit, each after its own
  fresh kill. There are 15 of 43 without the gate and 64 of 91 with the look
  alone.
- **The physical rule and the look overlap.** `vent_look_and_wait` alone, under
  the older both-rooms rule, still shows 10 exits seen only from the room left.
  All 10 are exits at the cap with a crewmate in the room left, which the cap
  may leave. With the physical rule there are none. Dropping the physical
  rule from `stage_b_full` changes nothing on 9p2i and adds one room-left
  sighting on 4p1i (3 of 4 exits seen, against 2 of 4).
- **Dropping the look** (`stage_b_full_minus_look_and_wait`) brings back
  one-tick trips only, with 8 of 16 exits seen.
- **Dropping the regroup** (`stage_b_full_minus_hub_with_grace`) leaves trips open
  across meetings. That gives 10 trips at the cap against 6, and 52 waits
  inside a vent against 29.
- **Meetings open more often with an impostor inside a vent**: 11 of 20 under
  `stage_b_full`, against 3 of 24 at baseline. The regroup ends those stays
  without an exit.

### Development: the crew idle-policy cross and whereabouts coverage, 2026-10-06

These rows cross what a finished crewmate does with its spare time under the
rules of the shown 9-player set. A crewmate is finished when it owns no
unfinished task. Every arm here runs the four Stage-B fields that act during a
fake game's play, at kill cooldown 6 unless named otherwise.

- **Hub wait** (`stage_b_full_kill_cooldown_6`, `crew_idle_policy = hub_wait`,
  the default). A finished crewmate waits at the meeting hub.
- **Patrol** (`stage_b_full_kill_cooldown_6_patrol`). A finished crewmate walks
  toward the room it has gone longest without visiting, the nearest first on a
  tie.
- **Accompany** (`stage_b_full_kill_cooldown_6_accompany`). A finished crewmate
  heads for a room where it saw someone in the last two ticks, the latest
  sighting first, unless it visited that room in the last four ticks; otherwise
  it patrols.
- In all three, a finished crewmate still answers a new task, a body it can
  see, a kill it sees, a sabotage that blocks tasks and an available emergency
  button, exactly as before. The two alternatives are the hand-written ones the
  rows above measured under the older rules; nothing about them changed.
- **`stage_b_full`** is the same rules at the map's own kill cooldown, 4 ticks.
  It is the other column of the two cooldown rows read below.

The counts are defined as follows.

- **Whereabouts coverage.** After every play tick, in the state the tick
  leaves, every living player is a subject. A subject is covered when it is not
  inside a vent and at least one other living player, also not inside a vent,
  stands in the same room. This is the engine's rule for who witnesses a kill,
  applied to every player after every tick. It reads where players are, whether
  they are alive and whether they are inside a vent. It reads no role, no seat
  and no sight radius, so it is the same for every role: sharing a room is the
  sight every player has in every visibility mode, and an impostor's wider
  sight is deliberately not used. It counts positions, not what anyone noticed,
  remembered or said, so it is an upper bound on the whereabouts any player
  held. It is the role-blind replacement for the step where the one committed
  training objective measures crew coverage. That objective's
  `patrol_coverage` term pays a crewmate for sharing a room with a player who
  is an impostor, which reads a role. `training/README.md` section 7 records
  that any reopening of the training work redefines that term without reading
  roles before any search; this cell is the measured candidate, and nothing
  here adopts it.
- **At kill ticks** sums the same over the play ticks with at least one kill,
  each tick counted once however many kills it holds. Each killer is one of
  those subjects, covered when anyone stood with it as the tick ended. That is
  company at the end of the tick, not an onlooker at the kill. The engine
  applies a tick's actions in order, so a player who walks in after the kill
  on the same tick covers the killer without having seen the kill, and a
  witness who walks out after the kill can leave the killer uncovered.
  Crew-witnessed kills and the two walk-in counts below read the moment of the
  kill, from the witnesses the engine recorded. **At play ticks** sums it over
  every play tick.
- **Crew-witnessed kills** counts kills a crewmate saw, as the engine recorded
  the kill's witnesses.
- **Walked in** counts, over all kills, the crewmate witnesses who moved into
  the kill's room from another room on the tick of the kill, out of all
  crewmate witnesses. The engine applies a tick's moves and kills in order and
  reads a kill's witnesses when the kill applies, so such a witness arrived
  before the kill. **Kills with a walk-in** counts kills with at least one.
- **Hub waits** counts waits a finished crewmate made at the meeting hub.
- **Task wins** and **parity wins** are read from each game's result: the crew
  finished every task, or the impostors reached parity.
- **Covered share per game** is one game's covered subjects over its subjects
  at kill ticks, shown as the minimum, median and maximum over the games with a
  kill tick.
- **Paired seeds** compare each alternative with hub wait on the same seed:
  among the seeds where both games have a kill tick, how many show the
  alternative's covered share higher, equal or lower; then the same over every
  play tick and every seed. Paired games share a seed and diverge after their
  first differing decision.

Inputs: the wider development split, seeds 1000-1099 on both rosters, which
begins with the eight development seeds above. The held-out split was not run.
Each game runs under the lab's limits (96 ticks, 256 calls, 1,000,000 input and
100,000 output tokens, 30 seconds and $0). The rows are
`stage-b-idle-policy-development.json`. Its runtime fingerprint is
`31814833632ed9cca17a7a3a43afe91082b9a23459925ad5989af73e0fe5a51d` and its git
head is `39e8fea7778497d1e297650aab121562ed59ee1a`. All 800 games completed, and
none aborted or hit a limit; the most any game used was 71 ticks, 52 calls and
220,212 input tokens. The fake provider made 14,190 calls, reporting 52,639,727
input and 815,925 output tokens, at $0. The run took 77 seconds on this machine.
Reproduce into an unused path:

```sh
uv run python -m experiments.tactical_gameplay --split development_wide --arms stage_b_full stage_b_full_kill_cooldown_6 stage_b_full_kill_cooldown_6_patrol stage_b_full_kill_cooldown_6_accompany --output /tmp/stage-b-idle-policy-development.json
```

The first eight seeds of every arm equal a `--split development` run of the
same four arms, row for row. One cooldown-6 game on 9p2i ends in a sabotage
win, so its task and parity wins add up to 99.

#### 4p1i, 100 games per arm

| Arm | Task wins | Parity wins | Tasks done | Kills | Crew-witnessed kills | Walked in | Kills with a walk-in | Meetings | Hub waits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `stage_b_full` | 32 | 68 | 222/300 | 162 | 0 | 0/0 | 0 | 82 | 559 |
| `stage_b_full_kill_cooldown_6` | 71 | 29 | 275/300 | 105 | 1 | 1/1 | 1 | 55 | 751 |
| `stage_b_full_kill_cooldown_6_patrol` | 76 | 24 | 276/300 | 93 | 5 | 5/5 | 5 | 54 | 0 |
| `stage_b_full_kill_cooldown_6_accompany` | 75 | 25 | 275/300 | 94 | 5 | 5/5 | 5 | 54 | 0 |

| Arm | Coverage at kill ticks | Coverage at play ticks | Games without a kill tick | Covered share per game, min / median / max |
| --- | ---: | ---: | ---: | ---: |
| `stage_b_full` | 28/418 (6.7%) | 1569/5045 (31.1%) | 6 | 0.000 / 0.000 / 0.667 |
| `stage_b_full_kill_cooldown_6` | 30/286 (10.5%) | 1888/5230 (36.1%) | 24 | 0.000 / 0.000 / 0.667 |
| `stage_b_full_kill_cooldown_6_patrol` | 42/255 (16.5%) | 1997/5235 (38.1%) | 31 | 0.000 / 0.000 / 0.800 |
| `stage_b_full_kill_cooldown_6_accompany` | 42/257 (16.3%) | 1996/5234 (38.1%) | 31 | 0.000 / 0.000 / 0.800 |

| Alternative, against hub wait | Seeds with a kill tick in both | Kill ticks higher / equal / lower | Seeds | Play ticks higher / equal / lower |
| --- | ---: | ---: | ---: | ---: |
| `stage_b_full_kill_cooldown_6_patrol` | 66 | 13 / 48 / 5 | 100 | 54 / 11 / 35 |
| `stage_b_full_kill_cooldown_6_accompany` | 66 | 13 / 48 / 5 | 100 | 52 / 11 / 37 |

#### 9p2i, 100 games per arm

| Arm | Task wins | Parity wins | Tasks done | Kills | Crew-witnessed kills | Walked in | Kills with a walk-in | Meetings | Hub waits |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `stage_b_full` | 4 | 96 | 1020/1399 | 497 | 17 | 20/20 | 17 | 228 | 2714 |
| `stage_b_full_kill_cooldown_6` | 27 | 72 | 1253/1400 | 457 | 32 | 45/45 | 32 | 254 | 4840 |
| `stage_b_full_kill_cooldown_6_patrol` | 31 | 69 | 1256/1399 | 445 | 45 | 54/54 | 45 | 262 | 0 |
| `stage_b_full_kill_cooldown_6_accompany` | 34 | 66 | 1277/1399 | 444 | 47 | 53/53 | 47 | 260 | 0 |

| Arm | Coverage at kill ticks | Coverage at play ticks | Games without a kill tick | Covered share per game, min / median / max |
| --- | ---: | ---: | ---: | ---: |
| `stage_b_full` | 1479/2862 (51.7%) | 14143/22414 (63.1%) | 0 | 0.083 / 0.533 / 0.846 |
| `stage_b_full_kill_cooldown_6` | 1650/2713 (60.8%) | 20361/30401 (67.0%) | 0 | 0.200 / 0.600 / 0.900 |
| `stage_b_full_kill_cooldown_6_patrol` | 1353/2624 (51.6%) | 17095/28247 (60.5%) | 0 | 0.227 / 0.511 / 0.767 |
| `stage_b_full_kill_cooldown_6_accompany` | 1397/2613 (53.5%) | 17467/28474 (61.3%) | 0 | 0.200 / 0.533 / 0.818 |

| Alternative, against hub wait | Seeds with a kill tick in both | Kill ticks higher / equal / lower | Seeds | Play ticks higher / equal / lower |
| --- | ---: | ---: | ---: | ---: |
| `stage_b_full_kill_cooldown_6_patrol` | 100 | 17 / 6 / 77 | 100 | 7 / 0 / 93 |
| `stage_b_full_kill_cooldown_6_accompany` | 100 | 22 / 8 / 70 | 100 | 10 / 0 / 90 |

The readings below are count-only, from 100 fake games per arm and roster. A
fake meeting ejects nobody, so the race, the kills and the coverage are
play-layer mechanics, not model play and not balance. The coverage figures are
reported, never a bar or a reward. Kills and meetings are read beside them,
as floors and never as rewards, because a crew that clumps together can raise
coverage while cutting kills and meetings.

- **Coverage, hub wait / patrol / accompany.** On 9p2i, at kill ticks, 60.8%,
  51.6% and 53.5% of subjects are covered, and over every play tick 67.0%,
  60.5% and 61.3%. On 4p1i, at kill ticks, 10.5%, 16.5% and 16.3%, and over
  every play tick 36.1%, 38.1% and 38.1%.
- **Paired seeds.** On 9p2i, patrol's covered share at kill ticks is below hub
  wait's on 77 of the 100 seeds (above on 17, equal on 6), and accompany's on
  70 (above on 22, equal on 8). Over every play tick they are below on 93 and
  90 of 100. On 4p1i, of the 66 seeds where both games have a kill tick, both
  alternatives are above hub wait on 13, equal on 48 and below on 5; over every
  play tick patrol is above on 54 of 100 (accompany 52), equal on 11 and below
  on 35 (37).
- **The best arm's uncovered remainder.** On 9p2i the best of the three at kill
  ticks is hub wait itself: 1,063 of its 2,713 subjects (39.2%) are uncovered.
  On 4p1i it is patrol: 213 of 255 (83.5%). That remainder is an upper bound on
  what any idle policy, hand-written or learned, could still cover in this cell
  under these rules. Whether a learned policy could cover any of it is not
  measured.
- **What the cross shows.** On the 9-player roster neither hand-written
  alternative raises whereabouts coverage. Waiting at the hub keeps more
  players in company than walking about does, at kill ticks and over the whole
  game. On the 4-player roster both raise it at kill ticks, from 10.5% to 16.5%
  and 16.3%, but 48 of the 66 paired seeds read equal. Walking about does put more
  crewmates where kills happen: on 9p2i crew-witnessed kills rise from 32 of
  457 to 45 of 445 (patrol) and 47 of 444 (accompany). Beside that, kills fall
  slightly (457 to 445 and 444) and meetings rise slightly (254 to 262 and
  260). Hub waits fall from 4,840 to 0. **This reading decides nothing about
  ML**; the hold on ML stands whatever it reads.
- **The two cooldown rows, as mechanics.** At the map's own cooldown of 4 ticks
  (`stage_b_full`) a crewmate saw 17 of 497 kills on 9p2i; at 6 ticks it saw
  32 of 457. In both, every crewmate witness walked into the kill's room on the
  kill tick (20 of 20 and 45 of 45), and every crew-witnessed kill had such a
  witness. On 4p1i it is 0 of 162 against 1 of 105. These are fake games, and a
  fake meeting ejects nobody, so the rise in the recorded hosted games, from 4
  of 227 kills a crewmate saw in the first Stage-B candidate round to 14 of 195
  in the shown 9-player set, is neither confirmed nor explained here.

Every count comes from the recordings the lab walked, with every tick and
meeting hash verified. This check reproduces every cell of the six tables
above from the JSON, in the order shown:

```python
import json
from collections import Counter
from pathlib import Path

data = json.loads(
    Path("audits/tactical-gameplay/stage-b-idle-policy-development.json").read_text()
)
arms = ("stage_b_full", "stage_b_full_kill_cooldown_6",
        "stage_b_full_kill_cooldown_6_patrol", "stage_b_full_kill_cooldown_6_accompany")
cell = lambda a, b: f"{a}/{b} ({100 * a / b:.1f}%)"
for roster in ("4p1i", "9p2i"):
    print(roster)
    for arm in arms:
        games = data["arms"][arm]["sets"][roster]
        c, wins = Counter(), Counter(game["reason"] for game in games)
        for game in games:
            c.update(game["counts"])
        print(f"| `{arm}` | {wins['CREWMATE_TASKS']} | {wins['IMPOSTOR_PARITY']} "
              f"| {c['terminal_tasks_completed']}/{c['terminal_tasks_total']} "
              f"| {c['event:Killed']} | {c['kills_crew_witnessed']} "
              f"| {c['crew_kill_witnesses_walked_in']}/{c['crew_kill_witnesses']} "
              f"| {c['kills_with_walk_in_crew_witness']} | {c['meetings']} "
              f"| {c['finished_crew_applied_waits_at_hub']} |")
    for arm in arms:
        s = data["whereabouts_coverage"][arm][roster]
        shares = [s[f"kill_tick_share_{k}"] for k in ("minimum", "median", "maximum")]
        print(f"| `{arm}` "
              f"| {cell(s['whereabouts_covered_at_kill_ticks'], s['whereabouts_subjects_at_kill_ticks'])} "
              f"| {cell(s['whereabouts_covered_at_play_ticks'], s['whereabouts_subjects_at_play_ticks'])} "
              f"| {s['games_without_a_kill_tick']} | {' / '.join(f'{v:.3f}' for v in shares)} |")
    for arm in arms[2:]:
        p = data["idle_policy_pairs"][arm][roster]
        print(f"| `{arm}` | {p['seeds_with_a_kill_tick_in_both']} "
              f"| {p['kill_tick_share_higher']} / {p['kill_tick_share_equal']} / {p['kill_tick_share_lower']} "
              f"| {p['seeds']} "
              f"| {p['play_tick_share_higher']} / {p['play_tick_share_equal']} / {p['play_tick_share_lower']} |")
```

### Held-out: 4p1i, 16 games per arm

| Arm | Waits | Reversals | Exposure | Allocations | Reactor starts | Task wins | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 71 | 7 | 6/14 | 4/18 | 0 | 7 | 78 |
| Least-work allocation | 45 | 7 | 6/14 | 0/16 | 0 | 10 | 72 |
| Patrol | 0 | 9 | 8/14 | 3/19 | 0 | 10 | 72 |
| Brief accompaniment | 0 | 8 | 8/14 | 3/18 | 0 | 11 | 72 |
| Observed vent risk | 73 | 6 | 5/14 | 4/16 | 0 | 7 | 78 |
| Meeting follow-through | 64 | 5 | 6/14 | 4/17 | 0 | 7 | 78 |
| Regroup with grace | 110 | 9 | 6/14 | 4/15 | 0 | 8 | 78 |
| Self-report | 79 | 10 | 0/0 | 4/16 | 0 | 8 | 90 |
| Earlier sabotage | 77 | 12 | 7/15 | 4/20 | 13 | 3 | 84 |

### Held-out: 9p2i, 16 games per arm

| Arm | Waits | Reversals | Exposure | Allocations | Reactor starts | Task wins | Calls |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | 233 | 65 | 32/53 | 103/133 | 5 | 1 | 676 |
| Least-work allocation | 68 | 48 | 47/55 | 0/121 | 4 | 2 | 754 |
| Patrol | 0 | 60 | 36/47 | 106/129 | 3 | 2 | 698 |
| Brief accompaniment | 0 | 62 | 31/43 | 106/130 | 3 | 2 | 674 |
| Observed vent risk | 299 | 67 | 33/61 | 103/136 | 8 | 1 | 738 |
| Meeting follow-through | 230 | 62 | 35/52 | 104/135 | 5 | 0 | 666 |
| Regroup with grace | 341 | 56 | 27/45 | 99/130 | 6 | 0 | 484 |
| Self-report | 185 | 55 | 0/0 | 85/119 | 6 | 1 | 808 |
| Earlier sabotage | 152 | 62 | 29/50 | 103/131 | 9 | 0 | 686 |

## Decisions and limits

| Area | Disposition and evidence |
| --- | --- |
| Workload allocation | Implemented, experimental. Held-out waits fall from 71→45 and 233→68; above-minimum allocations become zero. Larger-game witnessed exits rise from 32/53 to 47/55, so better task distribution does not imply better concealment or global balance. |
| Finished-crew purpose | Patrol and brief accompaniment are implemented, experimental. Both remove observed waiting and pass new-task/body/repair interrupts and exploration controls. Held-out 9p exposure rises from 32/53 to 36/47 or 31/43. Accompaniment consumes a visit opportunity and resumes exploration; it is not a permanent escort. |
| Vent choice | Implemented, experimental. Uses only recent first-hand non-teammate sightings and still leaves when every exit is risky. Held-out 9p exposure rate falls from 32/53 to 33/61, but total witnessed exits and waiting rise; no empty-room oracle or clean global improvement is claimed. |
| Meeting follow-through | Implemented, experimental. Keeps recent unrefuted leads only when locations are preserved and public survivors remain eligible. Held-out waits shift 71→64 / 233→230; the 9p task win disappears. Reset disables the preserved-location assumption. |
| Meeting reset | Implemented, experimental. One combined intervention regroups survivors, clears all bodies and vent occupancy, stops actions and restores full kill grace; task progress, sabotage and emergency uses remain. Held-out waits rise to 110/341. It cannot be described as a cosmetic location reset. Note of 2026-09-26: this row and its screen counts measured the arm before [the reset coherence card](../../tasks/work/meeting-reset-coherence.md) changed what agents perceive and remember after a regroup (the resume packet, the announced regroup on the default evidence path, the regroup relevance window). They are not regenerated: a later change never re-scores an earlier screen. |
| Self-report and role tells | Implemented, experimental tactical eligibility. Impostors call 15/15 and 55/63 held-out meetings, versus zero baseline callers, removing that absolute action-policy tell. Vent exits disappear and calls rise. This does not remove inherent witnessed-kill/vent proof or prove better deception. Existing impostor-roll-call verdicts and unresolved sibling-template composition limits remain unchanged. |
| Sabotage/task contribution | Earlier threshold implemented, experimental. In 4p it creates 13 held-out reactor starts and reduces fake crew task wins from 7→3; no sabotage win occurs. In 9p, starts rise 5→9 and the task win disappears. Kill priority and the existing rearm rule remain; this is a balance tradeoff. |
| Anti-oscillation | Retain the baseline; the scoped guard and config key are deleted. All 16 paired development trajectories and counts were unchanged, and their baseline trajectories match the final source. Fixed goals already reduce shortest-path distance. New repair goals and body escapes can legitimately reverse a move. |
| Identity-dependent order | Retain deterministic order; quantified below. Neither random priorities nor whole-game counterfactual outcomes are adopted. |
| RNG/mapping work | Retain current implementation. RNG reconstruction already avoids initialization. Five safe mapping copies remain; measured below. |
| Vent look and wait (2026-09-26) | `observed_risk` loses its mechanism when `look_and_wait` is adopted: both are values of `vent_exit_policy`, and the look replaces the risk-ranked exit. Adoption is the owner's decision after the round-1 record. Until then both stay selectable, and the observed-risk rows above stay as evidence. |

Every candidate remains available only for an explicitly selected comparison.
A future promotion needs source-pinned gameplay review, interaction/entitlement
checks and authorized fresh model responses on disjoint inputs. This screen
authorizes no fit, live model call, new protocol or adoption. A rejected candidate
must lose its mechanism while preserving its evidence, as the inert guard did.

## Coherent identity interventions

Each recorded transition is rerun twice, rotating IDs by one and reversing them.
Roles, positions, cooldowns, task ownership, player references and intentions
move together; RNG state and the map stay fixed. Actions are then sorted by
the real actor-ID rule. This includes identity-dependent allocation effects;
it does not isolate action ordering from task ownership tie-breaks. These are
one-transition interventions, not resimulated meetings or model win estimates.

| Set / permutation | Changed action dispositions | Changed survival | Changed phase | Changed task state |
| --- | ---: | ---: | ---: | ---: |
| 4p1i / rotate | 64/536 | 2/536 | 2/536 | 52/536 |
| 4p1i / reverse | 103/536 | 2/536 | 3/536 | 65/536 |
| 9p2i / rotate | 176/1239 | 14/1239 | 0/1239 | 195/1239 |
| 9p2i / reverse | 370/1239 | 70/1239 | 6/1239 | 296/1239 |

## Retained controls and validation

The warmed copy control measured 3.586 µs per WorldState replacement and
1.542 µs for the separate five-mapping-copy operation on this machine.
Each is the median of five 5,000-iteration loops. The second is not a causal
percentage of the first. Values and RNG bytes are preserved; externally
mutating an input mapping proxy cannot change the state. No optimization or
latency CI threshold is introduced.

`retained-controls.json` preserves the abandoned guard comparison as dated
exploratory evidence. Its earlier fingerprint covered Python/map/harness only;
it predates the expanded template/lock identity. The discarded implementation
is intentionally not callable, and that negative screen is not presented as a
rerunnable current arm. Current task-progress, legitimate-reversal and unknown-
configuration controls remain executable.

Independent review found a roster read/fingerprint race. The repaired harness
parses the exact captured bytes and validates them before games and after the
screen. A transient A→B→A input test fails before work. The final 49 focused
tests pass, including all 15 harness tests; the broader affected selection
passed 258 tests with three existing xfails. Ruff, format checks and strict mypy
pass for 13 owned source/test files. The coordinating agent owns the combined
full-project gate.

```sh
uv run pytest tests/agents/test_tactical_experiments.py tests/engine/test_redistribution_experiments.py tests/engine/test_meeting_reset_experiment.py tests/orchestrator/test_experiment_config.py tests/experiments/test_tactical_gameplay.py
```

Table cells are sums of each row’s `counts` fields, with winning reasons and
`model_calls` read directly. A compact check over the committed JSON is:

```python
import json
from collections import Counter
from pathlib import Path
data = json.loads(Path("audits/tactical-gameplay/held-out.json").read_text())
for arm, record in data["arms"].items():
    for roster, games in record["sets"].items():
        totals = Counter()
        for game in games:
            totals.update(game["counts"])
        print(arm, roster, dict(totals), sum(g["model_calls"] for g in games))
```
