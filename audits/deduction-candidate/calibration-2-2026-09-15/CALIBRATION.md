# Second development calibration of the fresh-model deduction instrument, 2026-09-15

A bounded live measurement of what the fifth run would actually DRAW, on
development inputs, run once by a runner session on
[the second calibration card](../../../tasks/work/fresh-deduction-calibration-2.md)
(acceptance item 11) under the owner's decision 7 of
[the diagnosis of 2026-09-15](../../../tasks/diagnosis-2026-09-15-truncation-stop.md),
recorded in [the execution manifest](../execution-manifest.md)'s
"Development calibration 2 (2026-09-15)" section.

**This measured nothing about the candidate's merit.** No grader ran, no paired
statistic was computed and no meeting outcome is recorded anywhere in this
directory. The primary outcome, the decision rule and the minimum actionable
effect are untouched, and no unit of this calibration counts towards them. What
it measures is what one call and one unit CHARGE on each arm, split by the
author's hidden role, and how often a call runs past its output cap.

## The design

| Field | Value |
| --- | --- |
| Mode | `experiments/fresh_deduction_instrument.py --calibrate --calibration-mode 2026-09-15` |
| Inputs | the first sixty accepted seeds, ascending, across `CONVERTED_BANDS` in the order those bands were converted: all fifty of the 3000–3999 record, then 5000–5009 of the 5000–5999 record |
| Arms | both, `repaired_clock` then `combined_accounts`, sequential, seed ascending, both arms per seed before the next seed |
| Units | 60 paired seeds x 2 arms = 120 units, 720 calls |
| Provider / model | `featherless` / `Qwen/Qwen3.6-27B`, non-thinking, `json_object` |
| Prompt set | `qwen3_6_27b`, at `ACCOUNT_PROMPT_SET_REVISION` **v4** (`agents/strategic/prompts/loader.py`) |
| Sampling | turn 4,096 output at temperature 0.4; ballot 1,024 at 0.2 — `AUTHORIZED_SAMPLING` itself, which is the point: what is measured is the draw the fifth run makes |
| Limits | `CALIBRATION_2_LIMITS`: per unit 60,000 in / 16,000 out, run 4,500,000 / 450,000, 5 h model work inside a 6 h elapsed window |
| Transport bound | 4 attempts per call, 180 s per attempt — the run's own, unchanged |
| Truncation | a MEASUREMENT in this mode, not a stop (`CALIBRATION_2_CLAUSE`); the live run's `STOP_RULE` is unedited |
| Instrument | `instrument_sha256` `3478a68c7589b3d2436b87c86cfe30fc9700834b4e97aa394f701c0090819de6` |
| Held-out record | not read, not rendered, not touched: `verify_frozen_set` is never called on this path, and `verify_calibration_draw` refuses `held-out/manifest.json` by name |

**One sitting.** The calibration ran once, start to finish, and was not re-run,
resumed or restarted. It began at `2026-09-15T13:39:46Z`, ended at
`2026-09-15T15:43:16Z` and exited 0 with all 120 units complete and all 720
calls resolved. The card's Constraints authorize one calibration and no retry
beyond the instrument's own transport bound; no retry was needed, because no
attempt failed. A calibration has no checkpoint and no resume, and a second
sitting would need the owner's say.

## The input binding

Both records the draw spans were bound before any spend:

```sh
shasum -a 256 audits/deduction-candidate/held-out/manifest-band-3000-3999.json \
              audits/deduction-candidate/held-out/manifest-band-5000-5999.json
git diff --exit-code origin/main -- audits/deduction-candidate/held-out/manifest-band-3000-3999.json
git diff --exit-code origin/main -- audits/deduction-candidate/held-out/manifest-band-5000-5999.json
```

| Record | sha256 | Status | Accepted | Drawn |
| --- | --- | --- | --- | --- |
| [held-out/manifest-band-3000-3999.json](../held-out/manifest-band-3000-3999.json) | `ca4cd057acb2119646190fb6fff923a897ec207d5f54c491c3e1dfae0944cf3c` | `development` since 2026-09-10 | 50 (8 skipped) | all 50, seeds 3000–3057 |
| [held-out/manifest-band-5000-5999.json](../held-out/manifest-band-5000-5999.json) | `4fc831dafeda0a6ee7fc311e6557c149506be1fabcf05c69b2117ddb436f7711` | `development` since 2026-09-13 | 50 (3 skipped) | the first 10, seeds 5000–5009 |

Both `git diff --exit-code` invocations exit 0, so both files are byte-identical
to `origin/main`'s. The same two digests are recorded inside the output as
`input_records[].record_sha256`, so the report names the bytes it drew from.
Seeds 3000–3004 were rendered by the calibration of 2026-09-14, which changes
nothing: a converted band is development data from its conversion, not from its
rendering.

## The measured profile

Per arm and per call type, over the 720 completions. `n` is the completion
count; `p95` is the nearest-rank percentile the report's `percentile_rule`
states (index `ceil(0.95 x n) - 1` of the ascending sample, no interpolation).

### `repaired_clock` (reference arm)

