# Run a second development calibration sized for the impostor ballot mode

**Status:** done

## Outcome

A second development calibration measures what the fifth run would actually
draw: sixty paired seeds across the converted records, both arms, at the RUN's
sampling, with a per-call truncation counted instead of ending the sitting. Per
arm, per call type and split by the voter's hidden role it reports output
tokens and the character lengths of the fields that carry prose, the truncation
count with its `finish_reason`, how many impostor ballots open by naming their
own role or kill, and a pre-declared count of public turns that leak a speaker's
hidden role. It proposes run ceilings that clear the feasibility gate under its
own maxima and refreshes the rehearsal double's usage profile. The owner's merge
is the authorization of the calibration's limits.

## Evidence

[The diagnosis of 2026-09-15](../diagnosis-2026-09-15-truncation-stop.md),
whose section-6 decisions the owner approved as a set that day, sets the bar in
decision 7: at least sixty impostor-authored candidate ballots, a 99.2% chance
of seeing a 1-in-13 event. Exposure is about one impostor draw per candidate
unit, so sixty draws is sixty candidate units, paired with the reference arm
into the 120 units below. The fourth run (PR #458, branch
`work/fresh-deduction-run-4` at `5f2383ea`, unmerged) stopped at unit 26 of 100
on a ballot whose author was that seed's impostor: one truncation in thirteen
impostor-authored candidate ballot draws, Wilson 95% [1.4%, 33.3%], and
P(a clean 50-pair run) = 1.8%.

The first calibration could not have seen it (diagnosis section 3): fifteen
candidate ballots, about five impostor-authored, 0.4 expected events, and a p95
that IS the maximum at n=15 under the nearest-rank rule this instrument uses
(`PERCENTILE_RULE`, `experiments/fresh_deduction_instrument.py:5398`), so its
237-token ballot maximum was never a bound. It measured tokens, not role.

The mode it ran in is small on purpose. `CALIBRATION_PAIRED_SEEDS = 5`
(`:357`), `CALIBRATION_LIMITS` (`:377-385`), `CALIBRATION_CLAUSE` (`:1364`),
and `assert_calibration_is_authorized` (`:1394`) refuses any provider but
`featherless` (`:1455`), any limits (`:1466`), sampling (`:1472`) or seed
count (`:1479`) but that set's, and a manifest without the clause (`:1500`).
`verify_calibration_set` (`:2865`) rebuilds the first `paired_seeds` accepted
seeds of ONE record, and `_converted_band_for` (`:2836`) refuses the held-out
record by name. Two of those refusals this card extends, because
`CALIBRATION_SAMPLING` (`:444`) is frozen at the shipped 2,048 turn cap
(`DEFAULT_TURN_MAX_TOKENS`, `meetings/manager.py:210`) and not the run's 4,096
(`:201`): its ceilings pay for a 9,216-token schedule, not the 15,360 the
raised cap reserves (`unit_output_reservation`, `:502`). The module's comment
(`:433-443`) says as much: a calibration of the raised draw needs its own
ceilings on its own card.

The split and the detector need no new privilege. `UnitRecord` (`:3212`) is
in-memory only and carries the ground-truth roles (`:3230`), the parsed ballots
(`:3226`) and the committed turns (`:3229`); `run_calibration` (`:5909`) keeps
every unit record until the report is built; the prose fields are
`rationale_text` (`meetings/schemas.py:766`), each claim's `reason` (`:417`,
`:426`) and `free_text` (`:591`).

