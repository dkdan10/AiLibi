# `llm/` — provider-neutral LLM client

This package owns the LLM call surface for AiLibi (DESIGN.md §4.4, §7,
§10.4). Every call site in `agents/strategic/`, `meetings/`, and
`orchestrator/` consumes the `LLMClient` Protocol — never a concrete
adapter — so swapping providers is a new-file change.

## Modules

- `client.py` — the `LLMClient` Protocol, `LLMResponse`, `TokenUsage`,
  `CallKind`. The Protocol does not expose provider-specific concepts
  (extended thinking, `cache_control`, prompt-caching beta headers,
  message-shape internals).
- `provider.py` — `AnthropicClient`, the real adapter, plus
  `build_default_client()` which picks the active adapter and model
  defaults from environment variables.
- `fake_provider.py` — `FakeProvider`, the deterministic stub CI uses.
  Same prompt + schema always yields the same response shape; no
  network calls; no recording or hashing of golden outputs.
- `cache.py` — `PromptCache`, a bounded in-memory prompt → response
  cache keyed only on engine-free fields.
- `budget.py` — `GameBudget`, a per-game token + USD ceiling. Overruns
  raise `BudgetExceededError`; the budget never silently truncates.

## Runtime provider/model selection

The active provider is chosen from environment variables read at client
construction time (see `provider.build_default_client`):

| Variable | Purpose | Default |
| --- | --- | --- |
| `AILIBI_LLM_PROVIDER` | `"anthropic"` or `"fake"` | `"fake"` |
| `AILIBI_LLM_MEETING_MODEL` | Meeting-strength model id | `claude-sonnet-4-6` |
| `AILIBI_LLM_TRIGGER_MODEL` | Triggered-check model id | `claude-haiku-4-5-20251001` |
| `ANTHROPIC_API_KEY` | Required when provider is `"anthropic"` | unset |

CI must leave `AILIBI_LLM_PROVIDER` unset (or set to `"fake"`) so no
test reaches the network. The real provider is exercised only by tests
marked `pytest.mark.real_provider`, which CI skips by default.

## Minimum surface a new adapter must implement

A second provider adapter (`OpenAIClient`, `DeepSeekClient`, a local
model wrapper, ...) is a new file. The adapter must:

1. Implement the `LLMClient` Protocol — `async def complete(...) ->
   LLMResponse`. Type-checkers verify the surface; `isinstance(client,
   LLMClient)` works at runtime because the Protocol is
   `@runtime_checkable`.
2. Map the provider's native usage counters into `TokenUsage` and
   compute `cost_usd` from the provider's pricing table (provider-
   internal detail, never leaked through the Protocol).
3. Translate the engine-free `schema: type[BaseModel] | None` argument
   into the provider's structured-output mechanism (JSON mode, schema-
   constrained sampling, tool-use, ...) and validate the returned
   string with `schema.model_validate_json(...)` before constructing
   `LLMResponse`.
4. Honor `call_kind` ("meeting" | "trigger") by routing to a sensible
   default model when the caller omits `model=`; let the caller
   override per-call with `model="..."`.

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
    ) -> LLMResponse:
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
identical in shape to `AnthropicClient`'s. To activate the new adapter,
extend `build_default_client` with a `provider == "openai"` branch and
set `AILIBI_LLM_PROVIDER=openai`.

## Cache and budget composition

Both are *layers* over an `LLMClient`. The cache lookup happens first;
on a hit, no budget charge is applied (the answer was free). On a miss
the wrapped client is called and the budget is charged from the
returned `LLMResponse`.

```python
client = build_default_client()           # FakeProvider by default
cache = PromptCache()
budget = GameBudget(max_cost_usd=0.30)

response = await cache.get_or_call(
    client,
    prompt=prompt,
    schema=ReportDocument,
    max_tokens=2048,
    temperature=0.7,
    call_kind="meeting",
)
budget.charge_response(response)
```

The `BudgetExceededError` raised by `budget.charge_response` is a typed
runtime error — fail-loud, not silent truncation.
