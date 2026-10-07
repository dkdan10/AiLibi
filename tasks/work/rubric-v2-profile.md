# The game-shape profile: rubric version 2

**Status:** ready

## Outcome

On 2026-10-06 the owner answered the rubric design memo, verbatim: "Profile as recommended, decisive, and ship the
shelf". Rubric version 1 (R1-R7, the weighted geomean, the scalar railroad floor, `rubric_score.py --set-dir`) is
retired for the `stage-b-r2` era and kept as baseline-9 lab history. The shown set (`replays/samples/9p2i`, round 2,
recorded under `replays/samples/9p2i/experiment-config.json`) has shipped no rubric since 2026-10-02: the Highlights
reel and the dashboard histogram show their empty states, and the refresh script skips the step by name.

This card contracts rubric version 2, the role-blind per-game game-shape profile of the memo's Part 2. When it is done:
- `eval/game_profile.py` computes, from committed bytes through the census carrier, each game's facets (a timeline of
  physical moments), the named shelves it sits on (fixed shelf order, games in seed order) and two tripwires. There is
  no score, no rank, no total and no zeroing floor.
- `scripts/publish_game_profile.py` writes `replays/samples/9p2i/results-game-profile.json` beside the recordings,
  stamped with its era, MANIFEST key and source fingerprint, with each candidate shelf's leak and saturation class
  recorded, plus the generated page `docs/game-profile.md`; `--check` pins both. The refresh script's rubric step runs
  it. `4p1i` ships no profile, by design.
- The API serves `/eval/game-profile` (view model version 6) in place of `/eval/rubric`. The Highlights tab opens on
  "Browse by moment": pre-reveal shelves in fixed order, games in seed order, facets per game; every reveal-only shelf
  and facet behind the existing reveal toggle; "wrong on what it held" always beside its "right" twin, in plain words,
  as the game working; a tripped game on no shelf, labelled, still under All games. No score, rank or histogram.
- Version 1's served path and viewer surfaces are deleted under craft rule 3; its lab text and results stay as history.

The held card `tasks/work/rubric-extractor-era.md`: its rubric half closes here without the widening, which version 2
does not need. The held card, amended to the optional extractor half, stays ready, and is dispatched, deferred or closed
as superseded only on the owner's D14 word (decision memo 8.6).

## Evidence

Every `path:line` is a citation at `76270d6c`, labelled by symbol and re-anchored by that symbol at dispatch; the code,
the recordings and the docs it cites are byte-identical at `2275bdba`, where only task documents moved (section 8 of
the decision memo, the direction addendum and the four round-3 cards). Counts are count-only, keyed by (set, meeting),
and re-measured at dispatch through the production path; the dispatch figure governs. No rendered prompt, transcript
text or seed-band prefix was printed.

