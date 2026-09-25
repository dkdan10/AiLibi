# A1: the gameplay census report

**Status:** done

## Outcome

The project gains a second committed report, beside and separate from the nine-row process
scorecard: a count of what happens in the games themselves. It folds the four committed sets,
with zero model calls, into cells for vent entries and exits and who saw them, kills and their
witnesses, corpses at each meeting, the state play resumes in, the meeting's speaking order, and
the impostors' ballots. Every cell publishes its numerator, its denominator, its not-evaluable
count and the event kinds it reads, per set and pooled within one era. Every cell that a Stage-B
arm makes zero by construction carries that arm's predicate and a guard that raises on a breach,
so the record card can stop on a code defect instead of reading it as a result.

`scripts/publish_gameplay_census.py` writes `docs/gameplay-census.md` and `.json`; `--check`
recomputes both and fails on drift; `--set-dir DIR --json-stdout` folds one directory (the
round-1 candidate, or a scratch rehearsal) and writes nothing. The committed pages stay on
baseline 9 through the whole wave. No agent behaviour, prompt byte, schema field, detector,
recorded byte or scorecard row moves. Role-correctness is reported beside, gates nothing, and
feeds nothing back to any agent. Wave 0, card 2 of the decision memo's section 3.1 table.

## Evidence

