# Make the fresh-model deduction instrument's rehearsal see what the provider does

**Status:** done

## Outcome

Before any live call, the instrument can refuse limits it cannot honour, and
its rehearsal exercises the dimension that has actually bound: a usage
profile keyed by arm and call type taken from real archived calls, including
the two provider behaviours that stopped earlier attempts. A run stopped by an
environmental cause can be resumed from a per-unit checkpoint, outcome-blind,
once the owner authorizes that clause; the mechanism exists and is proved.

## Evidence

[The diagnosis of 2026-09-13](../diagnosis-2026-09-13-live-run-stops.md)
records the three stops and the root cause: the per-unit output ceiling was
sized on charged spend and enforced on reserved spend
(`llm/budgeted_client.py:259` reserves the full per-call cap; one unit's
schedule is `3 x 2,048 + 3 x 1,024 = 9,216` against a 4,000 ceiling), and no
pre-run surface could show it: `DryRunProvider` reports 66 output tokens per
call on both arms (`experiments/fresh_deduction_instrument.py`, its usage is
derived from the serialised payload's length), the manifest's headroom check
covers input only (`audits/deduction-candidate/execution-manifest.md:852-859`),
and the only mention of the output ceilings in the test module is a
constant-value assertion. The retry classifier's empty-completion markers
cover two of the four fail-loud shapes the client raises; "carried no usage
block" and "usage block omitted prompt_tokens / completion_tokens"
(`llm/featherless_client.py:844,850`) still re-raise bare, uncharged and
unretried. The 36 resolved live calls archived on the three run branches carry
real usage per call, and the archived refusals carry usage on a schema-refused
payload. No checkpoint or resume path exists although the decision memo named
a per-unit checkpoint as owed (`tasks/owner-decisions-2026-09-07.md`, B.4).

## Acceptance

- [x] Review correction: a stop that lands INSIDE a pair carries what it
  charged. The stop path writes one final checkpoint whose `AbandonedSpend`
  rows hold that pair's tokens, cost and model-work seconds per arm, and a
  resume charges them against the run ceilings and the clock beside the graded
  units (`TestCheckpointAndResume::test_a_stop_inside_a_unit_carries_its_spend`,
  `::test_the_abandoned_spend_is_charged_against_the_run_ceiling`,
  `::test_a_second_stop_carries_the_first_ones_abandoned_calls`).
- [x] Review correction: the claims that said so are now true rather than
  corrected away — `RunCheckpoint`'s docstring, the resume comment in
  `run_instrument` and the Results below all name the graded and the abandoned
  halves, and `charged_usage_by_arm` / `charged_model_work_seconds` are what the
  resume reads (`::test_a_stop_inside_a_unit_carries_its_spend` asserts the file
  accounts for every token the stopped run reported).
- [x] Review correction: a resume narrower than its checkpoint is refused by
  name instead of returning an empty tail and reporting units it did not run
  (`::test_a_resume_narrower_than_its_checkpoint_is_refused`, planted with
  `--units 1` against a two-unit checkpoint).
- [x] Review correction: a checkpoint file holding JSON that is not an object
  raises the named `ResumeNotAuthorized`, not an incidental `AttributeError`
  (`::test_a_file_that_is_not_a_checkpoint_is_refused`, three non-object
  plants).
- [x] Review correction: a resume into the stopped sitting's own output
  directory is refused before anything runs, naming the half-recorded replay,
  and the manifest states the fresh-directory rule
  (`::test_a_resume_into_the_stopped_sittings_directory_is_refused`,
  `TestExecutionManifest::test_the_manifest_states_what_a_second_sitting_must_do`).
- [x] Review correction: `--resume` implies `--checkpoint` at the same path, so
  a resumed sitting keeps advancing the file a third sitting would need
  (`::test_the_cli_takes_the_checkpoint_and_the_resume`, which now drives
  `--resume` end to end and asserts the checkpoint advanced).
- [x] Review correction: the arm-surface identity names the prompt loader and
  `orchestrator/game.py`, and says what the NAMED set covers instead of
  claiming every byte an arm renders through
  (`::test_the_named_arm_surface_carries_the_code_that_renders`,
  `::test_a_moved_arm_surface_byte_refuses_the_resume` over a template, the
  loader and the game module).
- [x] `assert_ready_for_a_live_run` gains a feasibility gate, pure arithmetic
  over module constants: it refuses a per-unit output ceiling below the
  reservation schedule one unit makes (turns x turn cap + living voters x vote
  cap, with the policy stated in the manifest) and run-level ceilings below the
  calibrated per-unit figure times the unit count; planted with attempt 3's
  numbers (4,000 against 9,216) it goes red, with feasible numbers green, and
  it runs before any credential or client exists.
- [x] A usage-replaying provider double, keyed by (arm, call type), seeded
  deterministically, samples response length and usage from a committed
  profile built from the 36 archived resolved calls on the run branches
  (recorded as aggregate rows: arm, call type, input tokens, output tokens;
  never a prompt or a prefix), with modes for a billed-and-refused payload
  carrying usage, an empty body, a no-usage body and a transport error. Under
  today's authorized limits the 100-unit rehearsal reproduces attempt 3's stop
  string; a call-type-blind sampler is shown to manufacture a false
  truncation, which is the regression the keying prevents.
- [x] The retry classifier covers every fail-loud empty-response shape the
  authorized client raises, enumerated from the client's own messages rather
  than typed, with a planted test per shape; an uncovered shape fails the
  enumeration test.
- [x] A per-unit checkpoint is written after every completed paired seed
  (arm results, usage, attempts, the manifest digest, the frozen-set digest
  and the instrument source digests), and `--resume <checkpoint>` continues
  at the next unrendered seed of the ascending list under the same manifest
  with the budgets carried; a resumed rehearsal produces a report identical to
  the uninterrupted one apart from the calls the stop itself abandoned, which
  the first correction above carries; and a planted change to any arm-surface
  byte, the manifest or the frozen set is refused. The live gate keeps refusing a resume
  until the manifest carries the owner's resumption clause (a test proves the
  refusal).