| Call type | n | in mean | in p95 | in max | out mean | out p95 | out max | out cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| turn | 180 | 3,275.4 | 3,912 | 4,354 | 280.5 | 434 | 520 | 4,096 |
| ballot | 180 | 3,678.8 | 4,373 | 4,770 | 100.0 | 121 | 160 | 1,024 |

Per unit: input mean 20,862.4, max 25,604; output mean 1,141.5, max 1,526.
Arm totals: 1,251,743 input, 68,487 output over 360 attempts.

### `combined_accounts` (candidate arm)

| Call type | n | in mean | in p95 | in max | out mean | out p95 | out max | out cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| turn | 180 | 3,305.4 | 4,643 | 5,878 | 443.0 | 753 | 1,884 | 4,096 |
| ballot | 180 | 4,272.6 | 5,643 | 8,684 | 93.3 | 123 | 135 | 1,024 |

Per unit: input mean 22,733.8, max 38,440; output mean 1,608.9, max 4,176.
Arm totals: 1,364,026 input, 96,534 output over 360 attempts.

The candidate arm charges **1.41x** the reference arm's output (96,534 against
68,487) and 1.09x its input. On 2026-09-14 the same two ratios were 2.83x and
1.35x: the v4 revision's bounds are visible in the output ratio, and the input
ratio moved the other way because the candidate's ballot prompt grew.

**The candidate ballot no longer approaches its cap.** Its largest draw is 135
output tokens against the 1,024 cap — 13.2% — where the fourth run resolved at
624 and was refused at 1,024, and where 2026-09-14 measured 237. The candidate
TURN's largest draw is 1,884 against the 4,096 cap (46.0%), against the fourth
run's 1,900 at the same cap and 2026-09-14's 2,036 at the 2,048 cap it drew at.

## The role split

Per arm, per call type, split by the AUTHOR's hidden role: the draws, the output
tokens, and the character lengths of the fields that carry prose. The two
denominators differ on purpose — `draws` counts calls made, `samples` counts
authored payloads — so a fail-softed call is a draw that produced no text.
Nothing in this section is prose: it is counts and lengths.

### `repaired_clock`

| Call | Role | draws | out mean | out p95 | out max | truncations |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | 120 | 329.7 | 436 | 520 | 0 |
| turn | IMPOSTOR | 60 | 182.1 | 326 | 452 | 0 |
| ballot | CREWMATE | 120 | 100.9 | 123 | 160 | 0 |
| ballot | IMPOSTOR | 60 | 98.1 | 115 | 123 | 0 |

| Call | Role | Field | samples | chars mean | chars p95 | chars max |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | `free_text` | 120 | 232.3 | 364 | 518 |
| turn | CREWMATE | `claims[].reason` | 123 | 67.0 | 122 | 152 |
| turn | IMPOSTOR | `free_text` | 60 | 201.7 | 287 | 400 |
| turn | IMPOSTOR | `claims[].reason` | 60 | 58.7 | 86 | 105 |
| ballot | CREWMATE | `rationale_text` | 120 | 107.9 | 162 | 201 |
| ballot | IMPOSTOR | `rationale_text` | 60 | 105.2 | 153 | 193 |

### `combined_accounts`

| Call | Role | draws | out mean | out p95 | out max | truncations |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | 120 | 472.6 | 805 | 1,884 | 0 |
| turn | IMPOSTOR | 60 | 383.6 | 700 | 1,101 | 0 |
| ballot | CREWMATE | 120 | 97.1 | 124 | 135 | 0 |
| ballot | IMPOSTOR | 60 | 85.8 | 111 | 123 | 0 |

| Call | Role | Field | samples | chars mean | chars p95 | chars max |
| --- | --- | --- | --- | --- | --- | --- |
| turn | CREWMATE | `free_text` | 120 | 401.6 | 670 | 4,258 |
| turn | CREWMATE | `claims[].reason` | 115 | 100.8 | 184 | 236 |
| turn | IMPOSTOR | `free_text` | 60 | 245.9 | 365 | 467 |
| turn | IMPOSTOR | `claims[].reason` | 60 | 97.3 | 156 | 164 |
| ballot | CREWMATE | `rationale_text` | 120 | 133.7 | 249 | 262 |
| ballot | IMPOSTOR | `rationale_text` | 60 | 101.4 | 149 | 240 |

Three readings worth stating rather than leaving to a reader.

**The impostor ballot is no longer the long one.** The mechanism the diagnosis
named was role-conditioned: on the fourth run the candidate's impostor
`rationale_text` averaged 477 characters against the crew's 381 and reached
1,795. Here the candidate's impostor ballots average 101.4 characters against
the crew's 133.7 and reach 240 — the impostor draw is now the SHORTER of the
two, and the arm's whole ballot distribution sits an order of magnitude below
the cap. That is the v4 ballot bound doing what the reference template's bound
does; the reference arm's own figures (105.2 against 107.9) show the same shape.

