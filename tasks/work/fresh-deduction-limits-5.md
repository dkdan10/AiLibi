# Move the fresh-model deduction instrument to the fifth authorization's limits

**Status:** active

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

- [x] The three moved ceilings are copied verbatim from
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
- [x] `tests/experiments/deduction_usage_profile.json` is rebuilt from that
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
- [x] The 27 dependent cases the sitting enumerated are updated, not deferred
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
- [x] The `CALIBRATION_2_LIMITS` feasibility assertion is settled without
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
- [x] This closes acceptance item 8 of
  [the second calibration card](fresh-deduction-calibration-2.md): that card
  flips to `done` with a dated subsection naming this card, the profile's two
  maxima (38,440 / 4,176) and the ceilings they moved, and `tasks/README.md`'s
  derived inventory sentence is updated with it.
- [x] The manifest's limits table rows carry the new values verbatim with the
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
  and skip count read off the new `held-out/manifest.json`, names all four
  converted bands as development data with their dates (3000-3999, 5000-5999,
  6000-6999, 7000-7999), and the Roles table's preparer row gains the fifth
  session with its pull request; `assert_manifest_binds_the_live_band`
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

## Results

Round 1 of two. Every acceptance item that does not depend on
[the fifth freeze](held-out-prefix-freeze-5.md) is done and verified offline at
$0, on a fake or replay provider; no live call was made and no band prefix was
generated, printed or opened. Items 6 and 7 stay unchecked and this card stays
`active`: they re-bind the Inputs table to band 8000-8999, extend the Roles
table's preparer row and re-run the rehearsal on the new band, and all three
need that freeze merged into this branch first. The pull request is opened
against `main` and is retargeted onto `work/held-out-prefix-freeze-5` once that
branch is verified.

### The three ceilings, and where they reach the run

Copied verbatim from
[the fifth authorization](fresh-deduction-authorization-5.md)'s Constraints
table, which is their source of record:

| Constant | Was | Now |
| --- | --- | --- |
| `AUTHORIZED_UNIT_MAX_INPUT_TOKENS` | 106,000 | **116,000** |
| `AUTHORIZED_RUN_MAX_INPUT_TOKENS` | 3,710,000 | **3,844,000** |
| `AUTHORIZED_RUN_MAX_OUTPUT_TOKENS` | 459,000 | **422,000** |
| `AUTHORIZED_UNIT_MAX_OUTPUT_TOKENS` | 16,000 | 16,000, unchanged |
| turn cap / vote cap | 4,096 / 1,024 | unchanged (decision 5) |

The run-level OUTPUT ceiling FALLS. That is the rule being followed rather than
a budget being tightened: `CEILING_PROPOSAL_RULE` sizes it as the larger of a
hundred units at the measured mean x 1.5 and a hundred units at the largest
measured unit plus one turn cap of in-flight headroom, and v4 made units smaller
on output — the candidate arm's per-unit output mean fell from 3,481.5 at v3 to
1,608.9 and its largest unit from 4,816 to 4,176, so 100 x 4,176 + 4,096 =
421,696, rounded up to 422,000. The INPUT ceiling rises for the same reason read
the other way: the largest unit's input rose to 38,440, so a hundred of them
need 3,844,000 and the ceiling in force refused them.

None of the three reaches the meeting layer through a default-path file. They
are limits, not sampling: they are served to `run_instrument` as a `RunLimits`
object and enforced by `llm.budget.GameBudget`, while the caps and temperatures
the meeting layer does read still travel through the instrument's own
`AUTHORIZED_SAMPLING` and its explicit `MeetingConfig`. `orchestrator/game.py`
and `meetings/manager.py` are untouched, and no recorded prompt or cap moves —
`verify_samples.sh` and the four `--check` runs are green.

### The profile, the two calibrated constants and the reservation policy

`tests/experiments/deduction_usage_profile.json` is rebuilt from the sitting's
own output by the command the manifest documents, which makes no call:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile audits/deduction-candidate/calibration-2-2026-09-15/calibration.json \
  --profile-out tests/experiments/deduction_usage_profile.json
