# Instruments and reconstructors read the recorded arms, including the one-reply follow-through (B3)

**Status:** done

## Outcome

Stage B records every switch as a `RecordedExperimentConfig` field and lands its 50 seeds in a
candidate directory, so each recording carries its own arms and every reader must take them from
the recording, never from the shell. Today eight walk profiles refuse any experiment-stamped
recording, the prompt-byte golden walks two fixed directories with default meeting settings, the
rubric extractor re-simulates blind to the config, and a reader that forgot the physical vent
witness rule would still pass every hash check.

After this card, every instrument and reconstructor that re-reads a recording does one of two
things for every recorded field: it threads the field through the spine's one helper, or it
refuses the recording by name before its first advance. Concretely:

- kill-craft, the information funnel, solvability, the win-condition self-check and evidence
  honesty accept the wave's fields after a written per-instrument review; evidence honesty rebuilds
  impostor decisions with the policy the recording names, not the default one;
- the prompt-byte golden walks any directory with the recorded evidence profile, reset, trigger
  settings and arm stamps, and `tests/_helpers/committed.py` threads the same config;
- `walk_chain` accepts exactly the one reply the bounded-rebuttal selector picks (B3), and a new
  scripted-client helper records a real rebuttal turn offline, which the fake provider cannot do;
- the process scorecard gains a write-nothing `--set-dir` mode for a candidate column;
- the rubric extractor, off-menu, the anchor study, the surrogate and conviction tables and the
  watchability referee refuse experiment recordings by name, and tests pin each refusal.

B3 is recording `bounded_rebuttal_version=1` alone: no template changes, `reporter_reasoning` stays
OFF, and this card is B3's whole follow-through. No agent behaviour changes, no committed byte moves,
and nothing is re-recorded.

## Evidence

**Rulings relied on.** The owner, 2026-09-24, verbatim:
- "We should implement stage B"
- "B3. Allow one reply for the opener"
- "Hold off on ML as D suggests until gameplay is finished."
- "Tour fix can be deferred to after gameplay is finished"

The orchestrator's rulings, made under the owner's delegation of 2026-09-24 (rulings 6 to 10 and
13, "What do you think is best?"), in the Stage-B decision memo
(`~/.claude/projects/-Users-danielkeinan-projects-AiLibi/stage-b-2026-09-24/decision-memo.md`):
- R7: "a vent action is witnessed by the living non-vented occupants of the room where it
  physically happens, the entry by the room entered from and the exit by the room surfaced into".
- The B3 rider: "B3 adopts bounded_rebuttal_version=1 ALONE, reporter_reasoning does NOT ride
  along".
- R13: the gameplay census is a separate report; no scorecard cell; no D1 amendment.
- Decision 0.3 item 7: B3 has no behaviour code, so its follow-through folds into this card.
- Decision 0.3 item 10: the event-level walks are widened; the policy-re-running and frozen
  instruments keep refusing.

The dated 2026-09-24 addendum to `tasks/direction-2026-09-19-process-over-outcome.md` section 12,
which lands as a `docs:` commit before wave 1, names every wave field. This card cites it.

**The partial-record principle, as it binds this card.**
- Only `replays/samples/9p2i` is ever re-recorded, seeds 0-49, and only into a candidate directory
  (`replays/candidates/stage-b-r1/9p2i/`), by the record card.
- Every switch is a `RecordedExperimentConfig` field, default-OFF and omitted from the payload at
  its default.
- Every committed recording, derived view, fixture, gate and doc fact keeps verifying
  byte-identically.
- No registry prompt bump.
- Role-correctness is reported and never a gate.
- Nothing pushes an agent toward the correct answer.
- The meeting layer labels and never rewrites.

**What refuses today.** Citations are `path:line` at `e886b663`. A3 and the spine merge first and
move lines, so re-anchor each one by its named symbol at dispatch.
- `eval/replay_walk.py:505-515` refuses a recorded config, or a temporal version, unless the profile
  opts in. Eight profiles do not:
  - kill-craft `eval/kill_craft.py:527`, funnel `eval/funnel.py:254`, solvability
    `eval/solvability.py:698`, win-condition `eval/win_condition_selfcheck.py:205` and evidence
    honesty `eval/evidence_honesty.py:2605` (this card);
  - validity `eval/validity.py:508` and kill-gift `eval/balance_eval.py:914` (the record-plumbing
    card);
  - the watchability referee `eval/watchability.py:1544`, which keeps refusing.
