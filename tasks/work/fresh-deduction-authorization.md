# Authorize the fresh-model deduction evaluation

**Status:** done

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

- [x] The execution manifest's authorization fields carry exactly the values in
  Constraints, copied verbatim, and the cost statement appears verbatim.
  `audits/deduction-candidate/execution-manifest.md` §"Sampling configuration,
  caps and limits" copies the table and §"Cost statement" the paragraph;
  `tests/experiments/test_fresh_deduction_instrument.py` asserts the manifest
  quotes each `AUTHORIZED_*` constant. The runner reconciled them once more
  before spending anything — see Results, "Authorized values, reconciled before
  the run".
- [x] The instrument enforces a per-unit `GameBudget` with a run-level parent
  and one `RunDeadline` measured against elapsed wall, constructed by the
  instrument itself rather than by the tournament CLI's `--max-total-*` caps,
  which are mutually exclusive with `--attest-unknown-usage`. A planted overrun
  stops the run and reports the partial state, and the recorded spend is
  reconciled against the budget snapshot afterwards.
  `run_instrument` builds both itself
  (`experiments/fresh_deduction_instrument.py:2681-2690`) and the planted
  overruns are in the instrument's tests. This run exercised the reconciliation
  for real: it fired on unit 2 and stopped the run with its partial state, which
  is the behaviour this box claims. It also fired on a class the manifest's
  amended `STOP_RULE` exempts — recorded in Results and in
  [RESULTS.md](../../audits/deduction-candidate/run-2026-09-10/RESULTS.md).
- [x] One per-unit cap sized on the larger arm (`repaired_clock`) is applied
  identically to both arms, and per-arm usage is recorded separately so the
  asymmetry stays visible. A truncation in either arm is a stop, not a datum.
  One `unit_budget` per unit from the same `AUTHORIZED_LIMITS`, with
  `BUDGET_SIZING_ARM` naming the arm it is sized on. The run recorded 20,512
  input tokens on `repaired_clock` against 15,491 on `combined_accounts` for the
  same seed, so the asymmetry is visible in the archived rows. No response
  reached its cap (largest output 861 against 2,048), so the truncation stop did
  not fire.
- [x] The held-out prefix generator is bound to the same temporal version as the
  arms (temporal v2), and a mechanical assertion shows that no rendered prompt
  and no frozen prefix matches `body-p-\d+-\d+`.
  `assert_no_legacy_body_handles` ran over all 50 regenerated prefixes inside
  `verify_frozen_set`, before any client existed, and over unit 1's rendered
  prompts; neither matched. `_assert_arm_provenance` confirmed temporal version
  2 on both units.
