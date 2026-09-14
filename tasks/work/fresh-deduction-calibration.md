# Calibrate the fresh-model deduction instrument on development inputs

**Status:** active

## Outcome

The instrument can run a bounded live calibration on development inputs — the
first five accepted seeds of the converted 3000-3999 band, both arms, about
sixty calls — under its own small limits, and writes only aggregate outputs:
the measured per-arm, per-call-type token profile, the refusal and default
rates on the corrected prompts, and the pace. That profile replaces the
projection the fourth authorization's ceilings are sized from and refreshes the
replay double's committed profile. The execution manifest carries the owner's
resumption clause, so a run stopped by an environmental cause can resume from
its checkpoint with its spend carried.

## Evidence

[The diagnosis of 2026-09-13](../diagnosis-2026-09-13-live-run-stops.md)
names the one step that closes the root for provider behaviour not yet seen: a
live calibration on development inputs, which #437 forbade
(`tasks/work/fresh-deduction-authorization.md:159-160`). On 2026-09-14, in the
coordinator's session, the owner approved all three decisions the diagnosis
lists — the bounded calibration, the resumption clause and re-sized ceilings —
and instructed their execution in that order; this card is the record of the
first two. The converted record
`audits/deduction-candidate/held-out/manifest-band-3000-3999.json` is
development data (status `development`, fifty accepted seeds from 3000, each
with its digest), so rendering five of them to the model converts nothing
further. The instrument already refuses limits below a unit's reservation
schedule (`assert_limits_are_feasible`, merged in #453), refuses a live run
whose provider is not the authorized one, carries a per-unit checkpoint and a
`--resume` path refused until the manifest quotes `RESUMPTION_CLAUSE`
(`experiments/fresh_deduction_instrument.py:1158-1180`), and replays usage from
`tests/experiments/deduction_usage_profile.json`, built from 38 archived calls.

## Acceptance

- [x] A `--calibrate` mode: it accepts only a freeze record whose `status` is
  `development` and whose band is in `CONVERTED_BANDS`, takes the first
  `CALIBRATION_PAIRED_SEEDS = 5` accepted seeds ascending, rebuilds each prefix
  with the unchanged generator and refuses on any digest mismatch against the
  record, runs both arms per seed sequentially through the same public-API
  path as the evaluation, and never touches the held-out record at
  `MANIFEST_PATH`. A held-out record, a live provider without the runner flag,
  or a manifest without the dated calibration clause is refused, each with a
  planted test.
- [x] Calibration limits, distinct from `AUTHORIZED_LIMITS` and feasible under
  the gate: per unit 60,000 input / 12,000 output, run 600,000 input / 120,000
  output, 1 h of model work within 1.5 h elapsed, the merged per-call caps and
  transport bound unchanged; the feasibility gate runs on them; the frozen
  analysis is not evaluated (no grader, no McNemar) and the report says so.
- [x] The calibration writes aggregates only: per arm and per call type (turn,
  ballot) the count, mean, p95 and max of input and output tokens; refusals,
  defaults and charged failed attempts per arm; retried and unaccounted
  attempts; pace per attempt; and a re-sized-ceiling proposal computed by a
  stated rule (per-unit output = max(reservation schedule, 3 x measured
  maximum unit), run ceilings = 100 units x measured mean x 1.5, rounded up),
  as a committed JSON under `audits/deduction-candidate/calibration-<date>/`.
  Rendered prompts and prefixes are development data but are not committed;
  per-unit usage rows are.
- [x] The replay double's committed profile can be refreshed from a
  calibration output by a documented command, and the rehearsal on the
  refreshed profile passes the feasibility gate under the proposed ceilings.
- [x] The execution manifest gains a dated "Development calibration
  (2026-09-14)" section stating the mode, its inputs, its limits and the
  owner's approval, and a dated "Resumption clause (2026-09-14)" section
  quoting `RESUMPTION_CLAUSE` verbatim: a run stopped by transport exhaustion,
  a credential failure or a process crash may be resumed once per stop from
  its last checkpoint under the same manifest, with the interrupted unit's
  spend and model-work time carried; a stop by a limit, a truncation, a
  digest or provenance mismatch, or the legacy body handle is final. The
  frozen analysis strings stay byte-identical (test).
- [x] Every new gate has a planted failure; the fake-provider and replay-double
  calibrations run at $0 and Results records aggregate counts only.
- [ ] The live calibration itself is run by a separate runner session
  dispatched on this card after the code merges; its Results subsection
  records the measured profile, the proposal, actual usage against the
  calibration limits and $0.00 marginal cost, and the archive path.

## Constraints

The live calibration is the only live call this card authorizes: at most
`CALIBRATION_PAIRED_SEEDS` paired seeds from the converted 3000-3999 record,
within the calibration limits, once; no retry of the calibration beyond the
instrument's own transport bound; no held-out band is read, rendered or
converted. The primary outcome, decision rule, minimum actionable effect and
tradeoff bound do not change. The reservation policy of the shared budgeted
client does not change. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row. The runner of the calibration is not the
implementer of this card.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/usage_replay_double.py` and
`tests/experiments/deduction_usage_profile.json` (refresh path),
`audits/deduction-candidate/execution-manifest.md`,
`audits/deduction-candidate/calibration-<date>/` (the run's outputs),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card. Delivered on `work/fresh-deduction-calibration` and one
pull request into `main`; the calibration run lands on
`work/fresh-deduction-calibration-run` and a second pull request.

## Record impact

Adds a calibration mode and two dated manifest sections; adds a measurement
record under `audits/` when the calibration runs; no recording, report, DTO or
weight byte moves; no experiment becomes ON; no adopting record is created; the
held-out record at `MANIFEST_PATH` is untouched.

## Validation

`uv run pytest tests/experiments -q` (fake and replay doubles only), then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`. The
live calibration is not a check and runs only on the runner session's card
instructions.

## Results

Acceptance items 1 to 6 are implemented and verified offline on this branch.
Item 7 is the live calibration itself, which a separate runner session runs on
this card after the code merges (Constraints: "The runner of the calibration is
not the implementer of this card"), so the card stays `active` and the task
index's inventory sentence is unchanged.

### What was built, and where it sits in the design

The instrument gains a SECOND mode beside the evaluation, not a relaxation of
it. `docs/architecture.md` "Enforced boundaries" and "Explicit cleanup
experiments" are the sections it lives under: the calibration drives the same
public entry points through `run_unit`, under the same
`orchestrator/experiment_config.py` arms, and adds no import that
`.importlinter` would have to be told about. The preregistration's separation of
held-out inputs from development ones
(`audits/deduction-candidate/preregistration.md`) is what makes the mode
possible at all, and the manifest's two new dated sections are where the owner's
decisions of 2026-09-14 are recorded.

The two modes share the run path and share no authorization:

| | Evaluation | Calibration |
| --- | --- | --- |
| Inputs | `verify_frozen_set` over the held-out record | `verify_calibration_set` over a `CONVERTED_BANDS` record |
| Limits | `AUTHORIZED_LIMITS` (100 units) | `CALIBRATION_LIMITS` (10 units) |
| Gate | `assert_live_run_is_authorized` | `assert_calibration_is_authorized` |
| Manifest clause | the band binding and the run's own rows | `CALIBRATION_CLAUSE` |
| Grading | three graders, McNemar, primary outcome | none |

Each gate refuses the other's limits, and a `CalibrationSet` is a different type
from a `FrozenSet`, so neither can be handed to the other's path by a later
edit. `build_authorized_client` accepts either and requires one, which is what
keeps "the inputs are verified before a credential exists" a property of the
signatures rather than of the order of two lines.

### Decisions

1. **A separate `run_calibration` rather than a flag on `run_instrument`.** A
   parameter that swapped the input set would have put the held-out record one
   boolean away from a development path. The two functions share
   `_build_harness` (one wiring of the client wrapper, the run budget and the
   two clocks) and `run_unit`, so what is measured is what the run spends.
2. **The proposal is raised to the floor the feasibility gate enforces.** The
   card's rule — run ceiling = 100 units x measured mean x 1.5 — falls below
   `units x largest measured unit` whenever the maximum exceeds 1.5x the mean,
   which is the case on the archived distribution (max 3,381 output against a
   2,065 mean). A proposal the instrument itself would refuse is not a
   proposal, so `ceiling_proposal` takes the larger of the two and
   `CEILING_PROPOSAL_RULE` says so in every committed output. This is the one
   place the implementation adds to the rule the card states; it adds a floor
   and never a reduction.
3. **The per-unit INPUT ceiling takes the same 3x multiple.** The card's rule
   fixes the output half against the reservation schedule; nothing reserves an
   input cap, so the input half is 3x the largest measured unit with no floor,
   stated in the rule string rather than left to a reader.
4. **Per-call token counts are committed, per-call text is not.** The refresh in
   item 4 replays individual calls keyed by (arm, call type), so a bucket
   collapsed to its mean would hand a 1,024-capped ballot a turn's length — the
   regression `CallTypeBlindReplayProvider` exists to prevent. The output's
   `calls` rows therefore carry four counts each, the same field set the
   committed profile is already pinned to; no prompt, prefix, step or outcome
   appears in either.
5. **`CapturedCall` records its disposition.** Two of the ledger's four row
   kinds carry a marker for a model and two carry the served one, so a summary
   could not otherwise tell a billed-and-refused completion from a resolved one.
   The field defaults to `resolved`, so no existing reader moves.
6. **No outcome in the calibration's output.** Meeting outcomes on development
   inputs are how a development set becomes a training set; the mode measures
   cost, and `test_the_report_grades_nothing` scans the payload for the words
   rather than trusting the intention.
7. **"Once per stop" and the final-stop list are recorded as the runner's
   discipline.** A checkpoint records no stop class, so no code refuses a second
   resume; the manifest states which half of the clause the code enforces (the
   carried spend, by `AbandonedSpend`) and which half is the runner's. Claiming
   the refusal in the document would have been the worse error.

### Verification

All on this branch, offline, with the fake provider and the replay double; no
provider was reached and nothing was spent.

- `uv run pytest tests/experiments -q` — **378 passed** (348 before this card):
  28 new across `TestCalibrationInputs`, `TestCalibrationGate`,
  `TestCalibrationRun` and `TestCalibrationProfileRefresh`, and two more in
  `TestExecutionManifest`, where the one test that asserted the manifest did
  NOT carry the resumption clause became three that hold both clauses and the
  calibration's own limits to the document.
- `uv run python scripts/validate_task_docs.py` — passed.
- `uv run python scripts/check_doc_facts.py` — passed.
- `uv run python scripts/verify_ml_evidence.py` — `checks: 60 | OK 48 | FAIL 0 |
  ABSENT 7 | INFO 5`; the seven absences are the evidence branch a fresh clone
  does not carry.
- `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` — 80 passed.
- `bash scripts/check.sh` — passed (exit 0).
- `bash scripts/verify_samples.sh` and the four
  `scripts/build_sample_report.py --sample-dir <set> --check` runs — passed.

**The fake-provider calibration**, the mechanics check at $0:

```sh
uv run python -m experiments.fresh_deduction_instrument --calibrate --json calibration.json
```

writes 10 units (5 paired seeds x 2 arms), 60 completions and 10 unit rows at
`total_cost_usd 0.0`, drawing seeds 3000-3004 of
`audits/deduction-candidate/held-out/manifest-band-3000-3999.json` (status
`development`). Per arm both call schedules complete 15 of 15, with no default,
no charged failed attempt, no retry and no unaccounted attempt. Its proposal
reports `clears_the_feasibility_gate false`, which is correct and is the point:
`DryRunProvider` derives its usage from the length of the payload it serialises
(73 output tokens a turn), so a proposal computed from it is not a measurement,
and the output says so in the gate's own words.

**The replay-double calibration**, the same mode over the usage the real
endpoint reported (`tests/experiments/deduction_usage_profile.json`, 38 archived
calls):

| Arm | attempts | input | output | largest unit out | charged failed | defaulted turns |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 30 | 106,392 | 6,426 | 1,602 | 0 | 0 |
| `combined_accounts` | 30 | 100,209 | 14,221 | 3,381 | 3 | 3 |

with the two schedules kept apart — candidate turns mean 796.6 / p95 1,455 / max
1,455 output against a 2,048 cap, candidate ballots mean 151.5 / p95 223 / max
223 against a 1,024 cap — which is the asymmetry a pooled summary would erase.
Its proposal is per unit 73,000 input / 11,000 output and run-level 3,100,000 /
339,000, `clears_the_feasibility_gate true`. Reproduce with:

```sh
uv run python -c "
import tempfile
from pathlib import Path
import experiments.fresh_deduction_instrument as i
from tests.experiments.usage_replay_double import UsageReplayProvider
record = Path('audits/deduction-candidate/held-out/manifest-band-3000-3999.json')
with tempfile.TemporaryDirectory() as d:
    r = i.run_calibration(record, output_dir=Path(d), client=UsageReplayProvider())
for a in r.arms:
    print(a.arm, a.attempts, a.input_tokens, a.output_tokens,
          a.max_unit_output_tokens, a.charged_failed_attempts, a.defaulted_turns)
print(r.proposal.unit_max_input_tokens, r.proposal.unit_max_output_tokens,
      r.proposal.run_max_input_tokens, r.proposal.run_max_output_tokens,
      r.proposal.clears_the_feasibility_gate)
"
```

**The refresh path** (item 4) is
`test_the_rehearsal_on_a_refreshed_profile_runs_under_the_proposal`: it
measures, writes a profile with `--refresh-usage-profile`, then rehearses the
whole 100-unit design on that refreshed profile under
`proposed_limits(report.proposal)`. Both arms complete all fifty of their units
at `total_cost_usd 0.0`, and `assert_limits_are_feasible` accepts the proposal
for the full run.

### Planted failures

Each gate was removed or perturbed on this tree, the test that names it was run,
and the tree was restored.

1. **The held-out refusal.** `if resolved == held_out:` becomes `if False:` in
   `_converted_band_for`; `pytest -k held_out_record_is_refused_by_name` →
   `FAILED ... assert 'HELD-OUT' in ...`. The layer under it — the
   converted-path allow-list — still refuses the same call, so what the plant
   removes is the refusal that names the mistake rather than the protection.
2. **The digest comparison.** `if rebuilt != digest:` becomes `if False:`;
   `pytest -k moved_digest_is_refused_by_seed` → `Failed: DID NOT RAISE <class
   '...CalibrationInputsRejected'>`.
3. **The calibration clause.** `if CALIBRATION_CLAUSE not in text:` becomes `if
   False:`; `pytest -k manifest_without_the_clause_refuses_it` → `Failed: DID
   NOT RAISE <class '...LiveRunNotAuthorized'>`.
4. **The limits comparison.** `if limits != CALIBRATION_LIMITS:` becomes `if
   False:`; `pytest -k refuse_each_others_limits` → `FAILED ...
   LimitsInfeasible: the per-unit output ceiling is 4,000 tokens and one unit
   reserves 9,216`. The held-out run's ceilings reach the arithmetic instead of
   the authorization — a refusal for the wrong reason, and the test says so.
5. **The quoted clause.** One comma deleted from the manifest's quotation of
   `RESUMPTION_CLAUSE`; `pytest -k "two_clauses_of_2026_09_14_verbatim or
   live_resume_is_authorized_by_the_document"` → both FAILED, the second with
   `ResumeNotAuthorized: ... carries no resumption clause`. The gate reads
   bytes, and the test is what keeps the document's copy and the module's
   identical.

Two further plants live in the suite and cover the mode's inputs and its
ordering: `test_the_calibration_never_reads_the_held_out_record` mines
`verify_frozen_set` and requires the calibration to complete, and
`test_the_readiness_gate_verifies_the_inputs_after_the_arithmetic` mines
`verify_calibration_set` and requires the authorization to refuse first.

### Record impact and limitations

`audits/deduction-candidate/execution-manifest.md` is the only `audits/` byte
that moves. The `docs/artifacts.md` row is recomputed from the tracked `audits/`
inventory with the change staged: 14,992,123 → **15,001,060 tracked bytes / 206
files**, the file count unchanged, and `scripts/verify_ml_evidence.py` and
`tests/scripts/test_verify_ml_evidence.py` both pass on it. No recording,
report, DTO or weight byte moves; no experiment becomes ON; the held-out record
at `MANIFEST_PATH` is untouched; and the frozen analysis strings are the same
bytes the manifest already quoted
(`test_the_manifest_quotes_the_frozen_analysis` and the amendment walk in
`TestExecutionManifest` hold that against the history).

Limitations, stated rather than implied:

- **No live measurement exists yet.** Every number above is the fake provider's
  serialisation length or the archived profile's replay. Replacing exactly those
  with measured ones is what the calibration is for, and until the runner
  session runs it the ceilings a fourth authorization would carry are still
  sized on seven archived units.
- **The proposal authorizes nothing.** It is arithmetic in a committed record; a
  ceiling is the owner's, on a card, and `assert_live_run_is_authorized` keeps
  refusing anything but the limits it is handed.
- **"Once per stop" is not enforced in code** (decision 7): a checkpoint records
  no stop class, so a second resume after the same stop, or a resume after a
  limit stop, is refused by the runner reading the clause and not by the
  instrument.
- **`tests/experiments/deduction_usage_profile.json` is unchanged.** Refreshing
  it is the runner's step on the live output, and it moves
  `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` with it —
  `test_the_calibration_is_the_largest_unit_the_archives_charged` is where a
  refresh that forgot them goes red.
- **A calibration has no resume.** Ten units inside a ninety-minute window are
  re-run rather than continued, which spends development data the evaluation is
  not holding in reserve.