- Modules that reuse a profile this card flips: `eval/deception_instruments.py` (the funnel's walk),
  `scripts/counterfactual_phase20.py:99`, `tests/_helpers/committed.py:467` and
  `tests/agents/test_reported_testimony.py:44` (the honesty profile).
- The golden (`tests/meetings/test_prompt_byte_golden.py`) walks the fixed `_SAMPLE_SETS`
  (`:174-177`), advances with engine defaults (`:680`, `:1298`), applies meetings without the reset
  (`:723-725`), builds its manager with no evidence profile (`:447-460`), rebuilds the trigger with
  defaults (`:781`), and its window test asserts every stamp is a live default (`:1445-1467`). The
  investigation's fake probes found a rebuttal-ON recording whose rebuttal call goes unconsumed and
  a reset recording whose meeting post-hash mismatches (`partial_record.md` section 5, row 4).
- Evidence honesty's I-11 fold re-invokes `live_impostor_policy` (`eval/evidence_honesty.py:233-236`)
  by default, in `compute_evidence_honesty` (`:896-970`) and `reconstruct_impostor_decisions`
  (`:1238-1282`). The recorded arm's policy is the one `build_default_agent_factory`
  (`orchestrator/game.py:4437-4462`) builds; `TacticalAgent.tactical_experiment_options` (`:3628`)
  exposes its options; `recorded_agent_factory_kind` (`orchestrator/replay.py:866`) says whether
  the recording used the built-in agents.
- The rubric extractor (`audits/workflows/extract_gameplay_facts.py:2150-2182`) checks only the
  substrate stamp and re-simulates with no config (`:2235`, `:2751`). It runs only when the recorder
  targets `replays/samples/9p2i` (`scripts/refresh_samples.sh:1049`).
- Kept refusals: off-menu (`eval/off_menu.py:359-361`, FROZEN at `:1-2`), the anchor study
  (`training/anchor_study.py:443-447`), the surrogate meeting table
  (`training/surrogate/dataset.py:1025-1026`), the conviction table through `build_meeting_table`
  (`training/conviction/dataset.py:649`), and the referee.
- The scorecard folds only the four committed sets (`eval/process_scorecard.py:1883-1926`), and
  `load_set_inputs` names each source `replays/<parent>/<name>` (`:866-869`), which misnames a
  directory two levels below `replays/`.

**Why R7 needs its own proof.** Vent witness sets live in events, not in `WorldState`
(`engine/rules.py:146-156`). A reader that walks a physical-rule recording without the rule
reproduces every state hash and derives the wrong vent observations. The investigation's prototype
measured 221 of 221 hashes equal with 4 of 28 exits different (decision memo section 1, item 3;
B0's reader gate tests the rule end to end). The readers that fold vent witnesses are the
funnel (`eval/funnel.py:428-437`) and perception (`observation/service.py:651-663`), which evidence
honesty, the golden and `committed.py`'s `vent_witness_records_for_meeting` read.

**B3 today.**
- `select_bounded_rebuttal` (`meetings/rebuttal.py:17-55`) picks the earliest unanswered new charge
  against a living player who has already spoken.
- The manager appends one `reply` turn after the roll call (`meetings/manager.py:1508-1539`).
- `walk_chain` (`meetings/transcript.py:484-567`) raises on any non-`opt_in` turn after the chain.
  Its only callers are tests (`tests/meetings/test_manager.py`, `tests/meetings/test_transcript.py`).
- The fake provider emits no claims (`llm/fake_provider.py:193`), so it never fires a rebuttal. The
  scripted precedent is `ScriptedReplyClient` and `run_reply_scenario` in
  `eval/reasoning_evidence.py`, pinned by `tests/meetings/test_reasoning_evidence.py:106-114`.
- No committed recording carries the field, and `tests/conftest.py` clears every `AILIBI_*` export,
  so a test enables the arm only through a declared config.

**The deviation from ruling 4's words.** Version 1 is not opener-only. It gives the turn to the
target of the earliest unanswered new charge, whatever that player's seat or role.
- Projected on s9's recorded transcripts it fires 144 times: 123 to the opener and 21 to
  non-openers, 19 of them impostors and 2 other crewmates.
- Pooled over the four sets it fires 673 times: 548 to the opener, 113 to impostors and 12 to other
  crewmates. The opener loses the slot in 13 of the 561 meetings where it was accused (s9: 2 of
  125). Today the opener answers 0 of 561.
- These are count-only figures from the rebuttal investigation's scratch census
  (`rebuttal_and_body_handle.md` section 3), not from a committed instrument. Re-measure them at
  dispatch with a count-only projection of `select_bounded_rebuttal` over the recorded transcripts
  before restating them, and print no transcript text.

## Acceptance

- [x] Review correction (round 3): the settings refusal reads a recording's settings off a
  `TickOpened` only, and a stream led by any other event passes it through. In
  `tests/eval/test_recorded_arm_readers.py`,
  `test_a_leading_event_that_is_not_a_tick_row_passes_and_the_tick_row_refuses` leads a real walk
  with a `WalkComplete`, a `TickAdvanced` and a `MeetingOpened` in turn: each passes through
  untouched and the refusal, matched whole, arrives at the `TickOpened` after it.
  `test_an_empty_replay_walks_to_the_vacuous_self_check` walks an empty replay to its
  `WalkComplete` alone and pins the vacuous win-condition check, and
  `test_the_first_tick_row_speaks_for_the_recording` passes a later tick row carrying an unread
  setting. The verifier's probe V4 (the `TickOpened` filter dropped) and V5 (the first-row guard
  dropped) are red: Results, "Review corrections, round 3".
- [x] Review correction (round 3): the physical-witness leg of the event-level test runs, B0 (#485)
  having merged before this card's last merge of `main` (`fb9d2e31`). A fake game recorded under
  `vent_witness_rule="physical"` joins the arms every widened reader, evidence honesty and both
  reconstructors verify, so every recorded-arm refusal accepts it.
  `test_on_a_physical_recording_the_stand_in_and_the_rule_reach_every_advance` shows the stand-in
  and the recorded rule reaching every advance of each of the eight readers, with the stand-in
  moving no output; a helper that withholds the rule is told apart only by the rule the engine
  received. `test_withholding_the_physical_rule_changes_what_a_vent_folding_reader_folds` and
  `test_the_physical_recording_holds_exits_the_rule_changes` hold the folds and non-vacuity. Probes
  P1 and P2 (the golden's and the walk's helper handed no config) are red.
- [x] Review correction (round 2): `walk_chain`'s missing-pick and extra-turn refusals name the
  recorded pick and turn, pinned whole. `tests/meetings/test_transcript.py::TestWalkChainBoundedRebuttal`
  runs every case over two shapes whose pick speaker, charge and reply index all differ (`p-1`,
  `m-1:turn-1`, turn 4; `p-3`, `m-1:turn-2`, turn 3) and matches each message in full, and
  `test_walk_chain_accepts_exactly_the_selected_rebuttal` matches them in full with the generated
  values. The verifier's two probes (the pick's speaker set to `'p-1'`, the extra turn's index set
  to 5) are red: MA1 and MA16 in Results, "Review corrections, round 2".
- [x] Review correction (round 2): the settings, honesty and scorecard refusals name the values they
  were given, pinned whole. In `tests/eval/test_recorded_arm_readers.py`: formats 2 and 3 with two
  readers (`test_a_later_settings_format_is_refused_with_the_reader_and_the_format`), the reviewed
  field list joined in the unread-setting message for two lists
  (`test_refusing_unread_settings_names_the_reader_and_the_field`), a custom-factory recording at
  seeds 0 and 2 naming `headless-seed-0` and `headless-seed-2`, both policy labels and the real
  directory in the mixed-set raise. In `tests/scripts/test_process_scorecard.py`: the no-replay
  refusal names the real directory. Probes RS3, RS5, MA7, MA8 and MA10 are red.
- [x] Review correction (round 2): every message argument of `_check_bounded_rebuttal_tail` and of
  the no-setting tail refusal is pinned, the picked speaker and charge in the records-none message
  and the turn index, kind and speaker in the others, by the same two-shape class and property and,
  for the records-none message on a recorded game, by
  `tests/_helpers/test_scripted_meeting.py::test_the_same_script_without_the_setting_records_no_rebuttal`.
  Sixteen probes (MA1, MA12 to MA24 with MA15I and MA15E): fifteen red; MA15E is named equivalent.
- [x] Review correction (round 2): the outside-list refusal names its reader and fields
  (`test_a_field_list_outside_the_reviewed_set_is_refused_with_the_reader`, two readers), and the
  plain-copy scan asserts the real directory in the no-replay and mixed-policy refusals before
  replacing it with `DIR`. Probes MA6, RS2, H3 are red; MA8E is named equivalent.
- [x] Review correction (round 2): the `walk_chain` bullet in `meetings/transcript.py`'s module
  docstring now says the tail is opt-in turns except for the one selected rebuttal reply the
  recorded setting may add. Its closing grep, which now finds only the two corrected sentences, is
  quoted in Results.
- [x] Review correction: the committed-meeting walk and the golden walk every meeting of every arm
  that exists today, the meeting reset included, so a walk that stopped reading the reset (or any
  other readable setting) fails a positive case, not only a refusal case.
  `test_the_reconstructors_walk_every_meeting_of_every_arm_that_exists_today` (plain, workload,
  regroup reset, reset with a real rebuttal, observed risk with a real rebuttal),
  `test_the_reconstructors_walk_every_meeting_of_a_copy_carrying_the_pending_values` and
  `test_the_reconstructors_hand_the_recorded_witness_rule_to_the_engine_helper`, all in
  `tests/eval/test_recorded_arm_readers.py`. Dropping any one of the nine readable settings from
  either walk's list fails a case: 18 probes, all red (Results, "Review corrections, round 1").
- [x] Review correction: the plain-copy scan reads the two `--set-dir` parser refusals (the stderr
  the script prints, captured) and evidence honesty's mixed-policy raise, besides the settings
  refusals, the extractor's, the custom-factory raise and the help text it already read; each text
  is asserted to be the refusal it names, so none can scan clean by being empty.
  `test_the_copy_this_card_adds_carries_no_identifier`; "see Task 20.33" and "the R7 rule" planted
  into each of the three messages from a byte copy each turn it red (6 probes).
- [x] Review correction: every row of the B3 projection table, each set's meeting count included,
  and the pooled row are pinned by
  `tests/_helpers/test_scripted_meeting.py::test_the_rule_the_owner_is_asked_to_confirm_projected_on_the_committed_sets`,
  so `uv run pytest tests/_helpers/test_scripted_meeting.py -k projected` reproduces the whole table.
- [x] **Five profiles widened, each after a written review.** Kill-craft, the funnel, solvability,
  the win-condition self-check and evidence honesty set `supports_experiments=True`. Each declares,
  through the spine's thread-or-refuse mechanism, the fields it threads: at most the eight wave
  fields (`vent_witness_rule`, `vent_exit_policy`, `vent_entry_policy`, `meeting_reset`,
  `bounded_rebuttal_version`, `report_body_handle_version`, `ballot_kill_row_version`,
  `impostor_ballot_version`) plus `redistribution_policy`, at `format_version` 1.
  - Every other non-default field, format 2 or 3, and any temporal version stays refused. Each
    refusal pending a later card is named in the PR's Decisions, so that card can lift it.
  - Where a wave field changes something an instrument computes and the coherent fix belongs to a
    later card, that instrument refuses the field by name now, and the later card lifts the refusal
    with its fix. Example: B2 owns evidence honesty's `room_at` and clock alignment under the reset
    (decision memo section 2.3, item 5).
  - Kill-craft threads `meeting_reset` in this card and never refuses it pending B2: record
    plumbing's post-step walks a `hub_with_grace` fake recording through kill-craft, so that card's
    acceptance cannot wait on B2. Its proof below includes a `hub_with_grace` recording.
  - Enforced by the walk's refusal before the first advance.
  - Proof: each profile verifies an arms-ON fake recording of the fields it threads, with every hash
    checked. A planted recording carrying `crew_idle_policy="patrol"`, and one carrying
    `evidence_reasoning_version=1`, are each refused with an error naming the profile and the field.
  - Results holds one review paragraph per instrument, covering the modules that reuse its profile.
- [x] **R7 is a required keyword at every reader call site this card owns.** Each `advance_tick`,
  `apply_meeting_result` and `_build_meeting_trigger` call in the golden, `tests/_helpers/committed.py`
  and `tests/_helpers/scripted_meeting.py` passes the spine helper's engine arguments, the recorded
  `meeting_reset` and the recorded config explicitly. The vent witness rule then reaches each site
  as soon as B0 adds it to the helper, with no edit here and no engine default relied on (B0 keeps a
  default on `advance_tick`). Enforced by an AST test over those files. Proof: a planted module with
  a bare `advance_tick(state, actions, game_map=...)` call fails it.
- [x] **A planted event-level thread-or-refuse test for each reader.** The test monkeypatches the
  spine's engine-arguments helper to add one stand-in field, and replaces `advance_tick` with a
  double that accepts it and changes only the witness lists of vent exits: R7's shape, with state
  hashes unchanged and events different.
  - The readers are the five profiles, the golden's walk and `committed.py`'s walk. Each runs on one
    fake recording holding at least one vent exit, which the test asserts so the case cannot go
    vacuous.
  - Every hash still verifies, and the double saw the stand-in on every advance the reader drove.
  - The readers that fold vent observations change their output: the funnel, evidence honesty's
    perception, the golden's rendered memory and `vent_witness_records_for_meeting`.
  - Perturbed: bypassing the helper at any one reader's call site fails that reader's case. A
    stand-in field the helper does not thread is refused by name.
  - If B0 has merged before this card's last merge of `main`, the same test also runs on a fake
    `vent_witness_rule="physical"` recording.
- [x] **Evidence honesty rebuilds decisions with the recorded policy.** By default each game's
  impostor decisions are rebuilt with the policy its recorded config names.
  - With tactical arms: `ExperimentalImpostorPolicy` with the options that
    `build_default_agent_factory(experiment_config=...)` derives, read through
    `tactical_experiment_options` with no edit to `orchestrator/game.py`, and fed the same
    meeting-concluded hook the live loop calls. B1's values then arrive with no edit here.
  - Without a config: `live_impostor_policy`, byte-identically.
  - A block rebuilt with a recorded arm carries its own `policy_mode` label, never
    `live-policy-fold`. A recording whose `agent_factory_kind` is `custom` is refused by name.
  - Proof: on an `observed_risk` fake recording holding at least one exit where the two policies
    disagree, there are 0 mismatches with the recorded policy and more than 0 with
    `live_impostor_policy` passed explicitly; the test asserts the positive count. Every committed
    honesty pin stays green, and `scripts/measure_baseline.py --honesty` prints byte-identical
    output at the merge base and at the head.
- [x] **The golden reads any directory with its recorded config.** A public directory walk replaces
  the fixed-set entry.
  - The committed parametrization is the two sample sets plus every `replays/candidates/*/*/`
    directory holding replay files, discovered from a root a test can redirect. None exists at
    merge, so the parametrization does not change until the record card lands its candidate.
  - Per recording, the walk builds the manager from `profile_from_config(recorded)`, builds agents as
    `HeadlessGame` does for that config (the factory, then `bind_experiment`), applies meetings with
    the recorded reset, and rebuilds each trigger through `_build_meeting_trigger` with the recorded
    config. The temporal refusal (`:656`) stays.
  - Proof: the scripted rebuttal game re-renders byte-equal, with every recorded call consumed
    exactly once. Dropping the profile leaves the rebuttal call unconsumed and fails. Dropping the
    reset on a `hub_with_grace` fake recording fails the meeting post-hash. A planted candidate root
    is discovered and walked. The 25 cases collected at `e886b663` stay green on s9 and s4.
- [x] **Arm stamps resolve only on recordings that carry the arm.** `resolve_prompt_set` extends
  `_overlay_stamp_owners` to experiment-bound arms through
  `prompt_versions_for_set(name, experiment_config=recorded)`, over the spine's experiment-arm
  registry, which stays empty until B6. The window test accepts a stamp other than the live default
  only when it equals the arm stamp for that recording's own config. Proof: with a planted registry
  entry, a recording carrying the arm resolves, and the same stamp on a recording without the arm
  fails the window test. With the registry empty, every committed stamp resolves to the live
  default mapping.
- [x] **`walk_chain` accepts the selected rebuttal and nothing else.** It gains a keyword-only
  `bounded_rebuttal_version: Literal[1] | None = None`. `None` is the fail-closed reading, under which
  a trailing reply raises, so the existing callers in `tests/meetings/test_manager.py` (owned by A3,
  then B6) keep their meaning unedited.
  - Under 1, after the chain and the opt-in turns, it accepts exactly one trailing `reply` whose
    speaker and `reply_to` equal `select_bounded_rebuttal`'s pick on the turns before it. It raises
    when the selector picks and no reply is recorded.
  - Proof, planted: the selected tail passes. A wrong speaker, a wrong `reply_to`, two trailing
    replies, a trailing reply under `None`, and a missing pick each raise. With the equality check
    removed, the wrong-speaker case passes and its test fails.
  - The docstring describes the rebuttal case.
- [x] **The scripted rebuttal game.** A new `tests/_helpers/scripted_meeting.py` records a
  `HeadlessGame` into `tmp_path` from a declared config with `bounded_rebuttal_version=1`, using the
  spine's runner from a config and no environment export. A scripted client makes turn 1 accuse the
  opener. The helper is built so B6 can add ballot cases.
  - It loads through `ReplayLoader.load_replay` in a bare shell with `outcome_verified` true, and its
    meeting memory and belief frames build.
  - It passes the five widened walks, `walk_chain` under the recorded version, the golden and the
    scorecard's `--set-dir`. If A1 has merged, the census `--set-dir` also reads it.
  - It carries exactly one rebuttal, by the opener, replying to turn 1. The rebuttal's prompt
    contains the turn-1 charge; the test asserts this and never prints the prompt.
  - It stamps the default prompt versions, with `reporter_reasoning` false and no `<who_reported>`
    block in any prompt.
  - A second scripted meeting pins the deviation: the earliest unanswered new charge targets a
    non-opener, who gets the slot, and the opener gets none.
  - Perturbed: the same script without the field records no rebuttal, and `walk_chain` under
    version 1 then raises on the missing pick.
- [x] **The scorecard's `--set-dir DIR --json-stdout`.** `scripts/publish_process_scorecard.py`
  prints one set's scorecard to stdout, through the committed serializer with sorted keys, naming
  the directory's own repo-relative path as its source. It writes nothing.
  - It refuses `--check` beside it, `--set-dir` without `--json-stdout`, and a directory holding no
    replay files.
  - No cell is added (R13); role-correctness stays reported beside the rows.
  - `load_set_inputs` names every source `replays/<parent>/<name>`, which misnames a candidate, and
    `eval/process_scorecard.py` is B2's file, not this card's. The workaround lives in the publish
    script: it replaces the loaded `SetInputs.source` with the directory's true repo-relative path
    (`dataclasses.replace`) before folding, and a comment there names the loader behaviour it
    works around.
  - Proof: a fake set's output equals the in-process fold of the same directory; a listing of the
    repository and of the directory is identical before and after the run; a directory two levels
    below a planted `replays/` root prints its true path, and without the replacement it prints the
    misnamed one; each refusal fires.
  - On `replays/samples/9p2i` the output equals that set's entry in `docs/process-scorecard.json`.
    This is a Validation command, not a committed-set test walk.
- [x] **The rubric extractor refuses experiment recordings by name.** Before any re-simulation, a
  seed whose recording carries an experiment config raises `SystemExit`. The message names the seed
  and its recorded settings in plain words, and says the extractor reads only recordings made
  without them. Its acceptance of the rebuttal waits for adoption. Proof: the scripted rebuttal
  recording is refused with that message, not by a later extraction invariant, and an unstamped
  fake recording still extracts.
- [x] **The frozen and policy-re-running instruments keep refusing.** Off-menu, the anchor study,
  the surrogate meeting table, the conviction table and the watchability referee each raise their
  named refusal on an arms-ON fake recording before the first advance. None of their code changes.
  Proof: each case matches the refusal text, so a refusal that is removed and replaced by a later
  hash or reconstruction error fails it.
- [x] **The OFF path is byte-identical, and the bundle is unchanged.** No byte under `replays/`, and
  no derived report, fixture, prompt template, doc fact or ML artifact, moves. Enforced by the gates
  in Validation. Each gate is a byte comparison with its own planted failure: the golden's one-byte
  template perturbation (`:1690`), `build_sample_report --check`'s drift case and the scorecard
  `--check`'s. `api/replay_loader.py` imports `meetings/transcript.py`, so the demo bundle is built at
  the merge base and at the head, and `diff -r` between them is empty.
- [x] **The copy this card adds is plain.** Mechanism: a test scans every new refusal message and
  the `--set-dir` help text for task or audit identifiers (`Task \d`, `audit-`, and memo-style
  short ids such as `R7` or `B3`) and bare threshold arithmetic. Planted: a message containing
  "Task 20.33" fails the scan, and so does one containing "R7".
- [x] **The registry row follows the audit bytes.** This card edits
  `audits/workflows/extract_gameplay_facts.py`, so the `audits/` row of `docs/artifacts.md` (`:109`,
  26,635,440 tracked bytes / 329 files at `e886b663`) is recomputed with `git ls-files` as the last
  step, after the final merge of `main`. Mechanism: `test_every_counted_registry_row_matches_the_index`
  (`tests/scripts/test_verify_ml_evidence.py`, run by `check.sh`) and the offline
  `scripts/verify_ml_evidence.py`. Perturbed: with the row left stale after the extractor edit, that
  test fails; Results quotes the red run.
- [x] **The deviation goes to the owner.** The PR's Decisions state v1's beneficiaries with the
  re-measured counts from Evidence. Its Questions ask the owner to confirm v1, or to ask, before the
  record card, for an opener-only value under a new `bounded_rebuttal_version`. That would be new
  selector code with planted tests, and it would land before the record card. Enforced by the
  deviation case in the scripted helper, which pins the rule the owner is asked to confirm.

## Constraints

**Wave and order.**
- Card 4 of the memo's section 3.1, wave 2.
- It starts once the spine (`tasks/work/stage-b-arm-spine.md`) has merged. The spine follows A3
  (`tasks/work/docs-truth-typed-trigger.md`) and the direction addendum.
- It runs beside `tasks/work/stage-b-record-plumbing.md` and `tasks/work/vent-witness-physical.md`
  (B0), in separate worktrees. It shares no file with B0. With record plumbing it shares
  `tests/_helpers/committed.py` and `docs/artifacts.md`, both serial: this card merges first, and
  plumbing edits each only after this card has merged.
- It merges before record plumbing, which merges after it and A1. It also merges before
  `report-body-handle` (B4) and `meeting-reset-coherence` (B2), which start only after it merges.
- It is on the critical path: A3, then the spine, readers, B2, B6, B5.
- A1 (`tasks/work/gameplay-census.md`) is unordered against it, except in `tests/_helpers/committed.py`
  and `docs/artifacts.md`, where A1 writes first (see below).

**What it takes from the spine**, used and not re-implemented: the field-layer classification; the
engine-arguments helper and the walk's thread-or-refuse declaration; `profile_from_config` and the
meeting runner built from a config; the `report_body_handle_version` keyword on
`_build_meeting_trigger`; the empty experiment-arm stamp registry and
`prompt_versions_for_set(..., experiment_config=...)`. These names are the spine's; re-anchor them
at dispatch. If a reader cannot thread a field without editing a spine-owned file
(`orchestrator/experiment_config.py`, `orchestrator/game.py`, `meetings/evidence_profile.py`,
`eval/replay_walk.py`), stop and ask the orchestrator. Do not widen the spine from here.

**One writer per file** (decision memo section 3.2):

| file | writers, in order | this card's region |
|---|---|---|
| `eval/evidence_honesty.py` | readers, B2, B6 | the walk profile and the decision reconstruction |
| `eval/funnel.py` | readers, B2 | the walk profile |
| `meetings/transcript.py` | readers, B2 | `walk_chain` |
| `tests/meetings/test_prompt_byte_golden.py` | A3 (its construction at `:1641` only), readers, B2, B6 | the directory walk, config threading, arm-stamp resolution |
| `tests/_helpers/committed.py` | A3, A1, readers, record plumbing, B2 (all serial) | threading the config through `meeting_trigger_kind` and the walks |
| `docs/artifacts.md` | A1, readers, record plumbing, B1, B2, B5, in merge order, each writing only its own row | the `audits/` row only, recomputed last |
| `tests/_helpers/scripted_meeting.py` (new) | readers, B6 | the rebuttal case |
| `audits/workflows/extract_gameplay_facts.py` | readers only | the refusal |

- A1's census cache in `committed.py` and its census row in `docs/artifacts.md` are disjoint
  regions. If A1 is still in flight, this card merges `main` after A1 lands and only then edits
  either file.
- This card alone writes `eval/kill_craft.py`, `eval/solvability.py`, `eval/win_condition_selfcheck.py`,
  `scripts/publish_process_scorecard.py` and its new test files.

**Delivery.**
- Branch `work/stage-b-readers`; one pull request into `main`, merged by the owner as a merge
  commit or a fast-forward, never squashed.
- Never amend a pushed commit. Bring `main` in by merging it, never by rebasing.
- Each commit body ends with `Card: tasks/work/stage-b-readers.md`, immediately followed by
  the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs).
