# B4: close the kill-tick leak with the public body handle

**Status:** ready

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

- [ ] **The leak closes in play.** Mechanism: `_build_meeting_trigger` renders
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
- [ ] **OFF bytes are unchanged.** Mechanism: the `None` default takes the
  legacy branch.
  - `test_opening_prompt_body_handle_privacy_is_explicitly_versioned[False]`
    passes unedited, still reading `body-p-3-4 at tick 8`.
  - The golden stays green on s9 and s4, and `verify_samples` passes once per
    set directory on all four sets.
  - The four `build_sample_report --check` runs, the scorecard and census
    `--check` runs and the c9 refit pins, campaign tier included, all pass.
  - Planted: the same OFF game with the field forced ON produces openings that
    differ from the OFF recording's, so the comparison is not vacuous.
- [ ] **Reconstruction threads the recorded value, both ways.** Mechanism: the
  golden's directory-callable walk, landed by
  [the readers card](stage-b-readers.md), rebuilds the trigger through the
  production builder with the recorded config. Re-anchor its symbol at dispatch.
  - It reproduces the arm-ON recording above byte-equal.
  - Planted: the walk with the recorded field dropped misses the opening
    prompt's recorded-response lookup.
  - Planted: the walk over an OFF recording with the field forced ON misses it
    too.
- [ ] **Only the report openings differ.** Mechanism: the field gates only the
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
- [ ] **Edge cases of the builder.** Mechanism: unit tests on
  `_build_meeting_trigger` with hand-built states and events.
  - An emergency trigger's description is byte-identical with the field ON and
    OFF.
  - A report whose corpse is absent from `state.bodies` reads `reported a body`
    under the field and never falls back to the engine id.
  - The field ON together with `temporal_observations=True` gives the temporal
    description unchanged.
  - Planted: a builder that falls back to `body_id` when the victim is unknown
    fails the absent-corpse case.
- [ ] **The field round-trips and is omitted at its default.** Mechanism: the
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
- [ ] **A plain shell loads it.** Mechanism: the loader and the replay walk
  re-simulate from the recorded row, not the shell.
  - With no `AILIBI_*` export, `ReplayLoader` loads the arm-ON recording with
    `outcome_verified` true, and the shared walk verifies every tick and
    meeting hash.
  - Perturbed: a copy whose footer config disagrees with its tick rows raises
    in `validate_recorded_experiment_config`.
- [ ] **Joint with the reset.** Mechanism: the corpse clear at meeting close
  (`engine/meeting_reset.py:41`) does not change the id's form. The test runs a
  fake game on `{meeting_reset: "hub_with_grace", report_body_handle_version: 1}`.
  - A report meeting opened after a regroup names `body-p-N` without a kill
    tick, a button meeting names no body, and no prompt matches the pattern.
  - The implementer names the seed in Results. If no fake seed gives both
    meetings, build them through `apply_meeting_result` with
    `meeting_reset="hub_with_grace"` and then the builder.
  - Planted: the same game with the field `None` shows the legacy handle in the
    post-regroup report, so the reset alone does not close the leak.
- [ ] **End-to-end census conformance.** Mechanism: A1's opening-handle
  conformance cell (C31 in `census_and_record.md`; the flag computed in the
  loader so no text leaves it) and its arm predicate. The census folds the arm-ON
  recording through its write-nothing `--set-dir` path.
  - The cell reads 0. The OFF recording reads its count without raising.
  - Perturbed: a copy with one opening prompt given back its `body-p-N-T`
    handle raises the conformance guard.
  - B5's "kill-tick handle in an opening" STOP relies on this test.
- [ ] **The retirement rule is written down.** Mechanism: a scope note in
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

Not started. The worker fills this section with the architecture and design
sections referenced (`docs/architecture.md` "Observation timing and public
identities" and the spine's arm page, `docs/experiment-arms.md`), the decisions, every Validation
command with its real exit code, the seed used for the joint reset test, the
re-measured reach counts, and the limitations.
