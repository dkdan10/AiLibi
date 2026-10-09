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

- [ ] **The pre-registration and the owner's confirmation precede the first seed, and neither is rewritten.**
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
- [ ] **The before columns are computed, never typed.** Mechanism: at F the census and scorecard `--set-dir R2
  --json-stdout` equal the shipped `samples/9p2i` entries leaf for leaf; on R1 and R2 the readings command prints
  every round-1 and round-2 count round 2's audit section 6 and Evidence state, 0 differing; the instrument's r1 and
  r2 columns at F equal the committed JSON's (M, W and each reach). A moved count stops the card. Proof: each
  comparison against a copy with one cell edited prints that cell and exits 1.
- [ ] **The readings are pre-registered in three columns.** Mechanism: `readings.py CENSUS HONESTY ROUTE --column
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
  | held data | `holds_nothing_skips_naming_no_candidate` (table `holds_nothing_skips_naming_a_candidate_by_source`); `cited_lines_true_to_the_route`, `cited_lines_false_to_the_route` (tables `cited_placements_by_kind_and_verdict`, `supported_ejects_not_checkable_by_reason`) | 0/256 at authoring; measured at F | 0/214 at authoring; measured at F | reported, each beside its definition |
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
- [ ] **The reporter flag is re-keyed, with a proposed bar and its alternatives.** Mechanism: `readings.py` reads
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
- [ ] **The step rule after round 3 is pre-registered, reads no reporter line and no role-correct figure, and is the
  owner's to take or override.** Mechanism: `readings.py --step` prints one line by this sentence, carried whole:

  > **The step rule after round 3.** With every Conf. cell at 0, round 3's point share of impostor wins neither above
  > 0.60 nor below 0.20, and round 3's misjudged route cases (the route-check replay's M) at or below round 2's 40,
  > it names the era-keyed promotion of round 3 as the shown set; otherwise it names round 2 staying shown, with
  > round 3 kept as a comparison record. Either step is the owner's to take or override.

  The rule gates no acceptance item. The witness subset, the reach of each check and M per ejection are printed
  beside M and not read. Proof: the planted copies of the readings item.
- [ ] **The preflight holds at F.** Mechanism: `CFG`, read by `scripts/_declared_experiment.py`'s loader, validates
  as a `RecordedExperimentConfig` whose non-default fields are round 2's nine and the route field;
  `OMITTED_AT_DEFAULT` holds it; `engine_arguments` returns round 2's keywords unchanged; `prompt_versions_for_set`
  serves the four stamps; `self_report` is False, `evidence_reasoning_version` and `contextual_self_report_version`
  None, the slate bare. The instrument takes `r3`; the held-data and route cells exist under their cards' keys.
  Proof: an unknown key is refused (`extra_forbidden`); without the route key the bytes equal R2's declared file;
  the field card's refusals (an env switch, an unthreaded reader) pass at F, named by test id.
- [ ] **The fake dress rehearsal passes every instrument at F, at $0, and shows the field inert.** Mechanism: seeds
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
- [ ] **The scripted rehearsal and the lab still hold at F, and the field is served.** Mechanism: the field card's
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
- [ ] **The dry run and the probe pass before any batch.** Mechanism: the dry run echoes P's sha256, the ten fields
  and the bare slate, with `git status --porcelain --untracked-files=no` at 0 lines. The probe records seeds 0-1 as
  one leg on two workers; the probe's gates (Constraints) run before any batch. Seeds 0-1 with no meeting or no
  served route line extend by seeds 2-3 only; seeds 0-3 with a ballot and no served route line stop the card.
  Proof: the dry run with a stray `AILIBI_BOUNDED_REBUTTAL=1` exits 1.
- [ ] **The round is exactly the declaration, and every Conf. cell reads 0.** Mechanism: the validity gate on C
  passes its ten checks, named, with `--expected-model Qwen/Qwen3.6-27B --require-zero-cost`, the four
  `--expected-prompt-versions` pairs, `--expected-experiment-config CFG`, `--expected-seeds 0-49` and
  `--require-one-recording-sha`; the MANIFEST's flags column equals R2's and its policy column reads
  `fsm-default`; `grep -l deadline_default` counts 0; the census `--set-dir C` exits 0 (non-zero names set, seed,
  meeting on a breach), the route cells included; the golden reproduces every call. Proof: the gate with
  `--expected-seeds 0-50` fails; R2 against `CFG` fails `cost_and_provenance_exact`; the census card's planted
  breaches (its route conformance cases among them) and the field card's pass at F, named by test id.
- [ ] **The spend stays inside the ceilings.** Mechanism: the tally counts C's `llm_calls`; `reproject.py` applies
  Constraints' re-projection, exiting 1 with a STOP line past a 90% stop. Proof (at `76270d6c`): the tally prints
  `1502 9187880 418270 0.0` on R2 and `1556 9344346 433660 0.0` on R1; on a scratch copy of R1's seeds 0-11 with
  4,000 s of wall it projects 1,619 calls, 9,978,176 input, 470,463 output and 4.63 h and exits 0; with 50,000 output
  tokens added to one call it projects 677,314 output and exits 1 on output; with 9,400 s of wall it projects
  10.88 h and exits 1 on wall (all three re-run at authoring with the `reproject.py` Validation quotes).
- [ ] **The checkout never moves, a pause strands nothing, no key leaves, and the freeze held.** Mechanism: seeds
  record in a checkout detached at P, in batches, each ending in a count-only key scan (gzip decompressed) and a
  pushed `record:` checkpoint, the gates running after the probe and after every second batch (the owner's process
  amendment of 2026-10-09, decision memo 8.7); `git log --oneline F..HEAD` and `F..origin/main` print nothing over the frozen
  pathspec. Proof: the MANIFEST names one `git_sha`; each scan pattern fires on its planted key; with a planted pause
  file and the recorder replaced by `true` no batch starts; the pathspec over `76270d6c..F` is non-empty.
- [ ] **The derived views and the registration are rebuilt, never hand-edited.** Mechanism: the recorder's
  post-step writes the report through `eval/report_io.py` and `build_sample_report.py --sample-dir C --check`
  passes; the round README's `candidate-declaration` block holds the sha256 line and `9p2i seeds 0-49`; the two
  `docs/artifacts.md` rows are re-derived with `git ls-files` (111 files under `replays/candidates/`) and offline
  `verify_ml_evidence.py` reads OK; the golden's `candidates/stage-b-r3/9p2i` row is what its production walk
  measures on C. Proof: the candidate test's planted perturbations pass; without the row the golden raises `KeyError`.
- [ ] **The assessment is written as pre-registered.** Mechanism: round 3's column comes only from the census and
  scorecard `--set-dir C --json-stdout`, `measure_baseline.py C --honesty --json`, the gate's betrayal check and the
  instrument run at the delivery head with r1, r2 and r3 columns into scratch, through `readings.py`. Order: the
  process cells; each Conf. cell and carried reading; the route cells; the cooldown cell; the envelope and the flag;
  the route-check count; the step the rule names; the reported rows; role-correct ejection, the balance and the win
  split, gating nothing. The menu: the step; for the route field, adopt by the era-keyed promotion, iterate under a
  new value, or keep round 2 shown; Conf. cells only for the other nine fields; with the promotion, its card's
  follow-ups (a public-results label for the route field, which `frontend/src/components/PublicResults.tsx` cannot
  name today; the era registry entry; the pin sweep). Proof: pooling C with R2 or R1 raises the census era refusal.
- [ ] **Nothing publishes, nothing committed moves, and the copy is plain.** Mechanism: `git diff --stat F..HEAD`
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
      "holds_nothing_skips_naming_a_candidate_by_source")
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

Filled at delivery: the commits and checkouts (F, P, Q, each checkpoint), the rulings and confirmation verbatim, each
command's real exit code, the three columns, the flag, the route-check count, the step the rule names, the sections
relied on (this card; round 2's audit 1 and 6; `docs/architecture.md`; `docs/experiment-arms.md`), decisions and limits.
