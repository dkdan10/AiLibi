# Candidate round 3: the route lines on the shown set's rules

**Status:** ready

## Outcome

Round 2 is the shown 9-player set. Its one measured failure of the owner's first goal is held lines misapplied: the
route-check replay counts 40 ejections carried by a charge against a pair of places the map or the public regroup
reconciles, 7 of them at kill-witness meetings. The owner ruled on 2026-10-06 to re-key the reporter line and, on
the orchestrator's recommendation, to spend one round on the narrow role-blind route field. This card records that
round: one 50-seed recording that differs from round 2 in exactly one key, the route field ON at version 1, assessed
against readings committed, and confirmed by the owner, before the first seed.

After this card:
- `replays/candidates/stage-b-r3/9p2i/` holds seeds 0-49 of the 9-player roster (9 players, 2 impostors, 2 tasks
  per crewmate), recorded on featherless `Qwen/Qwen3.6-27B` with the prompt set `qwen3_6_27b`, the bare substrate
  slate and one declared config, round 2's plus the route field. Every tick row carries it; the README its sha256.
- `audits/audit-<YYYY-MM-DD>-stage-b-r3.md` opens with the pre-registration (pushed before the owner confirms it)
  and the owner's confirmation (pushed before the first seed), then the pre-spend, the spend, the gates and events,
  and the assessment in three columns never pooled (round 1, round 2, round 3), the step the rule names and a menu.
- Round 1 and the shown set stay byte for byte. Nothing publishes, the ladder tip stays at baseline 9, the round
  adopts nothing, and the step and any promotion (a later card, the owner's merge) are the owner's. This card changes
  no code, template or instrument; its one test edit is the golden's pin row for the new set.

## Evidence

Doctrine: `tasks/direction-2026-09-19-process-over-outcome.md` section 12 and addenda; the decision memo sections
0, 1, 3 and 7; `docs/architecture.md`; `docs/experiment-arms.md`; `docs/gameplay-census.md`;
`docs/process-scorecard.md`; `audits/audit-2026-10-01-stage-b-r2.md` sections 1 to 9 (the protocol copied here);
`tasks/work/stage-b-record-r2.md` (the template); `tasks/work/route-check-replay.md` (its Reading of 2026-10-03);
`tasks/work/census-reporter-base-rate.md`; `tasks/diagnosis-2026-10-02/README.md` Parts 1, 3 and 4; the baselines
memo of 2026-10-03, Parts 3.4 and 4. Every `path:line` is a citation at `76270d6c`, re-anchored by symbol at
dispatch; every count was measured at `76270d6c` (count-only) and is re-measured at dispatch.

**The owner's rulings, verbatim and dated**, quoted whole again at P: the 2026-09-24 50-seed record ruling, the
2026-09-27 ceilings and the 2026-09-28 wall, as round 2's audit 1.1 quotes them; 2026-10-01, "Merge.  Adopt all 7
non-balance arms. And run a balance round"; 2026-10-02 (that audit's 9.1), "1. Merge 2. Promote and run the
diagnostics."; and 2026-10-06, on the baselines memo:

  > 1. Rekey 2. What is your recommendation? I slightly lean to spend with narrow field, but would go with your
  > recommendation 3. Rebase the rubric. Maybe spend time thinking if it needs to be completely redone with the
  > context from this conversation. 4. README should be current and can be a focus in the last steps, once the
  > project is stable. 5. Sounds good 6. Sounds good 7. Sounds good 8. Merge when ready

**The orchestrator's readings of that ruling** (not the owner's words; they bind this card): (1) the envelope's
reporter line is re-keyed to reporter seats ejected without vent proof against other crewmate seats ejected without
vent proof, a flag the step rule does not read; round 2's reading under the old 0.104 line stands; this card
proposes the bar, the owner confirms it before the first seed. (2) Round 3 spends on the narrow route field: same
seeds, the eight rules plus cooldown 6, the standing ceilings, no `evidence_reasoning_version`, recording only after
the field card merges, its rehearsals pass, P lands and the owner confirms. (3) The carrier of round 2's not-carried
cells is named in P for the owner to confirm. (4) The ML hold stands. (5) The rubric, README and front door wait.

**Round 2, the comparison base** (its audit sections 5-6; now `replays/samples/9p2i`, era `stage-b-r2`): 50 seeds,
117 meetings, 691 ballots, tally `1502 9187880 418270 0.0`; spent with its two husks 1,588 calls, 9,726,227 input,
441,092 output, 12,927 s (3.59 h), $0. Impostor wins 24/50 = 0.48 (0.35-0.61). Its reporter line read 17/114 =
0.149, flagged above 0.104, so its rule named no step; the owner promoted it regardless (audit 9.2). **Round 1**
(`replays/candidates/stage-b-r1/9p2i`): 124 meetings, tally `1556 9344346 433660 0.0`, impostor wins 34/50.

**The route-check replay** (`experiments/lab/route_check_replay.py`; committed `results-route-check-replay.json`,
`rule_inputs`): misjudged cases M and the witness subset W read r2 40 and 7, r1 29 and 0, baseline-9 50 and 0. On
r2 the walkable-pair clause reaches 15 of 40; `evidence_reasoning_version = 2` as recorded reaches 16 and keeps
none of its 4,478 regroup-crossing rows at the recorded ballot budget; the reference check (c) reaches 29 of 40 and
7 of 7, every misjudged innocent ejection (21 of 21) and every ejected witness (5 of 5); its 11 unreached cases are
impostor ejections, 9 resting on a vent sighting. Reaching is showing a line, not changing a vote; no model was run.
The instrument takes only the labels `s9`, `r1`, `r2` (`COLUMN_LABELS`, `experiments/lab/route_check_replay.py:267`).

**The census cells** the readings read are named by key in the Acceptance table, round 1's and round 2's values from
`publish_gameplay_census.py --set-dir DIR --json-stdout` and `measure_baseline.py DIR --honesty --json` at
`76270d6c`; 18 read 0 by construction on both. The keys of the held-data and route cells are the ones
`census-held-data-cells` contracts (its items 1 to 4), and the route cells' model is `route-lines-field`'s. Of round
2's four not-carried cells, three are census cells now (the regroup notice, ballots citing a rebuttal, holds-nothing SKIPs);
false resume perceptions have no count source, and their carrier is the helper `compose_resume_events` plus the
golden's byte-equal re-render of every recorded prompt. The census and scorecard `--set-dir replays/samples/9p2i`
equal the shipped `samples/9p2i` entries (1,324 of 1,324 and 108 of 108 leaves).

**What `F` must hold.** F is `main` after the three first-wave cards, `route-lines-field`, `census-held-data-cells`
and `crew-idle-policy-lab`, and `rubric-v2-profile` merge, and after the field card's rehearsals pass (the cards'
Results name each item by key; this card writes none of it; the round reads none of the profile, which lands before
F because it writes `eval`, `api`, `scripts`, `frontend` and `experiments` and changes the bundle):
- from `route-lines-field`: the field (written here `route_lines_version`; default None, omitted at default, set only
  from the config file), its `FIELD_LAYER` entry, `READABLE_SETTINGS` readers that thread or refuse, a composite
  `vote_ballot` stamp served through the spine registry, its planted cases, rehearsals and lab rows passed (with
  the added-input projection on round-2 bytes), and an `r3` column in both route instruments declaring this round's
  config;
- from `census-held-data-cells`: the three held-data cells (baselines memo Part 3.4 items 1-3): holds-nothing SKIPs
  checked against the voter's own inputs; cited claims checked against the engine route; ejections whose target
  had a stated pair the map reconciles, with the witness-meeting subset; and the route field's conformance cell
  (`route_lines_false_to_the_map`, `route_lines_off_the_table`, presence `meetings_with_a_route_line`), on the
  field card's model;
- from `crew-idle-policy-lab`: its lab arms, split and capture and its `training/` text. The round reads none of it;
  it lands before F because it writes `experiments/`, `training/`, `audits/tactical-gameplay/` and the `audits/` row
  of `docs/artifacts.md`, which this card's nothing-moves diff and the round's freeze cover.

**The declared config**, one line plus a newline, 342 bytes if the field merges as `route_lines_version`: round 2's
316-byte file (sha256 `0c02fa61069c37131e2369a2a408d1a2f555521d696bbc7823b918709ac5192b`) with
`, "route_lines_version": 1` inserted before the closing brace, printing sha256
`a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d`; P recomputes it on the merged name. The stamps
are round 2's three `.v6` stamps and the `vote_ballot` composite of three arms in field-declaration order (ending
`+vote_ballot.qwen3_6_27b.v8.route_lines_v1` for a field declared last), as `prompt_versions_for_set` prints at F.

**Hazards.** The recorder reads `HEAD` once per run into every MANIFEST `git_sha` (`scripts/refresh_samples.sh:761`),
re-records any seed it is given, refuses the fake provider under `replays/` (`:683-706`) and stages beside the set,
where `_replays_tree_restored` (`tests/scripts/test_refresh_samples.py:1269`) deletes new paths. The golden raises
for an unpinned set (`tests/meetings/test_prompt_byte_golden.py:1360-1376`). Baseline-9's 9p2i bytes live at `d41c9006`.

## Acceptance

Each item names its enforcing mechanism and the planted or perturbed case that proves it bites. `F` is `main` after
the three first-wave cards (`route-lines-field`, `census-held-data-cells`, `crew-idle-policy-lab`) and
`rubric-v2-profile` merge and the field card's rehearsals pass. `P` is the pre-registration `coordination:` commit on
`work/stage-b-record-r3`; its
tree differs from `F`'s only in the audit, its `audits/README.md` row and the `audits/` row of `docs/artifacts.md`.
`Q` is the later `coordination:` commit adding the owner's confirmation as a dated addendum. `C` is
`replays/candidates/stage-b-r3/9p2i`, `R1` round 1's set, `R2` `replays/samples/9p2i`, `CFG` the round's config.

- [x] Review correction (round 2): the `audits/` row of `docs/artifacts.md` states the audit record's tracked bytes
  at the head that carries it. `13370e5c` appended section 11 (2,549 bytes) and left the row at 31,571,362, so the
  offline evidence check exited 1 and CI run 37937850895 at `13370e5c` read Project checks 2 failed; `6b014cba`
  re-derives it to 31,573,911 / 335 files (`git ls-tree -r -l 13370e5c audits`), and `08362561` again to 31,574,099 /
  335 files for its index edit. Proven by offline `scripts/verify_ml_evidence.py` (exit 0: OK 52, FAIL 0) and
  `tests/scripts/test_verify_ml_evidence.py` (90 passed, among them `test_every_counted_registry_row_matches_the_index`
  and `test_main_runs_the_cheap_legs_green_at_head`, the two red at `13370e5c`).
- [x] Review correction (round 2): the declared-round walk compares the loaded config's own sha256 and reads each
  declared set by its own name. Proven by
  `tests/meetings/test_route_lines_arm.py::test_only_a_declared_round_recording_the_field_on_may_read_it_on`
  (fourteen plants, `93ecd5f8`): a round holding other ON bytes than it declares is listed, and one declaring those
  bytes is not; a round declaring its seeds under `4p1i` is not listed, and one declaring `9p2i` and `4p1i` with its
  `4p1i` seed recorded OFF is. Both survivors of the review (the sha256 replaced by round 3's literal line; the set
  name by the literal `9p2i`) now fail 2 cases each; scratch probe, 18 mutants, 13 killed, 5 equivalent.
