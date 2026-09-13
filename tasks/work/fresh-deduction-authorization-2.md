# Second run of the fresh-model deduction evaluation

**Status:** done

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

- [x] The execution manifest's authorization fields carry exactly the values in
  Constraints, and the instrument enforces them: the per-unit `GameBudget` with
  a run-level parent, the `RunDeadline`, the per-call caps, sequential order.
  Reconciled once more before any wall time was committed, by printing the
  instrument's own constants and comparing them to this table field by field —
  `featherless`, `Qwen/Qwen3.6-27B`, caps 2,048 / 1,024, temperatures 0.4 / 0.2,
  2,400,000 / 200,000 run and 45,000 / 4,000 per unit, 14,400 s of model work
  inside 21,600 s elapsed, `sequential`, roster 4/1 with 3 living voters. Every
  value matched; the comparison is quoted in Results, "Authorized values,
  reconciled before the run". The instrument enforces rather than describes them
  (`AUTHORIZED_LIMITS`, `AUTHORIZED_SAMPLING`), and
  `tests/experiments/test_fresh_deduction_instrument.py` asserts the manifest
  quotes each constant — 260 passed before the run.
- [x] The runner regenerates the frozen set from the band in the manifest and
  the instrument verifies every digest and the skip list before any client is
  constructed; the runner opens no prefix before the run.
  `assert_ready_for_a_live_run` was run offline first, constructing no client:
  it ran `assert_live_run_is_authorized` — including
  `assert_manifest_binds_the_live_band`, the gate PR #447 added, which resolved
  the Inputs row to the band 5000-5999 — and then `verify_frozen_set`, matching
  all 50 digests and the 3 `witnessed_kill` skips against the freeze record at
  sha256 `b93262acc21af1b2c98ec97f84d9f3b23a8740ab7b22fc91ac79f3c2911cdfa1`,
  the record [the second freeze card](held-out-prefix-freeze-2.md) committed.
  The live run re-ran the same gate before its own client existed.
  **This runner opened, printed and reasoned about no prefix before the run**:
  the set was consumed only as `HeldOutPrefix` objects driving the engine, and
  the only per-seed values that reached this session before the run were the
  accepted seed numbers the freeze manifest already publishes. Only seed 5000
  was ever rendered to the model.
- [x] The run records actual tokens, elapsed wall, model-work time and the
  $0.00 marginal cost against these limits, per arm and for the run; an
  exhausted budget or deadline stops the run and authorizes no retry.
  Actual: 4 resolved calls (plus one failed attempt of unknown spend), 13,182
  input and 993 output tokens, 110.9 s elapsed and 106.3 s of model work,
  `cost_usd` 0.0 throughout, all on `repaired_clock`; `combined_accounts` was
  never started. Against 2,400,000 / 200,000 tokens, 45,000 / 4,000 per unit,
  6 h elapsed and 4 h of model work, the largest usage was 29.3% of one per-unit
  ceiling. No budget and no deadline came close and none fired; the run stopped
  on a provider fault instead, **and no retry was made**. The full table is in
  [RESULTS.md](../../audits/deduction-candidate/run-2026-09-13/RESULTS.md),
  "Usage against every authorized limit".
- [x] The paired result is evaluated under the frozen decision rule (exact
  McNemar p over the discordant pairs, the net difference bar, the
  wrongful-ejection bound) and written down in the preregistration's own
  vocabulary as a measurement; every stop condition is checked and reported.
  Evaluated and reported as **not evaluable**, clause by clause, which is the
  honest reading of zero paired units: `b` and `c` are undefined, the 1.0 that
  `exact_mcnemar_p(0, 0)` returns is the empty-sample constant its own docstring
  names and not a null result, and the wrongful-ejection bound is a net increase
  over 50 paired units that cannot be computed on zero. The conjunction is
  therefore not evaluable; `combined_accounts` is neither advanced nor rejected.
  In the preregistration's vocabulary the run reaches none of the four possible
  decisions, and the only route it identifies is more evidence under a new
  authorized manifest — which that document says is not an automatic spending
  authorization. Every `STOP_RULE` condition is tabulated against what the run
  recorded in RESULTS.md, "Every stop condition, checked", including the one
  that fired.
