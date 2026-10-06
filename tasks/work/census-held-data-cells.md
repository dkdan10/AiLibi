# Three held-data cells and the route field's conformance cell

**Status:** ready

## Outcome

The owner's first goal is that a vote or a skip rests on data the agent holds, true or false. The gameplay census
reads that goal through recorded labels only. It counts SKIP ballots labelled as holding nothing (214 of 281 on the
shown set) but never checks the label against what the voter was shown. It never asks whether the line an EJECT
cited was true. And the one measured failure of the goal on the shown set, charges against places the map or the
public regroup reconciles, is counted only by an offline lab reading. The baselines memo (Part 3.4, items 1 to 3)
names these three as the measures a round-3 pre-registration should carry. Round 3 is a spend on a new recorded
route field (built by the `route-lines-field` card), and nothing yet checks that field's lines against the map.

When this card is done, the census (`eval/gameplay_census.py`, published by `scripts/publish_gameplay_census.py` to
`docs/gameplay-census.md` and `.json`) carries four new groups of count-only cells. Each is grouped by era and never
pooled across eras. Each is role-blind in its numerator, published as a report and never a bar, and backed by a
planted breach:

1. **The checked holds-nothing label.** For each SKIP labelled `none_held`, whether the voter's own ballot prompt
   names any living player other than the voter in its observation rows, evidence rows, flags or turn lines. The
   cell is published with its complement and a table by source. The page says a held line is not a reason to vote.
2. **The truth of the cited line.** For every EJECT labelled `supported` whose cited turn holds a whereabouts or
   sighting statement placing the target, whether the engine route makes it true. There are two cells, true and
   false, over the checkable ones. They use the honesty instrument's route (`eval/evidence_honesty.py`) and its two
   clocks, applied to the cited turn: a whereabouts claim is read in I-2's window, and a sighting in the
   instrument's sighting clock.
3. **Route-reconcilable charges, as a standing cell.** Ejections whose target had a stated pair of places the map or
   the public regroup reconciles, and ejections whose charge rested on such a pair, per era. The witness-meeting
   subset sits beside them. The process count is the route-check replay's own functions, never re-implemented: the
   placement reader and `reconcilable` from their production home in `meetings/route_lines.py` (built by
   `route-lines-field`), and the charge functions lifted into a new `eval/route_charges.py`. On round 2 and round 1
   it agrees with the lab's committed JSON meeting by meeting, and a planted mismatch fails.
4. **The route field's conformance cell.** In games recorded with the route field, on that field's own model
   (`RouteLine`, `RouteStep` and `parse_route_lines`): the ballots carrying the block, the lines and the steps by
   reading per meeting, and whether each step's door count, reading and regroup tick are true to the map and the
   game. This reads the field's recorded value and its stamp. It is written after `route-lines-field` merges, and is
   planted with a false link, a wrong door count, a crossing where a walk fits and a step neither allows.

The card also proposes the memo's genre-shape tables (Part 3.4, items 6 to 11) as optional items the orchestrator
may strike. They are endings by reason, kill cadence, closeness at game over, sabotage in play, who found the body,
and co-presence density. Each is role-blind and descriptive.

No cell reads a role in its numerator. Nothing joins the scorecard. Nothing feeds back to an agent, and the census
draws no line through any cell.

## Evidence

Every `path:line` is a citation at `76270d6c`, labelled by its symbol, and is re-anchored by that symbol at
dispatch. Every count is re-measured at dispatch through the production path; nothing here is copied into a test.

**The measures asked for.** The baselines memo
(`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`)
covers them in Part 3.4, items 1 to 3 (`:703-723`): "Items 1, 2 and 3 are the ones a round-3 pre-registration should
name" (`:749`). Items 6 to 11 (`:730-747`) are the genre-shape tables. On 2026-10-06 the owner answered the memo's
Part 4 D2 (`:832-871`) with "What is your recommendation? I slightly lean to spend with narrow field, but would go
with your recommendation". The orchestrator's binding reading takes that as a spend on the narrow route field, the
lab's reading (c).

**The census today.**
- `skips_holding_nothing` reads 214/281 on `samples/9p2i` (`docs/gameplay-census.md:331`). Its definition says the
  label "restates the voter's own statement; it is not a checked fact" (`:550`). The cell lives in the census
  (`eval/gameplay_census.py:1587`), and the fold that counts it is `_fold_ballots` (`:2820`).
- The carrier already reads recorded prompts inside the loader and lets only ids and booleans out:
  `served_own_kill_rows` (`:2997`), `regroup_notices_held` (`:3146`) and `_meeting_fact` (`:3165`).
  `BallotFact` (`:731`) keeps the label and both citation ids. `MeetingFact` (`:763`) keeps the living set at the
  open.
- Every recorded setting field is classified in `FIELD_CLASSIFICATION` (`:488`). A test holds that table equal to
  `RecordedExperimentConfig.model_fields`, both ways (`tests/eval/test_gameplay_census.py:749-756`).