**`claims[].reason` has its own denominator.** 123 samples over 120 reference
crewmate turn draws and 115 over 120 candidate crewmate turn draws: a turn may
carry more than one claim or none, so the claim row counts claims and the
`free_text` row counts turns.

**One candidate `free_text` is a long tail at 4,258 characters** against that
row's 401.6 mean and 670 p95, drawn by a CREWMATE. It cost 1,884 output tokens
— 46.0% of the turn cap — so it is a long turn well inside its cap rather than
a runaway, and it is the largest single output this sitting drew.

## Truncation

**Zero, on both arms, on every call type and for both roles.** No completion of
the 720 reached its output cap by either signal.

| Arm | Denominator | draws | truncations | rate | Wilson 95% |
| --- | --- | --- | --- | --- | --- |
| `combined_accounts` | impostor-authored ballot draws | 60 | 0 | 0.00% | [0.00%, 6.02%] |
| `combined_accounts` | all ballot draws | 180 | 0 | 0.00% | [0.00%, 2.09%] |
| `combined_accounts` | all draws | 360 | 0 | 0.00% | [0.00%, 1.06%] |
| `repaired_clock` | impostor-authored ballot draws | 60 | 0 | 0.00% | [0.00%, 6.02%] |
| `repaired_clock` | all ballot draws | 180 | 0 | 0.00% | [0.00%, 2.09%] |
| `repaired_clock` | all draws | 360 | 0 | 0.00% | [0.00%, 1.06%] |

The denominator the owner's decision 7 set the bar on is the first row: sixty
impostor-authored candidate ballot draws, which is the exposure a fifty-pair run
makes, at a 99.2% chance of seeing a 1-in-13 event. It saw none. The interval is
computed by `scripts/paired_stats.py`'s `wilson_interval`.

Read against the fourth run, whose stop this calibration was sent to measure:
1 truncation in 13 impostor-authored candidate ballot draws, 7.7%, Wilson 95%
[1.4%, 33.3%]. The two intervals overlap between 1.4% and 6.0%, so this sitting
does not exclude every rate the fourth run's interval admits; what it does
exclude is the point estimate. At 7.7% the chance of drawing sixty clean
impostor ballots is 0.8%, so a rate that high is close to ruled out, and
P(a clean 50-pair run) at the upper bound this sitting leaves (6.02%) is 4.5%
rather than the 1.8% the fourth run's point estimate gave.

### `finish_reason`, and the two signals

| Arm | rows | `finish_reason` | observed truncations | inferred truncations | disagreements |
| --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 360 | `{"stop": 360}` | 0 | 0 | 0 |
| `combined_accounts` | 360 | `{"stop": 360}` | 0 | 0 | 0 |

`observed` is the provider's own `finish_reason == "length"`; `inferred` is
`output_tokens >= max_tokens`, the comparison this instrument has always made.
Every one of the 720 rows carries `"stop"`, the two readings agree on every row,
and no row is silent — which is the finish-reason card's contribution showing up
as a measurement: on 2026-09-14 the reading did not exist and every archived row
reads null.

## The impostor self-tell

Impostor-authored ballots whose `rationale_text` OPENS by stating that role or a
kill that voter committed (`opens_with_a_self_tell`):

| Arm | self-telling ballots | impostor ballot draws | share |
| --- | --- | --- | --- |
| `combined_accounts` | 39 | 60 | 65.0% |
| `repaired_clock` | 9 | 60 | 15.0% |

The fourth run's figures on the same measure were 11 of 12 candidate (91.7%) and
2 of 13 reference (15.4%). So the self-tell is REDUCED on the candidate arm and
unchanged on the reference, and it has not gone away: the model still writes the
concealment plan from the private truth forward in about two impostor ballots in
three. What changed is that it now does so in about a hundred characters instead
of five hundred, which is why the truncation it used to cause did not recur. The
behaviour and the stop had one root and only one of them is closed.

## The public-transcript role leak

The pre-declared diagnostic of the owner's decision 9, counted by
`ROLE_LEAK_RULE`, which the payload quotes in full:

| Arm | leaking turns | units with a leaking turn | units |
| --- | --- | --- | --- |
| `combined_accounts` | 1 | 1 | 60 |
| `repaired_clock` | 0 | 0 | 60 |

The fourth run's count on the same rule was 2 of 13 candidate games and 0 of 39
reference turns. Here it is 1 of 60 candidate units and 0 of 60 reference units.

**The count is an ESTIMATE carrying error in BOTH directions and is not a
floor.** `ROLE_LEAK_RULE` says so in those words. The rule reads no intent, so an
impostor that confesses in words its two shapes do not match is missed; and its
guards see one sentence at a time, so an attribution, denial or supposition
spread across two sentences is counted. It is a reported diagnostic and not a
gate: no stop condition reads it, the decision rule does not mention it, and it
changes no primary outcome. The fifth run reports the same column, so the leak is
visible beside the result rather than argued about after it.

## Refusals, defaults and charged failed attempts

**Zero, on both arms, in every category.**

