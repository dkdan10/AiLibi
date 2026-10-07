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
* era: `stage-b-r2`
* MANIFEST key: `43b5ee45`
* source fingerprint: `sha256:ebb629f67c36607e39733660db7e069729fff198adcf34c091a4d6252d796ae2`
* seedset: `9p2i`
* games: 50

### Tripwires

| reading | ejections | games | entries (seed, meeting index) |
| --- | --- | --- | --- |
| decisive, the governing reading: the ejecting ballots labelled off-target, uncited or invalid-citation removed | 1 | 1 | (26, 2) |
| decisive, those ballots read as SKIP instead | 1 | 1 | (26, 2) |
| decisive, every ballot so labelled removed, whatever its target | 1 | 1 | (26, 2) |
| every ejecting ballot so labelled | 0 | 0 | none |
| any ejecting ballot so labelled | 2 | 2 | (26, 2), (41, 0) |
| the ejected player named by an alibi-class flag row 3 classes as manufactured | 0 | 0 | none |

The governing readings trip seed 26. Row 3 can answer 1 of this set's 15 alibi-class flags, so the manufactured-contradiction tripwire is nearly blind here.

### Shelves before the reveal

| shelf | games | seeds |
| --- | --- | --- |
| The reporter saw it happen | 14 | 0, 1, 7, 9, 16, 19, 23, 28, 29, 30, 32, 35, 38, 43 |
| Double kill | 7 | 1, 3, 4, 8, 21, 24, 32 |
| Slow burn | 11 | 1, 5, 6, 8, 18, 19, 22, 25, 32, 39, 47 |
| Two kills after one regroup | 6 | 0, 4, 12, 13, 16, 36 |
| A close call | 16 | 0, 1, 9, 16, 21, 22, 23, 24, 25, 31, 36, 37, 38, 41, 43, 47 |
| Suspicion moved | 16 | 0, 1, 7, 8, 9, 13, 18, 21, 25, 30, 34, 35, 38, 39, 40, 47 |
| A third round | 19 | 0, 1, 3, 8, 9, 15, 16, 17, 18, 19, 22, 24, 32, 37, 38, 39, 41, 47, 49 |

*An eyewitness voted on it* marks 15 meetings in 14 games: 0, 1, 7, 9, 16, 19, 23, 28, 29, 30, 32, 35, 38, 43.

Games on no tripwire, by how many shelves before the reveal they sit on: 12 on 0, 11 on 1, 11 on 2, 7 on 3, 6 on 4, 1 on 5, 1 on 6.

### Shelves behind the reveal

| shelf | games | seeds |
| --- | --- | --- |
| Caught venting | 19 | 0, 3, 5, 6, 7, 9, 10, 11, 13, 18, 19, 20, 22, 27, 34, 37, 39, 42, 49 |
| One line, two readings | 20 | 2, 3, 5, 9, 11, 13, 18, 19, 20, 21, 22, 24, 32, 34, 36, 37, 38, 39, 43, 49 |
| One-vote ejection | 10 | 0, 1, 9, 16, 22, 23, 24, 37, 43, 47 |
| Nobody voted out | 4 | 4, 15, 31, 36 |
| Down to the wire | 12 | 0, 3, 8, 9, 13, 15, 16, 18, 29, 37, 38, 41 |
| Runaway | 14 | 5, 6, 7, 10, 11, 14, 17, 20, 27, 34, 40, 42, 44, 49 |
| Decided at a meeting | 14 | 0, 1, 5, 7, 9, 10, 11, 19, 20, 27, 34, 37, 48, 49 |
| Decided without proof: the table was right | 18 (19 ejections) | 0, 1, 7, 8, 9, 14, 16, 17, 19, 20, 24, 32, 34, 37, 38, 40, 44, 47 |
| Decided without proof: wrong on what it held | 20 (21 ejections) | 2, 8, 9, 12, 13, 21, 22, 23, 24, 25, 28, 29, 30, 33, 35, 39, 43, 45, 46, 48 |

### Classes this era

Each row is one 2x2 table over every game of the era: members holding the fact, members without it, non-members holding it, non-members without it, and the two-sided p.

