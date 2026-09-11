# Reconcile every paid call in the fresh-model deduction instrument

**Status:** done

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

- [x] Review correction: the post-run amendment log credits `STOP_RULE` with no
  stop it omits. The checkpoint refusal is attributed to the limit that grounds
  it — this manifest's own "Provider and model" row and the model the
  authorization card locks — rather than to the frozen rule, which enumerates no
  provider-identity stop; the pull request body carries the same correction. A
  gate holds the log to the rule the enforcement section is already held to,
  pointing the other way: every clause the section credits to `STOP_RULE` is one
  the rule states, the count it claims is the number it quotes, and provider
  identity stays absent from the frozen string.
- [x] Review correction: the two stops the client applies to a response — the
  output cap and the served checkpoint — also reach a call the provider billed
  and then refused on its own schema validation, read off that call's
  parse-failure metadata. Planted: a ballot burned at its 1,024-token cap stops
  the run instead of being fail-softed to a SKIP, and one served by a checkpoint
  this run does not authorize raises rather than reaching
  `InstrumentReport.model_ids`.
- [x] Review correction: a charge applied with no pre-flight left to refuse it
  stops the run. Both budgets are read back against their own caps after each
  unit, so the per-unit and run exhaustion `STOP_RULE` names is enforced for a
  burned call on a unit's last ballot, whose overrun `llm/budgeted_client.py`
  downgrades to a note. Planted at each dimension and end to end.
- [x] Review correction: the manifest's enforcement section states both, quoting
  the module's `BUDGET_CAP_READBACK` verbatim, and the post-run amendment
  section names this round's commit. Every Codex P1 thread on `ff575da8` is
  dispositioned in Results, the three valid ones by a fix and the fourth by a
  refutation that the delivery is not a squash.
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
- [x] The execution manifest's Inputs table binds the second held-out band
  frozen by [the second freeze card](held-out-prefix-freeze-2.md): the band,
  the accepted-seed range and skip count from the new
  `audits/deduction-candidate/held-out/manifest.json`, and a sentence stating
  that the 3000-3999 band is development data since 2026-09-10 and lives in
  `manifest-band-3000-3999.json`. Nothing else in the manifest's authorized
  values changes.
- [x] `assert_live_run_is_authorized` refuses a live run whose execution
  manifest does not bind the band `verify_frozen_set` would regenerate: the
  band the committed manifest's Inputs row names is read from the manifest text
  and compared against the record at
  `experiments.held_out_prefixes.MANIFEST_PATH`, so authorization written for
  one band cannot spend another. The gate raises `LiveRunNotAuthorized` before
  a client exists, and a planted stale binding — an Inputs row naming a band
  the live record does not hold — proves it. Raised as a P1 on PR #446, which
  could not close it: the freeze card may not edit this file.
- [x] The fake-provider dry run of the full pipeline completes at $0 on the new
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

**Every acceptance item is closed.** The card was delivered in rounds because
three of its items needed a held-out band that did not exist yet: rounds 1 and 2
below carry the reconciliation, the stops a charged failure has to meet and the
record corrections, and each of them ends by saying which items were still open
and why. [The second freeze](held-out-prefix-freeze-2.md) merged into this
branch in the stacking round of 2026-09-10, the last section below, which
re-bound the Inputs table, closed the runtime gate that freeze's review routed
here, and ran the dry run on the new band.

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

*(As written in this round, this paragraph said item 4's dry run had not been
run on the new band and that the manifest's "Verification of this manifest"
section still described the first one. Both were closed in the stacking round
below, whose aggregates and re-measurement supersede it.)*

What no dry run can limit is what a dry run says. The fake provider chooses the
same target in both arms, so the paired result is `b=0, c=0, p=1.0` by
construction on either band; the run establishes that the pipeline carries a
decision through to a graded outcome, and nothing about judgment.

### Review corrections, round 1 (2026-09-10)

Three of the four Codex P1 threads on `ff575da8` name three sides of one
omission, and review found it independently: the round above made a
billed-and-refused call COUNTABLE without making it JUDGEABLE. The accounting
stop it retired had been standing in for three real ones, and nothing replaced
them. `6215fda1` puts all three on that path.