Truncation ends a sitting today. `_unusable_response` (`:2394`) returns
`PerCallCapExceeded` when `output_tokens >= max_tokens` (`:2413`), and the
parse-failure path raises it (`:2276`) ahead of the meeting layer's shipped
fail-soft: a marked SKIP for a ballot (`meetings/manager.py:2288,2298`) or a
placeholder turn (`:1916-1922`). That ordering is deliberate on the live path
and stays (diagnosis section 4's rulings row; decision 6 is No). In a
calibration it is self-defeating: one truncation ends the sitting before it has
measured the tail it was sent to measure.

The proposal is one term short. `ceiling_proposal` (`:5815`) sizes each
run-level ceiling as max(units x measured mean x 1.5, units x measured
maximum), then runs the gate against the TREE's calibrated constants
(`:477-478`) rather than its own maxima, while `assert_limits_are_feasible`
adds one turn cap of in-flight headroom to the run-level OUTPUT comparison
(`:1264-1273`). So 2026-09-14 published 459,000 for a hundred units while its
own largest unit needs 4,590 x 100 + 4,096 = 463,096, a residual held by
`tests/experiments/test_fresh_deduction_instrument.py:4627`, handed back by
[the limits card](fresh-deduction-limits-4.md) and closed here.

The inputs exist. The 3000-3999 and 5000-5999 freeze records under
`audits/deduction-candidate/held-out/` are both `development` with fifty
accepted seeds each, first seeds 3000 and 5000. Seeds 3000 to 3004 were
rendered by the calibration of 2026-09-14
([its card](fresh-deduction-calibration.md)), which changes nothing: a
converted band is development data from its conversion, not from its
rendering. Sixty paired seeds is all fifty of the 3000 band plus 5000 to 5009.

## Acceptance

- [x] Review correction: the `records=` override cannot name a draw the card
  does not authorize, which is a PREFIX rule and not an ordering one.
  `CONVERTED_BANDS` holds THREE development records, so round 1's ordered,
  non-repeating subsequence still accepted `[band-5000, band-6000]` and
  `[band-3000, band-6000]` — each sixty seeds ending at 6010 where the
  authorized draw ends at 5009 — on `verify_calibration_draw` and on both
  live-capable entry points. A supplied list is now held to a prefix of
  `CONVERTED_BANDS`, refused before a prefix is rebuilt, which with the greedy
  fill makes an accepted list's seeds a function of the seed count alone.
  Planted: both lists on the helper and on the two live-capable entry points,
  plus a property case that enumerates every ordered arrangement of the
  converted records and holds each accepted one to the default draw's seeds.
- [x] Review correction: acceptance item 3's truncation COUNTING is driven end
  to end rather than asserted at the seam. A truncating provider double goes
  through `run_calibration` in this mode and the sitting finishes, and the case
  pins the whole role-split tally — per arm, per call type, per hidden role,
  with the provider's `finish_reason` — together with the fail-soft each
  truncation produces (eight marked SKIP ballots and one placeholder turn).
  Disabling the tally turns it red.
- [x] Review correction: the `records=` override of the live-capable pre-flight
  is held to `CONVERTED_BANDS`' own order with no record named twice, so the two
  shapes the round-1 review reproduced — `[band-5000, band-3000]` and
  `[band-3000, band-3000]`, the second of which filled sixty prefixes out of
  fifty distinct seeds — are refused, on `verify_calibration_draw`,
  `assert_ready_for_a_calibration` and `run_calibration` alike. Planted: both
  lists, on the helper and on the two live-capable entry points. Order and
  no-repetition are NOT the whole property: the round-2 correction above found
  the band-skipping shape they still admitted and replaced the rule.
- [x] Review correction: acceptance item 7's plant binds the branch it names.
  Its fixture set the measured mean equal to the measured maximum, so the mean
  rule dominated and the case passed with the in-flight headroom term deleted;
  the mean is now well below the maximum, the headroom branch decides the
  proposal, and deleting the term drops it to 459,000 and turns the case red.
- [x] Review correction: the leak detector counts out a statement that is
  SUPPOSED or ASKED rather than asserted, and `ROLE_LEAK_RULE` no longer claims
  the figure is a floor. A conditional self-reference scored as a confession
  and inflated both reported columns, so the guard now carries conditional,
  hypothetical and interrogative governors, and the rule string and the
  manifest's pre-declaration both say the count is an estimate carrying error
  in BOTH directions. Planted: four deflections counted out, and two
  confessions with a trailing conditional still counted.
- [x] A SECOND dated clause and constant set beside the 2026-09-14 set, not
  replacing it: `CALIBRATION_2_PAIRED_SEEDS = 60`, `CALIBRATION_2_LIMITS`, and
  `CALIBRATION_2_SAMPLING` equal to `AUTHORIZED_SAMPLING` (`:426`), so the draw
  is turn 4,096 / vote 1,024 and what is measured is what the fifth run would
  do; plus a `CALIBRATION_2_CLAUSE` the manifest quotes verbatim. The first
  mode keeps its own sampling, seeds and ceilings, and
  `assert_calibration_is_authorized` (`:1394`) accepts exactly one of the two
  sets whole and refuses every crossing, with a planted failure each: five seeds
  under the second's limits, sixty under the first's, either mode drawing at the
  other's caps.
- [x] The draw: accepted seeds ascending across `CONVERTED_BANDS`
  (`experiments/held_out_prefixes.py:375-394`) in list order until sixty paired
  seeds are bound, so all fifty of the 3000-3999 record then 5000 to 5009 of
  the 5000-5999 record. Each record is verified by `verify_calibration_set`
  (`:2865`), each prefix held to the digest that record froze, the held-out
  record still refused by name (`_converted_band_for`, `:2836`), and the inputs
  block names every record with its sha256 and the seeds drawn from it. Planted:
  a `status` that is not `development`, a moved digest, and a draw that runs out
  of accepted seeds before sixty.
- [x] In THIS mode a per-call truncation is a measurement, not a stop. The cap
  branch of `_unusable_response` (`:2413`) does not raise here, the truncated
  ballot or turn takes the meeting layer's existing fail-soft
  (`meetings/manager.py:2288,2298`; `:1916-1922`), and the call is counted per
  arm, per call type and per voter role with its `finish_reason`. The identity
  branch and the live path still stop: a planted failure proves a live
  evaluation invocation still raises `PerCallCapExceeded` on that response.
  `STOP_RULE` (`:619`) is not edited; the manifest's dated section says why.
- [x] Role-split reporting: per arm, per call type, split by the voter's or
  speaker's hidden role, the completions and the mean, p95 and max of output
  tokens and of the character lengths of `rationale_text`, `claims[].reason` and
  `free_text`, plus the count of impostor-authored candidate ballots that open
  by stating their own role or kill. The truncation rate's denominator is
  impostor DRAWS, since a fail-softed ballot is a draw that produced no
  rationale. Counts and lengths only: no prose, prompt, prefix or outcome.
- [x] The pre-declared leak diagnostic (decision 9): a detector over each unit's
  committed public turns counts, per arm, the turns in which a speaker states
  its own hidden role or a kill it committed, off the roles `UnitRecord`
  (`:3230`) already holds. Reported here AND pre-declared in the manifest as a
  reported column of the fifth run, so the primary outcome can be read against
  it. The owner's reading of decision 9 on 2026-09-15 is that the leak does not
  block the next run on its own, which is what makes a reported diagnostic the
  right instrument for it rather than a gate. Planted: the fourth run's two
  positive shapes (a first-person role statement, a first-person kill
  statement) and the negative the diagnosis counted out, an impostor rebutting
  an accusation against itself.
- [x] The Constraints table's limits are the mode's, and
  `assert_limits_are_feasible` (`:1203`) accepts them for 120 units: per-unit
  output 16,000 against a 15,360 schedule, per-unit input 60,000 against the
  24,282 largest archived unit (`:477`), run output 3,116 x 120 + 4,096 =
  378,016 against 450,000 and run input 2,913,840 against 4,500,000. Planted:
  the first mode's 12,000 per-unit output, which this draw cannot pay for.
- [x] The ceiling proposal rule adds the in-flight headroom term: a proposed
  run-level OUTPUT ceiling is at least units x the measured maximum unit plus
  one turn cap, the term the gate enforces (`:1264-1273`), and the proposal's
  own feasibility check (`:5862-5870`) runs against the CALIBRATION's maxima
  rather than the tree's constants, with `CEILING_PROPOSAL_RULE` (`:5415`)
  stating it. Planted: 4,590 over 100 units, which must propose 464,000 or more.
- [x] The rehearsal double's usage profile is refreshed from this calibration
  by the documented `--refresh-usage-profile` command, and the dependent tests
  are updated with it rather than deferred again:
  `test_the_calibration_is_the_largest_unit_the_archives_charged`
  (`tests/experiments/test_fresh_deduction_instrument.py:4688`), the run-ceiling
  residual at `:4627` and the profile's own test at `:4786`. The two calibrated
  constants (`:477-478`) move with it, and 2026-09-14's eight-red-test hand-back
  is settled in Results.
- [x] Aggregates only, committed under
  `audits/deduction-candidate/calibration-2-<date>/` with per-unit usage rows,
  in the shape the first calibration committed, with
  `assert_report_holds_no_prefix_bytes` (`:4178`) over the payload. Prefixes
  and rendered prompts are not committed; replays go to the runner's
  `--output-dir`, outside version control.
- [x] The execution manifest gains a dated "Development calibration 2
  (2026-09-15)" section: the clause verbatim, the inputs and their records, the
  limits and sampling table, the truncation ruling scoped to this mode, and the
  leak column pre-declared for the fifth run. The frozen analysis strings stay
  byte-identical (test) and the 2026-09-14 section is not edited.
- [x] The live sitting is run once, by a separate runner session on
  `work/fresh-deduction-calibration-2-run` under the manifest's calibration-2
  clause, and its Results subsection records the role-split profile, the
  truncation rate with its Wilson interval (`scripts/paired_stats.py:115`), the
  per-arm leak count, the proposal, usage at $0.00 and the archive path.

## Constraints

Stacked on BOTH [the v4 accounts prompt set](accounts-prompt-set-v4.md), the
surface being measured, and
[the finish-reason card](featherless-finish-reason.md), the field the truncation
rows record. Measuring the v3 family would measure a surface the fifth run will
not draw from. The values below are the ones the owner's merge authorizes:

| Field | Value |
| --- | --- |
| Paired seeds | 60, ascending across `CONVERTED_BANDS` in order: all fifty of `held-out/manifest-band-3000-3999.json`, then 5000-5009 of `-5000-5999.json` |
| Units and calls | 120 units (60 paired seeds x 2 arms), about 720 model calls |
| Provider and model | `featherless`, `Qwen/Qwen3.6-27B`, non-thinking, `json_object`, prompt set `qwen3_6_27b`: carried from the model lock, not re-decided here |
| Per-call token cap | turn 4,096 output / vote 1,024, `AUTHORIZED_SAMPLING` (`:426`), because the point is to measure the draw the fifth run makes |
| Per-unit token ceiling | 60,000 input / 16,000 output. The output figure clears the 15,360 schedule (`:502`); the input figure is about 1.6x the largest unit the fourth run charged (36,743) |
| Run-level token ceiling | 4,500,000 input / 450,000 output. The fourth run's per-unit means project about 2.87 M input and 276 k output over 120 units, so these are anomaly detectors at roughly 1.6x, not a budget |
| Wall-clock deadline | 5 h of model work within a 6 h elapsed deadline, one sitting |
| Transport bound | 4 attempts per call at a 180 s per-attempt wall, unchanged (`:256`, `:267`) |
| Dollar limit | $0.00 marginal, the same flat-rate subscription and the same reason as the run's cost statement |

The wall is the binding limit, stated rather than absorbed: 720 calls in 5 h
allows 25.0 s per call, against 17.23 s per attempt pooled and 21.85 s on the
candidate arm on 2026-09-14, so the margin is 1.45x pooled and 1.14x at the
slowest arm pace measured. A calibration has no checkpoint and no resume: a
stop is reported with its partial accounting, and a second sitting needs the
owner's say, as every live sitting does.

This is the only live spend the card authorizes. No held-out band is read,
rendered or converted, and the record at `MANIFEST_PATH` (band 7000-7999,
frozen by PR #456) is untouched;
[the fifth freeze](held-out-prefix-freeze-5.md) is dispatched after this
calibration reports and is not a predecessor of it. No grader runs, no paired
statistic is computed and no outcome is reported, so no unit reaches the
frozen analysis. The live run's
primary outcome (`:556`), decision rule (`:574`), minimum actionable effect
(`:569`), tradeoff bound (`:590`) and `STOP_RULE` (`:619`) do not change: the
truncation relaxation is scoped to this mode and the live path keeps its stop.
The shared budgeted client's reservation policy does not change. This card
changes no prompt byte; prompt-byte changes to the candidate family stay behind
the default-OFF experiment levers, with no recording and no re-record. The
runner of the sitting is not this card's implementer.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/usage_replay_double.py` and
`tests/experiments/deduction_usage_profile.json` (refreshed from this
calibration), `audits/deduction-candidate/execution-manifest.md`,
`audits/deduction-candidate/calibration-2-<date>/` (the sitting's outputs),
`docs/artifacts.md` (the `audits/` row), `tasks/README.md`'s derived inventory
sentence, this card.

Delivered on `work/fresh-deduction-calibration-2`, based on the later of
`work/accounts-prompt-set-v4` and `work/featherless-finish-reason` to merge and
retargeted onto `main` once both have landed, as one pull request into `main`;
merge commit or fast-forward, never squash; trailer
`Card: tasks/work/fresh-deduction-calibration-2.md`. Every acceptance item that
adds a gate carries a planted failure, and any `audits/` byte change recomputes
the `docs/artifacts.md` audits row. The live sitting lands on a second pull
request from `work/fresh-deduction-calibration-2-run`.

## Record impact

Adds a second calibration mode and one dated manifest section; adds a
measurement record under `audits/` when the sitting runs; refreshes the
rehearsal double's committed usage profile, a test fixture and not a recording.
The arm-surface digest moves because the instrument is in `ARM_SURFACE_SOURCES`
(`:4296-4304`): a fresh stamp before the fifth run, not a re-record, and
`llm/featherless_client.py` is not in that set, so the predecessor's
`finish_reason` change stays digest-neutral. No recording, report, DTO, metric
or weight byte moves; no experiment becomes ON; no adopting record; the
held-out record at `MANIFEST_PATH` is untouched.

## Validation

`uv run pytest tests/experiments -q` (fake and replay doubles only, at $0), then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.
Neither the live calibration nor the live evaluation is a check here.

## Results

Acceptance items 1 to 7 and 10 are implemented and verified offline, at $0, by
the implementer session. Items 8, 9 and 11 all depend on the live sitting, which
this card's Constraints reserve to a separate runner session ("The runner of the
sitting is not this card's implementer"), so they stay unchecked and the card
stays `active`; what each of them still needs is stated under **What is not
done** below.

That paragraph and the two sections below it are the implementer's record and
are left as written. The runner session ran the sitting on 2026-09-15 and closed
items 9 and 11; item 8 was still open, for a reason the sitting found rather
than for the one the implementer anticipated. It is now closed by
[the limits card](fresh-deduction-limits-5.md) and this card is `done`. See
**The live sitting (2026-09-15)** and **Item 8 closed by the fifth
authorization's limits card (2026-09-15)** below.

### Item 8 closed by the fifth authorization's limits card (2026-09-15)

Closed by [the limits card](fresh-deduction-limits-5.md), which is where the
sitting's hand-back landed: the refresh moves an owner-authorized ceiling, and
that is the owner's on a card rather than the runner's in a report.

`tests/experiments/deduction_usage_profile.json` is now this sitting's own 720
calls over 120 units, rebuilt by the documented `--refresh-usage-profile`
command, and `CALIBRATED_UNIT_INPUT_TOKENS` / `CALIBRATED_UNIT_OUTPUT_TOKENS`
moved with it in the same commit, from the three stopped runs' 24,282 / 3,116 to
this sitting's **38,440 / 4,176**. Those two maxima moved three authorized
ceilings, copied verbatim from
[the fifth authorization](fresh-deduction-authorization-5.md)'s Constraints
table: `AUTHORIZED_RUN_MAX_INPUT_TOKENS` 3,710,000 to **3,844,000**,
`AUTHORIZED_RUN_MAX_OUTPUT_TOKENS` 459,000 to **422,000** (it FALLS, because the
rule is followed and v4 made units smaller on output) and
`AUTHORIZED_UNIT_MAX_INPUT_TOKENS` 106,000 to **116,000**. The per-unit output
ceiling, the turn cap and the vote cap did not move.

The 27 red cases this directory's `CALIBRATION.md` enumerated are settled there
as well, in the three classes it named: the eleven feasibility refusals by the
re-sized ceilings and by pinning the two spent calibration modes to the profile
they were sized on, the eight archived-FAULT replays by committing the stopped
runs' rows as `tests/experiments/deduction_stopped_runs_usage_profile.json` and
pointing them at it, and the eight arithmetic cases by following the constants.
The pin this card named,
`test_the_calibration_is_the_largest_unit_the_archives_charged`, passes on the
refreshed profile.

The last limitation below — "`CALIBRATED_UNIT_INPUT_TOKENS` and
`CALIBRATED_UNIT_OUTPUT_TOKENS` are still the three stopped live runs' figures"
— is superseded by that commit and left as written, as the record of what was
true when this card reported.

### Where this sits

`experiments/` is an offline measurement harness whose outputs are artifacts
rather than behaviour (`docs/architecture.md` §Packages, "offline measurement
harnesses write separate artifacts"), so nothing here moves an engine, agent or
meeting byte and the four import-linter contracts of §Enforced boundaries are
untouched. The design this mode serves is
[the preregistration](../../audits/deduction-candidate/preregistration.md) and
[the execution manifest](../../audits/deduction-candidate/execution-manifest.md);
the manifest's frozen analysis — `PRIMARY_OUTCOME`, `DECISION_RULE`,
`WRONGFUL_EJECTION_TRADEOFF`, `MINIMUM_ACTIONABLE_EFFECT_UNITS` and `STOP_RULE` —
is byte-identical, which
`test_the_manifest_quotes_the_frozen_analysis` and
`test_the_stop_rule_still_says_a_truncation_is_a_stop` hold.

### Decisions

1. **Two modes in a table, not two sets of constants read independently.**
   `CalibrationMode` holds a mode's seeds, limits, sampling and clause as one
   value, `CALIBRATION_MODES` carries both, and `calibration_mode_for` accepts a
   calibration only when all three sizing values are ONE mode's. Five constants
   read independently would authorize the crossings nobody approved, which is
   how a sixty-seed draw ends up under ceilings sized for ten units.
2. **The draw is a list of records, not a bigger record.** `CalibrationSet`
   still binds one record and still runs every per-record check;
   `CalibrationDraw` is a sequence of them and `verify_calibration_draw` fills
   the seed count across `CONVERTED_BANDS` in list order. `verify_calibration_set`
   gained one keyword, `draw_at_most`, off by default — so the single-record
   path keeps its own "this record accepts 50 and I draw 51" refusal
   (`test_a_single_record_draw_still_refuses_a_record_it_cannot_fill`) and the
   "ran out of seeds" refusal lives over the whole draw, where the question is
   answerable.
3. **The truncation relaxation is a constructor flag on the client, defaulted
   off.** `_InstrumentClient(truncation_is_a_measurement=...)` and
   `_build_harness(truncation_is_a_measurement=...)`; `run_instrument` and
   `run_dry` never pass it, and `run_calibration` passes the matched mode's
   value. It reaches the cap branch of `_unusable_response` only: the identity
   branch still returns `ProviderIdentityMismatch` in this mode.
4. **The leak detector is scoped to the IMPOSTOR role, and its error is
   published in both directions.** A crewmate naming its own role is every
   crewmate's opening line; counting it would report the roster rather than a
   leak, and the figures the diagnosis published (2 of 13 candidate games, 0 of
   39 reference turns) are impostor self-tells. `ROLE_LEAK_RULE` says so and
   says what the rule cannot do. It was published as a FLOOR and is not one:
   the round-1 review corrections below found a conditional self-reference
   scoring as a confession, added the conditional governors that count it out,
   and reworded the rule and the manifest's pre-declaration to say the count is
   an estimate carrying error in both directions.
5. **`clears_the_feasibility_gate` now means the proposal's own claim, and the
   old comparison is reported beside it.** The card asks the proposal's
   feasibility check to run against the CALIBRATION's maxima; that check is
   cleared by construction, so the signal the fixture-vs-measurement case held
   would have been lost. It moved to a second field,
   `clears_the_committed_profiles_gate` / `committed_profile_refusal`, and
   `test_a_fixture_sized_proposal_says_it_clears_no_gate` reads it — the
   perturbation is unchanged, only the field it names.
6. **The mode is selected by `--calibration-mode`, and the second mode refuses
   `--calibration-record`.** The draw is `CONVERTED_BANDS` in order plus the
   seed count, with nothing left to the runner, so a flag that half-chose it
   would make the draw a runner decision.

### Verification

Every command below ran on this branch at the commit its section names, with the
fake provider, the replay double or no provider at all. No live provider call
was made by this card and `scripts/verify_ml_evidence.py --complete` was not run.

The card's Validation section, in order, run with `.venv/bin/python` (the
interpreter `uv run` selects on this worktree):

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 473 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 59 work cards` |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5` (the 7 absent are the evidence branch a fresh clone does not carry); `--complete` was NOT run |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 — ruff, ruff format, lint-imports (4 contracts kept), `validate_task_docs.py`, `generate_prompts.py --check` (390 in sync), strict mypy, 7,806 passed / 20 skipped / 3 xfailed, and the frontend leg 515 tests in 19 files |

`tests/experiments/test_fresh_deduction_instrument.py` alone: 387 passed, of
which 56 are this card's.

**The two $0 end-to-end sittings.** Both ran from this branch; neither output is
committed.

The fake provider, through the documented command:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --calibrate --calibration-mode 2026-09-15 \
  --output-dir <tmp>/units --json <tmp>/fake.json
```

exit 0; `mode 2026-09-15`, 120 units, 720 completions, `total_cost_usd 0.0`,
`dry_run true`; inputs `manifest-band-3000-3999.json` (50 seeds) then
`manifest-band-5000-5999.json` (10); role split on each arm
`turn/CREWMATE 120, turn/IMPOSTOR 60, ballot/CREWMATE 120, ballot/IMPOSTOR 60`
draws — sixty impostor ballot draws an arm, which is the owner's decision-7 bar.

The replay double, over the archived per-call counts: 120 units, $0.00,
`measured_max_unit_output_tokens 3,384`, proposal `run_max_output_tokens
343,000` against the 100 x 3,384 + 4,096 = 342,496 the gate requires — the
in-flight term, in a number. The candidate arm's role split reads
`turn/IMPOSTOR draws 60, output mean 958.4, max 1,455` against
`turn/CREWMATE draws 120, mean 757.6`, and its `free_text` samples are 43 and 97
against those 60 and 120 draws, which is the denominator rule doing its work: a
fail-softed turn is a draw that produced no text.

And the refresh path over that output, which makes no call:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile <tmp>/replay.json --profile-out <tmp>/profile.json
```

720 call rows, 120 unit rows, `built_from.mode 2026-09-15`, `built_from.records`
`[("3000-3999", 50), ("5000-5999", 10)]`. The COMMITTED profile
(`tests/experiments/deduction_usage_profile.json`) is deliberately unchanged —
see **What is not done** below.

### Planted and perturbed failures

Each new gate carries a case that fails on the defect it claims to catch. All of
them are committed, not demonstrated and reverted.

| Gate | Planted case | Test |
| --- | --- | --- |
| One mode whole, no crossing | sixty seeds under the 2026-09-14 ceilings | `test_sixty_seeds_under_the_first_modes_limits_are_refused` |
| One mode whole, no crossing | five seeds under the calibration-2 ceilings | `test_five_seeds_under_the_second_modes_limits_are_refused` |
| One mode whole, no crossing | each mode drawing at the other's caps | `test_either_mode_drawing_at_the_others_caps_is_refused` |
| The crossing is refused offline too | a fake-provider rehearsal of a crossing | `test_a_crossing_is_refused_on_the_rehearsal_path_too` |
| The clause authorizes the mode | the committed manifest with the second sentence removed | `test_a_manifest_without_the_second_clause_refuses_it` |
| The draw never reads the held-out record | `MANIFEST_PATH` named among the draw's records | `test_the_held_out_record_is_refused_by_name_inside_a_draw` |
| The draw is sixty or it is a stop | sixty seeds from one fifty-seed record | `test_a_draw_that_runs_out_of_accepted_seeds_is_refused` |
| Development data only | the second record flipped back to `held_out` | `test_a_status_that_is_not_development_stops_the_draw` |
| The generator still makes these inputs | one digest moved in the record the draw spills into | `test_a_moved_digest_stops_the_draw_by_seed` |
| The live path still stops on a truncation | a completion at its cap, both signals, on the run's wrapper | `test_the_live_path_still_stops_on_a_truncation` |
| A foreign checkpoint stops in every mode | a truncated completion from another model | `test_the_identity_branch_still_stops_in_the_measurement_mode` |
| The leak detector's three shapes | two first-person statements and the rebuttal counted out | `test_the_two_positive_shapes_are_counted`, `test_the_rebuttal_the_diagnosis_counted_out_is_not` |
| The role split cannot guess an author | a ledger row naming a speaker the unit holds no role for | `test_a_call_no_role_can_be_read_off_is_refused` |
| The ceilings pay for this draw | the first mode's 12,000 per-unit output against a 15,360 schedule | `test_the_first_modes_per_unit_output_cannot_pay_for_this_draw` |
| The proposal carries the in-flight headroom | 4,590 over a hundred units | `test_a_hundred_units_of_the_calibrations_largest_unit` |
| The gate reads the figures it is handed | the same limits against two calibrated unit sizes | `test_the_gate_reads_the_figures_it_is_handed` |
| The draw is not a runner decision | `--calibration-record` passed in the second mode | `test_the_second_mode_refuses_a_single_record_flag` |

### How the 2026-09-14 hand-back is settled

[The limits card](fresh-deduction-limits-4.md) handed back one residual: the
fourth authorization published 459,000 for a hundred units while its own largest
unit needs 4,590 x 100 + 4,096 = 463,096, and the gate accepts
`AUTHORIZED_LIMITS` on this tree only because `deduction_usage_profile.json`
still carries the older 3,116.

The CAUSE is closed here, in the rule that writes such numbers:
`ceiling_proposal` now adds the in-flight headroom term the gate enforces, so a
proposal can no longer publish a run-level output ceiling the gate would refuse,
and `test_a_hundred_units_of_the_calibrations_largest_unit` plants exactly that
arithmetic — 4,590 over a hundred units must propose at least 464,000.

The NUMBER stays where it is. 459,000 is the owner's, on the fourth
authorization card, and re-sizing it is the fifth authorization's decision on
the profile this calibration's sitting refreshes; nothing here moves an
authorized figure. So
`test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit` keeps
its plant and its meaning, and its docstring now records where the cause was
closed and what is still outstanding. The other two dependent tests are updated
rather than deferred:
`test_the_calibration_is_the_largest_unit_the_archives_charged` is unchanged and
still green, because the two calibrated constants move only when the committed
profile does; and the profile's own round-trip case gains a second-mode
counterpart, `test_the_refresh_path_reads_a_second_mode_output`, which drives
`--refresh-usage-profile` over a calibration-2 payload at $0 and checks the
720 call rows, the 120 unit rows, the `mode` and the per-record `records` block.

### What is not done, and why

* **Item 8 (the profile refresh).** The path works for calibration-2 output and
  is tested; the REFRESH itself needs the sitting's measured numbers.
  Refreshing the committed profile from a fixture-driven or replay-driven
  rehearsal would lower `CALIBRATED_UNIT_INPUT_TOKENS` and
  `CALIBRATED_UNIT_OUTPUT_TOKENS` to a serialisation length and quietly widen
  the feasibility gate, so it is deliberately not done here. The manifest's
  dated section says the refresh belongs to the sitting.
* **Item 9 (the committed aggregates).** The report shape, the per-unit usage
  rows and `assert_report_holds_no_prefix_bytes` over the payload are delivered
  and tested; the bytes under
  `audits/deduction-candidate/calibration-2-<date>/` are the sitting's output
  and land with it.
* **Item 11 (the live sitting).** A separate runner session, on
  `work/fresh-deduction-calibration-2-run`, after this pull request merges.

### Review corrections, round 1 (2026-09-15)

Six blocking findings, four distinct defects — two of the six are a second
lens's reading of the same Codex P1. All four are repaired at `0eb5eeb8`; no
finding was refuted. Every command below ran on this branch at `0eb5eeb8`, with
the fake provider, the replay double or no provider at all; the only later
change is this card's own prose. No live provider call was made and
`scripts/verify_ml_evidence.py --complete` was not run.

**1. The truncation tally had no enforcing test.** The reviewer neutered the
tally in `_role_split_rows` (`if False and any(...)`) and `pytest
tests/experiments -q` still reported 473 passed, identical to clean: every case
read a sitting with zero truncations, so `truncations == 0` and
`truncations_by_finish_reason == {}` held whether the counter worked or not, and
nothing drove a truncating provider through the mode at all. This is the
sitting's flagship measurement, so it is now driven end to end.
`TruncatedCompletionProvider` (`tests/experiments/burned_call_double.py`) cuts a
call off at its own `max_tokens`, reports `finish_reason="length"` and re-raises
with the usage the endpoint billed — the shape the fourth run stopped on — and
`TestATruncationIsMeasuredEndToEnd` runs a whole 120-unit sitting against it
through `run_calibration` in this mode. Ten planted truncations: one turn cut
across BOTH of its attempts, which is how the manager's placeholder turn is
reached rather than its retry, and eight consecutive ballots, a window chosen
because it spans the first pair of units and so reaches both arms and both
hidden roles. The case pins the entire role-split tally as a mapping —
`repaired_clock` turn/CREWMATE 2, ballot/CREWMATE 3, ballot/IMPOSTOR 2;
`combined_accounts` ballot/CREWMATE 2, ballot/IMPOSTOR 1; zero on the three rows
that drew none — each with `{"length": n}`, and beside it the fail-soft: eight
defaulted votes, one defaulted turn, nine defaults attributed to validation and
none to a deadline, and ten billed-and-refused attempts in the ledger. With the
tally disabled the mapping goes to zeros and the case fails.

The window is a window for a reason worth recording: three truncated turns in
one unit spend 12,288 output tokens and the next 4,096-token pre-flight exceeds
the mode's own 16,000 per-unit output ceiling, which stops the sitting. The
relaxation makes a truncation a datum, not free.

**2. The `records=` override could name a non-canonical draw.** Reproduced at
`63dd6e7c`: `verify_calibration_draw(records=[band-5000, band-3000])` drew fifty
seeds of the 5000 band and ten of the 3000 band, seeds not ascending, and
`records=[band-3000, band-3000]` returned sixty draws over fifty distinct seeds
— ten prefixes rendered twice and reported as sixty paired seeds. Both verified
clean, and both reach the live path through `assert_ready_for_a_calibration` and
`run_calibration`, which is the pre-flight the manifest documents as the gate.
`_draw_in_converted_order` now holds a supplied list to `CONVERTED_BANDS`' own
order with no record named twice, before a prefix is rebuilt. Membership stays
`_converted_band_for`'s, so the held-out record is still refused BY NAME and
first. Planted: `test_a_record_named_twice_is_refused`,
`test_a_record_list_in_another_order_is_refused`, and
`test_the_live_capable_preflight_refuses_the_same_two_lists`, which puts both
lists through the two entry points that can spend.

**3. The in-flight headroom plant was inert.** Its fixture set
`mean_unit_output_tokens` equal to the maximum, 4,590, so the mean rule
(100 x 4,590 x 1.5 = 688,500) dominated the headroom rule
(100 x 4,590 + 4,096 = 463,096) and the proposal was 689,000 either way: the
case passed with `+ sampling.turn_max_tokens` deleted. The fixture is now five
units averaging 2,000 with a 4,590 maximum, so the mean branch is 300,000 and
the headroom branch decides the number; the case asserts that inequality
explicitly rather than leaving a reader to re-derive which branch bound.
Verified by perturbation: with the term deleted the proposal is 459,000 and
`test_a_hundred_units_of_the_calibrations_largest_unit` fails
`assert 459000 >= 464000`.

**4. `ROLE_LEAK_RULE` claimed a floor it did not have.** Reproduced at
`63dd6e7c`: `states_own_role_or_kill("If I am the impostor, why would I report
the body?", role="IMPOSTOR")` returned True, and so did a supposition split by a
semicolon, which `_SENTENCE_SPLIT` does not treat as a boundary. The guard held
attribution and negation and no conditional, so a deflection scored as a
confession — and the same predicate drives `opens_with_a_self_tell`, so BOTH
reported columns inflated. An over-counting detector is not a floor. Repaired on
both halves the finding offered: `_ATTRIBUTED_TO_ANOTHER` is renamed
`_NOT_AN_ASSERTION` and gains a third family (`if`, `unless`, `whether`,
`suppose`/`assume`/`imagine`/`pretend` and their forms, `hypothetical*`,
`were I`, `why|how|what would`), and the rule string and the manifest's
pre-declaration now say the count is an ESTIMATE carrying error in BOTH
directions and is not a floor — which is honest about the residual the card's
own Limitations already admitted, a rebuttal spread across two sentences.
Planted both ways: `test_a_supposition_or_a_question_is_not_a_confession` counts
out four deflections on both columns, and
`test_the_guard_reaches_only_what_governs_the_words` keeps a confession with a
trailing conditional counted, because the guard is a prefix check and a governor
that trails the statement governs nothing.

**Gates, at `0eb5eeb8`.**

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 483 passed (473 before, plus this round's 10) |
| `.venv/bin/python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 59 work cards` |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; `--complete` was NOT run |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 |

**Record impact of this round.** One `audits/` byte change — the manifest's leak
pre-declaration — so the `docs/artifacts.md` audits row is re-derived with the
change staged: the tracked `audits/` inventory is 211 files and 15,118,706
bytes, up 361 from 15,118,345. No recording, report, DTO, metric or weight byte
moves, no prompt byte moves, no experiment becomes ON, and the held-out record
at `MANIFEST_PATH` is untouched. The arm-surface digest moves again, for the
same reason the card already declares:
`experiments/fresh_deduction_instrument.py` is in `ARM_SURFACE_SOURCES`.

**What is still not done** is unchanged: items 8, 9 and 11 belong to the live
sitting, which the Constraints reserve to a separate runner session. The card
stays `active`.

### Review corrections, round 2 (2026-09-15)

Two blocking findings, ONE defect: two lenses read the same hole in round 1's
repair of Codex P1. It is repaired at `f2f52e5a`; neither finding was refuted,
and the round-1 claim that drew them was indeed false. Every command below ran
on this branch at `f2f52e5a`, with the fake provider or with no provider at
all, and the only later change is this card's own prose; no live provider call
was made and `scripts/verify_ml_evidence.py --complete` was not run.

**The defect: an ordered subsequence is not the draw.** Round 1 held a supplied
`records` list to `CONVERTED_BANDS`' order with no record named twice, and
acceptance item 2 then claimed the override "cannot name a draw the card does
not authorize". That does not follow, because `CONVERTED_BANDS` holds THREE
development records — 3000-3999, 5000-5999 and 6000-6999, each `development`
with fifty accepted seeds — so a list may be ascending, name nothing twice, and
still skip a band. Reproduced at `74b9eea6`, on the helper and on both
live-capable entry points:

| Records | At `74b9eea6` | Seeds drawn | Authorized |
| --- | --- | --- | --- |
| `[band-5000, band-6000]` | ACCEPTED | 50 of 5000 then 10 of 6000, last seed 6010 | no |
| `[band-3000, band-6000]` | ACCEPTED | 50 of 3000 then 10 of 6000, last seed 6010 | no |
| `[band-3000, band-5000]` | ACCEPTED | 50 of 3000 then 10 of 5000, last seed 5009 | yes |

`CALIBRATION_2_CLAUSE` authorizes "the first sixty accepted seeds of the
converted bands, taken in the order those bands were converted", which is the
third row and only the third. The first two are a different sixty seeds under
the same authorization — the same defect class as Codex P1, which round 1 had
therefore only partly closed.

**The repair: a PREFIX, not a subsequence.** `_draw_in_converted_order` now
requires the supplied list to be `CONVERTED_BANDS` from its first record
onwards with none skipped — position *i* must be `CONVERTED_BANDS[i]` — checked
before any prefix is rebuilt, with the repetition refusal kept ahead of it so
`[band-3000, band-3000]` still fails by name. With the greedy fill in
`verify_calibration_draw` unchanged, that turns the drawn seeds into a function
of `paired_seeds` alone: an accepted `records` list draws EXACTLY what the
default draws, and the override can only shorten the list of records the same
draw may spill into. That is the property acceptance item 2 now claims, and the
wording of both the item and the helper's docstring — which had said
"SUBSEQUENCE" — is corrected to it.

**Planted.** Three cases, all committed:
`test_a_record_list_that_skips_a_converted_record_is_refused` puts both lists
through the helper; `test_the_live_capable_preflight_refuses_a_band_skipping_list`
puts both through `assert_ready_for_a_calibration` and `run_calibration`, the
two paths that can spend; and
`test_only_a_prefix_of_the_converted_records_is_accepted` enumerates every
ordered arrangement of the converted records up to their own length,
repetitions included, asserting that exactly the two prefixes long enough to
fill sixty are accepted and that each accepted draw's seeds equal the default
draw's. The property case exists because round 2 found this shape by
enumerating, where round 1 had reasoned from the two shapes it had reproduced;
a rule this one is worth checking exhaustively, since the list it ranges over
is three records long. Verified by perturbation: with the prefix comparison
replaced by round 1's "not earlier than any record already seen" test, all
three new cases go red and round 1's nine cases in the class stay green.

**One consequence, declared rather than absorbed.** The rule is uniform, so the
first calibration's `--calibration-record` can now name only
`CONVERTED_BANDS[0]` — its default, and the record the 2026-09-14 sitting drew
from. `CALIBRATION_CLAUSE` reads "a converted band", so this is NARROWER than
that mode's authorization. It is deliberate: a narrowed pre-flight can refuse a
spend that was approved but can never permit one that was not, and mode-aware
membership would have left the 60-seed case safe only by arithmetic (a
one-record draw cannot fill sixty today) rather than by rule, which is the
defect class being closed. The flag's `--help` and the helper's docstring both
say so.

**Gates, at `f2f52e5a`.**

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 486 passed (483 before, plus this round's 3) |
| `.venv/bin/python scripts/validate_task_docs.py` | `390 historical phase tasks and 390 prompts; 59 work cards` |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, `docs/ml-program.md` and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5`; `--complete` was NOT run |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0 |

**Record impact of this round.** No `audits/` byte moves, so the
`docs/artifacts.md` audits row is unchanged from round 1's 211 files and
15,118,706 bytes; the manifest's sentence that the draw is "the list and the
count, with nothing left to the runner" needed no edit, because this round is
what makes it true. No recording, report, DTO, metric or weight byte moves, no
prompt byte moves, no experiment becomes ON, and the held-out record at
`MANIFEST_PATH` is untouched. The arm-surface digest moves again, for the reason
the card already declares: `experiments/fresh_deduction_instrument.py` is in
`ARM_SURFACE_SOURCES`.

**What is still not done** is unchanged: items 8, 9 and 11 belong to the live
sitting, which the Constraints reserve to a separate runner session. The card
stays `active`.

### The live sitting (2026-09-15)

Run once by the runner session on `work/fresh-deduction-calibration-2-run`,
based at `0495c08a`, under the manifest's calibration-2 clause and the mode's
own limits. It began at `2026-09-15T13:39:46Z`, ended at `2026-09-15T15:43:16Z`
and exited 0 with all 120 units complete and all 720 calls resolved. It was not
re-run, resumed or restarted. The whole record — the design, the input binding,
every table below and the commands that reproduce them — is
[the archive](../../audits/deduction-candidate/calibration-2-2026-09-15/CALIBRATION.md);
this is the summary the card's item 11 asks for. **It measured nothing about
the candidate's merit**: no grader ran, no paired statistic was computed and no
meeting outcome is recorded.

**The inputs, bound before the spend.** `manifest-band-3000-3999.json` at
`ca4cd057acb2119646190fb6fff923a897ec207d5f54c491c3e1dfae0944cf3c` (all 50
accepted seeds, 3000–3057) and `manifest-band-5000-5999.json` at
`4fc831dafeda0a6ee7fc311e6557c149506be1fabcf05c69b2117ddb436f7711` (the first
10, 5000–5009); both `status: development`, both byte-identical to
`origin/main`'s by `git diff --exit-code`. The held-out record was not read.

**The role-split profile.** Per arm, per call type, by the author's hidden role:

| Arm | Call | Role | draws | out mean | out p95 | out max | prose field | samples | chars mean | chars max |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | turn | CREWMATE | 120 | 329.7 | 436 | 520 | `free_text` | 120 | 232.3 | 518 |
| `repaired_clock` | turn | IMPOSTOR | 60 | 182.1 | 326 | 452 | `free_text` | 60 | 201.7 | 400 |
| `repaired_clock` | ballot | CREWMATE | 120 | 100.9 | 123 | 160 | `rationale_text` | 120 | 107.9 | 201 |
| `repaired_clock` | ballot | IMPOSTOR | 60 | 98.1 | 115 | 123 | `rationale_text` | 60 | 105.2 | 193 |
| `combined_accounts` | turn | CREWMATE | 120 | 472.6 | 805 | 1,884 | `free_text` | 120 | 401.6 | 4,258 |
| `combined_accounts` | turn | IMPOSTOR | 60 | 383.6 | 700 | 1,101 | `free_text` | 60 | 245.9 | 467 |
| `combined_accounts` | ballot | CREWMATE | 120 | 97.1 | 124 | 135 | `rationale_text` | 120 | 133.7 | 262 |
| `combined_accounts` | ballot | IMPOSTOR | 60 | 85.8 | 111 | 123 | `rationale_text` | 60 | 101.4 | 240 |

The `claims[].reason` rows are in the archive; per unit the candidate arm
charged mean 22,733.8 input / 1,608.9 output (max 38,440 / 4,176) against the
reference arm's 20,862.4 / 1,141.5 (max 25,604 / 1,526).

**The truncation rate, on the denominator the owner's decision 7 named.** Zero
truncations in sixty impostor-authored candidate ballot draws: 0.00%, Wilson
95% [0.00%, 6.02%] (`scripts/paired_stats.py:115`). Arm-wide on the candidate:
0 of 360 draws, [0.00%, 1.06%]; the reference arm the same. `finish_reason` is
`{"stop": 360}` on each arm, observed truncations 0, inferred 0, signal
disagreements 0. The fourth run's figure on the same denominator was 1 of 13,
7.7%, [1.4%, 33.3%]. The candidate ballot's largest draw is 135 output tokens
against its 1,024 cap, where the fourth run resolved at 624 and was refused at
1,024: the runaway the diagnosis named did not recur at revision v4.

**The impostor self-tell**, which is the behaviour behind that stop rather than
the stop: 39 of 60 impostor-authored candidate ballots still OPEN by naming
that role or a kill (65.0%), against the fourth run's 11 of 12; the reference
arm is 9 of 60 (15.0%) against its 2 of 13. The impulse is intact and is now
bounded to about a hundred characters, which is the reference template's own
result.

**The pre-declared leak count.** `combined_accounts` 1 leaking turn in 1 of 60
units; `repaired_clock` 0 of 60. The fourth run's were 2 of 13 candidate games
and 0 of 39 reference turns. `ROLE_LEAK_RULE` is quoted in the payload and says
in its own words that the count is an estimate carrying error in both
directions and is not a floor.

**Refusals, defaults, transport.** Zero on both arms in every category: 0
charged failed attempts, 0 defaulted turns, 0 defaulted votes, 0 by validation,
0 by deadline, 0 degraded openings, 0 retried calls, 0 unaccounted attempts. All
720 `calls` rows read `resolved`.

**Pace and usage.** 10.28 s per attempt pooled (8.91 reference, 11.65
candidate), 7,403.0 s of model work inside 7,409.8 s elapsed. Against the
calibration-2 limits: run input 2,615,769 / 4,500,000 (58.1%), run output
165,021 / 450,000 (36.7%), largest unit input 38,440 / 60,000 (64.1%), largest
unit output 4,176 / 16,000 (26.1%), model work 41.1%, elapsed 34.3%.
**$0.00 marginal.**

**The proposal**, for the hundred-unit design: per unit 116,000 input / 16,000
output, run 3,844,000 / 422,000. `clears_the_feasibility_gate: true` — which is
true by construction, the rule computing those figures from the same measured
maxima it checks them against — and `clears_the_committed_profiles_gate: true`,
which is not by construction: the same figures also clear this tree's committed
24,282 / 3,116, because this sitting's units are larger. The output floor
carries the in-flight headroom term this card added: 100 x 4,176 + 4,096 =
421,696 -> 422,000. The proposal authorizes nothing.

**Archive.** `audits/deduction-candidate/calibration-2-2026-09-15/`:
`calibration.json` (199,101 bytes), `unit-usage.jsonl` (120 rows),
`calibration-run.log` (whose stdout body is byte-identical to the payload, both
sha256 `ddb2073aaa34276e3a5da9f14c4a37c76ab9b5dfe937a6fabdb02504fa7c9188`) and
`CALIBRATION.md`. `assert_report_holds_no_prefix_bytes` was re-run over the
archived payload against all sixty rebuilt prefixes and passed; the credential
scan over every file returns zero on both the key's first six characters and
the whole key. No prefix, prompt or rendered output is committed: the sitting's
replays went to an `--output-dir` outside version control.

**Item 8 is NOT closed, and the reason is a finding rather than a deferral.**
The refresh command was run and its output compared against the committed
profile through a $0 rehearsal on the replay double: the rehearsal's proposal
moves from per unit 74,000 / 16,000 and run 3,139,000 / 343,000 on the committed
profile to per unit 116,000 / 16,000 and run 3,844,000 / 422,000 on the
refreshed one, reproducing this sitting's live proposal to the token. But the
refreshed profile's largest charged unit is 38,440 input / 4,176 output, and
moving `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` to it
makes `assert_limits_are_feasible` REFUSE two standing sets of ceilings:

| Ceilings | Units | Run input | Needs | Run output | Needs |
| --- | --- | --- | --- | --- | --- |
| `AUTHORIZED_LIMITS` (fourth authorization) | 100 | 3,710,000 | **3,844,000 — refused** | 459,000 | 421,696 — clears |
| `CALIBRATION_2_LIMITS` (this mode) | 120 | 4,500,000 | **4,612,800 — refused** | 450,000 | **505,216 — refused** |

`pytest tests/experiments -q` on the refreshed profile with both constants moved
is 27 failed, 459 passed: eleven are that refusal reaching cases written to
check something else, eight are the archived FAULT modes a clean sitting carries
none of, and eight are arithmetic following the constants — including
`test_the_enforcement_section_quotes_the_reservation_policy`, because
`RESERVATION_POLICY` embeds both constants in its own text and the execution
manifest quotes that string verbatim. Every repair available to a runner is
either moving an authorized ceiling or weakening the gate, and this card says in
its own words that "nothing here moves an authorized figure". So the refresh is
handed to the fifth authorization card with the numbers it needs — run-level
input at least **3,844,000**, run-level output at least **421,696** (459,000
already clears it), both constants to **38,440** and **4,176** in the same
commit as the profile — and no committed profile byte or calibrated constant
moved here. The card therefore stays `active`.

Two results worth separating from that. The open item of 2026-09-14 is CLOSED by
measurement on the OUTPUT dimension — 459,000 clears 421,696 with 37,304 to
spare, where that day's own largest unit needed 463,096 — and the binding
dimension moved to INPUT, where the largest unit grew from 35,232 (2026-09-14)
through 36,743 (run 4) to 38,440 here, because the v4 revision added bytes to
the candidate's prompts.

**Deviations.** Three, all recorded in the archive's own Deviations section: the
credential reached the process through `uv run --env-file <a 0600 file outside
the repository>` rather than the ambient shell, exactly as 2026-09-14 recorded;
the committed usage profile was not refreshed, for the reason above; and
`audits/deduction-candidate/checkpoint.md` gained a dated line naming the
sitting, which the first calibration did not add.

### Limitations

* The leak detector is a lexical rule over committed turn text, gated on the
  speaker's ground-truth role. It reads no intent, so an impostor that
  confesses in words its two shapes do not match is missed; and its guard is a
  same-sentence check, so an attribution, denial or supposition spread across
  two sentences ("p-1 accuses me. I am the impostor, apparently.") is counted.
  The per-arm figure is therefore an ESTIMATE carrying error in BOTH
  directions, not a floor. `ROLE_LEAK_RULE` says so in those words, it is
  quoted in every calibration-2 output, the manifest's pre-declaration says the
  same, and the owner's decision 9 makes it a reported diagnostic rather than a
  gate for exactly this kind of reason.
* The guard's third family — conditional, hypothetical and interrogative
  governors — was added by the round-1 review corrections, which reproduced a
  deflection ("If I am the impostor, why would I report the body?") scoring as
  a confession on both reported columns. It is a prefix check like the other
  two, so a governor that trails the statement governs nothing and the
  confession is still counted; that asymmetry is tested in both directions.
* The role split's prose lengths are over AUTHORED payloads and its truncation
  denominator is DRAWS, which is the right pair for the rate but means the two
  numbers in a row have different denominators. The field names say which is
  which (`draws` against `lengths[].samples`) and `CALIBRATION_2_CLAUSE` and the
  manifest's section both state the rule.
* `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are still
  the three stopped live runs' figures. Every feasibility claim in this card's
  table is against those, and they move when the sitting's profile refresh does.
* The wall is the binding limit of the sitting and has a 1.14x margin at the
  slowest arm pace measured. A calibration has no checkpoint and no resume, so a
  stop is reported with its partial accounting and a second sitting needs the
  owner's say.
* The arm-surface digest moves, because `experiments/fresh_deduction_instrument.py`
  is in `ARM_SURFACE_SOURCES`. That is a fresh stamp before the fifth run, not a
  re-record: no recording, report, DTO, metric or weight byte moves, no
  experiment becomes ON, and the held-out record at `MANIFEST_PATH` is untouched.