| Per arm | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| charged failed attempts (billed and refused) | 0 | 0 |
| defaulted turns | 0 | 0 |
| defaulted votes | 0 | 0 |
| defaults by schema validation | 0 | 0 |
| defaults by deadline | 0 | 0 |
| units with any default | 0 | 0 |
| degraded openings | 0 | 0 |
| completions | 360 of 360 | 360 of 360 |

Every one of the 120 units resolved all six of its calls, and the only
disposition present in the output's 720 `calls` rows is `resolved`. The
`union_tag_invalid` refusals the diagnosis of 2026-09-13 found on the candidate
arm did not recur at revision v4, as they did not at v3: zero in 360
candidate-arm attempts.

## Transport

| Per arm | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| attempts | 360 | 360 |
| retried calls | 0 | 0 |
| unaccounted attempts | 0 | 0 |
| aborted attempts | 0 | 0 |
| attempts by trigger | none | none |

720 sends produced 720 completions; the transport bound (4 attempts, 180 s each)
was never reached.

## Pace

10.28 s per attempt pooled over 720 attempts: 8.91 s on the reference arm and
11.65 s on the candidate. Model work totalled 7,403.0 s inside 7,409.8 s elapsed
— the calibration is sequential, so the two are the same clock less setup.

The sitting therefore ran at 1.68x the pooled pace of 2026-09-14 (17.23 s) and
1.88x the candidate arm's pace that day (21.85 s). The card sized the wall
against those figures and called it a 1.14x margin at the slowest arm pace
measured; the realised margin was 2.43x. At this pace the held-out design's ~600
sequential calls need about 1.7 h of model work against the 6 h the fourth
authorization allows.

## Actual usage against the calibration-2 limits

| Dimension | Charged | Ceiling | Used |
| --- | --- | --- | --- |
| run input tokens | 2,615,769 | 4,500,000 | 58.1% |
| run output tokens | 165,021 | 450,000 | 36.7% |
| largest unit input | 38,440 | 60,000 | 64.1% |
| largest unit output | 4,176 | 16,000 | 26.1% |
| model work | 7,403.0 s | 18,000 s | 41.1% |
| elapsed | 7,409.8 s | 21,600 s | 34.3% |

**$0.00 marginal**, the report's `total_cost_usd` and both arms' `cost_usd`, on
the same flat-rate subscription and for the same reason as the manifest's cost
statement.

## The ceiling proposal

Computed by `ceiling_proposal` and carried in the output as `proposal`, with
`CEILING_PROPOSAL_RULE` quoted beside it. For the held-out design's **100**
units:

| Ceiling | Proposed |
| --- | --- |
| per unit input | **116,000** |
| per unit output | **16,000** |
| run input | **3,844,000** |
| run output | **422,000** |

`clears_the_feasibility_gate: true`, `feasibility_refusal: null`. That check now
runs against the maxima THIS sitting measured (38,440 / 4,176), which is the
proposal's own claim — these ceilings pay for a run of the units it saw — and it
is **true by construction**: the rule computes the figures from those same
maxima. `clears_the_committed_profiles_gate: true`,
`committed_profile_refusal: null` is the check that is not by construction: the
same four figures against the constants this tree carries (24,282 / 3,116), which
they also clear, because this sitting's units are LARGER than the committed
profile's and a proposal sized on the larger clears the smaller.

The two rules, reported separately because they disagree:

| Run ceiling | mean rule (100 x mean x 1.5) | max floor (100 x max, + one turn cap on output) | adopted |
| --- | --- | --- | --- |
| input | 3,270,000 | 3,844,000 | 3,844,000 (the floor) |
| output | 207,000 | 422,000 | 422,000 (the floor) |

The floor binds on BOTH dimensions this time, where on 2026-09-14 it bound on
output alone: the candidate arm's largest unit is 1.76x the pooled mean unit on
input (38,440 against 21,798.1) and 3.04x on output (4,176 against 1,375.2),
both above the 1.5 margin. The output floor carries the in-flight headroom term
the gate enforces — 100 x 4,176 + 4,096 = 421,696, rounded up to 422,000 — which
is the term the second calibration's card added and the defect of 2026-09-14
that it closes. The per-unit figures take no such disagreement: output is
max(15,360 reservation schedule, 3 x 4,176) = 15,360 -> 16,000, and input is
3 x 38,440 = 115,320 -> 116,000.

**The proposal authorizes nothing.** A ceiling is the owner's, on a card, and
`assert_live_run_is_authorized` keeps refusing any limits but the ones it is
handed.

## What this measurement does to the standing ceilings

This is the sitting's other finding, and it is the reason the section below does
not commit the profile refresh.

The largest unit this calibration charged is 38,440 input and 4,176 output. The
feasibility gate compares a run-level ceiling against the unit count times the
largest unit the archives hold, so moving the committed profile to this sitting's
figures moves what every standing ceiling is checked against:

