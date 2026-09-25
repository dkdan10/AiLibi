# The gameplay census

**This is not the process scorecard. The scorecard asks whether each decision rested on data the agent held; this census counts what happened in the games themselves. No cell here joins the scorecard, and nothing here is a gate.** The scorecard is [its own page](process-scorecard.md).

**Role-correctness is reported and gates nothing. Where a cell reads a role it is to describe the game, never to judge a decision, and nothing here feeds back to any agent or pushes one toward the correct answer.**

Every cell is a count over recordings already in the tree, made with zero model calls. The walk re-runs each game through the engine and verifies every recorded state hash; no prompt, speech or rationale text is copied into this report.

This page is generated. Do not edit it by hand: run `uv run python scripts/publish_gameplay_census.py` and commit the result. `uv run python scripts/publish_gameplay_census.py --check` recomputes this page and [`gameplay-census.json`](gameplay-census.json) from the recordings and fails on drift, and `uv run python scripts/publish_gameplay_census.py --set-dir DIR --json-stdout` folds one other directory and writes nothing.

## Terms

* **opener**: the player whose body report or button press opened a meeting; the opener speaks first.
* **trigger tick**: the play tick on which a meeting opened. Actions submitted for that tick after the one that opened the meeting are thrown away unexecuted.
* **vent proof**: a meeting's contradiction flag of the vent-sighting kind naming a player who was alive when the meeting opened.
* **vent band**: the ejections whose ejected player such a vent-sighting flag names.
* **regroup**: the optional meeting reset: when play resumes every survivor stands in the meeting room, corpses are cleared, no one is inside a vent and each impostor's kill cooldown restarts at the map's value.
* **grace window**: the ticks after a regroup before the impostors' restarted kill cooldown runs out: from the tick after the meeting through the map's kill cooldown.
* **vent trip**: an impostor's stay inside the vents, from its entry to its exit, or to the meeting or game end that closed it.
* **ticks inside**: the play ticks a vent trip lasted, counting again from zero at a meeting the trip spanned.
* **in-vent cap**: 4 ticks inside: under the look-and-wait exit an impostor must surface at this count.
* **fresh kill**: the impostor's own victim, killed at most 3 ticks earlier in the same room, with no meeting in between.
* **inferred-visible rooms**: the rooms an impostor inside a vent can infer it sees: the vent's own room and its map neighbours, or the own room alone while any sabotage is active. Never the engine's own visibility.
* **rebuttal**: a turn by a player who already spoke in the same meeting; the only such turn the meeting layer can produce is the bounded rebuttal.
* **era**: the recorded settings a group of games shares: its experiment settings, its observation delivery version, its substrate-flag stamp and its prompt versions. Games of different eras are never pooled.
* **by construction**: a count a recorded setting forces to zero. While the setting is on the census checks the count is zero and stops with an error naming the game and meeting if it is not, and the page says 0 by construction instead of presenting a measured improvement.
* **n/a**: an empty denominator: nothing of that kind happened, so no rate exists.

Each cell reads `numerator/denominator (rate)`. A cell whose count a recorded setting forces to zero reads `0/N by construction` while that setting is on, and every cell with nothing to count reads `n/a`.

## Recorded settings a zero depends on

* `vent_witness_rule`: who sees a vent exit: under physical, only the room surfaced into.
* `vent_entry_policy`: when an impostor enters a vent: under own_fresh_kill, only at its own fresh kill.
* `vent_exit_policy`: when an impostor surfaces: under look_and_wait, only when no non-teammate stands in its inferred-visible rooms, or at the in-vent cap.
* `meeting_reset`: what a meeting leaves behind: under hub_with_grace, a regroup.
* `report_body_handle_version`: how a report names the corpse: version 1 uses a handle without the death tick.
* `bounded_rebuttal_version`: whether one extra turn goes to a player charged after speaking: version 1 grants it; unset grants none.
* `self_report`: whether an impostor may report a corpse: off means never.
* `contextual_self_report_version`: a situational impostor self-report: unset means never.
* `ballot_kill_row_version`: whether a kill witness's ballot gets its own first-hand kill row: version 1 serves it.

Every recorded setting field, and how this census uses it:

| setting | use |
| --- | --- |
| `format_version` | not read: a serialization version, not a game rule |
| `redistribution_policy` | not read: decides who inherits a dead crewmate's tasks; no cell counts tasks |
| `meeting_reset` | read by: meeting_regroup |
| `crew_idle_policy` | not read: moves idle crewmates; no cell is forced by it |
| `vent_exit_policy` | read by: look_and_wait_exit |
| `post_meeting_retarget` | not read: retargets impostors after a meeting; no cell is forced by it |
| `self_report` | read by: no_impostor_self_report |
| `sabotage_threshold` | not read: a sabotage win rule; no cell is forced by it |
| `evidence_reasoning_version` | not read: changes what a meeting renders; no cell is forced by it |
| `bounded_rebuttal_version` | read by: bounded_rebuttal, no_rebuttal |
| `public_account_version` | not read: changes what a meeting renders; no cell is forced by it |
| `attributed_testimony_version` | not read: changes what a meeting renders; no cell is forced by it |
| `investigation_version` | not read: moves idle crewmates; no cell is forced by it |
| `contextual_self_report_version` | read by: no_impostor_self_report |
| `vent_witness_rule` | read by: physical_vent_witness |
| `vent_entry_policy` | read by: own_fresh_kill_entry |
| `report_body_handle_version` | read by: public_body_handle |
| `ballot_kill_row_version` | read by: own_kill_ballot_row |
| `impostor_ballot_version` | not read: an instructed ballot framing; the tally does not enforce it, so no cell is forced by it |

