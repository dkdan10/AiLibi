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
* **regroup**: the optional meeting reset: when play resumes every survivor stands in the meeting room, corpses are cleared, no one is inside a vent and each impostor's kill cooldown restarts at the recorded kill cooldown, else the map's value.
* **grace window**: the ticks after a regroup before the impostors' restarted kill cooldown runs out: from the tick after the meeting through the recorded kill cooldown, else the map's.
* **vent trip**: an impostor's stay inside the vents, from its entry to its exit, or to the meeting or game end that closed it.
* **ticks inside**: the play ticks a vent trip lasted, counting again from zero at a meeting the trip spanned.
* **in-vent cap**: 4 ticks inside: under the look-and-wait exit an impostor must surface at this count.
* **fresh kill**: the impostor's own victim, killed at most 3 ticks earlier in the same room, with no meeting in between.
* **inferred-visible rooms**: the rooms an impostor inside a vent can infer it sees: the vent's own room and its map neighbours, or the own room alone while any sabotage is active. Never the engine's own visibility.
* **rebuttal**: a turn by a player who already spoke in the same meeting; the only such turn the meeting layer can produce is the bounded rebuttal.
* **seat**: one living player at one report meeting. The reporter's seat is the reporter's whatever its role; every other seat belongs to a crewmate or an impostor. A player dead before the meeting has no seat.
* **living witnesses**: the crewmates the engine recorded as seeing a kill who are still alive at the next meeting, counted as one, or as two or more. A fellow impostor who saw the kill is never one of them.
* **held kill**: a kill a crewmate saw whose crew witness is still alive when the next meeting opens, a meeting on the kill's own tick included.
* **re-tally**: the meeting's recorded ballots counted again by the game's own vote count at the meeting's recorded confidence floor, with each impostor ballot read as a SKIP or removed. Every other ballot is held fixed, so a re-tally describes the ballots, not what the table would have done: real voters would have heard different speech.
* **holds-nothing label**: the grounding label a SKIP ballot carries when its voter stated outright that it held nothing that resolves the vote. The label restates the voter's own statement; nothing checks it against what the voter held.
* **rebuttal citation**: a ballot whose cited turn, or whose counter slot (the strongest thing the voter held pointing away from its choice), names a rebuttal of the same meeting.
* **era**: the recorded settings a group of games shares: its experiment settings, its observation delivery version, its substrate-flag stamp and its prompt versions. Games of different eras are never pooled.
* **by construction**: a count a recorded setting forces to zero. While the setting is on the census checks the count is zero and stops with an error naming the game and the meeting or tick if it is not, and the page says 0 by construction instead of presenting a measured improvement.
* **n/a**: nothing to count, so no rate exists: either nothing of that kind happened, or the cell or table counts only games recorded with a setting these games were not recorded with.

Each cell reads `numerator/denominator (rate)`. A cell whose count a recorded setting forces to zero reads `0/N by construction` while that setting is on, and every cell with nothing to count reads `n/a`. A cell or table that counts only games recorded with some setting reads `n/a` in every era without it, never a measured 0.

## Recorded settings a count depends on

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
| `kill_cooldown_ticks` | read as a value by: the length of the grace window, and the value the kill cooldown cell checks every cooldown write against |

## Eras

The committed sets are grouped by the era registry (`eval/eras.py`), and a count is pooled only with the other sets of its own era. Each era's settings below are derived from its recordings themselves rather than stated, and the named windows follow its recorded kill cooldown.

### baseline-9

Sets: `ml_corpus/9p2i`, `ml_corpus/4p1i`, `samples/4p1i`, recorded 2026-09-22. Declared config: none, every experimental switch off.

* recorded experiment settings: none beyond the historical defaults;
* temporal observations: not delivered;
* substrate flags on: absence_prior, citation_gate, coalesced_memory_render, evidence_quality_lift, grounded_prosecution, hard_evidence_gate, map_aware_arbitration, meeting_outcome_memory, movement_claim_shape, movement_perception, observation_id_rendering, reporter_exculpation, roll_call_round, self_location_trail, structured_turn_markers, task_completion_from_events, testimony_as_content, unfreeze_memory, vent_placement_contradictions, whereabouts_interior_flags, witnessed_kill_evidence; off: corroboration_discipline, impostor_roll_call, reporter_reasoning, temporal_observations, testimony_shapes;
* prompt stamps, read from the MANIFEST rows of games that held a meeting: `accusation_round.qwen3_6_27b.v6`, `crewmate_report.qwen3_6_27b.v6`, `impostor_report.qwen3_6_27b.v6`, `vote_ballot.qwen3_6_27b.v8`;
* named windows, in ticks: `button_cooldown_ticks` 6, `fresh_kill_window_ticks` 3, `grace_window_ticks` 4, `in_vent_cap_ticks` 4, `short_window_ticks` 2.

### stage-b-r2

Sets: `samples/9p2i`, recorded 2026-10-01. Declared config: `replays/samples/9p2i/experiment-config.json`.