| Ceilings | Units | Run input | Needs | Run output | Needs |
| --- | --- | --- | --- | --- | --- |
| Fourth authorization (`AUTHORIZED_LIMITS`) | 100 | 3,710,000 | **3,844,000 — REFUSED** | 459,000 | 421,696 — clears |
| Calibration 2026-09-14 (`CALIBRATION_LIMITS`) | 10 | 600,000 | 384,400 — clears | 120,000 | 43,808 — clears |
| Calibration 2026-09-15 (`CALIBRATION_2_LIMITS`) | 120 | 4,500,000 | **4,612,800 — REFUSED** | 450,000 | **505,216 — REFUSED** |

Two consequences, stated as findings and not acted on:

1. **The open item of 2026-09-14 is CLOSED by measurement, on the output
   dimension.** That day's residual was that 459,000 is exactly a hundred times
   its own largest unit (4,590) and 4,096 short of what a hundred such units
   reserve. This sitting's largest unit is 4,176, so a hundred of them plus the
   in-flight term need 421,696 and the authorized 459,000 clears them with
   37,304 to spare. The v4 revision made units SMALLER on output, which is what
   the ballot bound was for.
2. **The binding dimension moved to INPUT.** The fourth authorization's
   3,710,000 run-level input ceiling does not clear a hundred units of this
   sitting's largest unit (3,844,000), short by 134,000 — 3.6%. The v4 revision
   added bytes to the candidate's turn and ballot prompts, and the largest unit
   grew from the fourth run's 36,743 and 2026-09-14's 35,232 to 38,440. The
   proposal's run-input figure is exactly the 3,844,000 the gate would need.

Neither is a defect in this tree and neither is mine to repair: re-sizing an
authorized ceiling is the owner's, on the fifth authorization card, which is
where this measurement was always going to be read. The per-unit ceilings are
unaffected — 106,000 clears 38,440 and 16,000 clears max(15,360, 4,176) — so the
re-sizing the fifth authorization needs is one number on the run-level input
dimension, or two if it also re-sizes a calibration mode nobody plans to re-run.

## The replay double's committed profile was NOT refreshed

The card's item 8 documents a refresh of `tests/experiments/deduction_usage_profile.json`
from this output, and the manifest quotes the command. **It was run, its result
is recorded here, and the refreshed profile was not committed.** The reason is
the finding above, not an omission.

Running the documented command succeeds and produces a well-formed profile:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile audits/deduction-candidate/calibration-2-2026-09-15/calibration.json \
  --profile-out <a path outside version control>