```

720 call rows, 120 unit rows, `built_from.mode` `2026-09-15`, `built_from.records`
`[("3000-3999", 50), ("5000-5999", 10)]`, totals `resolved_calls` 720,
`refused_calls_with_usage` 0, `largest_charged_unit_input_tokens` 38,440,
`largest_charged_unit_output_tokens` 4,176 — the figures
`audits/deduction-candidate/calibration-2-2026-09-15/CALIBRATION.md` recorded
when the runner ran the same command and did not commit the result. In the same
commit `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` move
to 38,440 / 4,176, which is what
`test_the_calibration_is_the_largest_unit_the_archives_charged` requires, and
`RESERVATION_POLICY` — which embeds both — is restated to name the sitting that
measured them. The manifest's verbatim quotation of that string under "How each
limit is enforced" moved with it and
`test_the_enforcement_section_quotes_the_reservation_policy` passes on the new
bytes.

`assert_limits_are_feasible` then ACCEPTS `AUTHORIZED_LIMITS`
(`test_the_gate_accepts_the_fifth_authorizations_limits`, renamed from
`..._the_fourth_authorizations_limits`).

**Planted, as the card asks:**
`test_the_fourth_authorizations_run_input_ceiling_is_refused_on_this_profile`
puts 3,710,000 back on the run-level input dimension and the gate refuses it,
naming both numbers; the same case then shows the OUTPUT dimension of that
authorization still clears, which is why the rule lowered that one rather than
raising it.

```
$ .venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -q -p no:randomly \
    -k "test_the_fourth_authorizations_run_input_ceiling_is_refused_on_this_profile or test_the_gate_accepts_the_fifth_authorizations_limits"