- The page refuses a line or a ratio between two rates (`test_the_census_names_no_line_and_relates_no_two_rates`,
  `tests/scripts/test_publish_gameplay_census.py:717`). The census stays out of the scorecard under ruling R13
  (`tasks/decision-2026-09-24-stage-b-wave.md:57`).

**The ballot prompt** (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2`). It has these blocks:
- `<memory>` (`:187-189`). Inside it, the observations section is headed `## Recent observations (most salient
  first):` and the flags are `## Open contradictions:` (`agents/memory/store.py:3105`, `:3090`).
- `<transcript>` (`:191-232`). Each turn opens with a header line naming its speaker, then its typed lines, then a
  `said:` line.
- `<contradictions>` (`:235-254`) and `<evidence>` (`:289-294`).

The memory's `## Your current beliefs:` block (`store.py:3085`), the suspicion graph and the candidate list name
every living player. A reading that took them in would find every label false. So they are outside the definition.

**The honesty instrument's route check and its two clocks.** I-2 compares a spoken room's canonical set with the
speaker's engine room at ticks N and N-1, through `_contradicts` (`eval/evidence_honesty.py:2293`) in
`_fold_whereabouts` (`:2307`; the window at `:2335-2340`). The engine route is `room_at`, the state after each tick,
with a meeting's row read from its applied state (`:1701-1790`). I-2 reads 4/632 crew and 0/122 impostor false
self-placements on `samples/9p2i` (`tests/eval/test_evidence_honesty.py:1596-1640`). A sighting runs on another
clock: `_assert_clock_alignment` (`:2032`, its docstring `:2040-2060`) places a sighting stamped at agent tick T at
engine tick T-1 when it is read off the state, and at T-1 or T-2 when it carries a perceived action, and it raises
on anything else. A spoken sighting does not say which of the two it was, so its clock is T-1 or T-2.

**The route-check replay** (`experiments/lab/route_check_replay.py`; card `tasks/work/route-check-replay.md`, Reading
`:1452-1476`).
- The process count is a set of small functions: `Placement` (`:442`), `_placement_key` (`:453`),
  `_alibi_stay_placements` (`:457`), `spoken_placements` (`:474`), `placements_of` (`:556`), `reconcilable` (`:562`),
  `ordered_pairs` (`:585`), `Charge` (`:593`), `charges_against` (`:600`), `misjudging_pairs` (`:637`) and
  `is_witness_meeting` (`:1747`). The first seven (with `PlacementKind`) are the route field's placement reader and
  reconcile rule, and `route-lines-field` moves them into `meetings/route_lines.py`, their one home, with a planted
  `ast` test refusing a second definition of `spoken_placements` or `reconcilable`. The other four and
  `is_witness_meeting` are this card's to lift.
- These functions read only the recorded meeting row (transcript, ballots, flags, ejected player), the living roster,
  and the regroup ticks from `derive_regroup_ticks` (`orchestrator/replay.py:1498`).
- The module itself cannot be imported by the census. It imports `eval.gameplay_census` (`:89`), so the import
  would be circular. It also imports the prompt-byte golden's test-module walk (`:140`), which "a production `eval/`
  module should not" (`tasks/work/route-check-replay.md:387-392`). And `experiments/` is outside the import-linter
  roots (`.importlinter:1-16`).
- The committed JSON's r2 column is `replays/samples/9p2i` at `5877adb4`, tree `8197dc79`. That equals
  `git rev-parse 76270d6c:replays/samples/9p2i`. Its r1 tree `2c0529eb` equals the tree of
  `replays/candidates/stage-b-r1/9p2i` at this head.

**Authoring counts.** These come from a scratch, count-only fold at `76270d6c`. It walked each game under
`CENSUS_WALK_CONFIG` for the living roster and the honesty route, and applied the lab's functions and
`_contradicts` to the recorded meeting rows. The witness-meeting row is read from the lab's committed JSON. The
baseline-9 column pools `ml_corpus/9p2i`, `ml_corpus/4p1i` and `samples/4p1i`, as the census pools that era.

| reading | `samples/9p2i` (round 2) | `stage-b-r1/9p2i` (round 1) | baseline-9 era |
|---|---|---|---|
| `none_held` SKIPs; whose inputs name no living candidate | 214; 0 | 256; 0 | 764; 0 |
| of those, naming one in a flag; in an observation row since the previous meeting | 22; 166 | 13; 184 | 203; not read |
| `supported` EJECTs; citing no turn; cited turn places the target nowhere checkable | 407; 29; 97 | 384; 17; 108 | 1,589; 254; 487 |
| checkable; every cited placement true; a cited placement false | 281; 266; 15 | 259; 235; 24 | 848; 793; 55 |
| ejections; target had a reconcilable pair; charge rested on one | 66; 41; 40 | 54; 31; 29 | 321; 200; 198 |
| charges at the table resting on a reconcilable pair | 276/402 | 265/406 | 1,104/1,675 |
| ejections at witness meetings; charge rested on a pair | 12; 7 | 3; 0 | not read |
| meetings differing from the lab's committed JSON (charges, pairs, the misjudged flag) | 0 of 117 | 0 of 124 | no column |

