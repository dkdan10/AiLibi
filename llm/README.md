# `llm/` — provider-neutral LLM client

This package owns the LLM call surface for AiLibi (`docs/architecture.md`
is the current-architecture note; DESIGN.md §4.4, §7, §10.4 is the
historical design record). Every call site in `agents/strategic/`,
`meetings/`, and `orchestrator/` consumes the `LLMClient` Protocol —
never a concrete adapter — so swapping providers is a new-file change.

Four adapters sit behind the Protocol today: `fake`, `anthropic`,
`ollama`, and `featherless`. **Featherless is the canonical eval
provider** — the committed sample replays under `replays/samples/` were
recorded through it.

## Modules

- `client.py` — the `LLMClient` Protocol, `LLMResponse`, `TokenUsage`,
  `CallKind`. The Protocol does not expose provider-specific concepts
  (extended thinking, `cache_control`, prompt-caching beta headers,
  message-shape internals). `agent_id` is the one piece of non-provider
  metadata on `complete`: call-attribution for the recording layer,
  never forwarded upstream.
- `provider.py` — `AnthropicClient`, the Anthropic adapter, plus
  `build_default_client()` (picks the active adapter and model defaults
  from environment variables) and the shared seams every real adapter
  reuses: JSON extraction + normalization, provider-keyed cost
  computation, and the `LLMCallFailure` / `extract_parse_failure` pair
  that turns a schema-validation crash into a recoverable failed-call
  audit row.
- `fake_provider.py` — `FakeProvider`, the deterministic in-process stub
  CI uses. Same prompt + schema always yields the same response shape;
  no network calls; `cost_usd` is always `0.0`; no recording or hashing
  of golden outputs.
- `ollama_client.py` — `OllamaClient`, the local-server adapter
  (`qwen3.5:9b` on `localhost:11434`, `$0` keyed by provider). Runs with
  thinking disabled and fails loud if a response carries thinking anyway.
- `featherless_client.py` — `FeatherlessClient`, the hosted
  OpenAI-compatible adapter (`Qwen/Qwen3.6-27B`, flat-rate subscription
  recorded as `$0`). Carries the `response_format_mode`,
  `request_thinking`, and `thinking_policy` knobs — all constructor-
  private, none on the Protocol.
- `report_normalize.py` — `normalize_report_payload`, the pure
  discriminator-aware repair applied to a near-miss model report before
  validation (misplaced-key stripping; reversed `from_tick`/`to_tick`
  swap). Lives in the shared extract→validate seam, so all three real
  adapters inherit it.
- `budget.py` — `GameBudget`, a per-game USD + token-count ceiling.
  Overruns raise `BudgetExceededError`; the budget never silently
  truncates.
- `budgeted_client.py` — `BudgetedLLMClient`, an `LLMClient` that wraps
  any other `LLMClient` plus a `GameBudget` and enforces preflight +
  charge around every call, safe under the meeting manager's concurrent
  `TaskGroup` calls. A free provider zeroes the USD preflight dimension
  through an optional rate hint; the token caps always stand.

## Runtime provider/model selection

The active provider is chosen from environment variables read at client
construction time (see `provider.build_default_client`):

| Variable | Purpose | Default |
| --- | --- | --- |
| `AILIBI_LLM_PROVIDER` | `"fake"` \| `"anthropic"` \| `"ollama"` \| `"featherless"` | `"fake"` |
| `AILIBI_LLM_MEETING_MODEL` | Meeting-strength model id (all providers) | per provider, below |
| `AILIBI_LLM_TRIGGER_MODEL` | Triggered-check model id (all providers) | per provider, below |
| `ANTHROPIC_API_KEY` | Required when provider is `"anthropic"` | unset |
| `AILIBI_OLLAMA_HOST` | Ollama server address | `localhost:11434` |
| `AILIBI_OLLAMA_SEED` | Per-game seed folded into `options.seed` | `0` |
| `AILIBI_OLLAMA_NUM_CTX` | Ollama context window (`num_ctx`) | `8192` |
| `FEATHERLESS_API_KEY` | Required when provider is `"featherless"` | unset |
| `AILIBI_FEATHERLESS_BASE_URL` | Featherless endpoint override | `https://api.featherless.ai/v1` |