**The two stops a completion has to meet, whatever its body did.** The client's
truncation stop and its provider-identity refusal read a response. A call the
provider billed and then refused on its own schema validation was captured and
re-raised without either, and the meeting layer fail-softs the `ValidationError`
to a SKIP — so the usual CAUSE of a schema-invalid body, a completion cut off at
the output cap, was exactly the case that walked past "a truncation is a stop,
not a datum", and a hosted endpoint serving an unauthorized checkpoint reached
`InstrumentReport.model_ids` instead of stopping the run. Both stops now read the
`output_tokens` and `model` the parse-failure metadata carries, through one
`_InstrumentClient._unusable_response` the success path calls too, so the two
paths cannot enforce different lists again. The client's docstring claim about
job 3 — which the review noted had become false — is true again as written.

**The budget's missing arrival.** `llm/budget.py::GameBudget.charge` applies a
charge before reporting an overrun, and `llm/budgeted_client.py:331-349`
downgrades that overrun to `exc.add_note` on the parse failure, which the meeting
layer then fail-softs. Every other call meets a pre-flight, so an overrun is
found on the call that would cross the cap; a burned call meets none. On a unit's
LAST call the unit budget is then discarded and nothing ever finds it, and at the
run level the next unit's first pre-flight finds it one unit late — or never, on
the run's last call. `_assert_charged_spend_is_within_caps` reads both budgets
back against their own caps after each unit, raising the new `BudgetExhausted`;
`BUDGET_CAP_READBACK` is the module's statement of it and the manifest quotes it
verbatim. No stop condition is added: `STOP_RULE`'s "a token budget exhausted at
either the per-unit or the run level" is the clause this enforces, and
`STOP_RULE` is byte-identical.

**One consequence, stated rather than left to be found.** Raising a stop in place
of the provider's `ValidationError` means `BudgetedLLMClient` no longer charges
that call: it reads the burned spend off the parse-failure metadata, and the
metadata rides the exception this client replaced. The tokens are not lost from
the record — the call was appended to the client's own ledger first, which is
what `PartialRun.usage_by_arm` is built from, and the truncation case asserts
the stopped arm carries it — but on those two stops the budget snapshot
under-counts by that call. It is a snapshot of a run that is over, and the
alternative (re-attaching the metadata to the stop) would mean copying a private
attribute of `llm.provider` into this module.

**What the reviewed head did, probe by probe.** Each case is a
`BurnedCallProvider` through `run_instrument(units=1)` on the fake provider, at
`$0.00`, into a temporary directory — the same double the committed tests use.
The middle column restores `git show ff575da8:experiments/fresh_deduction_instrument.py`
over the module and runs the identical probe.

| Probe | At `ff575da8` | At `6215fda1` |
| --- | --- | --- |
| A ballot burned at its 1,024-token output cap | completes: units [1, 1], arm output 1,361 | `PerCallCapExceeded: a response reached its 1024-token output cap (1024 tokens); a truncation is a stop, not a datum` |
| 45,000 input burned on the unit's LAST ballot | completes: units [1, 1], arm input 59,519 against a 45,000 per-unit cap | `BudgetExhausted: seed 3000 on arm repaired_clock: the per-unit token budget is exhausted on input tokens (59519 charged against a 45000 cap)` |
| 20,000 input burned on the LAST ballot, run cap 30,000 | stops one unit late, on the NEXT pre-flight: `current=34519.0 + delta=2088.0 > cap=30000.0` | stops on the unit that crossed it: `the run token budget is exhausted on input tokens (34519 charged against a 30000 cap)` |

The identity case has no `run_instrument` probe by construction: `expected_model`
is bound only by a live invocation, which this card may not make, so it is
planted at the client seam instead. From the committed tree the right-hand
column is
`uv run pytest tests/experiments/test_fresh_deduction_instrument.py -q -k "TestBurnedCallStopConditions or TestChargedSpendAgainstCaps"`
— 12 passed; the probes are those same cases with the stop printed rather than
asserted.

**Planted failures.** Each perturbation was applied to the tree at `6215fda1`,
run, and reverted.

