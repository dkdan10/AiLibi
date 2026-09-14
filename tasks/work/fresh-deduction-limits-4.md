# Move the fresh-model deduction instrument to the fourth authorization's limits

**Status:** active

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

- [x] `AUTHORIZED_TURN_MAX_TOKENS` is 4,096, the vote cap stays 1,024, and the
  four token ceilings are 106,000 / 16,000 per unit and 3,710,000 / 459,000
  run-level, copied from the authorization card's Constraints table; the
  reservation schedule under the new caps is 15,360 and
  `assert_limits_are_feasible` accepts `AUTHORIZED_LIMITS` (a planted test
  with the old ceiling still goes red). The turn cap reaches the meeting
  layer's per-call `max_tokens` through the instrument's own sampling
  configuration, not through a default-path change; the default meeting
  path's recorded prompts and caps are unchanged (`verify_samples.sh`, the four
  `--check` runs).
- [x] The manifest's limits table carries the same values verbatim with the
  authorization card named as their source, the reservation-policy text states
  the new schedule, and a dated section "Fourth authorization (2026-09-14)"
  records the change and its basis; the test that pins the table to the
  constants passes and the frozen analysis strings are byte-identical (test).
- [ ] After [the fourth freeze](held-out-prefix-freeze-4.md) is merged into
  this branch, the Inputs table binds band 7000-7999 (band, accepted range,
  skip count from the new `held-out/manifest.json`), names all three converted
  bands as development data with their dates, and
  `assert_manifest_binds_the_live_band` passes against the merged record.
- [ ] The replay-double rehearsal of the full pipeline under the new limits
  clears the feasibility gate and completes at $0, and Results records its
  aggregate counts only.
- [x] Every new gate has a planted failure proving it detects the claimed
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

## Results

Acceptance items 1, 2 and 5 are done; 3 and 4 are this card's later round and
their boxes are open, so the card is `active`. The two open items both wait on
[the fourth freeze](held-out-prefix-freeze-4.md): the Inputs table cannot be
re-bound to 7000-7999 until that record exists on this branch, and the
replay-double rehearsal has to run on the band the run will draw. When that
freeze is merged into `work/fresh-deduction-limits-4`, the rehearsal and the
re-binding land in one further round and the card closes. The pull request is
retargeted onto `work/held-out-prefix-freeze-4` at the same time.

**What moved.** `AUTHORIZED_TURN_MAX_TOKENS` is 4,096 (written as a number, no
longer read from `meetings.manager`), the vote cap is still the shipped 1,024,
and the four ceilings are 106,000 / 16,000 per unit and 3,710,000 / 459,000
run-level — every figure copied from
[the fourth authorization card](fresh-deduction-authorization-4.md)'s
Constraints table. `unit_output_reservation()` is therefore 15,360 and
`assert_limits_are_feasible()` accepts `AUTHORIZED_LIMITS`, which is the first
time the gate the diagnosis of 2026-09-13 installed has passed on the committed
numbers.

**The turn cap reaches the meeting layer through the instrument's own sampling
configuration**, not through a default-path file. `run_unit` already built its
runner with `config=sampling.meeting_config()`
(`experiments/fresh_deduction_instrument.py`, the `build_default_meeting_runner`
call), and `MeetingConfig.turn_max_tokens` is what `meetings/manager.py` passes
as each turn's `max_tokens`; raising `AUTHORIZED_TURN_MAX_TOKENS` moves that
value and nothing else. `meetings/manager.py`'s `DEFAULT_TURN_MAX_TOKENS` is
still 2,048 and `orchestrator/game.py` is untouched, so no recorded campaign
and no default meeting path draws differently. The four `--check` runs and
`verify_samples.sh` below confirm it against the recorded samples.

**The refusal is kept as a plant rather than retired with the defect.** The
4,000 ceiling merged on 2026-09-07 is still red — now against the wider
schedule — and the two gate tests that used to rely on the committed limits
being infeasible plant those ceilings as the authorized set instead of
asserting the tree's own numbers
(`test_the_live_run_path_fails_closed_under_infeasible_limits`,
`test_the_gate_runs_before_the_frozen_set_is_read`). The
`_authorize_feasible_limits` helper those tests shared existed only to work
around the committed limits being unpayable and is deleted.

**The calibration mode keeps the caps it drew at.** `CALIBRATION_LIMITS` is
untouched, as the card requires, and that is exactly why the calibration's draw
had to be frozen beside it: its 12,000 per-unit output ceiling pays for the
9,216-token schedule the 2,048 cap reserves and not for the 15,360 the raised
cap reserves, so following the run to 4,096 would have authorized six calls the
calibration's own ceilings cannot pay for — the defect
`assert_limits_are_feasible` exists to refuse, one authorization down. A new
`CALIBRATION_SAMPLING` holds the calibration's caps,
`assert_calibration_is_authorized` now requires it, and the committed
`calibration-2026-09-14/calibration.json` stays re-derivable from this tree (a
test compares its recorded `sampling` block to the constant). No second
calibration is authorized by anything here; sizing a run that draws at 4,096
would need its own calibration and its own ceilings, on a card.