* recorded experiment settings: `ballot_kill_row_version = 1`, `bounded_rebuttal_version = 1`, `impostor_ballot_version = 1`, `kill_cooldown_ticks = 6`, `meeting_reset = hub_with_grace`, `report_body_handle_version = 1`, `vent_entry_policy = own_fresh_kill`, `vent_exit_policy = look_and_wait`, `vent_witness_rule = physical`;
* temporal observations: not delivered;
* substrate flags on: absence_prior, citation_gate, coalesced_memory_render, evidence_quality_lift, grounded_prosecution, hard_evidence_gate, map_aware_arbitration, meeting_outcome_memory, movement_claim_shape, movement_perception, observation_id_rendering, reporter_exculpation, roll_call_round, self_location_trail, structured_turn_markers, task_completion_from_events, testimony_as_content, unfreeze_memory, vent_placement_contradictions, whereabouts_interior_flags, witnessed_kill_evidence; off: corroboration_discipline, impostor_roll_call, reporter_reasoning, temporal_observations, testimony_shapes;
* prompt stamps, read from the MANIFEST rows of games that held a meeting: `accusation_round.qwen3_6_27b.v6`, `crewmate_report.qwen3_6_27b.v6`, `impostor_report.qwen3_6_27b.v6`, `vote_ballot.qwen3_6_27b.v8.ballot_kill_row_v1+vote_ballot.qwen3_6_27b.v8.impostor_ballot_v1`;
* named windows, in ticks: `button_cooldown_ticks` 6, `fresh_kill_window_ticks` 3, `grace_window_ticks` 6, `in_vent_cap_ticks` 4, `short_window_ticks` 2.

## The counts

### Witnesses

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Kills a crewmate saw | 17/674 (2.5%) | 16/550 (2.9%) | 0/58 (0.0%) | 1/66 (1.5%) | 14/195 (7.2%) |
| Vent entries a crewmate saw | 54/482 (11.2%) | 45/396 (11.4%) | 4/42 (9.5%) | 5/44 (11.4%) | 16/140 (11.4%) |
| Vent exits a crewmate saw | 251/427 (58.8%) | 209/350 (59.7%) | 24/38 (63.2%) | 18/39 (46.2%) | 8/72 (11.1%) |
| Vent exits seen from the room surfaced into | 198/427 (46.4%) | 173/350 (49.4%) | 17/38 (44.7%) | 8/39 (20.5%) | 8/72 (11.1%) |
| Vent exits seen only from the room left | 53/427 (12.4%) | 36/350 (10.3%) | 7/38 (18.4%) | 10/39 (25.6%) | 0/72 by construction |
| Impostors seen venting, then ejected | 260/278 (93.5%) | 214/227 (94.3%) | 26/28 (92.9%) | 20/23 (87.0%) | 24/24 (100.0%) |
| Impostors who vented unseen, then ejected | 10/81 (12.3%) | 10/48 (20.8%) | 0/14 (0.0%) | 0/19 (0.0%) | 12/52 (23.1%) |
| Impostors who never vented, then ejected | 18/41 (43.9%) | 17/25 (68.0%) | 1/8 (12.5%) | 0/8 (0.0%) | 8/24 (33.3%) |

### Vent trips and surfacings

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Vent entries not after the impostor's own fresh kill | 90/482 (18.7%) | 88/396 (22.2%) | 0/42 (0.0%) | 2/44 (4.5%) | 0/140 by construction |
| Surfacings before the cap with someone in view | 247/427 (57.8%) | 212/350 (60.6%) | 18/38 (47.4%) | 17/39 (43.6%) | 0/72 by construction |
| Vent trips longer than the cap | n/a | n/a | n/a | n/a | 0/66 by construction |
| Surfacings at the cap | n/a | n/a | n/a | n/a | 5/72 (6.9%) |
| Vent exits into a room a crewmate stood in | 197/427 (46.1%) | 173/350 (49.4%) | 15/38 (39.5%) | 9/39 (23.1%) | 0/72 (0.0%) |
| Vent exits into a room the impostor could see a crewmate in | 103/427 (24.1%) | 91/350 (26.0%) | 8/38 (21.1%) | 4/39 (10.3%) | 0/72 (0.0%) |
| Vent exits while a crewmate stood in the room left | 23/427 (5.4%) | 17/350 (4.9%) | 2/38 (5.3%) | 4/39 (10.3%) | 0/72 (0.0%) |
| Surfacings in place with a crewmate arriving before the walk-out | n/a | n/a | n/a | n/a | 2/44 (4.5%) |
| Kills soon after the killer surfaced | 8/674 (1.2%) | 8/550 (1.5%) | 0/58 (0.0%) | 0/66 (0.0%) | 0/195 (0.0%) |

**Ticks inside per surfaced vent trip.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| 1 | 427 | 350 | 38 | 39 | 49 |
| 2 | 0 | 0 | 0 | 0 | 3 |
| 3 | 0 | 0 | 0 | 0 | 15 |
| 4 | 0 | 0 | 0 | 0 | 5 |

### Vent proof at meetings

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Meetings with vent proof | 260/531 (49.0%) | 215/449 (47.9%) | 26/43 (60.5%) | 19/39 (48.7%) | 24/117 (20.5%) |
| Impostor ejections in the vent band | 256/288 (88.9%) | 211/241 (87.6%) | 26/27 (96.3%) | 19/20 (95.0%) | 24/44 (54.5%) |
| Crewmate ejections in the vent band | 0/33 (0.0%) | 0/32 (0.0%) | 0/1 (0.0%) | n/a | 0/22 (0.0%) |
| Impostor ejections without vent proof | 32/288 (11.1%) | 30/241 (12.4%) | 1/27 (3.7%) | 1/20 (5.0%) | 20/44 (45.5%) |
| Vent-band ejections resting only on the room left | 42/256 (16.4%) | 29/211 (13.7%) | 6/26 (23.1%) | 7/19 (36.8%) | 0/24 by construction |
| Meetings without vent proof that ejected | 63/271 (23.2%) | 60/234 (25.6%) | 2/17 (11.8%) | 1/20 (5.0%) | 42/93 (45.2%) |
| Ejections without vent proof that removed an impostor | 32/63 (50.8%) | 30/60 (50.0%) | 1/2 (50.0%) | 1/1 (100.0%) | 20/42 (47.6%) |
| Button meetings with vent proof | 43/43 (100.0%) | 33/33 (100.0%) | 7/7 (100.0%) | 3/3 (100.0%) | 3/3 (100.0%) |