**The ruling and its design.** The memo is
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/rubric-design-2026-10-06/rubric-design-memo.md`;
Part 2 is this contract's design (principles P1-P7, tripwires 2.2, shelves and facets 2.3, the two rules 2.4, record
impact 2.9, publication 2.10). The ruling takes its Part 4: the profile (item 1), the decisive quantifier (item 2), the
wrong-on-what-it-held shelf shipped locally beside its twin (item 3), leaking shelves behind the reveal (item 4) and the
routing (item 5). The baselines memo (`.../baselines-2026-10-03/baselines-memo.md`, Part 2.3 W13-W33, Part 3.4 items
6-10, D6/D7) gives the case: v1 zeroes 16 of 50 shown games, and 16 of the 17 crew ejections behind them rest on
ballots all labelled `supported`. The round-3 cards (`tasks/work/route-lines-field.md`, `census-held-data-cells.md`,
`stage-b-record-r3.md`, `crew-idle-policy-lab.md`, committed at `2275bdba`) and the orchestrator's one-writer map give
the order; `stage-b-record-r3` keeps the rubric cards undispatched until it merges (its "Wave, order and ownership").

**The shown set's reading.** From the repository root at `76270d6c`, and again at `2275bdba` with the same output,
`.venv/bin/python <memo dir>/rubric-v2-repro.py replays/samples/9p2i` (count-only, about 6 s) prints:
- Tripwires: T1 every 0; decisive (removed) 1, seed 26 meeting index 2; read as SKIP 1 and all ungrounded removed 1,
  the same meeting; any 2, seeds 26 (mi 2) and 41 (mi 0). T2 0, of 15 alibi-class flags (scorecard row 3 reads
  1/15 with 14 not evaluable, `docs/process-scorecard.md:113`). Ejecting ballots: 282 `supported`, 2 `off_target`.
  Of all 410 EJECT ballots, 0 carry `none_held` (407 `supported`, 3 `off_target`); 214 of the 281 SKIP ballots do
  (a count-only scratch tally of `load_census_inputs` labels by target, not a line the script prints).
- Endings: 13 `CREWMATE_EJECT`, 13 `CREWMATE_TASKS`, 24 `IMPOSTOR_PARITY`; 46 games eject someone.
- Pre-reveal shelves (seed 26 excluded): the reporter saw it happen 14 (0, 1, 7, 9, 16, 19, 23, 28, 29, 30, 32, 35,
  38, 43); double kill 7 (1, 3, 4, 8, 21, 24, 32); slow burn 11; two kills after one regroup 6 (0, 4, 12, 13, 16, 36);
  a close call 16; suspicion moved 16; a third round 19. Each passes the leak rule, whose 2x2 tables span all 50 games
  with seed 26 counted as a non-member of every shelf (`rubric-v2-repro.py:243-255`): the smallest p is 0.0655, two
  kills after one regroup against any ejection (members 4 with an ejection and 2 without; non-members 42 and 2).
- The leak rule moves caught venting (12 of its 19 games are ejection wins, p < 0.001) and one line, two readings
  (2 task wins of 20, p = 0.0498, on the boundary) behind the reveal. Saturation makes struck after the regroup (40 of
  50; leak p 0.0766) a facet: 70 of 109 post-regroup kills land in the wave. A scratch recomputation from the script's
  JSON output with seed 26 dropped from the tables reads two kills after one regroup 0.0681, one line two readings
  0.0473 and struck after the regroup 0.0256 (a leak that saturation hides): the universe is part of the rule.
- The eyewitness chip, a meeting chip and not a shelf (memo 2.3, "An eyewitness voted on it"): a kill witness's ballot
  cites its own kill row (`rubric-v2-repro.py:146-149`). From the script's JSON output, it marks 15 meetings in the
  same 14 games as the reporter shelf (seed 9 at meeting index 2 where the reporter shelf has 1; seed 38 at 0 and 1),
  seed 19 at meeting index 2, seed 14 none.
- Reveal shelves: caught venting 19, one line two readings 20, one-vote ejection 10, nobody voted out 4 (4, 15, 31,
  36), down to the wire 12, runaway 14, decided at a meeting 14; decided without proof, right 18 games (19 ejections),
  wrong on what it held 20 games (21 ejections).
- Pre-reveal shelves per game: 0:12, 1:11, 2:11, 3:7, 4:6, 5:1, 6:1; after the reveal every eligible game sits on one
  or more. Seed 19: reporter, slow burn, third round; after the reveal also caught venting, one line two readings,
  decided at a meeting, right. Seed 14: none; after the reveal runaway, right.
- Not served: mean pre-reveal shelves per game 1.92 (ejection wins), 1.96 (parity), 1.46 (task wins), n = 49, from the
  script's JSON output.
On a `git archive d41c9006 replays/samples/9p2i` export with its retired served file deleted first, T1 and T2 read 0 and
decided without proof reads right 11 games, wrong 9: history, never served. `uv run python
scripts/publish_gameplay_census.py --check` exits 0 at `76270d6c` (about 5 s).

**The carrier** (`eval/gameplay_census.py`, owned by `census-held-data-cells`). `load_census_inputs` (`:3488`);
`tally_outcome` (`:2708`); `grounding_labels` (`:2673`); `KillFact` (`:658`: tick, killer, room, witnesses, no victim);
`BodyFact` (`:679`: opaque body id, kill tick); `OwnKillRowFact` (`:752`: holder, subject, room, tick, citation id;
the subject is the killer the row names); `MeetingFact` (`:763`, with the role reads `in_vent_at_open` and
`impostor_cooldowns_at_open`); `GameFacts` (`:836`: roles, winner, terminal tick; no end reason, no task bar);
`CensusInputs.kill_cooldown_ticks` (`:855`). `_load_game` (`:3263`) already reads each kill's `KilledEvent.target` and
each body's `player_id`. Row 3: `ALIBI_FLAG_KINDS`, `load_set_inputs`, `_self_alibi_truths`, `_flag_is_manufactured`
(`eval/process_scorecard.py:220`, `:903`, `:1116`, `:1131`); the two helpers read a meeting's transcript and the route
only, but `load_set_inputs` returns `GameReport`s that carry `roles`, `winner` and `reason` (`eval/report_schema.py:269`,
`:353`; roles seeded at `eval/process_scorecard.py:914-923`). The meeting layer labels an uncited, unnulled ballot
whose basis is `none_held` as `none_held` whatever its target (`meetings/manager.py:4712-4713`), and no `VoteBallot`
validator ties that basis to SKIP (`meetings/schemas.py:1074`, `:1161`).

**What retires, and its consumers.**
- Producer: `regen_for_set` and `main`'s `--set-dir` branch (`experiments/lab/rubric_score.py:1337`, `:1381`, `:1478`).
  `_set_manifest_sha` (`:1309`) stays: the frozen parity pin imports it (`tests/eval/test_watchability.py:130-168`).
- Served path: `_RUBRIC_FILENAME`, `ReplayLoader.rubric` (`api/replay_loader.py:256`, `:1262`); the route
  (`api/routes/eval.py:228`); `RubricGameView`, `RubricView` (`api/schemas.py:1706`, `:1730`); `VIEW_MODEL_VERSION`
  "5" (`:76`); `_trimmed_rubric` (`scripts/build_demo_bundle.py:291`, `:404-412`); `scripts/gen_frontend_types.py:68`.
- Viewer: `ScoreBadge`, `SubScoreBar` (`HighlightCard.tsx:109`, `:181`, `:270`, `:280`); the reel order and filters
  (`ReplayPicker.tsx:180-245`; `:190` reads `ejected_impostors` under a role-blind label); the score buckets
  (`ReplayFilters.tsx:57-64`); `InterestingnessHistogram` (`TournamentDashboard.tsx:863`, `:911`); the tour fallback
  (`GuidedTour.tsx:65-80`); `RUBRIC_SPOKES` and the interestingness strings (`copy.ts:140`, `:368-385`, `:499`);
  `getRubric` (`client.ts:374`).
- Live-tense text that goes false: the skip clause and its dry-run line (`scripts/refresh_samples.sh:1134-1138`,
  `:585-589`); the `--experiment-config` help (`:68-77`) and the comment above `declared_args` (`:304-312`), which say
  a switched-on config records only outside the committed sets while `scripts/_declared_experiment.py` states the era
  rule; the no-rubric comments (`client.ts:366-372`, `ReplayPicker.tsx:19-21`, `TournamentDashboard.tsx:128-132`,
  `:885-887`, `HighlightCard.tsx:17-19`, `api/replay_loader.py:1269-1270`, `:3961`, `api/routes/eval.py:230-236`,
  `api/schemas.py:1734`); `docs/deployment.md:125`; the lab run line (`report-rubric-interestingness.md:65-68`).
- Absence pins: `tests/api/test_sets.py:328-336`, `:454-468`; `tests/api/test_view_model.py:1368-1551`;
  `tests/scripts/test_build_demo_bundle.py:308-388`; `tests/scripts/test_refresh_samples.py:1259-1265`, `:2239-2245`;
  the stale controls of `tests/scripts/test_public_recording_provenance.py`; `frontend/e2e/evidence-journey.ts:58-68`.

**The bundle today.** `build_demo_bundle.bake_data` at `76270d6c` writes 71 JSON files (1,979,606 bytes) for 9p2i seeds
19 and 14 and 4p1i seeds 2, 11 and 29, with no rubric file; the five replay views carry `viewModelVersion`. The bundle
dashboard renders its "No tournament report" card (`TournamentDashboard.tsx:1115-1148`), so no panel there is public.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that turns its test red; each new test is
seen red before the code it guards exists.

- [x] Review correction: CI's Project checks failed at `53b9ffd3` because item 17's planted case read `76270d6c`'s
  scorer with `git show`, which the shallow `actions/checkout` cannot answer. The case now rebuilds that scorer in
  `tmp_path` from today's module and the deleted served-file write the test carries as text
  (`_RETIRED_SERVED_FILE_WRITE` in `tests/api/test_sets.py`), so it reads no history; the rebuilt scorer still writes
  the file and still fails the check (`test_the_scorer_before_the_retirement_wrote_one_and_fails_the_check`), and its
  code is AST-identical to `76270d6c`'s with docstrings stripped. Proved on a `git archive` export of the head with
  no `.git` directory and in CI's shallow checkout, run 37624561446 (Results, round 1).
- [x] Review correction: T1's "ejects someone else" clause is pinned. Removing two ungrounded ballots hands the tally
  from `p-3` to `p-6`; decisive, read-as-SKIP and every-ungrounded-removed each trip
  (`test_a_removal_that_hands_the_tally_to_another_player_trips_decisive`), and the two `is None` mutants are red.
- [x] Review correction: the saturation count reads untripped games only, as the catalogue does. A 50-game era
  where 37 untripped games and 1 tripped game carry a double kill is a shelf of 37, and no game carries it as a
  moment (`test_a_tripped_member_does_not_saturate_a_candidate`); dropping the trip filter is red.
- [x] Review correction: a self-accusation keeps no suspicion on a player. The player who drew ballots only accuses
  themselves at the next meeting and suspicion moved holds (`test_a_self_accusation_keeps_no_suspicion_on_a_player`);
  dropping the speaker filter is red.
- [x] Review correction: the two loaded-source reads are pinned. A planted ending the recorded types gain leads the
  leak rows (`test_the_leak_facts_follow_the_recorded_endings`), and an eighth grounding label stops
  `read_pre_reveal` and `build_profile` (`test_an_eighth_grounding_label_stops_the_reading_and_the_profile`); each
  literal swap is red.
- [x] Review correction: the seven named raise-site arguments are pinned by full-message matches with values off
  every default: seed 9 and 1 against 2 meetings (`test_the_projection_refuses_a_mismatched_scorecard`), seed 6, tick
  5 and `body-p-1-5` (`test_a_kill_or_a_body_with_no_victim_raises`), and the set path
  (`test_a_set_with_no_roster_names_no_seedset`); each constant argument is red.
- [x] Review correction: item 1 and Results state the mypy plant at its strength. `BlindMeeting` holds no report, so
  strict mypy refuses `meeting.report.roles`; a T2 handed a `GameReport` as a parameter passes mypy and is caught by
  item 2's role property (`test_a_t2_reading_the_report_roles_fails_the_role_property`).
- [x] Review correction: the item 17 planted case is neither skipped nor weakened. It runs on every checkout and keeps
  both readings: today's scorer refuses `--set-dir` and writes nothing, the rebuilt pre-retirement scorer writes the
  file and fails the same check.
- [x] Review correction: the five location arguments are pinned. The copy's path in
  `test_the_stamp_is_read_before_and_after_the_walk`, `tmp_path` in `test_a_set_with_no_roster_names_no_seedset`, set
  `planted/9p2i` and seed 9 in the no-route and no-recorded-ending cases, and seed 9 in the ejection win with no
  meeting (`test_an_ejection_win_counts_at_the_deciding_meeting`); each constant argument is red.
- [x] Review correction: the publisher reads the impostor count and the registry it is given. A 9-player roster with
  1 or 3 impostors is refused by name (`test_a_nine_player_set_of_another_impostor_count_is_refused`), and a registry
  that omits the shown set gives it no era (`test_the_era_is_the_registrys`); both mutants are red.
- [x] Review correction: the gate's environment is stated. Results round 1 quotes `bash scripts/check.sh`'s exit code
  from this full-history worktree and the CI run of the pushed head (a shallow checkout) separately.
- [x] Review correction: mutation row M3 now reads SURVIVED on the first run. `test_a_malformed_file_fails_loud`
  matches the file path in both invalid-profile-file messages, and N5, T4 and B2, whose suites held the history
  test, were re-run against their named killers alone; each is red (Results, round 1).
- [x] Review correction: every listed location prefix is pinned in its existing test: the loader's two `{path}`
  arguments and its absent-file path, the ten profile-module locations, and the publisher's stamp race, missing
  roster and era id. Results round 1 carries the probe table.

- [x] **1. The pure module and its role-stripped projection.** `eval/game_profile.py` (new) imports the carrier
  (`load_census_inputs`, `tally_outcome`, `grounding_labels`) and row 3's helpers read-only, and writes nothing.
  - `BlindGame`, with `BlindMeeting`, `BlindBallot` and `BlindKill`, frozen dataclasses built only by
    `blind_projection`, is the sole input of every pre-reveal shelf, facet, chip and tripwire, T2 and the regroup wave
    included. It holds ids, ticks, rooms, labels, cited ids, accusations, vent-flag subjects, kill victims and
    witnesses, bodies, regroups, and the set-level kill cooldown (from `CensusInputs.kill_cooldown_ticks`, which the
    wave reads). Each `BlindMeeting` also holds the subjects of its row-3-manufactured alibi flags and each own-kill
    row's holder and citation id. `blind_projection` computes the manufactured subjects itself, from
    `load_set_inputs`'s meeting report and route through `_self_alibi_truths` and `_flag_is_manufactured`, joining the
    scorecard's meetings to the carrier's by meeting id (a mismatch raises, naming set, seed and meeting index). It
    holds no roles, winner, end reason, task bar, killer, own-kill-row subject, vent actor, per-impostor cooldown or
    in-vent set, and no `GameReport`.
  - `RevealGame` adds roles, the end reason and the final task count. Only reveal shelves, reveal facets and the leak
    check read it.
  - Mechanism: strict mypy. Planted: a test runs mypy on a `tmp_path` copy whose slow-burn predicate reads
    `game.roles` and requires the attribute error; a second copy whose T2 reads a report off its meeting
    (`meeting.report.roles`) fails mypy the same way, since `BlindMeeting` holds no report. A T2 handed a `GameReport`
    as a parameter passes mypy, because `GameReport` carries `roles`; item 2's role property catches that route
    (`test_a_t2_reading_the_report_roles_fails_the_role_property`).
- [x] **2. No pre-reveal byte reads a role or the ending.** Hypothesis properties over hand-built carriers and the
  committed one: permuting the seeded roles (counts kept) on the census carrier and on `load_set_inputs`'s
  `GameReport`s together, or swapping the end reason and winner for another recorded value on both, leaves every
  pre-reveal membership, pre-reveal facet, chip and tripwire byte-identical. Planted: a fold whose predicate closes over
  the full carrier and reads a role fails both properties; a T2 that also requires `GameReport.roles` to name the
  ejected player a crewmate fails the role property on a hand-built carrier whose manufactured flag names the ejected
  player.
- [x] **3. T1, decisive.** An ejection trips when, its ejecting ballots labelled `off_target`, `uncited` or
  `invalid_citation` removed, `tally_outcome` at the meeting's recorded floor ejects no one or someone else.
  `supported` and `flag_only` are held; `not_assessed` stays as recorded. A ballot with no label raises, naming set,
  seed, meeting and voter. An ejecting ballot labelled `none_held` is a case the ruled T1 does not classify: the
  meeting layer can produce one (Evidence, the carrier), and on the shown set 0 of 410 EJECT ballots carry it. Until
  the owner says how T1 reads one (open point 5), it raises an unclassified-case conformance error naming set, seed,
  meeting and voter, so a set that carries one stops the publisher and the refresh step rather than being read either
  way in silence; `rubric-v2-repro.py` would keep it as recorded, and on the shown set the two agree. Every ejection is
  read, whatever the ejected player's role. The served file and the page publish the decisive count with its games
  and meetings, and beside it the every and any counts and the two other decisive readings (read as SKIP; every
  ungrounded ballot removed). On the shown set: seed 26 meeting index 2 only; every 0; any 2.
  - Planted: the seed-41 shape (four held ballots carry it) trips any but not decisive; the seed-26 shape (removal
    leaves a tie) trips decisive; a `not_assessed` ejecting ballot kept; the floor perturbed changes a planted tally;
    a carrier on which removal and read-as-SKIP differ shows the removed reading governs; an ejecting `none_held`
    ballot raises the conformance error with all four names.
- [x] **4. T2, a manufactured contradiction.** An ejection trips when its `BlindMeeting`'s manufactured subjects
  (item 1: alibi-class flags that row 3's `_flag_is_manufactured` classes as manufactured over `load_set_inputs`'s
  route) name the ejected player. T2 reads only `BlindGame`; the join and its raise live in `blind_projection`. The page
  says it is nearly blind (row 3 evaluates 1 of the shown set's 15 alibi-class flags). Planted: a manufactured flag
  naming the ejected player trips; one naming another player, or an unevaluable flag, does not; a scorecard meeting id
  that differs from the carrier's raises in the projection.
- [x] **5. The pre-reveal shelves**, defined as the memo's Part 2.3 states and `rubric-v2-repro.py` implements (where
  the two differ in words the script governs, and Results names the difference): the reporter saw it happen, double
  kill, slow burn, two kills after one regroup, a close call, suspicion moved (ballots and accusations only, never the
  scalar), a third round. The witness test joins the trigger body to its kill by victim. Mechanism: one positive and
  one negative hand-built carrier per shelf; the committed file through `--check` (item 11). Planted per shelf: the
  boundary case (19 quiet ticks; a wave kill one tick past the window; a margin of two; two meetings; a reporter
  outside the witness list; same-tick double kills of two victims joined to the right body; a player who drew ballots
  and then died is not suspicion moving away).
- [x] **6. Reveal shelves and facets.** Reveal shelves: caught venting and one line, two readings (by the leak rule),
  one-vote ejection, nobody voted out, down to the wire, runaway, decided at a meeting, and decided without proof:
  right and wrong on what it held, always emitted as one pair. Pre-reveal facets: length in ticks, meetings by
  trigger, the kill timeline with regroup marks and the wave, reports with corpse age, bodies never found. Reveal
  facets: the ending, the distance from the other ending (measured the same way for each side), sabotage starts with
  the final task bar, each ejection's right or wrong annotation. Planted: a positive and a negative carrier per shelf;
  a task win with a planted living count reads the symmetric distance; an empty half of the pair is still emitted.
  - The pre-reveal meeting chip "An eyewitness voted on it" (memo 2.3: measured, not made a shelf, a chip on the
    meeting): a meeting carries it when some own-kill row's holder cast a ballot whose `cited_observation_id` equals
    that row's citation id (`MeetingFact.own_kill_rows` through `BlindMeeting`, as `rubric-v2-repro.py:146-149` reads
    it). It places a game on no shelf, takes no leak or saturation class (the leak rule covers shelves, memo 2.12
    risk 4), and is served in the pre-reveal half as the meeting index it marks. On the shown set: 15 meetings in 14
    games, seed 19 at meeting index 2. Planted: a positive carrier (the holder's ballot cites the row) and a negative
    one (the holder's ballot cites another observation id, or the row's citation id is `None`); the chip's meeting
    index is under item 14's pointer test.
- [x] **7. The leak rule.** Each candidate pre-reveal shelf (the seven, caught venting, one line two readings, struck
  after the regroup) is tested by a two-sided Fisher exact test against each recorded ending, any ejection and a
  crewmate ejected. Each 2x2 table spans every game of the era, a tripped game counted as a non-member of every shelf,
  as `rubric-v2-repro.py:243-255` computes; any p below `LEAK_P_LEVEL` makes the candidate reveal-only for that era.
  On the shown set (50 games, seed 26 a non-member): the seven pass, the smallest p 0.0655 (two kills after one
  regroup against any ejection); caught venting p < 0.001 and one line two readings p 0.0498 leak; struck after the
  regroup reads 0.0766 and is a facet by item 8. The served file's reveal half records each 2x2 table, p and class.
  Mechanism: a Hypothesis property holding the p to a brute-force hypergeometric enumeration. Planted: a candidate
  built to match one ending exactly fails; a one-sided p fails the property; a hand-built 50-game era with one tripped
  game, a 6-game candidate with 2 members carrying a fact and that fact on 2 of the 44 non-members, one of them the
  tripped game: the all-games table (2, 4, 2, 42) gives p 0.0655 and the candidate stays pre-reveal, while a fold
  that drops the tripped game reads (2, 4, 1, 42), p 0.0361, moves it behind the reveal and fails the test.
- [x] **8. The saturation rule.** A candidate holding more than `SATURATION_SHARE` of the era's games is served as a
  facet, never a shelf, and recorded so. Planted: 38 of 50 is a facet, 37 of 50 a shelf; saturation applies before
  the leak rule.
- [x] **9. Constants.** The design constants are `Final` and frozen by this card: slow burn 20 ticks, wave slack 4,
  close-call margin 1, third round 3 meetings, down-to-the-wire start 3, runaway half, `LEAK_P_LEVEL` 0.05,
  `SATURATION_SHARE` 3/4; a change needs profile version 3. The served file and the page render them from the module.
  - Mechanism for the freeze (`Final` stops only reassignment, so a source edit would pass): a pin test holds each of
    the eight to a table keyed by the stamped `rubric_version`, whose one row today is version 2 (20, 4, 1, 3, 3,
    one half, 0.05, 3/4); a module whose version has no row fails. Planted: a `tmp_path` copy of the module with slow
    burn set to 19 fails the pin, naming the constant, and keeps failing until its version moves to 3 and the table
    gains that row.
  - Sourced constants, each with a planted source-change case: the label partition from
    `get_args(BallotGroundingLabel)` (a copy with an eighth label raises unclassified); the end reasons from `get_args`
    of `WinResultType` and `GameStopReason` (an unknown reason raises); the alibi kinds from `ALIBI_FLAG_KINDS`
    (narrowed, the planted T2 trip goes); the wave from `BlindGame`'s set-level kill cooldown, projected from
    `CensusInputs.kill_cooldown_ticks` (5 moves a planted kill out); the era from `eval.eras` (a registry naming
    another id changes the stamp); the glossary's leak and saturation entries (a test holds their numbers to the
    module).
- [x] **10. The served file refuses a number to climb.** `GameProfile` (pydantic, frozen, `extra="forbid"`) has a
  pre-reveal half (shelves in fixed order, each member a seed with its meeting indexes or kill ticks; per-game facets
  and meeting chips; tripwires; All games) and a reveal half (reveal shelves, facets, the class tables). Mechanism and
  planted cases: a
  file carrying `score`, `rank` or a per-game total is refused at load; a key-name scan over both models refuses
  `score`, `rank`, `total`, `points`, `weight`, `best` and `top`; a member list out of seed order raises; a token test
  finds no `winner`, `reason`, `IMPOSTOR` or `CREWMATE` in the pre-reveal half (planted: an ending facet moved there).
- [x] **11. The publisher, the page and the drift check.** `scripts/publish_game_profile.py` writes the served file
  for each set in `PROFILE_SETS` (9p2i only) and `docs/game-profile.md`; `--check` recomputes both and exits 1 naming
  the drifted file, reporting an absent file before computing; `--set-dir DIR --json-stdout` prints a 9-player set's
  profile (a candidate round, a baseline-9 export) and writes nothing; a set of another roster (4p1i) is refused by
  name. The stamp reads the loader's own MANIFEST reader and `recording_fingerprint`, before and after the walk (a
  difference raises). The page states the definitions, the stamps, shelf sizes and members, the tripwire table with
  T2's near-blindness, the class tables, the chip-count lean, that facets the viewer already shows carry some ending
  information, and that no pre-registration, step rule, gate or objective reads the profile. Mechanism: a pytest drift
  test; planted: one edited membership turns `--check` red; a page naming a bar or a ratio of two rates fails.
- [x] **12. The refresh step and its text are true.** For `replays/samples/9p2i` under its era config the step runs
  the publisher and the dry run says it "would regenerate" the profile; any other target prints no profile line. The
  skip clause goes. The `--experiment-config` help and the `declared_args` comment state the era rule: a committed set
  records only its own era's declared config, or bare when its era declares none; a candidate round or a scratch
  directory takes any config. Mechanism: dry-run and `--help` cases in `tests/scripts/test_refresh_samples.py` (run
  `--dist loadfile`); `_REFRESH_OUTPUT_NAMES` names the profile. Planted: the old skip line and the old help sentence
  each fail their case.
- [x] **13. The API.** `GameProfileView` and its member views replace `RubricView`/`RubricGameView`, mirroring
  `GameProfile` field for field; `VIEW_MODEL_VERSION` goes to "6" with one comment line; `ReplayLoader.game_profile`
  serves the file, raises `FileNotFoundError` when absent (the route answers 404) and serves `stale: true` with no
  members on a MANIFEST, seedset or fingerprint mismatch; `/eval/game-profile` replaces `/eval/rubric`. The generator
  lists the new views and `frontend/src/types/api.ts` is regenerated; the client reads version "5" replay payloads.
  Mechanism: `tests/api/test_game_profile_view.py` (new) and the re-targeted `test_sets.py`, `test_view_model.py`,
  `test_schemas.py` and `test_leak.py`; `gen_frontend_types.py --check`. Planted: a field added to one model only fails
  the mirror test; each stale source suppresses members; 9p2i serves, 4p1i 404s.
- [x] **14. Every pointer is true of the served replay.** For every member of the committed profile and every meeting
  chip, each meeting index names a meeting the served `ReplayView` holds with the same id, and each kill tick a tick
  where it shows a kill, in the `api/public_results.py:98` `_check_case` idiom. Planted: a member pointing one meeting
  past the last fails, naming seed and shelf; an eyewitness chip moved one meeting past the last fails, naming seed
  and chip.
- [x] **15. The viewer.** The Highlights tab ("Browse by moment") renders the pre-reveal shelves in the file's order,
  each with its games in seed order as cards with chips (the eyewitness chip on the meeting it marks) and a facet
  timeline, then All games in seed order. With the
  reveal toggle on, the reveal shelves and reveal facets join; off, none of their names, members or counts render and
  no reveal-only filter acts. The two decided-without-proof shelves render as one block, wrong beside right, an empty
  half saying so. A tripped game sits on no shelf, carries its label and stays under All games. The dashboard panel
  lists shelf sizes and facet counts per value (reveal-only sizes only revealed), with no mean, bucket or link. The
  `hasEjection` filter reads the role-blind "someone was voted out"; the score and win-shape filters and their URL keys
  go; the tour fallback opens the first game in seed order. Mechanism: `HighlightCard.test.tsx`,
  `ReplayPicker.test.tsx`, a new `TournamentDashboard.test.tsx`, `client.test.ts`, and the evidence journey (9p2i
  shows shelves, 4p1i its set-neutral no-profile state). Planted: a reel sorted by shelf count, a reveal chip
  rendered unrevealed, a wrong shelf rendered alone and a tripped game on a shelf each fail; the journey's 9p2i leg
  fails on the base bundle.
- [x] **16. Copy and terms.** Every new string lives in `SPECTATOR_COPY`, in plain words with no task or audit id, no
  unexplained term and no threshold arithmetic; the copy walk (`dialectHits`) covers it and the component sources.
  The wrong shelf reads, in substance, "the voters cited lines they held and it pointed the wrong way; a wrong call on
  believable evidence is part of the game", beside "the table was right". `docs/glossary.md` extends its game-shape
  profile entry and adds the shelf names, the eyewitness chip, tripwire, decided without proof, wrong on what it held,
  and the leak and saturation rules. Planted: a description carrying "20 ticks" fails the copy test.
- [x] **17. Version 1 retires for the era.** Deleted: `regen_for_set`, the `--set-dir` branch and their tests;
  `rubric()`, the route, both DTOs, `_trimmed_rubric`; the score badge, spokes, buckets, histogram, `RUBRIC_SPOKES`
  and the interestingness strings. Kept as history: `experiments/lab/rubric.md` with one dated line (retired for
  `stage-b-r2` on the ruling's date, superseded by this profile), the two baseline-9 lab files (byte-identical to
  `d41c9006`), the frozen parity pin and `eval/watchability.py`. No code path left can write a v1 served file.
  Mechanism: `git grep` for the deleted names in Results; `git diff --exit-code d41c9006 --` the two lab files; a test
  that runs `rubric_score.main` with `--set-dir` on a `tmp_path` copy of the era's set, given synthetic facts stamped
  with that copy's recording fingerprint (the `_synthetic_facts` idiom of `tests/api/test_sets.py:341`, since the
  unwidened extractor refuses the era), and requires a non-zero exit and no `results-rubric-score.json` written.
  Planted: the same run against `76270d6c`'s scorer, rebuilt in `tmp_path` from today's module and the deleted
  served-file write the test carries as text (so it needs no git history; its code is `76270d6c`'s, docstrings
  aside), writes the file and fails the test.
- [x] **18. Nothing reaches an agent.** A new `.importlinter` forbidden contract keeps `agents`, `meetings`,
  `orchestrator`, `engine` and `training` from importing `eval.game_profile` or `scripts.publish_game_profile`;
  the bake-off entrant scan already bans every `eval.*` import. Mechanism: `uv run lint-imports`. Planted: one leg per
  source package in `tests/test_firewall.py`'s copied tree, each naming the contract BROKEN.
- [x] **19. The bundle.** `_trimmed_rubric` becomes a trimmed profile; 9p2i bakes `data/9p2i/eval/game-profile.json`,
  4p1i bakes none. The baked file keeps exactly these set-level keys, as provenance and catalogue only:
  `rubric_version`, the era id, the MANIFEST key, `source_fingerprint`, the seedset, `stale`, the design constants, and
  the shelf, chip and facet catalogue (each name, its half and its class, with no size, no 2x2 table and no p). Every
  member list, on both halves, is cut to the baked seeds: the pre-reveal shelves, the meeting chips, All games, the
  tripwire entries (seeds 26 and 41 are not baked, so none ships), every reveal shelf and both halves of the pair.
  Per-game facets, reveal facets included, are cut the same way. Cut entirely: the class tables, every shelf size,
  the tripwire counts (decisive, every, any; T2), and the pair's game and ejection counts. So the only reveal-half bytes
  that ship are seeds 14's and 19's own reveal memberships and facets, and the pinned shape is what Publication quotes.
  Mechanism: `tests/scripts/test_build_demo_bundle.py` and the re-targeted stale controls, with a key-set test that
  holds the baked file's keys to that list. Planted: a bake that skips the trim fails; a bake that passes the class
  tables or a shelf size through fails the key-set test; a stale profile bakes no member.
- [x] **20. The registry follows the bytes.** In `docs/artifacts.md`, re-derived last after the final merge of `main`:
  the `replays/samples/` row (107 files to 108 at authoring; its size re-measured) and one new row for
  `docs/game-profile.md`, scoped in `scripts/verify_ml_evidence.py`'s two tables. Mechanism:
  `test_every_counted_registry_row_matches_the_index` and offline `scripts/verify_ml_evidence.py`. Planted: a stale
  row fails; Results quotes the red run.
- [x] **21. The wave lessons hold.** Each production line is neutered alone and its suite goes red (Results carries
  the neuter table). One bounded mutation pass over the changed spans with exactly F drop a filter, S swap a
  collection, N None or comparison, K read to constant, M message argument, T drop a tuple member, B swap branches, L
  loaded source to literal; every survivor killed or named equivalent. No test is weakened: Results names each
  re-targeted test's old assertion and the strength it keeps. `bash scripts/check.sh` passes at the head stating the
  numbers.

## Constraints

**Dependencies and merge timing.**
- The carrier must hold, before this card's final merge of `main`: `KillFact.victim` (from `KilledEvent.target`) with
  the matching victim on `BodyFact` (from the body's `player_id`), so a report's trigger body joins its kill by victim
  even on a same-tick double kill; and item 5's end reason and final task count. The orchestrator adds the two victims
  to `census-held-data-cells` as a cross-card edit and keeps item 5's two fields required: its tables may be struck,
  the fields may not. If they are struck anyway, a census follow-on supplies them first. This card never writes
  `eval/gameplay_census.py`, `scripts/publish_gameplay_census.py` or `docs/gameplay-census.*`.
- `census-held-data-cells` item 3 holds the route-check JSON's recorded tree equal to the tree of
  `replays/samples/9p2i` at `HEAD`. Adding `results-game-profile.json` changes that tree, so that check must compare
  the recording files (the fingerprint), not the directory; the orchestrator reconciles the two cards before this one
  merges (cross-card edit). The route-check replay's own `--check` reads by pinned sha and stays green
  (`tests/experiments/test_route_check_replay.py:643-656`).
- Order: this card dispatches once `census-held-data-cells` has merged (it reads that card's carrier fields) and after
  `route-lines-field` (first writer of `api/schemas.py`, the generated types and `docs/glossary.md`), and it merges,
  as the owner's publication merge, BEFORE the round-3 frozen head F: the record card's F clause names this card
  among the merges F holds (decision memo 8.6, cross-card edit 6), so the round reads none of the profile and the
  freeze never bars it. Its Publication quotes are re-derived on the set shown at dispatch. If round 3 is later
  promoted, the promotion change re-derives the profile.
- This card writes `scripts/refresh_samples.sh` (the step, its dry-run line, the help, the `declared_args` comment),
  the `experiments/lab/rubric_score.py` deletions and the `report-rubric-interestingness.md` run line first.
  `rubric-extractor-era`, if the owner dispatches it under D14, branches from `main` after this card's merge and
  touches only the witness naming, the output name and any surviving comment line. This card never writes the
  extractor, `eval/process_scorecard.py` or the held card.
- Authorized: the view-model bump from 5 to 6, the removal of `/eval/rubric`, `RubricView` and `RubricGameView`, and
  the new `/eval/game-profile` are the design memo's Part 2.9 retirements, taken by the owner's ruling of 2026-10-06,
  "Profile as recommended, decisive, and ship the shelf" (decision memo 8.6); the memo's Part 3 drops the held card's
  no-DTO-change constraint for this card. No other DTO changes.

**One writer per file.** `docs/glossary.md`: the doctrine addendum's entry and "route line" land first; this card
extends that entry and adds its own after it. `docs/artifacts.md`: this card's two rows, re-derived after merging
`main`; `rubric-extractor-era`, if dispatched, writes after it. `tasks/README.md` and this card's Status line: the
orchestrator's, on `main`; this card writes its Results only. `frontend/src/lib/copy.ts`, `frontend/src/api/client.ts`
and the components: this card alone; the baselines memo's dashboard relabel comes after it. `replays/samples/9p2i/`: this card
adds `results-game-profile.json` and nothing else. A break this card causes in another card's file goes to the
orchestrator, never into an edit here.

**House rules.** The engine stays a pure, deterministic tick and nothing here touches it; replays stay byte-identical.
`agents/` never imports `engine/`. No module-level mutable state: tables are `Final` tuples or read-only mappings.
Invalid input raises, with no silent fallback. Each new gate carries a planted case. Claims name their mechanism;
numbers are measured at the head that states them, with the command in Results. Guarantees are stated at the strength
delivered; a live-tense sentence about old behaviour is fixed in the same pull request; universal guarantees are
properties, with `settings(deadline=None)` where the map loads.

**Out of scope.** No new `AILIBI_*` lever, environment switch or experiment field; no prompt registry or version bump;
no recorded byte edited; no history re-scored (v1's lab results stay); the corpus FROZEN line and the ML artifacts
never move (offline `scripts/verify_ml_evidence.py`, never `--complete`); no live provider call, recorder run or
held-out generator, and the untracked `.env` is never read. Role-correctness is reported and never a gate; the meeting
layer labels and never rewrites; the profile is computed after the fact and pushes no agent toward any answer. The
featured strip, `FEATURED_GAMES`, the public results tab, the curated cases and the README are untouched: whether a
wrong-but-believable ejection is ever featured stays D7's. The extractor, the W0/W1/W2 fixtures and the frozen parity
pin stay; their retirement is D14's.

**Publication.** Every push to `main` rebuilds the demo (`.github/workflows/pages.yml`), so the merge is the owner's.
The pull request states, re-measured at its head against its base:
- The bundle diff, file by file: added `data/9p2i/eval/game-profile.json` (seeds 14 and 19); changed the five replay
  views (`data/9p2i/replays/headless-seed-19.json`, `-14.json`; `data/4p1i/replays/headless-seed-2.json`, `-11.json`,
  `-29.json`) in `viewModelVersion` only, "5" to "6"; the other 66 JSON files byte-identical; no
  `data/4p1i/eval/game-profile.json`; `index.html` and the hashed assets carry the new viewer. Mechanism: `diff -rq`
  of bundles built at base and head, and a JSON diff of the five views.
- The baked file, quoted key by key with its values at the head: the provenance keys (`rubric_version` 2, the era id,
  the MANIFEST key, `source_fingerprint`, the seedset, `stale` false), the design constants, and the catalogue (each
  shelf, chip and facet name with its half and class, and no size, table or p); the members, chips and facets of
  seeds 14 and 19 only; no class table, no shelf size, no tripwire count or member, no pair count. On the shown set
  the reveal-half bytes that ship are seed 19's caught venting, one line two readings, decided at a meeting and
  "right", seed 14's runaway and "right", and the two games' reveal facets. A shelf header renders the number of games
  it lists from the members it is served: locally that is the set-level size; in the bundle it is the baked members
  only, and the trimmed file carries no set-level size, so no set-level count renders publicly. Mechanism: the key-set
  test of item 19 and a JSON dump of the baked file in the pull request.
- The copy that goes live: the 9p2i Highlights tab moves from "No interestingness rubric for this set" to "Browse by
  moment". Unrevealed: The reporter saw it happen, Slow burn, A third round (seed 19), with the eyewitness chip on seed
  19's meeting index 2, then All games (14, 19), seed 14 with facets only. Revealed, also: Caught venting, One line
  two readings, Decided at a meeting (19), Runaway (14), and the pair, "the table was right" (14, 19) beside "wrong on
  what it held" with its no-game line. Each shelf's description, the chip's words, the facet labels, the 4p1i
  no-profile state, and the removed strings ("Ordered by the interestingness rubric.", the unscored banner, the score
  legend) are quoted in full. No baked game is on the wrong shelf, and no panel is public because the bundle dashboard
  shows no tournament report. These quotes are re-derived on the set shown when this card dispatches (Order).

**Delivery.** Branch `work/rubric-v2-profile`, one pull request into `main`, merge commit or fast-forward, never squash;
merge `main` in, never rebase. Each commit body ends with `Card: tasks/work/rubric-v2-profile.md`, immediately followed
by the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

**Open points for the owner.**
1. The brief listed "the geomean parity pin's remains" for deletion. The memo keeps the frozen pin as history under
   D14, which is still yours, so this card keeps it and `_set_manifest_sha`; it deletes only the producer-loader key
   agreement written for a next v1 file (`tests/api/test_sets.py:454-468`), re-targeted to the profile's stamp.
2. The tripwire label shows before the reveal, as ruled, and its words say a player was voted out (one game here).
3. "One line, two readings" sits on the leak boundary (p = 0.0498): one game more or less flips its class.
4. The held `rubric-extractor-era`, amended to the optional extractor half, stays ready; whether it is dispatched,
   deferred or closed as superseded is your D14 word (decision memo 8.6), not this card's.
5. How T1 reads an ejecting ballot labelled `none_held`. The ruling's T1 assumed none exists ("`none_held` cannot
   eject", memo 2.2), but the meeting layer can label one. The shown set has none (0 of 410 EJECT ballots). This card
   refuses such a ballot as an unclassified case (item 3) until you choose: keep it as recorded (the script's reading),
   remove it as ungrounded, or keep the refusal.

## Expected scope

- New: `eval/game_profile.py`; `scripts/publish_game_profile.py`; the generated
  `replays/samples/9p2i/results-game-profile.json` and `docs/game-profile.md`; `tests/eval/test_game_profile.py`;
  `tests/scripts/test_publish_game_profile.py`; `tests/api/test_game_profile_view.py`;
  `frontend/src/components/TournamentDashboard.test.tsx`.
- API: `api/schemas.py`, `api/replay_loader.py`, `api/routes/eval.py` (the views, the version, the loader, the route,
  the comments); `scripts/gen_frontend_types.py`; `frontend/src/types/api.ts` (generated, never hand-edited).
- Scripts: `scripts/build_demo_bundle.py` (the trim); `scripts/refresh_samples.sh` (the step, its dry-run line, the
  help, the `declared_args` comment); `scripts/verify_ml_evidence.py` (the new row's two scope entries only);
  `.importlinter`.
- Lab: `experiments/lab/rubric_score.py` (the deletions only; scoring untouched); `experiments/lab/rubric.md` (one dated
  line); `experiments/lab/report-rubric-interestingness.md` (the run line only).
- Frontend: `frontend/src/components/HighlightCard.tsx`, `ReplayPicker.tsx`, `ReplayFilters.tsx`,
  `TournamentDashboard.tsx`, `GuidedTour.tsx`; `frontend/src/lib/copy.ts`; `frontend/src/api/client.ts`; their tests
  `HighlightCard.test.tsx`, `ReplayPicker.test.tsx`, `copy.test.ts`, `client.test.ts`,
  `frontend/src/store/replayStore.test.ts` (the mock); `frontend/src/stories/ReplayBrowser.stories.tsx`,
  `TournamentDashboard.stories.tsx`; `frontend/e2e/evidence-journey.ts`.
- Tests: `tests/api/test_sets.py`, `test_view_model.py`, `test_schemas.py`, `test_leak.py`;
  `tests/scripts/test_build_demo_bundle.py`, `test_public_recording_provenance.py`, `test_refresh_samples.py`;
  `tests/test_firewall.py`.
- Docs: `docs/glossary.md`, `docs/artifacts.md` (two rows), `docs/deployment.md` (one sentence).
- This card's Results. `tasks/README.md` and this card's Status line are the orchestrator's, on `main`.

Not written: `eval/gameplay_census.py`, `eval/process_scorecard.py`, `eval/watchability.py`, `eval/eras.py`, the
extractor and its fixtures, `experiments/lab/results-rubric-*.json`, every replay and MANIFEST, `agents/`, `meetings/`,
`orchestrator/`, `engine/`, `training/`, `README.md`, `api/public_results.py`. Follow-through outside this list needs a
line in Results naming the file and why.

## Record impact

- **Recorded bytes.** None move. One generated file is added beside the recordings, outside the recording fingerprint,
  as the baseline-9 rubric was; `bash scripts/verify_samples.sh` and the four `build_sample_report.py --check` runs
  recompute exactly what they did before.
- **Behaviour.** No agent, meeting, engine or tactical path reads the profile, and no game plays differently. No
  scorecard, census, evaluation or ML artifact moves; the census and scorecard pages stay byte-identical.
- **Compatibility.** The view model goes to version 6: `/eval/rubric` and its two views are removed, as authorized in
  Constraints (memo Part 2.9, the ruling of 2026-10-06). A version-5 client answers the missing route with its empty
  state; this client still reads version-5 replay payloads.
- **History.** The baseline-9 rubric stays at `d41c9006` (blob `4879637e`); the two lab files, the frozen pin and
  `rubric.md`'s v1 text stay. This card commits no v1 reading of the era; the optional `rubric-extractor-era` commits
  the era's geomean witness, per-game v1 rows, lab only.
- **What ships.** The served profile and the Highlights tab for 9p2i, through `pages.yml`, bounded by the bundle diff.
- **Next era.** Classes are recomputed per era by the publisher; the next promotion regenerates the file and the page.
- **Adoption.** Not applicable: no experimental behaviour.

Measurement: the profile is computed at the implementation head and agrees with `rubric-v2-repro.py` on every shelf,
tripwire and class; Results quotes both outputs and any difference by name.

## Validation

```
env | grep -c '^AILIBI_'                                     # 0
uv run pytest tests/eval/test_game_profile.py tests/scripts/test_publish_game_profile.py \
  tests/api/test_game_profile_view.py tests/api/test_sets.py tests/api/test_view_model.py tests/api/test_schemas.py \
  tests/api/test_leak.py tests/scripts/test_build_demo_bundle.py tests/scripts/test_public_recording_provenance.py \
  tests/test_firewall.py tests/eval/test_watchability.py -n 6 --dist loadfile
