# Closed unexecuted: the gameplay-facts extractor was not widened to a declared era

**Status:** done

## Outcome

CLOSED UNEXECUTED on 2026-10-09, as superseded. That day the owner ruled, verbatim: "Merge both when verified and
retire the memo's D14 list" (decision memo 8.9). The ruling retires the list, G27 among it, and does not dispatch this
card's optional widening, which its Constraints left to the owner's word under D14. Its other job, the W0 -> W1 -> W2
rows, is on the retired list: the baselines memo's G27 row (Part 3.1) deletes the three Phase-10 fixtures and first
replaces the extractor's reading of them with one history line, and 8.9 lands the whole list as one retirement card.
Nothing below was built. The rest of this card is the contract as it stood at `225d2b77`, kept unchanged as the
record of what was proposed; the Results say what closed and what stays.

On 2026-10-06 the owner ruled on the shown set's rubric, verbatim: "Profile as recommended, decisive, and ship the
shelf". Rubric version 2 is the role-blind game-shape profile of the design memo
(`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/rubric-design-2026-10-06/rubric-design-memo.md`,
Part 2), published by `rubric-v2-profile` from the census carrier. Version 1 (R1-R7, the weighted geomean, the
scalar railroad floor and `experiments/lab/rubric_score.py --set-dir`) is retired for the `stage-b-r2` era and kept
as baseline-9 lab history. This card used to widen the extractor so that version 1 could be served for the era. That
purpose is gone; the refresh step, the viewer copy, the bundle and the served file's registry row are the profile
card's. The extractor still refuses the era by name, and three things still reach it:
- **The W fixtures.** Its W0 -> W1 -> W2 rows read `tests/fixtures/phase10/corrected_w{0,1,2}_baseline.json`, those
  files' only code consumer outside tests (the baselines memo's G27), so retiring them under D14 is coupled to it.
- **The facts path.** Its temp facts JSON is where the gameplay-data audit workflows start, and what the refresh
  script's rubric step ran until the profile card rewires that step to its own publisher. After the rewire the
  refresh script runs no extractor.
- **The referee's historical mode.** The frozen `historical_15_2` mode of `eval/watchability.py` has one
  cross-implementation check: the baseline-9 fixture, held to itself. A row for the shown era needs an extractor
  that reads the era.

This card exists for those consumers. It is optional and dispatches only if the owner rules so under D14. When it
is done:
- The extractor reads a recording under its own recorded config. It names, field by field, the settings it reads,
  and refuses any other by name before its first advance. It runs the recorded engine, reset, rebuttal and regroup.
- Version 1 is never served for `stage-b-r2`. The facts stay a temp file. The era's only committed output is one lab
  file, `experiments/lab/results-rubric-geomean.stage-b-r2.json`: the extractor's correctness witness against the
  frozen referee, re-derived on every run. It holds the era's per-game version-1 geomean reading (each game's score,
  floor multiplier and r1, r2, r3 and r7 sub-scores, the shape of `experiments/lab/results-rubric-geomean.json`), lab
  only and never served: the labelled-history option of the design memo's Part 3.
- The W0 -> W1 -> W2 rows are deleted with one history line. The extractor reads nothing under
  `tests/fixtures/phase10/`, so D14 can retire those fixtures without touching it.
- Baseline-9 history does not move, and the widened extractor still reproduces it from its own bytes. Nothing ships.

## Evidence

Every `path:line` is at `76270d6c` (labelled as such) and is re-anchored by its symbol at dispatch. The extractor
and its two refusal tests, the lab scorer, the refresh script, the cooldown and arm gates, `engine/`, `agents/`,
`meetings/`, `orchestrator/`, every `eval/` module the extractor imports and `replays/samples/9p2i` are
byte-identical between `59bbd1be`, where this card was first written, and `76270d6c` (`git diff --stat` over those
paths prints nothing). Every count is count-only, keyed by (set, meeting), re-measured at `76270d6c` by the scratch
probes named below (about 3 s each, not committed), and re-measured at dispatch; the dispatch figure governs. No
prompt, transcript or seed-band prefix was printed.

**What the ruling moved off this card.** The design memo's reproduction script (`rubric-v2-repro.py`, beside the
memo; run from the repository root with `.venv/bin/python`) reads the census carrier, not the extractor. It exited
0 in 6.1 s at `76270d6c`. Tripwire T1 under the decisive quantifier trips seed 26, meeting index 2, only; "every"
trips none and "any" trips two (seeds 26 and 41). The ejecting ballots are 282 `supported` and 2 `off_target`.
`uv run python scripts/publish_gameplay_census.py --check` reports the census pages consistent with the committed
recordings. Neither needs this card. The memo's Part 3 splits the held card in two: this one (its Card A) and
`rubric-v2-profile` (its Card B).

**Who reaches the extractor** (at `76270d6c`):
- `scripts/refresh_samples.sh:1123-1166` runs it only inside the rubric step, and skips the era with one named line
  (`:1137-1138`; dry run `:585-589`). The profile card rewires that step.