**Which vent moment the vent band rests on.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| both | 8 | 8 | 0 | 0 | 0 |
| entry only | 46 | 37 | 4 | 5 | 16 |
| exit only | 202 | 166 | 22 | 14 | 8 |

### Ejections at report meetings, by seat

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Reporter seats ejected | 30/488 (6.1%) | 29/416 (7.0%) | 1/36 (2.8%) | 0/36 (0.0%) | 17/114 (14.9%) |
| Reporter seats ejected, without vent proof | 29/271 (10.7%) | 28/234 (12.0%) | 1/17 (5.9%) | 0/20 (0.0%) | 17/93 (18.3%) |
| Reporter seats ejected, with vent proof | 1/217 (0.5%) | 1/182 (0.5%) | 0/19 (0.0%) | 0/16 (0.0%) | 0/21 (0.0%) |
| Other crewmate seats ejected | 2/1390 (0.1%) | 2/1318 (0.2%) | 0/36 (0.0%) | 0/36 (0.0%) | 5/367 (1.4%) |
| Other crewmate seats ejected, without vent proof | 2/703 (0.3%) | 2/666 (0.3%) | 0/17 (0.0%) | 0/20 (0.0%) | 5/291 (1.7%) |
| Other crewmate seats ejected, with vent proof | 0/687 (0.0%) | 0/652 (0.0%) | 0/19 (0.0%) | 0/16 (0.0%) | 0/76 (0.0%) |
| Impostor seats ejected | 247/669 (36.9%) | 210/597 (35.2%) | 20/36 (55.6%) | 17/36 (47.2%) | 41/195 (21.0%) |
| Impostor seats ejected, without vent proof | 32/340 (9.4%) | 30/303 (9.9%) | 1/17 (5.9%) | 1/20 (5.0%) | 20/158 (12.7%) |
| Impostor seats ejected, with vent proof | 215/329 (65.3%) | 180/294 (61.2%) | 19/19 (100.0%) | 16/16 (100.0%) | 21/37 (56.8%) |
| Reporters among the crewmates ejected | 30/32 (93.8%) | 29/31 (93.5%) | 1/1 (100.0%) | n/a | 17/22 (77.3%) |
| Reporters among the crewmate seats | 488/1878 (26.0%) | 416/1734 (24.0%) | 36/72 (50.0%) | 36/72 (50.0%) | 114/481 (23.7%) |

### Corpses and the state play resumes in

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Stale report meetings | 124/488 (25.4%) | 124/416 (29.8%) | 0/36 (0.0%) | 0/36 (0.0%) | 0/114 by construction |
| Meetings opening with another unreported corpse | 261/531 (49.2%) | 251/449 (55.9%) | 7/43 (16.3%) | 3/39 (7.7%) | 48/117 (41.0%) |
| Play resumes with an impostor in a vent | 20/379 (5.3%) | 20/345 (5.8%) | 0/15 (0.0%) | 0/19 (0.0%) | 0/102 by construction |
| Play resumes with a corpse on the floor | 203/379 (53.6%) | 203/345 (58.8%) | 0/15 (0.0%) | 0/19 (0.0%) | 0/102 by construction |
| Kills soon after a meeting | 107/302 (35.4%) | 101/276 (36.6%) | 3/12 (25.0%) | 3/14 (21.4%) | 0/109 (0.0%) |
| Meetings opening with an impostor in a vent | 72/531 (13.6%) | 63/449 (14.0%) | 4/43 (9.3%) | 5/39 (12.8%) | 66/117 (56.4%) |
| Impostors able to kill when a meeting opened | 263/733 (35.9%) | 238/651 (36.6%) | 12/43 (27.9%) | 13/39 (33.3%) | 54/200 (27.0%) |

**Corpse age at report.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| 1 | 42 | 41 | 0 | 1 | 19 |
| 2 | 81 | 65 | 8 | 8 | 13 |
| 3 | 85 | 65 | 11 | 9 | 33 |
| 4 | 110 | 91 | 11 | 8 | 30 |
| 5 | 29 | 24 | 1 | 4 | 6 |
| 6 | 39 | 31 | 4 | 4 | 6 |
| 7 | 23 | 21 | 1 | 1 | 2 |
| 8 | 11 | 10 | 0 | 1 | 2 |
| 9 | 12 | 12 | 0 | 0 | 0 |
| 10 | 7 | 7 | 0 | 0 | 2 |
| 11 | 14 | 14 | 0 | 0 | 1 |
| 12 | 9 | 9 | 0 | 0 | 0 |
| 13 | 5 | 5 | 0 | 0 | 0 |
| 14 | 2 | 2 | 0 | 0 | 0 |
| 16 | 3 | 3 | 0 | 0 | 0 |
| 17 | 2 | 2 | 0 | 0 | 0 |
| 18 | 1 | 1 | 0 | 0 | 0 |
| 19 | 6 | 6 | 0 | 0 | 0 |
| 20 | 2 | 2 | 0 | 0 | 0 |
| 23 | 3 | 3 | 0 | 0 | 0 |
| 25 | 1 | 1 | 0 | 0 | 0 |
| 32 | 1 | 1 | 0 | 0 | 0 |