uv run pytest tests/scripts/test_refresh_samples.py -n 4 --dist loadfile
uv run python scripts/publish_game_profile.py --check                    # exit 0, run twice, no diff
uv run python scripts/publish_game_profile.py --set-dir replays/samples/4p1i --json-stdout   # refused by name
.venv/bin/python <memo dir>/rubric-v2-repro.py replays/samples/9p2i       # agrees with the served file
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/gen_frontend_types.py --check
uv run lint-imports
git diff --exit-code d41c9006 -- experiments/lab/results-rubric-score.json experiments/lab/results-rubric-geomean.json
git diff --stat main -- replays/                                         # the one profile file, nothing else
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir <set> --check  # samples and ml_corpus, 9p2i and 4p1i
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run python scripts/verify_ml_evidence.py                              # offline; never --complete
cd frontend && npm run lint && npm run tsc:check && npm run test && npm run build && npm run e2e
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base   # at the base; then bundle-head; diff -rq
bash scripts/check.sh                                                    # whole, in a clean worktree
```

Run `check.sh` to the end rather than stopping at the first failure, because `set -e` masks later gates. Results
records each exit code and count, the planted cases red then green by name, the neuter table and the mutation pass, and
the sections this card rests on: `docs/architecture.md` "Layering", "Enforced boundaries" and "Determinism and the
substrate ladder"; the memo's Part 2; direction sections 7 and 8 (row 9). Limitations to state: one 50-game recording
and no interval; the leak classes swing between eras; the constants were chosen with these numbers in view and the
0.05 level is not corrected for its 50 tests; facets the viewer already shows carry some ending information;
`none_held` is the voter's own statement, and an ejecting `none_held` ballot is refused until the owner says how T1
reads it; T2 is nearly blind; "wrong on what it held" is direction section 7's wrong-but-believable class without
that section's test that the cited line is true, which the census measures and the profile does not read; the
eyewitness chip is not leak-tested, since the leak rule covers shelves.

## Results

### Implementation (2026-10-07)

Built on `work/rubric-v2-profile` from `main` at `ef1a2a59` (the census card merged at `9caac0cf`, so the carrier holds
`KillFact.victim`, `BodyFact.victim`, `GameFacts.end_reason`, `final_tasks_completed` and `final_tasks_total`).
`origin/main` had not moved at the final fetch, so no merge of `main` was needed and the registry rows below are derived
on that base. Commits, in order: `a556a4ec` (the module, the publisher, the served file, the page, the contract),
`af275235` (the API, the bundle, the refresh step, the v1 retirement), `b46c5c53` (the viewer), `9033423e` (the
bundle's copy), then `f665249c`, `fb8af924`, `e4313207`, `4acaf286`, `00575283` and `dc023329` (what the neuter and
mutation passes asked for: tests, the viewer's request reads moved into pure functions, three strings moved into the
copy table), then the Results commits.

**Sections this rests on.** `docs/architecture.md` "Layering": `eval/game_profile.py` is an `eval/` reader of the
census carrier (`load_census_inputs`, `grounding_labels`, `game_endings`) and of row 3's helpers (`load_set_inputs`,
`_self_alibi_truths`, `_flag_is_manufactured`, `ALIBI_FLAG_KINDS`), read-only; the publisher is a script; the API
reads only the served JSON, through `GameProfileView`, and imports nothing from `eval.game_profile` (the mirror test
holds the two models together). "Enforced boundaries": `uv run lint-imports` keeps 5 contracts, 0 broken, the new one
`nothing_the_game_runs_reads_the_game_profile` among them; nothing under `agents/`, `meetings/`, `orchestrator/`,
`engine/` or `training/` changes. "Determinism and the substrate ladder": no recorded byte, stamp, prompt, detector
or lever moves (`git diff --stat main -- replays/` lists the one served file; `bash scripts/verify_samples.sh`
verifies all 50 samples of each committed set clean). The design memo's Part 2 (P1-P7, 2.2 tripwires, 2.3 shelves and
facets, 2.4 the two rules, 2.9 record impact, 2.10 publication) and its Part 4 items 1-5 as the ruling takes them;
the direction addendum's section 7 (the wrong-but-believable class) and section 8 row 9.

**What was built.**
- `eval/game_profile.py`. `blind_projection` builds `BlindSet` / `BlindGame` / `BlindMeeting` / `BlindBallot` /
  `BlindTurn` / `BlindOwnKillRow` / `BlindKill` / `BlindBody` (frozen dataclasses) from the carrier and the
  scorecard, joining meetings by id and computing each meeting's manufactured subjects through row 3's helpers; the
  `GameReport`s never leave the function. `reveal_projection` adds `RevealGame` (roles, end reason, final task count,
  sabotage starts). Readings: `meeting_readings` / `game_readings` / `tripped` (T1 in its five readings and T2),
  `candidate_pointers` (the seven pre-reveal candidates, caught venting, one line two readings, struck after the
  regroup), `eyewitness_meetings` (the chip), `reveal_pointers` and `distance` (the reveal shelves and the symmetric
  distance), `fisher_two_sided` (exact, in `Fraction`s), `is_saturated`, `classify_candidate` (saturation, then the
  leak rule over `era_facts`), `read_pre_reveal` (everything the pre-reveal half serves, from `BlindSet` alone) and
  `build_profile` / `serialize_profile`. The served model `GameProfile` (pydantic, frozen, `extra="forbid"`) has a
  pre-reveal half (shelves, the chip, tripwires, per-game facets, All games) and a reveal half (reveal shelves, the
  pair, reveal facets, class tables). Constants are `Final` and stamped `rubric_version` 2.
- `scripts/publish_game_profile.py` writes `replays/samples/9p2i/results-game-profile.json` (124,334 bytes) and
  `docs/game-profile.md`; `--check`, `--set-dir DIR --json-stdout`, the roster refusal (`ProfileRefused`), the stamp
  read before and after the walk (`read_stamp`: the loader's `_manifest_git_sha` and `_expected_seedset` and
  `recording_fingerprint`), and the era from `eval.eras` (an era holding two profiled sets is refused).
- API: 23 views in `api/schemas.py` mirroring the served model, `VIEW_MODEL_VERSION` "6" with one comment line,
  `ReplayLoader.game_profile` (absent raises `FileNotFoundError`; a non-object or a file carrying `stale` or a
  view-model key is refused; a MANIFEST, seedset or fingerprint mismatch serves `stale: true` with every member,
  entry, facet and table withheld by `_withheld_profile`), `/eval/game-profile`; `_rubric_is_stale` is renamed
  `_provenance_is_stale`, which `game_profile` now reads. Generated: `frontend/src/types/api.ts` and
  `frontend/src/types/api.fidelity.ts` (the generator writes both).
- Bundle: `_trimmed_profile` keeps the provenance keys, the constants and the catalogue, cuts every member list,
  tripwire entry and per-game facet to the baked seeds, and deletes the class tables and the two alibi-flag counts
  (`_UNBAKED_PROFILE_KEYS`). A shelf's size, a tripwire's count and the pair's counts are lengths of member lists,
  so no set-level size ships; a stale profile bakes no member.
- Refresh: for `replays/samples/9p2i` under its era config the step runs the publisher; the dry run prints
  "[dry-run] game-shape profile: would regenerate replays/samples/9p2i/results-game-profile.json and
  docs/game-profile.md from the refreshed replays (scripts/publish_game_profile.py; $0, no provider)"; every other
  target prints no profile line. The skip clause is gone; the `--experiment-config` help and the `declared_args`
  comment state the era rule.
- Viewer: the Highlights tab is "Browse by moment" (`ReplayPicker.tsx`: `reelSections`, `ShelfSection`, `PairBlock`,
  `MomentReel`; `HighlightCard.tsx`: `CardProfile`, the chips, the facet lines, the timeline, the reveal facet
  lines; `ReplayFilters.tsx`: the winner filter and "someone was voted out"; `TournamentDashboard.tsx`:
  `MomentsPanel` with shelf sizes and facet counts per value; `GuidedTour.tsx`: the first game in seed order).
- Retired (craft rule 3): `regen_for_set`, `--set-dir`, `RUBRIC_RESULTS_FILENAME` and the fingerprint import in
  `experiments/lab/rubric_score.py`; `_RUBRIC_FILENAME`, `ReplayLoader.rubric`, `/eval/rubric`, `RubricView`,
  `RubricGameView`, `_trimmed_rubric`; `ScoreBadge`, `SubScoreBar`, the score and win-shape filters and their URL
  keys, the score buckets, `InterestingnessHistogram`, `RUBRIC_SPOKES`, the interestingness strings and `getRubric`.
  `git grep -nE 'regen_for_set|RubricView|RubricGameView|_trimmed_rubric|ScoreBadge|SubScoreBar|RUBRIC_SPOKES|InterestingnessHistogram|getRubric|_RUBRIC_FILENAME|RUBRIC_RESULTS_FILENAME|def rubric\(|eval/rubric'`
  finds, outside history (`agent_prompts/`, `audits/`, `design/`, `tasks/`, `experiments/lab/report-rubric-design.md`),
  only the four absence pins (`frontend/src/api/client.test.ts:80`, `tests/api/test_game_profile_view.py:281`,
  `tests/api/test_view_model.py:194`, `:1369`). Kept: `_set_manifest_sha`, the frozen parity pin,
  `eval/watchability.py`, the two baseline-9 lab files (`git diff --exit-code d41c9006 --` both exits 0) and
  `experiments/lab/rubric.md` with one dated line.
- Docs: `docs/glossary.md` extends the game-shape profile entry and adds the shelves, the eyewitness chip, tripwire,
  decided without proof, wrong on what it held, the leak rule and the saturation rule; `docs/deployment.md` one
  sentence; `docs/artifacts.md` the two rows; `scripts/verify_ml_evidence.py` the new row's two scope entries.

**Follow-through outside Expected scope.** `frontend/src/types/api.fidelity.ts` (written by the same generator run as
`api.ts`); `tests/scripts/test_verify_ml_evidence.py` (its probe list names the new registry row, two lines);
`frontend/e2e/evidence.spec.ts` (one live-only case opening the dashboard's diagnostic report, whose moments panel
the static bundle does not build, so the shared journey cannot read it).

**Decisions.**
1. Orchestrator ruling (1): T1's governing quantifier is decisive (the ejecting ballots labelled `off_target`,
   `uncited` or `invalid_citation` removed, `tally_outcome` at the recorded floor ejects no one or someone else),
   published beside every, any and the two other decisive readings. An ejecting ballot labelled `none_held` raises
   `GameProfileConformanceError` as an unclassified case naming set, seed, meeting index and voter
   (`test_an_ejecting_none_held_ballot_raises_naming_all_four`); a `none_held` SKIP is read as recorded. The shown
   set carries none, so the publisher runs; open point 5 stays the owner's.
2. Orchestrator ruling (2): "wrong on what it held" ships locally beside its right twin, always as one pair, an
   empty half saying "No game listed here lands on this half."; in the bundle no baked game is on the wrong half, so
   the pair renders the right half (14, 19) beside that line.
3. Orchestrator ruling (3): the leak rule's 2x2 tables span every game of the era, a tripped game counted as a
   non-member of every candidate, and the classes are recomputed per era by the publisher
   (`test_the_leak_universe_counts_a_tripped_game_as_a_non_member`,
   `test_a_universe_dropping_the_tripped_game_moves_the_shelf_and_fails`).
4. Orchestrator ruling (4): no score, rank, total, histogram or mean is served or rendered; the shelf-count lean is
   on the generated page only, marked never served (`test_no_field_of_the_profile_names_a_score`,
   `test_no_key_of_the_served_view_names_a_score`, the copy test "names no score, rank or order anywhere a viewer
   reads the profile").
5. Orchestrator ruling (5): version 1 retires as the card lists; the geomean parity pin and `_set_manifest_sha` stay
   (open point 1).
6. Orchestrator ruling (6): the merge is the owner's publication decision; the pull request quotes the shown-set
   reading, the copy that goes live, the baked file key by key and the bundle diff file by file.
7. Orchestrator ruling (7): this card lands before the round-3 frozen head F, so the round reads none of it.
8. Where the memo's words and `rubric-v2-repro.py` differ, the script governs and the page states the script's
   reading: "one line, two readings" counts two ballots labelled `supported`, `none_held` or `off_target` that cite
   the same turn and name different targets (the memo: "reach different decisions"); "suspicion moved" counts a
   player who drew EJECT ballots (the memo: "drew ballots"). The memo's shelf sizes are the script's output, which the module
   reproduces.
9. Sabotage starts are read from the carrier's frames (the first tick a sabotage is active), so a sabotage started
   on a game's final tick is never in play: 43 starts against the script's 46, which reads the start events (seeds
   6, 42 and 44 each start one on the final tick). It is a reveal facet, no shelf, tripwire or class reads it, and
   the page says so.
10. "Struck after the regroup" is a facet by the saturation rule (40 of 50): the kill timeline marks each wave kill
    and the kills facet counts them; its class row stays in the reveal half's class tables.
11. The leak facts are each ending the era records (here `CREWMATE_TASKS`, `CREWMATE_EJECT`, `IMPOSTOR_PARITY`),
    then "some meeting ejected someone" and "a crewmate was ejected", as `rubric-v2-repro.py` reads them.
12. The tripwire labels, shown before the reveal as ruled (open point 2), are "Kept off the shelves: at meeting
    {meeting} a player was voted out on ballots that cited nothing the voters held about them, and without those
    ballots the meeting would have gone another way." and the manufactured-contradiction twin. The served names are
    `decided_by_a_vote_that_held_nothing` and `decided_on_a_manufactured_contradiction`.
13. A shelf that lists no game renders nothing (`ShelfSection`), so the bundle, which lists only seeds 14 and 19,
    never claims a set-level emptiness; All games says "Every game listed here, in seed order, including any a
    tripwire keeps off the shelves." for the same reason.
14. A shelf header's count is the number of members it is served: the set-level size locally, the baked members
    only in the bundle.

**Re-targeted tests: the old assertion, and the strength kept.** No assertion was loosened; each v1 assertion
either moved to the profile with the same shape or was deleted with the mechanism it guarded (craft rule 3).

| old test (file) | old assertion | now | strength kept |
| --- | --- | --- | --- |
| `test_eval_rubric_is_per_set` (`tests/api/test_sets.py`) | both committed sets 404 on `/eval/rubric`; a scratch parent serves the scored set and 404s the other | `test_eval_game_profile_is_per_set` | 9p2i serves fresh with its seedset, 4p1i 404s; the scratch parent serves the profiled set fresh on its key and 404s the bare one |
| `test_the_promoted_set_ships_no_rubric_and_keeps_its_key` (`test_sets.py`) | the loader raises; `_set_manifest_sha` agrees with the loader's key | `test_the_promoted_set_ships_its_profile_on_its_own_key` | the served file's MANIFEST key, fingerprint and era equal the loader's own derivations, and the loader serves it fresh |
| (new) | | `test_version_one_writes_no_served_file_for_the_era`, `test_the_scorer_before_the_retirement_wrote_one_and_fails_the_check` | item 17's run of `rubric_score.main --set-dir` exits non-zero and writes nothing; `76270d6c`'s scorer, rebuilt without git history (round 1), writes the file and fails |
| `test_rubric_endpoint_404_without_rubric_file` (`tests/api/test_view_model.py`) | `/eval/rubric` 404s with no file | `test_game_profile_endpoint_404_without_a_profile_file` | the same, on the new route |
| `test_rubric_stamps_git_sha_from_8col_flags_manifest` | the key read from an 8-column manifest | `test_the_profile_stamp_reads_git_sha_from_an_8col_flags_manifest` | the same key, through the publisher's stamp and the loader |
| `test_rubric_is_stale_prefix_logic`, and the fingerprint-shape cases | prefix, `None` and malformed cases of `_rubric_is_stale` | `test_provenance_is_stale_prefix_logic` and the same cases | every case kept, on the renamed `_provenance_is_stale` |
| `test_rubric_regen_producer_and_staleness` | `regen_for_set` writes a fresh file; another key reads stale | `test_the_profile_reads_fresh_on_its_key_and_stale_on_another` | fresh on its key with its games; stale on another, every member withheld |
| `test_rubric_regen_defaults_to_set_manifest_sha` | the producer stamps the set's key | `test_the_publisher_stamps_the_sets_manifest_key` | the publisher's stamp, read back fresh by the loader |
| `test_rubric_rejects_present_but_malformed_file` | a malformed file raises naming the field | `test_a_present_but_malformed_profile_fails_loud` | a missing field and a non-object each raise |
| `test_rubric_set_mismatch_is_stale` | a set mismatch reads stale despite a matching key | `test_a_profile_of_another_set_reads_stale` | the same |
| `test_rubric_is_trimmed_to_the_baked_seeds` (`tests/scripts/test_build_demo_bundle.py`) | per-game rows cut to the baked seed | `test_the_profile_is_trimmed_to_the_baked_seeds` plus the key-set helper | every member list, chip, entry and facet cut, and the baked keys held to item 19's list |
| `test_the_committed_sets_bake_no_rubric` | no committed set bakes a rubric | `test_the_featured_bake_ships_seeds_19_and_14_only`, `test_the_four_player_set_bakes_no_profile` | 9p2i bakes seeds 14 and 19 only, no tripwire entry, the wrong half empty; 4p1i bakes none and 404s |
| `test_an_unscored_set_bakes_no_rubric` | an unscored set bakes none | `test_a_stale_profile_bakes_no_member`, `test_a_bake_that_skips_the_trim_fails_the_shape`, `test_a_bake_passing_the_class_tables_through_fails_the_key_set` | a stale profile bakes no member; both planted bakes fail |
| `test_fresh_source_is_published_and_baked` (`tests/scripts/test_public_recording_provenance.py`) | a fresh v1 file serves and bakes its rows | the same name, on the profile | 50 games served, the bake holds exactly the baked seed |
| `test_changed_inputs_suppress_scores_and_cannot_be_restamped` | changed bytes withhold scores; `regen_for_set` refuses to re-stamp | `test_changed_inputs_withhold_members_and_the_stamp_follows_the_bytes`, `test_a_missing_stamp_fails_loud` | changed bytes withhold every member and bake none; the profile is recomputed from bytes, so a new stamp follows them, and a file without its stamp raises |
| `test_bundle_suppresses_legacy_stale_rows` | a stale v1 file bakes no row | `test_bundle_bakes_no_member_of_a_stale_profile` | the same, on the profile |
| the refresh skip-line pins (`tests/scripts/test_refresh_samples.py`) | the dry run prints the skip line; no rubric line | the profile line case, `test_the_old_skip_line_fails_the_profile_case`, `test_any_other_target_prints_no_profile_line`, the two era-rule cases | 9p2i prints exactly the profile line; every other target none; the old skip line and the old help sentence each fail |
| the v1 fixtures in `tests/api/test_schemas.py` and `tests/api/test_leak.py` | a hand-built `RubricView` round-trips; the DTO inventory names `RubricView` and `RubricGameView` | the committed profile round-trips as `GameProfileView`; the inventory names the 23 new views | the round-trip runs on the served bytes, and the inventory's equality check covers every new view |
| frontend: "rubric provenance in replay cards", "the rubric legend table", "highlight source freshness" | stale and absent rubric states; the spoke legend | "the no-profile and stale states", "the game-shape profile's copy", "the game-shape profile route" | stale and absent kept distinct and set-neutral; the copy has no threshold or score word; the client asks no v1 route and reads a version-5 replay |

**Verification** (at `00575283`, whose production code `dc023329` keeps, adding card tests only; `bash scripts/check.sh` is recorded in its own paragraph below).
- `env | grep -c '^AILIBI_'`: 0.
- `uv run pytest tests/eval/test_game_profile.py tests/scripts/test_publish_game_profile.py tests/api/test_game_profile_view.py tests/api/test_sets.py tests/api/test_view_model.py tests/api/test_schemas.py tests/api/test_leak.py tests/scripts/test_build_demo_bundle.py tests/scripts/test_public_recording_provenance.py tests/test_firewall.py tests/eval/test_watchability.py -n 6 --dist loadfile`:
  474 passed, 1 skipped (the pre-existing `tests/api/test_view_model.py:399` skip: the set holds no fabricated
  emergency opening), exit 0.
- `uv run pytest tests/scripts/test_refresh_samples.py -n 4 --dist loadfile`: 167 passed, exit 0.
- `uv run python scripts/publish_game_profile.py --check`, twice: exit 0 both times ("... are consistent with the
  committed recordings."), `git status --short` empty after.
- `uv run python scripts/publish_game_profile.py --set-dir replays/samples/4p1i --json-stdout`: exit 1, "refused:
  replays/samples/4p1i holds a 4-player, 1-impostor roster; the game-shape profile reads 9-player, 2-impostor sets
  only".
- `.venv/bin/python <memo dir>/rubric-v2-repro.py replays/samples/9p2i`: exit 0, its text output byte-identical to
  an earlier run on this branch; a count-only comparison of the module's profile with the script's JSON output agrees on all
  six tripwire readings, all 16 shelves and their pointers, every class and p, the chip (15 meetings in 14 games), T2's
  15 flags with 1 evaluable, the per-game shelf counts (0:12, 1:11, 2:11, 3:7, 4:6, 5:1, 6:1) and the wave (70 of 195
  kills); one difference, sabotage starts 43 against 46 (decision 9).
- `uv run python scripts/publish_gameplay_census.py --check`, `uv run python scripts/publish_process_scorecard.py
  --check`, `uv run python scripts/gen_frontend_types.py --check`: exit 0 each.
- `uv run lint-imports`: 5 contracts kept, 0 broken.
- `git diff --exit-code d41c9006 -- experiments/lab/results-rubric-score.json experiments/lab/results-rubric-geomean.json`:
  exit 0. `git diff --stat main -- replays/`: one file, `replays/samples/9p2i/results-game-profile.json`, 6,175
  insertions.
- `bash scripts/verify_samples.sh`: exit 0, all 50 samples verified clean in each of the three sets it walks.
- `uv run python scripts/build_sample_report.py --sample-dir <set> --check` for `replays/samples/9p2i`, `4p1i`,
  `replays/ml_corpus/9p2i`, `4p1i`: exit 0 each.
- `uv run python scripts/validate_task_docs.py`: exit 0 (390 historical phase tasks, 390 prompts, 102 work cards).
  `uv run python scripts/check_doc_facts.py`: exit 0. `uv run python scripts/verify_ml_evidence.py` (offline): exit 0,
  64 checks, 52 OK, 0 FAIL, 7 ABSENT (the evidence branch, not restored on this checkout), 5 INFO.
- Frontend: `npx tsc --noEmit -p .` and `npx eslint src e2e` clean; `npx vitest run src`: 27 files, 808 tests passed (at `dc023329`);
  `npm run e2e`: 15 passed, 3 skipped (the README media capture, skipped by default), exit 0, 1.4 min.
- Bundles: `uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-base` at `ef1a2a59` and `--out
  <scratch>/bundle-head` at `00575283`, then `diff -rq` and a JSON diff of every common file: 71 JSON files to 72;
  added `data/9p2i/eval/game-profile.json` (6,232 bytes, seeds 14 and 19); changed exactly the five replay views
  (`data/9p2i/replays/headless-seed-19.json`, `-14.json`, `data/4p1i/replays/headless-seed-2.json`, `-11.json`,
  `-29.json`), each in `viewModelVersion` only, "5" to "6"; the other 66 JSON files byte-identical; no
  `data/4p1i/eval/game-profile.json`; `index.html` and the hashed assets differ (the new viewer).

**Planted proofs, red then green.** Each named test holds the planted case beside the real one, so the suite shows
both readings.
- Item 1: `test_strict_mypy_refuses_a_role_read_in_a_pre_reveal_reading` (a slow-burn copy reading `game.roles`, and a
  T2 copy reading `meeting.report.roles`, each fail strict mypy with the attribute error, since `BlindGame` holds no
  roles and `BlindMeeting` no report; corrected in round 1: a T2 handed a `GameReport` as a parameter passes mypy and
  is caught only by item 2's `test_a_t2_reading_the_report_roles_fails_the_role_property`);
  `test_a_scorecard_meeting_id_differing_from_the_carriers_raises`.
- Item 2: `test_a_fold_reading_the_carrier_fails_both_properties`, `test_a_fold_reading_the_ending_fails_the_ending_property`,
  `test_a_t2_reading_the_report_roles_fails_the_role_property`.
- Item 3: `test_the_seed_41_shape_trips_any_but_not_decisive`, `test_the_seed_26_shape_trips_decisive`,
  `test_a_not_assessed_ejecting_ballot_is_kept_as_recorded`, `test_the_recorded_floor_decides_the_planted_tally`,
  `test_removal_governs_where_reading_as_skip_differs`, `test_an_ejecting_none_held_ballot_raises_naming_all_four`.
- Item 4: `test_a_manufactured_flag_naming_the_ejected_player_trips`,
  `test_a_flag_naming_another_player_or_one_row_3_cannot_answer_does_not_trip`, and the join raise above.
- Item 5: per shelf, `test_slow_burn_needs_twenty_quiet_ticks` (19 quiet ticks),
  `test_two_kills_after_one_regroup_and_a_kill_one_tick_past_the_wave`, `test_a_close_call_is_a_margin_of_one` (a
  margin of two), `test_a_third_round_needs_three_meetings` (two meetings), `test_the_reporter_saw_it_happen` (a
  reporter outside the witness list), `test_a_same_tick_double_kill_joins_each_body_by_victim`,
  `test_suspicion_moved_away_from_a_living_player_but_not_from_the_dead`, `test_only_a_report_meeting_counts_as_a_reporter_or_a_report`.
- Item 6: `test_a_task_win_reads_the_symmetric_distance_from_its_living_count`,
  `test_the_pair_is_always_emitted_with_an_empty_half`, `test_the_eyewitness_chip_marks_a_holder_citing_its_own_kill_row`
  (the holder citing another id, and a `None` citation, do not mark).
- Item 7: `test_a_candidate_matching_one_ending_exactly_leaks`, `test_a_one_sided_p_fails_the_brute_force_property`,
  `test_a_universe_dropping_the_tripped_game_moves_the_shelf_and_fails` ((2, 4, 2, 42) p 0.0655 stays; (2, 4, 1, 42) p
  0.0361 moves).
- Item 8: `test_thirty_eight_of_fifty_is_a_facet_and_thirty_seven_a_shelf`, `test_saturation_applies_before_the_leak_rule`.
- Item 9: `test_a_moved_constant_fails_the_pin_until_its_version_moves` (slow burn 19 fails naming the constant, and
  passes only once the copy says version 3 and the table has that row); the sourced constants:
  `test_an_eighth_grounding_label_raises_unclassified`, `test_the_endings_follow_the_recorded_types`,
  `test_the_alibi_kinds_are_row_3s`, `test_the_wave_follows_the_recorded_kill_cooldown`, `test_the_era_is_the_registrys`,
  `test_the_glossary_states_the_modules_leak_and_saturation_numbers`.
- Item 10: `test_a_file_carrying_a_score_rank_or_total_is_refused_at_load`, `test_the_key_scan_refuses_a_planted_total`,
  `test_members_out_of_seed_order_raise`, `test_an_ending_facet_moved_before_the_reveal_fails_the_token_test`.
- Item 11: `test_one_edited_membership_turns_check_red`, `test_an_edited_page_turns_check_red`,
  `test_check_reports_an_absent_file_before_computing`, `test_a_page_naming_a_bar_or_a_ratio_fails_the_scan`,
  `test_the_stamp_is_read_before_and_after_the_walk`, `test_a_four_player_set_is_refused_by_name`.
- Item 12: `test_the_old_skip_line_fails_the_profile_case`, and the two era-rule cases with the old help sentence
  and the old comment.
- Item 13: `test_a_field_added_to_one_model_only_fails_the_mirror`, `test_each_stale_source_withholds_every_member`,
  `test_the_route_serves_9p2i_and_404s_on_4p1i`.
- Item 14: `test_a_member_pointing_past_the_last_meeting_fails_naming_seed_and_shelf` (and a kill tick moved one tick),
  `test_an_eyewitness_chip_past_the_last_meeting_fails_naming_seed_and_chip`.
- Item 15: "a reel sorted by how many shelves a game holds fails the order check (planted)", "shows them once
  revealed, so the unrevealed check can fail (planted)", "a wrong half listed alone fails the pair check (planted)",
  the tripped game planted onto a shelf in "keeps a tripped game off every shelf and labelled under All games"; the
  journey's 9p2i leg run against the base bundle (`AILIBI_DEMO_BUNDLE_DIR=<scratch>/bundle-base npx playwright test
  e2e/bundle.spec.ts`) fails at `evidence-journey.ts:66` (no "The reporter saw it happen" shelf holding seed 19), and
  passes on the head's bundle.
- Item 16: "a description carrying a threshold fails (planted)".
- Item 17: `test_the_scorer_before_the_retirement_wrote_one_and_fails_the_check` (`76270d6c`'s scorer, rebuilt in
  `tmp_path` from today's module and the deleted served-file write since round 1, writes `results-rubric-score.json`)
  beside `test_version_one_writes_no_served_file_for_the_era`.
- Item 18: `test_import_linter_refuses_a_planted_import_of_the_game_profile`, one leg per source package, each
  naming the contract BROKEN.
- Item 19: `test_a_bake_that_skips_the_trim_fails_the_shape`, `test_a_bake_passing_the_class_tables_through_fails_the_key_set`,
  `test_a_stale_profile_bakes_no_member`.
- Item 20: with `docs/artifacts.md`'s `replays/samples/` row left at its old 107 files, offline
  `scripts/verify_ml_evidence.py` exits 1: "[FAIL] in-tree family inventory ... replays/samples/: docs/artifacts.md
  promises 107 files, the index tracks 108"; at the head it exits 0.

**The neuter table** (item 21). Every statement, module-level tuple or dict row and call keyword argument of the
Python lines this card adds (whole new files; the added spans of the others) was neutered alone in a scratch copy of
the tree (a statement to `pass`, a row or argument deleted), its suite run, and the file restored from the in-memory
original; every TypeScript line the diff adds was deleted alone, then `tsc --noEmit` and `vitest run src` ran. A
target is red when the suite fails (for TypeScript, "compile" means `tsc` refused the neutered file). The harness is
scratch (`neuter.py`, `ts_neuter.py`), so the per-line rows are summarized here by file, with every survivor by line.

| file | targets | red on the first run | survivors and their resolution |
| --- | --- | --- | --- |
| `eval/game_profile.py` | 812 (519 statements, 253 arguments, 40 rows) | 789 | 15 `frozen=` arguments (14 dataclasses and the pydantic base config): killed by `test_every_projection_and_reading_is_frozen`. `if len(kills) != 1:` and its raise in `_kill_of`: killed by the strengthened `test_a_reported_body_joining_no_kill_raises`. The `if ejected is None: return frozenset()` guard in `meeting_readings`: redundant (a meeting that ejects no one has no ejecting ballot, so every reading is already empty), deleted in `fb8af924`. `strict=True` in `game_readings`' zip: equivalent, since `per_meeting` is built from `game.meetings` one for one. 3 skipped (`READING_LABELS` on one line): each member dropped by hand, all red (`test_one_line_two_readings`, `test_a_label_the_meeting_layer_dropped_is_refused`, mutant T1). |
| `scripts/publish_game_profile.py` | 196 | 193 | 3 skipped one-line rows (`PROFILE_SETS`, the two `PROFILE_ROSTER` members): dropped by hand, all red (`test_the_committed_profile_matches_a_recomputation`, `test_set_dir_prints_a_profile_and_writes_nothing`). |
| `api/replay_loader.py` (added spans) | 21 | 21 | none |
| `api/routes/eval.py` (added spans) | 2 | 2 | none |
| `api/schemas.py` (added spans) | 88 | 88 | none |
| `scripts/build_demo_bundle.py` (added spans) | 28 | 26 | `separators=` in the trimmed profile's `json.dumps`: killed by the compact-form check added to `test_the_featured_bake_ships_seeds_19_and_14_only`. `mode="json"` in its `model_dump`: equivalent, since every field of the view is a JSON-native type, so both dumps serialize to the same bytes. |
| `scripts/gen_frontend_types.py` (added spans) | 1 | 1 | none |
| `experiments/lab/rubric_score.py` (added spans; the rest are docstrings) | 1 | 1 | none |
| `scripts/verify_ml_evidence.py` (the two scope rows) | 2 | 2 | none |
| TypeScript, 7 files (`client.ts` 5, `GuidedTour.tsx` 2, `HighlightCard.tsx` 156, `ReplayFilters.tsx` 14, `ReplayPicker.tsx` 247, `TournamentDashboard.tsx` 107, `copy.ts` 146) | 677 | 615 (577 compile, 38 test) | 62 survived; 55 are red at the head, 7 named equivalent below. |

The 62 TypeScript survivors. Killed by tests added after `e4313207`: the timeline's role, label and
mark positions, the timeline's mount, the chip on a game with no shelf (`HighlightCard.tsx`); the ejection checkbox's
type, state, disabled flag, change handler and words (`ReplayFilters.tsx`); the ejection filter's guard, a shelf's
seed sort, the reveal-only shelves in the reel, each shelf's description and cards, the pair's heading, note and
cards, the revealed half's heading and note, All games' note, the load, stale, empty and region words
(`ReplayPicker.tsx`); the stale caveat and both column headings (`TournamentDashboard.tsx`); four ending words
(`copy.ts`, also held to `game_endings()` from Python). The container lines (the picker's profile request and status,
the dashboard's request) moved into pure functions the unit suite reads (`settledProfile`, `browserState`,
`momentsState`). Neutered against the live e2e spec (`npx playwright test e2e/evidence.spec.ts` in a scratch copy),
the effects' writes of a settled request and the moments panel's mount each failed it, while the two loading resets
did not; they were then removed by deriving loading from the request a result answers (`activeProfile`,
`activeMoments`, unit-tested), and the two writes that replaced them were neutered against the e2e spec again and
failed it. A re-run over the survivors and every line changed since (150 targets) left 11 (its
text match also took in three pre-existing `disabled={disabled}` lines of `ReplayFilters.tsx` outside this card's
diff, not counted). Four of the 11 were class-name lines carrying a visual encoding (the chip's base classes, the
timeline track, the kill mark's base classes, the tripwire label's box); tests of those encodings (a reveal-only chip
dashed, a chip before the reveal solid, a wave kill hollow, the tripwire label in a dashed box) now hold them and each
neuter goes red. The 7 left are named equivalent:
- six React `key` props (`HighlightCard.tsx` four, `ReplayPicker.tsx` two): identity hints that change no markup;
- one line inside a JSX comment (`ReplayPicker.tsx`, the absent state's set-neutral note): a comment.

**The mutation pass** (item 21): one bounded pass of 37 mutants, every one of the eight classes (F 5, S 4, N 6, K 5,
M 3, T 4, B 4, L 6), each applied alone in a scratch copy and run against the touched suites (`mutate.py`; the
Python suites with `-x`, the frontend with `vitest run src/components src/lib src/api`). 35 were killed on the first
run. K1 survived (no planted game held an emergency meeting naming a body) and is killed at the head by
`test_only_a_report_meeting_counts_as_a_reporter_or_a_report` (`e4313207`); M1 survived on a copy synced before the
join test was strengthened in `fb8af924` and is killed at the head by `test_a_reported_body_joining_no_kill_raises`.
No survivor is named equivalent.

| id | file | mutant | result | killed by |
| --- | --- | --- | --- | --- |
| F1 | `eval/game_profile.py` | the SKIP filter on the EJECT tally (`_eject_votes`) | killed | `test_the_committed_profile_matches_a_recomputation` |
| F2 | `eval/game_profile.py` | the vent-flag filter in decided without proof | killed | `test_decided_without_proof_splits_right_and_wrong_by_the_ejected_role` |
| F3 | `eval/game_profile.py` | the tripped-game filter on the eligible games | killed | `test_the_committed_profile_matches_a_recomputation` |
| F4 | `scripts/build_demo_bundle.py` | the baked-seed filter on a shelf's members (`_trimmed_profile`) | killed | `test_the_profile_is_trimmed_to_the_baked_seeds` |
| F5 | `frontend/src/components/ReplayPicker.tsx` | the tripped-game filter on a reel list (`reelSections`) | killed | the vitest suite (`src/components`, `src/lib`, `src/api`) |
| S1 | `eval/game_profile.py` | the living count read from the last meeting (`distance`) | killed | `test_the_committed_profile_matches_a_recomputation` |
| S2 | `eval/game_profile.py` | the current meeting's turns for the previous meeting's (`_suspicion_moved`) | killed | `test_suspicion_moved_away_from_a_living_player_but_not_from_the_dead` |
| S3 | `frontend/src/components/ReplayPicker.tsx` | the pre-reveal shelves for the reveal shelves (`cardProfiles`) | killed | the vitest suite (`src/components`, `src/lib`, `src/api`) |
| S4 | `scripts/publish_game_profile.py` | the set's files with and without the served file (`recording_inputs`) | killed | `test_the_recording_inputs_are_every_set_file_but_the_served_one` |
| N1 | `eval/game_profile.py` | the unclassified-label test inverted (`meeting_readings`) | killed | `test_the_seed_26_shape_trips_decisive` |
| N2 | `eval/game_profile.py` | the decisive tally comparison inverted | killed | `test_the_seed_26_shape_trips_decisive` |
| N3 | `eval/game_profile.py` | the missing-ending test inverted (`reveal_projection`) | killed | `test_the_reveal_game_adds_the_roles_the_ending_and_the_task_count` |
| N4 | `eval/game_profile.py` | the missing-victim test inverted (`blind_projection`) | killed | `test_the_reporter_saw_it_happen` |
| N5 | `api/replay_loader.py` | the absent-file test inverted (`ReplayLoader.game_profile`) | killed | `test_the_shown_set_serves_its_profile_fresh` |
| N6 | `frontend/src/components/ReplayPicker.tsx` | the winner filter comparison inverted (`matchesFilters`) | killed | the vitest suite (`src/components`, `src/lib`, `src/api`) |
| K1 | `eval/game_profile.py` | the report-trigger read replaced by a constant (reporter shelf) | SURVIVED on the first run; killed at the head | `test_only_a_report_meeting_counts_as_a_reporter_or_a_report` |
| K2 | `eval/game_profile.py` | the ejected player's role read replaced by a constant (the pair) | killed | `test_decided_without_proof_splits_right_and_wrong_by_the_ejected_role` |
| K3 | `eval/game_profile.py` | the kill tick replaced by 0 in a report's corpse age | killed | `test_the_pre_reveal_facets` |
| K4 | `eval/game_profile.py` | the kill tick replaced by 0 in the kill facet | killed | `test_the_pre_reveal_facets` |
| K5 | `eval/game_profile.py` | the ejected player's role replaced by a constant (a crewmate ejected) | killed | `test_the_leak_facts_are_each_recorded_ending_then_the_two_ejection_facts` |
| M1 | `eval/game_profile.py` | the meeting index dropped from the reported-body join message | SURVIVED on the first run; killed at the head | `test_a_reported_body_joining_no_kill_raises` |
| M2 | `scripts/publish_game_profile.py` | the set path dropped from the roster refusal | killed | `test_a_four_player_set_is_refused_by_name` |
| M3 | `api/replay_loader.py` | the file path dropped from the malformed-file message | SURVIVED on the first run (the kill recorded here came from the history test failing in a scratch copy with no git history, not from the mutant); killed in round 1 | `test_a_malformed_file_fails_loud` (round 1 probe A1) |
| T1 | `eval/game_profile.py` | `off_target` dropped from `READING_LABELS` | killed | `test_one_line_two_readings` |
| T2 | `eval/game_profile.py` | `(RUNAWAY, reads_the_ending)` dropped from the reveal shelves | killed | `test_the_committed_profile_matches_a_recomputation` |
| T3 | `scripts/build_demo_bundle.py` | `(reveal, class_tables)` dropped from the unbaked keys | killed | `test_the_profile_is_trimmed_to_the_baked_seeds` |
| T4 | `api/replay_loader.py` | `view_model_version` dropped from the refused file keys | killed | `test_a_malformed_file_fails_loud` |
| B1 | `eval/game_profile.py` | saturation and the leak rule swapped | killed | `test_saturation_applies_before_the_leak_rule` |
| B2 | `api/replay_loader.py` | the stale and fresh branches swapped (`game_profile`) | killed | `test_the_shown_set_serves_its_profile_fresh` |
| B3 | `frontend/src/components/ReplayPicker.tsx` | the pair's wrong and right halves swapped (`reelSections`) | killed | the vitest suite (`src/components`, `src/lib`, `src/api`) |
| B4 | `frontend/src/components/HighlightCard.tsx` | the right and wrong ejection annotations swapped | killed | the vitest suite (`src/components`, `src/lib`, `src/api`) |
| L1 | `eval/game_profile.py` | `grounding_labels()` replaced by its literal | killed | `test_an_eighth_grounding_label_raises_unclassified` |
| L2 | `eval/game_profile.py` | `game_endings()` replaced by its literal | killed | `test_the_endings_follow_the_recorded_types` |
| L3 | `eval/game_profile.py` | the recorded kill cooldown replaced by 6 | killed | `test_the_wave_follows_the_recorded_kill_cooldown` |
| L4 | `eval/game_profile.py` | `ALIBI_FLAG_KINDS` replaced by its literal | killed | `test_the_alibi_kinds_are_row_3s` |
| L5 | `scripts/publish_game_profile.py` | the MANIFEST reader replaced by the shown set's key | killed | `test_the_profile_stamp_reads_git_sha_from_an_8col_flags_manifest` |
| L6 | `scripts/publish_game_profile.py` | the registry argument dropped from `era_id` | killed | `test_the_era_is_the_registrys` |

**Limitations.**
- One 50-game recording, and no interval is claimed for any count or class.
- The leak classes swing between eras: one line, two readings sits on the boundary (p = 0.0498, open point 3), and
  dropping the tripped game from the tables would move two kills after one regroup (0.0655 to 0.0681), one line two
  readings (0.0498 to 0.0473) and struck after the regroup (0.0766 to 0.0256), as the Evidence states.
- The constants were chosen with these numbers in view, and the 0.05 level is not corrected for its 50 tests on this
  set; the rule only hides more.
- The facets the viewer already shows before the reveal (length, meetings) carry some ending information; the page
  says so.
- `none_held` is the voter's own statement, and an ejecting `none_held` ballot is refused until the owner says how T1
  reads it (open point 5).
- T2 is nearly blind: row 3 evaluates 1 of the shown set's 15 alibi-class flags.
- "Wrong on what it held" is direction section 7's wrong-but-believable class without that section's test that the
  cited line is true; the census measures that, and the profile does not read it.
- The eyewitness chip is not leak-tested, since the leak rule covers shelves.
- Sabotage starts count from the frames, so a sabotage started on a game's final tick is not in play (decision 9).
- Task documents that cite `/eval/rubric` or the v1 views in the present tense (`tasks/work/rubric-genuine-class-selfcheck.md`,
  `tasks/work/rubric-extractor-era.md`) are other cards' and history; this card does not write them.

**The house gate.** `bash scripts/check.sh` ran once, whole, in this clean worktree at the pushed head `a23b07ef`
(the Results commit; the commit recording this changes only this paragraph and item 21's box), its exit code read
directly from the script, not through a pipe: **exit 0**. Its steps: `ruff check .` all passed; `ruff format --check .`
567 files already formatted; `lint-imports` 5 contracts kept, 0 broken; `validate_task_docs.py` passed (390 phase
tasks, 390 prompts, 102 work cards); `generate_prompts.py --check` "All 390 prompts are in sync."; `mypy .` no issues in 538 source files;
`pytest -n auto --dist loadfile` 10,855 passed, 20 skipped, 3 xfailed in 347.5 s; frontend `npm run lint`, `npm run
tsc:check`, `npm run test` (27 files, 808 tests passed) and `npm run build` clean. That exit code came from a
full-history local worktree: CI's Project checks, on a shallow checkout, failed one test at that head and at
`53b9ffd3` (the item 17 planted case read `76270d6c` with `git show`); round 1 below corrects it.

### Review corrections, round 1 (2026-10-07)

Built on `53b9ffd3`; `origin/main` was still `ef1a2a59` at the final fetch, so `main` needed no merge. Commits:
`6fdfa78b` (the tests), this Results commit, then the commit recording the gate. No production line moved:
`git diff --stat 53b9ffd3` lists this card and four test files only (`tests/eval/test_game_profile.py`,
`tests/scripts/test_publish_game_profile.py`, `tests/api/test_game_profile_view.py`, `tests/api/test_sets.py`), so the
served file, the page and every number above stand as they were measured; the reading and the bundle below are
re-measured at this head.

**The findings and their repair.** The thirteen verifier findings (correctness, integrity and documentation lenses)
name eight defects.
1. CI red at `53b9ffd3` (one finding in each lens). Run 37614414977, job 112769195055: 1 failed, 10,834 passed;
   `test_the_scorer_before_the_retirement_wrote_one_and_fails_the_check` ran `git show
   76270d6c:experiments/lab/rubric_score.py`, which exits 128 on the shallow `actions/checkout`. The planted case now
   rebuilds the pre-retirement scorer from today's module and `_RETIRED_SERVED_FILE_WRITE`, five pairs of (a line of
   today's module, that line with the deleted code restored beside it) carried as text in `tests/api/test_sets.py`,
   each anchor asserted to occur once. It is not skipped and not weakened: it runs on every checkout and keeps both
   readings (today's scorer refuses `--set-dir` and writes nothing; the rebuilt one writes
   `results-rubric-score.json` and fails the same check). The rebuild's code is `76270d6c`'s: an AST comparison with
   every docstring stripped reads equal, and a `diff` against `git show 76270d6c:experiments/lab/rubric_score.py`
   shows 13 hunks, every one a docstring or a comment (scratch `rebuild_diff.py`, `ast_equal.py`). Without history:
   on a `git archive HEAD` export with no `.git` directory, `tests/api/test_sets.py` reads 62 passed. CI at the pushed
   head: in the gate paragraph below.
2. T1's "ejects someone else" clause was unpinned (V12, V13).
   `test_a_removal_that_hands_the_tally_to_another_player_trips_decisive`: four ballots eject `p-3` over three for
   `p-6`; with the `off_target` and `uncited` ballots removed the table ejects `p-6`, and decisive, read as SKIP and
   every ungrounded ballot removed each trip.
3. The saturation count in `read_pre_reveal` was unpinned on its tripped-game filter (V04).
   `test_a_tripped_member_does_not_saturate_a_candidate`: 37 untripped games and one tripped game of 50 carry a
   double kill; the catalogue says shelf, the shelf lists seeds 1 to 37, no game carries it as a moment, and the
   reading's saturated list is empty.
4. Suspicion moved's self-accusation filter was unpinned (V01). `test_a_self_accusation_keeps_no_suspicion_on_a_player`:
   the player who drew a ballot only accuses themselves at the next meeting, and the shelf marks that meeting.
5. Two loaded-source reads survived the literal swap (V19, V20). `test_the_leak_facts_follow_the_recorded_endings`:
   a planted ending the recorded types gain, placed first, leads the leak rows with its game.
   `test_an_eighth_grounding_label_stops_the_reading_and_the_profile`: a label the meeting layer gains stops
   `read_pre_reveal` and `build_profile` with the unclassified error.
6. Raise-site message arguments were unpinned (correctness V15 to V18 and V21 to V23; integrity V5, V6, V31, V32,
   V34; the documentation lens's 15 sites). Each existing test now matches its full message, anchored, with values
   off every default: seeds 4, 6, 9 and 12, meeting index 1, 1 against 2 meetings, seeds [9] against [] and [8],
   tick 5 and `body-p-1-5`, set `planted/9p2i`, the copy's path, `tmp_path`, the era id and the loader's file path in
   both invalid-profile-file messages. Strengthened in the same pass: the absent-file path, the candidate name and
   only the members outside the era, the 2x2 tuple of the negative-count refusal, the value in `_decimal`'s refusal,
   the shelf and chip names in the seed-order refusal, and `(10, None)` beside `(None, 14)` for the final task count.
7. The publisher's roster impostor count (V10, K) and registry path set (V9, S) were unpinned.
   `test_a_nine_player_set_of_another_impostor_count_is_refused` (9 players with 1 or 3 impostors, refused by name)
   and, in `test_the_era_is_the_registrys`, a registry without the shown set gives it no era.
8. Two documentation claims overstated. Item 1's second mypy plant is restated at its strength in the acceptance item
   and the planted-proofs line: strict mypy refuses `meeting.report.roles` because `BlindMeeting` holds no report,
   while a T2 handed a `GameReport` as a parameter passes mypy and only item 2's
   `test_a_t2_reading_the_report_roles_fails_the_role_property` catches it. Mutation row M3 now reads SURVIVED on the
   first run: its recorded kill came from the history test failing in a scratch copy with no history, not from the
   mutant. Rows re-checked for the same cause: only M3 named that test; N5, T4 and B2, the other first-pass rows on
   `api/replay_loader.py`, whose suites held it, were re-run against their named killers alone and each is red (probe
   table); every other row's named killer reads no git history (the card's suites call git only in
   `tests/test_firewall.py`, `git ls-files`, and `tests/scripts/test_refresh_samples.py`, `git status`, both of which a
   shallow checkout answers).

**The probe table.** One bounded pass of 38 mutants over the spans the findings name and the spans this round
changed, from the eight listed classes only. Each mutant was applied alone in place, the targeted suite run with `-x`
(`tests/eval/test_game_profile.py`, `tests/scripts/test_publish_game_profile.py`, or
`tests/api/test_game_profile_view.py` with `tests/api/test_view_model.py`; N5, T4 and B2 against their named killer
alone), and the file restored from its saved bytes and checked equal (scratch `mutate.py`; `git status` showed no
production file changed after the pass). The killer is the first failing test. All 38 are killed; none survives and
none is named equivalent. The first run is the verifiers' at `53b9ffd3`, where each of V01, V04, V09, V10, V12, V13,
V19, V20 and the named message arguments passed every suite.

| id | class | file | mutant | killed by |
| --- | --- | --- | --- | --- |
| V12 | N | `eval/game_profile.py` | the decisive tally `!= ejected` read as `is None` | `test_a_removal_that_hands_the_tally_to_another_player_trips_decisive` |
| V13 | N | `eval/game_profile.py` | the read-as-SKIP tally `!= ejected` read as `is None` | `test_a_removal_that_hands_the_tally_to_another_player_trips_decisive` |
| V04 | F | `eval/game_profile.py` | the tripped-game filter dropped from the saturated count (`read_pre_reveal`) | `test_a_tripped_member_does_not_saturate_a_candidate` |
| V01 | F | `eval/game_profile.py` | the self-accusation filter dropped from the charged set (`_suspicion_moved`) | `test_a_self_accusation_keeps_no_suspicion_on_a_player` |
| V19 | L | `eval/game_profile.py` | `game_endings()` in `era_facts` replaced by its six-ending literal | `test_the_leak_facts_follow_the_recorded_endings` |
| V20 | L | `eval/game_profile.py` | `label_classes()` in `read_pre_reveal` replaced by `LABEL_CLASSES` | `test_an_eighth_grounding_label_stops_the_reading_and_the_profile` |
| Ma | M | `eval/game_profile.py` | the scorecard's meeting count in the count refusal set to 0 | `test_the_projection_refuses_a_mismatched_scorecard` |
| Mb | M | `eval/game_profile.py` | the carrier's meeting count in the count refusal set to 0 | `test_the_projection_refuses_a_mismatched_scorecard` |
| Mc | M | `eval/game_profile.py` | the seed in the no-route refusal set to 0 | `test_the_projection_refuses_a_mismatched_scorecard` |
| Md | M | `eval/game_profile.py` | the seed in the scorecard seed-twice refusal set to 0 | `test_the_projection_refuses_a_mismatched_scorecard` |
| Me | M | `eval/game_profile.py` | the seed in the carrier seed-twice refusal set to 0 | `test_the_projection_refuses_a_mismatched_scorecard` |
| Mf | M | `eval/game_profile.py` | the location in the kill-names-no-victim refusal set to a constant | `test_a_kill_or_a_body_with_no_victim_raises` |
| Mg1 | M | `eval/game_profile.py` | the location in the body-names-no-victim refusal set to a constant | `test_a_kill_or_a_body_with_no_victim_raises` |
| Mg2 | M | `eval/game_profile.py` | the body id in the body-names-no-victim refusal set to a constant | `test_a_kill_or_a_body_with_no_victim_raises` |
| Mh | M | `eval/game_profile.py` | the scorecard's seeds in the seed-set refusal set to `[]` | `test_the_projection_refuses_a_mismatched_scorecard` |
| Mi | M | `eval/game_profile.py` | the location in the carrier-holds-no-game refusal set to a constant | `test_the_reveal_projection_refuses_an_unknown_or_missing_ending` |
| Mj | M | `eval/game_profile.py` | the location in the no-recorded-ending refusal set to a constant | `test_the_reveal_projection_refuses_an_unknown_or_missing_ending` |
| Mk | M | `eval/game_profile.py` | the location in the no-final-task-count refusal set to a constant | `test_the_reveal_projection_refuses_an_unknown_or_missing_ending` |
| Ml | M | `eval/game_profile.py` | the location in the unknown-ending refusal set to a constant | `test_the_reveal_projection_refuses_an_unknown_or_missing_ending` |
| Mm | M | `eval/game_profile.py` | the candidate name in the members-outside-the-era refusal set to a constant | `test_members_outside_the_era_are_refused` |
| Mn | M | `eval/game_profile.py` | the seed in the ejection-win-with-no-meeting refusal set to 0 | `test_an_ejection_win_counts_at_the_deciding_meeting` |
| Mo | M | `eval/game_profile.py` | the meeting index in the projection's meeting location set to 0 | `test_a_scorecard_meeting_id_differing_from_the_carriers_raises` |
| Mp | M | `eval/game_profile.py` | the meeting index in the ejecting `none_held` refusal set to 0 | `test_an_ejecting_none_held_ballot_raises_naming_all_four` |
| Mq | M | `eval/game_profile.py` | the name in the seed-order refusal set to a constant | `test_members_out_of_seed_order_raise` |
| Mr | M | `eval/game_profile.py` | the table in the negative-count refusal set to `(0, 0, 0, 0)` | `test_the_fisher_p_reproduces_the_design_memos_tables` |
| Ms | M | `eval/game_profile.py` | the value in `_decimal`'s refusal set to a constant | `test_the_served_constants_are_the_modules` |
| P1 | K | `scripts/publish_game_profile.py` | the roster's impostor read replaced by 2 (`require_profile_roster`) | `test_a_nine_player_set_of_another_impostor_count_is_refused[1]` |
| P2 | S | `scripts/publish_game_profile.py` | the given registry's paths swapped for `COMMITTED_SETS`' (`era_id`) | `test_the_era_is_the_registrys` |
| P3 | M | `scripts/publish_game_profile.py` | the set path in the roster refusal set to a constant | `test_a_nine_player_set_of_another_impostor_count_is_refused[3]` |
| P4 | M | `scripts/publish_game_profile.py` | the set path in the no-roster refusal set to a constant | `test_a_set_with_no_roster_names_no_seedset` |
| P5 | M | `scripts/publish_game_profile.py` | the set path in the walk-changed refusal set to a constant | `test_the_stamp_is_read_before_and_after_the_walk` |
| P6 | M | `scripts/publish_game_profile.py` | the era id in the two-sets refusal set to a constant | `test_an_era_holding_two_sets_is_refused` |
| A1 | M | `api/replay_loader.py` | the path in the not-an-object message set to a constant (row M3 re-run) | `test_a_malformed_file_fails_loud` |
| A2 | M | `api/replay_loader.py` | the path in the loader's-to-set message set to a constant | `test_a_malformed_file_fails_loud` |
| A3 | M | `api/replay_loader.py` | the path in the absent-file error set to a constant | `test_the_four_player_set_ships_no_profile` |
| N5 | N | `api/replay_loader.py` | the absent-file test inverted (row N5 re-run, named killer alone) | `test_the_shown_set_serves_its_profile_fresh` |
| T4 | T | `api/replay_loader.py` | `view_model_version` dropped from the refused keys (row T4 re-run, named killer alone) | `test_a_malformed_file_fails_loud` |
| B2 | B | `api/replay_loader.py` | the stale and fresh branches swapped (row B2 re-run, named killer alone) | `test_the_shown_set_serves_its_profile_fresh` |

**Verification at `6fdfa78b`** (production code identical to `53b9ffd3`; a scratch `validate.sh` ran each command and
logged its exit code directly).
- `env | grep -c '^AILIBI_'`: 0.
- The card's first pytest line (eleven files, `-n 6 --dist loadfile`): 481 passed, 1 skipped (the pre-existing
  `tests/api/test_view_model.py:399` skip), the seven new cases among them. `uv run pytest
  tests/scripts/test_refresh_samples.py -n 4 --dist loadfile`: 167 passed, exit 0.
- `uv run python scripts/publish_game_profile.py --check`, twice: exit 0 both ("... are consistent with the committed
  recordings."). `--set-dir replays/samples/4p1i --json-stdout`: exit 1, "refused: replays/samples/4p1i holds a
  4-player, 1-impostor roster; the game-shape profile reads 9-player, 2-impostor sets only".
- `.venv/bin/python <memo dir>/rubric-v2-repro.py replays/samples/9p2i`: exit 0, the same reading as the served file
  (count-only): every 0; decisive removed, read as SKIP and all ungrounded removed 1 each, (26, 2); any 2, (26, 2) and
  (41, 0); manufactured 0 of 15 alibi-class flags; ejecting-ballot labels 282 `supported`, 2 `off_target`; endings 13
  `CREWMATE_EJECT`, 13 `CREWMATE_TASKS`, 24 `IMPOSTOR_PARITY`, 46 games ejecting someone; the seven pre-reveal shelves
  14, 7, 11, 6, 16, 16 and 19; caught venting (p under 0.001) and one line, two readings (0.050) leak; struck after
  the regroup 40 of 50, a facet; seeds 19 and 14 as Publication quotes them.
- `scripts/publish_gameplay_census.py --check`, `scripts/publish_process_scorecard.py --check`,
  `scripts/gen_frontend_types.py --check`: exit 0 each. `uv run lint-imports`: 5 contracts kept, 0 broken.
- `git diff --exit-code d41c9006 --` the two baseline-9 lab files: exit 0. `git diff --stat ef1a2a59 -- replays/`: the
  one served file, 6,175 insertions.
- `bash scripts/verify_samples.sh`: exit 0, "All 50 samples verified clean." for `replays/samples/4p1i`,
  `replays/samples/9p2i` and `replays/candidates/stage-b-r1/9p2i`. `build_sample_report.py --sample-dir <set> --check`
  for `replays/samples/9p2i`, `replays/samples/4p1i`, `replays/ml_corpus/9p2i`, `replays/ml_corpus/4p1i` and
  `replays/candidates/stage-b-r1/9p2i`: exit 0 each.
- `scripts/validate_task_docs.py`: exit 0 (390 phase tasks, 390 prompts, 102 work cards). `scripts/check_doc_facts.py`:
  exit 0. Offline `scripts/verify_ml_evidence.py`: exit 0, 64 checks, 52 OK, 0 FAIL, 7 ABSENT (the evidence branch,
  not restored here), 5 INFO. `uv run pytest -m campaign`: 337 passed, exit 0.
- Strict mypy over the four changed test files: no issues; `ruff check` and `ruff format --check` clean on them.
- Frontend: `npm run lint`, `npm run tsc:check` exit 0; `npm run test`: 27 files, 808 tests passed; `npm run e2e`
  (serial, one worker): 15 passed, 3 skipped (the README media capture), exit 0, 1.5 min.

**The gate, round 1.** Two environments, quoted separately.
- Local, this full-history worktree: `bash scripts/check.sh` ran once, at the pushed head `caac7e91` (the commit
  recording this changes only this paragraph and the first Review correction item's proof sentence, which now names
  the history-free export and the CI run), its exit code read from the background run's own report, not through
  a pipe: **exit 1**. Every step before pytest passed: `ruff check .` all passed; `ruff format --check .` 567 files
  already formatted; `lint-imports` 5 contracts kept, 0 broken; `validate_task_docs.py` passed (390, 390, 102);
  `generate_prompts.py --check` all 390 in sync; `mypy .` no issues in 538 source files. `pytest -n auto --dist
  loadfile`: 1 failed, 10,861 passed, 20 skipped, 3 xfailed in 351.7 s. The one failure is
  `tests/orchestrator/test_run_limits.py::test_wall_deadline_cancels_meeting_and_retains_success`, whose assertion
  needs a 0.25-second wall deadline to land inside a meeting in a loaded xdist worker (`assert 0 == 2`: the deadline
  passed before the first model call); earlier cards record it as load-sensitive
  (`tasks/work/followup-review-dispositions.md`, `tasks/work/fresh-deduction-instrument.md`). Run alone at the same
  head it passed five times in five, and this round changes no file it reads (four test files of other suites and
  this card). `set -e` then stopped the script before its frontend leg, which ran on its own instead: `npm run lint`,
  `npm run tsc:check` and `npm run test` (808 passed) at `6fdfa78b`, and `npm run build` at `caac7e91` inside the
  head bundle's build, each exit 0. The whole gate was not re-run, by the run-once rule.
- CI, a shallow `actions/checkout`: run 37624561446 at `caac7e91`, conclusion success. Project checks (job
  112802905173) 10,842 passed, 40 skipped, 3 xfailed in 1,286.8 s, with no failure (the item 17 planted case carries
  no skip, so it ran and passed); Frontend checks and Frontend e2e (Playwright) success.