- `_cross_era_trajectory` (`audits/workflows/extract_gameplay_facts.py:673-779`) reads the three fixtures
  (`:698-703`). It is called at `:3520`, carried into the facts at `:4548` and quoted by a self-check line at
  `:3822-3828`. A missing fixture reads as `{"present": False}` (`:702-703`), so deleting the fixtures first would
  degrade the rows silently. `git grep cross_era` finds no reader outside the extractor. On the era (under the
  widening below) the block compares the shown set's live row with `corrected_w2_baseline.json`, a frozen
  baseline-9 anchor (`tests/eval/test_gate_spec_metrics.py:111-119`): effective deflection False, genuine class
  True. It compares two eras and describes neither.
- `tests/eval/test_watchability.py:130-168` holds the baseline-9 geomean fixture to itself; its docstring says the
  extractor "does not read the promoted era" (`:139-140`). The audit workflows start from the extractor
  (`audits/workflows/gameplay-data-audit-v2.workflow.js:603`, `:827-828`; `forward-redesign.workflow.js:336-337`);
  they are dated prompt text and stay as written. Beyond those, three `tests/experiments/test_gameplay_facts_*.py`
  modules, `tests/eval/test_recorded_arm_readers.py:1660-1699` and comment lines in four other tests name it. No
  production surface reads it for the era.

**The refusal, and what it hides.** `refuse_experiment_settings` (`:184-206`, called at `:2152`) exits at the first
seed with any setting off its default, which on the shown set is seed 0. The extractor seeds at `:2135-2141`,
advances at `:2265` and applies meetings at `:2781-2786`, none of them with the recording's settings. Probe 1
imports the module and replaces the refusal with a no-op. The run records 1,885 invariant failures (1,801 tick-hash,
81 post-meeting-hash, 3 other), and 3 of its 16 self-checks fail.

**The minimal widening, measured.** Probe 2 wraps the module's three engine bindings. The seeding and every advance
take `engine_arguments(recorded_experiment_config(entries))` (`orchestrator/experiment_config.py:338-369`). Every
applied meeting takes the same values plus the recorded `meeting_reset`. On the shown set it reads 16 of 16
self-checks OK and no invariant failure. Its findings:
- 44 cross-room rejections (`REJ`, high) and 99 dead-actor rejections (`REJ`, informational), the kinds the walk
  always reports;
- 114 `OPTIN` and 3 `TERM` high findings, one per meeting (117). At authoring on `59bbd1be`, on identical bytes,
  each was traced to the meeting's last reply, the one `meetings.rebuttal.select_bounded_rebuttal` re-derives from
  the turns before it.

Probe 3 reads the same recordings and probe 2's facts:
- The regroup: 67 of 117 meetings carry derived regroup ticks. The re-derived flags are 78 with or without them, and
  no meeting's flags differ.
- The prompt classes: 120 opening, 420 opt-in, 271 reply and 691 vote calls, none unclassified. Every vote call
  parses at least one suspicion row (3,101 in all). The composite `v8` prompt stamps never reach the extractor,
  which reads no prompt-version field.
- Version 1's interestingness reading of the era (the served file's shape), for the lab only (never served, never
  committed): 50 rows, mean 25.1, median 18.4, top 86.2, and 16 games at 0, all from the railroad floor. Win shapes:
  impostor-win 24, eject-decided 13, stopwatch-some-eject 10, stopwatch-no-eject 3. The geomean witness this card
  does commit is a second per-game version-1 reading of the era (Acceptance, the witness item).
- The geomean body equals `compute_game_score(..., historical_15_2=True)` (`eval/watchability.py:2265`) on all 50
  games and all eleven `_PARITY_KEYS` (`tests/eval/test_watchability.py:65-77`), to 1e-6.

**Baseline 9 from its own bytes.** Probe 4 runs on a `git archive d41c9006 replays/samples/9p2i` export. The export
carries the retired served file (blob `4879637e`) at the very path the scorer wrote, so it was moved aside first.
The extractor exits 0, and none of its 17 self-check lines fails. Four values equal the retired file's four keys:
`interestingness(facts)`, `_set_manifest_sha` (`27646d67`), `recording_fingerprint` and the seedset. The JSON
rebuilt from them is byte-identical to the retired file. `geomean_validation(facts)` equals the frozen fixture's
body. The scorer reads no `cross_era_trajectory` key, so the reproduction does not depend on the rows this card
deletes. Nor does it need `regen_for_set` or `--set-dir` (`experiments/lab/rubric_score.py:1337`, `:1381`), which
the profile card deletes.

**The arms, and what each asks of the extraction.**

