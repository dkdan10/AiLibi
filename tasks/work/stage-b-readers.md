# Instruments and reconstructors read the recorded arms, including the one-reply follow-through (B3)

**Status:** ready

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

- [ ] **Five profiles widened, each after a written review.** Kill-craft, the funnel, solvability,
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
- [ ] **R7 is a required keyword at every reader call site this card owns.** Each `advance_tick`,
  `apply_meeting_result` and `_build_meeting_trigger` call in the golden, `tests/_helpers/committed.py`
  and `tests/_helpers/scripted_meeting.py` passes the spine helper's engine arguments, the recorded
  `meeting_reset` and the recorded config explicitly. The vent witness rule then reaches each site
  as soon as B0 adds it to the helper, with no edit here and no engine default relied on (B0 keeps a
  default on `advance_tick`). Enforced by an AST test over those files. Proof: a planted module with
  a bare `advance_tick(state, actions, game_map=...)` call fails it.
- [ ] **A planted event-level thread-or-refuse test for each reader.** The test monkeypatches the
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
- [ ] **Evidence honesty rebuilds decisions with the recorded policy.** By default each game's
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
- [ ] **The golden reads any directory with its recorded config.** A public directory walk replaces
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
- [ ] **Arm stamps resolve only on recordings that carry the arm.** `resolve_prompt_set` extends
  `_overlay_stamp_owners` to experiment-bound arms through
  `prompt_versions_for_set(name, experiment_config=recorded)`, over the spine's experiment-arm
  registry, which stays empty until B6. The window test accepts a stamp other than the live default
  only when it equals the arm stamp for that recording's own config. Proof: with a planted registry
  entry, a recording carrying the arm resolves, and the same stamp on a recording without the arm
  fails the window test. With the registry empty, every committed stamp resolves to the live
  default mapping.
- [ ] **`walk_chain` accepts the selected rebuttal and nothing else.** It gains a keyword-only
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
- [ ] **The scripted rebuttal game.** A new `tests/_helpers/scripted_meeting.py` records a
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
- [ ] **The scorecard's `--set-dir DIR --json-stdout`.** `scripts/publish_process_scorecard.py`
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
- [ ] **The rubric extractor refuses experiment recordings by name.** Before any re-simulation, a
  seed whose recording carries an experiment config raises `SystemExit`. The message names the seed
  and its recorded settings in plain words, and says the extractor reads only recordings made
  without them. Its acceptance of the rebuttal waits for adoption. Proof: the scripted rebuttal
  recording is refused with that message, not by a later extraction invariant, and an unstamped
  fake recording still extracts.
- [ ] **The frozen and policy-re-running instruments keep refusing.** Off-menu, the anchor study,
  the surrogate meeting table, the conviction table and the watchability referee each raise their
  named refusal on an arms-ON fake recording before the first advance. None of their code changes.
  Proof: each case matches the refusal text, so a refusal that is removed and replaced by a later
  hash or reconstruction error fails it.
- [ ] **The OFF path is byte-identical, and the bundle is unchanged.** No byte under `replays/`, and
  no derived report, fixture, prompt template, doc fact or ML artifact, moves. Enforced by the gates
  in Validation. Each gate is a byte comparison with its own planted failure: the golden's one-byte
  template perturbation (`:1690`), `build_sample_report --check`'s drift case and the scorecard
  `--check`'s. `api/replay_loader.py` imports `meetings/transcript.py`, so the demo bundle is built at
  the merge base and at the head, and `diff -r` between them is empty.
- [ ] **The copy this card adds is plain.** Mechanism: a test scans every new refusal message and
  the `--set-dir` help text for task or audit identifiers (`Task \d`, `audit-`, and memo-style
  short ids such as `R7` or `B3`) and bare threshold arithmetic. Planted: a message containing
  "Task 20.33" fails the scan, and so does one containing "R7".
- [ ] **The registry row follows the audit bytes.** This card edits
  `audits/workflows/extract_gameplay_facts.py`, so the `audits/` row of `docs/artifacts.md` (`:109`,
  26,635,440 tracked bytes / 329 files at `e886b663`) is recomputed with `git ls-files` as the last
  step, after the final merge of `main`. Mechanism: `test_every_counted_registry_row_matches_the_index`
  (`tests/scripts/test_verify_ml_evidence.py`, run by `check.sh`) and the offline
  `scripts/verify_ml_evidence.py`. Perturbed: with the row left stale after the extractor edit, that
  test fails; Results quotes the red run.
- [ ] **The deviation goes to the owner.** The PR's Decisions state v1's beneficiaries with the
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
  the `Co-Authored-By:` attribution line the worker's own session supplies (never a model name copied from this card).
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

Not started. When done, it records: the `docs/architecture.md` sections relied on ("Determinism and
the substrate ladder", "Enforced boundaries", "Explicit cleanup experiments" with the spine's
arm page, `docs/experiment-arms.md`); the per-instrument review, one paragraph per instrument and reusing module, naming
each wave field threaded or refused and why; each planted case and its perturbation, by test id;
every Validation command with its real exit code and the merge-base comparisons; the re-measured B3
counts with their count-only command; decisions, including each refusal pending a later card; and
limitations.
