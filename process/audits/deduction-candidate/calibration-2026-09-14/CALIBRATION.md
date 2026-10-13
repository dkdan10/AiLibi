# Development calibration of the fresh-model deduction instrument, 2026-09-14

A bounded live measurement of what the provider CHARGES, on development inputs,
run once by a runner session on
[the calibration card](../../../tasks/work/fresh-deduction-calibration.md)
(acceptance item 7) under the owner's decision 1 of
[the diagnosis of 2026-09-13](../../../tasks/diagnosis-2026-09-13-live-run-stops.md),
recorded in
[the execution manifest](../execution-manifest.md)'s
"Development calibration (2026-09-14)" section.

**This measured nothing about the candidate's merit.** No grader ran, no paired
statistic was computed and no meeting outcome is recorded anywhere in this
directory. The primary outcome, the decision rule and the minimum actionable
effect are untouched, and no unit of this calibration counts towards them. What
it measures is cost: what one call and one unit charge on each arm.

## The design

| Field | Value |
| --- | --- |
| Mode | `experiments/fresh_deduction_instrument.py --calibrate` |
| Inputs | the first five accepted seeds, ascending, of the converted 3000–3999 band: 3000, 3001, 3002, 3003, 3004 |
| Input record | [held-out/manifest-band-3000-3999.json](../held-out/manifest-band-3000-3999.json), `status: development` since 2026-09-10 |
| Arms | both, `repaired_clock` then `combined_accounts`, sequential, seed ascending, both arms per seed before the next seed |
| Units | 5 paired seeds x 2 arms = 10 units, 60 calls |
| Provider / model | `featherless` / `Qwen/Qwen3.6-27B` |
| Prompt set | `qwen3_6_27b`, with the corrected account prompts at `ACCOUNT_PROMPT_SET_REVISION` **v3** (`agents/strategic/prompts/loader.py:1236`) |
| Sampling | turn 2,048 output at temperature 0.4; ballot 1,024 at 0.2 — the run's own, unchanged |
| Limits | `CALIBRATION_LIMITS`: per unit 60,000 in / 12,000 out, run 600,000 / 120,000, 1 h model work inside a 1.5 h elapsed window |
| Transport bound | 4 attempts per call, 180 s per attempt — the run's own, unchanged |
| Instrument | `instrument_sha256` `d1b36d8cb459121188ab8108f4dac8261b73664044e1546df289535e697d6552` |
| Held-out record | not read, not rendered, not touched: `verify_frozen_set` is never called on this path |

**One sitting.** The calibration ran once, start to finish, and was not
re-run, resumed or restarted. It began at `2026-09-14T10:26:05Z`, ended at
`2026-09-14T10:43:20Z` and exited 0 with all ten units complete. The card's
Constraints authorize one calibration and no retry beyond the instrument's own
transport bound; no retry was needed, because no attempt failed.

**The input binding.** The record the calibration drew from was bound before
any spend:

```sh
sha256sum audits/deduction-candidate/held-out/manifest-band-3000-3999.json
git diff --exit-code origin/main -- audits/deduction-candidate/held-out/manifest-band-3000-3999.json
```

`ca4cd057acb2119646190fb6fff923a897ec207d5f54c491c3e1dfae0944cf3c`, and the
file is byte-identical to `origin/main`'s (the `git diff` exits 0). The same
digest is recorded inside the output as `inputs.record_sha256`, so the report
names the bytes it drew from.

## The measured profile

Per arm and per call type, over the 60 completions. `n` is the completion
count; `p95` is the nearest-rank percentile the report's `percentile_rule`
states (index `ceil(0.95 x n) - 1` of the ascending sample, no interpolation).

### `repaired_clock` (reference arm)

| Call type | n | in mean | in p95 | in max | out mean | out p95 | out max | out cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| turn | 15 | 3,316.9 | 4,266 | 4,266 | 273.9 | 448 | 448 | 2,048 |
| ballot | 15 | 3,691.7 | 4,667 | 4,667 | 95.4 | 124 | 124 | 1,024 |

Per unit: input mean 21,025.8, max 23,494; output mean 1,107.8, max 1,486.
Arm totals: 105,129 input, 5,539 output over 30 attempts.

### `combined_accounts` (candidate arm)

| Call type | n | in mean | in p95 | in max | out mean | out p95 | out max | out cap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| turn | 15 | 3,805.6 | 5,977 | 5,977 | 881.9 | 2,036 | 2,036 | 2,048 |
| ballot | 15 | 5,671.1 | 7,973 | 7,973 | 163.8 | 237 | 237 | 1,024 |

Per unit: input mean 28,430.2, max 35,232; output mean 3,137.0, max 4,590.
Arm totals: 142,151 input, 15,685 output over 30 attempts.