- The PR body fills `.github/pull_request_template.md`'s Summary, Definition of done (this
  Acceptance, ticked with evidence), Decisions and Questions, and ends with the Claude Code
  attribution line.
- Agents post no PR comments.
- The worker fills Results and leaves the Status line and the `tasks/README.md` inventory sentence
  to the orchestrator, who flips both in one commit: `scripts/validate_task_docs.py` derives that
  sentence from every card's Status.

**Providers and scope.**
- Fake provider and scripted clients only: no live provider call, no `.env`, no held-out band.
- No ML training or refit (owner ruling 12). No tour or featured-list change (owner ruling 11). No
  scorecard cell (R13).
- No template file changes, so no prompt stamp moves; `reporter_reasoning` stays OFF (the B3 rider).
- No test enables an arm through an environment export; every arm comes from a declared config.
- Each new invariant has a planted case that fails on the defect (AGENTS.md craft rule 2).
- No instrument or helper change alters what an agent sees or is told, and role-correctness stays a
  reported cell. `walk_chain` raises on a mismatch and never repairs a transcript.
- A test that walks a committed or candidate set goes through `tests/_helpers/committed.py`
  (`tests/_helpers/test_committed_single_home.py` flags a walker call that names `replays/`). The new
  tests walk fake or scripted recordings under `tmp_path`.

**Copy.** The refusal messages and the `--set-dir` help text are user-facing. They carry no task or
audit IDs, no unexplained jargon and no threshold arithmetic: name the recorded setting and what the
tool reads, in plain words.

**Known limits, stated here and not fixed.**
- The scorecard fold already accepts experiment recordings. Its room table under the reset is B2's
  (decision memo section 2.3, item 5), so this card's `--set-dir` tests use no reset fixture.
- The golden and `committed.py` mirror the live loop's current resume perception under the reset.
  B2 changes the live loop and the readers together.
- The B3 census cells (claim structure, accusations against players who already spoke, beneficiary
  kind with the accuser's role) are A1's, not this card's.

## Expected scope

- `eval/kill_craft.py`, `eval/funnel.py`, `eval/solvability.py`, `eval/win_condition_selfcheck.py`,
  `eval/evidence_honesty.py`: the profile flips and declarations, the named refusals the reviews
  call for, and evidence honesty's recorded-policy reconstruction with its `policy_mode` label.
- `meetings/transcript.py`: `walk_chain` and its docstring.
- `tests/meetings/test_prompt_byte_golden.py`, `tests/_helpers/committed.py`, and the new
  `tests/_helpers/scripted_meeting.py`.
- `scripts/publish_process_scorecard.py`: `--set-dir` and `--json-stdout`.
- `audits/workflows/extract_gameplay_facts.py`: the refusal only.
- `docs/artifacts.md`: the `audits/` row only, recomputed with `git ls-files` after the final merge
  of `main`.
- A module reusing a flipped profile that its review says must refuse (`eval/deception_instruments.py`,
  `scripts/counterfactual_phase20.py`, which B2 edits after this card) gets a named refusal there.
- Tests: `tests/meetings/test_transcript.py` for `walk_chain`; `tests/scripts/test_process_scorecard.py`
  for `--set-dir`; new `tests/eval/test_recorded_arm_readers.py` for the widening, the event-level
  cases, the recorded policy and the kept refusals; new
  `tests/experiments/test_gameplay_facts_refuses_experiments.py`; new
  `tests/_helpers/test_scripted_meeting.py`; and the AST test, in whichever of these files fits.
- This card's Results.

Not in scope:
- every spine-owned file, and `eval/replay_walk.py`;
- `eval/process_scorecard.py` (B2);
- `eval/validity.py`, `eval/balance_eval.py`, `scripts/validity_gate.py`, `scripts/refresh_samples.sh`,
  `scripts/run_tournament.py`, `scripts/verify_samples.sh` (record plumbing);
- `engine/`, `observation/`, `eval/leak_scan.py`, `eval/witness_entitlement.py` (B0);
- `eval/off_menu.py` (FROZEN), `eval/watchability.py`, `training/`;
- `api/`, `frontend/`, every prompt template, `docs/glossary.md`, `docs/architecture.md`;
- `tasks/README.md`, and anything under `replays/`.

## Record impact

**Nothing moves.** This card is default-OFF.
- Nothing is re-recorded. The four sets' replays, MANIFESTs and reports, `docs/process-scorecard.*`,
  the census files, every fixture, the prompt registry and its stamps, the ML artifacts and every
  doc fact stay as they are.
- What changes is what readers accept. An experiment-stamped recording of the wave's fields is now
  read with its recorded settings, or refused by name. No committed set carries one.
- The candidate round (card 11) depends on this card and adopts nothing.
- B3's switch stays OFF on every committed recording. Its adoption, and the owner's confirmation of
  v1, come later.

**Publication.** A push to `main` republishes the demo bundle (`.github/workflows/pages.yml`). This
card edits nothing under `api/` or `frontend/`. `api/replay_loader.py` does import
`meetings/transcript.py`, so the PR shows the bundle built at the merge base and at the head to be
byte-identical. The merge then republishes identical bytes.

**Measurement.** The gates in Validation prove the OFF path identical; the planted cases in
Acceptance prove the widening. No cell, bar or verdict is added.

## Validation

```
# targeted, while developing (not a substitute for the full gate)
uv run pytest tests/eval/test_recorded_arm_readers.py tests/meetings/test_transcript.py tests/meetings/test_prompt_byte_golden.py tests/_helpers tests/experiments/test_gameplay_facts_refuses_experiments.py tests/scripts/test_process_scorecard.py -q
uv run pytest tests/eval/test_evidence_honesty.py tests/eval/test_funnel.py tests/eval/test_kill_craft.py tests/eval/test_solvability.py tests/eval/test_win_condition_selfcheck.py tests/meetings/test_reasoning_evidence.py tests/meetings/test_manager.py -q
# the OFF path, byte for byte, once per set directory
bash scripts/verify_samples.sh replays/samples/9p2i
bash scripts/verify_samples.sh replays/samples/4p1i
bash scripts/verify_samples.sh replays/ml_corpus/9p2i
bash scripts/verify_samples.sh replays/ml_corpus/4p1i
uv run python scripts/build_sample_report.py --sample-dir replays/samples/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/samples/4p1i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/9p2i --check
uv run python scripts/build_sample_report.py --sample-dir replays/ml_corpus/4p1i --check
uv run python scripts/publish_process_scorecard.py --check
uv run python scripts/publish_gameplay_census.py --check        # once A1 has merged
uv run python scripts/measure_baseline.py --honesty > "$SCRATCH/honesty-head.json"   # equal to the merge base's run
uv run python scripts/publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout > "$SCRATCH/s9.json"   # equal to the s9 entry of docs/process-scorecard.json
# the bundle, at the merge base and at the head, into scratch directories outside the tree
uv run python scripts/build_demo_bundle.py --out "$SCRATCH/bundle-head"   # and --out "$SCRATCH/bundle-base" in a worktree at the merge base
diff -r "$SCRATCH/bundle-base" "$SCRATCH/bundle-head"                     # empty
# the remaining gates
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py                     # offline; never --complete
git ls-files audits | wc -l                                     # the audits/ row's file count
git ls-files -z audits | xargs -0 cat | wc -c                   # the audits/ row's tracked bytes
uv run pytest -m campaign -q                                    # the c9 refit pins' campaign half
bash scripts/check.sh; echo "check.sh exit $?"                  # whole, in a clean worktree
git diff --stat "$(git merge-base origin/main HEAD)" HEAD -- replays agents engine observation orchestrator api frontend docs/process-scorecard.md docs/process-scorecard.json   # empty
```

- Quote each command's real exit code in Results.
- `bash scripts/check.sh` runs whole in a clean worktree, so no gate after the first failure is
  masked. A test that also fails at the merge base on the local platform is named in Results with
  that merge-base run; CI is the gate of record.
- `npm --prefix frontend test` and the e2e are not required: this card edits nothing under `api/` or
  `frontend/`. The bundle comparison above stands in for them, and `check.sh` runs the frontend leg
  anyway.

## Results

Implemented on `work/stage-b-readers` from base `bdfa5b19` (the spine and the census merged). What it
implements: `docs/architecture.md` "Determinism and the substrate ladder" (every re-simulation takes
the recorded settings; replays stay byte-identical), "Enforced boundaries" (no `agents/` import of
`engine/`; `lint-imports` 4 kept, 0 broken) and "Explicit cleanup experiments" with the spine's arm
page `docs/experiment-arms.md` (one engine-arguments helper, thread-or-refuse by layer, the empty
experiment-arm stamp registry); the decision memo's sections 0.3 items 7 and 10, 2.4 (B3 with its
rider) and the card-4 brief in 3.4. Rulings relied on: "We should implement stage B", "B3. Allow one
reply for the opener", "B3 adopts bounded_rebuttal_version=1 ALONE, reporter_reasoning does NOT ride
along", "Hold off on ML as D suggests until gameplay is finished", and R7 through the event-level
cases. No agent behaviour changes, no committed byte moves, nothing is re-recorded.

