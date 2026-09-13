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

- [x] Review correction: `TRANSPORT_RETRY`, the manifest's verbatim quotation of
  it and the measures row state what this side can actually see — an unaccounted
  attempt is recorded as zero tokens, which is what is KNOWN about it, and may
  have been billed for tokens this side cannot see — because
  `llm/featherless_client.py::_raw_from_response_body` refuses a body with no
  completion in it before it reads that body's `usage` block and a failure that
  DOES carry usage is never retried. A test holds the wording to that ordering
  in the adapter's source; the gap is a named limitation and the provider-client
  change that would close it is outside this card's Constraints.
- [x] Review correction: `_ModelWorkClock`'s docstring carries the 6 h / 8 h
  authorization the constants and the manifest already carried, with its
  boundary example at 5 h 59 m and the seventh hour, and a test derives both
  figures from the constants so a widened authorization cannot leave the
  enforcing class describing the retired one.
- [x] Review correction: `transport_trigger` reads the status the adapter itself
  wrote before any response body it quotes, so a permanent 4xx whose body
  carries an empty-completion or transport phrase is a stop rather than four
  sends against an endpoint that already refused it.
- [x] Review correction: a retried call is counted once its next send begins
  rather than before the backoff, so a run the elapsed deadline cancels mid-wait
  cannot report a re-send that never happened.
- [x] Review correction: every number in Results reproduces from the command
  quoted beside it on the committed tree, each perturbation states the exact
  pytest selection it was measured under, and the `audits/` byte count uses the
  repo's portable command rather than a BSD-only `stat`.
- [x] Review correction: all seven Codex P1 comments on this pull request are
  dispositioned in the dated subsection of Results — four repaired, three
  refuted with reasons.
- [x] `_InstrumentClient` retries a call up to `MAX_TRANSPORT_ATTEMPTS = 4`
  attempts (three retries) only when the attempt produced no completion: an
  empty or `choices`-less body, a transport error, a retryable HTTP status, or a
  per-attempt timeout of `PER_ATTEMPT_TIMEOUT_SECONDS` (choose a value the
  measured 12-27 s/call band justifies, e.g. 180 s) — each with a short
  backoff, each attempt charged to the budget with whatever usage rides the
  failure and counted as an unaccounted attempt when none does — which the
  provider client makes every one of these four classes, as review correction 1
  below records. A fourth failure is a stop with the same partial accounting as
  today.
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

Round 1 of two, reopened once for review. The six review corrections and the
first five original acceptance items are met and evidenced below; the last two
— re-binding the Inputs table to the third band, and a dry run over it —
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
- **The classifier is a positive matcher, and what it reads is ordered.** It
  returns a trigger only for the four recognised shapes, so an exhausted limit,
  a refusal this instrument raised, and a failure it has never seen are all left
  exactly as they were — an unclassifiable provider failure is still a stop,
  which is the conservative direction. Three things are read before the empty-
  completion wording, and each is planted below: a failure carrying parse-
  failure metadata (a completion the provider billed for), the limit and refusal
  classes, and the HTTP status the adapter itself wrote. The status is last of
  the three and still ahead of the wording because `_format_send_error` puts the
  status first and quotes the response BODY after it, so a permanent 4xx whose
  body happens to carry one of the markers would otherwise be re-sent four times
  against an endpoint that had already refused it.
- **An unaccounted attempt occupies a row, and its zero is what is KNOWN.**
  It enters the call ledger with `UNACCOUNTED_ATTEMPT_MODEL`, zero tokens and
  its real wall, which is charged
  to the work clock, so the per-arm `model_work_seconds` and the clock keep
  describing the same seconds and a stop cannot understate itself. An attempt
  the model-work WINDOW cut off keeps its own older marker,
  `ABORTED_ATTEMPT_MODEL`, because the two cut-offs mean different things and
  only one of them is retried (`0eb0a514`; both markers are asserted). The arm's
  completions are `calls` minus `unaccounted_attempts`; the marker is in the
  report's `model_ids`, so a retried run cannot read as a clean one. The zero is
  not a claim that nothing was billed: `_raw_from_response_body` refuses a body
  with no completion in it before it reads that body's `usage` block, so no
  usage rides any of the four retried classes and the wrapper has none to
  charge. `TRANSPORT_RETRY`, the manifest quotation of it and the measures row
  say exactly that, and the gap is the first limitation below.
