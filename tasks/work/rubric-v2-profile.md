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

- [ ] **1. The pure module and its role-stripped projection.** `eval/game_profile.py` (new) imports the carrier
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
    `game.roles` and requires the attribute error; a second copy whose T2 takes a `GameReport` and reads its `roles`
    fails mypy the same way.
- [ ] **2. No pre-reveal byte reads a role or the ending.** Hypothesis properties over hand-built carriers and the
  committed one: permuting the seeded roles (counts kept) on the census carrier and on `load_set_inputs`'s
  `GameReport`s together, or swapping the end reason and winner for another recorded value on both, leaves every
  pre-reveal membership, pre-reveal facet, chip and tripwire byte-identical. Planted: a fold whose predicate closes over
  the full carrier and reads a role fails both properties; a T2 that also requires `GameReport.roles` to name the
  ejected player a crewmate fails the role property on a hand-built carrier whose manufactured flag names the ejected
  player.
- [ ] **3. T1, decisive.** An ejection trips when, its ejecting ballots labelled `off_target`, `uncited` or
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
- [ ] **4. T2, a manufactured contradiction.** An ejection trips when its `BlindMeeting`'s manufactured subjects
  (item 1: alibi-class flags that row 3's `_flag_is_manufactured` classes as manufactured over `load_set_inputs`'s
  route) name the ejected player. T2 reads only `BlindGame`; the join and its raise live in `blind_projection`. The page
  says it is nearly blind (row 3 evaluates 1 of the shown set's 15 alibi-class flags). Planted: a manufactured flag
  naming the ejected player trips; one naming another player, or an unevaluable flag, does not; a scorecard meeting id
  that differs from the carrier's raises in the projection.
- [ ] **5. The pre-reveal shelves**, defined as the memo's Part 2.3 states and `rubric-v2-repro.py` implements (where
  the two differ in words the script governs, and Results names the difference): the reporter saw it happen, double
  kill, slow burn, two kills after one regroup, a close call, suspicion moved (ballots and accusations only, never the
  scalar), a third round. The witness test joins the trigger body to its kill by victim. Mechanism: one positive and
  one negative hand-built carrier per shelf; the committed file through `--check` (item 11). Planted per shelf: the
  boundary case (19 quiet ticks; a wave kill one tick past the window; a margin of two; two meetings; a reporter
  outside the witness list; same-tick double kills of two victims joined to the right body; a player who drew ballots
  and then died is not suspicion moving away).
- [ ] **6. Reveal shelves and facets.** Reveal shelves: caught venting and one line, two readings (by the leak rule),
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
- [ ] **7. The leak rule.** Each candidate pre-reveal shelf (the seven, caught venting, one line two readings, struck
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
- [ ] **8. The saturation rule.** A candidate holding more than `SATURATION_SHARE` of the era's games is served as a
  facet, never a shelf, and recorded so. Planted: 38 of 50 is a facet, 37 of 50 a shelf; saturation applies before
  the leak rule.
- [ ] **9. Constants.** The design constants are `Final` and frozen by this card: slow burn 20 ticks, wave slack 4,
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
- [ ] **10. The served file refuses a number to climb.** `GameProfile` (pydantic, frozen, `extra="forbid"`) has a
  pre-reveal half (shelves in fixed order, each member a seed with its meeting indexes or kill ticks; per-game facets
  and meeting chips; tripwires; All games) and a reveal half (reveal shelves, facets, the class tables). Mechanism and
  planted cases: a
  file carrying `score`, `rank` or a per-game total is refused at load; a key-name scan over both models refuses
  `score`, `rank`, `total`, `points`, `weight`, `best` and `top`; a member list out of seed order raises; a token test
  finds no `winner`, `reason`, `IMPOSTOR` or `CREWMATE` in the pre-reveal half (planted: an ending facet moved there).
- [ ] **11. The publisher, the page and the drift check.** `scripts/publish_game_profile.py` writes the served file
  for each set in `PROFILE_SETS` (9p2i only) and `docs/game-profile.md`; `--check` recomputes both and exits 1 naming
  the drifted file, reporting an absent file before computing; `--set-dir DIR --json-stdout` prints a 9-player set's
  profile (a candidate round, a baseline-9 export) and writes nothing; a set of another roster (4p1i) is refused by
  name. The stamp reads the loader's own MANIFEST reader and `recording_fingerprint`, before and after the walk (a
  difference raises). The page states the definitions, the stamps, shelf sizes and members, the tripwire table with
  T2's near-blindness, the class tables, the chip-count lean, that facets the viewer already shows carry some ending
  information, and that no pre-registration, step rule, gate or objective reads the profile. Mechanism: a pytest drift
  test; planted: one edited membership turns `--check` red; a page naming a bar or a ratio of two rates fails.
