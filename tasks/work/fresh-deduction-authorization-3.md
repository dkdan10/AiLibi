# Third run of the fresh-model deduction evaluation

**Status:** active

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

- [ ] The execution manifest's authorization fields carry exactly the values in
  Constraints, and the instrument enforces them: the per-unit `GameBudget` with
  a run-level parent, the `RunDeadline` at 8 h elapsed, the 6 h model-work
  window, the per-call caps, sequential order, the transport retry bound.
- [ ] The runner regenerates the frozen set from the band in the manifest and
  the instrument verifies every digest and the skip list before any client is
  constructed; the runner opens no prefix before the run.
- [ ] The run records actual tokens, elapsed wall, model-work time, retried and
  unaccounted attempts, and the $0.00 marginal cost against these limits, per
  arm and for the run; an exhausted budget or deadline stops the run and
  authorizes no retry beyond the stated per-call bound.
- [ ] The paired result is evaluated under the frozen decision rule (exact
  McNemar p over the discordant pairs, the net difference bar, the
  wrongful-ejection bound) and written down in the preregistration's own
  vocabulary as a measurement; every stop condition is checked and reported.
- [ ] The results, the per-unit records, the usage reconciliation and the
  rendered prefixes (development data once archived) land under
  `audits/deduction-candidate/run-<date>/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row recomputed.

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