Notes on the table:
- The fold's truth reading of every living speaker's whereabouts claim on `samples/9p2i` gave 754 claims and 4
  false. That is I-2's 632 plus 122, and 4 plus 0, which shows the route and the whereabouts window are the honesty
  instrument's.
- The cited-line rows were measured at authoring with I-2's window (N, N-1) applied to every kind. Of round 2's 15
  false cited placements, 14 are true one tick before that window, which is where the instrument's sighting clock
  (T-1 or T-2) reads a sighting. Those two rows are therefore re-measured at dispatch under each kind's own clock;
  the authoring figures above are not the cell's.
- Every `none_held` SKIP had exactly one recorded ballot call (a call of the voter whose response parses as a
  ballot).

**The genre-shape sources.**
- Each game's end reason is recorded on `GameEndReplayEntry.reason` (`orchestrator/replay.py:673`).
- The carrier holds kills (`KillFact`, `eval/gameplay_census.py:658`), per-tick rooms and sabotage (`Frame`, `:691`),
  bodies, meetings and the terminal tick (`GameFacts`, `:836`).
- The final task count and the end reason are not yet kept.

**The field this card checks.** `route-lines-field` adds the meeting-layer `RecordedExperimentConfig` field
`route_lines_version: Literal[1] | None = None`, default off, omitted at its default, set only from the config file.
It serves the composite `vote_ballot` stamp through the spine registry, ending
`+vote_ballot.qwen3_6_27b.v8.route_lines_v1` (the suffix by the spine rule, "drop `_version` and append
`_v<value>`", `docs/experiment-arms.md:94-104`). Its block sits between `ROUTE_BLOCK_OPEN` (`<routes>`) and
`ROUTE_BLOCK_CLOSE`, parsed by its `parse_route_lines` into `RouteLine` values (a subject and one or more steps) and
`RouteStep` values (two stated places with their ticks, a door count, a reading `walking_fits` or `regroup_between`,
and for a crossing its regroup tick). A candidate has at most one line, and a change of room that neither walks nor
crosses is never rendered. Those names are the field card's contract (its "The census contract" paragraph), and this
card imports them, never copies them.

## Acceptance

Every item names its enforcing mechanism and the planted or perturbed case that must turn its test red.

- [ ] **1. The checked holds-nothing label.**
  - Mechanism: the loader keeps one `bool` per `none_held` SKIP. Its source is the voter's recorded ballot call at
    that meeting: the voter's last call whose response validates as a `VoteBallot`. A `none_held` SKIP with no such
    call raises, naming set, seed, meeting and voter.
  - What is read: the prompt's included blocks only. These are the memory's observations section and its open
    contradictions; the `<evidence>`, `<contradictions>` and `<transcript>` blocks; and, once item 4 lands, the route
    field's block as a source row of its own.
  - What is excluded: turn header lines.
  - What a hit is: a whole-token match of a player living at the open other than the voter.
  - What is published:
    - The cell `holds_nothing_skips_naming_no_candidate`, over `none_held` SKIPs, with its complement.
    - A table counting the SKIPs whose prompt names a candidate in each source class: an observation row; an
      observation row whose id's tick is later than the previous meeting's tick (later than 0 at a game's first
      meeting); an evidence row; a flag; a typed turn line; a spoken line. Rows overlap, and the table says so.
  - No prompt text leaves the loader.
  - Planted, each red on its defect:
    - `p-1` matched inside `p-10`;
    - a beliefs-block, suspicion-graph or candidate-list line counted;
    - a turn header counted;
    - a line naming only the voter or a dead player counted;
    - a prompt missing its memory or transcript block not raising;
    - a SKIP whose only ballot call fails to validate not raising.
  - **Sourced constant.** The included and excluded tags are pinned against every tag the `vote_ballot*.j2`
    templates render. A template copy carrying a new top-level tag fails the pin, and the loader raises on an
    unclassified tag in a recorded prompt. The `<routes>` tag the field adds is classified (an included source row
    of its own) when this branch merges `main` after `route-lines-field`, with item 4; until then the pin reads the
    base's templates.
- [ ] **2. The truth of the cited line.**
  - The denominator: `supported` EJECTs whose `primary_reason_id` names a turn of the same meeting that holds a
    placement of the target. The placement is one of the kinds `saw_player`, `company`, `saw_move` or
    `whereabouts`, as `spoken_placements` gives them. Alibi routes and vent sightings are not read.
  - The check: each such placement is compared through `eval.evidence_honesty._contradicts` with the target's room
    in the honesty instrument's route, at the engine ticks of its kind's own clock, both the instrument's:
    - a `whereabouts` claim spoken for tick N, at engine ticks N and N-1 (I-2's window, `_fold_whereabouts`);
    - a `saw_player`, `company` or `saw_move` placement spoken for agent tick T, at engine ticks T-1 and T-2 (the
      sighting clock `_assert_clock_alignment` enforces: T-1 for a state-read sighting, T-1 or T-2 for an
      action-stamped one, and a spoken sighting does not say which).
    The census rebuilds that route as the instrument does and adds no rule of its own; each kind's window is a
    `Final` mapping read by one helper, so the two clocks have one home here.
  - What is published:
    - Two cells, over the checkable ballots: `cited_lines_true_to_the_route` (every cited placement true) and
      `cited_lines_false_to_the_route` (at least one false).
    - A table `cited_placements_by_kind_and_verdict`. One row per kind counts placements false in their kind's
      window but true one tick before it (the edge row: N-2 for a whereabouts claim, T-3 for a sighting).
    - A table `supported_ejects_not_checkable_by_reason`: the ballot cites only the voter's own observation; the
      cited turn places the target nowhere checkable; every cited placement is unverifiable.
  - **Agreement, whereabouts.** A slow test applies the census's truth reading to every whereabouts claim of a living
    speaker on `samples/9p2i`. It requires the claim and false totals that `compute_evidence_honesty` gives for I-2
    (754 and 4 at authoring), summed over speakers so the census reads no role. Perturbed, a window of N and N+1
    breaks it.
  - **Agreement, sightings.** A slow test applies the census's sighting reading to every recorded `saw_player`
    memory row of every living observer on `samples/9p2i` (its subject, room and tick), the rows
    `_assert_clock_alignment` already holds to the clock, and requires 0 false. Perturbed, sightings read in I-2's
    window (T and T-1) make it name a row.
  - Planted:
    - a whereabouts claim true at N-1 only reads true; one true only at N-2 reads false and lands in the edge row;
    - a sighting true at T-2 only reads true, and one true only at T reads false (each red when the whereabouts
      window is applied to a sighting); one true only at T-3 reads false and lands in the edge row;
    - a non-spatial room is unverifiable, never false;
    - a cited placement of another player is not read;
    - a turn id from another meeting resolves nothing.
- [ ] **3. Route-reconcilable charges.** Built only on `main` after `route-lines-field` merges and this branch merges
  `main`, since its library imports that card's module.
  - The library: `Placement`, `PlacementKind`, the sort key, `_alibi_stay_placements`, `spoken_placements`,
    `placements_of` and `reconcilable` are imported from `meetings/route_lines.py`, under the names that module
    exports, and never defined here. Only `ordered_pairs`, `Charge`, `charges_against` and `misjudging_pairs` move
    from `experiments/lab/route_check_replay.py`, verbatim, into a new `eval/route_charges.py`, which imports the
    placement reader and `reconcilable` from `meetings.route_lines`. `is_witness_meeting` moves into
    `eval/gameplay_census.py`. The lab imports those five back and keeps no copy.
  - The loader keeps one fact per meeting from the recorded row, the living set and `derive_regroup_ticks`: charges
    at the table, charges resting on a reconcilable pair, and for an ejection whether its target had a pair and
    whether its charge rested on one.
  - What is published:
    - `ejections_on_a_reconcilable_pair` and `ejections_charged_on_a_reconcilable_pair`, over ejections;
    - the same two over ejections at witness meetings, `witness_meeting_ejections_on_a_reconcilable_pair` and
      `witness_meeting_ejections_charged_on_a_reconcilable_pair`;
    - `charges_on_a_reconcilable_pair`, over charges.
    `ejections_charged_on_a_reconcilable_pair` is the count the route-check replay calls M (r2 40, r1 29), and its
    witness-meeting form the count it calls W (r2 7, r1 0).
  - **One home.** Planted: the field card's `ast` test stays green with this card's modules in the tree; a copy of
    `reconcilable` defined in `eval/route_charges.py` turns it red.
  - **No drift from the lab.**
    - A test reads the committed JSON's r2 and r1 columns. It requires each recorded tree equal to the tree of its
      path at `HEAD`, and every meeting's facts equal to the census's, naming seed, meeting and field. A failed
      precondition fails by name and is never skipped.
    - Planted: a JSON copy with one meeting's misjudged flag flipped names that meeting; and a loader given no
      regroup ticks breaks the r2 agreement.
    - The lab's own tests pass unchanged. `python -m experiments.lab.route_check_replay --check` reproduces the
      committed JSON and report byte for byte after the move. It needs history, so it runs locally.
- [ ] **4. The route field's conformance cell.** It is written only after `route-lines-field` merges into `main` and
  this branch merges `main`, on that card's model and contract (its "The census contract" paragraph).
  - Mechanism: a new `SettingPredicate` on `route_lines_version = 1` scopes every cell and table here, and replaces
    the field card's not-read `FIELD_CLASSIFICATION` entry.
  - **Stamp.** A game whose config carries the field and whose `vote_ballot` stamp lacks
    `vote_ballot.qwen3_6_27b.v8.route_lines_v1` raises. So does a game whose stamp carries it without the field.
  - The loader parses each recorded ballot prompt's block with the field module's `ROUTE_BLOCK_OPEN`,
    `ROUTE_BLOCK_CLOSE` and `parse_route_lines`, imported and never copied, into its `RouteLine` and `RouteStep`
    values: per line a subject and one or more steps; per step the two stated places with their ticks, the door
    count, the reading (`walking_fits` or `regroup_between`) and, for a crossing, its regroup tick. A block the
    field's parser refuses raises `GameplayCensusConformanceError`, naming set, seed, meeting and voter.
  - The census re-checks every step on its own:
    - doors: a breadth-first search over its own `CensusInputs.neighbours` (the engine map), deliberately not
      through `meetings.transcript.room_hops`; the step's door count must equal it;
    - reading, by the rule computed here: `walking_fits` when the doors are at most the ticks between the two
      places; otherwise `regroup_between`, naming the first regroup tick in (earlier, later]; a pair with neither is
      never rendered, so a step over such a pair is a breach whatever its reading;
    - a named regroup tick must be one of the game's `derive_regroup_ticks` ticks;
    - both places must be stated placements of the subject at that meeting (the field's `spoken_placements`,
      imported);
    - each subject must be a living candidate of that voter, with at most one line per candidate.
  - What is published, per (set, meeting), count-only:
    - presence: the cell `meetings_with_a_route_line` (meetings where some ballot carried a line), over meetings;
    - the cell `ballots_carrying_route_lines`, over ballots;
    - the table `route_lines_per_meeting` (meetings by candidates with a line: 0, 1, 2, 3 or more);
    - the table `route_steps_by_reading` (`walking_fits`, `regroup_between`);
    - the guarded cells `route_lines_false_to_the_map` (steps whose doors, reading or regroup tick disagree with
      the census's own check, over steps rendered) and `route_lines_off_the_table` (lines whose subject is not a
      living candidate of the voter or whose place is not a stated placement, and second lines for one candidate,
      over lines rendered), each 0 by construction. The fold raises `GameplayCensusConformanceError` on a breach,
      naming set, seed, meeting and voter.
  - Planted, each red on its defect. Hand-built steps reach the census's check through `model_construct`, past the
    field's own validators, so the check is tested on its own:
    - a three-door pair read `walking_fits` within two ticks;
    - a pair that neither walks nor crosses (REACTOR at tick 4 to MEDBAY at tick 6, five doors, no regroup), under
      each of the two readings;
    - a wrong door count on a step whose reading is otherwise right;
    - a `regroup_between` step where a walk fits;
    - a regroup tick that never happened, and one outside (earlier, later];
    - a line naming an unstated place; two lines for one candidate; a line for the voter or a dead player;
    - each stamp mismatch;
    - a block the field's parser refuses;
    - a perturbed copy of the field's line pattern (the sourced constant's source-change case);
    - the search against `room_hops` on every room pair of the canonical map, with one door removed from the copy.
  - Every era without the field reads n/a.
- [ ] **4b. (Optional; the orchestrator may strike or move it to the record card.) The field's reach.** Built with
  item 4.
  - The cell `ejections_charged_on_a_reconcilable_pair_shown_a_route_line`, scoped by the field: ejections charged
    on a reconcilable pair at which some EJECT voter's prompt carried a route line about the ejected player, over
    those ejections. Every rendered step reconciles, so the cell counts reconciling steps only. This is the live
    counterpart of the lab's "reaches" for (c), which was 29 of 40 on round 2.
  - Planted: a line shown only to a SKIP voter does not reach; a line about another candidate does not reach.
- [ ] **5. (Optional; the orchestrator may strike any.) The genre-shape tables, role-blind and descriptive.** The
  carrier gains each game's end reason and its final task count, with defaults that leave hand-built carriers
  counting nothing. Each table is planted on a hand-built carrier:
  - **Endings by reason.** Games by recorded end reason. The rows are read with `typing.get_args` from
    `engine.win_conditions.WinResultType` and `orchestrator.replay.GameStopReason`, never copied; an unknown reason
    raises.
  - **Kill cadence.** Kills per game, ticks between consecutive kills, and ticks from a kill to the meeting that
    reported its body. Buckets are `Final` tuples.
  - **Closeness at game over.** Living players, and tasks left as a share of all tasks, by ending. The margin of
    crew over impostors reads role and is not built.
  - **Sabotage in play.** Sabotages started per game (an inactive-to-active change in `Frame`), and task wins in
    games with an active sabotage tick. The page says this measures no delay.
  - **Who found the body.** Report meetings opened by a witness of a kill since the last meeting, against those
    opened by another player, with the ticks from kill to report.
  - **Co-presence density.** Per game, the share of living-player ticks spent in a room with exactly one other
    living player. The role-reading version the memo names is not built.
  - Planted, each red on its defect: a meeting on the kill's own tick dropped; a vent tick counted as a room; a
    sabotage active across a meeting counted twice.
- [ ] **Era grouping.** New cells pool only through the existing `pool()` and `census_from_inputs`. Planted: a tally
  with round 1's era key pooled with the shown era's raises `GameplayCensusEraError` before any new cell is summed,
  and every scoped cell reads n/a, never 0, in an era without its setting. Round 1 is read with `--set-dir` and
  never pooled.
- [ ] **The census stays a census.** The page and JSON tests are extended.
  - No new cell or table has a guard or scope that reads a role.
  - No new definition names a bar, a flag value or a ratio of two rates.
  - The page carries the caveats: a held line is not a reason to vote; a true cited line is not a correct vote; a
    reconcilable pair proves no innocence.
  - Planted: a new definition saying "flagged above" turns the restatement scan red.
  - `docs/process-scorecard.md` and `.json` stay byte-identical.
- [ ] **Properties.** Hypothesis over hand-built carriers and prompts, with `settings(deadline=None)` on every test
  that loads the map. Each property names the perturbed fold that turns it red:
  - adding a line naming a living candidate to an included block always makes a SKIP held, while adding one to an
    excluded block, or naming the voter or a dead player, never does (a parser reading the beliefs block fails it);
  - true plus false equals checkable (a fold dropping mixed ballots fails it);
  - every ballot charged on a pair has a pair, and every witness count is at most its whole (a witness count
    taken over all meetings fails it);
  - the census's link check equals hops at most the ticks between, over random room pairs and gaps (`<` fails it),
    and where no walk fits it names the first regroup tick in (earlier, later] or reads a breach (a last regroup
    tick in place of the first fails it).
- [ ] **One bounded mutation pass.** A single pass over every production line this card adds or changes, using only
  the eight operator classes: F filter, S swap, N comparison, C constant for a role, kind, room or tick read,
  M message, T tuple member, B branch swap, L loaded source to literal. Each mutant runs alone against the touched
  suites. A survivor is killed by a new test, or named equivalent with its reason. Results carries a per-line neuter
  table: each production line, and the test that goes red when it is neutered.
- [ ] **Published and verified.** `publish_gameplay_census.py --check` is green on the regenerated page and JSON,
  and `bash scripts/check.sh` passes at the head that states the numbers.

## Constraints

- **House rules.**
  - The engine stays a pure, deterministic tick function, and replays stay byte-identical within their recorded
    scope.
  - LLMs run only at meetings, and tactical decisions stay rule-based. Agents reason from typed event memory and
    rendered memory.
  - `agents/` never imports `engine/` (import-linter and the firewall scan). The census is an `eval/` reader and may
    import `agents/`, `meetings/` and `engine/`. `eval/route_charges.py` imports only `meetings/`.
  - No module-level mutable state: new tables are `Final` tuples or read-only mappings. Invalid input raises, with
    no silent fallback.
  - Each new invariant gate carries its planted case. Every sourced constant (the template tags, the field's line
    pattern) carries a planted source-change case.
- **No new switch.**
  - No `AILIBI_*` lever, no environment switch, no experiment-config field.
  - No prompt registry bump and no prompt or detector byte change.
  - No recorded byte is edited and no history is re-scored. The round-2 record's lines stay as recorded, and a
    later instrument never changes an earlier verdict.
  - The corpus FROZEN line and the ML artifacts never move. Offline `scripts/verify_ml_evidence.py` passes; never
    `--complete`.
- **Role and the owner's direction.**
  - Role-correctness is reported, never a gate. No new numerator reads a role. The lab's split of route charges by
    ejection class stays the lab's report.
  - The memo's role-reading forms of items 8 and 11 are not built.
  - Nothing pushes an agent toward the correct answer. The meeting layer labels and never rewrites, and the census
    reads labels as recorded.
- **Not a bar.**
  - The re-keyed reporter line and every round-3 bar are the record card's, confirmed by the owner before the first
    seed. This card adds no line, flag value or step rule.
  - The census stays out of the scorecard (ruling R13).
  - The rubric is held for a design pass, and the README and front door are deferred; none is touched.
- **The library is reused, never re-implemented.**
  - Each definition has one home. `route-lines-field` owns `meetings/route_lines.py`, the one home of `Placement`,
    `PlacementKind`, the sort key, `_alibi_stay_placements`, `spoken_placements`, `placements_of` and `reconcilable`
    (and of `RouteStep`, `RouteLine`, the delimiters and `parse_route_lines`); this card imports them and never
    edits that module. This card owns `eval/route_charges.py`, the one home of `ordered_pairs`, `Charge`,
    `charges_against` and `misjudging_pairs`, and `eval/gameplay_census.py`, the home of `is_witness_meeting`.
  - The lifted definitions keep their bodies byte for byte, and the lab keeps no copy.
  - No `eval/` module imports the test-module walk or anything under `experiments/`, and `meetings/` imports
    nothing from `eval/`.
- **Coordination with `route-lines-field` and the round.**
  - This card dispatches in round 3's first wave, beside `route-lines-field` and `crew-idle-policy-lab`, and
    **merges after `route-lines-field`**, merging `main` (never rebased). Items 1, 2 and 5 are built from the
    dispatch base; items 3, 4 and 4b are built only after that merge, on `main`'s `meetings/route_lines.py`.
  - `route-lines-field` writes exactly one not-read `FIELD_CLASSIFICATION` entry for its field (the census suite
    refuses an unclassified field) and regenerates the census pages for that one row; it merges first. This card
    then merges `main`, owns `eval/gameplay_census.py` and replaces that entry with its predicate, and regenerates the
    pages after merging. Both writers regenerate the pages, never hand-edit them.
  - `experiments/lab/route_check_replay.py` and `tests/experiments/test_route_check_replay.py`: `route-lines-field`
    first (its seven definitions become imports, and the `r3` label), then this card after merging `main` (its four
    charge functions and `is_witness_meeting` become imports; the test file's imports only if strict mypy needs
    them). The committed lab JSON and report stay byte-identical, and the file is frozen from the first round-3 seed.
  - This card merges before F, the frozen head the round-3 pre-registration commit builds on (F is `main` after this
    card, `route-lines-field` and `crew-idle-policy-lab` merge), so the record card names cells 1 to 4 as carried
    by a committed instrument. From F to the record's merge, `eval/gameplay_census.py` is frozen.
  - On round-3 candidate bytes, the cells are read with `--set-dir` and never pooled. A promotion that replaces
    `samples/9p2i` retires or re-points the r2 agreement and never loosens it; r1's agreement survives it.
- **Page copy.**
  - The page's own Terms section defines, in plain words: living candidate, holds-nothing check, cited line,
    checkable, stated pair, reconciles, charge, witness meeting, route line.
  - The copy carries no task or audit IDs, unexplained jargon or threshold arithmetic.
- **Data handling.** Counts only, keyed by (set, meeting); no rendered prompt, transcript text or seed-band prefix is
  printed or published, and baseline-9 era cells appear only as era and set aggregates, never per meeting. No live
  provider call is made, and the untracked `.env` is never read.
- **Ownership**, as the orchestrator's one-writer map assigns it.
  - This card alone writes `eval/route_charges.py` (new, on `main` after the field merges),
    `scripts/publish_gameplay_census.py`, `tests/eval/test_route_charges.py`, `tests/eval/test_gameplay_census.py`
    and `tests/scripts/test_publish_gameplay_census.py`, and owns `eval/gameplay_census.py` after the field card's one
    entry, with these limits:
    - `experiments/lab/route_check_replay.py` only at the moved definitions and its imports, after the field card;
    - `docs/artifacts.md` only at the census row, plus the lab row's size if it moves, re-derived after merging
      `main` (the writers are serial, in merge order, each on its own rows: the field card's lab row, this card's
      census row, the idle-policy card's `audits/` row before F, the record card's rows last).
  - `tasks/README.md` (the inventory sentence) and this card's Status line are the orchestrator's, on `main`; the
    worker fills Results only. The doctrine documents (`tasks/decision-2026-09-24-stage-b-wave.md`,
    `tasks/direction-2026-09-19-process-over-outcome.md`) are not edited here.
  - A break this card's new raises cause in another card's file goes to the orchestrator, never into an edit here.
- **Lessons from the Stage-B wave.** Every production line is enforced by a test that goes red when it is neutered;
  guarantees are stated at the strength delivered; numbers are measured at the head that states them; no test is
  weakened. A live-tense sentence about old behaviour is fixed in the same PR: the census's Terms entry for the
  holds-nothing label says "nothing checks it against what the voter held", and the cell's definition says the same.
- **Delivery.** Branch `work/census-held-data-cells`, one PR into `main`, merge commit or fast-forward, never a
  squash. Each commit body ends with `Card: tasks/work/census-held-data-cells.md`, followed immediately by the exact
  line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.
- **Publication.** Nothing ships.
  - The census is not in the demo bundle. `pages.yml` builds from `replays/samples`, the featured list and the
    public-results payload, and importing `scripts/build_demo_bundle.py` loads none of `eval.gameplay_census`,
    `eval.evidence_honesty` or `experiments`.
  - This is the orchestrator's merge.

**Open points for the owner.**
1. At authoring, the literal check reads 0 everywhere: every holds-nothing voter was shown lines naming candidates. The
   label means "nothing resolves", not "nothing held". The card adds a since-the-previous-meeting row and a flag
   row as texture, and the page states the reading.
2. The truth check uses each kind's own two-tick clock from the honesty instrument: I-2's window for a whereabouts
   claim and the sighting clock for a sighting (at authoring, I-2's window on every kind left 15 false placements on
   round 2, 14 of them true one tick earlier, where the sighting clock reads). The edge row, true only one tick
   before its kind's window, is published beside the cells rather than widening either window.
3. The genre-shape tables (item 5) and the reach cell (4b) are optional.

## Expected scope

- `eval/route_charges.py` (new, after `route-lines-field` merges): `ordered_pairs`, `Charge`, `charges_against` and
  `misjudging_pairs`, lifted with their docstrings, importing the placement reader and `reconcilable` from
  `meetings.route_lines`.
- `eval/gameplay_census.py`:
  - the new carrier fields, each defaulting empty;
  - the loader's facts;
  - `is_witness_meeting`;
  - the predicate, the new cells, tables, headings and terms;
  - the `FIELD_CLASSIFICATION` entry `route-lines-field` writes, replaced after this branch merges `main`.
  `SCHEMA_VERSION` stays 2 because the change is additive, and Results confirms that no in-tree reader of the JSON
  breaks.
- `experiments/lab/route_check_replay.py`: the four charge functions and `is_witness_meeting` become imports, after
  `route-lines-field`'s edit, and nothing else.
- `scripts/publish_gameplay_census.py`: rendering of the new headings and tables, where its generic rendering needs
  it.
- `docs/gameplay-census.md` and `docs/gameplay-census.json`: regenerated, never hand-edited.
- `tests/eval/test_route_charges.py` (new): the library's own planted cases.
- `tests/eval/test_gameplay_census.py`: the planted cases, properties, both agreements and the field cases.
- `tests/scripts/test_publish_gameplay_census.py`: the page tests.
- `tests/experiments/test_route_check_replay.py`: imports only, if strict mypy's re-export rule needs them.
- `docs/artifacts.md`: the census row's description, plus the lab row's size only if it moves.
- `tasks/work/census-held-data-cells.md`: Results only.

Not written: `tasks/README.md` and this card's Status line (the orchestrator's, on `main`), `eval/evidence_honesty.py`
(imported only), `eval/process_scorecard.py`, `eval/eras.py`, the route field's modules and templates
(`meetings/route_lines.py` included, imported only), `orchestrator/`, `meetings/`, `agents/`, every replay and
MANIFEST. Follow-through outside this list needs a line in Results naming the file and why.

