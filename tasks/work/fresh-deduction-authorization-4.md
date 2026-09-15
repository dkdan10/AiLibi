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
  against a 16,000 per-unit output ceiling). Checked offline before any spend:
  `assert_limits_are_feasible(limits=AUTHORIZED_LIMITS)` returned,
  `unit_output_reservation()` is 15,360, and the constants the run enforced read
  provider `featherless`, model `Qwen/Qwen3.6-27B`, caps 4,096 / 1,024, run
  3,710,000 / 459,000, per unit 106,000 / 16,000, 21,600 s of model work inside
  28,800 s, sequential, 4 transport attempts at 180 s. See Results, "Before any
  spend".
- [x] The runner regenerates the frozen set from the band in the manifest and
  the instrument verifies every digest and the skip list before any client is
  constructed; the runner opens no prefix before the run.
  `assert_manifest_binds_the_live_band()` passed on band 7000-7999 and
  `assert_ready_for_a_live_run` returned the verified set — 50 accepted
  prefixes, seeds 7001-7057, 8 skips (7000, 7002, 7007, 7011, 7017, 7018, 7047,
  7048), freeze record sha256 `5fe4b1e3…58ed8b` — before a credential was read.
  The runner opened, printed and reasoned about no prefix before the run; the
  thirteen it rendered were written out afterwards, as development data.
- [x] The run records actual tokens, attempts (including retried and
  unaccounted ones), elapsed wall, model-work time and the $0.00 marginal cost
  against these limits, per arm and for the run; an exhausted budget or
  deadline stops the run; an environmental stop may be resumed once per stop
  under the manifest's resumption clause with the interrupted unit's spend
  carried, and every resumption is reported. Recorded per arm and for the run in
  [the results](../../audits/deduction-candidate/run-2026-09-15/RESULTS.md) and
  in its [usage reconciliation](../../audits/deduction-candidate/run-2026-09-15/usage-reconciliation.json):
  156 attempts, 155 completions, 1 charged-and-refused, 612,588 input, 58,986
  output, $0.00, 1,886.3 s elapsed and 1,884.6 s of model work, with 0 retried
  calls and 0 unaccounted attempts on both arms. No budget and no deadline was
  exhausted — the stop was a per-call truncation, which the resumption clause
  makes final — so there was no resumption to report, and the run had exactly
  one sitting.
- [x] The paired result is evaluated under the frozen decision rule (exact
  McNemar p over the discordant pairs, the net difference bar, the
  wrongful-ejection bound) and written down in the preregistration's own
  vocabulary as a measurement; every stop condition is checked and reported.
  `b = 0`, `c = 0`, net 0 on the 12 paired seeds that graded, exact McNemar p
  1.0 (the empty-sample constant), 0 wrongful ejections on both arms; all three
  clauses are NOT EVALUABLE on 12 of the 50 paired units the rule is stated on,
  so the candidate neither advances nor is rejected. Every `STOP_RULE` condition
  is tabulated in the results with the evidence for it, and the one that fired
  is named.