Named windows, in ticks:

* `button_cooldown_ticks`: 6
* `fresh_kill_window_ticks`: 3
* `grace_window_ticks`: 4
* `in_vent_cap_ticks`: 4
* `short_window_ticks`: 2

## One era

Every set below pooled, so every game shares one era, derived from the recordings themselves rather than stated:

* recorded experiment settings: none beyond the historical defaults;
* temporal observations: not delivered;
* substrate flags on: absence_prior, citation_gate, coalesced_memory_render, evidence_quality_lift, grounded_prosecution, hard_evidence_gate, map_aware_arbitration, meeting_outcome_memory, movement_claim_shape, movement_perception, observation_id_rendering, reporter_exculpation, roll_call_round, self_location_trail, structured_turn_markers, task_completion_from_events, testimony_as_content, unfreeze_memory, vent_placement_contradictions, whereabouts_interior_flags, witnessed_kill_evidence; off: corroboration_discipline, impostor_roll_call, reporter_reasoning, temporal_observations, testimony_shapes;
* prompt stamps, read from the MANIFEST rows of games that held a meeting: `accusation_round.qwen3_6_27b.v6`, `crewmate_report.qwen3_6_27b.v6`, `impostor_report.qwen3_6_27b.v6`, `vote_ballot.qwen3_6_27b.v8`.

## The counts

### Witnesses

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Kills a crewmate saw | 20/849 (2.4%) | 19/725 (2.6%) | 16/550 (2.9%) | 3/175 (1.7%) | 0/58 (0.0%) | 1/66 (1.5%) |
| Vent entries a crewmate saw | 73/587 (12.4%) | 64/501 (12.8%) | 45/396 (11.4%) | 19/105 (18.1%) | 4/42 (9.5%) | 5/44 (11.4%) |
| Vent exits a crewmate saw | 313/512 (61.1%) | 271/435 (62.3%) | 209/350 (59.7%) | 62/85 (72.9%) | 24/38 (63.2%) | 18/39 (46.2%) |
| Vent exits seen from the room surfaced into | 251/512 (49.0%) | 226/435 (52.0%) | 173/350 (49.4%) | 53/85 (62.4%) | 17/38 (44.7%) | 8/39 (20.5%) |
| Vent exits seen only from the room left | 62/512 (12.1%) | 45/435 (10.3%) | 36/350 (10.3%) | 9/85 (10.6%) | 7/38 (18.4%) | 10/39 (25.6%) |
| Impostors seen venting, then ejected | 330/355 (93.0%) | 284/304 (93.4%) | 214/227 (94.3%) | 70/77 (90.9%) | 26/28 (92.9%) | 20/23 (87.0%) |
| Impostors who vented unseen, then ejected | 13/89 (14.6%) | 13/56 (23.2%) | 10/48 (20.8%) | 3/8 (37.5%) | 0/14 (0.0%) | 0/19 (0.0%) |
| Impostors who never vented, then ejected | 26/56 (46.4%) | 25/40 (62.5%) | 17/25 (68.0%) | 8/15 (53.3%) | 1/8 (12.5%) | 0/8 (0.0%) |

### Vent trips and surfacings

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Vent entries not after the impostor's own fresh kill | 103/587 (17.5%) | 101/501 (20.2%) | 88/396 (22.2%) | 13/105 (12.4%) | 0/42 (0.0%) | 2/44 (4.5%) |
| Surfacings before the cap with someone in view | 299/512 (58.4%) | 264/435 (60.7%) | 212/350 (60.6%) | 52/85 (61.2%) | 18/38 (47.4%) | 17/39 (43.6%) |
| Vent trips longer than the cap | n/a | n/a | n/a | n/a | n/a | n/a |
| Surfacings at the cap | 0/512 (0.0%) | 0/435 (0.0%) | 0/350 (0.0%) | 0/85 (0.0%) | 0/38 (0.0%) | 0/39 (0.0%) |
| Vent exits into a room a crewmate stood in | 250/512 (48.8%) | 226/435 (52.0%) | 173/350 (49.4%) | 53/85 (62.4%) | 15/38 (39.5%) | 9/39 (23.1%) |
| Vent exits into a room the impostor could see a crewmate in | 134/512 (26.2%) | 122/435 (28.0%) | 91/350 (26.0%) | 31/85 (36.5%) | 8/38 (21.1%) | 4/39 (10.3%) |
| Vent exits while a crewmate stood in the room left | 24/512 (4.7%) | 18/435 (4.1%) | 17/350 (4.9%) | 1/85 (1.2%) | 2/38 (5.3%) | 4/39 (10.3%) |
| Surfacings in place with a crewmate arriving before the walk-out | n/a | n/a | n/a | n/a | n/a | n/a |
| Kills soon after the killer surfaced | 11/849 (1.3%) | 11/725 (1.5%) | 8/550 (1.5%) | 3/175 (1.7%) | 0/58 (0.0%) | 0/66 (0.0%) |