## Record impact

- **Recorded bytes.** None. Nothing under `replays/` moves, and no MANIFEST, stamp, prompt or detector byte changes.
- **Future behaviour.** None. No agent, meeting or engine path reads the census or `eval/route_charges.py`. The new
  raises stop only the census fold, and on every committed set they read 0 at authoring.
- **Compatibility.**
  - The census JSON gains cells and tables additively, at schema version 2.
  - The scorecard page and JSON are byte-identical.
  - The lab's JSON and report are byte-identical, and its module keeps its public names.
- **Evaluation.**
  - The census gains the three held-data measures per era, and the field's conformance once a recording carries it.
  - A round-3 pre-registration may name them as reported cells.
  - No verdict, envelope line or ruling changes.
- **Adoption.** Not applicable: there is no experimental behaviour.

Measurement: the cells are read on the four committed sets at the implementation head, and the round-1 column with
`--set-dir`. Results quotes the commands below with their output.

## Validation

```
env | grep -c '^AILIBI_'                      # 0
uv run pytest tests/eval/test_route_charges.py tests/eval/test_gameplay_census.py \
  tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py \
  tests/meetings/test_route_lines.py -n 6 --dist loadfile      # the last: the field's one-home ast test stays green
uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile
uv run python -m experiments.lab.route_check_replay --check     # byte-identical lab outputs; needs history
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/verify_ml_evidence.py   # offline; never --complete
uv run lint-imports
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
git diff --stat main -- replays/ docs/process-scorecard.md docs/process-scorecard.json \
  experiments/lab/results-route-check-replay.json experiments/lab/report-route-check-replay.md   # empty
bash scripts/check.sh
```

Results records each command's exit code and counts, the planted cases red before and green after by name, the
neuter table and the mutation pass, and the sections this card rests on: `docs/architecture.md` "Layering",
"Enforced boundaries" and "Determinism and the substrate ladder"; ruling R13; the memo's Part 3.4 and D2; the
route-check Reading. Limitations to state: each round is one hosted recording of 50 games; a held line is not a
reason to vote, and a true cited line is not a correct vote; reaching is showing a line, not changing a vote; each
kind's two-tick clock carries an edge, which the edge row shows.

## Results

Not started.
