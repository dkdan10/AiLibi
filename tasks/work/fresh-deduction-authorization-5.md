# Fifth run of the fresh-model deduction evaluation, on re-sized ceilings

**Status:** done

## Outcome

The fresh-model deduction instrument runs once more, on the fifth held-out
band, under token ceilings re-sized from the second live development
calibration by the instrument's own proposal rule and with the per-call caps
unchanged. It records tokens, attempts, `finish_reason`, wall, model work and
cost against every limit; its paired result is read under the frozen decision
rule and the v4 revision's two declared one-sided effects, and adopts nothing.

## Evidence

The owner approved the section 6 decisions of
[the diagnosis](../diagnosis-2026-09-15-truncation-stop.md) as a set on
2026-09-15. Section 9 carries the rulings this card rests on: the vote cap
stays 1,024 (decision 5, No); a cap truncation stays a stop in the live run
(decision 6, No); the role leak is a reported diagnostic, not a gate (decision
9); and this authorization is opened once the second calibration reports,
carrying the re-sized ceilings with the headroom term, the refreshed profile
and the leak column. That calibration has now reported: one sitting, 120 units
and 720 calls on development inputs at revision v4
(`agents/strategic/prompts/loader.py:1248`), archived under
`audits/deduction-candidate/calibration-2-2026-09-15/`, measuring no merit.

| Quantity | Run 4 (v3) | Calibration 2 (v4) |
| --- | --- | --- |
| Candidate ballot output mean / max | 182.3 / 624, one refused at 1,024 | 93.3 / 135 |
| Candidate turn output mean / max | 917.9 / 1,900 | 443.0 / 1,884 |
| Candidate per-unit input / output mean | 27,537 / 3,481.5 | 22,733.8 / 1,608.9 |
| Largest unit charged, input / output | 36,743 / 4,816 | 38,440 / 4,176 |
| Impostor candidate ballot truncations | 1 of 13 | 0 of 60 |
| Impostor self-tell, candidate / reference | 11 of 12 / 2 of 13 | 39 of 60 / 9 of 60 |
| Units with a leaking turn, candidate / reference | 2 of 13 / 0 of 13 | 1 of 60 / 0 of 60 |

Zero of sixty impostor-authored candidate ballot draws truncated, Wilson 95%
upper bound 6.02% on the denominator decision 7 set the bar on; nothing
truncated in any of the 720 completions; zero defaults, zero charged failed
attempts, zero retries; 10.28 s per attempt pooled. The sitting's size, pace,
self-tell, leak, ballot truncations and proposal recompute from its output:

```sh
.venv/bin/python -c "import json; d = json.load(open(
    'audits/deduction-candidate/calibration-2-2026-09-15/calibration.json'))
a = [x for x in d['arms'] if x['arm'] == 'combined_accounts'][0]
print(d['units'], round(d['seconds_per_attempt'], 2),
      a['self_telling_impostor_ballots'], a['units_with_a_leaking_turn'])
print([(r['role'], r['draws'], r['truncations']) for r in a['by_role']
       if r['call_type'] == 'ballot'])
print({k: v for k, v in d['proposal'].items() if k != 'rule'})"
```

The ceilings in Constraints are that `proposal` block verbatim, computed for
100 units by `ceiling_proposal` under `CEILING_PROPOSAL_RULE`
(`experiments/fresh_deduction_instrument.py:6881` and `:6008`); its in-flight
headroom term on output (`:1273`) closes the open item of 2026-09-14.

The sitting's other finding is why this card exists. On the refreshed usage
profile `assert_limits_are_feasible` REFUSES today's `AUTHORIZED_LIMITS`, whose
3,710,000 run-level input ceiling (`:230`) falls short of the 3,844,000 a
hundred of that sitting's largest units need, and refuses `CALIBRATION_2_LIMITS`
for 120 units on both run dimensions. The runner committed neither the refreshed
profile nor any constant, and left the second calibration card's acceptance item
8 unchecked: re-sizing an authorized ceiling is the owner's, on this card. The
constants and the manifest move on [the limits card](fresh-deduction-limits-5.md);
the band is [the fifth freeze card](held-out-prefix-freeze-5.md)'s 8000-8999,
bands 3000-3999, 5000-5999, 6000-6999 and 7000-7999 all being development data.