- [x] The results, the per-unit records, the usage reconciliation and the
  archived prefixes (development data once archived) land under
  `audits/deduction-candidate/run-2026-09-13/`, indexed from the candidate's
  README, with the `docs/artifacts.md` audits row recomputed.
  The directory holds `RESULTS.md`, the single per-unit replay
  `repaired_clock-seed-5000.jsonl` and `stop.log`, 68 KB in three files; no
  report JSON exists, because `main()` writes it only after `run_instrument`
  returns and it raised. The usage reconciliation is the RESULTS.md section
  named above, computed from the archived rows by a command it quotes, because
  the instrument's own post-unit reconciliation was never reached. Indexed from
  `audits/deduction-candidate/README.md` with a dated line in its
  `checkpoint.md`, and the `docs/artifacts.md` `audits/` row recomputed with
  everything staged. **Only the one rendered prefix is archived**, which is a
  decision recorded in Results and in RESULTS.md rather than an omission.

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

## Results

**The one authorized live run was made once, and it stopped inside its first
unit on a provider fault.** 0 of 100 units completed, no paired unit exists, the
primary outcome was not measured and the decision rule is not evaluable. No
retry was made and no limit was widened. The full record is
[RESULTS.md](../../audits/deduction-candidate/run-2026-09-13/RESULTS.md); this
section is the operating account.

### Architecture and design references

