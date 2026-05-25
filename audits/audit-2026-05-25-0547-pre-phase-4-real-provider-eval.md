# AiLibi Pre-Phase-4 Real-Provider Eval — Report

- **Date:** 2026-05-25 05:47 local
- **HEAD:** `b9d3300317cc8ad442d54bfdbd95c095d8822273` on `main`
- **Prompt:** [audits/prompts/pre-phase-4-real-provider-eval-prompt.md](prompts/pre-phase-4-real-provider-eval-prompt.md)
- **Preceding stages:**
  - Verification: [audit-2026-05-25-0345-pre-phase-4-verification.md](audit-2026-05-25-0345-pre-phase-4-verification.md)
  - Static audit (reconciled): [audit-2026-05-25-0414-reconciled.md](audit-2026-05-25-0414-reconciled.md) — verdict *Ready with fixes* (R-1, R-2)
  - R-1 + R-2 closed by commit `ec023be` (Task 3.13) merged in PR #49 (`b9d3300`)
- **Total live API spend this eval:** **$0.00** — no live call succeeded.

---

## 1. Verdict

**Pre-flight failed — eval not run. Live provider unreachable.**

The 50-game tournament was not started. The 3-game smoke was not started.
Both were gated on a direct sanity call to the live provider, and the
sanity call failed because no real Anthropic SDK transport is wired into
[llm/provider.py](../llm/provider.py).

This is a code/dependency gap, not an operator error. It is not
remediable from inside this audit prompt (the prompt forbids edits to
source files). It must be closed by a follow-up implementation task
before the real-provider eval can be re-attempted.

---

## 2. Environment

| Item | Value |
|---|---|
| Provider env var | `AILIBI_LLM_PROVIDER=anthropic` |
| Meeting model env var | `AILIBI_LLM_MEETING_MODEL=claude-sonnet-4-6` |
| Trigger model env var | `AILIBI_LLM_TRIGGER_MODEL=claude-haiku-4-5-20251001` |
| API key prefix (8 chars only) | `sk-ant-a` |
| API key length | 108 |
| `.env` source | repo-root `.env` (sourced via `set -a; source .env; set +a` because the project does not auto-load it — `grep -rn dotenv llm/ scripts/ pyproject.toml` returns no hits except a docstring reference) |
| Pre-flight smoke (3-game) | **Not run.** Gated on sanity call. |
| 50-game tournament | **Not run.** Gated on sanity call + smoke. |

Static gates re-run at HEAD `b9d3300`:

```
$ bash scripts/check.sh
All checks passed!
Contracts: 1 kept, 0 broken.
Task docs validation passed: 64 tasks and 64 prompts.
667 passed, 1 skipped in 4.43s
```

(One additional task vs. the reconciled audit's 63/63 is the
post-3.13 Task 3.14 cleanup task added by commit `59d29cd`.)

### Direct sanity-call invocation (exact command)

```bash
set -a && source .env && set +a && uv run python -c "
import asyncio
from llm.provider import build_default_client

async def main():
    client = build_default_client()
    resp = await client.complete(
        prompt='Respond with the single token: OK',
        schema=None,
        max_tokens=8,
        temperature=0.0,
    )
    print(f'model={resp.model} cost_usd={resp.cost_usd:.6f} text={resp.text!r}')

asyncio.run(main())
"
```

### Outcome

```
RuntimeError: AnthropicClient was constructed without a `send` hook and
the real Anthropic SDK is not wired in this build; pass `send=` for
tests or configure a real transport before invoking complete()
```

Exit code: `1`. `cost_usd` was never assigned. Provider class
construction succeeded (correctly routed to `AnthropicClient` because
`AILIBI_LLM_PROVIDER=anthropic` and `ANTHROPIC_API_KEY` was non-empty);
the call surface itself has no transport.

---

## 3. Tournament outcome

Not applicable. No tournament was executed.

---

## 4. Cost analysis

Not applicable. No live API calls were charged. Total spend for this
eval session is **$0.00**.

---

## 5. Win-rate analysis

Not applicable.

---

## 6. Leak scan result

Not applicable.

---

## 7. Replay record completeness

Not applicable.

---

## 8. Transcript readability

Not applicable.

---

## 9. Observations

