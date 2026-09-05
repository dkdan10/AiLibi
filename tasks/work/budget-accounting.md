# Account for provider usage even when response validation fails

**Status:** done

## Outcome

The per-game budget records every reported token and dollar already spent,
including responses that fail schema validation. Later calls cannot reuse that
spent capacity. Actual spend remains visible when it exceeds an estimate or cap.

## Evidence

At review HEAD `cfde4c89`, `BudgetedLLMClient.complete` releases reservations
on exceptions without charging the usage carried by `LLMCallFailure`.
An offline Featherless transport returning `{}` with 80 input and 10 output
tokens against a required-field schema can repeatedly fail validation while
the budget remains zero. With input/output caps of 100/20, three such calls
consume 240/30 but all are admitted. `GameBudget.charge` also rejects already
incurred over-cap spend before recording it.

## Acceptance

- [x] A real adapter with an injected transport proves invalid output still
  charges its reported usage and subsequent calls stop at the budget boundary.
- [x] Valid incurred charges remain recorded when over cap; preflight remains
  nonmutating and rejects new calls that would exceed remaining capacity.
- [x] Failure metadata and the original validation error remain available to
  existing recovery and audit consumers; no duplicate charge occurs.
- [x] Concurrent calls and cancellation release reservations, and failures
  without reported usage do not fabricate charges.
- [x] Focused tests, the full project gate, and committed replay verification pass.

## Constraints

Use the workflow pilot policy. Preserve the `LLMClient` protocol and
`docs/architecture.md` layering, model prompts, engine rules, and replay schemas.
Inspect all consumers of `GameBudget.charge` before changing its semantics.
Real model calls, new dependencies, aborted-meeting capture retention, and replay
loader repairs are outside this task. Input-token estimates are admission
heuristics, not guarantees about a provider's tokenizer or final bill.

## Expected scope

`llm/budget.py`, `llm/budgeted_client.py`, `llm/provider.py` only if necessary,
`tests/llm/test_budget.py`, `tests/llm/test_budgeted_client.py`, and this card.

## Record impact

Post-record, unconditional accounting repair. Future live runs with provider validation
failures may hit caps earlier; already incurred over-cap spend becomes visible.
Successful within-budget runs, prompt bytes, and historical recording files
are unchanged. No canonical re-record or experiment adoption is performed.

## Validation

Run `uv run pytest tests/llm/test_budget.py tests/llm/test_budgeted_client.py`,
`bash scripts/check.sh`, and `bash scripts/verify_samples.sh`.
The failure regression must fail against the prior implementation and pass
after repair; all provider traffic in validation uses deterministic fakes or
injected transports.

## Results

Verified 2026-09-05: 55 focused budget tests passed; the full LLM suite passed
311 tests with 17 opt-in skips. `bash scripts/check.sh` passed 6,115 Python
tests (20 skips, 3 expected failures), 440 frontend tests, and all other gates.
`bash scripts/verify_samples.sh` verified all 100 samples it selects.

Five accounting regressions failed against isolated budget modules from
`cfde4c89`; the cancellation control passed. All six pass after repair.
The cases cover incurred overruns, invalid Featherless token usage, invalid
Anthropic dollar usage, concurrent failure settlement, and cancellation.

Independent review confirmed the charge consumers are confined to the wrapper
and the original validation exception and metadata reach recovery consumers.
Known spend is retained even over cap; estimates still cannot guarantee the
final provider bill. Aborted-meeting audit retention is the next separate
repair, so this card does not claim complete replay/live-ledger reconciliation.