### After a regroup

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Kills in the grace window after a regroup | n/a | n/a | n/a | n/a | 0/109 by construction |
| Reported corpses older than the last regroup | n/a | n/a | n/a | n/a | 0/64 by construction |
| Vent trips ended by a regroup | n/a | n/a | n/a | n/a | 47/140 (33.6%) |
| Kill witnesses pressing the button soon after a regroup | n/a | n/a | n/a | n/a | 0/3 (0.0%) |
| Sabotage active at a regroup | n/a | n/a | n/a | n/a | 5/102 (4.9%) |
| Prompts after a regroup missing an earlier regroup's notice | n/a | n/a | n/a | n/a | 0/722 by construction |

**Trigger-tick movement and task events a regroup drops.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Moved | n/a | n/a | n/a | n/a | 46 |
| TaskCompleted | n/a | n/a | n/a | n/a | 10 |
| TaskProgressed | n/a | n/a | n/a | n/a | 22 |

### The kill cooldown

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Kill cooldowns that differ from the recorded value | 0/1074 by construction | 0/850 by construction | 0/108 by construction | 0/116 by construction | 0/447 by construction |

**Kill cooldown writes by writer.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| after_kill | 674 | 550 | 58 | 66 | 195 |
| regroup | 0 | 0 | 0 | 0 | 152 |
| round_start | 400 | 300 | 50 | 50 | 100 |

### Meeting structure

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| The first reply accuses the opener | 401/531 (75.5%) | 328/449 (73.1%) | 36/43 (83.7%) | 37/39 (94.9%) | 80/117 (68.4%) |
| Someone accuses the opener | 436/531 (82.1%) | 362/449 (80.6%) | 37/43 (86.0%) | 37/39 (94.9%) | 105/117 (89.7%) |
| The opener speaks a second time | 0/531 (0.0%) | 0/449 (0.0%) | 0/43 (0.0%) | 0/39 (0.0%) | 87/117 (74.4%) |
| An accused opener answers | 0/436 by construction | 0/362 by construction | 0/37 by construction | 0/37 by construction | 87/105 (82.9%) |
| Meetings where someone spoke twice | 0/531 by construction | 0/449 by construction | 0/43 by construction | 0/39 by construction | 117/117 (100.0%) |
| Meetings with two repeat-speaker turns | 0/531 by construction | 0/449 by construction | 0/43 by construction | 0/39 by construction | 0/117 by construction |
| Meetings opened by an impostor | 0/531 by construction | 0/449 by construction | 0/43 by construction | 0/39 by construction | 0/117 by construction |
| Report openings that name the kill tick in the body handle | 488/488 (100.0%) | 416/416 (100.0%) | 36/36 (100.0%) | 36/36 (100.0%) | 0/114 by construction |
| Openers among ejected crewmates | 31/33 (93.9%) | 30/32 (93.8%) | 1/1 (100.0%) | n/a | 17/22 (77.3%) |
| Report meetings that skipped | 209/488 (42.8%) | 175/416 (42.1%) | 15/36 (41.7%) | 19/36 (52.8%) | 51/114 (44.7%) |

**Meetings by trigger.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| emergency | 43 | 33 | 7 | 3 | 3 |
| report | 488 | 416 | 36 | 36 | 114 |

**Ejected crewmate openers by trigger.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| emergency | 1 | 1 | 0 | 0 | 0 |
| report | 30 | 29 | 1 | 0 | 17 |

**Actions thrown away on trigger ticks.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| do_task | 540 | 513 | 13 | 14 | 129 |
| emergency | 14 | 13 | 1 | 0 | 0 |
| kill | 32 | 30 | 1 | 1 | 3 |
| move | 621 | 566 | 26 | 29 | 134 |
| repair_sabotage | 3 | 3 | 0 | 0 | 0 |
| report | 70 | 70 | 0 | 0 | 25 |
| sabotage | 1 | 1 | 0 | 0 | 0 |
| vent | 89 | 80 | 4 | 5 | 11 |
| wait | 289 | 260 | 13 | 16 | 156 |

### Rebuttals

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Rebuttals the selector would not have chosen | n/a | n/a | n/a | n/a | 0/117 by construction |
| Rebuttals carrying an alibi | n/a | n/a | n/a | n/a | 89/117 (76.1%) |
| Rebuttals carrying a whereabouts claim | n/a | n/a | n/a | n/a | 89/117 (76.1%) |
| Rebuttals carrying a sighting | n/a | n/a | n/a | n/a | 79/117 (67.5%) |
| Rebuttals that only redirect | n/a | n/a | n/a | n/a | 27/117 (23.1%) |
| Rebuttal accusations against players who already spoke | n/a | n/a | n/a | n/a | 116/116 (100.0%) |
| Opener rebuttals answering the charged tick | n/a | n/a | n/a | n/a | 17/18 (94.4%), 69 not evaluable |
| Ballots whose cited turn is a rebuttal | n/a | n/a | n/a | n/a | 57/691 (8.2%) |
| Ballots whose counter slot names a rebuttal | n/a | n/a | n/a | n/a | 175/691 (25.3%) |

