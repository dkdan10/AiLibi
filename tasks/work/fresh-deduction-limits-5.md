# Move the fresh-model deduction instrument to the fifth authorization's limits

**Status:** ready

## Outcome

The instrument's authorized constants and the execution manifest's limits table
carry the fifth authorization's values, the committed usage profile becomes the
second calibration's, the feasibility gate accepts the new ceilings on it, the
Inputs table binds the fifth held-out band, and a dated amendment records the
change. The frozen analysis does not move, and the calibration-2 card closes.

## Evidence

[The fifth authorization](fresh-deduction-authorization-5.md) carries the
values with their basis: the second live development calibration of
2026-09-15 (`audits/deduction-candidate/calibration-2-2026-09-15/`). One
sitting, 120 units and 720 calls on development inputs, $0.00 marginal:

| Measured, candidate arm unless noted | Value |
| --- | --- |
| ballot output tokens | mean 93.3, max 135 against the 1,024 cap |
| turn output tokens | mean 443.0, max 1,884 against the 4,096 cap |
| per-unit tokens | mean 22,733.8 input / 1,608.9 output |
| largest unit charged | 38,440 input / 4,176 output |
| truncations, impostor ballots | 0 of 60, Wilson 95% upper 6.02% |
| defaults, charged failed attempts, retries | 0, 0, 0 |
| pace, pooled over 720 attempts | 10.28 s per attempt |
| role leak, self-tell (reference) | 1 of 60 units (0); 39 of 60 ballots (9) |

`CEILING_PROPOSAL_RULE` (`experiments/fresh_deduction_instrument.py:6008`,
computed by `ceiling_proposal`, `:6881`) sizes the proposal off those maxima,
with the in-flight headroom term on output: per unit 116,000 input
(3 x 38,440) and 16,000 output (15,360, the schedule `unit_output_reservation`
returns at `:572`, rounded up); run-level 3,844,000 input (100 x 38,440) and
422,000 output (100 x 4,176 + 4,096 = 421,696, rounded up).

Today the instrument pins the run ceilings at 3,710,000 / 459,000 (`:230-231`),
the per-unit ones at 106,000 / 16,000 (`:241-242`), the turn cap at 4,096 and
the vote cap at 1,024 (`:206-207`, `meetings/manager.py:212`), and
`CALIBRATED_UNIT_INPUT_TOKENS` / `CALIBRATED_UNIT_OUTPUT_TOKENS` at the three
stopped runs' 24,282 / 3,116 (`:547-548`). `assert_limits_are_feasible`
(`:1273`) reads those last two from module scope at call time, so refreshing
`tests/experiments/deduction_usage_profile.json` moves what every standing
ceiling is checked against, and the runner committed neither: on the refreshed
profile the gate REFUSES `AUTHORIZED_LIMITS` (`:326`) on run input (3,710,000
against 3,844,000) and `CALIBRATION_2_LIMITS` (`:504`) for 120 units, whose run
ceilings fall short on both dimensions (4,500,000 against 4,612,800 input;
450,000 against 505,216 output). That is why item 8 of
[the second calibration card](fresh-deduction-calibration-2.md) is unchecked and
that card is still `active`.

Section 9 of [the diagnosis](../diagnosis-2026-09-15-truncation-stop.md)
records the owner's rulings: the vote cap stays 1,024 (decision 5), a cap
truncation stays a stop in the live run (decision 6), the leak count is a
reported diagnostic and not a gate (decision 9), and the fifth authorization
is opened once this calibration reports, carrying the re-sized ceilings, the
refreshed profile and the leak column. The manifest's "Fourth authorization
(2026-09-14)" and "Accounts prompt set v4 (2026-09-15)" sections, whose two
declared one-sided effects stand, are not edited here.
[The fifth freeze](held-out-prefix-freeze-5.md) names this card in its
converted record's `converted.informed`, which
`test_a_binding_to_a_converted_record_stays_an_open_obligation`
(`tests/experiments/test_fresh_deduction_instrument.py:4722`; the freeze card
cites `:4412`, which is not that test at this tree) reads as a card path, so
this card must be present and OPEN in the tree that freeze merges into.

## Acceptance