## Acceptance

- [x] The execution manifest's authorization fields carry exactly the values in
  Constraints, the instrument's constants equal them, and
  `assert_limits_are_feasible` (`experiments/fresh_deduction_instrument.py:1273`)
  accepts `AUTHORIZED_LIMITS` on the REFRESHED profile, with
  `CALIBRATED_UNIT_INPUT_TOKENS` and `CALIBRATED_UNIT_OUTPUT_TOKENS` (`:547`,
  `:548`) at 38,440 and 4,176, and the 16,000 per-unit output ceiling clearing
  the 15,360 reservation schedule. A planted test at the old 3,710,000 goes red.
- [x] The runner regenerates the frozen set from the band the manifest binds,
  and `verify_frozen_set` (`:3043`) verifies every digest and the skip list
  before any client is constructed; the runner opens no prefix of band
  8000-8999 before the run, and none of the other four at all.
- [x] The run records tokens, attempts including retried and unaccounted ones,
  each call's `finish_reason` with the count of rows where it disagrees with
  the inferred `output_tokens >= max_tokens` cap signal, wall, model work and
  the $0.00 cost against every limit in Constraints, per arm and for the run;
  every stop condition of `STOP_RULE` (`:689`) is checked and reported, a
  truncation among them, final and buying no retry. An environmental stop may be
  resumed once per stop under the manifest's resumption clause, carrying and
  reporting the interrupted unit's spend.
- [x] The paired result is evaluated under the frozen decision rule (`:644`):
  the two-sided exact McNemar p, the net paired difference bar of 10 units and
  the wrongful-ejection bound (`:660`). It is ALSO read against the two
  one-sided effects the manifest's "Accounts prompt set v4 (2026-09-15)"
  section declares (`audits/deduction-candidate/execution-manifest.md:749`):
  the citation fix raises the candidate's ejection rate, and the turn bound
  edits a primary-outcome input through citation relevance, downward. The
  wrongful-ejection bound is read against the first by name: an ejection rate
  is what it polices. The fourth run's 24 complete units are NOT pooled.
- [x] The pre-declared leak column (`ROLE_LEAK_RULE`, `:6163`) and the per-arm,
  per-role ballot profile (draws, output mean, p95, max, truncations and
  self-tells) are reported beside the result as diagnostics: no stop condition
  reads either, and the decision rule names neither.