The candidate arm charges **2.83x** the reference arm's output (15,685 against
5,539) and 1.35x its input. The asymmetry is why the two schedules are reported
apart rather than pooled: a candidate turn's 881.9 mean output is 3.2x a
reference turn's, while the two ballot schedules differ by 1.7x.

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
| completions | 30 of 30 | 30 of 30 |

Every one of the ten units resolved all six of its calls, and the only
disposition present in the output's 60 `calls` rows is `resolved`.

**The `union_tag_invalid` refusals are gone.** The diagnosis of 2026-09-13
found two candidate-arm turns across two runs billed and refused on exactly
that union tag — the accounts prompt asking for a `whereabouts` claim the turn
schema refuses — against zero refusals in 23 reference-arm attempts. On the
corrected prompts at revision v3 this calibration saw **zero** refusals in 30
candidate-arm attempts. That is what was expected and it is what was measured;
30 attempts is not a bound on a rare rate, only evidence that the frequent
failure mode the diagnosis named is not frequent any more.

## Transport

| Per arm | `repaired_clock` | `combined_accounts` |
| --- | --- | --- |
| attempts | 30 | 30 |
| retried calls | 0 | 0 |
| unaccounted attempts | 0 | 0 |
| aborted attempts | 0 | 0 |
| attempts by trigger | none | none |

No attempt was retried, so no attempt went unaccounted. Sixty sends produced
sixty completions; the transport bound (4 attempts, 180 s each) was never
reached.

## Pace

17.23 s per attempt pooled over 60 attempts: 12.61 s on the reference arm and
21.85 s on the candidate. Model work totalled 1,033.9 s inside 1,034.5 s
elapsed — the calibration is sequential, so the two are the same clock less
setup.

At the pooled pace the held-out design's ~600 sequential calls need about
2.9 h of model work against the 6 h the authorization allows; at the candidate
arm's own pace its 300 calls need about 1.8 h and the reference arm's about
1.1 h, so about 2.9 h either way. The three earlier attempts measured a pooled
15.78 s per attempt over 39 attempts, so this sitting ran slightly slower and
within the same band.

## Actual usage against the calibration limits

| Dimension | Charged | Ceiling | Used |
| --- | --- | --- | --- |
| run input tokens | 247,280 | 600,000 | 41.2% |
| run output tokens | 21,224 | 120,000 | 17.7% |
| largest unit input | 35,232 | 60,000 | 58.7% |
| largest unit output | 4,590 | 12,000 | 38.2% |
| model work | 1,033.9 s | 3,600 s | 28.7% |
| elapsed | 1,034.5 s | 5,400 s | 19.2% |

**$0.00 marginal**, the report's `total_cost_usd` and both arms' `cost_usd`, on
the same flat-rate subscription and for the same reason as the manifest's cost
statement: the provider's zero pre-flight rate makes the dollar dimension
bookkeeping rather than a brake.

## The ceiling proposal

Computed by `ceiling_proposal` and carried in the output as `proposal`, with
`CEILING_PROPOSAL_RULE` quoted beside it. For the held-out design's **100**
units:

| Ceiling | Proposed |
| --- | --- |
| per unit input | **106,000** |
| per unit output | **14,000** |
| run input | **3,710,000** |
| run output | **459,000** |

`clears_the_feasibility_gate: true`, `feasibility_refusal: null` — the
instrument's own `assert_limits_are_feasible` accepts these for a 100-unit run.

The two rules, reported separately because they disagree on one figure. The
card states run ceiling = 100 units x measured mean unit x 1.5; the code adds a
floor of 100 units x measured maximum unit, because that product is what the
feasibility gate enforces and a proposal the instrument would refuse is not a
proposal:

| Run ceiling | card's rule (100 x mean x 1.5) | code's floor (100 x max) | adopted |
| --- | --- | --- | --- |
| input | 3,710,000 | 3,524,000 | 3,710,000 (the card's rule) |
| output | 319,000 | 459,000 | 459,000 (the floor) |

So the floor binds on output and not on input: the candidate arm's largest unit
(4,590 output) is 2.16x the pooled mean unit (2,122.4), above the 1.5 margin,
while its largest input unit (35,232) is 1.42x the mean (24,728) and below it.
The per-unit figures take no such disagreement: output is
max(9,216 reservation schedule, 3 x 4,590) = 13,770 -> 14,000, and input is
3 x 35,232 = 105,696 -> 106,000, each rounded up to the next 1,000.

**The proposal authorizes nothing.** A ceiling is the owner's, on a card, and
`assert_live_run_is_authorized` keeps refusing any limits but the ones it is
handed. Against the diagnosis's provisional figures (per unit 60,000 in /
12,000 out, run 3,600,000 / 350,000) the measurement asks for more on three of
the four: +76% per-unit input, +17% per-unit output, +3% run input and +31% run
output.

