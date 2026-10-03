# Route-check replay

Written by `experiments/lab/route_check_replay.py` from `experiments/lab/results-route-check-replay.json`; `--check` recomputes both from the commits recorded below.

## Decision informed

Whether a round 3 with one meeting-layer route check is worth the owner's spend, and which check. This report decides nothing and authorizes no recording.

## Hypothesis

Some ejections in the recorded games rest on a charge whose stated pair of places the map or the public regroup in fact allows, and at least one candidate check would have put a line about that pair in front of a voter who voted to eject.

## Method

Each column is one recording, read alone and never pooled, from the exact commit in the table below; the table also gives the seeds and the roster (players, impostors) that column's recorded games hold. Every meeting is re-run through the committed reconstruction walk with the recording's own settings: every state hash and every recorded prompt is reproduced or the run stops, and the meetings agree one for one with the gameplay census.

| column | commit | path | tree | declared config | seeds | players | impostors | games with a meeting |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| s9 | `d41c90067a0023d08997231f181cc02deb6461bc` | `replays/samples/9p2i` | `5c12c060e75b026daf643ab8b20e5aaca8de20b0` | none | 0-49 | 9 | 2 | 50 |
| r1 | `5877adb48e046042a1e2927675451f896168673a` | `replays/candidates/stage-b-r1/9p2i` | `2c0529eb694fc011c836cb564d241101da1957e4` | `replays/candidates/stage-b-r1/experiment-config.json` | 0-49 | 9 | 2 | 50 |
| r2 | `5877adb48e046042a1e2927675451f896168673a` | `replays/samples/9p2i` | `8197dc791afbe432186a5bd8c16e3e16f7dd8477` | `replays/samples/9p2i/experiment-config.json` | 0-49 | 9 | 2 | 50 |

Terms, as counted here:

- A **placement** is a player put in a room at a tick by something said at the meeting: a sighting (its subject and the company it names), a movement sighting (its destination), a whereabouts (its speaker), an alibi route (each end of each stay) or a vent sighting. Nothing is filtered out.
- A pair of placements of one player is **reconcilable** when the rooms differ and the doorway hops between them are at least one and at most the ticks elapsed, or when a public regroup falls inside the interval.
- A **charge** is an eject ballot whose cited turn places the target, or a contradiction flag naming the target whose two events both place the target.
- A **misjudged case** is an ejection with a charge whose placement is one end of a reconcilable pair. This is a count of process, not of who was guilty.
- A **witness meeting** is a report whose reporter the engine recorded watching a kill since the previous meeting; an **ejected witness** is that reporter voted out.
- A check **reaches** a case when it shows a line about the ejected player over two different rooms that reconciles, fits or crosses the regroup, to at least one voter who voted to eject; it **reaches the charge** when that line's pair holds a charged placement. Lines saying the timing is insufficient are counted apart and never reach.
- **(a) as built** is the corroboration ledger's walkable-pair clause with the movement records and regroup ticks the meeting manager passes: one door apart, one tick apart, at most two pairs per player. **(a) transcript only** drops those two inputs, as the earlier transcript-only probe did; the legs **no movement records** and **no regroup ticks** drop one each. **With movement origins** is informational and no check: (a) as built with each spoken movement sighting also placing its subject in the room it left, one tick earlier, a placement the live clause deliberately does not make.
- **(b) as recorded** is the travel-check block of the evidence-reasoning version 2 memory, rendered from the memory each voter held when the meeting opened and kept only if the ballot's memory budget keeps it. **(b-snapshot)** relabels each plain recorded sighting a start-of-tick snapshot; it is an approximation of the observation delivery that version requires, which would also add event rows these recordings do not hold.
- **(c) reference** pairs every stated placement of a living candidate, including alibi stays, over the whole map, and names a crossing of the regroup. It is a reading computed here, not a mechanism.
- **Lines shown to voters** sums, over the voters of every meeting, the lines each one would read: one per walkable pair under (a), one per kept travel-check row under (b), one per candidate with a reconciled pair under (c). A voter reads (a) and (c) lines about every candidate but themself.
- The **judgment net** is the committed pattern for ballot prose asserting a physical impossibility (`scripts/counterfactual_phase21.py`); it is an informational column, never the reading.
- An unreached misjudged case is given the first reason, in this order, that applies to any of its reconcilable charged pairs: placement kind outside the check's inputs; dropped by the relevance gate; beyond the hop bound; beyond the tick bound; cut by the cap or the memory budget; claim not yet held at ballot time; the unknown-phase rule; none of the listed reasons.

