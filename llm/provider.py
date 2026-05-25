"""Anthropic provider adapter (DESIGN.md §7, §10.4).

:class:`AnthropicClient` implements the :class:`~llm.client.LLMClient`
Protocol against the Anthropic SDK. Anthropic-specific knobs (extended
thinking, ``cache_control``, prompt-caching beta headers, message-shape
internals) are private parameters on :meth:`AnthropicClient.__init__` and
never leak through the Protocol.

CI never imports the real SDK: the adapter does the import lazily inside
:meth:`complete`. Unit tests that touch this file pass an injected
``_send`` hook so the SDK stays optional in the test environment.
"""

from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from typing import Final

from pydantic import BaseModel

from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage


DEFAULT_MEETING_MODEL: Final[str] = "claude-sonnet-4-6"
DEFAULT_TRIGGER_MODEL: Final[str] = "claude-haiku-4-5-20251001"

ENV_PROVIDER: Final[str] = "AILIBI_LLM_PROVIDER"
ENV_MEETING_MODEL: Final[str] = "AILIBI_LLM_MEETING_MODEL"
ENV_TRIGGER_MODEL: Final[str] = "AILIBI_LLM_TRIGGER_MODEL"
ENV_ANTHROPIC_API_KEY: Final[str] = "ANTHROPIC_API_KEY"

PROVIDER_ANTHROPIC: Final[str] = "anthropic"
PROVIDER_FAKE: Final[str] = "fake"

# Anthropic per-million-token list pricing as of 2026-05. Kept private so
# call sites never depend on it; if pricing changes only this file moves.
_ANTHROPIC_PRICING_USD_PER_MTOK: Final[dict[str, tuple[float, float]]] = {
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-haiku-4-5-20251001": (1.00, 5.00),
}
_FALLBACK_PRICING_USD_PER_MTOK: Final[tuple[float, float]] = (3.00, 15.00)


class AnthropicRawResponse(BaseModel):
    """Provider-agnostic shape that the injectable ``_send`` hook returns.

    Real SDK responses are unpacked into this Pydantic model inside the
    adapter; the rest of the adapter (pricing, structured-output
    validation, :class:`LLMResponse` construction) operates on this shape
    so unit tests can inject deterministic fixtures.
    """

    text: str
    model: str
    input_tokens: int
    output_tokens: int


SendHook = Callable[..., Awaitable[AnthropicRawResponse]]