## One thing the proposal does not cover: the per-call turn cap

The largest candidate turn charged **2,036 output tokens against the 2,048
cap** — 12 tokens of headroom, one of fifteen candidate turns. The per-call
caps are deliberately NOT re-sized by this calibration (a calibration that drew
differently would measure a distribution the run it sizes never draws from), and
the proposal re-sizes only the four token ceilings. But a response that reaches
its output cap is a truncation, and a truncation is a stop with no retry
(`execution-manifest.md`, "How each limit is enforced"). One candidate turn in
fifteen landing within 0.6% of the cap is a rate a 300-candidate-turn run should
be read against before it is authorized. This is an observation for the owner's
fourth authorization, not a proposal: nothing here changes a cap.

## The replay double's committed profile was NOT refreshed

The card's item 4 documents a refresh of `tests/experiments/deduction_usage_profile.json`
from this output, and the manifest quotes the command. **It was run, its result
is recorded here, and the refreshed profile was not committed.** The reason is a
finding, not an omission.

Running the documented command succeeds and produces a well-formed profile:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument \
  --refresh-usage-profile audits/deduction-candidate/calibration-2026-09-14/calibration.json \
  --profile-out <a path outside version control>
```

Rehearsing on that refreshed profile reproduces this calibration's proposal
exactly — per unit 106,000 / 14,000, run 3,710,000 / 459,000,
`clears_the_feasibility_gate true` — where the committed profile's rehearsal
proposes per unit 73,000 / 11,000 and run 3,100,000 / 339,000. **So yes, the
rehearsal's ceiling proposal changed**, and it changed to the measured one,
which is the outcome the card wanted. The whole 100-unit rehearsal also
completes on the refreshed profile under the proposed limits, both arms at
50 units, at `total_cost_usd 0.0`.

What stops the refresh being committed by this runner is what else moves with
it. `.venv/bin/pytest tests/experiments -q` on the refreshed profile is
**8 failed, 377 passed**, and only the first of the eight is the "forgot the
two constants" failure the card's Limitations anticipated:

1. `test_the_calibration_is_the_largest_unit_the_archives_charged` —
   `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` must move
   from 24,282 / 3,116 to 35,232 / 4,590. Anticipated; arithmetic.
2. `test_the_profile_is_the_archived_calls_and_nothing_else` — pins the profile
   at 36 resolved calls and 2 billed-and-refused; the refresh makes it 60 and 0.
3. `test_the_archived_refusal_is_replayed_where_it_happened` — there is no
   refusal left in the profile to replay.
4. `test_each_planted_provider_fault_reaches_a_running_unit[billed_refusal]` —
   same cause.
5. `test_the_rehearsal_reproduces_the_stop_of_2026_09_13` — the rehearsal no
   longer reproduces the live stop's own arithmetic
   (`current=3116.0 + delta=1024.0 > cap=4000.0` becomes
   `current=2936.0 + delta=2048.0 > cap=4000.0`).
6. `test_a_call_type_blind_sampler_manufactures_a_truncation` — the PLANTED
   failure stops failing: with the refreshed rows the call-type-blind sampler no
   longer manufactures the truncation the plant exists to catch.
7. `test_the_rehearsal_is_green_under_a_feasible_authorization` — it asserts
   that [the execution manifest](../execution-manifest.md) quotes the
   rehearsal's per-arm input totals, which move (its line 1224 figures
   1,072,642 and 1,015,417 become 1,051,290 and 1,421,510).
8. `test_a_stop_inside_a_unit_carries_its_spend` — pins the rotation's token
   rows, which the card's own round-1 record quotes.

Adopting the refresh therefore means deleting or rewriting the double's
billed-refusal and 2026-09-13-stop regressions — the coverage
[the instrument-realism card](../../../tasks/work/fresh-deduction-instrument-realism.md)
was written to build — amending the execution manifest's quoted headroom
figures, and re-pinning a merged card's record. Those are design decisions
about what the committed double should model, on a card whose Constraints say
"The runner of the calibration is not the implementer of this card". The
measurement is delivered; the decision is handed back with it.

The irony is worth stating plainly: the refresh guts those regressions
*because the corrected prompts worked*. The archived profile carries the fault
modes precisely because the runs that produced it hit them, and a clean sitting
has no fault to archive. Whoever takes this up has to decide whether the
committed double replays the latest measurement or keeps a library of the
faults the endpoint has ever shown — which is a question the diagnosis's
"no pre-run surface could observe either" root cause makes worth answering
deliberately.

## What was archived, and how to reproduce every number

Everything in this directory:

| File | What it is |
| --- | --- |
| `calibration.json` | the mode's whole output, 19,841 bytes; every figure above is read from it |
| `unit-usage.jsonl` | the ten per-unit usage rows, extracted verbatim from `calibration.json`'s `unit_usage` block |
| `calibration-run.log` | the sitting's log: the start and end stamps, the exit code, and the payload the mode printed to stdout |
| `CALIBRATION.md` | this file |

The rendered prompts and prefixes are development data and are NOT committed:
the run's replays went to an `--output-dir` outside version control, as the
manifest requires. The output itself carries no prompt, no prefix, no step and
no outcome — the evaluation's own `assert_report_holds_no_prefix_bytes` runs
over it before it is returned — and the 60 `calls` rows carry exactly five
fields each: `arm`, `call_type`, `input_tokens`, `output_tokens`, `disposition`.
The log's stdout body is byte-identical to `calibration.json`; the credential
scan over both files, comparing counts only against the key's first six
characters, returns zero.

Read the output:

```sh
.venv/bin/python -m json.tool audits/deduction-candidate/calibration-2026-09-14/calibration.json
```

Recompute every derived figure in this file — the per-arm and per-call-type
profile, the refusal and default counts, the transport counts, the pace, the
usage against the limits, and both ceiling rules:

```sh
.venv/bin/python - <<'PY'
import json, math
from pathlib import Path
d = json.loads(Path(
    "audits/deduction-candidate/calibration-2026-09-14/calibration.json").read_text())