- [x] The manifest's "How each limit is enforced" section states the units of
  account explicitly (reserved versus charged), the reservation schedule per
  unit, and that the rehearsal's headroom check now covers output; a dated
  section "Amendments after the diagnosis of 2026-09-13" records the change.
  The frozen analysis strings are byte-identical (a test asserts it).
- [x] Every new gate has a planted failure proving it detects the claimed
  defect; the fake-provider and replay-double rehearsals run at $0 and Results
  records aggregate counts only.

## Constraints

No live provider call. No change to `llm/budgeted_client.py`'s reservation
policy (it serves every recorded campaign); the per-unit policy is stated and
gated, not altered. The primary outcome, decision rule, minimum actionable
effect and tradeoff bound do not change. Do not edit
`experiments/held_out_prefixes.py`. The usage profile carries token counts
only; no prompt, prefix or response text from the archives is committed. The
resume clause is not enabled for live runs by this card; the owner's
authorization card enables it. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/burned_call_double.py` (extend) or a sibling replay double,
a committed usage profile under `tests/experiments/` or `experiments/`
(aggregate rows only), `audits/deduction-candidate/execution-manifest.md`,
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived
inventory sentence, this card. Delivered on
`work/fresh-deduction-instrument-realism` and one pull request into `main`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section and
an enforcement clarification; adds a committed aggregate usage profile; no
recording, report, DTO or weight byte moves; no experiment becomes ON; no
adopting record is created; the three run archives are not touched.

## Validation

`uv run pytest tests/experiments -q` (fake and replay doubles only), then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.
Do not run the live evaluation as a check.

## Results

Delivered on `work/fresh-deduction-instrument-realism` in two commits: the
instrument, its doubles, the committed usage profile and the enforcement text
(`78b136bd`), then this record with the manifest's dated amendment, the
verification figures and the derived counts. No live provider call of any kind
was made; every figure below comes from the fake provider or the replay double,
at `total_cost_usd` 0.0.

### What was built, and against which sections

The contract is [the diagnosis of 2026-09-13](../diagnosis-2026-09-13-live-run-stops.md)
and the design it serves is
[the execution manifest](../../audits/deduction-candidate/execution-manifest.md):
"Sampling configuration, caps and limits" for the numbers, "How each limit is
enforced" for the mechanism, "The live gate" for what authorizes a call, and
"Verification of this manifest" for what a committed rehearsal measures.
`docs/architecture.md`'s determinism and observation-firewall rules are
untouched: nothing here imports `engine/` into `agents/`, no module-level
mutable state is added, and every new refusal is an explicit `raise`.

1. **The feasibility gate.** `assert_limits_are_feasible` compares the per-unit
   output ceiling against `unit_output_reservation()` (living voters x turn cap
   + living voters x vote cap = 9,216), the per-unit input ceiling against the
   largest unit the archives charged, and both run ceilings against a hundred
   units at that figure. It is arithmetic over module constants, runs first in
   `assert_ready_for_a_live_run` and again inside
   `assert_live_run_is_authorized`, and **refuses the limits merged on
   2026-09-07** — the live gate now fails closed until a fourth authorization
   card re-sizes them. `RESERVATION_POLICY` states the rule and the manifest
   quotes it verbatim.
2. **The usage-replaying double.** `tests/experiments/usage_replay_double.py`
   answers each call with the tokens the real endpoint reported for a call of
   that arm and that kind, out of
   `tests/experiments/deduction_usage_profile.json` — 38 rows (36 resolved calls
   and the 2 the provider billed and refused) and the 7 archived units' charged
   totals, carrying arm, call type, two token counts, attempt and disposition
   and nothing else. The arm is read off the prompt family's own structure and
   the call type off the schema; a prompt carrying neither family's marker
   raises rather than guessing.
3. **The retry classifier.** `_EMPTY_COMPLETION_MARKERS` now covers all four
   shapes `llm/featherless_client.py::_raw_from_response_body` raises. The test
   ENUMERATES that function's `raise` statements from its source rather than
   listing them, so a fifth refusal shape is red here instead of an unretried
   stop mid-run.
4. **The checkpoint and the resume.** `RunCheckpoint` is written after every
   completed paired seed — and once more where a stop lands, carrying the spend
   of the pair it interrupted (round-1 correction below) — with the graded
   units, their telemetry, the execution manifest's digest, the frozen set's
   digest and the digests of every arm-surface source (`ARM_SURFACE_SOURCES`
   plus every file of the prompt set). `--resume` continues at the next
   unrendered seed with the run budget and the model-work clock carried, into
   an output directory of its own. It is outcome-blind: `next_seeds_after`
   reads the seeds the file lists and the run order, and no stop condition
   anywhere reads a grade. A live resume is refused until the manifest carries the owner's
   `RESUMPTION_CLAUSE`, which it does not.

### Decisions

- **The gate refuses today's limits, and that is the deliverable.** Four
  committed tests that exercised gates BEHIND it now pass a stand-in re-sizing
  through `_authorize_feasible_limits`; the committed constants are unchanged
  and no test reaches a provider. The alternative — a gate that warns — would
  have left the third attempt's stop discoverable only live.
- **The run-level rule is calibrated, not a projection.** Run ceilings are held
  against a hundred units at the largest unit the archives charged (24,282 in /
  3,116 out) rather than against a mean. A mean projection is what sized the
  ceilings that stopped attempt 3; a ceiling is a stop rule and belongs above
  the largest thing measured.
- **The refusal is replayed, not planted.** Two of the candidate arm's nine
  archived turns were billed and refused, both as a unit's third turn, so the
  profile carries them in the bucket in that position. The rehearsal therefore
  reproduces the defaulted-turn rate as well as the token counts. The three
  no-completion classes stay planted, because those are provider faults rather
  than behaviours of the prompt.
- **The draw is a rotation, not a random sample.** Each bucket is consumed in
  its committed order from a seeded offset, so a run exercises the whole
  measured distribution and two runs of the same rehearsal draw the same calls.
- **The elapsed wall is per sitting.** A resumed run carries the token budgets
  and the model-work clock; the 8 h elapsed deadline bounds a process and
  restarts. The record reports the run's total elapsed across sittings.
- **`llm/budgeted_client.py` is untouched**, as the Constraints require. The
  reservation policy is stated and gated, never altered.

### Verification

Run on this branch's tree with the whole change in place. `78b136bd` carries
the behaviour; the record commit beside it moves this card, the manifest, the
derived counts and one docstring the amendment corrects. The planted
demonstrations below were applied to the same tree and reversed.

| Command | Result |
| --- | --- |
| `uv run pytest tests/experiments -q` | 337 passed |
| `bash scripts/check.sh` | exit 0 — ruff, ruff format, 4 import contracts kept, validate_task_docs (51 work cards), generate_prompts --check, mypy over 476 files, then 7,622 passed / 20 skipped / 3 xfailed in 445 s, then 515 frontend tests over 19 files and the build |
| `uv run python scripts/validate_task_docs.py` | ok |
| `uv run python scripts/check_doc_facts.py` | ok |
| `uv run python scripts/verify_ml_evidence.py` | 60 checks, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/verify_samples.sh` | exit 0 — 50 + 50 samples verified clean |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` over the four sets | each report is consistent with its replays |

The rehearsal's own figures, reproducible with
`uv run pytest tests/experiments/test_fresh_deduction_instrument.py -k "TestUsageReplay or TestFeasibility" -q`:

- **Under the authorized limits**, the 100-unit rehearsal stops where the live
  run stopped and says the same thing: `LLM budget exceeded on output_tokens:
  current=3116.0 + delta=1024.0 > cap=4000.0`, candidate arm, 5 of 100 units
  completed. The 3,116 is the archived unit's own, because the rehearsal
  replays that unit's calls including the turn the provider billed and refused.
- **Under the re-sizing the diagnosis proposes**, all 100 units and 600 calls
  run at $0.00: `repaired_clock` 1,072,642 in / 66,105 out (21,453 and 1,322 a
  unit), `combined_accounts` 1,015,417 / 145,889 (20,308 and 2,918 a unit). The
  run total of 211,994 output tokens is 106.0% of the 200,000 run-level ceiling
  this manifest binds — the diagnosis projected 101%-111% from four units; this
  measures it over a hundred. Input is 87.0% of its ceiling. The candidate arm
  replays its archived refusal rate as 33 defaulted turns across 150, against
  none on the reference arm. A test asserts every one of these figures equals
  the manifest's, so the record cannot drift from the run that produced it.

Nothing graded in either rehearsal is evidence about the arms, and none of it
is reported as such: the double's decision does not depend on the arm and the
replayed refusals are the candidate arm's by construction.

### Planted failures

Each was applied, run and reversed on this tree.

| Planted defect | Command | Result |
| --- | --- | --- |
| `_EMPTY_COMPLETION_MARKERS` back to its two pre-card entries | `pytest -k TestEmptyResponseShapes` | 3 failed, 4 passed — the enumeration and both usage-block shapes |
| the per-unit reservation comparison removed | `pytest -k TestFeasibility` | 1 failed, 9 passed — the refusal became the run-level one instead |
| `assert_resume_is_authorized` returning unconditionally | `pytest -k "live_resume or readiness_gate_refuses"` | 2 failed |
| the arm-surface comparison removed from `assert_checkpoint_matches` | `pytest -k moved_arm_surface` | 1 failed |
| the archived refusal not replayed | `pytest -k "reproduces_the_stop or archived_refusal"` | 1 failed, 1 passed — the defaulted turn disappears; the stop string is unaffected, because the same tokens are charged either way |
| the default draw made call-type-blind | `pytest -k TestUsageReplay` | 2 failed, 9 passed — the blind sampler manufactures a 1,045-token ballot against a 1,024 cap |

Two committed cases carry their plant permanently rather than as a
demonstration: `CallTypeBlindReplayProvider` (the truncation a pooled sampler
manufactures) and `test_an_uncovered_wording_is_not_classified` (a fifth
refusal wording the marker tuple does not carry).

### Record impact and limitations

The `audits/` row of `docs/artifacts.md` moves with the manifest: 206 files /
14,978,051 bytes before this card, 206 files / 14,990,456 bytes after it,
recomputed with `git ls-files audits/` and the change staged. (The figure
`78b136bd` alone produced, 14,988,404, is superseded: the round-1 corrections
below amend the manifest a second time.) The held-out freeze manifest is
untouched — no file it hashes moved, so no restamp was needed, and no prefix
was printed, opened or committed. No recording, report, DTO or weight byte
moves; no experiment becomes ON; the three run archives are not touched.

Limitations:

- **The profile is 38 calls over seven units, from three stopped runs on two
  days.** It is the largest live sample this evaluation has; it is not a
  distribution. The calibrated output figure comes from an incomplete unit
  (3,116 over four of six calls), so it is a floor rather than a measurement,
  and the constant's own comment says so.
- **The rehearsal replays counts, not text.** A real response's bytes render a
  held-out prefix and are not committed, so the double's payloads remain the
  mechanics fixture's. It can therefore say what a unit would SPEND and nothing
  about what a model would say.
- **The resume is built, not authorized.** The live gate refuses it and this
  card does not enable it; the clause is the owner's, and the elapsed wall's
  per-sitting behaviour is part of what that decision has to settle.
- **The feasibility gate leaves the run unrunnable.** That is the intended
  state: no live run can start until the fourth authorization re-sizes the
  limits from a calibration the owner authorizes.

### Review corrections, round 1 (2026-09-14)

Seven blocking findings from two independent lenses, all valid, all repaired on
this branch. Six of them are one mechanism — the resume — and the seventh is the
identity that mechanism compares two sittings on. Nothing above is retracted
except the `audits/` byte count, which this round's second manifest amendment
moves and Record impact restates: the feasibility gate, the usage profile and
the retry enumeration are unchanged, and no constant, limit or frozen string
moved. Still no live provider call of
any kind, and every figure below is the fake provider or the replay double at
`total_cost_usd` 0.0.

**1-2. A stop inside a pair used to forget what it had charged.** The checkpoint
is written at PAIR boundaries, so the calls a stop makes after the last boundary
belong to no unit row. The stop path deliberately charges them into the partial
accounting, and unit budgets are children of the run budget, so they were
already spent against the run ceilings — but the next sitting rebuilt its budget
from the file and never saw them. Both lenses reproduced it the same way, and so
does this branch: a four-unit replay rehearsal stopped by transport exhaustion
on its 28th call, i.e. mid-unit, really spent `repaired_clock` 51,815 in /
3,579 out over 19 calls while the checkpoint accounted for 40,970 / 2,294 over
12 — 10,845 input and 1,285 output tokens forgiven per stop, unboundedly often,
because nothing bounds how many times a transport may drop.

The repair is to record them rather than to document the gap. `AbandonedSpend`
is a new checkpoint field holding, per arm, the tokens, cost, model-work seconds
and retry counts of the pair a stop interrupted; `run_instrument` writes one
final checkpoint on the stop path to carry it, and a resume charges
`charged_usage_by_arm()` (graded plus abandoned) into the run budget and
`charged_model_work_seconds()` into the clock before its first call. It
accumulates, so a run stopped twice charges both stops. On the same rehearsal
the checkpoint now accounts for the stopped sitting's spend exactly — 51,815 /
3,579 charged, of which 40,970 / 2,294 graded — and the resumed report's
per-arm totals are the uninterrupted run's plus exactly the abandoned rows
(`repaired_clock` 85,186 / 5,310 over 24 calls uninterrupted, 96,031 / 6,595
over 31 resumed; `combined_accounts` identical at 78,435 / 11,154). Every
figure in this paragraph is asserted by
`::test_a_stop_inside_a_unit_carries_its_spend`, so the record cannot drift
from the rehearsal that produced it; reproduce them with `uv run pytest
tests/experiments/test_fresh_deduction_instrument.py -k
test_a_stop_inside_a_unit_carries_its_spend -q`. The comment and the
`RunCheckpoint` docstring that claimed the carry now describe it, and
`usage_by_arm()` says in its own docstring that it is the graded half alone.

**3. A resume narrower than its checkpoint reported units it had not run.**
`next_seeds_after` computed the finished prefix over the TRUNCATED prefix list,
so a completed seed outside it was ignored rather than refused: `run_dry(units=2,
checkpoint_path=...)` then `run_dry(units=1, resume=...)` returned two units an
arm for a one-unit request, with no tail run and no refusal. It now refuses any
seed the checkpoint carries that this run would not draw, naming the extras.

**4. A checkpoint file that was not a JSON object raised `AttributeError`.**
The guard short-circuited on `not isinstance(loaded, dict)` and then formatted
the refusal with `loaded.get(...)`, so `[]` or `"hello"` reached an incidental
exception where AGENTS.md requires a named one. The schema is bound before the
raise.

**5. A resume into the stopped sitting's directory aborted on the partial
replay.** A mid-unit stop leaves that seed's half-written JSONL behind, so a
second sitting pointed at the same `--output-dir` reached the recorder's
`AlreadyExistsError` — after the resume gates passed and, live, after the tail
had begun to spend. `assert_the_tail_can_be_recorded` refuses first, names the
file, and says a resumed sitting writes into a fresh directory; the manifest
says so too.

**6. A resumed sitting wrote no checkpoint unless `--checkpoint` was repeated.**
The CLI passed `args.checkpoint` on both paths, so `--resume cp.json` alone
advanced nothing and a third sitting would have re-spent held-out calls already
bought. `--checkpoint` now defaults to the `--resume` path, and the CLI test
drives the flag combination end to end instead of only writing a checkpoint.

**7. The arm-surface identity omitted the code that renders the prompts.**
`agents/strategic/prompts/loader.py` builds the Jinja environment and selects
the renderers and was in neither the named set nor the freeze's comparison;
`orchestrator/game.py` was in the freeze's `source_sha256` block, which
`verify_frozen_set` deliberately does not re-compare. Both are now in
`ARM_SURFACE_SOURCES` (7 named files, 20 entries in the mapping with the 13
prompt files), and the docstring no longer says "every byte an arm renders
through": it says the set is NAMED and points at where the rest of the run path
is covered — the held-out manifest's digest, its `source_sha256` block and the
freeze test, and `_one_prompt_version_set` at report-build time.

#### Verification of the corrections

Run on this branch's tree with the whole change in place.

| Command | Result |
| --- | --- |
| `uv run pytest tests/experiments -q` | 346 passed (337 at `78b136bd`, which this round adds nine cases to) |
| `bash scripts/check.sh` | exit 0 — ruff, ruff format over 505 files, 4 import contracts kept, validate_task_docs (51 work cards), generate_prompts --check, mypy over 476 files, then 7,631 passed / 20 skipped / 3 xfailed, then 515 frontend tests over 19 files and the build |
| `uv run python scripts/validate_task_docs.py` | ok |
| `uv run python scripts/check_doc_facts.py` | ok |
| `uv run python scripts/verify_ml_evidence.py` | 60 checks, OK 48, FAIL 0, ABSENT 7, INFO 5 |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/verify_samples.sh` | exit 0 |
| `uv run python scripts/build_sample_report.py --sample-dir <set> --check` over the four sets | each report is consistent with its replays |

