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

- [ ] A `--calibrate` mode: it accepts only a freeze record whose `status` is
  `development` and whose band is in `CONVERTED_BANDS`, takes the first
  `CALIBRATION_PAIRED_SEEDS = 5` accepted seeds ascending, rebuilds each prefix
  with the unchanged generator and refuses on any digest mismatch against the
  record, runs both arms per seed sequentially through the same public-API
  path as the evaluation, and never touches the held-out record at
  `MANIFEST_PATH`. A held-out record, a live provider without the runner flag,
  or a manifest without the dated calibration clause is refused, each with a
  planted test.
- [ ] Calibration limits, distinct from `AUTHORIZED_LIMITS` and feasible under
  the gate: per unit 60,000 input / 12,000 output, run 600,000 input / 120,000
  output, 1 h of model work within 1.5 h elapsed, the merged per-call caps and
  transport bound unchanged; the feasibility gate runs on them; the frozen
  analysis is not evaluated (no grader, no McNemar) and the report says so.
- [ ] The calibration writes aggregates only: per arm and per call type (turn,
  ballot) the count, mean, p95 and max of input and output tokens; refusals,
  defaults and charged failed attempts per arm; retried and unaccounted
  attempts; pace per attempt; and a re-sized-ceiling proposal computed by a
  stated rule (per-unit output = max(reservation schedule, 3 x measured
  maximum unit), run ceilings = 100 units x measured mean x 1.5, rounded up),
  as a committed JSON under `audits/deduction-candidate/calibration-<date>/`.
  Rendered prompts and prefixes are development data but are not committed;
  per-unit usage rows are.
- [ ] The replay double's committed profile can be refreshed from a
  calibration output by a documented command, and the rehearsal on the
  refreshed profile passes the feasibility gate under the proposed ceilings.
- [ ] The execution manifest gains a dated "Development calibration
  (2026-09-14)" section stating the mode, its inputs, its limits and the
  owner's approval, and a dated "Resumption clause (2026-09-14)" section
  quoting `RESUMPTION_CLAUSE` verbatim: a run stopped by transport exhaustion,
  a credential failure or a process crash may be resumed once per stop from
  its last checkpoint under the same manifest, with the interrupted unit's
  spend and model-work time carried; a stop by a limit, a truncation, a
  digest or provenance mismatch, or the legacy body handle is final. The
  frozen analysis strings stay byte-identical (test).
- [ ] Every new gate has a planted failure; the fake-provider and replay-double
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
