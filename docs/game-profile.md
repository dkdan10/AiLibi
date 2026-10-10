# The game-shape profile

**This is a description of each game, not a score.** It has no score, no rank, no total and no zeroing floor. Shelves come in one fixed order and list their games in seed order, so nothing here orders a game by anything but its seed.

**Role-correctness is reported here and gates nothing.** No module under `agents`, `meetings`, `orchestrator`, `engine` or `training` may import the profile (`.importlinter`), and no pre-registration, step rule, gate or objective reads it. It is computed after the fact from committed bytes.

This page is generated. Do not edit it by hand: run `uv run python scripts/publish_game_profile.py` and commit the result. `uv run python scripts/publish_game_profile.py --check` recomputes this page and each served `results-game-profile.json` from the recordings and fails on drift, and `uv run python scripts/publish_game_profile.py --set-dir DIR --json-stdout` profiles one other 9-player directory and writes nothing. The four-player set ships no profile: its shelves would degenerate on a table that small.

## Definitions

Every definition reads committed bytes through the gameplay census's carrier and scorecard row 3's helpers. The constants are frozen for this profile version (2); a change to any of them needs a new version.

**Shelves before the reveal.** Each reads what the table held and did (ballots, grounding labels, cited ids, accusations, flags, meetings) and the engine's physical record (kills, the engine's witness lists, bodies, regroups), and no role and no ending.

* **The reporter saw it happen**: a report meeting opened by a player in the engine's witness list for the kill of the body reported, the body joined to its kill by victim.
* **Double kill**: two kills on the same tick.
* **Slow burn**: a stretch of at least 20 ticks with no kill, counted from tick 0, between kills or to the end.
* **Two kills after one regroup**: two kills inside one regroup's wave. A kill is in the wave of the last regroup before it when it lands more than the recorded kill cooldown, and at most 4 ticks past it, after that regroup.
* **A close call**: a meeting whose leading choice, a player or SKIP, beat the runner-up by at most 1 ballot.
* **Suspicion moved**: across two consecutive meetings, a player who drew EJECT ballots earlier is ejected later; or a player who drew EJECT ballots draws none, and no accusation, while alive; or the leading EJECT target changes while the old lead lives. Read from ballots and accusations, never from the engine's suspicion number.
* **A third round**: at least 3 meetings.
* **Caught venting**: a meeting with a vent-sighting flag.
* **One line, two readings**: two ballots labelled supported, holds-nothing or off-target cite the same turn and name different targets.
* **Struck after the regroup**: any kill in a regroup's wave.

Every one of them is a candidate. The publisher classes each per era:

* **The saturation rule**, applied first: a candidate holding more than 3 in 4 of the era's games is a facet, never a shelf.
* **The leak rule**: each candidate's membership is tested by a two-sided Fisher exact test against each recorded ending, against some meeting having ejected someone and against a crewmate having been ejected, over every game of the era, a game on a tripwire counted as a non-member. Any p below 0.05 puts the candidate behind the reveal for that era. The rule can only hide more; it never selects or orders a game.

**Shelves behind the reveal** read an ejection, the ending or a role:

* **One-vote ejection**: an ejection by a margin of one, SKIP counted as a choice.
* **Nobody voted out**: every meeting skipped.
* **Down to the wire**: the losing side was one step from its own ending, having started at least 3 steps away.
* **Runaway**: the losing side was still at least 1 in 2 of its starting distance from its ending.
* The distance is measured the same way for each side: an impostor win counts the crew's tasks left; a task win counts the impostors' kills short of parity at game over; an ejection win counts their kills short of parity at the deciding meeting.
* **Decided at a meeting**: the game ended at a meeting.
* **Decided without proof**: an ejection whose ejecting ballots are all labelled supported or flag-only, where no vent flag and no manufactured flag names the ejected player. The reveal splits it by the ejected player's role into two halves, always shown together: the table was right, and wrong on what it held. A wrong call on lines the voters held and believed is part of the game, shown beside its right twin; it is reported and gates nothing.

**The chip.** *An eyewitness voted on it* marks a meeting where some player's ballot cites the own-kill row that player held. It places a game on no shelf and takes no leak or saturation class.

**Facets.** Before the reveal: length in ticks; meetings, by what opened them; the kill timeline, with regroups and the wave; reports, with the corpse's age; bodies never found. Behind it: the ending; the losing side's distance from its ending; sabotages in play, with the final task count; each ejection, right or wrong. A sabotage is in play from the first tick it is active on the engine's frame, so one started on a game's final tick is never in play.