An unset or empty required key is fail-loud, as is an unknown
`AILIBI_LLM_PROVIDER` value or a non-integer `AILIBI_OLLAMA_SEED` /
`AILIBI_OLLAMA_NUM_CTX` — no silent fallback to the fake.

Per-provider model defaults and cost:

| Provider | Meeting / trigger defaults | Cost |
| --- | --- | --- |
| `fake` | `fake-meeting` / `fake-trigger` | `$0` |
| `anthropic` | `claude-sonnet-4-6` / `claude-haiku-4-5-20251001` | metered from a private per-model table; an unpriced model raises (Task 19.6 removed the fallback rate) |
| `ollama` | `qwen3.5:9b` for both | `$0`, keyed by provider |
| `featherless` | `Qwen/Qwen3.6-27B` for both | `$0`, keyed by provider (flat-rate subscription) |

Featherless has been the **canonical eval provider since Phase 14**; its
model was **locked on 2026-07-12 at Task 16.2**
(`audits/audit-phase-16-model-lock.md`) to `Qwen/Qwen3.6-27B` in
non-thinking mode. `Qwen/Qwen3.6-27B` is the exact served id — the
`-Instruct` variant 404s. Anthropic is retained as a still-supported
alternative (baseline re-recording, cross-provider validation), not dead
code; Ollama is the Phase-7-era local provider it succeeded.

Both open-model providers run **non-thinking by default and fail loud
rather than silently recording reasoning**. Ollama sends the top-level
`think=False` on every call and raises if the response's `thinking`
channel is populated. Featherless defaults to `request_thinking=False`
(sent as `chat_template_kwargs={"enable_thinking": false}` only for model
ids explicitly classified as honoring it — an unclassified id fails loud
rather than being guessed at) and `thinking_policy="fail_loud"`, which
inspects both the dedicated reasoning channel and the raw content
*before* JSON extraction, so a `reasoning\n{JSON}` response cannot slip
through as an implicit strip. The `strip` policy exists for the Task-14.4
sweep harness and logs every discard.

## CI posture

CI must leave `AILIBI_LLM_PROVIDER` unset (or set to `"fake"`) so no test
reaches the network. The live round trips are all opt-in behind the
`real_provider` marker — a `skipif` keyed on
`AILIBI_RUN_REAL_PROVIDER_TESTS == "1"` (`tests/llm/test_client.py`):
that gate covers the Anthropic tests (need `ANTHROPIC_API_KEY`) **and**
the live Featherless smoke tests
(`tests/llm/test_real_provider.py::TestFeatherlessRoundTrip`, which
additionally skip themselves unless `FEATHERLESS_API_KEY` is set). The
live-server Ollama round-trip sits behind `ollama_server`, keyed on
`AILIBI_RUN_OLLAMA_TESTS == "1"`. CI sets none of these, so all report
as skipped. What runs *in* CI for Featherless is the mock-transport
unit suite: `FeatherlessClient` is unit-tested end to end against an
injected transport, so its request shape, retry mapping, thinking
policy, and cost mapping are pinned without an API key.

## Minimum surface a new adapter must implement

A new provider adapter (`OpenAIClient`, `DeepSeekClient`, another local
model wrapper, ...) is a new file — the same shape the Ollama and
Featherless adapters already took. The adapter must:

1. Implement the `LLMClient` Protocol — `async def complete(...) ->
   LLMResponse`. Type-checkers verify the surface; `isinstance(client,
   LLMClient)` works at runtime because the Protocol is
   `@runtime_checkable`.