**Who received the rebuttal, and who had accused them.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| another crewmate, answering a crewmate | n/a | n/a | n/a | n/a | 1 |
| another crewmate, answering an impostor | n/a | n/a | n/a | n/a | 1 |
| another impostor, answering a crewmate | n/a | n/a | n/a | n/a | 28 |
| the opener, answering a crewmate | n/a | n/a | n/a | n/a | 28 |
| the opener, answering an impostor | n/a | n/a | n/a | n/a | 59 |

### Ballots

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Impostor ballots that skip | 596/733 (81.3%) | 530/651 (81.4%) | 33/43 (76.7%) | 33/39 (84.6%) | 89/200 (44.5%) |
| Impostor ballots that name a player | 137/733 (18.7%) | 121/651 (18.6%) | 10/43 (23.3%) | 6/39 (15.4%) | 111/200 (55.5%) |
| Impostor ballots naming a player with a supported label | 134/137 (97.8%) | 120/121 (99.2%) | 8/10 (80.0%) | 6/6 (100.0%) | 111/111 (100.0%) |
| Impostor ballots recorded against a teammate | 0/733 by construction | 0/651 by construction | 0/43 by construction | 0/39 by construction | 0/200 by construction |
| Impostor ballots written against a teammate | 12/733 (1.6%) | 12/651 (1.8%) | 0/43 (0.0%) | 0/39 (0.0%) | 16/200 (8.0%) |
| Ejections whose confidence floor only impostors met | 0/321 (0.0%) | 0/273 (0.0%) | 0/28 (0.0%) | 0/20 (0.0%) | 0/66 (0.0%) |
| Ejections that would not stand with impostor ballots read as SKIP | 15/321 (4.7%) | 14/273 (5.1%) | 1/28 (3.6%) | 0/20 (0.0%) | 14/66 (21.2%) |
| Ejections that would not stand with impostor ballots removed | 7/321 (2.2%) | 6/273 (2.2%) | 1/28 (3.6%) | 0/20 (0.0%) | 5/66 (7.6%) |
| Own-kill ballot rows naming a teammate or held by a non-witness | n/a | n/a | n/a | n/a | 0/23 by construction |
| Own-kill ballot rows their holder cited | n/a | n/a | n/a | n/a | 21/23 (91.3%) |
| Kills a crewmate saw, held by a living witness at the next meeting | 17/17 (100.0%) | 16/16 (100.0%) | n/a | 1/1 (100.0%) | 14/14 (100.0%) |
| Held kills whose witness voted the killer | 16/17 (94.1%) | 15/16 (93.8%) | n/a | 1/1 (100.0%) | 13/14 (92.9%) |
| Held kills whose killer was ejected | 10/17 (58.8%) | 10/16 (62.5%) | n/a | 0/1 (0.0%) | 6/14 (42.9%) |
| Held kills whose killer some later meeting ejected | 13/17 (76.5%) | 13/16 (81.2%) | n/a | 0/1 (0.0%) | 8/14 (57.1%) |
| Held kills whose living witness was ejected | 2/17 (11.8%) | 2/16 (12.5%) | n/a | 0/1 (0.0%) | 5/14 (35.7%) |
| SKIP ballots labelled as holding nothing | 764/1183 (64.6%) | 702/1052 (66.7%) | 34/63 (54.0%) | 28/68 (41.2%) | 214/281 (76.2%) |

**Outcomes a re-tally changes.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| impostor ballots as SKIP: an impostor ejected -> no one ejected | 1 | 1 | 0 | 0 | 1 |
| impostor ballots as SKIP: another crewmate ejected -> no one ejected | 1 | 1 | 0 | 0 | 3 |
| impostor ballots as SKIP: no one ejected -> someone ejected | 1 | 1 | 0 | 0 | 1 |
| impostor ballots as SKIP: the reporter ejected -> a different player ejected | 0 | 0 | 0 | 0 | 1 |
| impostor ballots as SKIP: the reporter ejected -> no one ejected | 13 | 12 | 1 | 0 | 9 |
| impostor ballots removed: another crewmate ejected -> no one ejected | 0 | 0 | 0 | 0 | 1 |
| impostor ballots removed: no one ejected -> someone ejected | 23 | 23 | 0 | 0 | 3 |
| impostor ballots removed: the reporter ejected -> a different player ejected | 0 | 0 | 0 | 0 | 1 |
| impostor ballots removed: the reporter ejected -> no one ejected | 7 | 6 | 1 | 0 | 3 |

**What the next meeting did after a held kill.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| one living crew witness: a witness ejected | 2 | 2 | 0 | 0 | 5 |
| one living crew witness: another player ejected | 1 | 1 | 0 | 0 | 1 |
| one living crew witness: no one ejected | 4 | 3 | 0 | 1 | 2 |
| one living crew witness: the killer ejected | 9 | 9 | 0 | 0 | 1 |
| two or more living crew witnesses: a witness ejected | 0 | 0 | 0 | 0 | 0 |
| two or more living crew witnesses: another player ejected | 0 | 0 | 0 | 0 | 0 |
| two or more living crew witnesses: no one ejected | 0 | 0 | 0 | 0 | 0 |
| two or more living crew witnesses: the killer ejected | 1 | 1 | 0 | 0 | 5 |

**SKIP ballots by grounding label.**

| row | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| flag_only | 0 | 0 | 0 | 0 | 0 |
| invalid_citation | 0 | 0 | 0 | 0 | 0 |
| none_held | 764 | 702 | 34 | 28 | 214 |
| not_assessed | 17 | 17 | 0 | 0 | 17 |
| off_target | 128 | 101 | 10 | 17 | 6 |
| supported | 274 | 232 | 19 | 23 | 44 |
| uncited | 0 | 0 | 0 | 0 | 0 |
| unlabelled | 0 | 0 | 0 | 0 | 0 |

