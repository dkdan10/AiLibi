# Fourth run of the fresh-model deduction evaluation

**Status:** done

## Outcome

The fresh-model deduction instrument runs once more, on the fourth held-out
band, under token ceilings and a turn cap sized from a live calibration on
development inputs rather than from a projection, with the resumption clause
in force. The run's actual tokens, attempts, wall and cost are recorded
against every limit, the paired result is evaluated under the frozen decision
rule, and the outcome is written down as a measurement that adopts nothing.

## Evidence

On 2026-09-14 the owner approved the three decisions of
[the diagnosis](../diagnosis-2026-09-13-live-run-stops.md) and instructed
their execution in order: the bounded live calibration on development inputs
(done: PR #455, merge `1b7af45d`, `audits/deduction-candidate/calibration-2026-09-14/`),
the resumption clause (in the execution manifest since #454, `6f28d6ee`),
and re-sized ceilings for this fourth authorization taken from that
calibration. The calibration ran sixty calls on five paired seeds of the
converted 3000 band at $0.00 marginal with zero refusals on the corrected
account prompts (revision v3) and measured, per unit, a reference mean of
21,026 input / 1,108 output tokens and a candidate mean of 28,430 / 3,137
(largest unit 35,232 / 4,590); its ceiling proposal is the basis of the
Constraints table. One further observation forces the one value the three
decisions did not name: the largest candidate turn charged 2,036 output
tokens against the 2,048 per-call cap, and a truncation is a stop with no
retry, so this card raises the turn cap to 4,096 (the setting the committed lab
rows for this model ran at) and lifts the per-unit output ceiling to clear the
reservation schedule that follows. Bands 3000-3999, 5000-5999 and 6000-6999
are development data (rendered seeds 3000, 5000, and 6000-6001); the run needs
[a fourth band](held-out-prefix-freeze-4.md). The instrument's constants and
the manifest's limits table are moved to these values by
[the limits card](fresh-deduction-limits-4.md), and its feasibility gate
accepts them.

## Acceptance

- [x] The execution manifest's authorization fields carry exactly the values in
  Constraints, the instrument's constants equal them, and the feasibility gate
  accepts them (the reservation schedule under the raised turn cap is 15,360
  against a 16,000 per-unit output ceiling).
- [x] The runner regenerates the frozen set from the band in the manifest and
  the instrument verifies every digest and the skip list before any client is
  constructed; the runner opens no prefix before the run.
- [x] The run records actual tokens, attempts (including retried and
  unaccounted ones), elapsed wall, model-work time and the $0.00 marginal cost
  against these limits, per arm and for the run; an exhausted budget or
  deadline stops the run; an environmental stop may be resumed once per stop
  under the manifest's resumption clause with the interrupted unit's spend
  carried, and every resumption is reported.
- [x] The paired result is evaluated under the frozen decision rule (exact
  McNemar p over the discordant pairs, the net difference bar, the
  wrongful-ejection bound) and written down in the preregistration's own
  vocabulary as a measurement; every stop condition is checked and reported.
- [x] The results, the per-unit records, the usage reconciliation and the
  rendered prefixes (development data once archived) land under
  `audits/deduction-candidate/run-<date>/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row recomputed.

## Constraints

Authorized limits for the fourth run: the cost, roster and execution values the
owner authorized by merging #437 on 2026-09-07 (merge commit `0f49d8e6`), the
wall window of 2026-09-13, and the token ceilings and turn cap re-sized on
2026-09-14 from the live development calibration under the owner's approval
of that day (see Evidence):

| Field | Value |
| --- | --- |
| Provider | `featherless` |
| Model | `Qwen/Qwen3.6-27B` (locked 2026-07-12, Task 16.2). Non-thinking with `enable_thinking=false` pinned on every call, `response_format_mode = json_object`, prompt set `qwen3_6_27b` — all carried from the model lock, not re-decided here |
| Per-call token cap | turn 4,096 output / vote 1,024. The turn cap is raised from the shipped 2,048 on 2026-09-14: the calibration's largest candidate-arm turn charged 2,036 output tokens against 2,048 (1 of 15 candidate turns), a truncation is a stop with no retry, and the committed lab rows for this model ran at `max_tokens=4096`; the vote cap is unchanged (largest measured ballot 237) |
| Total token budget | 3,710,000 input / 459,000 output run-level, and 106,000 input / 16,000 output per unit. Hard stop. Basis, from `audits/deduction-candidate/calibration-2026-09-14/calibration.json`: per unit, 3x the largest measured unit (35,232 input; 4,590 output gives 13,770) with the output ceiling lifted to clear the reservation schedule under the raised turn cap (3 x 4,096 + 3 x 1,024 = 15,360), rounded up to 16,000; run-level, the larger of 100 units x the measured mean x 1.5 and 100 units x the largest measured unit on each dimension (input 3,710,000; output 459,000). Both provider pre-flight rates are zero, so these ceilings are a stop rule sized as an anomaly detector at about three times the measured maximum, not a budget |
| Wall-clock deadline | 6 h of model work within an 8 h elapsed deadline, unchanged from the third authorization. The calibration paced 17.2 s per attempt pooled (12.6 reference, 21.9 candidate), so six hundred attempts need about 2.9 h |
| Dollar limit | $0.00 marginal, recorded as bookkeeping and not as an enforcement mechanism. The provider's zero pre-flight rate disables the USD dimension, so only the token budget and the deadline can stop a run |
| Cost statement | The paragraph quoted below, verbatim |
| Roster | 4p1i with 3 living voters at meeting open. A change of roster invalidates the token budget above and requires a new authorization |
| Execution mode | sequential |
| Held-out preparer | The fourth freeze's preparer session (the pull request of [the fourth freeze card](held-out-prefix-freeze-4.md); band 7000-7999). Runner: a fresh session dispatched by the coordinator on this card after that freeze and [the limits card](fresh-deduction-limits-4.md) are merged; it opens no prefix before the run, regenerates the set from the frozen band and verifies every digest; the manifest's resumption clause of 2026-09-14 is in force. The coordinator dispatches and runs nothing |
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
instrument, generator, manifest or frozen-analysis byte moves in the run's own
pull request. Delivered on `work/fresh-deduction-run-4` and one pull request
into `main`.

## Record impact

Adds a measurement record under `audits/`; adopts nothing; no recording,
report, DTO or weight byte moves; every candidate stays default-OFF. If the
result later informs a fix, the fourth band's freeze record is marked
development the same way the first three were.

## Validation

`uv run pytest tests/experiments -q` (fake and replay providers only) before
the run, the single authorized live invocation the manifest documents, then
`uv run python scripts/validate_task_docs.py`, `uv run python
scripts/check_doc_facts.py`, `uv run python scripts/verify_ml_evidence.py`
(offline; never `--complete`), `uv run pytest
tests/scripts/test_verify_ml_evidence.py -q`, and `bash scripts/check.sh`.

## Results

### Closed on main (2026-09-15)

The fourth authorized run was made once on 2026-09-15 (the sitting began late
on 2026-09-14 in the machine's zone) and stopped in unit 26 of 100 on a
per-call truncation: a ballot on `combined_accounts` seed 7016 reached the
1,024-token vote cap. `STOP_RULE` makes a truncation a stop with no retry and
the resumption clause of 2026-09-14 makes that class final, so there was one
sitting, no resume and no re-run. Twelve paired seeds were graded, neither arm
scored the primary outcome on any of them, and the decision rule is stated on
fifty, so its conjunction is not evaluable: `combined_accounts` neither
advances to an adopting review nor is rejected. The run's record, RESULTS.md,
the 26 replays, the final checkpoint, the usage reconciliation, the stop log
and the thirteen rendered prefixes under
`audits/deduction-candidate/run-2026-09-15/`, lives on the closed pull request
#458's branch `work/fresh-deduction-run-4` at `5f2383ea`, which the owner chose
not to merge; the acceptance boxes are checked against that record, not
against a completed measurement, as the first three cards were.
[The diagnosis of 2026-09-15](../diagnosis-2026-09-15-truncation-stop.md)
carries the root cause, the owner's rulings and the four cards that follow.

| Quantity | Value |
| --- | --- |
| Units completed | 25 of 100; 12 of 50 paired seeds graded |
| Primary outcome | 0 of 12 on each arm; `b` = `c` = 0; exact McNemar p 1.0, the empty-sample constant |
| Decision-rule clauses | all three not evaluable |
| Ejections | `repaired_clock` 0; `combined_accounts` 1 (role-correct, unsupported: both naming ballots were nulled for a malformed citation id) |
| Meeting-internal defaults | `combined_accounts` 2 defaulted turns by validation; `repaired_clock` 0 |
| Charged failed attempts | 1, the truncated ballot (4,734 in / 1,024 out) |
| Transport retries, unaccounted attempts, resumptions | 0, 0, none |
| Usage | 156 attempts; 612,588 input (16.5% of 3,710,000) and 58,986 output (12.9% of 459,000); $0.00 |
| Wall | 1,886.3 s elapsed of 28,800; 1,884.6 s of model work of 21,600; 12.1 s per attempt |
| Stop that fired | the per-call vote cap, once |
| Seeds rendered | 13 of the band's 50 (7001, 7003, 7004, 7005, 7006, 7008, 7009, 7010, 7012, 7013, 7014, 7015, 7016); 37 stay held out |

Every re-sized ceiling of this authorization held with wide margins and the
calibration's per-unit means predicted this run's within 5%; the vote cap,
the one number the fourth authorization did not move, is where the run
stopped, on an impostor-authored ballot whose free-text rationale ran away.
The pre-flight, the decisions the runner took, the verification commands and
the full outcome tables are in the card and RESULTS.md on the archive branch
(`git show origin/work/fresh-deduction-run-4:tasks/work/fresh-deduction-authorization-4.md`).
The gates on that branch passed with the real exit code: 7,708 Python tests,
strict mypy over 479 sources, 515 frontend tests. The fourth freeze record's
`status` is untouched here; [the fifth freeze card](held-out-prefix-freeze-5.md)
marks it development.