- **The commit order is forced at one point.** `0fa2a3e5` moves `STOP_RULE`,
  so the amendment log that must name it can only be written afterwards — a
  commit cannot carry its own hash. `55132350` is that log plus the rest of the
  record; `7689c01c` adds the two planted cases that make the classifier's
  guards load-bearing; `0eb0a514` separates the two cut-off markers. Round 1 of
  review repeats the shape: `4591cc17` carries the four code corrections and
  their planted cases, and the record commit after it writes the amendment entry
  that names it. The record commits re-pin the manifest's verification section
  and recompute the `audits/` row to the tree they land on.

### Verification

Run at `4591cc17`, the last commit that moves an instrument or test byte; the
record commit after it writes the round-1 amendment entry that names it, re-pins
the manifest's verification section and recomputes the `audits/` row, and
nothing else moves.

```sh
uv run pytest tests/experiments -q
```

287 passed (283 before round 1, plus its four gates). The card's remaining
validation, in order:

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
branch a fresh checkout does not carry, and `--complete` was not run; 80 passed
(`--collect-only` reports the same 80, and that file is unchanged in this
branch; round 1 corrected the 78 first stated here, which never reproduced).

The `audits/` inventory row in `docs/artifacts.md` was recomputed with the
amended manifest staged:

```sh
git ls-files audits | wc -l
git ls-files -z audits | xargs -0 wc -c | tail -1
```

205 files, 14,960,636 bytes — the row now reads `14,960,636 tracked bytes / 205
files` against 14,950,292 on `d2812f1c`. The byte-count idiom is the portable
one other cards here use; round 1 replaced a `stat -f%z` invocation that only
BSD `stat` accepts and that this repository's Linux CI cannot run.

The fake-provider mechanics check, re-run and re-pinned in the manifest's
verification section:

```sh
uv run python -m experiments.fresh_deduction_instrument --dry-run \
  --output-dir "$TMP/dryrun"
```

100 units, 600 calls, `total_cost_usd` 0.0, about two and a half seconds of
wall, written to a temporary directory, and every figure identical to the one
the manifest carried at `08aee9cc`: 49
ejections, 22 role-correct, 27 wrongful and 22 supported-correct per arm, 150
supported and 4 guard-rewritten ballots, 98 naming ballots with no off-target
citation, 889,373 and 585,214 input tokens. Both arms report `retried_calls` 0,
`unaccounted_attempts` 0 and no trigger: the dry-run provider answers every
call, so this run exercises the retry not at all, which is why every case below
is planted.

`bash scripts/check.sh` — exit 0. Counts are in the pull request.

### The planted cases

Each is `edit, run, restore` on the committed tree at `4591cc17`, the last
commit that moves an instrument or test byte, and each turns red exactly the
tests that claim the behaviour. Every count below is the line the quoted command
prints on that tree; the record commit after it moves no Python. Cases 1 to 5
are the first round's, re-run and re-counted here because round 1 added four
tests; cases 6 to 9 are round 1's own.

1. **No retry at all** — the pre-fix behaviour, planted as
   `MAX_TRANSPORT_ATTEMPTS = 1`:
   `uv run pytest tests/experiments/test_fresh_deduction_instrument.py -k
   TestTransportRetry -q` → `9 failed, 13 passed, 186 deselected`. The nine are
   the empty body recovered, four empty bodies stopping, the transport failure
   and the retryable status, the per-attempt wall, the unaccounted attempt's
   ledger row, the retry counted at the next send, the per-arm report and the
   stop's partial accounting.
2. **A classifier with no class guards** — the parse-failure and limit/refusal
   checks deleted from `transport_trigger`, same command → `2 failed, 20 passed,
   186 deselected`: the billed refusal worded like an empty body, and the
   refused payload whose rejected input quotes an HTTP 503. Without them the
   first would be charged twice on one unit and the second would read a status
   the MODEL wrote as one the endpoint returned.