### Reported beside the counts

| cell | baseline-9, pooled | ml_corpus/9p2i (baseline-9) | ml_corpus/4p1i (baseline-9) | samples/4p1i (baseline-9) | samples/9p2i (stage-b-r2) |
| --- | --- | --- | --- | --- | --- |
| Games the impostors won | 77/250 (30.8%) | 45/150 (30.0%) | 14/50 (28.0%) | 18/50 (36.0%) | 24/50 (48.0%) |
| Ejections that removed an impostor | 288/321 (89.7%) | 241/273 (88.3%) | 27/28 (96.4%) | 20/20 (100.0%) | 44/66 (66.7%) |

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

**Surfacings at the cap** (`forced_surfacings`). Vent exits made exactly at the in-vent cap, over all vent exits. Reads `VentEntered`, `VentExited`, `meeting row`. Counted only in games recorded with `vent_exit_policy = look_and_wait`; in any other era it reads n/a.

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

**Reporter seats ejected** (`reporter_seats_ejected`). Report meetings that ejected their reporter, over the reporter's seats: one per report meeting, whatever the reporter's role. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Reporter seats ejected, without vent proof** (`reporter_seats_ejected_without_vent_proof`). Report meetings without vent proof that ejected their reporter, over the reporter's seats at report meetings without vent proof. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Reporter seats ejected, with vent proof** (`reporter_seats_ejected_with_vent_proof`). Report meetings with vent proof that ejected their reporter, over the reporter's seats at report meetings with vent proof. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Other crewmate seats ejected** (`other_crewmate_seats_ejected`). Seats of living crewmates other than the reporter that a report meeting ejected, over those seats at every report meeting. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Other crewmate seats ejected, without vent proof** (`other_crewmate_seats_ejected_without_vent_proof`). Seats of living crewmates other than the reporter that a report meeting without vent proof ejected, over those seats at report meetings without vent proof. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Other crewmate seats ejected, with vent proof** (`other_crewmate_seats_ejected_with_vent_proof`). Seats of living crewmates other than the reporter that a report meeting with vent proof ejected, over those seats at report meetings with vent proof. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Impostor seats ejected** (`impostor_seats_ejected`). Seats of living impostors other than the reporter that a report meeting ejected, over those seats at every report meeting. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Impostor seats ejected, without vent proof** (`impostor_seats_ejected_without_vent_proof`). Seats of living impostors other than the reporter that a report meeting without vent proof ejected, over those seats at report meetings without vent proof. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Impostor seats ejected, with vent proof** (`impostor_seats_ejected_with_vent_proof`). Seats of living impostors other than the reporter that a report meeting with vent proof ejected, over those seats at report meetings with vent proof. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Reporters among the crewmates ejected** (`reporters_among_ejected_crewmates`). Crewmates a report meeting ejected who were its reporter, over all crewmates report meetings ejected. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Reporters among the crewmate seats** (`reporters_among_crewmate_seats`). Crewmate seats at report meetings that were the reporter's, over all crewmate seats at report meetings. Reads `MeetingTriggered`, `state at the meeting`, `meeting row`, `meeting row flags`.

**Stale report meetings** (`stale_report_meetings`). Report meetings whose reported corpse already lay on the floor when the previous meeting opened, over all report meetings. Reads `MeetingTriggered`, `state at the meeting`. Zero by construction while `meeting_reset = hub_with_grace`.

**Meetings opening with another unreported corpse** (`meetings_opening_with_another_unreported_corpse`). Meetings that opened with a corpse other than the reported one that no one had discovered, over all meetings. Reads `state at the meeting`.

**Play resumes with an impostor in a vent** (`play_resumes_with_impostor_in_vent`). Meetings after which play resumed with an impostor inside a vent, over meetings after which play resumed. Reads `state after the meeting`. Zero by construction while `meeting_reset = hub_with_grace`.

**Play resumes with a corpse on the floor** (`play_resumes_with_corpse`). Meetings after which play resumed with a corpse on the floor, over meetings after which play resumed. Reads `state after the meeting`. Zero by construction while `meeting_reset = hub_with_grace`.

**Kills soon after a meeting** (`post_meeting_kills_soon_after`). Kills made at most 2 ticks after the previous meeting's tick, over all kills made after some meeting. Reads `Killed`, `meeting row`.

**Meetings opening with an impostor in a vent** (`meetings_opening_with_impostor_in_vent`). Meetings that opened with an impostor inside a vent, over all meetings. Reads `state at the meeting`.

**Impostors able to kill when a meeting opened** (`impostor_cooldown_zero_at_open`). Living impostors whose kill cooldown was zero when a meeting opened, over living impostors at every meeting. Reads `state at the meeting`.

**Kills in the grace window after a regroup** (`kills_in_grace_window_after_regroup`). Kills made on a tick after a regroup meeting no later than the recorded kill cooldown, else the map's, over all kills made between a regroup and the next meeting. Reads `Killed`, `meeting row`. Zero by construction while `meeting_reset = hub_with_grace`.

**Reported corpses older than the last regroup** (`report_corpses_older_than_last_close`). Report meetings whose reported victim was killed on or before the previous meeting's tick, over report meetings whose previous meeting regrouped. Reads `Killed`, `MeetingTriggered`, `meeting row`. Zero by construction while `meeting_reset = hub_with_grace`.

