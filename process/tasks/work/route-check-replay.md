# Offline replay of the route checks on the committed recordings

**Status:** done

## Outcome

Before any round 3 is considered, the owner needs one count the diagnosis of 2026-10-02 could not give: on the
games already recorded, what each candidate route check would have shown each voter, and whether it would have
reached the meetings where the table charged a player with a move the map or the public regroup in fact allows.
Two readings of the existing check disagree today (it reaches 0 or 3 of the 5 ejected kill witnesses, and 12 or 17
of the 22 innocent ejections, in round 2), and the other check has never been counted on these games.

This card builds one offline, count-only lab instrument, `experiments/lab/route_check_replay.py`. It replays
the committed bytes of three 9-player columns, each read alone and never pooled:

- **r2**: `replays/samples/9p2i` at `59bbd1be`, the promoted round 2 (era `stage-b-r2`). Its 50 replays are
  byte-identical to `replays/candidates/stage-b-r2/9p2i` at `d41c9006` (`git ls-tree` of both: every replay
  blob equal; only `experiment-config.json` was added).
- **r1**: `replays/candidates/stage-b-r1/9p2i` at `59bbd1be`, unchanged since `d41c9006`.
- **s9**: the baseline-9 bytes of `replays/samples/9p2i`, which the promotion replaced in place, read from
  history at `d41c9006`. These are the same seeds 0-49 as r1 and r2, and the round-2 record (section 9.7)
  says the s9 column reproduces only there. `replays/ml_corpus/9p2i` is the same era but is **not read**: it
  is a different seed band, so it pairs with no r1 or r2 game, cannot settle a count the diagnosis made on
  seeds 0-49, and its meeting keys would expose a held band.

For every meeting it reports, per column and per meeting kind (report with vent proof, report without, button),
what each check would have shown each voter:

- **(a) the walkable-pair clause** of the corroboration ledger, built exactly as the meeting manager builds it
  (movement records, regroup ticks, trigger kind, living roster), with its one-hop, one-tick bound;
- **(b) the travel-check lines of the recorded field `evidence_reasoning_version = 2`**, as that field renders
  them into each voter's memory, read twice: on the recorded observations as they are, and with each legacy
  start-of-tick sighting labelled a snapshot (an approximation of the observation delivery that field
  requires; Evidence);
- **(c) a reference reading** of the narrow field the diagnosis sketches, computed inside the instrument from
  existing functions (stated placements at the table, several hops, a regroup crossing named). It is no
  mechanism and no arm; its gaps say what such a field would have to read.

Its reading is a **process count**, never role-correctness: impossible-move charges resting on stated pairs that
the map or the public regroup reconciles, and ejections of a player who had such a pair. It writes
`experiments/lab/report-route-check-replay.md` and `experiments/lab/results-route-check-replay.json`, and the
card's Results end with a dated reading the owner can decide round 3 on. It records nothing, changes no game
behaviour, prompt, recorded byte or published file, and authorizes no recording.

## Evidence

Every `path:line` is at `59bbd1be` (labelled as such) and is re-anchored by its symbol at dispatch;
`meetings/`, `agents/` and `engine/` are unchanged between `d41c9006` and `59bbd1be` (`git diff --stat` reads
empty), so the diagnosis's `d41c9006` citations name the same code. Every count below is re-measured by the
instrument at dispatch and the dispatch figure governs.

**The dispute** (diagnosis memo of 2026-10-02, `tasks/diagnosis-2026-10-02/README.md`, Part 2.2 amendment 7
and Part 3 card 2). A transcript-only probe (`walkfire.py`: no movement records, no
regroup ticks) finds a walkable pair for the ejected player in 12 of 22 round-2 innocent ejections, 1 of 44
impostor ejections and 0 of the 5 ejected witnesses; the refuter's version, adding the movement destinations
and regroup ticks the manager passes, finds 17 of 22 and 3 of 5. The memo calls the claim "not established
either way". The hand classification (route misjudged in 11 of 22) is one rater's, with five boundary cases
(9 to 12), and keyword stand-ins are not specific (11 of 17 ejected reporters against 12 of 44 impostor
ejections). The five ejected witnesses are r2 seeds 28, 29, 35 and 43 at their first meeting and seed 30 at
its second (`reporter-ejections.md`, same folder).

**Check (a) at `59bbd1be`.**
- The pair rule is `_walkable_transits` (`meetings/corroboration.py:561-600`): a pair qualifies when
  `1 <= hops <= elapsed` within `MAP_ARBITRATION_MAX_HOPS = 1` and `MAP_ARBITRATION_MAX_TICK_GAP = 1`
  (`meetings/constants.py:62-63`), at most `MAX_WALKABLE_TRANSITS_PER_SUBJECT = 2` per subject
  (`meetings/corroboration.py:97`). It reconciles or stays silent; it never charges.
- `build_testimony_ledger` (`:603-721`) builds rows only for players accused at the meeting, over
  `reconstruct_stated_paths` (`meetings/transcript.py:1415-1582`): spoken sightings that pass the relevance
  gate (spawn window, kill-scene rooms and the regroup window dropped, `:1250-1310`), plus each speaker's own
  whereabouts. Alibi routes are not placements.
- The manager builds it only under the ambient corroboration switch (`meetings/manager.py:1703-1716`, resolved
  at `:1363-1367`; the switch, `meetings/corroboration.py:100-124`), off in all three columns. The ballot
  shows each pair to a voter whose candidate list holds the subject
  (`agents/strategic/prompts/qwen3_6_27b/vote_ballot.j2:256-257`, `:269-270`). Because its only switch is
  ambient, (a) is not itself a round-3 arm; using its rule in a round would need a recorded field, which is
  the narrow field.
- Cross-check: the round-2 record's two committed cells for "ejected with a walkable pair" (section 9.8: 69/411
  over the four baseline-9 sets, 56/321 over three) differ by exactly s9's 90 ejections, so (a) on s9 reads 13
  of 90. s9 has no regroup, so the counterfactual's ledger there is (a) as built.

**Check (b) at `59bbd1be`.**
- `v2_evidence_context_rows` (`agents/memory/evidence_context.py:340-591`) reads one voter's memory: the
  voter's own sightings, each public regroup as a placement (`:379-391`), and reported claims of kind
  whereabouts, alibi or saw_player (`:395-406`). It walks the map with several hops through `assess_travel`
  (`:110-158`) and names an interval that crosses a public regroup undecidable (`:532-544`). The store renders
  these rows only under version 2 (`agents/memory/store.py:729-747`).
- **Timing.** Reported testimony is absorbed after each meeting (`orchestrator/game.py:3602-3625`), and the
  ballot renders the memory held at the meeting's open (`meetings/manager.py:2335-2341`). So at a first
  meeting (b) holds no claim at all, and at any meeting it never holds that meeting's own claims.
- **Phase.** All three columns use legacy observation delivery, so a recorded sighting carries no phase and
  reads "unknown"; under the unknown-phase rule (`agents/memory/evidence_context.py:146-151`) a walk fits only
  with one spare tick. One hop in one tick, or two hops in two, reads "insufficient timing", which is exactly
  the kill witness's walk-in.
- **Prerequisite.** The runner and the game refuse evidence version 2 without temporal observations version 2
  (`orchestrator/game.py:1576-1582`, `:2577-2583`). That is the ambient substrate toggle
  `AILIBI_TEMPORAL_OBSERVATIONS` (`docs/architecture.md`, "Determinism and the substrate ladder"), which the
  wave kept OFF because a temporal-ON set fails the validity gate's bare-shell provenance check and changes
  every prompt (`tasks/decision-2026-09-24-stage-b-wave.md:178-180`). The field is also a package (death
  evidence and account-uncertainty lines), and its one live reading, the archived fifth run, cast 14 EJECT
  and 136 SKIP ballots (`docs/process-scorecard.md:227-236`).
- A legacy snapshot packet is built from the pre-action world state
  (`tests/meetings/test_prompt_byte_golden.py:698-723`), the instant temporal version 2 calls a snapshot; a
  legacy move or action-sourced row is dated at delivery, not at its event. That is why the (b-snapshot)
  reading relabels plain sightings only.

**The walk.** `tests.meetings.test_prompt_byte_golden.walk_replay_meetings` (`:726-888`) is the one committed
reconstruction that drives the real `MeetingManager` and yields each meeting's participants (their sighting
and movement records) and each agent's memory at the meeting's open (`ReconstructedMeeting`, `:337-394`), under
the recording's own settings, with every state hash verified. `scripts/counterfactual_phase21.py:84-92`
records the ruling that lets a non-test module import it. `render_for_prompt` writes to working memory
(`agents/memory/store.py:768-776`), so a render made for counting runs on a deep copy.

**Counts to re-measure**, for s9, r1 and r2 (round-2 record sections 6.4 and 9.6; diagnosis section 1.4):
ejections 90, 54 and 66 (innocent 9, 15 and 22; impostor 81, 39 and 44); meetings 145, 124 and 117 (report
135, 118 and 114; button 10, 6 and 3). A **witness meeting** is a report meeting whose reporter the census's
kill facts record as a witness of a kill since the previous meeting: 3, 3 and 14 (crew-witnessed kills,
census `kills_seen_by_crew`, 3, 4 and 14).

## Acceptance

- [x] Review correction, round 3 (the correctness lens, survivor F): `run_columns` writes its columns in
  `COLUMN_LABELS` order whatever order the run is given. `test_columns_given_out_of_column_order_are_written_in_it`
  runs r2 before r1 and r1 before r2 from one temporary repository and requires the JSON's columns, the report's
  column sections and its provenance rows in `COLUMN_LABELS` order, both files byte-equal to the canonical-order
  run. Probe F1 (the sort dropped) turns it red.
- [x] Review correction, round 3 (the integrity lens, the same survivor F): the card's run command names r2, r1
  and s9 in that order and regenerates the committed JSON (s9, r1, r2) only through that sort, which `--check`,
  following the JSON's order, cannot see. The same test holds it; probes S1 (the order read from the labels as
  given) and T1 (r1 dropped from `COLUMN_LABELS`) turn it red too.
- [x] Review correction, round 3 (survivor N): `reading.rule_applies_to` is held by tests.
  `test_the_reading_applies_its_rule_to_r2_when_the_run_reads_r2` requires `r2` for the one-game r2 run, and
  `test_an_r1_column_reads_under_its_rounds_config` now also requires `None` for the r1-only run. Probes N1 (`not
  in`), N2 (`labels is not None`) and B1 (the branches swapped) turn them red.
- [x] Review correction, round 3 (survivor C): the origin leg's relevance gate is given the regroup ticks.
  `test_a_movement_origin_in_the_regroup_window_is_no_placement` plants a grounded movement into Admin at 12 whose
  origin, West Hall at 11, falls in the window of a regroup at 10 and alone pairs with the arrival: the leg reads
  False as built, True with the regroup ticks dropped, and True with a regroup at 9.
  `test_a_movement_origin_at_the_kill_scene_is_no_placement` isolates the same gate's body rooms. Probe C1 (the
  gate given no regroup ticks), C2 to C5, N3, N4 and F2 turn them red. The neuter-pass claim is corrected: no
  earlier row isolated those two call-site arguments.
