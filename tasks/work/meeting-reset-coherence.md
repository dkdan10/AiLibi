# B2: the full meeting reset, coherent for agents and instruments

**Status:** done

## Outcome

The existing `meeting_reset = "hub_with_grace"` arm is the full reset the owner ruled; no engine line changes.
At a meeting's close it gathers the living players in the meeting room, clears every corpse, empties the vents,
stops ongoing actions and restarts each living impostor's kill cooldown at the map's value (4). Tasks, sabotage
and button uses survive. This card makes what agents perceive, and what instruments measure, agree with that
reset, so the round-1 candidate records no false perception and no unexplained teleport. Every fix keys on the
recorded arm or on the public regroup row it produces, so each is byte-neutral on `preserve`:

1. **Resume perception.** One shared helper composes the resume tick's events. After a regroup it keeps only
   kill and vent events and reports what it dropped.
2. **Own-completion placement.** A task finished on the trigger tick is placed where it was done, not in the
   meeting room.
3. **The regroup notice on the default evidence path.** The existing line also renders when evidence
   reasoning is off. Version 1 stays excluded.
4. **A symmetric regroup relevance window.** A regroup tick and the tick after it carry no alibi evidence,
   whether they would corroborate an alibi or prosecute one (`alibi_vs_sighting`). Their sightings stay out
   of the ballot's own-evidence rows.
5. **Legible memory.** The regroup co-presence folds into one line; the self-location trail marks the regroup.
6. **Every reader follows:** game, replay helpers, loader, walk, funnel, evidence honesty, scorecard, the
   phase-20 counterfactual, transcript detectors, manager, corroboration and agent memory.

`eval/off_menu.py` is not edited: it is FROZEN and keeps refusing experiment recordings. No viewer file is
edited this wave. The arm stays default-OFF; only the record card records it ON, into the candidate directory.
This card carries out the owner's full-reset ruling, and so it supersedes the direction's section-9 deferral of
the body-freshness band and cleanup decision A-28.

## Evidence

Every `path:line` below is a citation at `e886b663`, labelled by its symbol; the implementer re-anchors each
by that symbol at dispatch. Sources, in `~/.claude/projects/-Users-danielkeinan-projects-AiLibi/`:
`stage-b-2026-09-24/decision-memo.md` (sections 0, 1, 2.3, 3.1, 3.2, 3.4 card 9 and 4),
`stage-b-2026-09-24/meeting_reset_full.md` (sections 1, 2.2 to 2.9, 4 and 5) and, for the planted tests,
Part 3 B2 of `analysis-2026-09-24/analysis-memo.md`.

**The owner's rulings of 2026-09-24, verbatim.** Ruling 1: "We should implement stage B". Ruling 3: "B2. full
reset." Ruling 11: "Tour fix can be deferred to after gameplay is finished". Ruling 12: "Hold off on ML as D
suggests until gameplay is finished." The record paragraph: "Let's not re-record all 300 seeds each time. When
it's time to record, record the smaller group of 50 seeds, assess if the implementations have been effective
and resulted in desired results. Also it is understood that updating the vent and body reset logic will
probably have a substantial effect on previous limits and statistics around the baseline voting results, that
is okay."

**The orchestrator's rulings, made under the owner's delegation of 2026-09-24.**
- Decision memo 2.3: "Record on the existing arm with no engine change". "Sabotage surviving the reset is
  documented, not changed." It also accepts the fold and trail marker, the symmetric window, the own-row
  exclusion, the priced resume loss and full caller threading.
- Decision 0.3 item 8 signs off Outcome items 3 and 4 (the memo's fixes 3 and 5): "Both are new prompt bytes
  and a detector change beyond the literal words "full reset". They are signed off here as material decisions
  and must be recorded as such in the B2 card." The reason: "without them, the recorded reset writes false
  perceptions and unexplained teleports into every post-meeting prompt, which is a defect, not an experiment."
- Decision 0.3 item 6: "Once round 1 is recorded, an arm value's meaning is frozen." It applies to
  `hub_with_grace` too. Decision 0.3 item 10: off-menu and the other policy-rerunning or frozen instruments
  "keep refusing".
- R6: impostor self-report stays OFF, and the reset adds no impostor callers. R13: no scorecard cell. The spine
  lands the validator's refusals of evidence version 1, and of `post_meeting_retarget`, with the reset.
- The dated direction addendum (decision memo section 6) reads: "B2 ("full reset") supersedes section 9's
  deferral of the body-freshness band and cleanup decision A-28." The superseded texts are "**Defer:** body
  freshness band" (`tasks/direction-2026-09-19-process-over-outcome.md:307`, restated at `:396`) and the A-28
  row (`docs/cleanup-dispositions.md:46`).

**The reset as coded.** In `apply_meeting_result` the trigger corpse is deleted (`orchestrator/game.py:1901-1904`)
and the win check returns on a win (`:1910-1921`). Only then does `regroup_after_meeting` run (`:1923-1924`;
`engine/meeting_reset.py:10-41`), followed by one tick and RNG advance. It clears `in_vent` and `last_action`,
moves the living players to the meeting room, sets cooldowns to `kill_cooldown_ticks` (4,
`engine/maps/canonical_1.yaml:34`) and empties `bodies`. `resolve_kill` needs cooldown 0 (`engine/rules.py:82`),
and the decrement runs after each play tick's actions (`engine/tick.py:629`, `:665`). So after a meeting at
tick T, kills are illegal at T+1 to T+4 and first legal at T+5 (pinned for the helper at
`tests/engine/test_meeting_reset_experiment.py:17-88`, with a crew-win case at `:98-130`). The docstring at
`orchestrator/game.py:1821-1825` still says the meeting freezes the cooldown counters.

**What the arm gets wrong today.** Count-only scratch walks over baseline 9, quoted from `meeting_reset_full.md`
sections 2.2, 2.3 and 5 and decision memo 2.3. Re-measure them at dispatch with that memo's appendix scripts; no
acceptance item depends on a quoted count.

| on 9p2i (s9 + c9) unless marked | count |
|---|---|
| non-terminal resumes with at least one false perception, arm as coded | 149 of 452 (s9 41 of 107) |
| movement views the observer could not have seen / task sightings placed in the meeting room wrongly | 95 / 914 |
| own trigger-tick completions misplaced into the meeting room | 39 of 43 |
| trigger-tick views the resume filter will drop | 398 movement, 136 task |
| visible-player rows on s9, `preserve` against the regroup | 421 against 3,009 |

The mechanisms:
- **Resume events.** `HeadlessGame._run_loop` builds the resume packet from the post-meeting state plus the
  trigger tick's events (`orchestrator/game.py:2635`). `ReplayLoader._walk` (`api/replay_loader.py:1958`),
  `_walk_replay` (`eval/replay_walk.py:795`), off-menu (`eval/off_menu.py:540`) and the golden's
  `walk_replay_meetings` (`tests/meetings/test_prompt_byte_golden.py:753`) copy it. `ObservationService` gates
  movement and task sightings on the post-state (`observation/service.py:541-631`), so after a regroup they
  read the regrouped rooms; kills and vents are witness-gated at event time. Evidence honesty's `_perceive_tick`
  and the leak scan read the walk's `last_events`.
- **Own completions.** `_build_observations` places a completion at the room of the self-state row where the
  task left the owned set (`agents/memory/store.py:1917-1948`, `completion_room` at `:1925`). After a regroup
  that row is the resume row.
- **The notice.** `_run_and_apply_meeting` (`orchestrator/game.py:2832-2850`), `ReplayLoader._walk`
  (`api/replay_loader.py:1936-1954`) and policy reconstruction (`orchestrator/policy_reconstruction.py:164-172`)
  call `ingest_public_regroup`, which returns unless evidence is version 2
  (`agents/memory/evidence_context.py:207`). The line renders only under version 2
  (`agents/memory/store.py:704-709`). The round-1 record runs evidence None.
- **The relevance gate.** `is_relevant_sighting` excludes only the spawn window, ticks 0 and 1
  (`meetings/transcript.py:850-856`, `:1202`). It is called in `reconstruct_stated_paths` (`:1425`),
  `detect_corroborations` (`:2132`), `_carries_relevant_observation` (`:2368`), `grounded_vouch_subjects`
  (`:3763`) and `derive_belief_evidence` (`meetings/manager.py:4822`). `_detect_alibi_vs_sightings`
  (`meetings/transcript.py:3175`) never calls it.
- **The ballot's own rows.** `_own_channel_evidence_rows` makes each sighting record a class-0 `own_sighting`
  row (`meetings/manager.py:3500-3522`). `MAX_EVIDENCE_ROWS_PER_SUBJECT = 8` (`:3407`) drops the earliest
  arrivals of a (subject, class) group (`:3883-3888`), so regroup co-presence can push an early `own_vent` row
  out of the block.
- **Fold and trail.** `_spawn_group_indices` folds only tick-0 runs (`agents/memory/store.py:2146-2179`,
  `:2170`). The trail docstrings (`:540-543` in `render_for_prompt`, `:1521-1524` in
  `_collect_self_location_spans`) say a meeting freezes movement.
- **Instruments.** `walk_routes` keeps the trigger tick's post-advance rooms, never the regrouped frame
  (`eval/process_scorecard.py:812-830`); its convention census 955 / 104 / 103 / 2 (`:78`) is pinned. Evidence
  honesty's `room_at` table in `_fold_game` (`eval/evidence_honesty.py:1453-1456`) and `_assert_clock_alignment`
  (`:1719`) would reject honest post-regroup sightings; the readers card leaves the reset refused there by
  name, for this card to lift.

**Callers to thread** (a `git grep` over non-test Python at `e886b663`):
- `extract_belief_evidence`: `api/replay_loader.py:1883`, `eval/evidence_honesty.py:1366`, `eval/funnel.py:1298`,
  `scripts/counterfactual_phase20.py:526`, `orchestrator/game.py:3261` (`_absorb_meeting_beliefs`).
- `reconstruct_stated_paths`: `eval/funnel.py:1419`, `meetings/corroboration.py:648`, and inside
  `meetings/transcript.py` at `:1619`, `:1901` and `:1912`.
- `fold_meeting_outcome_into_memories` (`orchestrator/replay.py:1282`): `api/replay_loader.py:1933`,
  `eval/evidence_honesty.py:1380`, `scripts/counterfactual_phase20.py:543` and the golden (`:744`).
- Kept at the no-regroup default, because each refuses experiment recordings or reads only committed
  `preserve` bytes: `eval/off_menu.py:520` and `:540` (FROZEN at `:1-2`, refusal at `:359-361`),
  `training/anchor_study.py:645` and `training/surrogate/dataset.py:943` (ML held), and
  `experiments/lab/inference_testimony_probe.py:70` (FROZEN).

**What the reset does not zero.** Openings with an impostor in a vent (s9 29 of 145): 102 of 105 pooled in-vent
slots (s9 28 of 29) were entered after the previous meeting, and the reset runs at close, so B2 zeroes "in a
vent when play resumes" (s9 10 of 107), not the opening (decision memo 0.4). `EMERGENCY_COOLDOWN_TICKS = 6`
(`agents/tactical/crewmate_policy.py:109`) gates the suspicion walk, but the kill-witness walk to the button
(`:382-387`) is ungated, hence a cell for kill-witness button calls within 6 ticks of a regroup. Sabotage
survives: 8 of 594 9p2i meetings opened with an active reactor, 5 of them non-terminal with 5 or 6 ticks left.

**No committed recording stamps the arm.** `git grep -l '"meeting_reset"' -- '*.jsonl' | wc -l` gives 101 files
(100 in `audits/deduction-candidate/run-2026-09-16`, 1 in `tests/fixtures/v3_policy_reconstruction`), and
`git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl' | sort | uniq -c` gives 956 occurrences, all
`"preserve"`. No file under `replays/` carries the key. Count-only at `e886b663` on 2026-09-24; re-run at dispatch.

## Acceptance

- [x] Review correction: **the walk's resume phase read is pinned by a recorded meeting that ends the game**
  (round 5, correctness lens). A 5-player reset game whose first meeting ejects the only impostor is recorded
  through `HeadlessGame` with a replay path and walked through `eval.replay_walk` under the evidence-honesty and
  funnel profiles. Each walk completes with the terminal `MeetingApplied` (phase `GAME_OVER`, its game-over
  event last) and then `WalkComplete` at the meeting's tick
  (`test_a_recorded_meeting_that_ends_the_game_walks_to_its_terminal_meeting`). With the walk's resume phase
  read replaced by `"PLAY"` both cases are red (`M-WK-compose-phase`, round 5 below).
- [x] Review correction: **the regroup fold is stated at the strength the code delivers** (round 5, correctness
  lens). The fold renders on the default evidence path only. Evidence version 2 folds no sightings, the spawn
  group's included, so each regroup sighting keeps its own row there while the notice and the route step
  render. `docs/observation-contract.md`, this card's Decisions and Limitations and the PR body say so.
  `test_under_version_2_the_regroup_sightings_keep_their_own_rows` pins the version-2 render, and
  `test_only_version_2_leaves_the_spawn_group_unfolded` pins the gate on all three paths. The Constraints
  sentence the finding names is the orchestrator's to amend (the PR's Questions).
- [x] Review correction: **the four listed-class mutation survivors are killed** (round 4, correctness lens).
  Each is red under its mutant through a planted case: a hand-built `public_regroup` row that lists its players
  renders byte-identically to the tuple row (`test_a_public_row_listing_its_players_reads_as_the_tuple_row_does`);
  the malformed-row refusal quotes the payload it read (`test_the_malformed_row_refusal_quotes_the_payload_it_read`,
  four payloads); the manager's refusal names the ticks it was handed
  (`test_the_manager_refusal_names_the_ticks_it_was_handed`); and the resume helper's property now matches the
  meeting's event count (`test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest`). The mutation
  table is in round 4 below.
- [x] Review correction: **the phase-21 counterfactual refuses a reset recording by name** (round 4, Codex P2 and
  the documentation lens). `scripts/counterfactual_phase21.py::_refuse_the_meeting_reset` reads each recording's
  settings and raises, naming `meeting_reset='hub_with_grace'` and the seed, before the walk re-derives anything.
  It runs in the shared `_walk`, so both modes refuse. Proof in `tests/eval/test_regroup_instruments.py`:
  `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking`,
  `test_the_phase21_command_refuses_a_reset_set_staged_under_replays` (`main(["--sets", ...])`),
  `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` and the three controls of
  `test_the_phase21_refusal_names_the_reset_and_nothing_else`. Command: `uv run python
  scripts/counterfactual_phase21.py --sets <a fake reset set staged under replays/>` exits 1, naming the setting
  and seed 1000.
- [x] Review correction: **the stop-and-ask over the phase-21 counterfactual, and the Status** (round 4, the
  integrity lens). The equality box now holds at the strength it states: no production caller reads a reset
  recording at the no-regroup default, because this one refuses. The repair is the first of the findings' three
  options, forwarded by the orchestrator's round-4 dispatch with the instruction to repair each finding. It
  restores the script's outcome at the merge base, a named refusal and no table, where `compute_evidence_honesty`
  refused a reset recording after the walk; the refusal now comes before it. The file is outside the decision
  memo's 3.2 map, and no Stage-B card writes it. The PR's Questions
  asks the orchestrator to confirm the disposition and to record the map row, as `cb0a4cfc` did for the three
  readers.