Replayed meetings do not carry their consequences forward: a different ejection would have changed every later meeting, so these counts are per meeting and never a re-simulated outcome.

## Result

### Column s9

| meetings | count | witness meetings | ejections | charges at the table | resting on a reconcilable pair | misjudged |
| --- | --- | --- | --- | --- | --- | --- |
| all meetings | 145 | 3 | 90 | 513 | 332 | 50 |
| report vent proof | 60 | 0 | 60 | 313 | 185 | 34 |
| report no vent proof | 75 | 3 | 20 | 144 | 110 | 9 |
| button | 10 | 0 | 10 | 56 | 37 | 7 |

| check | lines shown to voters | reaches misjudged | reaches the charge |
| --- | --- | --- | --- |
| (a) as built | 651 | 13 of 50 | 12 |
| (a) transcript only | 404 | 8 of 50 | 8 |
| (b) as recorded | 2697 | 27 of 50 | 26 |
| (b-snapshot), approximation | 2657 | 30 of 50 | 27 |
| (c) reference | 2405 | 32 of 50 | 28 |

By ejection class, as description only (an ejected witness is innocent too). Each check column counts the class's misjudged cases that check reaches; the judgment-net column counts the class's ejections with an eject ballot the net tags:

| class | ejections | misjudged | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference | judgment net |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| innocent | 9 | 6 | 5 | 0 | 3 | 4 | 6 | 6 |
| impostor | 81 | 44 | 8 | 8 | 24 | 26 | 26 | 23 |
| ejected witness | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

Ejections with a walkable pair under each leg of (a) (any pair, charged or not):

| class | ejections | as built | transcript only | no movement records | no regroup ticks | with movement origins |
| --- | --- | --- | --- | --- | --- | --- |
| innocent | 9 | 5 | 0 | 0 | 5 | 6 |
| impostor | 81 | 8 | 8 | 8 | 8 | 19 |
| ejected witness | 1 | 0 | 0 | 0 | 0 | 0 |

Ejections on which the legs of (a) disagree, and the input that moves each between (a) as built and the transcript-only leg:

| seed | meeting | classes | as built | transcript only | no movement records | no regroup ticks | with movement origins | moved by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 2 | impostor | False | False | False | False | True | not moved |
| 6 | 0 | impostor | False | False | False | False | True | not moved |
| 6 | 2 | innocent | True | False | False | True | True | movement records |
| 7 | 0 | impostor | False | False | False | False | True | not moved |
| 8 | 0 | impostor | False | False | False | False | True | not moved |
| 9 | 1 | innocent | True | False | False | True | True | movement records |
| 12 | 0 | innocent | True | False | False | True | True | movement records |
| 13 | 0 | innocent | True | False | False | True | True | movement records |
| 16 | 2 | impostor | False | False | False | False | True | not moved |
| 24 | 0 | impostor | False | False | False | False | True | not moved |
| 29 | 0 | impostor | False | False | False | False | True | not moved |
| 29 | 1 | innocent | False | False | False | False | True | not moved |
| 35 | 2 | impostor | False | False | False | False | True | not moved |
| 38 | 1 | impostor | False | False | False | False | True | not moved |
| 39 | 0 | innocent | True | False | False | True | True | movement records |
| 40 | 2 | impostor | False | False | False | False | True | not moved |
| 45 | 1 | impostor | False | False | False | False | True | not moved |

Unreached misjudged cases by reason:

