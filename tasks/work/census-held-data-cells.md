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

- [x] Review correction (round 6): the charge-fact refusals name their own set, seed and meeting. Each incoherent-fact
  plant is folded a second time under `other/set`, seed 11 and its meeting renamed, and every refusal is matched whole
  (`test_an_incoherent_charge_fact_is_refused_naming_its_meeting`); mutants `R6-M1` to `R6-M9` red, a constant for the
  seed, the set or the meeting at each of the fold's three refusals.
- [x] Review correction (round 6): only an ejecting ballot with no recorded call leaves the reach cell not evaluable. An
  ejecting ballot carrying a line about the ejected player beside a SKIP ballot with no recorded call reads 1 of 1
  (`test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter`); mutant `R6-S1` red.
- [x] Review correction (round 6): the loader reads each meeting's charges over the players living at its open. A spy on
  the field's scripted game holds every call's living set and regroup ticks to the meeting's own, and each meeting's
  living set to the roster less every player killed or ejected before it
  (`test_the_loader_reads_each_meetings_charges_over_the_players_living_at_its_open`); mutant `R6-S7` red.
- [x] Review correction (round 6, the fixer's own pass): the ejected player's charge on a pair reads the meeting's
  regroup ticks, and the loader's refusal of an unserved route block names its own place. The regroup-crossing plant
  also ejects its target (`test_a_charge_resting_only_on_a_regroup_crossing_needs_the_regroup_ticks`), and the refusal
  is matched whole, naming the copy's set directory
  (`test_the_loader_refuses_a_route_block_its_settings_do_not_serve`); mutants `R6-K4` and `R6-M10` red.
- [x] Review correction (round 5): `route_lines_per_meeting` counts the players some ballot carried a line about,
  never the distinct lines. A planted meeting whose two ballots carry different true lines about one player lands in
  row 1 (`test_two_different_lines_about_one_player_are_one_player_with_a_line`); mutant `R5-S1` red.
- [x] Review correction (round 5): a meeting's carrier `regroup_ticks` are the resume ticks of the earlier meetings
  only: none at a game's first meeting, never its own regroup or a later one, pinned on round 2's committed recording
  and on the field's scripted game (`test_a_meetings_regroup_ticks_are_the_earlier_meetings_resume_ticks`); mutants
  `R5-F1` and `R5-F2` red.
- [x] Review correction (round 5): the stamp refusal names its set and seed, and the route-block refusal carries the
  field parser's reason. A seed-3 fake game with the setting and its arm dropped is refused naming its own set and
  seed, every stamp refusal is matched whole (`test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises`),
  and the step-form and door-noun breaks each carry the parser's own reason
  (`test_a_route_block_the_fields_parser_refuses_raises_naming_the_voter[step-form]` and `[door-noun]`); mutants
  `R5-Ma`, `R5-Mb` and `R5-Mf` red.
- [x] Review correction (round 4): the presence cell counts meetings where some ballot carried a line, never
  meetings holding ballots. A meeting whose one ballot carries a recorded call and no line keeps
  `meetings_with_a_route_line` at 1 of 2 (`test_the_route_lines_cells_count_ballots_lines_and_steps`), and the field's
  reach derivation holds the presence and ballot cells to the route-lines replay's own per-meeting counts (116 of 117
  and 665 of 691 on round 2; 123 of 124 and 692 of 717 on round 1;
  `test_the_fields_reach_is_derivable_from_the_census_through_the_field`); mutants `R4-S1` and `R4-N1` red.
- [x] Review correction (round 3): phase 2 is built now that `route-lines-field` has merged. This branch merges
  `main` (both sides of `tests/eval/test_gameplay_census.py` kept) and builds items 3, 4 and 4b as contracted
  (`test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting`,
  `test_the_scripted_route_lines_game_is_read_back_and_counted`,
  `test_the_fields_reach_is_derivable_from_the_census_through_the_field`; both lab `--check` runs reproduce).
- [x] Review correction: the ending rows follow the runner's stop type. `GameStopReason` gaining a member lists it
  as a row of `games_by_ending` and counts a game ending on it (`test_the_ending_rows_follow_the_runners_type`;
  mutant E1 red).
- [x] Review correction: the fold reads a SKIP by the `SKIP_TARGET` it imports. Moved to a player, a checked
  `none_held` ballot on that player is counted by the holds-nothing cells, and the check on a ballot on the old SKIP
  string is refused as an EJECT carrying it (`test_the_fold_reads_a_skip_by_the_skip_target_it_imports`; mutant S1
  red).
- [x] Review correction: the unknown-source refusal follows `HeldSource`. The type gaining a member and losing
  others, a checked `none_held` SKIP naming a candidate in the new member folds into its own row, and one naming a
  candidate in a dropped member is refused, naming it (`test_the_source_rows_follow_their_type`, extended; mutants U1
  and U4 red).
- [x] Review correction: the SKIP half of the holds-nothing guard is enforced. A committed `none_held` SKIP
  retargeted to a living player carries no check, through `holds_nothing_check` and through the loader's
  `_meeting_fact`, and the guard follows the `SKIP_TARGET` it reads
  (`test_an_eject_labelled_as_holding_nothing_is_never_checked`; mutants H1 to H4 red).
- [x] Review correction: the cited placement rows follow their types. `CheckedPlacementKind` gaining a member
  lists that kind's every verdict row and its edge row at zero, and `PlacementVerdict` gaining a member lists a
  row of it for every kind (`test_the_cited_placement_rows_follow_the_kind_type` and
  `test_the_cited_placement_rows_follow_the_verdict_type`; mutants V1 and V2 red).
- [x] **1. The checked holds-nothing label.**
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
  - Phase 2 (2026-10-07): `routes` is a read block and its lines the source row `a route line`; the pin reads
    `main`'s templates (`test_the_classified_blocks_are_every_tag_the_ballot_templates_render`,
    `test_each_place_the_check_reads_names_its_own_row`, the held-place property).
- [x] **2. The truth of the cited line.**
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
- [x] **3. Route-reconcilable charges.** Built only on `main` after `route-lines-field` merges and this branch merges
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
        - A test reads the committed JSON's r2 and r1 columns. It requires each column's recording files
      (`replay-seed-*.jsonl`, `roster.json`, `MANIFEST.md`, the `recording_fingerprint` inputs) at the recorded
      `SHA:PATH` to be blob-identical to those at `HEAD:PATH`, so a derived file beside the recordings, such as
      `results-game-profile.json`, leaves it green; and every meeting's facts equal to the census's, naming seed,
      meeting and field. A failed precondition fails by name and is never skipped. Planted: a changed replay blob
      fails; an added results file does not.
    - Planted: a JSON copy with one meeting's misjudged flag flipped names that meeting; and a loader given no
      regroup ticks breaks the r2 agreement.
    - The lab's own tests pass unchanged. `python -m experiments.lab.route_check_replay --check` reproduces the
      committed JSON and report byte for byte after the move. It needs history, so it runs locally.
  - Phase 2 (2026-10-06): the charge library, the meeting-by-meeting agreement and its planted cases land in the
    review round after `route-lines-field` merges and this branch merges `main`. Landed in phase 1: the drift check's
    blob-comparing precondition (`recording_blob_problems`, planted: an added results file stays green, a changed or
    missing replay fails, with and without the recorded commit in the clone).
  - Landed (2026-10-07, review round 3): the library and the lab's imports back
    (`test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy`); the one home with the field's `ast` test
    (`test_the_field_one_home_test_holds_with_this_library_and_finds_a_copy_in_it`); the agreement on r2 and r1
    (`test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting`), the flipped flag
    (`test_a_column_with_one_misjudged_flag_flipped_names_that_meeting`) and the loader with no regroup ticks
    (`test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement`); both lab `--check` runs reproduce.
- [x] **4. The route field's conformance cell.** It is written only after `route-lines-field` merges into `main` and
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
  - Phase 2 (2026-10-06): lands in the review round after `route-lines-field` merges.
  - Landed (2026-10-07, review round 3): the positive carrier is the field card's scripted game
    (`test_the_scripted_route_lines_game_is_read_back_and_counted`); every planted case above is in
    `tests/eval/test_gameplay_census.py` (the Results name each).
- [x] **4b. (Optional; the orchestrator may strike or move it to the record card.) The field's reach.** Built with
  item 4.
  - The cell `ejections_charged_on_a_reconcilable_pair_shown_a_route_line`, scoped by the field: ejections charged
    on a reconcilable pair at which some EJECT voter's prompt carried a route line about the ejected player, over
    those ejections. Every rendered step reconciles, so the cell counts reconciling steps only. This is the live
    counterpart of the lab's "reaches" for (c), which was 29 of 40 on round 2.
  - Planted: a line shown only to a SKIP voter does not reach; a line about another candidate does not reach.
  - Phase 2 (2026-10-06): built with item 4.
  - Landed (2026-10-07, review round 3): built, under two hours, and derivable from the census carrier through
    `meetings.route_lines`: the census's fold, with each ballot carrying the lines the field's builder gives it,
    reproduces the route-lines replay's 31 of 40 and 7 of 7 on round 2
    (`test_the_fields_reach_is_derivable_from_the_census_through_the_field`); planted
    (`test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter`).