```

720 call rows, 120 unit rows, `built_from.mode` `2026-09-15`,
`built_from.records` `[("3000-3999", 50), ("5000-5999", 10)]`, totals
`resolved_calls 720`, `refused_calls_with_usage 0`,
`largest_charged_unit_input_tokens 38,440`,
`largest_charged_unit_output_tokens 4,176`.

**The rehearsal's ceiling proposal did change, and it changed to the measured
one** — which is the outcome the card wanted. A 120-unit calibration-2 rehearsal
on the replay double, at $0 and reaching no provider:

| Profile | measured max unit | proposal per unit | proposal run |
| --- | --- | --- | --- |
| committed (the three stopped runs' archives) | 24,360 in / 3,384 out | 74,000 / 16,000 | 3,139,000 / 343,000 |
| refreshed (this sitting) | 38,440 in / 4,176 out | 116,000 / 16,000 | 3,844,000 / 422,000 |

The refreshed rehearsal reproduces this sitting's live proposal exactly, to the
token, on all four figures.

What stops the refresh being committed by this runner is what moves with it.
`.venv/bin/pytest tests/experiments -q` on the refreshed profile, with
`CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` moved to
38,440 / 4,176 in the same edit, is **27 failed, 459 passed** against 486 passed
clean. They fall into three classes:

1. **Eleven are the finding above, not a test defect.** `assert_limits_are_feasible`
   refuses `AUTHORIZED_LIMITS` on the run-level input dimension and refuses
   `CALIBRATION_2_LIMITS` for 120 units on both, so every case that needs the
   authorized live run or the second calibration mode to be feasible raises
   before it reaches what it was written to check — `TestAuthorizedClient`'s
   three client-binding cases, the manifest-binding case, the live-resume
   refusal, `test_the_gate_accepts_the_fourth_authorizations_limits`,
   `test_the_run_output_ceiling_does_not_clear_the_calibrations_largest_unit`
   (whose first line asserts the committed limits are feasible, and which now
   raises on the INPUT dimension instead),
   `test_the_feasibility_gate_accepts_the_second_mode_for_120_units`,
   `test_each_mode_is_accepted_whole`, and the two draw-preflight cases whose
   planted refusals are masked by the earlier raise. Every repair available to a
   runner is either moving an authorized ceiling or weakening the gate, and both
   are out of a runner's hands: the card says so in its own words — "nothing
   here moves an authorized figure" — and `CEILING_PROPOSAL_RULE` says a ceiling
   is the owner's, on a card.
2. **Eight are the archived FAULT modes the clean sitting does not carry.**
   `test_the_rehearsal_reproduces_the_stop_of_2026_09_13`,
   `test_the_archived_refusal_is_replayed_where_it_happened`,
   `test_each_planted_provider_fault_reaches_a_running_unit[billed_refusal]`,
   `test_a_call_type_blind_sampler_manufactures_a_truncation`,
   `test_a_stop_inside_a_unit_carries_its_spend`, the two
   `test_the_rehearsal_is_green_under_*` cases that assert the manifest quotes
   the rehearsal's own per-arm totals, and
   `test_the_profile_is_the_archived_calls_and_nothing_else`. This sitting
   archived no refusal, no default and no truncation, so a profile built from it
   has no fault to replay — the same irony 2026-09-14 recorded, and for the same
   reason: the corrected prompts worked. Keeping that coverage means committing
   the stopped runs' rows as a fixture of their own and pointing those cases at
   it, which is a design decision about what the committed double should model.
3. **Eight are arithmetic that follows the constants**:
   `test_a_re_sized_authorization_passes`, both parametrisations of
   `test_a_run_ceiling_below_its_own_units_is_refused`,
   `test_a_run_output_ceiling_sized_at_exactly_its_units_is_refused`,
   `test_a_fixture_sized_proposal_says_it_clears_no_gate`,
   `test_the_rehearsal_on_a_refreshed_profile_runs_under_the_proposal`,
   `test_the_committed_calibration_and_profile_parse_and_read_null` (which pins
   that every committed profile row reads a null `finish_reason`, where a
   refreshed row reads `"stop"`), and
   `test_the_enforcement_section_quotes_the_reservation_policy`. The last is
   worth naming on its own: `RESERVATION_POLICY` embeds both constants in its
   own text — "24,282 input and 3,116 output" — and the execution manifest
   quotes that string verbatim under "How each limit is enforced", so moving the
   constants edits a committed record of the manifest as well as the module.
   These would be mechanical to update, but only on top of class 1, which is
   not. The pin the card named,
   `test_the_calibration_is_the_largest_unit_the_archives_charged`, is NOT in
   the 27: it stayed green, because the two constants moved in the same edit as
   the profile, which is the one thing the manifest says must happen together.

So the measurement is delivered and the decision is handed back with it, with
the numbers it needs: the fifth authorization's run-level input ceiling must be
at least **3,844,000**, its run-level output ceiling at least **421,696**
(459,000 already clears it), and the two constants move to **38,440** and
**4,176** in the same commit as the profile or
`test_the_calibration_is_the_largest_unit_the_archives_charged` is red. Nothing
in this directory moves any of them.

## Comparison with the calibration of 2026-09-14 and the fourth run

| Quantity | 2026-09-14 (v3, turn cap 2,048) | Run 4 (v3, turn cap 4,096) | This sitting (v4, turn cap 4,096) |
| --- | --- | --- | --- |
| Candidate ballot out mean | 163.8 | 182.3 | 93.3 |
| Candidate ballot out max | 237 (23% of cap) | 624 resolved, 1,024 refused | **135 (13.2% of cap)** |
| Candidate turn out mean | 881.9 | 917.9 | 443.0 |
| Candidate turn out max | 2,036 (99.4% of the 2,048 cap) | 1,900 (46.4%) | 1,884 (46.0%) |
| Candidate per-unit output | 3,137.0 | 3,481.5 | 1,608.9 |
| Reference per-unit output | 1,107.8 | 1,115.7 | 1,141.5 |
| Candidate per-unit input | 28,430.2 | 27,537 | 22,733.8 |
| Reference per-unit input | 21,025.8 | 20,278 | 20,862.4 |
| Largest unit input | 35,232 | 36,743 | **38,440** |
| Largest unit output | 4,590 | 4,816 | **4,176** |
| Impostor candidate ballot truncations | not measured | 1 of 13 | **0 of 60** |
| Impostor candidate ballot self-tells | not measured | 11 of 12 | 39 of 60 |
| Candidate units with a leaking turn | not measured | 2 of 13 | 1 of 60 |
| Pooled pace | 17.23 s/attempt | — | 10.28 s/attempt |

The row that matters for the stop is the second: the candidate ballot's maximum
fell from a refused 1,024 to 135 while its draw count rose from 15 to 180. The
row that matters for the ceilings is the ninth: the largest unit's INPUT rose
across all three, which is where the fourth authorization's run-level input
ceiling stopped clearing.

## What was archived, and how to reproduce every number

Everything in this directory:

| File | What it is |
| --- | --- |
| `calibration.json` | the mode's whole output, 199,101 bytes; every figure above is read from it |
| `unit-usage.jsonl` | the 120 per-unit usage rows, extracted verbatim from `calibration.json`'s `unit_usage` block |
| `calibration-run.log` | the sitting's log: the start and end stamps, the documented command with its credential and output paths elided, the exit code, and the payload the mode printed to stdout |
| `CALIBRATION.md` | this file |

The rendered prompts and prefixes are development data and are NOT committed:
the sitting's replays went to an `--output-dir` outside version control, as the
manifest requires. The output itself carries no prompt, no prefix, no step and
no outcome — `assert_report_holds_no_prefix_bytes` was re-run over the archived
payload against all sixty rebuilt prefixes and passed — and the 720 `calls` rows
carry exactly six fields each: `arm`, `call_type`, `input_tokens`,
`output_tokens`, `disposition`, `finish_reason`. The log's stdout body is
byte-identical to `calibration.json` (both sha256
`ddb2073aaa34276e3a5da9f14c4a37c76ab9b5dfe937a6fabdb02504fa7c9188`); the
credential scan over every file in this directory, comparing counts only against
the key's first six characters and against the whole key, returns zero.

Read the output:

```sh
.venv/bin/python -m json.tool audits/deduction-candidate/calibration-2-2026-09-15/calibration.json
```

Recompute every derived figure in this file — the per-arm and per-call-type
profile, the role split and its prose lengths, the truncation rate with its
Wilson interval, the `finish_reason` and signal-disagreement counts, the
self-tell and leak counts, the refusal, default and transport counts, the pace,
the usage against the limits, and both ceiling rules:

```sh
.venv/bin/python - <<'PY'
import json, math
from pathlib import Path
from scripts.paired_stats import wilson_interval
d = json.loads(Path(
    "audits/deduction-candidate/calibration-2-2026-09-15/calibration.json").read_text())