| recorded setting | layer | what the extractor must do |
|---|---|---|
| `redistribution_policy` (default in the era) | engine | take it from the helper at every advance and every meeting, as every reader does |
| `kill_cooldown_ticks` 6 | engine | take it from the helper at the seeding, every advance and every meeting; without it the hashes diverge |
| `vent_witness_rule` physical | engine | take it from the helper; no extractor fact reads a witness event (vent channels are rebuilt from recorded flags, `:437-521`) |
| `meeting_reset` hub_with_grace | orchestrator | pass it to every applied meeting; pass the derived regroup ticks to the contradiction re-derivation, as the live manager does (`meetings/manager.py:1476-1484`) |
| `bounded_rebuttal_version` 1 | meeting | accept exactly the one trailing reply the selector picks (`walk_chain`, `meetings/transcript.py:487`); today it reads as 117 protocol findings |
| `report_body_handle_version` 1 | orchestrator | nothing: it changes only a report's trigger text, which no fact reads |
| `ballot_kill_row_version` 1, `impostor_ballot_version` 1 | meeting | prompt composition only; the slot classifier and the suspicion-graph parse (`:572-634`) must keep classifying |
| `vent_exit_policy` look_and_wait, `vent_entry_policy` own_fresh_kill | tactical | nothing: they reach the walk as recorded actions, and no policy is re-run |
| `route_lines_version` (`route-lines-field`'s field, under the name it merges with; not in the shown era) | meeting | prompt composition only; the vote-slot classifier and the suspicion-graph parse must classify a ballot prompt that carries the routes block |

The regroup ticks and the prompt classification read as no-ops on these bytes (probe 3). They are kept because the
live game has them. The route-lines row has no committed era to measure on; it is planted on a scripted route-lines
recording (Acceptance, the first item and the arm item).

**What goes false when the extractor reads the era** (at `76270d6c`, outside dated history):
- The refusal's own tests and docstrings: `tests/experiments/test_gameplay_facts_refuses_experiments.py` (whole);
  `tests/experiments/test_gameplay_facts_genuine_class.py:18-21`, `:100-109`;
  `tests/eval/test_recorded_arm_readers.py:1660-1661`, `:1692-1699` (the "extractor" copy case);
  `tests/eval/test_watchability.py:139-140`.
- Lines on surfaces the profile card rewrites: `api/routes/eval.py:235-236`;
  `frontend/src/components/ReplayPicker.tsx:19-21`; `frontend/e2e/evidence-journey.ts:58-59`;
  `scripts/refresh_samples.sh:586`, `:1133-1138`; `tests/api/test_sets.py:331-332`, `:456`;
  `tests/scripts/test_build_demo_bundle.py:313-314`; `tests/scripts/test_refresh_samples.py:2239`. Whatever of
  these survives the profile card's merge is fixed here.
- The lab report's run line (`experiments/lab/report-rubric-interestingness.md:65-69`) names `--set-dir` and the
  unkeyed outputs. The profile card fixes the `--set-dir` half, and this card the output name.

**The alternatives weighed.**
- **(a) Widen the extractor: contracted, optional.** The measured cost is three threaded calls, the reset, the
  rebuttal acceptance and the regroup ticks. It buys an extractor the audit workflows can point at the shown era,
  an era-keyed parity row for the frozen referee, and a baseline-9 reproduction that stays runnable.
- **(b) Drop it.** This card closes as superseded with one history line, and D14's G27 card deletes
  `_cross_era_trajectory` itself. The era-keyed parity row is never built.
- **Not taken: moving the extractor onto `eval/replay_walk.py`.** That would put the threading in one place, but
  moving a 4,670-line fold is a refactor with its own byte-parity contract. The helper threading reaches the same
  engine values and is pinned by the same scan. The held card's options for serving version 1 (the referee's facts,
  an era-neutral facts source) fell with version 1.