- [x] The results, per-unit records, usage reconciliation and rendered prefixes
  (development data once archived) land under
  `audits/deduction-candidate/run-<date>/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row (`:109`) recomputed.

## Constraints

Authorized limits for the fifth run: the cost, roster and execution values the
owner authorized by merging #437 on 2026-09-07 (merge commit `0f49d8e6`), the
wall window of 2026-09-13, the per-call caps of 2026-09-14, and the token
ceilings re-sized on 2026-09-15 from the second calibration (see Evidence):

| Field | Value |
| --- | --- |
| Provider | `featherless` |
| Model | `Qwen/Qwen3.6-27B` (locked 2026-07-12, Task 16.2). Non-thinking with `enable_thinking=false` pinned on every call, `response_format_mode = json_object`, prompt set `qwen3_6_27b` at accounts revision **v4** (`agents/strategic/prompts/loader.py:1248`) |
| Per-call token cap | turn 4,096 output / vote 1,024. UNCHANGED from the fourth authorization. Basis: at v4 the calibration drew 180 candidate ballots, 60 of them impostor-authored; the largest of the 180 charged 135 output tokens, 13.2% of the vote cap, and the largest impostor-authored one charged 123; zero of the 360 candidate draws truncated, and zero of all 720; the largest candidate turn charged 1,884, 46.0% of the turn cap. The owner's decision 5 of 2026-09-15 is No to re-sizing the vote cap |
| Total token budget | 3,844,000 input / 422,000 output run-level, and 116,000 input / 16,000 output per unit. Hard stop. Basis, from `audits/deduction-candidate/calibration-2-2026-09-15/calibration.json`'s `proposal`: per unit, 3 x the largest measured unit (38,440 input; 4,176 output gives 12,528) with the output figure held to the reservation schedule 3 x 4,096 + 3 x 1,024 = 15,360 and rounded up to 16,000; run-level, the larger of 100 units x the measured mean x 1.5 and 100 units x the largest measured unit on each dimension, plus ONE further turn cap on the output side for the run's last in-flight reservation (100 x 4,176 + 4,096 = 421,696). The run OUTPUT ceiling FALLS from 459,000 to 422,000. No budget was tightened: the rule is followed, and v4 made units smaller on output. Both provider pre-flight rates are zero, so these ceilings are a stop rule sized as an anomaly detector, not a budget |
| Wall-clock deadline | 6 h of model work within an 8 h elapsed deadline, unchanged from the third authorization. The calibration paced 10.28 s per attempt pooled (8.91 reference, 11.65 candidate), so six hundred attempts need about 1.7 h |
| Dollar limit | $0.00 marginal, recorded as bookkeeping and not as an enforcement mechanism. The provider's zero pre-flight rate disables the USD dimension, so only the token budget and the deadline can stop a run |
| Cost statement | The paragraph quoted below, verbatim |
| Roster | 4p1i with 3 living voters at meeting open. A change of roster invalidates the token budget above and requires a new authorization |
| Execution mode | sequential |
| Held-out preparer | The fifth freeze's preparer session (the pull request of [the fifth freeze card](held-out-prefix-freeze-5.md); band 8000-8999). Runner: a fresh session dispatched by the coordinator on this card after that freeze and [the limits card](fresh-deduction-limits-5.md) are merged; it opens no prefix before the run, regenerates the set from the frozen band and verifies every digest; the manifest's resumption clause of 2026-09-14 is in force, once per environmental stop, and a truncation is final. The coordinator dispatches and runs nothing |
| Death-tick body handle | Left as temporal v2 renders it in both arms, stated in the manifest, and asserted by the regex over the rendered prompts and the frozen prefixes |

The cost statement the manifest carries, verbatim and unchanged. One citation
inside it has aged and stands as written: the zero pre-flight rates sit at
`llm/featherless_client.py:250-251` since the finish-reason change.

> This evaluation runs on the Featherless AI Premium plan, a flat-rate hosted
> subscription at $25/month authorized by the owner on 2026-06-25
> (`llm/provider.py:74`). Its marginal cost is $0.00: no per-token charge is
> incurred, and the provider-keyed zero rate makes every recorded `cost_usd` on
> this run exactly 0.0 by construction rather than by measurement. The resources
> this run actually consumes are subscription capacity and elapsed wall time:
> 600 projected model calls and about 2.0 M tokens over a 6-hour elapsed window,
> against a plan whose concurrency ceiling is four units and whose 32B-class
> request costs two — i.e. two workers saturate it, and this run uses one worker,
> two of those four units. The dollar cap recorded in this manifest is $0.00 and
> is not an enforcement mechanism on this provider: `BudgetedLLMClient`'s USD
> pre-flight dimension self-disables at a zero rate
> (`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`), so the
> token budget and the wall deadline are the only limits that can stop this run.
> The same run on a metered provider would cost about $2.17 on
> `claude-haiku-4-5` or $6.52 on `claude-sonnet-4-6` at the rates in
> `llm/provider.py:58-61` and would require its own separate authorization;
> nothing in this statement carries over to one.

Rejected on the unchanged grounds of
[the fourth authorization](fresh-deduction-authorization-4.md). Option B, the
9p2i shape with 5 living voters, runs the same 100 paired units at the same
power for 2.7x the tokens and roughly twice the wall, so the extra spend buys
realism, not resolution. Option C, a metered Anthropic cross-check on a
subsample, measures the prompt-model pair rather than the model, and is the one
option where a bug costs money; it needs its own authorization and dollar limit.

This card authorizes limits, not a run. Nothing is spent until
[the fifth freeze](held-out-prefix-freeze-5.md) and
[the limits card](fresh-deduction-limits-5.md) have merged and
`audits/deduction-candidate/execution-manifest.md` carries these values
verbatim. No pilot, no smoke run and no re-run is authorized, including on
flat-rate service: a free call is still a call. A result here is a measurement
in either direction, never an adoption. The primary outcome, decision rule,
minimum actionable effect, tradeoff bound and `STOP_RULE` do not change; no new
provider, model, dependency, map or role is added; baseline-only campaigns stay
unchanged.

## Expected scope

`audits/deduction-candidate/run-<date>/` (new), the candidate's `README.md`
index and one dated line in its `checkpoint.md`, `docs/artifacts.md` (the
`audits/` row, recomputed because `audits/` bytes move), `tasks/README.md`'s
derived inventory sentence, this card. No instrument, generator, manifest or
frozen-analysis byte moves in the run's own pull request, and every acceptance
item that adds a gate carries a planted failure. Delivered on
`work/fresh-deduction-authorization-5`, based on `main` rather than stacked
(the runner starts only once both predecessors have merged), as one pull
request into `main`, landed by merge commit or fast-forward and never squashed,
with the trailer `Card: tasks/work/fresh-deduction-authorization-5.md`.

## Record impact

Adds a measurement record under `audits/`; adopts nothing; no recording,
report, DTO or weight byte moves; every candidate stays default-OFF; the
`docs/artifacts.md` audits row is recomputed with the record staged. If the
result later informs a fix, the fifth band's freeze record is marked
development in place, as the first four were.

## Validation

`uv run pytest tests/experiments -q` (fake and replay providers only) before the
run, the single authorized live invocation the manifest documents, then `uv run
python` over `scripts/validate_task_docs.py`, `scripts/check_doc_facts.py` and
`scripts/verify_ml_evidence.py` (offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.

## Results

The run was made, once, and it COMPLETED — the first complete run of this
evaluation, after four attempts that stopped at 1, 0, 3 and 25 units of 100.
Its whole record is
[audits/deduction-candidate/run-2026-09-16/RESULTS.md](../../audits/deduction-candidate/run-2026-09-16/RESULTS.md),
and every figure below is read off that directory rather than retyped from a
console.

**The outcome, in one paragraph.** On the fifty paired units of band 8000-8999,
`repaired_clock` scored `supported_correct_ejection` 0 times and
`combined_accounts` 2, so `b = 2`, `c = 0`, the two-sided exact McNemar p is 0.5
and the net paired difference is 2. All three clauses of `DECISION_RULE` fail:
p is not below 0.05, the net is not at least 10, and the candidate's net
increase in wrongful crew ejections is +7 (8 against the reference's 1) against
a permitted 2. **`combined_accounts` does not advance to an explicitly scoped
adopting review; the result is inconclusive, and inconclusive is not success.**
It is not rejected either, for the reason the manifest declared before the run:
the v4 citation repair raises this arm's ejection rate one-sidedly, so its 12
ejections against the reference's 1 are a joint product of the candidate and of
a prompt fix made to let the arm be measured at all, and this design cannot
separate them. A result is a measurement and never an adoption: nothing here
flips a flag, and both candidate levers stay default-OFF.

### Architecture and design references

Nothing in this pull request moves a design. The run is the one
[the execution manifest](../../audits/deduction-candidate/execution-manifest.md)
binds — its Inputs table (band 8000-8999), its authorized-values table, its
"Fifth authorization (2026-09-15)" section, its live gate and its frozen
analysis — under
[the preregistration](../../audits/deduction-candidate/preregistration.md)'s
design. The two one-sided effects the result is read against are the manifest's
"Accounts prompt set v4 (2026-09-15)" section's, declared before any unit ran.
The band is [the fifth freeze card](held-out-prefix-freeze-5.md)'s, the ceilings
[the limits card](fresh-deduction-limits-5.md)'s, and the sizing measurement
[the second calibration](fresh-deduction-calibration-2.md)'s. No instrument,
generator, manifest, prompt or frozen-analysis byte moves here, which is what
this card's Expected scope requires.

### What was checked before the spend

All offline, all at $0, on commit `a495fec5`:

* `.venv/bin/pytest tests/experiments -q` — **491 passed**.
* One fake-provider dry run over two units, into a directory outside the
  repository: 2 units an arm, 12 calls an arm, `total_cost_usd` 0.0, limits
  3,844,000 / 422,000 run-level and 116,000 / 16,000 per unit, sampling
  4,096 / 0.4 and 1,024 / 0.2, freeze record sha256 `46f2ba61…fb4c1e`. Its
  output was not committed.
* The replay-double rehearsal on the refreshed profile under these limits:
  `.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py -k
  "TestUsageReplay or TestFeasibility" -q` — **27 passed**, including
  `test_the_rehearsal_is_green_on_the_refreshed_profile_under_the_new_limits`
  and the planted
  `test_the_fourth_authorizations_run_input_ceiling_is_refused_on_this_profile`.
* The offline gate, which constructs no client:
  `assert_limits_are_feasible(limits=AUTHORIZED_LIMITS)` returned,
  `assert_manifest_binds_the_live_band()` returned, and
  `assert_ready_for_a_live_run` returned the verified frozen set — 50 accepted
  seeds 8000 to 8057, 8 skips, record sha256 `46f2ba61…fb4c1e`.
* The authorized values the instrument will enforce, read out of the module and
  compared against Constraints: provider `featherless`, model
  `Qwen/Qwen3.6-27B`, prompt set `qwen3_6_27b` at `ACCOUNT_PROMPT_SET_REVISION`
  **v4**, caps 4,096 / 1,024, temperatures 0.4 / 0.2, run 3,844,000 / 422,000,
  per unit 116,000 / 16,000, 21,600 s of model work inside 28,800 s elapsed,
  `max_cost_usd` 0.0, roster 4/1/3, sequential, transport 4 attempts at 180 s,
  `CALIBRATED_UNIT_*` 38,440 / 4,176, `unit_output_reservation()` 15,360. The
  manifest carries `RESUMPTION_CLAUSE` verbatim. Nothing disagreed, so the run
  proceeded.

### The sitting

One sitting, `2026-09-16T08:33:05Z` to `2026-09-16T10:27:58Z`, exit 0, **no
stop and no resumption**. 100 of 100 units, 601 attempts, 600 completions and
one completion the provider billed and refused. Against every authorized limit:

| Limit | Authorized | Actual | Used |
| --- | --- | --- | --- |
| Run input / output tokens | 3,844,000 / 422,000 | 2,243,923 / 144,677 | 58.4% / 34.3% |
| Per-unit input / output tokens | 116,000 / 16,000 | 34,683 / 2,898 (largest unit) | 29.9% / 18.1% |
| Elapsed wall / model work | 28,800 s / 21,600 s | 6,891.9 s / 6,885.9 s | 23.93% / 31.88% |
| Per-call cap, turn / vote | 4,096 / 1,024 | 1,075 / 132 | 26.2% / 12.9% |
| Transport attempts | 4 per call at 180 s | 1 per call, 601 of 601 | 25% of the bound |
| Dollar | $0.00 marginal | $0.00 | not an enforcement mechanism here |

`repaired_clock`: 300 attempts, 300 completions, 1,059,714 in / 59,427 out,
2,988.2 s of model work, 0 charged failed attempts, 0 defaults, 0 retries.
`combined_accounts`: 301 attempts, 300 completions, 1,184,209 in / 85,250 out,
3,897.6 s, 1 charged failed attempt (3,460 in / 245 out), 1 defaulted turn by
validation, 0 retries. Cap-signal disagreements 0 on both arms; no truncation by
either signal. Every one of `STOP_RULE`'s conditions is tabulated in RESULTS.md
with its evidence, and none fired.

### Decisions this run took

1. **The stop rule was never reached, so the resumption clause was never
   used.** One sitting, one invocation, no `--resume`, and the final checkpoint
   carries an empty `abandoned` block.
2. **The archive is named for the UTC date its own records carry**
   (`run-2026-09-16`), as the fourth run's was, so a reader comparing a
   timestamp against the folder never reconciles two clocks.
3. **Everything was committed.** The archive is about 10 MB — the report, the
   log, all 100 replays, the final checkpoint, the reconciliation and its
   derivation, and all fifty rendered prefixes with the derivation that writes
   them — which is inside the size at which this card would have made the
   runner choose what to keep.
4. **The reconciliation is a committed derivation, not a typed table**, and it
   computes the two pre-declared diagnostics with the instrument's own frozen
   rules rather than a second implementation of them: `ROLE_LEAK_RULE` through
   `states_own_role_or_kill` over committed turns, and the role-split profile
   with `PERCENTILE_RULE`'s nearest-rank p95, with each seed's ground-truth
   impostor read off its own replay's scripted kill.
5. **The runner flag is elided in `run.log`.** No committed file outside the
   manifest and the instrument may carry it, and a `.log` is not exempt by
   being unscanned.
6. **The `finish_reason` acceptance item is met as far as the unchanged
   instrument allows, and the gap is stated rather than papered over.** The cap
   check reads each call's `finish_reason` live and either signal stops the run,
   and the report records `cap_signal_disagreements` per arm (0 and 0); the
   per-call reading itself is a calibration-mode field that the evaluation's
   `InstrumentReport` and the replays do not serialize. Recording it would have
   meant moving an instrument byte, which this card's Expected scope forbids in
   the run's own pull request. RESULTS.md says exactly what the archive does and
   does not support.

### Verification

```
$ .venv/bin/pytest tests/experiments -q
491 passed
$ .venv/bin/python scripts/validate_task_docs.py
Task docs validation passed: 390 historical phase tasks and 390 prompts; 61 work cards.
$ .venv/bin/python scripts/check_doc_facts.py
$ .venv/bin/python scripts/verify_ml_evidence.py
checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5
$ .venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q
80 passed
$ bash scripts/check.sh
7824 passed, 20 skipped, 3 xfailed, 10 warnings   (frontend: 515 tests, 19 files)
All checks passed!
```

`scripts/check.sh` was run directly, not through a pipe, and its real exit code
read: 0. The live evaluation is not a check and was not re-run. The archive was
scanned for the API key before it was committed — a count-only comparison
against the whole key and against its first six characters, over all 107 files
— and both counts are 0, and `assert_report_holds_no_prefix_bytes` was re-run
over the committed report against all fifty rebuilt prefixes and passed.

### Limitations

* **The two declared one-sided effects are not separated.** The citation repair
  raises the candidate's ejection rate and the turn bound lowers its citation
  relevance, both on the treatment arm alone. The wrongful-ejection bound fails,
  and this design cannot apportion that failure between the candidate and the
  revision that made its ejections visible. Seven of the candidate's 24 naming
  ballots were graded off-target and 44 of its 46 guard rewrites are still
  `uncited_coerced`, so both channels are visibly live.
* **Fifty paired units resolve a net of 10, not a net of 2.** A net of 2 is
  inside the noise this sample carries; nothing here says whether a real effect
  of that size exists.
* **The fourth run's 24 complete units are not pooled**, and this record does
  not pool them.
* **Both diagnostics are loose at these numerators.** One leaking turn per arm
  on a rule with two-sided error bounds the leak rather than measuring it, and
  the self-tell counts the ballot's OPENING only.
* **Every accepted seed of band 8000-8999 is now development data**, and there
  is no unrendered remainder to salvage: any future confirmation claim needs a
  new band frozen under a new card by a preparer who has not read the run's
  record.
* **One model, one prompt set, one roster.** 4p1i with three living voters on
  Featherless `Qwen/Qwen3.6-27B`; nothing here carries to another model, a
  metered provider or the 9p2i shape.
