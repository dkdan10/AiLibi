"""Provider-neutral LLM client surface (DESIGN.md §4.4, §7, §10.4).

The :class:`LLMClient` :class:`~typing.Protocol` is what every call site in
``agents/strategic/``, ``meetings/``, and ``orchestrator/`` consumes. The
Protocol does not expose provider-specific concepts (extended thinking,
``cache_control``, prompt-caching beta headers, message-shape internals).
Anthropic-only knobs live as private parameters on
:class:`llm.provider.AnthropicClient`; adding an OpenAI, DeepSeek, or local
adapter is a new-file change.

Minimum surface a second-provider adapter must implement
========================================================

To add a provider (``OpenAIClient``, ``DeepSeekClient``, ...), the new
adapter file does three things:

1. Implement the :class:`LLMClient` Protocol — one ``async def complete``
   method returning :class:`LLMResponse`.
2. Map provider-native usage counts into the engine-free
   :class:`TokenUsage` shape and compute ``cost_usd`` from the provider's
   pricing table (provider-internal detail, never leaked to callers).
3. Translate the engine-free ``schema`` argument into whatever structured-
   output mechanism the provider supports (JSON mode, schema validation,
   function calling) and validate the resulting string with the supplied
   Pydantic model before returning ``LLMResponse``.

Call sites accept the Protocol type. They never type-hint a concrete
adapter, so swapping providers requires editing only the constructor in
:func:`build_default_client` (see :mod:`llm.provider`).

Worked sketch — what an OpenAI adapter would look like
------------------------------------------------------

::

    class OpenAIClient:
        def __init__(self, *, api_key: str, default_model: str) -> None:
            self._api_key = api_key
            self._default_model = default_model

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
            response = await _openai_sdk_call(
                model=model or self._default_model,
                prompt=prompt,
                schema=schema,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            text = response.text
            if schema is not None:
                schema.model_validate_json(text)
            return LLMResponse(
                text=text,
                usage=TokenUsage(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                ),
                cost_usd=_openai_pricing(response.model, response.usage),
                model=response.model,
            )

The sketch shows that nothing about OpenAI's wire format leaks into the
Protocol — ``cost_usd`` is computed inside the adapter, structured output
goes through the same opaque ``schema`` knob, and the returned
:class:`LLMResponse` is identical in shape to the Anthropic adapter's.

Runtime provider/model selection
================================

The active provider and per-call-kind model defaults are chosen at
construction time from environment variables:

* ``AILIBI_LLM_PROVIDER`` — selects the adapter (``"anthropic"`` |
  ``"fake"``). Defaults to ``"fake"`` so unit tests and CI never hit the
  network. Real provider runs opt in explicitly.
* ``AILIBI_LLM_MEETING_MODEL`` — overrides the meeting-strength model id.
* ``AILIBI_LLM_TRIGGER_MODEL`` — overrides the triggered-check model id.

Per-call overrides go through the ``model`` argument to
:meth:`LLMClient.complete`. See :func:`llm.provider.build_default_client`.
"""

from __future__ import annotations

from typing import Literal, Protocol, runtime_checkable

from pydantic import BaseModel, ConfigDict


CallKind = Literal["meeting", "trigger"]


class TokenUsage(BaseModel):
    """Engine-free usage counts.

    Mirrors the two counts every real provider reports; cache-hit / cache-
    miss splits and provider-specific telemetry stay inside the adapter.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    input_tokens: int
    output_tokens: int


class LLMResponse(BaseModel):
    """One completion result, provider-neutral.

    ``cost_usd`` is computed by the adapter from provider pricing so
    consumers can budget without knowing the provider. ``model`` is the
    string id the adapter actually called — opaque to consumers, useful
    for replay records.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    text: str
    usage: TokenUsage
    cost_usd: float
    model: str


@runtime_checkable
class LLMClient(Protocol):
    """Minimal Protocol every adapter implements.

    ``call_kind`` is a Protocol-level tag that lets adapters route to the
    right model default without exposing model ids to call sites. It is
    *not* a provider-specific knob; every provider has at least one
    meeting-strength and one triggered-check tier.

    ``model`` overrides the adapter's per-call-kind default on this call
    only. Pass ``None`` to use the default for ``call_kind``.

    ``schema`` is an opaque Pydantic class. The adapter is responsible
    for telling the underlying provider to emit structured output and
    for validating the result before returning.
    """

    async def complete(
        self,
        *,
        prompt: str,
        schema: type[BaseModel] | None,
        max_tokens: int,
        temperature: float,
        call_kind: CallKind = "meeting",
        model: str | None = None,
    ) -> LLMResponse: ...


__all__ = [
    "CallKind",
    "LLMClient",
    "LLMResponse",
    "TokenUsage",
]