- [x] Review correction, round 3 (integration, the card's merge order): `main` at `a0fdb570`, the census card, is
  merged at `bc8d6ff1`, never rebased. The census denominators and the instrument's own census agreement
  (`--check`) re-run there read as before. The `tasks/README.md` inventory sentence is re-derived by
  `scripts/validate_task_docs.py` (96 cards: 3 ready, 93 done), and the `experiments/lab/` row holds at 167 files
  and 6.9 MB on the merged tree.

- [x] Review correction, round 2: a public regroup's room is read from the memory wherever the regroup gathers the
  table. `test_a_regroup_off_the_hub_takes_its_room_from_the_memory` plants Labs at 10 and a regroup to Admin at
  11: the regroup line's ends read Labs then Admin, and it holds a charged placement in Admin at 11 and not one in
  the Cafeteria. `test_a_regroup_from_the_hub_to_another_room_reaches_its_charge` plants the Cafeteria at 10 and a
  regroup to Admin at 11, where only the memory's room makes the line two-roomed, and requires (b) and
  (b-snapshot) to reach the ejection and its charge through the production case reader. Probe C1 (the room read
  replaced with the literal CAFETERIA) turns both red.
- [x] Review correction, round 2: (c)'s unreached reason tests kinds against (c)'s own inputs.
  `test_a_gated_sighting_against_an_alibi_stay_is_given_the_relevance_gate` plants a button meeting where p-1's
  own turn places p-5 in the Cafeteria at tick 1 (the spawn window the relevance gate drops) and p-5 states an
  alibi in Admin from 3 to 5: (c) does not reach, its reason is the relevance gate over both pairs, and (a)'s is
  kind. Probe S1 ((c)'s step read against (a)'s kinds) turns it red.
- [x] Review correction, round 2: the eleven raises the review named carry their real arguments, held by
  whole-message matches with values no likely constant matches: the malformed request's text; git's own detail
  (`fatal: Needed a single revision`) in the unknown-commit and unresolved-path raises; the path and sha of the
  unresolved-path and not-a-directory raises; the label and path of the no-config raise under r2 and under r1
  (`test_a_declared_r1_config_that_is_no_config_names_r1`); the declared path of the settings raise under r2 and
  under r1 (`test_r2s_tree_under_the_r1_label_names_r1s_config`); the sha, path and tree of the tree-mismatch raise
  under r2 and r1; the unknown label; both ledger bounds' names; the walk's own assertion, compared with
  `walk_replay_meetings`' raise on the same flipped copy; and the JSON and report paths of `--check`'s two
  problems. Probes M13 to M28 turn them red.
- [x] Review correction, round 2: the unknown-label guard of `recorded_sources` is held.
  `test_an_unknown_recorded_label_is_refused_by_name` plants a JSON copy with one column labelled r3 and requires
  `--check` to exit 1 with exactly "column 'r3' is not a known column"; neuter X4 (the guard off) turns it red
  with the uncaught `ValueError` the review saw.
- [x] Review correction, round 2: the run scans the JSON it would write.
  `test_a_run_whose_json_would_carry_a_rationale_writes_nothing` patches `serialize` so a recorded rationale
  reaches the JSON alone, and requires the run to exit 1 naming the scan and to write neither file. Neuter X5 (the
  verifier's P9: the run scans the report only) turns it red.
- [x] Review correction, round 2 (the integrity lens): the lab row's byte total after review round 1 is 7,192,265
  bytes over 167 files, not 7,192,231; Decisions now states it with its command (`git ls-tree -r -l 01dc8a9f --
  experiments/lab experiments/model_probe | awk '{n++; s+=$4} END {print n, s}'` prints `167 7192265`).
- [x] Review correction, round 2 (the documentation lens): the same figure reproduces with that command at
  `17aab62d` and `01dc8a9f`, beside `164 6591637` at `5877adb4` and `167 7189659` at `8b18aa53`; at `200e2a32`,
  this round's code commit, it prints `167 7195798`. The row's 6.9 MB and 167 files hold at every one.
- [x] Review correction, round 2 (Codex P2, valid): the census's tick is compared with the walk's. `read_game`
  raises when a census meeting's tick differs from the walked meeting's entry tick;
  `test_a_later_meeting_the_census_reads_differently_is_named[tick-1]` moves seed 1's third meeting by one tick
  and requires exactly "r1 seed 1 meeting 2: the census and the walk read different meetings". Neuter X1 and probe
  N1 turn it red. No committed count moved: the regenerated run walks all 386 meetings with the comparison on.
- [x] Review correction, round 2 (Codex P2, valid): the report states each column's seeds and roster as its
  recorded games hold them, never a fixed "seeds 0-49 at 9 players and 2 impostors". `seed_ranges` and
  `column_roster` write `seeds` and `roster` into each JSON column, and the report's provenance table prints them;
  a column whose games hold more than one roster raises. Tests: `test_seeds_are_stated_as_runs`,
  `test_no_seed_at_all_raises`, `test_a_columns_roster_is_its_games_own`,
  `test_a_columns_seeds_are_every_recorded_game_not_only_those_with_a_meeting`,
  `test_a_run_states_its_columns_own_seeds_and_roster` (the one-game run reads seed 2, and its report holds no
  0-49) and `test_the_report_states_the_seeds_and_roster_the_json_records`. Probes N3 to N5, B1, F1, F2, C2, S2, L1
  to L3 and neuters X6 to X13 turn them red. The six-game checkpoint the review ran (`9725ece0`) now reads seeds
  0-5 over 6 games.
- [x] Review correction, round 2 (Codex P2 of the first review, valid, unanswered in round 1): `--check` refuses a
  recorded sha that is not a commit's full sha. `test_a_recorded_sha_that_is_no_full_commit_sha_fails_check`
  [HEAD, short] records the very commit the run read under `HEAD` and under a 12-character abbreviation, with its
  tree unchanged, and requires exit 1 naming the value; the r1 tree-mismatch test does the same under r1. Neuter
  X3 and probes N2, M29 and M30 turn them red.
- [x] Review correction, round 2 (Codex P2 of the first review, valid, unanswered in round 1): the walk raises when
  the manager asks for a recorded call other than exactly once, by the golden's own `consumed_exactly_once`.
  `test_a_recorded_call_asked_for_other_than_once_raises` [a prompt recorded twice and asked once; recorded once
  and asked twice] requires exactly "r1 seed 7 meeting 1: the walk did not ask for each recorded call exactly as
  often as it was recorded"; neuter X2 and probe M31 turn it red. Every meeting of the three columns passes it.
- [x] Review correction: a contradiction flag is a charge only when both of its events place the target.
  `test_a_flag_whose_second_event_places_only_another_player_is_no_charge` plants a flag naming the target whose
  second event places only another player: `charges_against` returns no charge and `read_meeting` counts 0.
  Probe S1 (the flag's events resolved over every player's placements) turns it red.
- [x] Review correction: the raises the review named carry their real arguments: column, seed and meeting in the
  walk and census raises, and the voter, subject, meeting id, seed-set label and s9 figure in theirs. A state-hash flip and a prompt flip after seed 1's second meeting
  (`test_a_state_hash_flipped_after_the_second_meeting_names_the_third`,
  `test_a_prompt_flipped_in_the_third_meeting_names_it`), a planted missed-prompt count
  (`test_a_missed_prompt_count_is_the_meetings_own`), each of the four census fields disagreeing at a later
  meeting (`test_a_later_meeting_the_census_reads_differently_is_named`), and whole-message matches in the s9,
  seed-set, census-length, first-meeting-claim, re-render, shown-pair, input-kind, no-trigger and no-ballot-render
  raises. Probes M1 to M12 turn them red.
- [x] Review correction: the JSON labels (b-snapshot) an approximation. Its top-level `checks` block names every
  check and marks `b_snapshot`, and only it, an approximation of the temporal observation delivery evidence
  version 2 requires; the report reads its check names from that block.
  `test_the_json_labels_b_snapshot_an_approximation` and `test_the_report_names_each_check_as_the_json_does`;
  the JSON and report regenerated by the run, and `--check` exits 0 on them.
- [x] Review correction: the output scan finds recorded text that the JSON's escaping changes. `scan_outputs`
  seeks each text as written and as a JSON string body. `test_a_recorded_text_the_json_escapes_fails_the_scan`
  writes a recorded non-ASCII rationale and a recorded non-ASCII turn text into the JSON and into a report, and
  requires the raise from each. Probe F1 (the earlier scan, as written only) turns it red.
- [x] **Columns with exact provenance.** `uv run python -m experiments.lab.route_check_replay --set
  LABEL=COMMIT:PATH ...` resolves each COMMIT to its full commit sha when the run starts (`git rev-parse
  --verify COMMIT^{commit}`), materializes every column with `git archive SHA PATH` into a temporary directory,
  and records each column's full sha beside its path, tree id and recorded experiment config in the JSON.
  - `--check` takes its columns from the JSON, never from the command line or `HEAD`. It re-archives each
    recorded sha, and before it recomputes anything it refuses a column whose recorded tree id differs from the
    tree of `SHA:PATH`, naming the column.
  - The run refuses: a commit or path that does not resolve; a column whose rows' config differs from the one
    its label declares (r2: the era's declared config; r1: the round's config file; s9: none); and any request
    to pool columns.
  - Mechanism: the materializer and `tests/experiments/test_route_check_replay.py`, which resolves the
    checkout's `HEAD` to its sha or builds temporary repositories, and never reads a column through a symbolic
    ref.
  - Planted: r1's tree under the r2 label, and an unknown commit, each exit non-zero naming the cause. A copy of
    the JSON whose recorded tree id for one column differs from its sha's tree makes `--check` exit 1 naming that
    column. In a temporary repository, a file committed into a column's directory after the run (as
    `rubric-extractor-era` will add `replays/samples/9p2i/results-rubric-score.json`) leaves `--check` green,
    because `--check` reads the recorded sha.
- [x] **A faithful walk, or none.** Every meeting is read through `walk_replay_meetings` with the recording's
  settings. The instrument raises, naming (column, seed, meeting), when a recorded prompt is missed, when a
  state hash differs, and when its meetings per column differ from the census's (`load_census_inputs`). Each
  meeting is counted before the walk resumes, and the live memories are left as they were. Mechanism: the
  integrity checks, and a test comparing each live memory before and after the per-meeting counting. Planted:
  a temporary copy of one r2 game with one byte of a recorded prompt flipped raises; a census fact list with
  one meeting removed raises; a counting step that appends one row to the live store fails the comparison.
- [x] **(a) as the manager builds it.** The instrument calls `build_testimony_ledger` with the firewalled
  sighting mapping, the movement records, the opener, the living roster, the trigger kind and
  `derive_regroup_ticks(recorded, earlier meeting ticks)` (`orchestrator/replay.py:1498-1514`), and shows a
  row to the voters whose `_candidate_targets` (`meetings/manager.py:5472`) hold the subject. Mechanism: a
  parity test drives one recorded r2 game through the walk with the manager's corroboration resolver patched
  ON (a monkeypatch; no environment write), spies the arguments its ledger call receives at a meeting after
  the first, and requires them equal to the instrument's. Perturbed: dropping `regroup_ticks` or the movement
  records from the instrument's call turns the parity test red. Sourced constants, each patched in
  `meetings.corroboration`'s namespace: the tick bound set to 2 reconciles a planted West Hall at t, Admin at
  t+2; with it, the hop bound set to 2 also reconciles planted case 2; the subject cap set to 1 cuts a planted
  three-pair row to one line. So the instrument reads the live rule and holds no copy of it.
- [x] **The dispute settled.** Beside (a) as built, a perturbed leg drops the movement records and regroup ticks
  (the transcript-only probe). Results reports both on r2's innocent ejections, impostor ejections and ejected
  witnesses, names the input that moves each case between the legs, and explains any difference from 12/22,
  17/22, 0/5 or 3/5 case by case. On s9, (a) as built must read 13 of 90 ejections with a walkable pair; a
  different figure stops the card and goes to the orchestrator, and is never adjusted to fit. Mechanism: the
  two legs and the s9 agreement assertion. Perturbed: the assertion with its expected figure moved by one
  fails; Results also states whether the transcript-only leg would pass it on s9.
- [x] **(b) as the recorded field renders it.** For each voter, the instrument calls `v2_evidence_context_rows`
  on a version-2 view of the voter's memory at the meeting's open, deriving the voter's own id and teammates
  as the store does (`_latest_self_guard_fields`, `agents/memory/store.py:1162`). It classifies every travel
  row as fits, cannot reconcile, insufficient timing, crosses the regroup or unverifiable, and raises on a
  travel row it cannot classify. It counts rows offered and, separately, rows that a version-2
  `render_for_prompt` on a deep copy keeps, at the budget the recording's runner gives the ballot re-render
  (`orchestrator/game.py:1788`). It checks that at every first meeting the voters hold no reported claim, and
  raises otherwise. Mechanism: the classifier and an equivalence test: one ingestion sequence into a
  version-None and a version-2 memory yields identical travel rows. Planted: a travel line with an altered
  suffix raises; a claim row injected into a first-meeting memory raises.
- [x] **(b-snapshot), labelled.** The same rows with each plain recorded sighting (built from the pre-action
  state, no action payload) labelled a start-of-tick snapshot; move rows and action-sourced rows stay unknown.
  The report calls it an approximation of temporal delivery, which would also add event rows these bytes lack.
  Mechanism: the relabelling function and its unit test. Planted: relabelling a move row turns that test red.
- [x] **(c), the reference reading.** Its placements are `reconstruct_stated_paths` with the movement records,
  the regroup ticks and `include_kill_scene=True`, plus the stays of alibi routes about the candidate
  (`maximal_stays`, `meetings/transcript.py:991`) at their first and last tick, for every living candidate. A
  pair in two different rooms is reconciled when `1 <= hops <= elapsed` over the whole canonical map
  (`room_hops` bounded by the room count), and a pair whose interval holds a public regroup tick is reconciled
  by the regroup. No `meetings/` or `agents/` code changes. Mechanism: unit tests over the planted cases.
  Planted: dropping the regroup marking turns case 3 red.
- [x] **The planted route cases tell the checks apart.** Each runs through the code paths the walk uses (a
  built transcript for (a) and (c); a built memory on the canonical public map for (b)):

  | case | (a) | (b) unknown phase | (b) snapshot phase | (c) |
  | --- | --- | --- | --- | --- |
  | 1. West Hall at t, Admin at t+1 | reconciled | insufficient timing | fits | reconciled |
  | 2. Admin at t, Cafeteria at t+2 | silent | insufficient timing | fits | reconciled |
  | 2'. Admin at t, Cafeteria at t+3 | silent | fits | fits | reconciled |
  | 3. Labs at 10; regroup to Cafeteria at 11 | silent | crosses the regroup | crosses the regroup | by the regroup |

  In case 3 a meeting closes at tick 10, (a) leaves the charge unanswered, and a sighting inside the regroup
  window is dropped. Mechanism: the four tests. Proof: the four rows are pairwise distinct, so a classifier
  that conflated any two checks fails at least one row.
- [x] **Properties over the map.** Hypothesis, `settings(deadline=None)`, over pairs of distinct canonical rooms
  and ticks away from a regroup: (a) reconciled implies (c) reconciled; (b) fits at unknown phase implies (c)
  reconciled; (b) cannot reconcile at unknown phase implies (c) not reconciled; at snapshot phase, (b) fits
  exactly when (c) reconciles. Mechanism: the properties. Perturbed: (c) with its bound off by one in either
  direction fails at least one of them.
- [x] **The process count, role-blind.** The **universe** is every typed placement of a player spoken at the
  meeting (sightings naming them as subject or company, movement sightings, their whereabouts, the stays of
  alibi routes about them, vent sightings), ungated. A pair in it is **reconcilable** when its rooms differ
  and `1 <= hops <= elapsed` over the whole map, or its interval holds a public regroup tick. A **charge** is
  an EJECT ballot whose `primary_reason_id` cites a turn carrying a typed placement of the target, or a
  contradiction flag naming the target whose events are such placements. A **misjudged case** is an ejection
  carried by a charge whose placement ends a reconcilable pair. Check X **reaches** a case when it shows a line about the ejected player
  over two different rooms that reconciles, fits or crosses the regroup, to at least one voter who cast EJECT
  against them; it **reaches the charge** when that line's pair holds the charged placement.
  Insufficient-timing lines are counted apart, never as reaching. Each unreached case is attributed to the
  first reason in a fixed order: the placement is outside the check's inputs (by kind), the relevance gate,
  the hop bound, the tick bound, the cap, the claim not yet held at ballot time, the phase rule. The JSON
  carries every count per column and meeting kind; the report sets them out by ejection class (innocent,
  impostor, ejected witness) as description only. The committed judgment net (`IMPOSSIBLE_TRANSIT_PATTERN`,
  `scripts/counterfactual_phase21.py:299`) is an informational column, never the reading. Mechanism:
  role-free signatures, and a property that permuting the role map moves only the class columns. Planted: a
  role read inserted into a line computation fails the property.
- [x] **Count-only, no model call.** The JSON and the report carry ids, ticks, room ids, kinds, booleans and
  counts, keyed by (column, seed, meeting). They carry no rendered prompt, memory line, rationale, transcript
  text or seed-band prefix. No provider client is built: the walk's recorded-response stub answers from the
  recording's bytes. Mechanism: a scan test over a one-game run's outputs for any recorded turn text,
  rationale or travel line, and a run with socket connection refused. Planted: a rationale written into the
  JSON fails the scan.
- [x] **The artifacts, pinned.** The instrument writes the report (the decision informed; hypothesis, method,
  result, decision input; the lab's caveat that replayed ballots propagate no game state; each term defined
  where used) and the JSON. `--check` recomputes both from the recorded shas and compares, so it reproduces the
  committed JSON on any later `main`. The `experiments/lab/` row of `docs/artifacts.md` goes from 164 to 167
  files in this card's last commit, after its final merge of `main`: the count `scripts/verify_ml_evidence.py`
  holds against the git index (`_IN_TREE_INVENTORY`, `:2869`). No lab artifact is hash-pinned file by file, so
  nothing else is registered. Mechanism: `--check` and the offline evidence check. Perturbed: one count edited
  in a copy of the JSON makes `--check` exit 1; the row left at 164 fails the inventory leg.
- [x] **The dated reading, by a rule fixed here.** Results ends with "Reading (YYYY-MM-DD)", which applies this
  rule to r2 verbatim and reports s9 and r1 beside it. Let M be r2's misjudged cases, W the ones at witness
  meetings, and R(X) the cases check X reaches.
  1. M empty: name no route arm.
  2. Else, if (b-snapshot) reaches at least half of M, and of W when W is not empty: name
     `evidence_reasoning_version = 2`, conditional on the owner lifting the temporal exclusion it requires,
     with the package cautions; say whether (b) as recorded also reaches them.
  3. Else, if (c) does: name the narrow new field (versioned, default off, set only from the config file, its
     own stamp, one role-blind line per living candidate that never asserts presence or honesty), shaped by
     (c)'s unreached reasons, as a card to write with planted cases and fake and scripted rehearsals before any
     spend.
  4. Else: name no route arm, and state what the unreached cases share.
  The reading authorizes no recording; a round 3 is the owner's spend decision. Mechanism: the rule's inputs
  are JSON fields, and the report prints the branch taken. Perturbed: the rule on a copy of the JSON with every
  R set to 0 takes branch 4.
- [x] **The wave's lessons.** Every production line is enforced by a test that goes red when neutered (a neuter
  pass listed in Results); one bounded mutation pass over the instrument with the listed operator classes only
  (F filter, S swap, N comparison, C constant, M message, T tuple member, B branch swap, L loaded source to
  literal), each survivor killed or argued equivalent; no test weakened; every number in Results measured at
  the head that states it, with its command; guarantees stated at delivered strength; no live-tense sentence
  about older behaviour left in a touched file. Mechanism: Results' neuter and mutation tables. Proof: each
  row names its red test.
- [x] **Every gate, green.** `bash scripts/check.sh` in a clean worktree, run to its end, plus the commands in
  Validation, each with its real exit code in Results. Perturbed: the instrument's tests run against a build
  whose (a) leg ignores regroup ticks exit non-zero.

## Constraints

- **Authorization and spend.** No live provider call, no recorder run, no spend. The instrument builds no
  provider client; the walk's recorded-response stub answers every call from the recording's bytes, and the
  tests run on the fake provider as the suite always does. The untracked `.env` is never read and no
  `AILIBI_*` variable is exported. No rendered prompt, memory line, transcript text or seed-band prefix is
  printed or written.
