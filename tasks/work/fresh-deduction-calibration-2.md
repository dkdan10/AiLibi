# Run a second development calibration sized for the impostor ballot mode

**Status:** ready

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

- [ ] A SECOND dated clause and constant set beside the 2026-09-14 set, not
  replacing it: `CALIBRATION_2_PAIRED_SEEDS = 60`, `CALIBRATION_2_LIMITS`, and
  `CALIBRATION_2_SAMPLING` equal to `AUTHORIZED_SAMPLING` (`:426`), so the draw
  is turn 4,096 / vote 1,024 and what is measured is what the fifth run would
  do; plus a `CALIBRATION_2_CLAUSE` the manifest quotes verbatim. The first
  mode keeps its own sampling, seeds and ceilings, and
  `assert_calibration_is_authorized` (`:1394`) accepts exactly one of the two
  sets whole and refuses every crossing, with a planted failure each: five seeds
  under the second's limits, sixty under the first's, either mode drawing at the
  other's caps.
- [ ] The draw: accepted seeds ascending across `CONVERTED_BANDS`
  (`experiments/held_out_prefixes.py:375-394`) in list order until sixty paired
  seeds are bound, so all fifty of the 3000-3999 record then 5000 to 5009 of
  the 5000-5999 record. Each record is verified by `verify_calibration_set`
  (`:2865`), each prefix held to the digest that record froze, the held-out
  record still refused by name (`_converted_band_for`, `:2836`), and the inputs
  block names every record with its sha256 and the seeds drawn from it. Planted:
  a `status` that is not `development`, a moved digest, and a draw that runs out
  of accepted seeds before sixty.
- [ ] In THIS mode a per-call truncation is a measurement, not a stop. The cap
  branch of `_unusable_response` (`:2413`) does not raise here, the truncated
  ballot or turn takes the meeting layer's existing fail-soft
  (`meetings/manager.py:2288,2298`; `:1916-1922`), and the call is counted per
  arm, per call type and per voter role with its `finish_reason`. The identity
  branch and the live path still stop: a planted failure proves a live
  evaluation invocation still raises `PerCallCapExceeded` on that response.
  `STOP_RULE` (`:619`) is not edited; the manifest's dated section says why.
- [ ] Role-split reporting: per arm, per call type, split by the voter's or
  speaker's hidden role, the completions and the mean, p95 and max of output
  tokens and of the character lengths of `rationale_text`, `claims[].reason` and
  `free_text`, plus the count of impostor-authored candidate ballots that open
  by stating their own role or kill. The truncation rate's denominator is
  impostor DRAWS, since a fail-softed ballot is a draw that produced no
  rationale. Counts and lengths only: no prose, prompt, prefix or outcome.
- [ ] The pre-declared leak diagnostic (decision 9): a detector over each unit's
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
- [ ] The Constraints table's limits are the mode's, and
  `assert_limits_are_feasible` (`:1203`) accepts them for 120 units: per-unit
  output 16,000 against a 15,360 schedule, per-unit input 60,000 against the
  24,282 largest archived unit (`:477`), run output 3,116 x 120 + 4,096 =
  378,016 against 450,000 and run input 2,913,840 against 4,500,000. Planted:
  the first mode's 12,000 per-unit output, which this draw cannot pay for.
- [ ] The ceiling proposal rule adds the in-flight headroom term: a proposed
  run-level OUTPUT ceiling is at least units x the measured maximum unit plus
  one turn cap, the term the gate enforces (`:1264-1273`), and the proposal's
  own feasibility check (`:5862-5870`) runs against the CALIBRATION's maxima
  rather than the tree's constants, with `CEILING_PROPOSAL_RULE` (`:5415`)
  stating it. Planted: 4,590 over 100 units, which must propose 464,000 or more.
- [ ] The rehearsal double's usage profile is refreshed from this calibration
  by the documented `--refresh-usage-profile` command, and the dependent tests
  are updated with it rather than deferred again:
  `test_the_calibration_is_the_largest_unit_the_archives_charged`
  (`tests/experiments/test_fresh_deduction_instrument.py:4688`), the run-ceiling
  residual at `:4627` and the profile's own test at `:4786`. The two calibrated
  constants (`:477-478`) move with it, and 2026-09-14's eight-red-test hand-back
  is settled in Results.
- [ ] Aggregates only, committed under
  `audits/deduction-candidate/calibration-2-<date>/` with per-unit usage rows,
  in the shape the first calibration committed, with
  `assert_report_holds_no_prefix_bytes` (`:4178`) over the payload. Prefixes
  and rendered prompts are not committed; replays go to the runner's
  `--output-dir`, outside version control.
- [ ] The execution manifest gains a dated "Development calibration 2
  (2026-09-15)" section: the clause verbatim, the inputs and their records, the
  limits and sampling table, the truncation ruling scoped to this mode, and the
  leak column pre-declared for the fifth run. The frozen analysis strings stay
  byte-identical (test) and the 2026-09-14 section is not edited.
- [ ] The live sitting is run once, by a separate runner session on
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