- [ ] **12. The refresh step and its text are true.** For `replays/samples/9p2i` under its era config the step runs
  the publisher and the dry run says it "would regenerate" the profile; any other target prints no profile line. The
  skip clause goes. The `--experiment-config` help and the `declared_args` comment state the era rule: a committed set
  records only its own era's declared config, or bare when its era declares none; a candidate round or a scratch
  directory takes any config. Mechanism: dry-run and `--help` cases in `tests/scripts/test_refresh_samples.py` (run
  `--dist loadfile`); `_REFRESH_OUTPUT_NAMES` names the profile. Planted: the old skip line and the old help sentence
  each fail their case.
- [ ] **13. The API.** `GameProfileView` and its member views replace `RubricView`/`RubricGameView`, mirroring
  `GameProfile` field for field; `VIEW_MODEL_VERSION` goes to "6" with one comment line; `ReplayLoader.game_profile`
  serves the file, raises `FileNotFoundError` when absent (the route answers 404) and serves `stale: true` with no
  members on a MANIFEST, seedset or fingerprint mismatch; `/eval/game-profile` replaces `/eval/rubric`. The generator
  lists the new views and `frontend/src/types/api.ts` is regenerated; the client reads version "5" replay payloads.
  Mechanism: `tests/api/test_game_profile_view.py` (new) and the re-targeted `test_sets.py`, `test_view_model.py`,
  `test_schemas.py` and `test_leak.py`; `gen_frontend_types.py --check`. Planted: a field added to one model only fails
  the mirror test; each stale source suppresses members; 9p2i serves, 4p1i 404s.
- [ ] **14. Every pointer is true of the served replay.** For every member of the committed profile and every meeting
  chip, each meeting index names a meeting the served `ReplayView` holds with the same id, and each kill tick a tick
  where it shows a kill, in the `api/public_results.py:98` `_check_case` idiom. Planted: a member pointing one meeting
  past the last fails, naming seed and shelf; an eyewitness chip moved one meeting past the last fails, naming seed
  and chip.
- [ ] **15. The viewer.** The Highlights tab ("Browse by moment") renders the pre-reveal shelves in the file's order,
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
- [ ] **16. Copy and terms.** Every new string lives in `SPECTATOR_COPY`, in plain words with no task or audit id, no
  unexplained term and no threshold arithmetic; the copy walk (`dialectHits`) covers it and the component sources.
  The wrong shelf reads, in substance, "the voters cited lines they held and it pointed the wrong way; a wrong call on
  believable evidence is part of the game", beside "the table was right". `docs/glossary.md` extends its game-shape
  profile entry and adds the shelf names, the eyewitness chip, tripwire, decided without proof, wrong on what it held,
  and the leak and saturation rules. Planted: a description carrying "20 ticks" fails the copy test.
- [ ] **17. Version 1 retires for the era.** Deleted: `regen_for_set`, the `--set-dir` branch and their tests;
  `rubric()`, the route, both DTOs, `_trimmed_rubric`; the score badge, spokes, buckets, histogram, `RUBRIC_SPOKES`
  and the interestingness strings. Kept as history: `experiments/lab/rubric.md` with one dated line (retired for
  `stage-b-r2` on the ruling's date, superseded by this profile), the two baseline-9 lab files (byte-identical to
  `d41c9006`), the frozen parity pin and `eval/watchability.py`. No code path left can write a v1 served file.
  Mechanism: `git grep` for the deleted names in Results; `git diff --exit-code d41c9006 --` the two lab files; a test
  that runs `rubric_score.main` with `--set-dir` on a `tmp_path` copy of the era's set, given synthetic facts stamped
  with that copy's recording fingerprint (the `_synthetic_facts` idiom of `tests/api/test_sets.py:341`, since the
  unwidened extractor refuses the era), and requires a non-zero exit and no `results-rubric-score.json` written.
  Planted: the same run against `76270d6c`'s scorer, loaded from `git show` into `tmp_path`, writes the file and fails
  the test.
- [ ] **18. Nothing reaches an agent.** A new `.importlinter` forbidden contract keeps `agents`, `meetings`,
  `orchestrator`, `engine` and `training` from importing `eval.game_profile` or `scripts.publish_game_profile`;
  the bake-off entrant scan already bans every `eval.*` import. Mechanism: `uv run lint-imports`. Planted: one leg per
  source package in `tests/test_firewall.py`'s copied tree, each naming the contract BROKEN.
- [ ] **19. The bundle.** `_trimmed_rubric` becomes a trimmed profile; 9p2i bakes `data/9p2i/eval/game-profile.json`,
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
- [ ] **20. The registry follows the bytes.** In `docs/artifacts.md`, re-derived last after the final merge of `main`:
  the `replays/samples/` row (107 files to 108 at authoring; its size re-measured) and one new row for
  `docs/game-profile.md`, scoped in `scripts/verify_ml_evidence.py`'s two tables. Mechanism:
  `test_every_counted_registry_row_matches_the_index` and offline `scripts/verify_ml_evidence.py`. Planted: a stale
  row fails; Results quotes the red run.
- [ ] **21. The wave lessons hold.** Each production line is neutered alone and its suite goes red (Results carries
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

Not started.