L, P = d["limits"], d["proposal"]
up = lambda v: int(math.ceil(v / 1000.0) * 1000)
for a in d["arms"]:
    print(a["arm"], "attempts", a["attempts"], "completions", a["completions"],
          "| refused", a["charged_failed_attempts"],
          "defaults", a["defaulted_turns"], a["defaulted_votes"],
          "| retried", a["retried_calls"], "unaccounted", a["unaccounted_attempts"],
          "| s/attempt %.2f" % a["seconds_per_attempt"])
    for c in a["by_call_type"]:
        print("  ", c["call_type"], "n", c["completions"],
              "| in mean %.1f p95 %d max %d" % (c["input_mean"], c["input_p95"], c["input_max"]),
              "| out mean %.1f p95 %d max %d cap %d" % (
                  c["output_mean"], c["output_p95"], c["output_max"], c["max_tokens"]))
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
print("cost", d["total_cost_usd"], "| units", d["units"], "| seeds", d["inputs"]["seeds"])
print("proposal per unit %d/%d run %d/%d clears %s" % (
    P["unit_max_input_tokens"], P["unit_max_output_tokens"],
    P["run_max_input_tokens"], P["run_max_output_tokens"],
    P["clears_the_feasibility_gate"]))
print("card rule run  in %d out %d" % (
    up(P["units"] * P["measured_mean_unit_input_tokens"] * 1.5),
    up(P["units"] * P["measured_mean_unit_output_tokens"] * 1.5)))
print("code floor run in %d out %d" % (
    up(P["units"] * P["measured_max_unit_input_tokens"]),
    up(P["units"] * P["measured_max_unit_output_tokens"])))
PY
```

And the per-unit rows, which are the same bytes as `unit-usage.jsonl`:

```sh
.venv/bin/python -c "import json;d=json.load(open('audits/deduction-candidate/calibration-2026-09-14/calibration.json'));[print(json.dumps(u,sort_keys=True)) for u in d['unit_usage']]"
```

## Deviations from the manifest and the dispatch

Two, both recorded rather than silent.

1. **The invocation carried its credential through `uv run --env-file`.** The
   manifest documents `.venv/bin/python -m experiments.fresh_deduction_instrument
   --calibrate ...`; this sitting ran
   `uv run --env-file <a 0600 credential-only file outside the repository> python -m
   experiments.fresh_deduction_instrument --calibrate ...` with the module, the
   provider, the manifest path, the runner flag, the output directory and the
   `--json` path identical. The substitution injects `FEATHERLESS_API_KEY` from
   a file outside version control instead of the ambient shell, so the key never
   reaches a command line, a log or a commit; the file was deleted when the run
   finished. Nothing about what was drawn, gated or charged differs.
2. **The committed usage profile was not refreshed**, for the reason the
   section above gives. The refresh command itself was run and its result is
   recorded; no committed profile byte moved.

Nothing else departs from the manifest's documented calibration. The `--json`
destination — this dated directory — did not exist beforehand and the
invocation made it, as the manifest's command section says it does.