**Ticks inside per surfaced vent trip.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 512 | 435 | 350 | 85 | 38 | 39 |

### Vent proof at meetings

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Meetings with vent proof | 330/676 (48.8%) | 285/594 (48.0%) | 215/449 (47.9%) | 70/145 (48.3%) | 26/43 (60.5%) | 19/39 (48.7%) |
| Impostor ejections in the vent band | 326/369 (88.3%) | 281/322 (87.3%) | 211/241 (87.6%) | 70/81 (86.4%) | 26/27 (96.3%) | 19/20 (95.0%) |
| Crewmate ejections in the vent band | 0/42 (0.0%) | 0/41 (0.0%) | 0/32 (0.0%) | 0/9 (0.0%) | 0/1 (0.0%) | n/a |
| Impostor ejections without vent proof | 43/369 (11.7%) | 41/322 (12.7%) | 30/241 (12.4%) | 11/81 (13.6%) | 1/27 (3.7%) | 1/20 (5.0%) |
| Vent-band ejections resting only on the room left | 50/326 (15.3%) | 37/281 (13.2%) | 29/211 (13.7%) | 8/70 (11.4%) | 6/26 (23.1%) | 7/19 (36.8%) |
| Meetings without vent proof that ejected | 83/346 (24.0%) | 80/309 (25.9%) | 60/234 (25.6%) | 20/75 (26.7%) | 2/17 (11.8%) | 1/20 (5.0%) |
| Ejections without vent proof that removed an impostor | 43/83 (51.8%) | 41/80 (51.2%) | 30/60 (50.0%) | 11/20 (55.0%) | 1/2 (50.0%) | 1/1 (100.0%) |
| Button meetings with vent proof | 53/53 (100.0%) | 43/43 (100.0%) | 33/33 (100.0%) | 10/10 (100.0%) | 7/7 (100.0%) | 3/3 (100.0%) |

**Which vent moment the vent band rests on.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| both | 10 | 10 | 8 | 2 | 0 | 0 |
| entry only | 63 | 54 | 37 | 17 | 4 | 5 |
| exit only | 253 | 217 | 166 | 51 | 22 | 14 |

### Corpses and the state play resumes in

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Stale report meetings | 167/623 (26.8%) | 167/551 (30.3%) | 124/416 (29.8%) | 43/135 (31.9%) | 0/36 (0.0%) | 0/36 (0.0%) |
| Meetings opening with another unreported corpse | 335/676 (49.6%) | 325/594 (54.7%) | 251/449 (55.9%) | 74/145 (51.0%) | 7/43 (16.3%) | 3/39 (7.7%) |
| Play resumes with an impostor in a vent | 30/486 (6.2%) | 30/452 (6.6%) | 20/345 (5.8%) | 10/107 (9.3%) | 0/15 (0.0%) | 0/19 (0.0%) |
| Play resumes with a corpse on the floor | 263/486 (54.1%) | 263/452 (58.2%) | 203/345 (58.8%) | 60/107 (56.1%) | 0/15 (0.0%) | 0/19 (0.0%) |
| Kills soon after a meeting | 135/389 (34.7%) | 129/363 (35.5%) | 101/276 (36.6%) | 28/87 (32.2%) | 3/12 (25.0%) | 3/14 (21.4%) |
| Meetings opening with an impostor in a vent | 101/676 (14.9%) | 92/594 (15.5%) | 63/449 (14.0%) | 29/145 (20.0%) | 4/43 (9.3%) | 5/39 (12.8%) |
| Impostors able to kill when a meeting opened | 326/943 (34.6%) | 301/861 (35.0%) | 238/651 (36.6%) | 63/210 (30.0%) | 12/43 (27.9%) | 13/39 (33.3%) |

**Corpse age at report.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 56 | 55 | 41 | 14 | 0 | 1 |
| 2 | 103 | 87 | 65 | 22 | 8 | 8 |
| 3 | 108 | 88 | 65 | 23 | 11 | 9 |
| 4 | 140 | 121 | 91 | 30 | 11 | 8 |
| 5 | 40 | 35 | 24 | 11 | 1 | 4 |
| 6 | 53 | 45 | 31 | 14 | 4 | 4 |
| 7 | 30 | 28 | 21 | 7 | 1 | 1 |
| 8 | 13 | 12 | 10 | 2 | 0 | 1 |
| 9 | 14 | 14 | 12 | 2 | 0 | 0 |
| 10 | 7 | 7 | 7 | 0 | 0 | 0 |
| 11 | 17 | 17 | 14 | 3 | 0 | 0 |
| 12 | 11 | 11 | 9 | 2 | 0 | 0 |
| 13 | 6 | 6 | 5 | 1 | 0 | 0 |
| 14 | 2 | 2 | 2 | 0 | 0 | 0 |
| 16 | 4 | 4 | 3 | 1 | 0 | 0 |
| 17 | 2 | 2 | 2 | 0 | 0 | 0 |
| 18 | 1 | 1 | 1 | 0 | 0 | 0 |
| 19 | 6 | 6 | 6 | 0 | 0 | 0 |
| 20 | 3 | 3 | 2 | 1 | 0 | 0 |
| 23 | 3 | 3 | 3 | 0 | 0 | 0 |
| 25 | 1 | 1 | 1 | 0 | 0 | 0 |
| 26 | 1 | 1 | 0 | 1 | 0 | 0 |
| 29 | 1 | 1 | 0 | 1 | 0 | 0 |
| 32 | 1 | 1 | 1 | 0 | 0 | 0 |