The static / fake-provider audit substrate is healthy — Task 3.13's
production wire-up (commit `ec023be`) does close R-1 and R-2 *for the
FakeProvider path*: [scripts/run_game.py:77](../scripts/run_game.py#L77)
and [eval/balance_eval.py:147](../eval/balance_eval.py#L147) both
construct a `meeting_runner` + a fresh `GameBudget` per game, and the
667-test suite is green. The unreachability of the real provider is
not a regression introduced by Task 3.13; it predates that task and
was simply unobserved because no prior stage exercised
`build_default_client()` against a real key. Two distinct gaps
compound to produce the failure (described in §10 so the follow-up
task author can scope cleanly). The reconciled audit at 04:14 framed
the real-provider eval as out-of-scope and did not look at
`_default_send`; that omission is now visible. The reconciled audit's
remediation framing for cost overrun ("Haiku fallback for triggered
checks") and unreadable transcripts ("prompt-template rework") cannot
even be evaluated until live calls run, so neither concern is open
nor closed — they remain *pending evidence*.

---

## 10. Verdict justification

The §1 verdict — **Pre-flight failed — eval not run** — follows
directly from the §6 verdict rules in the prompt: "If any pre-flight
check fails, stop and report." The required sanity-call outcomes from
§2 of the prompt are: (a) command exits 0, (b) `cost_usd` non-zero,
(c) `text` a sensible response, (d) model id matches. Outcome (a)
failed with `RuntimeError`; outcomes (b)–(d) are unreachable. The
prompt mandates: "If the sanity call fails, stop and report. Verdict:
Pre-flight failed — live provider unreachable. Do not run the smoke
or the 50-game eval." That is the action this report records.

Two compounding gaps explain the failure; both must close before the
eval can be re-attempted.

**Gap A — production CLI/tournament path ignores
`AILIBI_LLM_PROVIDER`.** [scripts/run_game.py:77](../scripts/run_game.py#L77)
and [eval/balance_eval.py:147](../eval/balance_eval.py#L147) call
`build_default_meeting_runner(budget=GameBudget())` with no
`llm_client=` argument.
[orchestrator/game.py:342](../orchestrator/game.py#L342) then
unconditionally falls back to `FakeProvider()`. Setting
`AILIBI_LLM_PROVIDER=anthropic` in `.env` has no effect on the public
entry-points. The docstring at
[orchestrator/game.py:326-329](../orchestrator/game.py#L326)
acknowledges this: "explicit local / eval runs pass an
:class:`llm.provider.AnthropicClient`" — but no caller does so today.

**Gap B — `AnthropicClient` has no real transport.**
[llm/provider.py:207-221](../llm/provider.py#L207) `_default_send` is
a one-line `raise RuntimeError(...)`. The module docstring at
[llm/provider.py:9-11](../llm/provider.py#L9) describes a *plan*
("the adapter does the import lazily inside `complete`") but the
plan is not implemented — there is no `import anthropic` anywhere
in the source tree (`grep -rn 'import anthropic\|from anthropic'
--include='*.py' .` returns zero hits outside `.venv`). The
`anthropic` package is not declared in `pyproject.toml`
`dependencies` (the list is `fastapi`, `hypothesis`, `import-linter`,
`jinja2`, `mypy`, `pydantic`, `pytest`, `pyyaml`, `ruff`,
`uvicorn`). Even if Gap A is fixed and a caller threads
`build_default_client()` into `build_default_meeting_runner`, the
very first `complete()` call against the live provider raises.

**Recommended follow-up task scope** (informational; out of this
prompt's edit scope):

1. Add `anthropic` to `pyproject.toml` `dependencies` (pin a
   specific version per project convention).
2. Implement the real `_default_send` in
   [llm/provider.py](../llm/provider.py) — lazy `import anthropic`
   inside the function, construct an `AsyncAnthropic` client with
   `api_key`, call `messages.create(...)`, translate the response
   into `AnthropicRawResponse`. Mind: extended-thinking +
   prompt-caching-beta knobs are already plumbed through the
   call signature but are no-ops until the SDK call uses them.
3. In [scripts/run_game.py](../scripts/run_game.py) and
   [eval/balance_eval.py](../eval/balance_eval.py), pass
   `llm_client=build_default_client()` into
   `build_default_meeting_runner(...)` so the env-driven selector
   actually flows through.
4. Add one `pytest.mark.real_provider` round-trip test that the
   developer can opt into with `--real-provider`, mirroring the
   sanity call here. (CI continues to skip it by default per
   [llm/README.md](../llm/README.md).)
5. Re-run this prompt. If the sanity call passes and the 3-game
   smoke completes, the 50-game eval may proceed.

---

## Final summary lines (per prompt §5 closing requirements)

- **Report path:** `/Users/danielkeinan/projects/AiLibi/audits/audit-2026-05-25-0547-pre-phase-4-real-provider-eval.md`
- **Verdict:** Pre-flight failed — live provider unreachable. Eval not run.
- **Per-game mean cost:** n/a (no games run)
- **Decisive split:** n/a (no games run)
- **Total API spend for this eval:** $0.00