- [ ] The three moved ceilings are copied verbatim from
  [the fifth authorization](fresh-deduction-authorization-5.md)'s Constraints
  table: `AUTHORIZED_UNIT_MAX_INPUT_TOKENS` 106,000 to 116,000,
  `AUTHORIZED_RUN_MAX_INPUT_TOKENS` 3,710,000 to 3,844,000 and
  `AUTHORIZED_RUN_MAX_OUTPUT_TOKENS` 459,000 to 422,000
  (`experiments/fresh_deduction_instrument.py:230-231,241-242`); per-unit
  output stays 16,000, the turn cap 4,096 and the vote cap 1,024 (`:206-207`,
  decision 5). They reach the meeting layer through the instrument's own
  `AUTHORIZED_SAMPLING` and its explicit `MeetingConfig`, not through a
  default-path change; the default path's recorded prompts and caps stay
  unchanged (`verify_samples.sh`, the four `--check` runs).
- [ ] `tests/experiments/deduction_usage_profile.json` is rebuilt from that
  sitting's `calibration.json` by the documented command
  (`--refresh-usage-profile`, `:7469`, writing through `write_usage_profile`,
  `:7258`), and in the SAME commit `CALIBRATED_UNIT_INPUT_TOKENS` and
  `CALIBRATED_UNIT_OUTPUT_TOKENS` (`:547-548`) move to 38,440 / 4,176 and the
  `RESERVATION_POLICY` arithmetic that embeds them (`:591-616`) is restated,
  with the manifest's verbatim quotation moved with it.
  `assert_limits_are_feasible` then ACCEPTS the new `AUTHORIZED_LIMITS`, and
  `test_the_calibration_is_the_largest_unit_the_archives_charged`
  (`tests/experiments/test_fresh_deduction_instrument.py:5011`) and
  `test_the_enforcement_section_quotes_the_reservation_policy` (`:4303`) pass.
  Planted: the old 3,710,000 run input ceiling, refused on that profile.
- [ ] The 27 dependent cases the sitting enumerated are updated, not deferred
  again. Eight are arithmetic that follows the constants, among them
  `test_a_re_sized_authorization_passes` (`:4856`), both parametrisations of
  `test_a_run_ceiling_below_its_own_units_is_refused` (`:4872`) and
  `test_the_committed_calibration_and_profile_parse_and_read_null` (`:2963`),
  whose null `finish_reason` pin a refreshed row answers with `"stop"`. Eight
  replay an archived FAULT this clean sitting does not carry, among them
  `test_the_profile_is_the_archived_calls_and_nothing_else` (`:5109`); they are
  pointed at a committed fixture of the stopped runs' rows rather than at the
  clean profile, and Results names its path. The other eleven are the
  feasibility refusals items 1, 2 and 4 settle.
- [ ] The `CALIBRATION_2_LIMITS` feasibility assertion is settled without
  re-sizing the mode, whose limits record a spend the manifest authorizes ONCE
  (`audits/deduction-candidate/execution-manifest.md:1062-1065`) and which no
  further sitting may make. Either
  `test_the_feasibility_gate_accepts_the_second_mode_for_120_units`
  (`tests/experiments/test_fresh_deduction_instrument.py:7785`) and
  `test_each_mode_is_accepted_whole` (`:7668`) are pinned to the profile the
  mode was sized on, passing 24,282 / 3,116 through the gate's own parameters
  (`:1278-1279`), or the assertion becomes an explicit refusal case naming
  4,612,800 and 505,216 against 4,500,000 / 450,000. Which, and why, is
  declared in Results; `CALIBRATION_2_LIMITS` (`:504`) does not move.
- [ ] This closes acceptance item 8 of
  [the second calibration card](fresh-deduction-calibration-2.md): that card
  flips to `done` with a dated subsection naming this card, the profile's two
  maxima (38,440 / 4,176) and the ceilings they moved, and `tasks/README.md`'s
  derived inventory sentence is updated with it.
- [ ] The manifest's limits table rows carry the new values verbatim with the
  fifth authorization card named as their source, and a dated "Fifth
  authorization (2026-09-15)" section records the change, its basis (the
  second calibration, by the stated rule; the run-level OUTPUT ceiling FALLS
  from 459,000 to 422,000 because the rule is followed) and that the refreshed
  profile now sizes the gate. `test_the_manifest_quotes_each_authorized_value`
  (`tests/experiments/test_fresh_deduction_instrument.py:3906`) passes on the
  new strings and the frozen analysis stays byte-identical
  (`test_no_frozen_analysis_byte_has_moved_since_the_last_logged_amendment`,
  `:4358`).