3. **One wall instead of two** — `window_binds = True` and the await bounded by
   the work window alone, same command → `1 failed, 21 passed, 186 deselected`,
   with `test_an_attempt_past_the_per_attempt_wall_is_retried` failing on
   `the retry waited for the stalled attempt: 5.0s`, which is the defect
   measured rather than asserted.
4. **The window back at 4 h** — `AUTHORIZED_MODEL_WORK_SECONDS = 4 * 60 * 60`:
   `uv run pytest tests/experiments/test_fresh_deduction_instrument.py -q` →
   `3 failed, 205 passed`, the authorized-limits object, the manifest's wall row
   (the test that pins the table to the constants) and, since round 1, the work
   clock's own docstring.
5. **The manifest stating another bound** — its stop-rule quotation reworded to
   "retried up to five times", same whole-file command → `1 failed, 207 passed`:
   `test_the_manifest_quotes_the_frozen_analysis`, so the document cannot
   describe a bound the code does not enforce.
6. **The clock's docstring left at the retired authorization** — its two figures
   put back to 4 h inside 6 h and its example to 3 h 59 m and a fifth hour, with
   the constants untouched:
   `uv run pytest tests/experiments/test_fresh_deduction_instrument.py -k
   TestModelWorkWindow -q` → `1 failed, 4 passed, 203 deselected`, which is
   exactly the state this branch shipped in and review caught.
7. **A body read before the status** — the marker matches moved back ahead of
   the status check in `transport_trigger`:
   `uv run pytest tests/experiments/test_fresh_deduction_instrument.py -k
   TestTransportRetry -q` → `1 failed, 21 passed, 186 deselected`, the failure
   being the permanent HTTP 400 whose quoted body carries an empty-completion
   phrase and is classified `empty_completion` — four sends against an endpoint
   that refused it once.
8. **A retry counted before the backoff** — `_retried_calls` incremented ahead
   of the wait, same command → `1 failed, 21 passed, 186 deselected`: a run
   cancelled during the backoff reports one retried call and one attempt, which
   is a re-send that never happened.
9. **The record claiming usage the wrapper never sees** — `TRANSPORT_RETRY` put
   back to "with whatever usage the provider reported for it":
   `uv run pytest tests/experiments/test_fresh_deduction_instrument.py -k
   "TestTransportRetry or TestExecutionManifest" -q` → `2 failed, 58 passed, 148
   deselected`, the two being the disclosure test — which reads the adapter's
   source and holds the refusal AHEAD of the usage read — and the manifest's
   verbatim quotation, so the wording and the document cannot drift apart.

### Limitations

- **A retried attempt's usage is invisible to this side, and may not be zero.**
  `llm/featherless_client.py::_raw_from_response_body` refuses a 2xx body with
  no completion in it BEFORE it reads that body's `usage` block, so a body the
  provider billed for and then answered emptily reaches the wrapper as a bare
  `RuntimeError` with nothing on it; the ledger row is zero tokens and the run's
  2.4 M input cap under-counts that attempt. The bound on the exposure is
  `MAX_TRANSPORT_ATTEMPTS - 1` unseen attempts per call. This card's Constraints
  put the retry in the wrapper and keep `llm/featherless_client.py` untouched,
  precisely so no recorded campaign's behaviour moves, so closing it is a
  provider-client change and a card of its own; what this card does instead is
  say so, in `TRANSPORT_RETRY`, in the manifest's quotation of it and its
  measures row, and in a test that holds the wording to the adapter's actual
  ordering — the same phrasing `ABORTED_ATTEMPT_MODEL` already used for the
  window cut-off.
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

### Review corrections, round 1 (2026-09-13)

Eleven blocking findings across three lenses, and the seven Codex P1 comments on
`e13bec01`. Four of the Codex comments were valid and are repaired; three are
refuted below. Code and planted cases are `4591cc17`; this record is the commit
after it. Nothing about the design moved: the frozen analysis is the same bytes,
no limit was widened, and acceptance items 6 and 7 stay open for the stacking
round.

**Repaired.**

