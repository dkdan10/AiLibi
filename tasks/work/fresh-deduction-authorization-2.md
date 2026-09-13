# Second run of the fresh-model deduction evaluation

**Status:** active

## Outcome

The fresh-model deduction instrument runs once more, on the second held-out
band, under the limits the owner authorized for the first run, with the
reconciliation defect that stopped the first attempt repaired. The run's actual
tokens, wall and cost are recorded against every limit, the paired result is
evaluated under the frozen decision rule, and the outcome is written down as a
measurement that adopts nothing.

## Evidence

The first run (PR #445, closed unmerged; branch `work/fresh-deduction-run`
kept as its archive) stopped after one of one hundred units on the instrument's
spend reconciliation, spending 36,003 input and 3,401 output tokens at $0.00
marginal; seed 3000 of the first band was rendered and that band is development
data since 2026-09-10. The execution manifest's own rule says more evidence is
not an automatic spending authorization, so a second run needed a new owner
decision. That decision is recorded here: on 2026-09-13, in the coordinator's
session, after the merges of [the second freeze](held-out-prefix-freeze-2.md)
(#446, `ca6e97d6`) and [the reconciliation fix](fresh-deduction-instrument-reconciliation.md)
(#447, `7353ff88`), the owner instructed "Dispatch it" in reply to the
coordinator's statement that the remaining step was a new authorization card
with the same limits followed by a runner session. This card is that
authorization's record, committed directly to `main` as a contract document
under the delivery policy; the limits below are the first card's, unchanged.

The instrument is `experiments/fresh_deduction_instrument.py` at `7353ff88` or
later; the execution manifest `audits/deduction-candidate/execution-manifest.md`
binds the second band (5000-5999, accepted seeds 5000-5052, 3 skips) and carries
the dated amendments after the stopped run; the live gate refuses a manifest
whose band is not the frozen record's, a live client under the offline label,
and any invocation without the runner flag and the manifest's own path.

## Acceptance

- [ ] The execution manifest's authorization fields carry exactly the values in
  Constraints, and the instrument enforces them: the per-unit `GameBudget` with
  a run-level parent, the `RunDeadline`, the per-call caps, sequential order.
- [ ] The runner regenerates the frozen set from the band in the manifest and
  the instrument verifies every digest and the skip list before any client is
  constructed; the runner opens no prefix before the run.
- [ ] The run records actual tokens, elapsed wall, model-work time and the
  $0.00 marginal cost against these limits, per arm and for the run; an
  exhausted budget or deadline stops the run and authorizes no retry.
- [ ] The paired result is evaluated under the frozen decision rule (exact
  McNemar p over the discordant pairs, the net difference bar, the
  wrongful-ejection bound) and written down in the preregistration's own
  vocabulary as a measurement; every stop condition is checked and reported.
- [ ] The results, the per-unit records, the usage reconciliation and the
  archived prefixes (development data once archived) land under
  `audits/deduction-candidate/run-2026-09-13/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row recomputed.

## Constraints

Authorized limits, identical to those the owner authorized by merging #437 on
2026-09-07 (merge commit `0f49d8e6`), and re-authorized for a second run by the
owner's instruction on 2026-09-13 (see Evidence):

| Field | Value |
| --- | --- |
| Provider | `featherless` |
| Model | `Qwen/Qwen3.6-27B` (locked 2026-07-12, Task 16.2). Non-thinking with `enable_thinking=false` pinned on every call, `response_format_mode = json_object`, prompt set `qwen3_6_27b` — all carried from the model lock, not re-decided here |
| Per-call token cap | turn 2,048 output / vote 1,024, the shipped defaults unchanged. The committed lab rows for this model-and-prompt-set pair ran at `max_tokens=4096` and never exceeded 195 output tokens, so a truncation is a real signal rather than a cap artifact |
| Total token budget | 2,400,000 input / 200,000 output run-level, and 45,000 input / 4,000 output per unit. Hard stop. Projection for option A: 600 calls; input `repaired_clock` 3,636/call x 300 + `combined_accounts` 2,441/call x 300 = 1,823,100; output 600 x 220 = 132,000 |
| Wall-clock deadline | 4 h of model work within a 6 h elapsed deadline. The work window comes from the measured 12-23 s/call band; the 2 h margin covers one recorded 3h21m provider-side HTTP 529 stall (`audits/audit-phase-21-adopting-record.md:373-380`) |
| Dollar limit | $0.00 marginal, recorded as bookkeeping and not as an enforcement mechanism. The provider's zero pre-flight rate disables the USD dimension, so only the token budget and the deadline can stop a run |
| Cost statement | The paragraph quoted below, verbatim |
| Roster | 4p1i with 3 living voters at meeting open. A change of roster invalidates the token budget above and requires a new authorization |
| Execution mode | sequential |
| Held-out preparer | The second freeze's preparer session (PR #446, merged as `ca6e97d6`; band 5000-5999). Runner: a fresh session dispatched by the coordinator on this card on 2026-09-13, after the merges of #446 and #447; it opens no prefix before the run and regenerates the set from the frozen band, verifying every digest. The coordinator dispatches and runs nothing |
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

`audits/deduction-candidate/run-2026-09-13/` (new), the candidate's
`README.md` index and one dated line in its `checkpoint.md`, `docs/artifacts.md`
(the `audits/` row), `tasks/README.md`'s derived inventory sentence, this card.
No instrument, generator, manifest or frozen-analysis byte moves. Delivered on
`work/fresh-deduction-run-2` and one pull request into `main`.

## Record impact

Adds a measurement record under `audits/`; adopts nothing; no recording,
report, DTO or weight byte moves; every candidate stays default-OFF. If the
result later informs a fix, the second band's freeze record is marked
development the same way the first was.

## Validation

`uv run pytest tests/experiments -q` (fake provider only) before the run, the
single authorized live invocation the manifest documents, then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.