### After a regroup

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Kills in the grace window after a regroup | n/a | n/a | n/a | n/a | n/a | n/a |
| Reported corpses older than the last regroup | n/a | n/a | n/a | n/a | n/a | n/a |
| Vent trips ended by a regroup | 0/587 (0.0%) | 0/501 (0.0%) | 0/396 (0.0%) | 0/105 (0.0%) | 0/42 (0.0%) | 0/44 (0.0%) |
| Kill witnesses pressing the button soon after a regroup | n/a | n/a | n/a | n/a | n/a | n/a |
| Sabotage active at a regroup | n/a | n/a | n/a | n/a | n/a | n/a |

**Trigger-tick movement and task events a regroup drops.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| (none) | 0 | 0 | 0 | 0 | 0 | 0 |

### Meeting structure

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| The first reply accuses the opener | 521/676 (77.1%) | 448/594 (75.4%) | 328/449 (73.1%) | 120/145 (82.8%) | 36/43 (83.7%) | 37/39 (94.9%) |
| Someone accuses the opener | 561/676 (83.0%) | 487/594 (82.0%) | 362/449 (80.6%) | 125/145 (86.2%) | 37/43 (86.0%) | 37/39 (94.9%) |
| The opener speaks a second time | 0/676 (0.0%) | 0/594 (0.0%) | 0/449 (0.0%) | 0/145 (0.0%) | 0/43 (0.0%) | 0/39 (0.0%) |
| An accused opener answers | 0/561 by construction | 0/487 by construction | 0/362 by construction | 0/125 by construction | 0/37 by construction | 0/37 by construction |
| Meetings where someone spoke twice | 0/676 by construction | 0/594 by construction | 0/449 by construction | 0/145 by construction | 0/43 by construction | 0/39 by construction |
| Meetings with two repeat-speaker turns | 0/676 by construction | 0/594 by construction | 0/449 by construction | 0/145 by construction | 0/43 by construction | 0/39 by construction |
| Meetings opened by an impostor | 0/676 by construction | 0/594 by construction | 0/449 by construction | 0/145 by construction | 0/43 by construction | 0/39 by construction |
| Report openings that name the kill tick in the body handle | 623/623 (100.0%) | 551/551 (100.0%) | 416/416 (100.0%) | 135/135 (100.0%) | 36/36 (100.0%) | 36/36 (100.0%) |
| Openers among ejected crewmates | 38/42 (90.5%) | 37/41 (90.2%) | 30/32 (93.8%) | 7/9 (77.8%) | 1/1 (100.0%) | n/a |
| Report meetings that skipped | 264/623 (42.4%) | 230/551 (41.7%) | 175/416 (42.1%) | 55/135 (40.7%) | 15/36 (41.7%) | 19/36 (52.8%) |

**Meetings by trigger.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| emergency | 53 | 43 | 33 | 10 | 7 | 3 |
| report | 623 | 551 | 416 | 135 | 36 | 36 |

**Ejected crewmate openers by trigger.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| emergency | 1 | 1 | 1 | 0 | 0 | 0 |
| report | 37 | 36 | 29 | 7 | 1 | 0 |

**Actions thrown away on trigger ticks.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| do_task | 745 | 718 | 513 | 205 | 13 | 14 |
| emergency | 16 | 15 | 13 | 2 | 1 | 0 |
| kill | 39 | 37 | 30 | 7 | 1 | 1 |
| move | 809 | 754 | 566 | 188 | 26 | 29 |
| repair_sabotage | 4 | 4 | 3 | 1 | 0 | 0 |
| report | 96 | 96 | 70 | 26 | 0 | 0 |
| sabotage | 1 | 1 | 1 | 0 | 0 | 0 |
| vent | 121 | 112 | 80 | 32 | 4 | 5 |
| wait | 358 | 329 | 260 | 69 | 13 | 16 |

### Rebuttals

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Rebuttals the selector would not have chosen | n/a | n/a | n/a | n/a | n/a | n/a |
| Rebuttals carrying an alibi | n/a | n/a | n/a | n/a | n/a | n/a |
| Rebuttals carrying a whereabouts claim | n/a | n/a | n/a | n/a | n/a | n/a |
| Rebuttals carrying a sighting | n/a | n/a | n/a | n/a | n/a | n/a |
| Rebuttals that only redirect | n/a | n/a | n/a | n/a | n/a | n/a |
| Rebuttal accusations against players who already spoke | n/a | n/a | n/a | n/a | n/a | n/a |
| Opener rebuttals answering the charged tick | n/a | n/a | n/a | n/a | n/a | n/a |