1. The burned-path stops, deleted (the `except BaseException` branch re-raises
   without calling `_unusable_response`) — all three stop cases in
   `TestBurnedCallStopConditions` fail: the two at the client seam on the
   provider's own `pydantic_core._pydantic_core.ValidationError: 6 validation
   errors for ModelAuthoredVoteBallot` arriving where a stop was expected, and
   the end-to-end truncation on
   `Failed: DID NOT RAISE <class 'experiments.fresh_deduction_instrument.InstrumentAborted'>`.
   The fourth case — one token under the cap — stays green, which is what says
   the gate is the cap and not the refusal.
2. The identity half alone, disabled (`_unusable_response`'s `_expected_model`
   comparison made unreachable) — only
   `test_a_burned_call_from_another_checkpoint_stops_the_run` fails, and the
   truncation cases stay green: the two are separate gates, not one.
3. The read-back, returned from early — six of the eight cases in
   `TestChargedSpendAgainstCaps` fail: four on
   `Failed: DID NOT RAISE <class 'experiments.fresh_deduction_instrument.BudgetExhausted'>`
   (three dimensions and the run-level parent, at the seam), one on
   `DID NOT RAISE ... InstrumentAborted` (the burned last ballot end to end), and
   the run-level end-to-end case on the pre-flight message quoted in 4 below. The
   two that stay green are the boundary cases: a budget charged exactly to its
   cap, and a USD total inside the budget's own slack.
4. The RUN-level call site alone, deleted from `run_unit` —
   `test_an_overrun_that_only_the_run_budget_can_see_stops_the_run` fails:
   `assert 'the run token budget is exhausted on input tokens' in 'BudgetExceededError: LLM budget exceeded on input_tokens: current=34519.0 + delta=2088.0 > cap=30000.0'`.
   That is the leak's exact shape at the run level — the next unit's pre-flight,
   one unit late — and it is why the two call sites are both planted.
5. The manifest's read-back quotation, removed —
   `TestExecutionManifest::test_the_enforcement_section_quotes_the_budget_read_back`
   fails on the missing `BUDGET_CAP_READBACK` string.
6. The manifest's two refusal sentences, removed —
   `test_the_enforcement_section_applies_both_response_stops_to_a_refusal` fails.
7. This round's amendment commit, replaced with `0000000` —
   `test_the_post_run_amendments_name_their_reason_and_a_real_commit` fails:
   `AssertionError: 0000000 is not a commit here`.
8. The same entry, given a real commit that is NOT an ancestor of this branch
   (`884257b8`, the stopped run's branch tip) —
   `test_every_named_post_run_commit_is_in_this_branchs_history` fails:
   `assert ['884257b8'] == []`. That check is new this round, and item 4 of the
   dispositions below is why.

**Codex dispositions.** All four P1 threads on `ff575da8`, none of which had a
reply.

1. `experiments/fresh_deduction_instrument.py:1167` — "Stop on capped outputs
   even when schema validation fails". VALID, fixed. Probe A above.
2. `:1168` — "Reject the wrong model on failed structured responses". VALID,
   fixed. `test_a_burned_call_from_another_checkpoint_stops_the_run`.
3. `:2066` — "Preserve the budget stop for charged validation failures". VALID,
   fixed. Probes B and C above; the comment's "especially in the final unit"
   reading is right at the run level and understates the per-unit one, where the
   budget is discarded after every unit and the leak needs no final unit at all.
4. `audits/deduction-candidate/execution-manifest.md:101` — "Keep the cited
   implementation commit in this history". REFUTED on its premise, and a gate
   added anyway. The premise is that this delivery is "a squash directly onto
   `c12ec85`", which would orphan `d8eb7d36`. It is not: AGENTS.md's delivery
   rule is a merge commit or fast-forward and never a squash, and `d8eb7d36` is
   an ancestor of both `ff575da8` and this round's head —
   `git merge-base --is-ancestor d8eb7d36 HEAD` exits 0, and
   `git log --oneline c12ec85a..HEAD` lists it. The `27f264b` the comment
   resolves against is not a commit on this branch. The reviewer's underlying
   point about the CHECK was fair, though — the committed test asked only whether
   the object existed locally — so ancestry from `HEAD` is now asserted directly
   (planted failure 8).

**Verification, round 1.** Run on the tree at this round's second commit; this
card's own bytes are the only later ones, and no gate below reads it except
`validate_task_docs.py`, re-run after that edit.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 249 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 390 phase tasks, 390 prompts, 45 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5` |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0: ruff clean over 504 files, import-linter 4 contracts kept / 0 broken, mypy clean over 475 source files, 7534 passed / 20 skipped / 3 xfailed, frontend 515 tests in 19 files |

