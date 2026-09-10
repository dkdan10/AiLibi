# Reconcile every paid call in the fresh-model deduction instrument

**Status:** active

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

- [x] `_reconcile_recorded_spend` sums the recorded per-call spend over
  `llm_calls` AND over every defaulted call whose parse-failure metadata
  carries usage, and the partial accounting a stop reports uses the same sum. A
  test double shaped like a real provider — returning an invalid payload with
  nonzero usage on one call — makes the class reachable offline; the planted
  case reproduces the 2026-09-10 stop on the pre-fix code and passes after it,
  and a planted double-count (a defaulted call whose spend is already in
  `llm_calls`) is not counted twice.
- [x] The code's stop conditions and the execution manifest's `STOP_RULE`
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
- [x] Every new gate has a planted failure proving it detects the claimed
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

## Results

**Status is `active`, not `done`.** Acceptance items 3 and 4 need the second
held-out band, which [the second freeze card](held-out-prefix-freeze-2.md) has
not delivered into this branch yet. Re-binding the Inputs table to a band that
does not exist would bind a fiction, and the dry run item 4 asks for is a run on
that band. Both are closed in a later round, after the freeze is verified and
merged in; this round is items 1, 2 and 5.

### The accounting defect and the fix (2026-09-10, `d8eb7d36`)

`_reconcile_recorded_spend` summed `MeetingReplayEntry.llm_calls` alone, and the
budget layer does not. `llm/budgeted_client.py` charges a failed call's usage off
the parse-failure metadata riding its exception, and a real provider validates
the completion itself and raises before `orchestrator.game._RecordingLLMClient`
can log it (`meetings/manager.py:1712-1720` states the property), so a paid call
whose payload the provider refused is charged and carried nowhere the old sum
could see. The manifest's design section
"Sampling configuration, caps and limits" is where that check lives.

The reconciliation now reads `_recorded_spend`: the meeting row's resolved calls
plus `_charged_failed_attempts` — the replay's failed-call rows for this meeting
that carry usage. Usage is the discriminator and the producer writes it. The
orchestrator records a burned attempt with its real model, tokens and cost
(`_record_captured_failures`, or `_record_deadline_defaults` off a default's
`parse_failures` for a runner with no identified ledger), and writes a ZERO-spend
visibility marker for the two attempts whose spend is not the provider's to
charge again: a deadline miss that completed nothing, and a manager-side
validation of a returned payload whose spend `llm_calls` already holds. Summing
only the rows that carry usage therefore counts every charged call exactly once.

`_InstrumentClient` captures the same burned call before re-raising, with the
spend and the wall its parse-failure metadata carries, so the partial accounting
a stop reports counts it too. That mirrors the client's existing rule for an
attempt the model-work window cut off in flight, and the work clock is charged
alongside it so `ArmUsage.model_work_seconds` and the run's own clock keep
describing the same seconds.

### Making the class reachable offline

Every existing double RETURNS an invalid payload, which is the manager-side case
whose spend `llm_calls` already holds — which is why the defect survived to a
live run. `tests/experiments/burned_call_double.py` is shaped like a real
provider instead: it bills for one ballot and raises the `ValidationError` with
an `LLMCallFailure` attached the way `llm/featherless_client.py` does, using
`llm.provider._attach_parse_failure` rather than a copy of the attribute name, so
the double cannot drift from the seam `extract_parse_failure` reads. A vote is
the sharpest seam: the ballot path has no retry, so one raise is one burned call
and one defaulted SKIP, and the unit still resolves.

It lives beside the test module because that module may not import `llm.provider`
at all — `TestLiveGate::test_this_test_module_neither_names_the_flag_nor_builds_a_client`
keeps the file free of any route to a real client. That gate now reads the double
as well and enumerates what it may take from `llm.provider`: the failure model
and the attach helper, nothing that builds a client. The double is not a decision
to relax the live gate; it is held to it.

### The manifest and the stop rule (`827d6628`)

"How each limit is enforced" said of the reconciliation "a difference is a stop".
`STOP_RULE` carries no such condition, so the run of 2026-09-10 was stopped by a
rule the frozen analysis never stated — the 2026-09-09 amendment (`bfd5696b`)
reached the rule and the default counter but not this comparison. The
token-budget bullet now quotes the new `SPEND_RECONCILIATION` constant verbatim,
which is the string the module itself states, so the code's account of the check
and the manifest's are one string and cannot drift again. It describes the check
as the token budget's accounting rather than a limit of its own: a unit whose
accounting does not add up stops the run through the same clause every other unit
failure does ("every way a unit can fail is one of these stops").

