# Fresh-model deduction evaluation — run of 2026-09-13

**The run stopped inside the first unit of one hundred, on a provider-side
empty completion. No unit completed, no paired unit exists, the primary outcome
was not measured and the decision rule is not evaluable.** The stop authorizes
no retry and no widening of any limit. Nothing here is an adoption, and nothing
here is a measurement of the candidate either.

This directory is the partial evidence and the unresolved accounting that
[the execution manifest](../execution-manifest.md)'s stop rule requires a
stopped run to retain. It is the second such record. The first is not on `main`
— PR #445 was closed unmerged — and lives on the archive branch
`work/fresh-deduction-run` at
`audits/deduction-candidate/run-2026-09-10/RESULTS.md`, readable with
`git show origin/work/fresh-deduction-run:audits/deduction-candidate/run-2026-09-10/RESULTS.md`.
The two are compared at the end.

## The design that was attempted

One meeting per frozen held-out prefix under two paired arms — the reference
`repaired_clock` (`format_version=2`, `evidence_reasoning_version=2`) and the
candidate `combined_accounts` (the reference plus `public_account_version=1`
and `attributed_testimony_version=1`) — over the 50 proof-free scripted
prefixes of the **second** held-out band, 5000-5999, frozen by the owner's
merge of PR #446 as `ca6e97d6` (accepted seeds 5000-5052, 3 `witnessed_kill`
skips). Sequential, both arms per seed before the next seed, on Featherless
`Qwen/Qwen3.6-27B` under the limits the owner authorized by merging #437 as
`0f49d8e6` and re-authorized for this run on 2026-09-13
([the run's card](../../../tasks/work/fresh-deduction-authorization-2.md)).
50 prefixes x 2 arms = 100 units, about 600 model calls, scored on
`supported_correct_ejection` with the two-sided exact McNemar test over the
discordant pairs. **The run reached call 5 of about 600, inside unit 1 of 100.**

The run was made from commit `78fa2841` on branch `work/fresh-deduction-run-2`,
with `experiments/fresh_deduction_instrument.py` at sha256
`2e8e7f87 8b3f3ec5 f3e44ee4 09b8368b ebfb771c 4857d24a 0cdea52c 7f99c00b`:

```sh
.venv/bin/python -c "import hashlib, pathlib; \
print(hashlib.sha256(pathlib.Path('experiments/fresh_deduction_instrument.py').read_bytes()).hexdigest())"
```

The invocation was exactly the one
[the manifest documents](../execution-manifest.md) in its "The live gate"
section — the same module, provider, manifest path and runner flag, with
`--output-dir` and `--json` pointing outside the repository — run once, with
the API key delivered through `uv run --env-file` from a credential-only file
outside the repository that was deleted afterwards. It is not reproduced here:
no committed file outside the manifest and the instrument may carry the runner
flag, and
`tests/experiments/test_fresh_deduction_instrument.py::TestLiveGate::test_no_committed_file_outside_the_module_and_the_manifest_names_the_flag`
scans every tracked file to keep that true.

**No report JSON exists.** `main()` writes the report only after
`run_instrument` returns, and it raised, so `--json` produced no file. The
instrument's own partial-state record is [stop.log](stop.log), and the single
per-unit replay is [repaired_clock-seed-5000.jsonl](repaired_clock-seed-5000.jsonl).

## What ran

| Unit | Arm | Seed | Result |
| --- | --- | --- | --- |
| 1 | `repaired_clock` | 5000 | **stopped** during ballot collection, on the meeting's fifth model call |

No unit of `combined_accounts` was started. The game reached tick 7, the meeting
opened, three turns resolved and one ballot resolved; the second ballot's call
returned a completion the provider client refused to record, and the meeting was
written out as `meeting_aborted` rather than `meeting`.

## The stop

Quoted from [stop.log](stop.log):

```
RuntimeError: Featherless response carried no choices (model='Qwen/Qwen3.6-27B');
refusing to record an empty completion.
```

```
InstrumentAborted: RuntimeError: Featherless response carried no choices
(model='Qwen/Qwen3.6-27B'); refusing to record an empty completion.;
0/100 units completed, 110.9s elapsed, 106.3s model work;
repaired_clock: 4 calls, 13182 in, 993 out
```

### What actually happened, from the archived rows

Reproduce every figure in this section with:

```sh
.venv/bin/python -c "
import json
from pathlib import Path
D = Path('audits/deduction-candidate/run-2026-09-13')
rows = [json.loads(l) for l in (D / 'repaired_clock-seed-5000.jsonl').read_text().splitlines() if l.strip()]
kinds = {}
for r in rows:
    kinds[r['kind']] = kinds.get(r['kind'], 0) + 1
ab = next(r for r in rows if r['kind'] == 'meeting_aborted')
calls = ab['llm_calls']
print('row kinds        ', kinds)
print('meeting rows     ', sum(1 for r in rows if r['kind'] == 'meeting'))
print('failed_call rows ', sum(1 for r in rows if r['kind'] == 'failed_call'))
print('recorded calls   ', len(calls))
print('input tokens     ', sum(c['input_tokens'] for c in calls))
print('output tokens    ', sum(c['output_tokens'] for c in calls))
print('cost_usd         ', sum(c['cost_usd'] for c in calls))
print('largest output   ', max(c['output_tokens'] for c in calls))
print('models           ', sorted({c['model'] for c in calls}))
print('error_type       ', ab['error_type'])
print('experiment config', json.dumps(rows[0]['experiment_config'], sort_keys=True))
print('temporal version ', rows[0]['temporal_observation_version'])
"
```

```
row kinds         {'tick': 8, 'meeting_aborted': 1}
meeting rows      0
failed_call rows  0
recorded calls    4
input tokens      13182
output tokens     993
cost_usd          0.0
largest output    343
models            ['Qwen/Qwen3.6-27B']
error_type        RuntimeError
experiment config {"attributed_testimony_version": null, "bounded_rebuttal_version": null, "crew_idle_policy": "hub_wait", "evidence_reasoning_version": 2, "format_version": 2, "meeting_reset": "preserve", "post_meeting_retarget": false, "public_account_version": null, "redistribution_policy": "lowest_id", "sabotage_threshold": "six_sevenths", "self_report": false, "vent_exit_policy": "target_distance"}
temporal version  2
```

The four resolved calls are three meeting turns (`p-3` 3,301/343, `p-1`
3,242/210, `p-2` 2,784/323) and one ballot (`p-1` 3,855/117), every one of them
served by `Qwen/Qwen3.6-27B` — the authorized checkpoint, so the client's
identity refusal had nothing to refuse. The fifth call, the second voter's
ballot, is the one that failed. It appears in no row at all, for the reason
given below.

### What the provider returned, and why nothing recorded it

`llm/featherless_client.py::_raw_from_response_body` maps an OpenAI-shaped
chat-completions body onto a raw response and fails loud on the shapes a
completed response never produces. The first of them is the one that arrived:

> * empty / missing ``choices`` — no completion to record;

The body was a parseable 2xx JSON document carrying no `choices`. That is not in
the client's retry class: `_send_with_retry` retries a retryable status
(429/500/502/503/504), an `httpx.TransportError` and a `json.JSONDecodeError`,
and this response was none of the three — it was a well-formed body of the wrong
shape. So the send succeeded, the mapping refused it, and the `RuntimeError`
propagated.

It then crossed `_InstrumentClient.complete`'s `except BaseException` branch,
which captures a call the provider **billed and then refused** by reading the
spend off the parse-failure metadata riding the exception
(`llm.provider.extract_parse_failure`). A bare `RuntimeError` from the transport
mapping carries no such metadata, so `failure is None` and the module's stated
rule applies — "an exception without it bought nothing and is re-raised
untouched"
(`experiments/fresh_deduction_instrument.py:1253-1266`). The attempt therefore
entered neither the client's ledger nor the work clock, which is why the
accounting above reports 4 calls and 106.3 s of model work rather than 5 and
slightly more.

Two consequences, stated rather than left to be found:

1. **The failed attempt's spend is unknown, not zero.** If Featherless billed
   for the empty completion, those tokens are invisible to both sides of every
   comparison this instrument makes. On this provider the marginal cost is
   $0.00 either way, and the amount at stake is one call against a 2.4 M
   ceiling that the run used 0.55% of, so nothing here is load-bearing — but
   "bought nothing" is an assumption about the provider, not a measurement.
2. **The failed attempt's wall is unaccounted.** 110.9 s elapsed against 106.3 s
   of charged model work; the 4.6 s difference covers game setup, the eight
   ticks and the failed call together. The model-work window is charged for an
   attempt the window itself cut off, and for a billed-and-refused payload, but
   not for this class.

Neither of these is what stopped the run, and neither is a defect claim: the
first is a property of the provider, the second is the behaviour the module
documents in the comment quoted above.

### Is this the defect that stopped the first run? No.

The run of 2026-09-10 stopped because the instrument's own post-unit spend
reconciliation could not see a paid call. PR #447 repaired that, and
`tests/experiments/burned_call_double.py` reproduces the old stop and passes
now. **This run did not reach that code at all.** `_reconcile_recorded_spend`
and `_assert_charged_spend_is_within_caps` run after a unit's meeting resolves;
this unit's meeting never resolved, so the repair the run was made to exercise
under a real provider was not exercised. It remains proved offline and unproved
live.

### How the stop sits against the frozen rule

`STOP_RULE`'s enumeration does not name a provider transport failure. Two other
parts of the manifest do, and both describe exactly what happened:

- Inputs, "Maximum opportunities": "An attempt that never resolves — a transport
  failure, a truncation, an exhausted limit — is a stop, and the partial state is
  reported rather than replaced."
- "How each limit is enforced", last bullet: "every way a unit can fail is one of
  these stops, including a provider transport failure and a mid-run legacy body
  handle, so an attempt that never resolved reports its partial state rather than
  escaping as a bare exception."

So the manifest binds this as a stop in prose while the frozen string enumerates
the conditions the instrument can detect about a completion it received. That
asymmetry is recorded here as an observation, not as a finding: unlike
2026-09-10, the document and the code did not disagree about this run's fate.
The instrument did precisely what both sentences promise — it converted the
provider's exception into `InstrumentAborted` carrying the units completed, the
elapsed wall, the model work and the per-arm accounting, instead of letting it
escape bare. **No retry and no widening follows from it either way.**

## Primary outcome, discordant pairs and the decision rule

**Not measured.** The primary outcome is a per-seed paired binary and no seed
completed either arm, so there are zero paired units against the 50 the design
requires, and zero completed units against the 100 planned.

| Quantity | Value |
| --- | --- |
| Paired units completed | 0 of 50 |
| Units completed | 0 of 100 (decision coverage 0%) |
| `repaired_clock` supported-correct ejections | not computed; its only unit stopped before grading |
| `combined_accounts` supported-correct ejections | not computed; no unit was started |
| Discordant pairs `b` | not evaluable (no paired unit) |
| Discordant pairs `c` | not evaluable (no paired unit) |

No grader ran. Grading is a pure function over finished `UnitRecord`s that
`run_instrument` calls only after the last unit, and it never reached that
point.

`exact_mcnemar_p` on zero discordant pairs returns 1.0, and that value is an
artifact of an empty sample rather than a result:

```sh
.venv/bin/python -c "import sys; sys.path.insert(0, 'scripts'); \
from paired_stats import exact_mcnemar_p as p; print(p(0, 0))"
```

```
1.0
```

The docstring says so itself: "With no discordant pairs at all there is no
evidence either way and p is 1.0." It must not be read as a null result.

The three clauses of `DECISION_RULE`, each evaluated:

| Clause | Bar | State |
| --- | --- | --- |
| Two-sided exact McNemar p over the discordant pairs | below 0.05 | **not evaluable** — no paired unit; the 1.0 above is the empty-sample constant |
| Net paired difference `b - c` | at least 10 of 50 | **not evaluable** — `b` and `c` are undefined on 0 paired units |
| Candidate's net increase in wrongful crew ejections | no larger than `b - c` | **not evaluable** — see the bound below |

**Conjunction: not evaluable.** `combined_accounts` does not advance. It is
also not rejected: a run that produced no outcome refutes nothing. Under
`DECISION_RULE`'s own wording, "any other result is inconclusive, and
inconclusive is not success" — and this is weaker than inconclusive, because
inconclusive presumes a sample.

**Wrongful-ejection bound.** `WRONGFUL_EJECTION_TRADEOFF` counts a unit whose
meeting ejected a player whose hidden role is CREWMATE. **Zero wrongful
ejections on both arms, and the figure carries no information:** the one meeting
that opened was aborted mid-ballot, so it reached no verdict at all, and the
other 99 units never ran. The bound is defined as a net increase over 50 paired
units and cannot be computed on zero.

## Meeting-internal defaults and charged failed attempts, per arm

Counted here from the archived rows, since no report was written. The
`meeting_aborted` row carries no `deadline_default` marker and the replay carries
no `failed_call` row at all, so both counters are zero on both arms.

| Arm | Units | Defaulted turns | Defaulted votes | By validation | By deadline | Degraded openings | Units with defaults | Charged failed attempts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 0 completed (1 stopped) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `combined_accounts` | 0 (never started) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

The "a default this instrument cannot classify is a stop" condition did not
fire, because no default was recorded. The failed call described above is **not**
a charged failed attempt in the reconciliation's sense: a charged failed attempt
is a `FailedCallReplayEntry` row carrying usage, and this attempt produced no row
— the provider client raised before the meeting layer's failure handler could
record one. The zero in the last column is therefore the absence of the class,
not a measurement of its rate.

Both counters being zero says nothing about the rate the manifest anticipates
(about 1 in 50 calls); five calls establish no rate.

## Usage against every authorized limit

Actual spend, from the archived rows and the partial-state record:

| Arm | Recorded calls | Input tokens | Output tokens | `cost_usd` |
| --- | --- | --- | --- | --- |
| `repaired_clock` | 4 | 13,182 | 993 | 0.0 |
| `combined_accounts` | 0 | 0 | 0 | 0.0 |
| **Run total** | **4 recorded (+1 failed, unknown spend)** | **13,182** | **993** | **0.0** |

| Limit | Authorized | Actual | Used | Fired? |
| --- | --- | --- | --- | --- |
| Run input tokens | 2,400,000 | 13,182 | 0.55% | no |
| Run output tokens | 200,000 | 993 | 0.50% | no |
| Per-unit input tokens | 45,000 | 13,182 (`repaired_clock`) | 29.3% | no |
| Per-unit output tokens | 4,000 | 993 (`repaired_clock`) | 24.8% | no |
| Elapsed wall | 6 h (21,600 s) | 110.9 s | 0.51% | no |
| Model work | 4 h (14,400 s) | 106.3 s | 0.74% | no |
| Per-call output cap | 2,048 turn / 1,024 vote | largest output 343 (a turn) | 16.7% of its cap | no |
| Dollar | $0.00 marginal | $0.00 | — | not an enforcement mechanism on this provider |

**Marginal cost: $0.00.** Every recorded `cost_usd` on this run is exactly 0.0,
by construction rather than by measurement: the Featherless provider's zero
pre-flight rate disables `BudgetedLLMClient`'s USD dimension
(`llm/featherless_client.py:243-244`, `llm/budgeted_client.py:118-126`). The
resources consumed were subscription capacity and 110.9 seconds of wall on one
worker.

The one projection figure this run adds: 106.3 s of model work over 4 resolved
calls is 26.6 s per call, ABOVE the 12-23 s band the wall deadline was set on and
above the 11.7 s per call the run of 2026-09-10 measured over 12 calls. At 26.6 s
per call, 600 calls would be about 4 h 26 m of model work against an authorized
4 h — i.e. on this sample the model-work window, not the token budget, would have
been the binding constraint. Four calls establish no rate, and this is flagged as
a cell a future authorization should price rather than as a finding.

## Every stop condition, checked

`STOP_RULE`'s enumerated conditions, each against what the run recorded:

| Stop condition | Fired? | Evidence |
| --- | --- | --- |
| Token budget exhausted, per-unit or run level | no | 0.55% / 0.50% of the run ceilings; 29.3% of the per-unit input ceiling |
| Elapsed wall deadline | no | 110.9 s of 21,600 s |
| Model-work window | no | 106.3 s of 14,400 s |
| A response that reached its output cap (truncation) | no | largest output 343 against a 2,048 turn cap |
| A held-out digest or skip differing from the frozen manifest | no | `verify_frozen_set` passed: 50 prefixes, 3 skips, freeze manifest sha256 `b93262acc21af1b2c98ec97f84d9f3b23a8740ab7b22fc91ac79f3c2911cdfa1` |
| A rendered prompt or regenerated prefix matching `body-p-\d+-\d+` | no | asserted over all 50 regenerated prefixes before the run; the four rendered prompts carry only the v2 handle `body-p-4` (see below) |
| A unit whose recorded clock or experiment config is not the arm's | no | the recorded config is the reference arm's exactly (`format_version=2`, `evidence_reasoning_version=2`, both candidate versions null) at `temporal_observation_version` 2; the in-run assertion never executed, because it runs after a meeting resolves |
| A recorded meeting default the instrument cannot classify | no | no default was recorded |
| The recorded-spend reconciliation (repaired by PR #447) | no | never reached: it runs after a meeting resolves |
| **A provider transport failure** | **YES** | the stop above — bound as a stop by the manifest's Inputs row and its enforcement section, and absent from `STOP_RULE`'s own enumeration |

No stop condition reads an outcome, and none did here: the run stopped on a
provider fault, at a fixed point in a fixed sample, with no interim analysis.

**On the body-handle check.** Scanning the whole archive for
`body-p-\d+-\d+` returns exactly one match, and it is not on a surface the stop
condition covers: it is the engine's own entity id inside tick 7's `actions`
field of the replay, the raw record of the scripted report step. What the
condition covers is the regenerated prefixes, the rendered prompts and the
emitted report (`experiments/fresh_deduction_instrument.py:1730`, `:2072`,
`:2906`), and all three are clean — the four prompts the model was handed carry
only `body-p-4`, which is what temporal v2 renders by construction. Reproduce
both halves with:

```sh
.venv/bin/python -c "
import json, re
from pathlib import Path
rows = [json.loads(l) for l in Path('audits/deduction-candidate/run-2026-09-13/repaired_clock-seed-5000.jsonl').read_text().splitlines() if l.strip()]
ab = next(r for r in rows if r['kind'] == 'meeting_aborted')
print('legacy handles in tick actions:', re.findall(r'body-p-\d+-\d+', json.dumps([r for r in rows if r['kind'] == 'tick'])))
print('handles in the rendered prompts:', sorted({h for c in ab['llm_calls'] for h in re.findall(r'body-p-\d+(?:-\d+)?', c['prompt'] or '')}))
"
```

```
legacy handles in tick actions: ['body-p-4-4']
handles in the rendered prompts: ['body-p-4']
```

## Held-out status

**Seed 5000 of the second band is revealed by this archive. Seeds 5001-5052 were
never rendered to the model.**

The instrument serialized no prefix — it never does, and
`assert_report_holds_no_prefix_bytes` refuses a report that carries one. What
this directory publishes is the one replay file for seed 5000, whose
`meeting_aborted` row carries the four prompts that prefix rendered under the
reference arm, and whose tick rows carry the scripted steps. That prefix was run,
so it is no longer held out, and the manifest's rule is that the prefixes are
archived with the results once that is true.

The other 49 accepted prefixes were regenerated in process, checked against the
frozen digests and then discarded unrendered. **They are deliberately NOT
archived here**, and that is a decision rather than an omission: the manifest
archives prefixes "when they are no longer held out", and these 49 still are.
Committing them would convert the whole band to development data to no purpose,
which is the cost the first band already paid once. The runner opened, printed
and reasoned about no prefix before the run.

Three consequences the owner's next decision has to carry:

1. **This run did not convert the band's status.** The freeze manifest still
   reads `held_out`, and flipping it belongs to the decision that acts on this
   record, not to the runner. If this result informs a fix, the manifest's Roles
   section requires that flip and a new band under a new card.
2. **A re-run on this same band would not be a clean 50-unit held-out sample**,
   because one of its seeds is now public. Any future confirmation claim needs a
   new band frozen under a new card, by a preparer who has not read this
   document.
3. **Two of the band's 50 seeds' worth of margin are gone across two runs** —
   seed 3000 of the first band and seed 5000 of the second. Neither run reached
   a second seed.

## Compared with the first attempt

| | 2026-09-10 (PR #445, closed) | 2026-09-13 (this run) |
| --- | --- | --- |
| Band | 3000-3999 (now development) | 5000-5999 |
| Units completed | 1 of 100 | **0 of 100** |
| Arms reached | both (unit 2 stopped) | reference only |
| Calls | 12 paid | 4 resolved, 1 failed |
| Tokens | 36,003 in / 3,401 out | 13,182 in / 993 out |
| Elapsed / model work | 159.7 s / 140.2 s | 110.9 s / 106.3 s |
| Seconds per call | 11.7 | 26.6 |
| Cause | the instrument's spend reconciliation could not see a paid call | the provider returned a completion with no `choices` |
| Whose defect | the instrument's — repaired by PR #447 | the provider's; the instrument stopped as designed |
| Marginal cost | $0.00 | $0.00 |

The first run found a bug in this repository and it was fixed. This run found
nothing in this repository: every gate it reached was green, the client refused
an unrecordable completion exactly as it is written to, and the instrument
converted that into a partial-state stop exactly as the manifest promises. What
it establishes is that the evaluation has now twice failed to reach its second
seed, for two unrelated reasons, and that the repaired reconciliation has still
never been exercised against a real provider.

## Verdict

In the preregistration's own vocabulary — advance to an explicitly scoped
adopting review / revise and evaluate a new version / reject / gather more
evidence under a new authorized manifest — this run reaches **none of the
four**, because none of them is a statement a zero-unit sample supports. The
only route forward it identifies is **more evidence under a new authorized
manifest**, and the preregistration is explicit that "more evidence is not an
automatic spending authorization": that is an owner decision on a new card, with
its own limits.

What a third authorization would have to price, on this run's evidence and
without treating four calls as a rate:

- **The provider can return an unrecordable completion**, and a single one ends
  a 100-unit sequential run at whatever point it arrives. Nothing in the
  instrument decides that; the choice between stopping and retrying such a call
  is a design question for the owner, and both answers have a real cost — a
  retry re-samples a frozen design mid-run, and a stop makes the run's
  completion depend on ~600 consecutive provider successes.
- **26.6 s per call** would put 600 calls past the authorized 4 h of model work.
- **The repaired reconciliation is still unproved live**, so a third run is
  also the first live test of PR #447's fix.
- **A third run needs a third band**, because this one has a public seed.

**A result is a measurement and never an adoption.** This one is not even a
measurement: it is an operating record of a stop. `combined_accounts` neither
advanced nor was rejected, and this document changes no default, no experiment
switch and no baseline.