No live provider call of any kind was made, and `--complete` was not run on
`verify_ml_evidence.py`. An earlier run of `bash scripts/check.sh` on these same
bytes exited 1 on
`tests/orchestrator/test_run_limits.py::test_wall_deadline_cancels_meeting_and_retains_success`
(`assert 0 == 2`) while eight suites shared this machine and the run took 18m48s
rather than 3m52s: that test builds a `RunDeadline(0.25)` and the window closed
before its provider was reached. It passes on its own and in the clean run above,
and it reads no byte this card moves.

**Still open.** Acceptance items 3 and 4 are untouched by this round and the
card stays `active` for the same reason as above: the second freeze has not
merged into this branch, so there is no new band to bind or to run.

### Review corrections, round 2 (2026-09-10)

One blocking finding, and it is valid: the round-1 amendment entry was refuted
by its own quotation of the rule it quotes.

**The claim and what the rule says.** The entry for `6215fda1` opened "Three
stops `STOP_RULE` carries were reachable only on the success path" and closed
"each of these three is a clause it already carried". Two of the three are
quoted from the rule verbatim — "a truncation is a stop, not a datum" and "a
token budget exhausted at either the per-unit or the run level". The third, a
checkpoint this run does not authorize, is not in `STOP_RULE` at all, which is
why it was the only member with no quotation. On the committed tree at
`70a5c826`:

```console
$ .venv/bin/python -c "from experiments.fresh_deduction_instrument import STOP_RULE
s = STOP_RULE.lower()
print({w: w in s for w in ('checkpoint','identity','provider','endpoint','served','model')})"
{'checkpoint': False, 'identity': False, 'provider': False, 'endpoint': False,
 'served': False, 'model': True}
```

and the one `model` is "the model-work window". The frozen string has not moved
— the byte-identity walk
(`test_the_amendment_log_names_every_commit_that_moved_the_frozen_analysis`) is
green on this branch — so the document was wrong about a constant it carries in
full.

**What it is instead.** The refusal is the manifest's own limit, not a
borrowed one. The "Provider and model" row of the authorized values binds
`featherless` / `Qwen/Qwen3.6-27B` from the authorization card, and its
enforcement bullet has said since before the first run (`c12ec85a:195-202`)
that `_InstrumentClient` refuses a response whose `model` is not the authorized
one. `6215fda1` extended that refusal to a completion the provider billed for
and then refused, off the `model` its parse-failure metadata carries. The entry
now attributes it there, keeps the two frozen clauses quoted, and records that
its own attribution was corrected. Nothing else in the entry changes, and
`STOP_RULE` is untouched: adding a provider-identity clause to it would move the
frozen analysis, which is the owner's to do and not this card's.

**The code was right; the record was not.** The finding says so, and this round
changed no line of `experiments/fresh_deduction_instrument.py`. The identity
half of `_unusable_response` stays load-bearing: round-1's planted failure 2,
re-run on this round's tree with the `_expected_model` comparison made
unreachable, turns exactly two of the module's 175 cases red —
`TestBurnedCallStopConditions::test_a_burned_call_from_another_checkpoint_stops_the_run`
and `TestAuthorizedClient::test_a_response_from_another_model_stops_the_run`,
`2 failed, 173 passed` — with every truncation case green.

**The gate.** This round retired "a difference is a stop" from the enforcement
section and gated that direction; the same round then credited the frozen rule
with a stop it omits, and nothing watched that direction.
`TestExecutionManifest::test_the_post_run_amendments_credit_no_clause_the_stop_rule_omits`
now does: every phrase the post-run log quotes is a clause of `STOP_RULE`, a
heading or bullet of this document, or one the section says in so many words
that the rule does not carry; the count it credits to the rule equals the number
of clauses it quotes; and provider identity stays absent from the frozen string.

**Planted failures.** Each perturbation was applied to the tree at `75eeb6e3`,
run, and reverted.

1. The retired count, restored ("Two stops `STOP_RULE` carries" → "Three") —
   `test_the_post_run_amendments_credit_no_clause_the_stop_rule_omits` fails:
   `assert {3} == {2}`. That is the finding's defect exactly: a claim of three
   clauses against two quotations.