1. *The enforcement text claimed usage it never sees* (Codex `4001070464`, and
   the same finding from two lenses). `TRANSPORT_RETRY` said every failed
   attempt is recorded "with whatever usage the provider reported for it". No
   retried class can carry usage — the adapter refuses the body before it reads
   the `usage` block, and a failure that DOES carry parse-failure metadata is
   never retried — so for these four classes the code never looks. Preserving
   the usage means moving that read, which is a change to
   `llm/featherless_client.py` this card's Constraints exclude and which would
   move every recorded campaign; the wording, the manifest quotation, the
   measures row, the two comments and the retry's own acceptance item now say
   what the mechanism does, the gap is the first limitation above, and planted
   case 9 holds the wording to the adapter's ordering.
2. *The clock's docstring stated the retired 4 h / 6 h authorization* (Codex
   `4001070472`, three lenses). Repaired to 6 h inside 8 h with the 5 h 59 m /
   seventh-hour example, `:meth:`_InstrumentClient._attempt`` for the await it
   now bounds, and a test that derives both figures from the constants
   (planted case 6).
3. *The status was read after the body* (Codex `4001070475`). Valid: a permanent
   4xx whose quoted body carries an empty-completion or transport phrase would
   have been re-sent four times. The adapter's own status now decides first and
   only `_RETRYABLE_STATUS_CODES` are retryable (planted case 7).
4. *A retried call was counted before the next send* (Codex `4001070469`).
   Valid at a deadline boundary: a cancellation during the backoff left one
   retried call against one attempt. Counted after the wait now, with nothing
   awaited before the send (planted case 8).
5. *Numbers that did not reproduce.* `tests/scripts/test_verify_ml_evidence.py`
   is 80 tests, not the 78 stated here and in the pull request; that file is
   unchanged in this branch, so 78 never held. Planted case 1 was `7 failed, 10
   passed` and case 3 `1 failed, 22 passed` against a quoted selection that
   prints neither. Every case is re-run above on `4591cc17`, each with the exact
   command and the exact line it prints, and the pull request body carries the
   same numbers.
6. *A BSD-only byte count* (Codex `4001070471`). `stat -f%z` is a filesystem
   query to GNU coreutils and exits non-zero on the Linux CI. Replaced with the
   portable `xargs -0 wc -c` idiom other cards here use; the total is unchanged
   apart from this round's own manifest bytes (14,960,636 / 205 files).
7. *Provenance longer than one trailing line* (Codex `4001070465`, craft rule
   1). The work-window constants' comment carried the source card, the date, the
   superseded limits and two run measurements. It now explains the current
   intent and names its source in one trailing line; the history it dropped is
   in the manifest's amendment log, which is where the record lives.

**Refuted.**

- *"Retain retry counts for each unit"* (Codex `4001070467`). The report is
  aggregate-only by contract — `InstrumentReport`'s docstring and
  `assert_report_holds_no_prefix_bytes` — and "per unit" here means what it
  means for the meeting-internal defaults this counter was built beside:
  `UnitRecord.transport_attempts` carries each unit's own counts, the per-arm
  summary publishes `units_with_retries` exactly as it publishes
  `units_with_defaults`, and every unaccounted attempt is a row in that unit's
  `calls` with the `no-completion-returned` marker, which is where the
  granularity actually lives. Emitting a per-unit row keyed to a held-out unit
  would add a unit-resolved surface to a report whose whole design is that it
  carries none. Acceptance item 3 is met on the same reading its own "beside the
  meeting-internal defaults" points at.
- *"Preserve the amendment commit instead of squashing it"* (Codex
  `4001070474`). It reads a history this branch does not have: it names
  `f3d42d05`, whose sole parent it gives as `d2812f1c`. On this branch
  `0fa2a3e5` is an ancestor of `HEAD` and touches the instrument, which is what
  `test_the_transport_amendment_names_its_reason_and_a_real_commit` checks and
  what the green suite shows. Round 1 tightened that test rather than leaving
  the point untested: it now resolves EVERY dated entry's commit in the section,
  so the round-1 entry is held to the same standard as the first.
- *The empty-completion retry "potentially allows the authorized live run to
  cross a token cap without stopping"* (the reach of Codex `4001070464`). The
  under-count is real and is the limitation above; "without stopping" is not.
  The run-level budget is charged for every completion that arrives, the
  per-unit and run caps are read back after each unit, and the unseen quantity
  is bounded by three attempts per call. What it cannot do is turn a stop into a
  continue: nothing in this wrapper widens a limit, and an exhausted budget is
  never a retry class.