### The per-instrument review

Every recorded setting reaches a reader one of three ways: the engine settings through the spine's
`engine_arguments` at every advance (it refuses one it does not thread, today `vent_witness_rule`'s
`physical`), the meeting reset through the walk's `apply_meeting_result`, and every other setting
only as the recorded actions, turns, flags, ballots and prompts the walk replays. A reviewed reader
names the fields it reads in its own `*_READS` constant, a subset of
`eval.recorded_settings.READABLE_SETTINGS` (the eight wave fields and `redistribution_policy`), and
its profile's `threaded_layers` is derived from that constant (`layers_read`). Any other non-default
field, a settings format other than 1, and temporal delivery are refused by name at the walk's first
tick, before its first advance (`read_recorded_settings`; temporal by the walk's own
`supports_temporal_observations=False`).

- **Kill-craft** (`kill-craft`; reused by `scripts/build_sample_report.py::build_report`, the
  `eval.deduction_metrics` / `eval.meeting_quality` cells that read its report, and
  `tests/_helpers/committed.py::kill_craft_report`). Both folds read pre-advance engine states and
  `KilledEvent`s only. Threads all nine: the witness rule changes no kill witness list, the reset's
  post-meeting positions are the next pre-advance frame, the tactical, rebuttal, trigger and ballot
  settings are recorded actions and rows it never reads. Reads a `hub_with_grace` recording with every
  hash verified (`test_kill_craft_reads_the_regroup_reset_with_every_hash_verified`), so the record
  plumbing card's post-step can walk one. Refuses nothing pending a later card.
- **The information funnel** (`funnel-instrument`, both walks; reused by `eval/vj_instruments.py`
  and `eval/deception_instruments.py` through `_walk_set_vj`, `training/surrogate/dataset.py`
  through `_walk_game_vj` after its own refusal, `scripts/measure_baseline.py --funnel/--vj`, and
  `committed.py::funnel_report`). Threads all nine. Stage 2 and the pooled perception read the vent
  witness lists the advances produce, so a changed witness rule reaches them
  (`test_the_funnel_folds_the_stand_ins_vent_witness_lists`). Under the reset the per-tick perception
  across a meeting reads the pre-meeting play events plus the meeting's events, as the live loop and
  the loader do, and the belief fold mirrors the live loop's default path (the public regroup row is
  written only under evidence version 2, which is refused). The meeting-reset card changes the live
  loop and this walk together (the relevance window through its `extract_belief_evidence` and
  `reconstruct_stated_paths` calls), so nothing is refused pending it. A rebuttal is one more recorded
  turn; the ballot settings are recorded ballots. `eval/deception_instruments.py` (FROZEN) and
  `eval/vj_instruments.py` inherit the funnel's refusal through the shared walk and need no edit.
- **Solvability** (`solvability`; reused by `scripts/measure_baseline.py --solvability`, both
  counterfactual scripts and `committed.py::solvability_report`). Reads pre-advance states, kill
  events, the engine trigger's body id and the recorded ejection; sight comes from
  `compute_visibility_for_player`, never a recorded witness list. Threads all nine; the body-handle
  setting changes only the trigger's description, which it never reads.
- **The win-condition self-check** (`win-condition-selfcheck`; its logic is mirrored, not called, by
  `eval.validity`). Reads the living impostors after each advance and applied meeting and the
  recorded `game_over` row. Threads all nine.
- **Evidence honesty** (`evidence-honesty`; reused by `tests/_helpers/committed.py`'s channel walk,
  `tests/agents/test_reported_testimony.py` and `tests/eval/test_evidence_honesty.py` over committed
  sets, `scripts/counterfactual_phase20.py`'s walk, and `scripts/counterfactual_phase21.py` and
  `scripts/measure_baseline.py --honesty` through `compute_evidence_honesty`). Reads every readable
  setting except `meeting_reset`: the regroup moves every survivor to the hub between the trigger
  tick's frame and the resume tick, so `room_at` and `_assert_clock_alignment` would read honest
  post-regroup sightings as a moved clock; the meeting-reset card owns that fix and lifts this
  refusal. Perception reads the advances' witness lists
  (`test_honestys_perception_folds_the_stand_ins_vent_witness_lists`). The vent exit and entry
  policies reach I-11 as the recorded policy: `recorded_impostor_policy` builds, per impostor, what
  `build_default_agent_factory(experiment_config=...)` builds, read back through
  `tactical_experiment_options` (no edit to `orchestrator/game.py`), and `_ImpostorPolicies` gives
  each living experimental policy the announced dead roster after every applied meeting, as
  `TacticalAgent.note_meeting_concluded` does. Until the look-and-wait card builds `look_and_wait`
  and `own_fresh_kill`, building that policy raises `UnbuiltTacticalOptionError`, so an honesty run
  on such a recording raises that named error. A rebuttal, the body handle and both ballot settings
  reach the cells only as recorded turns, flags and prompts: the prompt folds count fixed row shapes
  and phrases in recorded prompts, and the ballot card adds its own family beside `_fold_grounding`.
  Reusers: the committed-meeting channel walk reads all nine including the reset (it mirrors the
  live resume perception, like the golden) and threads the trigger setting into
  `meeting_trigger_kind`; `scripts/counterfactual_phase20.py` is defined over recordings made
  without settings and now refuses any recorded setting by name (the meeting-reset card threads it or
  keeps that refusal); `scripts/counterfactual_phase21.py` adds no setting logic of its own and
  reads recordings only through the golden walk and `compute_evidence_honesty`, so it takes their
  thread-or-refuse behaviour.
- **The prompt-byte golden and `tests/_helpers/committed.py`** read at most the same nine and refuse
  the rest by name before the first advance (`the prompt-byte golden does not read ...`,
  `the committed-meeting channel walk does not read ...`). The golden threads the engine settings,
  the reset and the redistribution rule of each applied meeting, the trigger setting, the evidence
  profile (`profile_from_config`), the agents (the default factory for the recorded settings, then
  `bind_experiment`) and the stamp resolution. Until the body-handle card builds the handle text,
  `_build_meeting_trigger` refuses the recorded value, and until the look-and-wait card builds its
  policy the factory refuses those values; both refusals are reached by these readers, which is the
  proof the recorded values arrive (`test_the_reconstructors_hand_the_recorded_trigger_setting_to_the_builder`,
  `test_the_golden_builds_the_recorded_arms_agents`).

### Planted and perturbed cases

Each is a committed test; each was seen red with its defect (the neutering and mutation table
below lists the probe that shows it) and is green at the head.

| Claim | Case (test id) | What bites |
| --- | --- | --- |
| walk_chain accepts the pick and nothing else | `tests/meetings/test_transcript.py::TestWalkChainBoundedRebuttal` (9 tests; since round 2, 22 cases over two shapes and both trailing kinds) and `test_walk_chain_accepts_exactly_the_selected_rebuttal` (Hypothesis, 200 generated manager-shaped chains, `deadline=None`) | a wrong speaker, a wrong `reply_to`, two trailing replies, a trailing opt-in, a trailing reply without the setting, a missing pick, a non-reply in the slot, a reply where nothing is pending; with the speaker check removed the wrong-speaker case passes and its test fails (probe T10); since round 2 every message is matched whole with the values it names |
| five profiles widened | `tests/eval/test_recorded_arm_readers.py::test_a_widened_reader_verifies_every_arm_that_exists_today` (5 readers x 5 fake recordings: plain, workload, regroup reset, reset + real rebuttal, observed-risk + real rebuttal), `..._verifies_a_copy_carrying_every_wave_value`, `test_honesty_verifies_every_arm_it_reads`, `test_kill_craft_reads_the_regroup_reset_with_every_hash_verified` | every hash the profile checks verified; the copies carry `look_and_wait`, `own_fresh_kill`, body handle 1 and both ballot values with the pending guard patched open |
| a field outside the list is refused before the first advance | `test_a_setting_outside_the_reviewed_fields_is_refused_before_the_first_advance` (6 readers x `crew_idle_policy='patrol'`, `evidence_reasoning_version=1`), `test_a_later_settings_format_is_refused_by_name`, `test_the_reconstructors_refuse_an_unread_setting_by_name`, the golden's `test_a_setting_beyond_the_readable_ones_is_refused_before_the_first_advance` | the walk's `advance_tick` patched to raise, so a refusal after the first advance would surface as that error; each message names the profile or reader and the field |
| honesty refuses the reset pending its card | `test_honesty_refuses_the_meeting_reset_until_its_room_table_is_coherent` | both entry points, before any advance |
| event-level thread-or-refuse | `test_every_widened_reader_threads_the_helpers_arguments_to_every_advance` (6 readers), `test_the_funnel_folds_the_stand_ins_vent_witness_lists`, `test_honestys_perception_folds_the_stand_ins_vent_witness_lists`, `test_the_committed_meeting_walk_threads_the_helper_and_its_vent_records_change`, `test_the_golden_threads_the_helper_and_its_rendered_memory_changes`, `test_the_plain_recording_holds_exits_the_stand_in_changes` | the planted helper adds a stand-in field and the stand-in engine accepts it and rewrites vent exits to R7's shape (source witnesses dropped); the recording holds exits with living source-room witnesses; the double saw the stand-in on every advance; kill-craft, solvability and the win-condition check are unchanged; the four vent-folding outputs change |
| bypassing the helper fails | `test_a_call_site_that_bypasses_the_helper_fails_its_case` (the walk's site, the golden's site) | the stand-in engine without the planted helper raises `TypeError` naming the stand-in, and never advances |
| an engine setting the helper does not thread is refused | `test_an_engine_setting_the_helper_does_not_thread_is_refused_by_name` (8 readers) | `_THREADED_ENGINE_FIELDS` patched empty; the workload rule is refused by name before the first advance |
| recorded policy | `test_honesty_rebuilds_decisions_with_the_recorded_policy`, `test_without_a_config_the_default_is_the_live_policy`, `test_a_recording_from_a_custom_factory_is_refused_by_name`, `test_a_set_whose_games_name_different_policies_raises`, `test_a_living_experimental_policy_receives_the_announced_dead_roster`, `test_every_applied_meeting_reaches_the_meeting_concluded_hook` | observed-risk game: 0 mismatches recorded, more than 0 live, every disagreement at a vent action; plain game: default equals explicit live; custom refused, explicit still folds; mixed set raises; hook gets the dead roster, once per applied meeting |
| the golden reads any directory | the golden's `test_a_planted_candidate_root_is_discovered_and_walked`, `test_the_sample_sets_come_first_and_candidates_are_discovered` | an empty round directory and a stray file are not listed; the planted set walks byte-equal |
| recorded profile, reset, redistribution, trigger, agents | `test_the_scripted_rebuttal_game_re_renders_byte_equal`, `test_dropping_the_recorded_reset_fails_the_meeting_post_hash`, `test_an_applied_meeting_takes_the_recorded_redistribution_rule`, `test_the_reconstructors_hand_the_recorded_trigger_setting_to_the_builder`, `test_the_golden_builds_the_recorded_arms_agents` | profile dropped: the rebuttal call goes unconsumed; reset dropped or redistribution defaulted: `state_hash_after` fails; the trigger builder and the factory refuse the recorded unbuilt values, which a reader that dropped them never reaches |
| arm stamps | `test_an_arm_stamp_resolves_only_on_a_recording_that_carries_the_arm`, `test_a_recording_made_with_a_registered_arm_resolves_through_its_settings`, the window test over every golden directory | planted registry entry: the arm stamp resolves and passes only with the arm; the same stamp without it matches 0 sets; the default stamp on an arm recording fails the window; a recording made under the planted entry walks byte-equal and fails without its settings |
| the scripted game | `tests/_helpers/test_scripted_meeting.py` (13 cases) | bare-shell load with `outcome_verified`, memory and belief frames; exactly one rebuttal, by the opener, replying to turn 1, whose prompt carries the charge; default stamps, `reporter_reasoning` false, no `<who_reported>`; the five walks, `walk_chain`, the golden, the scorecard and census `--set-dir`; the deviation case; no rebuttal without the setting and `walk_chain` then raises on the missing pick; a script counts from each meeting's opening |
| scorecard `--set-dir` | `tests/scripts/test_process_scorecard.py::test_set_dir_*` (6 cases) | equals the in-process fold; no writer reached; set directory and `docs/` unchanged; true path two levels down, misnamed without the replacement; four refusals |
| extractor refusal | `tests/experiments/test_gameplay_facts_refuses_experiments.py` (3 cases) | exact message, no advance; unstamped fake recording extracts |
| kept refusals | `test_a_frozen_or_policy_rerunning_instrument_keeps_refusing` (5), `test_the_referee_floors_an_experiment_recording`, `test_the_offline_counterfactual_still_refuses_any_recorded_setting` | exact refusal text, every `advance_tick` patched to raise |
| call sites pass the recorded settings | `test_every_owned_call_site_passes_the_recorded_settings` (3 modules), `test_the_scan_bites_a_planted_call_site` (8 planted sources) | a bare `advance_tick(state, actions, game_map=...)`, a by-hand engine field, another spread, an apply without the reset or the redistribution rule, a trigger without its setting, an aliased import |
| plain copy | `test_the_copy_this_card_adds_carries_no_identifier`, `test_the_copy_scan_bites_an_identifier` | "Task 20.33" and "R7" each fail the scan |

