# Account for provider usage even when response validation fails

**Status:** active

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

- [ ] A real adapter with an injected transport proves invalid output still
  charges its reported usage and subsequent calls stop at the budget boundary.
- [ ] Valid incurred charges remain recorded when over cap; preflight remains
  nonmutating and rejects new calls that would exceed remaining capacity.
- [ ] Failure metadata and the original validation error remain available to
  existing recovery and audit consumers; no duplicate charge occurs.
- [ ] Concurrent calls and cancellation release reservations, and failures
  without reported usage do not fabricate charges.
- [ ] Focused tests, the full project gate, and committed replay verification pass.

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

Unconditional accounting repair. Future live runs with provider validation
failures may hit caps earlier; already incurred over-cap spend becomes visible.
Successful within-budget runs, prompt bytes, and historical recording files
are unchanged. No canonical re-record or experiment adoption is performed.

## Validation

Run `uv run pytest tests/llm/test_budget.py tests/llm/test_budgeted_client.py`,
`bash scripts/check.sh`, and `bash scripts/verify_samples.sh`.
The failure regression must fail against the prior implementation and pass
after repair; all provider traffic in validation uses deterministic fakes or
injected transports.
