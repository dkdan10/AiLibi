# Make the fresh-model deduction instrument survive a provider that returns nothing

**Status:** active

## Outcome

A call the provider answers with nothing — an empty completion body, a
transport error, a retryable status or a per-attempt timeout — is retried a
bounded number of times inside the instrument's own client wrapper, with every
attempt counted per arm and reported, before it becomes a stop. A truncated
response, a schema-invalid payload and an exhausted limit are never retried.
The execution manifest states the retry bound in its stop rule, dated as an
amendment made before any unit resolved, and its limits table carries the
wall window the owner widened for the third run.

## Evidence

The second live run (PR #448, closed unmerged; branch `work/fresh-deduction-run-2`,
`audits/deduction-candidate/run-2026-09-13/stop.log`) stopped on its fifth
call: Featherless returned a 2xx body with no `choices`;
`llm/featherless_client.py::_raw_from_response_body` (`:804-833`) refuses to
record an empty completion and raises a bare `RuntimeError`, which is in none
of the client's retry classes (`_RETRYABLE_STATUS`, `httpx.TransportError`,
`json.JSONDecodeError`, `:691-737`), so the instrument's `_InstrumentClient`
re-raised it and `run_instrument` aborted with partial accounting. A sequential
run of one hundred units needs about six hundred consecutive provider successes;
the same provider stalled for 3 h 21 m in an earlier record
(`audits/audit-phase-21-adopting-record.md:373-380`). An empty completion is
not a sample — the model produced nothing — so retrying it does not re-sample
the frozen design; a truncated or schema-invalid completion is a sample and
stays what the stop rule and the meeting layer already make of it. The four
resolved calls ran at 26.6 s each against 11.7 s three days earlier; at that
pace six hundred calls need about 4 h 26 m, over the 4 h model-work window the
first authorization set, which is why
[the third authorization](fresh-deduction-authorization-3.md) widens the window
to 6 h of model work within 8 h elapsed with the token budget unchanged.

## Acceptance

- [x] `_InstrumentClient` retries a call up to `MAX_TRANSPORT_ATTEMPTS = 4`
  attempts (three retries) only when the attempt produced no completion: an
  empty or `choices`-less body, a transport error, a retryable HTTP status, or a
  per-attempt timeout of `PER_ATTEMPT_TIMEOUT_SECONDS` (choose a value the
  measured 12-27 s/call band justifies, e.g. 180 s) — each with a short
  backoff, each attempt charged to the budget when the provider reported usage
  and counted as an unaccounted attempt when it did not. A fourth failure is a
  stop with the same partial accounting as today.
- [x] Never retried: a response that reached its output cap (a truncation stays
  a stop), a returned payload that fails schema validation (the meeting layer's
  default path keeps handling it and the reconciliation counts its spend), an
  exhausted budget or deadline, a live-gate refusal.
- [x] Attempts are counted per arm and per unit (retried calls, unaccounted
  attempts, the trigger class of each) in the report and in the partial
  accounting a stop reports, beside the meeting-internal defaults.
- [x] Planted cases with a real-provider-shaped double: an empty body once then
  a valid completion continues the unit and counts one retry; four empty bodies
  stop the run with the attempts in the partial accounting; a transport error
  and a per-attempt timeout are retried; a truncated response is not; a
  schema-invalid payload is not retried by the wrapper; each case reproduced red
  on the pre-fix code where it changes behaviour.