**Who received the rebuttal, and who had accused them.**

| row | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| (none) | 0 | 0 | 0 | 0 | 0 | 0 |

### Ballots

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Impostor ballots that skip | 760/943 (80.6%) | 694/861 (80.6%) | 530/651 (81.4%) | 164/210 (78.1%) | 33/43 (76.7%) | 33/39 (84.6%) |
| Impostor ballots that name a player | 183/943 (19.4%) | 167/861 (19.4%) | 121/651 (18.6%) | 46/210 (21.9%) | 10/43 (23.3%) | 6/39 (15.4%) |
| Impostor ballots naming a player with a supported label | 178/183 (97.3%) | 164/167 (98.2%) | 120/121 (99.2%) | 44/46 (95.7%) | 8/10 (80.0%) | 6/6 (100.0%) |
| Impostor ballots recorded against a teammate | 0/943 by construction | 0/861 by construction | 0/651 by construction | 0/210 by construction | 0/43 by construction | 0/39 by construction |
| Impostor ballots written against a teammate | 13/943 (1.4%) | 13/861 (1.5%) | 12/651 (1.8%) | 1/210 (0.5%) | 0/43 (0.0%) | 0/39 (0.0%) |
| Ejections whose confidence floor only impostors met | 0/411 (0.0%) | 0/363 (0.0%) | 0/273 (0.0%) | 0/90 (0.0%) | 0/28 (0.0%) | 0/20 (0.0%) |
| Own-kill ballot rows naming a teammate or held by a non-witness | n/a | n/a | n/a | n/a | n/a | n/a |
| Own-kill ballot rows their holder cited | n/a | n/a | n/a | n/a | n/a | n/a |
| Kills a crewmate saw, held by a living witness at the next meeting | 20/20 (100.0%) | 19/19 (100.0%) | 16/16 (100.0%) | 3/3 (100.0%) | n/a | 1/1 (100.0%) |
| Held kills whose witness voted the killer | 19/20 (95.0%) | 18/19 (94.7%) | 15/16 (93.8%) | 3/3 (100.0%) | n/a | 1/1 (100.0%) |
| Held kills whose killer was ejected | 12/20 (60.0%) | 12/19 (63.2%) | 10/16 (62.5%) | 2/3 (66.7%) | n/a | 0/1 (0.0%) |

### Reported beside the counts

| cell | all four sets | the two nine-player sets | ml_corpus/9p2i | samples/9p2i | ml_corpus/4p1i | samples/4p1i |
| --- | --- | --- | --- | --- | --- | --- |
| Games the impostors won | 88/300 (29.3%) | 56/200 (28.0%) | 45/150 (30.0%) | 11/50 (22.0%) | 14/50 (28.0%) | 18/50 (36.0%) |
| Ejections that removed an impostor | 369/411 (89.8%) | 322/363 (88.7%) | 241/273 (88.3%) | 81/90 (90.0%) | 27/28 (96.4%) | 20/20 (100.0%) |

## Definitions

**Kills a crewmate saw** (`kills_seen_by_crew`). Kills with at least one crewmate among the engine's recorded witnesses, over all kills. Reads `Killed`.

**Vent entries a crewmate saw** (`vent_entries_seen_by_crew`). Vent entries with a crewmate among either recorded witness list, over all vent entries. Reads `VentEntered`.

**Vent exits a crewmate saw** (`vent_exits_seen_by_crew`). Vent exits with a crewmate among either recorded witness list, over all vent exits. Reads `VentExited`.

**Vent exits seen from the room surfaced into** (`vent_exits_seen_from_exit_room`). Vent exits with a crewmate among the witnesses in the room the impostor surfaced into, over all vent exits. Reads `VentExited`.

**Vent exits seen only from the room left** (`vent_exits_seen_only_from_room_left`). Vent exits with a crewmate among the witnesses in the room the impostor left and none in the room it surfaced into, over all vent exits. Reads `VentExited`. Zero by construction while `vent_witness_rule = physical`.

**Impostors seen venting, then ejected** (`impostors_seen_venting_ejected`). Impostors ejected at some meeting, over impostors with at least one vent entry or exit a crewmate saw. Reads `VentEntered`, `VentExited`, `meeting row`.

**Impostors who vented unseen, then ejected** (`impostors_vented_unseen_ejected`). Impostors ejected at some meeting, over impostors who vented but whom no crewmate ever saw venting. Reads `VentEntered`, `VentExited`, `meeting row`.

**Impostors who never vented, then ejected** (`impostors_never_vented_ejected`). Impostors ejected at some meeting, over impostors who never vented. Reads `VentEntered`, `VentExited`, `meeting row`.

**Vent entries not after the impostor's own fresh kill** (`vent_entries_not_after_own_fresh_kill`). Vent entries where no victim of the entering impostor lies in that room, killed at most 3 ticks before the entry with no meeting in between, over all vent entries. Reads `VentEntered`, `Killed`, `meeting row`. Zero by construction while `vent_entry_policy = own_fresh_kill`.