**Tripwires.** A game that trips one sits on no shelf, keeps a plain label and stays under All games; it is never hidden and never scored.

* **Decided by a vote that held nothing**: with the ejecting ballots labelled off-target, uncited or invalid-citation removed, the game's own tally at the meeting's recorded confidence floor ejects no one or someone else. Supported and flag-only ballots are held; not-assessed ballots stay as recorded. An ejecting ballot labelled as holding nothing is a case the tripwire does not classify, so it stops the publisher, naming the set, the seed, the meeting and the voter, until the owner says how it reads.
* **Decided on a manufactured contradiction**: the ejected player is named by an alibi-class flag that row 3 classes as manufactured over the engine's route. Row 3 can answer few flags, so this tripwire is nearly blind.

## `replays/samples/9p2i`

* rubric version: 2
* era: `stage-b-r3`
* MANIFEST key: `641b4254`
* source fingerprint: `sha256:ea53a00f4c59aa23dd6c014c92443b36049ee192ec8a33e07d3ca69301f55329`
* seedset: `9p2i`
* games: 50

### Tripwires

| reading | ejections | games | entries (seed, meeting index) |
| --- | --- | --- | --- |
| decisive, the governing reading: the ejecting ballots labelled off-target, uncited or invalid-citation removed | 0 | 0 | none |
| decisive, those ballots read as SKIP instead | 0 | 0 | none |
| decisive, every ballot so labelled removed, whatever its target | 0 | 0 | none |
| every ejecting ballot so labelled | 0 | 0 | none |
| any ejecting ballot so labelled | 1 | 1 | (44, 0) |
| the ejected player named by an alibi-class flag row 3 classes as manufactured | 0 | 0 | none |

The governing readings trip no game. Row 3 can answer 0 of this set's 15 alibi-class flags, so the manufactured-contradiction tripwire is nearly blind here.

### Shelves before the reveal

| shelf | games | seeds |
| --- | --- | --- |
| The reporter saw it happen | 13 | 0, 7, 19, 23, 28, 29, 30, 32, 35, 38, 43, 45, 46 |
| Double kill | 7 | 1, 3, 4, 8, 21, 24, 32 |
| Slow burn | 15 | 5, 6, 8, 16, 17, 18, 19, 20, 22, 28, 32, 34, 39, 45, 46 |
| Suspicion moved | 16 | 0, 8, 13, 17, 21, 24, 26, 28, 30, 32, 34, 35, 36, 39, 40, 49 |
| A third round | 22 | 0, 3, 8, 9, 13, 15, 17, 18, 19, 20, 21, 22, 26, 28, 32, 37, 39, 41, 45, 46, 48, 49 |

*An eyewitness voted on it* marks 14 meetings in 13 games: 0, 7, 19, 23, 28, 29, 30, 32, 35, 38, 43, 45, 46.

Games on no tripwire, by how many shelves before the reveal they sit on: 12 on 0, 17 on 1, 11 on 2, 7 on 3, 2 on 4, 1 on 5.

### Shelves behind the reveal

| shelf | games | seeds |
| --- | --- | --- |
| Two kills after one regroup | 8 | 0, 1, 2, 4, 12, 26, 36, 38 |
| A close call | 16 | 0, 1, 2, 8, 21, 22, 24, 25, 30, 33, 35, 37, 43, 45, 46, 49 |
| Caught venting | 19 | 0, 3, 5, 6, 7, 9, 10, 11, 18, 19, 20, 21, 22, 27, 37, 39, 42, 45, 49 |
| One line, two readings | 24 | 0, 2, 3, 5, 6, 9, 10, 11, 13, 17, 18, 19, 20, 21, 22, 23, 27, 28, 32, 34, 37, 42, 45, 49 |
| One-vote ejection | 9 | 0, 1, 21, 22, 24, 25, 33, 37, 45 |
| Nobody voted out | 8 | 2, 4, 15, 26, 31, 34, 36, 48 |
| Down to the wire | 12 | 0, 3, 15, 17, 18, 20, 26, 28, 29, 37, 41, 45 |
| Runaway | 14 | 5, 6, 7, 9, 10, 11, 14, 16, 27, 40, 42, 44, 47, 49 |
| Decided at a meeting | 15 | 0, 5, 7, 9, 10, 11, 16, 19, 21, 23, 27, 37, 45, 47, 49 |
| Decided without proof: the table was right | 19 (21 ejections) | 0, 7, 8, 9, 13, 14, 16, 17, 19, 21, 28, 32, 33, 37, 40, 41, 45, 46, 47 |
| Decided without proof: wrong on what it held | 14 (15 ejections) | 1, 12, 13, 17, 22, 23, 24, 25, 29, 30, 33, 35, 38, 43 |

