# Move the fresh-model deduction instrument to the fourth authorization's limits

**Status:** ready

## Outcome

The instrument's authorized constants and the execution manifest's limits
table carry the fourth authorization's values — the raised turn cap and the
calibrated token ceilings — the feasibility gate accepts them, the Inputs
table binds the fourth held-out band, and a dated amendment records the
change before any unit of the fourth run exists. The frozen analysis does not
move.

## Evidence

[The fourth authorization](fresh-deduction-authorization-4.md) carries the
values with their basis: the live development calibration of 2026-09-14
(`audits/deduction-candidate/calibration-2026-09-14/calibration.json`) and the
near-cap candidate turn it recorded (2,036 output tokens against a 2,048 cap).
Today the instrument pins `AUTHORIZED_TURN_MAX_TOKENS = 2048`,
`AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS = 4000`, `AUTHORIZED_UNIT_MAX_INPUT_TOKENS =
45000`, `AUTHORIZED_RUN_MAX_INPUT_TOKENS = 2400000` and
`AUTHORIZED_RUN_MAX_OUTPUT_TOKENS = 200000`
(`experiments/fresh_deduction_instrument.py:205-210` and the sampling block
around `:389`), and `assert_limits_are_feasible` refuses them because one
unit's reservation schedule (`living_voters x (turn cap + vote cap)`,
`:463`) exceeds the per-unit output ceiling. The manifest's limits table
(`audits/deduction-candidate/execution-manifest.md`, "Sampling configuration,
caps and limits") quotes the constants and a test holds the two together; the
Inputs table binds band 6000-6999, which [the fourth freeze](held-out-prefix-freeze-4.md)
converts to development.

## Acceptance

- [ ] `AUTHORIZED_TURN_MAX_TOKENS` is 4,096, the vote cap stays 1,024, and the
  four token ceilings are 106,000 / 16,000 per unit and 3,710,000 / 459,000
  run-level, copied from the authorization card's Constraints table; the
  reservation schedule under the new caps is 15,360 and
  `assert_limits_are_feasible` accepts `AUTHORIZED_LIMITS` (a planted test
  with the old ceiling still goes red). The turn cap reaches the meeting
  layer's per-call `max_tokens` through the instrument's own sampling
  configuration, not through a default-path change; the default meeting
  path's recorded prompts and caps are unchanged (`verify_samples.sh`, the four
  `--check` runs).
- [ ] The manifest's limits table carries the same values verbatim with the
  authorization card named as their source, the reservation-policy text states
  the new schedule, and a dated section "Fourth authorization (2026-09-14)"
  records the change and its basis; the test that pins the table to the
  constants passes and the frozen analysis strings are byte-identical (test).
- [ ] After [the fourth freeze](held-out-prefix-freeze-4.md) is merged into
  this branch, the Inputs table binds band 7000-7999 (band, accepted range,
  skip count from the new `audits/deduction-candidate/held-out/manifest.json`),
  names all three converted bands as development data with their dates and
  their record paths, including
  `audits/deduction-candidate/held-out/manifest-band-6000-6999.json`, which
  this row binds until then, and
  `assert_manifest_binds_the_live_band` passes against the merged record.
- [ ] The replay-double rehearsal of the full pipeline under the new limits
  clears the feasibility gate and completes at $0, and Results records its
  aggregate counts only.
- [ ] Every new gate has a planted failure proving it detects the claimed
  defect.

## Constraints

No live provider call. The primary outcome, decision rule, minimum actionable
effect, tradeoff bound and stop rule do not change. The reservation policy of
the shared budgeted client does not change. Do not edit
`experiments/held_out_prefixes.py`; this card lands after
[the fourth freeze](held-out-prefix-freeze-4.md) and merges that branch in
before re-binding the Inputs table. If the turn cap can only reach the meeting
layer through `orchestrator/game.py`, stop and report rather than editing a
hashed default-path file. No band prefix is printed or opened; the rehearsal
writes to a temporary directory. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`audits/deduction-candidate/execution-manifest.md`, `docs/artifacts.md` (the
`audits/` row), `tasks/README.md`'s derived inventory sentence, this card.
Delivered on `work/fresh-deduction-limits-4`, stacked on
`work/held-out-prefix-freeze-4`, one pull request into `main`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section, a
re-bound Inputs table and new limit rows; no recording, report, DTO or weight
byte moves; no experiment becomes ON; no adopting record is created.

## Validation

`uv run pytest tests/experiments -q` (fake and replay providers only), then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, `bash scripts/verify_samples.sh`,
the four `uv run python scripts/build_sample_report.py --sample-dir <set>
--check` runs, and `bash scripts/check.sh`. Do not run the live evaluation as
a check.