**Surfacings before the cap with someone in view** (`surfacings_before_cap_in_view`). Vent exits made before the in-vent cap while a living non-teammate stood, just before the exit tick, in a room the impostor infers it can see from inside the vent, over all vent exits. Reads `VentEntered`, `VentExited`, `state before the tick`. Zero by construction while `vent_exit_policy = look_and_wait`.

**Vent trips longer than the cap** (`trips_longer_than_cap`). Vent trips whose ticks inside exceed the in-vent cap, over vent trips that stayed inside for more than one tick. Reads `VentEntered`, `VentExited`, `meeting row`. Zero by construction while `vent_exit_policy = look_and_wait`.

**Surfacings at the cap** (`forced_surfacings`). Vent exits made exactly at the in-vent cap, over all vent exits. Reads `VentEntered`, `VentExited`, `meeting row`.

**Vent exits into a room a crewmate stood in** (`vent_exits_into_occupied_room`). Vent exits whose destination room held a living crewmate just before the exit tick, over all vent exits. Reads `VentExited`, `state before the tick`.

**Vent exits into a room the impostor could see a crewmate in** (`vent_exits_into_visibly_occupied_room`). Vent exits whose destination room was among the impostor's inferred-visible rooms and held a living crewmate just before the exit tick, over all vent exits. Reads `VentExited`, `state before the tick`.

**Vent exits while a crewmate stood in the room left** (`vent_exits_while_room_left_occupied`). Vent exits whose source room held a living crewmate just before the exit tick, over all vent exits. Reads `VentExited`, `state before the tick`.

**Surfacings in place with a crewmate arriving before the walk-out** (`in_place_surfacings_near_crew`). Vent exits back into the room the impostor entered from, where a living crewmate stands in that room on some tick after the surfacing and before the impostor leaves it, over all such in-place exits. Reads `VentExited`, `state before the tick`.

**Kills soon after the killer surfaced** (`kills_soon_after_surfacing`). Kills made at most 2 ticks after the killer's own vent exit, over all kills. Reads `Killed`, `VentExited`.

**Meetings with vent proof** (`meetings_with_vent_proof`). Meetings with a vent-sighting flag naming a player alive when the meeting opened, over all meetings. Reads `meeting row flags`.

**Impostor ejections in the vent band** (`vent_band_impostor_ejections`). Impostor ejections whose ejected player a vent-sighting flag names, over all impostor ejections. Reads `meeting row flags`.

**Crewmate ejections in the vent band** (`vent_band_crew_ejections`). Crewmate ejections whose ejected player a vent-sighting flag names, over all crewmate ejections. Reads `meeting row flags`.

**Impostor ejections without vent proof** (`impostor_ejections_without_vent_proof`). Impostor ejections at meetings without vent proof, over all impostor ejections. Reads `meeting row flags`.

**Vent-band ejections resting only on the room left** (`vent_band_resting_only_on_room_left`). Vent-band impostor ejections where every crewmate who saw the ejected impostor vent before the meeting, and was alive at it, saw only an exit from the room left, over all vent-band impostor ejections. Reads `VentEntered`, `VentExited`, `meeting row flags`. Zero by construction while `vent_witness_rule = physical`.

**Meetings without vent proof that ejected** (`meetings_without_vent_proof_ejecting`). Meetings without vent proof that ejected someone, over all meetings without vent proof. Reads `meeting row flags`.

**Ejections without vent proof that removed an impostor** (`ejections_without_vent_proof_of_impostors`). Impostor ejections, over all ejections at meetings without vent proof. Reads `meeting row flags`.

**Button meetings with vent proof** (`button_meetings_with_vent_proof`). Button meetings with vent proof, over all button meetings. Reads `MeetingTriggered`, `meeting row flags`.

**Stale report meetings** (`stale_report_meetings`). Report meetings whose reported corpse already lay on the floor when the previous meeting opened, over all report meetings. Reads `MeetingTriggered`, `state at the meeting`. Zero by construction while `meeting_reset = hub_with_grace`.

**Meetings opening with another unreported corpse** (`meetings_opening_with_another_unreported_corpse`). Meetings that opened with a corpse other than the reported one that no one had discovered, over all meetings. Reads `state at the meeting`.

**Play resumes with an impostor in a vent** (`play_resumes_with_impostor_in_vent`). Meetings after which play resumed with an impostor inside a vent, over meetings after which play resumed. Reads `state after the meeting`. Zero by construction while `meeting_reset = hub_with_grace`.

**Play resumes with a corpse on the floor** (`play_resumes_with_corpse`). Meetings after which play resumed with a corpse on the floor, over meetings after which play resumed. Reads `state after the meeting`. Zero by construction while `meeting_reset = hub_with_grace`.

**Kills soon after a meeting** (`post_meeting_kills_soon_after`). Kills made at most 2 ticks after the previous meeting's tick, over all kills made after some meeting. Reads `Killed`, `meeting row`.