- [x] **5. (Optional; the orchestrator may strike any table, never the fields.) The genre-shape tables, role-blind
  and descriptive.** The carrier gains, outside the strikable tables: each game's end reason and its final task
  count, with defaults that leave hand-built carriers counting nothing; `KillFact.victim` (from `KilledEvent.target`,
  read in `_load_game`) and `BodyFact.victim` (the body's `player_id`), each `PlayerId | None = None` and always filled
  by the loader. The end reason and the final task count are kept even if every table below is struck, because
  `rubric-v2-profile` reads them. Planted for the victims: a same-tick double kill joins each trigger body to its own
  kill by victim, and a loader that swaps the two victims fails. Each table is planted on a hand-built carrier:
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
  - Ruled 2026-10-06: every table is built, none struck; the fields are kept for `rubric-v2-profile`.
- [x] **Era grouping.** New cells pool only through the existing `pool()` and `census_from_inputs`. Planted: a tally
  with round 1's era key pooled with the shown era's raises `GameplayCensusEraError` before any new cell is summed,
  and every scoped cell reads n/a, never 0, in an era without its setting. Round 1 is read with `--set-dir` and
  never pooled.
  - Phase 1's part is met: real round-1 and round-2 tallies refuse to pool before any cell is summed
    (`test_round_1_and_the_promoted_set_never_pool_before_a_new_cell_is_summed`), and no phase-1 cell or table carries
    a scope. The scoped cells are item 4's, so the box closes in phase 2.
  - Phase 2 (2026-10-07): every route line cell and table reads n/a in every committed column, never 0
    (`test_on_baseline_9_every_scoped_cell_and_table_reads_n_a`), and without the setting counts nothing, a
    not-evaluable entry included (`test_every_route_line_cell_and_table_reads_n_a_without_the_setting`).
- [x] **The census stays a census.** The page and JSON tests are extended.
  - No new cell or table has a guard or scope that reads a role.
  - No new definition names a bar, a flag value or a ratio of two rates.
  - The page carries the caveats: a held line is not a reason to vote; a true cited line is not a correct vote; a
    reconcilable pair proves no innocence.
  - Planted: a new definition saying "flagged above" turns the restatement scan red.
  - `docs/process-scorecard.md` and `.json` stay byte-identical.
  - Phase 1's part is met: no new guard or scope, the restatement scan refuses a line, a flag value and a bar
    (planted), two of the three caveats stand on the page, and the scorecard is byte-identical. The third caveat, a
    reconcilable pair proves no innocence, lands with item 3.
  - Phase 2 (2026-10-07): the third caveat stands on the page and in the `reconciles` term; no phase-2 guard or
    scope reads a role (`test_the_phase_two_cells_and_tables_read_no_role`); the scorecard is byte-identical.
- [x] **Properties.** Hypothesis over hand-built carriers and prompts, with `settings(deadline=None)` on every test
  that loads the map. Each property names the perturbed fold that turns it red:
  - adding a line naming a living candidate to an included block always makes a SKIP held, while adding one to an
    excluded block, or naming the voter or a dead player, never does (a parser reading the beliefs block fails it);
  - true plus false equals checkable (a fold dropping mixed ballots fails it);
  - every ballot charged on a pair has a pair, and every witness count is at most its whole (a witness count
    taken over all meetings fails it);
  - the census's link check equals hops at most the ticks between, over random room pairs and gaps (`<` fails it),
    and where no walk fits it names the first regroup tick in (earlier, later] or reads a breach (a last regroup
    tick in place of the first fails it).
  - Phase 1's part is met: the held-place property and true plus false equals checkable, each red on its perturbed
    fold, and a role-permutation property over the promoted set's games. Items 3 and 4's two properties land in phase
    2.
  - Phase 2 (2026-10-07): `test_every_ejection_charged_on_a_pair_has_one_and_the_witness_counts_are_a_part` and
    `test_the_link_check_is_doors_within_the_ticks_or_the_first_regroup_crossed`, each red on its perturbed fold
    (Results).
- [x] **One bounded mutation pass.** A single pass over every production line this card adds or changes, using only
  the eight operator classes: F filter, S swap, N comparison, C constant for a role, kind, room or tick read,
  M message, T tuple member, B branch swap, L loaded source to literal. Each mutant runs alone against the touched
  suites. A survivor is killed by a new test, or named equivalent with its reason. Results carries a per-line neuter
  table: each production line, and the test that goes red when it is neutered.
  - Run over phase 1's lines (Results: 243 neuters and 38 mutants); phase 2 runs it again over its own.
  - Phase 2 (2026-10-07): 180 neuters, 173 red on the first run and the 7 green ones killed by a test added for each; 39 mutants of the eight classes, 33 killed on the first run and the 6 survivors killed by a test added for each (Results, round 3).
- [x] **Published and verified.** `publish_gameplay_census.py --check` is green on the regenerated page and JSON,
  and `bash scripts/check.sh` passes at the head that states the numbers.
  - Phase 1: `--check` is green on the regenerated pages and `bash scripts/check.sh` ran once at the pushed head
    (Results); phase 2 runs both again.
  - Phase 2 (2026-10-07): `--check` is green on the regenerated pages at `39e03863`; `bash scripts/check.sh` exited 0 at
    `ca6ab4c6` (10,697 passed; frontend 695 passed), after a first run at `1b2bc938` failed on the field suite's pin of
    the replaced entry (Results, round 3).

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
    - The rubric is `rubric-v2-profile`'s (decision memo 8.6); this card adds only the carrier fields that card reads
    and no profile cell; the README and front door stay deferred.
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
  - the new carrier fields, each defaulting empty, among them `KillFact.victim` and `BodyFact.victim` (`PlayerId | None
    = None`, always filled by the loader) and each game's end reason and final task count, which stay even if every
    item-5 table is struck;
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

### Phase 1 (2026-10-06): items 1, 2 and 5, and item 3's blob-comparing drift check

Built from the dispatch base `83806ab0` on `work/census-held-data-cells`, before `route-lines-field` merges, in the
order the card's Constraints ("Coordination with `route-lines-field` and the round") and the decision memo's 8.5
set. Items 3 (the charge library), 4 (the route field's conformance cell) and 4b are phase 2: they land in the review
round after `route-lines-field` merges and this branch merges `main`, and their boxes stay unchecked. This phase
creates no `meetings/route_lines.py`, and touches neither `experiments/lab/route_check_replay.py` nor
`eval/route_charges.py`; the `FIELD_CLASSIFICATION` entry for `route_lines_version` is the field card's.

**Sections this rests on.** `docs/architecture.md` "Layering" (the census is an `eval/` reader of `agents/`,
`meetings/`, `engine/` and `orchestrator/`; it now also imports `eval.evidence_honesty._contradicts` and
`meetings.transcript.canonical_rooms`), "Enforced boundaries" (`uv run lint-imports`: 4 contracts kept, 0 broken;
nothing under `agents/` or `meetings/` changes) and "Determinism and the substrate ladder" (no recorded byte, stamp,
prompt or detector byte moves; the walk still verifies every state hash). Ruling R13 (the census is a separate
report: `docs/process-scorecard.md` and `.json` are byte-identical). The baselines memo's Part 3.4 items 1, 2 and 6
to 11, and its D2 as the decision memo 8.1 and 8.2 item 2 read it. The route-check card's Reading
(`tasks/work/route-check-replay.md`), whose placement reader item 2 mirrors.

**What was built** (`eval/gameplay_census.py`, published to `docs/gameplay-census.md` and `.json` by the unchanged
generic renderer of `scripts/publish_gameplay_census.py`):
- Item 1, the holds-nothing check. `BallotFact.held_sources` holds, for every SKIP labelled `none_held`, the places
  in the voter's own recorded ballot prompt that name a living candidate (`held_sources`, `holds_nothing_check`).
  The prompt is the voter's last call whose response validates as a `VoteBallot` (`ballot_call`); none raises,
  naming set, seed, meeting and voter. Read: the memory's observations section and open contradictions, the
  `<transcript>` block's typed and spoken lines, `<contradictions>` and `<evidence>`. Excluded: turn headers, every
  other memory section (beliefs, role, tasks, meetings so far, where you were), every other block and the page
  outside the blocks (suspicion graph, candidate list). A hit is a whole token (`(?<![\w-])p-\d+(?!\w)`) naming a
  player living at the open other than the voter. Cells `holds_nothing_skips_naming_no_candidate` and its
  complement `holds_nothing_skips_naming_a_candidate`; table `holds_nothing_skips_by_source` (rows overlap, and
  the definition says so). The sourced constants: `READ_BALLOT_BLOCKS` and `UNREAD_BALLOT_BLOCKS` are pinned to
  every column-0 tag the `vote_ballot*.j2` templates render, `MEMORY_SECTIONS` to every `## ` heading
  `agents/memory/store.py` renders (an `ast` scan), and the loader raises on an unclassified tag or heading. The
  `<routes>` tag is classified in phase 2.
- Item 2, the truth of the cited line. `TurnFact.placements` (`turn_placements`) holds each turn's spoken
  placements of the four kinds; `GameFacts.settled_rooms` and `resolved_rooms` hold the honesty instrument's route
  (the state after each tick, a meeting's tick read from its applied state; and the state its actions resolved
  in). `placement_verdict` reads each placement through `eval.evidence_honesty._contradicts` at its kind's own
  clock, one `Final` mapping (`PLACEMENT_WINDOWS`) read by one helper (`route_rooms`): a whereabouts claim at N
  and N-1 (I-2's window); a sighting at T-1 settled (state-read), T-1 resolved and T-2 (action-stamped), the window
  `_assert_clock_alignment` holds every recorded sighting to. The edge window is derived, one settled tick before
  the window's earliest (N-2, T-3). Cells `cited_lines_true_to_the_route` and `cited_lines_false_to_the_route`;
  tables `cited_placements_by_kind_and_verdict` (with the edge row) and `supported_ejects_not_checkable_by_reason`.
- Item 5, the carrier fields and the genre-shape tables. `KillFact.victim` (from `KilledEvent.target`),
  `BodyFact.victim` (the body's `player_id`), `GameFacts.end_reason`, `final_tasks_completed` and
  `final_tasks_total`, each defaulting to `None` and always filled by the loader. Tables `games_by_ending` (rows
  from `get_args(WinResultType)` and `get_args(GameStopReason)`; an unknown reason raises), `kills_per_game`,
  `ticks_between_kills`, `ticks_from_kill_to_report` (joined by victim), `living_players_at_game_over_by_ending`,
  `tasks_left_at_game_over_by_ending`, `sabotages_started_per_game`, `report_openers_by_witness`,
  `copresence_share_per_game`, and the cell `task_wins_with_sabotage_in_play`. Buckets are `Final` tuples.
- Item 3's precondition, the lab-drift check in its blob-comparing form (`recording_blob_problems` in
  `tests/eval/test_gameplay_census.py`): the committed route-check JSON's r2 and r1 columns are held to HEAD's
  recording files (every `replay-seed-*.jsonl`, `roster.json`, `MANIFEST.md`, the recording fingerprint's inputs)
  blob for blob. The meeting-by-meeting agreement it guards is phase 2's.

**Decisions.**
1. Orchestrator ruling (1), 2026-10-06: the carrier fields (the two victims, the end reason, the final task count)
   are kept whatever is struck, because `rubric-v2-profile` reads them (decision memo 8.6).
2. Orchestrator ruling (2): item 5's tables are all built; none is struck.
3. Orchestrator ruling (3): the none_held reading is stated on the page, in the cell definition and in the
   `holds-nothing check` term: the label reads as nothing that resolves the vote, not as nothing held, and a line
   held is not a reason to vote.
4. Orchestrator ruling (4): each kind keeps its own clock, and the edge row is published beside the cells rather
   than widening either window.
5. Orchestrator ruling (5): this merge is the orchestrator's, after `route-lines-field` merges (an owner merge) and
   after phase 2 is verified; Status and the `tasks/README.md` inventory sentence are the orchestrator's on `main`
   and are untouched here.
6. Phase 1 reads placements through a census-local `turn_placements`, because the field's `spoken_placements` has
   no production home until `route-lines-field` merges and `eval/` may not import `experiments/`. It is held
   equal, as a multiset per turn, to the route-check replay's `spoken_placements` restricted to the four kinds on
   every committed meeting of both round columns (`test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds`;
   measured on all five sets at authoring: 2,931, 3,007, 8,727, 249 and 248 placements, 0 turns differing). Phase
   2 replaces it with the import from `meetings/route_lines.py` and deletes it, so one definition remains.
7. The sighting clock includes the resolved frame at T-1, as `_assert_clock_alignment` does for an action-stamped
   row; the two frames differ only at a regroup meeting's tick (`test_a_sighting_reads_the_resolved_frame_one_tick_before`).
8. A placement with no canonical room, or with no route room in its window, is unverifiable, never false; a ballot
   whose every cited placement is unverifiable lands in the third not-checkable row.
9. "Since the previous meeting" compares the observation id's tick with the previous meeting's tick (0 at a game's
   first meeting), as the card states.
10. "Who found the body" classes an opener as a witness when it is among the recorded witnesses of any kill after the
    previous meeting's tick and at or before this meeting's, as the card states; the gap reads the reported body's
    kill tick.
11. The living count at game over is derived from kills and ejections, with no new carrier field, and a loader test
    holds it to the walk's final state (`test_the_loader_keeps_each_kill_and_body_victim_and_the_ending`).
12. CI's checkout is depth 1, so the recorded commit `5877adb4` is absent there. The drift check never skips: with the
    commit in the clone it compares blob ids; without it, it must find the recorded tree id as HEAD's listing with
    some non-recording files left out, computed in Python (`flat_tree_id`, held to git's own id by
    `test_the_python_tree_id_is_gits`), which proves every recording file unchanged; otherwise it fails by name. In
    a shallow clone a changed non-recording file (say a rewritten `experiment-config.json`) also fails, which is the
    stricter reading.
13. `SCHEMA_VERSION` stays 2: the JSON gains cells and tables only. In-tree readers of `docs/gameplay-census.json`
    are the publisher, `scripts/verify_ml_evidence.py` (presence probe) and the census's own tests; none breaks.
14. Live-tense follow-through (lesson 3): the `skips_holding_nothing` definition and the `holds-nothing label` term
    no longer say nothing checks the label; `redistribution_policy`'s classification no longer says no cell counts
    tasks; the census module docstring names the new checks; the `docs/artifacts.md` census row names the new
    groups. The process scorecard's own "does NOT measure whether the cited line was factually true" stays true of
    the scorecard and is not edited (R13).
15. The restatement scan (`tests/scripts/test_publish_gameplay_census.py`) also refuses "flagged above/below",
    "bar(s)" and "flag value(s)", planted by `test_a_definition_drawing_a_line_turns_the_restatement_scan_red`.

**Measured at this head, count-only, through the production path** (`uv run python scripts/publish_gameplay_census.py
--check` recomputes the four committed sets; the r1 column is `uv run python scripts/publish_gameplay_census.py
--set-dir replays/candidates/stage-b-r1/9p2i --json-stdout`, exit 0, never pooled).

| reading | `samples/9p2i` (stage-b-r2) | `stage-b-r1/9p2i` (`--set-dir`) | baseline-9, pooled |
|---|---|---|---|
| holds-nothing SKIPs naming no living candidate | 0/214 | 0/256 | 0/764 |
| ... naming one in a flag; in an observation row since the previous meeting | 22; 166 | 13; 184 | 203; 560 |
| supported EJECTs: checkable; citing no turn; nowhere checkable; all unverifiable | 281; 29; 97; 0 | 259; 17; 108; 0 | 842; 254; 487; 6 |
| checkable: the route makes the cited line true; false | 278; 3 | 244; 15 | 818; 24 |
| false placements true one tick before their window (edge rows) | 2 (saw_move) | 20 (12 company, 8 saw_player) | 4 |
| games by ending: crew eject; crew tasks; impostor parity | 13; 13; 24 | 12; 4; 34 | 150; 23; 77 |
| task wins with a sabotage in play | 11/13 | 4/4 | 2/23 |

The authoring counts of item 1 reproduce exactly (214; 0; 22; 166 and 256; 0; 13; 184; baseline-9 764; 0; 203). The
authoring cited-line rows were read in I-2's window on every kind; under each kind's own clock round 2 reads 3 false
of 281, not 15, and the edge row shows the 2 of them a clock one tick earlier would turn true.

**Agreements with the honesty instrument** (slow tests, on `samples/9p2i`). The census's truth reading of every living
speaker's whereabouts claim gives 754 claims and 4 false, `compute_evidence_honesty`'s I-2 totals summed over speakers
(632 + 122 and 4 + 0), so no role is read (`test_the_census_reads_every_whereabouts_claim_as_i2_does`). Every
recorded `saw_player` memory row the instrument rebuilt (24,317 rows) reads 0 false under the census's sighting clock
(`test_the_census_reads_every_recorded_sighting_true_on_its_clock`).

**Planted and perturbed cases, each run as edit, run, restore from a saved copy** (harness: `<scratch>/harness.py`,
targeted suites `tests/eval/test_gameplay_census.py` and `tests/scripts/test_publish_gameplay_census.py`, the fast
subset first and the full suites on a survivor):

| perturbation | kind | result | test that went red |
|---|---|---|---|
| `P1-whereabouts-window-N-and-N+1` | perturbed | killed | `test_a_whereabouts_claim_is_read_at_its_tick_and_the_one_before` |
| `P2-sightings-in-the-whereabouts-window` | perturbed | killed | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `P3-reader-takes-in-the-beliefs` | perturbed | killed | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `P4-fold-drops-mixed-ballots` | perturbed | killed | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `P5-fold-reads-the-voters-role` | perturbed | killed | `test_permuting_the_roles_moves_no_new_count` |
| `P6-loader-swaps-the-victims` | perturbed | killed | `test_the_loader_keeps_each_kill_and_body_victim_and_the_ending` |
| `P7-a-vent-tick-counted-as-a-room` | perturbed | killed | `test_a_player_inside_a_vent_stands_in_no_room_for_copresence` |
| `P8-a-report-on-the-kills-own-tick-dropped` | perturbed | killed | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `P9-a-sabotage-across-a-meeting-counted-twice` | perturbed | killed | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `P10-p-1-matched-inside-p-10` | perturbed | killed | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `P11-a-turn-header-counted` | perturbed | killed | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `P12-the-voter-counted` | perturbed | killed | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `P13-a-dead-player-counted` | perturbed | killed | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `P14-a-missing-block-not-raising` | perturbed | killed | `test_a_prompt_missing_its_memory_or_transcript_block_raises` |
| `P15-an-unvalidated-ballot-call-taken` | perturbed | killed | `test_the_loader_reads_the_voters_last_validating_ballot_call` |
| `P16-a-non-spatial-room-read-false` | perturbed | killed | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `P17-another-players-placement-read` | perturbed | killed | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `P18-a-turn-from-another-meeting-read` | perturbed | killed | `test_a_cited_turn_resolves_only_within_its_own_meeting` |

The two agreements, run alone on their perturbations (`<scratch>/agreement_perturb.py`, edit, run, restore): with the whereabouts window read at N and N+1, `test_the_census_reads_every_whereabouts_claim_as_i2_does` fails `assert (754, 470) == (754, 4)`; with sightings read in the whereabouts window (T and T-1), `test_the_census_reads_every_recorded_sighting_true_on_its_clock` fails naming the rows it reads false. Restored, both pass.

**Neuter table** (lesson 1): every production line, row and argument phase 1 adds or changes, neutered alone.

243 neuters: 234 red on the first run; 8 of the 9 green ones killed by a test added for it (commit `0128fc46`), 1 named equivalent. The red test is the first one the run reported.

| neuter | first run | test that went red |
|---|---|---|
| `held-row-observation` | red | `test_every_value_the_census_holds_is_read_only` |
| `held-row-since` | red | `test_every_value_the_census_holds_is_read_only` |
| `held-row-evidence` | red | `test_every_value_the_census_holds_is_read_only` |
| `held-row-flag` | red | `test_every_value_the_census_holds_is_read_only` |
| `held-row-typed` | red | `test_every_value_the_census_holds_is_read_only` |
| `held-row-spoken` | red | `test_every_value_the_census_holds_is_read_only` |
| `read-block-memory` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `read-block-transcript` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `read-block-contradictions` | red | `test_each_place_the_check_reads_names_its_own_row` |
| `read-block-evidence` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `unread-block-persona` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `unread-block-voice` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `unread-block-testimony` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `unread-block-map` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `unread-block-output` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `memory-row-role` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `memory-row-tasks` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `memory-row-meetings` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `memory-row-trail` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `memory-row-observations` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `memory-row-beliefs` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `memory-row-contradictions` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `block-tag-closing` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `turn-header-pattern` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `player-token-lookbehind` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `player-token-lookahead` | green, killed by a new test | `test_a_player_id_counts_only_as_a_whole_token` |
| `observation-tag-pattern` | red | `test_an_observation_row_counts_as_since_the_previous_meeting_only_after_it` |
| `kind-saw-player` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `kind-company` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `kind-saw-move` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `kind-whereabouts` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `window-whereabouts-0` | red | `test_a_whereabouts_claim_is_read_at_its_tick_and_the_one_before` |
| `window-whereabouts-1` | red | `test_a_whereabouts_claim_is_read_at_its_tick_and_the_one_before` |
| `window-saw-player-settled-1` | red | `test_the_census_reads_every_recorded_sighting_true_on_its_clock` |
| `window-saw-player-resolved-1` | red | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `window-saw-player-settled-2` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `window-company-settled-1` | green, killed by a new test | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `window-company-resolved-1` | green, killed by a new test | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `window-company-settled-2` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `window-saw-move-settled-1` | green, killed by a new test | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `window-saw-move-resolved-1` | green, killed by a new test | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `window-saw-move-settled-2` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `verdict-true` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `verdict-false` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `verdict-unverifiable` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `edge-verdict-text` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `reason-0-text` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `reason-1-text` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `reason-2-text` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `task-win` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `gap-row-same` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `gap-row-1-2` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `gap-row-3-5` | red | `test_tick_gaps_and_shares_land_in_their_buckets` |
| `gap-row-6-10` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `gap-row-11-20` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `long-gap-text` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `never-reported-text` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `share-quarters` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `share-row-none` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `share-row-quarter` | red | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `share-row-half` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `share-row-three-quarters` | red | `test_tick_gaps_and_shares_land_in_their_buckets` |
| `share-row-more` | red | `test_every_value_the_census_holds_is_read_only` |
| `opener-witness-text` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `opener-other-text` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `redistribution-reason` | red | `test_the_committed_census_matches_a_recomputation` |
| `heading-held-listed` | red | `test_the_new_cells_and_tables_carry_no_guard_and_no_scope` |
| `heading-shape-listed` | red | `test_the_new_cells_and_tables_carry_no_guard_and_no_scope` |
| `held-reads-ballots` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `held-reads-prompt` | red | `test_set_dir_prints_the_committed_section_of_that_set` |
| `held-reads-state` | red | `test_set_dir_prints_the_committed_section_of_that_set` |
| `cited-reads-ballots` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `cited-reads-turns` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `cited-reads-tick` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `cited-reads-meeting` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `skips-definition` | red | `test_set_dir_prints_the_committed_section_of_that_set` |
| `cell-no-candidate` | red | `test_every_value_the_census_holds_is_read_only` |
| `cell-a-candidate` | red | `test_every_value_the_census_holds_is_read_only` |
| `cell-true` | red | `test_every_value_the_census_holds_is_read_only` |
| `cell-false` | red | `test_every_value_the_census_holds_is_read_only` |
| `cell-sabotage` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `table-sources` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-placements` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-reasons` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-endings` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-kills` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-gaps` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-kill-report` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-living` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-tasks` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-sabotage` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-finders` | red | `test_every_value_the_census_holds_is_read_only` |
| `table-copresence` | red | `test_every_value_the_census_holds_is_read_only` |
| `term-label-fixed` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-living-candidate` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-check` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-cited-line` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-checkable` | red | `test_the_committed_census_matches_a_recomputation` |
| `all-entry-held-sources` | red | `test_the_module_exports_every_public_name_it_defines` |
| `fold-call-held` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `fold-call-shape` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `rows-held-source` | red | `test_every_value_the_census_holds_is_read_only` |
| `rows-verdicts` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `rows-kinds` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `route-settled-frame` | red | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `route-resolved-frame` | red | `test_a_sighting_reads_the_resolved_frame_one_tick_before` |
| `route-offset` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `route-append` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `edge-plus-one` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `verdict-unverifiable-guard` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `verdict-unverifiable-route` | red | `test_a_placement_with_no_route_or_no_room_is_unverifiable_never_false` |
| `verdict-false-branch` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `edge-blank-guard` | red | `test_a_placement_with_no_route_or_no_room_is_unverifiable_never_false` |
| `edge-contradicts` | red | `test_a_sighting_is_read_at_the_two_ticks_before_its_tick` |
| `zero-rows-sources` | red | `test_the_holds_nothing_cells_count_the_check_with_its_complement` |
| `zero-rows-placements` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `zero-rows-reasons` | red | `test_set_dir_prints_the_committed_section_of_that_set` |
| `dispatch-skip` | red | `test_every_value_the_census_holds_is_read_only` |
| `refuse-eject-check` | red | `test_the_check_on_a_ballot_it_never_reads_is_refused` |
| `dispatch-supported` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `refuse-unlabelled-check` | red | `test_the_check_on_a_ballot_it_never_reads_is_refused` |
| `unchecked-not-evaluable-a` | red | `test_the_holds_nothing_cells_count_the_check_with_its_complement` |
| `unchecked-not-evaluable-b` | red | `test_the_holds_nothing_cells_count_the_check_with_its_complement` |
| `refuse-unknown-source` | red | `test_the_check_on_a_ballot_it_never_reads_is_refused` |
| `count-no-candidate-hit` | red | `test_the_holds_nothing_cells_count_the_check_with_its_complement` |
| `count-a-candidate-hit` | red | `test_the_holds_nothing_cells_count_the_check_with_its_complement` |
| `tally-sources` | red | `test_the_holds_nothing_cells_count_the_check_with_its_complement` |
| `reason-0-tally` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `cited-lookup` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `cited-target-filter` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `reason-1-tally` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `verdict-tally` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `edge-tally` | red | `test_the_edge_row_counts_a_false_placement_true_one_tick_before_its_window` |
| `checkable-filter` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `reason-2-tally` | red | `test_a_cited_line_that_cannot_be_checked_lands_in_its_reason_row` |
| `false-any` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `count-true` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `count-false` | red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `endings-stop` | red | `test_the_ending_rows_are_the_engines_and_the_runners_read_from_their_types` |
| `endings-win` | red | `test_a_kill_or_body_without_a_victim_is_not_joined` |
| `gap-rows-long` | red | `test_tick_gaps_and_shares_land_in_their_buckets` |
| `gap-negative` | red | `test_tick_gaps_and_shares_land_in_their_buckets` |
| `gap-long-return` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `share-guard` | red | `test_tick_gaps_and_shares_land_in_their_buckets` |
| `ending-zero-rows` | red | `test_the_ending_rows_are_the_engines_and_the_runners_read_from_their_types` |
| `ending-refuse` | red | `test_the_ending_rows_follow_the_engines_type` |
| `ending-not-evaluable` | red | `test_the_ending_rows_are_the_engines_and_the_runners_read_from_their_types` |
| `ending-tally` | red | `test_the_ending_rows_are_the_engines_and_the_runners_read_from_their_types` |
| `shape-call-cadence` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `shape-call-closeness` | red | `test_a_kill_or_body_without_a_victim_is_not_joined` |
| `shape-call-sabotage` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `shape-call-finders` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `shape-call-copresence` | red | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `cadence-zero-gaps` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `cadence-zero-report` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `cadence-zero-never` | green, killed by a new test | `test_every_listed_row_stands_at_zero_in_a_game_with_nothing_to_count` |
| `cadence-kills-per-game` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `cadence-sorted` | red | `test_kills_soon_after_the_killer_surfaced` |
| `cadence-gap-tally` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `cadence-report-filter` | red | `test_every_value_the_census_holds_is_read_only` |
| `cadence-unjoinable` | red | `test_a_kill_or_body_without_a_victim_is_not_joined` |
| `cadence-first-report` | green, killed by a new test | `test_a_body_reported_twice_joins_its_kill_to_the_first_report` |
| `cadence-victim-guard` | red | `test_a_kill_or_body_without_a_victim_is_not_joined` |
| `cadence-never-reported` | red | `test_the_kill_cadence_counts_kills_their_gaps_and_each_kill_to_its_report` |
| `closeness-victim-guard` | red | `test_a_kill_or_body_without_a_victim_is_not_joined` |
| `closeness-kills-removed` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `closeness-ejections-removed` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `closeness-living-tally` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `closeness-tasks-guard` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `closeness-tasks-tally` | red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` |
| `sabotage-start` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `sabotage-previous` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `sabotage-sorted` | green | equivalent: read backwards, the frames hold the same number of maximal active runs; the dropped sort (mutant `F5`) is killed by the shuffled-frames case |
| `sabotage-tally` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `sabotage-task-win` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `sabotage-hit` | red | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `finders-zero-rows` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `finders-lower-bound` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `finders-upper-bound` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `finders-opener` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `finders-gap` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `finders-previous` | red | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `copresence-pair` | red | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `copresence-ticks` | red | `test_a_player_inside_a_vent_stands_in_no_room_for_copresence` |
| `copresence-empty` | red | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `copresence-tally` | red | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `turn-fact-placements` | red | `test_the_census_reads_every_whereabouts_claim_as_i2_does` |
| `place-saw-player-room-skip` | red | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `place-saw-player` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-company-not-subject` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-company-dedupe` | red | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `place-company` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-saw-move-to-room` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-saw-move-rooms` | red | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-whereabouts-speaker` | red | `test_the_census_reads_every_whereabouts_claim_as_i2_does` |
| `place-whereabouts-guard` | red | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `call-voter-filter` | red | `test_the_loader_reads_the_voters_last_validating_ballot_call` |
| `call-validate` | red | `test_the_loader_reads_the_voters_last_validating_ballot_call` |
| `call-last` | red | `test_the_loader_reads_the_voters_last_validating_ballot_call` |
| `blocks-known` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `blocks-close` | red | `test_a_block_the_census_does_not_classify_raises` |
| `blocks-append` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `blocks-closing-outside` | red | `test_a_block_the_census_does_not_classify_raises` |
| `blocks-unknown` | red | `test_a_block_the_census_does_not_classify_raises` |
| `blocks-twice` | red | `test_a_block_the_census_does_not_classify_raises` |
| `blocks-never-closes` | red | `test_a_block_the_census_does_not_classify_raises` |
| `blocks-required` | red | `test_a_prompt_missing_its_memory_or_transcript_block_raises` |
| `memory-heading-split` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `memory-heading-unknown` | red | `test_a_memory_heading_the_census_does_not_classify_raises` |
| `memory-started` | red | `test_a_memory_heading_the_census_does_not_classify_raises` |
| `memory-section-skip` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `memory-since-bound` | red | `test_an_observation_row_counts_as_since_the_previous_meeting_only_after_it` |
| `transcript-header` | red | `test_a_quiet_prompt_names_no_living_candidate_anywhere_the_check_reads` |
| `transcript-said` | red | `test_each_place_the_check_reads_names_its_own_row` |
| `transcript-typed` | red | `test_each_place_the_check_reads_names_its_own_row` |
| `transcript-outside` | red | `test_a_transcript_line_outside_any_turn_raises` |
| `transcript-empty-note` | red | `test_a_transcript_line_outside_any_turn_raises` |
| `held-voter-excluded` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `held-memory` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `held-transcript` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `held-flags` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `held-evidence` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `held-token` | red | `test_a_living_candidate_in_a_read_place_always_holds_and_nowhere_else` |
| `check-label-filter` | red | `test_every_value_the_census_holds_is_read_only` |
| `check-no-call` | red | `test_a_holds_nothing_skip_without_a_validating_ballot_call_raises` |
| `check-wrap` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `check-voter` | red | `test_set_dir_prints_the_committed_section_of_that_set` |
| `meeting-where` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `meeting-held-arg` | red | `test_a_holds_nothing_prompt_the_check_cannot_read_raises_naming_the_voter` |
| `meeting-since-arg` | red | `test_the_loader_bounds_since_the_previous_meeting_by_its_tick` |
| `loader-previous-tick` | red | `test_the_loader_bounds_since_the_previous_meeting_by_its_tick` |
| `loader-where` | green, killed by a new test | `test_the_loader_names_the_set_and_seed_of_an_unchecked_holds_nothing_skip` |
| `loader-route-advanced` | red | `test_the_census_reads_every_whereabouts_claim_as_i2_does` |
| `loader-kill-victim` | red | `test_the_loader_keeps_each_kill_and_body_victim_and_the_ending` |
| `loader-body-victim` | red | `test_the_loader_keeps_each_kill_and_body_victim_and_the_ending` |
| `loader-route-applied` | red | `test_the_census_reads_every_recorded_sighting_true_on_its_clock` |
| `loader-final-state` | red | `test_every_value_the_census_holds_is_read_only` |
| `loader-end-reason` | red | `test_the_loader_keeps_each_kill_and_body_victim_and_the_ending` |
| `loader-tasks-completed` | red | `test_the_loader_keeps_each_kill_and_body_victim_and_the_ending` |
| `loader-tasks-total` | red | `test_the_loader_keeps_each_kill_and_body_victim_and_the_ending` |
| `loader-settled` | red | `test_the_census_reads_every_whereabouts_claim_as_i2_does` |
| `loader-resolved` | red | `test_the_loader_keeps_the_honesty_route_settled_and_resolved` |
| `rooms-of` | red | `test_the_loader_keeps_the_honesty_route_settled_and_resolved` |

**The bounded mutation pass** (lesson 10): 38 mutants of exactly the eight classes over `eval/gameplay_census.py`,
the one production module phase 1 touches (`scripts/publish_gameplay_census.py` is unchanged).

38 mutants (F 5, S 4, N 6, C 5, M 4, T 4, B 4, L 6): 34 killed on the first run, 2 killed by a test added for them, 2 named equivalent. The pass then stopped.

| mutant | class | result | test that went red |
|---|---|---|---|
| `F1-companions-filter` | F | killed | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `F2-finder-kill-window` | F | killed | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `F3-closeness-ejected-filter` | F | survived, equivalent | `None` joins the removed set and names no player, so the living count is the same |
| `F4-ballot-call-voter` | F | killed | `test_the_loader_names_the_set_and_seed_of_an_unchecked_holds_nothing_skip` |
| `F5-sabotage-sorted` | F | killed | `test_a_sabotage_active_across_a_meeting_is_one_start` |
| `S1-flags-evidence-swap` | S | killed | `test_each_place_the_check_reads_names_its_own_row` |
| `S2-finder-witnesses-living` | S | killed | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `S3-copresence-keys` | S | killed | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `S4-ballot-call-reversed` | S | killed | `test_the_loader_reads_the_voters_last_validating_ballot_call` |
| `N1-route-room-none` | N | killed | `test_a_compound_or_transit_label_is_read_by_its_canonical_rooms` |
| `N2-primary-reason-none` | N | killed | `test_a_cited_turn_resolves_only_within_its_own_meeting` |
| `N3-ending-none` | N | killed | `test_a_cited_turn_resolves_only_within_its_own_meeting` |
| `N4-kill-victim-none` | N | killed | `test_a_same_tick_double_kill_joins_each_body_to_its_own_kill_by_victim` |
| `N5-ballot-call-none` | N | killed | `test_every_value_the_census_holds_is_read_only` |
| `N6-eject-check-none` | N | killed | `test_a_cited_turn_resolves_only_within_its_own_meeting` |
| `C1-verdict-tick` | C | killed | `test_a_compound_or_transit_label_is_read_by_its_canonical_rooms` |
| `C2-verdict-kind` | C | killed | `test_a_whereabouts_claim_is_read_at_its_tick_and_the_one_before` |
| `C3-finder-kill-tick` | C | killed | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `C4-copresence-room` | C | killed | `test_copresence_counts_player_ticks_with_exactly_one_other` |
| `C5-since-tick` | C | killed | `test_an_observation_row_counts_as_since_the_previous_meeting_only_after_it` |
| `M1-no-call-message` | M | killed | `test_a_holds_nothing_skip_without_a_validating_ballot_call_raises` |
| `M2-unknown-block-message` | M | killed | `test_a_block_the_census_does_not_classify_raises` |
| `M3-unknown-ending-message` | M | killed | `test_the_ending_rows_follow_the_engines_type` |
| `M4-eject-check-message` | M | killed | `test_the_check_on_a_ballot_it_never_reads_is_refused` |
| `T1-required-transcript` | T | killed | `test_a_prompt_missing_its_memory_or_transcript_block_raises` |
| `T2-claims-subheading` | T | killed | `test_every_value_the_census_holds_is_read_only` |
| `T3-opener-rows` | T | killed | `test_every_listed_row_stands_at_zero_in_a_game_with_nothing_to_count` |
| `T4-edge-zero-row` | T | killed | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` |
| `B1-verdict-branches` | B | killed | `test_a_compound_or_transit_label_is_read_by_its_canonical_rooms` |
| `B2-said-typed-branches` | B | killed | `test_each_place_the_check_reads_names_its_own_row` |
| `B3-never-reported-branches` | B | killed | `test_a_same_tick_double_kill_joins_each_body_to_its_own_kill_by_victim` |
| `B4-opener-branches` | B | killed | `test_who_found_the_body_reads_the_witnesses_since_the_last_meeting` |
| `L1-endings-literal` | L | killed | `test_the_ending_rows_follow_the_engines_type` |
| `L2-held-rows-literal` | L | killed | `test_the_source_rows_follow_their_type` |
| `L3-canonical-rooms-literal` | L | killed | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `L4-contradicts-literal` | L | survived, equivalent | every route room is a map room, whose canonical set is itself (`CANONICAL_ROOMS` is pinned to the map), so the instrument's comparison and a plain intersection agree on every route the engine writes |
| `L5-holds-nothing-literal` | L | survived, then killed | `test_the_loader_checks_the_label_its_constant_names` |
| `L6-task-win-literal` | L | survived, then killed | `test_the_sabotage_cell_reads_the_task_win_its_constant_names` |

**Verification at this head.**

Measured at `0128fc46`, except where a row names `b53d4fb1`. `b53d4fb1` changes only the placement reader's dispatch (below); `publish_gameplay_census.py --check` is green on it, so every count above reproduces there, and the demo bundle loads no census module, so its empty diff stands.

| command | exit | result |
|---|---|---|
| `env \| grep -c '^AILIBI_'` | - | 0 |
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py -n 6 --dist loadfile` | 0 | 600 passed (`tests/eval/test_route_charges.py` and `tests/meetings/test_route_lines.py` are phase 2's and do not exist yet) |
| `uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile` | 0 | 114 passed |
| `uv run python -m experiments.lab.route_check_replay --check` (full clone) | 0 | reproduced, 41.9 s |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0 | the r1 column above |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent; the scorecard page and JSON are byte-identical |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | 63 checks, 51 OK, 0 FAIL, 7 evidence-branch absent, 5 info |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks and prompts; 101 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 | every checked figure true |
| `git diff --stat main -- replays/ docs/process-scorecard.md docs/process-scorecard.json experiments/lab/results-route-check-replay.json experiments/lab/report-route-check-replay.md` | - | empty |
| `bash scripts/verify_samples.sh replays/<set>`, for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| demo bundle, built in this one checkout at `83806ab0` and at `0128fc46` (`uv run python scripts/build_demo_bundle.py --out DIR` each, then `diff -r`) | 0 | 109 files each, empty diff: nothing ships |
| `bash scripts/check.sh` at `ecb8cf7a` | 1 | 1 failed, 10,354 passed: `tests/eval/test_sighting_vocabulary.py::test_the_narrow_sighting_remainder_is_exactly_the_allow_list` named `eval/gameplay_census.py::turn_placements` (fixed below) |
| `uv run python scripts/publish_gameplay_census.py --check` at `b53d4fb1` | 0 | consistent |
| `bash scripts/check.sh` at `eb419e69`, the pushed head (exit code captured directly) | 0 | pytest 10,355 passed, 20 skipped, 3 xfailed; frontend 695 passed; the build succeeds; later commits touch only this row |

**The first gate run, and its fix.** The repository's sighting-vocabulary walk (`tests/eval/test_sighting_vocabulary.py`) reads every `isinstance` check over `SawPlayerObservation` that omits `SawMoveObservation` as a narrow first-hand predicate, and it read `turn_placements`' separate `isinstance` branches that way, although the next branch reads the movement sighting. `b53d4fb1` dispatches the three kinds with one `match` statement, which the walk does not read as narrow and which reads every placement as before; the walk's allow-list is untouched. The reader's ten neuters and two mutants (`F1`, `L3`) were re-run on the new dispatch, with one more neuter for the movement case itself, and all twelve went red:

| probe | test that went red |
|---|---|
| `place-saw-player-room-skip` | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `place-saw-player` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-company-not-subject` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-company-dedupe` | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `place-company` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-saw-move-to-room` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-saw-move-rooms` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-whereabouts-speaker` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `place-whereabouts-guard` | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `place-saw-move-case (never matches)` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `F1-companions-filter` | `test_the_census_placement_reader_is_the_route_check_replays_on_these_kinds` |
| `L3-canonical-rooms-literal` | `test_turn_placements_read_the_four_kinds_and_nothing_else` |

**Limitations.**
- Each round is one hosted recording of 50 games; the counts describe those games and are no bar.
- A held line is not a reason to vote, and a true cited line is not a correct vote; reaching is showing a line, not
  changing a vote (phase 2's 4b).
- Each kind's two-tick clock carries an edge, which the edge row shows instead of widening a window.
- The holds-nothing check finds a living candidate in every committed holds-nothing SKIP's prompt: it says the label
  reads as "nothing resolves", and it does not judge whether a held line resolves the vote.
- The placement reader is census-local until phase 2 swaps in the field's.
- In a shallow clone the drift check also fails on a changed non-recording file beside the recordings.

### Review corrections, round 1 (2026-10-06)

Two blocking findings of the round-1 verifiers on phase 1 (head `99e07d55`), both surviving mutants of the listed
classes. Each is repaired with a planted case in `tests/eval/test_gameplay_census.py`; no production line moves, so
every count, the committed census, the scorecard and the demo bundle are unchanged.

1. **The SKIP half of the holds-nothing guard was unenforced** (correctness lens). `holds_nothing_check` returns
   `None` unless the ballot is a SKIP labelled `none_held`. The ballot schema admits a `none_held` EJECT and no
   committed set holds one, so replacing `ballot.target != SKIP_TARGET` with `ballot.target is None`, or dropping
   that disjunct, left both suites green (457 passed). Planted:
   `test_an_eject_labelled_as_holding_nothing_is_never_checked` takes the first committed `none_held` SKIP of
   `samples/4p1i` (the `_ballot_meeting` helper), retargets it to the first player, in sorted id order, living at the open other
   than the voter, and requires `None` from `holds_nothing_check` and `held_sources is None` on the loader's ballot
   fact from `_meeting_fact`, while the untouched SKIP still carries the check. The guard's `SKIP_TARGET` is a constant
   read from `meetings.voting` (lesson 9), so the same test then moves `census.SKIP_TARGET` to that player and
   requires the check to follow: the SKIP is no longer checked and the retargeted ballot is.
2. **The cited placement rows read from their types had no source-change case** (integrity lens).
   `checked_placement_kinds()` and `placement_verdicts()` read `get_args` of `CheckedPlacementKind` and
   `PlacementVerdict`; swapping either for its canonical literal tuple left both suites green, because the only test
   of the rows compared the table against the same two functions. Planted, shaped like
   `test_the_source_rows_follow_their_type`: `test_the_cited_placement_rows_follow_the_kind_type` gives
   `CheckedPlacementKind` a fifth member and requires every verdict row of it and its edge row, at zero, in
   `cited_placements_by_kind_and_verdict` over a game with nothing to count;
   `test_the_cited_placement_rows_follow_the_verdict_type` gives `PlacementVerdict` a fourth member and requires a
   zero row of it for every kind.

**The bounded mutation pass over the spans this round touches and the findings name** (lesson 10; harness
`<scratch>/census-fix-r1/mutate.py`: edit `eval/gameplay_census.py`, run `tests/eval/test_gameplay_census.py` and
`tests/scripts/test_publish_gameplay_census.py` with `-n 6`, restore from a saved copy; unmutated, 460 passed). 12
mutants of the listed classes: 12 killed, 0 equivalent. H1, V1 and V2 are the verifiers' survivors at `99e07d55`; H1,
H2, H4, V1 and V2 are killed only by this round's tests, so each came back green before it. The pass then stopped.

| mutant | class | result | test that went red |
|---|---|---|---|
| `H1` guard `ballot.target != SKIP_TARGET` to `ballot.target is None` | None test | killed (was green) | `test_an_eject_labelled_as_holding_nothing_is_never_checked` |
| `H2` guard drops the SKIP disjunct | drop a filter | killed (was green) | `test_an_eject_labelled_as_holding_nothing_is_never_checked` |
| `H3` guard `!= SKIP_TARGET` to `== SKIP_TARGET` | inverse comparison | killed, 11 red | `test_the_loader_reads_the_voters_last_validating_ballot_call` among them |
| `H4` guard `SKIP_TARGET` to the literal `'SKIP'` | canonical literal | killed (was green) | `test_an_eject_labelled_as_holding_nothing_is_never_checked` |
| `H5` guard label `!= HOLDS_NOTHING_LABEL` to `is None` | None test | killed, 16 red | `test_the_loader_checks_the_label_its_constant_names` among them |
| `H6` guard drops the label disjunct | drop a filter | killed, 16 red | `test_the_committed_census_matches_a_recomputation` among them |
| `V1` `get_args(CheckedPlacementKind)` to the four-kind literal | canonical literal | killed (was green) | `test_the_cited_placement_rows_follow_the_kind_type` |
| `V2` `get_args(PlacementVerdict)` to the three-verdict literal | canonical literal | killed (was green) | `test_the_cited_placement_rows_follow_the_verdict_type` |
| `V3` the zero rows drop `EDGE_VERDICT` | drop a tuple member | killed, 6 red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` among them |
| `V4` the zero rows drop the last verdict | drop a tuple member | killed, 7 red | `test_the_cited_placement_rows_follow_the_verdict_type` among them |
| `V5` the zero rows drop the last kind | drop a tuple member | killed, 7 red | `test_the_cited_placement_rows_follow_the_kind_type` among them |
| `V6` the zero row's kind to the constant `saw_player` | message constant | killed, 7 red | `test_the_cited_line_cells_count_true_false_and_mixed_ballots` among them |

**Verification at the fix head.** Measured on the fix commit; this round changes only
`tests/eval/test_gameplay_census.py` and this card, so no recorded, published or hashed byte moves and no
`docs/artifacts.md` row is recomputed.

| command | exit | result |
|---|---|---|
| `env \| grep -c '^AILIBI_'` | - | 0 |
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py -n 6 --dist loadfile` | 0 | 603 passed (600 before, plus this round's three) |
| `uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile` | 0 | 114 passed |
| `uv run python -m experiments.lab.route_check_replay --check` (full clone) | 0 | reproduced, 54.8 s |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0 | the r1 column, unchanged |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | 63 checks, 51 OK, 0 FAIL, 7 evidence-branch absent, 5 info |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks and prompts; 101 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 | every checked figure true |
| `uv run mypy tests/eval/test_gameplay_census.py`; `uv run ruff check` and `ruff format --check` on it | 0 | clean |
| `git diff --stat origin/main -- replays/ docs/process-scorecard.md docs/process-scorecard.json experiments/lab/results-route-check-replay.json experiments/lab/report-route-check-replay.md` | - | empty |
| `bash scripts/verify_samples.sh replays/<set>`, for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| demo bundle, built in this one checkout at `83806ab0` and at `62a91057` (`uv run python scripts/build_demo_bundle.py --out DIR` each, then `diff -r`) | 0 | 109 files each, empty diff: nothing ships |
| `bash scripts/check.sh` at `62a91057`, the fix head (run once, output to a file, exit code from the run itself) | 0 | pytest 10,358 passed, 20 skipped, 3 xfailed (10,355 before, plus this round's three); frontend 695 passed; the build succeeds; the commit after it touches only this row |

### Review corrections, round 2 (2026-10-06)

Three blocking findings of the round-2 verifiers on phase 1 (head `0fbf65e1`). Each is a surviving mutant of a listed
class at a constant the census reads from a source, with no case where the source changes and the output follows it
(lesson 9). Each is repaired with a planted case in `tests/eval/test_gameplay_census.py`, shaped like
`test_the_source_rows_follow_their_type`: the type or constant is monkeypatched on the census module, and the output
must follow it. No production line moves, so every count, the committed census, the scorecard and the demo bundle are
unchanged, and every ruling in Phase 1's Decisions stands: the carrier fields kept whatever is struck, every item-5
table built, the `none_held` reading stated as nothing that resolves the vote, each kind on its own clock.

1. **The runner's half of the ending rows had no source-change case** (correctness lens). `game_endings()` reads
   `get_args` of `WinResultType` and of `GameStopReason`. `test_the_ending_rows_follow_the_engines_type` moves only
   the first, so the literal `'TICK_BUDGET_REACHED', 'MEETING_PHASE_REACHED'` in place of the second left every suite
   green. Planted: `test_the_ending_rows_follow_the_runners_type` gives `GameStopReason` a third member,
   `OPERATOR_ABORT`, and requires `games_by_ending` to list every engine ending and every runner stop at zero, with
   `OPERATOR_ABORT` at 1 for a game ending on it. Under the literal, that game is refused as an ending neither the
   engine nor the runner records.
2. **The fold's SKIP read had no source-change case** (integrity lens). `_fold_held_data` sends a ballot to the
   holds-nothing count when `ballot.target == SKIP_TARGET`, a constant read from `meetings.voting`. Round 1 moved
   `census.SKIP_TARGET` only over `holds_nothing_check`, the loader's guard, so the literal `'SKIP'` in the fold
   survived. Planted: `test_the_fold_reads_a_skip_by_the_skip_target_it_imports` moves `census.SKIP_TARGET` to
   `p-3`. A checked `none_held` ballot on `p-3` naming a candidate in a flag is counted (naming a candidate 1 of 1,
   naming none 0 of 1, the flag row 1). The same check on a ballot on the string `SKIP`, now an EJECT, is refused
   with the fold's own message. Each ballot is unconfident, so the meeting's recorded skip re-tallies as a skip under
   the game's own `tally_ballots`, which keeps its own constant.
3. **The unknown-source refusal had no type-change case** (integrity lens). `_fold_holds_nothing` refuses a source
   outside `held_source_rows()`. The type-change plant folded an empty game, so the literal six-member set at the
   refusal site survived. Extended: `test_the_source_rows_follow_their_type`, with `HeldSource` patched to two
   members, now folds a checked `none_held` SKIP naming a candidate in the new member, `a rumour`, and requires it in
   its own row and counted. It then requires a SKIP naming a candidate in a dropped member, `a flag`, to be refused
   naming `['a flag']`. That second half also kills U4 below: a survivor of the message-constant class that this
   round's pass found in the same refusal, because the only refusal case named `a rumour`, so the message's
   `{unknown}` replaced by `['a rumour']` stayed green.

**The bounded mutation pass over the spans the findings name** (lesson 10; harness `<scratch>/census-fix-r2/mutate.py`:
edit `eval/gameplay_census.py`, run `tests/eval/test_gameplay_census.py` and
`tests/scripts/test_publish_gameplay_census.py` with `-n 6`, restore from a saved copy; unmutated, 462 passed, the 460
of round 1 plus this round's two new tests). The three named survivors E1, S1 and U1 were first run against the tests
at `0fbf65e1`: each 460 passed, so each was green before this round. 13 mutants of the listed classes: 13 killed, 0
equivalent. E1, S1, U1 and U4 are killed only by this round's tests. The pass then stopped.

| mutant | class | result | test that went red |
|---|---|---|---|
| `E1` `*get_args(GameStopReason)` to the literal `'TICK_BUDGET_REACHED', 'MEETING_PHASE_REACHED'` | canonical literal | killed (was green) | `test_the_ending_rows_follow_the_runners_type` |
| `E2` `*get_args(WinResultType)` to the four-ending literal | canonical literal | killed, 1 red | `test_the_ending_rows_follow_the_engines_type` |
| `E3` the endings drop the `GameStopReason` member | drop a tuple member | killed, 6 red | `test_the_committed_census_matches_a_recomputation` among them |
| `E4` the endings drop the `WinResultType` member | drop a tuple member | killed, 20 red | `test_closeness_reads_the_living_and_the_tasks_left_at_game_over` among them |
| `S1` fold `ballot.target == SKIP_TARGET` to `== 'SKIP'` | canonical literal | killed (was green) | `test_the_fold_reads_a_skip_by_the_skip_target_it_imports` |
| `S2` fold `== SKIP_TARGET` to `!= SKIP_TARGET` | inverse comparison | killed, 22 red | `test_a_cited_placement_of_another_player_is_not_read` among them |
| `S3` fold `ballot.target == SKIP_TARGET` to `ballot.target is None` | None test | killed, 16 red | `test_set_dir_prints_the_committed_section_of_that_set` among them |
| `S4` fold `held_sources is not None` to `is None` | inverse None test | killed, 68 red | `test_a_cited_turn_resolves_only_within_its_own_meeting` among them |
| `S5` the fold's SKIP branch and its EJECT refusal swapped | swap adjacent branches | killed, 16 red | `test_set_dir_prints_the_committed_section_of_that_set` among them |
| `U1` the refusal's `set(held_source_rows())` to the six-source literal | canonical literal | killed (was green) | `test_the_source_rows_follow_their_type` |
| `U2` the refusal drops its `sorted` wrapper | drop a wrapper | killed, 2 red | `test_the_check_on_a_ballot_it_never_reads_is_refused` and `test_the_source_rows_follow_their_type` |
| `U3` the refusal reads `checked_placement_kinds()` for `held_source_rows()` | swap a related collection | killed, 15 red | `test_set_dir_prints_the_committed_section_of_that_set` among them |
| `U4` the refusal's message `{unknown}` to the constant `['a rumour']` | message constant | killed (was green on this pass's first run) | `test_the_source_rows_follow_their_type` |

**Noticed, outside this card.** `test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing` fails
when it is the first census walk in its process (`uv run pytest` on that test alone: 1 failed, 4 passed, the same at
`0fbf65e1`, and the test is on `main`). It installs its walk spy before the cached committed game first loads, so the
spy records that load. The parallel runs of this round and the gates of earlier rounds passed it. It is flagged
for a separate task and not changed here.

**Verification at the fix head.** Measured on the fix commit; this round changes only
`tests/eval/test_gameplay_census.py` and this card, so no recorded, published or hashed byte moves and no
`docs/artifacts.md` row is recomputed.

| command | exit | result |
|---|---|---|
| `env \| grep -c '^AILIBI_'` | - | 0 |
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py -n 6 --dist loadfile` | 0 | 605 passed (603 before, plus this round's two new tests) |
| `uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile` | 0 | 114 passed |
| `uv run python -m experiments.lab.route_check_replay --check` (full clone) | 0 | reproduced, 43.1 s |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0 | the r1 column; `eval/` unchanged since round 1 |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | 63 checks, 51 OK, 0 FAIL, 7 evidence-branch absent, 5 info |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks and prompts; 101 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 | every checked figure true |
| `uv run mypy tests/eval/test_gameplay_census.py`; `uv run ruff check` and `ruff format --check` on it | 0 | clean |
| `git diff --stat origin/main -- replays/ docs/process-scorecard.md docs/process-scorecard.json experiments/lab/results-route-check-replay.json experiments/lab/report-route-check-replay.md` | - | empty |
| `bash scripts/verify_samples.sh replays/<set>`, for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| demo bundle | - | not rebuilt this round: installing the frontend's packages was refused in this environment. Since `62a91057`, built in one checkout beside `83806ab0` (109 files each, empty diff), only this card and `tests/eval/test_gameplay_census.py` moved (`git diff --stat 62a91057`), neither an input of the bundle, so nothing ships |
| `AILIBI_SKIP_FRONTEND=1 bash scripts/check.sh` at `b5270be4`, the fix head (run once, output to a file, exit code from the run itself; the frontend leg opted out as CI's Python job runs it, because installing the frontend's packages was refused in this environment, and the PR's frontend-checks job runs that leg) | 0 | pytest 10,360 passed, 20 skipped, 3 xfailed (10,358 before, plus this round's two new tests); frontend skipped; the commit after it touches only this row |

### Review corrections, round 3 (2026-10-07)

One blocking finding of the round-3 dispatch, on `4549f38f` (correctness lens): phase 2 of this card is contracted to
land after `route-lines-field` merges, and it has merged (PR #501 at `47bee59a`; PR #503, the census spy's cold-cache
fix, at `e0bf4d92`; `main` at `2228eb4a`). This round is phase 2, built by the card's own order (Constraints,
"Coordination with `route-lines-field` and the round"; decision memo 8.5). Phase 1 was verified at `4549f38f` over three
review rounds and is not re-verified here beyond the merge. Every ruling in Phase 1's Decisions and in rounds 1 and 2
stands.

**The merge of `main`** (`331540a3`, a merge commit, never a rebase). Git merged every file without a conflict. In
`tests/eval/test_gameplay_census.py` both sides are kept: `main`'s `_spied_walk` warms the committed game before the
spy goes in, and its two callers install the spy before any other patch; this branch's phase-1 tests stand beside
them. `main`'s not-read `FIELD_CLASSIFICATION` entry for `route_lines_version` was kept by the merge and replaced by
this round's predicate (item 4), and both census pages were regenerated through the production path, never hand-edited.

**Sections this rests on.** `docs/architecture.md` "Layering" (the census is an `eval/` reader; `eval/route_charges.py`
imports only `meetings/` and the standard library, and the census now also imports `eval.route_charges`,
`meetings.route_lines` and the arm spine's `orchestrator.game.experiment_arm_suffix` and `EXPERIMENT_ARM_TEMPLATES`),
"Enforced boundaries" (`uv run lint-imports`: 4 kept, 0 broken; nothing under `agents/`, `meetings/` or `engine/`
changes) and "Determinism and the substrate ladder" (no recorded, stamp, prompt or detector byte moves; the walk still
verifies every state hash). `tasks/work/route-lines-field.md`, its "The census contract" paragraph and Results (the
`RouteLine` and `RouteStep` model, the two readings, at most one line per candidate, the stamp, the block reader). The
route-check card's Reading (`tasks/work/route-check-replay.md`). Decision memo section 8 (the rubric ruled a role-blind
game-shape profile, 8.5's order and one-writer map). Ruling R13 (the census joins no scorecard).

**What was built.**
- **Item 3, the route-reconcilable charges.** `ordered_pairs`, `Charge`, `charges_against` and `misjudging_pairs` move
  from `experiments/lab/route_check_replay.py` into the new `eval/route_charges.py`, body for body (each definition's
  source text equals the lab's at `2228eb4a`, checked by `ast.get_source_segment`), importing `Placement`, the sort key,
  `placements_of` and `reconcilable` from `meetings/route_lines.py`. `is_witness_meeting` moves, body for body, into
  `eval/gameplay_census.py`. The lab imports all five back (re-exported with `as`, so its public names and its tests stay
  as they were) and keeps no copy; its only other change is the two imports the move left unused (`KillFact`,
  `_placement_key`). The loader keeps one `RouteChargeFact` per meeting from the recorded row, the living set at the open
  and `derive_regroup_ticks` over the earlier meetings' ticks (`route_charge_fact`): the charges at the table, those
  resting on a reconcilable pair, and at an ejection the ejected player's reconcilable pairs and whether a charge against
  them rested on one. The census-local `turn_placements` reader is deleted: `turn_placements` now groups the field's
  `spoken_placements` by turn, for the four checked kinds, in a fixed order, so no placement or reconcile definition
  exists outside `meetings/route_lines.py`. Cells `charges_on_a_reconcilable_pair` (over charges),
  `ejections_on_a_reconcilable_pair` and `ejections_charged_on_a_reconcilable_pair` (over ejections, the second the
  replay's M), and their witness-meeting forms (over ejections at witness meetings, the second the replay's W), under a
  new heading, "Stated places the map or the regroup reconciles". The page carries the third caveat: a reconcilable pair
  proves no innocence.
- **Item 4, the route field's conformance cell.** `route_lines_version` is read by the new `route_lines` predicate
  (`route_lines_version = 1`), which scopes every route line cell and table and guards the two conformance cells; its
  `FIELD_CLASSIFICATION` entry is that predicate. The loader refuses a game whose recorded settings serve route lines
  while its ballot stamp lacks the arm, and one whose stamp credits the arm without the setting
  (`route_lines_stamped`: a `+`-part of the ballot template's stamp ending in the suffix the arm spine derives). It reads
  each ballot's served block with the field's own `parse_route_lines` (`ballot_route_lines`, on the voter's last call
  that validates as a ballot), and refuses a block the parser refuses and a block in a game that does not serve route
  lines, naming set, seed, meeting and voter. The fold re-checks every served step on its own (`step_true_to_the_map`):
  the doors by a breadth-first search over the set's own `CensusInputs.neighbours` (`census_doors`, never the meeting
  layer's `room_hops`), the reading by the rule (`census_reading`: walking fits when the doors are at most the ticks
  between, otherwise the first regroup tick in (earlier, later], and neither is a breach whatever the step reads), the
  regroup tick against the meeting's `derive_regroup_ticks`; and every line against the voter's living candidates, the
  places the meeting stated for its subject (`stated_places`, the field's reader on its route kinds) and one line per
  candidate (`line_on_the_table`). Cells `meetings_with_a_route_line`, `ballots_carrying_route_lines`, and the guarded
  `route_lines_false_to_the_map` (over steps served) and `route_lines_off_the_table` (over lines served); tables
  `route_lines_per_meeting` (0, 1, 2, 3 or more) and `route_steps_by_reading` (rows read from the field's
  `RouteReading`). The `<routes>` block is a held-data source of its own, `a route line` (item 1's open note).
- **Item 4b, the field's reach.** The cell `ejections_charged_on_a_reconcilable_pair_shown_a_route_line`, scoped by the
  field: ejections charged on a reconcilable pair at which some voter who voted to eject that player was served a line
  about them. It is derivable from the census carrier through `meetings.route_lines` without re-implementing the
  instrument: with each recorded ballot carrying the lines the field's own `build_route_lines` gives it (the meeting's
  transcript, the voter's living candidates, the meeting's regroup ticks), the census's own fold of that carrier gives
  the route-lines replay's published reach, 31 of 40 and 7 of 7 at witness meetings on round 2, and 22 of 29 and 0 of 0
  on round 1, and its steps by reading (1,343 walking fits and 25 regroup crossings on round 2; 1,499 and 37 on round
  1), with every one of those lines and steps passing the census's own map and table check
  (`test_the_fields_reach_is_derivable_from_the_census_through_the_field`). It cost well under the two hours the
  dispatch allowed, so the box is checked.

**Decisions.**
1. Every route line cell and table is scoped by `route_lines_version = 1`, as item 4 and the Era grouping item contract
   ("every era without the field reads n/a"; "every scoped cell reads n/a, never 0"). On every committed set the field
   is off, so they read n/a in every column; the page states it in each definition ("Counted only in games recorded with
   `route_lines_version = 1`; in any other era it reads n/a") and in its legend. In a set recorded with the field the
   two conformance cells read `0/N by construction` (the scripted game: 0/15 and 0/15). The dispatch note's "presence
   reads 0" is read as that in-scope reading; the card's n/a governs the committed sets.
2. The meeting's charge count composes the lifted functions as the replay's `read_meeting` does (every living player a
   ballot or a flag names), in the census loader's `route_charge_fact`; the replay's `read_meeting` is unchanged, and the
   meeting-by-meeting agreement holds the two together.
3. A route block is read on every ballot of every game, and one in a game whose settings do not serve route lines
   raises, beside the card's two stamp refusals: on the committed sets no ballot carries one.
4. `route_steps_by_reading` and `route_lines_per_meeting` count each meeting's distinct lines, as the route-lines
   replay does (its 1,343 and 25 reproduce); the conformance cells count every line and step served on every ballot.
5. `_Accumulator.not_evaluable` now counts nothing in a cell out of its scope, as `count` already did: a ballot with
   no recorded ballot call in an era without the route lines would otherwise publish a not-evaluable entry in an n/a
   cell, which the published model refuses. No committed count moves.
6. Each turn's placements are kept in a fixed order (tick, rooms, player, kind), since the field's reader orders
   equal-keyed placements by set iteration.
7. Test follow-through, each named: the carrier shape check now also walks the field's frozen pydantic models
   (`RouteLine.subject` and `RouteStep`'s rooms are ids, and `MeetingFact.stated_places` holds ids and rooms); a stamped
   copy recording the route lines credits their arm in its stamps (`_stamps_for`), and the later-settings walk asserts
   those credited stamps; the planted unclassified block is `<rumours>`, since `<routes>` is now read; the heading order,
   the scoped cell and table maps, the predicate listing and the n/a test name the new entries; the two route guards
   share their scope, so they have no publishing twin and carry their own planted breaches (`ROUTE_GUARD_BREACHES`).
8. `SCHEMA_VERSION` stays 2: the JSON gains cells, tables, terms and a row only. Its in-tree readers (the publisher,
   `scripts/verify_ml_evidence.py`, the census's tests) read it unchanged.
9. Follow-through outside the card's file list: one test in the field card's merged file,
   `tests/meetings/test_route_lines_arm.py`. Its `test_the_census_classifies_it_as_not_read` pinned the not-read
   `FIELD_CLASSIFICATION` entry that this card is contracted to replace with its predicate (item 4; both cards'
   coordination paragraphs), so the first full gate failed on it; it now reads
   `test_the_census_reads_it_by_its_route_lines_predicate` and pins the predicate. The field card has merged and
   writes that file no more; no assertion is dropped, only the pinned classification follows the contract.
   `docs/artifacts.md`'s census row names the new groups; the `experiments/lab/` row's size does not move (170
   files, 7.0 MB).

**Measured at this head, count-only, through the production path** (`uv run python scripts/publish_gameplay_census.py
--check` recomputes the four committed sets; the r1 column is `--set-dir replays/candidates/stage-b-r1/9p2i
--json-stdout`, never pooled).

| reading | `samples/9p2i` (stage-b-r2) | `stage-b-r1/9p2i` (`--set-dir`) | baseline-9, pooled |
|---|---|---|---|
| charges resting on a reconcilable pair | 276/402 | 265/406 | 1,104/1,675 |
| ejections whose target had a reconcilable pair | 41/66 | 31/54 | 200/321 |
| ejections charged on a reconcilable pair (M) | 40/66 | 29/54 | 198/321 |
| at witness meetings: the target had a pair; charged on one (W) | 7/12; 7/12 | 0/3; 0/3 | 8/13; 8/13 |
| every route line cell and table | n/a | n/a | n/a |

The authoring counts reproduce exactly (66; 41; 40, 276/402, 12; 7 on round 2; 54; 31; 29, 265/406, 3; 0 on round 1;
321; 200; 198, 1,104/1,675 on baseline 9). Every phase-1 count is unchanged: the cited-line check now reads the field's
reader and still gives 278 true and 3 false of 281 on round 2 and 244 and 15 of 259 on round 1.

**The route-check replay, meeting by meeting.** On both round columns every meeting's charges, charges on a
reconcilable pair and witness-meeting flag, and at an ejection the target's pairs and the misjudged flag, equal the
committed JSON's: 117 meetings on round 2 and 124 on round 1, 0 differing
(`test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` and `[r1]`, after the blob-comparing
precondition of phase 1). Planted: a JSON copy with one meeting's misjudged flag flipped names that meeting and field
(`test_a_column_with_one_misjudged_flag_flipped_names_that_meeting`); the charge facts recomputed with no regroup tick
break the r2 agreement, and with the loader's regroup ticks reproduce its facts
(`test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement`).

**The positive carrier.** The route field's scripted game (`tests/_helpers/scripted_routes.py`), recorded with the
setting and folded through the production loader: 2 of 2 meetings with a route line; 12 of 13 ballots carrying lines
(the ejected opener's own ballot carries none); 0 of 15 steps false to the map and 0 of 15 lines off the table, each by
construction; one meeting with one player's line and one with two; 2 walking fits and 1 regroup crossing; the one
ejection, charged on a reconcilable pair, reached by a line (1 of 1). Recorded without the setting, every ballot
carries no line and every route line cell reads n/a.

**Planted cases**, each red on its defect (all in `tests/eval/test_gameplay_census.py` unless named):
- Charges: the cells over a witness's report, a button ejection with a pair and no charge on it, and a meeting
  ejecting no one (`test_the_route_charge_cells_count_charges_ejections_and_witness_meetings`); a missing fact is not
  evaluable (`test_a_meeting_without_its_charge_fact_is_not_evaluable`); four incoherent facts are refused, naming the
  set, seed and meeting (`test_an_incoherent_charge_fact_is_refused_naming_its_meeting`); a witness meeting's window and
  opener (`test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one`).
- The library (`tests/eval/test_route_charges.py`): one home for the charge half, a copy left in the lab found
  (`test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy`); the field's `ast` test green with this library in the
  tree and a copy of `reconcilable` in `eval/route_charges.py` found
  (`test_the_field_one_home_test_holds_with_this_library_and_finds_a_copy_in_it`); the library imports only `meetings/`
  and the standard library, a planted `experiments` import found; a charge by ballot and by flag, a pair misjudged only
  when the map or the regroup reconciles it, and every pair in placement order.
- Route lines: a three-door pair read as a walk within two ticks; a pair that neither walks nor crosses (REACTOR at 4 to
  MEDBAY at 6, five doors, no regroup) under each reading; a wrong door count with the reading otherwise right; a
  crossing where a walk fits; a regroup tick that never happened and one outside (earlier, later]; the last regroup tick
  in place of the first; a walk naming a regroup tick; a step that is no change of room; a room off the map
  (`test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map`); the card's example steps read true; a line at an
  unstated place, a second line for one candidate, the voter's own line and a dead player's line, each raising with the
  setting on and naming set, seed, meeting and voter, and counting nothing (n/a) without it
  (`test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter`, five cases); the off-the-table predicate
  (`test_a_line_is_on_the_table_only_for_a_living_candidate_at_stated_places`); each stamp mismatch
  (`test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises`); the arm's suffix and template moved, the check
  follows (`test_the_stamp_check_follows_the_arm_spines_derivation`), and a composite stamp is split wherever the arm
  stands (`test_the_stamp_check_splits_a_composite_stamp_wherever_the_arm_stands`); a block the field's parser refuses
  (`test_a_route_block_the_fields_parser_refuses_raises_naming_the_voter`); a block in a game that does not serve route
  lines (`test_a_route_block_in_a_game_that_does_not_serve_route_lines_raises`); a perturbed copy of the field's line
  pattern refuses the served block (`test_the_census_reads_a_route_line_by_the_fields_own_pattern`); the census's search
  equals `room_hops` on every room pair of the canonical map, and one door removed from the copy breaks it
  (`test_the_census_door_search_is_the_maps_hop_count_on_every_room_pair`); a walk across a door cut from the set's own
  inputs is a breach (`test_the_fold_checks_a_step_against_the_doors_its_inputs_carry`); a vent sighting states no route
  place and an alibi stay states its two ends (`test_stated_places_are_the_route_kinds_only`); the rows follow
  `RouteReading` and the cap (`test_the_route_rows_follow_their_types`); every route line cell and table reads n/a
  without the setting, a not-evaluable entry included
  (`test_every_route_line_cell_and_table_reads_n_a_without_the_setting`).
- The reach: a line shown only to a SKIP voter does not reach; a line about another candidate does not reach; a line
  about the ejected player on an EJECT ballot does; an ejection not charged on a pair is outside the cell; an ejecting
  ballot with no recorded call is not evaluable (`test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter`).
- The page (`tests/scripts/test_publish_gameplay_census.py`): the caveats now include a reconcilable pair proving no
  innocence and showing a line not changing a vote; the restatement scan reads every new definition.

**Properties** (Hypothesis, `settings(deadline=None)` on each):
- `test_every_ejection_charged_on_a_pair_has_one_and_the_witness_counts_are_a_part`: over generated meetings, every
  ejection charged on a pair has one, and each witness-meeting count is exactly the ejections at witness meetings and
  never more than its whole.
- `test_the_link_check_is_doors_within_the_ticks_or_the_first_regroup_crossed`: over random room pairs, gaps and regroup
  ticks, walking fits exactly when the doors are at most the ticks between, otherwise the first regroup tick in
  (earlier, later] is crossed, and with neither every reading is a breach.
- The held-place property gains the route block as a read place; the scope property now also requires a not-evaluable
  entry to count only in scope; `test_permuting_the_roles_moves_no_route_count` holds every charge cell under any
  permutation of the promoted set's roles.

**The properties' perturbations**, each run against its property alone (harness `<scratch>/census-fix-r3/perturb.py`:
edit `eval/gameplay_census.py`, run, restore from a saved copy):

| perturbation | result | test that went red |
|---|---|---|
| `P1` witness counts taken over every meeting | killed | `test_every_ejection_charged_on_a_pair_has_one_and_the_witness_counts_are_a_part` |
| `P2` the last regroup tick crossed in place of the first | killed (green on the first draw, which rarely held two regroup ticks inside a pair's ticks; the property now draws them around the pair and carries an explicit two-tick example) | `test_the_link_check_is_doors_within_the_ticks_or_the_first_regroup_crossed` |
| `P3` `<` for `<=` in the walk rule | killed | `test_the_link_check_is_doors_within_the_ticks_or_the_first_regroup_crossed` |

**Neuter table** (lesson 1): every production line, row and argument phase 2 adds or changes in
`eval/gameplay_census.py`, `eval/route_charges.py` and the lab's imports, neutered alone (harness
`<scratch>/census-fix-r3/harness.py` with the probe list `probes.py`: edit, run `tests/eval/test_gameplay_census.py`,
`tests/scripts/test_publish_gameplay_census.py` and `tests/eval/test_route_charges.py`, with
`tests/experiments/test_route_check_replay.py` for the library and the lab, `-n 8 -x`, Hypothesis reporting a failing
example without shrinking it, restore from a saved copy). A cell, table or term neuter drops the whole entry; an
`__all__` neuter drops the one name. The red test is the first one the run reported. The seven green neuters were each
re-run, red, against the test added for it in `39e03863`; two door-search neuters made the first run never end (the
search loops), and the bounded door test added in `39e03863` now fails each instead.

180 neuters: 173 red on the first run; 7 of the 7 green ones killed by a test added for it, 0 named equivalent.

| neuter | first run | test that went red |
|---|---|---|
| `read-block-routes` | red | `test_the_classified_blocks_are_every_tag_the_ballot_templates_render` |
| `held-row-route` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `held-read-routes` | red | `test_each_place_the_check_reads_names_its_own_row` |
| `route-field-name` | red | `test_the_classification_and_the_predicates_name_each_other` |
| `count-cap` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `predicate-value` | red | `test_on_baseline_9_every_scoped_cell_and_table_reads_n_a` |
| `predicates-listed` | red | `test_the_classification_and_the_predicates_name_each_other` |
| `field-classified` | red | `test_the_classification_and_the_predicates_name_each_other` |
| `heading-listed` | red | `test_every_cell_and_table_is_published_and_ordered_under_a_heading` |
| `charge-reads-turns` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `charge-reads-ballots` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `charge-reads-flags` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `charge-reads-state` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `charge-reads-earlier` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `line-reads-prompt` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `line-reads-turns` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `line-reads-state` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `line-reads-earlier` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `cell-charges_on_a_reconcilable_pair` | red | `test_the_rows_found_are_the_denominator_so_a_mismatch_reads_n_a` |
| `cell-ejections_on_a_reconcilable_pair` | red | `test_resting_on_the_room_left_needs_a_living_crew_sighting` |
| `cell-ejections_charged_on_a_reconcilable_pair` | red | `test_resting_on_the_room_left_needs_a_living_crew_sighting` |
| `cell-witness_meeting_ejections_on_a_reconcilable_pair` | red | `test_the_phase_two_cells_and_tables_read_no_role` |
| `cell-witness_meeting_ejections_charged_on_a_reconcilable_pair` | red | `test_the_phase_two_cells_and_tables_read_no_role` |
| `cell-meetings_with_a_route_line` | red | `test_corpse_age_reads_the_kill_event_tick_never_the_body_id` |
| `cell-ballots_carrying_route_lines` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `cell-route_lines_false_to_the_map` | red | `test_every_guarded_cell_has_a_planted_pair` |
| `cell-route_lines_off_the_table` | red | `test_every_guarded_cell_has_a_planted_pair` |
| `cell-ejections_charged_on_a_reconcilable_pair_shown_a_route_line` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `table-route_lines_per_meeting` | red | `test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off[own_kill_rows_breaching-_own_kill_row_citing_nothing]` |
| `table-route_steps_by_reading` | red | `test_the_rows_found_are_the_denominator_so_a_mismatch_reads_n_a` |
| `scope-meetings` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `scope-ballots` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `scope-reach` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `guard-false-map` | red | `test_every_guarded_cell_has_a_planted_pair` |
| `scope-false-map` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `guard-off-table` | red | `test_every_guarded_cell_has_a_planted_pair` |
| `scope-off-table` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `scope-per-meeting` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `scope-by-reading` | red | `test_the_scoped_cells_and_tables_are_exactly_these` |
| `term-stated pair` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-reconciles` | red | `test_the_page_states_what_a_held_or_a_true_line_is_not` |
| `term-charge` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-witness meeting` | red | `test_the_committed_census_matches_a_recomputation` |
| `term-route line` | red | `test_the_page_states_what_a_held_or_a_true_line_is_not` |
| `term-check-route` | red | `test_the_committed_census_matches_a_recomputation` |
| `meaning-route-lines` | red | `test_every_setting_a_guard_or_scope_reads_has_its_meaning_on_the_page` |
| `definition-held-route` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `definition-sources-route` | red | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `fold-call-routes` | red | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting[fact2-p-0-an` |
| `not-evaluable-scope` | red | `test_resting_on_the_room_left_needs_a_living_crew_sighting` |
| `witness-report` | red | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `witness-floor` | red | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `witness-opener` | red | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `witness-upper` | red | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `witness-lower` | red | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `readings-type` | red | `test_the_route_rows_follow_their_types` |
| `count-rows-more` | red | `test_the_route_rows_follow_their_types` |
| `count-row-min` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `doors-off-map` | green, killed by a new test | `test_the_door_search_reads_no_door_count_for_a_room_off_the_map` |
| `doors-frontier` | red | `test_the_card_example_steps_are_true_to_the_map` |
| `doors-seen` | green, killed by a new test | `test_the_door_search_reads_each_room_once_and_ends_where_no_door_leads` |
| `doors-hit` | red | `test_the_card_example_steps_are_true_to_the_map` |
| `doors-count` | red | `test_the_card_example_steps_are_true_to_the_map` |
| `doors-unseen` | red | the run did not finish in 300 s (the search never ends); since `39e03863` `test_the_door_search_reads_each_room_once_and_ends_where_no_door_leads` fails it |
| `doors-seen-add` | green, killed by a new test | `test_the_door_search_reads_each_room_once_and_ends_where_no_door_leads` |
| `doors-reached` | red | `test_the_card_example_steps_are_true_to_the_map` |
| `doors-advance` | red | the run did not finish in 300 s (the search never ends); since `39e03863` `test_the_door_search_reads_each_room_once_and_ends_where_no_door_leads` fails it |
| `reading-walk` | red | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted4-regroups4]` |
| `reading-window` | red | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted6-regroups6]` |
| `reading-crossing` | red | `test_the_card_example_steps_are_true_to_the_map` |
| `step-door-guard` | red | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted3-regroups3]` |
| `step-door-zero` | red | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted9-regroups9]` |
| `step-door-count` | red | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted3-regroups3]` |
| `step-reading` | red | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted4-regroups4]` |
| `step-regroups` | red | `test_the_card_example_steps_are_true_to_the_map` |
| `line-candidate` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_the_voters_own_line]` |
| `line-place` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_unstated_place]` |
| `line-from-place` | green, killed by a new test | `test_a_line_is_off_the_table_at_an_unstated_first_place` |
| `line-to-place` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_unstated_place]` |
| `routes-zero-counts` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `routes-zero-readings` | red | `test_the_route_rows_follow_their_types` |
| `routes-previous` | red | `test_every_ejection_charged_on_a_pair_has_one_and_the_witness_counts_are_a_part` |
| `routes-call-charges` | red | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting[fact2-p-0-an` |
| `routes-call-lines` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `charges-none-charges` | red | `test_a_meeting_without_its_charge_fact_is_not_evaluable` |
| `charges-none-on-pair` | red | `test_a_meeting_without_its_charge_fact_is_not_evaluable` |
| `charges-none-charged` | red | `test_a_meeting_without_its_charge_fact_is_not_evaluable` |
| `charges-none-witness` | red | `test_a_meeting_without_its_charge_fact_is_not_evaluable` |
| `charges-coherent-count` | red | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting[fact0-None-more` |
| `charges-count-loop` | red | `test_the_route_charge_cells_count_charges_ejections_and_witness_meetings` |
| `charges-count-hit` | red | `test_the_route_charge_cells_count_charges_ejections_and_witness_meetings` |
| `charges-coherent-none` | red | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting[fact1-None-a` |
| `charges-coherent-pairs` | red | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting[fact2-p-0-an` |
| `charges-count-on-pair` | red | `test_every_ejection_charged_on_a_pair_has_one_and_the_witness_counts_are_a_part` |
| `charges-count-charged` | red | `test_every_ejection_charged_on_a_pair_has_one_and_the_witness_counts_are_a_part` |
| `charges-count-witness` | red | `test_the_route_charge_cells_count_charges_ejections_and_witness_meetings` |
| `reach-charged-only` | red | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `reach-ejecting` | red | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `reach-unreadable` | red | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `reach-subject` | red | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `lines-none` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `lines-ballots` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `lines-candidates` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_the_voters_own_line]` |
| `lines-second` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_second_line]` |
| `lines-subjects-add` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_second_line]` |
| `lines-off-table` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_a_dead_players_line]` |
| `lines-false-map` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_false_to_the_map-_off_map]` |
| `lines-neighbours` | red | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_second_line]` |
| `lines-regroups` | red | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `lines-distinct` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `lines-meetings` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `lines-per-meeting` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `lines-steps` | red | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `placements-kinds` | red | `test_every_value_the_census_holds_is_read_only` |
| `placements-sorted` | red | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `placements-order-player` | red | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `placements-player` | red | `test_turn_facts_keep_ids_ticks_and_alibi_legs` |
| `placements-tick` | red | `test_turn_facts_keep_ids_ticks_and_alibi_legs` |
| `stated-kinds` | red | `test_stated_places_are_the_route_kinds_only` |
| `stated-tick` | red | `test_the_scripted_route_lines_game_is_read_back_and_counted` |
| `charge-fact-ballots` | red | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` |
| `charge-fact-flags` | red | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` |
| `charge-fact-charges` | red | `test_every_value_the_census_holds_is_read_only` |
| `charge-fact-resting` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `charge-fact-regroups` | green, killed by a new test | `test_a_charge_resting_only_on_a_regroup_crossing_needs_the_regroup_ticks` |
| `charge-fact-no-ejection` | red | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` |
| `charge-fact-pairs` | red | `test_every_value_the_census_holds_is_read_only` |
| `charge-fact-charged` | red | `test_the_scripted_route_lines_game_is_read_back_and_counted` |
| `charge-fact-union` | red | `test_the_scripted_route_lines_game_is_read_back_and_counted` |
| `stamp-template` | red | `test_the_stamp_check_follows_the_arm_spines_derivation` |
| `stamp-suffix` | red | `test_the_loader_reads_the_game_ending_trigger_tick_of_samples_4p1i_seed_3` |
| `stamp-split` | red | `test_the_stamp_check_splits_a_composite_stamp_wherever_the_arm_stands` |
| `block-no-call` | red | `test_the_opening_handle_is_read_from_the_openers_own_first_prompt` |
| `block-parse-wrap` | red | `test_the_census_reads_a_route_line_by_the_fields_own_pattern` |
| `block-not-served` | red | `test_a_route_block_in_a_game_that_does_not_serve_route_lines_raises` |
| `block-return` | red | `test_the_census_reads_a_route_line_by_the_fields_own_pattern` |
| `meeting-placements` | red | `test_round_1_and_the_promoted_set_never_pool_before_a_new_cell_is_summed` |
| `meeting-route-lines` | red | `test_the_scripted_route_lines_game_is_read_back_and_counted` |
| `meeting-served` | green, killed by a new test | `test_the_loader_refuses_a_route_block_its_settings_do_not_serve` |
| `meeting-charges` | red | `test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement` |
| `meeting-charge-regroups` | red | `test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement` |
| `meeting-regroup-field` | red | `test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement` |
| `meeting-stated` | red | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `game-served` | red | `test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing[route_lines_version-1]` |
| `game-stamp-check` | red | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises` |
| `game-config` | red | `test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement` |
| `game-earlier` | red | `test_a_loader_given_no_regroup_ticks_breaks_the_round_2_agreement` |
| `game-served-arg` | red | `test_the_scripted_route_lines_game_is_read_back_and_counted` |
| `export-ROUTE_LINES` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-ROUTE_LINES_FIELD` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-ROUTE_LINE_COUNT_CAP` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-RouteChargeFact` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-ballot_route_lines` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-census_doors` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-census_reading` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-is_witness_meeting` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-line_on_the_table` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-route_charge_fact` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-route_line_count_row` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-route_line_count_rows` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-route_lines_stamped` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-route_readings` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-stated_places` | red | `test_the_module_exports_every_public_name_it_defines` |
| `export-step_true_to_the_map` | red | `test_the_module_exports_every_public_name_it_defines` |
| `lab-witness` | red | `test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy` |
| `lab-charge` | red | `test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy` |
| `lab-charges-against` | red | `test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy` |
| `lab-misjudging` | red | `test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy` |
| `lab-ordered` | red | `test_the_charge_half_has_one_home_and_the_lab_keeps_no_copy` |
| `lib-ordered-sort` | green, killed by a new test | `test_ordered_pairs_sort_their_input_by_the_placement_key` |
| `lib-ordered-later` | red | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `lib-ballot-guard` | red | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `lib-cited` | red | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `lib-cited-guard` | red | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `lib-flag-subject` | red | `test_a_charge_rests_on_a_cited_placement_or_a_flag_of_placements` |
| `lib-flag-event` | red | `test_a_charge_rests_on_a_cited_placement_or_a_flag_of_placements` |
| `lib-flag-all` | red | `test_a_charge_rests_on_a_cited_placement_or_a_flag_of_placements` |
| `lib-flag-union` | red | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` |
| `lib-misjudged-charged` | red | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `lib-misjudged-rule` | red | `test_every_value_the_census_holds_is_read_only` |

**The bounded mutation pass** (lesson 10): 39 mutants of exactly the eight listed classes over `eval/route_charges.py`
and the census spans phase 2 adds, each run alone against the touched suites by the same harness. The six survivors
were each re-run, red, against the test added for it in `39e03863`. The pass then stopped.

39 mutants (F 7, S 4, N 7, C 5, M 4, T 4, B 2, L 6): 33 killed on the first run, 6 killed by a test added for them, 0 named equivalent. The pass then stopped.

| mutant | class | result | test that went red |
|---|---|---|---|
| `F1-charge-targets-living` | F | survived, then killed | `test_a_dead_player_brings_no_charge_by_ballot_or_flag` |
| `F2-charge-flags-living` | F | survived, then killed | `test_a_dead_player_brings_no_charge_by_ballot_or_flag` |
| `F3-reach-ejecting` | F | killed | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `F4-placements-sorted` | F | killed | `test_turn_placements_read_the_four_kinds_and_nothing_else` |
| `F5-stated-kinds` | F | killed | `test_stated_places_are_the_route_kinds_only` |
| `F6-reading-window` | F | killed | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted6-regroups6]` |
| `F7-lib-misjudged-charged` | F | killed | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `S1-candidates-with-voter` | S | killed | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_the_voters_own_line]` |
| `S2-stated-any-player` | S | killed | `test_a_line_is_on_the_table_only_for_a_living_candidate_at_stated_places` |
| `S3-charge-own-universe` | S | killed | `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` |
| `S4-reach-all-ballots` | S | killed | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `N1-witness-floor` | N | killed | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `N2-block-call` | N | killed | `test_the_opening_handle_is_read_from_the_openers_own_first_prompt` |
| `N3-charge-fact` | N | killed | `test_entries_keep_the_fresh_kill_window_and_the_meeting_boundary` |
| `N4-lines-none` | N | killed | `test_resting_on_the_room_left_needs_a_living_crew_sighting` |
| `N5-walk-strict` | N | killed | `test_the_card_example_steps_are_true_to_the_map` |
| `N6-door-count-inverse` | N | killed | `test_the_card_example_steps_are_true_to_the_map` |
| `N7-no-ejection` | N | killed | `test_every_value_the_census_holds_is_read_only` |
| `C1-witness-meeting-tick` | C | killed | `test_a_witness_meeting_is_a_report_opened_by_a_witness_since_the_last_one` |
| `C2-stated-tick` | C | killed | `test_the_scripted_route_lines_game_is_read_back_and_counted` |
| `C3-line-to-tick` | C | killed | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_false_to_the_map-_off_map]` |
| `C4-placement-kind` | C | killed | `test_turn_facts_keep_ids_ticks_and_alibi_legs` |
| `C5-step-reading` | C | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `M1-stamp-lacks` | M | killed | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises` |
| `M2-block-voter` | M | killed | `test_a_route_block_in_a_game_that_does_not_serve_route_lines_raises` |
| `M3-lines-voter` | M | survived, then killed | `test_a_route_line_breach_names_whichever_voter_was_served_it` |
| `M4-charges-where` | M | survived, then killed | `test_an_incoherent_charge_fact_names_whichever_meeting_holds_it` |
| `T1-read-blocks-routes` | T | killed | `test_the_classified_blocks_are_every_tag_the_ballot_templates_render` |
| `T2-held-source-route` | T | killed | `test_the_script_runs_from_any_directory_and_exits_with_mains_code` |
| `T3-count-rows-more` | T | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `T4-charge-reads-flags` | T | killed | `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing` |
| `B1-walk-and-crossing` | B | killed | `test_a_step_the_map_or_the_game_does_not_give_is_false_to_the_map[planted4-regroups4]` |
| `B2-serve-message` | B | killed | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises` |
| `L1-readings-literal` | L | killed | `test_the_route_rows_follow_their_types` |
| `L2-stamp-suffix-literal` | L | killed | `test_the_stamp_check_follows_the_arm_spines_derivation` |
| `L3-stamp-template-literal` | L | killed | `test_the_stamp_check_follows_the_arm_spines_derivation` |
| `L4-checked-kinds-literal` | L | survived, then killed | `test_the_checked_placements_follow_their_type` |
| `L5-route-kinds-literal` | L | survived, then killed | `test_the_stated_places_follow_the_fields_route_kinds` |
| `L6-neighbours-canonical` | L | killed | `test_the_fold_checks_a_step_against_the_doors_its_inputs_carry` |

**Verification at this head.** Measured at `39e03863`, the code head; the commits after it touch only this card.

| command | exit | result |
|---|---|---|
| `env \| grep -c '^AILIBI_'` | - | 0 |
| `uv run pytest tests/eval/test_route_charges.py tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py tests/meetings/test_route_lines.py -n 6 --dist loadfile` | 0 | 791 passed (the field's one-home `ast` test among them, green) |
| `uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile` | 0 | 114 passed |
| `uv run pytest tests/experiments/test_route_lines_replay.py -n 6 --dist loadfile` | 0 | 26 passed |
| `uv run python -m experiments.lab.route_check_replay --check` (full clone) | 0 | reproduced, 46.5 s |
| `uv run python -m experiments.lab.route_lines_replay --check` (full clone) | 0 | reproduced, 44.6 s |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0 | the r1 column above |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent; the scorecard page and JSON are byte-identical |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | 63 checks, 51 OK, 0 FAIL, 7 evidence-branch absent, 5 info |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks and prompts; 102 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 | every checked figure true |
| `uv run mypy` on the three production modules and the three test modules; `uv run ruff check` and `ruff format --check` on `eval/`, `experiments/lab/`, `tests/eval/`, `tests/scripts/` | 0 | clean |
| `git diff --stat origin/main -- replays/ docs/process-scorecard.md docs/process-scorecard.json experiments/lab/results-route-check-replay.json experiments/lab/report-route-check-replay.md experiments/lab/results-route-lines-replay.json experiments/lab/report-route-lines-replay.md` | - | empty |
| `bash scripts/verify_samples.sh replays/<set>`, for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| demo bundle, built in this one checkout at `2228eb4a` (`main`) and at `39e03863` (`uv run python scripts/build_demo_bundle.py --out DIR` each, then `diff -r`) | 0 | 109 files each, empty diff: nothing ships |
| `bash scripts/check.sh` at `1b2bc938` (output to a file, exit code from the run itself) | 1 | 1 failed, 10,696 passed, 20 skipped, 3 xfailed: `tests/meetings/test_route_lines_arm.py::test_the_census_classifies_it_as_not_read` pinned the entry this card replaces (Decision 9; fixed in the next commit) |
| `uv run pytest tests/meetings/test_route_lines_arm.py -n 6` after the fix | 0 | 57 passed |
| `bash scripts/check.sh` at `ca6ab4c6`, the pushed head after the fix (run once, output to a file, exit code from the run itself) | 0 | pytest 10,697 passed, 20 skipped, 3 xfailed; frontend 695 passed; the build succeeds; the commit after it touches only this row and the box above |

**Limitations.**
- Each round is one hosted recording of 50 games; the counts describe those games and are no bar.
- A reconcilable pair proves no innocence: the charge cells count a process at the table, not a wrong vote.
- No committed set carries the route lines, so every route line cell reads n/a there; the conformance check is
  exercised by the field's scripted game, the planted carriers and the reach derivation, and first reads a hosted
  recording at round 3.
- The reach derivation runs the field's builder over the recorded ballots as a reading, never a recording; reaching is
  showing a line, not changing a vote.
- The r2 agreement reads `replays/samples/9p2i` as the route-check replay pinned it; a promotion that replaces that set
  retires or re-points the r2 agreement, as the card's Constraints say, and the r1 agreement survives it.

### Review corrections, round 4 (2026-10-07)

One blocking finding of the round-4 dispatch, on `50830711` (correctness lens): the presence cell
`meetings_with_a_route_line` survived its argument `bool(distinct)` swapped for `bool(meeting.ballots)`, a listed
class S mutant (one collection swapped for a related one). Every planted meeting with no line held no ballots, so a
count of meetings holding ballots read the same; on a route-lines carrier a meeting whose ballots carry no line tells
the two apart (on the round-2 carrier with the field builder's lines, 116 of 117 against 117 of 117). The finding is
valid and is repaired by tests alone: no production line, recorded byte, page or JSON moves. Every ruling in Phase 1's
Decisions and in rounds 1 to 3 stands.

**Sections this rests on.** As round 3: `docs/architecture.md` "Layering" and "Determinism and the substrate ladder";
`tasks/work/route-lines-field.md` (the census contract); item 4's presence cell ("meetings where some ballot carried a
line, over meetings").

**What changed.**
- `test_the_route_lines_cells_count_ballots_lines_and_steps`: the second meeting now holds one ballot carrying a
  recorded call and no line (it held none before), and the test asserts every planted meeting holds ballots. The
  presence cell stays 1 of 2; `ballots_carrying_route_lines` reads 2 of 4, 1 not evaluable (was 2 of 3); the tables and
  conformance cells are unchanged.
- `test_the_fields_reach_is_derivable_from_the_census_through_the_field`: on each round column the census's presence
  cell equals the route-lines replay's count of meetings serving a line over its meetings, and the ballot cell equals
  its `ballots_with_block` over `ballots`, both read from the committed `experiments/lab/results-route-lines-replay.json`,
  never typed in. The test also asserts that some meeting in the column serves no line, so the assertion can tell the
  two counts apart. At this head: 116 of 117 meetings and 665 of 691 ballots on round 2; 123 of 124 and 692 of 717 on
  round 1.

**Neuter and mutation table** (lessons 1 and 10), over the one production span the finding names, `_fold_route_lines`'s
presence count in `eval/gameplay_census.py`. Each was run alone (harness `<scratch>/fix-r4-census/mut.py`: edit the
argument, run `tests/eval/test_gameplay_census.py`, `tests/meetings/test_route_lines.py` and
`tests/meetings/test_route_lines_arm.py` with `-x`, restore from a saved copy), first against the round-3 tests at
`50830711`, then against this round's.

| probe | class | round-3 tests | this round | test that went red |
|---|---|---|---|---|
| `R4-S1` `bool(distinct)` for `bool(meeting.ballots)` | S | survived | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps`; also `test_the_fields_reach_is_derivable_from_the_census_through_the_field[r2]` and `[r1]` (117/117 and 124/124 against 116/117 and 123/124) |
| `R4-S2` `bool(distinct)` for `bool(meeting.living)` | S | killed | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `R4-N1` `bool(distinct)` for some ballot's `route_lines is not None` | N | survived | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `R4-N2` `bool(distinct)` for `not distinct` | N | killed | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `presence-argument` `bool(distinct)` for `True` (the neuter) | neuter | killed | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |

5 probes: 3 killed by the round-3 tests, the other 2 (`R4-S1`, the finding's, and `R4-N1`) killed by this round's planted
meeting; 0 survivors, 0 named equivalent. The pass then stopped.

**Verification at this head.** The code head is this round's test commit, `e91d8332`; the card commits after it touch
only this card. The lab `--check` runs and every other row of round 3's table do not depend on a test-only change and were not re-run
beyond the gate; the gate's row records its exit code.

| command | exit | result |
|---|---|---|
| `uv run pytest tests/eval/test_gameplay_census.py -k test_the_route_lines_cells_count_ballots_lines_and_steps` | 0 | 1 passed |
| `uv run pytest tests/eval/test_gameplay_census.py -k test_the_fields_reach_is_derivable_from_the_census_through_the_field` | 0 | 2 passed (r2, r1) |
| `uv run ruff check`, `ruff format --check` and `mypy` on `tests/eval/test_gameplay_census.py` | 0 | clean |
| `uv run python scripts/validate_task_docs.py` | 0 | Task docs validation passed: 390 phase tasks and prompts; 102 work cards |
| demo bundle, built in this one checkout at `2228eb4a` (`main`) and at `5e62e38a` (`uv run python scripts/build_demo_bundle.py --out DIR` each, then `diff -r`) | 0 | 109 files each, empty diff: nothing ships |
| `bash scripts/check.sh` at `5e62e38a`, the pushed head (run once, output to a file, exit code from the run itself) | 0 | pytest 10,697 passed, 20 skipped, 3 xfailed; frontend 695 passed; the build succeeds; the commit after it touches only this card |

**Limitations.** As round 3. The presence cell is still exercised only by planted carriers, the field's scripted game
and the reach derivation, since no committed set carries the route lines.

### Review corrections, round 5 (2026-10-07)

Three blocking findings of the round-5 dispatch, on `c25feb26` (correctness lens), each a survivor of a listed class over
a span phase 2 wrote. All three are valid and are repaired by tests alone: no production line, recorded byte, page or
JSON moves. Every ruling in Phase 1's Decisions and in rounds 1 to 4 stands.

1. **`route_lines_per_meeting` counts players, not lines** (class S). The row argument
   `len({line.subject for line in distinct})` swapped for `len(distinct)` survived, since every planted meeting's
   distinct lines were about distinct players. A planted meeting whose two ballots carry different true lines about one
   player tells the two apart: the head lands it in row 1, the mutant in row 2.
2. **A meeting's `regroup_ticks` are the earlier meetings' only** (class S). The loader's `applied_meetings[:index]`
   swapped for `applied_meetings` survived: no committed count moves, because every stated place on the committed
   rounds is at or before its meeting's tick, and so is every planted one. The repair is the finding's first option, a
   pin of the carrier field on recorded regroup games, never a claim that the mutant is equivalent: no mechanism of the
   census bounds a stated tick by the meeting's tick, so a later recording could tell the two apart.
3. **The two refusals' message arguments** (class M). In the stamp refusal, `seed {seed}` for the literal `seed 0`
   survived (the only planted game was seed 0 and the test matched by search) and `set {path.parent}` for a constant
   survived (no test read it); in the route-block refusal, the parser's `{error}` for a constant survived (the test
   read only the prefix).

**Sections this rests on.** As round 3: `docs/architecture.md` "Layering" and "Determinism and the substrate ladder";
`tasks/work/route-lines-field.md` (the census contract); `orchestrator.replay.derive_regroup_ticks`, whose docstring
gives the regroup ticks that follow the meetings before the current one; `meetings.route_lines.parse_route_lines`, which
refuses with its own reason; item 4's table ("meetings by candidates with a line") and its refusals.

**What changed** (`tests/eval/test_gameplay_census.py` only).
- `test_two_different_lines_about_one_player_are_one_player_with_a_line` (new): one meeting, `p-2` served MEDBAY 6 to
  WEST_HALL 7 about `p-0` and `p-3` served WEST_HALL 7 to ADMIN 8 about `p-0`, all three places stated.
  `route_lines_per_meeting` reads row 1 = 1, `route_steps_by_reading` 2 walks, both conformance cells 0 of 2.
- `test_a_meetings_regroup_ticks_are_the_earlier_meetings_resume_ticks` (new): on round 2's committed recording
  (`replays/samples/9p2i`) and on the field's scripted game, every game's first meeting holds no regroup tick, each
  meeting holds exactly the tick after each earlier meeting, and none after its own tick.
- `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises`: both seed-0 refusals are now matched whole,
  naming the restamped set's directory, and a new module fixture `fake_routes_on` records a fake game at seed 3 under
  round 2's config with the setting (3 meetings; no line is served, but the setting and its stamp hold). With its arm
  dropped it is refused naming its own set directory and seed 3.
- `test_a_route_block_the_fields_parser_refuses_raises_naming_the_voter`: parametrized over two planted breaks of a
  served step, `walking fits` to `walking flies` (the field's "a route step is not in the served form") and
  `1 door apart` to `1 doors apart` (its "a route step's door noun agrees with its count"). Each asserts the field's
  parser raises exactly that reason on the broken prompt, and that the census's refusal is the whole message ending in
  it.

**Neuter and mutation table** (lessons 1 and 10). This round's diff holds no production line, so the pass runs over the
spans the findings name: `_fold_route_lines`'s row count, the loader's regroup-tick derivation, the stamp refusal and
the loader's `where`, and `ballot_route_lines`'s refusal, all in `eval/gameplay_census.py`; `eval/route_charges.py` is
untouched this round. Each probe was run alone (harness `<scratch>/fix-r5-census/mut.py`: edit one span, run
`tests/eval/test_gameplay_census.py` and `tests/eval/test_route_charges.py` with `-x`, restore from a saved copy), first
against the round-4 tests (a copy of `c25feb26`'s test file run in place of this round's), then against this round's.

| probe | class | round-4 tests | this round | test that went red |
|---|---|---|---|---|
| `R5-S1` the row count `len({line.subject for line in distinct})` for `len(distinct)` (the finding's) | S | survived | killed | `test_two_different_lines_about_one_player_are_one_player_with_a_line` |
| `R5-S2` the row count over the last ballot's `lines` for `distinct` | S | killed | killed | crashes on planted meetings with no ballot (`test_corpse_age_reads_the_kill_event_tick_never_the_body_id` first) |
| `R5-F1` the regroup ticks over `applied_meetings` for `applied_meetings[:index]` (the finding's) | S | survived | killed | `test_a_meetings_regroup_ticks_are_the_earlier_meetings_resume_ticks` |
| `R5-F2` the regroup ticks over `applied_meetings[: index + 1]` (the meeting's own regroup) | S | survived | killed | `test_a_meetings_regroup_ticks_are_the_earlier_meetings_resume_ticks` |
| `R5-L1` `derive_regroup_ticks(None, ...)` for the recorded config | L | killed | killed | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]`; also the scripted game's test |
| `R5-Ma` the stamp refusal's `seed {seed}` for `seed 0` (the finding's M-a) | M | survived | killed | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises` (the seed-3 plant) |
| `R5-Mb` the stamp refusal's `set {path.parent}` for `set planted` (the finding's M-b) | M | survived | killed | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises` |
| `R5-B1` the stamp refusal's `lacks` and `credits` branches swapped | B | killed | killed | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises`; also `test_the_stamp_check_follows_the_arm_spines_derivation` |
| `R5-B2` its `serve` and `do not serve` branches swapped | B | killed | killed | `test_a_stamp_without_the_arm_or_the_arm_without_the_setting_raises` |
| `R5-Mg` the loader's `where` for `set planted, seed 0, ` (the finding's M-g, re-checked) | M | killed | killed | `test_the_loader_names_the_set_and_seed_of_an_unchecked_holds_nothing_skip` |
| `R5-Mf` the route-block refusal's `{error}` for `refused` (the finding's M-f) | M | survived | killed | `test_a_route_block_the_fields_parser_refuses_raises_naming_the_voter[step-form]` |

Classes: S swaps one collection for a related one, L replaces a read of a loaded source with a literal, M replaces a
message argument with a constant, B swaps adjacent branches. 11 probes: 5 killed by the round-4 tests, the other 6 (the
finding's five and `R5-F2`) killed by this round's tests; 0 survivors, 0 named equivalent. The pass then stopped.

**Verification at this head.** The code head is this round's test commit, `584576a3`; the card commits after it touch
only this card.

| command | exit | result |
|---|---|---|
| `env`, counting `AILIBI_` names with `grep -c` | 1 (no match) | 0 |
| `uv run pytest tests/eval/test_route_charges.py tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py tests/meetings/test_route_lines.py tests/meetings/test_route_lines_arm.py tests/experiments/test_route_lines_replay.py -n 6 --dist loadfile` | 0 | 877 passed |
| `uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile` | 0 | 114 passed |
| `uv run python -m experiments.lab.route_check_replay --check` | 0 | reproduced |
| `uv run python -m experiments.lab.route_lines_replay --check` | 0 | reproduced |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0 | 82,949 bytes of JSON |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0 | every check passed; 7 report EVIDENCE-BRANCH-ABSENT, the expected fresh-clone state |
| `bash scripts/verify_samples.sh replays/<set>`, for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run python scripts/validate_task_docs.py` | 0 | Task docs validation passed: 390 phase tasks and prompts; 102 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 | budgets verified |
| `git diff --stat origin/main --` the recordings, the scorecard page and JSON, and both lab JSONs and reports | 0 | empty |
| `uv run ruff check`, `ruff format --check` and `mypy` on `tests/eval/test_gameplay_census.py` | 0 | clean |
| `uv run pytest -m campaign -n 6 --dist loadfile` | 0 | 337 passed |
| demo bundle, built in this one checkout at `2228eb4a` (`main`) and at `6b4ad15d` (`uv run python scripts/build_demo_bundle.py --out DIR` each, then `diff -r`) | 0 | 109 files each, empty diff: nothing ships |
| `bash scripts/check.sh` at `6b4ad15d`, the pushed head (run once, output to a file, exit code from the run itself) | 0 | pytest 10,700 passed, 20 skipped, 3 xfailed; frontend 695 passed; the build succeeds; the commit after it touches only this card |

**Commit trailer.** This round's commits carry `Co-Authored-By: Claude Opus 5.5`, the model that wrote them and the line
the session's harness names, as round 4's did; the dispatch named another model's line, which would misattribute them.

**Limitations.** As round 3. The regroup pin holds the carrier on the two regroup recordings it reads; no committed
stated place lies after its meeting's tick, so the census's counts on the committed rounds cannot themselves show the
slice. The presence cell is still exercised only by planted carriers, the field's scripted game and the reach
derivation, since no committed set carries the route lines.

### Review corrections, round 6 (2026-10-07)

Three blocking findings of the round-6 dispatch, on `e78fd7cc` (correctness lens), each a survivor of a listed class over
a span phase 2 wrote. All three are valid and are repaired by tests alone. The fixer's own bounded pass over every phase-2
span then found two more survivors, killed the same way. No production line, recorded byte, page or JSON moves. Every
ruling in Phase 1's Decisions and in rounds 1 to 5 stands.

1. **The charge-fact refusals' seed and set** (class M). `_fold_route_charges` raises at three places, each naming
   `set {acc.label}, seed {seed}, {where}`. Every incoherent-fact plant folded only `planted/set` at seed 7, so a
   constant for the seed or the set survived at each of the three; this round's pass found the meeting (`{where}`)
   surviving at the second and third as well, since only the first refusal's meeting was varied (round 3's
   `M4-charges-where`).
2. **The reach cell's not-evaluable guard** (class S). `any(ballot.route_lines is None for ballot in ejecting)` swapped
   for every ballot of the meeting survived: no plant put a SKIP ballot without a recorded call beside readable ejecting
   ballots. There the head reads 1 of 1 and the mutant 0 of 0 with 1 not evaluable, voiding an ejection item 4b counts.
3. **The loader's living argument to `route_charge_fact`** (class S). `living=living` swapped for
   `frozenset(state.players)` survived: the dead-player test calls the reader directly with its own living set, and no
   recording the loader reads names a dead player in a ballot or a flag. The repair is the finding's first option, a spy
   on the loader's call.
4. **From this round's pass: the ejected player's charge on a pair with no regroup ticks** (`R6-K4`, class K).
   `misjudging_pairs(own, charged, regroup_ticks=frozenset())` survived: on the committed rounds no ejection's charge
   rests only on a crossing of the regroup, and the regroup-crossing plant ejected no one.
5. **From this round's pass: the loader's place in the unserved-route-block refusal** (`R6-M10`, class M). The `where`
   argument at `ballot_route_lines`'s call site swapped for the constant `set planted, seed 0, meeting meeting-0`
   survived: the loader test matched the refusal by a search for its seed, meeting and voter.

**Sections this rests on.** As round 3: `docs/architecture.md` "Layering" and "Determinism and the substrate ladder";
`tasks/work/route-lines-field.md` (the census contract); item 3's charge cells and their refusals; item 4b's reach cell
(ejections charged on a reconcilable pair whose ejecting voter was served a line about the ejected player);
`eval/route_charges.py`, whose charges the census counts only against the living players a ballot or a flag names.

**What changed** (`tests/eval/test_gameplay_census.py` only).
- `test_an_incoherent_charge_fact_is_refused_naming_its_meeting`: each of the four plants is folded as planted and again
  under `other/set`, seed 11 and its meeting renamed `gathering-3` (`_renamed_meetings`, as
  `assert_breach_names_its_place` does), and each refusal is matched whole; the third refusal's two plants now carry its
  whole text.
- `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter`: two plants beside a SKIP ballot with no
  recorded call. An ejecting ballot carrying a walk about the ejected player reads 1 of 1, 0 not evaluable; one carrying
  no line reads 0 of 1.
- `test_the_loader_reads_each_meetings_charges_over_the_players_living_at_its_open` (new): a spy on
  `census.route_charge_fact` during `load_census_inputs` on the field's scripted game records each call's meeting, living
  set and regroup ticks. The calls are exactly the two meetings' (`MeetingFact.meeting_id`, `.living`,
  `.regroup_ticks`), and each meeting's living set is the roster less every player killed before its tick or ejected at
  an earlier meeting (8 of 9 at the first, 5 of 9 at the second), so it is never the roster.
- `test_a_charge_resting_only_on_a_regroup_crossing_needs_the_regroup_ticks`: the planted row also ejects the charge's
  target. With the meeting's regroup ticks its fact is `RouteChargeFact(1, 1, ejected_pairs=1,
  ejected_charged_on_pair=True)`; without them `RouteChargeFact(1, 0, ejected_pairs=0, ejected_charged_on_pair=False)`.
- `test_the_loader_refuses_a_route_block_its_settings_do_not_serve`: the refusal is matched whole, naming the copy's own
  set directory, seed 0, the first meeting's id and the first voter served a line.

**Neuter and mutation table** (lessons 1 and 10). This round's diff holds no production line, so the pass runs over the
phase-2 spans the dispatch names: `_fold_route_charges`, `_fold_route_lines`, `route_charge_fact` and the phase-2
call-site arguments of `_meeting_fact` in `eval/gameplay_census.py`, and `eval/route_charges.py`. It covers every raise
site's message arguments, every call-site argument and every collection read the eight classes reach, 38 probes. Each
was run alone (harness `<scratch>/fix-r6-census/mut.py`: edit one span, run the seven route suites of round 5's
verification with `-x`, restore from a saved copy), first against the round-5 tests (`e78fd7cc`'s test file run in place
of this round's), then against this round's at `372e66d8`. The red test is the first one `-x` met.

| probe | class | round-5 tests | this round | test that went red |
|---|---|---|---|---|
| `R6-M1` first refusal's `seed {seed}` for `seed 7` (the finding's) | M | survived | killed | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting` (first refusal's plant) |
| `R6-M2` second refusal's `seed {seed}` for `seed 7` (the finding's) | M | survived | killed | the same (second refusal's plant) |
| `R6-M3` third refusal's `seed {seed}` for `seed 7` (the finding's) | M | survived | killed | the same (third refusal's first plant) |
| `R6-M4` first refusal's `set {acc.label}` for `set planted/set` (the finding's) | M | survived | killed | the same (first refusal's plant) |
| `R6-M5` second refusal's `set {acc.label}` for `set planted/set` | M | survived | killed | the same (second refusal's plant) |
| `R6-M6` third refusal's `set {acc.label}` for `set planted/set` (the finding's) | M | survived | killed | the same (third refusal's first plant) |
| `R6-M7` first refusal's `{where}` for `meeting meeting-3` | M | killed | killed | round 5: `test_an_incoherent_charge_fact_names_whichever_meeting_holds_it`; this round: the first refusal's plant |
| `R6-M8` second refusal's `{where}` for `meeting meeting-3` | M | survived | killed | `test_an_incoherent_charge_fact_is_refused_naming_its_meeting` (second refusal's plant) |
| `R6-M9` third refusal's `{where}` for `meeting meeting-3` | M | survived | killed | the same (third refusal's first plant) |
| `R6-S1` the reach guard over `meeting.ballots` for `ejecting` (the finding's) | S | survived | killed | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `R6-S2` the reach count over `meeting.ballots` for `ejecting` | S | killed | killed | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `R6-F1` the `ejecting` filter `if ballot.target == meeting.ejected` dropped | F | killed | killed | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `R6-N1` the reach guard's `is None` for `is not None` | N | killed | killed | `test_a_route_line_reaches_an_ejection_only_through_an_ejecting_voter` |
| `R6-N2` the ejection-on-a-pair count's `pairs > 0` for `pairs is not None` | N | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-N3` the witness-meeting count's `pairs > 0` for `pairs is not None` | N | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-S3` a ballot's candidates `meeting.living` for `meeting.living - {ballot.voter}` | S | killed | killed | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_the_voters_own_line]` |
| `R6-F2` the one-line-per-candidate filter `line.subject in subjects or` dropped | F | killed | killed | `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter[route_lines_off_the_table-_second_line]` |
| `R6-K1` the map check's `regroup_ticks=meeting.regroup_ticks` for `frozenset()` | K | killed | killed | `test_the_route_lines_cells_count_ballots_lines_and_steps` |
| `R6-N4` `if lines is None` for `if lines is not None` | N | killed | killed | `test_impostor_fate_splits_seen_unseen_and_never_vented` (crashes on a ballot with no route lines) |
| `R6-F3` the ballot targets' `if ballot.target in living` dropped | F | killed | killed | `test_a_dead_player_brings_no_charge_by_ballot_or_flag` |
| `R6-F4` the flag subjects' `if subject in living` dropped | F | killed | killed | `test_a_dead_player_brings_no_charge_by_ballot_or_flag` |
| `R6-S4` a charge's pairs over `universe` for the target's `own` | S | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-S5` the ejected player's pairs `ordered_pairs(universe)` for `ordered_pairs(own)` | S | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-S6` the ejected player's charge on a pair over `universe` for `own` | S | killed | killed | `test_every_value_the_census_holds_is_read_only` |
| `R6-K2` a charge's pairs with `regroup_ticks=frozenset()` | K | killed | killed | `test_a_charge_resting_only_on_a_regroup_crossing_needs_the_regroup_ticks` |
| `R6-K3` the ejected player's pairs with `regroup_ticks=frozenset()` | K | killed | killed | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` |
| `R6-N5` the ejected player's pairs' `is not None` for `is None` | N | killed | killed | `test_every_value_the_census_holds_is_read_only` |
| `R6-K4` the ejected player's charge on a pair with `regroup_ticks=frozenset()` (this pass's) | K | survived | killed | `test_a_charge_resting_only_on_a_regroup_crossing_needs_the_regroup_ticks` |
| `R6-S7` the loader's `living=living` for `frozenset(state.players)` (the finding's) | S | survived | killed | `test_the_loader_reads_each_meetings_charges_over_the_players_living_at_its_open` |
| `R6-K5` the loader's `regroup_ticks=regroup_ticks` for `frozenset()` | K | killed | killed | `test_the_census_route_charges_are_the_route_check_replays_meeting_by_meeting[r2]` |
| `R6-L1` the loader's `served=route_lines_served` for `True` | L | killed | killed | `test_the_loader_refuses_a_route_block_its_settings_do_not_serve` |
| `R6-M10` the loader's `where=meeting_where` at `ballot_route_lines` for a constant (this pass's) | M | survived | killed | `test_the_loader_refuses_a_route_block_its_settings_do_not_serve` |
| `R6-N6` `charges_against`'s `primary_reason_id is None` for `is not None` | N | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-F5` `charges_against`'s `if target not in flag.subjects` filter dropped | F | killed | killed | `test_a_charge_rests_on_a_cited_placement_or_a_flag_of_placements` |
| `R6-D1` a flag's events `(flag.event_a_id, flag.event_b_id)` less `event_b_id` | D | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-F6` `misjudging_pairs`'s charged-end filter dropped | F | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-S8` `ordered_pairs`'s `ordered[index + 1 :]` for `ordered` | S | killed | killed | `test_the_committed_census_matches_a_recomputation` |
| `R6-F7` `ordered_pairs`'s `sorted(..., key=_placement_key)` wrapper dropped | F | killed | killed | `test_ordered_pairs_sort_their_input_by_the_placement_key` |

Classes: M replaces a message argument with a constant, S swaps one collection for a related one, F drops a filter or
wrapper on a collection, N replaces a comparison with a None test or its inverse, K replaces a tick read with a constant,
L replaces a read of a loaded source with the canonical literal, D drops one member of a tuple. 38 probes: 26 killed by
the round-5 tests; the other 12 (the findings' five seed and set constants with the sixth at the second refusal, the two
meeting constants, `R6-S1`, `R6-S7`, `R6-K4` and `R6-M10`) killed by this round's tests; 0 survivors, 0 named
equivalent. The pass then stopped.

**Verification at this head.** The code head is this round's test commit, `372e66d8`; the card commits after it touch
only this card.

| command | exit | result |
|---|---|---|
| `env`, counting `AILIBI_` names with `grep -c` | 0 | 0 names |
| `uv run pytest tests/eval/test_route_charges.py tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py tests/experiments/test_route_check_replay.py tests/meetings/test_route_lines.py tests/meetings/test_route_lines_arm.py tests/experiments/test_route_lines_replay.py -n 6 --dist loadfile` | 0 | 878 passed |
| `uv run pytest tests/eval/test_evidence_honesty.py -n 6 --dist loadfile` | 0 | 114 passed |
| `uv run python -m experiments.lab.route_check_replay --check` | 0 | reproduced |
| `uv run python -m experiments.lab.route_lines_replay --check` | 0 | reproduced |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout` | 0 | 82,949 bytes of JSON |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/verify_ml_evidence.py` (offline) | 0 | every check passed; 7 report EVIDENCE-BRANCH-ABSENT, the expected fresh-clone state |
| `bash scripts/verify_samples.sh replays/<set>`, for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run python scripts/validate_task_docs.py` | 0 | Task docs validation passed: 390 phase tasks and prompts; 102 work cards |
| `uv run python scripts/check_doc_facts.py` | 0 | budgets verified |
| `git diff --stat origin/main --` the recordings, the scorecard page and JSON, and both lab JSONs and reports | 0 | empty |
| `git diff --stat e78fd7cc 372e66d8 --` every source, script, page, recording and lab directory | 0 | empty: the round's code diff is the one test file |
| `uv run ruff check`, `ruff format --check` and `mypy` on `tests/eval/test_gameplay_census.py` | 0 | clean |
| `uv run pytest -m campaign -n 6 --dist loadfile` | 0 | 337 passed |
| demo bundle, built in this one checkout at `2228eb4a` (`main`) and at `27e14ec6` (`uv run python scripts/build_demo_bundle.py --out DIR` each, then `diff -r`) | 0 | 109 files each, empty diff: nothing ships |
| `bash scripts/check.sh` at `27e14ec6`, the pushed head (run once, output to a file, exit code from the run itself) | 0 | pytest 10,701 passed, 20 skipped, 3 xfailed; frontend 695 passed; the build succeeds; the commit after it touches only this card |

**Commit trailer.** As rounds 4 and 5: this round's commits carry `Co-Authored-By: Claude Opus 5.5`, the model that wrote
them and the line the session's harness names; the dispatch named another model's line, which would misattribute them.

**Limitations.** As round 3. The living-set spy holds the loader's argument on the field's scripted game; the swap it
kills, `R6-S7`, moved no committed count (it survived the round-5 tests, the census's recomputation and both rounds'
meeting-by-meeting agreements among them), so the committed rounds cannot themselves tell the living set from the
roster. Likewise the regroup-crossing ejection is a planted row: `R6-K4` moved no committed count either.