- [x] The results, the per-unit records, the usage reconciliation and the
  rendered prefixes (development data once archived) land under
  `audits/deduction-candidate/run-<date>/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row recomputed.
  `audits/deduction-candidate/run-2026-09-15/` holds the results, 26 per-unit
  replays, the final checkpoint, the usage reconciliation and its derivation,
  the stop log and the 13 rendered prefixes and their derivation — about 2.8 MB,
  nothing left out. The candidate's `README.md` indexes it, `checkpoint.md`
  carries one dated line, and the `docs/artifacts.md` `audits/` row is
  recomputed with everything staged.

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

**The run was made, once, and it stopped.** It completed 25 of its 100 units and
stopped in unit 26 on a per-call truncation — a ballot response that reached its
1,024-token output cap on `combined_accounts` seed 7016. `STOP_RULE` makes a
truncation a stop with no retry ("a truncation is a stop, not a datum"), and the
manifest's resumption clause of 2026-09-14 makes that class of stop FINAL, so
this run had one sitting, no resume and no re-run. Twelve paired seeds graded,
neither arm scored the primary outcome on any of them, and the decision rule is
stated on fifty paired units, so its conjunction is not evaluable: the candidate
neither advances to an adopting review nor is rejected. The record is
[audits/deduction-candidate/run-2026-09-15/RESULTS.md](../../audits/deduction-candidate/run-2026-09-15/RESULTS.md),
which carries every figure below with the command that reproduces it.

### Architecture and design references

Nothing was designed here. The run executes
[the execution manifest](../../audits/deduction-candidate/execution-manifest.md)
— its Inputs table (band 7000-7999, the fourth freeze), its authorized values as
[the limits card](fresh-deduction-limits-4.md) moved them to this card's
Constraints, its live gate, its grading passes, its frozen decision rule and its
stop rule — through
`experiments/fresh_deduction_instrument.py`, unchanged. No instrument,
generator, manifest or frozen-analysis byte moves in this pull request, which is
what this card's Expected scope requires.

### Before any spend

Every pre-flight was offline and at $0.00:

| Check | Result |
| --- | --- |
| `.venv/bin/pytest tests/experiments -q` | 396 passed |
| `.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run --units 2 --output-dir <outside the repo>` | 100 units' machinery on 2 units, `total_cost_usd` 0.0, uncommitted |
| the replay-double rehearsal under these limits (`-k test_the_rehearsal_is_green_under_the_fourth_authorizations_limits`) | 1 passed, 314 deselected |
| `assert_limits_are_feasible(limits=AUTHORIZED_LIMITS)` | returned; `unit_output_reservation()` 15,360 against a 16,000 ceiling |
| `assert_manifest_binds_the_live_band()` | passed on band 7000-7999 |
| `assert_ready_for_a_live_run(...)` | returned the verified set — 50 prefixes, seeds 7001-7057, 8 skips, freeze sha256 `5fe4b1e3…58ed8b` — before any client |
| the manifest carries `RESUMPTION_CLAUSE` verbatim | true |

and the authorized values the instrument would enforce were read back and
matched this card's Constraints table item for item: provider `featherless`,
model `Qwen/Qwen3.6-27B`, prompt set `qwen3_6_27b`, caps 4,096 / 1,024,
temperatures 0.4 / 0.2, run 3,710,000 / 459,000, per unit 106,000 / 16,000,
21,600 s of model work within 28,800 s elapsed, `$0.00`, sequential, 4p1i with 3
living voters, 100 units, 4 transport attempts at 180 s each.

### Decisions

1. **The stop was treated as final and no resume was attempted.** The clause
   authorizes a resume for transport exhaustion, a credential failure or a
   process crash, and names a truncation among the stops it does not cover. The
   instrument nevertheless wrote its final checkpoint on the stop path, so the
   abandoned pair's 11 calls, 40,208 input, 4,102 output and 112.4 model-work
   seconds are accounted for; they are reported as spend, not carried into a
   sitting that never happened.
2. **The archive is named for the UTC date its own records carry.** The owner
   authorized on 2026-09-14 and the sitting ran `2026-09-15T03:34:25Z` to
   `04:05:52Z`, which is late on 2026-09-14 in the machine's zone. The directory
   is `run-2026-09-15` so that a reader comparing a timestamp against the folder
   never has to reconcile two clocks; the results say both dates in their first
   section.
3. **Thirteen rendered prefixes are archived; thirty-seven are not.** The same
   decision the three earlier runners made, and the manifest's own rule: a
   prefix is archived once it is no longer held out. The thirty-seven that were
   regenerated, digest-checked and discarded unrendered stay held out.
4. **The reconciliation is a committed derivation, not a typed table.**
   `reconcile.py` and `render_rendered_prefixes.py` sit beside the files they
   write, so both can be recomputed rather than trusted. Neither is instrument
   code and neither runs in any gate.

### Verification

The run, and then every gate this card's Validation section names:

```sh
.venv/bin/python audits/deduction-candidate/run-2026-09-15/reconcile.py \
  audits/deduction-candidate/run-2026-09-15
```

reprints the committed `usage-reconciliation.json` byte for byte, and

```sh
.venv/bin/python audits/deduction-candidate/run-2026-09-15/render_rendered_prefixes.py \
  audits/deduction-candidate/run-2026-09-15