### Classes this era

Each row is one 2x2 table over every game of the era: members holding the fact, members without it, non-members holding it, non-members without it, and the two-sided p.

| candidate | games on it | fact | table | p | class |
| --- | --- | --- | --- | --- | --- |
| The reporter saw it happen | 13 of 50 | CREWMATE_TASKS | 4, 9, 15, 22 | 0.7415 | a shelf before the reveal |
| The reporter saw it happen | 13 of 50 | CREWMATE_EJECT | 4, 9, 10, 27 | 1.0000 | a shelf before the reveal |
| The reporter saw it happen | 13 of 50 | IMPOSTOR_PARITY | 5, 8, 12, 25 | 0.7413 | a shelf before the reveal |
| The reporter saw it happen | 13 of 50 | some meeting ejected someone | 13, 0, 29, 8 | 0.0928 | a shelf before the reveal |
| The reporter saw it happen | 13 of 50 | a crewmate was ejected | 6, 7, 8, 29 | 0.1489 | a shelf before the reveal |
| Double kill | 7 of 50 | CREWMATE_TASKS | 2, 5, 17, 26 | 0.6948 | a shelf before the reveal |
| Double kill | 7 of 50 | CREWMATE_EJECT | 1, 6, 13, 30 | 0.6565 | a shelf before the reveal |
| Double kill | 7 of 50 | IMPOSTOR_PARITY | 4, 3, 13, 30 | 0.2098 | a shelf before the reveal |
| Double kill | 7 of 50 | some meeting ejected someone | 6, 1, 36, 7 | 1.0000 | a shelf before the reveal |
| Double kill | 7 of 50 | a crewmate was ejected | 2, 5, 12, 31 | 1.0000 | a shelf before the reveal |
| Slow burn | 15 of 50 | CREWMATE_TASKS | 9, 6, 10, 25 | 0.0564 | a shelf before the reveal |
| Slow burn | 15 of 50 | CREWMATE_EJECT | 4, 11, 10, 25 | 1.0000 | a shelf before the reveal |
| Slow burn | 15 of 50 | IMPOSTOR_PARITY | 2, 13, 15, 20 | 0.0555 | a shelf before the reveal |
| Slow burn | 15 of 50 | some meeting ejected someone | 14, 1, 28, 7 | 0.4074 | a shelf before the reveal |
| Slow burn | 15 of 50 | a crewmate was ejected | 2, 13, 12, 23 | 0.1787 | a shelf before the reveal |
| Two kills after one regroup | 8 of 50 | CREWMATE_TASKS | 1, 7, 18, 24 | 0.1343 | behind the reveal, by the leak rule |
| Two kills after one regroup | 8 of 50 | CREWMATE_EJECT | 1, 7, 13, 29 | 0.4143 | behind the reveal, by the leak rule |
| Two kills after one regroup | 8 of 50 | IMPOSTOR_PARITY | 6, 2, 11, 31 | 0.0134 | behind the reveal, by the leak rule |
| Two kills after one regroup | 8 of 50 | some meeting ejected someone | 4, 4, 38, 4 | 0.0158 | behind the reveal, by the leak rule |
| Two kills after one regroup | 8 of 50 | a crewmate was ejected | 3, 5, 11, 31 | 0.6699 | behind the reveal, by the leak rule |
| A close call | 16 of 50 | CREWMATE_TASKS | 2, 14, 17, 17 | 0.0134 | behind the reveal, by the leak rule |
| A close call | 16 of 50 | CREWMATE_EJECT | 5, 11, 9, 25 | 0.7455 | behind the reveal, by the leak rule |
| A close call | 16 of 50 | IMPOSTOR_PARITY | 9, 7, 8, 26 | 0.0299 | behind the reveal, by the leak rule |
| A close call | 16 of 50 | some meeting ejected someone | 15, 1, 27, 7 | 0.4092 | behind the reveal, by the leak rule |
| A close call | 16 of 50 | a crewmate was ejected | 8, 8, 6, 28 | 0.0396 | behind the reveal, by the leak rule |
| Suspicion moved | 16 of 50 | CREWMATE_TASKS | 9, 7, 10, 24 | 0.1171 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | CREWMATE_EJECT | 3, 13, 11, 23 | 0.5012 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | IMPOSTOR_PARITY | 4, 12, 13, 21 | 0.5241 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | some meeting ejected someone | 13, 3, 29, 5 | 0.6994 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | a crewmate was ejected | 5, 11, 9, 25 | 0.7455 | a shelf before the reveal |
| A third round | 22 of 50 | CREWMATE_TASKS | 11, 11, 8, 20 | 0.1501 | a shelf before the reveal |
| A third round | 22 of 50 | CREWMATE_EJECT | 7, 15, 7, 21 | 0.7527 | a shelf before the reveal |
| A third round | 22 of 50 | IMPOSTOR_PARITY | 4, 18, 13, 15 | 0.0696 | a shelf before the reveal |
| A third round | 22 of 50 | some meeting ejected someone | 19, 3, 23, 5 | 1.0000 | a shelf before the reveal |
| A third round | 22 of 50 | a crewmate was ejected | 3, 19, 11, 17 | 0.0605 | a shelf before the reveal |
| Caught venting | 19 of 50 | CREWMATE_TASKS | 4, 15, 15, 16 | 0.0742 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | CREWMATE_EJECT | 12, 7, 2, 29 | under 0.0001 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | IMPOSTOR_PARITY | 3, 16, 14, 17 | 0.0632 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | some meeting ejected someone | 19, 0, 23, 8 | 0.0177 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | a crewmate was ejected | 1, 18, 13, 18 | 0.0079 | behind the reveal, by the leak rule |
| One line, two readings | 24 of 50 | CREWMATE_TASKS | 8, 16, 11, 15 | 0.5700 | behind the reveal, by the leak rule |
| One line, two readings | 24 of 50 | CREWMATE_EJECT | 11, 13, 3, 23 | 0.0110 | behind the reveal, by the leak rule |
| One line, two readings | 24 of 50 | IMPOSTOR_PARITY | 5, 19, 12, 14 | 0.0775 | behind the reveal, by the leak rule |
| One line, two readings | 24 of 50 | some meeting ejected someone | 22, 2, 20, 6 | 0.2503 | behind the reveal, by the leak rule |
| One line, two readings | 24 of 50 | a crewmate was ejected | 4, 20, 10, 16 | 0.1192 | behind the reveal, by the leak rule |
| Struck after the regroup | 41 of 50 | CREWMATE_TASKS | 14, 27, 5, 4 | 0.2729 | a facet, by the saturation rule |
| Struck after the regroup | 41 of 50 | CREWMATE_EJECT | 10, 31, 4, 5 | 0.2447 | a facet, by the saturation rule |
| Struck after the regroup | 41 of 50 | IMPOSTOR_PARITY | 17, 24, 0, 9 | 0.0198 | a facet, by the saturation rule |
| Struck after the regroup | 41 of 50 | some meeting ejected someone | 33, 8, 9, 0 | 0.3216 | a facet, by the saturation rule |
| Struck after the regroup | 41 of 50 | a crewmate was ejected | 13, 28, 1, 8 | 0.4138 | a facet, by the saturation rule |

### The lean of the shelf count

Never served and never used to order a game: the mean number of shelves before the reveal per game on no tripwire, by ending.

| ending | games | mean shelves |
| --- | --- | --- |
| `CREWMATE_EJECT` | 14 | 1.36 |
| `CREWMATE_TASKS` | 19 | 1.84 |
| `IMPOSTOR_PARITY` | 17 | 1.12 |

## Limitations

* One recording of 50 games per set, and no interval is claimed.
* The classes swing between eras, which is why they are recomputed per era and recorded in the served file.
* The constants were chosen with these numbers in view, and the leak level is not corrected for the many tests it is applied to, so a false leak verdict is plausible. The rule errs in one direction only: it can only hide more.
* The facets the viewer already shows before the reveal (the length, the meetings) carry some information about the ending.
* A ballot labelled as holding nothing is the voter's own statement. An ejecting one stops the publisher until the owner says how the tripwire reads it.
* The manufactured-contradiction tripwire is nearly blind.
* *Wrong on what it held* reads the grounding labels, not whether the cited line is true; the gameplay census measures that, and the profile does not read it.
* The chip is not leak-tested; the leak rule covers shelves.