## Acceptance

  - No test is weakened. Results names each re-targeted test's old assertion and the strength it keeps.
  - It reads `eval.recorded_settings.READABLE_SETTINGS` (`eval/recorded_settings.py:40-53`), looked up at call
    time, as `REFEREE_READS` is (`eval/watchability.py:1604`). An immutable module constant maps each field to one
    line of reason from the arm table. A test holds its keys equal to `READABLE_SETTINGS`, so a field another card
    adds fails until its row lands. `route-lines-field`'s field is the known one, and its row is this card's (the arm
    table's last row), since this card dispatches from a `main` that holds that field.
  - Before the first advance, a seed with a recorded setting outside that list is refused through
    `refuse_unread_settings` (`:68`). The message names the seed, the reader and the field.
  - `refuse_experiment_settings` is deleted, together with its consumers.
  - Mechanism: the new test module, plus a Hypothesis property over the closed config space (every field, every
    value, every valid format). The extractor refuses exactly when that function refuses, names the same field, and
    never advances first.
  - Planted:
    - a `self_report` true config, a `crew_idle_policy` patrol config and a format-2 config are each refused by
      name;
    - a tick row whose `experiment_config` carries a key the model does not know is refused at parse, naming it;
    - with `READABLE_SETTINGS` narrowed by `kill_cooldown_ticks`, the extractor refuses the cooldown game with
      `kill_cooldown_ticks=6` in the message (it joins `INSTRUMENTS`, `tests/eval/test_kill_cooldown_readers.py:579`);
    - with `READABLE_SETTINGS` widened by a planted field, the reason-table test fails, naming the field.
- [ ] **The re-simulation runs the recorded engine and reset.**
  - The seeding, every advance and every applied meeting take their values from the engine-arguments helper.
    Every applied meeting also takes the recorded `meeting_reset` and redistribution rule.
  - On `replays/samples/9p2i` the extraction completes with every self-check OK and no invariant failure. With the
    refusal bypassed and nothing threaded, the run records 1,885 failures (probe 1).
  - Mechanism:
    - the extractor joins `_RESIMULATION_MODULES` (`tests/orchestrator/test_experiment_arms.py:428`), whose `ast`
      scan fails any engine call made without the helper's arguments;
    - the cooldown gate and its site table (`test_kill_cooldown_readers.py:375`, `:492-516`) gain the extractor's
      three calls, as `extractor: seeding`, `advance` and `meeting`.
  - Planted: `_forgotten_at` at each of the three sites makes the gate name that site. The scan's own planted
    sources stay.
- [ ] **The chain re-walk reads the recorded rebuttal.**
  - With `bounded_rebuttal_version` 1, the re-walk accepts one trailing reply when, and only when, it equals the
    selector's pick. It reads that through the one home, `walk_chain` or `select_bounded_rebuttal`, never a replica.
    Every other chain finding keeps its meaning.
  - Mechanism: a count test on the shown set. `OPTIN` and `TERM` read 0; the rejections stay at 44 and 99.
  - Planted:
    - the scripted rebuttal recording (`tests/_helpers/scripted_meeting.py`, `ACCUSE_THE_OPENER`) yields no chain
      finding;
    - read with the version as `None`, it yields one;
    - with the rebuttal's speaker swapped, or a second trailing reply appended, it still yields one.
- [ ] **The contradiction re-derivation sees the regroup.**
  - Each meeting's re-derivation receives the ticks `orchestrator.replay.derive_regroup_ticks`
    (`orchestrator/replay.py:1498`) derives from the meetings that resumed play: the set the live manager passes.
  - On the shown set no re-derived flag changes (67 meetings carry ticks; 78 flags). Results states this as a no-op
    on these bytes.
  - Planted: a constructed meeting whose alibi falls inside a regroup window mints the flag without the ticks, and
    does not mint it with them.
- [ ] **Prompt-derived facts classify on the era.**
  - On the shown set every meeting call classifies to a named slot (120, 420, 271 and 691; none unclassified), and
    every vote call parses at least one suspicion row (3,101).
  - Mechanism: a count test on the committed set.
  - Planted (source change): with the era's header removed from `_SUSPICION_GRAPH_HEADERS` (`:299-302`), the vote
    count falls to 0 and the test fails; an era vote prompt whose first header is rewritten lands in the
    unclassified slot.
  - The route-lines row: on a scripted route-lines recording (the field on, `record_game` with the fake provider),
    every ballot prompt that carries the routes block classifies to the vote slot and parses its suspicion rows.
    Planted: that recording read with the route-lines row dropped from the read list is refused by name (the first
    item); a copy of one of its ballot prompts with the vote slot's header rewritten lands in the unclassified slot
    and fails the test.
- [ ] **Each arm changes only what it affects.**
  - For each readable setting, a fake recording of one seed with that setting alone off its default extracts with
    every self-check OK.
  - For the cooldown, the reset and the rebuttal, the same seed recorded without the setting yields facts that
    differ in the fields the arm table names: kill and meeting ticks, post-meeting positions, chain turns.
  - For each setting the table marks "nothing", the reason table states why, and dropping the setting from the read
    list makes that recording refused by name.
  - Mechanism: the new test module, on fixed seeds with the fake provider (`record_game`,
    `tests/_helpers/scripted_meeting.py`).
  - Planted: dropping the reset from the meeting call turns the post-meeting self-check red on the reset recording;
    dropping the cooldown at any one site turns the tick-hash self-check red.
- [ ] **The era's facts stay a temp file, and version 1 is never served for `stage-b-r2`.**
  - The extractor gains `--sample-dir` (default `replays/samples/9p2i`, hardcoded today at `:180-181`). Its facts go
    to `${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json` (`:4648-4652`) and nowhere under the set. The embedded
    R1-R7 rows (`:4626`, from `rubric_score.score`, imported at `:164`) stay a temp-file lab reading.
  - No path writes a version-1 served file for the era. The profile card deletes `regen_for_set` and `--set-dir` and
    holds the deletion with its own test (its item 17: `rubric_score.main` with `--set-dir` on a `tmp_path` copy of
    the era exits non-zero and writes no `results-rubric-score.json`). This card keeps that test green and never
    edits it.
  - Mechanism: the profile card's deletion test, and an extraction in `tmp_path` after which the set's file listing
    is unchanged. Planted: an extraction whose facts path is redirected into the copied set directory changes the
    listing and fails the listing test.
- [ ] **The era's one lab output is the geomean witness, and history is never rewritten.**
  - `rubric_score.main` resolves the facts' `sample_dir` through the era registry (`eval.eras.committed_set`,
    `eval/eras.py:106-123`). For `replays/samples/9p2i` it writes `experiments/lab/results-rubric-geomean.<era id>.json`,
    stamped with the set's MANIFEST key, whatever the era. Today that is `results-rubric-geomean.stage-b-r2.json` at
    `43b5ee45`, committed.
  - The witness is itself the era's per-game version-1 geomean reading: each game's score, floor multiplier and r1,
    r2, r3 and r7 sub-scores, in the shape of `results-rubric-geomean.json`. It is lab only and never served, the
    labelled-history option of the design memo's Part 3. Beside it this card writes no other version-1 file for any
    era: no code path writes `experiments/lab/results-rubric-score.json` or `results-rubric-geomean.json` again, both
    stay byte-identical to `d41c9006` (`git_head` `27646d67`), and no interestingness file of the era (the served
    file's shape) is committed. Any other directory (a baseline-9 set, a candidate round, a scratch export) gets no lab
    file and one line naming it.
  - Mechanism:
    - a currency test re-runs the extraction on the committed set into `tmp_path`, and asserts that the committed
      witness equals `geomean_validation(facts)` with the set's own stamp;
    - a Hypothesis property of the naming over generated registries: the name always carries the set's era id and
      is never the unkeyed name.
  - Planted: a registry that names the set under another era id changes the name; a naming that returns the
    unkeyed name fails; a `tmp_path` witness with one cell changed fails currency; a MANIFEST copy with another key
    fails the stamp.
- [ ] **The parity pin is keyed by era.** The historical pin in `test_watchability.py` becomes a table keyed by
  era id.
  - `stage-b-r2`: the committed witness equals `compute_game_score(..., historical_15_2=True)` over
    `replays/samples/9p2i` for every game and every `_PARITY_KEYS` key, to 1e-6 (50 of 50 at `76270d6c`). It is
    re-derived on every run.
  - `baseline-9`: what D14 decides at dispatch. Either it is held to itself and to `27646d67` as today (`:130-168`,
    assertions unchanged), or it retires with one history line. It is never re-derived.
  - The docstring's "does not read the promoted era" goes; the bytes-gone reason stays.
  - Planted: one cell changed in a `tmp_path` copy fails the pin, and so does a copy stamped with another key.
- [ ] **The W0 -> W1 -> W2 rows retire (the G27 extractor half).**
  - `_cross_era_trajectory`, its call, the facts' `cross_era_trajectory` key and the self-check's "W2 fixture
    match" clause are deleted. The module docstring keeps one history line. The extractor reads no file under
    `tests/fixtures/phase10/`.
  - The three fixtures, their anchor tests, `WAVE2_GATE_SPEC` and `--baseline-out` are untouched: their retirement
    is D14's own card (the baselines memo, Part 3.1, the G27 row).
  - Mechanism: an `ast` scan in the new module finds no string constant in the extractor naming `phase10` or
    `corrected_w`, and the era's facts carry no `cross_era_trajectory` key at any depth.
  - Planted: a `tmp_path` copy of the source with the fixture read restored fails the scan, naming the line; facts
    with the key planted fail the key check.
- [ ] **Baseline 9 reproduces from its own bytes.** The input is a `git archive` export of `d41c9006`'s
  `replays/samples/9p2i`.
  - The widened extractor, given that directory as `--sample-dir`, exits 0. `interestingness(facts)` and the set's
    three stamps equal the retired served file's four keys, and the JSON rebuilt from them is byte-identical to it.
    `geomean_validation(facts)` equals the frozen fixture's body.
  - The export carries the retired file at the path the scorer used to write. It is deleted right after the export,
    and the run checks that it is gone.
  - Mechanism: the Validation commands, quoted in Results with their exit codes; the bytes are not in the tree, so
    no test can read them. Planted: against a copy of the retired file with one per-game score changed the
    comparison reports the difference, and with the facts file deleted it fails; Results quotes both red runs.
- [ ] **No sentence says the extractor refuses the era.** At the head the Validation scan (a `git grep` for the
  phrases it names, over tracked files outside `audits/`, `tasks/`, `agent_prompts/` and `design/`, plus the
  extractor) finds nothing. Every sentence it found on this card's base is fixed in the same pull request and named
  in Results; on a profile-card surface only a surviving comment or copy line is touched. Planted: the scan on
  `76270d6c` lists 17 lines in 10 files plus 1 in the extractor, the sites Evidence names; Results quotes it.
- [ ] **The registry rows follow the bytes.** In `docs/artifacts.md`, two rows are recomputed as the last step,
  after the final merge of `main`, with no figure carried from authoring: the `experiments/lab/`,
  `experiments/model_probe/` row (167 files at `76270d6c`, `:118`; this card adds one, so it states one more than it
  reads at that merge) and the `audits/` row (`:113`, exact tracked bytes; the extractor's bytes move, its file
  count stays). Mechanism: `test_every_counted_registry_row_matches_the_index`
  (`tests/scripts/test_verify_ml_evidence.py:2166`) and the offline `scripts/verify_ml_evidence.py`, never with
  `--complete`. Planted: with a row left stale the test fails; Results quotes the red run.
- [ ] **The wave lessons hold.**
  - The neuter pass: every production line this card adds or changes is neutered alone, and its suite goes red.
    Results lists the probes.
  - One bounded mutation pass, over the changed spans, with exactly the eight listed classes: F drop a filter,
    S swap a collection, N None test, K read to constant, M message argument, T drop a tuple member, B swap
    branches, L loaded source to literal. Every survivor is killed or named equivalent.
  - No test is weakened. Results names each re-targeted test's old assertion and the strength it keeps.

## Constraints

**Status and dispatch.** The validator accepts three statuses, `ready`, `active` and `done`
(`scripts/validate_task_docs.py:45`, `_CARD_STATUSES`). Until 2026-10-09 this card was `ready`, meaning the contract
was complete, not that dispatch was authorized: it was to dispatch only on the owner's word under D14 (Part 4, D14,
the G27 item, of the baselines memo,
`/Users/danielkeinan/.claude/projects/-Users-danielkeinan-projects-AiLibi/baselines-2026-10-03/baselines-memo.md`),
and otherwise to close as superseded with one history line, D14's G27 card deleting `_cross_era_trajectory` itself.
The word was "retire the memo's D14 list" (decision memo 8.9), so it closed that way on 2026-10-09: `done`, with a
title and Results that say it closed unexecuted, the form the house used for `held-out-prefix-freeze-6` (`034cad1d`).