2. Map the provider's native usage counters into `TokenUsage` and
   compute `cost_usd` from the provider's pricing table (provider-
   internal detail, never leaked through the Protocol). A flat-rate or
   free provider keys its rate by *provider*, not by model name, so an
   A/B model swap cannot route through another provider's table.
3. Translate the engine-free `schema: type[BaseModel] | None` argument
   into the provider's structured-output mechanism (JSON mode, schema-
   constrained sampling, tool-use, ...) and validate the returned
   string with `schema.model_validate_json(...)` before constructing
   `LLMResponse`. Routing the raw text through
   `provider._extract_json_block` first inherits the shared fence-
   stripping and report normalization for free.
4. Honor `call_kind` ("meeting" | "trigger") by routing to a sensible
   default model when the caller omits `model=`; let the caller
   override per-call with `model="..."`.
5. Accept `agent_id` and *not* send it upstream — it is replay-
   attribution metadata that `orchestrator.game._RecordingLLMClient`
   stamps onto the captured call record.

`build_default_client` is the only function that needs to learn the new
adapter's name. Call sites continue to depend on the Protocol type.

### Worked sketch: an OpenAI adapter

```python
# llm/openai_provider.py — illustrative, not shipped.
from pydantic import BaseModel
from llm.client import CallKind, LLMResponse, TokenUsage


class OpenAIClient:
    def __init__(
        self,
        *,
        api_key: str,
        meeting_model: str = "gpt-5",
        trigger_model: str = "gpt-5-mini",
    ) -> None:
        self._api_key = api_key
        self._meeting_model = meeting_model
        self._trigger_model = trigger_model

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
        agent_id: str | None = None,
    ) -> LLMResponse:
        # Call-attribution metadata for the replay layer, not a provider
        # knob — accepted and deliberately not forwarded.
        del agent_id
        chosen = model or (
            self._meeting_model if call_kind == "meeting" else self._trigger_model
        )
        raw = await _openai_sdk_call(
            api_key=self._api_key,
            model=chosen,
            prompt=prompt,
            schema=schema,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if schema is not None:
            schema.model_validate_json(raw.text)
        return LLMResponse(
            text=raw.text,
            usage=TokenUsage(
                input_tokens=raw.usage.input_tokens,
                output_tokens=raw.usage.output_tokens,
            ),
            cost_usd=_openai_pricing(raw.model, raw.usage),
            model=raw.model,
        )
```

Nothing about OpenAI's wire format leaks through the public surface —
`cost_usd` is computed inside the adapter, structured output goes
through the opaque `schema` knob, and the returned `LLMResponse` is
identical in shape to `AnthropicClient`'s, `OllamaClient`'s, and
`FeatherlessClient`'s. To activate the new adapter, extend
`build_default_client` with a `provider == "openai"` branch and set
`AILIBI_LLM_PROVIDER=openai`.

## Budget composition

The budget is a *layer* over an `LLMClient`: the wrapped client is
called and the budget is charged from the returned `LLMResponse`.

```python
client = build_default_client()           # FakeProvider by default
budget = GameBudget(max_cost_usd=0.30)

response = await client.complete(
    prompt=prompt,
    schema=ReportDocument,
    max_tokens=2048,
    temperature=0.7,
    call_kind="meeting",
)
budget.charge_response(response)
```

`BudgetedLLMClient` is the same composition wearing the Protocol, for
call sites that take one client and nothing else:

```python
client = BudgetedLLMClient(inner=build_default_client(), budget=budget)
response = await client.complete(
    prompt=prompt,
    schema=ReportDocument,
    max_tokens=2048,
    temperature=0.7,
    call_kind="meeting",
)
```

It pre-flights before the inner call, so a doomed request never spends a
turn waiting, and charges the provider-reported actuals afterward.

The `BudgetExceededError` raised by `budget.charge_response` (and by the
pre-flight inside `BudgetedLLMClient`) is a typed runtime error —
fail-loud, not silent truncation.