**Vent trips ended by a regroup** (`trips_closed_by_regroup`). Vent trips that ended because a regroup cleared the vent, with no exit, over all vent trips that ended. Reads `VentEntered`, `VentExited`, `meeting row`. Counted only in games recorded with `meeting_reset = hub_with_grace`; in any other era it reads n/a.

**Kill witnesses pressing the button soon after a regroup** (`kill_witness_button_calls_soon_after_regroup`). Button meetings called at most 6 ticks after a regroup by a player who witnessed a kill since it, over button meetings whose previous meeting regrouped. Reads `Killed`, `MeetingTriggered`, `meeting row`.

**Sabotage active at a regroup** (`sabotage_active_at_regroup`). Regroup meetings that opened with a sabotage active, over all regroup meetings. Reads `state at the meeting`.

**Prompts after a regroup missing an earlier regroup's notice** (`prompts_missing_a_regroup_notice`). Recorded meeting prompts of a player at a meeting after a regroup that lack the notice of some earlier regroup of the same game, in the wording the memory renders from that regroup's tick and room, over all such prompts. Reads `recorded meeting prompts`, `meeting row`. Zero by construction while `meeting_reset = hub_with_grace`.

**Kill cooldowns that differ from the recorded value** (`kill_cooldowns_differing_from_recorded`). Impostor kill cooldowns that differ from the recorded kill cooldown, else the map's, read on the state each engine write leaves: every impostor at round start, the killer after each of its kills and every living impostor after each regroup; over all such writes. Reads `state at round start`, `Killed`, `state after the meeting`. Zero by construction in every recording.

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

**Rebuttals carrying a sighting** (`rebuttals_with_sighting`). Repeat-speaker turns carrying a sighting (an observation naming a player seen in a room, venting, killing or moving, the speaker included), over all repeat-speaker turns. Reads `meeting row turns`.

**Rebuttals that only redirect** (`rebuttals_redirect_only`). Repeat-speaker turns carrying an accusation and no alibi, whereabouts or sighting, over all repeat-speaker turns. Reads `meeting row turns`.

**Rebuttal accusations against players who already spoke** (`rebuttal_accusations_against_earlier_speakers`). Accusations in repeat-speaker turns naming a player who spoke earlier in the meeting, over all accusations in repeat-speaker turns. Reads `meeting row turns`.

**Opener rebuttals answering the charged tick** (`opener_rebuttals_answering_charged_tick`). Repeat-speaker turns by the opener carrying an alibi leg, a whereabouts claim or a sighting at a tick the answered turn observed the opener, over such turns whose answered turn observed the opener at some tick; the rest are not evaluable. Reads `meeting row turns`.

**Ballots whose cited turn is a rebuttal** (`ballots_citing_a_rebuttal`). Ballots whose cited turn is a repeat-speaker turn of the same meeting, over all ballots at meetings with a repeat-speaker turn. Reads `meeting row turns`, `meeting row ballots`. Counted only in games recorded with `bounded_rebuttal_version = 1`; in any other era it reads n/a.

**Ballots whose counter slot names a rebuttal** (`ballots_countering_with_a_rebuttal`). Ballots whose counter slot, the strongest thing the voter held pointing away from its choice, names a repeat-speaker turn of the same meeting, over all ballots at meetings with a repeat-speaker turn. Reads `meeting row turns`, `meeting row ballots`. Counted only in games recorded with `bounded_rebuttal_version = 1`; in any other era it reads n/a.

**Impostor ballots that skip** (`impostor_skip_ballots`). Impostor ballots whose recorded target is SKIP, over all impostor ballots. Reads `meeting row ballots`.

**Impostor ballots that name a player** (`impostor_eject_ballots`). Impostor ballots whose recorded target is a player, over all impostor ballots. Reads `meeting row ballots`.

**Impostor ballots naming a player with a supported label** (`impostor_ejects_labelled_supported`). Impostor ballots naming a player whose meeting-layer grounding label is supported, over impostor ballots naming a player. Reads `meeting row ballots`.

**Impostor ballots recorded against a teammate** (`recorded_teammate_ballot_targets`). Impostor ballots whose recorded target is a fellow impostor, over all impostor ballots. Reads `meeting row ballots`. Zero by construction in every recording.

**Impostor ballots written against a teammate** (`authored_teammate_ballot_targets`). Impostor ballots whose authored target, read from the typed guard fields, is a fellow impostor, over all impostor ballots. Reads `meeting row ballots`.

**Ejections whose confidence floor only impostors met** (`ejections_carried_only_by_impostor_ballots`). Ejections where every ballot for the ejected player at or above the tally's recorded confidence floor was cast by an impostor, over all ejections. Reads `meeting row ballots`.

**Ejections that would not stand with impostor ballots read as SKIP** (`ejections_undone_with_impostor_ballots_as_skip`). Ejections whose re-tally, with every impostor ballot read as SKIP and every other ballot held fixed, ejects no one or a different player, over all ejections. Reads `meeting row ballots`.

**Ejections that would not stand with impostor ballots removed** (`ejections_undone_with_impostor_ballots_removed`). Ejections whose re-tally, with every impostor ballot removed and every other ballot held fixed, ejects no one or a different player, over all ejections. Reads `meeting row ballots`.

**Own-kill ballot rows naming a teammate or held by a non-witness** (`own_kill_rows_breaching`). Served own-kill rows that name the holder's fellow impostor as the killer, whatever they cite, or that do not cite, by the holder's own observation id, a kill the named player made with the holder among its witnesses, over all served own-kill rows. A row citing nothing counts here, because the row is specified to cite its kill. Reads `recorded ballot prompt`, `Killed`. Zero by construction while `ballot_kill_row_version = 1`.