**Order.**
- It dispatches from a `main` that holds the merge of `rubric-v2-profile`. That card deletes `regen_for_set` and
  `--set-dir` (and holds the deletion with its own test), rewires the refresh step, and owns every served surface.
  This card writes none of those, and it branches from `main` only after that merge, so the order on
  `experiments/lab/rubric_score.py`, `report-rubric-interestingness.md` and `scripts/refresh_samples.sh` is fixed:
  the profile card first, then this card.
- The round-3 record also governs timing. `stage-b-record-r3` keeps the rubric cards undispatched until it merges
  ("Wave, order and ownership"), and its F-based gates cover `experiments/`, `scripts/`, `api/` and the `audits/`
  row of `docs/artifacts.md` it re-derives, all of which this card may write. So it never merges between that
  record's F and its merge; under the current record card it dispatches after the record merges, from a `main` that
  holds `rubric-v2-profile`, and only on the owner's D14 word.
- It does not depend on the census carrier; the kill and body victims and the end reason and final task count are
  the profile card's dependency on the cells card.

**Shared files, one writer at a time.**
- `experiments/lab/rubric_score.py`: the profile card first (its deletions; `_set_manifest_sha` stays, `:1309`),
  then this card (the witness naming in `main`). The scoring functions are untouched.
- `experiments/lab/report-rubric-interestingness.md`: the profile card first (the `--set-dir` half of the run line),
  then this card (the output name).