### Planted and perturbed cases (pinned to `b80cb92e`)

Each is the claimed defect reintroduced, and each turns the gate red. Run from
the repository root with the change applied, then reverted.

1. The committed per-unit output ceiling put back to the 4,000 merged on
   2026-09-07 (`AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS: Final[int] = 4_000`):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k test_the_gate_accepts_the_fourth_authorizations_limits
   ```

   ```
   E  experiments.fresh_deduction_instrument.LimitsInfeasible: the per-unit output ceiling is 4,000 tokens and one unit reserves 15,360 (3 x 4,096 + 3 x 1,024): this run authorizes calls it cannot pay for, and the budget would refuse one of them on the reservation rather than on the spend
   FAILED ...::TestFeasibility::test_the_gate_accepts_the_fourth_authorizations_limits
   1 failed, 309 deselected
   ```

   The same defect is held from the other side by
   `test_the_ceilings_merged_on_2026_09_07_are_still_refused`, which plants that
   ceiling and requires the refusal to name both 4,000 and 15,360.

2. `CALIBRATION_SAMPLING` made to follow the run's raised cap
   (`turn_max_tokens=AUTHORIZED_TURN_MAX_TOKENS`):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k "calibration_at_its_own_caps or kept_the_caps_it_drew_at"
   ```

   ```
   E  assert 4096 == 2048
   FAILED ...::TestCalibrationGate::test_the_feasibility_gate_accepts_the_calibration_at_its_own_caps
   FAILED ...::TestAuthorizedConstants::test_the_calibration_kept_the_caps_it_drew_at
   2 failed, 308 deselected
   ```

3. The dated manifest section's reservation arithmetic replaced by a phrase
   ("`3 x 4,096 + 3 x 1,024 = 15,360`" to "the raised reservation schedule"):

   ```
   .venv/bin/python -m pytest tests/experiments/test_fresh_deduction_instrument.py \
     -q -p no:randomly -k fourth_authorization_section
   ```

   ```
   E  AssertionError: 3 x 4,096 + 3 x 1,024 = 15,360
   FAILED ...::TestExecutionManifest::test_the_fourth_authorization_section_records_the_change_and_its_basis
   1 failed, 309 deselected
   ```

A fourth case is already committed rather than demonstrated by hand: the
per-call cap gate is parametrized over 8,192, 2,048 and 512, and 2,048 — the
shipped turn default, an authorized cap until 2026-09-14 — is now refused by
`_InstrumentClient`, so a caller still drawing at the old cap is a stop rather
than a silent second distribution.

### Verification

Every command below was run on this branch at `b80cb92e` (the commit that moves
the instrument and test bytes; only the manifest's dated section, this card and
the task index move after it, and no command below reads a held-out prefix).

| Command | Result |
| --- | --- |
| `uv run pytest tests/experiments -q` | 390 passed (fake and replay providers only; no live call) |
| `uv run python scripts/validate_task_docs.py` | pass |
| `uv run python scripts/check_doc_facts.py` | pass |
| `uv run python scripts/verify_ml_evidence.py` | 60 checks, 48 OK, 0 FAIL, 7 EVIDENCE-BRANCH-ABSENT, 5 INFO |
| `uv run pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/verify_samples.sh` | 4p1i and 9p2i, all 50 samples each, clean |
| `scripts/build_sample_report.py --sample-dir <set> --check` x 4 | `replays/samples/{4p1i,9p2i}` and `replays/ml_corpus/{4p1i,9p2i}` all consistent with their replays |
| `bash scripts/check.sh` | exit 0: 7,702 passed / 20 skipped / 3 xfailed, 515 frontend tests, strict mypy over 477 files, ruff clean, production build |

`docs/artifacts.md`'s `audits/` row is recomputed for the manifest's changed
bytes (210 files, unchanged count; the byte total moves).

### Limitations

- The Inputs table still binds 6000-6999 and the verification section's dry-run
  and rehearsal figures are still the third band's, labelled as such in the
  document. Both are items 3 and 4, in the later round.
- The manifest's headroom figures are re-expressed against the new ceilings
  from the SAME committed rehearsal rather than from a fresh one: the replay
  double's spend does not depend on a cap it never reaches, so the arm totals
  are byte-identical and only the percentages move. The rehearsal item 4 owes
  is a new run on the new band, and it is not claimed here.
- `tests/experiments/deduction_usage_profile.json` is unchanged, so
  `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are still
  the three stopped live runs' largest unit (24,282 / 3,116) rather than the
  calibration's (35,232 / 4,590). The re-sized run ceilings clear both figures,
  so the gate is not weakened by it; refreshing the profile is the open question
  [the calibration card](fresh-deduction-calibration.md)'s Results hands back,
  and it is not this card's.
- `assert_calibration_is_authorized` now refuses a live calibration drawn at the
  run's cap. Nothing is authorized to run one, so this is a closed door rather
  than a regression, but it is stated: a future calibration needs a card that
  carries both a draw and ceilings that pay for it.