### The neutering and mutation pass

One bounded pass over every production line and call-site argument this card added or changed (and
the golden's and `committed.py`'s reader threading), with exactly the named operator classes: drop a
filter or wrapper, swap a collection for a related one, replace a comparison with a `None` test or
its inverse, replace a role, kind or setting read with a constant, replace a message argument with a
constant, drop one member of a tuple or set of kinds, swap related types, replace a read of a loaded
source with the canonical literal; plus neutering a whole statement. Each probe edited one file in
place from a byte copy, ran only its targeted suites (`pytest -x -q -n 6`: `test_transcript.py -k
walk_chain` for `walk_chain`; `tests/eval/test_recorded_arm_readers.py` for the readers, adding
`tests/_helpers/test_scripted_meeting.py` or `test_evidence_honesty.py -k policy` where the probe
touches them; the golden; the scorecard's `-k set_dir`; the extractor's file), restored the copy and
compared sha256 (all 156 restored). The probe script is a scratch file, not committed.

| File | Probes | Red on the first pass | Green on the first pass |
| --- | --- | --- | --- |
| `meetings/transcript.py` | 15 | 15 | none |
| `eval/recorded_settings.py` | 25 | 23 | R17, R21 |
| `eval/kill_craft.py` | 6 | 6 | none |
| `eval/funnel.py` | 9 | 9 | none |
| `eval/solvability.py` | 6 | 6 | none |
| `eval/win_condition_selfcheck.py` | 6 | 6 | none |
| `eval/evidence_honesty.py` | 34 | 31 | H8, H13, H14 |
| `scripts/counterfactual_phase20.py` | 3 | 3 | none |
| `scripts/publish_process_scorecard.py` | 11 | 11 | none |
| `audits/workflows/extract_gameplay_facts.py` | 6 | 5 | X4 |
| `tests/_helpers/committed.py` | 6 | 6 | none |
| `tests/meetings/test_prompt_byte_golden.py` | 29 (one a no-op control, green) | 22 | G11, G12, G18, G21, G22, G29 |
| `tests/_helpers/committed.py`, review round 1: the walk's readable list with one setting dropped (C2.1 to C2.9) | 9 | 1 at `f3473b61` (C2.6) | C2.1 to C2.5, C2.7 to C2.9 at `f3473b61`; all nine red at `078ab37a` |
| `tests/meetings/test_prompt_byte_golden.py`, review round 1: the same at the golden's list (GR.1 to GR.9) | 9 | 6 at `f3473b61` | GR.1, GR.7, GR.8 at `f3473b61`; all nine red at `078ab37a` |
| review round 1: an identifier planted in each refusal the copy scan missed (CP1 to CP3, two plants each) | 6 | 0 at `f3473b61` | all six at `f3473b61`; all six red at `078ab37a` |
| `meetings/transcript.py`, review round 2: a message argument of the rebuttal-tail and no-setting refusals replaced with a constant (MA1, MA12 to MA24, MA15I, MA15E) | 16 | 0 at `9bab8d16` | all 16 at `9bab8d16`; 15 red at `29707b99`, MA15E equivalent |
| `eval/recorded_settings.py`, review round 2: the same over the three refusal messages (MA6, RS2 to RS8) | 8 | 4 at `9bab8d16` (RS4, RS6, RS7, RS8) | MA6, RS2, RS3, RS5 at `9bab8d16`; all 8 red at `29707b99` |
| `eval/evidence_honesty.py`, review round 2: the same over the custom-factory and mixed-set raises (MA7, MA8, MA8E, H3) | 4 | 0 at `9bab8d16` | all 4 at `9bab8d16`; 3 red at `29707b99`, MA8E equivalent |
| `scripts/publish_process_scorecard.py`, review round 2: the same over the no-replay refusal (MA10) | 1 | 0 at `9bab8d16` | green at `9bab8d16`; red at `29707b99` |

The review-round-1 and round-2 rows are detailed in "Review corrections, round 1 (2026-09-26)" and
"Review corrections, round 2 (2026-09-26)" below. The first pass did not probe every message
argument: round 2 found 25 message-argument probes green at `9bab8d16` in four files, so each of
those files' first-pass rows (the "none" for `meetings/transcript.py` included) held only for the
probes it ran, and round 1's "no survivor remains" covered only round 1's own probes. The twelve
probes of the first pass that first came back green, and what became of each:

- **Killed by a new planted case** (re-run red at `5d6d640a`):
  - H8 (the reconstruction's reader label replaced with a constant): the reset refusal test now
    asserts `reconstruct_impostor_decisions`' message names `replay profile 'evidence-honesty'`.
  - X4 (the extractor's `format_version` exclusion dropped): a format-2 config must name only
    `bounded_rebuttal_version = 1`.
  - G18 (the `hit` filter dropped from `consumed_exactly_once`): a unit case with a defaulted miss
    beside two hits, one missing hit and one double hit.
  - G22 (`sorted` dropped from `golden_directories`): a root whose `glob` returns reverse path order.
- **Equivalent, with the reason:**
  - R17: the `format_version` clause in the field loop: a config reaching the loop is format 1, which
    is the field's default, so the value check skips it anyway.
  - R21: checking every `TickOpened` instead of the first: every tick row carries the same settings,
    which the walk has already checked agree.
  - H13: `normalize_experiment_config` dropped before the factory: a config that normalizes to `None`
    has no tactical change, and the factory builds the default policy for it either way.
  - H14: the factory asked for a crewmate: it derives one options object for both roles, and the
    recorded policy is always built as the impostor class from those options.
  - G11, G12: `bind_experiment` given `None`, or not called: everything it binds (the evidence,
    account and testimony versions, format-3 decisions, the public map the evidence context reads)
    is reachable only under settings the golden refuses before it builds agents.
  - G21: `is_dir()` dropped from the candidate listing: a file two levels down holds no replay files,
    so `_seed_paths` already excludes it.
  - G29: `_first_meeting_state`'s advance given `engine_arguments(None)`: it walks only the committed
    9p2i seed 0, which records no settings; the `ast` scan still holds the call to the helper form.

### Verification at `f489cf13`

Every command from the card's Validation, with its real exit code, at `f489cf13` (main unchanged at
`bdfa5b19`). The `verify_samples`, report, scorecard, census, honesty, bundle, doc-fact and
evidence runs were made on production bytes identical to `f489cf13`'s (the commits after them change
only tests, one docstring and the registry row, all present when they ran). The commit that carries
this section changes only this card and `tasks/README.md`.