- [x] Review correction (round 2): the card, the audit index and the pull request body match the head. The step
  subsection no longer claims CI green at a head whose run failed; the index row says section 11 records the step
  (Codex 4230751225); the pull request body cites the green run at its pushed head by id and marks its draft and
  step-not-written statements superseded by `13370e5c`. Proven by `scripts/validate_task_docs.py` and
  `scripts/check_doc_facts.py` (exit 0 each), `copy_problems` 0 and the identifier scan 0 on the index row's prose,
  and `gh run view` on the run the body cites (its `headSha` the pull request's head, conclusion success).
- [x] Review correction: the route-lines card's committed-payload case asserts, at the strength it had, that every
  committed payload, every listed set and every `experiment-config.json` under `replays/` reads `route_lines_version`
  OFF, leaving out only a candidate round's declared config whose round recorded the field ON, enumerated from the
  candidate declarations, never by a path (the record's one stop, audit 7.5, re-scoped test-only by the
  orchestrator's assignment). Proven by
  `tests/meetings/test_route_lines_arm.py::test_only_a_declared_round_recording_the_field_on_may_read_it_on` (ten
  plants: an ON config under `samples/9p2i` or `ml_corpus/9p2i` and a listed set recorded ON are listed, and so is
  the round's config when its declaration names other bytes, names no set or appears twice, or a declared seed is
  missing or recorded OFF; the round as declared, on round 3's bytes, and a round still recording are not), by a
  scratch ON config in `replays/samples/9p2i` turning the committed case red, and by CI run 37932710107 at
  `368109f7`, green.
- [x] **The pre-registration and the owner's confirmation precede the first seed, and neither is rewritten.**
  Mechanism: no provider call before Q is pushed. P holds the rulings and readings above verbatim and dated, the
  config bytes and sha256, Constraints' ceilings, stops and discipline, the table, the flag and the step rule below,
  and `readings.py` and `reproject.py` whole, as Validation quotes them (each with its sha256 as extracted from this
  card). The config is not committed at P (a round directory without its set directory fails the candidate test);
  the delivery commit adds it with P's sha256. Until then each checkout holds an untracked copy at `CFG`, checked by
  `shasum -a 256` before the dry run and every gate (a mismatch stops the card), and no pytest or `check.sh` runs
  beside that copy. Q quotes the owner, in their own words and dated, confirming five
  points: the ceilings; the pre-registration; the reporter flag's form and bar; the carrier of round 2's
  not-carried cells (resume perceptions by the helper plus the golden; the turn citation as the cell for ballots
  citing a rebuttal, the counter slot beside it); and that the step rule may take the impostor win share as one of
  its conditions. The owner confirmed all five as proposed on 2026-10-09, before P (decision memo 8.7); Q quotes
  that confirmation. An amendment lands as a new pre-registration commit (the old
  section kept, the amendment dated) and is confirmed again; the recording checkout detaches at the commit holding
  the confirmed text, which this card calls P. `git merge-base --is-ancestor` exits 0 for F before P, P before Q, Q
  before the first `record:` checkpoint and P against the MANIFEST's one `git_sha`; Q's committer date precedes the
  probe's start in the operator log and every MANIFEST `refreshed_at`; P's section equals the PR head's. Proof: the
  head in place of P exits 1; a scratch MANIFEST with one `refreshed_at` before Q fails the date check; a
  one-character edit to a reading prints a diff.
- [x] **The before columns are computed, never typed.** Mechanism: at F the census and scorecard `--set-dir R2
  --json-stdout` equal the shipped `samples/9p2i` entries leaf for leaf; on R1 and R2 the readings command prints
  every round-1 and round-2 count round 2's audit section 6 and Evidence state, 0 differing; the instrument's r1 and
  r2 columns at F equal the committed JSON's (M, W and each reach). A moved count stops the card. Proof: each
  comparison against a copy with one cell edited prints that cell and exits 1.
- [x] **The readings are pre-registered in three columns.** Mechanism: `readings.py CENSUS HONESTY ROUTE --column
  {r1,r2,r3} [--bar {A,B,C}] [--after] [--step]` (Validation, quoted whole) computes each reading from the keys
  named here; with `--after` it exits 1 on a Conf. miss, an empty cooldown writer and, on the r3 column, route
  cells out of scope or a route presence of 0 included. Conf. cells read exactly as built; a miss is a code defect
  that stops the round. Reported cells carry no rule. Rates carry Wilson 95% intervals; no column is pooled. Every
  cell is named by its census key (a cell outside the census names its command). Values are round 1's and round
  2's at `76270d6c` (the census and honesty `--set-dir` sections and the committed route JSON), re-measured at F;
  a held-data cell built after `76270d6c` reads "measured at F", with the census card's authoring figure where it
  states one.

  | arm | cell | round 1 | round 2 | round 3 reading |
  |---|---|---|---|---|
  | physical witness | `vent_exits_seen_only_from_room_left`; `vent_band_resting_only_on_room_left` | 0/72; 0/24 | 0/72; 0/24 | Conf. 0; 0 |
  | look and wait | `surfacings_before_cap_in_view`; `trips_longer_than_cap` | 0/72; 0/63 | 0/72; 0/66 | Conf. 0; 0 |
  | look and wait | `vent_exits_seen_from_exit_room` (beside it `vent_exits_into_visibly_occupied_room`) | 8/72, effective (0/72) | 8/72, effective (0/72) | round 2's rule: effective at 0.30 or below; not effective at 0.52 or above, naming the hidden-travel escalation; partial between; n/a with no vent exit |
  | look and wait | `forced_surfacings`; table `ticks_inside_per_trip`; `in_place_surfacings_near_crew`; `kills_soon_after_surfacing` | 13/72; 1 tick 51, 2 ticks 6, 3 ticks 2, 4 ticks 13; 2/37; 0/227 | 5/72; 1 tick 49, 2 ticks 3, 3 ticks 15, 4 ticks 5; 2/44; 0/195 | reported |
  | own fresh kill | `vent_entries_not_after_own_fresh_kill` | 0/142 | 0/140 | Conf. 0 |
  | full reset | `stale_report_meetings`; `report_corpses_older_than_last_close`; `play_resumes_with_impostor_in_vent`; `play_resumes_with_corpse`; `kills_in_grace_window_after_regroup`; `prompts_missing_a_regroup_notice` | 0/118; 0/68; 0/110; 0/110; 0/139; 0/782 | 0/114; 0/64; 0/102; 0/102; 0/109; 0/722 | Conf. 0 each (grace window T+1 to T+6) |
  | full reset | false resume perceptions | not carried | not carried | carried by mechanism and golden, as the owner confirms |
  | full reset | `skipped_report_meetings`; `trips_closed_by_regroup`; `kill_witness_button_calls_soon_after_regroup`; table `trigger_tick_events_dropped_by_regroup`; `meetings_opening_with_impostor_in_vent` (beside them `post_meeting_kills_soon_after`) | 70/118; 46/142; 0/6; Moved 51, TaskProgressed 26, TaskCompleted 6; 66/124 (0/139) | 51/114; 47/140; 0/3; Moved 46, TaskProgressed 22, TaskCompleted 10; 66/117 (0/109) | reported |
  | one reply | `rebuttals_differing_from_selector`; `meetings_with_second_repeat_speaker` | 0/121; 0/124 | 0/117; 0/117 | Conf. 0; 0 |
  | one reply | `opener_rebuttals_answering_charged_tick`; `rebuttals_redirect_only` | 19/19 (82 not evaluable); 17/121; effective | 17/18 (69 not evaluable); 27/117; effective | round 2's rule, verbatim: effective if half or more answer; not effective below 0.2, or if redirect-only reaches half; partial otherwise; conflicting if both hold; n/a with none evaluable |
  | one reply | `accused_opener_answers`; `rebuttals_with_alibi`, `rebuttals_with_whereabouts`, `rebuttals_with_sighting`; `rebuttal_accusations_against_earlier_speakers`; table `rebuttal_beneficiaries` | 101/112; 104/121, 104/121, 91/121; 121/121; 71, 30, 17, 3 | 87/105; 89/117, 89/117, 79/117; 116/116; 59, 28, 28, 1, 1 | reported |
  | body handle | `report_openings_with_kill_tick_handle` | 0/118 | 0/114 | Conf. 0 |
  | kill row | `own_kill_rows_breaching`; rows served (its denominator) | 0/4; 4 | 0/23; 23 | Conf. 0; present when one or more |
  | kill row | `own_kill_rows_cited_by_holder`; honesty cell 5 (`kill_holders`, `kill_holders_citing_the_kill`) | 3/4; 4 holders, 3 of 4 | 21/23; 23 holders, 21 of 23 | reported |
  | impostor ballot | `recorded_teammate_ballot_targets`; the gate's betrayal check (`validity_gate.py`) | 0/203; 0 of 717 | 0/200; 0 of 691 | Conf. 0; 0 |
  | impostor ballot | honesty cell 3 (`ejects_citing_only_neutral`) | 0/107 | 0/111 | round 2's rule: holds at 0.10 or below; does not bind above 0.25; between otherwise; n/a with no impostor EJECT |
  | impostor ballot | `impostor_eject_ballots`; `impostor_ejects_labelled_supported`; `authored_teammate_ballot_targets` | 107/203; 107/107; 16/203 | 111/200; 111/111; 16/200 | reported |
  | self-report off | `impostor_openers` | 0/124 | 0/117 | Conf. 0 |
  | kill cooldown | `kill_cooldowns_differing_from_recorded`, table `kill_cooldown_writes_by_writer` | 0/487 against 4 | 0/447 against 6 (100, 195, 152) | Conf. 0 against 6, a count at each of the three writers |
  | route lines | `route_lines_false_to_the_map`; `route_lines_off_the_table`; presence `meetings_with_a_route_line` (beside them `ballots_carrying_route_lines` and tables `route_lines_per_meeting`, `route_steps_by_reading`) | n/a | n/a | Conf. 0; 0; present, a count above 0 (a presence of 0 is a miss) |
  | route check | the route-check replay's M and W (`rule_inputs`); the reach of (a), (b) and (c) over M (`rule_inputs.R`) and of (c) over W; beside them the route-lines instrument's served reach on r3 | 29; 0; 8, 8, 20; 0 | 40; 7; 15, 16, 29; 7 | reported as a process count, never a bar on correctness; the step reads M |
  | per seat | `reporter_seats_ejected`, `other_crewmate_seats_ejected`, `impostor_seats_ejected`; the same three `_without_vent_proof`; the same three `_with_vent_proof`; `reporters_among_ejected_crewmates`, `reporters_among_crewmate_seats` | 11/118, 2/372, 35/194; 11/98, 2/303, 15/160; 0/20, 0/69, 20/34; 11/13, 118/490 | 17/114, 5/367, 41/195; 17/93, 5/291, 20/158; 0/21, 0/76, 21/37; 17/22, 114/481 | reported; the flag below reads the reporter and other-crewmate cells without vent proof |
  | kill witness | `held_kill_witnesses_ejected`; table `held_kill_next_meeting_outcomes`; `held_kill_killers_ejected`, `held_kill_killers_ejected_at_any_later_meeting` | 0/3; killer ejected 3; 3/3, 3/3 | 5/14; witness 5, other 1, no one 2, killer 1, two or more killer 5; 6/14, 8/14 | reported |
  | counterfactual | `ejections_undone_with_impostor_ballots_as_skip`; `ejections_undone_with_impostor_ballots_removed`; `ejections_carried_only_by_impostor_ballots`; table `retally_outcome_changes` | 8/54; 2/54; 0/54 | 14/66; 5/66; 0/66 | reported |
  | held data | `holds_nothing_skips_naming_no_candidate` (table `holds_nothing_skips_by_source`); `cited_lines_true_to_the_route`, `cited_lines_false_to_the_route` (tables `cited_placements_by_kind_and_verdict`, `supported_ejects_not_checkable_by_reason`) | 0/256 at authoring; measured at F | 0/214 at authoring; measured at F | reported, each beside its definition |
  | held data | `ejections_on_a_reconcilable_pair`; `ejections_charged_on_a_reconcilable_pair`; `witness_meeting_ejections_on_a_reconcilable_pair`; `witness_meeting_ejections_charged_on_a_reconcilable_pair`; `charges_on_a_reconcilable_pair` | 31/54; 29/54; measured at F; 0/3; 265/406, at authoring | 41/66; 40/66; measured at F; 7/12; 276/402, at authoring | reported; the charged count is the route-check replay's M and its witness form W |
  | held data | `skips_holding_nothing`; `ballots_citing_a_rebuttal` with `ballots_countering_with_a_rebuttal` beside | 256/330; 70/707, 150/707 | 214/281; 57/691, 175/691 | reported; for ballots citing a rebuttal the turn citation is the cell and the counter slot sits beside it, as the owner confirms |
  | envelope | impostor win share (`impostor_wins`) | 34/50 = 0.68 | 24/50 = 0.48 | non-gating; flagged outside 0.20-0.60 (route lines that save witnesses help the crew, so the floor is watched); read by the step rule |
  | envelope | the re-keyed reporter flag (below), `reporter_seats_ejected_without_vent_proof` against `other_crewmate_seats_ejected_without_vent_proof` | relative rate 17.0 | relative rate 10.6 | non-gating; flagged above the confirmed bar; never read by the step rule |
  | reported | `role_correct_ejections`; innocent ejections (its denominator less its numerator); `meetings_with_vent_proof`; kills (`kills_seen_by_crew`'s denominator); `impostor_cooldown_zero_at_open`; the win split (`impostor_wins`); scorecard rows 1-9 (`publish_process_scorecard.py --set-dir`) | 39/54; 15; 26/124; 227; 84/203; 16-34 | 44/66; 22; 24/117; 195; 54/200; 26-24 | reported, gating nothing |

  Round 2's reading under the old line (17/114, flagged above 0.104) stands as recorded; the readings command does
  not compute that line and nothing re-scores round 2. Round 2's 40 is a constant at P (`ROUND_2_M`), and the
  command exits 1 unless the route JSON's r2 column reads it. Proof, at F on scratch copies of round 2's census
  section with the route cells put in scope at 0 and presence 12, and of the committed route JSON with its r2 column
  copied as r3: `--column r3 --after --step` exits 0 and names the promotion of round 3 (M 40, win share 24/50); with
  presence 0 it exits 1 naming the route field; with one Conf. numerator raised (a route cell, then
  `stale_report_meetings`) it exits 1 naming that key; with M 41 or the win share 31/50 the step line names round 2
  staying shown; with the flag forced on (reporter numerator 60) or `role_correct_ejections` edited, the line
  beginning `step rule:` is byte-identical to the unedited run's. At authoring, the scratch command on hand-built
  copies at `76270d6c` (the not-yet-built cells added by hand) gave exactly these exits and lines.
- [x] **Amendment of 2026-10-09 (the orchestrator, before P): the merged census table is named.** The held-data row
  above and `readings.py` below named the table `holds_nothing_skips_naming_a_candidate_by_source`;
  `census-held-data-cells` merged it as `holds_nothing_skips_by_source` (`eval/gameplay_census.py`,
  `docs/gameplay-census.json`). The operator stopped before P on this card's rule that a key merged under another
  name is a stop, never a silent edit. The name is corrected in both places, which changes `readings.py`'s sha256;
  the cell read is the same, so the owner's confirmation of 2026-10-09 (decision memo 8.7) covers it. Every other
  count the table states reproduced at F `7dfaa7f3` through the production path (the stopped operator's evidence).
- [x] **The reporter flag is re-keyed, with a proposed bar and its alternatives.** Mechanism: `readings.py` reads
  `reporter_seats_ejected_without_vent_proof` (k1/n1) against `other_crewmate_seats_ejected_without_vent_proof`
  (k2/n2); the relative rate is (k1/n1)/(k2/n2), compared by cross-multiplication in exact fractions, so no zero is
  divided by. Proposed bar **A**: flagged above twice round 2's relative rate, 2 x 10.64 = 21.28. Its zero case:
  with k2 = 0, any reporter seat ejected flags as "reporters alone". Alternatives for the owner, read on the same
  cells (rates without vent proof; the baseline-9 column is readable only at `d41c9006`, context only):

  | bar | line | baseline-9 9p2i: 7/75 vs 2/243 | round 1: 11/98 vs 2/303 | round 2: 17/93 vs 5/291 |
  |---|---|---|---|---|
  | **A** (proposed) twice round 2's relative rate | above 21.28 | 11.3, not flagged | 17.0, not flagged | 10.6, not flagged |
  | **B** round 2's relative rate itself | above 10.64 | flagged | flagged | at the line, not flagged |
  | **C** the reporter rate alone (amends the form) | above 17/93 = 0.183 | 0.093, not flagged | 0.112, not flagged | at the line, not flagged |

  Why A: the other-crewmate numerators are 2, 2 and 5, so one ejection more or less moves the relative rate by a
  factor of 1.25 to 2 (round 2 reads 8.9 with 6, 13.3 with 4); B flags both earlier 9-player columns and would flag
  noise in a round that changed nothing; C reads the reporter seat alone, which the re-keying set aside. The flag
  gates nothing and the step rule never reads it. Proof: the command prints 17.0 and 10.6 on R1 and R2, not flagged
  under A; under B it flags R1; a scratch copy with k2 = 0 and k1 = 1 prints "flagged, reporters alone".
- [x] **The step rule after round 3 is pre-registered, reads no reporter line and no role-correct figure, and is the
  owner's to take or override.** Mechanism: `readings.py --step` prints one line by this sentence, carried whole:

  > **The step rule after round 3.** With every Conf. cell at 0, round 3's point share of impostor wins neither above
  > 0.60 nor below 0.20, and round 3's misjudged route cases (the route-check replay's M) at or below round 2's 40,
  > it names the era-keyed promotion of round 3 as the shown set; otherwise it names round 2 staying shown, with
  > round 3 kept as a comparison record. Either step is the owner's to take or override.

  The rule gates no acceptance item. The witness subset, the reach of each check and M per ejection are printed
  beside M and not read. Proof: the planted copies of the readings item.
- [x] **The preflight holds at F.** Mechanism: `CFG`, read by `scripts/_declared_experiment.py`'s loader, validates
  as a `RecordedExperimentConfig` whose non-default fields are round 2's nine and the route field;
  `OMITTED_AT_DEFAULT` holds it; `engine_arguments` returns round 2's keywords unchanged; `prompt_versions_for_set`
  serves the four stamps; `self_report` is False, `evidence_reasoning_version` and `contextual_self_report_version`
  None, the slate bare. The instrument takes `r3`; the held-data and route cells exist under their cards' keys.
  Proof: an unknown key is refused (`extra_forbidden`); without the route key the bytes equal R2's declared file;
  the field card's refusals (an env switch, an unthreaded reader) pass at F, named by test id.
- [x] **The fake dress rehearsal passes every instrument at F, at $0, and shows the field inert.** Mechanism: seeds
  0-49 record with `AILIBI_LLM_PROVIDER=fake` on `CFG` into scratch outside `replays/`; each exits 0 on it: the census
  `--set-dir` (every Conf. cell 0, and route presence exactly 0: `meetings_with_a_route_line` and
  `ballots_carrying_route_lines` read 0, since a fake turn states no place and so no block is served), the scorecard
  `--set-dir`, the validity gate with `--expected-experiment-config`, `--expected-seeds 0-49` and
  `--require-one-recording-sha`, `verify_samples.sh`, the golden's walk, `measure_baseline.py --honesty`,
  `scan_recording_packets.py`, and both route instruments' r3 columns on a throwaway commit of a scratch clone
  holding the fake set and `CFG` at the round's paths, never pushed. `readings.py --after` is not run on the fake
  set (its presence check is for the hosted round). The fake tally beside the same rehearsal on R2's declared file
  reads equal, the inertness the field card proved; the route lines' added input for planning is the field card's
  projection on round-2 bytes (`experiments/lab/results-route-lines-replay.json`, the r2 column's projected added
  input tokens beside round 2's 9,187,880), stated at P, gating nothing. Proof: gated against R2's declared file,
  the gate fails `cost_and_provenance_exact`.
- [x] **The scripted rehearsal and the lab still hold at F, and the field is served.** Mechanism: the field card's
  planted cases (West Hall to Admin, 1 hop in 1 tick; Admin to Cafeteria, 2 hops in 2 ticks; across a regroup) and
  round 2's scripted and ballot-arm cases pass; a scratch scripted game from `CFG` (the field card's
  `tests/_helpers/scripted_routes.py`, whose turns state places) passes the loader, census, scorecard, gate and
  golden, with route presence above 0 (`meetings_with_a_route_line`) and every route Conf. cell 0, which is where
  served-line presence is proved before the probe; the tactical lab's ten round-1 arm rows equal
  `audits/tactical-gameplay/stage-b-r1-frozen-head.json` on the frozen file's own keys (every top-level row field,
  and `counts` on the frozen file's keys, since `crew-idle-policy-lab` adds seven count keys to every lab row), as
  that card compares them (the field touches no tactical code); the field card's lab rows reproduce by its own
  command. Proof: dropping the recorded evidence profile leaves a scripted call unconsumed; one edited lab counter
  prints that field.
- [x] **The dry run and the probe pass before any batch.** Mechanism: the dry run echoes P's sha256, the ten fields
  and the bare slate, with `git status --porcelain --untracked-files=no` at 0 lines. The probe records seeds 0-1 as
  one leg on two workers; the probe's gates (Constraints) run before any batch. Seeds 0-1 with no meeting or no
  served route line extend by seeds 2-3 only; seeds 0-3 with a ballot and no served route line stop the card.
  Proof: the dry run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exits 1.
- [x] **The round is exactly the declaration, and every Conf. cell reads 0.** Mechanism: the validity gate on C
  passes its ten checks, named, with `--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, the four
  `--expected-prompt-versions` pairs, `--expected-experiment-config CFG`, `--expected-seeds 0-49` and
  `--require-one-recording-sha`; the MANIFEST's flags column equals R2's and its policy column reads
  `fsm-default`; `grep -l deadline_default` counts 0; the census `--set-dir C` exits 0 (non-zero names set, seed,
  meeting on a breach), the route cells included; the golden reproduces every call. Proof: the gate with
  `--expected-seeds 0-50` fails; R2 against `CFG` fails `cost_and_provenance_exact`; the census card's planted
  breaches (its route conformance cases among them) and the field card's pass at F, named by test id.
- [x] **The spend stays inside the ceilings.** Mechanism: the tally counts C's `llm_calls`; `reproject.py` applies
  Constraints' re-projection, exiting 1 with a STOP line past a 90% stop. Proof (at `76270d6c`): the tally prints
  `1502 9187880 418270 0.0` on R2 and `1556 9344346 433660 0.0` on R1; on a scratch copy of R1's seeds 0-11 with
  4,000 s of wall it projects 1,619 calls, 9,978,176 input, 470,463 output and 4.63 h and exits 0; with 50,000 output
  tokens added to one call it projects 677,314 output and exits 1 on output; with 9,400 s of wall it projects
  10.88 h and exits 1 on wall (all three re-run at authoring with the `reproject.py` Validation quotes).
- [x] **The checkout never moves, a pause strands nothing, no key leaves, and the freeze held.** Mechanism: seeds
  record in a checkout detached at P, in batches, each ending in a count-only key scan (gzip decompressed) and a
  pushed `record:` checkpoint, the gates running after the probe and after every second batch (the owner's process
  amendment of 2026-10-09, decision memo 8.7); `git log --oneline F..HEAD` and `F..origin/main` print nothing over the frozen
  pathspec. Proof: the MANIFEST names one `git_sha`; each scan pattern fires on its planted key; with a planted pause
  file and the recorder replaced by `true` no batch starts; the pathspec over `76270d6c..F` is non-empty.
- [x] **The derived views and the registration are rebuilt, never hand-edited.** Mechanism: the recorder's
  post-step writes the report through `eval/report_io.py` and `build_sample_report.py --sample-dir C --check`
  passes; the round README's `candidate-declaration` block holds the sha256 line and `9p2i seeds 0-49`; the two
  `docs/artifacts.md` rows are re-derived with `git ls-files` (111 files under `replays/candidates/`) and offline
  `verify_ml_evidence.py` reads OK; the golden's `candidates/stage-b-r3/9p2i` row is what its production walk
  measures on C. Proof: the candidate test's planted perturbations pass; without the row the golden raises `KeyError`.
- [x] **The assessment is written as pre-registered.** Mechanism: round 3's column comes only from the census and
  scorecard `--set-dir C --json-stdout`, `measure_baseline.py C --honesty --json`, the gate's betrayal check and the
  instrument run at the delivery head with r1, r2 and r3 columns into scratch, through `readings.py`. Order: the
  process cells; each Conf. cell and carried reading; the route cells; the cooldown cell; the envelope and the flag;
  the route-check count; the step the rule names; the reported rows; role-correct ejection, the balance and the win
  split, gating nothing. The menu: the step; for the route field, adopt by the era-keyed promotion, iterate under a
  new value, or keep round 2 shown; Conf. cells only for the other nine fields; with the promotion, its card's
  follow-ups (a public-results label for the route field, which `frontend/src/components/PublicResults.tsx` cannot
  name today; the era registry entry; the pin sweep). Proof: pooling C with R2 or R1 raises the census era refusal.
- [x] **Nothing publishes, nothing committed moves, and the copy is plain.** Mechanism: `git diff --stat F..HEAD`
  is empty over `replays/samples`, `replays/ml_corpus`, R1's round directory, `tests/fixtures`, `training`, `api`,
  `frontend`, `experiments` and the census and scorecard docs; `verify_samples.sh` and `build_sample_report.py
  --check` pass on every set and round; the scorecard and census `--check`, `check_doc_facts.py` and the instrument's
  `--check` exit 0; the demo bundle built at F and at the head is identical (`diff -r`, mtimes pinned). The round
  README, the candidate sentence and the index row pass `copy_problems` with 0 problems and a count-only scan for
  `\b[AB][0-9]\b|\bR[0-9]+\b` prints 0. Proof: `test_audits_index_ladder_tip_drift_detected` and
  `test_unindexed_audit_detected` pass; a scratch copy with "6/7" inserted gives one problem, with "R7" one hit.

## Constraints

**House rules.** The engine stays a pure deterministic tick function and replays stay byte-identical within their
recorded scope; LLMs run only at meetings; tactical decisions stay rule-based; agents reason from typed event memory
and rendered memory; `agents/` never imports `engine/` (import-linter, the observation firewall); no module-level
mutable state; invalid input raises. No `AILIBI_*` lever, environment switch, prompt registry bump or field is added
here; the route field is the field card's, default OFF and omitted at its default (the committed-payload byte test,
`tests/orchestrator/test_experiment_arms.py`). No recorded byte is edited and no history re-scored; the corpus FROZEN
line and the ML artifacts never move (offline `verify_ml_evidence.py`, never `--complete`). Role-correctness is
reported, never a gate; nothing pushes an agent toward the correct answer; the meeting layer labels, never rewrites.
Numbers are measured at the head that states them, with the command in Results; no test is weakened.

**The partial-record principle.** Only C is recorded; the recorder refuses `CFG` aimed at `replays/ml_corpus/` or a
committed sample set (whose era declares another file or none). `CFG` differs from R2's file in exactly the route key.
`evidence_reasoning_version` stays unset. Round 1 stays as a comparison column; retiring it is a later card's.

**Ceilings, unchanged from rounds 1 and 2** (round 2's audit 1.6), each confirmed again by the owner at Q:

| limit | ceiling | hard stop at 90% |
|---|---|---|
| model calls | **2,800** | 2,520 |
| input tokens | **17,500,000** | 15,750,000 |
| output tokens | **750,000** | 675,000 |
| recording wall | **12 h** summed over sittings, each inside an **18 h** elapsed window | **10.8 h** (38,880 s) |
| marginal cost | **$0.00** (flat-rate Featherless, already paid) | any `cost_usd` other than 0.0000 |

Recording wall is each leg's "Refresh complete in" figure summed over sittings. Round 2 spent 56.7%, 55.6%, 58.8% and
29.9% of the four ceilings; the stops leave 1.59x its calls, 1.62x its input, 1.53x its output and 3.0x its wall.

**Re-projection**, round 2's rule with the anchor moved to R2, since the baseline-9 9p2i bytes left the tree: after
the probe, after the first checkpoint holding 10 seeds and at every batch checkpoint, each count is (C's total over
its completed seeds / R2's total over the same seeds) x R2's leg total, and the wall is the summed recording wall /
the completed seeds x 50, each against its 90% stop; past a stop, the round stops. The R1 ratio is context only.

**Stop and report to the owner**, with the partial output and the last checkpoint pushed, on: any `cost_usd` other
than 0.0000; a re-projection past a 90% stop; a leg past 1.5x the probe's projected wall, summed wall past 10.8 h,
or a sitting past its 18 h window; a provider refusal surviving the 8-attempt budget; a raise from
`measure_baseline.py --honesty`; any Conf. miss, the route cells included. A Conf. miss is a code defect, not a
result: the fix lands under a new field value (a recorded value's meaning is frozen) and the round re-records from
seed 0 under a new declared config, with a dated addendum and the owner's clearance.

**Stalls and failed seeds.** A stall is 45 minutes with no completed seed: kill the batch and re-run it for the seeds
not on disk, or relaunch a fresh operator from the last pushed checkpoint; a seed on disk is never re-recorded to
recover a stall. A `(deadline_default)` row marks a failed recording: move its husk outside the repository (its
spend counts) and re-record that seed alone at P, logging the cause as it happens. No other re-record.

**Operating discipline.** After the probe, batches of 5 naming only seeds not on disk, never `--full`: 2-6, 7-11, ...,
42-46, 47-49; after an extension, 4-8, 9-13, ..., 44-48, 49. A batch in flight when a pause is called finishes,
runs its gates and pushes its checkpoint before the pause takes effect; no batch is killed to pause (a stall is
the only kill). Before each batch the operator checks a pause file outside the repository; if it exists no batch
starts, the key file is deleted, the last checkpoint is pushed and the operator log (outside the repository) names
the seed reached and the next batch; the next sitting opens a new 18 h window, copies the key again and resumes
there. After every batch, in the delivery checkout and a bare shell: the tally, the re-projection, the key scan, then
a pushed `record:` checkpoint. After the probe and after every second batch (10 seeds), before that checkpoint:
the gate with `--expected-seeds 0-N`, `verify_samples.sh`, the golden's walk, the census Conf. cells, the scorecard
fold, `measure_baseline.py --honesty` and `scan_recording_packets.py`; a gate failure stops the sitting and names the
batches it covers (a checkpointed seed is never re-recorded). The gates every second batch and the checkpoint every
batch are the owner's process amendment of 2026-10-09 (decision memo 8.7).

**Checkouts, shells and the key.** Recording: a fresh worktree detached at P (`uv sync --frozen`, no `.env`) running
only the recorder, never pytest, `check.sh` or a commit; no pytest or `check.sh` runs in any checkout beside its
untracked `CFG` copy (a round directory without its set directory fails the candidate test). Verification: a
worktree at F. Delivery: the branch's worktree. Each gate runs in a bare shell and first prints its `AILIBI_*`
count (0). The recording shell sets only round 2's slate with `AILIBI_SAMPLE_DIR` and `AILIBI_MANIFEST` on C
(featherless, `qwen3_6_27b`, `Qwen/Qwen3.6-27B`, 9/2/2, 2 workers, 8 attempts). `FEATHERLESS_API_KEY` is copied programmatically from the main checkout's untracked
`.env` to a mode-0600 file in a mode-0700 directory outside every checkout, passed only by `uv run --env-file`,
deleted at a pause and when the sitting ends, never printed or logged; the recorder's run log, which carries the key's
first eight characters, stays outside the repository. No rendered prompt, transcript text or seed-band prefix is
printed; scans and censuses are count-only, keyed by (set, meeting). `CFG` stays untracked until the delivery commit
adds it with P's sha256; each checkout checks its copy before the dry run and every gate (a mismatch stops the card).

**The freeze.** From the first seed to the merge nothing merges into `engine agents meetings observation orchestrator
eval api scripts llm` or `experiments/lab/route_check_replay.py`, and nothing merges into `training`, `experiments`,
`audits/tactical-gameplay` or the other paths this card's nothing-moves diff covers. A card that writes there merges
before F or after this card: `crew-idle-policy-lab`, which writes `experiments/tactical_gameplay.py`,
`training/README.md`, `training/rewards.py`, `audits/tactical-gameplay/` and the `audits/` row of
`docs/artifacts.md`, merges before F, so F holds it. If `main` moves there, stop and ask; otherwise merge `main` in
and re-run every gate.

**Wave, order and ownership.** Dispatches only at F: after `route-lines-field`, `census-held-data-cells`,
`crew-idle-policy-lab` and `rubric-v2-profile` merge and the field's rehearsals pass; the held `rubric-extractor-era`
and `retire-temporal-evidence-v1` stay undispatched until this card merges. One writer per file, as the
orchestrator's one-writer map assigns: the field
card owns the field, its readers, templates, the route-lines instrument, both instruments' `r3` column, the field's
tests and the field's row on `docs/experiment-arms.md`; `census-held-data-cells` owns the census cells, the route
field's conformance cell among them (`route_lines_false_to_the_map` and `route_lines_off_the_table` as Conf.,
`meetings_with_a_route_line` as presence), and its page; `crew-idle-policy-lab` owns the tactical lab, its capture
under `audits/tactical-gameplay/` and its `training/` text. This card owns `replays/candidates/stage-b-r3/**`, its
audit, `audits/README.md` (its index row), the two `docs/artifacts.md` rows it re-derives after merging `main` (the
last writer of that file in the round), its sentence on `docs/experiment-arms.md` (after the field card's edit,
never the Adopted arms paragraph), the one `_RETIRED_GUARD_PINS` row in `tests/meetings/test_prompt_byte_golden.py`
(after F) and this card's Results. Never edited here: R1's and R2's bytes and audits, `experiments/`,
`audits/tactical-gameplay/`, `scripts/verify_ml_evidence.py`, `training/`, the doctrine documents, and
`tasks/README.md` and this card's Status line (the orchestrator's, on `main`).

**Delivery and publication.** Branch `work/stage-b-record-r3`, one PR into `main`, merged or fast-forwarded, never
squashed, never amended after push; merge `main` in, never rebase. Each commit body, P and Q included, carries
`Card: tasks/work/stage-b-record-r3.md` immediately followed by the exact line
`Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`. The PR fills every template section and ends with the
Claude Code attribution line; agents post no PR comments. Nothing ships (`pages.yml` builds from `replays/samples`
and the featured list; candidate bytes ship only by a promotion), so the orchestrator merges; the step and any
promotion are the owner's.

**What stays out:** other sets, the held-out band, ML (the hold stands), the rubric, the README and front door, the
tour, featured list and public results, census or scorecard cells, floors, adoption, promotion, graduation, retiring
round 1 and impostor self-report.

**Stop and ask** if the owner amends the ceilings, the table, the bar, the step rule or the config before the first
seed (P changes with them); if at F the route field, its cells, stamp or readers, the held-data cells or the `r3`
column are missing or named otherwise than their cards' Results; if a round-1 or round-2 count moves at F; if a gate
needs a code change; if the scripted helper cannot take `CFG`; or if a test besides the golden pin turns red only
because another round exists.

## Expected scope

- `replays/candidates/stage-b-r3/README.md` (plain copy: the shown set's rules, the one added switch in plain words,
  the `candidate-declaration` block) and `replays/candidates/stage-b-r3/experiment-config.json`.
- `replays/candidates/stage-b-r3/9p2i/`, written by the recorder: `replay-seed-0.jsonl` to `replay-seed-49.jsonl`,
  `MANIFEST.md`, `roster.json` and `tournament-eval-report.json.gz`.
- `audits/audit-<YYYY-MM-DD>-stage-b-r3.md`, dated the day P lands, and its row in `audits/README.md` under the
  Stage-B gameplay wave.
- `docs/artifacts.md`: the `replays/candidates/` and `audits/` rows, re-derived.
- `docs/experiment-arms.md`: a "Candidate round 3" heading and one sentence: "`replays/candidates/stage-b-r3/9p2i`
  is candidate round 3, recorded with the shown set's rules and one more switch that gives each voter a plain line
  about the places stated at the table, as its README names; it adopts nothing and is not a canonical sample set."
- `tests/meetings/test_prompt_byte_golden.py`: one `_RETIRED_GUARD_PINS` row for `candidates/stage-b-r3/9p2i`,
  measured through the production walk; directly necessary, since the golden raises on an unpinned set.
- `tasks/work/stage-b-record-r3.md`: Results.

Not in scope: every other code, template, instrument and test file; `replays/samples/`, `replays/ml_corpus/`,
`replays/candidates/stage-b-r1/`, `tests/fixtures/`, `training/`, `experiments/`; the census and scorecard docs,
`docs/architecture.md`, `docs/glossary.md`, `README.md`, the featured list, public results and floors.

## Record impact

**What moves:** a new candidate directory (55 new tracked files, about 35 MB if it matches round 2), the audit and its
index row, two `docs/artifacts.md` rows, one candidate sentence, one golden pin row and this card.

**What stays unchanged:** every byte, MANIFEST and report under `replays/samples/*`, `replays/ml_corpus/*` and R1; the
census and scorecard docs; the route-check replay's committed outputs; the tour, public results, floors and ladder
tip; the corpus freeze and ML fits; the levers, the prompt registry and every default. CI reads round 3 as it reads
round 1. **Publication:** none. **Evaluation:** the audit reports cells, readings, the flag and the step the rule
names, with no verdict; the owner decides, and a promotion is a later card and the owner's merge.

## Validation

Every command runs in a bare shell unless it is the recording shell; quote each exit code as it came back. The
tally is round 2's command, carried whole and unchanged; at `76270d6c` it prints `1502 9187880 418270 0.0` on R2
and `1556 9344346 433660 0.0` on R1.

```
env | grep -c '^AILIBI_'                                        # 0
CFG=replays/candidates/stage-b-r3/experiment-config.json; C=replays/candidates/stage-b-r3/9p2i
R2=replays/samples/9p2i; R1=replays/candidates/stage-b-r1/9p2i
shasum -a 256 "$CFG"; git merge-base --is-ancestor F P && git merge-base --is-ancestor P Q   # P's line; exit 0
# P against the MANIFEST's one git_sha (round 2's command), after the leg; exit 0
git merge-base --is-ancestor P "$(awk -F'|' '$2 ~ /^ *[0-9]+ *$/ {gsub(/ /,"",$8); print $8}' "$C/MANIFEST.md" | sort -u)"
# the tally, round 2's command unchanged (count-only)
uv run python -c 'import glob,json,sys
c=i=o=0; u=0.0
for p in glob.glob(sys.argv[1]+"/replay-seed-*.jsonl"):
  for r in map(json.loads,open(p)):
    for k in r.get("llm_calls") or []:
      c+=1; i+=k["input_tokens"]; o+=k["output_tokens"]; u+=k["cost_usd"]
print(c,i,o,u)' <set dir>
# the recording checkout, detached at P, with Constraints' slate set inline (no pytest or check.sh here)
bash scripts/refresh_samples.sh --full --expect-levers "" --experiment-config "$CFG" --dry-run
uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh --seeds 0,1 --expect-levers "" --experiment-config "$CFG"
# only if seeds 0-1 hold no meeting or no served route line: the extension, seeds 2-3
uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh --seeds 2,3 --expect-levers "" --experiment-config "$CFG"
test -e "$PAUSEFILE" || uv run --env-file "$KEYFILE" bash scripts/refresh_samples.sh \
  --seeds 2,3,4,5,6 --expect-levers "" --experiment-config "$CFG"      # then 7-11 ... 42-46, 47-49
# (after an extension: --seeds 4,5,6,7,8, then 9-13 ... 44-48, 49)
# gates, in the verification or delivery worktree
uv run python scripts/validity_gate.py "$C" --expected-model Qwen/Qwen3.6-27B --require-zero-cost \
  --expected-prompt-versions <the four KEY=VER pairs> --expected-experiment-config "$CFG" \
  --expected-seeds 0-49 --require-one-recording-sha
python3 "$SCRATCH/reproject.py" "$C" "$R2" <summed recording wall, s>   # at each checkpoint
for d in "$R1" "$R2" "$C"; do n=$(echo "$d" | tr / _)
  uv run python scripts/publish_gameplay_census.py --set-dir "$d" --json-stdout > "$SCRATCH/census-$n.json"
  uv run python scripts/publish_process_scorecard.py --set-dir "$d" --json-stdout > "$SCRATCH/scorecard-$n.json"
  uv run python scripts/measure_baseline.py "$d" --honesty --json > "$SCRATCH/honesty-$n.json"; done
uv run python -m experiments.lab.route_check_replay --set r1=<F sha>:"$R1" --set r2=<F sha>:"$R2" \
  --set r3=<head sha>:"$C" --out-json "$SCRATCH/route.json" --out-report "$SCRATCH/route.md"
uv run python -m experiments.lab.route_check_replay --check     # the committed outputs, unchanged
# the field's served reach on r3, by the route-lines instrument's own columns (its CLI as the field card delivers it)
uv run python -m experiments.lab.route_lines_replay --set r1=<F sha>:"$R1" --set r2=<F sha>:"$R2" \
  --set r3=<head sha>:"$C" --out-json "$SCRATCH/route-lines.json" --out-report "$SCRATCH/route-lines.md"
uv run python -m experiments.lab.route_lines_replay --check     # the committed outputs, unchanged
python3 "$SCRATCH/readings.py" "$SCRATCH/census-replays_candidates_stage-b-r1_9p2i.json" \
  "$SCRATCH/honesty-replays_candidates_stage-b-r1_9p2i.json" "$SCRATCH/route.json" --column r1 --after
python3 "$SCRATCH/readings.py" "$SCRATCH/census-replays_samples_9p2i.json" \
  "$SCRATCH/honesty-replays_samples_9p2i.json" "$SCRATCH/route.json" --column r2 --after
python3 "$SCRATCH/readings.py" "$SCRATCH/census-replays_candidates_stage-b-r3_9p2i.json" \
  "$SCRATCH/honesty-replays_candidates_stage-b-r3_9p2i.json" "$SCRATCH/route.json" --column r3 \
  --bar <the confirmed bar> --after --step
uv run python scripts/scan_recording_packets.py "$C"
bash scripts/verify_samples.sh                                  # every sample set and round
for d in replays/samples/9p2i replays/samples/4p1i replays/ml_corpus/9p2i replays/ml_corpus/4p1i "$R1" "$C"; do
  bash scripts/verify_samples.sh "$d"; uv run python scripts/build_sample_report.py --sample-dir "$d" --check; done
grep -l deadline_default "$C"/replay-seed-*.jsonl | wc -l       # 0
git log --oneline F..HEAD -- engine agents meetings observation orchestrator eval api scripts llm \
  experiments/lab/route_check_replay.py                         # empty; also F..origin/main
git log --oneline F..origin/main -- engine agents meetings observation orchestrator eval api scripts llm \
  experiments/lab/route_check_replay.py                         # empty
git diff --stat F..HEAD -- replays/samples replays/ml_corpus replays/candidates/stage-b-r1 tests/fixtures training \
  api frontend experiments audits/tactical-gameplay docs/process-scorecard.md docs/process-scorecard.json \
  docs/gameplay-census.md docs/gameplay-census.json             # empty
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-head"   # and bundle-F at F; diff -r is empty
# the copy scan, over the round README, the candidate sentence and the index row, each saved to scratch
uv run python -c 'import sys; sys.path[:0]=["scripts"]
from tests.scripts.test_candidate_sets import copy_problems
for p in sys.argv[1:]: print(p, len(copy_problems(open(p).read())))' <the three scratch files>   # 0 each
grep -cE '\b[AB][0-9]\b|\bR[0-9]+\b' <the three scratch files>  # 0 each
# the whole gate, in the delivery worktree, after the leg
uv run python scripts/publish_process_scorecard.py --check; uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/check_doc_facts.py; uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py                     # offline; never --complete
uv run pytest tests/meetings/test_prompt_byte_golden.py -k "retired_guard or stage-b-r3" -q
uv run pytest -m campaign -q                                    # check.sh's default tier excludes it
# the house gate: CI's green run at the exact head stands as the gate record, cited by run id (memo 8.7);
# no local check.sh at the final head and no card-only commit recording it
```

`readings.py` is the round-3 readings command, quoted whole here and again at P, so it is reviewed before P
(standard library only; it prints counts and rates, never a prompt). It is round 2's (its audit 1.12) with these
changes: a third input, the route-check replay's scratch JSON, read for the named column's `rule_inputs`, with
round 2's M held as a constant the r2 column must read; the column is named (`--column r1|r2|r3`); the route cells
and `prompts_missing_a_regroup_notice` join the Conf. set, and on r3 a route field out of scope or a presence of 0
is a miss; the per-seat, kill-witness, counterfactual and held-data rows print; the envelope prints the re-keyed
flag at the bar `--bar` names, by exact cross-multiplication, and no 0.104 line; and `--step` computes the step from
the Conf. misses, `impostor_wins` and M alone. At authoring it ran on scratch copies of the round-1 and round-2
sections at `76270d6c` with the not-yet-built cells added by hand, giving the exits and lines the readings item's
proof states. Before P the implementer re-runs those proofs at F on the real cells; a key that merged under another
name is a stop (Stop and ask), never a silent edit.

```python
"""Print round 3's pre-registered table from its named sources (count-only).

Usage: readings.py CENSUS.json HONESTY.json ROUTE.json --column {r1,r2,r3}
                   [--bar {A,B,C}] [--after] [--step]

CENSUS.json is one census section, `publish_gameplay_census.py --set-dir DIR
--json-stdout`. HONESTY.json is `measure_baseline.py DIR --honesty --json`.
ROUTE.json is the route-check replay's scratch JSON; --column names the column
whose `rule_inputs` are read, and its r2 column must read round 2's M. --bar
names the reporter flag's bar (default A, the proposed one; the assessment
passes the bar the owner confirmed). With --after, each reading is computed by
its pre-registered rule and the command exits 1 on a Conf. miss (an empty
cooldown writer and, on r3, route cells out of scope or a route presence of 0
included); without it, values only. With --step (r3, after --after), the last
line names the step the step rule names, computed from the Conf. misses,
`impostor_wins` and M alone: never from the reporter flag or a role-correct
figure.
"""

import argparse
import json
import math
import sys
from fractions import Fraction

ROUND_2_M = 40  # the route-check replay's misjudged cases on round 2 (committed r2 column)
ROUND_2_RELATIVE = Fraction(17 * 291, 93 * 5)  # 17/93 against 5/291, without vent proof: 10.64
BARS = {
    "A": ("relative", 2 * ROUND_2_RELATIVE, "above twice round 2's relative rate, 21.28"),
    "B": ("relative", ROUND_2_RELATIVE, "above round 2's relative rate, 10.64"),
    "C": ("reporter", Fraction(17, 93), "the reporter rate alone above 17/93 = 0.183"),
}

parser = argparse.ArgumentParser()
parser.add_argument("census")
parser.add_argument("honesty")
parser.add_argument("route")
parser.add_argument("--column", required=True, choices=("r1", "r2", "r3"))
parser.add_argument("--bar", default="A", choices=tuple(BARS))
parser.add_argument("--after", action="store_true")
parser.add_argument("--step", action="store_true")
args = parser.parse_args()
if args.step and not (args.after and args.column == "r3"):
    sys.exit("--step reads round 3: pass --column r3 --after --step")


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def rate(k, n):
    if n == 0:
        return f"{k}/{n} (n/a)"
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.3f} (Wilson {lo:.2f}-{hi:.2f})"


census = json.load(open(args.census))
if "sets" in census:
    sys.exit("CENSUS.json must be one --set-dir section, never the published page")
honesty = json.load(open(args.honesty))[0]["ballot_conduct"]
columns = {column["label"]: column for column in json.load(open(args.route))["columns"]}
if columns["r2"]["rule_inputs"]["M"] != ROUND_2_M:
    sys.exit(f"the route JSON's r2 column reads M {columns['r2']['rule_inputs']['M']}, not {ROUND_2_M}")
route = columns[args.column]["rule_inputs"]
after = args.after
cells = census["cells"]
tables = census["tables"]
misses = []


def cell(key):
    c = cells[key]
    return c["numerator"], c["denominator"]


def show(label, key):
    k, n = cell(key)
    if not cells[key]["in_scope"]:
        print(f"  {label} [{key}]: n/a (out of scope: {cells[key]['scope']})")
        return k, n
    ne = cells[key]["not_evaluable"]
    extra = f"; {ne} not evaluable" if ne else ""
    print(f"  {label} [{key}]: {rate(k, n)}{extra}")
    return k, n


def conf(label, key):
    k, n = show(label, key)
    if after:
        print(f"    Conf.: {'reads 0 as built' if k == 0 else 'BREACH'}")
        if k != 0:
            misses.append(key)
    return k, n


def table(label, key):
    print(f"  {label} [{key}]: {json.dumps(tables[key]['counts'], sort_keys=True)}")


print(f"column {args.column}; games {census['games']}; meetings {census['meetings']}; "
      f"meetings per game {census['meetings'] / census['games']:.2f}")
print("physical witness")
conf("exits seen only from the room left", "vent_exits_seen_only_from_room_left")
conf("vent-band ejections resting only on them", "vent_band_resting_only_on_room_left")
print("look and wait")
conf("surfacings before the cap with someone in view", "surfacings_before_cap_in_view")
conf("trips over the cap", "trips_longer_than_cap")
show("  beside: exits into a room the impostor could see a crewmate in",
     "vent_exits_into_visibly_occupied_room")
k, n = show("exits seen from the exit room", "vent_exits_seen_from_exit_room")
if after:
    if n == 0:
        print("    reading: n/a (no vent exit)")
    else:
        share = k / n
        verdict = ("effective" if share <= 0.30 else
                   "not effective (names the hidden-travel escalation)" if share >= 0.52
                   else "partial")
        print(f"    reading: {verdict}")
show("forced exits", "forced_surfacings")
table("ticks inside per surfaced trip", "ticks_inside_per_trip")
show("near-body cost: in-place surfacings a crewmate reaches", "in_place_surfacings_near_crew")
show("kills within 2 ticks of the killer's surfacing", "kills_soon_after_surfacing")
print("own fresh kill")
conf("entries not after the impostor's own fresh kill", "vent_entries_not_after_own_fresh_kill")
print("full reset")
conf("stale report meetings", "stale_report_meetings")
conf("reported corpses older than the last regroup", "report_corpses_older_than_last_close")
conf("play resumes with an impostor in a vent", "play_resumes_with_impostor_in_vent")
conf("play resumes with a corpse", "play_resumes_with_corpse")
conf("kills in the grace window after a regroup", "kills_in_grace_window_after_regroup")
conf("prompts after a regroup missing an earlier regroup's notice", "prompts_missing_a_regroup_notice")
show("  beside: kills within 2 ticks of any meeting", "post_meeting_kills_soon_after")
show("skipped report meetings", "skipped_report_meetings")
show("trips closed by a regroup", "trips_closed_by_regroup")
show("kill-witness button calls within 6 ticks of a regroup",
     "kill_witness_button_calls_soon_after_regroup")
table("dropped trigger-tick events", "trigger_tick_events_dropped_by_regroup")
show("meetings opening with an impostor in a vent", "meetings_opening_with_impostor_in_vent")
print("one reply")
conf("rebuttals the selector would not have chosen", "rebuttals_differing_from_selector")
conf("meetings with two repeat-speaker turns", "meetings_with_second_repeat_speaker")
show("an accused opener answers", "accused_opener_answers")
ka, na = show("opener rebuttals answering the charged tick",
              "opener_rebuttals_answering_charged_tick")
kr, nr = show("rebuttals that only redirect", "rebuttals_redirect_only")
if after:
    effective = na > 0 and ka / na >= 0.5
    not_effective = (na > 0 and ka / na < 0.2) or (nr > 0 and kr / nr >= 0.5)
    if na == 0 and not (nr > 0 and kr / nr >= 0.5):
        print("    reading: n/a (no evaluable opener rebuttal)")
    elif effective and not_effective:
        print("    reading: conflicting (an effective and a not-effective condition both hold)")
    elif effective:
        print("    reading: effective")
    elif not_effective:
        print("    reading: not effective")
    else:
        print("    reading: partial")
show("rebuttals carrying an alibi", "rebuttals_with_alibi")
show("rebuttals carrying a whereabouts claim", "rebuttals_with_whereabouts")
show("rebuttals carrying a sighting", "rebuttals_with_sighting")
show("rebuttal accusations against players who already spoke",
     "rebuttal_accusations_against_earlier_speakers")
table("beneficiaries", "rebuttal_beneficiaries")
print("body handle")
conf("report openings carrying the kill-tick handle", "report_openings_with_kill_tick_handle")
print("kill row")
conf("own-kill rows naming a teammate or held by a non-witness", "own_kill_rows_breaching")
served = cell("own_kill_rows_breaching")[1]
show("own-kill rows their holder cited", "own_kill_rows_cited_by_holder")
holders = honesty["kill_holders"]
citing = honesty["kill_holders_citing_the_kill"]
print(f"  honesty cell 5: kill holders {holders}; citing the kill "
      f"{rate(citing['numerator'], citing['denominator'])}")
if after:
    print(f"    presence: {'present' if served > 0 else 'absent'} ({served} rows served)")
print("impostor ballot")
conf("recorded teammate ballot targets", "recorded_teammate_ballot_targets")
neutral = honesty["ejects_citing_only_neutral"]
print(f"  honesty cell 3: impostor EJECTs citing only a neutral row "
      f"{rate(neutral['numerator'], neutral['denominator'])}")
if after:
    if neutral["denominator"] == 0:
        print("    reading: n/a (no impostor EJECT)")
    else:
        share = neutral["numerator"] / neutral["denominator"]
        verdict = ("the wording holds" if share <= 0.10 else
                   "it does not bind (a revision under a new value)" if share > 0.25
                   else "between the two readings")
        print(f"    reading: {verdict}")
show("impostor EJECT share", "impostor_eject_ballots")
show("impostor EJECTs labelled supported", "impostor_ejects_labelled_supported")
show("authored teammate targets", "authored_teammate_ballot_targets")
print("self-report off")
conf("impostor openers", "impostor_openers")
print("kill cooldown")
conf("kill cooldowns that differ from the recorded value",
     "kill_cooldowns_differing_from_recorded")
writes = tables["kill_cooldown_writes_by_writer"]["counts"]
print(f"  writes by writer [kill_cooldown_writes_by_writer]: "
      f"{json.dumps(writes, sort_keys=True)}")
if after:
    for writer in ("round_start", "after_kill", "regroup"):
        if writes.get(writer, 0) == 0:
            print(f"    Conf.: BREACH (no write counted at {writer})")
            misses.append(f"kill_cooldown_writes_by_writer.{writer}")
print("route lines")
routed = cells["meetings_with_a_route_line"]["in_scope"]
conf("steps false to the map", "route_lines_false_to_the_map")
conf("lines off the table", "route_lines_off_the_table")
kp, _ = show("meetings with a route line (presence)", "meetings_with_a_route_line")
show("ballots carrying route lines", "ballots_carrying_route_lines")
if routed:
    table("lines per meeting", "route_lines_per_meeting")
    table("steps by reading", "route_steps_by_reading")
if after and args.column == "r3":
    if not routed:
        print("    Conf.: BREACH (the route field is out of scope on round 3)")
        misses.append("route field out of scope")
    elif kp == 0:
        print("    Conf.: BREACH (no route line served: the route field reads absent)")
        misses.append("route field presence 0")
    else:
        print(f"    presence: present ({kp} meetings)")
print("route check (a process count, never a bar on correctness)")
m, w = route["M"], route["W"]
reach = route["R"]
print(f"  misjudged cases M {m}; at witness meetings W {w} (rule_inputs, column {args.column})")
print(f"  reach over M: (a) {reach['a']}, (b) {reach['b']}, (b-snapshot) {reach['b_snapshot']}, "
      f"(c) {reach['c']}; over W: (c) {route['R_W']['c']}")
print("per seat (reported)")
for seat in ("reporter", "other_crewmate", "impostor"):
    for suffix in ("", "_without_vent_proof", "_with_vent_proof"):
        key = f"{seat}_seats_ejected{suffix}"
        show(key.replace("_", " "), key)
show("reporters among ejected crewmates", "reporters_among_ejected_crewmates")
show("reporters among crewmate seats", "reporters_among_crewmate_seats")
print("kill witness (reported)")
show("held kill witnesses ejected", "held_kill_witnesses_ejected")
table("next meeting after a held kill", "held_kill_next_meeting_outcomes")
show("held kills whose killer was ejected at the next meeting", "held_kill_killers_ejected")
show("at any later meeting", "held_kill_killers_ejected_at_any_later_meeting")
print("counterfactual (reported)")
show("ejections undone with impostor ballots as SKIP", "ejections_undone_with_impostor_ballots_as_skip")
show("ejections undone with impostor ballots removed", "ejections_undone_with_impostor_ballots_removed")
show("ejections whose floor only impostors met", "ejections_carried_only_by_impostor_ballots")
table("re-tally outcome changes", "retally_outcome_changes")
print("held data (reported, each beside its definition)")
show("holds-nothing SKIPs whose inputs name no living candidate",
     "holds_nothing_skips_naming_no_candidate")
table("holds-nothing SKIPs naming a candidate, by source",
      "holds_nothing_skips_by_source")
show("cited lines true to the route", "cited_lines_true_to_the_route")
show("cited lines false to the route", "cited_lines_false_to_the_route")
table("cited placements by kind and verdict", "cited_placements_by_kind_and_verdict")
table("supported EJECTs not checkable, by reason", "supported_ejects_not_checkable_by_reason")
show("ejections whose target had a reconcilable pair", "ejections_on_a_reconcilable_pair")
show("ejections charged on a reconcilable pair", "ejections_charged_on_a_reconcilable_pair")
show("  at witness meetings: target had a pair", "witness_meeting_ejections_on_a_reconcilable_pair")
show("  at witness meetings: charged on a pair",
     "witness_meeting_ejections_charged_on_a_reconcilable_pair")
show("charges resting on a reconcilable pair", "charges_on_a_reconcilable_pair")
show("SKIPs labelled as holding nothing", "skips_holding_nothing")
show("ballots citing a rebuttal (the cell)", "ballots_citing_a_rebuttal")
show("  beside: ballots countering with a rebuttal", "ballots_countering_with_a_rebuttal")
print("envelope (non-gating)")
k, n = show("impostor win share", "impostor_wins")
if after and n:
    share = Fraction(k, n)
    print(f"    envelope: {'flagged above 0.60' if share > Fraction(3, 5) else 'flagged below 0.20' if share < Fraction(1, 5) else 'inside 0.20-0.60'}")
k1, n1 = cell("reporter_seats_ejected_without_vent_proof")
k2, n2 = cell("other_crewmate_seats_ejected_without_vent_proof")
form, line, words = BARS[args.bar]
if n1 == 0 or n2 == 0:
    flag = "n/a (no reporter seat or no other crewmate seat without vent proof)"
elif form == "reporter":
    flag = ("flagged" if Fraction(k1, n1) > line else "not flagged") + f" (reporter rate {k1}/{n1})"
elif k2 == 0:
    flag = "flagged, reporters alone" if k1 > 0 else "not flagged (no seat ejected)"
else:
    relative = Fraction(k1 * n2, k2 * n1)
    flagged = k1 * n2 > line * (k2 * n1)  # cross-multiplied, exact
    flag = f"relative rate {float(relative):.1f}, {'flagged' if flagged else 'not flagged'}"
print(f"  the re-keyed reporter flag, bar {args.bar} ({words}): reporter seats {k1}/{n1} against "
      f"other crewmate seats {k2}/{n2} without vent proof: {flag}; never read by the step rule")
print("reported, gating nothing")
rk, rn = show("role-correct ejections", "role_correct_ejections")
print(f"  innocent ejections: {rn - rk} of {rn} ejections")
show("meetings with vent proof", "meetings_with_vent_proof")
print(f"  kills [kills_seen_by_crew, its denominator]: {cell('kills_seen_by_crew')[1]}")
show("impostors able to kill when a meeting opened", "impostor_cooldown_zero_at_open")
print(f"  the win split [impostor_wins]: {n - k} crew, {k} impostor")
if args.step:
    inside = n > 0 and Fraction(1, 5) <= Fraction(k, n) <= Fraction(3, 5)
    step = ("the era-keyed promotion of round 3 as the shown set"
            if not misses and inside and m <= ROUND_2_M
            else "round 2 staying shown, with round 3 kept as a comparison record")
    print(f"step rule: names {step}, the owner's to take or override "
          f"(Conf. misses {len(misses)}; impostor wins {k}/{n}; M {m} against round 2's {ROUND_2_M})")
if misses:
    print(f"Conf. misses: {', '.join(misses)}")
    sys.exit(1)
```

`reproject.py` is Constraints' re-projection, quoted whole here and again at P (standard library only,
count-only). It is round 2's (its audit 1.13) with the anchor moved from the baseline-9 s9 bytes, which left the
tree, to R2, and a refusal when a completed candidate seed has no round-2 seed beside it. On a scratch copy of R1's
seeds 0-11 it gives the three runs the spend item states.

```python
"""Re-project round 3's spend against the 90% stops (count-only).

Usage: reproject.py CAND_DIR R2_DIR SUMMED_WALL_SECONDS

Each count is (the candidate's total over its completed seeds / round 2's
total over the same seeds) x round 2's leg total; the wall is the summed
recording wall / the completed seeds x 50. Exits 1 when any figure is past its
stop, or when any call's cost is not zero.
"""

import glob
import json
import re
import sys

STOPS = {"calls": 2_520, "input": 15_750_000, "output": 675_000}
WALL_STOP = 38_880  # 10.8 h


def tally(directory):
    per_seed = {}
    for path in glob.glob(directory + "/replay-seed-*.jsonl"):
        seed = int(re.search(r"replay-seed-(\d+)\.jsonl$", path).group(1))
        calls = tokens_in = tokens_out = 0
        cost = 0.0
        for row in map(json.loads, open(path)):
            for call in row.get("llm_calls") or []:
                calls += 1
                tokens_in += call["input_tokens"]
                tokens_out += call["output_tokens"]
                cost += call["cost_usd"]
        per_seed[seed] = (calls, tokens_in, tokens_out, cost)
    return per_seed


cand = tally(sys.argv[1])
r2 = tally(sys.argv[2])
wall = float(sys.argv[3])
seeds = sorted(cand)
if not seeds or any(s not in r2 for s in seeds):
    sys.exit("every completed candidate seed must have round 2's seed beside it")
stops = []
print(f"completed seeds {len(seeds)} ({seeds[0]}-{seeds[-1]})")
for index, name in enumerate(("calls", "input", "output")):
    done = sum(cand[s][index] for s in seeds)
    base = sum(r2[s][index] for s in seeds)
    projected = done / base * sum(v[index] for v in r2.values())
    past = projected > STOPS[name]
    stops += [name] if past else []
    print(f"  {name}: {done} / {base} x round 2 = {projected:,.0f} "
          f"({projected / STOPS[name]:.1%} of the {STOPS[name]:,} stop){' STOP' if past else ''}")
wall_projected = wall / len(seeds) * 50
past = wall_projected > WALL_STOP
stops += ["wall"] if past else []
print(f"  wall: {wall:,.0f} s / {len(seeds)} x 50 = {wall_projected:,.0f} s "
      f"= {wall_projected / 3600:.2f} h (stop 10.8 h){' STOP' if past else ''}")
nonzero = [s for s in seeds if cand[s][3] != 0.0]
if nonzero:
    stops.append("cost")
    print(f"  cost: non-zero on seeds {nonzero} STOP")
if stops:
    print(f"STOP: {', '.join(stops)}")
    sys.exit(1)
```

The pre-spend at F runs the fake rehearsal, the scripted cases, the lab, and the readings and re-projection proofs
on scratch targets; the section comparison diffs `git show P:<audit>`'s pre-registration section against the head's.
On macOS the evolution-strategy hash pin is Linux-only: gate in a clean worktree, cite CI for it.

## Results

**This phase: P and Q only (2026-10-09).** The orchestrator dispatched the card in two phases. This one landed the
pre-registration P, the owner's confirmation Q, the pre-spend evidence at `F` and P, and a draft pull request; no
provider was called, no key was copied, read or referenced, and the recorder ran only as the dry run, with no seed.
The fake dress rehearsal, the scripted game and lab, the probe, the sittings, the delivery and the assessment are
phase 2, dispatched by the orchestrator after this phase is reviewed; every item they carry stays unchecked below,
and this section gains their evidence then. Full evidence: `audits/audit-2026-10-09-stage-b-r3.md` sections 1 to 3.

**Commits and checkouts.** `F` = `e4fc6cbf` (`main` after #500, #501, #502, #503 and #504, the cards flipped, memo
8.7 and 8.8, and this card's amendment). On `work/stage-b-record-r3`: P = `641b4254` (`coordination:`, the audit's
section 1, its index row, the `audits/` row of `docs/artifacts.md`); Q = `bb13fbc7` (`coordination:`, the audit's
section 2 and the row re-derived for its length); `d1221611` (merge of `main` at `335cbdc9`, two document commits
adding memo 8.9); `9a7cb992` (`coordination:`, the audit's section 3 and the row); then this Results commit. The dry
run ran in a scratch worktree detached at `641b4254` outside the repository's working tree (removed after); the
pre-spend ran in this worktree at `F` with a clean status; the gates of section 3.7 at Q.

**Sections relied on.** This card; decision memo sections 0, 1, 3.1 to 3.3 and 3.4's brief, 8.1 to 8.8 (8.9 noted
below); round 2's audit sections 1 and 6 and card (the template); `tasks/work/route-lines-field.md` and
`tasks/work/census-held-data-cells.md` Results (the field, its rehearsals, stamp and instrument; the cells by key);
`docs/gameplay-census.md`; `docs/architecture.md` "Determinism and the substrate ladder" (a candidate round is its
own era and instruments never pool eras; the recording is the hosted run's reproducibility boundary) and
"Explicit cleanup experiments" (the closed config, omitted at default, refused when unknown);
`docs/experiment-arms.md` (the route field's row and its stamp).

**Acceptance, item by item (this phase).**
- *P and Q precede the first seed* (unchecked: its MANIFEST and probe-date checks run after the legs). Held now:
  P holds the rulings (2026-09-24 to 2026-10-09) and memo 8.2 verbatim and dated, the config bytes and sha256, the
  ceilings, stops and amended discipline, the table, flag and step rule, and `readings.py` and `reproject.py` whole
  (sha256 `9e22e40c420e6082b05b55596b0073fbf53c0b5c7e0f22cb04ee76733d257abc` and
  `0cd632e045dc06725df8bdc07a8320876a219a6af53fe64db5b494543496445c` as extracted from this card at `F`, byte-equal
  in the audit); `git diff --name-only e4fc6cbf 641b4254` lists only the audit, its index row file and
  `docs/artifacts.md`; the config is not committed. Q quotes the owner's words, memo 8.7 whole with each of the five
  points against its confirming words, and memo 8.8 whole. `git merge-base --is-ancestor` exits 0 for F before P and
  P before Q; with Q in place of P, and P in place of F, it exits 1. Section 1 at P against the head: 951 lines,
  0 differing; with "0.30" edited to "0.31" in one reading of a scratch copy, 2 differing, exit 1. Waiting on phase
  2: Q before the first `record:` checkpoint, Q's committer date (2026-10-09T02:43:47-04:00) before the probe's start
  and every `refreshed_at`, P against the MANIFEST's one `git_sha`, and the scratch-MANIFEST date proof.
- *The before columns are computed* (checked). Census and scorecard `--set-dir replays/samples/9p2i --json-stdout`
  equal the shipped `samples/9p2i` entries in 1,753 of 1,753 and 108 of 108 leaves (the census grew from 1,324 by the
  held-data and route cells); a count-only comparison of the 245 round-1 and round-2 counts that round 2's audit
  section 6 and this card's Evidence and table state reads 245 equal, 0 differing; the route-check replay at `F`
  with r1 and r2 equals the committed `rule_inputs` in 24 of 24 leaves (r1 29, 0, 8, 8, 20, 0; r2 40, 7, 15, 16, 29,
  7). Proofs, each one cell edited: the census leaf compare prints
  `cells.holds_nothing_skips_naming_no_candidate.denominator: set-dir=215 shipped=214`, exit 1; the scorecard
  `grounded_skip.numerator: set-dir=45 shipped=44`, exit 1; the route compare `r2.R.c: scratch=30 committed=29`,
  exit 1; the whole-table compare `DIFF r1 impostor_cooldown_zero_at_open: re-measured (85, 203), stated (84, 203)`,
  exit 1.
- *The readings are pre-registered in three columns* (checked). `readings.py --after` exits 0 on round 1 and round 2
  with no Conf. miss; every key it names exists at `F`; the cells the table marked "measured at F" read 0/256 and
  0/214; 244/259 and 278/281 true, 15/259 and 3/281 false; 0/3 and 7/12. The readings item's planted copies give
  exactly the card's exits and lines (audit 3.3): unedited exit 0 naming the promotion (M 40, 24/50); presence 0 exit
  1 naming the route field; `route_lines_false_to_the_map` then `stale_report_meetings` raised, exit 1 naming each;
  M 41 or 31/50 name round 2 staying shown; the flag forced on (numerator 60) or `role_correct_ejections` edited
  leave the `step rule:` line byte-identical (`cmp`). Also: an r2 column off 40 exits 1; `--step` off r3 exits 1.
- *The amendment of 2026-10-09* (checked before this phase): the merged name `holds_nothing_skips_by_source` is the
  one `readings.py` reads, and it reads at `F` without a refusal.
- *The reporter flag* (checked). Bar A, as the owner confirmed: 17.0 on round 1 and 10.6 on round 2, not flagged;
  under bar B round 1 flags; a scratch copy with k2 = 0 and k1 = 1 prints `flagged, reporters alone`. The baseline-9
  column, folded by the census at `F` from `d41c9006`'s 9p2i bytes (`git archive` into scratch), reads 7/75 against
  2/243: A 11.3 not flagged, B flagged, C not flagged. Every reading in the bar table reproduces.
- *The step rule* (checked). The sentence is carried whole at P (1.11); its proofs are the readings item's; the
  win-share condition is confirmed by the owner (memo 8.7) and the step itself is delegated to the orchestrator on
  the owner's criteria (memo 8.8), both quoted in the audit's section 2.
- *The preflight holds at F* (checked). The declared file (342 bytes,
  `a788b9eba5e8f2f5d29033fece2d0dc0dbac7d3528ea93c7c7a93327dbc6d57d`, the card's figure) validates with ten fields
  off default, the route field on the meeting layer, in `OMITTED_AT_DEFAULT`; `engine_arguments` equals round 2's;
  the four stamps are served; `self_report` False, the two versions None; `COLUMN_LABELS` holds `r3`. Proofs: an
  unknown key refused (`extra_forbidden`); without the route key the bytes equal round 2's declared file; the field
  card's refusals pass at `F` (`test_no_environment_sets_a_config_only_field`,
  `test_a_config_only_field_must_equal_the_runners_both_ways[route_lines_version]`,
  `test_each_instrument_refuses_it_once_the_field_leaves_its_reads` (7), `test_the_golden_refuses_it_once_the_field_leaves_its_reads`).
- *The fake dress rehearsal* and *the scripted rehearsal and the lab* (unchecked): they run the recorder or the lab
  on the declared config, which phase 2 does before the probe. The field card's own rehearsal suites pass at `F`:
  199 passed over its three suites, 40 of them the fake-inertness, scripted-presence and refusal cases; CI at `F`
  is run 37892577802, success.
- *The dry run and the probe* (unchecked: the probe is phase 2). The dry run at P exits 0, echoing the declared
  file's sha256 `a788b9eb...6d57d`, the ten fields and the bare slate, with `git status --porcelain
  --untracked-files=no` at 0 lines before and after; with a stray `AILIBI_BOUNDED_REBUTTAL=1` it exits 1 ("Refused:
  the environment exports AILIBI_BOUNDED_REBUTTAL ... Nothing was staged.").
- *The round is the declaration*, *the spend*, *the checkout and freeze*, *the derived views*, *the assessment* and
  *nothing publishes* (unchecked): phase 2. Held so far: the re-projection proofs at `F` give the card's figures
  (1,619 / 9,978,176 / 470,463 / 4.63 h, exit 0; 677,314 output, exit 1; 10.88 h, exit 1; an unmatched seed, exit
  1); the frozen pathspec over `e4fc6cbf..HEAD` and `..origin/main` prints 0 commits (12 over `76270d6c..e4fc6cbf`);
  the nothing-moves diff is empty; the index row's prose passes `copy_problems` with 0 and the identifier scan with 0.

**Commands and exits** (bare shell, `env | grep -c '^AILIBI_'` 0; scratch outside the repository): census, scorecard
and honesty `--set-dir` on round 1 and round 2, exit 0 each; the route-check replay with r1 and r2, exit 0;
`route_check_replay --check` and `route_lines_replay --check`, exit 0 each (47.1 s, 48.2 s); the tally,
`1556 9344346 433660 0.0` and `1502 9187880 418270 0.0`; `validity_gate.py` on both with their own declared
configs, exit 0, ten checks PASS, betrayal 0 of 717 and 0 of 691; `pytest -n 6` over the field's three suites, 199
passed; over the arms, config, census, candidate-set, ballot-arm, scripted-meeting and recorded-reader suites, 921
passed; `scripts/verify_ml_evidence.py` offline (never `--complete`), exit 0 at P, Q and `9a7cb992` (64 checks: 52
OK, 0 FAIL, 7 ABSENT, 5 INFO); `scripts/check_doc_facts.py` and `scripts/validate_task_docs.py`, exit 0 each at the
same three heads; `tests/scripts/test_verify_ml_evidence.py` with `tests/scripts/test_check_doc_facts.py`, 415
passed. The `audits/` row of `docs/artifacts.md`, re-derived with `git ls-files audits` and the files' sizes at each
commit: 31,431,870 / 334 at `F`; 31,494,430 / 335 at P; 31,503,145 at Q; 31,523,225 at `9a7cb992`. The house gate
is CI's green run at the pull request's pushed head (memo 8.7 item 1), cited by run id in the pull request body; this
card cannot name the run of the commit that carries it, and no local `check.sh` ran at the head.

**Decisions.**
1. The orchestrator's rulings for this dispatch, recorded: the owner's words of 2026-10-06 and 2026-10-09 bind
   (memo 8.1, 8.7, 8.8); memo D14's retirements were not ruled at `F`, so nothing is retired and
   `replays/candidates/stage-b-r1/` stays. After P, `main` gained memo 8.9 (2026-10-09), which rules D14's list for
   retirement by its own card after this record merges and keeps the comparison records: round 1's directory stays,
   as section 1 states. 8.9 also keeps round 2's bytes as `replays/candidates/stage-b-r2` on a promotion; that is a
   follow-up for a promotion card and changes nothing pre-registered.
2. `main` moved only in the decision memo, outside the frozen pathspec, so it was merged in (`d1221611`), as the
   freeze rule says; P and Q are unchanged and the recording checkout still detaches at P.
3. Q also re-derives the `audits/` row of `docs/artifacts.md`, because the audit grew and the offline evidence check
   pins the row's bytes; this is the only file besides the addendum that Q touches.
4. The audit's section 1 carries the owner's words of 2026-10-09 beside the earlier rulings (the dispatch asked for
   section 8's rulings verbatim and dated); section 2 quotes the confirmation and the delegation whole, point by point.
5. The pull request is a draft in this phase; nothing merges until the round completes.

**Limitations.** The scratch tools (leaf, route and whole-table comparisons, the planted copies, the section
comparison) are session aids, not committed; each count they read comes from a committed source through a named
command. The 9 of (c)'s 11 unreached cases resting on a vent sighting are the committed reports' count, reproduced
by the instruments' `--check`, not re-derived by the comparison. The baseline-9 flag column is context only, folded
from `d41c9006`'s bytes. Everything that needs a recorded seed waits on phase 2.

**Phase 2: the recording (2026-10-09).** Round 3 is recorded: `replays/candidates/stage-b-r3/9p2i` holds seeds 0-49
on the declared config (sha256 `a788b9eb…6d57d`), every gate passes on the round, every Conf. cell reads 0 (the
cooldown cell at all three writers, the route cells included), and the step rule names **the era-keyed promotion of
round 3 as the shown set**. The step itself is not taken here: memo 8.8 gives it to the orchestrator, who writes it
into the audit after reading the round. One stop is open: after the declared config entered the tree, one test of the
route-lines card turned red only because the round exists (below, and audit 7.5), so the pull request stays a draft
and no green CI run at the head can be cited yet. Full evidence: `audits/audit-2026-10-09-stage-b-r3.md` sections 4
to 10 (4 the rehearsals, dry run, pause and key; 5 the probe; 6 the batches and events; 7 the gates, spend, derived
views, freeze and the stop; 8 the assessment; 9 the menu; 10 the limitations).

**Commits and checkouts.** Recording: a worktree detached at P (`641b4254`) outside the repository's working tree
(`uv sync --frozen`, no `.env`, the untracked declared copy checked by `shasum -a 256` before the dry run and every
leg), which ran only the recorder. Verification: a worktree detached at `F` (`e4fc6cbf`, no declared copy) for the
rehearsals, the lab and the planted suites, and a scratch clone at `F` (no remote) for the fake set's throwaway
instrument commit, never pushed. Delivery: this branch's worktree. The eleven `record:` checkpoints, each pushed:
`a09065cc` (the probe), `3800a6ce`, `d4ce0c6b`, `99950ebd`, `0d450119`, `d03a1a9d`, `48bdccbf`, `ddf45f4d`,
`152c9bd0`, `502e70a8`, `97b68014`. Then `f35ff99c` (the delivery commit: the declared config with P's sha256, the
round README), `e1d0c8d4` (the golden's pin row), `7bdb490d` (merge of `main` at `9775c9d6`, three document commits
under `tasks/`), `45d28b68` (the candidate sentence), and the commits carrying the audit's sections 4 to 10 and this
section.

**Sections relied on.** This card; `AGENTS.md`; `docs/architecture.md` "Determinism and the substrate ladder" (a
candidate round is its own era; byte-identical re-simulation within the recorded scope, which the verifier, the golden
and the gate rely on) and "Explicit cleanup experiments" (the closed config, omitted at default, refused when
unknown); `docs/experiment-arms.md` (the route field's row and stamp); decision memo sections 0, 1, 3.1 to 3.3 and
3.4's brief, 8.1, 8.7, 8.8 and 8.9; round 2's audit sections 4 to 9 and card Results (the template for the spend, the
gates, the readings and the assessment); `docs/workflow.md`.

**Acceptance, item by item (phase 2).** Every count below is count-only, in a bare shell (`env | grep -c
'^AILIBI_'` 0), and reproduces from the committed bytes with the command beside it.
- *P and Q precede the first seed* (checked). `git merge-base --is-ancestor`: F before P, P before Q, Q before the
  first `record:` checkpoint `a09065cc`, and P against the MANIFEST's one `git_sha` (`641b4254`), exit 0 each; the head
  in place of P exits 1. Q's committer date (06:43:47Z) precedes the probe's start in the operator log (07:59:44Z)
  and every MANIFEST `refreshed_at` (2026-10-09 on all 50 rows, a UTC date): exit 0; a scratch MANIFEST with seed 7 at
  2026-10-08 exits 1 (1 row before), and a probe start of 06:40Z exits 1. Section 1 at P against the head: 951 lines
  each, 0 differing; section 2 at Q against the head: 109 lines, 0 differing; with the first "0.30" of a scratch copy
  edited to "0.31", 2 differing lines, exit 1.
- *The fake dress rehearsal* (checked; audit 4.1). Seeds 0-49, `AILIBI_LLM_PROVIDER=fake`, scratch outside the tree,
  at `F`: exit 0, 19 s, $0, 132 meetings. Gate (ten checks PASS), `verify_samples.sh` (50 clean), the golden's walk
  (1,652 prompts, 0 not reproduced), census (20 Conf. cells 0; cooldown 0/591 at 100, 227 and 264; route presence
  0/132 and 0/826 ballots: no block served), scorecard, honesty and the packet scan exit 0; both route instruments'
  r3 columns on a throwaway commit of a scratch clone exit 0 (route-check r3 M 0; route-lines r3 served, 0 blocks).
  The fake tally `1652 6409973 94990 0.0` equals the same rehearsal on round 2's file, and the two sets' 2,433 rows
  are equal once the config key and the stamp suffix are removed. Proof: gated against round 2's file, exit 1 on
  `cost_and_provenance_exact` alone (50 lines naming `route_lines_version`).
- *The scripted rehearsal and the lab* (checked; audit 4.2). The route-lines card's scripted game recorded from the
  declared file through its own loader: loader, census, scorecard, gate (ten checks) and golden (26 prompts) pass,
  presence 2/2 meetings and 12/13 ballots, `route_lines_false_to_the_map` 0/15 and `route_lines_off_the_table` 0/15.
  At `F`: 457 passed over the field's three suites and round 2's scripted, ballot-arm and recorded-reader suites
  (among them `test_the_fake_rehearsal_is_inert`, `test_the_scripted_on_game_walked_without_the_field_fails_at_every_block`
  and `test_the_manager_passing_no_lines_fails_the_scripted_on_golden`); the golden's scripted cases 4 passed. The
  lab's ten round-1 arms equal `stage-b-r1-frozen-head.json` on its own keys: 160 rows, 13,622 fields, 0 differing;
  `route_lines_replay --check` and `route_check_replay --check` reproduce. Proofs: dropping the recorded evidence
  profile leaves 13 of 26 prompts not reproduced and 2 meetings miscounted; one edited lab counter prints
  `stage_b_full/9p2i/1000: counts['applied:IMPOSTOR:kill']`, exit 1.
- *The dry run and the probe* (checked; audit 4.3, 5). The dry run at P exits 0 echoing `a788b9eb…6d57d`, the ten
  settings and the bare slate, porcelain with untracked hidden 0 lines before and after; with
  `AILIBI_BOUNDED_REBUTTAL=1` it exits 1 ("Refused: ... Nothing was staged."). The probe, seeds 0-1 on two workers:
  631 s, exit 0, 5 meetings, route lines served in 5/5 meetings, so no extension; its gates all exit 0.
- *The round is the declaration* (checked; audit 7.1). The gate on the round: exit 0, ten checks PASS by name, with
  `--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, the four prompt-version pairs, the declared config,
  `--expected-seeds 0-49 --require-one-recording-sha`; MANIFEST flags equal round 2's, policy `fsm-default`;
  `grep -l deadline_default` 0; census `--set-dir` exit 0 with the route cells; the golden reproduces all 1,523 calls.
  Proofs: `--expected-seeds 0-50` exit 1 ("missing [50]"); round 2 against the declared file exit 1 on
  `cost_and_provenance_exact`; the census card's planted breaches (`test_every_guarded_cell_has_a_planted_pair`,
  `test_a_route_line_breach_raises_naming_set_seed_meeting_and_voter`) and the field card's cases pass (the census
  suite in the targeted run at the head; the field's suites at `F`).
- *The spend* (checked; audit 6.3, 7.2). The tally `1523 9653306 426116 0.0`: 54.4%, 55.2% and 56.8% of the call,
  input and output ceilings, 12,008 s = 3.34 h of recording wall (27.8%), $0, one sitting, no husk. Every
  re-projection stayed inside its stop (the 10-seed one at seeds 0-11: 57.4%, 57.8%, 60.2%, 3.31 h); the probe's
  projected wall 4.38 h puts the 1.5x line at 6.57 h, which nothing approached. The reprojection proofs are phase
  1's at `F` (3.3).
- *The checkout, the pause, the key and the freeze* (checked; audit 4.3, 7.4). One `git_sha`, P's; each of the seven
  scan patterns fires on its planted file (exit 1) and the plants were deleted; the key scan read 0 at every push;
  with a planted pause file and the recorder replaced by `true` the leg runner exits 3 and starts nothing.
  `git log --oneline e4fc6cbf..HEAD` and `..origin/main` over the frozen pathspec: 0 commits each; over
  `76270d6c..e4fc6cbf`, 12.
- *The derived views and the registration* (checked; audit 7.3). The report is the recorder's rebuild and
  `build_sample_report.py --check` passes on the round; the README's `candidate-declaration` block holds the sha256
  line and `9p2i seeds 0-49`; the `replays/candidates/` row reads 72 MB / 111 files and the `audits/` row is
  re-derived with `git ls-files` at the commit carrying this section; offline `verify_ml_evidence.py` reads OK; the
  golden's row `candidates/stage-b-r3/9p2i` is (119, 702, 0, 0). Proofs: without the row, 2 failed (`KeyError: 'no
  retired-guard pin for candidates/stage-b-r3/9p2i'`), with it 12 passed; the candidate test's planted perturbations
  pass (`tests/scripts/test_candidate_sets.py` in the targeted run).
- *The assessment* (checked; audit 8). Round 3's column comes only from the census, scorecard and honesty
  `--set-dir`, the gate's betrayal check and the route-check replay at `45d28b68`, through `readings.py` unchanged
  (`9e22e40c…57abc`), in the pre-registered order; the menu as 1.12 lists it. Proof: pooled with round 2 and with
  round 1 through `fold_set` then `pool`, `GameplayCensusEraError` both times.
- *Nothing publishes, and the copy is plain* (checked; audit 7.1, 7.4). The nothing-moves diff is empty;
  `verify_samples.sh` (bare: four sets clean) and per set, and `build_sample_report.py --check` on all six
  directories, exit 0; the scorecard and census `--check`, `check_doc_facts.py` and both instruments' `--check` exit
  0; the demo bundle at `F` and at the head, 110 files each, `diff -r` exit 0 with the sample mtimes pinned. The README,
  the candidate sentence and the index row's prose: `copy_problems` 0, 0, 0 and the identifier scan 0, 0, 0; "6/7"
  in a copy of the README gives 1 problem, "R7" in a copy of the sentence 1 hit;
  `test_audits_index_ladder_tip_drift_detected` and `test_unindexed_audit_detected` pass.

**The readings** (audit 8). Every Conf. cell 0, the route cells 0/7,956 steps false to the map and 0/2,416 lines off
the table, route presence 117/119 meetings (671/702 ballots); cooldown 0/442 against 6 at round start 100, after a
kill 192, at a regroup 150. Look and wait **effective** (7/70); one reply **effective** (20/20 evaluable, redirect-only
25/119); kill row **present** (22 rows); impostor ballot, **the wording holds** (0/101). Envelope: impostor win share
**17/50 = 0.34 (0.22-0.48)**, inside 0.20-0.60; the re-keyed reporter flag under bar A, 10/95 against 5/302, relative
rate **6.4, not flagged** (round 1 17.0, round 2 10.6). The route-check count: M **29** (round 1 29, round 2 40), W 7;
reach over M (a) 8, (b) 15, (b-snapshot) 18, (c) 25, (c) over W 7; the field's served reach 26 of 29 and 7 of 7. The
step line: `step rule: names the era-keyed promotion of round 3 as the shown set, the owner's to take or override
(Conf. misses 0; impostor wins 17/50; M 29 against round 2's 40)`. Reported, gating nothing: role-correct ejections
46/61, innocent ejections 15, kills 192, the win split 33 crew and 17 impostor.

**Commands and exits at the head** (`45d28b68`, before the documentation commits): the battery of the Validation
section, as audit 7.1 lists it, every exit 0, except the one case of the stop; CI run 37924867474 at `45d28b68`:
Project checks 1 failed, 10,850 passed, 40 skipped, 3 xfailed; Frontend checks and Frontend e2e passed. Targeted
suites (`tests/scripts/test_candidate_sets.py`, `tests/eval/test_gameplay_census.py`, the route-lines arm, field and
instrument suites, `tests/orchestrator/test_experiment_arms.py`, `tests/orchestrator/test_experiment_config.py`): 1
failed (the stop), 861 passed; `pytest -m campaign`: 337 passed; the golden `-k "retired_guard or stage-b-r3"`: 12
passed. The document gates are re-run at the commit carrying this section and quoted in the pull request.

**The stop (open).** `tests/meetings/test_route_lines_arm.py::test_every_committed_payload_reads_the_field_off`
asserts that no `replays/**/experiment-config.json` reads `route_lines_version` ON, and so finds exactly one file,
`replays/candidates/stage-b-r3/experiment-config.json`, the round's declared config, which reads it ON by design. This
card's Constraints name that a stop ("Stop and ask ... if a test besides the golden pin turns red only because
another round exists"); its one permitted test edit is the golden's pin row, and the file is the route-lines card's.
So the case is not edited here, the pull request stays a draft, and the question is the orchestrator's: who edits the
case, and how (for example, reading OFF every committed payload and file except a candidate round's declared config
that its README declares, with a planted stray config under `replays/samples` that still fails), before this record
can merge. Nothing recorded depends on it.

**Decisions (phase 2).**
1. The orchestrator's rulings for this dispatch, recorded: the owner's words of 2026-10-06 and 2026-10-09 bind (memo
   8.1, 8.7, 8.8, 8.9); the comparison records are kept: round 1 stays, and if round 3 is promoted round 2's bytes
   become `replays/candidates/stage-b-r2` by the promotion card, not this one. Under 8.9 the promotion's merge is the
   orchestrator's; audit 3.7 gains a paragraph saying so and the index row reads it, while sections 1 and 2 stay as
   quoted.
2. The step rule's line is recorded and the step is not taken (memo 8.8 reserves it); nothing here merges.
3. `route_lines_replay` takes its r1 and r2 columns at the commit the committed route-check JSON pins (`5877adb4`), as
   the instrument requires; the card's Validation line names `F`, whose set bytes are the same. The route-check
   replay's columns run at `F` as written.
4. The 1.5x rule reads the probe's projected wall (4.38 h, so 6.57 h), applied to the summed wall and every
   re-projection, as round 2 applied it.
5. The candidates row of `docs/artifacts.md` is re-derived at every checkpoint, so the offline evidence check stays OK
   at each; the declared config and README enter the tree after the last seed, as this card says (round 2 committed
   them before seed 0), so the intermediate checkpoints' CI runs were red by design (the candidate shape check and the
   golden's unpinned set) and are not gate records.
6. `main` moved only under `tasks/` during the sitting and was merged in after the last seed (`7bdb490d`).
7. The key file stayed mode 0600 outside every checkout until the last push, so that push's scan could count the exact
   value, and was deleted right after it; the operator log outside the repository records the time.
8. The card's Status line and `tasks/README.md`'s inventory sentence are the orchestrator's on `main` and are not
   edited; the acceptance boxes are ticked on their evidence, and the stop keeps the card from being done.

**Limitations (phase 2).** One hosted recording of 50 games per round: rounds 2 and 3 differ in one key, and their win
shares' intervals (0.35-0.61 and 0.22-0.48) overlap, so each difference is the field's only within hosted-generation
noise. M counts charged reconcilable pairs; a served line is shown, not proven read. The scratch tools (the leg runner,
the sync, the count-only walk and Conf. check, the key scan, the date, section, pooling and copy checks) are session
aids kept outside the repository; every count they read comes from committed bytes through a named production command.
Recording wall and the per-leg times come from the recorder's logs and the operator log, outside the repository. The
CI gate at the head is red until the stop is resolved.

### Review corrections, round 1 (2026-10-09)

Three review lenses over the head `fd9eef64` returned one blocking finding, the record's one stop (audit 7.5): CI
run 37927577127 at `fd9eef64` read Project checks 1 failed, 10,850 passed, the one failure
`tests/meetings/test_route_lines_arm.py::test_every_committed_payload_reads_the_field_off`, which walked every
`replays/**/experiment-config.json` and found `replays/candidates/stage-b-r3/experiment-config.json`, the round's
declared config, reading `route_lines_version` ON by design (audit 1.3). No other finding was returned.

**The resolution, by the orchestrator's assignment.** The orchestrator ruled the case re-scoped, test-only, under
the one-writer map: the route-lines card is done and merged, and this record carries the edit as directly necessary
follow-through, as round 1's fourteen re-scopes did. `368109f7` (`test:`) makes the edit in that one file; no
recorded byte, no production code and no other test moved.
- *Old assertion.* `_committed_payloads_reading_the_field_on() == []`, the helper listing any committed
  `experiment_config` payload under `audits/` or `tests/fixtures` reading the field ON, any
  `replays/**/experiment-config.json` whose `route_lines_version` is not None, and any of the five listed sets
  (`samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i`, `candidates/stage-b-r1/9p2i`) whose first
  replay recorded it.
- *New assertion.* `_committed_payloads_reading_the_field_on(_REPO / "replays", _COMMITTED_SETS) == []`, the same
  three walks: the payload walk unchanged (106 files, 1,193 payloads), the five sets unchanged, and every
  `replays/**/experiment-config.json` still read (3 files) except a candidate round's declared config whose round
  recorded the field ON. That exception is enumerated from the candidate declarations, never named by a path: a
  round `candidate_rounds()` lists, whose README holds one `candidate-declaration` block (parsed, without a problem,
  by `tests/scripts/test_candidate_sets.py`'s own `declaration_blocks` and `parse_declaration`) naming the file's
  sha256, and every seed of every set it declares has a replay that recorded the field at the file's value. Only a
  file directly inside a round directory under `candidates/` can be left out, so a file under `samples/` or
  `ml_corpus/` never is. The walk takes its root and its sets, and refuses an empty set list. On the tree it leaves
  out one file, round 3's declared config, and lists none.
- *Strength kept.* On every committed payload, on `replays/samples/9p2i/experiment-config.json` and
  `replays/candidates/stage-b-r1/experiment-config.json`, and on each of the five sets, the case asserts what it
  asserted before; the one file it no longer asserts OFF is a declared config whose 50 recordings read the field ON,
  which `test_every_committed_round_holds_its_declared_shape` already holds to its declaration.
- *Planted.* `test_only_a_declared_round_recording_the_field_on_may_read_it_on` builds a scratch `replays/` from
  round 2's declared file and the fake rehearsal's ON and OFF games, beside a round whose config is round 2's file
  plus the field (342 bytes, sha256 `a788b9eb…6d57d`, round 3's declared bytes) declared for seeds 0-1. Ten plants:
  as declared, 0 listed; a round still recording, holding no config yet, 0; an ON config under `samples/9p2i` (the
  declared round beside it) lists exactly that file; one under `ml_corpus/9p2i` lists exactly it; a listed set
  recorded ON lists `samples/9p2i`; a declaration naming round 2's bytes, naming no set or appearing twice, and a
  declared seed recorded OFF or missing, each list exactly the round's config. `test_the_walk_refuses_to_read_no_set`
  pins the refusal. In the tree, a scratch copy of the round's declared config at
  `replays/samples/9p2i/scratch-plant/experiment-config.json` turned the committed case red listing exactly that file
  (1 failed); deleted, with `git status --short` showing only the test edit, the case passed (1 passed).
- *Mutation probe* (scratch, 23 mutants over the changed spans): 21 killed. Two survive: `== value` made
  `is not None`, equivalent because the field validates only to 1 or None
  (`test_a_value_other_than_one_or_none_is_refused`); and the committed case's set list narrowed to its first set,
  the class the old inline loop carried too, since every committed set reads the field OFF.

**Gates at `368109f7`** (bare shell, `env | grep -c '^AILIBI_'` 0, count-only). The targeted suites (the
route-lines arm and field suites, `tests/eval/test_route_charges.py`, both route instruments' suites,
`tests/scripts/test_candidate_sets.py`, `tests/eval/test_gameplay_census.py`, the arms and config suites): 1,023
passed, 0 failed; the golden `-k "retired_guard or stage-b-r3"`: 12 passed; `check_doc_facts.py` and
`validate_task_docs.py` exit 0; offline `verify_ml_evidence.py` exit 0 (never `--complete`); the scorecard and census
`--check` exit 0; `route_check_replay --check` and `route_lines_replay --check` exit 0; `verify_samples.sh` bare and
on each of the six set directories, and `build_sample_report.py --check` on each, exit 0; `pytest -m campaign`
337 passed. The frozen pathspec over `e4fc6cbf..HEAD` and `e4fc6cbf..origin/main` prints 0 commits (12 over
`76270d6c..e4fc6cbf`); the nothing-moves diff over `e4fc6cbf..HEAD` is empty, and `fd9eef64..HEAD` touches nothing
under `replays/`, `audits/` or `docs/`. The house gate (memo 8.7 item 1): CI run 37932710107 at `368109f7`,
success: Project checks 10,862 passed, 40 skipped, 3 xfailed, 0 failed (10,850 before, plus the re-scoped case and
the eleven new cases); Frontend checks and Frontend e2e passed. The run at the head carrying this section is cited in
the pull request.

**The step (ruling 2) is not written here.** The orchestrator's text for the audit's section 11 is to be written
verbatim only if nothing in the audit's readings contradicts it. Every reading it names reproduces from sections 6 to
8, except two phrases, which do not read as section 7.2 states them: "one sitting of 3.34 h" (7.2: the sitting ran
07:59:44Z to 11:32:31Z, 3 h 32 min 47 s; 3.34 h is the recording wall summed over the eleven legs) and "the spend at
54 to 57 percent of each ceiling" (7.2: calls 54.4%, input 55.2% and output 56.8% of their ceilings, the recording
wall 27.8% of its 12 h). The text is not edited and the section is not written; the question is the orchestrator's,
and the pull request stays a draft until the step is written.

### The step taken (2026-10-09)

The orchestrator took the step the rule names, under decision memo 8.8: round 3 is promoted as the shown set by the
era-keyed path, in one card with the tour's re-curation, keeping round 2's bytes as a candidate copy. The decision
and the readings it rests on are audit section 11; the one stop (audit 7.5) was resolved by the test-only re-scope
recorded in review round 1 above, with CI green at `368109f7` (run 37932710107) and `002bb56b` (run 37935832774);
the gate record is CI's green run at the pull request's head, cited by run id in its body (review round 2 below:
the run at `13370e5c` itself was red on a stale `docs/artifacts.md` row). Nothing here moves a recorded byte.

### Review corrections, round 2 (2026-10-09)

Three lenses over `13370e5c` (the whole record, the re-scope and the orchestrator's step) returned seven blocking
findings, three defects; Codex reviewed the same commit with four comments. The orchestrator's round-2 dispatch
assigns each repair, including two outside a fix round's audit text, card and pull request body: `docs/artifacts.md`,
whose two rows this card re-derives as the file's last writer in the round, and the route-lines card's test file, as
it assigned `368109f7`. No recorded byte, no production code and no text of section 11 moved.

1. *The `audits/` row of `docs/artifacts.md` is stale* (the correctness, integrity and documentation lenses; Codex
   4230751203). `13370e5c` appended section 11 to the audit (138,669 bytes at `002bb56b`, 141,218 at `13370e5c`)
   and left the row at 31,571,362, the `32b96529` value; offline `verify_ml_evidence.py` exited 1 (the in-tree family
   inventory) and CI run 37937850895 at `13370e5c` read Project checks 2 failed
   (`test_main_runs_the_cheap_legs_green_at_head`, `test_every_counted_registry_row_matches_the_index`), 10,860 passed.
   `6b014cba` (`docs:`) re-derives the row from `git ls-tree -r -l 13370e5c audits`: 31,573,911 tracked bytes / 335
   files; `08362561` re-derives it again for its index edit (finding 3): 31,574,099 / 335, the sum of
   `git ls-files audits` sizes at the head. Offline `uv run python scripts/verify_ml_evidence.py` (never
   `--complete`): exit 0 at both, 64 checks, OK 52, FAIL 0, ABSENT 7, INFO 5; `uv run pytest
   tests/scripts/test_verify_ml_evidence.py -n 6`: 90 passed.
2. *Two survivors of the class a loaded source read replaced by its literal* (the correctness and integrity lenses).
   In `_declared_configs_recording_the_field_on`, the sha256 of the loaded config bytes replaced by round 3's literal
   line and the declared set name replaced by the literal `9p2i` each survived every plant, since every plant held
   round 3's 342 bytes and declared only `9p2i`; memo 8.7 item 2 keeps that class blocking. `93ecd5f8` (`test:`,
   test-only) adds four plants to the ten: "holds on bytes it does not declare" (the round's config holds other ON
   bytes, the field's key first, while its declaration names round 3's bytes: the config is listed); "declares the
   other on bytes it holds" (nothing listed); "declares another set" (the round declares `4p1i seeds 0-1`, recorded
   ON under `4p1i`: nothing listed); "a second set recorded off" (`9p2i seeds 0-1` and `4p1i seeds 0-0`, the `4p1i`
   seed recorded OFF: the config is listed). The helper, the committed case and every other test are unchanged.
   *Mutation probe* (scratch, 18 mutants over the helper and the listing it feeds, run by
   `pytest tests/meetings/test_route_lines_arm.py -k "declared_round or walk_refuses or every_committed_payload"`,
   the file restored after): 13 killed, both survivors among them (2 failed each), and the walk narrowed to the
   first declared set (killed by the second-set plant). Five survive, each equivalent: the file name in the compared
   line made the literal `experiment-config.json` (the helper reads only that name); `== value` made `is not None`
   and the read value made the literal 1 (the field validates only to 1 or None,
   `test_a_value_other_than_one_or_none_is_refused`, and an OFF file is never listed whether or not it is left out);
   the `value is None` skip dropped (the same reason); `blocks[0]` made `blocks[-1]` (exactly one block is required
   on the line before).
3. *The card, the gate record and the pull request body did not match the head* (the integrity and documentation
   lenses; Codex 4230751225 on the audit index). The step subsection said the stop was resolved "with CI green at
   the head" while the run at `13370e5c` failed; the pull request body cited run 37935832774 (head `002bb56b`) as the
   head's run and still said the step was not written and the pull request stayed a draft; the index row said the
   audit gives no verdict and that the step is taken, with section 11 already written. The step subsection now names
   the green runs at `368109f7` and `002bb56b` and leaves the head's run to the pull request body; `08362561` makes
   the index row say its readings give no verdict and that its dated section 11 records the step (round 3 to be
   promoted by a later card, which the orchestrator merges; the shown set stays `replays/samples/9p2i` until then),
   with `copy_problems` 0 and the identifier scan 0 on its prose; the pull request body cites the green run at its
   pushed head by id and marks its draft and step-not-written statements superseded by `13370e5c`.

*Codex comments refuted, not edited.* 4230751212 (the MANIFEST's `git_sha` orphaned if the record lands squashed):
the comment reviewed a squashed commit (`7471688`, whose one parent is `9775c9d6`); this record is delivered by merge
commit or fast-forward, never a squash (`AGENTS.md` Delivery, this card's Constraints), a procedure the merger
follows, since the repository's settings allow a squash; `git merge-base --is-ancestor 641b4254 HEAD` exits 0, so a
merge keeps P and every checkpoint on `main`. 4230751233 (the card's `Status: ready`): the Status line and
`tasks/README.md`'s inventory sentence are the orchestrator's on `main` (`AGENTS.md`, this card's Constraints), so
they are not edited here; dispatch reads `tasks/README.md`, whose active ownership the orchestrator keeps.

*Superseded statements, kept as dated history.* Phase 2's "The stop (open)" paragraph, its Limitations' "The CI gate
at the head is red until the stop is resolved", its Decision 8's "the stop keeps the card from being done", and
round 1's "The step (ruling 2) is not written here" with its "the pull request stays a draft until the step is
written": the stop was resolved by `368109f7`, the step was written by `13370e5c` (audit section 11), and the pull
request is ready. Audit 7.5 and the menu's last bullet are history of the same kind; section 11 records the
resolution, so the audit file does not move.

*Gates at this section's commit* (bare shell, `env | grep -c '^AILIBI_'` 0, count-only): the route-lines arm, field
and instrument suites, `tests/scripts/test_candidate_sets.py`, `tests/eval/test_gameplay_census.py`,
`tests/scripts/test_verify_ml_evidence.py`, `tests/scripts/test_check_doc_facts.py` and the arms and config suites,
1,442 passed, 0 failed; the golden `-k "retired_guard or stage-b-r3"`, 12 passed; `check_doc_facts.py`,
`validate_task_docs.py` and offline `verify_ml_evidence.py`, exit 0 each; the frozen pathspec over `e4fc6cbf..HEAD`
and `e4fc6cbf..origin/main`, 0 commits; the nothing-moves diff over `e4fc6cbf..HEAD`, empty; `13370e5c..HEAD`
touches only `docs/artifacts.md`, `audits/README.md`, `tests/meetings/test_route_lines_arm.py` and this card. The
house gate (memo 8.7 item 1) is CI's green run at the pull request's head, cited by run id in its body; this card
cannot name the run of the commit that carries it.