| reason | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference |
| --- | --- | --- | --- | --- | --- |
| placement kind outside the check's inputs | 35 | 35 | 0 | 0 | 17 |
| dropped by the relevance gate | 2 | 7 | 0 | 0 | 1 |
| beyond the hop bound | 0 | 0 | 0 | 0 | 0 |
| beyond the tick bound | 0 | 0 | 0 | 0 | 0 |
| cut by the cap or the memory budget | 0 | 0 | 12 | 12 | 0 |
| claim not yet held at ballot time | 0 | 0 | 7 | 5 | 0 |
| the unknown-phase rule | 0 | 0 | 0 | 0 | 0 |
| none of the listed reasons | 0 | 0 | 4 | 3 | 0 |

The same cases' reconcilable charged pairs, each given its own first reason:

| reason | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference |
| --- | --- | --- | --- | --- | --- |
| placement kind outside the check's inputs | 242 | 242 | 0 | 0 | 25 |
| dropped by the relevance gate | 16 | 61 | 0 | 0 | 1 |
| beyond the hop bound | 12 | 10 | 0 | 0 | 0 |
| beyond the tick bound | 6 | 7 | 0 | 0 | 0 |
| cut by the cap or the memory budget | 0 | 0 | 25 | 25 | 0 |
| claim not yet held at ballot time | 0 | 0 | 25 | 12 | 0 |
| the unknown-phase rule | 0 | 0 | 6 | 0 | 0 |
| none of the listed reasons | 12 | 12 | 29 | 22 | 0 |

Lines saying the timing is insufficient, about a misjudged ejected player over two rooms, shown to a voter who voted to eject: (b) 225, (b-snapshot) 84.

s9 agreement: (a) as built reads 13 of 90 ejections with a walkable pair, the figure the round-2 record's committed cells imply; the transcript-only leg reads 8 of 90 and would not.

### Column r1

| meetings | count | witness meetings | ejections | charges at the table | resting on a reconcilable pair | misjudged |
| --- | --- | --- | --- | --- | --- | --- |
| all meetings | 124 | 3 | 54 | 406 | 265 | 29 |
| report vent proof | 20 | 0 | 20 | 135 | 55 | 7 |
| report no vent proof | 98 | 3 | 28 | 222 | 182 | 19 |
| button | 6 | 0 | 6 | 49 | 28 | 3 |

| check | lines shown to voters | reaches misjudged | reaches the charge |
| --- | --- | --- | --- |
| (a) as built | 616 | 8 of 29 | 7 |
| (a) transcript only | 442 | 10 of 29 | 8 |
| (b) as recorded | 2232 | 8 of 29 | 7 |
| (b-snapshot), approximation | 2196 | 15 of 29 | 11 |
| (c) reference | 2350 | 20 of 29 | 20 |

By ejection class, as description only (an ejected witness is innocent too). Each check column counts the class's misjudged cases that check reaches; the judgment-net column counts the class's ejections with an eject ballot the net tags:

| class | ejections | misjudged | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference | judgment net |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| innocent | 15 | 13 | 8 | 8 | 2 | 6 | 13 | 3 |
| impostor | 39 | 16 | 0 | 2 | 6 | 9 | 7 | 5 |
| ejected witness | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Ejections with a walkable pair under each leg of (a) (any pair, charged or not):

| class | ejections | as built | transcript only | no movement records | no regroup ticks | with movement origins |
| --- | --- | --- | --- | --- | --- | --- |
| innocent | 15 | 9 | 9 | 8 | 10 | 10 |
| impostor | 39 | 1 | 2 | 0 | 3 | 2 |
| ejected witness | 0 | 0 | 0 | 0 | 0 | 0 |

Ejections on which the legs of (a) disagree, and the input that moves each between (a) as built and the transcript-only leg:

| seed | meeting | classes | as built | transcript only | no movement records | no regroup ticks | with movement origins | moved by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 0 | innocent | True | False | False | True | True | movement records |
| 17 | 1 | innocent | False | True | False | True | False | regroup ticks |
| 23 | 1 | impostor | False | True | False | True | False | regroup ticks |
| 29 | 0 | impostor | False | False | False | False | True | not moved |
| 33 | 0 | impostor | True | False | False | True | True | movement records |
| 35 | 0 | innocent | False | False | False | False | True | not moved |
| 36 | 1 | impostor | False | True | False | True | False | regroup ticks |

