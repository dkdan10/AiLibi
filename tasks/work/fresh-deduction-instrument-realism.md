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
  the uninterrupted one, and a planted change to any arm-surface byte, the
  manifest or the frozen set is refused. The live gate keeps refusing a resume
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
   completed paired seed with the graded units, their telemetry, the execution
   manifest's digest, the frozen set's digest and the digests of every
   arm-surface source (`ARM_SURFACE_SOURCES` plus every file of the prompt set).
   `--resume` continues at the next unrendered seed with the run budget and the
   model-work clock carried. It is outcome-blind: `next_seeds_after` reads the
   completed seeds and the run order, and no stop condition anywhere reads a
   grade. A live resume is refused until the manifest carries the owner's
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
14,978,051 bytes before, 206 files / 14,988,404 bytes after, recomputed with
`git ls-files audits/` and the change staged. The held-out freeze manifest is
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
