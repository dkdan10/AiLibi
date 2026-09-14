# Third run of the fresh-model deduction evaluation

**Status:** done

## Outcome

The fresh-model deduction instrument runs once more, on the third held-out
band, with the provider's empty completions retried within a stated bound and
the wall window widened to the pace the second attempt measured. The run's
actual tokens, wall and cost are recorded against every limit, the paired
result is evaluated under the frozen decision rule, and the outcome is written
down as a measurement that adopts nothing.

## Evidence

Two attempts have stopped inside their first unit: the first (PR #445, closed)
on an accounting defect repaired by #447, the second (PR #448, closed) on a
provider response that carried no completion, which the instrument treated as
a stop with no retry. Each rendered one held-out seed, so bands 3000-3999 and
5000-5999 are development data. On 2026-09-13, in the coordinator's session,
the owner instructed "Perform all of the recommended steps and close 448" in
reply to the coordinator's four-step recommendation: a bounded retry for
provider failures that return nothing, a third band, a third authorization
with the model-work window widened to 6 h within 8 h elapsed, and a fresh
runner. This card is the record of that authorization; the limits below are
the first authorization's with only the wall row changed. The run is
dispatched after [the third freeze](held-out-prefix-freeze-3.md) and
[the transport-resilience card](fresh-deduction-instrument-transport-resilience.md)
are merged, so that the execution manifest carries the retry bound, the widened
window and the third band's binding before any call is made.

## Acceptance

- [x] The execution manifest's authorization fields carry exactly the values in
  Constraints, and the instrument enforces them: the per-unit `GameBudget` with
  a run-level parent, the `RunDeadline` at 8 h elapsed, the 6 h model-work
  window, the per-call caps, sequential order, the transport retry bound.
  Checked against the module constants before any wall time was committed —
  `AUTHORIZED_LIMITS` reads 2,400,000 / 200,000 run, 45,000 / 4,000 per unit,
  `max_cost_usd` 0.0, `elapsed_seconds` 28,800, `model_work_seconds` 21,600;
  `AUTHORIZED_SAMPLING` 2,048 / 0.4 and 1,024 / 0.2;
  `MAX_TRANSPORT_ATTEMPTS` 4 at `PER_ATTEMPT_TIMEOUT_SECONDS` 180.0 — and
  enforced in the event: the per-unit output ceiling is what stopped the run
  (Results, "The stop").
- [x] The runner regenerates the frozen set from the band in the manifest and
  the instrument verifies every digest and the skip list before any client is
  constructed; the runner opens no prefix before the run.
  `assert_manifest_binds_the_live_band` and `assert_ready_for_a_live_run` were
  run offline first and returned the verified set — 50 accepted prefixes,
  9 skips, freeze record sha256 `7ded1990…6ecd37` — and the live run repeated
  both before building a client. No prefix was opened, printed or reasoned
  about before the run; the two the run rendered are archived after it.
- [x] The run records actual tokens, elapsed wall, model-work time, retried and
  unaccounted attempts, and the $0.00 marginal cost against these limits, per
  arm and for the run; an exhausted budget or deadline stops the run and
  authorizes no retry beyond the stated per-call bound.
  `audits/deduction-candidate/run-2026-09-13-3/usage-reconciliation.json` and
  the RESULTS tables: 22 attempts, 82,904 input, 9,200 output, $0.00, 369.1 s
  elapsed and 368.8 s model work, 0 retried calls and 0 unaccounted attempts on
  both arms. The exhausted per-unit output budget stopped the run and no retry
  or widening followed.
- [x] The paired result is evaluated under the frozen decision rule (exact
  McNemar p over the discordant pairs, the net difference bar, the
  wrongful-ejection bound) and written down in the preregistration's own
  vocabulary as a measurement; every stop condition is checked and reported.
  All three clauses are **not evaluable** on the 1 paired unit the run reached;
  `b = c = 0`, `exact_mcnemar_p(0, 0)` is the empty-sample constant 1.0, and
  wrongful ejections are 0 on both arms because no meeting ejected anyone. The
  verdict reaches none of the preregistration's four decisions. Every
  `STOP_RULE` condition is tabulated in RESULTS with its evidence; exactly one
  fired.
- [x] The results, the per-unit records, the usage reconciliation and the
  rendered prefixes (development data once archived) land under
  `audits/deduction-candidate/run-<date>/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row recomputed.
  `audits/deduction-candidate/run-2026-09-13-3/` holds `RESULTS.md`,
  `stop.log`, the four per-unit replays, `usage-reconciliation.json` and
  `rendered-prefixes.json` (seeds 6000 and 6001 only); the candidate README
  indexes it, `checkpoint.md` carries one dated line, and the `audits/` row is
  recomputed below.

## Constraints

Authorized limits: the token, per-call, cost, roster and execution values the
owner authorized by merging #437 on 2026-09-07 (merge commit `0f49d8e6`),
unchanged, with the wall window widened by the owner's instruction of
2026-09-13 (see Evidence):

| Field | Value |
| --- | --- |
| Provider | `featherless` |
| Model | `Qwen/Qwen3.6-27B` (locked 2026-07-12, Task 16.2). Non-thinking with `enable_thinking=false` pinned on every call, `response_format_mode = json_object`, prompt set `qwen3_6_27b` — all carried from the model lock, not re-decided here |
| Per-call token cap | turn 2,048 output / vote 1,024, the shipped defaults unchanged. The committed lab rows for this model-and-prompt-set pair ran at `max_tokens=4096` and never exceeded 195 output tokens, so a truncation is a real signal rather than a cap artifact |
| Total token budget | 2,400,000 input / 200,000 output run-level, and 45,000 input / 4,000 output per unit. Hard stop. Projection for option A: 600 calls; input `repaired_clock` 3,636/call x 300 + `combined_accounts` 2,441/call x 300 = 1,823,100; output 600 x 220 = 132,000 |
| Wall-clock deadline | 6 h of model work within an 8 h elapsed deadline. Widened from 4 h / 6 h on 2026-09-13: the second attempt measured 26.6 s/call over its four resolved calls against 11.7 s/call on 2026-09-10, and six hundred calls at the slower pace need about 4 h 26 m; the 2 h elapsed margin still covers one recorded 3h21m provider-side stall (`audits/audit-phase-21-adopting-record.md:373-380`) |
| Dollar limit | $0.00 marginal, recorded as bookkeeping and not as an enforcement mechanism. The provider's zero pre-flight rate disables the USD dimension, so only the token budget and the deadline can stop a run |
| Cost statement | The paragraph quoted below, verbatim |
| Roster | 4p1i with 3 living voters at meeting open. A change of roster invalidates the token budget above and requires a new authorization |
| Execution mode | sequential |
| Held-out preparer | The third freeze's preparer session (the pull request of [the third freeze card](held-out-prefix-freeze-3.md); band 6000-6999). Runner: a fresh session dispatched by the coordinator on this card after that freeze and [the transport-resilience card](fresh-deduction-instrument-transport-resilience.md) are merged; it opens no prefix before the run and regenerates the set from the frozen band, verifying every digest. The coordinator dispatches and runs nothing |
| Death-tick body handle | Left as temporal v2 renders it in both arms, stated in the manifest, and asserted by the regex over the rendered prompts and the frozen prefixes |

The cost statement the manifest carries, verbatim:

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

Rejected, with grounds, so the choice is on the record rather than implied by
the number that was written down:

Option B, the 9p2i shape with 5 living voters, runs the same 100 paired units
and therefore has the same statistical power, at 2.7x the tokens and roughly
twice the wall. The extra spend buys a larger table and a roster closer to the
corpus the calibration was measured on — realism, not resolution.

Option C, a metered Anthropic cross-check on a subsample at $0.22-$6.52, is
rejected from this authorization on a different ground: the `qwen3_6_27b` prompt
family was authored for this model and locked on that basis, so a metered run
measures the prompt-model pair rather than the model. It is also the only option
where a bug costs money. If the owner wants it, it needs its own authorization
with its own dollar limit.

This authorizes limits, not a run. Nothing may be spent until
[the renderer repair](evidence-renderer-salience.md) and
[the provenance gaps](recorded-provenance-gaps.md) have landed and
`audits/deduction-candidate/execution-manifest.md` exists with these values
copied verbatim. No pilot, no smoke run and no retry is authorized, including on
flat-rate service: a free call is still a call. No adoption — a result from this
evaluation is not an adopting record. No new provider, model, dependency, map or
role, and existing baseline-only training campaigns stay unchanged. An exhausted
budget or an exceeded deadline stops the run and reports partial state; neither
authorizes a retry.

## Expected scope

`audits/deduction-candidate/run-<date>/` (new), the candidate's `README.md`
index and one dated line in its `checkpoint.md`, `docs/artifacts.md` (the
`audits/` row), `tasks/README.md`'s derived inventory sentence, this card. No
instrument, generator, manifest or frozen-analysis byte moves. Delivered on
`work/fresh-deduction-run-3` and one pull request into `main`.

## Record impact

Adds a measurement record under `audits/`; adopts nothing; no recording,
report, DTO or weight byte moves; every candidate stays default-OFF. If the
result later informs a fix, the third band's freeze record is marked
development the same way the first two were.

## Validation

`uv run pytest tests/experiments -q` (fake provider only) before the run, the
single authorized live invocation the manifest documents, then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.

## Results

**The one authorized run was made and it stopped on an authorized limit.** It
reached 22 provider attempts of about 600 and unit 4 of 100, and stopped there
on the per-unit output token budget: `BudgetExceededError: LLM budget exceeded
on output_tokens: current=3116.0 + delta=1024.0 > cap=4000.0`, raised by the
budget's pre-flight before the second ballot of `combined_accounts` seed 6001.
That is the first clause of `STOP_RULE`. No retry, no re-run and no widening
followed, and none is authorized by it. Three units completed and one seed
carried both arms, so the primary outcome was never graded and the decision rule
is not evaluable: `combined_accounts` neither advanced nor was rejected.

The record is [the run directory](../../audits/deduction-candidate/run-2026-09-13-3/RESULTS.md),
which carries every figure below with the command that reproduces it.

### Architecture and design references

No instrument, generator, manifest or frozen-analysis byte moved; this branch
adds an `audits/` record and closes this card, which is what Expected scope
allows. The design is [the execution manifest](../../audits/deduction-candidate/execution-manifest.md)
as it stood at `c461c9d0`: the third held-out band 6000-6999 bound by the
stacking round of [the transport-resilience card](fresh-deduction-instrument-transport-resilience.md),
the retry bound that card added, the widened wall window this card authorized,
and the reconciliation [its own card](fresh-deduction-instrument-reconciliation.md)
repaired. The run was driven by `experiments/fresh_deduction_instrument.py` at
sha256 `22373f6037d09169d2fe15b4910b446804afb2d9959eb0c6e9d0145848141e85`.

### Decisions

- **The stop was left to stand.** The manifest's stop rule is the run's stop
  rule; a process that hit it was not restarted, re-run or given a wider ceiling.
  Raising a number the owner authorized is not the runner's call, and the
  record says what was reached rather than proposing a new figure.
- **Two seeds are archived, forty-eight are not.** Seeds 6000 and 6001 were
  rendered to the model and are development data now, so they are archived —
  the four replays carry the prompts and the scripted steps, and
  `rendered-prefixes.json` carries the two prefixes themselves. The other 48
  accepted prefixes were regenerated in process, checked against the frozen
  digests and discarded unrendered; they stay held out and are deliberately
  absent, which is the decision the first two runners made for the same reason.
- **The band's `status` was not flipped.** The freeze record still reads
  `held_out`. Converting it belongs to the decision that acts on this record,
  not to the runner, and the manifest's Roles section says so.
- **The primary outcome is reported as ungraded, with one mechanical
  consequence stated separately.** No `grade_*` function ran, so no graded field
  exists. That all three completed meetings resolved `SKIPPED` with no ejection
  means each would have scored 0 under `PRIMARY_OUTCOME_RUBRIC`'s own wording —
  recorded as a consequence of the rubric applied to the recorded verdicts, not
  as a grader result.
- **The defaults on the stopped unit were classified with the module's own two
  regexes.** `count_defaulted_attempts` runs only when a meeting resolves, and
  this one aborted, so the archive's classification was recomputed from the
  recorded row against `_DEFAULTED_VOTE_MESSAGE` / `_DEFAULTED_TURN_MESSAGE`
  rather than invented. It matches the turn pattern with trigger `validation`.

### What the run measured

Not deduction. Two things it does establish, both about the authorized budget:

| Arm | Attempts | Resolved | Charged-and-refused | Input | Output | `cost_usd` |
| --- | --- | --- | --- | --- | --- | --- |
| `repaired_clock` | 12 | 12 | 0 | 44,664 | 3,028 | 0.0 |
| `combined_accounts` | 10 | 9 | 1 | 38,240 | 6,172 | 0.0 |
| Run | 22 | 21 | 1 | 82,904 (3.45% of 2,400,000) | 9,200 (4.60% of 200,000) | 0.0 |

1. **The per-unit output ceiling of 4,000 is the binding constraint, and it
   binds on the candidate arm.** Its one completed unit charged 3,056 (76.4%)
   and cleared its last ballot pre-flight by 28 tokens; the reference arm's two
   units charged 1,601 and 1,427 (40.0% and 35.7%). On the stopped unit one
   schema-invalid turn — the fail-soft class the manifest accepts at about 1 in
   50 calls — was billed for another 1,455 output tokens, and the next ballot's
   mandatory 1,024 reservation crossed the cap.
2. **The run-level output ceiling of 200,000 would have bound too.** About 4,570
   output tokens per paired seed on this sample gives roughly 43 of the 50
   seeds. The authorization projected 220 output per call; measured, the
   reference arm ran at 252 and the candidate at 617.

Everything else had large margins: 369.1 s elapsed of 28,800 (1.28%), 368.8 s of
model work of 21,600 (1.71%), 16.8 s per attempt, and 54.0% of the per-unit
input ceiling at its largest.

Two repairs were exercised live for the first time and both held.
[PR #447](fresh-deduction-instrument-reconciliation.md)'s post-unit
reconciliation ran on all three completed units and passed, and its client-side
capture of a billed-and-refused call fired — the 4,541 / 1,455 attempt is in the
arm's partial accounting, which the 2026-09-10 defect would have lost entirely.
Its `_charged_failed_attempts` branch is still unproved live, because the only
unit carrying one is the unit that aborted.
[PR #450](fresh-deduction-instrument-transport-resilience.md)'s retry bound was
in force and never engaged: 22 attempts produced 22 completions, and
`retried_calls`, `unaccounted_attempts` and `attempts_by_trigger` are empty on
both arms.

### Verification

Pre-flight, before any wall time was committed:

```sh
.venv/bin/pytest tests/experiments -q
.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run --units 2 --output-dir <temp dir>
```

290 passed; the fake-provider mechanics check returned `total_cost_usd` 0.0 on
two units and its output was not committed. The offline gate then ran
`assert_manifest_binds_the_live_band` and `assert_ready_for_a_live_run`, which
returned the verified set — 50 accepted prefixes, 9 skips, freeze record sha256
`7ded19906a7026ae3724894af67cf3667d35f4230d532bf825e495d4666ecd37`, accepted
seeds 6000-6058 — with no client constructed. The authorized constants were read
off the module and compared with this card's Constraints table before the run;
every value agreed.

The live run was the invocation the manifest documents, made once, with the
credential delivered through `uv run --env-file` from a 0600 file outside the
repository that was deleted afterwards. The archive was scanned for the key's
first six characters with a count-only comparison before anything was committed:
7 files scanned, 0 occurrences.

The card's Validation order, on the tree this branch delivers:

```sh
.venv/bin/python scripts/validate_task_docs.py
.venv/bin/python scripts/check_doc_facts.py
.venv/bin/python scripts/verify_ml_evidence.py
.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q
.venv/bin/pytest tests/experiments -q
bash scripts/check.sh
```

The counts are in the pull request. `--complete` was not run on
`verify_ml_evidence.py`; its ABSENT rows are the evidence-branch bytes a fresh
checkout does not carry.

The `docs/artifacts.md` `audits/` row was recomputed with everything staged:

```sh
git ls-files audits | wc -l
git ls-files -z audits | xargs -0 wc -c | tail -1
```

### Outcome

In the preregistration's own vocabulary the run reaches **none** of the four
possible decisions, because none of them is a statement a one-paired-unit sample
supports. The only route it identifies is more evidence under a new authorized
manifest, which is an owner decision on a new card with its own limits — and
"more evidence is not an automatic spending authorization". A result is a
measurement and never an adoption; this one changes no default, no experiment
switch and no baseline. The full account, with every stop condition checked and
every figure reproducible, is in
[RESULTS.md](../../audits/deduction-candidate/run-2026-09-13-3/RESULTS.md).

### Limitations

- **The evaluation was not measured.** One paired unit of fifty, nothing graded,
  the decision rule not evaluable. Nothing here says anything about whether
  `combined_accounts` improves deduction.
- **Three units are not a rate.** Both budget findings above are arithmetic on
  three completed units and one stopped one. They are the right order of
  magnitude to price a fourth authorization against, not measurements of the
  arms' token distributions.
- **Two more held-out seeds are spent.** Seeds 6000 and 6001 are development
  data now, so a confirmation claim on this band is no longer available and a
  fourth run needs a fourth band. Four seeds are gone across three runs.
- **The reconciliation's charged-failed-attempt branch is still unproved
  live**, for the reason above: the only unit that carried one aborted before
  the reconciliation could run.
- **A retried attempt's usage stays invisible**, as the transport-resilience
  card's own limitation records. It did not matter here — no attempt was
  retried — but the gap is unchanged.
- **This card authorized one run and it is spent.** Nothing in this record
  authorizes another, and the stop authorized no retry.