| Command | Result |
| --- | --- |
| `uv run pytest tests/eval/test_recorded_arm_readers.py tests/meetings/test_transcript.py tests/meetings/test_prompt_byte_golden.py tests/_helpers tests/experiments/test_gameplay_facts_refuses_experiments.py tests/scripts/test_process_scorecard.py -q -n 6` | exit 0, 370 passed |
| `uv run pytest tests/eval/test_evidence_honesty.py tests/eval/test_funnel.py tests/eval/test_kill_craft.py tests/eval/test_solvability.py tests/eval/test_win_condition_selfcheck.py tests/meetings/test_reasoning_evidence.py tests/meetings/test_manager.py -q -n 6` | exit 0, 491 passed |
| `bash scripts/verify_samples.sh replays/samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i` | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `uv run python scripts/publish_process_scorecard.py --check` | exit 0, consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | exit 0, consistent |
| `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` and `... replays/samples/4p1i`, at the merge base (a `git archive` export of `bdfa5b19` reading the same replay bytes) and at the head | exit 0 each; byte-identical (sha256 `97aa858e...` for 9p2i, `d0500f96...` for 4p1i). Run with no set argument the two outputs differ only in the absolute checkout path each prints in its header lines, and are identical once that root is normalised |
| `uv run python scripts/publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; equal to the `samples/9p2i` entry of `docs/process-scorecard.json` as parsed JSON and byte for byte under the committed serializer settings |
| `uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head`, and `--out <scratch>/bundle-base` in the base export (the replays copied in with their mtimes, since the loader bakes `created_at` from them) | exit 0 each: 7 featured games, 156 baked JSON files |
| `diff -r bundle-base bundle-head` | empty, exit 0 (194 files each) |
| `uv run python scripts/check_doc_facts.py` | exit 0 |
| `uv run python scripts/validate_task_docs.py` | exit 0, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 62 checks, 50 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 329 files; 26,636,557 bytes (the `docs/artifacts.md` row) |
| `uv run pytest -m campaign -q` | exit 0, 336 passed |
| `bash scripts/check.sh; echo "check.sh exit $?"` (clean worktree) | exit 0: 8,994 passed, 20 skipped, 3 xfailed; frontend lint, `tsc:check`, 559 vitest tests and the build pass |
| `git diff --stat $(git merge-base origin/main HEAD) HEAD -- replays agents engine observation orchestrator api frontend docs/process-scorecard.md docs/process-scorecard.json` | empty |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |

The first `check.sh` run at `4a5067d5` stopped at `uv run mypy .` (exit 2): the copy scan imported
`audits/workflows/extract_gameplay_facts.py` statically, so mypy saw it under two module names.
`f489cf13` imports it dynamically, as the extractor's own tests do; the run above is after it.

### Publication and record impact

Nothing moves. No byte under `replays/`, no derived report, fixture, prompt template, doc fact or ML
artifact changed (`git diff --stat` above is empty over the protected paths; the four
`build_sample_report --check` runs, the scorecard and census `--check` runs, the golden on s9 and s4
and the four `verify_samples` runs are the byte comparisons, each with its own planted failure: the
golden's one-byte template case, `build_sample_report --check`'s drift case and the scorecard
`--check`'s edited-cell case, all in the suite `check.sh` ran). This card edits nothing under `api/`
or `frontend/`; `api/replay_loader.py` imports `meetings/transcript.py`, so the demo bundle was built
at the merge base and at the head and `diff -r` is empty: the merge republishes identical bytes. A
first base build read the replays through a symlink out of the export, and its bundle README then
said the data came from outside the repository (the only difference); the export was rebuilt with
the replays copied in, mtimes kept, and the comparison above is that one. The only tracked audit byte
change is the extractor's refusal, reflected in the `audits/` row of `docs/artifacts.md` (26,635,440
to 26,636,557 bytes, 329 files; recomputed after merging `main`, which had not moved from
`bdfa5b19`). With the row stale, `test_every_counted_registry_row_matches_the_index` failed:
"audits/: docs/artifacts.md promises 26,635,440 tracked bytes, the tracked files contain 26,636,557
bytes".

### B3, re-measured

Count-only, keyed by set, by projecting `select_bounded_rebuttal` over the recorded transcripts (the
manager runs it on exactly those turns after the roll call). The projection is pinned by
`tests/_helpers/test_scripted_meeting.py::test_the_rule_the_owner_is_asked_to_confirm_projected_on_the_committed_sets`,
so `uv run pytest tests/_helpers/test_scripted_meeting.py -k projected` reproduces it; no transcript
text leaves the test.

| Set | Meetings | Fires | To the opener | To impostors | To other crewmates | Opener accused | Opener loses the slot |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `samples/9p2i` | 145 | 144 | 123 | 19 | 2 | 125 | 2 |
| `ml_corpus/9p2i` | 449 | 447 | 351 | 86 | 10 | 362 | 11 |
| `samples/4p1i` | 39 | 39 | 37 | 2 | 0 | 37 | 0 |
| `ml_corpus/4p1i` | 43 | 43 | 37 | 6 | 0 | 37 | 0 |
| pooled | 676 | 673 | 548 | 113 | 12 | 561 | 13 |

These equal the Evidence section's figures. Today the opener answers 0 of 561
(`docs/gameplay-census.md`, `accused_opener_answers`). The deviation from ruling 4's words and the
question to the owner are in the PR's Decisions and Questions; the rule is pinned by
`test_the_one_reply_goes_to_the_earliest_charge_not_to_the_opener`.

### Closing greps

Case-insensitive, over the whole tree except `tasks/`, `audits/` and `agent_prompts/`:

- `git grep -niE 'walk_chain.{0,80}(any|every) non|tail turns are .?.?opt_in|non-.?.?opt_in.?.?.? turn after the chain'`:
  one hit, `meetings/transcript.py:496`, `walk_chain`'s opening sentence, which since `d575b12c`
  continues "save the one selected rebuttal the recorded setting may add"; none describes the old
  rule.
- `git grep -niE '(eight|8) (walk )?profiles|profiles? refuses? (any|every) experiment'`: one hit,
  `eval/replay_walk.py:121` ("the eight profiles that already verify tick hashes"), about action
  dispositions and still true.
- `git grep -niE 'defaults? to the (one|policy) in the tree|impostor_policy.{0,40}defaults? to'`: none.
- `git grep -niE 'golden.{0,60}(two|fixed|committed) (sample )?sets? only|walks the fixed'`: none.
- `git grep -ni 'does not support experimental'` outside tests: the walk's two messages, off-menu, the
  anchor study and `require_baseline_experiments`, each a kept refusal or check and still true.

### Decisions

- **One field list per reader, in a new module.** The spine's walk check is by layer, and
  `supports_experiments` accepts every pre-wave setting, so a per-field refusal needs its own home.
  `eval/replay_walk.py` is the spine's and out of scope, so it lives in a new
  `eval/recorded_settings.py` (a deviation from Expected scope, reported in the PR): the readable set,
  `layers_read` deriving each profile's `threaded_layers` from its field list, and the refusal. The
  refusal reads the first tick row's settings, which the walk has already checked agree across every
  row, so nothing is parsed twice.
- **Refusals pending a later card.** Evidence honesty refuses `meeting_reset` (the meeting-reset
  card lifts it with its `room_at` and clock-alignment fix). `scripts/counterfactual_phase20.py`
  refuses every recorded setting (the meeting-reset card threads it or keeps the refusal). The engine
  helper still refuses `vent_witness_rule='physical'` in every reader (the physical-witness card
  threads it). `_build_meeting_trigger` refuses `report_body_handle_version=1` in the golden and the
  committed walk (the body-handle card). The default factory refuses `look_and_wait` and
  `own_fresh_kill` in the golden and in honesty's recorded policy (the look-and-wait card). No other
  refusal is pending: the pre-wave settings (crew idle policy, retarget, self-report, sabotage timing,
  evidence, accounts, testimony, investigation, contextual self-report), formats 2 and 3 and temporal
  delivery stay refused with no card to lift them.
- **The recorded policy is the default, by game, with one label per set.** `impostor_policy=None`
  means the policy each game's settings name; a set whose games name different kinds raises rather
  than mixing labels. An explicit factory still folds a counterfactual and keeps its old label, so
  `impostor_policy=live_impostor_policy` on an arm recording is the live-policy counterfactual the
  proof compares against. The custom-factory refusal applies to the recorded policy only.
- **The golden reads the same nine settings as the instruments.** It could thread more (evidence
  version 1 through the profile and `bind_experiment`), but the absorb fold, the public regroup row
  and the account renderers would each need threading with no recording to prove them, so it refuses
  them by name instead. `bind_experiment` and the factory are called as `HeadlessGame` calls them;
  within the readable settings their only observable effect is the factory's refusal of unbuilt
  tactical values.
- **Consumption, not only count.** The golden's consumption case counted one `RerenderedPrompt` per
  recorded call, which cannot fail; `walk_directory` now records every meeting whose calls the
  manager did not ask for exactly once, and the case asserts none.
- **The scripted helper also scripts an ejection.** The golden's applied-meeting redistribution rule
  is observable only when a meeting ejects someone, and the fake provider never ejects, so
  `Ejection` makes every voter but the target eject a named speaker. It is the one ballot case this
  card adds; the ballot card adds its own. The helper's meeting boundary is read off the ballot
  schema the manager actually requests (`ModelAuthoredVoteBallot`).
- **The B3 projection is pinned as a test**, count-only
  (`test_the_rule_the_owner_is_asked_to_confirm_projected_on_the_committed_sets`), so the figures in
  the PR's Decisions are reproducible from a committed command rather than a scratch script.
- **Status and inventory.** The card reserves the Status line and the index sentence for the
  orchestrator; the dispatch delegated the flip, so the Results commit flips Status to done and
  re-derives the sentence with `scripts/validate_task_docs.py`, as the spine card did.

### Limitations

- The pending wave values are proved read only on rewritten copies (the pending guard patched
  open), never on a recording that ran them: no behaviour exists for them yet. Evidence honesty's
  recorded policy for `look_and_wait` and `own_fresh_kill` raises `UnbuiltTacticalOptionError` until
  the look-and-wait card, which then proves it reconstructs with 0 mismatches.
- The meeting-concluded hook is proved called once per applied meeting and proved to pass the
  announced dead roster, but no built tactical value within honesty's fields reads it today
  (`observed_risk` does not), so its effect on a decision is unexercised until the look-and-wait card.
- The golden and the committed walk mirror the live loop's current resume perception under the
  reset; the meeting-reset card changes the live loop and these readers together. The scorecard
  `--set-dir` tests use no reset fixture, since the scorecard's room table under the reset is that
  card's.
- `vent_witness_rule='physical'` was refused by the engine helper everywhere until the
  physical-witness card (#485) threaded it. Since this card merged `main` at `fb9d2e31`, the
  event-level test also runs on a physical recording (Results, "Review corrections, round 3"); the
  pending refusal the Decisions above name for it is lifted.
- `scripts/counterfactual_phase21.py` gains no refusal of its own; it reads recordings only through
  the golden walk and evidence honesty and takes their behaviour.
- The B3 figures are a projection of the selector over transcripts recorded without it; a game
  recorded with the setting would diverge after the first reply.
- The scorecard `--set-dir` "writes nothing" proof checks the set directory, the checkout's `docs/`
  status and the two published files, and that no writer is reached; it does not snapshot the whole
  checkout, which other test workers may touch concurrently.

### Review corrections, round 1 (2026-09-26)

Three blocking findings from the round-1 verifiers on `f3473b61`, each repaired in `078ab37a`
(tests only: no production module, recording, derived view, fixture or doc fact changed; `git diff
--stat f489cf13 078ab37a` lists only this card, `tasks/README.md` and the two test files below).
No Codex comment was posted on the PR beyond its review summary, so there is none to answer.

- **The committed walk reading the meeting reset was untested (correctness).** The verifier's probe
  C2 (`tests/_helpers/committed.py:583`, `reads=READABLE_SETTINGS` with `meeting_reset` removed)
  left every test green, though the per-instrument review above says this walk reads all nine
  settings, the reset included. Three positive cases in `tests/eval/test_recorded_arm_readers.py` now
  hold it, for the committed walk and the golden alike:
  - `test_the_reconstructors_walk_every_meeting_of_every_arm_that_exists_today` walks the plain,
    workload, regroup-reset, reset-with-rebuttal and observed-risk-with-rebuttal fake recordings and
    asserts the committed walk yields every recorded meeting id in order, and the golden walks as
    many meetings, re-renders every prompt byte-equal and consumes every call once;
  - `test_the_reconstructors_walk_every_meeting_of_a_copy_carrying_the_pending_values` does the same
    on rewritten copies (the pending guard patched open) carrying the values each reconstructor
    reads without reaching a builder that refuses them: the committed walk, which builds no agents,
    takes the pending vent exit and entry values and both ballot values; the golden takes both ballot
    values. The body handle and the golden's pending tactical values keep their earlier proofs (the
    builders' refusals, `test_the_reconstructors_hand_the_recorded_trigger_setting_to_the_builder`,
    `test_the_golden_builds_the_recorded_arms_agents`);
  - `test_the_reconstructors_hand_the_recorded_witness_rule_to_the_engine_helper` walks a copy
    stamped `vent_witness_rule="physical"` through a spy on the engine-arguments helper that records
    the rule it receives and then runs the default rule the copy's events were made with: the spy
    sees `physical` and the walk reaches every meeting. It holds whether or not the helper threads
    the rule, so the physical-witness card needs no edit to it.
- **The plain-copy scan missed three new refusals (integrity).** `_new_copy` now captures the two
  `--set-dir` parser refusals (the standard error the script prints, with `sys.argv[0]` pinned and
  the named directory replaced by `DIR`) and evidence honesty's mixed-policy raise (on a directory
  whose two games name different policies, the directory replaced by `DIR`), and
  `test_the_copy_this_card_adds_carries_no_identifier` asserts each of its seven named texts is the
  refusal it names before scanning, so none can pass by being empty or another error. The scan now
  reads every new refusal message this card adds: the settings refusal in its four shapes (an unread
  setting, with and without fields read; a later format; a list outside the reviewed set), the
  extractor's, the custom-factory and mixed-policy raises, the two `--set-dir` parser refusals, and
  the `--set-dir` and `--json-stdout` help with the script's docstring. `walk_chain`'s mismatch
  errors and the two unreachable pins (`pragma: no cover`) are invariant errors, not refusals, and
  are not scanned.
- **The B3 table rows beyond s9 and pooled were not pinned (docs).**
  `test_the_rule_the_owner_is_asked_to_confirm_projected_on_the_committed_sets` now counts each
  set's meetings and asserts all four per-set dicts in full (every count present, zeros included)
  and the pooled dict, so `uv run pytest tests/_helpers/test_scripted_meeting.py -k projected`
  reproduces every row and column of the table in "B3, re-measured" (1 passed at `078ab37a`). The
  values did not move.

**Round-1 probes**, run from byte copies with the round's scratch script (one edit per probe, the
targeted suites only, `pytest -x -q -n 6 -rf -p no:cacheprovider`; each file restored from its copy
and its sha256 compared, all 24 restored). The C2 and GR probes ran
`tests/eval/test_recorded_arm_readers.py tests/_helpers tests/meetings/test_prompt_byte_golden.py`;
the CP probes ran `tests/eval/test_recorded_arm_readers.py`. Operator classes: swap one collection
for a related one (the readable list minus one setting, which is also dropping one member of a set
of kinds) and a message argument replaced (an identifier planted in a message).

| Probe | Edit | At `f3473b61` | At `078ab37a` |
| --- | --- | --- | --- |
| C2.1 to C2.9 | the committed walk's `reads=READABLE_SETTINGS` minus `vent_witness_rule`, `vent_exit_policy`, `vent_entry_policy`, `meeting_reset`, `bounded_rebuttal_version`, `report_body_handle_version`, `ballot_kill_row_version`, `impostor_ballot_version`, `redistribution_policy` in turn | red only C2.6 (the trigger builder case); the other eight green | all nine red |
| GR.1 to GR.9 | the same nine at the golden's `refuse_unread_settings` call | green GR.1, GR.7, GR.8; the other six red | all nine red |
| CP1.T, CP1.R | " (see Task 20.33)" or " (the R7 rule)" appended to the `--set-dir and --json-stdout go together` refusal | green (the scan never read it) | both red |
| CP2.T, CP2.R | the same, appended to the `holds no replay files` refusal | green | both red |
| CP3.T, CP3.R | the same, appended to evidence honesty's `different impostor policies` raise | green | both red |

C2.4, the verifier's probe, fails
`test_the_reconstructors_walk_every_meeting_of_every_arm_that_exists_today[reset]`; C2.1 fails
`test_the_reconstructors_hand_the_recorded_witness_rule_to_the_engine_helper[committed-meeting walk]`;
GR.7 fails `test_the_reconstructors_walk_every_meeting_of_a_copy_carrying_the_pending_values`. No
survivor remains, so none is named equivalent.

**Verification at `078ab37a`**, every command from the card's Validation with its real exit code
(production bytes are those of `f489cf13`, so the base-and-head bundle comparison above still holds:
no file under `api/`, `frontend/`, `meetings/` or any production module changed since).

| Command | Result |
| --- | --- |
| `uv run pytest tests/eval/test_recorded_arm_readers.py tests/meetings/test_transcript.py tests/meetings/test_prompt_byte_golden.py tests/_helpers tests/experiments/test_gameplay_facts_refuses_experiments.py tests/scripts/test_process_scorecard.py -q -n 6` | exit 0, 379 passed (370 before, plus the nine new cases) |
| `uv run pytest tests/eval/test_evidence_honesty.py tests/eval/test_funnel.py tests/eval/test_kill_craft.py tests/eval/test_solvability.py tests/eval/test_win_condition_selfcheck.py tests/meetings/test_reasoning_evidence.py tests/meetings/test_manager.py -q -n 6` | exit 0, 491 passed |
| `bash scripts/verify_samples.sh replays/samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i` | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each |
| `uv run python scripts/publish_process_scorecard.py --check`; `uv run python scripts/publish_gameplay_census.py --check` | exit 0 each |
| `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` and `... replays/samples/4p1i` | exit 0 each; sha256 `97aa858e...` and `d0500f96...`, the merge base's values above |
| `uv run python scripts/publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; byte-equal to the `samples/9p2i` entry of `docs/process-scorecard.json` under the committed serializer settings |
| `uv run python scripts/check_doc_facts.py`; `uv run python scripts/validate_task_docs.py` | exit 0 each |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 62 checks, 50 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |
| `uv run pytest -m campaign -q -n 6` | exit 0, 336 passed |
| `bash scripts/check.sh` (exit code read directly, no pipe) | exit 0: ruff and format clean, `lint-imports` 4 kept, task docs valid, mypy clean over 506 files, 9,003 passed, 20 skipped, 3 xfailed; frontend lint, `tsc:check`, 559 vitest tests and the build pass |