class AnthropicClient:
    """Real LLM adapter behind the :class:`~llm.client.LLMClient` Protocol.

    Public surface is just :meth:`complete`. Anthropic-only configuration
    lives on the constructor:

    * ``meeting_model`` — model id for ``call_kind == "meeting"``. Defaults
      to :data:`DEFAULT_MEETING_MODEL`.
    * ``trigger_model`` — model id for ``call_kind == "trigger"``. Defaults
      to :data:`DEFAULT_TRIGGER_MODEL`.
    * ``api_key`` — Anthropic API key. Read from ``ANTHROPIC_API_KEY`` by
      :func:`build_default_client` when not passed explicitly.
    * ``extended_thinking`` / ``prompt_caching_beta`` — Anthropic-only
      knobs. Private; never on the Protocol.
    * ``send`` — injectable transport hook used by unit tests in place of
      the real SDK. Defaults to ``None`` (real SDK).
    """

    def __init__(
        self,
        *,
        api_key: str,
        meeting_model: str = DEFAULT_MEETING_MODEL,
        trigger_model: str = DEFAULT_TRIGGER_MODEL,
        extended_thinking: bool = False,
        prompt_caching_beta: bool = False,
        send: SendHook | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("AnthropicClient requires a non-empty api_key")
        self._api_key = api_key
        self._meeting_model = meeting_model
        self._trigger_model = trigger_model
        self._extended_thinking = extended_thinking
        self._prompt_caching_beta = prompt_caching_beta
        self._send: SendHook = send if send is not None else _default_send

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
        chosen_model = model if model is not None else self._model_for(call_kind)
        raw = await self._send(
            api_key=self._api_key,
            model=chosen_model,
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            extended_thinking=self._extended_thinking,
            prompt_caching_beta=self._prompt_caching_beta,
        )
        if schema is not None:
            schema.model_validate_json(raw.text)
        return LLMResponse(
            text=raw.text,
            usage=TokenUsage(
                input_tokens=raw.input_tokens,
                output_tokens=raw.output_tokens,
            ),
            cost_usd=_compute_cost_usd(
                model=raw.model,
                input_tokens=raw.input_tokens,
                output_tokens=raw.output_tokens,
            ),
            model=raw.model,
        )

    def _model_for(self, call_kind: CallKind) -> str:
        if call_kind == "meeting":
            return self._meeting_model
        if call_kind == "trigger":
            return self._trigger_model
        # Unreachable under `mypy --strict` because `CallKind` is a
        # `Literal`, but AGENTS.md mandates no silent fallbacks even for
        # type-system-guarded branches.
        raise ValueError(f"unknown call_kind: {call_kind!r}")


def build_default_client(
    *,
    env: dict[str, str] | None = None,
    send: SendHook | None = None,
) -> LLMClient:
    """Construct the default :class:`LLMClient` from environment configuration.

    Selection rules:

    * ``AILIBI_LLM_PROVIDER=fake`` (or unset) → :class:`llm.fake_provider.FakeProvider`.
      This is the default because CI must never hit the network.
    * ``AILIBI_LLM_PROVIDER=anthropic`` → :class:`AnthropicClient`, with model
      ids picked from ``AILIBI_LLM_MEETING_MODEL`` /
      ``AILIBI_LLM_TRIGGER_MODEL`` when set, otherwise their canonical
      defaults.

    The function takes an ``env`` dict so callers can construct clients
    deterministically in tests; production callers pass ``env=None`` and
    the real process environment is consulted.
    """

    environment = env if env is not None else dict(os.environ)
    provider = environment.get(ENV_PROVIDER, PROVIDER_FAKE).strip().lower()
    if provider == PROVIDER_FAKE:
        from llm.fake_provider import FakeProvider

        return FakeProvider()
    if provider == PROVIDER_ANTHROPIC:
        api_key = environment.get(ENV_ANTHROPIC_API_KEY, "")
        if not api_key:
            raise ValueError(
                f"{ENV_ANTHROPIC_API_KEY} must be set when "
                f"{ENV_PROVIDER}={PROVIDER_ANTHROPIC}"
            )
        return AnthropicClient(
            api_key=api_key,
            meeting_model=environment.get(ENV_MEETING_MODEL, DEFAULT_MEETING_MODEL),
            trigger_model=environment.get(ENV_TRIGGER_MODEL, DEFAULT_TRIGGER_MODEL),
            send=send,
        )
    raise ValueError(
        f"unknown {ENV_PROVIDER} value: {provider!r}; "
        f"expected one of {PROVIDER_ANTHROPIC!r} or {PROVIDER_FAKE!r}"
    )


def _compute_cost_usd(
    *,
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> float:
    input_rate, output_rate = _ANTHROPIC_PRICING_USD_PER_MTOK.get(
        model, _FALLBACK_PRICING_USD_PER_MTOK
    )
    return (input_tokens / 1_000_000.0) * input_rate + (
        output_tokens / 1_000_000.0
    ) * output_rate


async def _default_send(
    *,
    api_key: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
    extended_thinking: bool,
    prompt_caching_beta: bool,
) -> AnthropicRawResponse:
    # Lazy import per the module docstring (lines 9-11): the real SDK is
    # only imported when an AnthropicClient is actually invoked, so
    # FakeProvider-only test runs and `bash scripts/check.sh` never need
    # it loaded at import time.
    import anthropic

    # extended_thinking and prompt_caching_beta are plumbed through the
    # signature for a future task; wiring them to the SDK is a separate
    # concern (see PR ## Decisions). Bind them so they read as
    # intentionally-unused rather than dropped.
    _ = extended_thinking
    _ = prompt_caching_beta

    # Use the client as an async context manager so its underlying httpx
    # connection pool is closed deterministically after each call.
    # `_default_send` is a stateless module-level send-hook, so there is no
    # AnthropicClient instance on which to hang a long-lived pooled client
    # without introducing module-level state (which the design forbids).
    async with anthropic.AsyncAnthropic(api_key=api_key) as client:
        response = await client.messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}],
        )

    text_blocks = [
        block.text
        for block in response.content
        if isinstance(block, anthropic.types.TextBlock)
    ]
    if not text_blocks:
        raise RuntimeError(
            f"Anthropic returned no text content blocks (model={model!r})"
        )

    return AnthropicRawResponse(
        model=response.model,
        text="".join(text_blocks),
        input_tokens=response.usage.input_tokens,
        output_tokens=response.usage.output_tokens,
    )


__all__ = [
    "AnthropicClient",
    "AnthropicRawResponse",
    "DEFAULT_MEETING_MODEL",
    "DEFAULT_TRIGGER_MODEL",
    "ENV_ANTHROPIC_API_KEY",
    "ENV_MEETING_MODEL",
    "ENV_PROVIDER",
    "ENV_TRIGGER_MODEL",
    "PROVIDER_ANTHROPIC",
    "PROVIDER_FAKE",
    "SendHook",
    "build_default_client",
]