2 passed, 402 deselected
```

The refusal the plant reads, in the gate's own words:

```
the run-level input ceiling is 3,710,000 tokens and 100 units at the largest
unit the live archives charged (38,440) need 3,844,000: a run this long would
stop on the run ceiling rather than on its own evidence
```

### The 27 dependent cases, in the three classes the sitting named

Twenty-three went red on this tree when the profile and the two constants moved
— four fewer than the sitting counted, because moving the three ceilings in the
same commit settles four of its class-1 cases outright. All are updated, none
deferred.

* **The eleven feasibility refusals** are settled by the re-sized ceilings and
  by the calibration-mode pin below. `test_a_re_sized_authorization_passes`,
  both parametrisations of `test_a_run_ceiling_below_its_own_units_is_refused`,
  `test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused` and the
  three client-binding, manifest-binding and live-resume cases pass again once
  `feasible_limits()` clears the refreshed profile (its two run ceilings move
  from 3,600,000 / 350,000 to 3,900,000 / 430,000; still nobody's authorization,
  and still refused by `assert_live_run_is_authorized`).
  `test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit` is
  the residual this card closes, and it is renamed to
  `test_the_run_output_ceiling_clears_the_calibrations_largest_unit`: its plant
  flips to the SUPERSEDED pairing — the fourth authorization's 459,000 under the
  2026-09-14 calibration's own 4,590, which is 100 x 4,590 to the token and
  4,096 short of what those hundred units reserve — and the gate refuses it.
* **The eight archived-FAULT replays** are pointed at a committed fixture of the
  stopped runs' rows:
  **`tests/experiments/deduction_stopped_runs_usage_profile.json`**, the exact
  bytes `deduction_usage_profile.json` carried at `b720d764` (38 rows, 36
  resolved and two the provider billed and refused, seven units). It sits beside
  the current profile in `tests/experiments/` rather than under
  `tests/fixtures/`, because that is where the profile it is a copy of has
  always lived and because the `tests/fixtures/` row of `docs/artifacts.md`
  inventories a different family; no `tests/fixtures/` byte moves and that row
  is untouched. `usage_replay_double.stopped_runs_profile()` loads it and the
  eight cases pass it to their doubles: the stop of 2026-09-13, the archived
  refusal, the `billed_refusal` fault, the call-type-blind truncation, the
  mid-unit transport drop and the two `test_the_rehearsal_is_green_under_*`
  cases whose per-arm totals the manifest quotes — which is why those totals did
  not have to be re-measured — plus
  `test_the_profile_is_the_archived_calls_and_nothing_else`, whose subject is
  that archive's shape.
* **The eight arithmetic cases** follow the constants.
  `test_the_committed_calibration_and_profile_parse_and_read_null` now reads
  both sides: the stopped runs' rows still parse and still read null, which is
  the compatibility claim, and every row of the refreshed profile reads a
  measured `"stop"`.
  `test_the_committed_calibration_and_profile_parse_and_read_null`,
  `test_a_fixture_sized_proposal_says_it_clears_no_gate` and
  `test_the_rehearsal_on_a_refreshed_profile_runs_under_the_proposal` needed
  more than arithmetic and are described under **Decisions** below.

### The `CALIBRATION_2_LIMITS` assertion: pinned, not re-sized

The card offered two settlements and this takes the first: the mode's
feasibility is **pinned to the profile the mode was sized on**, passed through
the gate's own parameters. Two new module constants,
`CALIBRATION_SIZING_UNIT_INPUT_TOKENS` / `CALIBRATION_SIZING_UNIT_OUTPUT_TOKENS`
(24,282 / 3,116), carry that profile's maxima, and
`assert_calibration_is_authorized` and `assert_ready_for_a_calibration` hand them
to `assert_limits_are_feasible`. `CALIBRATION_2_LIMITS` does not move, and
neither does `CALIBRATION_LIMITS`.

Why this rather than the explicit refusal case: the refusal had to be settled in
the PRODUCTION path, not only in two tests. Both calibration gates read the
calibrated constants from module scope, so a refreshed profile refuses both
spent modes wherever they are checked, and two of the card's own class-1 cases —
the draw-preflight refusals at `test_the_live_capable_preflight_refuses_*` —
are cases whose planted refusals that earlier raise masks. Turning the mode into
a refusal would have left those two unable to reach what they check. And the
reading itself is right: a mode's ceilings record a spend the manifest
authorizes ONCE, both have been spent, and checking a spent sitting against a
measurement that sitting itself produced asks whether something that already
happened could be authorized under numbers that did not exist when it was.

The refusal is kept as its own case rather than lost:
`test_the_second_mode_is_refused_on_the_refreshed_profile` names 4,612,800 and
505,216 against the mode's 4,500,000 / 450,000, and says in its own words that
this is why no further calibration-2 sitting is authorized and not a reason to
re-size the mode. `test_the_sizing_figures_are_the_committed_stopped_runs_archive`
holds the two new constants to the committed fixture's own maxima, so they are
read off evidence rather than typed, and asserts they are NOT the live run's.

### The manifest

The limits table's total-token-budget row carries the three new values verbatim
with the fifth authorization card named as their source, and the section
preamble says which card each moved row is copied from. A dated
**"Fifth authorization (2026-09-15)"** section records the change, its basis
(the second calibration, read through the instrument's own proposal rule), that
the run-level OUTPUT ceiling falls because the rule is followed, and that the
refreshed profile now sizes the gate. The enforcement section's
`RESERVATION_POLICY` quotation and its surrounding paragraph carry the new
numbers (421,696 against 422,000), and the verification section's two headroom
paragraphs carry the new denominators — 50.2% of 422,000 on output, 54.3% of
3,844,000 on input, 51% and 20% on the dry run's input heuristic — with the
superseded figures named as superseded rather than deleted.

`test_the_manifest_quotes_each_authorized_value` passes on the new strings, and
`test_no_frozen_analysis_byte_has_moved_since_the_last_logged_amendment` passes:
no frozen-analysis byte moved. The "Fourth authorization (2026-09-14)" and
"Accounts prompt set v4 (2026-09-15)" sections are NOT edited, and the cost
statement is not edited — its `llm/featherless_client.py:243-244` citation has
aged, which the fifth authorization card flags and which stands as the record of
what was authorized. `docs/artifacts.md`'s `audits/` row is recomputed with the
change staged: **15,598,331 tracked bytes / 215 files** (was 15,592,140 / 215),
by `git ls-files audits` and the summed sizes of those paths;
`scripts/verify_ml_evidence.py` and `tests/scripts/test_verify_ml_evidence.py`
agree.

### The rehearsal, on the refreshed profile under the new limits

The half of item 7 that does not need the freeze is done and pinned:
`TestUsageReplay::test_the_rehearsal_is_green_on_the_refreshed_profile_under_the_new_limits`
clears `assert_limits_are_feasible` first, then runs the whole pipeline — 100
units, 600 calls, `total_cost_usd` 0.0 — replaying the refreshed profile under
`AUTHORIZED_LIMITS` and `AUTHORIZED_SAMPLING`:

| Arm | input | output | calls | units |
| --- | --- | --- | --- | --- |
| `repaired_clock` | 1,038,160 | 56,765 | 300 | 50 |
| `combined_accounts` | 1,134,054 | 80,441 | 300 | 50 |
| run | 2,172,214 | 137,206 | 600 | 100 |

That is 56.5% of the 3,844,000 run-level input ceiling and 32.5% of the 422,000
output one — headroom checks, not predictions. The band is whatever the live
freeze record holds today; the double answers from an archived distribution
keyed by arm and call type, so these figures do not depend on which prefix a
unit ran and the re-run on band 8000-8999 in the stacked round is a
confirmation rather than a re-measurement. `run_dry` writes to a temporary
directory and no prefix of any band is opened.

### Decisions

1. **The fault fixture lives in `tests/experiments/`, not `tests/fixtures/`.**
   It is a byte-for-byte copy of the profile this card replaces, its only
   consumer is `usage_replay_double`, and `docs/artifacts.md`'s
   `tests/fixtures/` row inventories a different family. No row of that
   inventory moves.
2. **`CALIBRATION_2_LIMITS` is pinned, not refused and not re-sized.** Reasons
   above. The refusal survives as its own named case.
3. **`test_a_fixture_sized_proposal_says_it_clears_no_gate` patches the two
   calibrated constants to the archive its double replays.** The comparison it
   plants — a fixture distribution against a real endpoint's — was written when
   the committed profile and the replayed archive were the same seven units. On
   a 120-unit committed profile a five-seed calibration subsamples 30 of each
   bucket's 360 rows, so its maximum is legitimately below the profile's and
   EVERY proposal computed from it is told so, fixture and measurement alike.
   Restoring the identity restores the plant; a third block then reads the
   unpatched state directly and asserts that subsample arithmetic as arithmetic.
   `test_the_rehearsal_on_a_refreshed_profile_runs_under_the_proposal` is the
   same question and checks the proposal at its OWN measured maxima, which is
   the claim the proposal makes.
4. **Two tests are renamed**, both to stop a name asserting something false:
   `test_the_gate_accepts_the_fourth_authorizations_limits` to
   `..._the_fifth_authorizations_limits`, and
   `test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit` to
   `..._clears_...`. `test_the_rehearsal_is_green_under_the_fourth_authorizations_limits`
   is deliberately NOT renamed: the manifest's frozen "Fourth authorization
   (2026-09-14)" section cites it by name and this card may not edit that
   section.

### Verification

```
$ .venv/bin/pytest tests/experiments -q
490 passed
$ .venv/bin/python scripts/validate_task_docs.py
$ .venv/bin/python scripts/check_doc_facts.py
$ .venv/bin/python scripts/verify_ml_evidence.py
checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5
$ .venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q
$ bash scripts/verify_samples.sh
All 50 samples verified clean.  (x2: replays/samples/{4p1i,9p2i})
$ .venv/bin/python scripts/build_sample_report.py --sample-dir <set> --check   # x4
replays/samples/{4p1i,9p2i} and replays/ml_corpus/{4p1i,9p2i}: consistent with their replays
$ bash scripts/check.sh
7823 passed, 20 skipped, 3 xfailed, 10 warnings   (frontend: 515 tests, 19 files)
All checks passed!
```

`scripts/check.sh` was run directly and its real exit code read: 0. The live
evaluation was not run and is not a check here.

### Limitations

* Items 6 and 7 are not finished. The Inputs table still binds the fourth band,
  the Roles table's preparer row still ends at the fourth freeze, and the
  rehearsal has not been run on band 8000-8999. All three wait on
  [the fifth freeze](held-out-prefix-freeze-5.md) merging into this branch.
  `assert_manifest_binds_the_live_band` and
  `test_the_gate_says_which_bands_actually_moved` pass against the record this
  tree holds, which is the fourth band's.
* The rehearsal's numbers are a REPLAY of an archived distribution, not a
  prediction of the fifth run. They say the pipeline completes inside these
  ceilings on the units this evaluation has measured; a live model writes a
  different transcript.
* The two `test_the_rehearsal_is_green_under_*` cases now read an archive that
  is no longer the tree's current profile. That is deliberate — the manifest
  paragraph they check is that archive's — but it means those two figures will
  not move again when a later calibration refreshes the profile, and a reader
  should take them as a record of the three stopped runs rather than as the
  current measurement. The case added above is the current one.
* The arm-surface digest moves, because
  `experiments/fresh_deduction_instrument.py` is in `ARM_SURFACE_SOURCES`. That
  is a fresh stamp before the fifth run, not a re-record: no recording, report,
  DTO, metric or weight byte moves, no experiment becomes ON, and no constant
  pins the digest.