The gate ran on `078ab37a` with this subsection in the working tree, all of it but the `check.sh` row
above; the commit carrying this subsection adds that row too and changes nothing else (the task-docs
validator was re-run on it, exit 0). A first run stopped at the frontend lint with exit 127
(`eslint: command not found`) after every Python stage had passed, because this worktree had no
`frontend/node_modules`; after `npm ci` in `frontend/` the run above passed.

### Review corrections, round 2 (2026-09-26)

Five blocking findings from the round-2 verifiers on `9bab8d16`, all repaired in `29707b99`. That
commit changes tests and one docstring. No production logic, recording, derived view, fixture, doc
fact or `audits/` byte moved: `git diff --stat 9bab8d16 29707b99` lists `meetings/transcript.py`
(one docstring bullet) and four test files. No Codex comment was posted on the PR beyond its review
summary, so there is none to answer.

- **Survivors in `walk_chain`'s rebuttal errors (correctness).** The missing-pick message with the
  pick's speaker set to `'p-1'`, and the extra-turn message with its index set to 5, left every test
  green. The tests matched fixed phrases, and their only pick and index equalled those constants.
  `TestWalkChainBoundedRebuttal` now runs every case over two shapes. The opener of four has pick
  `p-1`, charge `m-1:turn-1`, reply at turn 4 and extra turn 5. The first speaker of three has pick
  `p-3`, charge `m-1:turn-2`, reply at turn 3 and extra turn 4. Each shape also has its own wrong
  speaker and wrong charge. Every message is matched whole (`^...$`). The no-setting and no-pick
  cases take both kinds that can reach the trailing slot (`reply`, `opening`), and the no-pick case
  runs over two transcripts, three turns long and two. `test_walk_chain_accepts_exactly_the_selected_rebuttal`
  matches all seven messages whole with the generated index, kind, speaker and charge. It gains the
  wrong-charge, extra-turn and non-reply cases, and it checks the no-setting refusal on every
  generated chain. `test_the_same_script_without_the_setting_records_no_rebuttal` pins the
  records-none message on a recorded game, with the pick read back and checked against the opener
  and turn 1.
- **Survivors in the new refusal messages of three modules (correctness).** Each message is now
  matched whole, with values that differ between cases:
  - `eval/recorded_settings.py`: formats 2 and 3 under two reader names; the unread-setting message
    for two field lists, the nine readable settings and `meeting_reset, vent_witness_rule`, with two
    fields, two values and two readers; the outside-list refusal with two readers and two outside
    lists.
  - `eval/evidence_honesty.py`: the custom-factory raise on recordings made at seeds 0 and 2, naming
    `headless-seed-0` and `headless-seed-2`. The mixed-set raise names the real directory and
    `['live-policy-fold', 'recorded-arm-policy-fold']`.
  - `scripts/publish_process_scorecard.py`: the no-replay parser refusal's last line ends with the
    real temporary directory.
- **Survivors MA1 and MA12 to MA17 in `_check_bounded_rebuttal_tail` (docs lens).** The round-1
  table claimed 15 of 15 red and no survivor for this file. That held only for the probes that pass
  ran. The same cases now pin each argument, and the round-2 probes below cover every message
  argument of the tail check and the no-setting refusal, 16 in all.
- **Survivors MA6, MA7, MA8 and MA10 (docs lens).** They are covered by the cases above. The
  plain-copy scan now asserts, before it swaps in `DIR`, that the no-replay refusal's last line
  names the real directory and that the mixed-set raise starts with it. The rewrite can no longer
  hide a refusal that named a constant.
- **The module docstring (docs lens).** The `walk_chain` bullet in `meetings/transcript.py`'s module
  docstring said the tail is `opt_in`. It now says the tail is opt-in turns except for the one
  selected rebuttal reply the recorded `bounded_rebuttal_version` setting may add after them.

**Changed and renamed tests** (none weakened, skipped or deleted; every old `match` fragment is a
substring of the new whole message for the first shape):

- `TestWalkChainBoundedRebuttal`: its 9 tests are parametrized over the two shapes (22 cases).
  - `test_a_trailing_reply_without_the_setting_raises` is renamed
    `test_a_trailing_turn_without_the_setting_raises` and takes both trailing kinds.
  - `test_no_pick_and_no_reply_passes_and_a_reply_then_raises` is renamed
    `test_no_pick_and_no_reply_passes_and_a_trailing_turn_then_raises` and runs over two
    transcripts and both kinds.
- `test_walk_chain_accepts_exactly_the_selected_rebuttal` draws the trailing kind as well.
- `test_refusing_unread_settings_names_the_reader_and_the_field` matches whole. Its outside-list
  assertion moves to the new `test_a_field_list_outside_the_reviewed_set_is_refused_with_the_reader`.
  `test_a_later_settings_format_is_refused_with_the_reader_and_the_format` is new.
- `test_a_recording_from_a_custom_factory_is_refused_by_name` now records its own source game at
  seeds 0 and 2, where it used to read the module fixture's seed-0 recording.
- `test_a_set_whose_games_name_different_policies_raises` and
  `test_set_dir_refuses_what_it_cannot_serve` match whole.

**Round-2 probes.** One edit per probe, made in place from a byte copy. Each probe ran only its
targeted suites (`pytest -x -q -n 6 -p no:cacheprovider`): for `meetings/transcript.py`,
`tests/meetings/test_transcript.py`, `tests/_helpers/test_scripted_meeting.py` and
`tests/meetings/test_manager.py`; for `eval/recorded_settings.py` and `eval/evidence_honesty.py`,
`tests/eval/test_recorded_arm_readers.py`; for the scorecard, that file and
`tests/scripts/test_process_scorecard.py`. The file was restored from its copy and its sha256
compared; all 58 restores matched. Every probe ran twice: first with the four test files installed
at their `9bab8d16` bytes, then with them restored from copies of the round-2 bytes (sha256 checked).
The one operator class is a message argument replaced with a constant; each constant is the value
the round-1 tests used, where they used one. The probe script is a scratch file, not committed.

| Probe | Edit (the argument, and the constant it became) | At `9bab8d16` | At `29707b99` |
| --- | --- | --- | --- |
| MA1 | records-none: `pick.speaker` to `'p-1'` | green | red |
| MA12 | records-none: `pick.reply_to` to `'m-1:turn-1'` | green | red |
| MA13 | no-charge-left: `turn.turn_index` to 3 | green | red |
| MA14 | no-charge-left: `turn.turn_kind` to `'reply'` | green | red |
| MA15 | non-reply slot: `turn.turn_kind` to `'reply'` | green | red |
| MA15E | non-reply slot: `turn.turn_kind` to `'opening'` | green | green, equivalent |
| MA15I | non-reply slot: `turn.turn_index` to 4 | green | red |
| MA16 | extra turn: `extra.turn_index` to 5 | green | red |
| MA17 | wrong speaker: `turn.speaker` to `'p-5'` | green | red |
| MA18 | wrong speaker: `turn.turn_index` to 4 | green | red |
| MA19 | wrong speaker: `pick.speaker` to `'p-1'` | green | red |
| MA20 | wrong charge: `turn.turn_index` to 4 | green | red |
| MA21 | wrong charge: `turn.reply_to` to `'m-1:turn-0'` | green | red |
| MA22 | wrong charge: `pick.reply_to` to `'m-1:turn-1'` | green | red |
| MA23 | no setting: `turn.turn_index` to 4 | green | red |
| MA24 | no setting: `turn.turn_kind` to `'reply'` | green | red |
| MA6 | outside list: `reader` to `'r'` | green | red |
| RS2 | outside list: `outside` to `['crew_idle_policy']` | green | red |
| RS3 | later format: `recorded.format_version` to 2 | green | red |
| RS4 | later format: `reader` to `'r'` | red | red |
| RS5 | unread setting: the joined field list to `'x'` | green | red |
| RS6 | unread setting: `reader` to `'r'` | red | red |
| RS7 | unread setting: `field` to `crew_idle_policy` | red | red |
| RS8 | unread setting: `value` to `'patrol'` | red | red |
| MA7 | custom factory: `game_id` to `headless-seed-0` | green | red |
| MA8 | mixed set: `sorted(modes)` to `['live-policy-fold']` | green | red |
| MA8E | mixed set: `sorted(modes)` to `['live-policy-fold', 'recorded-arm-policy-fold']` | green | green, equivalent |
| H3 | mixed set: `sample_dir` to `DIR` | green | red |
| MA10 | no replay: `args.set_dir` to `DIR` | green | red |

29 probes: 25 green and 4 red against the round-1 tests; 27 red and 2 green against the round-2
tests. Both greens are equivalent:

- MA15E: a trailing `opt_in` joins the roll call and a `reply` takes the next branch, so the only
  kind that reaches the non-reply message is `opening`. That literal prints the same bytes.
- MA8E: an explicit policy gives every game one mode, and the recorded policy gives each game the
  live fold or the recorded-arm fold. So the only set with two modes names exactly those two
  labels, which is that literal.

The verifier's probes are MA1 and MA16 (finding 1), MA1 and MA12 to MA17 (finding 3), RS3, RS5,
MA7, MA8, MA10 (finding 2) and MA6, MA7, MA8, MA10 (finding 4). MA1 fails
`test_a_missing_pick_raises[first-speaker-of-three]` and the scripted-game case. MA16 fails
`test_two_trailing_replies_raise[first-speaker-of-three]`. MA10 fails
`test_set_dir_refuses_what_it_cannot_serve[no-replays]`.

**Closing greps.** Case-insensitive, over the whole tree except `tasks/`, `audits/` and
`agent_prompts/`:

- `git grep -niE 'tail (is|are|turns are|must be) .{0,4}opt.?in'`: two hits, the two corrected
  sentences. One is the module docstring's bullet (`meetings/transcript.py:24`), which continues
  "except for the one selected rebuttal reply". The other is `walk_chain`'s opening sentence
  (`:498`), which continues "save the one selected rebuttal".
- `git grep -niE 'tail.{0,40}opt.?in|opt.?in.{0,40}tail'` outside `tests/`: those two, the
  docstring's line on a recording made without the setting (`:507`) and three code lines.
- `git grep -niE 'terminal opt.?ins?'` outside `tests/`: two hits.
  `agents/strategic/prompts/qwen3_5_9b/accusation_round.j2:20` is a frozen prompt template about the
  roll-call turn. It is true under both settings and out of scope: a prompt byte change needs an
  adopting record. `design/phase-12/stage-0-understand.md:86` is the phase-12 understanding
  snapshot. It describes a meeting made without the setting, which is every committed recording.
  The seven hits under `tests/` describe fake games recorded without the setting.

**Verification.** These runs used `29707b99`'s production and test bytes, before the commit that
carries this subsection. That commit changes only this card.

