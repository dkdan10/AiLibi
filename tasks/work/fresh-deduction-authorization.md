# Authorize the fresh-model deduction evaluation

**Status:** ready

## Outcome

The owner's authorization fields for the fresh-model deduction evaluation exist
as concrete proposed values instead of an outstanding decision: provider, exact
model, per-call token cap, total token budget, wall-clock deadline, dollar
limit, cost statement, and the death-tick body-handle choice, plus the two
fields that bind the budget — roster shape and execution mode.

Merging this card is the authorization of those limits. While it is unmerged
nothing is authorized. Once merged it authorizes limits, not a run: no live
call may be made until the instrument, its frozen held-out prefixes and the
execution manifest of [the instrument card](fresh-deduction-instrument.md)
exist, and until that card's preconditions —
[the renderer repair](evidence-renderer-salience.md) and
[the provenance gaps](recorded-provenance-gaps.md) — have landed.

## Evidence

`tasks/post-merge-plan.md:80` and `:83` record both decisions as outstanding.
`fresh-deduction-instrument.md:64-75` wires a per-call cap and a wall-clock
deadline into the instrument and lands the manifest's owner fields present and
empty; `:82-85` authorizes no live call, pilot, smoke run or retry, including on
flat-rate service; `:96-101` names the two preconditions and leaves the
death-tick handle as a disjunction.
`audits/deduction-candidate/preregistration.md:105-122` states what the manifest
must bind — `:113-115` is the owner-fields bullet (exact provider and model,
sampling configuration, requested token caps, elapsed-time limit, cost limit,
the owner's explicit authorization, and a cost statement that flat-rate access
does not excuse) and `:120-121` states that no live call, "including a pilot or
retry on flat-rate service", is authorized by that draft. `:143-149` requires a
separate reviewer to prepare and freeze the held-out inputs before the candidate
is evaluated on them.

The values below are read from committed sources, not chosen. `llm/provider.py:74`
records Featherless as a flat-rate hosted subscription, $25/mo Premium, owner
decision 2026-06-25. `llm/featherless_client.py:147` holds the served model id
and `:243-244` exposes zero pre-flight rates, which disable the USD dimension in
`llm/budgeted_client.py:118-126` — so a dollar cap cannot stop a call on this
provider. `meetings/manager.py:210-213` holds the shipped per-call caps, 2048
output per turn and 1024 per vote. `llm/budget.py:109-110` gives `GameBudget`
two token dimensions rather than one, so a single "about 2.5 M" figure has to be
split, and `:111` provides the run-level `parent` that makes a per-unit budget
charge upward. `orchestrator/run_limits.py:18` is the single cooperative
`RunDeadline` clock, measured against elapsed wall.
`experiments/tactical_gameplay.py:585-620` is the copy-ready precedent: build
the budget and the deadline, hand both to the runner and the game, then
reconcile the recorded spend against the budget snapshot and raise on any
mismatch. `scripts/paired_stats.py:95` is the exact paired McNemar the design
scores with. `orchestrator/game.py:3352-3363` chooses the rendered body handle
and `observation/body_ids.py:6-11` returns a handle carrying no death tick, so
under temporal v2 both arms already render `body-p-N` by construction.

Two corrections this card carries, because a stale figure in a `ready` card
propagates into the manifest:

Real output tokens are about **1.51x** the committed `len//4` heuristic, not
3.7x. The 3.7x figure compares real output per call against the scripted
capture's per-call output — a different denominator — on which the honest ratio
is 3.05x. Both denominators are legitimate; conflating them over-provisions the
output dimension by roughly 2.5x. Any ratio the manifest quotes must name its
denominator. Real input is about 1.28x the same heuristic.

Per-call latency for this exact model and prompt set **is** recorded.
`experiments/lab/results-featherless-sweep-qwen3-6-27b-ab.jsonl` carries 104
committed non-thinking rows for `Qwen/Qwen3.6-27B` on prompt set `qwen3_6_27b`
at a median of 23.1 s/call, and the 2026-09-03 four-leg recording implies about
12 s/call sequential. The wall deadline below is therefore set on a measured
12-23 s band rather than on a pilot, and no pilot is needed to set it.

The reasoning of record for every value here is item B of
[the 2026-09-07 owner decision memo](../owner-decisions-2026-09-07.md), which
carries the anchors, the arithmetic and the rejected options in full.

## Acceptance

- [ ] The execution manifest's authorization fields carry exactly the values in
  Constraints, copied verbatim, and the cost statement appears verbatim.
- [ ] The instrument enforces a per-unit `GameBudget` with a run-level parent
  and one `RunDeadline` measured against elapsed wall, constructed by the
  instrument itself rather than by the tournament CLI's `--max-total-*` caps,
  which are mutually exclusive with `--attest-unknown-usage`. A planted overrun
  stops the run and reports the partial state, and the recorded spend is
  reconciled against the budget snapshot afterwards.
- [ ] One per-unit cap sized on the larger arm (`repaired_clock`) is applied
  identically to both arms, and per-arm usage is recorded separately so the
  asymmetry stays visible. A truncation in either arm is a stop, not a datum.
- [ ] The held-out prefix generator is bound to the same temporal version as the
  arms (temporal v2), and a mechanical assertion shows that no rendered prompt
  and no frozen prefix matches `body-p-\d+-\d+`.
- [ ] The held-out prefixes are prepared, frozen and hashed by the named
  preparer, and the runner never opens them.
- [ ] The run records actual tokens, elapsed wall and the $0.00 marginal cost
  against these limits. An exhausted budget or deadline stops the run and
  authorizes no retry.

## Constraints

Authorized limits, effective since the owner merged this card as #437 on
2026-09-07 (merge commit `0f49d8e6`):

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
| Held-out preparer | Ruled 2026-09-07 (mechanical generation from a preregistered band; two separate sessions). The preparer is a fresh session dispatched on [the freeze card](held-out-prefix-freeze.md): it builds a deterministic generator, draws from the band preregistered there, commits the hashes and opens the pull request whose owner merge is the freeze. The runner is a separate session started after that merge, dispatched on [the instrument card](fresh-deduction-instrument.md): it regenerates the set from the frozen band, verifies the committed hashes and opens no prefix before the run. The coordinator dispatches both and runs neither. Inspecting a held-out input converts it to development data; a held-out result that informs a fix marks the set development, and a new band is frozen under a new card |
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

This card, and the authorization fields of
`audits/deduction-candidate/execution-manifest.md` once
[the instrument card](fresh-deduction-instrument.md) creates that file. No
source file changes here.

## Record impact

No recording, report, DTO, metric or weight byte moves. No experiment becomes ON
and no adopting record is created; the evaluation these limits bound produces a
measurement whose adoption stays a separate decision.

## Validation

`uv run python scripts/validate_task_docs.py` and `bash scripts/check.sh` for this
card as a document. The authorized limits are exercised, not validated, by
[the instrument card](fresh-deduction-instrument.md)'s own validation; do not
run the prospective live evaluation as a check.