- **House rules.** The engine stays a pure deterministic tick; no module under `agents/` gains an `engine/`
  import, and `lint-imports` stays green. No module-level mutable state; invalid input raises, with no silent
  fallback. A new invariant check carries a planted or perturbed case. Claims name their enforcing mechanism,
  and every number is reproducible from committed bytes, with its command in Results. One writer per file.
- **No behaviour moves.** No new `AILIBI_*` lever, no environment switch, no new experiment field, no prompt
  registry bump, no template or detector change. Nothing under `engine/`, `agents/`, `meetings/`,
  `observation/`, `orchestrator/`, `llm/`, `training/`, `replays/` or `tests/fixtures/` is written. No recorded
  byte is edited, no history re-scored; the corpus FROZEN line and every ML artifact stay put (offline
  `scripts/verify_ml_evidence.py`, never `--complete`). ML stays held (ruling 12).
- **The owner's direction.** A vote or skip must rest on data the agent holds. Role-correctness is reported and
  never a gate, and nothing here pushes an agent toward the right answer: the instrument is offline and feeds
  nothing back. The meeting layer labels and never rewrites. A check that also reaches impostor ejections is
  reported, not discounted.
- **Why `experiments/lab/` and not `eval/`.** It is a one-off counterfactual on committed bytes for one owner
  decision, which is the lab's charter (`experiments/lab/README.md`: offline labs read committed or history
  bytes and write only reports there). It is not a standing census cell: the census stays a separate report,
  and its new cells are the sibling card's. It imports a test-module walk, which the counterfactual script
  does by recorded ruling but a production `eval/` module should not. Lab modules stay under strict mypy
  (`pyproject.toml`'s exclusion names only listed spikes).
- **History.** The s9 column needs `d41c9006`, and `--check` re-archives every recorded sha, so the full run and
  `--check` run in a full clone. The tests resolve the checkout's `HEAD` to its sha or build temporary
  repositories, so CI's shallow checkout runs them.
- **Sibling cards and merge order.** This card dispatches in parallel with `census-reporter-base-rate` and
  `post-promotion-follow-through` from `main` at the coordination commit that lands the four cards. The three
  merge one at a time: census first, then this card, then the follow-through card (by the owner).
  `rubric-extractor-era` dispatches after the follow-through merge and merges last.
  - It reads `eval/gameplay_census.py` (`load_census_inputs`), `eval/eras.py` and
    `scripts/counterfactual_phase21.py` (`IMPOSSIBLE_TRANSIT_PATTERN`) and writes none of them; they and
    `scripts/publish_gameplay_census.py` are `census-reporter-base-rate`'s. The census card merges first, so this
    card merges `main` after that merge and re-runs its denominator agreement there; Results quotes that run.
  - `docs/artifacts.md`: this card writes only the `experiments/lab/` row (164 to 167), in its last commit after
    merging `main`, then re-runs `scripts/verify_ml_evidence.py` offline. `rubric-extractor-era` is the later
    writer of the same row: it recounts it from 167 to 169 when it merges, after this card. The census and
    follow-through cards write other rows.
  - `tasks/README.md`: the inventory sentence only, re-derived with `scripts/validate_task_docs.py` at this
    card's final merge of `main`, after the census card's.
  - `replays/samples/9p2i/`: `rubric-extractor-era` adds `results-rubric-score.json` there, which gives the
    directory a new tree id. This card reads that directory as its r2 column by the commit sha the JSON records,
    never `HEAD`.
  - `experiments/lab/`: `rubric-extractor-era` adds two `stage-b-r2` JSONs and edits the run line in
    `report-rubric-interestingness.md`; no file is shared with this card.
  - It never writes `tests/scripts/test_refresh_samples.py`.
- **Publication.** Lab artifacts, a lab module, its tests and one registry row: nothing the demo bundle reads
  changes, so the merge publishes nothing new (`pages.yml` rebuilds an identical bundle; the PR shows
  `build_demo_bundle.py --out` at base and head with an empty `diff -rq`). The merge is the orchestrator's.
- **Delivery.** Branch `work/route-check-replay`, one PR into `main` with every section of the PR template,
  merged by merge commit or fast-forward, never squash. Each commit body ends with
  `Card: tasks/work/route-check-replay.md` immediately followed by the exact line
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. Scratch work stays outside the repository.

## Expected scope

- `experiments/lab/route_check_replay.py` (new): the instrument and its CLI.
- `experiments/lab/report-route-check-replay.md` (new): written by the instrument.
- `experiments/lab/results-route-check-replay.json` (new): written by the instrument.
- `tests/experiments/test_route_check_replay.py` (new): planted cases, properties, parity, integrity, scan.
- `docs/artifacts.md`: the `experiments/lab/` row's file count only.
- `tasks/work/route-check-replay.md`: this card's Status and Results.
- `tasks/README.md`: the inventory sentence, as the validator derives it.

Test-side reads of committed sets use `tests/_helpers/committed.py` as it stands; it is not written. A file
outside this list needs a line in Results naming it and why; a file another card of the wave owns is not
touched, and the conflict goes to the orchestrator.

## Record impact

None. No recording is made or changed, no future game behaves differently, no prompt or detector byte moves,
and no evaluation cell, scorecard row or census cell changes. The new lab artifacts are class (b) records in
`experiments/lab/`, counted by the registry row. Measurement: the instrument's JSON and report at the
implementing head, reproduced by `--check`.

## Validation

```sh
git fetch origin && git checkout --detach origin/main && uv sync --frozen   # then branch work/route-check-replay
# the dispatch base is the coordination commit that lands the four cards; it moves nothing under replays/,
# so its trees there are 59bbd1be's
# the run: three columns, never pooled (a full clone, for d41c9006); each column names a commit, never HEAD
uv run python -m experiments.lab.route_check_replay \
  --set r2=59bbd1be:replays/samples/9p2i \
  --set r1=59bbd1be:replays/candidates/stage-b-r1/9p2i \
  --set s9=d41c9006:replays/samples/9p2i \
  --out-report experiments/lab/report-route-check-replay.md \
  --out-json experiments/lab/results-route-check-replay.json
uv run python -m experiments.lab.route_check_replay --check   # the JSON's recorded shas; exit 0
git rev-parse 59bbd1be 59bbd1be:replays/samples/9p2i 59bbd1be:replays/candidates/stage-b-r1/9p2i
git rev-parse d41c9006 d41c9006:replays/samples/9p2i   # the shas and tree ids the JSON records
# the denominators, count-only, each column alone (s9's census runs inside the instrument, on its copy)
uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout
uv run python scripts/publish_gameplay_census.py --set-dir replays/candidates/stage-b-r1/9p2i --json-stdout
# the instrument's tests, then the gates
uv run pytest tests/experiments/test_route_check_replay.py
uv run lint-imports
uv run python scripts/verify_ml_evidence.py   # offline; never --complete
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/build_demo_bundle.py --out <scratch>/base   # at 59bbd1be
uv run python scripts/build_demo_bundle.py --out <scratch>/head && diff -rq <scratch>/base <scratch>/head
bash scripts/check.sh   # clean worktree, run to its end
```

Run each gate to its end, because `set -e` in `check.sh` hides later gates. On macOS the evolution-strategy hash
pin is Linux-only, so gate in a clean worktree and cite CI for it.

## Results

### Delivered (2026-10-02 to 2026-10-03, branch `work/route-check-replay` from `5877adb4`)

Commits: `2ccf7af6` (the instrument, its report and JSON, its tests), `8d65bfad` (the committed-column golden and
the refusal pins), `319a6e36` (r2's declared config read from the era registry; further planted cases),
`0f566756` and `45e109dd` (the planted cases the neuter and mutation passes called for), `8b18aa53` (these
Results and the `docs/artifacts.md` row), `5d227914` (the scan helper reworked after the first gate), then the
Results update the final gate ran on and the gate's commit. Files written: the four new files of the
Expected scope, the `experiments/lab/` row of `docs/artifacts.md`, this card and the `tasks/README.md` inventory
sentence. Nothing under `engine/`, `agents/`, `meetings/`, `observation/`, `orchestrator/`, `llm/`, `training/`,
`replays/` or `tests/fixtures/` was written; no recorded byte, prompt, template, detector or ML artifact moved.

Sections relied on: this card; the diagnosis memo (`tasks/diagnosis-2026-10-02/README.md`) Parts 1.4, 2.2
(amendment 7, the dispute), 3 (card 2) and 4 (item 3); the round-2 record
(`audits/audit-2026-10-01-stage-b-r2.md`) sections 6.4 and 9.6 to 9.8 (the denominators, the before columns and
the two committed walkable-pair cells); `docs/architecture.md` "Determinism and the substrate ladder" (the walk
re-derives every state hash, eras are never pooled, `temporal_observations` stays a default-OFF toggle this card
does not touch) and "Explicit cleanup experiments" (evidence version 2, its temporal prerequisite, and
`evidence_context.py`'s conditional walking feasibility); `docs/experiment-arms.md`; the decision memo's
sections 1 and 7 (the partial-record principle; round 1's rulings).

### The run, at its exact commits

```sh
uv run python -m experiments.lab.route_check_replay \
  --set r2=5877adb4:replays/samples/9p2i \
  --set r1=5877adb4:replays/candidates/stage-b-r1/9p2i \
  --set s9=d41c9006:replays/samples/9p2i \
  --out-report experiments/lab/report-route-check-replay.md \
  --out-json experiments/lab/results-route-check-replay.json
#   route-check replay: wrote ... (43.0 s)                              exit 0
uv run python -m experiments.lab.route_check_replay --check
#   route-check replay: reproduced (43.2 s)                             exit 0
git rev-parse 59bbd1be 59bbd1be:replays/samples/9p2i 59bbd1be:replays/candidates/stage-b-r1/9p2i
#   59bbd1bebe2da9431092287f80f76b5d1977ef31
#   8197dc791afbe432186a5bd8c16e3e16f7dd8477
#   2c0529eb694fc011c836cb564d241101da1957e4
git rev-parse 5877adb4 5877adb4:replays/samples/9p2i 5877adb4:replays/candidates/stage-b-r1/9p2i
#   5877adb48e046042a1e2927675451f896168673a  8197dc79...  2c0529eb...  (the same trees)
git rev-parse d41c9006 d41c9006:replays/samples/9p2i
#   d41c90067a0023d08997231f181cc02deb6461bc  5c12c060e75b026daf643ab8b20e5aaca8de20b0
```

The JSON records those shas and tree ids, and `--check` re-archives them. The r1 and r2 trees at `5877adb4` are
the trees at `59bbd1be` that the card names. Wall time of the full run on this machine: 43 to 56 s across the
runs made (the instrument prints it); `--check` takes the same. The census denominators, run beside it on the
checkout (`publish_gameplay_census.py --set-dir ... --json-stdout`, exit 0 each): r2 117 meetings, 24 with vent
proof (21 report, 3 button), 93 report meetings without proof ejecting 42; r1 124 meetings, 26 with vent proof
(20 report, 6 button), 98 without proof ejecting 28. The instrument's own meeting kinds read the same, and it
re-derives the census per column and checks every meeting one for one (s9's census runs inside it, on its
archived copy): s9 145 meetings (60 report with proof, 75 without, 10 button), r1 124 (20, 98, 6), r2 117 (21, 93,
3); ejections 90, 54 and 66 (innocent 9, 15 and 22); witness meetings 3, 3 and 14. Every count the card asked to
re-measure reads as the card states.

### Acceptance, item by item

Test file: `tests/experiments/test_route_check_replay.py`, 104 tests at delivery (117 after review round 1,
139 after review round 2 and 143 after review round 3, below), `uv run pytest tests/experiments/test_route_check_replay.py -n 6` → 104 passed (exit 0). Each planted case below
is a test that asserts the failure it plants, so a green run is the planted case failing as claimed.

- **Columns with exact provenance.** Mechanism: `resolve_column` (`git rev-parse --verify COMMIT^{commit}`),
  `tree_at`, `materialize` (`git archive SHA -- PATH`), `declared_config` and `require_declared_settings` (the era
  registry's own comparison of canonical recorded settings); `--check` builds its columns from the JSON by
  `recorded_sources`, which refuses an unknown label, a recorded sha that is not a commit's full sha (since review
  round 2) and a tree mismatch before anything is recomputed. Planted:
  `test_r1s_tree_under_the_r2_label_is_refused` (exit 1, "column r2: seed 2 recorded settings that differ from the
  config its label declares"), `test_an_unknown_commit_is_refused` (exit 1, "commit '0123456789abcdef' does not
  resolve"), `test_a_tree_named_as_the_commit_is_refused`, `test_a_recorded_tree_id_that_is_not_the_shas_tree_fails_check`
  (exit 1, "column r2: the recorded tree id ...") and its r1 twin, `test_a_file_committed_into_the_column_after_the_run_leaves_check_green`
  (the `results-rubric-score.json` shape: exit 0) and `test_a_later_commit_that_rewrites_the_column_leaves_check_green`;
  pooling (`test_a_request_to_pool_columns_is_refused`), an unknown label, a malformed request, a file path, a
  path that does not resolve, r2 bytes under the s9 label, a broken declared config, `--set` with `--check`, and a
  moved era config (`test_the_r2_config_is_read_from_the_era_registry`) are refused. The tests resolve the
  checkout's `HEAD` to its sha or build temporary repositories; none reads a column through a symbolic ref.
- **A faithful walk, or none.** Mechanism: `walk_game` (a state hash the walk cannot reproduce, a recorded
  prompt it did not re-render, or, since review round 2, a recorded call the manager asked for other than exactly
  once, raises naming column, seed and meeting), `read_game` (the census's meetings must be the walk's, one for
  one, by id, tick (since review round 2), opener, ejection and trigger), and `require_faithful_rerender` (each voter's
  memory, re-rendered on a deep copy at the default budget with the pre-vote suspicion, must be the whole
  `<memory>` block of its recorded ballot; it held at every one of the 386 meetings of the full run). Planted:
  `test_a_flipped_byte_in_a_recorded_prompt_raises` (two seeds and labels), `test_a_state_hash_the_walk_cannot_reproduce_raises`,
  `test_a_census_with_one_meeting_removed_raises`, `..._one_meeting_more_raises`, `..._no_meeting_for_a_games_first_raises`,
  `test_a_census_that_names_a_different_meeting_raises`, `test_a_census_of_other_seeds_raises`,
  `test_the_rerender_check_pins_the_ballot_budget` (a quarter budget raises). Live memories:
  `test_counting_leaves_every_live_memory_as_it_was` compares every live store's events, working memory, beliefs
  and meeting history before and after each meeting's counting; the planted
  `test_a_counting_step_that_appends_to_a_live_store_fails_the_comparison` fails it.
- **(a) as the manager builds it.** Mechanism: `ledger_call` and `a_readings`, which call the live
  `build_testimony_ledger` and ask the live `_walkable_transits` about each stated pair; voters see a row when
  `_candidate_targets` holds its subject. Parity: `test_the_ledger_call_is_the_managers_own` patches the manager's
  corroboration resolver ON (a monkeypatch, no environment write), spies the manager's ledger call on r2 seed 0,
  and requires the instrument's call equal at all four meetings and different under the three dropped legs at the
  three meetings after the first. Perturbed, edited and restored from a copy: the instrument's `ledger_call` with
  `regroup_ticks=frozenset()` turns the suite red (3 failed, 101 passed: the parity test, case 3, the r2 golden;
  exit 1), and with `move_witness_records` dropped (2 failed, 102 passed: the parity test and the r2 golden; exit
  1). Sourced constants, patched in `meetings.corroboration`: tick bound 2 reconciles West Hall at t, Admin at
  t+2; with it, hop bound 2 reconciles case 2; cap 1 cuts a three-pair row to one line; the unreached-reason
  bounds follow the same namespace (`test_the_unreached_bounds_follow_the_ledgers_namespace`).
- **The dispute settled.** Mechanism: the four ledger legs plus one informational leg, and `s9_agreement`, which
  raises on any figure but 13 of 90. s9 reads 13 of 90 under (a) as built (the transcript-only leg reads 8 of 90 and
  would not pass). Perturbed: `test_the_s9_expectation_moved_by_one_fails` and
  `test_a_different_s9_figure_stops_the_run` (12, 14 of 90 and 13 of 89 raise). The case-by-case account is
  below.
- **(b) as the recorded field renders it.** Mechanism: `b_voter_reading` (a version-2 deep copy, own id and
  teammates from `_latest_self_guard_fields`, `v2_evidence_context_rows`, a version-2 `render_for_prompt` on a
  further copy at the default budget with the voter's pre-vote suspicion), `classify_travel_row` (five classes;
  a walking row must name placements the memory holds), and `require_no_claim_at_first_meeting`. Equivalence:
  `test_a_version_none_and_a_version_2_ingestion_give_identical_travel_rows` (one ingestion sequence of packets,
  a roster, absorbed testimony derived under each version and a regroup yields the same travel rows, six or more).
  Planted: `test_a_travel_row_with_an_altered_suffix_raises` and `test_a_claim_held_at_a_first_meeting_raises`;
  `test_rows_the_budget_sheds_are_offered_but_not_kept` separates offered from kept.
- **(b-snapshot), labelled.** Mechanism: `relabel_plain_sightings`, unit-tested by
  `test_relabelling_marks_plain_sightings_only`; the JSON's `checks` block and the report, which reads its check
  names from that block, name the column an approximation (the block since review round 1), and it
  is never merged into (b)'s. Planted (neuter 77): relabelling move rows too turns that test red.
- **(c), the reference reading.** Mechanism: `c_spots` (`reconstruct_stated_paths` with the movement records, the
  regroup ticks and `include_kill_scene=True`, plus every alibi stay end about a living candidate) and `c_pairs`
  over `reconcilable` (whole-map hops bounded by the room count; the regroup interval). No `meetings/` or
  `agents/` code changed. Planted (neuter 33): dropping the regroup branch turns case 3 red.
- **The planted route cases tell the checks apart.** `test_a_planted_route_case_reads_as_the_card_tabulates`
  [1, 2, 2', 3] reproduces the card's table through the walk's own code paths;
  `test_case_3_drops_the_sighting_inside_the_regroup_window` shows the regroup-window sighting dropped and the
  charge unanswered by (a); `test_the_planted_cases_tell_every_pair_of_checks_apart` proves the four rows and the
  four columns pairwise distinct.
- **Properties over the map.** `test_the_checks_order_by_the_map` (Hypothesis, `settings(deadline=None)`, 80
  examples over distinct canonical rooms and gaps 1 to 8 away from a regroup): (a) implies (c); (b) fits at unknown
  phase implies (c); (b) cannot reconcile implies not (c); (b) fits at snapshot phase exactly when (c). Perturbed:
  `test_a_reference_bound_off_by_one_fails_a_property` (the bound one higher and one lower each fail at least one).
- **The process count, role-blind.** Mechanism: `read_meeting` and `_read_case` take no role; roles reach only
  `class_payload` and, since review round 2, the column's roster (`column_roster` counts each game's players
  and impostors, which a permutation of the role map leaves equal; `seed_ranges` reads only the seeds). `test_permuting_the_roles_moves_only_the_class_columns` (Hypothesis, four role maps) and the
  planted `test_a_role_read_inside_a_line_computation_fails_the_property`. Charges, the universe and the
  misjudged definition: `test_a_charge_rests_on_a_cited_placement_or_a_flag_of_placements`,
  `test_the_universe_is_ungated_and_typed`, `test_charges_are_counted_for_living_targets_only`. The judgment net is
  an informational column.
- **Count-only, no model call.** Mechanism: `scan_outputs`, run before any write, against every recorded turn text,
  ballot rationale and travel row of 16 or more characters the run read (`_SCAN_MIN_LENGTH`; shorter strings are
  ids and room names the outputs carry, so the guarantee holds from that length), each sought as written and, since review round 1, as the JSON
  escapes it. `test_the_outputs_carry_no_recorded_text`, the planted
  `test_a_rationale_written_into_the_json_fails_the_scan` and `..._turn_text_...` (ASCII texts), the planted
  `test_a_recorded_text_the_json_escapes_fails_the_scan` (non-ASCII texts the JSON escapes), `test_a_run_holds_its_outputs_to_every_travel_row_it_read`
  (a report carrying a travel row is refused), `test_a_run_whose_json_would_carry_a_rationale_writes_nothing` (since
  review round 2: a JSON carrying a recorded rationale stops the run, which writes nothing), and `test_a_run_needs_no_network` (`--check` with
  `socket.connect` and `create_connection` refused: exit 0). No provider client is built; the walk's
  recorded-response stub answers every call.
- **The artifacts, pinned.** `--check` reproduces both committed files (exit 0 above);
  `test_one_count_edited_in_a_copy_of_the_json_fails_check` and `test_a_report_that_differs_from_its_recomputation_fails_check`
  (exit 1); `test_the_committed_r2_column_recomputes_from_the_checkouts_bytes` recomputes the committed r2 column
  on any shallow clone; `test_the_committed_report_is_the_committed_jsons_rendering`. The `experiments/lab/` row
  reads 167 files: `uv run python scripts/verify_ml_evidence.py` with the row still at 164 exited 1 ("experiments/lab/:
  docs/artifacts.md promises 164 files, the index tracks 167"), and at 167 exits 0 ("every check passed", 51 OK, 7
  ABSENT as a fresh clone expects); `tests/scripts/test_verify_ml_evidence.py` 86 passed.
- **The dated reading, by a rule fixed here.** Mechanism: `rule_inputs` and `reading_branch` read JSON fields;
  the report prints the branch. `test_the_rule_takes_each_branch`; perturbed:
  `test_the_committed_reading_takes_the_branch_its_rule_inputs_give` sets every R to 0 in a copy of each committed
  column's inputs and reads branch 4.
- **The wave's lessons.** The neuter and mutation tables below; no test was weakened, skipped or deleted; every
  number here was measured at the head that states it, with its command; guarantees are stated at the strength the
  code delivers (see Limitations).
- **Every gate, green.** See Verification.

### The per-column counts (the committed JSON; the report sets them out in full)

| column | meetings | ejections | charges at the table | resting on a reconcilable pair | misjudged | at witness meetings |
| --- | --- | --- | --- | --- | --- | --- |
| s9 | 145 | 90 | 513 | 332 | 50 | 0 |
| r1 | 124 | 54 | 406 | 265 | 29 | 0 |
| r2 | 117 | 66 | 402 | 276 | 40 | 7 |

Misjudged cases each check reaches (reaches the charge in brackets):

| column | (a) as built | (a) transcript only | (b) as recorded | (b-snapshot) | (c) reference |
| --- | --- | --- | --- | --- | --- |
| s9 (of 50) | 13 (12) | 8 (8) | 27 (26) | 30 (27) | 32 (28) |
| r1 (of 29) | 8 (7) | 10 (8) | 8 (7) | 15 (11) | 20 (20) |
| r2 (of 40) | 15 (15) | 13 (9) | 16 (14) | 20 (16) | 29 (28) |

r2 by ejection class, as description (misjudged / reached by a, a transcript only, b, b-snapshot, c): innocent
21 of 22 misjudged, reached 15, 12, 8, 12, 21; impostor 19 of 44, reached 0, 1, 8, 8, 8; ejected witness 5 of 5,
reached 2, 0, 2, 3, 5. r2's unreached misjudged cases by first reason: (a) 18 placement kind (an alibi stay or a
vent sighting at an end), 7 relevance gate; (b) 13 cap or memory budget, 4 claim not yet held, 4 kind, 3 residual;
(c) 9 kind (a vent sighting at an end), 2 relevance gate; every case (c) leaves unreached is an impostor
ejection. At the recorded ballot budget (b) as recorded keeps 2,158 of 28,564 travel rows it offers in r2, and none
of the 4,478 rows that say an interval crosses the regroup: they sort after the walking rows and are shed (r1: 1 of
5,003; s9 has no regroup). Insufficient-timing rows about a misjudged ejected player over two rooms, shown to a
voter who voted to eject: (b) 115, (b-snapshot) 49 in r2.

### The dispute, case by case (r2)

Ejections with a walkable pair under each leg (the JSON's `classes.counts`): as built innocent 15 of 22, impostor
0 of 44, ejected witnesses 2 of 5; transcript only 12 of 22, 1 of 44, 0 of 5, which is the earlier probe's 12/22,
1/44 and 0/5 exactly. What moves each case between the two legs (`moved by`, from the single-input legs):

- seeds 2 m0, 28 m0 (witness), 43 m0 (witness) and 45 m1 gain a pair from the movement records alone (a confirmed
  movement places its subject at the destination);
- seed 21 m1 (innocent) and seed 16 m1 (impostor) lose their pair to the regroup ticks alone (a sighting inside the
  regroup window is no placement).

So 12 + 4 − 1 = 15 innocent, 0 + 2 = 2 witnesses, 1 − 1 = 0 impostors. The refuter's 17 of 22 and 3 of 5 differ
from as built by exactly two committed cases: seed 29 m0 (witness) has a pair only when a spoken movement
sighting's origin is also placed one tick earlier (the informational `a_with_movement_origins` leg; the live clause
deliberately places the destination alone), and seed 21 m1 has one only without the regroup window (the
`a_no_regroup` leg). As built plus those two is 17 of 22 and 3 of 5; that is the reading of the refuter's figure,
whose script is not committed. The origin leg alone reads 16 of 22, 4 of 44 and 3 of 5. The claim of the diagnosis
amendment 7 is settled at this strength: (a) as built shows a walkable pair for 15 of 22 innocent ejections and
2 of 5 ejected witnesses (28 m0 and 43 m0); 29 m0, 30 m1 (the regroup relocation) and 35 m0 are beyond it.

### Neuter pass

`experiments/lab/route_check_replay.py`, every production line and row, and the call-site arguments its rows
name, switched off in turn (review round 3 found that no row isolated the origin leg's relevance-gate arguments,
`regroup_ticks` and `triggering_body_rooms`; its subsection adds them) on a copy-backed working file (`<harness> neuter_probes.py`, scratch, not committed): apply the edit, run
`pytest tests/experiments/test_route_check_replay.py -x -n 6 -k 'not recomputes_from_the_checkouts'`, then the r2
golden alone if that stage stayed green, restore the module from its byte copy. 171 probes. A first attempt
(stopped and restored to rebuild the harness in two stages) came back green on probes 4 and 11; both were killed
before the counted run. The counted run: 142 red, 28 green, one probe string re-anchored (12 as 172). Each green
was killed by a planted test written for it and re-run red, except probe 56, argued equivalent. Final: 170 red, 1
equivalent.

| # | neutered | first run | final | red test |
| --- | --- | --- | --- | --- |
| 1 | parse: drop the malformed-request guard | RED | RED | a_malformed_column_request_is_refused[r2=abc] |
| 2 | parse: keep a trailing slash | RED | RED | a_column_path_is_recorded_without_a_trailing_slash |
| 3 | _git: ignore a failing return code | RED | RED | a_path_that_does_not_resolve_is_refused |
| 4 | resolve_commit: drop ^{commit} | GREEN (aborted run) | RED | a_tree_named_as_the_commit_is_refused |
| 5 | resolve_commit: rewrap error dropped | RED | RED | an_unknown_commit_is_refused |
| 6 | tree_at: drop the directory check | RED | RED | a_path_that_names_a_file_is_refused |
| 7 | tree_at: rewrap error dropped | RED | RED | a_path_that_does_not_resolve_is_refused |
| 8 | resolve_column: drop the label guard | RED | RED | an_unknown_label_is_refused |
| 9 | resolve_column: record the commit as given in the sha slot | RED | RED | the_checkouts_head_resolves_to_its_full_sha_and_tree |
| 10 | resolve_column: record the commit field as the sha | RED | RED | the_checkouts_head_resolves_to_its_full_sha_and_tree |
| 11 | materialize: archive HEAD instead of the sha | GREEN (aborted run) | RED | a_later_commit_that_rewrites_the_column_leaves_check_green |
| 13 | declared_config: skip validation | RED | RED | a_declared_config_that_is_no_config_is_refused |
| 14 | require_declared_settings: never refuse | RED | RED | r1s_tree_under_the_r2_label_is_refused |
| 15 | require_declared_settings: expect nothing for a declared config | RED | RED | one_game_run fixture (errors) |
| 16 | declared path: r1 declares no config | GREEN | RED | an_r1_column_reads_under_its_rounds_config |
| 17 | declared path: r2 declares no config | RED | RED | the_r2_config_is_read_from_the_era_registry |
| 18 | alibi stays: drop the non-spatial filter | GREEN | RED | the_universe_is_ungated_and_typed |
| 19 | alibi stays: first tick only | RED | RED | the_universe_is_ungated_and_typed |
| 20 | universe: drop sightings' subject | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 21 | universe: drop company | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 22 | universe: company includes the subject | GREEN | RED | the_universe_is_ungated_and_typed |
| 23 | universe: drop movement sightings | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 24 | universe: movement placed at its origin | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 25 | universe: drop whereabouts | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 26 | universe: drop vent sightings | RED | RED | the_universe_is_ungated_and_typed |
| 27 | universe: drop alibi stays | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 28 | universe: drop the non-spatial sighting filter | RED | RED | the_universe_is_ungated_and_typed |
| 29 | placements_of: every player's | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 30 | reconcilable: drop the order guard | GREEN | RED | a_pair_out_of_tick_order_is_refused |
| 31 | reconcilable: same room reconciles | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 32 | reconcilable: drop the walk branch | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[1] |
| 33 | reconcilable: drop the regroup branch | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[3] |
| 34 | reconcilable: hop search bounded at one | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[2] |
| 35 | charges: any target's ballots | RED | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 36 | charges: ballots need no cited placement | RED | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 37 | charges: drop ballot charges | RED | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 38 | charges: flags naming anyone | GREEN | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 39 | charges: any event suffices | RED | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 40 | charges: drop flag charges | RED | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 41 | misjudging: no charged end required | RED | RED | a_charge_rests_on_a_cited_placement_or_a_flag_of_placements |
| 42 | misjudging: later end only | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 43 | meeting_inputs: drop the trigger guard | RED | RED | a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises |
| 44 | meeting_inputs: drop the ballot render guard | RED | RED | a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises |
| 45 | meeting_inputs: no suspicion override | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 46 | meeting_inputs: renders of any kind | RED | RED | a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises |
| 47 | meeting_inputs: renders of any voter | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 48 | meeting_inputs: unfirewalled sightings | RED | RED | the_ledger_call_is_the_managers_own |
| 49 | meeting_inputs: no movement records | RED | RED | the_ledger_call_is_the_managers_own |
| 50 | meeting_inputs: first meeting never | GREEN | RED | the_first_meeting_is_marked_and_a_later_one_is_not |
| 51 | meeting_inputs: opener from the transcript's first speaker set to ejected | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 52 | ledger build: drop regroup ticks | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 53 | ledger build: drop movement records | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 54 | ledger build: drop the roster | GREEN | RED | a_subject_outside_the_roster_gets_no_row |
| 55 | ledger build: drop the trigger kind | GREEN | RED | a_button_meetings_opening_body_is_no_kill_scene |
| 56 | ledger build: no contradictions | GREEN | GREEN | equivalent: the walkable clause reads no contradiction (the ledger's rows and walkable pairs are built from the transcript and the paths) |
| 57 | stated_paths: drop movement records | RED | RED | a_census_with_one_meeting_more_raises |
| 58 | stated_paths: drop regroup ticks | RED | RED | case_3_drops_the_sighting_inside_the_regroup_window |
| 59 | ledger_call: never drop movement | RED | RED | the_ledger_call_is_the_managers_own |
| 60 | ledger_call: never drop regroup | RED | RED | the_ledger_call_is_the_managers_own |
| 61 | A_LEG_DROPS: transcript-only drops only movement | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 62 | A_LEG_DROPS: no-regroup drops nothing | RED | RED | the_ledger_call_is_the_managers_own |
| 63 | a_readings: drop the shown-subset guard | GREEN | RED | a_shown_pair_resting_on_no_stated_pair_raises |
| 64 | a_readings: shown pairs are every qualifying pair | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 65 | origins: drop the relevance gate | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 66 | origins: any subject's movement | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 67 | origins: origin at the arrival tick | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 68 | origins: add nothing | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 69 | shown lines: a voter also sees themself | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 70 | c_spots: kill scene excluded | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 71 | c_spots: no movement records | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 72 | c_spots: no regroup ticks | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 73 | c_spots: drop alibi stays | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[3] |
| 74 | c_spots: stays of anyone | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 75 | c_pairs: drop the reconcile filter | RED | RED | the_checks_order_by_the_map |
| 76 | two_rooms: any rooms | GREEN | RED | a_one_room_line_neither_reaches_nor_counts_two_rooms |
| 77 | relabel: relabel move rows too | RED | RED | relabelling_marks_plain_sightings_only |
| 78 | relabel: relabel action rows too | RED | RED | relabelling_marks_plain_sightings_only |
| 79 | relabel: relabel nothing | RED | RED | relabelling_marks_plain_sightings_only |
| 80 | version_2_view: keep version None | RED | RED | rows_the_budget_sheds_are_offered_but_not_kept |
| 81 | version_2_view: never relabel | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[1] |
| 82 | held_rooms: drop regroups | GREEN | RED | a_regroup_lines_ends_take_their_rooms_from_the_memory |
| 83 | held_rooms: drop claims | RED | RED | the_context_reads_claims_of_exactly_the_three_kinds |
| 84 | held_rooms: move rows by origin | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 85 | held_rooms: any player's sightings | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 86 | classify: unknown verdict passes as fits | RED | RED | a_travel_row_with_an_altered_suffix_raises |
| 87 | classify: drop the held-placement check | RED | RED | a_travel_row_with_an_altered_suffix_raises |
| 88 | classify: regroup ends hold no rooms | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 89 | classify: an unmatched row passes as unverifiable | RED | RED | a_travel_row_with_an_altered_suffix_raises |
| 90 | _WALK_VERDICTS: insufficient read as fits | RED | RED | each_travel_row_shape_is_classified |
| 91 | b_voter_reading: every row kept | RED | RED | rows_the_budget_sheds_are_offered_but_not_kept |
| 92 | b_voter_reading: no suspicion override | GREEN | RED | the_b_render_takes_the_voters_pre_vote_suspicion |
| 93 | b_voter_reading: rows of every kind | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 94 | b_voter_reading: no own id | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 95 | b_voter_reading: no teammates | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 96 | first-meeting claim check off | RED | RED | a_claim_held_at_a_first_meeting_raises |
| 97 | rerender check off | RED | RED | the_rerender_check_pins_the_ballot_budget |
| 98 | rerender check without the override | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 99 | a reason: drop the kind step | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 100 | a reason: drop the relevance step | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 101 | a reason: drop the hop step | RED | RED | the_unreached_bounds_follow_the_ledgers_namespace |
| 102 | a reason: drop the tick step | RED | RED | the_unreached_bounds_follow_the_ledgers_namespace |
| 103 | a reason: drop the cap step | GREEN | RED | a_qualifying_pair_the_cap_cuts_is_given_the_cap |
| 104 | c reason: drop the kind step | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 105 | c reason: drop the relevance step | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 106 | b reason: drop the kind step | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 107 | b reason: drop the cap step | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 108 | b reason: drop the phase step | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 109 | reaching: shed lines reach | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 110 | reaching: one-room lines reach | GREEN | RED | a_one_room_line_neither_reaches_nor_counts_two_rooms |
| 111 | reaching: insufficient lines reach | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 112 | holds charge (b): tick ignored | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 113 | case reason: last instead of first | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 114 | check case: reason even when reached | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 115 | input-kind guard off | GREEN | RED | an_input_of_a_kind_the_check_is_not_read_to_take_raises |
| 116 | read_meeting: no first-meeting check call | GREEN | RED | reading_a_meeting_checks_the_first_meetings_claims_first |
| 117 | read_meeting: no rerender check call | RED | RED | the_rerender_check_pins_the_ballot_budget |
| 118 | read_meeting: targets from ballots only | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 119 | read_meeting: charges resting never counted | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 120 | read_meeting: b snapshot never | RED | RED | an_unchanged_copy_of_a_game_reads_cleanly |
| 121 | read_meeting: (b) lines count offered | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 122 | read_meeting: (c) lines per pair | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 123 | read_meeting: no travel texts for the scan | RED | RED | the_outputs_carry_no_recorded_text |
| 124 | case: eject voters of any target | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 125 | case: (a) reaches without a voter | GREEN | RED | a_line_reaches_only_a_voter_who_voted_to_eject |
| 126 | case: (a) reaches the charge whatever | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 127 | case: (b) voters are every voter | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 128 | case: (b) lines about anyone | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 129 | case: (b) insufficient lines need no two rooms | GREEN | RED | an_insufficient_line_counts_only_over_two_rooms |
| 130 | case: (c) reaches the charge whatever | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 131 | case: reporter regardless of trigger | GREEN | RED | a_button_meetings_ejected_opener_is_no_reporter |
| 132 | case: pit net over any ballot | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 133 | case: origin leg always false | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 134 | meeting_kind: proof among the dead too | GREEN | RED | vent_proof_names_a_living_player_and_a_witness_reports |
| 135 | meeting_kind: buttons read as reports | RED | RED | meeting_kinds_agree_with_the_census_vent_proof_cells |
| 136 | witness: any trigger | GREEN | RED | vent_proof_names_a_living_player_and_a_witness_reports |
| 137 | witness: no floor | RED | RED | witness_meetings_read_the_kill_facts_since_the_previous_meeting |
| 138 | witness: kills after the meeting | RED | RED | witness_meetings_read_the_kill_facts_since_the_previous_meeting |
| 139 | walk: swallow a state-hash failure | RED | RED | a_state_hash_the_walk_cannot_reproduce_raises |
| 140 | walk: never check missed prompts | RED | RED | a_flipped_byte_in_a_recorded_prompt_raises[1-r2] |
| 141 | read_game: drop the census-short guard | RED | RED | a_census_with_one_meeting_removed_raises |
| 142 | read_game: drop the meeting identity check | GREEN | RED | a_census_that_names_a_different_meeting_raises |
| 143 | read_game: drop the census-long guard | RED | RED | a_census_with_one_meeting_more_raises |
| 144 | read_game: no regroup ticks | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 145 | read_game: earlier ticks never grow | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 146 | read_game: previous tick never passed | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 147 | read_set: drop the seed guard | GREEN | RED | a_census_of_other_seeds_raises |
| 148 | forbidden: no rationales | RED | RED | the_outputs_carry_no_recorded_text |
| 149 | forbidden: no turn texts | GREEN | RED | the_outputs_carry_no_recorded_text |
| 150 | scan: never raise | RED | RED | a_rationale_written_into_the_json_fails_the_scan |
| 151 | half: strict majority | RED | RED | the_rule_takes_each_branch |
| 152 | rule: drop the M-empty branch | RED | RED | the_rule_takes_each_branch |
| 153 | rule: ignore W | RED | RED | the_rule_takes_each_branch |
| 154 | rule: (c) before (b-snapshot) | RED | RED | the_committed_reading_takes_the_branch_its_rule_inputs_give |
| 155 | s9: never raise | RED | RED | a_different_s9_figure_stops_the_run[found0] |
| 156 | s9 agreement only for s9: for every label | RED | RED | one_game_run fixture (errors) |
| 157 | classes: witnesses are not innocent | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 158 | moved_by: never | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 159 | run: allow pooling | RED | RED | a_request_to_pool_columns_is_refused |
| 160 | run: no settings check | RED | RED | r2s_tree_under_the_s9_label_is_refused |
| 161 | run: no travel rows in the scan | GREEN | RED | a_rationale_written_into_the_json_fails_the_scan |
| 162 | outputs: no scan | GREEN | RED | a_run_holds_its_outputs_to_every_travel_row_it_read |
| 163 | check: no tree check | RED | RED | a_recorded_tree_id_that_is_not_the_shas_tree_fails_check |
| 164 | check: no JSON comparison | RED | RED | one_count_edited_in_a_copy_of_the_json_fails_check |
| 165 | check: no report comparison | GREEN | RED | a_report_that_differs_from_its_recomputation_fails_check |
| 166 | main: --check accepts --set | RED | RED | check_takes_no_columns_from_the_command_line |
| 167 | main: --check problems exit 0 | RED | RED | one_count_edited_in_a_copy_of_the_json_fails_check |
| 168 | main: errors exit 0 | RED | RED | an_unknown_label_is_refused |
| 169 | ledger bound: no integer guard | RED | RED | a_ledger_bound_that_is_no_integer_raises |
| 170 | group counts: misjudged at witness not counted | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 171 | declared path: s9 declares r1's config | RED | RED | r2s_tree_under_the_s9_label_is_refused |
| 172 | declared_config: no config for any label | - | RED | a_file_committed_into_the_column_after_the_run_leaves_check_green |

### Mutation pass

One bounded pass over the instrument with exactly the classes F, S, N, C, M, T, B and L, 39 mutants, the same
harness. First run: 31 red, 8 survivors; 5 survivors killed by planted tests and re-run red, 3 argued equivalent.

| # | mutant | first run | final | red test or reason |
| --- | --- | --- | --- | --- |
| 1 | F: c_spots keeps stays of dead speakers' subjects (drop the roster filter) | GREEN | equivalent | equivalent: (c) reads only each roster candidate's own stays, so a stay of a player outside the roster is never read |
| 2 | F: flag subjects outside the roster become targets | GREEN | RED | charges_are_counted_for_living_targets_only |
| 3 | F: movement-record mapping keeps empty records | RED | RED | the_ledger_call_is_the_managers_own |
| 4 | F: forbidden strings keep short texts | GREEN | equivalent | equivalent: the scan skips texts under the same length itself |
| 5 | F: (b) case lines keep shed rows (drop the kept filter on insufficient lines) | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 6 | S: ballot charges cite placements of any player | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 7 | S: (b) case reads the other view | RED | RED | an_insufficient_line_counts_only_over_two_rooms |
| 8 | S: (a) reasons use (c)'s input kinds | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 9 | S: (b) reasons use (a)'s input kinds | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 11 | N: same-room test inverted | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[1] |
| 12 | N: (a) reaches when there is no row | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 13 | N: (b) charge test inverted on ends | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 14 | N: line-over test inverted on ends | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 15 | N: walk test inverted | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[1] |
| 16 | N: regroup interval inverted | RED | RED | a_planted_route_case_reads_as_the_card_tabulates[3] |
| 17 | C: sighting tick read as 0 | RED | RED | the_hop_search_is_bounded_by_the_room_count |
| 18 | C: alibi stay room read as the Cafeteria | RED | RED | the_universe_is_ungated_and_typed |
| 19 | C: ejected role read as crewmate | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 20 | C: trigger kind read as report | RED | RED | a_button_meetings_ejected_opener_is_no_reporter |
| 21 | C: movement kind read as a sighting | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 22 | C: kill tick read as the meeting tick | RED | RED | witness_meetings_read_the_kill_facts_since_the_previous_meeting |
| 23 | C: regroup tick read as 0 in held rooms | RED | RED | a_regroup_lines_ends_take_their_rooms_from_the_memory |
| 24 | M: walk failure names a constant label | RED | RED | a_flipped_byte_in_a_recorded_prompt_raises[2-r1] |
| 25 | M: walk failure names a constant seed | RED | RED | a_flipped_byte_in_a_recorded_prompt_raises[2-r1] |
| 26 | M: tree mismatch names a constant column | GREEN | RED | an_r1_columns_tree_mismatch_names_r1 |
| 27 | M: settings refusal names a constant column | GREEN | RED | r2s_tree_under_the_s9_label_is_refused |
| 28 | M: census-short failure names a constant meeting | GREEN | RED | a_census_with_no_meeting_for_a_games_first_raises |
| 29 | T: travel rows without the contradicted kind | RED | RED | each_travel_row_shape_is_classified |
| 30 | T: (a) inputs without company | RED | RED | a_file_committed_into_the_column_after_the_run_leaves_check_green |
| 31 | T: (b) claims without whereabouts | RED | RED | the_context_reads_claims_of_exactly_the_three_kinds |
| 32 | T: held rooms read no alibi claims | RED | RED | the_context_reads_claims_of_exactly_the_three_kinds |
| 33 | T: reaching verdicts without the regroup | GREEN | RED | a_regroup_lines_ends_take_their_rooms_from_the_memory |
| 34 | B: walk and regroup branches swapped | RED | RED | a_pair_the_map_reconciles_reads_as_a_walk_across_a_regroup |
| 35 | B: vent-proof kinds swapped | RED | RED | meeting_kinds_agree_with_the_census_vent_proof_cells |
| 36 | B: moved-by movement and regroup branches swapped | GREEN | equivalent | equivalent: the branch for both inputs runs first, so at most one of the swapped branches can hold |
| 37 | B: b reason cap and phase swapped | RED | RED | the_committed_r2_column_recomputes_from_the_checkouts_bytes |
| 38 | L: room-count bound as the literal 10 | RED | RED | the_hop_search_is_bounded_by_the_room_count |
| 39 | L: ledger tick bound as the literal 1 | RED | RED | the_unreached_bounds_follow_the_ledgers_namespace |
| 40 | L: r2's declared config as the literal path | RED | RED | the_r2_config_is_read_from_the_era_registry |

### Decisions

- **Orchestrator ruling 1 (2026-10-02).** Each column is pinned to a resolved full commit sha recorded in the JSON:
  s9 at `d41c9006`, r1 and r2 at the dispatch base `5877adb4` (nothing under `replays/` moved since `59bbd1be`; the
  tree ids above show it); `--check` re-materializes the recorded sha, with the planted mismatched-tree and
  later-file cases.
- **Orchestrator ruling 2.** The dated reading is advisory; its threshold is the card's recommendation rule and
  gates nothing; the owner decides on a round 3 and which check; `evidence_reasoning_version = 2` would be named only
  conditionally on lifting the temporal-observations exclusion.
- **Orchestrator ruling 3.** The instrument reads recordings through the committed walk with no provider (the
  recorded-response stub), prints no transcript text or prompt, keys every count by (column, seed, meeting), and
  leaves `agents/` free of `engine/` imports (`lint-imports`: 4 kept, 0 broken).
- **Orchestrator ruling 4.** (a) is built exactly as the manager builds it (the parity test) and (b) exactly as the
  store renders it (the equivalence test and the per-voter re-render check), each with its planted case.
- **Orchestrator ruling 5.** (b-snapshot) relabels plain sightings only, is labelled an approximation in the report
  and the JSON (the JSON's `checks` block, added in review round 1, which the report reads), and is a column of
  its own.
- **"Ends a reconcilable pair"** is read as "is one end of": a charged placement may be either end. A same-room
  pair is no move, so the regroup branch, like the walk, needs two different rooms. A regroup lies inside an
  interval when `earlier < tick <= later`, the evidence context's own test. When a pair both walks and crosses a
  regroup, it reads as a walk (`test_a_pair_the_map_reconciles_reads_as_a_walk_across_a_regroup`).
- **A flag is a charge** when it names the target and every event resolves to a typed placement of the target; an
  alibi event stands for every stay end of its claim. Charges are counted for every living target at the table;
  misjudged cases only at ejections.
- **Reaching uses kept rows** for (b): a row the ballot budget sheds is offered but not shown. For a crosses-the-regroup
  row, whose text names no rooms, each end takes the rooms the memory places the subject in at that tick
  (`held_rooms`); a walking row's rooms must be among them, which checks that recovery on every walking row.
- **Unreached reasons:** each misjudged pair takes the first reason in the card's order that applies to it, and the
  case takes the first reason in that order among its pairs; the JSON also carries every pair's reason. (b) adds
  "residual" for a held pair over which no row was offered (it pairs only adjacent placements).
- **The informational `a_with_movement_origins` leg** was added to explain the refuter's 3 of 5 from committed code;
  it is no check and enters no reading.
- **r2's declared config is read from the era registry at call time** (`declared_config_path`), so a moved era
  file moves the run (a planted case), rather than a copy frozen at import.
- **The `docs/artifacts.md` row** also states the row's tracked size, 6.9 MB (7,189,659 bytes across 167 files at
  delivery, `8b18aa53`; 7,192,265 after review round 1, `01dc8a9f`, corrected in review round 2 from a mistyped
  7,192,231; 7,195,798 after review round 2's code commit, `200e2a32`, and at the merge of `main`, `bc8d6ff1`;
  7,196,210 after review round 3's code commit, `400361d3`; 6.3 MB was 6,591,637 bytes over 164 files
  before, `5877adb4`), so the row stays true; the count is what `verify_ml_evidence.py` holds. Each figure is
  `git ls-tree -r -l <commit> -- experiments/lab experiments/model_probe | awk '{n++; s+=$4} END {print n, s}'`.

### Verification

Each command ran alone, its exit code captured directly (no pipe), on this branch at `45e109dd` plus the
`docs/artifacts.md` row of the Results commit; no frontend file changed, so the frontend suite and the browser
journeys were not required.

| command | exit | result |
| --- | --- | --- |
| `uv run pytest tests/experiments/test_route_check_replay.py -n 6` | 0 | 104 passed |
| `uv run python -m experiments.lab.route_check_replay --check` | 0 | reproduced (43.2 s) |
| `bash scripts/verify_samples.sh replays/<set>` for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout` and `--set-dir replays/candidates/stage-b-r1/9p2i` | 0 each | the denominators quoted above |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed: 51 OK, 7 ABSENT, 5 INFO |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -n 6` | 0 | 86 passed |
| `uv run python scripts/check_doc_facts.py` | 0 | every fact verified |
| `uv run python scripts/validate_task_docs.py` | 0 | (re-run in the gate commit) |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run pytest -m campaign` | 0 | 337 passed, 10,172 deselected |
| `build_demo_bundle.py --out <scratch>/base` at `5877adb4`, then `--out <scratch>/head` at this branch, one checkout; `diff -rq` | 0, 0, 0 | no difference across 109 files: nothing publishes |

The first full gate, `bash scripts/check.sh` at `8b18aa53`, exited 1 (624 s): 10,148 passed, 20 skipped, 3 xfailed and 1 failed, `tests/_helpers/test_committed_single_home.py::test_every_committed_walk_goes_through_the_shared_cache`, which flagged the scan helper's census walk over a column read from a committed path. `5d227914` reworks the helper to walk nothing itself (the scan probes 148 to 162 re-run red against it). **The final gate, `bash scripts/check.sh` at `14eb297f` in this clean worktree, run to its end: exit 0 (927 s)**: ruff check and format, import contracts 4 kept and 0 broken, task docs (390 phase tasks, 96 work cards), prompt sync, strict mypy over 524 sources, pytest 10,149 passed, 20 skipped and 3 xfailed, and the frontend lint, type check, 649 tests in 25 files and production build. This commit changes only this card and the derived `tasks/README.md` sentence; `scripts/validate_task_docs.py` re-runs on it (exit 0). The evolution-strategy hash pin, Linux-only by its own note, did not fail here; the PR's CI carries the Linux run.

### Limitations

- Replayed meetings carry no consequence forward: the counts are per meeting and never a re-simulated outcome.
- (b) is read on recordings made with legacy delivery: the version-2 view flips the field on memories recorded
  without it, and the equivalence test proves the travel rows match for the same ingestion; a temporal-ON
  recording would also hold event rows these bytes lack, which (b-snapshot) only approximates.
- The process count is generous by construction: it counts any charge whose placement ends any reconcilable pair,
  with no reading of what the charge said; the judgment net is reported beside it and is not specific.
- (c) is a reading computed here, not a rendered field; whether the 27B would change a ballot on any line was not
  measured and cannot be offline.
- The refuter's own script is uncommitted; its 17 of 22 is explained by two committed legs, not reproduced by one.
- The full run and `--check` need history (`d41c9006`); CI's shallow clone runs the tests, which recompute r2 from
  the working tree.
- The census card (`census-reporter-base-rate`) had not merged when this card was delivered (`origin/main` was
  `5877adb4`), so the denominator agreement above first ran there. Done in review round 3: the census card
  merged at `a0fdb570`, this branch merged it at `bc8d6ff1`, and the agreement ran again on the merged tree with
  every figure unchanged (round 3, item 4).

### Deviations

- `docs/artifacts.md`: the row's size moved with its count (Decisions). The row lands in the Results commit, before
  the final gate, and the last commit records only the gate (the gate needs the row to pass).
- The card's Validation names `59bbd1be` for r1 and r2; the run names `5877adb4` (ruling 1), whose trees are equal.

### Review corrections, round 1 (2026-10-03)

Review round 1 of PR 499 returned four blocking findings. Each is repaired here, and `## Acceptance` opens with
one review-correction item per finding. Commits: `17aab62d` (the JSON's check labels and the scan of escaped text,
with the regenerated JSON), `aa7eab23` (the planted cases), `c6ba6918` (the test module's summary of the outputs),
then the commit adding this subsection and the gate's.
Files written: `experiments/lab/route_check_replay.py`, `experiments/lab/results-route-check-replay.json`,
`tests/experiments/test_route_check_replay.py` and this card, all inside the Expected scope. The report is
byte-identical, no count moved, and `docs/artifacts.md` and `tasks/README.md` need no change (the row's 167 files
and 6.9 MB still hold; Decisions).

1. **A flag's events resolved over every player (correctness).** `charges_against` was right, resolving a
   flag's two events over the target's own placements, but no test held it: resolving them over every player's
   placements passed all 104 tests and `--check`, because no committed flag pairs a placement of its target with
   one of another player. Planted: `test_a_flag_whose_second_event_places_only_another_player_is_no_charge`
   (no charge from `charges_against`, 0 charges from `read_meeting`).
2. **Message arguments set to constants (correctness).** All 11 of the verifier's probes survived. Planted, each
   chosen so that no likely constant matches: a state-hash flip and a prompt flip after the second meeting of r2
   seed 1, read under the label r1, so the raise must read `r1 seed 1 meeting 2: ...`; a walk stub whose second
   meeting misses 2 of its 3 prompts (`r1 seed 7 meeting 1: 2 recorded prompt(s) ...`), because a real flip's
   miss count cascades through the recorded-response stub's fail-soft answer; each of the census's four
   compared fields (meeting id, opener, ejection, trigger) disagreeing at seed 1's third meeting; and whole-message
   matches for the s9 figure (12 of 90, 14 of 90 and 13 of 89), the seed-set raise under r1, the census-length
   raise, the first-meeting-claim and re-render raises naming p-7 (not the first voter in order), the shown-pair
   raise (p-5), the input-kind raise (subject p-5, check (c)), and both meeting-input raises
   (`headless-seed-2:meeting-0`, and the fourth participant's missing ballot render).
3. **The JSON did not label (b-snapshot) (integrity).** `CHECK_LABELS` holds each check's name and, for
   (b-snapshot) alone, what it approximates; `checks_payload` writes them as the JSON's top-level `checks` block
   (`name`, `approximation`, `approximates`), and `render_report` reads its check names from that block, so the
   report's label is the JSON's. The regenerated JSON differs from the one it replaces by that 27-line block
   alone, which is the instrument's own wording and holds no recorded text: the JSON now carries check names
   beside its ids, ticks, rooms, kinds, booleans and counts. `test_the_json_labels_b_snapshot_an_approximation` holds the committed block equal to the instrument's
   and marks `b_snapshot` alone; `test_the_report_names_each_check_as_the_json_does` renames it in a copy and
   requires the report to follow.
4. **The scan missed text the JSON escapes (Codex P2, valid).** `serialize` writes with `json.dumps`' default
   ASCII escaping, so a recorded text with a non-ASCII character could reach the JSON only as escapes, which the
   scan's raw-substring test could not see. Recorded texts of 16 or more characters whose JSON form differs from
   the text: s9 94 of 1,677, r1 103 of 1,535, r2 88 of 1,477, every one by a non-ASCII character. The committed
   JSON held none of them (it holds counts); the defect was that the scan could not have shown it.
   `scan_outputs` now seeks each text as written (the report's form) and as a JSON string body
   (`json.dumps(text)[1:-1]`, the encoder `serialize` uses); the module docstring and the Count-only bullet above
   say so. The regenerated outputs pass the new scan inside the run and inside `--check`. The count, per column
   (r2 shown; r1 with `replays/candidates/stage-b-r1/9p2i`; s9 on `git archive d41c9006 replays/samples/9p2i`
   extracted to a scratch directory), printing scanned, escaped and non-ASCII:

```sh
uv run python -c "import json; from pathlib import Path; import experiments.lab.route_check_replay as r; f = r.forbidden_strings(Path('replays/samples/9p2i')); print(len(f), sum(json.dumps(t)[1:-1] != t for t in f), sum(not t.isascii() for t in f))"
#   1477 88 88   (r1: 1535 103 103; s9: 1677 94 94)
```

**Mutation pass, round 1.** One bounded pass with the listed classes only, over the spans the findings name and
the spans this round changed: 23 mutants. Harness (`probes.py`, scratch, not committed): apply one edit to
`experiments/lab/route_check_replay.py`, run the named tests with `pytest -x -n 4`, and, only if they pass, the
whole file; restore the module from its byte copy, never `git checkout` (its sha1 matched the copy after the run).
First run: 23 red, no survivor. Before this round, at `096b9bf6`, the verifier's run had S1 (their V9) and the
mutants here numbered M1 to M11 green; F1 is the scan as it stood, which the new planted case fails.

| # | mutant | first run | red test |
| --- | --- | --- | --- |
| S1 | S: a flag's events resolved over the whole universe, not the target's own placements | RED | a_flag_whose_second_event_places_only_another_player_is_no_charge |
| M1 | M: the state-hash raise names meeting 0 | RED | a_state_hash_flipped_after_the_second_meeting_names_the_third |
| M2 | M: the missed-prompt raise names meeting 0 | RED | a_missed_prompt_count_is_the_meetings_own (and a_prompt_flipped_in_the_third_meeting_names_it) |
| M3 | M: the missed-prompt count is the constant 1 | RED | a_missed_prompt_count_is_the_meetings_own |
| M4a | M: the s9 raise names 0 for the walkable count found | RED | a_different_s9_figure_stops_the_run[found0] |
| M4b | M: the s9 raise names 0 for the ejections found | RED | a_different_s9_figure_stops_the_run[found1] |
| M5 | M: the first-meeting-claim raise names a constant voter | RED | a_claim_held_at_a_first_meeting_raises |
| M6 | M: the re-render raise names a constant voter | RED | a_rerender_that_is_not_the_ballots_block_names_its_voter |
| M7 | M: the shown-pair raise names a constant subject | RED | a_shown_pair_resting_on_no_stated_pair_raises |
| M8a | M: the input-kind raise names a constant subject | RED | an_input_of_a_kind_the_check_is_not_read_to_take_raises |
| M8b | M: the input-kind raise names a constant check | RED | an_input_of_a_kind_the_check_is_not_read_to_take_raises |
| M9a | M: the no-trigger raise names a constant meeting id | RED | a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises |
| M9b | M: the no-ballot-render raise names a constant meeting id | RED | a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises |
| M9c | M: the no-ballot-render raise names a constant participant | RED | a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises |
| M10 | M: the seed-set raise names a constant label | RED | a_census_of_other_seeds_raises |
| M11a | M: the different-meetings raise names seed 0 | RED | a_later_meeting_the_census_reads_differently_is_named |
| M11b | M: the different-meetings raise names meeting 0 | RED | a_later_meeting_the_census_reads_differently_is_named |
| M11c | M: the different-meetings raise names a constant label | RED | a_later_meeting_the_census_reads_differently_is_named |
| M12 | M: the census-length raise names 0 meetings walked | RED | a_census_with_one_meeting_more_raises |
| F1 | F: the scan drops the JSON-escaped form (the scan before this round) | RED | a_recorded_text_the_json_escapes_fails_the_scan[rationale] and [turn text] |
| F2 | F: the scan drops the form as written | RED | a_recorded_text_the_json_escapes_fails_the_scan[rationale] and [turn text] |
| N1 | N: the approximation flag inverted (`is None`) | RED | the_json_labels_b_snapshot_an_approximation |
| L1 | L: the report's check names read from the labels literal, not the JSON | RED | the_report_names_each_check_as_the_json_does |

**Neuter pass, round 1.** Every line this round added or changed in the module, switched off in turn with the
same harness: 13 probes, all red on the first run.

| # | neutered | first run | red test |
| --- | --- | --- | --- |
| X1 | (b-snapshot) approximates nothing | RED | the_json_labels_b_snapshot_an_approximation |
| X2 | the checks block drops `approximation` | RED | the_json_labels_b_snapshot_an_approximation |
| X3 | the checks block drops `approximates` | RED | the_json_labels_b_snapshot_an_approximation |
| X4 | the checks block drops `name` | RED | the_json_labels_b_snapshot_an_approximation |
| X5 | the payload drops the checks block | RED | the_json_labels_b_snapshot_an_approximation |
| X6 | the per-check table names each check by its key | RED | the_committed_report_is_the_committed_jsons_rendering |
| X7 | the class table names each check by its key | RED | the_committed_report_is_the_committed_jsons_rendering |
| X8 | the case-reason table names each check by its key | RED | the_committed_report_is_the_committed_jsons_rendering |
| X9 | the pair-reason table names each check by its key | RED | the_committed_report_is_the_committed_jsons_rendering |
| D1 | the census comparison ignores the meeting id | RED | a_later_meeting_the_census_reads_differently_is_named[meeting_id-elsewhere] |
| D2 | the census comparison ignores the opener | RED | a_later_meeting_the_census_reads_differently_is_named[opener-p-gone] |
| D3 | the census comparison ignores the ejection | RED | a_later_meeting_the_census_reads_differently_is_named[ejected-p-gone] |
| D4 | the census comparison ignores the trigger | RED | a_later_meeting_the_census_reads_differently_is_named[trigger_kind-elsewhere] |

The test-only findings (1 and 2) change no production line; the scan's two forms, the labels block and the
report's read of it are this round's production lines, and each row above names its red test. No test was
weakened, skipped or deleted: four existing match patterns now require the whole message they were part of
(`test_a_census_with_one_meeting_more_raises`, the no-trigger raise in
`test_a_meeting_the_walk_threaded_no_trigger_or_ballot_for_raises`, `test_a_different_s9_figure_stops_the_run`,
`test_a_shown_pair_resting_on_no_stated_pair_raises`), and every other earlier assertion stands as it was beside
the new ones.

**Verification, round 1.** Each command ran alone with its exit code captured directly, on this branch with this
round's changes; no frontend file changed.

| command | exit | result |
| --- | --- | --- |
| the run (the five `--set`/`--out` arguments above) | 0 | wrote both files (48.7 s); counts and report unchanged, the JSON gains the `checks` block |
| `uv run pytest tests/experiments/test_route_check_replay.py -n 6` | 0 | 117 passed |
| `uv run python -m experiments.lab.route_check_replay --check` | 0 | reproduced (41.1 s) |
| `bash scripts/verify_samples.sh replays/<set>`, the five sets | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the five | 0 each | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent |
| `publish_gameplay_census.py --set-dir ... --json-stdout`, r2 and r1 | 0 each | the denominators quoted above |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed: 51 OK, 7 ABSENT, 5 INFO |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -n 6` | 0 | 86 passed |
| `uv run python scripts/check_doc_facts.py` | 0 | every fact verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 historical phase tasks and prompts; 96 work cards |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run mypy --strict` on the two touched Python files | 0 | no issues (the gate's `mypy .` covers the tree) |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| `build_demo_bundle.py --out <scratch>/base` at `5877adb4`, then `--out <scratch>/head` at `aa7eab23`, one checkout; `diff -rq` | 0, 0, 0 | no difference across 109 files: nothing publishes |

**The gate, round 1: `bash scripts/check.sh` at `8c155150` in this clean worktree, run once to its end, exit 0**
(about six minutes by the clock, 02:27 to 02:33): ruff check and format (553 files), import contracts 4 kept and 0
broken, task docs (390 phase tasks, 96 work cards), prompt sync, strict mypy over 524 sources, pytest 10,162
passed, 20 skipped and 3 xfailed (the 13 new instrument tests on top of the earlier gate's 10,149), and the
frontend lint, type check, 649 tests in 25 files and production build. The commit after it changes only this
card. The evolution-strategy hash pin, Linux-only by its own note, did not fail here; the PR's CI carries the
Linux run.

Deviations, round 1: the heading carries 2026-10-03, the day these corrections were made (the dispatch named
2026-10-02). `npm ci` ran in `frontend/` so the gate's frontend legs could run; no frontend file changed. Record
impact: none. No recording, prompt, template, detector, recorded byte or ML artifact moved; the JSON gains its
labels block and nothing else, and the merge publishes nothing (the empty bundle diff above).

### Review corrections, round 2 (2026-10-03)

Review round 2 of PR 499 returned nine blocking findings, and two of the five Codex comments on the first review
(at `8b18aa5`) had gone unanswered in round 1. Each is repaired here, and `## Acceptance` opens with one
review-correction item per finding. Commits: `200e2a32` (the instrument, its regenerated JSON and report, and the
planted cases), then the commit adding this subsection and the gate's. Files written:
`experiments/lab/route_check_replay.py`, `experiments/lab/results-route-check-replay.json`,
`experiments/lab/report-route-check-replay.md`, `tests/experiments/test_route_check_replay.py` and this card, all
inside the Expected scope. `docs/artifacts.md` and `tasks/README.md` need no change: the row's 167 files and 6.9 MB
hold at `200e2a32` (7,195,798 bytes), and the card's Status stays done.

1. **A regroup room read as the canonical literal (C7).** `held_rooms` read the regroup's room from the memory,
   but every planted regroup gathered the table in the Cafeteria, so the literal survived. `_sighting_memory` now
   takes the regroup's room, and two planted cases put the regroup in Admin: Labs at 10 then Admin at 11 (the
   line's ends and its charge follow the memory), and the Cafeteria at 10 then Admin at 11 (only the memory's room
   makes the line two-roomed, so (b) and (b-snapshot) reach the ejection and its charge through `_read_case`).
2. **(c)'s reason step read against (a)'s kinds (S14).** No planted case put an alibi stay at the end of a pair
   (c) left unreached. The planted button meeting does: a sighting at tick 1, which the relevance gate drops, against
   an alibi in Admin from 3 to 5; (c)'s reason is the relevance gate over both pairs, and (a)'s is kind.
3. **Eleven message arguments set to constants.** Every test now matches the whole message, with values chosen
   so that no likely constant matches, and two refusals gain r1 twins (a broken r1 config; r2's tree under the r1
   label), so a label or path constant of r2 fails too. The walk's raise is compared with the assertion
   `walk_replay_meetings` itself raises on the same flipped copy. No assertion was loosened: each earlier substring
   is part of the whole message now required.
4. **The unknown-label guard, untested.** Planted: a JSON copy with one column labelled r3 makes `--check` exit 1
   with the named refusal; without the guard, `--check` stops on an uncaught `ValueError` from `run_columns`' sort,
   and the test fails.
5. **The run's scan of the JSON, untested through the run.** Every earlier JSON-leak case called `scan_outputs`
   directly. Planted: `serialize` patched to carry a recorded rationale of r2 seed 2 into the JSON alone; the run
   exits 1, prints "an output carries recorded text; nothing written", and writes neither file.
6. and 7. **The round-1 byte total.** 7,192,231 was a typing slip: the sum at `17aab62d` and `01dc8a9f` is
   7,192,265 (`git ls-tree -r -l 01dc8a9f -- experiments/lab experiments/model_probe | awk '{n++; s+=$4} END {print n, s}'`
   prints `167 7192265`). Decisions carries the corrected figure, the command and this round's 7,195,798.
8. **The census tick (Codex P2 at line 1819, valid).** `read_game` compared id, opener, ejection and trigger and
   then used the census's tick for the record and the witness window. It now also compares `fact.tick` with the
   walked meeting's entry tick. Committed bytes: all 386 meetings agree (the regenerated run and `--check` walk
   every one with the comparison on), so no count moved.
9. **The fixed seeds sentence (Codex P2 at line 1858, valid).** Of the two repairs offered, the report now derives
   each column's seeds and roster from its recorded games rather than refusing a column outside 0 to 49: the
   statement is then true of any column the run reads, the one-game test columns need no seam, and the committed
   columns' pairing on seeds 0 to 49 is held where it matters, by `test_the_report_states_the_seeds_and_roster_the_json_records`
   (each committed column reads `0-49`, 9 players, 2 impostors) and by `test_the_committed_r2_column_recomputes_from_the_checkouts_bytes`,
   which recomputes r2's `seeds` and `roster` from the bytes. The seeds are the census's games (equal to the seeds on
   disk by `read_set`), so a game with no meeting still counts in its band. The report's Method sentence no longer
   states a band or a roster; its provenance table gains seeds, players and impostors columns. The six-game
   checkpoint the review ran now reads `0-5 | 9 | 2 | 6`.
10. **A recorded sha that could move (Codex P2 at line 2793, valid).** `recorded_sources` accepted any tree-ish the
    JSON recorded, so a hand-edited `HEAD`, branch or abbreviation would pass `--check` while it pointed at the
    recorded tree, and `--check` would then archive a moving name. It now resolves the recorded value as a commit
    and requires the result to equal it. The run itself always records `rev-parse`'s full sha, so no committed
    byte moved.
11. **Prompt multiplicity in the faithful walk (Codex P2 at line 1784, valid).** The walk compared sets, so a
    recorded prompt consumed once of twice, or asked for twice, passed. After the missed-prompt check, `walk_game`
    now requires the golden's own `consumed_exactly_once` (hits counted against the recorded calls), imported from
    the walk's module by the same ruling that imports the walk. Every meeting of the three columns passes it.

**The Codex review, answered.** The first Codex review (`8b18aa5`, five P2 comments): the escaped-text scan was
fixed in round 1 (correction 4 there); the census tick and the seeds sentence are corrections 8 and 9 here; the
symbolic sha and the prompt multiplicity are corrections 10 and 11 here. All five were valid; none is refuted.

**Mutation pass, round 2.** One bounded pass with the listed classes only, over the spans the findings name and
the spans this round changed: 34 mutants. Harness (`probes.py`, scratch, not committed): apply one edit to
`experiments/lab/route_check_replay.py`, run the named tests with `pytest -n 4 -k`, and, only if they pass, the
whole file; restore the module from its byte copy, never `git checkout` (its sha1 matched the copy after the run).
First run: 34 red, no survivor. Before this round, at `01dc8a9f`, the verifiers' runs had C1 (their C7), S1
(their S14) and the eleven class-M probes they listed (here M13, M14, M16, M18, M20 and M22 to M27) green; each is
red now through the planted cases above.

| # | mutant | first run | red test |
| --- | --- | --- | --- |
| C1 | C: `held_rooms` adds the literal CAFETERIA for a public regroup | RED | a_regroup_off_the_hub_takes_its_room_from_the_memory, a_regroup_from_the_hub_to_another_room_reaches_its_charge |
| S1 | S: (c)'s reason step tests kinds against `A_INPUT_KINDS` | RED | a_gated_sighting_against_an_alibi_stay_is_given_the_relevance_gate |
| M13 | M: the malformed-request raise names a constant text | RED | a_malformed_column_request_is_refused (all six) |
| M14 | M: the git raise names a constant detail | RED | an_unknown_commit_is_refused, a_path_that_does_not_resolve_is_refused |
| M15 | M: the unresolved-commit raise names a constant commit | RED | an_unknown_commit_is_refused, a_tree_named_as_the_commit_is_refused |
| M16 | M: the unresolved-path raise names a constant sha | RED | a_path_that_does_not_resolve_is_refused |
| M17 | M: the unresolved-path raise names a constant path | RED | a_path_that_does_not_resolve_is_refused |
| M18 | M: the not-a-directory raise names a constant path | RED | a_path_that_names_a_file_is_refused |
| M19 | M: the not-a-directory raise names a constant sha | RED | a_path_that_names_a_file_is_refused |
| M20 | M: the no-config raise names the constant label r2 | RED | a_declared_r1_config_that_is_no_config_names_r1 |
| M21 | M: the no-config raise names a constant path | RED | a_declared_config_that_is_no_config_is_refused, a_declared_r1_config_that_is_no_config_names_r1 |
| M22 | M: the settings raise names the no-config constant for the declared path | RED | r1s_tree_under_the_r2_label_is_refused, r2s_tree_under_the_r1_label_names_r1s_config |
| M23 | M: the tree-mismatch raise names a constant sha | RED | a_recorded_tree_id_that_is_not_the_shas_tree_fails_check, an_r1_columns_tree_mismatch_names_r1 |
| M24 | M: the unknown-column raise names a constant label | RED | an_unknown_recorded_label_is_refused_by_name |
| M25 | M: the ledger-bound raise names the constant bound MAP_ARBITRATION_MAX_HOPS | RED | a_ledger_bound_that_is_no_integer_raises |
| M26 | M: the walk raise names a constant detail | RED | a_state_hash_flipped_after_the_second_meeting_names_the_third |
| M27 | M: `--check` names a constant JSON path | RED | one_count_edited_in_a_copy_of_the_json_fails_check |
| M28 | M: `--check` names a constant report path | RED | a_report_that_differs_from_its_recomputation_fails_check |
| M29 | M: the full-sha raise names the constant label r2 | RED | an_r1_columns_tree_mismatch_names_r1 |
| M30 | M: the full-sha raise names a constant sha | RED | a_recorded_sha_that_is_no_full_commit_sha_fails_check[short] |
| M31 | M: the call-count raise names the constant label r2 | RED | a_recorded_call_asked_for_other_than_once_raises (both) |
| N1 | N: the census tick comparison inverted | RED | a_later_meeting_the_census_reads_differently_is_named (all five rows), an_unchanged_copy_of_a_game_reads_cleanly |
| N2 | N: the full-sha comparison inverted | RED | check_reproduces_a_run_from_its_recorded_sha, a_recorded_sha_that_is_no_full_commit_sha_fails_check (both) |
| N3 | N: the seed-run continuation test inverted | RED | seeds_are_stated_as_runs (three of four) |
| N4 | N: the empty-seed test inverted | RED | seeds_are_stated_as_runs (all four), no_seed_at_all_raises |
| N5 | N: the one-roster test inverted | RED | a_columns_roster_is_its_games_own |
| B1 | B: the single-seed and run branches swapped | RED | seeds_are_stated_as_runs (all four) |
| F1 | F: the seed sort and dedup dropped | RED | seeds_are_stated_as_runs (the unsorted and repeated rows) |
| F2 | F: the seed dedup dropped | RED | seeds_are_stated_as_runs[3-4, 9] |
| C2 | C: the impostor count reads a constant role | RED | a_columns_roster_is_its_games_own |
| S2 | S: the seeds read from the meeting records, not every recorded game | RED | a_columns_seeds_are_every_recorded_game_not_only_those_with_a_meeting |
| L1 | L: the column's seeds replaced by the canonical literal `0-49` | RED | a_run_states_its_columns_own_seeds_and_roster, a_columns_seeds_are_every_recorded_game_not_only_those_with_a_meeting |
| L2 | L: the column's roster replaced by the canonical 9 and 2 | RED | a_columns_seeds_are_every_recorded_game_not_only_those_with_a_meeting |
| L3 | L: the report's seeds cell replaced by the canonical literal `0-49` | RED | a_run_states_its_columns_own_seeds_and_roster, the_report_states_the_seeds_and_roster_the_json_records |

**Neuter pass, round 2.** Every production line this round added or changed, and the two lines the review named,
switched off in turn with the same harness: 13 probes, all red on the first run. X4 and X5 are the review's own
probes (the guard removal and P9), green at `01dc8a9f`.

| # | neutered | first run | red test |
| --- | --- | --- | --- |
| X1 | the census tick left out of the comparison | RED | a_later_meeting_the_census_reads_differently_is_named[tick-1] |
| X2 | the call-count check switched off | RED | a_recorded_call_asked_for_other_than_once_raises (both) |
| X3 | the full-sha guard switched off | RED | a_recorded_sha_that_is_no_full_commit_sha_fails_check (both) |
| X4 | the unknown-label guard of `recorded_sources` switched off | RED | an_unknown_recorded_label_is_refused_by_name |
| X5 | the run scans the report only (the review's P9) | RED | a_run_whose_json_would_carry_a_rationale_writes_nothing |
| X6 | the payload drops the seeds | RED | a_run_states_its_columns_own_seeds_and_roster, a_columns_seeds_are_every_recorded_game_not_only_those_with_a_meeting |
| X7 | the payload drops the roster | RED | the same two |
| X8 | the report's players cell blank | RED | a_run_states_its_columns_own_seeds_and_roster, the_report_states_the_seeds_and_roster_the_json_records |
| X9 | the report's impostors cell blank | RED | the same two |
| X10 | the empty-seed raise switched off | RED | no_seed_at_all_raises |
| X11 | the one-roster raise switched off | RED | a_columns_roster_is_its_games_own |
| X12 | the player count read as the constant 9 | RED | a_columns_roster_is_its_games_own, a_columns_seeds_are_every_recorded_game_not_only_those_with_a_meeting |
| X13 | the Method sentence restored to its fixed band and roster | RED | a_run_states_its_columns_own_seeds_and_roster |

The module docstring now names the full-sha refusal and the derived seeds and roster; it is prose and carries no
probe. No test was weakened, skipped or deleted: eleven earlier substring matches now require the whole message
they were part of, `test_a_missed_prompt_count_is_the_meetings_own` builds its walked meetings with the calls the
golden's count reads (its expected message is unchanged), and `test_a_later_meeting_the_census_reads_differently_is_named`
gains its tick row beside the four it had.

**Verification, round 2.** Each command ran alone with its exit code captured directly (no pipe), at `200e2a32`;
no frontend file changed.

| command | exit | result |
| --- | --- | --- |
| the run (the five `--set`/`--out` arguments above) | 0 | wrote both files (41.7 s); every count unchanged, the JSON gains `seeds` and `roster` per column |
| `uv run python -m experiments.lab.route_check_replay --check` | 0 | reproduced (39.2 s) |
| the run with `--set r1=9725ece0:replays/candidates/stage-b-r1/9p2i` into scratch (the review's checkpoint) | 0 | its report's provenance row reads seeds `0-5`, 9 players, 2 impostors, 6 games, and holds no `0-49` |
| `uv run pytest tests/experiments/test_route_check_replay.py -n 6` | 0 | 139 passed |
| `uv run ruff format --check` and `uv run ruff check` on the two Python files; `uv run mypy --strict` on them | 0, 0, 0 | formatted, clean, no issues (the gate covers the tree) |
| `bash scripts/verify_samples.sh replays/<set>` for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `publish_gameplay_census.py --set-dir ... --json-stdout`, r2 and r1 | 0 each | r2 117 meetings, 24 with vent proof, 3 button; r1 124, 26, 6: the denominators quoted above |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -n 6` | 0 | 86 passed |
| `uv run python scripts/check_doc_facts.py` | 0 | every fact verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 historical phase tasks and 390 prompts; 96 work cards (on this card at the subsection commit) |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| `build_demo_bundle.py --out <scratch>/base` at `5877adb4`, then `--out <scratch>/head` at `200e2a32`, one checkout; `diff -rq` | 0, 0, 0 | no difference across 109 files: nothing publishes |

**The gate, round 2: `bash scripts/check.sh` at `e4b94163` in this clean worktree, run once to its end, exit 0**
(about six and a half minutes by the clock, 03:26 to 03:33): ruff check and format (553 files), import contracts 4
kept and 0 broken, task docs (390 phase tasks, 96 work cards), prompt sync, strict mypy over 524 sources, pytest
10,184 passed, 20 skipped and 3 xfailed (the 22 new instrument tests on top of round 1's 10,162), and the frontend
lint, type check, 649 tests in 25 files and production build. The commit after it changes only this card. The
evolution-strategy hash pin, Linux-only by its own note, did not fail here; the PR's CI carries the Linux run.

Deviations, round 2: the heading carries 2026-10-03, the day these corrections were made (the dispatch named
2026-10-02), as round 1's did. The two Codex comments of the first review that round 1 left unanswered are treated
as findings, as the dispatch's rule for valid Codex comments requires. `npm ci` ran in `frontend/` so the gate's
frontend legs could run; no frontend file changed. Record impact: none. No recording, prompt, template, detector,
recorded byte or ML artifact moved; the JSON gains `seeds` and `roster` per column and the report the matching
table columns and Method sentence, with every count unchanged, and the merge publishes nothing (the empty bundle
diff above).

### Review corrections, round 3 (2026-10-03)

Review round 3 of PR 499, at `24ea077f`: the documentation lens passed, and the correctness and integrity lenses
left four listed-class findings, two of them the same mutant (the column sort). Each is repaired here, and
`## Acceptance` opens with one review-correction item per finding plus one for the integration the card's merge
order requires. Commits: `bc8d6ff1` (the merge of `main`), `400361d3` (the planted cases, the wording and the
regenerated report), then the commit adding this subsection and the gate's. Files written:
`experiments/lab/route_check_replay.py` (docstrings and one report header), `experiments/lab/report-route-check-replay.md`
(that header, regenerated by the run), `tests/experiments/test_route_check_replay.py`, `tasks/README.md` (the
inventory sentence, in the merge) and this card, all inside the Expected scope. The run rewrote the JSON
byte-identical. `docs/artifacts.md` needs no change: the row's 167 files and 6.9 MB hold at `400361d3` (7,196,210
bytes) and at `bc8d6ff1` (7,195,798).

1. **The column sort (F, the correctness and integrity lenses).** `run_columns` sorts the requested columns into
   `COLUMN_LABELS` order, but every run in the suite that wrote its outputs read one column (the only
   two-column request is the refused pool), so dropping the sort passed all 139 tests while the card's own
   command (r2, r1, s9) would then write r2, r1, s9 and stop regenerating the committed JSON. Planted: one temporary repository holding r1 and r2 seed 2, run twice, r2
   first and r1 first; the r2-first run must write the JSON's columns, the `### Column` sections and the
   provenance rows as r1 then r2, and both files byte-equal to the r1-first run's.
2. **`rule_applies_to` (N).** `build_payload` names the column the dated rule applies to, r2 when the run reads
   r2, and no test read it (only `--check` on a full run would). The one-game r2 run must read `r2` and the r1-only
   run `None`.
3. **The origin leg's regroup ticks (C).** `walkable_with_movement_origins` passes each spoken movement's origin
   through `is_relevant_sighting` with the meeting's body rooms and regroup ticks, but no case put an origin in a
   regroup window, so the gate given no regroup ticks passed every test. Planted: p-1 holds the record of p-5
   moving from West Hall into Admin at 12 and says so, so the live clause places p-5 in Admin at 12 alone (the
   test checks that path under every regroup setting it uses); the origin, West Hall at 11, is one door and one
   tick from it. With a regroup at 10 (window 10 and 11) the leg reads False; with no regroup ticks, and with a
   regroup at 9 (window 9 and 10), True. The same plant at a report meeting whose body lies in West Hall reads
   False, and as a button meeting True, which isolates the gate's other call-site argument.
   **The neuter pass's claim, corrected.** Its paragraph said every call-site argument was switched off in turn.
   Its rows 65 to 68 drop the whole gate, any subject's movement, the origin's tick and the leg itself, and no row
   isolated the gate's `regroup_ticks` or `triggering_body_rooms`. The paragraph now states what it covered, and
   C1 and C2 below are those two arguments.
4. **Integration.** The card's merge order is census first, then this card. The census card merged into `main`
   at `a0fdb570` after this branch's base; `bc8d6ff1` merges it (no rebase; the one conflict, the derived
   inventory sentence, re-derived by the validator). On the merged tree, with the census card's
   `eval/gameplay_census.py` and `eval/eras.py`:
   - `publish_gameplay_census.py --set-dir ... --json-stdout`, exit 0 each, count-only: r2 117 meetings,
     `meetings_with_vent_proof` 24, `button_meetings_with_vent_proof` 3 of 3, `meetings_without_vent_proof_ejecting`
     42 of 93, `role_correct_ejections` 44 of 66 (22 innocent), `kills_seen_by_crew` 14, 114 report meetings; r1
     124, 26, 6 of 6, 28 of 98, 39 of 54 (15 innocent), 4, 118. Every denominator the delivery quoted reads the same.
   - `--check` exit 0 (62.5 s at `bc8d6ff1`, 38.5 s at `400361d3`): the instrument re-derives each column's
     census with the merged `load_census_inputs` (s9's on its archived copy) and compares every meeting one for
     one, so s9's 145 meetings and 90 ejections, r1's and r2's, and the witness meetings 3, 3 and 14 stand.
   - The inventory sentence reads 96 cards, 3 ready and 93 done (both this card and the census card are done);
     `validate_task_docs.py` exits 0 on it. The `experiments/lab/` row is unchanged: the merge moves nothing under
     `experiments/`.
5. **Wording, from the round's nonblocking notes, with no new mechanism.** The module docstring said roles were
   read only for the ejection classes; since review round 2 they also give each column's roster, and it now says
   so (as does the role-blind bullet of Acceptance, item by item, above). The scan's 16-character floor
   (`_SCAN_MIN_LENGTH`) is stated where the guarantee is: the module docstring, `scan_outputs`,
   `forbidden_strings` and the Count-only bullet above. The report's provenance column `games` counts the games
   with a meeting (`len({record.seed for record in records})`, beside `seeds`, every recorded game) and its header
   now reads "games with a meeting". The post-census obligations of Limitations are marked done there.

**Codex.** No new Codex comment since the first review at `8b18aa5`; its five comments were answered in round 2.

**Mutation pass, round 3.** One bounded pass with the listed classes only, over the spans the findings name
(`run_columns`' sort, `build_payload`'s `rule_applies_to`, the origin leg's gate and the reads feeding it) and the
spans this round changed: 14 mutants and one neuter. Harness (`probes.py`, scratch, not committed): apply one edit
to `experiments/lab/route_check_replay.py`, run the named tests with `pytest -x -n 4 -k`, and, only if they pass,
the whole file; restore the module from its byte copy (its sha1 matched the copy after the run). First run: all 15
red, no survivor; a second run without `-x` named every red test below. At `24ea077f` the verifiers' runs had F1, N1
and C1 green (139 passed each).

| # | mutant | first run | red test |
| --- | --- | --- | --- |
| F1 | F: `run_columns` iterates the sources as given (the sort dropped; finding F, both lenses) | RED | columns_given_out_of_column_order_are_written_in_it |
| S1 | S: the sort reads the labels as given, not `COLUMN_LABELS` | RED | columns_given_out_of_column_order_are_written_in_it |
| T1 | T: `COLUMN_LABELS` drops r1 | RED | columns_given_out_of_column_order_are_written_in_it |
| N1 | N: `rule_applies_to` tests `"r2" not in labels` (finding N) | RED | an_r1_column_reads_under_its_rounds_config, the_reading_applies_its_rule_to_r2_when_the_run_reads_r2 |
| N2 | N: `rule_applies_to` tests `labels is not None` | RED | an_r1_column_reads_under_its_rounds_config |
| B1 | B: `rule_applies_to`'s two branches swapped | RED | an_r1_column_reads_under_its_rounds_config, the_reading_applies_its_rule_to_r2_when_the_run_reads_r2 |
| C1 | C: the origin gate given `frozenset()` for the regroup ticks (finding C) | RED | a_movement_origin_in_the_regroup_window_is_no_placement |
| C2 | C: the origin gate given `frozenset()` for the body rooms | RED | a_movement_origin_at_the_kill_scene_is_no_placement |
| C3 | C: the origin leg reads the trigger kind as `emergency` | RED | a_movement_origin_at_the_kill_scene_is_no_placement |
| C4 | C: the origin's tick read as 0 | RED | a_movement_origin_at_the_kill_scene_is_no_placement, a_movement_origin_in_the_regroup_window_is_no_placement |
| C5 | C: the origin's room read as the Cafeteria | RED | the same two |
| N3 | N: the origin leg's subject test inverted | RED | the same two |
| N4 | N: the origin leg's empty-room test inverted | RED | the same two |
| F2 | F: the origin leg drops its movement-sighting filter | RED | a_movement_origin_at_the_kill_scene_is_no_placement |

**Neuter pass, round 3.** The one production line this round changed that is not a docstring, switched off with
the same harness: X1, the provenance header read as `games` again, is red through
`test_the_committed_report_is_the_committed_jsons_rendering`. The docstrings are prose and carry no probe. No test
was weakened, skipped or deleted: `test_an_r1_column_reads_under_its_rounds_config` keeps both its assertions and
gains the `rule_applies_to` one; four tests are new.

**Verification, round 3.** Each command ran alone with its exit code captured directly (no pipe), at `400361d3`
unless named; no frontend file changed.

| command | exit | result |
| --- | --- | --- |
| the run (the five `--set`/`--out` arguments above) | 0 | wrote both files (38.8 s); the JSON byte-identical, the report's provenance header the only change |
| `uv run python -m experiments.lab.route_check_replay --check` at `bc8d6ff1` and at `400361d3` | 0, 0 | reproduced (62.5 s, 38.5 s) |
| `uv run pytest tests/experiments/test_route_check_replay.py -n 6` | 0 | 143 passed (139 on the merged tree before the repairs) |
| `uv run ruff format --check` and `uv run ruff check` on the two Python files; `uv run mypy --strict` on them | 0, 0, 0 | formatted, clean, no issues (the gate covers the tree) |
| `bash scripts/verify_samples.sh replays/<set>` for samples/9p2i, samples/4p1i, ml_corpus/9p2i, ml_corpus/4p1i, candidates/stage-b-r1/9p2i | 0 each | 50, 50, 150, 50 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --check --sample-dir replays/<set>`, the same five | 0 each | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent with the committed recordings |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent with the committed recordings |
| `publish_gameplay_census.py --set-dir ... --json-stdout`, r2 and r1, at `bc8d6ff1` | 0 each | the denominators in item 4 |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO; `experiments/lab/` OK |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -n 6` | 0 | 86 passed |
| `uv run python scripts/check_doc_facts.py` | 0 | every fact verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 historical phase tasks and 390 prompts; 96 work cards (at `bc8d6ff1`, and on this card at the subsection commit) |
| `uv run lint-imports` | 0 | 4 kept, 0 broken |
| `uv run pytest -m campaign -n 6` | 0 | 337 passed |
| the lab row's byte total: `ls-tree -r -l 400361d3 -- experiments/lab experiments/model_probe`, summed by the Decisions command | 0 | `167 7196210` (`167 7195798` at `bc8d6ff1`) |
| `build_demo_bundle.py --out <scratch>/base` at `a0fdb570` (`main`), then `--out <scratch>/head` at `400361d3`, one checkout; `diff -rq` | 0, 0, 0 | no difference across 109 files: nothing publishes |

**The gate, round 3: `bash scripts/check.sh` at `96694a77` in this clean worktree, run once to its end, exit 0**
(about six minutes by the clock, 04:31 to 04:37), its exit code captured directly with no pipe: ruff check and
format (553 files), import contracts 4 kept and 0 broken, task docs (390 phase tasks, 96 work cards), prompt sync,
strict mypy over 524 sources, pytest 10,249 passed, 20 skipped and 3 xfailed (on the merged tree: the census
card's tests from `main` and this round's 4 on top of round 2's 10,184), and the frontend lint, type check, 649
tests in 25 files and production build. `96694a77` is the merged head plus this round's code and card commits;
the commit after it changes only this card. The evolution-strategy hash pin, Linux-only by its own note, did not
fail here; the PR's CI carries the Linux run.

Deviations, round 3: the two findings that name the same mutant share one planted test, with an Acceptance item
each. The body-room half of the origin gate (C2, C3) was not a finding; it is planted because the corrected neuter
claim names both of the gate's call-site arguments. The bundle's base is now `a0fdb570`, `main` after the census
merge, where rounds 1 and 2 built it at `5877adb4`. `npm ci` ran in `frontend/` so the bundle and the gate's
frontend legs could run; no frontend file changed. Record impact: none. No recording, prompt, template, detector,
recorded byte or ML artifact moved; the report's one header is the instrument's own wording, every count is
unchanged, and the merge publishes nothing (the empty bundle diff above).

### Reading (2026-10-03)

The card's rule, applied to r2 verbatim, from the JSON's `rule_inputs` (the report prints the same branch). M is
r2's 40 misjudged cases; W is the 7 of them at witness meetings.

1. M is not empty.
2. (b-snapshot) reaches 20 of the 40, exactly half, but 3 of the 7 at witness meetings, under half. Branch 2 is not
   taken. (b) as recorded reaches 16 of 40 and 2 of 7, and at the recorded ballot budget it never shows a row that
   says an interval crosses the regroup.
3. (c) reaches 29 of the 40 and 7 of the 7. **Branch 3: name the narrow new field**, as a card to write: versioned,
   default off, set only from the config file, its own stamp, one role-blind line per living candidate that never
   asserts presence or honesty, with planted cases and fake and scripted rehearsals before any spend. Shaped by
   (c)'s unreached reasons: (c) reaches every misjudged innocent ejection (21 of 21) and every ejected witness (5 of
   5); the 11 cases it leaves are all impostor ejections, 9 resting on a vent sighting at one end of the pair (a
   kind the reading does not take, and a role-proving one) and 2 on a sighting the relevance gate drops (the
   spawn or regroup window). Its reach comes from what (a) lacks: several hops over the whole map, alibi stays
   (18 of (a)'s 25 unreached cases rest on a kind (a) does not read) and a named regroup crossing. It also reaches 8
   of the 19 misjudged impostor ejections; that is reported, not discounted.

Beside it, at the same rule: s9 takes branch 2 (M 50, W 0; (b-snapshot) reaches 30) and r1 takes branch 2 (M 29,
W 0; (b-snapshot) reaches 15). Neither column has a misjudged case at a witness meeting, which is the half of the
rule r2 fails for (b-snapshot).

What this does not say: reaching is showing a line, not changing a vote, and no model was run. The reading is
advisory and gates nothing; it authorizes no recording, and a round 3 is the owner's spend decision.