- These are the profile card's files: `scripts/refresh_samples.sh`, `api/routes/eval.py`,
  `frontend/src/components/ReplayPicker.tsx`, `frontend/e2e/evidence-journey.ts`, `tests/api/test_sets.py`,
  `tests/scripts/test_build_demo_bundle.py` and `tests/scripts/test_refresh_samples.py`. After that merge, this card
  edits a comment or copy line there only where the scan finds a surviving sentence, and names it in Results.
- `tests/orchestrator/test_experiment_arms.py` and `tests/eval/test_recorded_arm_readers.py`: `route-lines-field`
  first, then this card. `eval/recorded_settings.py` is that card's; this card only reads `READABLE_SETTINGS`.
- This card's alone: the extractor, its three `tests/experiments/` modules in Expected scope,
  `tests/eval/test_kill_cooldown_readers.py` and `tests/eval/test_watchability.py`. If D14's own card retires the
  baseline-9 pin, it lands before or after this one, never alongside.
- `docs/artifacts.md`: this card's two rows, last, in the merge order (`route-lines-field` and the census card also
  write the lab row, the idle-policy and record cards the `audits/` row). `tasks/README.md` and this card's Status
  line are the orchestrator's.
- Never written here: `eval/gameplay_census.py`, `scripts/publish_gameplay_census.py` and `docs/gameplay-census.*`
  (the census card's); `tests/fixtures/phase10/`, `tests/eval/test_gate_spec_metrics.py` and
  `eval/meeting_quality.py` (D14's); `audits/workflows/*.workflow.js` (dated prompt text).

**Out of scope.**
- Version 1's R-items, weights, floors and scoring functions. No history is re-scored, and version 1's lab results
  stay as history. The served rubric and every viewer surface are the profile card's.
- Any recorded byte: nothing under `replays/` moves, `replays/candidates/stage-b-r1/` included; the ladder tip
  stays at baseline 9. Engine, agent, meeting, orchestrator, LLM and training code; any DTO, schema, loader mapping
  or generated type.
- No new `AILIBI_*` lever, environment switch or experiment field, and no prompt registry or prompt version bump.
  The ML corpus's FROZEN line and every ML artifact stay put, and ML stays on hold (ruling 12).
- No live provider call, recorder run or held-out generator; the untracked `.env` is never read. Censuses are
  count-only, keyed by (set, meeting); no rendered prompt, transcript text or seed-band prefix is printed.

**House rules carried.** The engine stays a pure, deterministic tick, and nothing here touches it; replays stay
byte-identical in their recorded scope, and `agents/` never imports `engine/`. The extractor reads roles as engine
truth, offline and after the fact, and nothing agent-side may import it: `tests/test_firewall.py:381` bans `audits`
and `experiments` from `agents`, `llm`, `meetings` and `observation`, with one planted leg per banned name
(`:507-519`). Role-correctness stays a reported lab reading, never a gate. No module-level mutable state: the read
list and the reason table are immutable constants. Invalid input raises, with no silent fallback. Each new gate
carries a planted case that fails on its claimed defect. Every claim names its enforcing mechanism, and every number
is measured at the head that states it, with its command in Results. Guarantees are stated at the strength
delivered, and a live-tense sentence about old behaviour is fixed in the same pull request. Universal guarantees are
Hypothesis properties; any property that loads the map carries `settings(deadline=None)`. Every sourced constant has
a planted source-change case: the read list from `READABLE_SETTINGS`, the lab key from `eval/eras.py`, the stamp
from the MANIFEST, the slot literals from the era's templates. One writer per file.

**Publication.** Nothing ships. The bundle bakes no extractor output and no lab file, so `pages.yml` republishes an
identical demo. The pull request quotes the empty `diff -rq` between the base and head bundles. The served rubric
is the profile card's.

**Delivery.** The branch is `work/rubric-extractor-era`, delivered as one pull request into `main` and merged by
merge commit or fast-forward, never squash. Each commit body ends with `Card: tasks/work/rubric-extractor-era.md`,
immediately followed by the line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>`.

## Expected scope

- `audits/workflows/extract_gameplay_facts.py`: the read list and its reason table, the refusal, the threading, the
  reset, the rebuttal acceptance, the regroup ticks, `--sample-dir`, the W-row deletion and the docstring.
- `experiments/lab/rubric_score.py`: the witness naming in `main`, after the profile card's deletions. Its scoring is
  untouched.
- New committed output: `experiments/lab/results-rubric-geomean.stage-b-r2.json`.
- `experiments/lab/report-rubric-interestingness.md`: the run line only.
- Tests: the new `tests/experiments/test_gameplay_facts_era.py`;
  `tests/experiments/test_gameplay_facts_refuses_experiments.py` (rewritten in place for the read-list rule);
  `tests/experiments/test_gameplay_facts_genuine_class.py`; `tests/eval/test_recorded_arm_readers.py`;
  `tests/eval/test_kill_cooldown_readers.py`; `tests/eval/test_watchability.py`;
  `tests/orchestrator/test_experiment_arms.py`.
- `docs/artifacts.md`: two rows.
- Only where the scan finds a surviving sentence, comment or copy text only: `scripts/refresh_samples.sh`,
  `api/routes/eval.py`, `frontend/src/components/ReplayPicker.tsx`, `frontend/e2e/evidence-journey.ts`,
  `tests/api/test_sets.py`, `tests/scripts/test_build_demo_bundle.py`, `tests/scripts/test_refresh_samples.py`.
- This card's Results.

Directly necessary follow-through inside these files is permitted. Any other file belongs to another card or needs
the owner.

## Record impact

- **What is added.** No recorded byte is edited. One era-keyed lab file is added,
  `experiments/lab/results-rubric-geomean.stage-b-r2.json`: the era's per-game version-1 geomean reading, lab only
  and never served. The facts JSON stays a temp file. Nothing is added under `replays/`.
- **What is unchanged.** `bash scripts/verify_samples.sh` and the four `build_sample_report.py --check` runs
  recompute exactly what they did before. The census and scorecard pages do not move.
- **History.** The baseline-9 served rubric stays at `d41c9006`. The two unkeyed lab files stay byte-identical, and
  the frozen pin stays as D14 decides. The baseline-9 reproduction runs in scratch and writes nothing into the tree.
- **Behaviour.** The extractor, an offline audit tool, reads the era and no longer reads the Phase-10 fixtures. No
  agent, engine, meeting or tactical path changes, and no game plays out differently. No scorecard, census,
  evaluation or ML artifact moves.
- **What ships.** Nothing: the bundle diff is empty.
- **The next re-record.** When `replays/samples/9p2i` is next re-recorded or promoted, the witness is regenerated in
  the same change; its currency test goes red until it is.

## Validation

```
# development
uv run pytest tests/experiments/ tests/eval/test_watchability.py tests/eval/test_kill_cooldown_readers.py \
  tests/eval/test_recorded_arm_readers.py tests/orchestrator/test_experiment_arms.py tests/test_firewall.py -q
# the era, from the repository root ($0, no provider), run twice; the second leaves no diff
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py --sample-dir replays/samples/9p2i >/dev/null
uv run python experiments/lab/rubric_score.py "${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json"
git status --porcelain     # the stage-b-r2 witness only; nothing under replays/
git diff --exit-code d41c9006 -- experiments/lab/results-rubric-score.json experiments/lab/results-rubric-geomean.json
# baseline 9 from its own bytes, in scratch only
git archive -o <scratch>/b9.tar d41c9006 replays/samples/9p2i && tar -xf <scratch>/b9.tar -C <scratch>
rm <scratch>/replays/samples/9p2i/results-rubric-score.json
test ! -e <scratch>/replays/samples/9p2i/results-rubric-score.json
PYTHONPATH=. uv run python audits/workflows/extract_gameplay_facts.py \
  --sample-dir <scratch>/replays/samples/9p2i >/dev/null                        # exit 0
git show d41c9006:replays/samples/9p2i/results-rubric-score.json > <scratch>/retired.json
uv run python -c "import json, pathlib as p; from experiments.lab import rubric_score as r; \
from orchestrator.recording_fingerprint import recording_fingerprint as fp; d = p.Path('<scratch>/replays/samples/9p2i'); \
f = json.loads(p.Path('${TMPDIR:-/tmp}/ailibi-gameplay-facts-9p2i.json').read_text()); \
new = json.dumps({'seedset': f['seedset'], 'git_head': r._set_manifest_sha(d), 'source_fingerprint': fp(d), \
'interestingness': r.interestingness(f)}, indent=2); g = json.loads(p.Path('experiments/lab/results-rubric-geomean.json').read_text()); \
print(new == p.Path('<scratch>/retired.json').read_text(), all(g[k] == v for k, v in r.geomean_validation(f).items()))"
# True True; planted: with one per-game score changed in <scratch>/retired.json it prints False True
# the sentence scan: empty at the head; on 76270d6c it lists 17 lines in 10 files, plus 1 in the extractor
git grep -n -i -e "extractor does not read" -e "extractor refuses" -e "extractor reads only" \
  -e "read the promoted era" -e "refuses the shown" -e "fixture does not read" \
  -- . ':!audits' ':!tasks' ':!agent_prompts' ':!design'
git grep -n -i -e "extractor reads only" -e "extractor refuses" -- audits/workflows/extract_gameplay_facts.py
# nothing recorded moves; the gates
bash scripts/verify_samples.sh
uv run python scripts/build_sample_report.py --sample-dir <set> --check   # samples and ml_corpus, 9p2i and 4p1i
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run python scripts/verify_ml_evidence.py        # offline; never --complete
uv run python scripts/build_demo_bundle.py --out <scratch>/before|after && diff -rq <scratch>/before <scratch>/after
bash scripts/check.sh                              # whole, in a clean worktree, real exit code quoted
```

Run `check.sh` to the end rather than stopping at the first failure, because `set -e` masks later gates.

## Results

### Closed unexecuted, 2026-10-09

**The ruling.** On 2026-10-09 the owner ruled, verbatim: "Merge both when verified and retire the memo's D14 list"
(`tasks/decision-2026-09-24-stage-b-wave.md:1601-1622`, section 8.9, at `335cbdc9`). Section 8.9 reads the list as
the baselines memo's Part 4 D14, with D14-T1 to T3, and the RETIRE rows of its Part 3.1, and lands the retirement as
one card whose merge waits for round 3's freeze to lift; its amendment of the same day, verbatim "Keep the
comparison records", takes only the round-1 item off the list. This card's Constraints left its dispatch to the
owner's word under D14 and named the other branch: close as superseded, with D14's G27 card deleting
`_cross_era_trajectory` itself. The word retires and does not widen, so the card closes on that branch, and nothing
in it ran. The closure lands before the retirement card merges, so this card is closed while that card deletes the
rows.

**What supersedes each of its three reasons.**
- The W fixtures. The baselines memo's row "RETIRE, after D6 and D14" (G27, Part 3.1) deletes the three
  `corrected_w*_baseline.json` files with their anchor tests, `WAVE2_GATE_SPEC` and `--baseline-out`, and first
  replaces the extractor's W0 -> W1 -> W2 rows with their one-line history. The profile card, the D6 card, left
  them, so at `225d2b77` they stand at `audits/workflows/extract_gameplay_facts.py:673`, `:698-703`, `:3520`,
  `:3827` and `:4548`. They are the D14 retirement card's: the extractor's reading of the fixtures retires with
  the fixtures.
- The facts path. Since the profile card (PR #504) rewired the refresh script's rubric step to its own publisher,
  the refresh script runs no extractor: `git grep -c extract_gameplay_facts -- scripts/refresh_samples.sh` prints
  nothing at `225d2b77`. The dated audit workflows still start from the extractor (Limitations).
- The referee's historical mode. The era-keyed parity row was option (a) in Evidence; this closure is option (b),
  which never builds it. The baseline-9 pin (`tests/eval/test_watchability.py:131`, held to itself) stays as it is
  unless the D14 retirement card's list retires it; this closure does not decide that.

**What did not move.** No line of the extractor, the lab scorer, its report, a test, `docs/artifacts.md` or any
recording moved, and no lab file was written. The sentences this card would have fixed stay true, because the
extractor still refuses the era: the refusal's own tests and the pin's docstring ("does not read the promoted era",
`tests/eval/test_watchability.py:139-140`). The profile card's open point 4 (`tasks/work/rubric-v2-profile.md:492`)
left this card's fate to the owner's D14 word; section 8.9 and its dated closure line answer it, and that done card
is not edited.

**Delivery states.** Implemented, verified and independently reviewed: not applicable, as no implementation exists.
Merged: the closure is a `docs:` commit on `main`, the AGENTS.md route for contract documents, checked by the
documentation lens alone (decision memo 8.7, item 4). Adopted: not applicable.

**Verification.** At the closing commit, which precedes the D14 retirement card's merge, each command below gives
the output beside it. These are readings at that commit, not standing claims: once the retirement merges,
`_cross_era_trajectory` and the three `tests/fixtures/phase10/corrected_w*_baseline.json` files are gone, the grep
prints `audits/workflows/extract_gameplay_facts.py:1`, `git ls-files tests/fixtures/phase10` no longer lists the three
files, and that card's Results name every path it deleted.

```sh
uv run python scripts/validate_task_docs.py      # passes; tasks/README.md carries the derived inventory sentence
uv run python scripts/check_doc_facts.py         # passes
git grep -c -E 'def (refuse_experiment_settings|_cross_era_trajectory)\(' -- audits/workflows/extract_gameplay_facts.py
                                                 # audits/workflows/extract_gameplay_facts.py:2
git ls-files -- experiments/lab/results-rubric-geomean.stage-b-r2.json   # prints nothing
```

Planted, the validator fails on this card with one former item restored unchecked, and again with this section
emptied, printing the two messages Acceptance quotes.

**Limitations.** The audit workflows that start from the extractor
(`audits/workflows/gameplay-data-audit-v2.workflow.js:603`) still cannot point it at the shown era; an audit of the
era starts from the census carrier (`eval/gameplay_census.py`), which reads it, or from a new card. If the D14
retirement card deleted the fixtures without the extractor's rows, the rows would read each missing file as
`{"present": False}` (`:702-703`), the silent degradation Evidence names, so the extractor half of the G27 row has
to land with the fixtures, in the same card.