- [x] The held-out prefixes are prepared, frozen and hashed by the named
  preparer, and the runner never opens them.
  Prepared and frozen by the preparer session on
  [the freeze card](held-out-prefix-freeze.md), merged as `23a23c2d` (#438).
  This runner opened, printed and reasoned about no prefix before the run: the
  set was consumed only as `HeldOutPrefix` objects driving the engine, and
  `verify_frozen_set` matched all 50 digests and the 8 skips against the frozen
  manifest. Only seed 3000 was ever rendered to the model; the archive reveals
  that one and seeds 3001-3057 remain unrendered.
- [x] The run records actual tokens, elapsed wall and the $0.00 marginal cost
  against these limits. An exhausted budget or deadline stops the run and
  authorizes no retry.
  Actual: 12 paid calls, 36,003 input and 3,401 output tokens, 159.7 s elapsed
  and 140.2 s of model work, `cost_usd` 0.0 throughout — against 2,400,000 /
  200,000 tokens, 6 h elapsed and 4 h of model work. No limit came close and
  none fired; the run stopped on the spend reconciliation instead, and no retry
  was made. The full table is in
  [RESULTS.md](../../audits/deduction-candidate/run-2026-09-10/RESULTS.md).

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

## Results

Delivered on `work/fresh-deduction-run`, from `origin/main` at `5281e297`. The
branch name deviates from this card's slug because
`work/fresh-deduction-authorization` already exists from the merged #437, and a
second branch on that name would collide with published history.

The limits this card authorized were exercised by the one authorized live run,
executed once on 2026-09-10 by a runner session separate from the preparer
(#438) and from the instrument builder (#443). **The run stopped after 1 of 100
units.** No paired unit completed, the primary outcome was not measured and the
decision rule is not evaluable. The full record is
[RESULTS.md](../../audits/deduction-candidate/run-2026-09-10/RESULTS.md); this
section states what the card itself is accountable for.

### Architecture and design references

`audits/deduction-candidate/execution-manifest.md` is the binding document: its
"Sampling configuration, caps and limits" table carries this card's Constraints
verbatim, its "How each limit is enforced" section names the mechanism behind
each, and its `STOP_RULE` and "Meeting-internal defaults: counted, not stopped"
sections are the two clauses this run found to disagree.
`audits/deduction-candidate/preregistration.md:105-122` is the field list the
manifest answers and the source of the "no live call is authorized by a draft"
rule. `docs/workflow.md` §"Records and experiments" supplies the standard this
result is written to: record negative results and stop rules with the same care
as apparent improvements.

### Authorized values, reconciled before the run

Every authorized value was compared against what the instrument enforces before
any client was constructed:

```sh
.venv/bin/python -c "
import experiments.fresh_deduction_instrument as I
print(I.AUTHORIZED_PROVIDER, I.AUTHORIZED_MODEL, I.AUTHORIZED_PROMPT_SET, I.AUTHORIZED_EXECUTION_MODE)
print(I.AUTHORIZED_ROSTER_PLAYERS, I.AUTHORIZED_ROSTER_IMPOSTORS, I.AUTHORIZED_LIVING_VOTERS)
print(I.AUTHORIZED_LIMITS.model_dump())
print(I.AUTHORIZED_SAMPLING.model_dump())
"
```

```
featherless Qwen/Qwen3.6-27B qwen3_6_27b sequential
4 1 3
{'run_max_input_tokens': 2400000, 'run_max_output_tokens': 200000, 'unit_max_input_tokens': 45000, 'unit_max_output_tokens': 4000, 'max_cost_usd': 0.0, 'elapsed_seconds': 21600.0, 'model_work_seconds': 14400.0}
{'turn_max_tokens': 2048, 'turn_temperature': 0.4, 'vote_max_tokens': 1024, 'vote_temperature': 0.2}
```

Each line equals this card's Constraints table: `featherless`,
`Qwen/Qwen3.6-27B`, 2,048 turn / 1,024 vote, 2,400,000 / 200,000 run-level and
45,000 / 4,000 per unit, 4 h of model work inside 6 h elapsed, $0.00, 4p1i with
3 living voters, sequential. Nothing disagreed, so the run proceeded.

### Decisions

**The run was made once and not retried.** It stopped on a manifest stop
condition, and a stop authorizes no retry and no widening of any limit. The
diagnosis below is offline and cost $0.00; re-running is a new spending decision
for the owner on a new card, and this runner did not make it.

**The credential was supplied without a wrapper around the instrument.** The key
lives in the untracked repo-root `.env` and the instrument carries exactly one
value over from the ambient environment
(`authorized_client_environment`). The documented command was run under
`uv run --env-file <credential-only file>`, which loads that one variable into
the process environment and execs the command unchanged. The file held only the
`FEATHERLESS_API_KEY` line, lived outside the repository, and no ambient
`AILIBI_*` variable reached the run — the instrument pins provider, model and
prompt set itself. The key was never printed, logged, placed on a command line
or committed; the archive was scanned for it and holds 0 occurrences.

**The archive publishes seed 3000 and nothing else from the frozen set.** That
prefix was rendered to the model, so it is no longer held out, and the manifest
says the prefixes are archived with the results once that is true. Seeds
3001-3057 were regenerated in process, digest-checked and discarded unrendered.

**The freeze manifest's `status` was not converted.** It still reads
`held_out`. The manifest's Roles section makes that conversion the consequence
of a fix informed by a held-out result; the fix does not exist yet and recording
it is not the runner's job.

### Verification

Pre-flight, before any spend:

```sh
.venv/bin/pytest tests/experiments/test_fresh_deduction_instrument.py \
  tests/experiments/test_held_out_prefixes.py -q
```

```
180 passed in 20.73s
```

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run --units 2 \
  --output-dir <temp dir>
```

Green on the fake provider at $0, `b=0, c=0, p=1.0` by construction as the
manifest says a dry run must be.

The live gate and the frozen-set check were run offline first, which constructs
no client and reaches no provider:

```sh
.venv/bin/python -c "
import experiments.fresh_deduction_instrument as I
from pathlib import Path
inv = I.LiveRunInvocation.naming(Path('audits/deduction-candidate/execution-manifest.md'),
                                 provider='featherless', model=I.AUTHORIZED_MODEL)
frozen = I.assert_ready_for_a_live_run(provider='featherless', invocation=inv, units=None)
print(len(frozen.prefixes), len(frozen.skipped_seeds), frozen.manifest_sha256)
"
```

```
50 8 b6a3bdc5b216e1b7b3d6c1eb46e5f416bb23fba77a8087ef025c31819bff1367
```

The run itself, and its result, are in
[RESULTS.md](../../audits/deduction-candidate/run-2026-09-10/RESULTS.md), whose
every figure is reproducible from the archived replays by the commands quoted
there.

### Outcome summary

| | |
| --- | --- |
| Units completed | 1 of 100 |
| Paired units | 0 of 50 |
| Primary outcome | not measured |
| Decision rule | not evaluable; the candidate neither advances nor is rejected |
| Wrongful ejections | 0 on each arm — neither meeting ejected anyone |
| Spend | 12 paid calls, 36,003 in / 3,401 out, 159.7 s elapsed, 140.2 s model work, $0.00 |
| Stop | the post-unit spend reconciliation, on unit 2 |

The stop's cause is a paid provider call whose payload failed `MeetingTurn`
schema validation. Its tokens are charged to the budget and recorded on a
`failed_call` row, but never on `MeetingReplayEntry.llm_calls`, which is what
`_reconcile_recorded_spend` compares the budget against — so the two differ by
exactly that call (2,228 in / 861 out) and the run stops. The manifest's amended
`STOP_RULE` explicitly exempts this class ("a schema-validation default is NOT
[a stop]") and does not list the reconciliation among its stop conditions, while
its enforcement section says a reconciliation difference is a stop. The two
clauses disagree and the code follows the enforcement one.

### Limitations

- **This card's Acceptance is about the limits, and the limits held.** None of
  them was approached, let alone exhausted. That is not evidence the design is
  sound; it is evidence the run ended too early to test it.
- **Nothing here measures the candidate.** One unit per arm, both resolving
  `SKIPPED`, is not a sample. No grader ran.
- **The 11.7 s per call this run measured is the only projection figure it
  earned**, and it is drawn from 12 calls.
- **The instrument's partial accounting understates spend for the failing
  class**, by exactly the paid call it could not see, so a stop of this kind
  reports less than was actually spent. On this run the gap is 2,228 input and
  861 output tokens.
- **A fix is not in this card's scope and is not attempted here.** It changes
  `experiments/fresh_deduction_instrument.py`, which this card's Expected scope
  excludes, and it is informed by a held-out result, which the manifest says
  marks the set development and requires a new band under a new card.