**Meetings opening with an impostor in a vent** (`meetings_opening_with_impostor_in_vent`). Meetings that opened with an impostor inside a vent, over all meetings. Reads `state at the meeting`.

**Impostors able to kill when a meeting opened** (`impostor_cooldown_zero_at_open`). Living impostors whose kill cooldown was zero when a meeting opened, over living impostors at every meeting. Reads `state at the meeting`.

**Kills in the grace window after a regroup** (`kills_in_grace_window_after_regroup`). Kills made on a tick after a regroup meeting no later than the map's kill cooldown, over all kills made between a regroup and the next meeting. Reads `Killed`, `meeting row`. Zero by construction while `meeting_reset = hub_with_grace`.

**Reported corpses older than the last regroup** (`report_corpses_older_than_last_close`). Report meetings whose reported victim was killed on or before the previous meeting's tick, over report meetings whose previous meeting regrouped. Reads `Killed`, `MeetingTriggered`, `meeting row`. Zero by construction while `meeting_reset = hub_with_grace`.

**Vent trips ended by a regroup** (`trips_closed_by_regroup`). Vent trips that ended because a regroup cleared the vent, with no exit, over all vent trips that ended. Reads `VentEntered`, `VentExited`, `meeting row`.

**Kill witnesses pressing the button soon after a regroup** (`kill_witness_button_calls_soon_after_regroup`). Button meetings called at most 6 ticks after a regroup by a player who witnessed a kill since it, over button meetings whose previous meeting regrouped. Reads `Killed`, `MeetingTriggered`, `meeting row`.

**Sabotage active at a regroup** (`sabotage_active_at_regroup`). Regroup meetings that opened with a sabotage active, over all regroup meetings. Reads `state at the meeting`.

**The first reply accuses the opener** (`first_reply_accuses_opener`). Meetings whose second turn carries a structured accusation of the opener, over all meetings. Reads `meeting row turns`.

**Someone accuses the opener** (`opener_accused_after_opening`). Meetings where a speaker other than the opener accused the opener, over all meetings. Reads `meeting row turns`.

**The opener speaks a second time** (`opener_speaks_again`). Meetings where the opener took more than one turn, over all meetings. Reads `meeting row turns`.

**An accused opener answers** (`accused_opener_answers`). Meetings where the opener spoke again after another speaker accused them, over meetings where another speaker accused the opener. Reads `meeting row turns`. Zero by construction while `bounded_rebuttal_version = unset`.

**Meetings where someone spoke twice** (`meetings_with_repeat_speaker`). Meetings with at least one turn by a player who had already spoken, over all meetings. Reads `meeting row turns`. Zero by construction while `bounded_rebuttal_version = unset`.

**Meetings with two repeat-speaker turns** (`meetings_with_second_repeat_speaker`). Meetings with two or more turns by players who had already spoken, over all meetings. Reads `meeting row turns`. Zero by construction in every recording.

**Meetings opened by an impostor** (`impostor_openers`). Meetings whose opener is an impostor, over all meetings. Reads `MeetingTriggered`. Zero by construction while `self_report = off and contextual_self_report_version = unset`.

**Report openings that name the kill tick in the body handle** (`report_openings_with_kill_tick_handle`). Report meetings whose opener's first recorded prompt carries a body handle embedding the death tick, over report meetings with a recorded opener prompt. Reads `MeetingTriggered`, `recorded opener prompt`. Zero by construction while `report_body_handle_version = 1`.

**Openers among ejected crewmates** (`openers_among_innocent_ejections`). Crewmate ejections that removed the meeting's opener, over all crewmate ejections. Reads `MeetingTriggered`, `meeting row`.

**Report meetings that skipped** (`skipped_report_meetings`). Report meetings that ejected no one, over all report meetings. Reads `MeetingTriggered`, `meeting row`.

**Rebuttals the selector would not have chosen** (`rebuttals_differing_from_selector`). Meetings whose first repeat-speaker turn has a speaker or answered turn different from the bounded-rebuttal selector's pick on the turns before it, over meetings with a repeat-speaker turn. Reads `meeting row turns`. Zero by construction while `bounded_rebuttal_version = 1`.

**Rebuttals carrying an alibi** (`rebuttals_with_alibi`). Repeat-speaker turns carrying an alibi about the speaker, over all repeat-speaker turns. Reads `meeting row turns`.

**Rebuttals carrying a whereabouts claim** (`rebuttals_with_whereabouts`). Repeat-speaker turns carrying a whereabouts observation, over all repeat-speaker turns. Reads `meeting row turns`.

**Rebuttals carrying a sighting** (`rebuttals_with_sighting`). Repeat-speaker turns carrying an observation of another player, over all repeat-speaker turns. Reads `meeting row turns`.

**Rebuttals that only redirect** (`rebuttals_redirect_only`). Repeat-speaker turns carrying an accusation and no alibi, whereabouts or sighting, over all repeat-speaker turns. Reads `meeting row turns`.

**Rebuttal accusations against players who already spoke** (`rebuttal_accusations_against_earlier_speakers`). Accusations in repeat-speaker turns naming a player who spoke earlier in the meeting, over all accusations in repeat-speaker turns. Reads `meeting row turns`.