| Command | Result |
| --- | --- |
| `uv run pytest tests/eval/test_recorded_arm_readers.py tests/meetings/test_transcript.py tests/meetings/test_prompt_byte_golden.py tests/_helpers tests/experiments/test_gameplay_facts_refuses_experiments.py tests/scripts/test_process_scorecard.py -q -n 6` | exit 0, 397 passed (379 before; 13 more rebuttal-class cases, 4 new settings cases, 1 more custom-factory case) |
| `uv run pytest tests/eval/test_evidence_honesty.py tests/eval/test_funnel.py tests/eval/test_kill_craft.py tests/eval/test_solvability.py tests/eval/test_win_condition_selfcheck.py tests/meetings/test_reasoning_evidence.py tests/meetings/test_manager.py -q -n 6` | exit 0, 491 passed |
| `bash scripts/verify_samples.sh replays/samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i` | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `uv run python scripts/publish_process_scorecard.py --check`; `uv run python scripts/publish_gameplay_census.py --check` | exit 0 each, consistent |
| `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` and `... replays/samples/4p1i` | exit 0 each; sha256 `97aa858e...` and `d0500f96...`, the merge base's values |
| `uv run python scripts/publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; equal to the `samples/9p2i` entry of `docs/process-scorecard.json` as parsed JSON and byte for byte under the committed serializer settings |
| `uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head`, and `--out <scratch>/bundle-prev` with `meetings/transcript.py` at its `9bab8d16` bytes, restored from a copy afterwards (sha256 checked) | exit 0 each: 7 featured games, 156 baked JSON files |
| `diff -r bundle-prev bundle-head` | empty, exit 0 (194 files each). `9bab8d16`'s production bytes equal `f489cf13`'s, whose bundle equalled the merge base's (above), so the merge republishes identical bytes |
| `uv run python scripts/check_doc_facts.py`; `uv run python scripts/validate_task_docs.py` | exit 0 each (88 work cards) |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 62 checks, 50 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |
| `uv run pytest -m campaign -q -n 6` | exit 0, 336 passed |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 329 files; 26,636,557 bytes, the `docs/artifacts.md` row, unchanged (no `audits/` byte moved, and `main` has not moved from `bdfa5b19`) |
| `git diff --stat $(git merge-base origin/main HEAD) HEAD -- replays agents engine observation orchestrator api frontend docs/process-scorecard.md docs/process-scorecard.json` | empty |
| `bash scripts/check.sh` (exit code read directly, no pipe), at `325fd4f9` in this clean worktree | exit 0: ruff and format clean, `lint-imports` 4 kept, task docs valid, mypy clean over 506 files, 9,021 passed (9,003 before, plus the 18 new cases), 20 skipped, 3 xfailed; frontend lint, `tsc:check`, 559 vitest tests and the build pass |

The gate ran once, on `325fd4f9`, which carries this subsection without the `check.sh` row above.
The commit that adds the row changes nothing else, and the task-docs validator was re-run on it
(exit 0).

### Review corrections, round 3 (2026-09-26)

One blocking finding from the round-3 verifiers on `f35e0fe5`, plus the dispatch's scoped follow-up:
merge `main` now that the physical-witness card (B0, #485) has landed, and run the physical-witness
leg of the event-level test that the Limitations above left to B0. No Codex comment was posted on
the PR beyond its review summary, so there is none to answer.

- **The merge (`638a7c26`).** `origin/main` at `fb9d2e31` merged in with `git merge`, no rebase. The
  two histories share one file, `tasks/README.md`'s derived inventory sentence. It merged textually
  clean at "8 ready, 80 done", but that was stale, since each side had flipped a different card to
  done. `scripts/validate_task_docs.py` re-derived it as 7 ready, 81 done. From here on, `git diff
  fb9d2e31 <head>` shows only this card's work.
- **Survivor V4 in `read_recorded_settings` (correctness).** With the `TickOpened` filter dropped
  (`if not checked:`), every test stayed green, because every stream the tests fed the refusal
  opened with a `TickOpened`. The mutant is not equivalent: an empty replay's walk opens with its
  `WalkComplete`, which has no `entry`, so the mutant raises `AttributeError` where
  `check_replay_win_condition` returns the vacuous check. Three planted cases now hold the filter
  (`29d27544`, tests only), all in `tests/eval/test_recorded_arm_readers.py`:
  - `test_a_leading_event_that_is_not_a_tick_row_passes_and_the_tick_row_refuses` puts a
    `WalkComplete`, a `TickAdvanced` or a `MeetingOpened` from the workload recording's own walk in
    front of that walk. The leading event comes back as the same object, and the next pull raises
    the unread-setting message, matched whole, under a reader name no other case uses.
  - `test_an_empty_replay_walks_to_the_vacuous_self_check` shows an empty replay's walk is its
    `WalkComplete` alone. It pins `check_replay_win_condition` at seed 2 to the all-`None` check
    named `headless-seed-2`.
  - `test_the_first_tick_row_speaks_for_the_recording` plants `crew_idle_policy="patrol"` on the
    second tick row. The walk has already checked that every row agrees, so only the first row is
    read and every event passes through as the same object. This also holds the first-row guard,
    probe V5 below.
- **The physical-witness leg (the event-level acceptance item's B0 clause).** B0 threads
  `vent_witness_rule` through the spine's engine helper and drops the rule from the wave's pending
  guard. So the module fixture now records a fake game under `vent_witness_rule="physical"`, with no
  guard patched open.
  - The recorded-arm refusals accept the rule. The physical recording joins the arms of
    `test_a_widened_reader_verifies_every_arm_that_exists_today` (five readers) and
    `test_the_reconstructors_walk_every_meeting_of_every_arm_that_exists_today`. There the committed
    walk yields every recorded meeting and the golden re-renders every prompt byte-equal. It also
    joins `test_honesty_verifies_every_arm_it_reads`.
  - The stand-in reaches every reader under the rule.
    `test_on_a_physical_recording_the_stand_in_and_the_rule_reach_every_advance` covers the five
    profiles, the pooling funnel, the committed walk and the golden, each threaded and withheld (16
    cases). It installs the planted helper and the stand-in engine at the walk and the golden. The
    engine then sees the stand-in on every tick row's advance, and the rule `physical` on every
    advance. The stand-in is R7's shape, which the physical rule already produces, so each reader's
    output equals its output without the stand-in. For the golden that means every prompt
    re-renders byte-equal. The perturbed case plants a helper that withholds the rule. Every hash
    still verifies, and only the rule the engine received (`both_rooms`) tells it apart.
  - The folding readers follow the rule.
    `test_withholding_the_physical_rule_changes_what_a_vent_folding_reader_folds` reads the same
    recording through a helper that withholds the rule. The funnel's vent sightings, evidence
    honesty's rebuilt memories, the committed walk's vent witness records and the golden's rendered
    memory each change, at the same size.
  - Non-vacuity. `test_the_physical_recording_holds_exits_the_rule_changes` asserts the recording
    holds vent exits and that no exit into another room lists the room left under the recorded rule.
    It also asserts that withholding the rule gives at least one exit a witness in the room left
    who is absent from the room surfaced into.
  - Only sizes, counts, witness records and one boolean reach these assertions, so a failure prints
    no rendered prompt or memory.
  - The earlier spy case, `test_the_reconstructors_hand_the_recorded_witness_rule_to_the_engine_helper`,
    is unchanged. It holds whether or not the helper threads the rule.

**Changed tests** (none weakened, skipped or deleted): the two arm parametrizations now read one
`_ARMS_TODAY` tuple with `physical` added. `_StandIn` also records the rule each advance handed the
engine, and it takes a `withhold` switch. The readers file goes from 122 to 154 cases: 3 leading
events, the first-row case, the empty replay, the non-vacuity case, 16 reach cases, 4 fold cases, 5
widened-reader arms and 1 reconstructor arm.

**Round-3 probes.** One edit per probe, made in place from a byte copy. Each probe ran twice with
`pytest -x -q -n 6 -p no:cacheprovider`: first with the readers test file at its `f35e0fe5` bytes,
then at its `29d27544` bytes. The V probes ran `tests/eval/test_recorded_arm_readers.py`. The P
probes ran the same file with `-k physical`, so only the physical leg could turn them red. Each file
was restored from its copy and its sha256 compared; all 9 restores matched and the tree was clean
after. Red means real test failures: a re-run of each red probe without `-x` names the failing
cases. The probe script is a scratch file, not committed.

| Probe | Edit (operator class) | At `f35e0fe5` | At `29d27544` |
| --- | --- | --- | --- |
| V4 | `if not checked and isinstance(event, TickOpened)` to `if not checked` (drop a filter; the verifier's probe) | green | red: the three leading-event cases and the empty replay |
| V4I | `isinstance(...)` to `not isinstance(...)` (the check's inverse) | red | red |
| V4S | `TickOpened` to `TickAdvanced` (one type swapped for a related one) | red | red |
| V5 | `not checked and` dropped (drop a filter) | green | red: `test_the_first_tick_row_speaks_for_the_recording` |
| V6 | `event.entry.experiment_config` to `None` (a loaded source's read replaced with the canonical literal) | red | red |
| V7 | `reads=reads` to `reads=READABLE_SETTINGS` (one collection swapped for a related one) | red | red |
| V8 | `reader=reader` to `reader='r'` (a message argument to a constant) | red | red |
| P1 | the golden walk's `engine_arguments(recorded)` to `engine_arguments(None)` (a loaded source's read replaced with the canonical literal) | no physical case to run (pytest exit 5) | red: 4 cases, the golden's reach, fold and every-meeting cases |
| P2 | `eval/replay_walk.py`'s `engine_arguments(experiment)` to `engine_arguments(None)` (the same class, at the spine's site the other seven readers use) | no physical case to run | red: 13 cases |

9 probes, no survivor. P2 edits the spine's file only inside the probe, restored byte for byte;
neither this card nor round 3 changes it.

**Verification.** These runs used the production and test bytes of `29d27544`, before the commit
that carries this subsection. That commit changes only this card. No production module, recording,
derived view, fixture, doc fact or `audits/` byte moved in round 3. `git diff --stat 638a7c26
29d27544` lists the one test file, and the merge adds only `main`'s own bytes plus the re-derived
inventory sentence.

| Command | Result |
| --- | --- |
| `uv run pytest tests/eval/test_recorded_arm_readers.py tests/meetings/test_transcript.py tests/meetings/test_prompt_byte_golden.py tests/_helpers tests/experiments/test_gameplay_facts_refuses_experiments.py tests/scripts/test_process_scorecard.py -q -n 6` | exit 0, 429 passed (397 before, plus the 32 new cases) |
| `uv run pytest tests/eval/test_evidence_honesty.py tests/eval/test_funnel.py tests/eval/test_kill_craft.py tests/eval/test_solvability.py tests/eval/test_win_condition_selfcheck.py tests/meetings/test_reasoning_evidence.py tests/meetings/test_manager.py -q -n 6` | exit 0, 491 passed |
| the same, plus B0's `tests/eval/test_vent_witness_readers.py` and `tests/eval/test_replay_walk.py` | exit 0, 555 passed |
| `bash scripts/verify_samples.sh replays/samples/9p2i`, `samples/4p1i`, `ml_corpus/9p2i`, `ml_corpus/4p1i` | exit 0 each: 50, 50, 150, 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, the four sets | exit 0 each, consistent |
| `uv run python scripts/publish_process_scorecard.py --check`; `uv run python scripts/publish_gameplay_census.py --check` | exit 0 each, consistent |
| `uv run python scripts/measure_baseline.py --honesty replays/samples/9p2i` and `... replays/samples/4p1i` | exit 0 each; sha256 `97aa858e...` and `d0500f96...`, the values above |
| `uv run python scripts/publish_process_scorecard.py --set-dir replays/samples/9p2i --json-stdout` | exit 0; equal, as parsed JSON, to the `samples/9p2i` entry of `docs/process-scorecard.json` (`sets[1]`) |
| `uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head`, and `--out <scratch>/bundle-base` with this card's ten production files at their `fb9d2e31` bytes (`eval/recorded_settings.py` removed), restored from copies afterwards (sha256 checked) | exit 0 each: 7 featured games, 156 baked JSON files |
| `diff -r bundle-base bundle-head` | empty, exit 0 (194 files each): merging this card into `fb9d2e31` republishes identical bytes |
| `uv run python scripts/check_doc_facts.py`; `uv run python scripts/validate_task_docs.py` | exit 0 each (88 work cards) |
| `uv run python scripts/verify_ml_evidence.py` (offline) | exit 0: 62 checks, 50 OK, 0 FAIL, 7 ABSENT, 5 INFO |
| `uv run lint-imports` | exit 0: 4 kept, 0 broken |
| `uv run pytest -m campaign -q -n 6` | exit 0, 336 passed |
| `git ls-files audits \| wc -l`; `git ls-files -z audits \| xargs -0 cat \| wc -c` | 329 files; 26,636,557 bytes, the `docs/artifacts.md` row, unchanged (B0 moved no `audits/` byte) |
| `git diff --stat fb9d2e31 HEAD -- replays agents engine observation orchestrator api frontend docs/process-scorecard.md docs/process-scorecard.json` | empty |