The design is [the preregistration](../../audits/deduction-candidate/preregistration.md)
as bound by [the execution manifest](../../audits/deduction-candidate/execution-manifest.md);
the runner is `experiments/fresh_deduction_instrument.py`, unchanged by this
card (sha256 `2e8e7f87…7f99c00b`). The inputs are the second held-out band,
5000-5999, frozen by [the second freeze card](held-out-prefix-freeze-2.md)
(PR #446, `ca6e97d6`); the instrument's spend reconciliation is the one repaired
by [the reconciliation card](fresh-deduction-instrument-reconciliation.md)
(PR #447, `7353ff88`). The run was made from `78fa2841` on
`work/fresh-deduction-run-2`. No instrument, generator, manifest or
frozen-analysis byte moves on this branch.

### Authorized values, reconciled before the run

Printed from the instrument's own constants and compared to Constraints above,
before any wall time was committed:

```text
provider            featherless
model               Qwen/Qwen3.6-27B
prompt set          qwen3_6_27b
limits              {'run_max_input_tokens': 2400000, 'run_max_output_tokens': 200000,
                     'unit_max_input_tokens': 45000, 'unit_max_output_tokens': 4000,
                     'max_cost_usd': 0.0, 'elapsed_seconds': 21600.0,
                     'model_work_seconds': 14400.0}
sampling            {'turn_max_tokens': 2048, 'turn_temperature': 0.4,
                     'vote_max_tokens': 1024, 'vote_temperature': 0.2}
exec mode           sequential
roster              4 1 3
manifest path       audits/deduction-candidate/execution-manifest.md
min effect / alpha  10 0.05
primary outcome     supported_correct_ejection
```

Every field matches this card's Constraints table and the manifest's copy of it.
The band binding was checked separately — `manifest_bound_band` resolved the
Inputs row to `(5000, 5999)` and `assert_manifest_binds_the_live_band` accepted
it against the freeze record, which reads `status: held_out`, band 5000-5999,
50 accepted seeds 5000-5052, 3 skips all `witnessed_kill`.

### What happened

Four calls resolved — three meeting turns and one ballot, all served by the
authorized checkpoint — and the fifth, the second voter's ballot, returned a
2xx body carrying no `choices`. `llm/featherless_client.py::_raw_from_response_body`
refuses to record an empty completion and raised; that shape is not in the
client's retry class (retryable status, transport error, JSON decode error), so
the send itself had succeeded. `_InstrumentClient` found no parse-failure
metadata on the exception — it is a transport-mapping `RuntimeError`, not a
billed-and-refused payload — and re-raised it untouched, which the module's own
comment describes. `run_instrument` converted it into `InstrumentAborted`
carrying the partial accounting, which is what the manifest promises for "a
provider transport failure".

The stop is the provider's, not this repository's. Every gate the run reached
was green, and the run never reached the code PR #447 repaired:
`_reconcile_recorded_spend` and `_assert_charged_spend_is_within_caps` run after
a unit's meeting resolves, and this meeting was written out as
`meeting_aborted`. **The repaired reconciliation is still unproved against a
real provider.**

### Decisions

1. **No retry, and no second attempt.** Both the manifest's stop rule and this
   card authorize one run; a stop authorizes no retry and no widening, and an
   environmental failure that is not a stop condition is a new owner decision
   rather than a runner's. The process was not re-run, and the credential file
   was deleted as soon as it exited.
2. **Only the rendered prefix is archived.** The manifest archives prefixes
   "when they are no longer held out". Seed 5000 was rendered and is revealed by
   the archived replay; the other 49 were regenerated in process, checked
   against the frozen digests and discarded unrendered, and they are still held
   out. Committing them would convert the whole band to development data for no
   gain — the cost the first band already paid once — so they are deliberately
   not archived. This narrows Acceptance item 5's "archived prefixes" to the one
   that qualifies, and says so rather than quietly satisfying it.
3. **The band's `status` is not flipped.** The freeze record still reads
   `held_out`. The manifest's Roles section puts that flip on the decision that
   acts on a result which informs a fix, not on the runner, and the first run set
   the same precedent.
4. **The usage reconciliation is computed offline from the archived rows**,
   because the instrument's own never ran. RESULTS.md quotes the command that
   reproduces every figure in it.
5. **A documentation asymmetry is recorded, not filed as a finding.** A provider
   transport failure is bound as a stop by the manifest's Inputs row and its
   enforcement section but is absent from `STOP_RULE`'s enumeration. Unlike
   2026-09-10 the document and the code did not disagree about this run's fate —
   the instrument did exactly what both sentences promise — so this is written
   down for the owner rather than repaired here, which would move a frozen
   analysis this card may not touch.

### Verification

Run on this branch with every change staged. No live provider call was made
after the single authorized run, and `--complete` was not run on
`verify_ml_evidence.py`; its seven `ABSENT` rows are the archived ML evidence
this checkout does not carry.

| Command | Result |
| --- | --- |
| `.venv/bin/pytest tests/experiments -q` (before the run) | 260 passed |
| `.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run --units 2 --output-dir <temp>` | exit 0, fake provider, `total_cost_usd` 0.0, 24 calls; output not committed |
| `assert_ready_for_a_live_run` offline, constructing no client | gate passed; 50 prefixes verified, freeze sha256 `b93262ac…911cdfa1` |
| the single authorized live invocation | `InstrumentAborted` after 4 resolved calls; 0/100 units, 110.9 s elapsed, 106.3 s model work, $0.00 |
| `.venv/bin/pytest tests/experiments -q` (after) | 260 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 390 phase tasks, 390 prompts, 46 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5` |
| `.venv/bin/pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0: ruff clean over 504 files, import-linter 4 contracts kept / 0 broken, mypy clean over 475 source files, 7545 passed / 20 skipped / 3 xfailed, frontend 515 tests in 19 files |

`docs/artifacts.md`'s `audits/` row is recomputed with everything staged: 208
files, 15,042,993 tracked bytes, from

```text
$ git ls-files -z audits | xargs -0 wc -c | awk '$2 != "total" {n += 1; s += $1} END {print n, s}'
208 15042993
```

The archive was scanned before committing and carries neither the API key's
first six characters (0 occurrences across both files, counted without printing
the needle) nor the runner flag (0 occurrences), and the death-tick body-handle
regex matches nothing on any surface the stop condition covers.

### Outcome summary

`combined_accounts` is neither advanced nor rejected. In the preregistration's
vocabulary the run reaches none of the four possible decisions, because none of
them is a statement a zero-unit sample supports; the only route it identifies is
more evidence under a new authorized manifest, which is explicitly not an
automatic spending authorization. What a third authorization would have to price
is listed in RESULTS.md's verdict: an unrecordable completion can end a
sequential 100-unit run wherever it arrives, and the choice between stopping and
retrying such a call is the owner's design question; the four resolved calls ran
at 26.6 s each, which would put 600 calls past the authorized 4 h of model work;
the repaired reconciliation is still unproved live; and a third run needs a third
band, because this one now has a public seed.

### Limitations

Four calls establish no rate, and nothing in this record should be read as one —
not the 26.6 s per call, not the zero meeting-internal defaults, not the zero
charged failed attempts. The failed attempt's spend is unknown rather than zero:
if Featherless billed for the empty completion those tokens are invisible to both
sides of every comparison the instrument makes, and its wall is likewise
uncharged to the model-work clock (110.9 s elapsed against 106.3 s charged). On
this provider the marginal cost is $0.00 either way and the amount at stake is one
call against a ceiling the run used 0.55% of, so neither is load-bearing here —
but "an exception without parse-failure metadata bought nothing" is an assumption
about the provider rather than a measurement, and it is stated rather than left to
be discovered. The evaluation has now twice failed to reach its second seed, for
two unrelated reasons, and has spent one seed of each of two held-out bands.