Unreached misjudged cases by reason:

| reason | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference |
| --- | --- | --- | --- | --- | --- |
| placement kind outside the check's inputs | 16 | 15 | 2 | 2 | 8 |
| dropped by the relevance gate | 4 | 3 | 0 | 0 | 1 |
| beyond the hop bound | 1 | 1 | 0 | 0 | 0 |
| beyond the tick bound | 0 | 0 | 0 | 0 | 0 |
| cut by the cap or the memory budget | 0 | 0 | 11 | 7 | 0 |
| claim not yet held at ballot time | 0 | 0 | 3 | 2 | 0 |
| the unknown-phase rule | 0 | 0 | 2 | 0 | 0 |
| none of the listed reasons | 0 | 0 | 3 | 3 | 0 |

The same cases' reconcilable charged pairs, each given its own first reason:

| reason | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference |
| --- | --- | --- | --- | --- | --- |
| placement kind outside the check's inputs | 214 | 124 | 5 | 5 | 25 |
| dropped by the relevance gate | 37 | 22 | 0 | 0 | 13 |
| beyond the hop bound | 4 | 6 | 0 | 0 | 0 |
| beyond the tick bound | 0 | 0 | 0 | 0 | 0 |
| cut by the cap or the memory budget | 0 | 0 | 107 | 86 | 0 |
| claim not yet held at ballot time | 0 | 0 | 128 | 91 | 0 |
| the unknown-phase rule | 0 | 0 | 16 | 0 | 0 |
| none of the listed reasons | 0 | 0 | 131 | 68 | 0 |

Lines saying the timing is insufficient, about a misjudged ejected player over two rooms, shown to a voter who voted to eject: (b) 84, (b-snapshot) 28.

### Column r2

| meetings | count | witness meetings | ejections | charges at the table | resting on a reconcilable pair | misjudged |
| --- | --- | --- | --- | --- | --- | --- |
| all meetings | 117 | 14 | 66 | 402 | 276 | 40 |
| report vent proof | 21 | 1 | 21 | 141 | 68 | 9 |
| report no vent proof | 93 | 13 | 42 | 246 | 197 | 29 |
| button | 3 | 0 | 3 | 15 | 11 | 2 |

| check | lines shown to voters | reaches misjudged | reaches the charge |
| --- | --- | --- | --- |
| (a) as built | 602 | 15 of 40 | 15 |
| (a) transcript only | 493 | 13 of 40 | 9 |
| (b) as recorded | 2158 | 16 of 40 | 14 |
| (b-snapshot), approximation | 2135 | 20 of 40 | 16 |
| (c) reference | 2323 | 29 of 40 | 28 |

By ejection class, as description only (an ejected witness is innocent too). Each check column counts the class's misjudged cases that check reaches; the judgment-net column counts the class's ejections with an eject ballot the net tags:

| class | ejections | misjudged | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference | judgment net |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| innocent | 22 | 21 | 15 | 12 | 8 | 12 | 21 | 10 |
| impostor | 44 | 19 | 0 | 1 | 8 | 8 | 8 | 6 |
| ejected witness | 5 | 5 | 2 | 0 | 2 | 3 | 5 | 5 |

Ejections with a walkable pair under each leg of (a) (any pair, charged or not):

| class | ejections | as built | transcript only | no movement records | no regroup ticks | with movement origins |
| --- | --- | --- | --- | --- | --- | --- |
| innocent | 22 | 15 | 12 | 11 | 16 | 16 |
| impostor | 44 | 0 | 1 | 0 | 1 | 4 |
| ejected witness | 5 | 2 | 0 | 0 | 2 | 3 |

Ejections on which the legs of (a) disagree, and the input that moves each between (a) as built and the transcript-only leg:

| seed | meeting | classes | as built | transcript only | no movement records | no regroup ticks | with movement origins | moved by |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | impostor | False | False | False | False | True | not moved |
| 2 | 0 | innocent | True | False | False | True | True | movement records |
| 7 | 0 | impostor | False | False | False | False | True | not moved |
| 16 | 1 | impostor | False | True | False | True | False | regroup ticks |
| 21 | 1 | innocent | False | True | False | True | False | regroup ticks |
| 22 | 1 | impostor | False | False | False | False | True | not moved |
| 28 | 0 | innocent, ejected witness | True | False | False | True | True | movement records |
| 29 | 0 | innocent, ejected witness | False | False | False | False | True | not moved |
| 38 | 1 | impostor | False | False | False | False | True | not moved |
| 43 | 0 | innocent, ejected witness | True | False | False | True | True | movement records |
| 45 | 1 | innocent | True | False | False | True | True | movement records |

Unreached misjudged cases by reason:

| reason | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference |
| --- | --- | --- | --- | --- | --- |
| placement kind outside the check's inputs | 18 | 19 | 4 | 3 | 9 |
| dropped by the relevance gate | 7 | 8 | 0 | 0 | 2 |
| beyond the hop bound | 0 | 0 | 0 | 0 | 0 |
| beyond the tick bound | 0 | 0 | 0 | 0 | 0 |
| cut by the cap or the memory budget | 0 | 0 | 13 | 10 | 0 |
| claim not yet held at ballot time | 0 | 0 | 4 | 4 | 0 |
| the unknown-phase rule | 0 | 0 | 0 | 0 | 0 |
| none of the listed reasons | 0 | 0 | 3 | 3 | 0 |

The same cases' reconcilable charged pairs, each given its own first reason:

| reason | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot), approximation | (c) reference |
| --- | --- | --- | --- | --- | --- |
| placement kind outside the check's inputs | 203 | 295 | 24 | 13 | 26 |
| dropped by the relevance gate | 84 | 88 | 0 | 0 | 5 |
| beyond the hop bound | 11 | 15 | 0 | 0 | 0 |
| beyond the tick bound | 12 | 8 | 0 | 0 | 0 |
| cut by the cap or the memory budget | 0 | 0 | 137 | 85 | 0 |
| claim not yet held at ballot time | 0 | 0 | 198 | 176 | 0 |
| the unknown-phase rule | 0 | 0 | 10 | 0 | 0 |
| none of the listed reasons | 0 | 0 | 289 | 217 | 0 |

Lines saying the timing is insufficient, about a misjudged ejected player over two rooms, shown to a voter who voted to eject: (b) 115, (b-snapshot) 49.

## Decision input

The card's rule, applied to r2 and set beside s9 and r1: with M the misjudged cases, W those at witness meetings and R(X) the cases check X reaches, branch 1 when M is empty; branch 2 when (b-snapshot) reaches at least half of M, and of W when W is not empty; branch 3 when (c) does; branch 4 otherwise.

| column | M | W | R(b) / of W | R(b-snapshot) / of W | R(c) / of W | branch |
| --- | --- | --- | --- | --- | --- | --- |
| s9 | 50 | 0 | 27 / 0 | 30 / 0 | 32 / 0 | 2: name evidence_reasoning_version = 2, conditional on the owner lifting the temporal-observations exclusion it requires |
| r1 | 29 | 0 | 8 / 0 | 15 / 0 | 20 / 0 | 2: name evidence_reasoning_version = 2, conditional on the owner lifting the temporal-observations exclusion it requires |
| r2 | 40 | 7 | 16 / 2 | 20 / 3 | 29 / 7 | 3: name the narrow new field, shaped by the reference reading's unreached reasons |

The branch is advisory and gates nothing. Branch 2 would need the owner to lift the exclusion of temporal observations, which changes every prompt and fails the validity gate's provenance check, and that field also carries death-evidence and account-uncertainty lines; its one live reading cast 14 eject and 136 skip ballots. A round 3 is the owner's spend decision.