- [x] The execution manifest's `STOP_RULE` quotation and the code's frozen
  string move together to name the bound ("retried up to three times, then a
  stop"), the "How each limit is enforced" section describes the wrapper's
  retry, a dated section "Amendments after the stopped run of 2026-09-13"
  records the change and the reason, and the limits table's wall row and the
  instrument's `AUTHORIZED_MODEL_WORK_SECONDS` / `AUTHORIZED_ELAPSED_SECONDS`
  carry 6 h / 8 h, copied from the third authorization card, with the test
  that pins the table to the constants updated.
- [ ] The Inputs table binds the third band frozen by
  [the third freeze](held-out-prefix-freeze-3.md) (band, accepted range, skip
  count from the new `held-out/manifest.json`), names the 5000-5999 band as
  development data since 2026-09-13, and `assert_manifest_binds_the_live_band`
  passes against the merged record.
- [ ] A fake-provider dry run of the full pipeline on the new band completes at
  $0 with the empty-body double active for at least one call, and Results
  records its aggregate counts only.

## Constraints

No live provider call: the third run is authorized by
[its own card](fresh-deduction-authorization-3.md) and dispatched separately.
The primary outcome, the decision rule, the minimum actionable effect and the
tradeoff bound do not change; only the stop rule's transport clause, the
enforcement text and the wall window move, dated in the manifest before any
unit resolves. The retry lives in the instrument's wrapper, not in
`llm/featherless_client.py`, so recorded campaigns keep their behaviour. Do
not edit `experiments/held_out_prefixes.py`; this card lands after
[the third freeze](held-out-prefix-freeze-3.md) and merges that branch in before
re-binding the Inputs table. No band prefix is printed or opened; the dry run
writes to a temporary directory. Any `audits/` byte change recomputes the
`docs/artifacts.md` audits row.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py`,
`tests/experiments/burned_call_double.py` (extend the double) or a sibling
double, `audits/deduction-candidate/execution-manifest.md`, `docs/artifacts.md`
(the `audits/` row), `tasks/README.md`'s derived inventory sentence, this card.
Delivered on `work/fresh-deduction-instrument-transport-resilience`, stacked on
`work/held-out-prefix-freeze-3`, one pull request into `main`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section, a
re-bound Inputs table and the widened wall row; no recording, report, DTO or
weight byte moves; no experiment becomes ON; no adopting record is created;
the archives of both stopped runs on their branches are not touched.

## Validation

`uv run pytest tests/experiments -q` (fake provider only), then `uv run python
scripts/validate_task_docs.py`, `uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh`. Do not run the live evaluation as a check.

## Results

Round 1 of two. Acceptance items 1 to 5 are met and evidenced below; items 6
and 7 — re-binding the Inputs table to the third band, and a dry run over it —
stay unchecked and this card stays `active`, because
[the third freeze](held-out-prefix-freeze-3.md) is not merged yet. They are the
coordinator's stacking round: this branch merges that one in, re-binds the
table, runs the dry run on the new band into a temporary directory, and closes
both boxes then. No prefix of any band was printed, opened or committed here,
and no provider was reached: every case below runs on the fake provider or on a
double.

### What changed

`_InstrumentClient.complete` is now a bounded retry loop over a new
`_attempt`, which is the old body: one send, recorded whatever it does. The
wrapper is the sixth job named in its own docstring, and the placement is the
decision — `llm/featherless_client.py` is untouched, so every recorded campaign
keeps the retry classes it was recorded under, and this run's own wrapper is
what changes. `transport_trigger` names the four ways an attempt can produce
nothing (`empty_completion`, `transport_error`, `retryable_status`,
`attempt_timeout`); `TransportAttempts` counts what was re-sent; `STOP_RULE`
gains the clause that states the bound and `TRANSPORT_RETRY` states how it is
enforced. The two clocks are unchanged in kind and widened in size:
`AUTHORIZED_MODEL_WORK_SECONDS` / `AUTHORIZED_ELAPSED_SECONDS` are 6 h / 8 h,
copied from
[the third authorization card](fresh-deduction-authorization-3.md)'s
Constraints table.

The record moves with it, in the manifest's "Amendments after the stopped run
of 2026-09-13" (`55132350`, naming the code commit `0fa2a3e5`): the frozen stop
rule is quoted in its new bytes, "How each limit is enforced" gains a Transport
bullet quoting `TRANSPORT_RETRY` verbatim, the Wall bullet and the authorized
table carry the widened window, the Inputs row on a missing attempt says the
bound, and the measures table gains the per-arm attempt counts. The
preregistration's "Reaching an authorized time, token or cost limit stops new
calls, retains partial evidence and unresolved accounting, and does not trigger
unbudgeted retries or silent expansion" is what the design answers to: no limit
is widened by a retry, every attempt is inside the model-work window, and an
exhausted bound is a stop with the partial accounting `PartialRun` already
carried.

### Decisions

- **The bound is four attempts.** A retry re-draws nothing — an attempt that
  produced no completion is not a sample — so more attempts buy only a longer
  wait before the same stop. Four is what a sequential hundred units needs
  against a transient, and `MAX_TRANSPORT_ATTEMPTS` is what a test pins the
  frozen rule's "retried up to three times" to.
- **The per-attempt wall is 180 s**, sized off this evaluation's own measured
  band: 11.7 s/call on 2026-09-10 and 26.6 s/call on 2026-09-13, so 180 s is
  about seven times the slowest call anyone has measured and a healthy call
  cannot reach it. What it bounds is the provider client's own budget — six
  sends at a 600 s timeout — so one stalled call can no longer hold the run for
  the better part of an hour; four attempts at this wall cost at most 12 minutes
  of a 6 h window.
- **Which wall expired decides what a cut-off means.** Each attempt is bounded
  by `min(work_clock.remaining(), PER_ATTEMPT_TIMEOUT_SECONDS)`. The window is a
  limit the run reached and stays the stop it was; the per-attempt wall is an
  endpoint that stopped answering and is a retry. A `TimeoutError` the inner
  client raises itself is classified `transport_error` — the wording the
  pre-existing test used for it — and the stop that eventually follows is
  `TransportAttemptsExhausted`, never the window.
- **The classifier is a positive matcher with two class guards.** It returns a
  trigger only for the four recognised shapes, so an exhausted limit, a refusal
  this instrument raised, and a failure it has never seen are all left exactly
  as they were — an unclassifiable provider failure is still a stop, which is
  the conservative direction. The two guards ahead of the wording (a failure
  carrying parse-failure metadata, and the limit/refusal classes) are
  load-bearing and planted below.
- **An unaccounted attempt occupies a row.** It enters the call ledger with
  `UNACCOUNTED_ATTEMPT_MODEL`, zero tokens and its real wall, which is charged
  to the work clock, so the per-arm `model_work_seconds` and the clock keep
  describing the same seconds and a stop cannot understate itself. An attempt
  the model-work WINDOW cut off keeps its own older marker,
  `ABORTED_ATTEMPT_MODEL`, because the two cut-offs mean different things and
  only one of them is retried (`0eb0a514`; both markers are asserted). The arm's
  completions are `calls` minus `unaccounted_attempts`; the marker is in the
  report's `model_ids`, so a retried run cannot read as a clean one.
- **The commit order is forced at one point.** `0fa2a3e5` moves `STOP_RULE`,
  so the amendment log that must name it can only be written afterwards — a
  commit cannot carry its own hash. `55132350` is that log plus the rest of the
  record; `7689c01c` adds the two planted cases that make the classifier's
  guards load-bearing; `0eb0a514` separates the two cut-off markers. The record
  commits re-pin the manifest's verification section and recompute the
  `audits/` row to the tree they land on.

### Verification

Run at `0eb0a514`, the last commit that moves an instrument byte; the record
commit after it re-pins the manifest's verification section and the `audits/`
row, and nothing else moves.

```sh
uv run pytest tests/experiments -q
```

283 passed. The card's remaining validation, in order:

```sh
uv run python scripts/validate_task_docs.py
uv run python scripts/check_doc_facts.py
uv run python scripts/verify_ml_evidence.py
uv run pytest tests/scripts/test_verify_ml_evidence.py -q
```

`Task docs validation passed: 390 historical phase tasks and 390 prompts; 49
work cards.`; the four doc-fact lines (front door, ml-program, budgets)
verified; `checks: 60 | OK 48 | FAIL 0 | ABSENT 7 | INFO 5` with
`verify-ml-evidence: every check passed` — the 7 absent rows are the evidence
branch a fresh checkout does not carry, and `--complete` was not run; 78 passed.

The `audits/` inventory row in `docs/artifacts.md` was recomputed with the
amended manifest staged:

```sh
git ls-files audits | wc -l
git ls-files -z audits | xargs -0 -n1 -I{} stat -f%z {} | awk '{s+=$1} END {print s}'
```

205 files, 14,958,353 bytes — the row now reads `14,958,353 tracked bytes / 205
files` against 14,950,292 before.

The fake-provider mechanics check, re-run and re-pinned in the manifest's
verification section:

```sh
.venv/bin/python -m experiments.fresh_deduction_instrument --dry-run
```

100 units, 600 calls, `total_cost_usd` 0.0, about three seconds of wall, and
every figure identical to the one the manifest carried at `08aee9cc`: 49
ejections, 22 role-correct, 27 wrongful and 22 supported-correct per arm, 150
supported and 4 guard-rewritten ballots, 98 naming ballots with no off-target
citation, 889,373 and 585,214 input tokens. Both arms report `retried_calls` 0,
`unaccounted_attempts` 0 and no trigger: the dry-run provider answers every
call, so this run exercises the retry not at all, which is why every case below
is planted.

`bash scripts/check.sh` — exit 0. Counts are in the pull request.

### The planted cases

Each is `edit, run, restore` on the committed tree at `7689c01c`, and each
turns red exactly the tests that claim the behaviour. The counts below are that
tree's; `0eb0a514` adds two marker assertions to two of the same tests and
changes none of these outcomes.

1. **No retry at all** — the pre-fix behaviour, planted as
   `MAX_TRANSPORT_ATTEMPTS = 1`:
   `uv run pytest tests/experiments/test_fresh_deduction_instrument.py -k
   TestTransportRetry` → `7 failed, 10 passed`, the seven being the empty body
   recovered, four empty bodies stopping, the transport failure and the
   retryable status, the per-attempt wall, the per-arm report and the stop's
   partial accounting.
2. **A classifier with no class guards** — the parse-failure and
   limit/refusal checks deleted from `transport_trigger`: `2 failed, 17 passed`,
   the two being the billed refusal worded like an empty body and the refused
   payload whose rejected input quotes an HTTP 503. Without them the first would
   be charged twice on one unit and the second would read a status the MODEL
   wrote as one the endpoint returned.
3. **One wall instead of two** — `window_binds = True` and the await bounded by
   the work window alone: `1 failed, 22 passed`, with
   `test_an_attempt_past_the_per_attempt_wall_is_retried` failing on
   `the retry waited for the stalled attempt: 5.0s`, which is the defect
   measured rather than asserted.
4. **The window back at 4 h** — `AUTHORIZED_MODEL_WORK_SECONDS = 4 * 60 * 60`:
   `2 failed`, the authorized-limits object and the manifest's wall row, which
   is the test that pins the table to the constants.
5. **The manifest stating another bound** — its stop-rule quotation reworded to
   "retried up to five times": `test_the_manifest_quotes_the_frozen_analysis`
   fails, so the document cannot describe a bound the code does not enforce.

### Limitations

- The empty-completion class has no exception type of its own: the adapter
  raises a bare `RuntimeError`, so the classifier keys on its wording.
  `test_the_classifier_keys_on_wording_the_adapter_still_uses` reads
  `llm/featherless_client.py` as TEXT — never an import, so this test module
  gains no route to a real client — and holds every fragment and the retryable
  status set to that source, which turns a rewording red here instead of into a
  stop mid-run. It does not cover a failure shape that module does not yet
  produce.
- A provider failure the classifier cannot place is not retried. That is the
  choice, not an oversight, and the pre-existing
  `test_a_provider_transport_failure_stops_the_run_with_partial_state` is the
  case: an ad-hoc `RuntimeError` still stops the run with its partial
  accounting.
- Nothing here was proven against the endpoint. The doubles wear the adapter's
  own message shapes, and a live call is neither made nor authorized by this
  card; the third run is
  [its own card](fresh-deduction-authorization-3.md)'s, dispatched separately
  after both of these merge.
- The cost statement the manifest quotes is unchanged and still projects "2.0 M
  tokens over a 6-hour elapsed window". That sentence is the first
  authorization's and the third card did not re-cut it; the elapsed limit this
  manifest binds is the 8 h row above it, and the amendment says so.
- The Inputs table still binds 5000-5999, which is development data since the
  stopped run of 2026-09-13 rendered its first seed. Until round 2 re-binds it,
  `assert_manifest_binds_the_live_band` would pass against a band no run may
  draw; the live gate that would refuse such a run is the third freeze's
  record, not this card's.
