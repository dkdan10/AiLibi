# Reconcile every paid call in the fresh-model deduction instrument

**Status:** ready

## Outcome

The instrument's post-unit spend reconciliation counts every call the provider
charged, including a call whose payload failed schema validation and whose
usage rides the surfaced default, so a schema-validation default is no longer a
stop by the back door. The stop rule the code enforces and the one the
execution manifest states are the same list, and the partial accounting a stop
reports no longer understates spend. The execution manifest is re-bound to the
second held-out band.

## Evidence

The live run of 2026-09-10 (PR #445, branch `work/fresh-deduction-run`, left
unmerged by the owner's decision; `audits/deduction-candidate/run-2026-09-10/stop.log`
on that branch) stopped after one of one hundred units on
`_reconcile_recorded_spend` (`experiments/fresh_deduction_instrument.py:1916-1935`):
the recorded spend, summed over `MeetingReplayEntry.llm_calls`, was 13,263 in /
1,448 out against an enforced budget of 15,491 / 2,309, and the gap was one paid
call (2,228 in / 861 out) whose payload failed `MeetingTurn` validation.
`meetings/manager.py:1712-1720` documents that a real provider validates before
the recording client logs the call, so that spend is carried on the surfaced
default (`MeetingManager.defaulted_calls`, written by the orchestrator as
`defaulted_calls` on the meeting record, `orchestrator/game.py:734-763`) and
never appears in `llm_calls`. The execution manifest's amended `STOP_RULE` says
a schema-validation default is not a stop while its "How each limit is
enforced" section says a reconciliation difference is one; the amendment of
2026-09-09 reached the rule and the default counter but not the reconciliation.
The defect was unreachable offline: every planted default in the tests carries
zero usage and the fake provider never returns an invalid payload with usage.
Spend on the stopped run was 36,003 input and 3,401 output tokens, 1.5% of the
authorized budget, at $0.00 marginal.

## Acceptance

- [ ] `_reconcile_recorded_spend` sums the recorded per-call spend over
  `llm_calls` AND over every defaulted call whose parse-failure metadata
  carries usage, and the partial accounting a stop reports uses the same sum. A
  test double shaped like a real provider — returning an invalid payload with
  nonzero usage on one call — makes the class reachable offline; the planted
  case reproduces the 2026-09-10 stop on the pre-fix code and passes after it,
  and a planted double-count (a defaulted call whose spend is already in
  `llm_calls`) is not counted twice.
- [ ] The code's stop conditions and the execution manifest's `STOP_RULE`
  quotation are the same list: the "How each limit is enforced" section no
  longer names a reconciliation difference as a stop of its own but as the
  check that every charged call is accounted for, and a dated section
  "Amendments after the stopped run of 2026-09-10" records the change, the
  reason and the commit. A test asserts the manifest quotes the frozen rule
  strings verbatim.
- [ ] The execution manifest's Inputs table binds the second held-out band
  frozen by [the second freeze card](held-out-prefix-freeze-2.md): the band,
  the accepted-seed range and skip count from the new
  `audits/deduction-candidate/held-out/manifest.json`, and a sentence stating
  that the 3000-3999 band is development data since 2026-09-10 and lives in
  `manifest-band-3000-3999.json`. Nothing else in the manifest's authorized
  values changes.
- [ ] The fake-provider dry run of the full pipeline completes at $0 on the new
  band with the defaulted-call double in the loop for at least one unit, and
  Results records its aggregate counts only.
- [ ] Every new gate has a planted failure proving it detects the claimed
  defect.

## Constraints

No live provider call of any kind: the second run needs a new authorization
card carrying the owner's fields, and this card is not it. The frozen analysis
(primary outcome, decision rule, minimum actionable effect, tradeoff bound) does
not change; only the reconciliation and the stop-rule text move, and the change
is dated in the manifest before any second unit runs. Do not edit
`experiments/held_out_prefixes.py`; this card lands after
[the second freeze](held-out-prefix-freeze-2.md) and merges that branch in
before re-binding the Inputs table. No band prefix is printed or opened; the
dry run writes to a temporary directory. Any `audits/` byte change recomputes
the `docs/artifacts.md` audits row.

## Expected scope

`experiments/fresh_deduction_instrument.py`,
`tests/experiments/test_fresh_deduction_instrument.py` (and a test double under
`tests/experiments/` if one is needed), `audits/deduction-candidate/execution-manifest.md`,
`docs/artifacts.md` (the `audits/` row), this card. Delivered on
`work/fresh-deduction-instrument-reconciliation`, stacked on
`work/held-out-prefix-freeze-2`, one pull request into `main`.

## Record impact

Amends the execution manifest (an `audits/` document) with a dated section and
a re-bound Inputs table; no recording, report, DTO or weight byte moves; no
experiment becomes ON; no adopting record is created; the stopped run's archive
on `work/fresh-deduction-run` is not touched.

## Validation

`uv run pytest tests/experiments -q` (fake provider only), then `uv run python
scripts/validate_task_docs.py`, `uv run python scripts/check_doc_facts.py`,
`uv run python scripts/verify_ml_evidence.py` (offline; never `--complete`),
`uv run pytest tests/scripts/test_verify_ml_evidence.py -q`, and
`bash scripts/check.sh`. Do not run the live evaluation as a check.