L, S, P = d["limits"], d["sampling"], d["proposal"]
caps = {"turn": S["turn_max_tokens"], "vote": S["vote_max_tokens"]}
up = lambda v: int(math.ceil(v / 1000.0) * 1000)
for r in d["input_records"]:
    print(r["record"], r["record_sha256"], r["status"],
          "| drawn", len(r["seeds"]), r["seeds"][0], "..", r["seeds"][-1])
for a in d["arms"]:
    print(a["arm"], "units", a["units"], "attempts", a["attempts"],
          "completions", a["completions"],
          "| refused", a["charged_failed_attempts"],
          "defaults", a["defaulted_turns"], a["defaulted_votes"],
          "| retried", a["retried_calls"], "unaccounted", a["unaccounted_attempts"],
          "| s/attempt %.2f" % a["seconds_per_attempt"])
    for c in a["by_call_type"]:
        print("  ", c["call_type"], "n", c["completions"],
              "| in mean %.1f p95 %d max %d" % (c["input_mean"], c["input_p95"], c["input_max"]),
              "| out mean %.1f p95 %d max %d cap %d" % (
                  c["output_mean"], c["output_p95"], c["output_max"], c["max_tokens"]))
    for r in a["by_role"]:
        print("   ", r["call_type"], r["role"], "draws", r["draws"],
              "| out mean %.1f p95 %d max %d" % (
                  r["output_mean"], r["output_p95"], r["output_max"]),
              "| truncations", r["truncations"], r["truncations_by_finish_reason"])
        for ln in r["lengths"]:
            print("        ", ln["field"], "samples", ln["samples"],
                  "| chars mean %.1f p95 %d max %d" % (ln["mean"], ln["p95"], ln["max"]))
    imp = next(r for r in a["by_role"]
               if r["call_type"] == "ballot" and r["role"] == "IMPOSTOR")
    lo, hi = wilson_interval(imp["truncations"], imp["draws"])
    print("   impostor ballot truncation rate %d/%d = %.2f%% Wilson [%.2f%%, %.2f%%]" % (
        imp["truncations"], imp["draws"],
        100 * imp["truncations"] / imp["draws"], 100 * lo, 100 * hi))
    draws = sum(r["draws"] for r in a["by_role"])
    trunc = sum(r["truncations"] for r in a["by_role"])
    lo, hi = wilson_interval(trunc, draws)
    print("   arm-wide truncation rate %d/%d = %.2f%% Wilson [%.2f%%, %.2f%%]" % (
        trunc, draws, 100 * trunc / draws, 100 * lo, 100 * hi))
    rows = [c for c in d["calls"] if c["arm"] == a["arm"]]
    reasons, observed, inferred, disagree = {}, 0, 0, 0
    for c in rows:
        key = "null" if c["finish_reason"] is None else c["finish_reason"]
        reasons[key] = reasons.get(key, 0) + 1
        cap = caps["vote" if c["call_type"] == "ballot" else "turn"]
        obs, inf = c["finish_reason"] == "length", c["output_tokens"] >= cap
        observed += obs; inferred += inf
        disagree += c["finish_reason"] is not None and obs != inf
    print("   finish_reason", dict(sorted(reasons.items())),
          "| observed", observed, "inferred", inferred, "disagreements", disagree)
    print("   self-telling impostor ballots", a["self_telling_impostor_ballots"],
          "| leaking turns", a["leaking_turns"],
          "| units with one", a["units_with_a_leaking_turn"])
    print("   unit in mean %.1f max %d | unit out mean %.1f max %d | totals %d/%d"
          % (a["mean_unit_input_tokens"], a["max_unit_input_tokens"],
             a["mean_unit_output_tokens"], a["max_unit_output_tokens"],
             a["input_tokens"], a["output_tokens"]))
ti = sum(a["input_tokens"] for a in d["arms"])
to = sum(a["output_tokens"] for a in d["arms"])
print("run  %d/%d in (%.1f%%)  %d/%d out (%.1f%%)" % (
    ti, L["run_max_input_tokens"], 100 * ti / L["run_max_input_tokens"],
    to, L["run_max_output_tokens"], 100 * to / L["run_max_output_tokens"]))
