# B4: close the kill-tick leak with the public body handle

**Status:** active

## Outcome

With a new recorded experiment field, `report_body_handle_version`, set to 1, a
body-report meeting opens with the victim's public handle (`body-p-3`) instead of
the engine's body id (`body-p-3-4`). The engine id carries the kill tick, and
today it reaches the opener's report prompt in every report meeting. Under the
field no handle carrying the kill tick reaches any model-facing text. The
builder changes nothing else: the trigger tick, the emergency text, the prompt
stamps and tactical play stay as they are. What the opener then says, and so
the meeting, may differ with a real model; that is the intended effect.

The field is default `None`. At the default the builder keeps today's legacy
branch, so every committed recording, derived view, fixture, gate and doc fact
keeps verifying byte-identically. The field is recorded ON only when
[the round-1 record](stage-b-record-r1.md) writes the Stage-B candidate into
`replays/candidates/stage-b-r1/9p2i/`.

This is the minimal change. It is not the `temporal_observations` lever, which
changes more than the handle and meets the bare-shell provenance wall that kept
Phase-21's lever-ON evidence out of the sample sets (Evidence). At retirement
the field's key stays as a read-only recorded field, because the config model
forbids unknown keys and the candidate carries it.

## Evidence

Every `path:line` below is at `e886b663`. A3 (`docs-truth-typed-trigger`) and
the spine (`stage-b-arm-spine`) move `orchestrator/game.py` lines before this
card starts, so re-anchor each citation by the named symbol at dispatch. Counts
come from the Stage-B investigation memos of 2026-09-24: the decision memo
section 0.4, `rebuttal_and_body_handle.md` section 4 and `census_and_record.md`
section 1. They are count-only. Re-measure them at dispatch, from the published
gameplay census once [A1](gameplay-census.md) has merged.

**The leak.**

- The engine mints `body-{victim}-{tick}` at the kill (`engine/rules.py:87`).
  `BodyState` has no kill-tick field (`engine/entities.py:43-49`), so the id is
  the tick's only carrier.
- `_build_meeting_trigger` (`orchestrator/game.py:3399`) renders the report
  description. It passes the raw engine id when `temporal_observations` is OFF
  and `public_body_id(victim)` when it is ON (`:3459-3470`;
  `observation/body_ids.py:6-11`).
- The description reaches only the opener's report prompt
  (`agents/strategic/prompts/qwen3_6_27b/crewmate_report.j2:96`,
  `impostor_report.j2:85`).
- Packets already use the public handle unconditionally
  (`observation/service.py:425-433`).
- The limitation is documented at `docs/architecture.md:131-133` and
  `docs/observation-contract.md:35-38`.

**Reach**, over the 623 report meetings of the four committed sets:

| channel | s9 | c9 | s4 | c4 | pooled |
|---|---|---|---|---|---|
| report meetings whose opening carries `body-p-N-T` | 135/135 | 416/416 | 36/36 | 36/36 | 623/623 |
| recorded calls carrying it (retries included) | 138 | 422 | 36 | 36 | 632 |

The other channels are clean. Non-opener prompts carrying the id: 0. The
opener's later prompts: 0. Spoken turns: 0. Opening `found_body` observations
dated at the kill tick: 0. Opening free text names the kill tick in 38 openings,
against neighbour-tick controls of 17 (tick k-1) and 25 (tick k+1). Whether
those 38 come from the leak is not established, because settling it needs
reading speech, which the investigation excluded.

On s9 the corpse age at report (report tick minus kill tick) has median 4, 46 of
135 at 5 ticks or more, and max 29 (pooled: median 4, 216 of 623, max 32). The
section-4 assessment cell reads 135/135 (138 calls) before and must read 0
after (decision memo, section 4).

**What this card does not fix.** It removes the reporter's privileged anchor,
which only the killer, fellow impostors and kill witnesses otherwise hold. It
does not repair the 11 innocent ejections the investigator attributes to
listeners assuming the kill time from the report time; those listeners never
had the tick. No public death bound renders in this wave: that needs an
evidence-reasoning version, and none is set
(`agents/memory/evidence_context.py:250-251`). The honest cost: it may also
remove a correct time that a reporter passed on.

**Why a narrow field, not the temporal lever** (investigator options a and b).

- `AILIBI_TEMPORAL_OBSERVATIONS=2` closes the leak but changes tactical
  trajectories: on paired fake seeds 0-7, seed 0 diverged from tick 14 and
  seed 6 from tick 22.
- It delivers same-tick vents and kills to the meeting, the channel B1, R7 and
  R8 measure. And `=1` selects v1, which `--expect-levers` cannot tell from v2.
- The validity gate compares every game's substrate stamp with the bare-shell
  snapshot (`eval/validity.py:960-993`), so a temporal-ON set fails the gate
  B5 runs in a bare shell. That is the Phase-21 wall
  (`audits/audit-phase-21-adopting-record.md:1050-1058`).
- The golden refuses temporal recordings outright
  (`tests/meetings/test_prompt_byte_golden.py:656`).
- Nothing narrower than a field exists. An unconditional change breaks the
  golden, which rebuilds the trigger with defaults (`:781`). Changing the
  engine id moves every state hash. Coupling the handle to another arm would be
  a dishonest gate.

**A correction to the investigator's narrowness count.** The memo says 0 of 44
other prompts differ on seed 12. That holds only after normalization. The fake
provider seeds every string field from a hash of its prompt
(`llm/fake_provider.py:133`, `:188-199`), so the opener's reply text changes
with the handle, and every later prompt of that meeting quotes the reply.

A count-only probe re-ran this at `e886b663` on 2026-09-24. It swaps the handle
through a monkeypatched builder and never prints a prompt
(`.../scratchpad/b4card/probe.py`, outside the tree):

| game | prompts | report openings | state hashes | non-opening prompts differing | after normalizing |
|---|---|---|---|---|---|
| seed 1, 7p1i, 80 ticks | 22 | 2 | equal | 20 of 20 | 0 |
| seed 12, 9p2i, 200 ticks | 44 | 4 | equal | 40 of 40 | 0 |

The normalization replaces the fake's `fake-<field>-<8 hex>` tokens. Each ON
opening equals its OFF opening with the one handle substituted. With the swap,
no prompt carries a legacy handle; without it, every opening does. The same
caveat applies to the investigator's "44 of 44" for the temporal option. That
option's rejection rests on the trajectory divergence and the bare-shell wall,
not on that count.

**Pins that hold the OFF bytes today.** OFF reads `reported body body-p-3-4 at
tick 8` (`tests/orchestrator/test_temporal_delivery.py:372-417`). The
prompt-byte golden passed 25 at `e886b663`, re-run while this card was written.
`tests/experiments/test_held_out_prefixes.py:705-720` calls the builder with
temporal True and False. The held-out generator lists `orchestrator/game.py` in
`GENERATOR_SOURCES` (`experiments/held_out_prefixes.py:173-195`), but the band
is archived and checked against its own frozen bytes
(`tests/experiments/test_held_out_prefixes.py:824-870`), so this edit owes it
no restamp.

**The default-path ruling this card leaves standing.**
`docs/cleanup-dispositions.md:264` retains the death-tick handle on the default
path by the owner's ruling with #437 on 2026-09-07. The field keeps that path,
so the row stays true until an adopting decision revisits it.

**Rulings relied on.** The owner, 2026-09-24, verbatim:

- "We should implement stage B"
- "B4. close the tick kill leak"
- "Hold off on ML as D suggests until gameplay is finished."
- "Tour fix can be deferred to after gameplay is finished"
- On the record: "Let's not re-record all 300 seeds each time. When it's time to
  record, record the smaller group of 50 seeds, assess if the implementations
  have been effective and resulted in desired results."

The orchestrator's rulings, made under the owner's delegation of 2026-09-24
("What do you think is best?"):

- The B4 rider: "B4 is the minimal change that closes the leak". It stands as
  the narrow `report_body_handle_version` field.