| candidate | games on it | fact | table | p | class |
| --- | --- | --- | --- | --- | --- |
| The reporter saw it happen | 14 of 50 | CREWMATE_TASKS | 2, 12, 11, 25 | 0.3030 | a shelf before the reveal |
| The reporter saw it happen | 14 of 50 | CREWMATE_EJECT | 5, 9, 8, 28 | 0.4737 | a shelf before the reveal |
| The reporter saw it happen | 14 of 50 | IMPOSTOR_PARITY | 7, 7, 17, 19 | 1.0000 | a shelf before the reveal |
| The reporter saw it happen | 14 of 50 | some meeting ejected someone | 14, 0, 32, 4 | 0.5660 | a shelf before the reveal |
| The reporter saw it happen | 14 of 50 | a crewmate was ejected | 7, 7, 14, 22 | 0.5344 | a shelf before the reveal |
| Double kill | 7 of 50 | CREWMATE_TASKS | 1, 6, 12, 31 | 0.6596 | a shelf before the reveal |
| Double kill | 7 of 50 | CREWMATE_EJECT | 1, 6, 12, 31 | 0.6596 | a shelf before the reveal |
| Double kill | 7 of 50 | IMPOSTOR_PARITY | 5, 2, 19, 24 | 0.2387 | a shelf before the reveal |
| Double kill | 7 of 50 | some meeting ejected someone | 6, 1, 40, 3 | 0.4641 | a shelf before the reveal |
| Double kill | 7 of 50 | a crewmate was ejected | 3, 4, 18, 25 | 1.0000 | a shelf before the reveal |
| Slow burn | 11 of 50 | CREWMATE_TASKS | 4, 7, 9, 30 | 0.4446 | a shelf before the reveal |
| Slow burn | 11 of 50 | CREWMATE_EJECT | 3, 8, 10, 29 | 1.0000 | a shelf before the reveal |
| Slow burn | 11 of 50 | IMPOSTOR_PARITY | 4, 7, 20, 19 | 0.5010 | a shelf before the reveal |
| Slow burn | 11 of 50 | some meeting ejected someone | 11, 0, 35, 4 | 0.5635 | a shelf before the reveal |
| Slow burn | 11 of 50 | a crewmate was ejected | 4, 7, 17, 22 | 0.7412 | a shelf before the reveal |
| Two kills after one regroup | 6 of 50 | CREWMATE_TASKS | 0, 6, 13, 31 | 0.3192 | a shelf before the reveal |
| Two kills after one regroup | 6 of 50 | CREWMATE_EJECT | 1, 5, 12, 32 | 1.0000 | a shelf before the reveal |
| Two kills after one regroup | 6 of 50 | IMPOSTOR_PARITY | 5, 1, 19, 25 | 0.0925 | a shelf before the reveal |
| Two kills after one regroup | 6 of 50 | some meeting ejected someone | 4, 2, 42, 2 | 0.0655 | a shelf before the reveal |
| Two kills after one regroup | 6 of 50 | a crewmate was ejected | 2, 4, 19, 25 | 1.0000 | a shelf before the reveal |
| A close call | 16 of 50 | CREWMATE_TASKS | 3, 13, 10, 24 | 0.5075 | a shelf before the reveal |
| A close call | 16 of 50 | CREWMATE_EJECT | 4, 12, 9, 25 | 1.0000 | a shelf before the reveal |
| A close call | 16 of 50 | IMPOSTOR_PARITY | 9, 7, 15, 19 | 0.5470 | a shelf before the reveal |
| A close call | 16 of 50 | some meeting ejected someone | 14, 2, 32, 2 | 0.5843 | a shelf before the reveal |
| A close call | 16 of 50 | a crewmate was ejected | 7, 9, 14, 20 | 1.0000 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | CREWMATE_TASKS | 3, 13, 10, 24 | 0.5075 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | CREWMATE_EJECT | 5, 11, 8, 26 | 0.7310 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | IMPOSTOR_PARITY | 8, 8, 16, 18 | 1.0000 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | some meeting ejected someone | 16, 0, 30, 4 | 0.2919 | a shelf before the reveal |
| Suspicion moved | 16 of 50 | a crewmate was ejected | 8, 8, 13, 21 | 0.5427 | a shelf before the reveal |
| A third round | 19 of 50 | CREWMATE_TASKS | 6, 13, 7, 24 | 0.5213 | a shelf before the reveal |
| A third round | 19 of 50 | CREWMATE_EJECT | 6, 13, 7, 24 | 0.5213 | a shelf before the reveal |
| A third round | 19 of 50 | IMPOSTOR_PARITY | 7, 12, 17, 14 | 0.2549 | a shelf before the reveal |
| A third round | 19 of 50 | some meeting ejected someone | 18, 1, 28, 3 | 1.0000 | a shelf before the reveal |
| A third round | 19 of 50 | a crewmate was ejected | 5, 14, 16, 15 | 0.1391 | a shelf before the reveal |
| Caught venting | 19 of 50 | CREWMATE_TASKS | 3, 16, 10, 21 | 0.3203 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | CREWMATE_EJECT | 12, 7, 1, 30 | under 0.0001 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | IMPOSTOR_PARITY | 4, 15, 20, 11 | 0.0038 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | some meeting ejected someone | 19, 0, 27, 4 | 0.2839 | behind the reveal, by the leak rule |
| Caught venting | 19 of 50 | a crewmate was ejected | 4, 15, 17, 14 | 0.0374 | behind the reveal, by the leak rule |
| One line, two readings | 20 of 50 | CREWMATE_TASKS | 2, 18, 11, 19 | 0.0498 | behind the reveal, by the leak rule |
| One line, two readings | 20 of 50 | CREWMATE_EJECT | 8, 12, 5, 25 | 0.1004 | behind the reveal, by the leak rule |
| One line, two readings | 20 of 50 | IMPOSTOR_PARITY | 10, 10, 14, 16 | 1.0000 | behind the reveal, by the leak rule |
| One line, two readings | 20 of 50 | some meeting ejected someone | 19, 1, 27, 3 | 0.6411 | behind the reveal, by the leak rule |
| One line, two readings | 20 of 50 | a crewmate was ejected | 8, 12, 13, 17 | 1.0000 | behind the reveal, by the leak rule |
| Struck after the regroup | 40 of 50 | CREWMATE_TASKS | 8, 32, 5, 5 | 0.1009 | a facet, by the saturation rule |
| Struck after the regroup | 40 of 50 | CREWMATE_EJECT | 10, 30, 3, 7 | 0.7068 | a facet, by the saturation rule |
| Struck after the regroup | 40 of 50 | IMPOSTOR_PARITY | 22, 18, 2, 8 | 0.0766 | a facet, by the saturation rule |
| Struck after the regroup | 40 of 50 | some meeting ejected someone | 36, 4, 10, 0 | 0.5710 | a facet, by the saturation rule |
| Struck after the regroup | 40 of 50 | a crewmate was ejected | 18, 22, 3, 7 | 0.4880 | a facet, by the saturation rule |

### The lean of the shelf count

Never served and never used to order a game: the mean number of shelves before the reveal per game on no tripwire, by ending.

| ending | games | mean shelves |
| --- | --- | --- |
| `CREWMATE_EJECT` | 13 | 1.92 |
| `CREWMATE_TASKS` | 13 | 1.46 |
| `IMPOSTOR_PARITY` | 23 | 1.96 |

## Limitations

* One recording of 50 games per set, and no interval is claimed.
* The classes swing between eras, which is why they are recomputed per era and recorded in the served file.
* The constants were chosen with these numbers in view, and the leak level is not corrected for the many tests it is applied to, so a false leak verdict is plausible. The rule errs in one direction only: it can only hide more.
* The facets the viewer already shows before the reveal (the length, the meetings) carry some information about the ending.
* A ballot labelled as holding nothing is the voter's own statement. An ejecting one stops the publisher until the owner says how the tripwire reads it.
* The manufactured-contradiction tripwire is nearly blind.
* *Wrong on what it held* reads the grounding labels, not whether the cited line is true; the gameplay census measures that, and the profile does not read it.
* The chip is not leak-tested; the leak rule covers shelves.