Line numbers below are at `e886b663`; the implementer re-anchors each by the symbol named with it
before editing. The memo paths are under
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/stage-b-2026-09-24/`:
`decision-memo.md` sections 0, 2.6, 3.2, 3.4 card 2 and 4, and `census_and_record.md` sections 1
and 4 (this card's investigation).

**Rulings relied on.** The owner's rulings of 2026-09-24, verbatim: "We should implement stage B";
and on the record, "Let's not re-record all 300 seeds each time. When it's time to record, record
the smaller group of 50 seeds, assess if the implementations have been effective and resulted in
desired results." The census is the instrument that assessment reads. "Hold off on ML as D
suggests until gameplay is finished." and "Tour fix can be deferred to after gameplay is finished"
keep it away from training code and the viewer. The orchestrator's rulings under the owner's
delegation of 2026-09-24 ("What do you think is best?"): **R13**, "the gameplay census stays a
separate published report beside the nine-row scorecard; no cell joins the scorecard; no D1
amendment", with candidate columns computed by `--set-dir` modes that write nothing; **R6**,
impostor self-report stays OFF, which the census reports as a conformance cell; decision 0.3
item 6, a recorded arm value's meaning is frozen once round 1 is recorded; decision 0.3 item 9,
the pending-arm guard.

**Every acceptance figure reproduces today.** Re-measured on 2026-09-24 at `e886b663` with the
investigation's count-only walk (`scratchpad/census_rec/walk2.py` through the process-scorecard
walk profile, then `cen.py`); its output was byte-identical to the investigator's walk. Scratch
scripts are not an instrument: every figure is re-measured at dispatch by the committed census,
and a difference is reported in Results, never pinned over.

| cell | s9 | 9p2i pool | four-set pool |
|---|---|---|---|
| kills seen by crew | 3/175 | 19/725 | 20/849 |
| vent entries seen by crew | 19/105 | 64/501 | 73/587 |
| vent exits seen by crew | 62/85 | 271/435 | 313/512 |
| exits seen from the exit room / only from the room left | 53 / 9 | 226 / 45 | 251 / 62 |
| impostors seen venting / vented unseen / never vented: ejected | 70/77, 3/8, 8/15 | 284/304, 13/56, 25/40 | 330/355, 13/89, 26/56 |
| meetings with vent proof / without | 70 / 75 | 285 / 309 | 330 / 346 of 676 |
| impostor ejections in the vent band / without vent proof | 70 / 11 | 281 / 41 | 326 / 43 |
| vent band by moment: exit only / both / entry only | 51 / 2 / 17 | 217 / 10 / 54 | 253 / 10 / 63 |
| vent-band ejections resting only on crew in the room left | 8 | 37 | 50 |
| stale report meetings | 43/135 | 167/551 | 167/623 |
| meetings opening with another unreported corpse | 74/145 | 325/594 | 335/676 |
| first reply accuses the opener | 120/145 | 448/594 | 521/676 |
| opener speaks a second time | 0/145 | 0/594 | 0/676 |
| openers among innocent ejections | 7/9 | 37/41 | 38/42 (37 report, 1 button) |
| moves thrown away on trigger ticks | 188 | 754 | 809 |

The same walk gives the before values the record card's assessment table quotes (s9; pooled):
play resumes with an impostor in a vent 10/107 (30/486) and with a corpse 60/107 (263/486);
post-meeting kills within 2 ticks 28/87 (135/389); meetings opening with an impostor in a vent
29/145 (101/676); impostor ballots 210 with 164 SKIP, 46 EJECT, 44 labelled `supported`; the
opener accused after turn 0 in 125 (561) meetings; impostor openers 0/676; repeat-speaker turns 0;
411 pooled ejections (369 impostor, 42 crew); 623 report and 53 button meetings. The ruled entry
gate (own victim in that room, killed at most 3 ticks earlier, no meeting between) removes 13 of
105 s9 entries and 103 of 587 pooled (`scratchpad/synth_b/entry_gate.py`, re-run). From the
memos, not re-run here: 135/135 s9 report openings (623/623 pooled) carry the kill-tick body id,
on 632 calls (s9 138, c9 422, s4 36, c4 36; decision memo 0.4); exits into a room the impostor
could see and a crewmate occupied, 31/85 (134/512), measured on the engine's sight set; crew kill
witnesses alive at the next meeting / voting the killer / killer ejected, 3/3/2 (20/19/12);
ejections whose confidence floor only impostor ballots met, 0 of 411.

**One definitional correction is already known.** The analysis memo's 808 thrown-away moves is
809: read from the recorded `action_dispositions` (`orchestrator/replay.py:206`), a trigger tick
that also ended the game (s4 seed 3) counts; slicing events on meeting-phase ticks misses it.

**The shape to copy exists.** `eval/process_scorecard.py` separates an impure loader from a pure
fold over a hand-buildable carrier (`SetInputs` `:745`, `load_set_inputs` `:835`, `fold_set`
`:1293`, `pool` `:1746`), publishes `RateCell` (`:390`) with an `n/a` rule for an empty
denominator, takes its set lists from `COMMITTED_SETS` / `NINE_PLAYER_SETS` (`:1856`, `:1862`)
and defines the vent band as a `vent_sighting` flag naming the ejected player (`:1116`). Its
publisher (`scripts/publish_process_scorecard.py`: `protected_inputs` `:54`, `publish` `:317`,
`check_report` `:331`) preflights every destination through `scripts/_report_output.py`, and it
states "These four sets are one era" as fixed text (`:252`), which the census must not copy: the
census derives the era from the recordings.

**Why the census needs its own walk profile.** Eight of eleven walk profiles refuse any recording
that carries an experiment config (`eval/replay_walk.py:505-508`). The current-report profile
supports experiments and verifies tick hashes, dispositions, meeting post hashes and chronology
(`eval/balance_eval.py:933-949`); the lab derives its profiles from it with `replace`
(`experiments/tactical_gameplay.py:199`, `:363`). Vent witnesses live only in engine events,
never in state, so a walk that forgets an engine arm passes every hash check with wrong witness
sets (census memo F5); the census must refuse any field it does not thread.

**Facts the cells rest on.** The body id embeds the kill tick (`engine/rules.py:87`), so the
census joins a body to its victim's `KilledEvent`, never to the id. After a regroup the impostor
kill cooldown restarts at the map's `kill_cooldown_ticks` (`engine/meeting_reset.py:36-40`, 4 at
`engine/maps/canonical_1.yaml:34`); a kill needs cooldown 0 at validation (`engine/rules.py:82`),
so after a meeting at tick T kills are illegal at T+1 to T+4 and first legal at T+5 (decision memo
0.4). The rebuttal is the only turn by a player who already spoke (`meetings/manager.py:1508-1539`,
`select_bounded_rebuttal` at `meetings/rebuttal.py:17`). The emergency button cooldown is 6 ticks
(`EMERGENCY_COOLDOWN_TICKS`, `agents/tactical/crewmate_policy.py:109`). An in-vent impostor gets no
visible-room list; the ruled exit policy infers own room plus map neighbours, and own room only
under any active sabotage (`vent_witness_and_exit.md` section 1.3). The tree's one kill-tick handle
pattern is `LEGACY_BODY_HANDLE_PATTERN` (`experiments/held_out_prefixes.py:168`). A MANIFEST row for
a game with no meeting records no prompt stamp: 11 of 50 rows in `replays/samples/4p1i` and 7 of 50
in `replays/ml_corpus/4p1i`. Authored teammate targets (`teammate_coerced`) are 1 on s9 and 13
pooled (`docs/process-scorecard.md:164`, `:57`).

## Acceptance

Unless an item names another mechanism, it is enforced by `tests/eval/test_gameplay_census.py`
over hand-built carriers, with no replay on disk.

- [x] Review correction (round 3): the grace window and the ballot floor each follow their source,
  planted. A carrier walked on a map whose kill cooldown is 6 breaches on a kill at T+6, not on
  one at T+7, and publishes `grace_window_ticks` 6
  (`test_the_grace_window_follows_the_kill_cooldown_the_carrier_holds`). The loader loads its map
  once, every game walks on it, and the carrier's cooldown follows a planted map
  (`test_the_loader_reads_the_kill_cooldown_from_the_map_it_loads`). A meeting that recorded
  `skip_confidence_threshold` 0.75 reads `ballot_floor` 0.75, and one that recorded none reads the
  tally's historical 0.6 (`test_the_ballot_floor_is_the_threshold_the_meeting_recorded`). The
  other constants bound from a source are planted the same way
  (`test_the_constants_bound_from_a_source_follow_it`,
  `test_the_own_kill_join_reads_the_scorecards_clock_offset`). Each probe is red with a literal
  and green with the read (Results, Review corrections, round 3).
- [x] Review correction (round 3): with the arm spine merged, the census-local defaults for five
  fields and the tripwire test that pinned them are deleted, one history line each. Every default
  is read from `RecordedExperimentConfig`'s own declaration (`_field_default`), and the
  classification is held equal to the model's fields both ways. Planted:
  `test_a_classification_naming_an_undeclared_field_fails`,
  `test_a_classified_field_the_config_does_not_declare_has_no_default` and
  `test_a_default_follows_the_config_models_declaration`. The walk-profile item below is closed.
- [x] Review correction (round 3): the Delivery sentence names the house trailer,
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, and every commit of this pass ends
  with it. Mechanism: the commit bodies of this pass, read back after the push. Results names the
  trailer each earlier commit carries.
- [x] Review correction (round 2): on baseline 9 the two added cells that count what a setting's
  own mechanism did, among things every era has, read `n/a`, not a measured 0. "Vent trips ended
  by a regroup" is counted only in games recorded with `meeting_reset = hub_with_grace`.
  "Surfacings at the cap" is counted only in games recorded with
  `vent_exit_policy = look_and_wait`. The two added tables whose rows only a setting's mechanism
  makes (the trigger-tick events a regroup drops, and who received a rebuttal) read `n/a`
  instead of `(none)` with a 0. Mechanism: `CellSpec.scope` and `TableSpec.scope`, applied in
  the fold's accumulator and published as `scope` and `in_scope`. Planted:
  `test_where_no_meeting_regroups_no_trip_is_ended_by_a_regroup`,
  `test_without_the_look_and_wait_exit_no_surfacing_is_at_a_cap`,
  `test_where_no_meeting_regroups_the_dropped_events_table_reads_n_a` and
  `test_the_rebuttal_beneficiaries_table_is_counted_only_with_the_rebuttal_on`. A property over
  every cell and table is `test_every_cell_and_table_counts_exactly_when_its_scope_holds`, and
  `test_on_baseline_9_every_scoped_cell_and_table_reads_n_a` reads the committed JSON and page.
- [x] Review correction: an own-kill row that names the holder's fellow impostor as its killer is
  a breach whether or not it cites anything, and every served row is in the cell's denominator:
  a row citing nothing joins no kill and is a breach too, because the ballot card specifies that
  each row cites its kill. Mechanism: `_own_kill_row_breaches` tests the teammate before the
  citation. Planted: three new `GUARD_PAIRS` rows in
  `test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off` (a teammate row citing
  nothing, a witness row citing nothing, and a row naming someone other than the cited kill's
  killer), and `test_the_rows_found_are_the_denominator_so_a_mismatch_reads_n_a`.
- [x] Review correction: the census module's and the publisher's sub-expressions are pinned. Of
  1,049 mutants from twelve sub-expression operators over both files, the two census suites
  catch 1,018 (a failing test, a module that no longer imports, or one hang); the other 31 are
  named in Results one by one, each with the reason no input can tell it apart from the source. The method, the operators and the tables are in Results (Review
  corrections, round 1).
- [x] **Shape.** `eval/gameplay_census.py` holds an impure `load_census_inputs(set_dir)` that walks
  one set and a pure fold over a frozen carrier holding only ids, rooms, ticks, kinds, labels,
  dispositions, plain recorded arm values and loader-computed booleans; `pool` adds counts and
  recomputes rates from pooled numerators and denominators. Enforced by a test that walks the
  carrier's fields and fails on any string-typed field outside a named allow-list of id, room, kind
  and label fields. Planted: a carrier class with a `rationale: str` field fails it.
- [x] **Walk profile and thread-or-refuse.** The census walks with
  `replace(_CURRENT_REPORT_WALK_CONFIG, profile="gameplay-census",
  missing_meeting_row="violation", reject_duplicate_meeting_rows=True, require_terminal_tick=True)`,
  threads engine-layer arms through the spine's engine-arguments helper and layer classification,
  declares its own `threaded_layers` in that `replace` (never inheriting `current-report`'s, which
  record plumbing declares), and raises on a recorded field it does not thread. The census also classifies every
  `RecordedExperimentConfig` field as read by a named cell predicate or deliberately not read.
  Enforced by a test enumerating `RecordedExperimentConfig.model_fields`. Planted: a classification
  with one field removed fails that test, and a carrier with an unknown recorded arm key raises.
  Mechanism: `CENSUS_THREADED_LAYERS` (orchestrator, tactical, meeting) set in the census's own
  `replace`; the walk's layer check before its first advance; the spine's `engine_arguments`,
  which every advance of `walk_replay` takes; and `FIELD_CLASSIFICATION` held equal to the
  model's fields both ways. Proved by
  `test_the_walk_profile_is_the_current_report_profile_plus_three_refusals`,
  `test_the_census_declares_its_own_layers_every_one_it_classifies`,
  `test_the_census_walk_reads_every_later_setting_it_declares` (a full-config copy of one
  committed game walks with every hash verified, and its era reads each recorded value),
  `test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing` (five settings),
  `test_the_census_walk_takes_its_engine_settings_from_the_spines_helper`,
  `test_a_recorded_setting_no_one_declared_is_refused_before_advancing` and
  `test_a_declared_setting_the_census_has_not_classified_is_refused`.
- [x] **The figures reproduce.** The committed JSON reproduces the Evidence table: 20/849, 73/587,
  313/512 with 251 from the exit room and 62 only from the room left, 330/355, 13/89, 26/56, 330
  meetings with vent proof and 346 without of 676, 326 vent-band impostor ejections (253 exit only,
  10 both, 63 entry only) and 43 without vent proof, 50 resting only on the room left, 167/551
  stale on the 9p2i pool, 335/676, 521/676, 0/676, 38/42, and 809 moves thrown away. Enforced by
  `--check` and by a test that reads each named figure from the committed JSON. Planted: `--check`
  is red on one edited cell and on a missing file. Each figure is re-measured at dispatch; a
  figure that moves is reported in Results with its cause, and never pinned to the memo's value.
- [x] **Body kill tick from the event.** Corpse age and staleness join each body to its victim's
  `KilledEvent` on the tick the body first appears. Enforced by the fold. Planted: a carrier whose
  body id encodes a tick different from the event tick reads the event tick.
- [x] **Thrown-away actions from the recorded dispositions.** The trigger-tick cell counts
  `discarded_by_meeting` dispositions by action type. Enforced by the fold. Planted: a move
  discarded on a game-ending trigger tick is counted (the 808 to 809 case).
- [x] **Exit witnesses.** Exits seen, seen from the exit room, and seen only from the room left
  read the recorded `source_witnesses` / `destination_witnesses`, crew only. Planted: an exit seen
  only from the room left counts as seen and as room-left-only, and moving that crewmate out of the
  room left at the pre-tick flips both.
- [x] **Stale reports.** A report meeting is stale when its trigger body was on the floor at the
  previous meeting's open. Planted: a stale corpse flips to fresh when its kill moves after the
  previous meeting's open.
- [x] **Vent band against vent proof.** Vent-proof meetings (a `vent_sighting` flag naming a living
  player) and the vent band (a flag naming the ejected player) are separate cells with separate
  denominators. Planted: moving the flag onto a living, non-ejected player takes that ejection out
  of the vent band while the meeting stays vent-proof.
- [x] **Impostor ballots.** Recorded SKIP, EJECT, EJECT labelled `supported`, recorded teammate
  targets, and authored teammate targets read from the typed guard fields. Planted: an authored
  teammate target is counted while the recorded target is SKIP.
- [x] **Era-keyed pooling.** Each game carries an era key: its normalized experiment config, its
  temporal-observation version, its substrate-flag stamp, and its prompt-stamp set taken only from
  MANIFEST rows that record a meeting. `pool` raises across eras, and the loader raises on a set
  whose games carry two eras. On baseline 9 the four sets are one era. Planted: pooling two
  carriers with different era keys raises; a set mixing two keys raises. Perturbed: a rule taking
  the stamp from every MANIFEST row splits `replays/samples/4p1i` on its 11 no-meeting rows and
  raises, while the ruled key reads one era.
- [x] **Conformance guards.** Each cell an arm makes zero by construction carries its arm
  predicate, read from the carrier's plain recorded values (a missing key means the historical
  default); the predicates never build a `RecordedExperimentConfig`, because this card merges while
  `WAVE_ARMS_PENDING` still refuses those values at config validation. With the predicate true the
  publisher asserts 0 and renders "0 by construction", naming the field and value; a non-zero count
  raises `GameplayCensusConformanceError` naming (set, seed, meeting). Planted, one pair per row
  below: a hand-built carrier with the arm ON and one violating fact raises, and the same fact with
  the arm OFF publishes 1 of N. Vacuity: with the arm ON and an empty denominator the cell renders
  `n/a`, never 0. The rows:

  | cell | predicate | s9 today (arm off) |
  |---|---|---|
  | exits seen only from the room left; vent-band ejections resting on them | `vent_witness_rule == "physical"` | 9/85; 8 |
  | entries not after the impostor's own fresh kill (own victim in that room, killed at most 3 ticks earlier, no meeting between) | `vent_entry_policy == "own_fresh_kill"` | 13/105 |
  | surfacings before the cap with a non-teammate in the inferred-visible set; trips longer than the cap | `vent_exit_policy == "look_and_wait"` | re-measured; n/a |
  | stale reports; play resumes with an impostor in a vent; play resumes with a corpse | `meeting_reset == "hub_with_grace"` | 43/135; 10/107; 60/107 |
  | kills in the grace window after a regroup; corpse age above the ticks since the last close | `meeting_reset == "hub_with_grace"` | n/a; n/a |
  | report openings carrying the kill-tick body id | `report_body_handle_version == 1` | 135/135 |
  | rebuttals differing from the selector's pick | `bounded_rebuttal_version == 1` | n/a |
  | a second repeat-speaker turn in one meeting (a second rebuttal) | always | 0 |
  | any repeat-speaker turn; an accused opener answering | `bounded_rebuttal_version` None | 0; 0/125 |
  | impostor openers | `self_report` False and `contextual_self_report_version` None | 0/145 |
  | recorded teammate ballot targets | always (the guard) | 0 |
  | own-kill rows naming a teammate or held by a non-witness | `ballot_kill_row_version == 1` | n/a |

  The two tick counts that define an arm value are named constants documented as that value's
  frozen meaning (decision 0.3 item 6): the fresh-kill window of 3 and the in-vent cap of 4 play
  ticks, restarted at a meeting boundary. The exit-policy card's end-to-end test is where its
  own constants are pinned equal to these; that is a note for that card, not this card's check.
- [x] **The own-kill extraction, built now against the specified row.** The loader finds served
  own-kill rows by the ballot card's specified row: kind `own_kill`, text `you watched them KILL in
  {room} at tick {tick}`, cited by the kill's observation id. The text is one named pattern
  constant in `eval/gameplay_census.py`; the ballot card pins its row text to that constant and
  never edits this file. The cited id joins the row to its `KilledEvent`: a row whose killer is the
  voter's teammate, or whose voter is not among that kill's witnesses, is a breach. Rows found are
  the cell's denominator, so a wording mismatch reads `n/a`, never 0. There is no unsupported-arm
  error: a recording with `ballot_kill_row_version` 1 loads like any other. Mechanism: the pattern
  constant and the fold. Planted: with the arm ON, a carrier holding one own-kill row cited by a
  teammate's kill raises, and so does one held by a voter who did not witness the kill; the same
  carriers with the arm OFF publish 1 of N; a loader unit test extracts the row from a synthetic
  prompt string in the specified wording and finds none in a different wording, printing nothing.
- [x] **The exit-policy predicate is the policy's own view.** A breach is a surfacing before the cap
  while a non-teammate stood, in the impostor's own observation at the pre-tick, in a room of the
  inferred-visible set: the own room plus its map neighbours, or the own room alone while any
  sabotage is active. It never tests the engine's visibility set. Planted: a surfacing during a
  reactor sabotage, with a crewmate in a neighbour that is truly visible, is not a breach; the
  same case with the crewmate in the own room is. The s9 value is re-measured on this definition
  and reported beside the memo's 31/85, with any difference attributed to exits under sabotage.
- [x] **The grace window is the map's.** The window after a regroup at meeting tick T is T+1 to
  T+`kill_cooldown_ticks`, read from the loaded map, never a literal. Enforced by the fold and a test
  pinning the window length to the map. Planted: a kill at T+4 after a regroup is a breach; a kill
  at T+5 is outside the window and publishes as an ordinary post-meeting kill.
- [x] **The added cells** (decision memo 2.6) are computed and each has a planted carrier. Exit
  behaviour: forced (cap) exits; ticks inside per trip; in-place surfacings where a crewmate enters
  or shares the corpse room before the impostor walks out; kills within 2 ticks of a surfacing.
  Regroup: trips closed by a regroup (an entry with no exit event); kill-witness button calls within
  6 ticks of a regroup; trigger-tick move and task events a regroup discards; sabotage active at a
  regroup. Rebuttal: claim structure (alibi, whereabouts, sighting, redirect only); rebuttal
  accusations against players who already spoke; beneficiary kind with the accuser's role; opener
  rebuttals answering the charged tick. Ballots: ejections carried only by impostor ballots, with the
  floor read from the tally's own parameter. Also reported: meetings per game, SKIP at report
  meetings, the win split and role-correct ejections. On baseline 9 each arm-dependent cell renders
  `n/a`, and its planted carrier fills it.
- [x] **Publisher.** `scripts/publish_gameplay_census.py` writes both files through
  `preflight_report_output` / `atomic_write_report`, with every `replays/**` path, the recording
  directories and the census's own inputs protected by containment; `--check` exits 1 on drift and
  names the regenerate command; `--set-dir DIR --json-stdout` folds one directory, prints JSON and
  writes nothing, and exits non-zero on a conformance breach. Enforced by
  `tests/scripts/test_publish_gameplay_census.py`, calling `check_report` as the scorecard's test
  does. Planted: a destination inside `replays/` is refused before anything is computed; a
  `--set-dir` run over a planted copy leaves the tree's file list unchanged.
- [x] **Copy.** The page opens by saying it is not the scorecard, that role-correctness is reported
  and gates nothing, and by defining each term it uses (vent band, era, regroup, opener, trigger
  tick, by construction). No cell is named by a memo number, a wave letter, a task or audit id, or
  threshold arithmetic; keys and titles are descriptive. Enforced by a test scanning the rendered
  page for those id shapes. Planted: a title carrying a memo-style id fails it.
- [x] **Registry.** `docs/artifacts.md` gains one class-(b) row, in git, sized "2 files", beside the
  scorecard's (`:111`); `_IN_TREE_PROBES` (`:2754`) and `_IN_TREE_INVENTORY` (`:2816`) in
  `scripts/verify_ml_evidence.py` gain matching entries. Enforced by the offline
  `verify_ml_evidence.py` run. Planted: the row without its probe entry fails it.
- [x] **The meeting-structure counts reach the direction.** On merge, one dated sentence is
  appended to the 2026-09-24 addendum of `tasks/direction-2026-09-19-process-over-outcome.md`: the
  first reply accuses the opener in 521 of 676 meetings, the opener speaks a second time in 0 of
  676, and `uv run python scripts/publish_gameplay_census.py --check` recomputes both. Enforced by
  the figures test above, which pins both counts in the committed JSON the sentence cites; the
  sentence is dated history and is not re-bound after an adoption. Perturbed: editing either count
  in the JSON reddens that test and `--check`. If the addendum is not on `main` yet, this card
  does not write it: it stops and asks.
- [x] **Nothing else moves.** The golden on s9 and s4, `verify_samples` on each of the four set
  directories, the four `build_sample_report --check` runs, `publish_process_scorecard --check`
  and the c9 refit pins including the campaign tier read as before, and `git diff` from the merge
  base shows no path under `replays/`, `api/`, `frontend/`, `agents/`, `meetings/`, `engine/`,
  `orchestrator/` or `observation/`. Enforced by those gates and the scope check in Validation.
  Perturbed: the scope check run against a scratch commit touching `api/` prints that path; each
  gate keeps its own planted failure in its suite, and this card removes none.

## Constraints

**Wave and order.** Wave 0, parallel with `docs-truth-typed-trigger` (A3); starts now, on `main` at
`e886b663` or later. It merges after `stage-b-arm-spine`, and before every arm card
(`vent-witness-physical`, then the B1, B4, B2 and B6 cards), before `stage-b-record-plumbing`
(which merges after readers and this card), and before `stage-b-readers`, which writes
`tests/_helpers/committed.py` after this card. It consumes the spine's `FIELD_LAYER`, its
engine-arguments helper and the eight declared fields, so it cannot pass its classification test
until the spine has merged; it waits for the spine rather than stubbing them. Each arm card then
adds one end-to-end test in its own test file: a fake or scripted arm-ON recording reads 0 on its
cell, and a perturbed copy raises. The record card's STOP rules rely on both halves.

**One writer per file (decision memo 3.2).** `eval/gameplay_census.py`,
`tests/eval/test_gameplay_census.py`, the new script, its test and the two `docs/gameplay-census.*`
files are this card's alone. Shared, in order: `tests/_helpers/committed.py` (A3 writes the trigger
kind at `:382-392`, then this card writes only a new census cache region, then readers, then record
plumbing, then B2, all serial); `docs/artifacts.md` (this card's census row first, then, in merge
order, readers, record plumbing, look-and-wait, the meeting reset and the record card, each writing
only its own row); `scripts/verify_ml_evidence.py` (this card's probe and inventory entry, then
record plumbing); the direction file (the orchestrator's `docs:`
addendum commit lands first, then this card's one appended sentence). The 3.2 map says this card
"rebases on A3": under the wave rules that means merging `main` into the branch after A3 merges,
never a rebase. This card writes no line of `eval/replay_walk.py` (the spine, then B2, own it), so
the census profile is documented in `eval/gameplay_census.py`, not in that file's drift table.

**The partial-record principle, where it binds.** Only `replays/samples/9p2i` is ever re-recorded,
and only into a candidate directory under `replays/candidates/`, by the record card, never here.
Every Stage-B switch is a `RecordedExperimentConfig` field, default-OFF and omitted from the payload
at its default; the census reads a missing key as the historical default. Every committed
recording, derived view, fixture, gate and doc fact keeps verifying byte-identically. No registry
prompt version moves. `docs/gameplay-census.*` stays on baseline 9 until an adopting decision; a
candidate's columns come from `--set-dir` into the record's audit, never into these files.

**Measurement discipline.** Fake and replay providers only; no live provider call, no recorder
run, no `.env` read, no held-out band (2100-2999 stays unseen), no seed-band prefix printed. The
census is count-only: the loader reads a recorded prompt only to compute a boolean or an id
inside itself, and no prompt, speech or rationale text leaves it or reaches any output, log or
test message. Role-correctness is reported and never a gate; roles are read for reported cells and
structural guards only and feed nothing back to any agent. No instrument pushes an agent toward
the correct answer, and the census changes nothing the meeting layer does: the meeting layer
labels and never rewrites. No scorecard cell and no D1 amendment (R13). No ML consumer (ruling 12).

**Delivery.** Branch `work/gameplay-census`; one pull request into `main`, with every section of
`.github/pull_request_template.md` filled: Summary, Definition of done, Decisions and Questions,
the body ending with the Claude Code attribution line. Merge or fast-forward, never squash; never
amend a pushed commit; take `main` by merging it in, never by rebasing. Every commit body ends
`Card: tasks/work/gameplay-census.md` immediately followed by the exact line
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever
model the worker session runs). No agent posts PR comments. The merge is the owner's.

**Status and the task index.** `tasks/README.md` is the orchestrator's: its inventory sentence is
derived from every card's `**Status:**`, so the worker fills Results and leaves the Status line to
the orchestrator, who flips it with the sentence in one commit.

**Stop and ask.** A figure that does not reproduce at dispatch is reported with its cause, not
tuned. A breach on baseline-9 bytes of a guard whose predicate is already true today (the
always-on guards and the arm-OFF guards) stops the card.

**The own-kill extraction is ruled.** The orchestrator ruled it before dispatch: this card builds
the extraction now against the ballot card's specified row (the acceptance item above), with no
unsupported-arm error, and the ballot card pins its row text to this card's constant and never
edits `eval/gameplay_census.py`. No writer exception exists.

## Expected scope

New: `eval/gameplay_census.py`, `scripts/publish_gameplay_census.py`, `docs/gameplay-census.md`,
`docs/gameplay-census.json`, `tests/eval/test_gameplay_census.py`,
`tests/scripts/test_publish_gameplay_census.py`. Edited: `tests/_helpers/committed.py` (one cached
census walk, the single-home rule at `:1-30`); `docs/artifacts.md` (one row);
`scripts/verify_ml_evidence.py` (one probe and one inventory entry);
`tasks/direction-2026-09-19-process-over-outcome.md` (one appended sentence); this card's Results.
Permitted follow-through, declared in Results: if the single-home pin must name the census loader
in `WALKERS`, one line in `tests/_helpers/test_committed_single_home.py` (the 3.2 map gives that file
to no other card; the orchestrator confirms at dispatch).

Not in scope: `eval/replay_walk.py`, `eval/process_scorecard.py`,
`scripts/publish_process_scorecard.py`, `docs/process-scorecard.*`, `docs/glossary.md` (the page
defines its own terms; a term that needs a glossary entry goes to the orchestrator for the
glossary's writer order), `orchestrator/experiment_config.py`, every file under `engine/`,
`agents/`, `meetings/`, `observation/`, `orchestrator/`, `api/`, `frontend/`, `llm/`, `training/`,
`experiments/` and `replays/`, every prompt template, and `tasks/README.md`.

## Record impact

Nothing recorded moves: no recording, MANIFEST, report gz, fixture, prompt byte, weight or DTO. No
experiment turns ON and no adopting record is created. Two new committed files are the change,
class (b) in `docs/artifacts.md` by the same reasoning as the scorecard's row: a regenerated view
whose bytes a gate pins is a record. Their numbers describe baseline 9 and stay there through the
wave; the round-1 candidate is read only through `--set-dir`, which writes nothing.

Publication: a push to `main` republishes the demo bundle (`.github/workflows/pages.yml`). This card
touches no path the bundle reads (nothing under `api/`, `frontend/`, `replays/samples/` or the
featured list, and not `scripts/build_demo_bundle.py`), so the republished bundle is byte-identical;
the scope check in the last acceptance item is the proof, and Results quotes it.

Measurement: every cell is a count with a stated denominator, per set and within one era; rates are
never pooled across eras. Once an arm is recorded, its conformance cells read 0 by construction, and
the page says so instead of presenting a measured improvement.

## Validation

- `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q`
- `uv run python scripts/publish_gameplay_census.py --check`
- `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout`
  (compared with the committed s9 section; `git status --porcelain` empty afterwards)
- `uv run python scripts/publish_process_scorecard.py --check`
- `bash scripts/verify_samples.sh replays/samples/9p2i`, then the same for `replays/samples/4p1i`,
  `replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i`, once per set directory
- `uv run python scripts/build_sample_report.py --sample-dir <set> --check` for each of the four sets
- `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` (the golden on s9 and s4)
- `uv run python scripts/check_doc_facts.py` and `uv run python scripts/validate_task_docs.py`
- `uv run python scripts/verify_ml_evidence.py` offline, never `--complete`, with
  `uv run pytest tests/scripts/test_verify_ml_evidence.py -q`
- `uv run lint-imports` and `uv run mypy .`
- `uv run pytest -m campaign` (the c9 refit pins' campaign half; `pyproject.toml:91` excludes it by
  default)
- `bash scripts/check.sh` whole, in a clean worktree, with its real exit code reported
- `git diff --stat $(git merge-base origin/main HEAD) -- replays api frontend agents meetings engine
  orchestrator observation scripts/build_demo_bundle.py` empty
- No frontend e2e: this card touches neither `api/` nor `frontend/`; the frontend unit tests run
  inside `check.sh`.

## Results

### 2026-09-25: implementation, measured at the branch head

**State: active, one acceptance item open.** Every item is met except the spine half of **Walk
profile and thread-or-refuse**. The census walks with the ruled `replace` of the current-report
profile, classifies every `RecordedExperimentConfig` field, and raises on a carrier or recording
naming a setting it has not classified. Not done: threading engine-layer arms through the spine's
engine-arguments helper and `FIELD_LAYER`, declaring the census's own `threaded_layers` in that
`replace`, and refusing a recorded field the walk does not thread. `stage-b-arm-spine` has not merged
(it is `ready` on `main` at `13f2c4d3`), and Constraints say this card waits for it rather than
stubbing it. The card therefore stays `active`, and the pull request is open for review. When the
spine lands, `main` is merged in and three things finish the item: the `threaded_layers` declaration,
the refusal test, and the equality form of the classification test (see Decisions, item 3).
Review round 3 finished all three after the spine merged (Review corrections, round 3).

**References.** `docs/architecture.md` on layering: `eval/` is an offline reader over the engine and
the orchestrator, `agents/` is untouched, and the four import-linter contracts are kept. It also
covers determinism: the census walk re-simulates every game and verifies tick hashes, dispositions,
meeting post-hashes and chronology. The design follows decision memo sections 0.3 (items 6 and 9),
0.4, 2.6, 3.2, and the 3.4 brief for this card. It also follows census memo section 4
(`tasks/investigations-2026-09-24/census_and_record.md`).

**What landed.**
- `eval/gameplay_census.py`: the impure `load_census_inputs`, the pure `fold_set` over a frozen
  carrier, `pool`, the setting predicates, `FIELD_CLASSIFICATION`, era keys, and the published models.
- `scripts/publish_gameplay_census.py`: publish, `--check`, and `--set-dir DIR --json-stdout`.
- `docs/gameplay-census.md` and `.json`: 67 cells and 8 tables, each per set and pooled.
- Tests: `tests/eval/test_gameplay_census.py` and `tests/scripts/test_publish_gameplay_census.py`.
- `tests/_helpers/committed.py`, census cache region: `census_inputs` and `census_walk_events`.
- `docs/artifacts.md`: the census row.
- `scripts/verify_ml_evidence.py`: one probe entry and one inventory entry.
- `tasks/direction-2026-09-19-process-over-outcome.md`: one appended sentence.

**Every figure, re-measured at the head through the production path.** The source is
`uv run python scripts/publish_gameplay_census.py --check` (consistent) and the committed JSON it
pins. The table below is read from that JSON, count-only. All reproduce the Evidence table and its
before values. No figure moved.

| cell | s9 | 9p2i pool | four-set pool |
|---|---|---|---|
| `kills_seen_by_crew` | 3/175 | 19/725 | 20/849 |
| `vent_entries_seen_by_crew` | 19/105 | 64/501 | 73/587 |
| `vent_exits_seen_by_crew` | 62/85 | 271/435 | 313/512 |
| `vent_exits_seen_from_exit_room` | 53/85 | 226/435 | 251/512 |
| `vent_exits_seen_only_from_room_left` | 9/85 | 45/435 | 62/512 |
| `impostors_seen_venting_ejected` | 70/77 | 284/304 | 330/355 |
| `impostors_vented_unseen_ejected` | 3/8 | 13/56 | 13/89 |
| `impostors_never_vented_ejected` | 8/15 | 25/40 | 26/56 |
| `meetings_with_vent_proof` | 70/145 | 285/594 | 330/676 |
| `vent_band_impostor_ejections` | 70/81 | 281/322 | 326/369 |
| `impostor_ejections_without_vent_proof` | 11/81 | 41/322 | 43/369 |
| `vent_band_resting_only_on_room_left` | 8/70 | 37/281 | 50/326 |
| `stale_report_meetings` | 43/135 | 167/551 | 167/623 |
| `meetings_opening_with_another_unreported_corpse` | 74/145 | 325/594 | 335/676 |
| `first_reply_accuses_opener` | 120/145 | 448/594 | 521/676 |
| `opener_speaks_again` | 0/145 | 0/594 | 0/676 |
| `openers_among_innocent_ejections` | 7/9 | 37/41 | 38/42 |
| `vent_entries_not_after_own_fresh_kill` | 13/105 | 101/501 | 103/587 |
| `surfacings_before_cap_in_view` | 52/85 | 264/435 | 299/512 |
| `vent_exits_into_visibly_occupied_room` | 31/85 | 122/435 | 134/512 |
| `trips_longer_than_cap` | n/a | n/a | n/a |
| `play_resumes_with_impostor_in_vent` | 10/107 | 30/452 | 30/486 |
| `play_resumes_with_corpse` | 60/107 | 263/452 | 263/486 |
| `post_meeting_kills_soon_after` | 28/87 | 129/363 | 135/389 |
| `meetings_opening_with_impostor_in_vent` | 29/145 | 92/594 | 101/676 |
| `report_openings_with_kill_tick_handle` | 135/135 | 551/551 | 623/623 |
| `opener_accused_after_opening` | 125/145 | 487/594 | 561/676 |
| `impostor_openers` | 0/145 (0 by construction) | 0/594 (0 by construction) | 0/676 (0 by construction) |
| `impostor_skip_ballots` | 164/210 | 694/861 | 760/943 |
| `impostor_eject_ballots` | 46/210 | 167/861 | 183/943 |
| `impostor_ejects_labelled_supported` | 44/46 | 164/167 | 178/183 |
| `recorded_teammate_ballot_targets` | 0/210 (0 by construction) | 0/861 (0 by construction) | 0/943 (0 by construction) |
| `authored_teammate_ballot_targets` | 1/210 | 13/861 | 13/943 |
| `ejections_carried_only_by_impostor_ballots` | 0/90 | 0/363 | 0/411 |
| `crew_witnessed_kills_held_at_next_meeting` | 3/3 | 19/19 | 20/20 |
| `held_kill_witnesses_voting_killer` | 3/3 | 18/19 | 19/20 |
| `held_kill_killers_ejected` | 2/3 | 12/19 | 12/20 |
| `role_correct_ejections` | 81/90 | 322/363 | 369/411 |
| `impostor_wins` | 11/50 | 56/200 | 88/300 |
| `vent_band_by_moment` | both 2, entry only 17, exit only 51 | both 10, entry only 54, exit only 217 | both 10, entry only 63, exit only 253 |
| `innocent_opener_ejections_by_trigger` | report 7 | emergency 1, report 36 | emergency 1, report 37 |
| `meetings_by_trigger` | emergency 10, report 135 | emergency 43, report 551 | emergency 53, report 623 |
| moves thrown away on trigger ticks | 188 | 754 | 809 |

Also reproduced from the Evidence text:
- Impostor ballots on s9: 210, of which 164 SKIP, 46 EJECT and 44 labelled `supported`.
- Ejections: 411 pooled, 369 of impostors and 42 of crewmates.
- The entry gate removes 13 of 105 entries on s9 and 103 of 587 pooled.
- Report openings carrying the kill-tick handle: 135 of 135 on s9, 623 of 623 pooled.
- Crew kill witnesses held, voting the killer, and seeing the killer ejected: 3/3/2 on s9, 20/19/12
  pooled.
- Floor met only by impostor ballots: 0 of 411.

The 809 thrown-away moves include `samples/4p1i` seed 3's game-ending trigger tick
(`test_the_loader_reads_the_game_ending_trigger_tick_of_samples_4p1i_seed_3`).

**The exit-policy predicate on s9: 52/85, beside the memo's 31/85.** The two count different
things, and the difference is fully attributed:
- The ruled predicate counts a surfacing before the cap while a non-teammate stood in any
  inferred-visible room: the vent's own room or a neighbour.
- The memo's 31/85 counts exits whose destination room was visible and occupied.
- The census publishes that destination-restricted count on the inferred-visible definition too
  ("Vent exits into a room the impostor could see a crewmate in"). It reads 31/85 on s9 and 134/512
  pooled, equal to the memo's engine-sight figures.
- Inferred and engine sight can differ only under a sabotage, so no s9 exit is attributable to
  exits under sabotage.
- The other 21 exits had a crewmate in a visible neighbour other than the destination.
- "Trips longer than the cap" reads `n/a` on every set: all 512 exits have 1 tick inside once the
  count restarts at a meeting boundary. The memo's 19 two-tick trips all span a meeting.

**Decisions.**
1. The own-kill pattern constant is `eval.gameplay_census.OWN_KILL_ROW_TEXT`
   (`"you watched them KILL in {room} at tick {tick}"`). Rows are found by the ballot template's
   evidence-row line around that text. The row joins to its kill through the cited observation id:
   agent-frame tick minus `AGENT_CLOCK_OFFSET`, with the killer equal to the row's subject. At this
   head a row citing nothing was not evaluable; review round 1 made it a breach (Review
   corrections, round 1).
2. `WALKERS` in `tests/_helpers/test_committed_single_home.py` gains `load_census_inputs`, the
   permitted line. The same file's docstring "six committed-set walks" becomes "seven" so the
   sentence stays true. `test_a_census_walk_outside_the_shared_cache_is_flagged` plants the case.
3. Five fields are read before the spine declares them: `vent_witness_rule`, `vent_entry_policy`,
   `report_body_handle_version`, `ballot_kill_row_version` and `impostor_ballot_version`. Their
   historical defaults sit in `_UNDECLARED_DEFAULTS`, and every other default is read from the model.
   `test_the_names_read_before_the_spine_declares_them` pins the five as exactly the difference, so
   the spine's merge turns it red and forces the retirement. This is not a stub of any spine symbol.
   (Retired in review round 3, after the spine merged; see Review corrections, round 3.)
4. The kill-tick handle pattern is a census constant pinned equal to
   `experiments.held_out_prefixes.LEGACY_BODY_HANDLE_PATTERN` by a test. `eval/` does not import the
   held-out generator.
5. A regroup is a loader-computed carrier boolean: the recorded reset is `hub_with_grace` and play
   resumed. The grace window reads `kill_cooldown_ticks` from the loaded map.
6. "Corpse age above the ticks since the last close" is published as "Reported corpses older than
   the last regroup": the victim was killed on or before the previous meeting's tick. This avoids an
   off-by-one where a kill on the trigger tick itself would read "not above".
7. Publisher protection is the recording root (containment) plus every file under it (file identity
   for a hard link). Every census input lives under that root. The neuter pass showed separate
   set-directory and input entries were redundant, so they were dropped.
8. The MANIFEST prompt cell is read by the census itself: the third cell in every table width. A
   test pins it equal to `_manifest_writer.parse_manifest` on all four sets. A game with a meeting
   whose cell names no stamp raises.
9. The loader refuses any seed in 2100-2999 before opening it.
10. The selector-guard row has no publishing twin. At `bounded_rebuttal_version` 1 the selector guard
    raises; at the default the repeat-speaker guard raises instead. The two always-on guards have no
    OFF value. All three are pinned (`test_a_rebuttal_off_the_selector_raises_under_either_value`,
    `test_the_always_guards_raise_under_every_setting`).
11. A breach names the set and seed always. It names the meeting id for a meeting fact, and the
    tick for a play fact (a vent entry or exit, a trip, a kill). The acceptance text's "(set,
    seed, meeting)" is met at that strength, and the page, the error's docstring and the publisher
    say so.

**Follow-through outside Expected scope, declared.**
- `tests/scripts/test_verify_ml_evidence.py` links the census pair in its availability tree, two
  lines. Without them the new probed row reads missing in that scratch tree and fails
  `test_complete_accepts_a_manifestless_recorded_loss_end_to_end`.
- `tasks/README.md`'s derived inventory sentence is re-derived for this card's Status flip, as the
  dispatch instructed.

**Verification (all at the head).**

The table was measured at `d75ff36c`. `9800b718` changes only the text of the page's
"by construction" definition and the publisher's docstring. At `9800b718`, with this Results
section in place, the following were re-run:
- the two census suites: 146 passed;
- `--check`: consistent;
- `validate_task_docs.py`: exit 0;
- `bash scripts/check.sh`: exit 0, with the same counts as the table's last row.

Each exit code was captured directly, never through a pipe. The commits are `612bbeaa` (the
instrument, the publisher, the pages, the tests and the direction sentence), `d75ff36c` (the
registry), `9800b718` (the text fix) and this card commit.

| command | result |
|---|---|
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q` | 146 passed |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, both files consistent |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; the printed JSON equals the committed `samples/9p2i` section; `git status --porcelain` empty afterwards |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `bash scripts/verify_samples.sh <set>`, once for each of the four set directories | exit 0 each: 50, 50, 150 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, all four | exit 0 each, consistent |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | 25 passed |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: checks 62, OK 50, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 82 passed |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `uv run mypy .` | no issues in 498 source files |
| `uv run pytest -m campaign` | 336 passed |
| `bash scripts/check.sh` | exit 0: 8,453 Python passed, 20 skipped, 3 xfailed; 558 frontend tests passed |

No frontend e2e: this card touches neither `api/` nor `frontend/`.

**Planted and perturbed failures.** Each item's planted case is a named test:
- Shape: `test_a_carrier_holding_a_rationale_fails_the_shape_check`.
- Classification: `test_a_classification_missing_one_field_fails`.
- Unknown key: `test_an_unknown_recorded_setting_raises`.
- `--check`: `test_one_edited_cell_turns_check_red` and `test_a_missing_published_file_is_red`.
- Body tick: `test_corpse_age_reads_the_kill_event_tick_never_the_body_id`.
- 809: `test_a_move_discarded_on_a_game_ending_trigger_tick_is_counted`.
- Exit witnesses: `test_an_exit_seen_only_from_the_room_left_flips_when_the_crewmate_leaves`.
- Stale reports: `test_a_stale_corpse_flips_to_fresh_when_its_kill_moves_after_the_last_open`.
- Vent band: `test_moving_the_flag_leaves_the_band_but_keeps_the_proof`.
- Ballots: `test_an_authored_teammate_target_counts_while_the_recorded_target_skips`.
- Eras: `test_pooling_two_eras_raises`, `test_a_set_mixing_two_eras_raises`, and
  `test_the_ruled_prompt_stamp_reads_samples_4p1i_as_one_era`. The every-row rule splits
  `samples/4p1i` on its 11 no-meeting rows.
- Guards: 16 parametrized pairs in
  `test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off`, plus the vacuity test.
- Own-kill: `test_the_row_is_found_in_the_specified_wording_and_nowhere_else` and the two own-kill
  guard pairs.
- Reactor sabotage: `test_a_reactor_surfacing_with_crew_in_a_visible_neighbour_is_no_breach`.
- Grace window: `test_a_kill_at_the_first_legal_tick_is_an_ordinary_post_meeting_kill`.
- Writer: `test_the_writer_refuses_a_recording_destination_before_computing`, 12 cases.
- `--set-dir`: `test_set_dir_over_a_planted_copy_prints_json_and_writes_nothing`.
- Copy: `test_a_title_carrying_a_memo_style_id_fails_the_copy_scan`.

**Registry, planted.** Each perturbation ran the offline verifier, then the file was restored
from a copy (sha256 identical afterwards; the verifier read exit 0 again):
- row without its probe entry: exit 1, FAIL on registry coverage;
- row without its inventory entry: exit 2, the inventory refuses an unscoped row;
- probe without its row: exit 1;
- the row stating 3 files: exit 1, FAIL on the in-tree family inventory.

**Scope check** (the demo-bundle proof: no path the bundle reads moved).
`git diff --stat 13f2c4d3 -- replays api frontend agents meetings engine orchestrator observation
scripts/build_demo_bundle.py` printed nothing at the head. Perturbed: with one comment line
appended to `api/schemas.py` from a saved copy, it printed ` api/schemas.py | 2 ++`. After
restoring from the copy it printed nothing again.

**The mechanical neuter pass**, statement-level, over every production line of the census module
and the publisher, run with a scratch harness. The harness does not ship. It did not perturb the
sub-expressions inside a condition, and review round 1 found conditions it left unpinned; the
sub-expression pass in Review corrections, round 1 replaces this pass's coverage claim.
- Each mutation was generated from the AST: every `acc.count` hit set to `False`, every
  `acc.tally` and `acc.not_evaluable` call dropped, every cell guard set to `None`, every `raise`
  replaced by `pass`, and every carrier constructor argument set to a neutral value. To these were
  added hand-written perturbations of each constant, predicate value, default and publisher branch.
- For each one the harness ran both census test files with `-x`, recorded red or green, and
  restored the file from an in-memory copy taken before the pass, never from git.
- A sha256 check confirmed the files byte-identical afterwards.

| round | perturbed | red | green |
|---|---|---|---|
| 1, before the fixes below | 329 | 307 | 22 |
| 2 | 325 | 324 | 1 |
| 3, at `d75ff36c` | 324 | 324 | 0 |

The 22 probes that first came back green, and what closed each one:
- The `_field_default` refusal: `test_a_default_is_read_only_for_a_classified_field`.
- The opener-speaks-again hit: planted in
  `test_a_rebuttal_off_the_selector_raises_under_either_value`.
- The era's temporal version: `test_the_loader_reads_the_temporal_observation_version`.
- `Frame.in_vent`, `KillFact.victim` and `BodyFact.victim`: no cell read them, so they were deleted.
- `TurnFact.index` and `reply_to`: the turn-fact test now uses non-default values.
- `MeetingFact.meeting_id`, `sabotage_active` and `ballot_floor`, and `BallotFact.confidence` and
  `cited_observation_id`: `test_the_loader_copies_ids_the_floor_ballots_and_sabotage`.
- The regroup flag's play-resumed condition: a game-ending variant in
  `test_the_loader_reads_the_recorded_reset`.
- The publisher's path bootstrap and `raise SystemExit(main())`:
  `test_the_script_runs_from_any_directory_and_exits_with_mains_code`.
- The JSON-destination preflight: the refusal test now covers both destinations.
- The two `--check` messages: now asserted.
- The replay-file protection: `test_a_hard_link_to_a_recording_is_refused_by_file_identity`.
- The census-input and set-directory protection entries: redundant under the root's containment,
  so they were removed (Decisions, item 7).

Round 2's one green was `TurnFact.turn_kind`. No cell read it, so it was deleted before commit.

Five more perturbations outside the two files each went red, with each file restored:
- the `WALKERS` entry;
- the direction sentence;
- the census cache returning another set;
- the census walk events emptied;
- the availability tree without the census pair.

**Limitations.**
- The spine half of the walk-profile item is open (above). (Closed in review round 3.)
- Fifteen cells read `n/a` on baseline 9 because no committed recording carries a regroup,
  a rebuttal, a served own-kill row, an in-place surfacing or a trip that waited. Their meaning rests on planted carriers until an
  arm card's end-to-end test and the round-1 record fill them. (At this head. Review round 2
  moved two more cells and two tables to `n/a`; see Review corrections, round 2.)
- The census is count-only over recorded events and states. It cannot tell why a policy acted.
- The own-kill extraction depends on the ballot card rendering the row with the template's
  evidence-row line around `OWN_KILL_ROW_TEXT`. A different line format reads `n/a`, never 0.
- Nothing in this card joins the scorecard, gates a decision, or feeds any agent.

### Review corrections, round 1 (2026-09-25)

**State: still active.** Both review findings are repaired, and the two `Review correction`
items at the top of Acceptance record them. The walk-profile item stays open for the same reason
as before: `stage-b-arm-spine` has not merged (`origin/main` is still `13f2c4d3`), so there is no
`main` to merge in yet. The code, tests and pages are commit `f91aa8eb`; this subsection is the
card commit after it.

**Finding 1: an own-kill row naming a teammate and citing nothing was not a breach.** The join
returned "not evaluable" for a row with no citation before it compared the row's named killer
with the holder's teammates, so an uncited teammate row folded without raising. The row names its
killer, so no citation is needed to see the teammate. `_own_kill_row_breaches` now tests the
teammate first. A row citing nothing joins no kill, and the ballot card specifies that every row
cites its kill, so an uncited row is a breach too. Every served row is therefore in the
denominator, and the cell has no not-evaluable count. The cell's published definition says so.
That one definition is the only byte change in `docs/gameplay-census.*`; every committed figure is
unchanged.
- Planted: three new `GUARD_PAIRS` rows, each raising with `ballot_kill_row_version = 1` and
  publishing 1 of 1 with it off. They are a teammate row citing nothing, a witness row citing
  nothing, and a row naming someone other than the cited kill's killer.
- The round-0 order, rebuilt as a mutant (an uncited row let through before the teammate test),
  fails `test_a_breach_raises_with_the_setting_on_and_publishes_with_it_off` on its
  `_own_kill_row_of_teammate_citing_nothing` case.

**Finding 2: production conditions no test enforced.** Each condition the review listed now has
a planted case:
- the two regroup equalities (a kill on the regroup tick, a button press at the cooldown tick);
- a vent and a kill on the trigger tick;
- a dead room-left witness, and empty sightings under the physical rule;
- a row naming someone other than the cited killer, and the cited-by-holder join;
- a non-witness ballot for the killer;
- an alibi about another player, and an observation of someone other than the opener;
- both leg edges, and both edges of the unseen seed band.

A sub-expression mutation pass then found the rest. Each survivor was either planted or, where no
input could reach it, removed as dead code:
- The meeting carrier now couples its outcome and its ejected player, as `MeetingResult` does, and
  raises otherwise. Four re-checks of `outcome == "EJECTED"` in the fold are gone.
- The carrier's terminal tick is required. The census walk profile already refuses a game that
  never ends, and the loader raises if a walk yields none. The unreachable "open" trip kind is
  gone.
- `load_census_inputs(set_dir)` loses its `game_map` parameter, which no caller passed.
- Meeting rows no longer enter the era's entry list; the era helpers read only tick and game-over
  rows. The regroup flag is read from the game's era after the walk, not from the first tick row.
- `prompt_stamps_from_cell` loses an empty-list check that `str.split` can never meet.

**The sub-expression pass.** The method:
- A scratch harness, not shipped, generates each mutant from the AST of
  `eval/gameplay_census.py` and `scripts/publish_gameplay_census.py`. Each mutant replaces one
  node's exact source span with a re-rendered variant.
- The twelve operators:
  - swap each comparison operator in place (`<`/`<=`, `>`/`>=`, `==`/`!=`, `in`/`not in`,
    `is`/`is not`);
  - drop each operand of `and`/`or`, and swap the two;
  - drop each `not`, and flip each boolean literal;
  - move each integer literal by +1 and -1;
  - swap `any`/`all`, swap `+`/`-`, and keep one side of each `&`/`|`;
  - replace each conditional expression by either branch, and negate each `if`/`while` test;
  - replace each `raise`, `continue`, bare `return` and call statement by `pass`.

  Docstrings, annotations, f-strings and `__all__` are not mutated.
- Each mutant is compiled from the file's bytes and installed in `sys.modules` before pytest
  imports anything. The files are never written. Eight processes each run both census suites with
  `-x`, with a 300-second timeout.
- The sha256 of both source files, both test files and both pages was identical before and after
  every pass.
- The publisher's path bootstrap and its `raise SystemExit(main())` are seen only by the test
  that runs the script as a subprocess, so their eight mutants were also neutered on disk. The
  harness saved a copy of the file, wrote the mutant, ran both suites, restored the file from the
  copy (never from git) and checked the sha256.

| pass | state | mutants | caught | survived |
|---|---|---|---|---|
| 1 | finding 1 fixed, the review's list planted | 1,026 | 928 | 98 |
| 2 | survivors planted or removed | 997 | 961 | 36 |
| 3 | final, at `f91aa8eb` | 1,049 | 1,012 in memory, then 6 more on disk | 31 |

Pass 3's 1,049 mutants are 917 in the census module and 132 in the publisher. The 1,012 caught in
memory are:
- 998 failing tests;
- 11 modules that no longer import, because a class invariant, the module-level defaults table or
  the row pattern was turned against itself;
- 2 exits at import, where the `__main__` test is negated;
- 1 hang, where the in-place walk-out loop stops advancing.

Between passes 2 and 3, `&`/`|` operand drops and boolean flips were added to the operators. They
found four more reachable conditions, each now planted:
- the entry witness list the moment table reads;
- the pairing of dispositions with actions;
- the JSON's text bytes;
- the frozen record types, checked by a property over every dataclass and model in the module,
  with only the fold's own accumulator exempt.

Every expression the review listed is red in pass 3.

The 31 survivors, none observable by any input:
- `keys[1:]` in `resolve_era` read as `keys[0:]`: this only compares the first key with itself.
- The `player is not None` operand of `_is_impostor` and of `_vent_flag_names`: `roles.get(None)`
  is `None`, and no flag names `None`. Both operands only narrow the type.
- `entry_tick <= t` read as `<` in the ticks-inside anchor: a meeting on the entry tick adds the
  entry tick to the `max` either way.
- Five mutants of the same-tick order key in `_trips` (both constants, and the key reading the
  tick twice): vents are listed before meetings and the sort is stable, so the key only restates
  the list order.
- The `player != exit_fact.actor` operand of the in-view test: the surfacing impostor is inside
  the vent at the pre-tick, and a frame lists no one inside a vent
  (`test_the_frame_holds_living_players_outside_the_vents_and_live_sabotage`).
- The `trigger_body is None` operand of the corpse join: `None not in bodies` raises the same way.
- `first_charge + 1` read as `first_charge` in the accused-opener cell: the charging turn's
  speaker is never the opener.
- `repeats[0]` read as `repeats[-1]`: it differs only with two repeat-speaker turns, which the
  always-on guard refuses earlier in the same fold.
- `other.index < turn.index` read as `<=`: this adds the repeat speaker, who had already spoken.
- The `reply_to is not None` conditional read as `by_id.get(turn.reply_to)`: `get(None)` is
  `None`.
- The `spec.guard is not None` operand of `by_construction`: `holds` already requires a guard.
- `zip(tallies, inputs, strict=True)` without `strict`: the tallies are built one per input.
- Six constants of `_row_order`, and the same six in the publisher's table-row sort: they only
  order a numeric row against a text row, and every table's rows are all one or the other.
- The publisher's `sys.path.insert` at position 1 or at the end instead of 0: the root is still on
  the path, and nothing shadows it. On disk these two stay green; the other six bootstrap mutants
  are red on disk.

**Changed expectations.** No test was deleted, skipped or weakened. Two expectations changed:
- `test_the_rows_found_are_the_denominator_so_a_mismatch_reads_n_a`: an uncited row read (0, 0,
  1) under the setting. It now reads (1, 1, 0) with the setting off and raises with it on.
- `test_a_trip_is_closed_by_a_regroup_an_ejection_or_the_game_end`: the carrier without a
  terminal tick, whose open trip left the denominator, can no longer be built. It became a game
  without a recorded winner, whose trip closes at the game end.
  `test_the_loader_refuses_a_walk_that_never_ended` plants the refusal.

Test-only refactors keep their old behaviour at their defaults. `_planted_inputs` in the
publisher test gains `era`, `label` and `rows_without_dispositions` parameters, and the
charged-tick test's builder gains `charged`.

**Planted tests added.** The two census suites go from 146 tests to 185.
- Fold: `test_a_corpse_killed_on_the_regroup_tick_is_older_than_the_regroup`,
  `test_a_vent_on_the_trigger_tick_came_before_the_meeting`,
  `test_resting_on_the_room_left_needs_a_living_crew_sighting`,
  `test_a_kill_on_the_trigger_tick_is_held_by_that_meeting`,
  `test_only_a_living_witness_naming_the_killer_votes_the_killer`,
  `test_a_kill_witness_button_at_the_cooldown_tick_counts`,
  `test_an_alibi_about_another_player_is_no_alibi_of_the_rebuttal`,
  `test_an_impostors_teammates_exclude_the_impostor_itself`,
  `test_a_meeting_carrier_couples_the_outcome_and_the_ejected_player`,
  `test_a_new_trip_after_a_regroup_closes_the_old_one_first`,
  `test_an_entry_seen_through_either_witness_list_is_seen`,
  `test_a_kill_on_the_surfacing_tick_is_not_after_the_surfacing`,
  `test_a_crewmate_on_the_first_tick_after_an_in_place_surfacing_counts`,
  `test_only_an_undiscovered_corpse_other_than_the_reported_one_counts`,
  `test_a_button_soon_after_a_regroup_with_no_kill_since_is_no_witness_call`,
  `test_the_opener_accusing_themself_is_no_one_accusing_the_opener`,
  `test_rebuttal_claim_kinds_are_told_apart`,
  `test_the_charged_tick_cell_reads_opener_rebuttals_only`,
  `test_a_row_joins_the_one_kill_it_cites_among_several`,
  `test_the_impostor_only_floor_reads_only_confident_ballots_for_the_ejected`,
  `test_every_census_record_type_is_frozen` and `test_the_json_keeps_text_as_written`.
- Two existing tests gained cases. The charged-tick test gained an observation of another player,
  both leg edges and a leg past the tick. The own-kill join test gained three cited-by-holder
  mismatches.
- Loader: `test_the_frame_holds_living_players_outside_the_vents_and_live_sabotage`,
  `test_the_meeting_fact_reads_living_impostor_cooldowns_and_live_sabotage`,
  `test_an_unrewritten_ballot_was_authored_as_recorded`,
  `test_the_loader_refuses_a_meeting_applied_under_another_id`,
  `test_the_game_over_row_joins_the_era_and_names_the_winner`,
  `test_the_loader_refuses_dispositions_that_do_not_pair_with_the_actions`,
  `test_the_loader_refuses_a_walk_that_never_ended`,
  `test_the_loader_reads_a_recording_without_substrate_flags`,
  `test_the_manifest_reader_skips_prose_and_reads_a_three_cell_row`,
  `test_the_loader_refuses_both_edges_of_the_unseen_band` and
  `test_the_unseen_band_ends_at_its_edges`.
- Publisher: `test_a_not_evaluable_row_shows_when_any_group_has_one` and
  `test_the_era_lines_name_every_recorded_part_or_say_none`.

**Closing greps**, run at the card commit:
- `git grep -n -i -E "citing nothing|cites nothing|cite nothing|uncited" --
  eval/gameplay_census.py scripts/publish_gameplay_census.py docs/gameplay-census.md
  tasks/work/gameplay-census.md` prints only sentences stating the new rule, plus the dated
  Decision 1 above, which is now annotated.
- `git grep -n -F '"open"' -- eval/gameplay_census.py` prints nothing.
- `git grep -n game_map -- eval/gameplay_census.py` prints only `_load_game`'s parameter, its walk
  call, and the two places `load_census_inputs` passes the canonical map.
- `git grep -n -i -E "citing nothing|not evaluable" --
  tasks/work/ballot-kill-row-and-impostor-strategy.md tasks/work/stage-b-record-r1.md` prints
  nothing, so no other card describes the old own-kill rule.

**Verification, measured on the tree of `f91aa8eb` (`e144483a`).** Each exit code was captured directly, never through a
pipe. The card commit after it changes only this card.

| command | result |
|---|---|
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q` | 185 passed |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, both files consistent |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; the printed JSON equals the committed `samples/9p2i` section; `git status --porcelain` identical before and after |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `bash scripts/verify_samples.sh <set>`, once for each of the four set directories | exit 0 each: 50, 50, 150 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, all four | exit 0 each, consistent |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | 25 passed |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: checks 62, OK 50, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 82 passed |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `uv run mypy .` | no issues in 498 source files |
| `uv run pytest -m campaign -q` | 336 passed |
| `git diff --stat 13f2c4d3 -- replays api frontend agents meetings engine orchestrator observation scripts/build_demo_bundle.py` | prints nothing, so the demo bundle cannot move |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards |
| `bash scripts/check.sh` | exit 0 on the card commit's tree, before this cell was filled: 8,492 Python passed, 20 skipped, 3 xfailed; 558 frontend tests passed. A first run exited 127 because this fresh worktree had no `eslint`; after `npm --prefix frontend ci` it passed |

No `docs/artifacts.md` row moved: the census row states files, not bytes, and no `audits/` or
`tests/fixtures/` byte changed. No frontend e2e: nothing under `api/` or `frontend/` moved.

**Limitations of this round.**
- The pass claims only the twelve operators above. Swapping one name or field for another (for
  example one witness list for the other outside a `|`) is outside it.
- The harness is scratch and not shipped, as in the round-0 pass. Its counts reproduce only by
  re-running an equivalent harness over the same two files.
- The walk-profile item is still open until the spine merges (State, above).

### Review corrections, round 2 (2026-09-25)

**State: still active.** The one round-2 finding is repaired, and the `Review correction (round 2)`
item at the top of Acceptance records it. The walk-profile item stays open for the same reason as
before: `stage-b-arm-spine` has not merged (`origin/main` is still `13f2c4d3`), so there is no
`main` to merge in. The code, tests and pages are commit `64b9ef28`; the card commit after it adds
this subsection.

**Finding: two arm-dependent added cells published a measured 0 on baseline 9.** "Vent trips
ended by a regroup" read 0 of 587 and "Surfacings at the cap" 0 of 512 in every column, while the
sibling regroup cells read `n/a`. Both cells counted every vent trip or exit in every era, but a
trip can only end by a regroup, and an exit can only be forced by the cap, under a setting no
committed recording carries.

**Repair.**
- `CellSpec` and `TableSpec` gain `scope`: the setting predicate the counted thing exists under.
  The fold's accumulator counts a cell, or tallies a table, only while its scope holds for the
  group's recorded settings. Out of scope it counts nothing, so the denominator stays empty and
  the cell reads `n/a`. Every game in a set shares the set's era (the fold refuses a set that does
  not), so this is the per-game rule the finding asked for.
- `trips_closed_by_regroup` is scoped to `meeting_reset = hub_with_grace`, and `forced_surfacings`
  to `vent_exit_policy = look_and_wait`.
- The finding offered two rules for the cap cell. The recorded exit policy was chosen, not "trips
  that reached the cap": under look-and-wait every trip that reaches the cap surfaces at it, so
  that denominator would read 100% by construction and say nothing.
- The same defect sat in two added tables the finding did not name: the trigger-tick events a
  regroup drops, and who received a rebuttal. On baseline 9 both printed `(none)` with a 0 in
  every column, which reads as a measured count. They are scoped to
  `meeting_reset = hub_with_grace` and `bounded_rebuttal_version = 1`, and the page prints `n/a`
  for a table out of its scope.
- Each published cell and table carries `scope` (the predicate's description, or null) and
  `in_scope`. The models refuse an entry with no scope marked out of scope, and an out-of-scope
  entry that counts anything.
- The page copy follows:
  - the `n/a` term names both causes;
  - the paragraph under the terms says a cell or table counted only with some setting reads
    `n/a` without it;
  - each scoped definition ends "Counted only in games recorded with `X`; in any other era it
    reads n/a.";
  - the settings heading reads "Recorded settings a count depends on", because those settings now
    decide whether a count exists as well as whether it is zero.
- `SCHEMA_VERSION` stays 1. The JSON gains two keys per cell and table, but it has never been
  published on `main`, so version 1 is still its first publication.

**Which cells are arm-dependent, at the head.** On the pooled column 17 of 67 cells read `n/a`
(15 before this round), and so do the two scoped tables.
- Scoped, so `n/a` in every era without their setting: the two cells and two tables above.
- `n/a` because their denominator is made only by a setting's mechanism, with no scope:
  - the four other regroup cells (grace-window kills, reported corpses older than the last
    regroup, kill-witness button calls, sabotage at a regroup);
  - the seven rebuttal cells;
  - the two own-kill row cells.

  The loader marks a regroup only under the recorded reset, and at the historical default any
  rebuttal raises the repeat-speaker guard, so those denominators are empty in every other era.
  No committed recording serves an own-kill row. The guarded cells among these must publish 1 of
  N with their setting off under the Conformance guards item, so a scope would break that item.
- `n/a` from the data, and measured as before values rather than arm-dependent: trips longer than
  the cap (no trip stays inside more than one tick) and in-place surfacings (no exit returns to
  the room it left).
- Every other added cell is measured on baseline 9. That includes kills soon after the killer
  surfaced (11 of 849), which counts kills after any exit.

**A question for the orchestrator, not blocking.** Two tables pre-register "s9 before" values of 0
for "forced exits" and "trips closed by a regroup": the decision memo's section 4 table
(`tasks/decision-2026-09-24-stage-b-wave.md`, the B1 exit and B2 rows) and the assessment table in
`tasks/work/stage-b-record-r1.md`. The census now publishes `n/a` for both on s9. Both rows are
"reported", so nothing gates on them, and neither file is this card's to edit. The orchestrator
either restates those two before values as `n/a`, or rules they are real baseline zeros; in that
case this correction is reverted and the ticked item is restated at that strength. The PR's
Questions carry it.

**Planted tests added.** The two census suites go from 185 tests to 197.
- `test_where_no_meeting_regroups_no_trip_is_ended_by_a_regroup`: under the historical reset the
  cell reads `n/a`. That includes a carrier whose meeting is marked regrouped, so the `n/a` comes
  from the recorded reset.
- `test_without_the_look_and_wait_exit_no_surfacing_is_at_a_cap`, for the default exit policy and
  `observed_risk`: the same four-tick trip reads `n/a`.
- `test_where_no_meeting_regroups_the_dropped_events_table_reads_n_a` and
  `test_the_rebuttal_beneficiaries_table_is_counted_only_with_the_rebuttal_on`.
- `test_the_scoped_cells_and_tables_are_exactly_these`: pins the four scope rows.
- `test_every_cell_and_table_counts_exactly_when_its_scope_holds`: a Hypothesis property over
  every cell and table and a generated family of settings. Its expectation restates the rule
  without the module's helper.
- `test_every_setting_a_guard_or_scope_reads_has_its_meaning_on_the_page`: the page's setting
  meanings name exactly the fields a guard or scope reads. Planted: a meanings map missing
  `meeting_reset`, and one with an extra field, each fail it.
- `test_a_published_cell_or_table_out_of_its_scope_counts_nothing`: the model checks, each
  operand planted.
- `test_on_baseline_9_every_scoped_cell_and_table_reads_n_a`: reads every section of the committed
  JSON, and the page.
- Publisher: `test_a_table_out_of_its_scope_reads_n_a_and_in_scope_reads_its_count` and
  `test_the_definitions_name_the_setting_a_scoped_count_needs`.

**Changed expectations.** No test was deleted, skipped or weakened.
- `test_a_trip_is_closed_by_a_regroup_an_ejection_or_the_game_end`:
  - The preserve-reset trip that read (0, 1, 0) now reads (0, 0, 0), which
    `test_where_no_meeting_regroups_no_trip_is_ended_by_a_regroup` asserts.
  - The regroup, ejection, game-end and unrecorded-winner cases moved into a `hub_with_grace`
    carrier with their old expectations.
  - The ejection case now also marks its meeting regrouped, so it proves an ejection wins over a
    regroup.
  - The game-end case no longer holds a meeting. The preserve carrier with its meeting keeps the
    `trips_longer_than_cap` (0, 1, 0) assertion.
- `test_the_regroup_cells_read_regroups_only`: the dropped-events assertion reads a
  `hub_with_grace` carrier holding only the regroup meeting. The test's main carrier holds a kill
  inside the grace window, which that era refuses. The `kept` carrier moved into the regroup era,
  so its empty table belongs to a meeting that did not regroup rather than to an out-of-scope table.
- `test_a_new_trip_after_a_regroup_closes_the_old_one_first`: the carrier moved into the regroup
  era, with the same (1, 2, 0).
- Test-only: the `CensusCell` field dicts in
  `test_a_published_cell_cannot_carry_a_nonzero_count_by_construction` and in the publisher test's
  `rendered()` gain `scope=None` and `in_scope=True`, their values for an unscoped cell.

**The neuter pass over this round's diff.** A scratch harness (not shipped) applied 47
hand-written mutants one at a time on disk.
- Each mutant replaced one exact span of `eval/gameplay_census.py` or
  `scripts/publish_gameplay_census.py`.
- It then ran both census suites with `-x` and restored the file from a copy taken before the
  pass, never from git.
- The sha256 of both files matched before and after the pass.
- All 47 were red on their first run; no probe came back green.

| group | perturbed | red | green |
|---|---|---|---|
| the scope helper: each operand dropped, `is None` swapped, `or` to `and`, always true, the predicate negated | 6 | 6 | 0 |
| the four scope rows: each removed, and two re-pointed to another predicate | 6 | 6 | 0 |
| the accumulator's two scope checks: dropped, negated, `return` to `pass`, reading the guard | 7 | 7 | 0 |
| the cell model's two checks: each to `pass`, each operand dropped, `is None` swapped | 8 | 8 | 0 |
| the table model's two checks | 7 | 7 | 0 |
| the published `scope` and `in_scope`, for cells and tables | 4 | 4 | 0 |
| the `n/a` term reverted | 1 | 1 | 0 |
| the publisher: the empty-table value both ways, the scope sentence's guard and body, both definition joins, the paragraph, the heading | 8 | 8 | 0 |
| total | 47 | 47 | 0 |

The round-1 sub-expression pass (1,049 mutants) was measured at `f91aa8eb` and is not re-run here.
This pass covers only this round's diff.

**Closing greps**, run at the head. The first two exclude this card, which quotes them:
- `git grep -n -i "empty denominator: nothing of that kind" -- . ':!tasks/work/gameplay-census.md'`
  prints nothing (the old `n/a` term).
- `git grep -n -i "zero depends on" -- . ':!tasks/work/gameplay-census.md'` prints nothing (the old
  heading).
- `git grep -n -F "| (none) | 0" -- docs/gameplay-census.md` prints nothing.
- `git grep -n -w -E "0/587|0/512" -- docs/gameplay-census.md docs/gameplay-census.json` prints
  nothing.
- The pattern `trips (closed|ended) by (a )?regroup|surfacings? at the cap|forced (cap )?(exits|surfacings)`,
  run as `git grep -n -i -E` over the tree without `docs/gameplay-census.json` and `tests/`,
  prints, besides the cells' own titles and definitions and this card:
  - the decision memo's list of the added cells (`:525`), and the two pre-registered before
    values in the question above (the memo's `:1178` and `:1181`, and `stage-b-record-r1.md:149`
    and `:152`);
  - `tasks/work/meeting-reset-coherence.md`, which expects a count and not `n/a` on trips closed
    by a regroup with the reset on (still true);
  - planning text in `tasks/investigations-2026-09-24/` and `tasks/work/vent-look-and-wait.md`
    that projects forced exits under the arm.

**Verification, measured on the tree of `64b9ef28`.** Each exit code was captured directly, never
through a pipe. One module-docstring sentence was reworded and folded into that commit before it
was pushed. The census suites, `--check` and `check.sh` ran after that edit. The other rows, and
the neuter pass, ran just before it; the edit changes no code and no page byte.

| command | result |
|---|---|
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q` | 197 passed |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, both files consistent |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; the printed JSON equals the committed `samples/9p2i` section, where both scoped cells read 0 of 0 with `in_scope` false; `git status --porcelain` identical before and after |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `bash scripts/verify_samples.sh <set>`, once for each of the four set directories | exit 0 each: 50, 50, 150 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, all four | exit 0 each, consistent |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | 25 passed |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: checks 62, OK 50, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 82 passed |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `uv run mypy .` | no issues in 498 source files |
| `uv run pytest -m campaign -q` | 336 passed |
| `git diff --stat 13f2c4d3 -- replays api frontend agents meetings engine orchestrator observation scripts/build_demo_bundle.py` | prints nothing, so the demo bundle cannot move |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards |
| `bash scripts/check.sh` | exit 0, with this subsection in place before this cell was filled: 8,504 Python passed, 20 skipped, 3 xfailed; 558 frontend tests passed |

No `docs/artifacts.md` row moved: the census row states files, not bytes, and no `audits/` or
`tests/fixtures/` byte changed. No frontend e2e: nothing under `api/` or `frontend/` moved.

**Limitations of this round.**
- The neuter pass is hand-written over this round's diff, not the twelve-operator pass of round
  1, and its harness is scratch.
- The two pre-registered before values above wait for the orchestrator.
- The walk-profile item is still open until the spine merges (State, above).

### Review corrections, round 3 (2026-09-25)

**State: done.** The three round-3 findings are repaired, and the three `Review correction (round
3)` items at the top of Acceptance record them. The arm spine merged into `main` (`8df69e15`), so
the walk-profile item is finished and ticked, and no box is left open. The Status line flips to
`done` in this pass on the dispatch's instruction. `tasks/README.md`'s inventory sentence is
re-derived with `scripts/validate_task_docs.py`: 88 cards, 9 ready, 79 done.

**References.** The walk follows the arm spine's contract as `docs/experiment-arms.md` states it
(the eight fields, what a missing key means, the one engine-arguments helper and a profile's
`threaded_layers`), under decision memo sections 0.3 (items 2, 6 and 9) and 3.4 (this card's
brief). `docs/architecture.md`'s layering is unchanged: `eval/` reads the orchestrator's config
module and never touches `agents/`, and the four import-linter contracts are kept.

**Merging `main`.** `b5772553` merges `origin/main` at `52a6ac58` into the branch, never a rebase.
That brings docs-truth-typed-trigger (#482), the arm spine (#484), and the commit that states the
house trailer in eight other cards. The one conflict was `tasks/README.md`'s derived sentence,
re-derived for this card still active (9 ready, 1 active, 78 done). `tests/_helpers/committed.py`
merged without conflict; A3's trigger-kind region and this card's census cache region are both
kept. From here the diff base is `52a6ac58`: `git diff 52a6ac58 <head>` shows only this card's
work.

**Finding 1: the grace window and the ballot floor read their sources, but no test pinned it.**
Every committed map and meeting holds the value a literal would, so a literal passed every test.
Each source now moves in a planted case, and the output follows:
- The fold: a carrier walked on a map whose kill cooldown is 6. A kill at T+6 after a regroup
  raises, one at T+7 counts as outside the window, and the published `grace_window_ticks` reads 6
  (`test_the_grace_window_follows_the_kill_cooldown_the_carrier_holds`).
- The loader: its map loader is stubbed to hand out a map whose cooldown is 6. The carrier's
  cooldown follows it, the map is loaded once, and every game walks on it
  (`test_the_loader_reads_the_kill_cooldown_from_the_map_it_loads`).
- The ballot floor: one meeting's recorded `skip_confidence_threshold` is moved to 0.75, and
  `ballot_floor` reads 0.75. With nothing recorded it reads the tally's historical 0.6
  (`test_the_ballot_floor_is_the_threshold_the_meeting_recorded`).

The same lesson applies to every other constant the module binds from a source, and each is
planted the same way:
- `test_the_constants_bound_from_a_source_follow_it` executes the module's source a second time,
  under its own name, after moving each source. The button cooldown follows the crew policy's,
  the two set lists follow the scorecard's, the defaults table follows the config model's
  declaration, and the walk profile follows the current-report profile it is a `replace` of.
  The imported module is untouched.
- `test_the_own_kill_join_reads_the_scorecards_clock_offset` moves the agent clock offset, and the
  citation that joins a kill moves with it.

**Finding 2: the spine has declared the fields the census read ahead of it.**
- `_UNDECLARED_DEFAULTS` and `test_the_names_read_before_the_spine_declares_them` are deleted
  (craft rule 3). Each leaves one history line: the docstring of `_field_default`, and a comment
  above the classification tests.
- `_field_default` reads every default from `RecordedExperimentConfig`'s own declaration. It
  raises on a name the census has not classified, and on a classified name the config does not
  declare.
- The classification test is now its equality form: the recorded fields and `FIELD_CLASSIFICATION`
  name the same set, both ways. The planted cases are a classification missing `meeting_reset`
  and one naming an undeclared `hidden_travel`.
- The census reads arm values as before. The loader dumps the recorded config, where the spine's
  serializer omits each Stage-B field at its default, and a missing key reads the declared default.
  No predicate builds a `RecordedExperimentConfig`.
- The walk profile declares its own `threaded_layers` in its `replace`: `CENSUS_THREADED_LAYERS`
  is orchestrator, tactical and meeting. That is every layer a profile can declare, because the
  census classifies every field in them. The declaration is the census's own, so record plumbing's
  change to the current-report profile's layers cannot reach it.
- Engine-layer settings reach each advance through the spine's `engine_arguments`, inside
  `walk_replay`. The census walks nothing else.

The walk-profile proofs (Acceptance names each test):
- **A full-config copy is read.** One committed game (`samples/4p1i` seed 5) is copied with every
  tick row and its footer recording each Stage-B setting outside the engine layer at its ON value.
  The settings are derived from the spine's own `wave_settings`, not listed by hand. The pending
  set is patched open. The census walk verifies every hash, the facts equal the committed game's,
  and the era reads each recorded value.
- **A missing layer refuses.** The census profile with one layer taken out refuses that layer's
  setting before its first advance, naming the field, the value and `'gameplay-census'`. The walk
  yields no event. This runs once for each of the five settings.
- **Engine settings come from the helper.** A copy recording `redistribution_policy =
  least_remaining_work` walks, and its era reads the value. With the helper patched to thread no
  engine field, the same copy is refused before any event.
- **Unknown settings are refused.** A recorded key the config does not declare is refused before
  any event. A stand-in field added to the config model, which the census never classified, raises
  `GameplayCensusFieldError`.
- **End to end.** With `report_body_handle_version = 1` recorded, the committed opening that
  carries the kill-tick handle raises the body-handle guard, naming set, seed and meeting.
  Without that setting the same game folds.

Decisions made while repairing it:
1. The full-config recording is a copy of a committed game, not of a fake-provider recording as
   the spine card suggests for its profile owners. The committed game's prompts carry the real
   kill-tick handle, so a recorded setting can be carried to its guard end to end, and the copy
   reuses the cached loader facts it is compared with.
2. `vent_witness_rule = physical` is not stamped, and no census test depends on which arms are
   still pending. The helper refuses `physical` until the physical-witness card threads it, and
   the arm cards cannot edit this file. The engine proof patches the helper instead. The pending
   set is opened with `raising=False`, so the tests keep working once the ballot card deletes
   `WAVE_ARMS_PENDING`.
3. The census declares the meeting layer although it deliberately reads no predicate from
   `impostor_ballot_version`. Its counts read the recorded ballots, and the tally does not enforce
   that setting, so the classification's reason holds under either value.

**Finding 3: the Delivery sentence.** It now names the exact house line,
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`, in the wording `52a6ac58` gave the
eight other open cards. This pass's commits end with it: `b5772553`, `3283181f`, `420e95f8` and
the card commit after them. Earlier commits are pushed and are never rewritten:
- `612bbeaa`, `d75ff36c`, `9800b718` and `727baa84` carry
  `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`;
- `f91aa8eb`, `a0403021`, `64b9ef28` and `ea1e3aa1` carry
  `Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>`.

**The neuter pass.** A scratch harness (not shipped) applied each mutant on disk as one exact span
of `eval/gameplay_census.py`. It ran both census suites with `-x`, then restored the file from a
copy taken before the pass, never from git. The sha256 of the module and its test file matched
before and after every pass.

"Before" means the pre-round module and tests at the merged head `b5772553`, with only the retired
tripwire deselected. "After" means `420e95f8`: the module of `3283181f` and the final tests. The
before column is the finding's evidence reproduced: the verifiers' three probes and nine more of
the same kind were all green.

| probe | before | after | the test that turns red |
|---|---|---|---|
| the fold's window as the literal 4 | green | red | `test_the_grace_window_follows_the_kill_cooldown_the_carrier_holds` |
| the published window from `_constants(4)` | green | red | the same |
| the constants table's window as 4 | green | red | the same |
| `ballot_floor=0.6` | green | red | `test_the_ballot_floor_is_the_threshold_the_meeting_recorded` |
| the loader's cooldown as 4 | green | red | `test_the_loader_reads_the_kill_cooldown_from_the_map_it_loads` |
| each game walked on a second map load | green | red, second run | the same |
| the button cooldown as 6 | green | red | `test_the_constants_bound_from_a_source_follow_it` |
| the set list as a literal | green | red | the same |
| the nine-player list as a literal | green | red | the same |
| the defaults table as a literal | green | red | the same |
| the clock offset as 1 | green | red | `test_the_own_kill_join_reads_the_scorecards_clock_offset` |
| the walk profile as a literal `ReplayWalkConfig` with the same flags | green | red | `test_the_constants_bound_from_a_source_follow_it` |

This round's production lines:

| probe | after | the test that turns red |
|---|---|---|
| the classification check dropped, or its raise made `pass` (2) | red | `test_a_default_is_read_only_for_a_classified_field` |
| the declaration check negated | red | the module does not import (8 collection errors) |
| the declaration raise made `pass` | red | `test_a_classified_field_the_config_does_not_declare_has_no_default` |
| one default read from a literal | red | `test_a_default_follows_the_config_models_declaration` |
| one of the three layers dropped (3) | red | `test_the_census_declares_its_own_layers_every_one_it_classifies` |
| `threaded_layers` left out of the `replace`, inherited, or empty (3) | red | `test_the_walk_profile_is_the_current_report_profile_plus_three_refusals` |
| the `ConfigLayer` import dropped | red | `uv run mypy` (the name is an annotation only) |

Totals: 12 probes red after and green before, and 12 more over this round's lines, all red. Two
probes first came back green on the after side:
- Each game walked on a second map load. The stub handed out the same planted map on every call.
  The test now also requires that the map is loaded once, and the second run is red.
- The walk-profile probe was added after the first pass, when a scan of the module's constants
  bound from an imported name found the profile beside the three already planted. Its first run
  was green, and `420e95f8` extends the re-execution test to move the current-report profile. The
  final pass is red.

`__all__`'s new entry is not mutated, as in rounds 1 and 2.

**Changed expectations.** No test was skipped or weakened. The one deletion is the tripwire,
retired as the finding directs.
- `unclassified` becomes `classification_problems`, which reports both directions.
  `test_a_classification_missing_one_field_fails` now expects `"unclassified meeting_reset"`
  instead of `"meeting_reset"`: the same planted case, in the new message shape.
- The walk-profile test gains `threaded_layers` in its `replace`, and asserts the three
  verification flags the full-config proof relies on.

**Tests added.** The two census suites go from 197 tests to 216. The twenty new tests are:
- `test_the_census_declares_its_own_layers_every_one_it_classifies`;
- `test_a_classification_naming_an_undeclared_field_fails`;
- `test_a_default_follows_the_config_models_declaration`;
- `test_a_classified_field_the_config_does_not_declare_has_no_default`;
- `test_the_grace_window_follows_the_kill_cooldown_the_carrier_holds`;
- `test_the_loader_reads_the_kill_cooldown_from_the_map_it_loads`;
- `test_the_constants_bound_from_a_source_follow_it`;
- `test_the_own_kill_join_reads_the_scorecards_clock_offset`;
- `test_the_ballot_floor_is_the_threshold_the_meeting_recorded`;
- `test_the_later_settings_cover_every_layer_the_census_declares`;
- `test_the_census_walk_reads_every_later_setting_it_declares`;
- `test_the_recorded_body_handle_setting_reaches_its_guard`;
- `test_a_census_walk_without_a_layer_refuses_its_setting_before_advancing`, five cases;
- `test_the_census_walk_takes_its_engine_settings_from_the_spines_helper`;
- `test_a_recorded_setting_no_one_declared_is_refused_before_advancing`;
- `test_a_declared_setting_the_census_has_not_classified_is_refused`.

**Every figure, re-measured at the merged head.** On the merged tree,
`uv run python scripts/publish_gameplay_census.py --check` recomputes both pages from the
recordings and reads consistent. No page byte moved in this round.
- A count-only scratch script re-read the implementation table from `docs/gameplay-census.json`.
  All 42 rows match in all three columns, 0 mismatches. Moves thrown away still read 188, 754
  and 809.
- So every Evidence figure and before value quoted above still holds. That includes 20/849,
  73/587, 313/512 (251 and 62), 330/355, 13/89, 26/56, 330/676 with 326/369 and 43/369,
  253+10+63, 50/326, 167/551, 335/676, 521/676, 0/676, 38/42, 52/85 beside 31/85, and 0 of 411.
- The pooled column has 67 cells, 17 of them `n/a`. It has 8 tables, 2 of them out of scope on
  baseline 9.
- The constants read: grace window 4, button cooldown 6, fresh-kill window 3, in-vent cap 4,
  short window 2.

**Verification.** Each exit code was captured directly, never through a pipe. Every row except the
first and the last three was measured at `3283181f`. `420e95f8` changes one test, so the census
suites were re-run on it; `check.sh` re-runs mypy, ruff and the whole default tier. The card
commit after it changes only this card and `tasks/README.md`.

| command | result |
|---|---|
| `uv run pytest tests/eval/test_gameplay_census.py tests/scripts/test_publish_gameplay_census.py -q` | 216 passed |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, both files consistent |
| `uv run python scripts/publish_gameplay_census.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; the printed JSON equals the committed `samples/9p2i` section; `git status --porcelain` empty before and after |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `bash scripts/verify_samples.sh <set>`, once for each of the four set directories | exit 0 each: 50, 50, 150 and 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, all four | exit 0 each, consistent |
| `uv run pytest tests/meetings/test_prompt_byte_golden.py -q` | 25 passed |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: checks 62, OK 50, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 82 passed |
| `uv run lint-imports` | 4 contracts kept, 0 broken |
| `uv run mypy .` | no issues in 501 source files |
| `uv run pytest -m campaign -q` | 336 passed |
| `uv run python scripts/check_doc_facts.py` | exit 0, on the card commit's tree |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards, on the card commit's tree |
| `bash scripts/check.sh` | exit 0 on the card commit's tree at `420e95f8` with this subsection in place, before this cell was filled: 8,730 Python passed, 20 skipped, 3 xfailed; 559 frontend tests passed. `npm ci` in `frontend/` ran first in this fresh worktree |

**Scope check** (the demo-bundle proof).
`git diff --stat 52a6ac58 -- replays api frontend agents meetings engine orchestrator observation
scripts/build_demo_bundle.py` prints nothing at the head, so no path the bundle reads moved and the
republished bundle is byte-identical. `git diff --stat 52a6ac58` names only this card's 14 files:
the census module, the publisher, the two pages, the three test files,
`tests/_helpers/committed.py`, `tests/_helpers/test_committed_single_home.py`,
`docs/artifacts.md`, `scripts/verify_ml_evidence.py`, the direction file, `tasks/README.md` and
this card.

No `docs/artifacts.md` row moved: the census row states files, not bytes, and no `audits/` or
`tests/fixtures/` byte changed. No frontend e2e: nothing under `api/` or `frontend/` moved.

**Closing greps**, run at the card commit. Each one excludes this card, which quotes the old names
as history:
- `git grep -n -E "_UNDECLARED_DEFAULTS|names_read_before_the_spine|[^_]unclassified\("`
  prints nothing.
- `git grep -n -i -E "before the (arm )?spine declares|read here before"` prints nothing.
- `git grep -n -F "attribution line the worker's own session supplies"` prints only the two merged
  cards whose wording `52a6ac58` deliberately kept (`docs-truth-typed-trigger`,
  `stage-b-arm-spine`).

**Limitations of this round.**
- The neuter pass covers this round's production lines and the constants the module binds from a
  source. It is hand-written, and its harness is scratch.
- The full-config proof stamps every Stage-B setting outside the engine layer. The physical
  witness rule is refused by the spine's helper until its arm card threads it, and that card's
  own end-to-end test is where a census walk first reads it.
- The shipped profile declares every layer a profile can declare. So a refusal in the shipped
  census comes from the engine helper, from the config model's refusal of an undeclared key, or
  from the census's classification. The layer refusal is proved on a copy of the profile with one
  layer taken out.
- The re-execution test shows each module-level binding follows its source when the module is
  executed, which is when those bindings are made.
- The round-2 question on the two pre-registered before values still waits for the orchestrator
  (the PR's Questions).