- Decisions 0.3 items 1 (candidate landing), 2 (a new field is omitted at its
  default), 6 (a recorded value's meaning is frozen) and 9 (the pending guard).
- R13: the census is a separate report, with no scorecard cell.

The dated 2026-09-24 addendum of
[the direction](../direction-2026-09-19-process-over-outcome.md) lists this
field among the wave's recorded experiment fields.

## Acceptance

Every test below lives in `tests/orchestrator/test_report_body_handle.py`, uses
the fake provider or a hand-built state, and writes only under `tmp_path`.
`LEGACY_BODY_HANDLE_PATTERN` is `experiments/held_out_prefixes.py:168`.

- [x] Review correction: the branch takes `main` at `f83050c6` (the look-and-wait card, PR #489)
  by merge commit `ef391150`, never by a rebase. `WAVE_ARMS_PENDING` keeps both cards' removals,
  so only the two ballot values stay pending, and the arm page's pending sentence and the
  re-derived inventory sentence say the same. Proof at the merged head:
  `tests/orchestrator/test_experiment_arms.py::test_a_value_is_pending_exactly_while_its_behaviour_is_unbuilt`
  and `test_the_arm_is_no_longer_pending` pass. Restoring any removed name, dropping a ballot
  name or changing a ballot value fails the first (round-3 probe R1-R7). `scripts/validate_task_docs.py`
  passes and refuses either side's sentence (R10, R11). Every Validation command passes at
  `ef391150`, and `bash scripts/check.sh` at the round's final head.
- [x] Review correction: the Results claim no more about the card's probe table than the module
  asserts, and the module now asserts every cell. For each of the table's three rows,
  `test_the_probe_table_is_measured_on_these_games` pins the prompts, the report and emergency
  openings, the state hashes, the non-opening prompts and how many of them differ raw and after
  normalizing. It pins two handle-blind contrast rows the same way, whose raw count is 0.
  `test_the_probe_table_covers_every_narrowness_pair` ties the table to the compared pairs.
  Perturbed: `test_a_perturbed_game_moves_its_one_cell_of_the_probe_row` (a moved tick state
  hash, an edited later prompt) and `test_a_pair_that_disagrees_on_a_shared_count_is_refused`.
- [x] Review correction: the builder docstring states the absent-corpse reading
  at the strength the code delivers. With neither version 1 nor
  `temporal_observations`, a report names the event's engine id whether or not
  the corpse is still in `state.bodies`. With the arm, temporal delivery or
  both, a corpse missing from `state.bodies` reads `a body`, and the engine id
  is never the fallback. Proof:
  `test_only_neither_switch_names_the_engine_id_of_a_gone_corpse` pins all four
  settings, and two planted builders fail it: an engine-id fallback, and a
  builder that hides the engine id under every setting.
- [x] **The leak closes in play.** Mechanism: `_build_meeting_trigger` renders
  `public_body_id(victim)` when `report_body_handle_version == 1`. The test runs
  a fake game with a declared
  `RecordedExperimentConfig(report_body_handle_version=1)` and temporal OFF:
  seed 1, 7p1i, 1 task each, 80-tick scheduler, the shape of the OFF control.
  - No recorded prompt matches the pattern, retries included.
  - A report opening reads `reported body body-p-3 at tick 8`.
  - The same assertions pass on seed 12 at 9p2i, and with the prompt set
    round 1 records with (`AILIBI_PROMPT_SET=qwen3_6_27b`, set by the test).
  - Planted: a builder with the substitution removed (monkeypatched to the
    legacy description) fails both assertions.
- [x] **OFF bytes are unchanged.** Mechanism: the `None` default takes the
  legacy branch.
  - `test_opening_prompt_body_handle_privacy_is_explicitly_versioned[False]`
    passes unedited, still reading `body-p-3-4 at tick 8`.
  - The golden stays green on s9 and s4, and `verify_samples` passes once per
    set directory on all four sets.
  - The four `build_sample_report --check` runs, the scorecard and census
    `--check` runs and the c9 refit pins, campaign tier included, all pass.
  - Planted: the same OFF game with the field forced ON produces openings that
    differ from the OFF recording's, so the comparison is not vacuous.
- [x] **Reconstruction threads the recorded value, both ways.** Mechanism: the
  golden's directory-callable walk, landed by
  [the readers card](stage-b-readers.md), rebuilds the trigger through the
  production builder with the recorded config. Re-anchor its symbol at dispatch.
  - It reproduces the arm-ON recording above byte-equal.
  - Planted: the walk with the recorded field dropped misses the opening
    prompt's recorded-response lookup.
  - Planted: the walk over an OFF recording with the field forced ON misses it
    too.
- [x] **Only the report openings differ.** Mechanism: the field gates only the
  `described_body` selection. ON versus OFF, on seed 1 (7p1i) and seed 12 (9p2i):
  - equal tick and meeting state hashes, and equal call counts;
  - each ON report opening equals its OFF opening with its one `body-p-N-T`
    replaced by `body-p-N`;
  - every emergency opening is byte-identical;
  - every other prompt is byte-identical once the fake's prompt-seeded
    `fake-<field>-<8 hex>` tokens are normalized, or under a client whose
    responses do not depend on the handle;
  - the ON tick rows carry no temporal version and
    `substrate_flags.temporal_observations` is false;
  - ON and OFF record equal `prompt_versions`, the registry mapping for the set
    in use; for `qwen3_6_27b` that is three `.v6` stamps and
    `vote_ballot.qwen3_6_27b.v8` (`orchestrator/game.py:439-442`).
  - Planted: a builder variant that also drops or alters `at tick T` fails the
    opening-equality assertion.
  - Planted: the same run under `AILIBI_TEMPORAL_OBSERVATIONS=2` fails the
    no-temporal assertion.
- [x] **Edge cases of the builder.** Mechanism: unit tests on
  `_build_meeting_trigger` with hand-built states and events.
  - An emergency trigger's description is byte-identical with the field ON and
    OFF.
  - A report whose corpse is absent from `state.bodies` reads `reported a body`
    under the field and never falls back to the engine id.
  - The field ON together with `temporal_observations=True` gives the temporal
    description unchanged.
  - Planted: a builder that falls back to `body_id` when the victim is unknown
    fails the absent-corpse case.
- [x] **The field round-trips and is omitted at its default.** Mechanism: the
  spine's omit-at-default serializer and this card's deletion of its name from
  `WAVE_ARMS_PENDING`.
  - `RecordedExperimentConfig(report_body_handle_version=1)` validates at
    `format_version` 1, serializes with the key and parses back equal.
  - The default serializes without the key.
  - Every committed experiment-config payload still re-serializes
    byte-identically, by the spine's committed-bytes test (947 rows across the
    100 recordings of `audits/deduction-candidate/run-2026-09-16`, 9 rows of the
    v3 fixture and 237 audit-JSON payloads at `e886b663`), which this card
    re-runs unchanged.
  - The spine's pending-refusal test reads `WAVE_ARMS_PENDING`'s live contents,
    so this card does not edit `tests/orchestrator/test_experiment_arms.py`.
  - Perturbed: `True` and `2` are refused. That refusal is the spine's
    validator; a failure here is reported under Questions, not patched here.
- [x] **A plain shell loads it.** Mechanism: the loader and the replay walk
  re-simulate from the recorded row, not the shell.
  - With no `AILIBI_*` export, `ReplayLoader` loads the arm-ON recording with
    `outcome_verified` true, and the shared walk verifies every tick and
    meeting hash.
  - Perturbed: a copy whose footer config disagrees with its tick rows raises
    in `validate_recorded_experiment_config`.
- [x] **Joint with the reset.** Mechanism: the corpse clear at meeting close
  (`engine/meeting_reset.py:41`) does not change the id's form. The test runs a
  fake game on `{meeting_reset: "hub_with_grace", report_body_handle_version: 1}`.
  - A report meeting opened after a regroup names `body-p-N` without a kill
    tick, a button meeting names no body, and no prompt matches the pattern.
  - The implementer names the seed in Results. If no fake seed gives both
    meetings, build them through `apply_meeting_result` with
    `meeting_reset="hub_with_grace"` and then the builder.
  - Planted: the same game with the field `None` shows the legacy handle in the
    post-regroup report, so the reset alone does not close the leak.
- [x] **End-to-end census conformance.** Mechanism: A1's opening-handle
  conformance cell (C31 in `census_and_record.md`; the flag computed in the
  loader so no text leaves it) and its arm predicate. The census folds the arm-ON
  recording through its write-nothing `--set-dir` path.
  - The cell reads 0. The OFF recording reads its count without raising.
  - Perturbed: a copy with one opening prompt given back its `body-p-N-T`
    handle raises the conformance guard.
  - B5's "kill-tick handle in an opening" STOP relies on this test.
- [x] **The retirement rule is written down.** Mechanism: a scope note in
  `tasks/work/retire-temporal-evidence-v1.md`, Expected scope. When temporal v2
  graduates there, the narrow branch in `_build_meeting_trigger` and its keyword
  are dead code and are deleted (craft rule 3), unless the Stage-B adopting card
  has already graduated them. Either way, `report_body_handle_version` stays in
  `RecordedExperimentConfig` as a read-only recorded key whose missing value
  means `None`. That card's Status stays `ready` and its boxes stay unchecked.
  - Perturbed proof of the reason: a tick-row payload carrying a misspelled
    `report_body_handle_vers: 1` is refused (`extra="forbid"`). So deleting the
    field would make every recording that carries it unparseable.
- [ ] **Nothing else moves.** The diff touches only the Expected-scope files.
  `orchestrator/experiment_config.py` changes by the one deleted pending name.
  No template, `PROMPT_VERSION_SETS` entry, `EXPERIMENT_ENV_NAMES` entry or
  `.env.example` line changes. `bash scripts/check.sh` exits 0 in a clean
  worktree with the exit code printed, and every Validation command passes.
  Mechanism: a scope check that compares `git diff --name-only` from the merge
  base with the Expected-scope list and prints every other path. Planted: run
  against a scratch branch that also touches one out-of-scope path (for example
  a line in `orchestrator/replay.py`), it prints that path and exits non-zero.

## Constraints

**Wave and order.** Card 8 of the Stage-B set, in wave 3.

- Starts after [the readers card](stage-b-readers.md) has merged. That card
  follows [the spine](stage-b-arm-spine.md), which follows
  [A3](docs-truth-typed-trigger.md). Runs in parallel with
  [B1](vent-look-and-wait.md) and [B2](meeting-reset-coherence.md).
- Needs [A1](gameplay-census.md) on `main` for its census test. A1 merges before
  any arm card. If A1 is still open at dispatch, write the other tests first and
  merge `main` once A1 lands.
- Merges after [B0](vent-witness-physical.md) and B1, because
  `WAVE_ARMS_PENDING` names leave in the order B0, B1, B4, B6.
- Merges before B2, which builds on this card's `_build_meeting_trigger` body by
  merging `main`, and before [B6](ballot-kill-row-and-impostor-strategy.md) and
  [B5](stage-b-record-r1.md).
- The dated direction addendum must be on `main` first. If it is not, stop and
  ask. Every merge is the owner's.

**Shared files (decision memo 3.2), one writer per file.**

- `orchestrator/game.py` is region-owned. This card's region is the body of
  `_build_meeting_trigger`: the `described_body` selection (`:3459-3465` at
  `e886b663`), its comment, and the docstring sentences that say which handle
  renders. It is not the signature and keyword (the spine's), the typed-kind
  construction (A3's), the call site in `_run_and_apply_meeting` (the spine
  threads the recorded value there), or any B2 or B6 function.
- If the end-to-end test shows the call site does not pass the recorded value,
  that is a spine defect. Name it under Questions and coordinate with the
  orchestrator before editing outside the region.
- `orchestrator/experiment_config.py` is a declared exception: this card deletes
  only its own `WAVE_ARMS_PENDING` entry.
- `tests/orchestrator/test_report_body_handle.py` is new, and this card is its
  only writer. So is `tasks/work/retire-temporal-evidence-v1.md` in this wave.

**Files this card calls but does not edit.** The golden (readers, then B2 and
B6), `tests/_helpers/committed.py`, `eval/gameplay_census.py` (A1) and
`docs/architecture.md` (A3, the spine and B5). Also `docs/observation-contract.md`
(B0, then B2): its sentence at `:35-38` says full model-facing removal is
implemented only in temporal mode. That becomes incomplete when this card
merges. The PR records it under Decisions as a hand-off to that file's next
writer.

**The partial-record principle, as it binds this card.**

- Only `replays/samples/9p2i`'s seeds are ever re-recorded, and only into a
  candidate directory, by B5. This card records nothing.
- The switch is a `RecordedExperimentConfig` field, default OFF and omitted at
  its default, with no `AILIBI_*` lever and no environment switch.
- Every committed recording, derived view, fixture, gate and doc fact keeps
  verifying byte-identically.
- No registry prompt bump: the trigger text is a template variable, and the
  recorded config carries the provenance.
- Role-correctness is reported, never a gate. The only cell this card touches
  is a conformance count.
- Nothing pushes an agent toward the correct answer. The field removes a
  privileged anchor and adds no information.
- The meeting layer labels and never rewrites. This card changes the
  orchestrator's trigger text, never text an agent authored.

**Delivery.**

- Branch `work/report-body-handle`, with one PR into `main`, merged by merge
  commit or fast-forward and never squashed. Never amend a pushed commit. Take
  `main` by merging it, never by rebasing.
- Each commit body ends with `Card: tasks/work/report-body-handle.md`,
  immediately followed by
  the exact line `Co-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>` (the house trailer, verbatim, whichever model the worker session runs).
- The PR body has the sections Summary, Definition of done (this Acceptance,
  ticked with evidence), Decisions and Questions, and ends with the Claude Code
  attribution line. Agents post no PR comments.

**Status and the task index.** `tasks/README.md` is the orchestrator's.
`scripts/validate_task_docs.py` derives its inventory sentence from every card's
Status, so the worker fills Results and leaves the Status line to the
orchestrator. The orchestrator flips it together with the sentence in one commit
after the merge.

**Non-goals.** No live provider call: fake provider and scripted clients only,
never `.env`, no held-out band. Never print a rendered prompt or a seed-band
prefix; probes are count-only. No ML training or refit (ruling 12), no tour or
featured-list change (ruling 11), no scorecard cell (R13). No lab arm: the
field changes no simulation, which the equal state hashes prove. No new
user-facing copy: under the field the model-facing trigger reads exactly as
temporal mode already renders it, and the field's view label is the spine's.

## Expected scope

- `orchestrator/game.py`: the `_build_meeting_trigger` body region only. The
  arm condition joins the temporal one
  (`temporal_observations or report_body_handle_version == 1`), the
  absent-victim path stays `a body`, and the comment and docstring state the
  field.
- `orchestrator/experiment_config.py`: delete `report_body_handle_version` from
  `WAVE_ARMS_PENDING`.
- `tests/orchestrator/test_report_body_handle.py` (new).
- `tasks/work/retire-temporal-evidence-v1.md`: one scope paragraph under its
  Expected scope.
- This card's Results.

Out of scope: the prompt templates and `PROMPT_VERSION_SETS`; `engine/`,
`agents/`, `meetings/`, `observation/`, `eval/`, `api/` and `frontend/`; the
golden, `tests/_helpers/committed.py`,
`tests/orchestrator/test_temporal_delivery.py` and the held-out files, which are
run unchanged; `docs/architecture.md`, `docs/observation-contract.md`,
`docs/cleanup-dispositions.md` and `.env.example`; and every file under
`replays/`. Directly necessary test follow-through inside the in-scope files is
permitted. Anything else goes under Questions.

## Record impact

- **Default OFF; no committed byte moves.** The four sets, their MANIFESTs and
  report gz files stay as they are. So do `docs/process-scorecard.*`,
  `docs/gameplay-census.*`, the fixtures, the ladder tip and the ML fits. The c9
  derivation reads the default path, which the c9 pins prove. The only tree
  changes are code, one test file and two card texts.
- **The field is recorded ON first by B5**, in
  `replays/candidates/stage-b-r1/9p2i/`. Its conformance cell must read 0
  there, where s9 at baseline 9 reads 135/135.
- **Adoption is a later owner decision.** At graduation the behaviour switch
  and its dead branch are deleted. The key stays read-only, and a missing key
  keeps meaning `None`. Recordings after adoption write the adopted value
  explicitly.
- **Publication.** A push to `main` republishes the demo bundle
  (`.github/workflows/pages.yml`). This card touches no file under `api/` or
  `frontend/` and no shown replay, and the loader never rebuilds trigger text,
  so the bundle's content is unchanged. The PR proves this: a bundle built at
  the merge base and one built at the head have identical `data/` trees.
- **Nothing is re-scored.** The dispositions row on the default-path handle
  stays true. The observation-contract sentence named in Constraints is handed
  on, not left silent.

## Validation

```sh
uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q
uv run pytest -p no:cacheprovider tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_experiment_config.py tests/experiments/test_held_out_prefixes.py tests/meetings/test_prompt_byte_golden.py -q
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
uv run python scripts/check_doc_facts.py
uv run python scripts/validate_task_docs.py
uv run python scripts/verify_ml_evidence.py
uv run pytest -m campaign
git diff --name-only "$(git merge-base origin/main HEAD)" HEAD   # only Expected-scope paths
uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head
bash scripts/check.sh; echo "check.sh exit $?"
```

- Build the base bundle the same way, in a detached worktree at the merge base,
  then run `diff -r` on the two `data/` trees. It must print nothing.
- Every gate runs in a bare shell with 0 `AILIBI_*` exports, and the PR prints
  that count. `verify_ml_evidence` runs offline and never with `--complete`.
- `check.sh` runs whole in a clean worktree, so no gate after a first failure is
  masked. It includes the frontend unit tests. The e2e journey is not required:
  this card touches neither `api/` nor `frontend/`.

## Results

Implemented on `work/report-body-handle` from `f98bfae9`: `59f957e1` (the arm, the pending
removal, the new test module and the follow-through), `1ddd6798` (the retirement scope note) and
`c2aa9023` (three planted cases that kill the mutation survivors). Every command below ran at
`c2aa9023` in a bare shell with 0 `AILIBI_*` exports, unless a line names another commit.

**Status.** Ten of eleven boxes are met. "Nothing else moves" stays unchecked, and the card stays
`active`, for one reason. The diff touches four paths outside Expected scope (see Deviations).
Deleting the spine's builder refusal forced three of them: two tests in
`tests/orchestrator/test_experiment_config.py` and one in `tests/eval/test_recorded_arm_readers.py`
asserted that refusal, and `docs/experiment-arms.md` listed the body handle as pending. The card
expected only `tests/orchestrator/test_experiment_arms.py` to depend on the refusal, and that file
needed no edit. The fourth is `tasks/README.md`, whose inventory sentence the dispatch asked this
card to re-derive. Every other part of that box holds and is evidenced below. The PR asks the
owner under Questions to accept the four paths, and then this box is ticked.

**Sections relied on.** `docs/architecture.md`, "Observation timing and public identities" (the
packet handle and the legacy OFF opening). The spine's arm page, `docs/experiment-arms.md` (the
eight fields, the missing-key rule and the pending guard). `docs/observation-contract.md` (public
packet handles). The decision memo `tasks/decision-2026-09-24-stage-b-wave.md`: 0.2 (the B4
rider), 0.3 items 1, 2, 6 and 9, section 1, 2.4, 3.2 (region ownership), 3.3 and the card-8 brief
in 3.4. The investigation `tasks/investigations-2026-09-24/rebuttal_and_body_handle.md`, section 4.
The dated 2026-09-24 addendum of `tasks/direction-2026-09-19-process-over-outcome.md`, which lists
this field.

**What was built.**
- `orchestrator/game.py::_build_meeting_trigger`, body only:
  - The spine's refusal of value 1 is deleted. A guard refuses every value other than `None` and
    the integer 1 (`True`, `False`, 0, 2, `1.0` and `"1"` raise, naming the value).
  - The `described_body` selection takes the public handle when
    `temporal_observations or report_body_handle_version == 1`. Under either, a corpse missing
    from `state.bodies` reads `a body`; OFF, the legacy branch still names the event's engine id.
  - The comment and the docstring state the field.
  - The signature, the keyword, the typed-kind construction and the call site are unchanged.
- `orchestrator/experiment_config.py`: `report_body_handle_version` is deleted from
  `WAVE_ARMS_PENDING`, and nothing else in that file changed.
- `tests/orchestrator/test_report_body_handle.py` (new, 59 tests). It records 14 named fake games
  once per module under a temporary root, with the meeting runner built from the declared config
  and an explicit environment. It prints no prompt: a failure names handles, meeting ids and counts.
- `tasks/work/retire-temporal-evidence-v1.md`: one scope paragraph under Expected scope. That
  card's Status stays `ready` and its boxes stay unchecked.

**Acceptance evidence** (test names are in `tests/orchestrator/test_report_body_handle.py` unless
a path is given):

| item | evidence | planted or perturbed |
|---|---|---|
| leak closes | `test_no_recorded_prompt_carries_a_kill_tick_handle_under_the_arm` over five arm-ON games: seed 1 (7p1i, 1 task, 80 ticks) and seed 12 (9p2i, 2 tasks, 200 ticks), each on the default set and on `qwen3_6_27b`, plus seed 0 (9p2i, full game, `qwen3_6_27b`). No recorded prompt matches `LEGACY_BODY_HANDLE_PATTERN`, counting every call of every meeting and aborted-meeting row, retries included. Each report opening carries `<opener> reported body body-p-N at tick T`. `test_the_first_report_reads_the_public_handle_at_its_report_tick`: seed 1 reads `reported body body-p-3 at tick 8`, where its engine id is `body-p-3-4`. | `test_a_builder_without_the_substitution_fails_both_leak_checks`: the live builder monkeypatched to the legacy description fails both checks on seed 1 and seed 12 (`qwen3_6_27b`). |
| OFF bytes unchanged | `tests/orchestrator/test_temporal_delivery.py::test_opening_prompt_body_handle_privacy_is_explicitly_versioned[False]` passes unedited (`git diff f98bfae9 -- tests/orchestrator/test_temporal_delivery.py` is empty). The golden passes 35 on s9 and s4; `verify_samples` passes on all four sets; the four report checks, the scorecard and census checks and the campaign tier all pass (Validation below). | `test_forcing_the_arm_on_changes_every_report_opening`: in all five OFF/ON pairs, every OFF report opening names its engine id and differs from its ON opening. |
| reconstruction threads both ways | `test_the_golden_re_renders_the_arm_on_recording_byte_equal`: `golden.walk_directory` (its `_run_recorded_meeting` rebuilds the trigger with the recorded config) reproduces every recorded prompt of seed 1 (default set) and seed 0 (`qwen3_6_27b`), and consumes every recorded call exactly once. | `test_the_golden_misses_the_opening_when_the_recorded_value_is_dropped`: the golden's builder is forced to `None`, and exactly the 4 report meetings of seed 0 miscount. `test_the_golden_misses_the_opening_of_an_off_recording_stamped_on`: an OFF recording is stamped ON (every tick row and the footer), and exactly its 4 report meetings miscount; the unstamped copy is clean. |
| only the openings differ | `test_only_the_report_openings_differ`, over five pairs. Seed 1, seed 12 (default set, fake provider, fake tokens normalized) and seed 0 (`qwen3_6_27b`, 1 emergency and 4 report meetings) give equal tick and meeting state hashes and equal call counts per meeting. Each ON report opening equals its OFF opening with its one engine id replaced by `body-p-N`. The emergency opening is byte-identical. Every other prompt is equal after normalization. Seed 1 and seed 12 under a handle-blind client (`_HandleBlindClient`: the fake provider fed the prompt with ticks stripped from handles) are equal raw. No tick row carries a temporal version, and `substrate_flags.temporal_observations` is false. `prompt_versions` equal the registry mapping for the set in use. `test_the_round_one_stamps_are_the_registry_defaults`: three `.qwen3_6_27b.v6` stamps and `vote_ballot.qwen3_6_27b.v8`. `test_the_normalization_is_needed_and_the_blind_client_removes_the_need` shows why both forms are run. | `test_a_builder_that_moves_the_report_tick_fails_the_opening_equality`: a builder that moves `at tick T` to `T+1`, or drops it, fails the opening equality for every report meeting. `test_temporal_observations_fail_the_no_temporal_check`: the same game with `AILIBI_TEMPORAL_OBSERVATIONS=2` in the runner's environment carries a temporal version on all 24 tick rows and a true flag. |
| builder edge cases | `test_the_arm_changes_only_a_reported_corpses_handle` (Hypothesis, 200 examples, `deadline=None`, over kind, tick, corpse age, victim, corpse present or absent, and temporal): every returned value except the description is equal under `None` and 1. No ON description carries a kill-tick handle. A report without temporal names `body-p-N` for a present corpse and `a body` for an absent one; everything else is byte-identical. `test_an_emergency_description_is_the_same_under_the_arm`, `test_an_absent_corpse_reads_a_body_and_never_the_engine_id`, `test_the_arm_beside_temporal_observations_keeps_the_temporal_text`, `test_the_builder_refuses_a_version_it_does_not_write` (6 values, whole message matched). | `_falls_back_to_the_engine_id` fails the absent-corpse case on description and engine id. |
| round-trip and omission | `test_the_field_round_trips_at_format_one`. `test_the_default_serializes_without_the_key` (the default, the reset alone, format 2, format 3 with evidence 2). `test_the_arm_is_no_longer_pending`. The spine's `tests/orchestrator/test_experiment_arms.py::test_every_committed_recorded_payload_reserializes_byte_for_byte` (956 rows across 101 files, that is 947 rows over the 100 archive recordings plus 9 rows of the v3 fixture) and `test_every_committed_audit_json_payload_reserializes_unchanged` (237 payloads) pass unedited, as does its pending-refusal equality `test_a_value_is_pending_exactly_while_its_behaviour_is_unbuilt`. | `test_a_coerced_or_unknown_version_is_refused`: `True` and 2 are refused by the spine's validator. No Question arises. |
| plain shell | `test_a_plain_shell_loads_the_arm_on_recording`: with every `AILIBI_*` export removed (count asserted 0), `ReplayLoader` loads seed 0 with `outcome_verified` true. The shared walk (the census profile with meeting pre-hashes on) verifies all 57 tick rows and all 5 meetings. | `test_a_footer_that_disagrees_with_the_tick_rows_is_refused`: a footer set to the default config raises `terminal experiment configuration disagrees with tick rows` in `validate_recorded_experiment_config`, through `recorded_experiment_config` and through the loader. |
| joint with the reset | Seed 0, 9p2i, 2 tasks each, full game, `qwen3_6_27b`, `{meeting_reset: "hub_with_grace", report_body_handle_version: 1}`: 3 meetings, 38 calls. Meeting 0 is a button call, and its description is `<opener> called an emergency meeting at tick T`, with no body. Meetings 1 and 2 are reports; each follows a meeting that closed with every survivor in the meeting room and no corpse left, and each opening names `body-p-N`. No prompt matches the pattern. | `test_the_reset_alone_leaves_the_kill_tick_handle`: the same game with the field `None` carries 2 kill-tick handles, each in a post-regroup report opening. |
| census end to end | `test_the_census_counts_no_kill_tick_opening_on_the_arm_on_recording`: `publish_gameplay_census.py --set-dir DIR --json-stdout` folds seed 0 arm ON to `report_openings_with_kill_tick_handle` 0 of 4, guard `report_body_handle_version = 1`. The OFF recording folds to 4 of 4 without raising. B5's STOP on a kill-tick handle in an opening relies on this test. | `test_one_opening_given_back_its_kill_tick_handle_breaks_the_census_guard`: one opening prompt in a copy gets its engine id back. The command exits 1 with nothing on stdout, and stderr names the conformance breach, the setting and the meeting; `set_dir_json` raises `GameplayCensusConformanceError`. |
| retirement rule | The scope paragraph in `tasks/work/retire-temporal-evidence-v1.md`. | `test_a_recorded_key_the_model_does_not_declare_leaves_the_row_unparseable`: an arm-ON tick row parses, and the same row with the key misspelled `report_body_handle_vers` is refused (`extra="forbid"`). |
| nothing else moves | Not met as worded; see Status. `orchestrator/experiment_config.py` changes by the one deleted line. No template, `PROMPT_VERSION_SETS` entry, `EXPERIMENT_ENV_NAMES` entry or `.env.example` line changes. `check.sh` exits 0 and every Validation command passes. | The scope check below, with its planted branch. |

**Re-measured reach** (count-only, at `c2aa9023`). The published census cell
`report_openings_with_kill_tick_handle` in `docs/gameplay-census.json` reads s9 135/135, c9
416/416, s4 36/36, c4 36/36 and pooled 623/623;
`uv run python scripts/publish_gameplay_census.py --check` recomputes it and exits 0. Recorded
calls carrying a `body-p-N-T` handle, retries included, number s9 138, c9 422, s4 36 and c4 36, 632
in all. Calls carrying one from anyone but the opener number 0 in every set. The per-set count
command prints numbers only:
`python3 -c 'import json,re,glob,sys;p=re.compile(r"body-p-\d+-\d+");print(sys.argv[1],sum(1 for f in glob.glob(sys.argv[1]+"/replay-seed-*.jsonl") for l in open(f) for r in [json.loads(l)] if r["kind"]=="meeting" for c in r["llm_calls"] if p.search(c["prompt"])))' replays/samples/9p2i`.
Every number equals the card's Evidence.

**The card's probe, re-measured** through the production path at `c2aa9023` (count-only). At
`c2aa9023` the module above asserted only two of these columns, the state hashes and the count
after normalizing. Round 2 pins every cell in
`test_the_probe_table_is_measured_on_these_games`; see "Review corrections, round 2 (2026-09-27)":

| game | prompts | report openings | state hashes | non-opening prompts differing | after normalizing |
|---|---|---|---|---|---|
| seed 1, 7p1i, 80 ticks, default set | 22 | 2 | equal | 20 of 20 | 0 |
| seed 12, 9p2i, 200 ticks, default set | 44 | 4 | equal | 40 of 40 | 0 |
| seed 0, 9p2i, full game, `qwen3_6_27b` | 66 | 4 (plus 1 emergency) | equal | 46 of 61 | 0 |

**Neuter pass** over every production line this card adds or changes. Each row is one edit applied
to the pristine bytes copied into the scratchpad. The targeted suites then run (the new module,
`tests/orchestrator/test_experiment_config.py`, `tests/orchestrator/test_temporal_delivery.py`,
`tests/meetings/test_meeting_trigger_kind.py`, `tests/orchestrator/test_experiment_arms.py` and
`tests/eval/test_recorded_arm_readers.py`, run as `pytest -n 6 --dist loadfile`). The pass ran
with the module as committed at `c2aa9023` minus its three survivor-killing cases, 437 tests. The
file is then restored from the copy, never from git, and its sha256 is checked equal. Every row
was killed on first run, and every restore matched.

| row | neutered | failed / passed | first failing |
|---|---|---|---|
| N1 | the whole unknown-value guard deleted | 6 / 431 | `test_the_builder_refuses_a_version_it_does_not_write` |
| N2 | the guard's `type(...) is not int` clause dropped | 2 / 435 | the same, for `True` and `False` |
| N3 | the guard's `!= 1` clause dropped | 2 / 435 | the same, for 2 and 0 |
| N4 | the guard's message replaced by a constant | 6 / 431 | the same (whole message matched) |
| N5 | `or report_body_handle_version == 1` dropped | 28 / 409 | the leak, opening-equality, absent-corpse and census tests |
| N6 | `temporal_observations or` dropped | 6 / 431 | `test_opening_prompt_body_handle_privacy_is_explicitly_versioned`, the property, the temporal edge case |
| N7 | the pending entry restored | 10 / 379 (module import error) | `test_a_value_is_pending_exactly_while_its_behaviour_is_unbuilt`, the live-meeting spy, the readers spy, the new module |

**Mutation pass**, once and bounded to the lines this card owns: the body of
`_build_meeting_trigger` and the `WAVE_ARMS_PENDING` mapping. It used exactly the eight operator
classes and the same runner and suites as the neuter pass, and produced 33 mutants.

| class | mutants | outcome |
|---|---|---|
| drop a filter or wrapper | A1 `public_body_id(...)` unwrapped; A2 the `isinstance` filter on `events` dropped | A1 killed (20 failed). A2 SURVIVED at `1ddd6798`, then killed at `c2aa9023` by `test_the_builder_reads_the_trigger_among_the_ticks_other_events` (1 failed). |
| swap a collection | B1 `state.bodies` to `state.players` | killed (25) |
| comparison to a None test | C1 `== 1` to `is not None`; C2 `== 1` to `is None`; C3 `!= 1` to `is None`; C4 `type(...) is not int` to `is None`; C5 the guard's `is not None` inverted; C6 `body_id is not None` inverted; C7 `corpse is not None` inverted; C8 `victim_id is not None` inverted; C9 `described_body is not None` inverted; C10 the kind comparison to `is None` | C1 equivalent: the guard lets only `None` and the integer 1 past, so `== 1` and `is not None` agree on every reachable value. The other nine were killed (31, 2, 2, 200, 25, 28, 23, 38 and 117 failed). |
| read to constant | D1 report `at tick` tick; D2 `trigger_tick`; D3 `kind`; D4 returned kind; D5 victim id; D6 the kind test; D7 emergency tick; D8 the event's body id | all killed (19, 132, 13, 3, 10, 4, 3 and 109 failed) |
| message argument to constant | E1 the refused value in the message; E2 report actor; E3 emergency actor; E4 the described body | all killed (6, 12, 3 and 35 failed) |
| drop a member | F1 `impostor_ballot_version` dropped from the pending mapping; F2 `vent_entry_policy` dropped | both killed by the spine's pending equality (1 failed each) |
| swap branches | G1 the handle selection's branches; G2 the victim guard's branches; G3 the body phrase's branches; G4 the report/emergency branches | all killed (35, 23, 38 and 119 failed) |
| loaded source to literal | H1 `EMERGENCY_TRIGGER_PHRASE` to its literal; H2 `public_body_id(v)` to `f"body-{v}"` | Both SURVIVED at `1ddd6798`. At `c2aa9023` they are killed by `test_an_emergency_description_follows_its_phrase` and `test_the_handle_follows_its_source` (1 failed each). |

The probes that first came back green were A2, H1, H2 and C1; the neuter rows all failed on
first run. The three survivors, re-run at `c2aa9023`, fail as shown, and C1 is named equivalent.
The runner, the tables and the probes are under the session scratchpad's `b4run/` directory,
outside the tree.

**Validation**, at `c2aa9023`, 0 `AILIBI_*` exports, each command's real exit code:

| command | exit | result |
|---|---|---|
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q` | 0 | 59 passed |
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_experiment_config.py tests/experiments/test_held_out_prefixes.py tests/meetings/test_prompt_byte_golden.py -q` | 0 | 197 passed (the golden alone: 35 passed, as at `f98bfae9`) |
| `bash scripts/verify_samples.sh replays/samples/9p2i` | 0 | all 50 verified clean |
| `bash scripts/verify_samples.sh replays/samples/4p1i` | 0 | all 50 verified clean |
| `bash scripts/verify_samples.sh replays/ml_corpus/9p2i` | 0 | all 150 verified clean |
| `bash scripts/verify_samples.sh replays/ml_corpus/4p1i` | 0 | all 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, once per set | 0, 0, 0, 0 | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent |
| `uv run python scripts/check_doc_facts.py` | 0 | verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks, 390 prompts, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed |
| `uv run pytest -m campaign` | 0 | 336 passed, 9365 deselected |
| `git diff --name-only "$(git merge-base origin/main HEAD)" HEAD` | 0 | 7 paths (the Expected-scope four plus the three follow-through paths) |
| `bash scripts/check.sh` in the clean worktree | 0 | ruff clean, 540 files formatted, 4 import contracts kept, task docs valid, strict mypy clean on 511 files, 9342 passed, 20 skipped and 3 xfailed, then 559 vitest tests and the frontend build |

**The scope check** (`scope_check.py` in the scratchpad) prints every changed path outside a given
list and exits 1 if there is any. Against the Expected-scope list at `c2aa9023` it prints
`docs/experiment-arms.md`, `tests/eval/test_recorded_arm_readers.py` and
`tests/orchestrator/test_experiment_config.py`, and exits 1. With those three declared paths and
`tasks/README.md` added to the list, it prints nothing and exits 0. Planted: a scratch branch with
one comment line appended to `orchestrator/replay.py` makes the declared-list run print
`outside the expected scope: orchestrator/replay.py` and exit 1. The scratch branch was then
deleted and never pushed.

**Publication.** `uv run python scripts/build_demo_bundle.py --out <scratch>/bundle-head` at
`c2aa9023`, and the same script at `f98bfae9`, each baked 156 JSON files for 7 featured games in 2
sets. `diff -r` on the two `data/` trees printed nothing (exit 0). The base tree came from
`git archive f98bfae9`. A replay view's `created_at` is its file's mtime (`api/replay_loader.py`,
`_iso_mtime`), and an archive stamps the commit time. So a first diff differed only in
`created_at`, in 9 files. The 319 replay files were confirmed byte-identical to the head
checkout's and given its mtimes, and the base was rebuilt before the diff above.

**Decisions.**
1. The builder refuses any value other than `None` and 1, so a value past the config's validator
   (a `model_construct` config) never silently renders the legacy text.
2. Under the arm, a report whose corpse is missing from `state.bodies` reads `a body`, as temporal
   mode already does. OFF still names the event's engine id there. The property states both.
3. The retirement note states when the branch may be deleted. It is dead for play once temporal
   version 2 graduates. But the golden rebuilds each recorded opening through the keyword, so
   while a walked recording holds the field ON with temporal OFF (the Stage-B candidate will),
   the branch stays as the golden's read path, or the deletion moves that reading into the
   reconstruction. The card's "are dead code" is true for play only.
4. `docs/observation-contract.md` (its "Full model-facing removal is implemented only in temporal
   mode" sentence) is incomplete now that the arm exists. This is handed to that file's next
   writer, the reset card. `docs/architecture.md` "Complete model-facing body-ID privacy remains
   gated" and `docs/cleanup-dispositions.md` rows A-32 and G1-01 stay true: the default path still
   renders the engine id.
5. The card leaves Status to the orchestrator, but the dispatch asked this card to set it and to
   re-derive the index sentence. With one box unchecked, Status is `active`, not `done`.

**Deviations from Expected scope, all direct follow-through of deleting the refusal**, with every
changed expectation:
- `tests/orchestrator/test_experiment_config.py`:
  - `test_no_body_handle_arm_builds_todays_trigger_byte_for_byte` replaces its `pytest.raises`
    block with the arm's expectation. Version 1 gives today's trigger with the one handle
    substituted for a report without temporal, and the same trigger otherwise.
  - `test_the_live_meeting_passes_the_recorded_body_handle_arm` now runs the game. A spy on the
    builder must see 1 on every meeting, and the test no longer patches the guard open.
- `tests/eval/test_recorded_arm_readers.py::test_the_reconstructors_hand_the_recorded_trigger_setting_to_the_builder`:
  a spy on the builder both readers call must see `None` on every meeting of the plain recording
  and 1 on every meeting of the stamped copy, where it used to expect the refusal.
- `docs/experiment-arms.md`: the pending-guard sentence no longer lists the body handle.
- `tasks/README.md`: the inventory sentence, re-derived for this card's Status.

No test was deleted or skipped. Closing greps at `c2aa9023`:
`git grep -n -i -E 'trigger text (that is|no builder)|names a trigger|body.handle[^.]*(pending|not built|unbuilt|refus)|(pending|unbuilt|not built)[^.]*body.handle' -- . ':!tasks/decision-2026-09-24-stage-b-wave.md' ':!tasks/investigations-2026-09-24' ':!audits' ':!agent_prompts' ':!replays'`
finds only dated card Results, B1's card (not this card's file), this card and the new test. A
second grep for `only in temporal`, `model-facing ... privacy` and `death-tick handle` outside
`tasks/`, `audits/`, `agent_prompts/`, `replays/`, `training/reports/` and the census pages finds
only the rows named in Decision 4 and test or held-out-generator text that concerns temporal
version 2.

**Record impact, as delivered.** No committed byte under `replays/`, `audits/`, `tests/fixtures/`
or `docs/` (apart from the one arm-page sentence) moved. So no `docs/artifacts.md` row changes.
The held-out manifest and generator are untouched: the band is checked against its own frozen
bytes, and `tests/experiments/test_held_out_prefixes.py` passes. The field is first recorded ON
by the round-1 record card.

**Limitations.**
- Fake games establish the mechanism, not what a real model says. The 38 openings whose free text
  names the kill tick (Evidence) are neither explained nor addressed, and the arm may remove a
  correct time a reporter passed on.
- The hash chain cannot tell which value a recording was made under: an OFF recording stamped ON
  re-simulates with every hash equal. The golden (its misses) and the census guard (a kill-tick
  handle under the ON stamp) are the checks that see it. The committed-meeting walk reads only
  the trigger kind, so it cannot.
- The golden still refuses temporal recordings, so it re-renders the arm only with temporal
  delivery OFF.
- The mutation pass covered only the lines this card owns, with the eight listed classes.

### Review corrections, round 1 (2026-09-27)

Review at `1cdee965` raised one blocking finding, from the docs verifier. It is the same defect as
Codex's P2 inline comment on PR #488 (`orchestrator/game.py:3599`, 2026-09-27). The fix is
`29519860`, and this subsection lands in the commit after it. Every command below ran at
`29519860` in a bare shell with 0 `AILIBI_*` exports, unless a line names another commit.

**The finding.** The `_build_meeting_trigger` docstring said: "Under either, a corpse missing
from `state.bodies` reads "a body" and the engine id is never the fallback." It followed sentences
about `None` and version 1, so it read as a guarantee under both values. The code does not deliver
that. With neither version 1 nor `temporal_observations`, the builder names the event's engine id
whether or not the corpse is still in `state.bodies`. The other three settings read `a body`. The
property `test_the_arm_changes_only_a_reported_corpses_handle` already asserted the OFF reading.
The sentence before it ("`None` names a reported corpse by the engine's body id") was overstated
too: `None` beside `temporal_observations` names the public handle.

**The Codex comment: valid, accepted.** It asked to "qualify the statement to the arm/temporal
branches or describe the legacy fallback". The fix does both. It is answered here and in the PR
body, not on the PR, because agents post no PR comments.

**What changed in `29519860`.**
- `orchestrator/game.py`, inside this card's region: the docstring paragraph on the field and the
  `described_body` comment. No production line changed. The docstring now states each setting at
  the strength the code delivers:
  - With neither version 1 nor `temporal_observations`, a report names the event's engine id,
    whether or not the corpse is still in `state.bodies`.
  - With version 1, `temporal_observations` or both, a report names the public handle, and a
    corpse missing from `state.bodies` reads `a body`: the engine id is never the fallback.
  - A report event that carries no body id reads `a body` under every setting.
  - The arm changes at most the report's body phrase, and only without `temporal_observations`.
- `tests/orchestrator/test_report_body_handle.py`:
  - New `test_only_neither_switch_names_the_engine_id_of_a_gone_corpse`. It reads, under all four
    `(report_body_handle_version, temporal_observations)` settings, a report of corpse `p-6`
    (killed at tick 11) gone from the state and a report event with no body id. The production
    builder gives `p-4 reported body body-p-6-11 at tick 17` for the gone corpse only with both
    switches off, and `p-4 reported a body at tick 17` in the other seven cells.
  - Planted: `_falls_back_to_the_engine_id` names the engine id under all four settings. The new
    `_hides_the_engine_id` reads `a body` under all four. Each fails the table.
  - The module docstring's builder bullet is narrowed the same way.
- No other file changed. No expectation changed, and no test was weakened, skipped or deleted.
  The module has 60 tests, one more than at `1cdee965`.

**Closing greps** at `29519860`:
- `grep -rniE 'never the fallback|never falls? back to the engine|under either|either one exposes|names a reported corpse by the engine' orchestrator tests/orchestrator docs observation meetings api`
  finds only the new comment's "Either one exposes at most the victim's public handle" and an
  unrelated resume sentence at `orchestrator/game.py:1923`.
- The same pattern over the `eval/` package, this card and `tasks/work/retire-temporal-evidence-v1.md`
  finds only this card's Acceptance item on the absent corpse (scoped to "under the field") and
  its "What was built" line. That line is scoped to the arm-or-temporal condition, and it names
  the OFF engine id in the same sentence.
- The PR body's Decision 2 already scoped the claim to the field.

**Mutation probe**, bounded to the span the finding names (the corpse lookup, the
`described_body` selection and the body phrase in `_build_meeting_trigger`), with the eight
operator classes only. Each mutant is one exact-string edit applied to the pristine bytes. The
runner first runs the new test alone, then the targeted suites: the new module,
`tests/orchestrator/test_experiment_config.py`, `tests/orchestrator/test_temporal_delivery.py` and
`tests/meetings/test_meeting_trigger_kind.py`, 207 tests, as `pytest -n 6 --dist loadfile`. The
file is restored from a copy, never from git, and every restore's sha256 matched.

| mutant | class | edit | new test | suites failed |
|---|---|---|---|---|
| M1 | drop a filter | `temporal_observations or` dropped | killed | 7 |
| M2 | drop a filter | `or report_body_handle_version == 1` dropped | killed | 31 |
| M3 | drop a wrapper | `public_body_id(...)` unwrapped | passed | 22 |
| M4 | swap a collection | `state.bodies` to `state.players` | passed | 27 |
| M5 | None test | `corpse is not None` inverted | killed | 31 |
| M6 | None test | `victim_id is not None` inverted | killed | 26 |
| M7 | None test | `== 1` to `is not None` | passed | 0, equivalent |
| M8 | None test | `body_id is not None` inverted | passed | 27 |
| M9 | None test | `described_body is not None` inverted | killed | 41 |
| M10 | read to constant | the legacy `else body_id` to `else None` | killed | 23 |
| M11 | read to constant | the victim read to `None` | passed | 27 |
| M12 | read to constant | the event's body id to `None` | killed | 45 |
| M13 | message argument to constant | the described body in the phrase | killed | 38 |
| M14 | swap branches | the handle selection's branches | killed | 38 |
| M15 | swap branches | the victim guard's branches | killed | 26 |
| M16 | swap branches | the body phrase's branches | killed | 41 |
| M17 | loaded source to literal | `public_body_id(v)` to `f"body-{v}"` | passed | 1 |

Sixteen of 17 are killed by the suites. M7 is equivalent: the guard admits only `None` and the
integer 1, so `== 1` and `is not None` agree on every reachable value. This is the earlier pass's
C1. The six that pass the new test alone (M3, M4, M7, M8, M11 and M17) change present-corpse
readings, or none at all. The new test builds only gone corpses and events without an id, and
the other tests in the suites kill those five. M10 is the finding's own defect class: it hides
the legacy engine id. The new table kills it, and so do 22 other tests. The runner and its log are under the session scratchpad's `fix-b4-r1/` directory, outside the
tree.

**Validation** at `29519860`, each command's real exit code:

| command | exit | result |
|---|---|---|
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q` | 0 | 60 passed |
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_experiment_config.py tests/experiments/test_held_out_prefixes.py tests/meetings/test_prompt_byte_golden.py -q` | 0 | 197 passed |
| `uv run pytest -p no:cacheprovider tests/meetings/test_prompt_byte_golden.py -q` | 0 | 35 passed |
| `bash scripts/verify_samples.sh <set>` on `replays/samples/9p2i`, `replays/samples/4p1i`, `replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i` | 0, 0, 0, 0 | 50, 50, 150 and 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, once per set | 0, 0, 0, 0 | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent |
| `uv run python scripts/check_doc_facts.py` | 0 | verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks, 390 prompts, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed |
| `uv run pytest -m campaign` | 0 | 336 passed, 9366 deselected |
| `git diff --name-only 1cdee965 HEAD` | 0 | `orchestrator/game.py` and `tests/orchestrator/test_report_body_handle.py` |
| `git diff --name-only "$(git merge-base origin/main HEAD)" HEAD` | 0 | the same 9 paths as at `1cdee965`; `main` is still `f98bfae9` |

**Publication.** `uv run python scripts/build_demo_bundle.py --out <scratch>` ran twice in this
checkout: once at `29519860`, and once with `1cdee965`'s `orchestrator/game.py` copied in and then
restored from the copy (sha256 checked). Each baked 156 JSON files for 7 featured games in 2 sets.
`diff -r` on the two `data/` trees printed nothing (exit 0). Both builds read the same checkout, so
the replay mtimes were equal. The earlier comparison of `c2aa9023` with the merge base still
stands, because `1cdee965` changed only this card and `tasks/README.md`.

**The full gate.** `bash scripts/check.sh` runs once in this round, alone, in this clean worktree,
at the round's final head: the commit that adds this subsection. PR #488's body records its exit
code and counts.

**Status.** It stays `active`. The dispatch for this round assumed `done`, but the card was
`active` at `1cdee965`, and its last box waits on the owner's answer to the PR's Question. This
round does not tick a box the owner has not answered. The inventory sentence in `tasks/README.md`
is unchanged, and `validate_task_docs.py` re-derives it and passes. No `audits/` or
`tests/fixtures/` byte moved, so no `docs/artifacts.md` row changes. The held-out band is
untouched.

### Review corrections, round 2 (2026-09-27)

Review at `7622b11d` raised one blocking finding, from the docs verifier. The fix is `dd034a10`,
and this subsection lands in the commit after it. Every command below ran at `dd034a10` in a bare
shell with 0 `AILIBI_*` exports, unless a line names another commit.

**The finding: valid, accepted.** The paragraph "The card's probe, re-measured" said "the module
above asserts each cell". At `7622b11d` the module asserted three things about that table: equal
state hashes and 0 differences after normalizing, both in `test_only_the_report_openings_differ`,
and a non-empty raw difference on seed 1 in
`test_the_normalization_is_needed_and_the_blind_client_removes_the_need`. No test pinned the
prompt counts (22, 44, 66), the report openings (2, 4, and 4 plus 1 emergency) or the raw
non-opening differences (20 of 20, 40 of 40, 46 of 61). No command in Results or the PR
reproduced them.

**What changed.**
- `dd034a10` changes `tests/orchestrator/test_report_body_handle.py` only:
  - `_probe_row` counts every cell of the table from a recorded OFF/ON pair into a `_ProbeRow`:
    - prompts: every call of every meeting and aborted-meeting row;
    - report and emergency openings: from the triggers the live builder returned;
    - whether the state hashes are equal: tick and meeting hashes and per-meeting call counts;
    - the non-opening prompts, and how many of them differ raw and after normalizing.
  - Both games must agree on every count they share, or `_probe_row` raises and names the pair.
  - `PROBE_TABLE` holds the card's three rows and two handle-blind contrast rows.
    `test_the_probe_table_is_measured_on_these_games` asserts that each pair's measured row equals
    its pinned row. `test_the_probe_table_covers_every_narrowness_pair` ties the table's keys to
    `NARROWNESS_PAIRS`.
  - Perturbed, `test_a_perturbed_game_moves_its_one_cell_of_the_probe_row`:
    - one ON tick row given another state hash changes only the hashes cell, to not equal;
    - one word appended to the first meeting's last prompt changes only the cell after
      normalizing, to 1.
  - Perturbed, `test_a_pair_that_disagrees_on_a_shared_count_is_refused`: one report trigger
    re-labelled as an emergency makes `_probe_row` refuse the pair.
  - The module docstring names the pinned table. The module has 69 tests, 9 more than at
    `7622b11d`.
- This commit rewords the parenthetical above. It now names the two columns `c2aa9023` asserted
  and the round-2 test. It also adds this subsection and one Acceptance item.
- No production line changed. No expectation changed, and no test was weakened, skipped or
  deleted.

**The table, re-measured at `dd034a10`** through the production path: fake games recorded by
`_play` with the live builder. The command
`uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q -k probe_table`
passes 6 tests only when every cell below holds. It prints no prompt.

| pair | prompts | report openings | emergency openings | state hashes | non-opening prompts | differing raw | after normalizing |
|---|---|---|---|---|---|---|---|
| seed 1, 7p1i, 80 ticks, default set | 22 | 2 | 0 | equal | 20 | 20 | 0 |
| seed 12, 9p2i, 200 ticks, default set | 44 | 4 | 0 | equal | 40 | 40 | 0 |
| seed 0, 9p2i, full game, `qwen3_6_27b` | 66 | 4 | 1 | equal | 61 | 46 | 0 |
| seed 1, handle-blind client, `qwen3_6_27b` | 22 | 2 | 0 | equal | 20 | 0 | 0 |
| seed 12, handle-blind client, `qwen3_6_27b` | 44 | 4 | 0 | equal | 40 | 0 | 0 |

The first three rows equal the card's table at `c2aa9023`, cell for cell. Seed 1 and seed 12 also
equal the Evidence table measured at `e886b663`.

**Mutation probe.** It is bounded to the round-2 span (`_ProbeRow`, `_probe_row`, `PROBE_TABLE`,
the three perturbations and the four new tests) and uses the eight operator classes only. Each
mutant is one exact-string edit applied to the pristine bytes. The runner then runs the whole
module as `pytest -n 6 --dist loadfile` and restores the file from a copy, never from git. All 27
restores matched the pristine sha256, and the file equalled `HEAD` afterwards.

| mutant | class | edit | failed | first failing |
|---|---|---|---|---|
| P1 | drop a filter | report count to all openings | 1 | measured row, seed 0 |
| P2 | drop a filter | openings not subtracted from calls | 7 | every measured row, both perturbations |
| P3 | drop a wrapper | `list(...)` dropped from the coverage check | 1 | coverage |
| P4 | swap a collection | prompts to meetings | 7 | every measured row, both perturbations |
| P5 | swap a collection | openings to report openings | 1 | measured row, seed 0 |
| P6 | swap a collection | `(off, on)` to `(off, off)` in the shared counts | 1 | shared-count refusal |
| P7 | swap a collection | raw differences measured OFF against OFF | 5 | fake-provider rows, both perturbations |
| P8 | comparison inverse | shared-count equality inverted | 8 | all eight new game tests |
| P9 | comparison inverse | hashes cell inverted | 7 | every measured row, both perturbations |
| P10 | to a None test | the measured-row verdict | 0 | survived; see below |
| P11 | to a None test | the coverage verdict | 0 | survived; see below |
| P12 | read to constant | trigger kind to `"report"` | 2 | measured row, seed 0; shared-count refusal |
| P13 | read to constant | emergency count to 0 | 1 | measured row, seed 0 |
| P14 | read to constant | hashes cell to `True` | 1 | moved state hash |
| P15 | read to constant | raw count to 0 | 5 | fake-provider rows, both perturbations |
| P16 | read to constant | normalized count to 0 | 1 | edited later prompt |
| P17 | message to constant | the refusal message | 1 | shared-count refusal |
| P18 | drop a member | seed 0 row | 1 | coverage |
| P19 | drop a member | seed 12 blind row | 1 | coverage |
| P20 | source to literal | `NARROWNESS_PAIRS` to the card's three pairs | 1 | coverage |
| P21 | swap a collection | tick row to meeting row in the hash perturbation | 1 | moved state hash |
| P22 | read to constant | the moved hash to the row's own | 1 | moved state hash |
| P23 | drop a member | the edited call to the original | 1 | edited later prompt |
| P24 | read to constant | the edited prompt to the original | 1 | edited later prompt |
| P25 | comparison inverse | the not-the-opening guard inverted | 1 | edited later prompt |
| P26 | read to constant | the re-label to `"report"` | 1 | shared-count refusal |
| P27 | to a None test | the perturbed-row verdict | 0 | survived; see below |

"Swap adjacent branches" has no site: the span has no branch. P10, P11 and P27 each replace a new
test's own final equality with a None test. They are equivalent on these bytes. The equality they
replace holds, so the weakened test passes on every run, and no test can fail on a mutant that
only weakens a true assertion. Each of these verdict lines is shown live by the mutants of its
inputs that make that line, not an earlier helper assertion, fail:
- P10's measured-row verdict by P1, P2, P4, P5, P7, P9, P12, P13 and P15;
- P11's coverage verdict by P18, P19 and P20;
- P27's perturbed-row verdict by P2, P4, P7, P9, P14, P15, P16, P23 and P24.

These mutants first came back green in a draft that had only the state-hash perturbation: P6,
P10, P11, P16, P17, and a mutant that swapped the pinned row for its own literal (equivalent,
the same value). The draft then gained the edited-prompt perturbation, which kills P16. It also
gained the re-label perturbation with a message naming the pair, which kills P6 and P17. Only
the final bytes were committed. The runner, its logs and the count-only probes are under the
session scratchpad's `fix-b4-r2/` directory, outside the tree.

**Validation** at `dd034a10`, each command's real exit code:

| command | exit | result |
|---|---|---|
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q` | 0 | 69 passed |
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_experiment_config.py tests/experiments/test_held_out_prefixes.py tests/meetings/test_prompt_byte_golden.py -q` | 0 | 197 passed |
| `uv run pytest -p no:cacheprovider tests/meetings/test_prompt_byte_golden.py -q` | 0 | 35 passed |
| `bash scripts/verify_samples.sh <set>` on `replays/samples/9p2i`, `replays/samples/4p1i`, `replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i` | 0, 0, 0, 0 | 50, 50, 150 and 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, once per set | 0, 0, 0, 0 | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent |
| `uv run python scripts/check_doc_facts.py` | 0 | verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks, 390 prompts, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed |
| `uv run pytest -p no:cacheprovider -m campaign -q` | 0 | 336 passed, 9375 deselected |
| `git diff --name-only 7622b11d HEAD` | 0 | `tests/orchestrator/test_report_body_handle.py` |
| `git diff --name-only f98bfae9 HEAD` | 0 | the same 9 paths as at `7622b11d`; `main` is still `f98bfae9` |

**Publication.** This round touches no file under `api/` or `frontend/` and no replay, and the
demo bundle reads no test module. So the earlier bundle comparisons stand, and no bundle was
rebuilt.

**The full gate.** `bash scripts/check.sh` runs once in this round, alone, in this clean worktree,
at the round's final head: the commit that adds this subsection. PR #488's body records its exit
code and counts.

**Status.** It stays `active`. The dispatch for this round again assumed `done`, but the last box
still waits on the owner's answer to the PR's Question, and this round does not tick it. The
inventory sentence in `tasks/README.md` is unchanged, and `validate_task_docs.py` re-derives it
and passes. No `audits/` or `tests/fixtures/` byte moved, so no `docs/artifacts.md` row changes.
The held-out band is untouched. The dispatch named this subsection's date 2026-09-26; it carries
the date the work was done, 2026-09-27, after round 1's subsection of the same date.

### Review corrections, round 3 (2026-09-27)

The integration review at `609b3541` raised one blocking finding. `main` moved from `f98bfae9` to
`f83050c6` when the look-and-wait card (B1, PR #489) merged, and PR #488 then conflicted. The fix
is merge commit `ef391150`, and this subsection lands in the commit after it. Every command below
ran at `ef391150` in a bare shell with 0 `AILIBI_*` exports, unless a line names another commit.

**The finding: valid, accepted.** B1 deleted its two names from `WAVE_ARMS_PENDING` and flipped
its card. This branch deleted `report_body_handle_version` from the same mapping and re-derived the
same index sentence. The merge had to keep both deletions and re-derive the sentence, and then
every gate had to run again at the merged head.

**The merge.** `git merge origin/main` at `f83050c6`, never a rebase. `ef391150` has the parents
`609b3541` and `f83050c6`. Three paths conflicted, and each keeps both sides:
- `orchestrator/experiment_config.py`: `WAVE_ARMS_PENDING` keeps B1's deletion of
  `vent_exit_policy` `look_and_wait` and `vent_entry_policy` `own_fresh_kill`, and this card's
  deletion of `report_body_handle_version` 1. Only `ballot_kill_row_version` 1 and
  `impostor_ballot_version` 1 stay pending.
- `docs/experiment-arms.md`: the pending-guard sentence lists version 1 of both ballot fields. It
  names the physical rule, `look_and_wait`, `own_fresh_kill` and version 1 of the body handle as
  built.
- `tasks/README.md`: the inventory sentence reads 88 cards: 4 ready, 1 active, 83 done.
  `scripts/validate_task_docs.py` re-derives it and passes. The dispatch expected 4 ready and 84
  done, which assumes this card is `done`. It is `active` on its branch (see Status below), so the
  validator counts 1 active and 83 done.

Every other path merged without a conflict. That includes B1's edits to
`tests/orchestrator/test_experiment_config.py` and `tests/eval/test_recorded_arm_readers.py`,
which this card also edits.

**The card's diff after the merge.** `git diff --name-only f83050c6 HEAD` lists the same 9 paths
as `git diff --name-only f98bfae9 609b3541`. For 7 of them the changed lines are the same before
and after the merge. The check compares the `+` and `-` lines of
`git diff f98bfae9 609b3541 -- <path>` with those of `git diff f83050c6 ef391150 -- <path>`. The
two paths that differ are the two resolved sentences, in `docs/experiment-arms.md` and
`tasks/README.md`. `orchestrator/experiment_config.py` still changes by one deleted pending line.

**Mutation probe**, bounded to the resolved spans: the `WAVE_ARMS_PENDING` mapping, the arm page's
pending sentence and the inventory sentence. Each mutant is one exact-string edit applied to the
pristine bytes. For a code mutant the runner runs the suites the merge touches as
`pytest -n 6 --dist loadfile`:
- `tests/orchestrator/test_experiment_config.py`
- `tests/orchestrator/test_experiment_arms.py`
- `tests/eval/test_recorded_arm_readers.py`
- this card's module
- B1's `tests/agents/test_vent_look_and_wait.py`, `tests/experiments/test_vent_look_and_wait_game.py`
  and `tests/experiments/test_tactical_gameplay.py`

For a text mutant it runs `scripts/check_doc_facts.py`, `scripts/validate_task_docs.py` and
`tests/orchestrator/test_experiment_arms.py`. The file is restored from a copy, never from git.
Every restore matched the pristine sha256, and `git status` was empty afterwards.

| mutant | class | edit | result | failing, among others |
|---|---|---|---|---|
| R1 | drop a member | `report_body_handle_version` 1 put back as pending (resolved as main's side) | killed: 4 failed, 6 errors | the spine's pending equality, `test_the_live_meeting_passes_the_recorded_body_handle_arm`, both readers' trigger spies, this card's module |
| R2 | drop a member | `look_and_wait` put back as pending | killed: 28 failed, 6 errors | the pending equality, the lab-candidate tests, B1's game tests |
| R3 | drop a member | `own_fresh_kill` put back as pending | killed: 29 failed, 6 errors | the same, and the factory refusal |
| R4 | drop a member | both put back (resolved as this branch's side) | killed: 31 failed, 6 errors | the pending equality |
| R5 | drop a member | `ballot_kill_row_version` dropped | killed: 1 failed | the pending equality |
| R6 | drop a member | `impostor_ballot_version` dropped | killed: 1 failed | the pending equality |
| R7 | read to constant | the kill-row value 1 changed to 2 | killed: 4 failed | the pending equality, the validation and runner refusals |
| R8 | text | the arm-page sentence resolved as this branch's side | not caught | none |
| R9 | text | the arm-page sentence resolved as main's side | not caught | none |
| R10 | text | the index sentence resolved as this branch's side (5 ready, 1 active, 82 done) | killed | `validate_task_docs.py` exits 1 |
| R11 | text | the index sentence resolved as main's side (5 ready, 83 done) | killed | `validate_task_docs.py` exits 1 |

The spine's pending equality is
`tests/orchestrator/test_experiment_arms.py::test_a_value_is_pending_exactly_while_its_behaviour_is_unbuilt`.
It failed under each of R1 to R7.

R8 and R9 are not code mutants. The arm page's pending sentence is prose, and no gate reads it:
`check_doc_facts.py`, `validate_task_docs.py` and the spine's page checks (fields, links and
environment switches) all pass on both variants. This round adds no gate for the sentence, for
three reasons:
- it states no number;
- the spine's test module is outside this card's scope;
- the ballot card rewrites the sentence when it deletes the guard.

The resolved sentence was checked by reading it against the live mapping. The runner and its
count-only logs are under the session scratchpad's `fix-b4-r3/` directory, outside the tree.

**B1's lab rows at the merged head.** This command exits 0:
`uv run python -m experiments.tactical_gameplay --split development --arms baseline stage_b_full --output <scratch>/lab.json`.
All 32 games, 8 seeds on each roster for each arm, reproduce the replay hash, trajectory hash and
counts of their rows in `audits/tactical-gameplay/stage-b-development.json`. Both arms' configs
are equal. This command prints 32:

```sh
python3 -c 'import json,sys;a,b=(json.load(open(p)) for p in sys.argv[1:3]);print(sum(x["replay_sha256"]==y["replay_sha256"] and x["counts"]==y["counts"] and x["trajectory_sha256"]==y["trajectory_sha256"] for arm in ("baseline","stage_b_full") for s in ("4p1i","9p2i") for x,y in zip(a["arms"][arm]["sets"][s],b["arms"][arm]["sets"][s])))' <scratch>/lab.json audits/tactical-gameplay/stage-b-development.json
```

`stage_b_full` leaves the body handle out (`STAGE_B_FULL_SETTINGS`), so the lab walks only this
card's default path. The run's `source_sha256` differs from the committed one, as it must: it
hashes `orchestrator/`, which this card changes. It records the run's provenance, and no gate
compares it. No byte under `audits/` moved.

**Validation** at `ef391150`, each command's real exit code:

| command | exit | result |
|---|---|---|
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q` | 0 | 69 passed |
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_temporal_delivery.py tests/orchestrator/test_experiment_config.py tests/experiments/test_held_out_prefixes.py tests/meetings/test_prompt_byte_golden.py -q` | 0 | 197 passed |
| `uv run pytest -p no:cacheprovider tests/meetings/test_prompt_byte_golden.py -q` | 0 | 35 passed |
| `uv run pytest -p no:cacheprovider tests/orchestrator/test_report_body_handle.py -q -k probe_table` | 0 | 6 passed: every cell of the probe table holds |
| `bash scripts/verify_samples.sh <set>` on `replays/samples/9p2i`, `replays/samples/4p1i`, `replays/ml_corpus/9p2i` and `replays/ml_corpus/4p1i` | 0, 0, 0, 0 | 50, 50, 150 and 50 verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check`, once per set | 0, 0, 0, 0 | each report consistent with its replays |
| `uv run python scripts/publish_process_scorecard.py --check` | 0 | consistent |
| `uv run python scripts/publish_gameplay_census.py --check` | 0 | consistent |
| `uv run python scripts/check_doc_facts.py` | 0 | verified |
| `uv run python scripts/validate_task_docs.py` | 0 | 390 phase tasks, 390 prompts, 88 work cards |
| `uv run python scripts/verify_ml_evidence.py` (offline, never `--complete`) | 0 | every check passed |
| `uv run pytest -p no:cacheprovider -m campaign -q` | 0 | 336 passed, 9516 deselected |
| `git diff --name-only f83050c6 HEAD` | 0 | the 9 paths listed above; `f83050c6` is the merge base |

The 69 tests of this card's module include the planted and perturbed cases the dispatch named:
- the arm-ON leak checks and their planted builder without the substitution;
- the OFF control forced ON (`test_forcing_the_arm_on_changes_every_report_opening`);
- the reset-alone plant;
- the census end-to-end test and its perturbed opening.

Each passes at `ef391150` with the numbers in the Acceptance evidence table above. The module is
byte-identical to `609b3541`'s.

**Publication.** `uv run python scripts/build_demo_bundle.py --out <scratch>` ran twice in this
checkout: once at `ef391150`, and once with every path of `git diff --name-only f83050c6 ef391150`
set to its `f83050c6` bytes. The paths were then restored from copies, sha256 checked, and
`git status` was empty. Each build baked 156 JSON files for 7 featured games in 2 sets. `diff -r`
printed nothing, both on the two `data/` trees and on the two whole bundles. Both builds read the
same checkout, so the replay mtimes were equal.

**The full gate.** `bash scripts/check.sh` runs once in this round, alone, in this clean worktree,
at the round's final head, which is the commit that adds this subsection. PR #488's body records
its exit code and counts.

**Status.** It stays `active`. The last box still waits on the owner's answer to the PR's
Question, and this round does not tick it. This card's changes to the four paths that Question
names are the same after the merge, apart from the two resolved sentences. No `audits/` or
`tests/fixtures/` byte moved, so
no `docs/artifacts.md` row changes. The held-out band is untouched, and
`tests/experiments/test_held_out_prefixes.py` passes.