- [ ] After [the fifth freeze](held-out-prefix-freeze-5.md) merges into this
  branch, the Inputs table binds band 8000-8999 with the accepted seed range
  and skip count read off the new
  `audits/deduction-candidate/held-out/manifest.json`, names all four converted
  bands as development data with their dates and their records (3000-3999,
  5000-5999, 6000-6999 and
  `audits/deduction-candidate/held-out/manifest-band-7000-7999.json` for
  7000-7999, which that freeze marked `development` on 2026-09-15), and the
  Roles table's preparer row gains the fifth session with its pull request;
  `assert_manifest_binds_the_live_band`
  (`experiments/fresh_deduction_instrument.py:1060`) and
  `test_the_gate_says_which_bands_actually_moved`
  (`tests/experiments/test_fresh_deduction_instrument.py:1476`) pass against
  the merged record.
- [ ] The replay-double rehearsal of the full pipeline runs on the refreshed
  profile under the new limits, clears the feasibility gate and completes at $0
  (`run_dry`, `experiments/fresh_deduction_instrument.py:5908`;
  `test_the_rehearsal_on_a_refreshed_profile_runs_under_the_proposal`,
  `tests/experiments/test_fresh_deduction_instrument.py:6948`). It is re-run in
  the stacked round on the new band, and Results records its aggregate counts.

## Constraints

No live provider call, and no eval. The primary outcome, decision rule,
minimum actionable effect, tradeoff bound and `STOP_RULE`
(`experiments/fresh_deduction_instrument.py:689`) do not change: a cap
truncation stays a stop in the live run (decision 6), the leak count stays a
reported diagnostic (decision 9) and the vote cap stays 1,024 (decision 5).
`CALIBRATION_2_LIMITS` is not re-sized, the manifest's 2026-09-14 and v4
sections are not edited, and the shared budgeted client's pre-flight behaviour
does not change. Do not edit `experiments/held_out_prefixes.py`; this card
lands after [the fifth freeze](held-out-prefix-freeze-5.md) and merges that
branch in before re-binding the Inputs table. If the moved constants can only
reach the meeting layer through `orchestrator/game.py` or another default-path
file, stop and report rather than edit a hashed one. No band prefix is
generated, printed or opened, and the rehearsal writes to a temporary
directory: 3000-3999, 5000-5999 and 6000-6999 are development data, 7000-7999
becomes development data at that freeze, and 8000-8999 is then the live band
nobody opens.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/deduction_usage_profile.json` (and the fault fixture the
third item adds), `audits/deduction-candidate/execution-manifest.md`,
`docs/artifacts.md` (the `audits/` row),
[the second calibration card](fresh-deduction-calibration-2.md),
`tasks/README.md`'s derived inventory sentence, this card. Every acceptance
item that adds a gate carries a planted failure proving it detects the claimed
defect, and any `audits/` byte change recomputes the `docs/artifacts.md`
audits row. Delivered on `work/fresh-deduction-limits-5`, stacked on
`work/held-out-prefix-freeze-5` and retargeted to `main` once that branch
merges; one pull request into `main`, landed by merge commit or fast-forward and
never squashed, with the trailer `Card: tasks/work/fresh-deduction-limits-5.md`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section, a
re-bound Inputs table, an extended Roles row and new limit rows, and refreshes
a test fixture from a committed record. No recording, report, DTO, metric or
weight byte moves; no experiment becomes ON; no adopting record is created. The
arm-surface digest moves because the instrument is in `ARM_SURFACE_SOURCES`
(`experiments/fresh_deduction_instrument.py:4874`): a fresh stamp before the
fifth run, not a re-record.

## Validation

`uv run pytest tests/experiments -q` (fake and replay providers only), then
`uv run python` over `scripts/validate_task_docs.py`,
`scripts/check_doc_facts.py` and `scripts/verify_ml_evidence.py` (offline; never
`--complete`), `uv run pytest tests/scripts/test_verify_ml_evidence.py -q`,
`bash scripts/verify_samples.sh`, the four `uv run python
scripts/build_sample_report.py --sample-dir <set> --check` runs, and `bash
scripts/check.sh`. Do not run the live evaluation as a check.