**Opener rebuttals answering the charged tick** (`opener_rebuttals_answering_charged_tick`). Repeat-speaker turns by the opener carrying an alibi leg, a whereabouts claim or a sighting at a tick the answered turn observed the opener, over such turns whose answered turn observed the opener at some tick; the rest are not evaluable. Reads `meeting row turns`.

**Impostor ballots that skip** (`impostor_skip_ballots`). Impostor ballots whose recorded target is SKIP, over all impostor ballots. Reads `meeting row ballots`.

**Impostor ballots that name a player** (`impostor_eject_ballots`). Impostor ballots whose recorded target is a player, over all impostor ballots. Reads `meeting row ballots`.

**Impostor ballots naming a player with a supported label** (`impostor_ejects_labelled_supported`). Impostor ballots naming a player whose meeting-layer grounding label is supported, over impostor ballots naming a player. Reads `meeting row ballots`.

**Impostor ballots recorded against a teammate** (`recorded_teammate_ballot_targets`). Impostor ballots whose recorded target is a fellow impostor, over all impostor ballots. Reads `meeting row ballots`. Zero by construction in every recording.

**Impostor ballots written against a teammate** (`authored_teammate_ballot_targets`). Impostor ballots whose authored target, read from the typed guard fields, is a fellow impostor, over all impostor ballots. Reads `meeting row ballots`.

**Ejections whose confidence floor only impostors met** (`ejections_carried_only_by_impostor_ballots`). Ejections where every ballot for the ejected player at or above the tally's recorded confidence floor was cast by an impostor, over all ejections. Reads `meeting row ballots`.

**Own-kill ballot rows naming a teammate or held by a non-witness** (`own_kill_rows_breaching`). Served own-kill rows whose killer is the holder's fellow impostor, or whose cited observation joins to no kill the holder witnessed, over all served own-kill rows; rows citing nothing are not evaluable. Reads `recorded ballot prompt`, `Killed`. Zero by construction while `ballot_kill_row_version = 1`.

**Own-kill ballot rows their holder cited** (`own_kill_rows_cited_by_holder`). Served own-kill rows whose holder's ballot cites the row's observation, over all served own-kill rows. Reads `recorded ballot prompt`, `meeting row ballots`.

**Kills a crewmate saw, held by a living witness at the next meeting** (`crew_witnessed_kills_held_at_next_meeting`). Crew-witnessed kills with a crewmate witness alive at the next meeting, over crew-witnessed kills a meeting followed; the rest are not evaluable. Reads `Killed`, `meeting row`.

**Held kills whose witness voted the killer** (`held_kill_witnesses_voting_killer`). Held crew-witnessed kills where a living witness's ballot names the killer, over held crew-witnessed kills. Reads `Killed`, `meeting row ballots`.

**Held kills whose killer was ejected** (`held_kill_killers_ejected`). Held crew-witnessed kills whose killer the next meeting ejected, over held crew-witnessed kills. Reads `Killed`, `meeting row`.

**Games the impostors won** (`impostor_wins`). Games whose recorded winner is the impostors, over games with a recorded winner. Reads `game over row`.

**Ejections that removed an impostor** (`role_correct_ejections`). Impostor ejections, over all ejections. Reported, never a gate. Reads `meeting row`.

**Ticks inside per surfaced vent trip** (`ticks_inside_per_trip`). Vent exits by the number of play ticks the impostor spent inside, the count restarting at a meeting boundary. Reads `VentEntered`, `VentExited`, `meeting row`.

**Which vent moment the vent band rests on** (`vent_band_by_moment`). Vent-band impostor ejections by whether a crewmate saw the ejected impostor's exit only, entry only, both, or neither before the meeting. Reads `VentEntered`, `VentExited`, `meeting row flags`.

**Corpse age at report** (`corpse_age_at_report`). Report meetings by the ticks between the reported victim's kill and the meeting. Reads `Killed`, `MeetingTriggered`.

**Trigger-tick movement and task events a regroup drops** (`trigger_tick_events_dropped_by_regroup`). Movement and task events on the trigger tick of every regroup meeting, by kind. Reads `Moved`, `TaskProgressed`, `TaskCompleted`.

**Meetings by trigger** (`meetings_by_trigger`). Meetings by what opened them: a reported corpse or a button press. Reads `MeetingTriggered`.

**Ejected crewmate openers by trigger** (`innocent_opener_ejections_by_trigger`). Crewmate ejections that removed the opener, by what opened the meeting. Reads `MeetingTriggered`, `meeting row`.

**Actions thrown away on trigger ticks** (`actions_thrown_away_on_trigger_ticks`). Submitted actions the engine never ran because an earlier action on the same tick opened a meeting, by action type, read from the recorded dispositions; tick rows recorded without dispositions are not evaluable. Reads `recorded action dispositions`.

**Who received the rebuttal, and who had accused them** (`rebuttal_beneficiaries`). Repeat-speaker turns by the speaker's seat (the opener, or another crewmate or impostor) and the role of the speaker of the turn answered. Reads `meeting row turns`.