```

reprints `rendered-prefixes.json`, each of the thirteen prefixes checked against
its frozen digest on the way out.

| Command | Result |
| --- | --- |
| `.venv/bin/python scripts/validate_task_docs.py` | passed |
| `.venv/bin/python scripts/check_doc_facts.py` | passed |
| `.venv/bin/pytest tests/experiments -q` | 396 passed |
| `.venv/bin/python scripts/verify_ml_evidence.py` | passed (offline; never `--complete`) |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | passed, real exit code 0: 7,708 Python tests passed with 20 skips and 3 xfails, strict mypy clean over 479 sources, 4 import contracts kept, 515 frontend tests in 19 files, production build green |

### Outcome summary

| Quantity | Value |
| --- | --- |
| Units completed | 25 of 100 (decision coverage 25%) |
| Paired seeds graded | 12 of 50 |
| Primary outcome, `repaired_clock` | 0 of 12 |
| Primary outcome, `combined_accounts` | 0 of 12 |
| `b` / `c` / net | 0 / 0 / 0 |
| Exact McNemar p | 1.0 — the empty-sample constant, not a null result |
| Decision-rule clauses | all three NOT EVALUABLE; conjunction not evaluable |
| Wrongful ejections | 0 on both arms |
| Ejections | `repaired_clock` 0, `combined_accounts` 1 (role-correct, not supported: both naming ballots were uncited) |
| Meeting-internal defaults | `combined_accounts` 2 defaulted turns, both by validation, in 2 units; `repaired_clock` 0 |
| Charged failed attempts | 1 — the truncated ballot, 4,734 in / 1,024 out |
| Retried calls / unaccounted attempts | 0 / 0 on both arms |
| Usage | 156 attempts, 612,588 input (16.5% of the run ceiling), 58,986 output (12.9%), $0.00 |
| Wall | 1,886.3 s elapsed (6.6% of 8 h), 1,884.6 s of model work (8.7% of 6 h) |
| Stop that fired | the per-call vote cap: one ballot at exactly 1,024 output tokens |
| Resumptions | none, and none permitted for this stop class |
| Seeds rendered | 13 of the band's 50; the other 37 stay held out |

The verdict, in the preregistration's own vocabulary: `combined_accounts` does
not advance to an explicitly scoped adopting review, and it is not rejected. The
only one of the four possible decisions a stopped run can point to is gathering
more evidence under a new authorized manifest, which the preregistration is
explicit "is not an automatic spending authorization". **A result is a
measurement and never an adoption**, and that is as true of this one as of a
conclusive one: nothing here adopts anything, flips any flag or makes any
experiment ON.

### Limitations

1. **This is not a measurement of the candidate's deduction.** Twelve paired
   seeds of fifty, with neither arm scoring, says nothing about the difference
   the design exists to detect. The one ejection the run recorded is one
   meeting.
2. **The stop is the fourth in four attempts, and the second provider-facing
   property discovered on a held-out band.** The per-unit ceilings the
   calibration sized held almost exactly — its per-unit means predicted this
   run's to within 5% — but the vote cap is the one authorized number the fourth
   authorization did not move, on the strength of a thirty-ballot calibration
   sample whose largest ballot was 237. This run's candidate ballots ran to 624
   resolved and one to the cap. Thirty calls do not bound a rare tail; the
   calibration record says the same of its own zero refusal count. What follows
   is the owner's: a stop authorizes no widening of any limit and this record
   proposes none.
3. **Thirteen more seeds of held-out margin are spent**, seventeen across four
   runs. Any future confirmation claim on this design needs a fifth band frozen
   under a new card by a preparer who has not read the run record.
4. **The band's `status` is untouched.** Flipping the fourth freeze record to
   `development` belongs to the decision that acts on this record, not to the
   runner.
5. **One asymmetry is recorded and not explained.** The candidate arm's ballots
   were guard-rewritten 13 times in 36 (12 `uncited_coerced`, 1
   `under_gate_redirect`) against the reference arm's 0, and both meeting
   defaults fell on the candidate arm. On twelve pairs that is an observation
   about what the archive contains, not a finding.