**Own-kill ballot rows their holder cited** (`own_kill_rows_cited_by_holder`). Served own-kill rows whose holder's ballot cites the row's observation, over all served own-kill rows. Reads `recorded ballot prompt`, `meeting row ballots`.

**Kills a crewmate saw, held by a living witness at the next meeting** (`crew_witnessed_kills_held_at_next_meeting`). Crew-witnessed kills with a crewmate witness alive at the next meeting, over crew-witnessed kills a meeting followed; the rest are not evaluable. Reads `Killed`, `meeting row`.

**Held kills whose witness voted the killer** (`held_kill_witnesses_voting_killer`). Held crew-witnessed kills where a living witness's ballot names the killer, over held crew-witnessed kills. Reads `Killed`, `meeting row ballots`.

**Held kills whose killer was ejected** (`held_kill_killers_ejected`). Held crew-witnessed kills whose killer the next meeting ejected, over held crew-witnessed kills. Reads `Killed`, `meeting row`.

**Held kills whose killer some later meeting ejected** (`held_kill_killers_ejected_at_any_later_meeting`). Held crew-witnessed kills whose killer the next meeting, or any meeting after it, ejected, over held crew-witnessed kills. Reads `Killed`, `meeting row`.

**Held kills whose living witness was ejected** (`held_kill_witnesses_ejected`). Held crew-witnessed kills where the next meeting ejected one of the kill's living crew witnesses, over held crew-witnessed kills. Reads `Killed`, `meeting row`.

**SKIP ballots labelled as holding nothing** (`skips_holding_nothing`). SKIP ballots, whatever the voter's role, whose recorded grounding label says the voter stated outright that it held nothing that resolves the vote, over all SKIP ballots. The label restates the voter's own statement; it is not a checked fact. Reads `meeting row ballots`.

**Games the impostors won** (`impostor_wins`). Games whose recorded winner is the impostors, over games with a recorded winner. Reads `game over row`.

**Ejections that removed an impostor** (`role_correct_ejections`). Impostor ejections, over all ejections. Reported, never a gate. Reads `meeting row`.

**Ticks inside per surfaced vent trip** (`ticks_inside_per_trip`). Vent exits by the number of play ticks the impostor spent inside, the count restarting at a meeting boundary. Reads `VentEntered`, `VentExited`, `meeting row`.

**Which vent moment the vent band rests on** (`vent_band_by_moment`). Vent-band impostor ejections by whether a crewmate saw the ejected impostor's exit only, entry only, both, or neither before the meeting. Reads `VentEntered`, `VentExited`, `meeting row flags`.

**Corpse age at report** (`corpse_age_at_report`). Report meetings by the ticks between the reported victim's kill and the meeting. Reads `Killed`, `MeetingTriggered`.

**Trigger-tick movement and task events a regroup drops** (`trigger_tick_events_dropped_by_regroup`). Movement and task events on the trigger tick of every regroup meeting, by kind. Reads `Moved`, `TaskProgressed`, `TaskCompleted`. Counted only in games recorded with `meeting_reset = hub_with_grace`; in any other era it reads n/a.

**Kill cooldown writes by writer** (`kill_cooldown_writes_by_writer`). The writes the kill cooldown cell checks, by the engine step that made them: round_start (the seeding), after_kill (the killer's own cooldown) and regroup (every living impostor at a regroup). Reads `state at round start`, `Killed`, `state after the meeting`.

**Meetings by trigger** (`meetings_by_trigger`). Meetings by what opened them: a reported corpse or a button press. Reads `MeetingTriggered`.

**Ejected crewmate openers by trigger** (`innocent_opener_ejections_by_trigger`). Crewmate ejections that removed the opener, by what opened the meeting. Reads `MeetingTriggered`, `meeting row`.

**Actions thrown away on trigger ticks** (`actions_thrown_away_on_trigger_ticks`). Submitted actions the engine never ran because an earlier action on the same tick opened a meeting, by action type, read from the recorded dispositions; tick rows recorded without dispositions are not evaluable. Reads `recorded action dispositions`.

**Who received the rebuttal, and who had accused them** (`rebuttal_beneficiaries`). Repeat-speaker turns by the speaker's seat (the opener, or another crewmate or impostor) and the role of the speaker of the turn answered. Reads `meeting row turns`. Counted only in games recorded with `bounded_rebuttal_version = 1`; in any other era it reads n/a.

**Outcomes a re-tally changes** (`retally_outcome_changes`). Meetings whose re-tally differs from the recorded outcome, by re-tally, by the recorded outcome (the reporter, another crewmate, an impostor or no one ejected) and by what the re-tally gives instead. Every other ballot is held fixed; real voters would have heard different speech. Reads `MeetingTriggered`, `meeting row ballots`.

**What the next meeting did after a held kill** (`held_kill_next_meeting_outcomes`). Held crew-witnessed kills by how many of the kill's crew witnesses were alive at the next meeting, one or two or more, and by what that meeting did: ejected the killer, ejected one of those witnesses, ejected another player, or ejected no one. Every row is listed. Reads `Killed`, `meeting row`.

**SKIP ballots by grounding label** (`skips_by_grounding_label`). Every SKIP ballot by its recorded grounding label. Every label the meeting layer can write is listed, and unlabelled counts a ballot recorded before ballots were labelled. Reads `meeting row ballots`.