- [x] Review correction: **the round-3 test counts are corrected** (round 4, documentation lens): 14 new
  instrument tests, 26 already in the file, and 16 added in total. Command: `uv run pytest --collect-only -q
  tests/eval/test_regroup_instruments.py` collects 26 items at `1ad1b57c` and 40 at `711e488f`.
- [x] Review correction: **the three readers the stop-and-ask named, resolved by the orchestrator's ruling of
  2026-09-27.** `eval/meeting_quality.py` reads the regroup window in `_ejected_in_inform_band` through
  `_regroup_ticks_before` (the one derivation, `orchestrator.replay.derive_regroup_ticks`);
  `eval/vj_instruments.py` passes each walked meeting's `regroup_ticks` to its pre-vote derivation; the FROZEN
  `eval/deception_instruments.py` refuses a `hub_with_grace` recording by name and seed before its walk and
  changes no evidence semantics. Proof, in `tests/eval/test_regroup_instruments.py`:
  `test_the_inform_band_reads_the_window_each_live_meeting_ran_with`,
  `test_a_voice_resting_on_a_regroup_sighting_informs_nobody` against
  `test_with_the_window_withheld_the_same_fold_credits_the_inform` and
  `test_the_preserve_twin_of_the_planted_game_folds_as_before`;
  `test_the_vj_pre_vote_fold_reads_each_meetings_window` and
  `test_a_regroup_sighting_lifts_no_row_in_the_vj_pre_vote_graphs`;
  `test_the_deception_instruments_refuse_the_reset_by_name_before_walking`,
  `test_a_set_with_one_reset_recording_is_refused_at_that_seed` and
  `test_the_deception_refusal_names_the_reset_and_nothing_else`. Commands: `build_sample_report.py` on a fake
  `hub_with_grace` set, and the four committed `--check` runs.
- [x] Review correction: **`main` merged and the body-handle hand-off written.** `main` at `cb0a4cfc` (B1, B4
  and the one-writer amendment) is merged in `1ad1b57c`, never rebased. `docs/observation-contract.md` names
  `report_body_handle_version = 1` and what it changes
  (`test_the_contract_names_the_recorded_body_handle_setting`, planted
  `test_the_paragraph_before_the_setting_fails_the_body_handle_check`). Every Validation gate is re-run at
  `6fb328a8` and `check.sh` at the head (round 3 below).
- [x] **The reset at the orchestrator entry.** Mechanism: the arm-gated `regroup_after_meeting` call in
  `apply_meeting_result`. The fixture is a MEETING state with the trigger corpse, two unreported corpses, an
  impostor in a vent with cooldown 0, an active reactor with repair progress, and used button presses. Under
  the arm the result has no corpses, nobody in a vent, the impostor at the map's `kill_cooldown_ticks` (4) and
  every living player in the meeting room. Tasks, sabotage, emergency uses and alive flags are unchanged; the
  tick is +1 and the RNG advanced once. Planted proof: the same assertions fail on the `preserve` twin, which
  keeps the two unreported corpses, the vent and cooldown 0 and loses only the trigger corpse.
  `git diff --stat <merge-base> -- engine/` is empty.
- [x] **Order and openings.** Mechanism: the win check returns before the regroup call; a button names no body.
  - An impostor-parity win at the meeting (a crewmate ejection that reaches parity) ends before any reset,
    beside the existing crew-win case.
  - A button meeting under the arm with an unreported corpse on the floor: the description names no body,
    `_assert_no_emergency_opening_body` passes, the corpse is gone after the close, and the victim is in
    `dead_ids` at the next meeting.
  - Planted proof: moving the regroup call above the win check fails the parity case, and a `found_body`
    emergency opening still raises.
- [x] **The grace window, end to end.** Mechanism: the cooldown the regroup sets, read from the map. A kill
  through `apply_meeting_result` and `advance_tick` is rejected at T+1 to T+4 after a regroup at meeting tick T
  and succeeds at T+5. A1's census window for that meeting, read through its write-nothing `--set-dir` fold, is
  T+1 to T+4. Planted proof: under `preserve` with cooldown 0 at the meeting, the same kill succeeds at T+1;
  a carrier with the kill moved to T+4 raises the census breach.
- [x] **Resume perception, one helper.** Mechanism: one helper in `orchestrator/replay.py` composes the resume
  events, with a keyword-only regroup flag that defaults to no regroup. After a regroup it keeps `KilledEvent`,
  `VentEnteredEvent` and `VentExitedEvent`, drops the rest, and returns the dropped movement and task events by
  kind. It is called at `orchestrator/game.py:2635`, `api/replay_loader.py:1958`, `eval/replay_walk.py:795` and
  the golden (`:753`); evidence honesty and the leak scan inherit it through the walk.
  - Fixture: on the trigger tick before a report, one crewmate leaves the meeting room, another does a task
    step in MEDBAY, and an impostor vents in view of a third. Under the arm no observer gets a movement view or
    a meeting-room task sighting for the first two, and the vent witness still gets the vent.
  - Planted proof: removing the filter fails the test, and a helper that also drops `KilledEvent` fails a
    kill-witness case. The `preserve` twin still delivers the MEDBAY task sighting to the MEDBAY observer.
- [x] **Own-completion placement.** Mechanism: a completion detected across a public regroup row takes the
  previous self-state row's room (a `do_task` tick is never a move tick). A trigger-tick completion in LABS
  renders "(you were in LABS)" under the arm. Planted proof: reverting the placement renders the meeting room.
  The `preserve` render is byte-identical.
- [x] **The regroup notice on the default path** (signed-off decision 1).
  - Mechanism: `ingest_public_regroup` ingests under evidence None as well as version 2, and still returns
    under version 1. The existing line renders whenever a public row exists and the version is not 1.
  - The ingestion moves into `fold_meeting_outcome_into_memories` behind a keyword-only regroup argument, so
    the live loop, the loader, the golden, evidence honesty and the counterfactual share one home. Policy
    reconstruction's direct call routes through it, or Results names that call as unchanged and idempotent.
  - Test: under the arm with evidence None, the second meeting's rendered memory carries the line, and the
    loader's `get_meeting_memory` text equals the live prompt's memory block.
  - Planted proof: removing the ingestion from the fold fails both. `preserve` renders no line, and an
    evidence-version-1 memory ingests nothing.
- [x] **Legible memory: the fold and the trail marker.** Mechanism: under a public regroup row,
  `_spawn_group_indices` and its caller also fold runs that begin at the regroup tick when they name every other
  living player in the row's `player_ids`, all in the meeting room. The trail renders the regroup as its own
  step, in the notice's words. The two freeze docstrings and `apply_meeting_result`'s name the reset.
  - A planted 9-player regroup renders one fold line where it rendered eight rows; a partial view (one player
    unseen) keeps its rows. Under the arm, memory rendered with the public row differs from memory rendered
    without it only in the notice line, the fold line and the trail step.
  - Planted proof: removing the fold extension restores eight rows, and removing the marker restores the bare
    arrow. The golden keeps `preserve` byte-identical.
- [x] **The symmetric regroup window** (signed-off decision 2).
  - Mechanism: one function beside the resume helper derives the regroup ticks R from the recorded config and
    the meeting rows. R is the resume tick (meeting tick + 1), as the public row records it
    (`tests/orchestrator/test_public_regroup_evidence.py:68-75` pins meetings at 2 and 6 against regroups at 3
    and 7). The orchestrator passes the ticks to `MeetingManager.run` beside `dead_ids`; they are public
    knowledge and never become a field of a recorded schema. `is_relevant_sighting` gains a keyword-only
    `regroup_ticks` argument, empty by default, and excludes R and R+1. `_detect_alibi_vs_sightings` excludes
    the same sightings from prosecution.
  - Tests: a co-presence sighting at R, or at R+1, does not corroborate; with no regroup ticks it does. An
    envelope alibi spanning a regroup, contradicted only by a sighting at R, mints no flag; with no regroup
    ticks it does. The spawn window is unchanged.
  - Planted proof: each case fails with the exclusion removed.
- [x] **Regroup sightings stay out of the ballot's own rows.** Mechanism: `_own_channel_evidence_rows` skips
  sighting records at R or R+1; the spawn-window rows are unchanged, because changing them would move
  `preserve` bytes. Planted test: a voter holds an `own_vent` row for subject X at tick 5, seven ordinary
  sightings of X after tick 5, and co-presence sightings of X at R and R+1. The `own_vent` row survives the
  8-row budget. Removing the exclusion drops it and fails the test.
- [x] **Full caller threading, proved by equality.** Mechanism: the regroup ticks and the resume helper reach
  every production caller that can read a reset recording: the live meeting run and its detectors, the vouch
  gate in `derive_belief_evidence`, every caller listed in Evidence (including `meetings/corroboration.py:648`),
  and `agents/memory` through the public row. `scripts/counterfactual_phase20.py` (`:526`, `:543`, `:781`) is
  threaded, or keeps the named refusal the readers card gave it; Results says which.
  - Fixture: one fake-provider arm-ON game (`HeadlessGame` from a declared config, no environment variable)
    recorded into `tmp_path`; the test asserts at least two non-terminal meetings. At each meeting open, four
    readings agree: the live agents' beliefs and rendered memory, the `ReplayLoader` reconstruction, the golden
    walker (every prompt byte-equal) and the evidence-honesty walk.
  - Planted proof, parametrised over the threaded sites: withholding the regroup ticks, or the resume helper,
    at any one site fails the test.