A dated section "Amendments after the stopped run of 2026-09-10" records the
change, its reason and `d8eb7d36`, kept apart from the pre-run amendments because
it is made after a unit ran. The frozen analysis does not move: `PRIMARY_OUTCOME`,
`DECISION_RULE`, `MINIMUM_ACTIONABLE_EFFECT_UNITS`,
`WRONGFUL_EJECTION_TRADEOFF` and `STOP_RULE` are byte-identical, which
`TestExecutionManifest::test_the_amendment_log_names_every_commit_that_moved_the_frozen_analysis`
checks by walking this branch's history rather than taking the claim.

`docs/artifacts.md`'s `audits/` row is recomputed for the moved manifest bytes:
204 files, 14,929,977 tracked bytes (`git ls-files audits/` with the change
staged).

### Planted failures

Each perturbation was applied to the tree at `827d6628`, run, and reverted.

1. The usage discriminator, dropped (`_charged_failed_attempts` returns every
   failed row for the meeting) —
   `TestChargedCallAccounting::test_only_the_rows_that_carry_usage_are_charged_calls`
   fails: `assert (...) == (captured, legacy_default)`, `At index 0 diff:` the
   zero-spend `deadline_default` marker.
2. The pre-fix sum (`_charged_failed_attempts` returns `()`) —
   `test_a_burned_call_is_reconciled_instead_of_stopping_the_run` reproduces the
   2026-09-10 stop:

   ```text
   InstrumentError: seed 3000 on arm repaired_clock: the recorded spend over 5
   resolved calls and 0 charged failed attempts (14855 in / 337 out / 0.0 USD)
   differs from the enforced budget (17083 in / 1198 out / 0.0 USD)
   ```

   The gap is 2,228 input and 861 output — the shape of the live stop, which the
   double plants deliberately.
3. The client-side capture, deleted (`_InstrumentClient` re-raises a charged
   parse failure without recording it) —
   `test_the_burned_calls_spend_reaches_the_partial_accounting` and
   `test_a_stop_after_a_burned_call_reports_that_spend` fail: the stopped arm
   reports `ArmUsage(calls=3, input_tokens=8866, output_tokens=219, ...)`,
   `assert 219 >= 861`.
4. A double count planted at the producer (`orchestrator/game.py`'s zero-spend
   marker written with `input_tokens=11`) —
   `test_a_returned_invalid_payload_is_charged_once` fails with the over-count
   detected: `the recorded spend over 6 resolved calls and 1 charged failed
   attempts (18008 in / 343 out ...) differs from the enforced budget (17997 in
   / 343 out ...)`.
5. The retired sentence, restored to the manifest's token-budget bullet —
   `TestExecutionManifest::test_the_enforcement_section_claims_no_stop_the_stop_rule_omits`
   fails on the missing `SPEND_RECONCILIATION` quotation.
6. The amendment's commit, replaced with `0000000` —
   `test_the_post_run_amendment_names_its_reason_and_a_real_commit` fails:
   `git rev-parse --verify 0000000^{commit}` returns 128.
7. The double, given a third `llm.provider` import (`build_default_client`) —
   `TestLiveGate::test_this_test_module_neither_names_the_flag_nor_builds_a_client`
   fails on the enumerated import set.

### Verification

Run on the tree at `827d6628` (the card and the task index are the only later
bytes, and no gate below reads them except `validate_task_docs.py`, re-run after
that edit).

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 234 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 390 phase tasks, 390 prompts, 45 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5` |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0: ruff clean over 504 files, import-linter 4 contracts kept / 0 broken, mypy clean over 475 source files, 7519 passed / 20 skipped / 3 xfailed, frontend 515 tests in 19 files |

No live provider call of any kind was made. `--complete` was not run on
`verify_ml_evidence.py`; its seven ABSENT rows are the archived ML evidence this
checkout does not carry.

### Limitations

The reconciliation is only as good as the producer's zero-spend convention. It
reads usage off the replay rows and trusts that the orchestrator writes a
charged attempt with its real spend and an already-counted one with none —
planted failure 4 is what turns a break in that convention red rather than into
a silent over-count. It also compares against the budget SNAPSHOT, so a provider
that burns tokens without reporting them in its parse-failure metadata is
invisible to both sides of the comparison and cannot be caught here.

The burned call now enters the unit's captured prompts, so the supported grader
sees the bytes of an attempt whose response was discarded. That is the honest
reading — the voter was handed those bytes — but it is a change in what
"the voter's own prompts" contains, and it is stated here rather than left to be
discovered: a defaulted ballot carries no citation, so no grade in the dry run
moves, and no live unit exists to compare against.

Item 4's dry run has not been run on the new band, so the aggregate counts this
card will record are not in it yet. The 100-unit dry run in the manifest's
"Verification of this manifest" section still describes the first band and is
left untouched for that reason; it is re-measured with the Inputs table in the
later round.