2. The checkpoint refusal, quoted as if it were a clause ("a checkpoint this run
   does not authorize" put in quotation marks in the same entry) — the same test
   fails:
   `AssertionError: quoted as the frozen rule's, but it does not state it: 'a checkpoint this run does not authorize'`.
   The two plants cover both ways the document can credit the rule with a stop
   it omits — by counting and by quoting.
3. The rule itself, given the clause (a `; a response served by a checkpoint
   this run does not authorize` inserted into `STOP_RULE`) — the same test fails
   `the frozen rule now names provider identity: ['checkpoint', 'served']`. That
   perturbation also reddens the frozen-analysis quotation and byte-identity
   gates, which is the point: it is the owner's amendment, not a document edit.

**Verification, round 2.** Run on the tree at `75eeb6e3`; this card's own bytes
are the only later ones, and no gate below reads it except
`validate_task_docs.py`, re-run after that edit.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 250 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 390 phase tasks, 390 prompts, 45 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5` |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0: ruff clean over 504 files, import-linter 4 contracts kept / 0 broken, mypy clean over 475 source files, 7535 passed / 20 skipped / 3 xfailed, frontend 515 tests in 19 files |

`docs/artifacts.md`'s `audits/` row is recomputed for the moved manifest bytes:
204 files, 14,933,995 tracked bytes (`git ls-files audits/` summed on disk, with
the change staged). No live provider call of any kind was made, and `--complete`
was not run on `verify_ml_evidence.py`.

**Still open.** Acceptance items 3 and 4 are untouched by this round as well.
The card stays `active` for the reason it has stayed active throughout: the
second freeze has not merged into this branch, so there is no new band to bind
or to run.

### Stacking and re-binding (2026-09-10)

The round the card was held open for. [The second freeze](held-out-prefix-freeze-2.md)
is verified at `f9ab0024` on `work/held-out-prefix-freeze-2` (PR #446), so it is
merged in here — `git merge --no-ff`, never a rebase — and acceptance items 3, 4
and the gate that freeze's own review routed to this card are closed on it.

**The merge (`f3b700a6`).** Two conflicts, both resolved by recomputing rather
than by choosing a side: `docs/artifacts.md`'s `audits/` row, re-summed over the
merged tree, and `tasks/README.md`'s derived card-inventory sentence, re-derived
from the merged set of cards. The held-out manifests came from the freeze side
untouched. Two tests of this card's own named the first band's first seed in a
replay filename and went red on the merge; they read `_first_accepted_seed()`
now, which is the helper the freeze side added for exactly that.

**The defect the re-binding closes, reproduced.** `verify_frozen_set` regenerates
whatever record sits at `MANIFEST_PATH` and holds it to the generator's
`PREREGISTERED_BAND`. Neither reads the execution manifest, and the live gate
checked that document's path and digest but not the inputs it names — so on the
merge commit the manifest authorized 3000-3999 while the run would have drawn
5000-5999, with every gate green. On the tree at `ee37cb06` with the Inputs row
put back to the first band:

```text
LiveRunNotAuthorized: audits/deduction-candidate/execution-manifest.md binds
seed band 3000-3999, but the held-out record at
audits/deduction-candidate/held-out/manifest.json holds 5000-5999: the
authorization was written for one band and this run would spend another
```

**What moved (`08aee9cc`, `f77b524d`).** The Inputs table binds 5000–5999,
accepted seeds 5000–5052, 3 `witnessed_kill` skips, each number read off
`audits/deduction-candidate/held-out/manifest.json`, and says that the first band
is development data since 2026-09-10 and where its record now lives. The Roles
table names the second preparer session beside the first.
`assert_manifest_binds_the_live_band` reads the band out of the Inputs row and
refuses a live run whose freeze record holds another; it runs inside
`assert_live_run_is_authorized`, the first call `assert_ready_for_a_live_run`
makes, so the refusal lands before a provider, a credential or a connection
exists, and a dry run returns before it. `manifest_bound_band` is the single
reader of that row — the gate and the binding test both use it, so the document
and the check cannot reach different conclusions, and a document with no such row
or two of them is refused rather than resolved by taking the first. The post-run
amendment log gains its third entry, and the manifest's
"Verification of this manifest" section is re-measured on the new band with the
first band's figures named as superseded rather than quietly replaced.

`ee37cb06` is a repair to this round's own first commit: the new test class had
been inserted above three `TestAuthorizedClient` cases, which were then collected
under it. Every case still ran and still passed — which is why it would have gone
unnoticed — but they belong to the class whose docstring describes them.

**The dry runs (item 4).** Both on the tree at `08aee9cc`, fake provider, `$0.00`,
into a temporary directory; no prefix was printed, opened or written anywhere but
there, and the aggregates are all that is recorded.

| Run | Units | Calls | Cost | Per-arm outcome |
| --- | --- | --- | --- | --- |
| `--dry-run` | 100 (50 × 2) | 600 | `0.0` | 49 ejections, 22 role-correct, 27 wrongful, 22 supported-correct, 150 supported ballots, 4 guard-rewritten, 98 naming ballots, 0 off-target citations, 1 partial unit |
| `run_instrument` with `BurnedCallProvider` | 100 (50 × 2) | 600 | `0.0` | as above, plus one defaulted vote and one unit with defaults on `repaired_clock` |

The double burns the run's first ballot, so it is in the loop for the first unit
of the reference arm: that arm's output tokens rise by the 861 the burned call
carried (19,800 → 20,602) and its input falls by the one prompt that was never
re-sent, and the unit still resolves to the same graded outcome. Both runs report
`held_out_accepted_seeds` 50 and `held_out_skipped_seeds` 3, which is the new
record. The paired result is `b=0, c=0, p=1.0` in both, by construction.

**Planted failures.** Each perturbation was applied to the tree at `ee37cb06`,
run, and reverted.

1. The gate's call site, deleted from `assert_live_run_is_authorized` —
   `test_a_stale_binding_stops_the_run_before_a_client_exists` fails:
   `Failed: DID NOT RAISE <class 'experiments.fresh_deduction_instrument.LiveRunNotAuthorized'>`.
   One case, and only that one, which is what says the gate is the call and not
   something else on the path.
2. The row anchor, dropped (`manifest_bound_band` reads a bare pair of numbers
   anywhere in the document) — 9 cases fail, on
   `LiveRunNotAuthorized: ... carries 46 'Seed band' rows naming a band`. The
   document names many ranges in prose, including the band it supersedes; without
   the anchor the reader cannot say which one is bound.
3. The Inputs row, put back to the first band —
   `test_the_committed_manifest_binds_the_live_band` and
   `TestAuthorizedClient::test_the_pre_client_gate_returns_the_verified_set` fail
   on the refusal quoted above, and
   `test_the_manifest_binds_a_committed_held_out_record` on
   `assert 'accepted seeds run 3000–3057' in ...`. That is the state the merge
   commit was in, turned red.
4. The new amendment entry's commit, replaced with `0000000` —
   `test_the_post_run_amendments_name_their_reason_and_a_real_commit` fails:
   `AssertionError: 0000000 is not a commit here`.
5. The same entry, given a real commit that is not an ancestor of this branch
   (`884257b8`, the stopped run's branch tip) —
   `test_every_named_post_run_commit_is_in_this_branchs_history` fails:
   `named but not an ancestor of HEAD: ['884257b8']`.

**Verification, stacking round.** The first five commands were run on the tree at
`ee37cb06` and re-run after this card and `tasks/README.md` moved; `check.sh` was
run on `6a0f0dfd`, which carries those bytes.

| Command | Result |
| --- | --- |
| `.venv/bin/python -m pytest tests/experiments -q` | 260 passed |
| `.venv/bin/python scripts/validate_task_docs.py` | passed; 390 phase tasks, 390 prompts, 45 work cards |
| `.venv/bin/python scripts/check_doc_facts.py` | doc facts, front door, ml-program and budgets all verified |
| `.venv/bin/python scripts/verify_ml_evidence.py` | `checks: 60 \| OK 48 \| FAIL 0 \| ABSENT 7 \| INFO 5` |
| `.venv/bin/python -m pytest tests/scripts/test_verify_ml_evidence.py -q` | 80 passed |
| `bash scripts/check.sh` | exit 0: ruff clean over 504 files, import-linter 4 contracts kept / 0 broken, mypy clean over 475 source files, 7545 passed / 20 skipped / 3 xfailed, frontend 515 tests in 19 files |

An earlier invocation of `bash scripts/check.sh` on these same bytes exited 127
on `sh: eslint: command not found`: this worktree had no `frontend/node_modules`
yet. `npm ci` in `frontend/` installs nothing the Python gates read, and the run
above is after it.

`docs/artifacts.md`'s `audits/` row is recomputed once per commit that moved
`audits/` bytes: 205 files and 14,948,022 tracked bytes at `08aee9cc`, 14,950,280
at `f77b524d`, and 14,950,292 on the last commit of this round, which spells the
first band's numbers into the Inputs row (`git ls-files audits/` summed on disk,
with the change staged). No live provider call of any kind was made, and
`--complete` was not run on `verify_ml_evidence.py`.