- [x] **Instruments and the viewer data layer.**
  - `walk_routes` takes a meeting tick's room table from `MeetingApplied.state`. Under the arm a resume-tick
    self-claim naming the meeting room scores true. Planted proof: reverted, it scores false.
  - Evidence honesty walks a reset fixture, and its `room_at` table and clock alignment pass. Planted proof:
    reverted, the alignment raises.
  - Each `meeting_reset` refusal the readers card named as pending this card (read from that PR's Decisions) is
    lifted, and only with its fix. Planted proof: every other field that card refused is still refused.
  - The loader's first post-meeting `TickView.bodies` is `()` under the arm, and the `preserve` twin shows the
    unreported corpse. This covers the analysis memo's "no corpse after a meeting" without a frontend edit.
- [x] **The `process-scorecard` walk profile declares its layers.** Mechanism: the profile
  (`eval/process_scorecard.py:787`) sets the spine's `threaded_layers` to the layers the scorecard
  reads, named in Results; the spine names this card as its owner. Proof: it reads the spine's fake
  full-config recording (a copy of a fake recording on today's arms, its tick rows and footer
  rewritten to carry every wave field at its ON value, with the pending set patched empty) with
  every hash verified, and it refuses a planted unknown field (a stand-in added to the config model
  and `FIELD_LAYER` in a layer the profile does not declare) by name before its first advance.
  Perturbed: the profile with its layer declaration removed refuses the full-config copy. The
  record card's scorecard `--set-dir` on the candidate walks this profile.
- [x] **The census, end to end** (in this card's own test file). Mechanism: A1's conformance cells whose arm
  predicate is `meeting_reset == "hub_with_grace"`, folded through its `--set-dir` path. The fake arm-ON game
  reads 0 on stale reports, on play resuming with an impostor in a vent or with a corpse, and on kills in the
  grace window. Its trigger-tick discard count equals the sum of the resume helper's dropped counts. It reads a
  count, not `n/a`, on trips closed by a regroup and on sabotage active at a regroup. Every living agent holds
  exactly one `public_regroup` row per non-terminal regroup.
  - A kill-witness button call within 6 ticks of a regroup is counted. The case comes from a count-only scan of
    fake arm-ON development games (seeds 1000-1007), or failing that from a carrier built from this game's walk
    with the call inserted; Results names which.
  - Planted proof: a perturbed carrier with one corpse restored at a resume raises that cell's breach, and so
    does one with a kill moved to T+4. B5's conformance stops on corpses, vents and grace kills rely on this.
- [x] **The OFF path, the c9 and c4 derivations and the demo bundle are byte-identical.** Mechanism: every fix
  keys on the recorded arm or on a public regroup row, and no committed recording holds either. At the branch
  head: `verify_samples` once per set directory for all four sets; the four `build_sample_report --check` runs;
  the golden on s9 and s4; `publish_process_scorecard --check` (the 955 / 104 / 103 / 2 census cannot move);
  `publish_gameplay_census --check`; and `uv run pytest -m campaign` for the campaign-tier half of the c9 refit
  pins. The demo bundle reads `api/replay_loader.py`, so `scripts/build_demo_bundle.py` at the merge base and
  at the head gives an empty `diff -r` of the two `data/` trees, and `npm --prefix frontend test` and the
  Playwright journey pass. Planted proof: applying the resume filter under `preserve` turns the golden and the
  census `--check` red; Results names both failures.
- [x] **The documents, and the copy.**
  - `docs/observation-contract.md` states the resume rule (after a regroup the resume packet carries only the
    trigger tick's kills and vents) and the default-path ingestion of the public row. It also takes the
    body-handle card's hand-off: the sentence at `:35-38` names the recorded body-handle setting.
  - `docs/glossary.md` gains "regroup": what moves, what is cleared, and that tasks, button uses and an active
    sabotage survive. `docs/cleanup-dispositions.md` A-28 gains one line: superseded by the owner's full-reset
    ruling, pointing at the direction addendum. `audits/tactical-gameplay/README.md` gains a dated note that
    its reset row measured the arm before these fixes.
  - Mechanism: a test asserts that the contract and the glossary name each event kind in the helper's keep-set
    (read from the helper's constant) and that the glossary has a "regroup" heading. A copy test scans the new
    model-facing strings (notice, fold, trail step) and the glossary entry for task, audit and card
    identifiers and for arithmetic.
  - Planted proof: an event kind added to the keep-set without the documents fails the first test, and a
    planted identifier fails the copy test.
- [x] **The registry row follows the audit bytes.** This card edits `audits/tactical-gameplay/README.md`, so
  the `audits/` row of `docs/artifacts.md` (`:109`, 26,635,440 tracked bytes / 329 files at `e886b663`, moved
  since by earlier cards) is recomputed with `git ls-files` as the last step, after the final merge of `main`.
  Mechanism: `test_every_counted_registry_row_matches_the_index` (`tests/scripts/test_verify_ml_evidence.py`,
  run by `check.sh`) and the offline `scripts/verify_ml_evidence.py`. Perturbed: with the row left stale after
  the README note, that test fails; Results quotes the red run.

## Constraints

**The partial-record principle binds this card.**
- Only `replays/samples/9p2i`'s seeds 0-49 are ever re-recorded, only into `replays/candidates/stage-b-r1/9p2i/`,
  and only by the record card. This card records nothing.
- Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted at its default. This card adds none:
  it gives the existing `meeting_reset` value its coherent meaning, and does not touch
  `orchestrator/experiment_config.py` (`hub_with_grace` is not in `WAVE_ARMS_PENDING`).
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying byte-identically. No
  registry prompt bump and no template change.
- Role-correctness is reported and never a gate; the B2 outcome cells are reported only. Nothing pushes an agent
  toward the correct answer: the notice, fold and trail step state a public relocation.
- The meeting layer labels and never rewrites: the window marks relevance, an excluded sighting stays in the
  voter's memory block, and no transcript turn is altered.

**Wave, order and prerequisites.** Wave 3, card 9 of the decision memo's section 3.1.
- Starts after `tasks/work/stage-b-readers.md` has merged, which follows `tasks/work/stage-b-arm-spine.md`, which
  follows `tasks/work/docs-truth-typed-trigger.md`. `tasks/work/gameplay-census.md` and
  `tasks/work/vent-witness-physical.md` are on `main` first.
- Runs in parallel with `tasks/work/vent-look-and-wait.md` (B1) and `tasks/work/report-body-handle.md` (B4), and
  merges after both. Merges before `tasks/work/ballot-kill-row-and-impostor-strategy.md` (B6), which starts only
  once this card has merged; `tasks/work/stage-b-record-r1.md` records last.
- The dated direction addendum is on `main` (the `docs:` commit before wave 1); if it is not, stop and ask.
  Every merge is the owner's.

**Shared files, one writer at a time** (decision memo 3.2).
- `orchestrator/game.py` is region-owned. This card's regions: the resume composition in `_run_loop` (`:2635`),
  the regroup ticks passed to `MeetingManager.run` (near `:1283`), the regroup ingestion in
  `_run_and_apply_meeting` (`:2832-2850`), the belief call in `_absorb_meeting_beliefs` (`:3261`) and the
  `apply_meeting_result` docstring (`:1821-1825`). Not `_build_meeting_trigger` (A3's construction, the
  spine's keyword, B4's body), the live tick or the runner construction (spine), or B6's protocol,
  participants and accessor. B4 merges first. Where the memo says "B2 rebases", this card merges `main` into
  its branch and never rebases.
- Serial, in order: `meetings/manager.py` (A3; this card's `run` threading, vouch gate and own-row exclusion;
  B6); `meetings/transcript.py` (readers, this card);
  `meetings/corroboration.py` (this card, B6); `agents/memory/store.py` (A3, this card);
  `orchestrator/replay.py`, `eval/replay_walk.py` and `api/replay_loader.py` (spine, this card);
  `eval/evidence_honesty.py` (readers, this card, B6); `eval/funnel.py` (readers, this card); the golden
  (readers, this card, B6); `tests/_helpers/committed.py` (A3, A1, readers, record plumbing, this card: record
  plumbing is the prior writer, and this card starts its edit of that file only after record plumbing has
  merged and `main` is merged in); `docs/artifacts.md` (A1, readers, record plumbing, B1, this card, B5, in
  merge order, each writing only its own row: this card's is the `audits/` row);
  `docs/observation-contract.md` (B0, this card); `docs/glossary.md` (A3, spine, this card);
  `audits/tactical-gameplay/README.md` (B1, this card).
- This card alone: `eval/process_scorecard.py`, `scripts/counterfactual_phase20.py`,
  `agents/memory/evidence_context.py`, `docs/cleanup-dispositions.md`, the new test files, and
  `orchestrator/policy_reconstruction.py` only if its call must route through the fold. By the orchestrator's
  ruling of 2026-09-27 on this card's stop-and-ask (the decision memo's 3.2 map, amended in `cb0a4cfc`), also
  `eval/meeting_quality.py`, `eval/vj_instruments.py` and one refusal in the FROZEN
  `eval/deception_instruments.py`.
- Not written here: `engine/`, `observation/`, `orchestrator/experiment_config.py`, `eval/gameplay_census.py`,
  `eval/off_menu.py`, `eval/leak_scan.py`, `frontend/`, `api/schemas.py`, `docs/architecture.md`, the direction
  file and `tasks/README.md`.

**Decisions this card makes; the PR's Decisions and Results record each one.**
- Outcome items 3 and 4 are the orchestrator's signed-off material decisions (0.3 item 8), named as such.
- The resume keep-set is exactly kills and the two vent kinds. Re-gating the other channels against
  pre-regroup visibility is rejected: it needs two visibility frames in one packet.
- One derivation of R feeds every reader, so all of them compute the same window.
- The vent branch of accusation backing (`meetings/transcript.py:2364-2366`) keeps only its spawn test: a
  witnessed vent is gated at event time and stays evidence across a regroup.
- Sabotage survives the reset; it is documented, not changed. The fold and the trail marker key on the public
  row, so they also apply to evidence-version-2 memories. No committed recording carries that row; any test
  expectation that moves is listed in Results with its reason.

**What stays out.**
- No engine change. No `eval/off_menu.py` edit: it is FROZEN, its inline composition stays, it keeps refusing.
- No viewer edit. The `frontend/src/components/MapView.tsx` snap and the `frontend/src/lib/bodies.ts` comment
  move to adoption (decision memo section 1, adoption item 8): the demo does not serve the candidate, and a
  viewer change republishes on merge. `frontend/src/lib/bodies.fixture.json` stays bound to unchanged s9
  bytes, and the tour waits (ruling 11).
- No ML: the training readers keep refusing (ruling 12). No new field, lever or environment switch, and no
  recorded schema gains a field. No census cell definition (A1's), no scorecard cell (R13), no change to
  `post_meeting_retarget`; self-report stays off (R6).
- Fake provider and scripted clients only: no live call, no `.env`, no held-out band. Never print a rendered
  prompt or a seed-band prefix; probes are count-only.

**Delivery.** Branch `work/meeting-reset-coherence`, one PR into `main`, merged or fast-forwarded and never
squashed. Never amend a pushed commit; take `main` by merging, never by rebasing. Each commit body carries
`Card: tasks/work/meeting-reset-coherence.md` immediately followed by
the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs). The PR body has Summary, Definition of done,
Decisions and Questions, ending with the Claude Code attribution line. Agents post no PR comments.
`tasks/README.md` and this card's Status line are the orchestrator's; the worker fills Results.

**Stop and ask** if a `preserve` byte, derived view or census cell moves; the golden needs more than threading
to stay green on s9 or s4; the keep-set would grow beyond kills and vents; a reader outside Expected scope would
read a reset recording at the no-regroup default; a fix needs `engine/`, `frontend/` or `eval/off_menu.py`; or
merging B1 or B4 overlaps a region of this card.

## Expected scope

- Orchestrator: `orchestrator/game.py` (the regions above); `orchestrator/replay.py` (the resume helper, the
  regroup-tick derivation, the fold's regroup argument); `orchestrator/policy_reconstruction.py` only if its
  call must route through the fold.
- Readers: `api/replay_loader.py`, `eval/replay_walk.py`, `eval/funnel.py`, `eval/evidence_honesty.py`,
  `eval/process_scorecard.py` (with the `process-scorecard` profile's layers), `scripts/counterfactual_phase20.py`.
- Meetings: `meetings/transcript.py`, `meetings/manager.py`, `meetings/corroboration.py`.
- Agent memory: `agents/memory/evidence_context.py`, `agents/memory/store.py`. No engine import; `.importlinter`
  is unchanged.
- Test helpers: `tests/meetings/test_prompt_byte_golden.py` (the resume helper, and regroup ingestion through
  the fold) and `tests/_helpers/committed.py` (the reset).
- Instruments, by the orchestrator's ruling of 2026-09-27 on the stop-and-ask: `eval/meeting_quality.py` and
  `eval/vj_instruments.py` (the regroup window), and `eval/deception_instruments.py` (one refusal; the FROZEN
  departure is declared under Record impact).
- Docs: `docs/observation-contract.md`, `docs/glossary.md`, `docs/cleanup-dispositions.md`,
  `audits/tactical-gameplay/README.md`, and the `audits/` row of `docs/artifacts.md`, recomputed last.
- New tests: `tests/orchestrator/test_meeting_reset_coherence.py` (entry, order, grace, resume, equality,
  census, viewer data, documents), `tests/agents/test_regroup_memory.py`,
  `tests/meetings/test_regroup_relevance_window.py`, `tests/eval/test_regroup_instruments.py`.
- Directly necessary test follow-through in these files, and this card's Results.

## Record impact

**What moves: nothing.** No committed recording stamps the arm: no file under `replays/` carries the key, and
the 101 files that do all hold `"preserve"`. The four sets with their MANIFESTs and report gz files,
`docs/process-scorecard.*`, `docs/gameplay-census.*`, the fixtures, the prompt stamps, the ladder tip, the ML
fits and every doc fact keep their bytes. The c9 and c4 derivations read the default path, which
`verify_samples` and the campaign-tier pins prove.

**The first recording.** The new model-facing bytes (the default-path notice, the fold line, the trail step and
the excluded rows) appear only in an arm-ON recording, whose recorded config carries their provenance, so no
stamp is needed. The record card records the arm ON into the candidate. Its pre-registered B2 cells (decision
memo section 4) read against s9's before-column: stale reports 43/135, resumes with a vented impostor 10/107,
resumes with a corpse 60/107. The conformance cells must read 0 and the notice must be present at every
regroup. Outcome cells are reported, never gated; the owner has accepted that the statistics move.

**Meaning and history.** `hub_with_grace` gains its coherent meaning here, while no recording stamps it; from
round 1 that meaning is frozen, and a revision adds a new value. The lab's reset row
(`audits/tactical-gameplay/README.md:141`, `development.json`, `held-out.json`) measured the arm before these
fixes and is not regenerated, since a later experiment never changes an earlier verdict; the note says so.

**Publication.** A push to `main` republishes the demo bundle (`.github/workflows/pages.yml`). This card edits
`api/replay_loader.py`, which the bundle executes, and no shown replay or viewer file. The empty `data/` diff,
`npm --prefix frontend test` and the Playwright journey are the proof.

**Declared FROZEN departure.** `eval/deception_instruments.py:1-2` limits the module to bug fixes and evidence
readers. This card adds one refusal there: a set holding a recording whose `meeting_reset` is `hub_with_grace`
is refused by name and seed before the walk re-derives anything. No evidence semantics change, and the header
is not edited. The orchestrator's ruling of 2026-09-27 on this card's stop-and-ask, made under the owner's
delegation of 2026-09-24, authorizes the departure; the record-plumbing card's `refresh_samples.sh` departure is
the precedent. The PR states it under Decisions.

**Adoption, stated now.** A missing config means `preserve` while any committed recording lacks the key, so each
`preserve` branch stays a reader path. Graduation also needs `post_meeting_retarget` and evidence version 1
retired first, the fixes made unconditional, the viewer snap, the `bodies.ts` comment and a per-replay reset
note, and the `RecordedExperimentConfig` retirement procedure the adopting card writes. A limitation stays: the
fake provider ejects nobody, so how a model reasons after a regroup is first measured by the record.

## Validation

```sh
uv run pytest -p no:cacheprovider tests/orchestrator/test_meeting_reset_coherence.py \
  tests/agents/test_regroup_memory.py tests/meetings/test_regroup_relevance_window.py \
  tests/eval/test_regroup_instruments.py tests/engine/test_meeting_reset_experiment.py \
  tests/orchestrator/test_public_regroup_evidence.py tests/meetings/test_prompt_byte_golden.py -q
uv run lint-imports
bash scripts/verify_samples.sh replays/samples/9p2i
bash scripts/verify_samples.sh replays/samples/4p1i
bash scripts/verify_samples.sh replays/ml_corpus/9p2i
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check
uv run python scripts/gen_frontend_types.py --check
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py
git ls-files audits | wc -l                        # the audits/ row's file count
git ls-files -z audits | xargs -0 cat | wc -c      # the audits/ row's tracked bytes
uv run pytest -m campaign
git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl' | sort | uniq -c
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
npm --prefix frontend test
npm --prefix frontend run e2e
bash scripts/check.sh; echo "check.sh exit $?"
```

Build the base bundle the same way in a detached worktree at the merge base, then `diff -r` the two `data/`
trees; it must print nothing. Every gate runs in a bare shell with 0 `AILIBI_*` exports, and the PR prints that
count. `verify_ml_evidence` runs offline, never with `--complete`. `check.sh` runs whole in a clean worktree, so
no gate after a first failure is masked, and Results quotes its real exit code. Fixtures and probes print ids,
rooms, ticks and counts only.

## Results

Implemented on `work/meeting-reset-coherence` from base `f98bfae9` (the record plumbing merged; B1
`vent-look-and-wait` and B4 `report-body-handle` were not on `main` at the last fetch, 2026-09-27). Commits:
`bcfbbf6d` (the meeting layer's window), `c0767039` (agent memory), `0034e39e` (the resume helper, the
derivation, the fold and every in-scope reader, with the contract and glossary entries its tests pin) and
`d801eb3c` (A-28, the lab's dated note and the `audits/` row). What it implements: `docs/architecture.md`
"Determinism and the substrate ladder" (every reader re-derives the regroup from the recorded settings; replays
stay byte-identical), "Enforced boundaries" (`agents/` imports no `engine/`; `.importlinter` unchanged) and
"Explicit cleanup experiments"; the decision record `tasks/decision-2026-09-24-stage-b-wave.md` sections 0.3
items 6, 8 and 10, 2.3, 3.2 and 3.4 card 9; the spine's arm page `docs/experiment-arms.md`; and
`docs/observation-contract.md`'s public-regroup paragraph. No engine line, no recorded schema field, no new
setting, no prompt registry bump; nothing is recorded.

**Status at `d801eb3c`: active, two boxes open**; round 3 below closes both and sets `done`. The other
fourteen acceptance items were met at `d801eb3c`.

- **Blocked at `d801eb3c`, stop and ask (resolved in round 3): three readers outside Expected scope read a
  reset recording at the no-regroup default.** The card's stop-and-ask list names exactly this case. Each re-derives meeting evidence from a
  recorded transcript without the regroup ticks, so on a `hub_with_grace` recording it can read a sighting in
  the window that the live meeting excluded:
  - `eval/meeting_quality.py::_ejected_in_inform_band` calls `derive_belief_evidence(meeting.transcript,
    contradictions=, roster=, trigger_kind=)`. `scripts/build_sample_report.py` reaches it through the
    validity profile, which threads all three layers, so the record card's sample report on the candidate would
    compute each ejection's inform band without the window.
  - `eval/vj_instruments.py` (`derive_belief_evidence` in the pre-vote graph, `:388`) reads through the
    funnel's shared walk, whose meetings now carry `regroup_ticks`, but this call does not pass them.
  - `eval/deception_instruments.py` (FROZEN; `grounded_vouch_subjects` at `:642`) reads the same walk and
    passes no window.

  The owner's options: widen this card to thread the window into the first two (one keyword each: the funnel
  meeting's `regroup_ticks`, or `derive_regroup_ticks` over the recorded settings and meeting rows) and decide
  the FROZEN third (its header allows "Bug fixes and evidence readers only"); make all three refuse a reset
  recording by name; or accept the unwindowed reading as a named limitation of those cells. The equality box
  stayed open until one was chosen, and no pull request was opened.
- **Waited on B4 at `d801eb3c` (closed in round 3): the body-handle hand-off.** The contract sentence at `docs/observation-contract.md:43-47`
  ("Full model-facing removal is implemented only in temporal mode ...") is to name the recorded body-handle
  setting once B4 has merged. B4 was not on `main`, so the documents box stayed open. This card merges after B1
  and B4: round 3 takes `main` by merging, reruns every gate and recomputes the `audits/` row after B1's section of
  `audits/tactical-gameplay/README.md`.

### Decisions

- **Signed-off material decisions** (decision record 0.3 item 8): Outcome item 3, the regroup notice on the
  default evidence path, and Outcome item 4, the symmetric regroup relevance window (this card's signed-off
  decisions 1 and 2). Both are new model-facing bytes or a detector change beyond the words "full reset"; they
  appear only in an arm-ON recording.
- **The keep-set is exactly `KilledEvent`, `VentEnteredEvent` and `VentExitedEvent`**
  (`orchestrator.replay.REGROUP_KEPT_EVENTS`). The helper reports the dropped `Moved`, `TaskProgressed` and
  `TaskCompleted` events by kind (`REGROUP_REPORTED_DROPS`), the kinds the census table
  `trigger_tick_events_dropped_by_regroup` counts. Re-gating the other channels against pre-regroup visibility
  is rejected: it needs two visibility frames in one packet. A regrouped meeting's own events must be empty,
  and the helper raises otherwise.
- **One derivation of R** (`derive_regroup_ticks`: each earlier non-terminal meeting's tick plus one, empty
  unless the recorded reset is `hub_with_grace`) feeds the live loop, the loader, the walk, the golden, the
  funnel, evidence honesty and the policy rebuild, so every in-scope reader computes the same window. The ticks
  reach `MeetingManager.run` beside `dead_ids` as a keyword with an empty default, validated as non-negative
  integers; they are public knowledge and no recorded schema gains a field. A runner of a game's own that
  predates the keyword runs unchanged outside the reset and is refused by a `TypeError` naming it in a regroup
  game.
- **The window** is R and R+1 (`meetings.transcript.in_regroup_window`). The relevance gate excludes it, the
  alibi-versus-sighting detector does not prosecute with it, and `_own_channel_evidence_rows` makes no row for
  it; the sighting stays in the voter's memory. The spawn window's rows are unchanged. The vent branch of
  accusation backing keeps only its spawn test: a witnessed vent is gated at event time and stays evidence
  across a regroup (`test_a_witnessed_vent_in_the_window_still_backs_a_voice`).
- **Ingestion moved into the fold.** `fold_meeting_outcome_into_memories` takes a keyword-only `regroup_room`
  and calls `fold_public_regroup`; the live loop calls the same helper beside its own post-meeting folds. The
  policy rebuild (`orchestrator/policy_reconstruction.py`) does not run the full meeting fold, so its direct
  call now routes through `fold_public_regroup` and `regroup_room_for`, the same home.
  `ingest_public_regroup` ingests under evidence None and version 2 and returns under version 1.
- **Sabotage survives the reset**: documented in the glossary entry, not changed. The notice and the trail step
  key on the public row, so an evidence-version-2 memory renders them too. The fold renders on the default
  evidence path only: version 2 folds no sightings, the spawn group's included, so each regroup sighting keeps
  its own row there (corrected in round 5; `test_under_version_2_the_regroup_sightings_keep_their_own_rows`).
  No committed recording carries the row. The completion line keeps its detection-row tick (evidence honesty's
  fabricated-sighting rule dates it) and takes the previous self-state row's room when the detection row is a
  regroup tick.
- **Evidence honesty reads two frames** under the reset: `room_at` is the frame an agent reads (the regrouped
  frame at a meeting tick) and `resolved_at` the frame each tick's actions resolved in. A state-read sighting
  is checked against the first and an action-stamped sighting against the second.
- **The `process-scorecard` profile's layers** are `SCORECARD_THREADED_LAYERS = {orchestrator, tactical,
  meeting}`. The route is engine rooms only: the regroup reaches it through the applied meeting's state, the
  body-handle setting changes only trigger text, a tactical setting arrives as recorded actions and a meeting
  setting as the recorded result.
- **Status and index.** The card assigns the Status line and `tasks/README.md` to the orchestrator. As the
  record-plumbing card did under the same dispatch, this worker set Status to `active` and re-derived the
  inventory sentence with `scripts/validate_task_docs.py`. Round 3 sets `done` the same way.

### Caller dispositions

| Caller | Disposition |
| --- | --- |
| `orchestrator/game.py`: the resume composition, `MeetingManager.run`, `_absorb_meeting_beliefs`, the regroup fold | threaded (the helper, the ticks, the ticks, `fold_public_regroup`) |
| `api/replay_loader.py`: `extract_belief_evidence`, the fold, the resume, the policy rebuild | threaded |
| `eval/replay_walk.py`: the resume; `MeetingOpened.regroup_ticks`, `MeetingApplied.regroup_ticks` and `.regroup_room`; the policy rebuild | threaded |
| `eval/evidence_honesty.py`: extraction, fold, `room_at` and `resolved_at` | threaded; the readers card's `meeting_reset` refusal lifted with its fix |
| `eval/funnel.py`: extraction, `reconstruct_stated_paths`, the vouch and absence folds, `VJMeeting.regroup_ticks` | threaded |
| `eval/process_scorecard.py` (`walk_routes`) | reads `MeetingApplied.state`; layers declared |
| `meetings/corroboration.py:648` and the `meetings/transcript.py` internal sites | threaded |
| `tests/meetings/test_prompt_byte_golden.py` (`walk_replay_meetings`) and `tests/_helpers/committed.py` | threaded (the helper, the fold, the ticks) |
| `scripts/counterfactual_phase20.py` (`:526`, `:543`, `:781`) | unchanged: keeps the readers card's named refusal (`test_the_offline_lever_counterfactual_keeps_refusing_the_reset`) |
| `scripts/counterfactual_phase21.py` (`_ledger_for` over the golden walk, both modes) | round 4: refuses a reset recording by name and seed before its walk (`_refuse_the_meeting_reset`); before round 4, from the lift of honesty's refusal on, it read one without the window |
| `eval/off_menu.py` (FROZEN), `training/anchor_study.py`, `training/surrogate/dataset.py`, `experiments/lab/inference_testimony_probe.py` (FROZEN) | unchanged, at the no-regroup default: each refuses experiment recordings or reads only committed `preserve` bytes |
| `audits/workflows/extract_gameplay_facts.py`, `eval/reasoning_evidence.py` | unchanged: the first refuses experiment settings (`refuse_experiment_settings`), the second reads fixtures only |
| `eval/meeting_quality.py`, `eval/vj_instruments.py`, `eval/deception_instruments.py` | round 3: the first two threaded, the FROZEN third refuses the reset by name; at `d801eb3c` not threaded (the stop-and-ask above) |

The readers card named one refusal pending this card, evidence honesty's `meeting_reset`. It is lifted
(`test_honesty_reads_the_meeting_reset_now_its_room_table_is_coherent`, both reset arms), and every other field
that card refused is still refused (`test_every_other_setting_the_readers_refused_is_still_refused`).

### Acceptance evidence

- **The reset at the entry**: `test_the_reset_at_the_orchestrator_entry_clears_what_it_must`; the planted twin
  `test_the_preserve_twin_keeps_the_unreported_corpses_the_vent_and_the_cooldown`;
  `test_the_reset_reads_its_room_and_its_cooldown_from_the_map`. `git diff --stat f98bfae9 -- engine/` prints
  nothing.
- **Order and openings**: `test_an_impostor_parity_win_at_the_meeting_ends_before_any_reset` beside the engine's
  crew-win case, `test_a_button_meeting_under_the_reset_names_no_body_and_clears_the_corpse`,
  `test_a_found_body_emergency_opening_still_raises`, and
  `test_a_meeting_that_ends_the_game_under_the_reset_resumes_nothing` (the meeting's game-over event reaches
  the loop's end).
- **The grace window**: `test_a_kill_after_a_regroup_is_refused_until_the_map_cooldown_runs_out` (refused at T+1
  to T+4, legal at T+5); `test_under_preserve_the_ready_impostor_kills_on_the_resume_tick`;
  `test_the_census_grace_window_is_the_engines` (a carrier kill at T+1 to T+4 raises the grace breach, at T+5
  and T+6 it does not).
- **Resume perception**: `test_after_a_regroup_no_observer_views_the_trigger_ticks_walk_or_task`,
  `test_after_a_regroup_the_witnessed_vent_and_kill_still_arrive`; planted
  `test_without_the_filter_the_regroup_hands_every_observer_false_views` and
  `test_a_keep_set_without_the_kill_loses_the_kill_witness`; the twin
  `test_the_preserve_twin_still_delivers_the_medbay_task_sighting`;
  `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest`.
- **Own-completion placement**: `test_a_trigger_tick_completion_is_placed_where_it_was_done` ("(you were in
  LABS)"), planted `test_without_the_row_the_completion_takes_the_resume_room`,
  `test_an_ordinary_resume_places_the_completion_as_before`.
- **The notice on the default path**: `test_the_regroup_row_is_ingested_on_the_default_path_and_under_version_2`,
  `test_version_1_ingests_no_regroup_row`, `test_the_default_path_renders_the_notice_whenever_the_row_exists`,
  `test_version_1_renders_no_notice_even_beside_a_row`,
  `test_the_second_meeting_carries_the_notice_live_and_reconstructed` (the loader's `get_meeting_memory` equals
  the live memory block), planted `test_without_the_folds_ingestion_the_reconstruction_loses_the_notice`,
  `test_the_preserve_game_renders_no_notice`.
- **The fold and the trail step**: `test_a_nine_player_regroup_folds_eight_rows_into_one_line`,
  `test_a_partial_view_of_the_regroup_keeps_its_rows`, `test_the_route_states_the_regroup_as_its_own_step`,
  `test_the_regroup_breaks_a_stay_in_the_meeting_room_too`,
  `test_the_row_changes_only_the_notice_the_fold_and_the_route`. Removing the fold extension (N-ST-coalesce)
  and the marker (N-ST-trail-step) is red in the table below; the golden keeps `preserve` byte-identical.
- **The symmetric window**: `tests/meetings/test_regroup_relevance_window.py` (the window and gate as Hypothesis
  properties with `deadline=None`; corroboration, claim-stated and grounded vouches, voices, placements, the
  envelope alibi, the physical and kill-scene detectors and the testimony ledger each at R and R+1, with the
  no-window and just-outside cases; the spawn window unchanged).
- **Own rows**: `test_an_early_vent_row_survives_the_budget_past_a_regroup`, planted
  `test_without_the_exclusion_the_regroup_sightings_push_the_vent_row_out`,
  `test_a_spawn_window_sighting_row_is_unchanged`.
- **Equality**: the fixture is seed 1000, recorded with the fake provider from the declared config into
  `tmp_path`: 3 meetings at ticks 8, 20 and 31, all skipped, handed regroup ticks `[]`, `[9]` and `[9, 21]`;
  0 disagreements among the live agents, the loader, the golden walker and the evidence-honesty walk
  (`test_the_four_readings_agree_at_every_meeting_open`). Withholding the ticks, the resume or the notice at any
  of the 4 live sites and 9 reader sites breaks agreement (13 parametrised cases). The three readers above are
  closed in round 3 by their own planted cases.
- **Instruments and the viewer data layer**: `test_a_resume_tick_self_claim_naming_the_meeting_room_scores_true`,
  planted `test_without_the_applied_meeting_the_same_claim_scores_false`;
  `test_honesty_walks_a_reset_recording_and_checks_its_regrouped_clock`, planted
  `test_with_the_pre_regroup_room_table_the_clock_alignment_raises`; `test_the_first_frame_after_a_regroup_shows_no_corpse`
  (the loader's first post-meeting `TickView.bodies` is `()`, the `preserve` twin shows the corpse).
- **The scorecard profile**: `test_the_profile_declares_the_layers_the_route_reads`,
  `test_the_profile_reads_the_full_config_copy_with_every_hash_verified`, planted
  `test_without_its_declaration_the_profile_refuses_the_full_config_copy` and
  `test_a_stand_in_field_in_an_undeclared_layer_is_refused_before_advancing` (each layer).
- **The census**: `test_the_census_reads_zero_where_the_reset_forces_it` (stale reports, a vented impostor or a
  corpse at a resume, grace kills: 0 over a positive denominator; trips closed by a regroup and sabotage at a
  regroup read a count), `test_the_census_discards_what_the_resume_helper_dropped`,
  `test_every_living_agent_holds_one_public_row_per_regroup`,
  `test_a_kill_witness_button_call_soon_after_a_regroup_is_counted`, planted
  `test_a_corpse_restored_at_a_resume_raises_the_breach` and the grace carrier above. The kill-witness case is a
  carrier: a count-only scan of fake arm-ON games at seeds 1000-1007 read 0 such calls in every game.
- **The OFF path**: the Verification table (every gate at the head, the 956 `"preserve"` stamps, an empty bundle
  `data/` diff) and the planted filter below.
- **The documents**: the contract's "The regroup reset" section (the resume rule and the announced
  regroup), the glossary's "regroup (the full meeting reset)", the A-28 line and the lab's dated note;
  `test_the_contract_and_the_glossary_name_every_kept_event_kind`, planted
  `test_a_kind_added_to_the_keep_set_without_the_documents_fails`,
  `test_the_glossary_says_what_moves_what_clears_and_what_survives`,
  `test_the_new_copy_carries_no_identifier_and_no_arithmetic`, planted
  `test_a_planted_identifier_fails_the_copy_scan` (three identifiers). The body-handle sentence is written in round 3.
- **The registry row**: `audits/` read 26,636,941 tracked bytes / 329 files at `d801eb3c`; round 3 recomputes
  it after the merge. The stale-row failure is below.

### Planted failures

Each ran through a harness that edits one snippet, runs one command and restores the file from an in-memory copy,
comparing its sha256.

- **The regroup above the win check** (`apply_meeting_result` with the arm's regroup call copied above
  `resolve_win_conditions`): `pytest tests/orchestrator/test_meeting_reset_coherence.py -k "parity or
  found_body"` exit 1. `FAILED ...::test_an_impostor_parity_win_at_the_meeting_ends_before_any_reset`: the
  survivors' rooms read `{'p-5': 'CAFETERIA'} != {'p-5': 'STORAGE'}` and three more. The found-body case still
  raises (1 passed).
- **The resume filter applied under `preserve`** (the no-regroup branch keeping only the keep-set):
  `pytest tests/meetings/test_prompt_byte_golden.py -n 8` exit 1, 5 failed and 30 passed: on `[9p2i]`
  `test_every_recorded_prompt_re_renders_byte_identically`, `test_reconstructed_transcript_matches_the_recording`,
  `test_every_reconstruction_divergence_is_a_retired_guard`, `test_every_recorded_llm_call_is_consumed_exactly_once`
  and `test_defaults_are_the_only_lookup_misses` (1202 prompts reproduced against 1694). The s4 cases stayed
  green. **`scripts/publish_gameplay_census.py --check` stayed green (exit 0) under the same plant**: the census
  folds the engine's own `TickAdvanced` events and computes its discard table itself, only under the arm, so it
  never reads the resume composition. The card expected it to turn red; that half of the proof cannot fail, and
  the census's own `--check` at the head is its evidence instead.
- **The row left stale after the README note**: `pytest tests/scripts/test_verify_ml_evidence.py -k
  registry_row` exit 1, `FAILED ...::test_every_counted_registry_row_matches_the_index`: "audits/:
  docs/artifacts.md promises 26,636,557 tracked bytes, the tracked files contain 26,636,941 bytes".

### Neutering and the bounded mutation pass

One pass at the production bytes of `0034e39e` (the bytes `d801eb3c` carries), over the 13 production modules
this card edits. 96 neutering probes removed or blanked one added line, argument or condition each; 52 mutants
used exactly the eight listed classes (a: drop a filter or wrapper on a collection, 4; b: swap a collection
for a related one, 3; c: a comparison replaced by a None test or its inverse, 10; d: a role, kind, room, tick
or phase read replaced by a constant, 14; e: a message argument replaced by a constant, 2; f: one member of a
tuple of kinds or layers dropped, 9; g: adjacent branches swapped, 5; h: a loaded source replaced by its
canonical literal, 5). Each ran the four new test files plus `tests/orchestrator/test_public_regroup_evidence.py`
and `tests/engine/test_meeting_reset_experiment.py` (`-x -n 8`), with the readers test or the golden,
`tests/eval/test_replay_walk.py` and `tests/orchestrator/test_meeting_integration.py` added where the site
feeds them; every file was restored from a byte copy and its sha256 compared (148 restored).

First pass: 90 of 96 probes and 45 of 52 mutants red. The thirteen that came back green:

| Id | What stayed green | Planted case that kills it |
| --- | --- | --- |
| N-GM-game-gate | the runner handed the ticks under any recorded settings | `test_outside_the_reset_a_runner_written_before_the_ticks_runs_unchanged[other-settings]` |
| N-MG-detect-chain, -opt-in, -rebuttal | the chain, opt-in and rebuttal detections without the window | `test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window` (a meeting that runs every phase) |
| N-MG-prevote, N-MG-absent | the pre-vote derivation and the absence set without the window | the same test |
| M-GM-compose-phase | the live resume told play resumed after a game-ending meeting | `test_a_meeting_that_ends_the_game_under_the_reset_resumes_nothing` |
| M-GM-fold-room, M-LD-fold-room-const, M-WK-room-const | the regroup room as `"CAFETERIA"` instead of the map's | `test_the_live_notice_names_the_maps_meeting_room`, `test_the_readers_name_the_maps_meeting_room` (the canonical map with its meeting room moved to ADMIN) |
| M-ST-trail-room-const, M-ST-notice-room | the trail step's and the notice's room as `"CAFETERIA"` | `test_the_notice_and_the_route_step_read_the_rows_room` |
| M-RP-kind-source | `REGROUP_REPORTED_DROP_KINDS` as the literal `("Moved", "TaskProgressed", "TaskCompleted")` | equivalent: the literal is value-equal to the three event classes' `type` tags, which no mutant here can change; `test_the_helper_names_the_kinds_the_census_table_counts` pins them to the census table's kinds |

Every one of the twelve was red when rerun against its planted case. The whole table, with the first red
test each `-x` run reported (id prefixes: RP `orchestrator/replay.py`, GM `orchestrator/game.py`, PR
`orchestrator/policy_reconstruction.py`, LD `api/replay_loader.py`, WK `eval/replay_walk.py`, EH
`eval/evidence_honesty.py`, FN `eval/funnel.py`, SC `eval/process_scorecard.py`, TR `meetings/transcript.py`,
MG `meetings/manager.py`, CR `meetings/corroboration.py`, EC `agents/memory/evidence_context.py`, ST
`agents/memory/store.py`):

| Id | Kind | First red test |
| --- | --- | --- |
| N-RP-fold | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| M-RP-fold-none | None test / inverse | `test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement[golden-notice]` |
| M-RP-keep-kill | drop a tuple member | `test_after_a_regroup_the_witnessed_vent_and_kill_still_arrive` |
| M-RP-keep-enter | drop a tuple member | `test_after_a_regroup_the_witnessed_vent_and_kill_still_arrive` |
| M-RP-keep-exit | drop a tuple member | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-drop-moved | drop a tuple member | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-drop-progress | drop a tuple member | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-drop-complete | drop a tuple member | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| N-RP-plain-meeting-events | neuter | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| N-RP-refusal | neuter | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-regrouped-branch | swap branches | `test_without_the_filter_the_regroup_hands_every_observer_false_views` |
| N-RP-keep-append | neuter | `test_after_a_regroup_the_witnessed_vent_and_kill_still_arrive` |
| N-RP-count | neuter | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-count-kind | read to constant | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-dropped-filter | drop a filter | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| M-RP-kind-source | loaded source to literal | survives, equivalent (below) |
| N-RP-regrouped-reset | neuter | `test_a_meeting_regroups_only_under_the_reset_and_only_when_play_resumes[config2-PLAY-False]` |
| N-RP-regrouped-phase | neuter | `test_a_meeting_regroups_only_under_the_reset_and_only_when_play_resumes[config1-GAME_OVER-False]` |
| M-RP-regrouped-none | None test / inverse | `test_a_meeting_regroups_only_under_the_reset_and_only_when_play_resumes[None-PLAY-False]` |
| M-RP-room-const | read to constant | `test_the_regroup_room_is_the_maps_meeting_room_under_the_reset[ADMIN]` |
| N-RP-room-guard | neuter | `test_the_regroup_room_is_the_maps_meeting_room_under_the_reset[ADMIN]` |
| M-RP-ticks-const | read to constant | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| N-RP-ticks-guard | neuter | `test_the_regroup_ticks_are_each_prior_meetings_resume_tick` |
| N-RP-fold-phase | neuter | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| M-RP-fold-living | drop a filter | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| M-RP-fold-skip | None test / inverse | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| N-RP-fold-ingest | neuter | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| M-RP-fold-tick | read to constant | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| M-RP-fold-room | message argument | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| N-GM-runner-ticks | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-GM-derive-arg | neuter | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| N-GM-append | neuter | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| M-GM-append-phase | None test / inverse | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| M-GM-meeting-tick | read to constant | `test_each_meeting_receives_the_resume_tick_of_every_meeting_before_it` |
| N-GM-compose | neuter | `test_the_game_resumes_from_at_least_two_regroups` |
| M-GM-compose-phase | read to constant | first green; killed by `test_a_meeting_that_ends_the_game_under_the_reset_resumes_nothing` |
| N-GM-game-gate | neuter | first green; killed by `test_outside_the_reset_a_runner_written_before_the_ticks_runs_unchanged[other-settings]` |
| M-GM-game-gate-none | None test / inverse | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| N-GM-run-kwargs | neuter | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| M-GM-run-kwargs-branch | swap branches | `test_a_runner_written_before_the_ticks_is_refused_in_a_regroup_game` |
| N-GM-absorb-ticks | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-GM-fold-call | neuter | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| M-GM-fold-none | None test / inverse | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| M-GM-fold-room | loaded source to literal | first green; killed by `test_the_live_notice_names_the_maps_meeting_room` |
| M-GM-fold-filter | drop a filter | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| M-GM-fold-state | swap a collection | `test_a_runner_of_its_own_receives_the_ticks_and_a_memoryless_agent_is_skipped` |
| N-GM-extract-ticks | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-PR-absorb-ticks | neuter | `test_the_policy_rebuild_folds_the_meeting_with_its_regroup_ticks` |
| N-PR-fold | neuter | `test_the_policy_rebuild_folds_the_meeting_with_its_regroup_ticks` |
| M-PR-room | loaded source to literal | `test_the_policy_rebuild_folds_the_meeting_with_its_regroup_ticks` |
| N-LD-derive-arg | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-LD-policy-ticks | neuter | `test_each_reader_hands_the_policy_rebuild_every_meetings_regroup_ticks[loader]` |
| N-LD-extract-ticks | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-LD-fold-room | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| M-LD-fold-room-const | loaded source to literal | first green; killed by `test_the_readers_name_the_maps_meeting_room` |
| N-LD-append | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| M-LD-append-tick | read to constant | `test_the_four_readings_agree_at_every_meeting_open` |
| N-LD-compose | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-WK-opened-ticks | neuter | `test_the_funnel_walk_carries_each_meetings_regroup_ticks` |
| N-WK-applied-ticks | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-WK-applied-room | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| M-WK-room-const | loaded source to literal | first green; killed by `test_the_readers_name_the_maps_meeting_room` |
| N-WK-policy-ticks | neuter | `test_each_reader_hands_the_policy_rebuild_every_meetings_regroup_ticks[walk]` |
| N-WK-compose | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-WK-append | neuter | `test_each_reader_hands_the_policy_rebuild_every_meetings_regroup_ticks[walk]` |
| M-WK-append-phase | None test / inverse | `test_each_reader_hands_the_policy_rebuild_every_meetings_regroup_ticks[walk]` |
| N-WK-derive-arg | neuter | `test_each_reader_hands_the_policy_rebuild_every_meetings_regroup_ticks[walk]` |
| N-EH-extract-ticks | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-EH-fold-room | neuter | `test_the_four_readings_agree_at_every_meeting_open` |
| N-EH-room-at-override | neuter | `test_honesty_walks_a_reset_recording_and_checks_its_regrouped_clock` |
| N-EH-resolved-fill | neuter | `test_with_the_pre_regroup_room_table_the_clock_alignment_raises` |
| M-EH-resolved-swap | swap a collection | `test_the_clock_reads_state_rows_on_the_regrouped_frame_and_actions_where_resolved` |
| M-EH-resolved-branch | swap branches | `test_honesty_walks_a_reset_recording_and_checks_its_regrouped_clock` |
| M-EH-resolved-none | None test / inverse | `test_the_clock_reads_state_rows_on_the_regrouped_frame_and_actions_where_resolved` |
| N-EH-pass-resolved | neuter | `test_with_the_pre_regroup_room_table_the_clock_alignment_raises` |
| N-EH-reads | neuter | `test_every_other_setting_the_readers_refused_is_still_refused[crew_idle_policy-patrol]` |
| N-FN-vj-ticks | neuter | `test_the_funnel_walk_carries_each_meetings_regroup_ticks` |
| N-FN-extract-ticks | neuter | `test_the_funnel_belief_fold_reads_the_window` |
| N-FN-vouch-ticks | neuter | `test_the_pooling_folds_read_the_window` |
| N-FN-absence-ticks | neuter | `test_the_pooling_folds_read_the_window` |
| N-SC-override | neuter | `test_a_resume_tick_self_claim_naming_the_meeting_room_scores_true` |
| N-SC-layers | neuter | `test_a_stand_in_field_in_an_undeclared_layer_is_refused_before_advancing[tactical]` |
| M-SC-layer-orchestrator | drop a tuple member | `test_a_stand_in_field_in_an_undeclared_layer_is_refused_before_advancing[orchestrator]` |
| M-SC-layer-tactical | drop a tuple member | `test_the_profile_reads_the_full_config_copy_with_every_hash_verified` |
| M-SC-layer-meeting | drop a tuple member | `test_the_profile_declares_the_layers_the_route_reads` |
| M-TR-window-now | neuter | `test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement[loader-ticks]` |
| M-TR-window-next | neuter | `test_a_co_presence_sighting_in_the_window_does_not_corroborate[13]` |
| M-TR-window-tick | read to constant | `test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement[loader-ticks]` |
| N-TR-gate-prong | neuter | `test_a_sighting_in_the_window_backs_no_voice[13]` |
| N-TR-reconstruct | neuter | `test_a_placement_in_the_window_places_nobody[12]` |
| N-TR-absent | neuter | `test_a_placement_in_the_window_places_nobody[12]` |
| N-TR-avs-thread | neuter | `test_an_envelope_alibi_spanning_a_regroup_is_not_prosecuted_in_the_window[12]` |
| N-TR-paths | neuter | `test_co_presence_in_the_window_cannot_physically_contradict_an_alibi` |
| N-TR-killscene-paths | neuter | `test_a_kill_scene_co_presence_in_the_window_contradicts_nothing` |
| N-TR-avs-skip | neuter | `test_an_envelope_alibi_spanning_a_regroup_is_not_prosecuted_in_the_window[12]` |
| M-TR-avs-tick | read to constant | `test_an_envelope_alibi_spanning_a_regroup_is_not_prosecuted_in_the_window[12]` |
| N-TR-corroborations | neuter | `test_a_co_presence_sighting_in_the_window_does_not_corroborate[12]` |
| N-TR-voices | neuter | `test_a_sighting_in_the_window_backs_no_voice[12]` |
| N-TR-carries | neuter | `test_a_sighting_in_the_window_backs_no_voice[12]` |
| N-TR-vouch | neuter | `test_a_grounded_vouch_in_the_window_grounds_nothing[12]` |
| N-MG-detect-inner | neuter | `test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows` |
| N-MG-detect-chain | neuter | first green; killed by `test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window` |
| N-MG-detect-opt-in | neuter | first green; killed by `test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window` |
| N-MG-detect-roll-call | neuter | `test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows` |
| N-MG-detect-rebuttal | neuter | first green; killed by `test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window` |
| N-MG-detect-final | neuter | `test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows` |
| N-MG-validate | neuter | `test_the_manager_refuses_a_tick_that_is_not_a_non_negative_integer[bad1]` |
| N-MG-prevote | neuter | first green; killed by `test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window` |
| N-MG-absent | neuter | first green; killed by `test_every_in_meeting_detection_and_the_pre_vote_fold_receive_the_window` |
| N-MG-ledger | neuter | `test_the_manager_hands_the_testimony_ledger_the_window` |
| N-MG-ballots | neuter | `test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows` |
| N-MG-one-ballot | neuter | `test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows` |
| N-MG-rows | neuter | `test_the_manager_reads_the_window_in_every_detection_and_the_ballot_rows` |
| N-MG-own-rows | neuter | `test_an_early_vent_row_survives_the_budget_past_a_regroup` |
| N-MG-own-skip | neuter | `test_an_early_vent_row_survives_the_budget_past_a_regroup` |
| M-MG-own-skip-tick | read to constant | `test_an_early_vent_row_survives_the_budget_past_a_regroup` |
| N-MG-claim-vouch | neuter | `test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement[loader-ticks]` |
| N-MG-derive-corroborations | neuter | `test_a_co_presence_sighting_in_the_window_does_not_corroborate[12]` |
| N-MG-derive-grounded | neuter | `test_a_grounded_vouch_in_the_window_grounds_nothing[12]` |
| N-MG-derive-voices | neuter | `test_a_sighting_in_the_window_backs_no_voice[12]` |
| N-MG-derive-absent | neuter | `test_a_placement_in_the_window_places_nobody[12]` |
| N-MG-extract | neuter | `test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement[loader-ticks]` |
| N-CR-ledger | neuter | `test_the_manager_hands_the_testimony_ledger_the_window` |
| N-EC-guard | neuter | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| M-EC-guard-none | None test / inverse | `test_the_regroup_row_goes_to_every_living_memory_and_to_nobody_else` |
| N-ST-regroups | neuter | `test_the_default_path_renders_the_notice_whenever_the_row_exists` |
| M-ST-public-filter | drop a filter | `test_only_a_public_row_is_an_announced_regroup` |
| N-ST-malformed | neuter | `test_a_malformed_public_row_is_refused` |
| N-ST-completion-ticks | neuter | `test_a_trigger_tick_completion_is_placed_where_it_was_done` |
| M-ST-completion-branch | swap branches | `test_a_trigger_tick_completion_is_placed_where_it_was_done` |
| N-ST-completion-room | neuter | `test_a_trigger_tick_completion_is_placed_where_it_was_done` |
| N-ST-last-room | neuter | `test_a_trigger_tick_completion_is_placed_where_it_was_done` |
| N-ST-coalesce | neuter | `test_a_nine_player_regroup_folds_eight_rows_into_one_line` |
| M-ST-group-loop | neuter | `test_a_nine_player_regroup_folds_eight_rows_into_one_line` |
| M-ST-group-start | read to constant | `test_a_nine_player_regroup_folds_eight_rows_into_one_line` |
| M-ST-group-expected | swap a collection | `test_the_fold_expects_the_players_the_row_gathered_not_the_known_roster` |
| N-ST-group-room | neuter | `test_the_fold_reads_the_rows_room` |
| M-ST-group-room-none | None test / inverse | `test_withholding_the_window_or_the_resume_at_a_live_site_breaks_agreement[live-run-ticks]` |
| M-ST-group-prefix | swap branches | `test_a_nine_player_regroup_folds_eight_rows_into_one_line` |
| M-ST-group-start-obs | read to constant | `test_a_nine_player_regroup_folds_eight_rows_into_one_line` |
| M-ST-consumed | neuter | `test_a_nine_player_regroup_folds_eight_rows_into_one_line` |
| N-ST-trail-regroups | neuter | `test_the_route_states_the_regroup_as_its_own_step` |
| M-ST-trail-break | neuter | `test_the_regroup_breaks_a_stay_in_the_meeting_room_too` |
| M-ST-trail-room-const | read to constant | first green; killed by `test_the_notice_and_the_route_step_read_the_rows_room` |
| N-ST-trail-step | neuter | `test_the_route_states_the_regroup_as_its_own_step` |
| M-ST-trail-step-tick | read to constant | `test_the_route_states_the_regroup_as_its_own_step` |
| N-ST-notice | neuter | `test_the_default_path_renders_the_notice_whenever_the_row_exists` |
| M-ST-notice-room | message argument | first green; killed by `test_the_notice_and_the_route_step_read_the_rows_room` |

### Verification at `d801eb3c`

A bare shell with 0 `AILIBI_*` exports; each exit code captured from the process, never through a pipe.

| Command | Result |
| --- | --- |
| `bash scripts/check.sh` | exit 0: ruff clean, 543 files formatted, `lint-imports` 4 kept 0 broken, task docs (88 work cards) and prompts valid, mypy clean on 514 files, pytest 9430 passed, 20 skipped, 3 xfailed; frontend lint, types, 559 vitest tests and build |
| the card's seven test files (`-q`) | exit 0: 183 passed |
| `bash scripts/verify_samples.sh <set>`, once per set | exit 0 each: s9 50, s4 50, c9 150, c4 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent (the 955 / 104 / 103 / 2 census cannot have moved) |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, consistent |
| `uv run python scripts/gen_frontend_types.py --check`, `scripts/check_doc_facts.py`, `scripts/validate_task_docs.py` | exit 0 each |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 329; 26,636,941 |
| `uv run pytest -m campaign -n auto --dist loadfile -q` | exit 0: 336 passed |
| `git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl' \| sort \| uniq -c` | 956 `"meeting_reset":"preserve"`, in 101 files |
| `scripts/build_demo_bundle.py`, at an export of `f98bfae9` and at the head | exit 0 each, 156 JSON files baked; `diff -r` of the two `data/` trees prints nothing (exit 0). The base export read the same replay bytes through a link (`diff -rq` of the two `replays/` trees empty), so the file times that stamp `created_at` agree; the two READMEs differ only in that sentence |
| `npm --prefix frontend test`; `npm --prefix frontend run e2e` | exit 0: 559 passed; 13 passed, 3 skipped (the media-capture journeys) |
| `git diff --stat f98bfae9 -- engine/ frontend/ eval/off_menu.py replays/` | empty |

A first full `pytest -n 10` run (not `check.sh`'s `--dist loadfile`) also failed
`tests/scripts/test_record_ml_corpus.py::test_fake_target_guard_resolves_symlinks_and_dot_dot`, a file this card
does not touch; it passes alone and in `check.sh`.

### Changed test expectations

- `tests/eval/test_recorded_arm_readers.py`: `HONESTY_READS` is now all of `READABLE_SETTINGS`, and the refusal
  test became `test_honesty_reads_the_meeting_reset_now_its_room_table_is_coherent`: the refusal was lifted with
  its fix, as the readers card specified.
- `tests/meetings/test_meeting_trigger_kind.py` (`_WatchedManager._detect_contradictions`) and
  `tests/agents/test_beliefs.py` (the two `_ungated` stand-ins for `is_relevant_sighting`): each stand-in gained
  the `regroup_ticks` keyword the real signature gained; no assertion changed.
- `tests/eval/test_replay_walk.py` and `tests/agents/test_memory_rendering.py`: a docstring and a comment now say
  the stated contract holds without a regroup; no assertion changed.
- No test was weakened and no committed fixture byte moved. The description in
  `tests/fixtures/memory_rendering/self_location_trail.json` ("a meeting freezes movement") is still true of
  its ordinary meeting, so it is left as is.

### Closing greps

`git grep -n -i -E "freez(es|e) (the )?movement|meeting freezes|pre-meeting play events plus|refuses the (meeting
)?reset|until that setting's own card|written only under evidence version 2|only under version 2" --
':!tasks/phase-*' ':!agent_prompts' ':!audits'`, at the head. The hits:
- `eval/funnel.py:413` and `tests/eval/test_replay_walk.py:276`: rewritten here to state both cases;
- `tests/agents/test_memory_rendering.py:2291` ("An ordinary meeting freezes movement") and the fixture above:
  true of an ordinary meeting;
- this card's Evidence (citations at `e886b663`) and `tasks/work/stage-b-readers.md:595-597` and `:656`, that
  card's record of the state before this card; neither is rewritten.

### Limitations

- The resume filter drops every trigger-tick event outside the keep-set and counts only the three reported
  kinds. In the default delivery the only other trigger-tick event an observer reads is a rejected `do_task`
  (`observation/service.py:557`), which is dropped uncounted.
- The notice and the trail step key on the public row, so an evidence-version-2 memory under the reset
  renders them too; the fold line renders on the default evidence path only, and version 2 renders each
  regroup sighting on its own row (corrected in round 5). No committed recording has the row. The notice stays
  excluded under evidence version 1.
- The fake provider ejects nobody, so every fake reset game's meetings resume. A meeting that ends the game
  under the reset is covered by a runner of the test's own; how a model reasons after a regroup is first
  measured by the record.
- No development game at seeds 1000-1007 holds a kill-witness button call within 6 ticks of a regroup, so that
  census case is a carrier built from the fixture game's walk with the call inserted.
- The planted census `--check` cannot turn red under the filter applied to `preserve` (above).
- The three readers the stop-and-ask named are resolved in round 3; the further readers round 3 found are
  listed there.

### Review corrections, round 3 (2026-09-27)

The resume after the stop-and-ask. Commits: `1ad1b57c` (the merge of `main`), `6fb328a8` (the three readers and
the contract sentence) and the card commits that follow it. All three verifier lenses run on this round, the
card's first.

**The merge.** `main` at `cb0a4cfc` (B1 `#489`, B4 `#488`, the flip of B4's card and the orchestrator's
amendment of the decision memo's one-writer map for this card's three readers) is merged in `1ad1b57c`; nothing
is rebased. `orchestrator/game.py` merged without a conflict and by region: B4 changed only the body of
`_build_meeting_trigger`, this card's regions are the resume composition, the regroup ticks and the absorb.
`audits/tactical-gameplay/README.md` keeps B1's rows and this card's dated reset-row note. Two conflicts, both
derived: the `tasks/README.md` inventory sentence, re-derived with `scripts/validate_task_docs.py`, and the
`audits/` row of `docs/artifacts.md`, recomputed with `git ls-files` over the merged tree (330 files, 27,303,776
tracked bytes; neither later commit touches `audits/`, and the row is re-read at the head below).

**Finding 1: the three readers, by the orchestrator's ruling of 2026-09-27.** Candidate-facing instruments read
the window; a FROZEN instrument keeps its evidence semantics and refuses.

- (a) `eval/meeting_quality.py`. `_ejected_in_inform_band` takes a required keyword `regroup_ticks` and hands it
  to `derive_belief_evidence`. `decompose_ejection_channels` passes `_regroup_ticks_before(game, meeting_index)`:
  `orchestrator.replay.derive_regroup_ticks` over the report's recorded settings (`GameReport.experiment_config`,
  filled from the recording by `eval.balance_eval`) and the earlier meetings' ticks. Every earlier meeting of a
  game resumed play, since a meeting that ends the game is its last, so this is the live derivation. Consumers:
  `compute_multi_signal_conversion` and `decompose_ejection_channels`, read by `scripts/build_sample_report.py`
  (the summary at `:336`, `--baseline-out` at `:502` and `:513`) and by `audits/workflows/extract_gameplay_facts.py`,
  which refuses experiment settings (`refuse_experiment_settings`). The scorecard, the census and the validity
  gate do not reach it: `eval/process_scorecard.py` names it only in a definition that says it is not used.
  Planted: on the fake reset recording (`vouching_game`, assembled by `assemble_tournament_report`, the sample
  report's own assembly), `_regroup_ticks_before` equals the ticks each live meeting ran with (none at the
  first meeting, then every earlier meeting's resume tick); the last meeting turned into an impostor ejection whose one voice rests on a sighting
  at the previous regroup tick or the tick after it decomposes to `{body_proximity}` and the multi-signal fold
  counts 0 inform conversions; with the window withheld (`derive_regroup_ticks` patched empty) the same fold
  reads `{single_witness_inform}` and counts 1; a sighting two ticks past the regroup still informs; the
  `preserve` twin (the same planted game with no recorded settings) reads `{single_witness_inform}` and 1, as
  before this card. The committed sets fold byte-identically: the four `build_sample_report --check` runs.
- (b) `eval/vj_instruments.py`: **threaded**, not refused. `_pre_vote_graphs` passes the walked meeting's
  `regroup_ticks` (the funnel walk's `_VJMeeting` already carried them). Consumer: `compute_vj_instruments`, read
  by `scripts/measure_baseline.py --vj` (`:785`) on any directory; `eval/deception_instruments.py` imports only
  the funnel's carriers, not this module. `measure_baseline.py` is the command the record card runs on the
  candidate (`--honesty`), and `--vj` is a flag of the same command, so it is candidate-facing. Planted: a spy on
  the derivation reads each meeting's live window over the whole fold of the fake reset recording, and a
  planted one-voice turn at the last regroup tick moves every listening crewmate's row by the absence lift
  (+0.08) with the window and by the inform lift (+0.05) without it.
- (c) `eval/deception_instruments.py` (FROZEN): `_refuse_the_meeting_reset` reads each replay's recorded
  settings (`recorded_experiment_config`) and raises, naming `meeting_reset='hub_with_grace'` and the seed,
  before `_walk_set_vj` runs. No evidence semantics change: `_restricted_grounded_subjects` and every other fold
  are byte-identical, `tests/eval/test_deception_instruments.py` stays green, and the refusal fires on the reset
  alone (a `preserve` recording, one stating `preserve` explicitly, and one with two other wave settings all reach
  the walk). The departure is declared under Record impact.

**Finding 2: integration.** Beside the merge above, `docs/observation-contract.md` now takes the body-handle
card's hand-off: full model-facing removal is in temporal mode; without it,
`report_body_handle_version = 1` changes the report opening alone, naming the corpse by its public
`body-{victim_id}` handle (no death tick) and reading "a body" for a corpse missing from the state; with neither,
the opening still carries the internal id. That is the builder's docstring at the strength it delivers
(`orchestrator/game.py`, `_build_meeting_trigger`). The test reads the setting from `RecordedExperimentConfig`
and the handle from `observation.body_ids.public_body_id`; the planted case is the paragraph as it read before
the setting existed.

**Further readers found, not in the ruling and left unchanged.** A search over every production caller of the
window-bearing functions (`derive_belief_evidence`, `extract_belief_evidence`, `grounded_vouch_subjects`,
`is_relevant_sighting`, `reconstruct_stated_paths`, `detect_corroborations`, `detect_contradictions`,
`independent_voices`, `absent_players`, `build_testimony_ledger`, `build_evidence_rows`) found two more that can
read a reset recording at the no-regroup default. Neither is in the record card's path, and neither file is this
card's, so both are the PR's question to the orchestrator:
- `scripts/counterfactual_phase21.py::_ledger_for` builds the testimony ledger without the window over the
  golden walk. Its `--sets` mode takes any set name under `replays/`; its `--recording` mode requires the Wave-2
  substrate slate, which a Stage-B candidate does not carry. (Round 4: it now refuses a reset recording by name.)
- The FROZEN concluded lab probes `experiments/lab/deception_battery.py`, `deflection_probe.py`,
  `forward_redesign_conversion_probe.py`, `forward_redesign_detector_sweep.py`, `meeting_prompt_battery.py` and
  `vent_escape_lab.py` call `detect_contradictions` without the window, like `inference_testimony_probe.py`,
  which the Evidence section already lists.

**Red before, green after.** The 14 new instrument tests and the contract test, run against the pre-round
bytes of the three modules and the contract (swapped in from byte copies, restored, sha256 equal):
`pytest tests/eval/test_regroup_instruments.py tests/orchestrator/test_meeting_reset_coherence.py::test_the_contract_names_the_recorded_body_handle_setting`
exit 1, 10 failed and 31 passed. Red: both `informs_nobody` cases (the inform credited), the two V&J tests (no
window reaches the derivation; the rows equal the unwindowed ones), the two deception refusals (the walk ran
first), the contract test, and three tests that call the new helper (`window_each`, `reads_no_window`,
`withheld`, red because the helper and the module's import of the derivation do not exist yet). Green, as controls must be: `just_past_the_window`, the `preserve` twin, the
three `names_the_reset_and_nothing_else` cases, and the 26 tests this card already had in the file. With the
round's bytes: 41 passed.

**The bounded mutation pass**, over the spans this round changed, with the listed classes only. Each mutant
replaced one snippet, ran `tests/eval/test_regroup_instruments.py` plus the module's own suite
(`test_gate_spec_metrics.py` and `test_wave2_metrics.py`, `test_vj_instruments.py`, or
`test_deception_instruments.py`) with `-x`, and was restored from a byte copy (20 restored, sha256 equal). 20
mutants, 19 red on the first run; the one survivor is equivalent. None needed a new planted case.

| Id | Class | First red test |
| --- | --- | --- |
| N-MQ-derive-kw | neuter the keyword | `test_a_voice_resting_on_a_regroup_sighting_informs_nobody[0]` |
| M-MQ-call-arg | message argument to constant (`frozenset()`) | `test_a_voice_resting_on_a_regroup_sighting_informs_nobody[0]` |
| M-MQ-call-index | tick read to constant (`meeting_index` to 0) | `test_a_voice_resting_on_a_regroup_sighting_informs_nobody[0]` |
| M-MQ-config | loaded source to literal (settings to `None`) | `test_the_inform_band_reads_the_window_each_live_meeting_ran_with` |
| M-MQ-tick | tick read to constant | `test_the_inform_band_reads_the_window_each_live_meeting_ran_with` |
| M-MQ-slice | drop a filter (every meeting) | `test_the_inform_band_reads_the_window_each_live_meeting_ran_with` |
| M-MQ-slice-next | swap a collection (this meeting too) | `test_the_inform_band_reads_the_window_each_live_meeting_ran_with` |
| M-MQ-branch | swap branches (the band test inverted) | `test_a_voice_resting_on_a_regroup_sighting_informs_nobody[0]` |
| N-VJ-kw | neuter the keyword | `test_the_vj_pre_vote_fold_reads_each_meetings_window` |
| M-VJ-const | message argument to constant | `test_the_vj_pre_vote_fold_reads_each_meetings_window` |
| N-DI-call | neuter the refusal | `test_the_deception_instruments_refuse_the_reset_by_name_before_walking` |
| M-DI-order | swap adjacent statements (walk first) | `test_the_deception_instruments_refuse_the_reset_by_name_before_walking` |
| M-DI-none | None test inverted | `test_the_deception_refusal_names_the_reset_and_nothing_else[settings0]` |
| M-DI-none-only | comparison replaced by a None test | `test_the_deception_refusal_names_the_reset_and_nothing_else[settings2]` |
| M-DI-eq | comparison inverted | `test_the_deception_refusal_names_the_reset_and_nothing_else[settings2]` |
| M-DI-literal | loaded source to literal (`"preserve"`) | `test_the_deception_refusal_names_the_reset_and_nothing_else[settings2]` |
| M-DI-seeds | swap a collection (first seed only) | `test_a_set_with_one_reset_recording_is_refused_at_that_seed` |
| M-DI-seed-path | read to constant (first seed's file) | `test_a_set_with_one_reset_recording_is_refused_at_that_seed` |
| M-DI-msg-seed | message argument to constant | `test_the_deception_instruments_refuse_the_reset_by_name_before_walking` |
| M-DI-msg-value | message argument to constant (`'hub_with_grace'`) | survives, equivalent: the branch runs only when the value is `'hub_with_grace'`, so the message bytes are equal |

**Verification at `6fb328a8`.** A bare shell with 0 `AILIBI_*` exports; each exit code captured from the process,
never through a pipe.

| Command | Result |
| --- | --- |
| the card's seven test files (`-q -n 8`) | exit 0: 199 passed |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |
| `bash scripts/verify_samples.sh <set>`, once per set | exit 0 each: s9 50, s4 50, c9 150, c4 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `build_sample_report.py` on a fake `hub_with_grace` set (seeds 1000-1002, 7 meetings, recorded into the scratchpad by `tests/_helpers/scripted_meeting.record_game`): write, then `--check`, then `--baseline-out` | exit 0 each; 0 impostor ejections, so every channel count reads 0 |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, consistent |
| `uv run python scripts/gen_frontend_types.py --check`, `scripts/check_doc_facts.py`, `scripts/validate_task_docs.py` | exit 0 each |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run pytest -m campaign -n auto --dist loadfile -q` | exit 0: 336 passed |
| `git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl'`, sorted and counted; `git grep -l` for the files | 956 `"meeting_reset":"preserve"`, in 101 files |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 330; 27,303,776, the row as recomputed in the merge |
| `scripts/build_demo_bundle.py`, at an export of `cb0a4cfc` and at `6fb328a8` | exit 0 each, 156 JSON files baked; `diff -r` of the two `data/` trees prints nothing (exit 0). The export reads the same replay bytes through a link (`diff -rq` of its archived `replays/` against the branch's is empty), so the file times that stamp `created_at` agree |
| `npm --prefix frontend test`; `npm --prefix frontend run e2e` | exit 0: 559 passed; 13 passed, 3 skipped (the media-capture journeys) |
| `git diff --stat cb0a4cfc 6fb328a8 -- engine/ frontend/ eval/off_menu.py replays/ observation/ orchestrator/experiment_config.py eval/gameplay_census.py eval/leak_scan.py api/schemas.py docs/architecture.md` | empty |

`bash scripts/check.sh` ran once, at `faa61591`, the commit that first carried this subsection, in a bare shell
with its exit code captured from the process: exit 0 (ruff clean, 546 files formatted, `lint-imports` 4 kept 0
broken, task docs with 88 work cards and prompts valid, mypy clean on 517 files, pytest 9654 passed, 20 skipped,
3 xfailed; frontend lint, types, 559 vitest tests and build). The commit after it changes only this paragraph;
`scripts/validate_task_docs.py` and `scripts/check_doc_facts.py` re-run at that head.

**Changed test expectations.** None. The round adds 16 tests (14 in `tests/eval/test_regroup_instruments.py`, 2
in `tests/orchestrator/test_meeting_reset_coherence.py`) and weakens, skips or deletes none.

**Closing greps.** `git grep -n -i -E "removal is implemented only in temporal|only in temporal mode|OFF opening
descriptions|passes no window|does not pass them|inherit the funnel's refusal|need no edit" -- ':!tasks/phase-*'
':!agent_prompts' ':!audits'`, at `6fb328a8`. The hits:
- this card's own record of `d801eb3c` (Results, the stop-and-ask bullets), now stated in the past;
- `tasks/work/report-body-handle.md:350` and `:642`, that card's hand-off, and
  `tasks/work/stage-b-readers.md:601`, that card's record of the readers before this ruling; neither is
  rewritten;
- `tasks/investigations-2026-09-24/vent_witness_and_exit.md:155`, an unrelated "need no edit";
- `tests/orchestrator/test_meeting_reset_coherence.py`, the planted pre-setting paragraph.

**Limitations.**
- The planted ejections are carriers built from a fake reset game: the fake provider ejects nobody, so the fake
  set's own fold reads 0 on every channel with or without the window. The record is the first real reading.
- The two readers under "Further readers found" read a reset recording without the window if pointed at one.
  (Round 4: the phase-21 counterfactual now refuses one; the lab probes remain the PR's question.)

### Review corrections, round 4 (2026-09-27)

The repair of the four blocking findings the three verifier lenses and the Codex review raised on round 3.
Commits: the commit that first carries this subsection (the phase-21 refusal, the planted cases and this record)
and the card commit after it, which records the `check.sh` run. `main` is still `cb0a4cfc`, the round-3 merge
base, so nothing is merged. No `audits/` or `tests/fixtures/` byte moves, so the `audits/` row stays
(330 files, 27,303,776 tracked bytes, re-read at the head below).

**Finding 1: four listed-class survivors in lines this card added (correctness).** The verifiers' harness kept
four mutants green over the six non-golden card suites at `711e488f` (164 passed each). Each is now red through
a planted case; none is named equivalent:

| Id | Mutant | Planted case that kills it |
| --- | --- | --- |
| S1 | `_public_regroups`: `isinstance(players, (tuple, list))` to `(tuple,)` (drop a tuple member) | `test_a_public_row_listing_its_players_reads_as_the_tuple_row_does`: the row's contract is a room and a list of player ids; a hand-built row holding a list renders the same notice, fold and route step as the tuple row the one writer stores |
| S2 | the same refusal's `{event.payload!r}` to a constant (message argument) | `test_the_malformed_row_refusal_quotes_the_payload_it_read`: four malformed payloads (no player list, a non-string room, a string, a frozenset), each message equal to `public regroup row is malformed: <the payload's repr>` |
| S3 | `MeetingManager.run`: `{sorted(regroup_ticks)}` to `{[]}` (message argument) | `test_the_manager_refusal_names_the_ticks_it_was_handed`: `{9, -1}` reads `[-1, 9]` and `{4, 2, True}` reads `[True, 2, 4]`, no model call made |
| S4 | `compose_resume_events`: `{len(meeting_events)}` to `{0}` (message argument) | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest`: the property's refusal `match` now ends `; got {len(meeting_events)}$`, over its generated one to three meeting events |

**Findings 2 and 3: the phase-21 counterfactual read a reset recording without the window (integrity; the
documentation lens and Codex P2).** Both are valid. At the merge base the script refused a `hub_with_grace`
recording through `compute_evidence_honesty` (the readers card: it "takes their thread-or-refuse behaviour").
This card lifted honesty's refusal with honesty's fix, and the script's own ledger (`_ledger_for`, which calls
`build_testimony_ledger` without the window) went on reading the recording. The verifiers reproduced it: 7
ledger calls over a fake reset set, 0 carrying the window, and `--sets` exiting 0 with a table.

- **The repair.** `scripts/counterfactual_phase21.py::_refuse_the_meeting_reset` reads each recording's settings
  (`recorded_experiment_config`) and raises `SystemExit`, naming the setting and the seed, when the reset is not
  the default `"preserve"`. `_walk` calls it after the empty-set check and before `roles_by_seed`, so it runs
  before the walk re-derives anything, in both modes. No evidence semantics change, and a recording without the
  reset walks exactly as before (`tests/scripts/test_counterfactual_phase21.py` 105 passed).
- **The ruling.** The round-3 PR asked the orchestrator this question. The round-4 dispatch forwards the
  findings with their three options (a named refusal, threading, or a ruled limitation) and the instruction to
  repair each finding; it carries no separate ruling text. The repair is the first option, the one the
  orchestrator's ruling of 2026-09-27 chose for the analogous FROZEN reader (`eval/deception_instruments.py`),
  and it restores the script's outcome at the merge base (a named refusal and no table; honesty refused there
  after the walk, the refusal now comes before it). It edits a file outside the decision memo's 3.2 map;
  no Stage-B card writes that file. The PR's Questions asks the orchestrator to confirm the disposition and to
  record the map row, as `cb0a4cfc` did for the three readers. Threading was not chosen: the golden walk's
  `ReconstructedMeeting` does not carry the ticks, and the script prices the Wave-2 levers over lever-OFF
  committed bytes, which no Stage-B recording is; the refusal leaves its evidence semantics unchanged.
- **The strength stated.** The equality box's guarantee now holds as written: every production caller that can
  read a reset recording either receives the regroup ticks or refuses by name. The FROZEN concluded lab probes
  in `experiments/lab/` are lab code, not production callers, and stay the PR's question.
- **Proof** (`tests/eval/test_regroup_instruments.py`, each with `roles_by_seed` and `walk_replay_meetings`
  replaced by a sentinel raised where the walk would begin):
  `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` (`walk_set`, seed 1000);
  `test_the_phase21_command_refuses_a_reset_set_staged_under_replays` (`main(["--sets", "staged/9p2i"])` with the
  script's repository root pointed at a checkout whose only set is the reset recording);
  `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` (seed 1001 among `preserve` seeds); and
  `test_the_phase21_refusal_names_the_reset_and_nothing_else` (no settings, an explicit `preserve`, and two other
  wave settings each reach the walk).
- **The command.** A fake `hub_with_grace` set (seeds 1000-1002, 7 meetings, recorded with
  `tests/_helpers/scripted_meeting.record_game` into the scratchpad) staged as `replays/zz_r4_tmp/9p2i`:
  `uv run python scripts/counterfactual_phase21.py --sets zz_r4_tmp/9p2i` exit 1, printing `the phase-21
  counterfactual does not read the recorded meeting_reset='hub_with_grace' (seed 1000): its testimony ledger does
  not apply the regroup window`. The staged directory was removed and `git status` is clean under `replays/`.
- **Red before.** The six phase-21 test items against the script's pre-round bytes (swapped in from `711e488f`, restored
  from a byte copy, sha256 equal): `pytest tests/eval/test_regroup_instruments.py -k phase21` exit 1, 3 failed
  and 3 passed. Red: the three reset cases (the walk began). Green, as controls must be: the three
  `names_the_reset_and_nothing_else` cases. With the round's bytes: 6 passed.

**Finding 4: the round-3 counts (documentation).** Valid. `uv run pytest --collect-only -q
tests/eval/test_regroup_instruments.py` collects 26 items at `1ad1b57c` and 40 at `711e488f`: 14 new items, 9 red
and 5 green controls in the red-before run (10 failed, 31 passed with the contract test). The three sentences
now read 14 new instrument tests, 26 tests already in the file, and 16 added in total (14 there, 2 in
`tests/orchestrator/test_meeting_reset_coherence.py`).

**The bounded mutation pass**, over the spans this round changed and the four spans the findings named, with the
listed classes only, plus three neutering probes of the new production lines. Each mutant replaced one snippet
(its count asserted to be exactly one), ran the six non-golden card suites (`tests/orchestrator/test_meeting_reset_coherence.py`,
`tests/agents/test_regroup_memory.py`, `tests/meetings/test_regroup_relevance_window.py`,
`tests/eval/test_regroup_instruments.py`, `tests/engine/test_meeting_reset_experiment.py`,
`tests/orchestrator/test_public_regroup_evidence.py`, `-x -n 8`), and was restored from a byte copy: 18
restored, sha256 equal, and `git status` showed only this round's edits. 18 probes, 17 red on the first run;
the one that came back green is equivalent.

| Id | Class | File | First red test |
| --- | --- | --- | --- |
| S1 | f, drop a tuple member | `agents/memory/store.py` | `test_a_public_row_listing_its_players_reads_as_the_tuple_row_does` |
| S2 | e, message argument | `agents/memory/store.py` | `test_the_malformed_row_refusal_quotes_the_payload_it_read[payload0]` |
| S3 | e, message argument | `meetings/manager.py` | `test_the_manager_refusal_names_the_ticks_it_was_handed[ticks0-[-1, 9]]` |
| S4 | e, message argument | `orchestrator/replay.py` | `test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` |
| P-seeds-first | b, the first seed only | `scripts/counterfactual_phase21.py` | `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` |
| P-none-inverse | c, `is not None` to `is None` | same | `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` |
| P-cmp-is-not-none | c, `!= "preserve"` to `is not None` | same | `test_the_phase21_refusal_names_the_reset_and_nothing_else[settings2]` |
| P-cmp-is-none | c, `!= "preserve"` to `is None` | same | `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` |
| P-cmp-inverse | c, `!=` to `==` | same | `test_the_phase21_command_refuses_a_reset_set_staged_under_replays` |
| P-reset-const | d, the reset read to `"preserve"` | same | `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` |
| P-seed-const | d, the seed read to `0` | same | `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` |
| P-msg-seed | e, message seed to `1000` | same | `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` |
| P-msg-value | e, message value to `'hub_with_grace'` | same | green, equivalent: the branch runs only when the value is not `"preserve"`, and `RecordedExperimentConfig.meeting_reset` admits one other value, `"hub_with_grace"`, so the message bytes are equal |
| P-order | g, the refusal moved after `roles_by_seed` | same | `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` |
| P-source-literal | h, the recorded settings to `None` | same | `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` |
| N-P-call | neuter, the call in `_walk` removed | same | `test_a_phase21_set_with_one_reset_recording_is_refused_at_that_seed` |
| N-P-body | neuter, the helper returns at once | same | `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` |
| N-P-raise | neuter, the raise removed | same | `test_the_phase21_counterfactual_refuses_the_reset_by_name_before_walking` |

**Verification of this round's code and tests.** Every gate below ran on the bytes the commit that first carries
this subsection holds, in a bare shell with 0 `AILIBI_*` exports, each exit code captured from the process and
never through a pipe; `scripts/validate_task_docs.py` and `scripts/check_doc_facts.py` re-ran after this
subsection was written.

| Command | Result |
| --- | --- |
| the card's seven test files (`-q -n 8`) | exit 0: 212 passed |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |
| `bash scripts/verify_samples.sh <set>`, once per set | exit 0 each: s9 50, s4 50, c9 150, c4 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `build_sample_report.py` on the fake `hub_with_grace` set above: write, then `--check`, then `--baseline-out` | exit 0 each; 3 games, 7 meetings, 0 ejections |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, consistent |
| `uv run python scripts/gen_frontend_types.py --check`, `scripts/check_doc_facts.py`, `scripts/validate_task_docs.py` | exit 0 each (88 work cards) |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run pytest tests/scripts/test_counterfactual_phase21.py -q -n 8` | exit 0: 105 passed |
| `uv run pytest -m campaign -n auto --dist loadfile -q` | exit 0: 336 passed |
| `git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl'`, sorted and counted; `git grep -l` for the files | 956 `"meeting_reset":"preserve"`, in 101 files |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 330; 27,303,776, the row as it stands |
| `scripts/build_demo_bundle.py`, at an export of `cb0a4cfc` and at this round's bytes | exit 0 each, 156 JSON files baked; `diff -r` of the two `data/` trees prints nothing (exit 0). Both read the branch's `replays/samples` (the export's archived `replays/` is `diff -rq` identical), and the export's build imported the export's own `api/` and `orchestrator/` |
| `npm --prefix frontend test`; `npm --prefix frontend run e2e` | exit 0: 559 passed; 13 passed, 3 skipped (the media-capture journeys) |
| `git diff --stat 711e488f -- engine/ frontend/ api/ observation/ replays/ eval/off_menu.py orchestrator/experiment_config.py eval/gameplay_census.py eval/leak_scan.py api/schemas.py docs/architecture.md audits/ tests/fixtures/` | empty |

`bash scripts/check.sh` ran once, at `dbb32f6c`, the commit that first carries this subsection, in a bare shell with
0 `AILIBI_*` exports and its exit code captured from the process: exit 0 (ruff clean, 546 files formatted,
`lint-imports` 4 kept 0 broken, task docs with 88 work cards and prompts valid, mypy clean on 517 files, pytest
9667 passed, 20 skipped, 3 xfailed, the round's 13 new items above round 3's 9654; frontend lint, types, 559
vitest tests and build). The commit after it changes only this paragraph; `scripts/validate_task_docs.py` and
`scripts/check_doc_facts.py` re-run at that head.

**Changed test expectations.** One, stricter: the refusal `match` in
`test_the_helper_keeps_exactly_the_kills_and_vents_and_counts_the_rest` now also pins `; got
{len(meeting_events)}$`. The round adds 13 test items in 7 functions: 5 in `tests/agents/test_regroup_memory.py`
(the four-payload refusal and the list row), 2 in `tests/meetings/test_regroup_relevance_window.py` and 6 in
`tests/eval/test_regroup_instruments.py` (the four phase-21 functions, one of them with three controls). No test
is weakened, skipped or deleted.

**Closing greps.** `git grep -n -i -E "gains no refusal|thread-or-refuse|takes their (thread|behaviou?r)|without
the window if pointed|reset recording without the window|read a reset recording at the no-regroup" --
':!tasks/phase-*' ':!agent_prompts' ':!audits'`, at the head. The hits about the phase-21 script are this card's
round-3 record (annotated in place with its round-4 outcome), this subsection's own account and grep, the card's
stop-and-ask rule under Constraints, and `tasks/work/stage-b-readers.md:634` and `:890-891`, that card's record
of the script before this card, which is not rewritten. The remaining hits name the spine's thread-or-refuse
mechanism, which is unchanged. `git grep -n -i -E
"counterfactual_phase21|phase-21 counterfactual" -- docs README.md` prints nothing, so no live document states the
script's reading of a reset recording.

**Limitations.**
- The phase-21 disposition awaits the orchestrator's confirmation and its map row (the PR's Questions). If the
  orchestrator rules for threading instead, this refusal is the thing to replace.
- The FROZEN concluded lab probes named in round 3 still call `detect_contradictions` without the window if
  pointed at a reset recording; they are lab code, and the question stands.

### Review corrections, round 5 (2026-09-27)

The repair of the two blocking findings the correctness lens raised on round 4. Commits: the commit that first
carries this subsection (the planted cases, the contract paragraph, one comment and this record) and the card
commit after it, which records the `check.sh` run. `main` is still `cb0a4cfc`, the round-3 merge base, so
nothing is merged. No `audits/` or `tests/fixtures/` byte moves, so the `audits/` row stays (330 files,
27,303,776 tracked bytes, re-read below). Status stays `done` and the `tasks/README.md` sentence is unchanged.

**Finding 1: the walk's resume phase read (correctness).** Valid. `eval/replay_walk.py::_walk_replay` composes
the resume events before it stops at game over, so `meeting_regrouped(experiment, phase_after=state.phase)` is
load-bearing there. After a meeting that ends a reset game the phase is `GAME_OVER`, no regroup ran, and the
meeting's own events (the ejection's game-over event) pass through. With the read replaced by `"PLAY"`, the
helper is told a regroup ran and refuses the non-empty meeting events. The loader and the golden stop at game
over before they compose, so their phase reads are equivalent. No test recorded a reset game whose meeting ends
it (the fake provider ejects nobody), so the constant stayed green.

- **The planted case.** `_EjectingRunner` is the test's own runner that ejects the only impostor at the first
  meeting. Every ballot it casts now names the impostor with full confidence, so the ballots tally to the
  ejection the result states and the game can be recorded. `_button_game` takes an optional replay path, `None`
  by default, so every other caller runs as before.
  `test_a_recorded_meeting_that_ends_the_game_walks_to_its_terminal_meeting` records the 5-player reset game at
  seed 4 into `tmp_path` through `HeadlessGame.run` and walks it under the evidence-honesty and funnel profiles.
  Each walk yields one `MeetingApplied` in phase `GAME_OVER` whose post events end with the game-over event,
  then `WalkComplete` whose terminal tick is the meeting's.
- **Red under the mutant.** `M-WK-compose-phase` below: both parametrised cases are red (2 failed). At the
  round's bytes both pass.
- `test_a_meeting_that_ends_the_game_under_the_reset_resumes_nothing` keeps every assertion; only its runner's
  ballots changed.

**Finding 2: the fold under evidence version 2 (correctness).** Valid. `render_for_prompt` folds sightings only
when the evidence version is not 2. Version-2 observations also carry no sighting key, the key the fold groups
on. So a version-2 memory under the reset renders the notice and the route step, and keeps each regroup sighting
on its own row, as it keeps the spawn sightings. It is now stated at that strength:

- `docs/observation-contract.md`, "The announced regroup": the fold is on the default evidence path; evidence
  version 2 folds no sightings.
- This card's Decisions ("Sabotage survives the reset") and Limitations lines, corrected in place with a round-5
  note; the PR body's Summary and Decisions.
- `agents/memory/store.py`: one comment at the fold's version gate, and no code change;
  `tests/agents/test_regroup_memory.py`: the module docstring.
- Tests in `tests/agents/test_regroup_memory.py`:
  `test_under_version_2_the_regroup_sightings_keep_their_own_rows` checks the notice line and the route step are
  present, with no regroup fold line and no spawn fold. The regroup-tick rows equal those rendered without the
  row, one per other player. `test_only_version_2_leaves_the_spawn_group_unfolded` checks the default path and
  version 1 fold the spawn group and version 2 does not.
- The Constraints sentence the finding names ("so they also apply to evidence-version-2 memories", under
  "Decisions this card makes") is the orchestrator's contract text; the PR's Questions asks the orchestrator to
  amend it. The Acceptance box "Legible memory" holds as written: it states the fold and the difference the row
  makes on the default path, the path its tests render.

**The bounded mutation pass.** It covers the span finding 1 names (the walk's resume composition) and the spans
finding 2 names (the fold's version gate and its regroup argument, the notice's version gate, the route's regroup
argument), with the listed classes only. Each mutant replaced one snippet (its count asserted to be exactly
one) and ran the targeted suites with `-x -n 8`. For the walk: `tests/orchestrator/test_meeting_reset_coherence.py`
and `tests/eval/test_replay_walk.py`. For the store: `tests/agents/test_regroup_memory.py`,
`tests/agents/test_memory_rendering.py` and `tests/orchestrator/test_meeting_reset_coherence.py`. Each file was
restored from a byte copy (18 restorations, sha256 equal each time), and `git status` showed only this round's
edits. 14 mutants, 11 red on the first run. Of the three that came back green, one is killed by a new planted
case and two are equivalent:

| Id | Class | File | First red test |
| --- | --- | --- | --- |
| M-WK-compose-phase | d, the phase read to `"PLAY"` | `eval/replay_walk.py` | `test_a_recorded_meeting_that_ends_the_game_walks_to_its_terminal_meeting[funnel-instrument]` (both cases red) |
| M-WK-compose-settings | h, the recorded settings to `None` | same | `test_the_four_readings_agree_at_every_meeting_open` |
| M-WK-compose-meeting-events | b, the meeting's events swapped for the trigger tick's | same | `test_the_readers_name_the_maps_meeting_room` |
| M-WK-compose-trigger-events | b, the trigger tick's events swapped for the meeting's | same | `test_withholding_the_window_or_the_resume_at_a_reader_breaks_agreement[walk-resume]` |
| M-WK-break-first | g, the game-over break moved above the composition | same | green, equivalent: the walk reads neither `last_events` nor `resumed_meeting_ticks` after it breaks, so composing before or after the break yields the same events |
| M-ST-fold-gate-inverse | c, `!= 2` to `== 2` | `agents/memory/store.py` | `test_the_fold_expects_the_players_the_row_gathered_not_the_known_roster` |
| M-ST-fold-gate-not-none | c, `!= 2` to `is not None` | same | `test_the_fold_expects_the_players_the_row_gathered_not_the_known_roster` |
| M-ST-fold-gate-none | c, `!= 2` to `is None` | same | first green (also over the wider memory suites, 1862 passed); killed by `test_only_version_2_leaves_the_spawn_group_unfolded[1-True]` |
| M-ST-fold-gate-dropped | a, the version gate dropped | same | green, equivalent: version-2 observations carry no sighting key (`_build_v2_observations`), so `_coalesce_sightings` passes every one through unchanged and the render sorts them afterwards |
| M-ST-fold-regroups-empty | b, the fold's regroups to `()` | same | `test_the_fold_expects_the_players_the_row_gathered_not_the_known_roster` |
| M-ST-notice-gate-none | c, `!= 1` to `is None` | same | `test_under_version_2_the_regroup_sightings_keep_their_own_rows` (the one red test: the round's new case) |
| M-ST-notice-gate-inverse | c, `!= 1` to `== 1` | same | `test_the_default_path_renders_the_notice_whenever_the_row_exists` |
| M-ST-notice-gate-dropped | a, the notice's version gate dropped | same | `test_version_1_renders_no_notice_even_beside_a_row` |
| M-ST-trail-regroups-empty | b, the route's regroups to `()` | same | `test_the_route_states_the_regroup_as_its_own_step` |

The fold's version gate predates this card (this card added only its regroup argument). No test pinned that
version 1 folds the spawn group, so `M-ST-fold-gate-none` survived. The finding names that span, so the round
kills it rather than naming it pre-existing. The restorations: 14 in the first run, 1 in the wider run and 3 in
the rerun of the three greens, where `M-ST-fold-gate-none` came back red and the two equivalents came back green.

**Verification of this round's code and tests.** Every gate below ran on the round's code and test bytes, in a
bare shell with 0 `AILIBI_*` exports. Each exit code was captured from the process, never through a pipe.
`scripts/validate_task_docs.py` and `scripts/check_doc_facts.py` re-ran after this subsection was written.

| Command | Result |
| --- | --- |
| the card's seven test files (`-q -n 8`) | exit 0: 218 passed (212 at round 4, plus the round's 6 items) |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |
| `bash scripts/verify_samples.sh <set>`, once per set | exit 0 each: s9 50, s4 50, c9 150, c4 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `build_sample_report.py` on a fake `hub_with_grace` set (seeds 1000-1002, 7 meetings, recorded with `tests/_helpers/scripted_meeting.record_game` into the scratchpad): write, then `--check`, then `--baseline-out` | exit 0 each |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, consistent |
| `uv run python scripts/gen_frontend_types.py --check`, `scripts/check_doc_facts.py`, `scripts/validate_task_docs.py` | exit 0 each (88 work cards) |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 63 checks, 51 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run pytest -m campaign -n auto --dist loadfile -q` | exit 0: 336 passed |
| `git grep -h -o '"meeting_reset": *"[a-z_]*"' -- '*.jsonl'`, sorted and counted; `git grep -l` for the files | 956 `"meeting_reset":"preserve"`, in 101 files |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 330; 27,303,776, the row as it stands |
| `scripts/build_demo_bundle.py`, at an export of `cb0a4cfc` and at the round's bytes | exit 0 each, 156 JSON files baked; `diff -r` of the two `data/` trees prints nothing (exit 0). Both read the branch's `replays/samples` (the export links the branch's `replays/`), and the export's build imports the export's own `api/` and `orchestrator/` |
| `npm --prefix frontend test`; `npm --prefix frontend run e2e` | exit 0: 559 passed; 13 passed, 3 skipped (the media-capture journeys) |
| `git diff --stat b590eb17` | five files: `agents/memory/store.py` (one comment, no code), `docs/observation-contract.md`, this card and the two test files; nothing under `engine/`, `frontend/`, `api/`, `eval/`, `observation/`, `orchestrator/`, `meetings/`, `scripts/`, `replays/`, `audits/` or `tests/fixtures/` |

`bash scripts/check.sh` ran once, at `c3edd856`, the commit that first carries this subsection, in a bare shell
with 0 `AILIBI_*` exports and its exit code captured from the process: exit 0 (ruff clean, 546 files formatted,
`lint-imports` 4 kept 0 broken, task docs with 88 work cards and prompts valid, mypy clean on 517 files, pytest
9673 passed, 20 skipped, 3 xfailed, the round's 6 new items above round 4's 9667; frontend lint, types, 559
vitest tests and build). The commit after it changes only this paragraph; `scripts/validate_task_docs.py` and
`scripts/check_doc_facts.py` re-run at that head.

**Changed test expectations.** None is weakened, skipped or deleted. Two test helpers changed in
`tests/orchestrator/test_meeting_reset_coherence.py`: `_EjectingRunner`'s ballots now name the impostor, and
`_button_game` takes an optional replay path. The round adds 6 test items in 3 functions:
`test_a_recorded_meeting_that_ends_the_game_walks_to_its_terminal_meeting` (2) in that file, and
`test_under_version_2_the_regroup_sightings_keep_their_own_rows` (1) and
`test_only_version_2_leaves_the_spawn_group_unfolded` (3) in `tests/agents/test_regroup_memory.py`.

**Closing greps.** `git grep -n -i -E "also apply to evidence|apply to evidence-version-2|version-2 memor|renders?
them too|it folds the sightings|fold(s|ed)? .{0,30}under (evidence )?version 2|under (evidence )?version 2.{0,40}fold"
-- ':!tasks/phase-*' ':!agent_prompts' ':!audits'`, at the head. The hits:
- this card's Constraints sentence, the orchestrator's (the PR's Questions);
- this card's Decisions and Limitations lines as corrected, which say the notice and the trail step render under
  version 2 and the fold does not;
- this subsection's own quotation and grep.
`docs/observation-contract.md` no longer says the memory folds the regroup wherever the row exists.

**Limitations.**
- The Constraints sentence stands until the orchestrator amends it.
- The recorded game-ending case is a runner of the test's own: the fake provider ejects nobody, so no fake-provider
  reset game ends at a meeting. The record is the first real reading.
