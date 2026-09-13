# Make the fresh-model deduction instrument survive a provider that returns nothing

**Status:** ready

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

- [ ] `_InstrumentClient` retries a call up to `MAX_TRANSPORT_ATTEMPTS = 4`
  attempts (three retries) only when the attempt produced no completion: an
  empty or `choices`-less body, a transport error, a retryable HTTP status, or a
  per-attempt timeout of `PER_ATTEMPT_TIMEOUT_SECONDS` (choose a value the
  measured 12-27 s/call band justifies, e.g. 180 s) — each with a short
  backoff, each attempt charged to the budget when the provider reported usage
  and counted as an unaccounted attempt when it did not. A fourth failure is a
  stop with the same partial accounting as today.
- [ ] Never retried: a response that reached its output cap (a truncation stays
  a stop), a returned payload that fails schema validation (the meeting layer's
  default path keeps handling it and the reconciliation counts its spend), an
  exhausted budget or deadline, a live-gate refusal.
- [ ] Attempts are counted per arm and per unit (retried calls, unaccounted
  attempts, the trigger class of each) in the report and in the partial
  accounting a stop reports, beside the meeting-internal defaults.
- [ ] Planted cases with a real-provider-shaped double: an empty body once then
  a valid completion continues the unit and counts one retry; four empty bodies
  stop the run with the attempts in the partial accounting; a transport error
  and a per-attempt timeout are retried; a truncated response is not; a
  schema-invalid payload is not retried by the wrapper; each case reproduced red
  on the pre-fix code where it changes behaviour.
- [ ] The execution manifest's `STOP_RULE` quotation and the code's frozen
  string move together to name the bound ("retried up to three times, then a
  stop"), the "How each limit is enforced" section describes the wrapper's
  retry, a dated section "Amendments after the stopped run of 2026-09-13"
  records the change and the reason, and the limits table's wall row and the
  instrument's `AUTHORIZED_MODEL_WORK_SECONDS` / `AUTHORIZED_ELAPSED_SECONDS`
  carry 6 h / 8 h, copied from the third authorization card, with the test
  that pins the table to the constants updated.
- [ ] The Inputs table binds the third band frozen by
  [the third freeze](held-out-prefix-freeze-3.md) (band, accepted range, skip
  count read off `audits/deduction-candidate/held-out/manifest.json`), names the
  5000-5999 band as development data since 2026-09-13 and links its record at
  `audits/deduction-candidate/held-out/manifest-band-5000-5999.json`, and
  `assert_manifest_binds_the_live_band` passes against the merged record. Until
  this item lands the committed Inputs row is the open obligation the converted
  record's `converted.informed` names, and
  `TestExecutionManifest::test_a_binding_to_a_converted_record_stays_an_open_obligation`
  fails the moment this card closes with the row still stale.
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