Each repair carries a planted proof, applied to this tree and reversed
(`pytest tests/experiments/test_fresh_deduction_instrument.py -k <selector>`):

| Planted defect | Selector | Result |
| --- | --- | --- |
| the resume charges only `usage_by_arm()` and `model_work_seconds` | `carries_its_spend or charged_against_the_run_ceiling or second_stop_carries` | 2 failed, 1 passed |
| the stop path writes no final checkpoint | same selector | 3 failed |
| the out-of-list seed refusal removed from `next_seeds_after` | `narrower_than_its_checkpoint` | 1 failed |
| `schema_version` read off the payload before the shape check | `not_a_checkpoint_is_refused` | 1 failed |
| the output-directory check removed from the resume path | `stopped_sittings_directory` | 1 failed |
| `--checkpoint` no longer defaulting to `--resume` | `cli_takes_the_checkpoint_and_the_resume` | 1 failed |
| the loader and the game module removed from `ARM_SURFACE_SOURCES` | `named_arm_surface_carries or moved_arm_surface_byte` | 3 failed, 1 passed |

#### What these corrections do not change

The live gate still fails closed under the limits merged on 2026-09-07, the
resume is still refused on a live provider until the manifest carries the
owner's clause, and the elapsed wall is still per sitting. One limitation is
sharper than it was: a resumed run's per-arm `calls`, `input_tokens` and
`output_tokens` now include the calls its stops abandoned, so a report of a
resumed run says what the RUN spent rather than what its graded units cost. That
is the honest reading of a ceiling that bounds spending, and the checkpoint
names the difference so either figure can be recovered.