print("work %.1f/%.0f s (%.1f%%) | elapsed %.1f/%.0f s (%.1f%%) | %.2f s/attempt" % (
    d["model_work_seconds"], L["model_work_seconds"],
    100 * d["model_work_seconds"] / L["model_work_seconds"],
    d["elapsed_seconds"], L["elapsed_seconds"],
    100 * d["elapsed_seconds"] / L["elapsed_seconds"], d["seconds_per_attempt"]))
print("cost", d["total_cost_usd"], "| units", d["units"], "| mode", d["mode"])
print("proposal per unit %d/%d run %d/%d clears %s committed %s" % (
    P["unit_max_input_tokens"], P["unit_max_output_tokens"],
    P["run_max_input_tokens"], P["run_max_output_tokens"],
    P["clears_the_feasibility_gate"], P["clears_the_committed_profiles_gate"]))
print("mean rule  run in %d out %d" % (
    up(P["units"] * P["measured_mean_unit_input_tokens"] * 1.5),
    up(P["units"] * P["measured_mean_unit_output_tokens"] * 1.5)))
print("max floor  run in %d out %d" % (
    up(P["units"] * P["measured_max_unit_input_tokens"]),
    up(P["units"] * P["measured_max_unit_output_tokens"] + S["turn_max_tokens"])))
PY
```

And the per-unit rows, which are the same bytes as `unit-usage.jsonl`:

```sh
.venv/bin/python -c "import json;d=json.load(open('audits/deduction-candidate/calibration-2-2026-09-15/calibration.json'));[print(json.dumps(u,sort_keys=True)) for u in d['unit_usage']]"
```

## Limitations

* Zero truncations in sixty impostor-authored candidate ballot draws bounds the
  rate; it does not prove it is zero. The Wilson 95% upper bound is 6.02% on
  that denominator, so a rate up to about one draw in seventeen remains
  consistent with this sitting, and P(a clean 50-pair run) at that bound is
  4.5%. The bar the owner set was the chance of SEEING a 1-in-13 event, and it
  was met; a tighter bound needs more draws.
* This is a different prompt surface from the fourth run. The candidate arm ran
  at accounts revision v4, so nothing here pools with the fourth run's 24 units
  and the comparison table above is between surfaces, not within one.
* The leak detector is a lexical rule over committed turn text gated on the
  speaker's ground-truth role; `ROLE_LEAK_RULE` states in its own words that the
  count is an estimate carrying error in both directions and is not a floor.
  One leaking turn in sixty candidate units is a small numerator on a rule with
  two-sided error, so it bounds the leak loosely rather than measuring it.
* The role split's prose lengths are over AUTHORED payloads and its truncation
  denominator is DRAWS, so two numbers in the same row have different
  denominators. The field names say which is which (`draws` against
  `lengths[].samples`).
* `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` are still
  the three stopped live runs' 24,282 / 3,116. Every feasibility claim this tree
  makes is against those, and the section above says exactly what happens when
  they move.
* This measured cost and shape, not merit. No grader ran and no outcome is
  reported, so nothing here says whether the candidate arm deduces better.

## Deviations from the manifest and the dispatch

Three, all recorded rather than silent.

1. **The invocation carried its credential through `uv run --env-file`.** The
   manifest documents `.venv/bin/python -m experiments.fresh_deduction_instrument
   --calibrate --calibration-mode 2026-09-15 ...`; this sitting ran
   `uv run --env-file <a 0600 credential-only file outside the repository> python
   -m experiments.fresh_deduction_instrument --calibrate --calibration-mode
   2026-09-15 ...` with the module, the mode, the provider, the manifest path,
   the runner flag, the output directory and the `--json` path identical. The
   substitution injects `FEATHERLESS_API_KEY` from a file outside version
   control instead of the ambient shell, so the key never reaches a command
   line, a log or a commit; the file was deleted when the sitting finished. It
   is the same substitution the calibration of 2026-09-14 recorded, and nothing
   about what was drawn, gated or charged differs.
2. **The committed usage profile was not refreshed**, for the reason the section
   above gives at length: the refresh makes this tree refuse both the fourth
   authorization's limits and the second calibration mode's own, and every
   repair is either moving an authorized ceiling or weakening the gate. The
   refresh command was run, its output was compared against the committed
   profile through a $0 rehearsal on the replay double, and both proposals are
   recorded; no committed profile byte and neither calibrated constant moved.
3. **`audits/deduction-candidate/checkpoint.md` gained a dated line** naming this
   sitting. That file is a historical checkpoint of the 2026-09-06 mechanics
   capture and the calibration of 2026-09-14 added nothing to it; the line is
   added because the dispatch asked for one, and it states only what this
   directory holds.

Nothing else departs from the manifest's documented second calibration. The
`--json` destination — this dated directory — did not exist beforehand and the
invocation made it, as the manifest's command section says it does.
