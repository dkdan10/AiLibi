from __future__ import annotations

import asyncio
import inspect
import os
from collections.abc import Awaitable
from typing import TypeVar

import pytest
from pydantic import BaseModel, ConfigDict

from llm.cache import PromptCache
from llm.client import CallKind, LLMClient, LLMResponse, TokenUsage
from llm.fake_provider import FakeProvider
from llm.provider import (
    DEFAULT_MEETING_MODEL,
    DEFAULT_TRIGGER_MODEL,
    ENV_ANTHROPIC_API_KEY,
    ENV_MEETING_MODEL,
    ENV_PROVIDER,
    ENV_TRIGGER_MODEL,
    PROVIDER_ANTHROPIC,
    PROVIDER_FAKE,
    AnthropicClient,
    AnthropicRawResponse,
    build_default_client,
)

_T = TypeVar("_T")


class _ReportSchema(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    agent_id: str
    tick: int
    confidence: float


class _NestedSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    primary: _ReportSchema
    rationale: str


def _run(coro: Awaitable[_T]) -> _T:
    return asyncio.new_event_loop().run_until_complete(coro)


class TestLLMClientProtocolSurface:
    def test_protocol_complete_signature_is_provider_neutral(self) -> None:
        signature = inspect.signature(LLMClient.complete)
        parameter_names = tuple(signature.parameters.keys())
        assert parameter_names == (
            "self",
            "prompt",
            "schema",
            "max_tokens",
            "temperature",
            "call_kind",
            "model",
        )

    def test_fake_provider_is_an_llm_client(self) -> None:
        assert isinstance(FakeProvider(), LLMClient)

    def test_anthropic_client_is_an_llm_client(self) -> None:
        client = AnthropicClient(api_key="anthropic-test-key")
        assert isinstance(client, LLMClient)


class TestFakeProviderDeterminism:
    def test_same_inputs_yield_byte_identical_response(self) -> None:
        provider = FakeProvider()

        first = _run(
            provider.complete(
                prompt="hello world",
                schema=_ReportSchema,
                max_tokens=512,
                temperature=0.0,
            )
        )
        second = _run(
            provider.complete(
                prompt="hello world",
                schema=_ReportSchema,
                max_tokens=512,
                temperature=0.0,
            )
        )

        assert isinstance(first, LLMResponse)
        assert isinstance(second, LLMResponse)
        assert first == second

    def test_response_is_schema_valid(self) -> None:
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt="schema-valid prompt",
                schema=_ReportSchema,
                max_tokens=512,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        parsed = _ReportSchema.model_validate_json(response.text)
        assert isinstance(parsed, _ReportSchema)

    def test_response_with_no_schema_is_still_deterministic_string(self) -> None:
        provider = FakeProvider()

        first = _run(
            provider.complete(
                prompt="no schema",
                schema=None,
                max_tokens=64,
                temperature=0.0,
            )
        )
        second = _run(
            provider.complete(
                prompt="no schema",
                schema=None,
                max_tokens=64,
                temperature=0.0,
            )
        )

        assert isinstance(first, LLMResponse)
        assert isinstance(second, LLMResponse)
        assert first == second
        assert first.text.startswith("fake-response:")

    def test_cost_is_always_zero(self) -> None:
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt="cost zero",
                schema=None,
                max_tokens=64,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.cost_usd == 0.0

    def test_meeting_and_trigger_call_kinds_pick_distinct_fake_models(self) -> None:
        provider = FakeProvider()

        meeting = _run(
            provider.complete(
                prompt="x",
                schema=None,
                max_tokens=4,
                temperature=0.0,
                call_kind="meeting",
            )
        )
        trigger = _run(
            provider.complete(
                prompt="x",
                schema=None,
                max_tokens=4,
                temperature=0.0,
                call_kind="trigger",
            )
        )

        assert isinstance(meeting, LLMResponse)
        assert isinstance(trigger, LLMResponse)
        assert meeting.model != trigger.model

    def test_explicit_model_overrides_call_kind_default(self) -> None:
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt="explicit model",
                schema=None,
                max_tokens=4,
                temperature=0.0,
                call_kind="meeting",
                model="claude-sonnet-4-6",
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.model == "claude-sonnet-4-6"

    def test_invalid_temperature_is_rejected(self) -> None:
        provider = FakeProvider()

        with pytest.raises(ValueError, match="temperature"):
            _run(
                provider.complete(
                    prompt="x",
                    schema=None,
                    max_tokens=4,
                    temperature=-0.1,
                )
            )

    def test_zero_max_tokens_is_rejected(self) -> None:
        provider = FakeProvider()

        with pytest.raises(ValueError, match="max_tokens"):
            _run(
                provider.complete(
                    prompt="x",
                    schema=None,
                    max_tokens=0,
                    temperature=0.0,
                )
            )


class TestFakeProviderSchemaCoverage:
    def test_handles_nested_pydantic_schema(self) -> None:
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt="nested",
                schema=_NestedSchema,
                max_tokens=128,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        parsed = _NestedSchema.model_validate_json(response.text)
        assert isinstance(parsed.primary, _ReportSchema)

    def test_response_is_returned_as_json_when_schema_supplied(self) -> None:
        provider = FakeProvider()

        response = _run(
            provider.complete(
                prompt="json check",
                schema=_ReportSchema,
                max_tokens=128,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        assert response.text.startswith("{")
        assert response.text.endswith("}")


class TestAnthropicClientPrivateKnobsAndCallKindRouting:
    def test_call_kind_meeting_picks_meeting_model_default(self) -> None:
        captured: dict[str, str] = {}

        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            captured["model"] = str(kwargs["model"])
            return AnthropicRawResponse(
                text="ok",
                model=str(kwargs["model"]),
                input_tokens=10,
                output_tokens=4,
            )

        client = AnthropicClient(api_key="key", send=fake_send)

        response = _run(
            client.complete(
                prompt="meeting",
                schema=None,
                max_tokens=512,
                temperature=0.0,
                call_kind="meeting",
            )
        )

        assert isinstance(response, LLMResponse)
        assert captured["model"] == DEFAULT_MEETING_MODEL
        assert response.model == DEFAULT_MEETING_MODEL

    def test_call_kind_trigger_picks_trigger_model_default(self) -> None:
        captured: dict[str, str] = {}

        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            captured["model"] = str(kwargs["model"])
            return AnthropicRawResponse(
                text="ok",
                model=str(kwargs["model"]),
                input_tokens=10,
                output_tokens=4,
            )

        client = AnthropicClient(api_key="key", send=fake_send)

        _ = _run(
            client.complete(
                prompt="trigger",
                schema=None,
                max_tokens=128,
                temperature=0.0,
                call_kind="trigger",
            )
        )

        assert captured["model"] == DEFAULT_TRIGGER_MODEL

    def test_per_call_model_override_takes_precedence(self) -> None:
        captured: dict[str, str] = {}

        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            captured["model"] = str(kwargs["model"])
            return AnthropicRawResponse(
                text="ok",
                model=str(kwargs["model"]),
                input_tokens=10,
                output_tokens=4,
            )

        client = AnthropicClient(api_key="key", send=fake_send)

        _ = _run(
            client.complete(
                prompt="override",
                schema=None,
                max_tokens=128,
                temperature=0.0,
                call_kind="meeting",
                model="claude-haiku-4-5-20251001",
            )
        )

        assert captured["model"] == "claude-haiku-4-5-20251001"

    def test_constructor_overrides_default_model_ids(self) -> None:
        captured: dict[str, str] = {}

        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            captured["model"] = str(kwargs["model"])
            return AnthropicRawResponse(
                text="ok",
                model=str(kwargs["model"]),
                input_tokens=10,
                output_tokens=4,
            )

        client = AnthropicClient(
            api_key="key",
            meeting_model="custom-meeting",
            trigger_model="custom-trigger",
            send=fake_send,
        )

        _ = _run(
            client.complete(
                prompt="custom",
                schema=None,
                max_tokens=8,
                temperature=0.0,
            )
        )

        assert captured["model"] == "custom-meeting"

    def test_extended_thinking_and_caching_beta_flow_through_send_hook(self) -> None:
        captured: dict[str, object] = {}

        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            captured.update(kwargs)
            return AnthropicRawResponse(
                text="ok",
                model=str(kwargs["model"]),
                input_tokens=1,
                output_tokens=1,
            )

        client = AnthropicClient(
            api_key="key",
            extended_thinking=True,
            prompt_caching_beta=True,
            send=fake_send,
        )

        _ = _run(
            client.complete(
                prompt="anthropic-only",
                schema=None,
                max_tokens=8,
                temperature=0.0,
            )
        )

        assert captured["extended_thinking"] is True
        assert captured["prompt_caching_beta"] is True

    def test_empty_api_key_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="api_key"):
            AnthropicClient(api_key="")

    def test_cost_usd_uses_known_model_pricing(self) -> None:
        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            return AnthropicRawResponse(
                text="ok",
                model=DEFAULT_MEETING_MODEL,
                input_tokens=1_000_000,
                output_tokens=1_000_000,
            )

        client = AnthropicClient(api_key="key", send=fake_send)

        response = _run(
            client.complete(
                prompt="cost",
                schema=None,
                max_tokens=8,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        # Sonnet pricing: $3/Mtok input + $15/Mtok output = $18 per million.
        assert response.cost_usd == pytest.approx(18.0)

    def test_unknown_model_uses_fallback_pricing(self) -> None:
        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            return AnthropicRawResponse(
                text="ok",
                model="unknown-model-id",
                input_tokens=2_000_000,
                output_tokens=0,
            )

        client = AnthropicClient(api_key="key", send=fake_send)

        response = _run(
            client.complete(
                prompt="cost",
                schema=None,
                max_tokens=8,
                temperature=0.0,
            )
        )

        assert isinstance(response, LLMResponse)
        # Fallback uses Sonnet rates: 2M input @ $3 = $6.
        assert response.cost_usd == pytest.approx(6.0)

    def test_schema_validation_rejects_non_schema_payload(self) -> None:
        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            return AnthropicRawResponse(
                text="not json",
                model=DEFAULT_MEETING_MODEL,
                input_tokens=1,
                output_tokens=1,
            )

        client = AnthropicClient(api_key="key", send=fake_send)

        with pytest.raises(Exception):
            _run(
                client.complete(
                    prompt="bad",
                    schema=_ReportSchema,
                    max_tokens=8,
                    temperature=0.0,
                )
            )

    def test_default_send_raises_when_unconfigured(self) -> None:
        # No send hook injected and no real Anthropic SDK is wired in this
        # build; the adapter must raise loudly rather than silently fall back.
        client = AnthropicClient(api_key="key")

        with pytest.raises(RuntimeError, match="Anthropic SDK"):
            _run(
                client.complete(
                    prompt="x",
                    schema=None,
                    max_tokens=8,
                    temperature=0.0,
                )
            )


class TestBuildDefaultClient:
    def test_defaults_to_fake_provider(self) -> None:
        client = build_default_client(env={})

        assert isinstance(client, FakeProvider)

    def test_explicit_fake_provider(self) -> None:
        client = build_default_client(env={ENV_PROVIDER: PROVIDER_FAKE})

        assert isinstance(client, FakeProvider)

    def test_anthropic_provider_requires_api_key(self) -> None:
        with pytest.raises(ValueError, match=ENV_ANTHROPIC_API_KEY):
            build_default_client(env={ENV_PROVIDER: PROVIDER_ANTHROPIC})

    def test_anthropic_provider_uses_env_model_overrides(self) -> None:
        captured: dict[str, str] = {}

        async def fake_send(**kwargs: object) -> AnthropicRawResponse:
            captured["model"] = str(kwargs["model"])
            return AnthropicRawResponse(
                text="ok",
                model=str(kwargs["model"]),
                input_tokens=1,
                output_tokens=1,
            )

        client = build_default_client(
            env={
                ENV_PROVIDER: PROVIDER_ANTHROPIC,
                ENV_ANTHROPIC_API_KEY: "k",
                ENV_MEETING_MODEL: "env-meeting",
                ENV_TRIGGER_MODEL: "env-trigger",
            },
            send=fake_send,
        )

        assert isinstance(client, AnthropicClient)

        _ = _run(
            client.complete(
                prompt="x",
                schema=None,
                max_tokens=8,
                temperature=0.0,
                call_kind="meeting",
            )
        )
        assert captured["model"] == "env-meeting"

        _ = _run(
            client.complete(
                prompt="x",
                schema=None,
                max_tokens=8,
                temperature=0.0,
                call_kind="trigger",
            )
        )
        assert captured["model"] == "env-trigger"

    def test_unknown_provider_value_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown"):
            build_default_client(env={ENV_PROVIDER: "deepseek"})


class TestPromptCache:
    def test_miss_then_hit(self) -> None:
        cache = PromptCache()
        client = FakeProvider()

        first = _run(
            cache.get_or_call(
                client,
                prompt="cached",
                schema=None,
                max_tokens=32,
                temperature=0.0,
            )
        )
        second = _run(
            cache.get_or_call(
                client,
                prompt="cached",
                schema=None,
                max_tokens=32,
                temperature=0.0,
            )
        )

        assert isinstance(first, LLMResponse)
        assert isinstance(second, LLMResponse)
        assert first == second
        assert cache.hits == 1
        assert cache.misses == 1
        assert len(cache) == 1

    def test_keys_are_provider_neutral(self) -> None:
        cache = PromptCache()
        cache.put(
            prompt="p",
            schema=None,
            max_tokens=32,
            temperature=0.0,
            call_kind="meeting",
            model=None,
            response=LLMResponse(
                text="x",
                usage=TokenUsage(input_tokens=1, output_tokens=1),
                cost_usd=0.0,
                model="m",
            ),
        )

        # Distinct call kinds key separately even on the same prompt — the
        # cache is provider-agnostic, not collision-on-prompt.
        hit_meeting = cache.get(
            prompt="p",
            schema=None,
            max_tokens=32,
            temperature=0.0,
            call_kind="meeting",
            model=None,
        )
        miss_trigger = cache.get(
            prompt="p",
            schema=None,
            max_tokens=32,
            temperature=0.0,
            call_kind="trigger",
            model=None,
        )

        assert hit_meeting is not None
        assert miss_trigger is None

    def test_temperature_and_max_tokens_affect_key(self) -> None:
        cache = PromptCache()
        cache.put(
            prompt="p",
            schema=None,
            max_tokens=32,
            temperature=0.0,
            call_kind="meeting",
            model=None,
            response=LLMResponse(
                text="x",
                usage=TokenUsage(input_tokens=1, output_tokens=1),
                cost_usd=0.0,
                model="m",
            ),
        )

        # Different temperature is a different cache entry.
        assert (
            cache.get(
                prompt="p",
                schema=None,
                max_tokens=32,
                temperature=0.7,
                call_kind="meeting",
                model=None,
            )
            is None
        )

        # Different max_tokens is a different cache entry too.
        assert (
            cache.get(
                prompt="p",
                schema=None,
                max_tokens=64,
                temperature=0.0,
                call_kind="meeting",
                model=None,
            )
            is None
        )

    def test_fifo_eviction_respects_max_entries(self) -> None:
        cache = PromptCache(max_entries=2)

        for i in range(3):
            cache.put(
                prompt=f"p{i}",
                schema=None,
                max_tokens=32,
                temperature=0.0,
                call_kind="meeting",
                model=None,
                response=LLMResponse(
                    text=str(i),
                    usage=TokenUsage(input_tokens=1, output_tokens=1),
                    cost_usd=0.0,
                    model="m",
                ),
            )

        # First insert was evicted, last two survive.
        assert (
            cache.get(
                prompt="p0",
                schema=None,
                max_tokens=32,
                temperature=0.0,
                call_kind="meeting",
                model=None,
            )
            is None
        )
        assert (
            cache.get(
                prompt="p2",
                schema=None,
                max_tokens=32,
                temperature=0.0,
                call_kind="meeting",
                model=None,
            )
            is not None
        )

    def test_zero_max_entries_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="max_entries"):
            PromptCache(max_entries=0)

    def test_clear_resets_counters_and_entries(self) -> None:
        cache = PromptCache()
        cache.put(
            prompt="p",
            schema=None,
            max_tokens=32,
            temperature=0.0,
            call_kind="meeting",
            model=None,
            response=LLMResponse(
                text="x",
                usage=TokenUsage(input_tokens=1, output_tokens=1),
                cost_usd=0.0,
                model="m",
            ),
        )
        cache.get(
            prompt="p",
            schema=None,
            max_tokens=32,
            temperature=0.0,
            call_kind="meeting",
            model=None,
        )

        cache.clear()

        assert len(cache) == 0
        assert cache.hits == 0
        assert cache.misses == 0


# Real-provider tests opt in via an environment flag. CI does not set
# AILIBI_RUN_REAL_PROVIDER_TESTS so anything decorated with
# `real_provider` is skipped by default. The mechanism is "equivalent" to
# `pytest.mark.real_provider` per the Task 3.1 DoD: opt-in by default,
# never reaches the network in CI.
real_provider = pytest.mark.skipif(
    os.environ.get("AILIBI_RUN_REAL_PROVIDER_TESTS") != "1",
    reason=(
        "real-provider tests skipped by default; set "
        "AILIBI_RUN_REAL_PROVIDER_TESTS=1 to enable"
    ),
)


class TestRealProviderIsCISkipped:
    """Pin that the real-provider tests are CI-skippable.

    The `real_provider` marker above wraps `pytest.mark.skipif` on an
    env-var gate. CI does not set the env var so any test decorated with
    `@real_provider` is reported as skipped — no real network call ever
    runs in CI.
    """

    @real_provider
    def test_marked_real_provider_test_is_visible_to_pytest(self) -> None:
        # Body is intentionally trivial; the assertion is that this test
        # exists and is gated by the marker (collected, but skipped).
        assert True

    def test_real_provider_marker_is_skipif_in_ci(self) -> None:
        # Direct check that the marker is a skipif gate and that the gate
        # condition is True under the CI environment.
        assert real_provider.mark.name == "skipif"
        assert real_provider.mark.args[0] is True


def test_call_kind_literal_has_only_two_values() -> None:
    from typing import get_args

    assert set(get_args(CallKind)) == {"meeting", "trigger"}


def test_fake_provider_is_default_and_makes_no_network_calls() -> None:
    # The CI default is the fake; pin that build_default_client with an
    # empty environment never returns a real-network adapter.
    client = build_default_client(env={})
    assert isinstance(client, FakeProvider)
    response = _run(
        client.complete(
            prompt="ci-default",
            schema=None,
            max_tokens=8,
            temperature=0.0,
        )
    )
    assert isinstance(response, LLMResponse)
    assert response.cost_usd == 0.0
